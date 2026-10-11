//! Phase 3 (docs/designs/EXCITON_FLUID_PHASE3_PREREG.md): driven-dissipative Gross-Pitaevskii equation with an incoherent
//! reservoir on a 16x16 periodic grid. CVODE (BDF) for all flows; the ARKode-style IMEX module of sundials-core for D-e/D-f.
//!
//!     dd <mode> <out_dir>      mode in a | b | c | d | e | f | g
use cvode::{Cvode, Method, Task};
use nvector::SerialVector;
use qf_exciton_p1::rng::SplitMix64;
use std::f64::consts::PI;
use std::fmt::Write as _;
use std::fs;
use std::io::Write as _;
use sundials_core::arkode::imex::{ImexSolver, ImexTableau};

#[cfg(not(feature = "m8"))]
const M: usize = 16;
#[cfg(feature = "m8")]
const M: usize = 8; // amendment A3 of the Phase 3 pre-registration: compute-budget grid for D-a, D-d, D-g
const LOGM: u32 = M.trailing_zeros();
const NN: usize = M * M;
const NY: usize = 3 * NN;
const L: f64 = M as f64;
const SIGMA: f64 = if M == 16 { 3.0 } else { 1.5 };

#[derive(Clone, Copy)]
struct Par {
    g: f64,
    gr: f64,
    gamma: f64,
    gamma_r: f64,
    r: f64,
    r_psi: f64, // R as seen by the psi equation (equal to r unless a bug is planted)
    p: f64,
}

impl Par {
    fn reg() -> Par {
        Par { g: 0.04, gr: 1.0, gamma: 0.1, gamma_r: 200.0, r: 1.0, r_psi: 1.0, p: 21.0 }
    }
}

struct Model {
    k2: Vec<f64>,
    tc: Vec<f64>,
    ts: Vec<f64>,
    v: Vec<f64>,
    par: Par,
    om_frame: f64, // frame rotating at om_frame
}

fn mfreq(i: usize) -> i32 {
    if i > M / 2 {
        i as i32 - M as i32
    } else {
        i as i32
    }
}


/// Radix-2 FFT of length 16 on interleaved complex arrays (in place), forward `e^{-i}` or inverse `e^{+i}` (unnormalised).
fn fft16(re: &mut [f64; M], im: &mut [f64; M], inverse: bool) {
    // bit reversal
    for i in 0..M {
        let j = (i as u32).reverse_bits() as usize >> (32 - LOGM);
        if j > i {
            re.swap(i, j);
            im.swap(i, j);
        }
    }
    let mut len = 2;
    while len <= M {
        let ang = if inverse { 2.0 * PI } else { -2.0 * PI } / len as f64;
        for k in (0..M).step_by(len) {
            for j in 0..len / 2 {
                let (wr, wi) = ((ang * j as f64).cos(), (ang * j as f64).sin());
                let (a, b) = (k + j, k + j + len / 2);
                let (tr, ti) = (re[b] * wr - im[b] * wi, re[b] * wi + im[b] * wr);
                re[b] = re[a] - tr;
                im[b] = im[a] - ti;
                re[a] += tr;
                im[a] += ti;
            }
        }
        len <<= 1;
    }
}

fn fft2(re: &[f64], im: &[f64], inverse: bool) -> ([f64; NN], [f64; NN]) {
    let mut or = [0.0; NN];
    let mut oi = [0.0; NN];
    let (mut r, mut i_) = ([0.0; M], [0.0; M]);
    for x in 0..M {
        r.copy_from_slice(&re[x * M..(x + 1) * M]);
        i_.copy_from_slice(&im[x * M..(x + 1) * M]);
        fft16(&mut r, &mut i_, inverse);
        or[x * M..(x + 1) * M].copy_from_slice(&r);
        oi[x * M..(x + 1) * M].copy_from_slice(&i_);
    }
    for y in 0..M {
        for x in 0..M {
            r[x] = or[x * M + y];
            i_[x] = oi[x * M + y];
        }
        fft16(&mut r, &mut i_, inverse);
        for x in 0..M {
            or[x * M + y] = r[x];
            oi[x * M + y] = i_[x];
        }
    }
    if inverse {
        let f = 1.0 / NN as f64;
        or.iter_mut().for_each(|v| *v *= f);
        oi.iter_mut().for_each(|v| *v *= f);
    }
    (or, oi)
}

fn gate(v0: f64, sigma: f64) -> Vec<f64> {
    let mut v = vec![0.0; NN];
    for x in 0..M {
        for y in 0..M {
            let dx = (x as f64 - M as f64 / 2.0).abs().min(M as f64 - (x as f64 - M as f64 / 2.0).abs());
            let dy = (y as f64 - M as f64 / 2.0).abs().min(M as f64 - (y as f64 - M as f64 / 2.0).abs());
            v[x * M + y] = v0 * (-(dx * dx + dy * dy) / (2.0 * sigma * sigma)).exp();
        }
    }
    v
}

impl Model {
    fn new(par: Par, v: Vec<f64>, om_frame: f64) -> Model {
        let mut k2 = vec![0.0; NN];
        for i in 0..M {
            for j in 0..M {
                let kx = 2.0 * PI * mfreq(i) as f64 / L;
                let ky = 2.0 * PI * mfreq(j) as f64 / L;
                k2[i * M + j] = kx * kx + ky * ky;
            }
        }
        let mut tc = vec![0.0; M * M];
        let mut ts = vec![0.0; M * M];
        for j in 0..M {
            for m in 0..M {
                let a = 2.0 * PI * ((j * m) % M) as f64 / M as f64;
                tc[j * M + m] = a.cos();
                ts[j * M + m] = a.sin();
            }
        }
        Model { k2, tc, ts, v, par, om_frame }
    }

    fn dft2(&self, re: &[f64], im: &[f64], inverse: bool) -> (Vec<f64>, Vec<f64>) {
        let sgn = if inverse { 1.0 } else { -1.0 };
        let mut tr = vec![0.0; NN];
        let mut ti = vec![0.0; NN];
        for x in 0..M {
            for ky in 0..M {
                let (mut sr, mut si) = (0.0, 0.0);
                for y in 0..M {
                    let c = self.tc[ky * M + y];
                    let s = sgn * self.ts[ky * M + y];
                    let (a, b) = (re[x * M + y], im[x * M + y]);
                    sr += a * c - b * s;
                    si += a * s + b * c;
                }
                tr[x * M + ky] = sr;
                ti[x * M + ky] = si;
            }
        }
        let mut or = vec![0.0; NN];
        let mut oi = vec![0.0; NN];
        for ky in 0..M {
            for kx in 0..M {
                let (mut sr, mut si) = (0.0, 0.0);
                for x in 0..M {
                    let c = self.tc[kx * M + x];
                    let s = sgn * self.ts[kx * M + x];
                    let (a, b) = (tr[x * M + ky], ti[x * M + ky]);
                    sr += a * c - b * s;
                    si += a * s + b * c;
                }
                or[kx * M + ky] = sr;
                oi[kx * M + ky] = si;
            }
        }
        if inverse {
            let f = 1.0 / NN as f64;
            or.iter_mut().for_each(|v| *v *= f);
            oi.iter_mut().for_each(|v| *v *= f);
        }
        (or, oi)
    }

    /// kinetic part `-1/2 lap psi` (FFT; `dft2_kin` is the original naive DFT version, kept for the equivalence test)
    fn kin(&self, re: &[f64], im: &[f64]) -> ([f64; NN], [f64; NN]) {
        let (mut pr, mut pi) = fft2(re, im, false);
        for i in 0..NN {
            pr[i] *= 0.5 * self.k2[i];
            pi[i] *= 0.5 * self.k2[i];
        }
        fft2(&pr, &pi, true)
    }

    fn kin_naive(&self, re: &[f64], im: &[f64]) -> (Vec<f64>, Vec<f64>) {
        let (pr, pi) = self.dft2(re, im, false);
        let tr: Vec<f64> = (0..NN).map(|i| 0.5 * self.k2[i] * pr[i]).collect();
        let ti: Vec<f64> = (0..NN).map(|i| 0.5 * self.k2[i] * pi[i]).collect();
        self.dft2(&tr, &ti, true)
    }

    /// Right-hand side in the frame rotating at `om_frame`. `stiff_in_f`: include the `-gamma_r nR` decay (CVODE: yes;
    /// IMEX explicit part: no).
    fn rhs(&self, y: &[f64], yd: &mut [f64], with_decay: bool) {
        let p = &self.par;
        let (re, rest) = y.split_at(NN);
        let (im, nr) = rest.split_at(NN);
        let (kr, ki) = self.kin(re, im);
        for i in 0..NN {
            let n = re[i] * re[i] + im[i] * im[i];
            let w = self.v[i] + p.g * n + p.gr * nr[i];
            let hr = kr[i] + w * re[i];
            let hi = ki[i] + w * im[i];
            let gain = 0.5 * (p.r_psi * nr[i] - p.gamma);
            yd[i] = hi + gain * re[i] - self.om_frame * im[i];
            yd[NN + i] = -hr + gain * im[i] + self.om_frame * re[i];
            let decay = if with_decay { p.gamma_r } else { 0.0 };
            yd[2 * NN + i] = p.p - (decay + p.r * n) * nr[i];
        }
    }

    fn rhs_vec(&self, y: &[f64]) -> Vec<f64> {
        let mut yd = vec![0.0; NY];
        self.rhs(y, &mut yd, true);
        yd
    }
}

fn state_uniform(n: f64, nr: f64, noise: f64, seed: u64) -> Vec<f64> {
    let mut rng = SplitMix64::new(seed);
    let mut y = vec![0.0; NY];
    for i in 0..NN {
        y[i] = n.sqrt() * (1.0 + noise * (2.0 * rng.uniform() - 1.0));
    }
    for i in 0..NN {
        y[NN + i] = n.sqrt() * noise * (2.0 * rng.uniform() - 1.0);
    }
    for i in 0..NN {
        y[2 * NN + i] = nr;
    }
    y
}

struct Flow {
    y: Vec<f64>,
    steps: usize,
    error: Option<String>,
}

fn flow(model: &std::sync::Arc<Model>, y0: &[f64], t_end: f64, rtol: f64, atol: f64) -> Flow {
    let m = std::sync::Arc::clone(model);
    let rhs = move |_t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
        m.rhs(y, yd, true);
        Ok(())
    };
    let mut s = match Cvode::builder(Method::Bdf).rtol(rtol).atol(atol).max_steps(2_000_000).build(rhs, 0.0, SerialVector::from_slice(y0)) {
        Ok(s) => s,
        Err(e) => return Flow { y: y0.to_vec(), steps: 0, error: Some(format!("build: {e:?}")) },
    };
    let mut t = 0.0;
    let mut y = y0.to_vec();
    let dt = if t_end > 400.0 { 250.0 } else { t_end };
    while t < t_end - 1e-12 {
        t = (t + dt).min(t_end);
        match s.solve(t, Task::Normal) {
            Ok((_, v)) => y = v.to_vec(),
            Err(e) => return Flow { y, steps: s.num_steps(), error: Some(format!("solve at t={t}: {e:?}")) },
        }
    }
    Flow { y, steps: s.num_steps(), error: None }
}

struct Obs {
    mean_n: f64,
    mean_nr: f64,
    std_n: f64,
    omega: f64,
    resid: f64,
    norm2: f64,
    budget_rel: f64,
    n_center: f64,
    n_corner: f64,
    max_j: f64,
}

fn observe(model: &Model, y: &[f64]) -> Obs {
    // observables in the LAB frame: use a copy of the model with om_frame = 0
    let lab = Model { k2: model.k2.clone(), tc: model.tc.clone(), ts: model.ts.clone(), v: model.v.clone(), par: model.par, om_frame: 0.0 };
    let yd = lab.rhs_vec(y);
    let (re, rest) = y.split_at(NN);
    let (im, nr) = rest.split_at(NN);
    let n: Vec<f64> = (0..NN).map(|i| re[i] * re[i] + im[i] * im[i]).collect();
    let norm2: f64 = n.iter().sum();
    let mean_n = norm2 / NN as f64;
    let mean_nr = nr.iter().sum::<f64>() / NN as f64;
    let std_n = (n.iter().map(|v| (v - mean_n) * (v - mean_n)).sum::<f64>() / NN as f64).sqrt();
    let im_ov: f64 = (0..NN).map(|i| re[i] * yd[NN + i] - im[i] * yd[i]).sum();
    let omega = -im_ov / norm2;
    let mut r2 = 0.0;
    for i in 0..NN {
        let a = yd[i] - omega * im[i];
        let b = yd[NN + i] + omega * re[i];
        r2 += a * a + b * b;
    }
    let p = &model.par;
    let gain_budget: f64 = NN as f64 * p.p;
    let loss: f64 = (0..NN).map(|i| p.gamma_r * nr[i] + p.gamma * n[i]).sum();
    // current j = Im(conj(psi) grad psi) spectral, max |j|
    let (pr, pi) = lab.dft2(re, im, false);
    let mut max_j: f64 = 0.0;
    let (mut jx, mut jy) = (vec![0.0; NN], vec![0.0; NN]);
    {
        let (mut ar, mut ai, mut br, mut bi) = (vec![0.0; NN], vec![0.0; NN], vec![0.0; NN], vec![0.0; NN]);
        for i in 0..M {
            for j in 0..M {
                let kx = 2.0 * PI * mfreq(i) as f64 / L;
                let ky = 2.0 * PI * mfreq(j) as f64 / L;
                let (mut kxe, mut kye) = (kx, ky);
                if i == M / 2 {
                    kxe = 0.0;
                }
                if j == M / 2 {
                    kye = 0.0;
                }
                let idx = i * M + j;
                // i k psi_hat
                ar[idx] = -kxe * pi[idx];
                ai[idx] = kxe * pr[idx];
                br[idx] = -kye * pi[idx];
                bi[idx] = kye * pr[idx];
            }
        }
        let (gxr, gxi) = lab.dft2(&ar, &ai, true);
        let (gyr, gyi) = lab.dft2(&br, &bi, true);
        for i in 0..NN {
            jx[i] = re[i] * gxi[i] - im[i] * gxr[i];
            jy[i] = re[i] * gyi[i] - im[i] * gyr[i];
            max_j = max_j.max((jx[i] * jx[i] + jy[i] * jy[i]).sqrt());
        }
    }
    Obs {
        mean_n,
        mean_nr,
        std_n,
        omega,
        resid: r2.sqrt() / norm2.sqrt(),
        norm2,
        budget_rel: (gain_budget - loss).abs() / gain_budget,
        n_center: n[(M / 2) * M + M / 2],
        n_corner: n[0],
        max_j,
    }
}

fn jstr(s: &Option<String>) -> String {
    match s {
        Some(m) => format!("\"{}\"", m.replace('\\', "\\\\").replace('"', "'")),
        None => "null".into(),
    }
}

fn obs_json(o: &Obs) -> String {
    format!(
        "\"mean_n\":{:.17e},\"mean_nr\":{:.17e},\"std_n\":{:.6e},\"omega\":{:.17e},\"resid_rel\":{:.6e},\"norm2\":{:.17e},\"budget_rel\":{:.6e},\"n_center\":{:.12e},\"n_corner\":{:.12e},\"max_j\":{:.6e}",
        o.mean_n, o.mean_nr, o.std_n, o.omega, o.resid, o.norm2, o.budget_rel, o.n_center, o.n_corner, o.max_j
    )
}

fn arc(m: Model) -> std::sync::Arc<Model> {
    std::sync::Arc::new(m)
}

fn write_jac(model: &Model, y: &[f64], path: &str) {
    let d = 1e-6;
    let mut f = std::io::BufWriter::new(fs::File::create(path).unwrap());
    for c in 0..NY {
        let mut yp = y.to_vec();
        let mut ym = y.to_vec();
        yp[c] += d;
        ym[c] -= d;
        let fp = model.rhs_vec(&yp);
        let fm = model.rhs_vec(&ym);
        for r in 0..NY {
            // column-major: column c, rows r
            f.write_all(&((fp[r] - fm[r]) / (2.0 * d)).to_le_bytes()).unwrap();
        }
    }
}

fn mode_a(out: &str, bug: bool) {
    let mut lines = String::new();
    let mut par = Par::reg();
    if bug {
        par.r_psi = 2.0 * par.r;
    }
    let om = 0.5; // amendment A2: flow integrated in the frame rotating at the registered reference frequency
    for (label, p, n0, nr0) in [("above", 21.0, 10.0, 0.1), ("below", 16.0, 0.25, 0.0)] {
        if bug && label == "below" {
            continue;
        }
        if let Ok(c) = std::env::var("DD_CASE") {
            if c != label {
                continue;
            }
        }
        for seed in 1..=10u64 {
            let mut pp = par;
            pp.p = p;
            let m = arc(Model::new(pp, vec![0.0; NN], om));
            let y0 = state_uniform(n0, nr0, 1e-3, seed);
            let t0 = std::time::Instant::now();
            let f = flow(&m, &y0, 4000.0, 1e-10, 1e-12);
            let o = observe(&m, &f.y);
            let maxpsi = (0..NN).map(|i| (f.y[i] * f.y[i] + f.y[NN + i] * f.y[NN + i]).sqrt()).fold(0.0f64, f64::max);
            writeln!(
                lines,
                "{{\"gate\":\"D-a{}\",\"case\":\"{label}\",\"seed\":{seed},\"P\":{p},{},\"max_psi\":{:.6e},\"steps\":{},\"seconds\":{:.2},\"error\":{}}}",
                if bug { "-bug" } else { "" },
                obs_json(&o),
                maxpsi,
                f.steps,
                t0.elapsed().as_secs_f64(),
                jstr(&f.error)
            )
            .unwrap();
            eprintln!("{label} seed {seed}: n={:.8} nR={:.8} omega={:.8} budget={:.2e} err={:?}", o.mean_n, o.mean_nr, o.omega, o.budget_rel, f.error);
        }
    }
    let tag = std::env::var("DD_TAG").unwrap_or_default();
    fs::write(format!("{out}/{}{tag}.jsonl", if bug { "g" } else { "a" }), lines).unwrap();
}

fn mode_b(out: &str) {
    let par = Par::reg();
    let m = Model::new(par, vec![0.0; NN], 0.5);
    let mut y = vec![0.0; NY];
    for i in 0..NN {
        y[i] = 10f64.sqrt();
        y[2 * NN + i] = 0.1;
    }
    let f0 = m.rhs_vec(&y);
    let r = f0.iter().fold(0.0f64, |a, b| a.max(b.abs()));
    eprintln!("max|rhs| at exact uniform state, rotating frame: {r:.3e}");
    write_jac(&m, &y, &format!("{out}/jac_uniform.f64"));
    fs::write(format!("{out}/b.json"), format!("{{\"gate\":\"D-b\",\"max_abs_rhs_exact_state\":{r:.6e},\"n\":{NY},\"layout\":\"column-major f64 LE\"}}")).unwrap();
}

fn mode_c(out: &str) {
    let mut par = Par::reg();
    par.gamma = 0.0;
    par.r = 0.0;
    par.r_psi = 0.0;
    par.p = 0.0;
    let m = arc(Model::new(par, gate(0.5, SIGMA), 0.0));
    let y0 = state_uniform(10.0, 0.0, 1e-2, 1);
    let mut y0 = y0;
    for i in 0..NN {
        y0[2 * NN + i] = 0.0;
    }
    let energy = |y: &[f64]| -> (f64, f64) {
        let (re, rest) = y.split_at(NN);
        let (im, _) = rest.split_at(NN);
        let (kr, ki) = m.kin(re, im);
        let mut e = 0.0;
        let mut nrm = 0.0;
        for i in 0..NN {
            let n = re[i] * re[i] + im[i] * im[i];
            e += re[i] * kr[i] + im[i] * ki[i] + 0.5 * par.g * n * n + m.v[i] * n;
            nrm += n;
        }
        (nrm, e)
    };
    let (n0, e0) = energy(&y0);
    let f = flow(&m, &y0, 20.0, 1e-11, 1e-13);
    let (n1, e1) = energy(&f.y);
    let line = format!(
        "{{\"gate\":\"D-c\",\"norm0\":{n0:.17e},\"norm1\":{n1:.17e},\"energy0\":{e0:.17e},\"energy1\":{e1:.17e},\"norm_rel\":{:.6e},\"energy_rel\":{:.6e},\"steps\":{},\"error\":{}}}",
        (n1 - n0).abs() / n0,
        (e1 - e0).abs() / e0.abs(),
        f.steps,
        jstr(&f.error)
    );
    eprintln!("{line}");
    fs::write(format!("{out}/c.json"), line).unwrap();
}

fn mode_d(out: &str) {
    let mut lines = String::new();
    for v0 in [0.0, 0.25, 0.5, 1.0] {
        if let Ok(v) = std::env::var("DD_V0") {
            if (v.parse::<f64>().unwrap() - v0).abs() > 1e-9 {
                continue;
            }
        }
        for seed in 1..=10u64 {
            let m = arc(Model::new(Par::reg(), gate(v0, SIGMA), 0.5)); // amendment A2: rotating frame
            let y0 = state_uniform(10.0, 0.1, 1e-3, seed);
            let t0 = std::time::Instant::now();
            let f = flow(&m, &y0, 4000.0, 1e-10, 1e-12);
            let o = observe(&m, &f.y);
            writeln!(lines, "{{\"gate\":\"D-d\",\"V0\":{v0},\"seed\":{seed},{},\"steps\":{},\"seconds\":{:.2},\"error\":{}}}", obs_json(&o), f.steps, t0.elapsed().as_secs_f64(), jstr(&f.error)).unwrap();
            eprintln!("V0={v0} seed {seed}: omega={:.8} nc={:.5} resid={:.2e} budget={:.2e} err={:?}", o.omega, o.n_center, o.resid, o.budget_rel, f.error);
            if seed == 1 {
                // rotating-frame Jacobian about the numerical steady state
                let mr = Model::new(Par::reg(), gate(v0, SIGMA), o.omega);
                write_jac(&mr, &f.y, &format!("{out}/jac_V{}.f64", (v0 * 100.0).round() as i32));
            }
        }
    }
    let tag = std::env::var("DD_TAG").unwrap_or_default();
    fs::write(format!("{out}/d{tag}.jsonl"), lines).unwrap();
}

/// one IMEX step sequence; returns Err(message) if a step fails, or the final state
fn imex_run(par: Par, v0: f64, y0: &[f64], h: f64, t_end: f64) -> Result<Vec<f64>, String> {
    let m = Model::new(par, gate(v0, SIGMA), 0.5);
    let fe = |_t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
        m.rhs(y, yd, false);
        Ok(())
    };
    let gr = par.gamma_r;
    let fi = move |_t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
        for v in yd.iter_mut().take(2 * NN) {
            *v = 0.0;
        }
        for i in 0..NN {
            yd[2 * NN + i] = -gr * y[2 * NN + i];
        }
        Ok(())
    };
    let solver = ImexSolver::new(ImexTableau::ars222(), fe, fi, NY).tolerances(1e-6, 1e-6);
    let mut y = y0.to_vec();
    let mut yn = vec![0.0; NY];
    let nsteps = (t_end / h).round() as usize;
    for s in 0..nsteps {
        solver.step(s as f64 * h, &y, h, &mut yn)?;
        y.copy_from_slice(&yn);
    }
    Ok(y)
}

fn max_norm_diff_rel(a: &[f64], b: &[f64]) -> f64 {
    let d = a.iter().zip(b).map(|(x, y)| (x - y).abs()).fold(0.0f64, f64::max);
    let nb = b.iter().map(|x| x * x).sum::<f64>().sqrt();
    d / nb
}

fn mode_e(out: &str) {
    let par = Par::reg();
    let y0 = state_uniform(10.0, 0.1, 1e-3, 1);
    let mut lines = String::new();
    for h in [0.005, 0.01, 0.0125, 0.02, 0.05] {
        let r = imex_run(par, 0.5, &y0, h, h);
        let (status, finite) = match &r {
            Ok(y) => ("ok", y.iter().all(|v| v.is_finite())),
            Err(_) => ("error", true),
        };
        writeln!(lines, "{{\"gate\":\"D-e\",\"kind\":\"one_step\",\"h\":{h},\"status\":\"{status}\",\"finite\":{finite},\"message\":{}}}", jstr(&r.as_ref().err().cloned())).unwrap();
        eprintln!("h={h}: {status} finite={finite}");
    }
    // trajectory to t = 20 with h = 0.01 vs CVODE
    let mrot = arc(Model::new(par, gate(0.5, SIGMA), 0.5));
    let reference = flow(&mrot, &y0, 20.0, 1e-12, 1e-14);
    let traj = imex_run(par, 0.5, &y0, 0.01, 20.0);
    match traj {
        Ok(y) => {
            let d = max_norm_diff_rel(&y, &reference.y);
            writeln!(lines, "{{\"gate\":\"D-e\",\"kind\":\"trajectory\",\"h\":0.01,\"t\":20,\"diff_rel\":{d:.6e},\"finite\":{},\"cvode_error\":{}}}", y.iter().all(|v| v.is_finite()), jstr(&reference.error)).unwrap();
            eprintln!("trajectory diff {d:.3e}");
        }
        Err(e) => {
            writeln!(lines, "{{\"gate\":\"D-e\",\"kind\":\"trajectory\",\"h\":0.01,\"status\":\"error\",\"message\":{}}}", jstr(&Some(e))).unwrap();
        }
    }
    fs::write(format!("{out}/e.jsonl"), lines).unwrap();
}

fn mode_f(out: &str) {
    let mut par = Par::reg();
    par.gamma_r = 2.0;
    par.p = 0.2;
    let y0 = state_uniform(10.0, 0.1, 1e-3, 1);
    let mrot = arc(Model::new(par, gate(0.5, SIGMA), 0.5));
    let reference = flow(&mrot, &y0, 2.0, 1e-12, 1e-14);
    let mut errs = Vec::new();
    let mut lines = String::new();
    for h in [0.04, 0.02, 0.01] {
        match imex_run(par, 0.5, &y0, h, 2.0) {
            Ok(y) => {
                let d = max_norm_diff_rel(&y, &reference.y);
                errs.push(d);
                writeln!(lines, "{{\"gate\":\"D-f\",\"h\":{h},\"err\":{d:.6e}}}").unwrap();
                eprintln!("h={h} err={d:.3e}");
            }
            Err(e) => {
                writeln!(lines, "{{\"gate\":\"D-f\",\"h\":{h},\"error\":{}}}", jstr(&Some(e))).unwrap();
            }
        }
    }
    fs::write(format!("{out}/f.jsonl"), lines).unwrap();
}

/// Visualisation dump (not a gate): fields of seed 1 at several times, V0 in {0, 0.5, 1.0}; rotating frame 0.5.
fn mode_v(out: &str) {
    for v0 in [0.0, 0.5, 1.0] {
        let m = arc(Model::new(Par::reg(), gate(v0, SIGMA), 0.5));
        let mut y = state_uniform(10.0, 0.1, 1e-3, 1);
        let mut t_prev = 0.0;
        for t in [0.0, 10.0, 40.0, 150.0, 600.0, 4000.0] {
            if t > t_prev {
                let f = flow(&m, &y, t - t_prev, 1e-10, 1e-12);
                y = f.y;
            }
            t_prev = t;
            let mut fh = std::io::BufWriter::new(fs::File::create(format!("{out}/field_V{}_t{}.f64", (v0 * 100.0).round() as i32, t as i32)).unwrap());
            for v in &y {
                fh.write_all(&v.to_le_bytes()).unwrap();
            }
            eprintln!("V0={v0} t={t} done");
        }
    }
}

/// Equivalence of the FFT path and the original naive DFT path; timing of one right-hand side.
fn mode_t(out: &str) {
    let m = Model::new(Par::reg(), gate(0.5, SIGMA), 0.5);
    let y = state_uniform(10.0, 0.1, 1e-1, 7);
    let (re, rest) = y.split_at(NN);
    let (im, _) = rest.split_at(NN);
    let (a, b) = m.kin(re, im);
    let (c, d) = m.kin_naive(re, im);
    let diff = (0..NN).map(|i| (a[i] - c[i]).abs().max((b[i] - d[i]).abs())).fold(0.0f64, f64::max);
    let t0 = std::time::Instant::now();
    let mut acc = 0.0;
    for _ in 0..2000 {
        let f = m.rhs_vec(&y);
        acc += f[0];
    }
    let us = t0.elapsed().as_secs_f64() / 2000.0 * 1e6;
    let line = format!("{{\"gate\":\"fft_equivalence\",\"max_abs_diff\":{diff:.3e},\"rhs_microseconds\":{us:.1},\"acc\":{acc:.3e}}}");
    eprintln!("{line}");
    fs::write(format!("{out}/fft_equivalence.json"), line).unwrap();
    for (rtol, atol) in [(1e-10, 1e-12), (1e-8, 1e-10)] {
        let mm = arc(Model::new(Par::reg(), gate(0.5, SIGMA), 0.5));
        let t1 = std::time::Instant::now();
        let f = flow(&mm, &state_uniform(10.0, 0.1, 1e-3, 1), 20.0, rtol, atol);
        eprintln!("flow t=20 rtol={rtol:e}: steps={} seconds={:.2} error={:?}", f.steps, t1.elapsed().as_secs_f64(), f.error);
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let (mode, out) = (args[1].as_str(), args[2].as_str());
    fs::create_dir_all(out).ok();
    match mode {
        "a" => mode_a(out, false),
        "b" => mode_b(out),
        "c" => mode_c(out),
        "d" => mode_d(out),
        "e" => mode_e(out),
        "f" => mode_f(out),
        "g" => mode_a(out, true),
        "v" => mode_v(out),
        "t" => mode_t(out),
        _ => panic!("mode"),
    }
}
