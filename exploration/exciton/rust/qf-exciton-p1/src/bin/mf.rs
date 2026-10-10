//! Phase 2 (docs/designs/EXCITON_FLUID_PHASE2_PREREG.md): mean-field Gross-Pitaevskii with a nonlocal kernel on a
//! 16x16 periodic grid, rusty-SUNDIALS CVODE for the imaginary-time flows, and the solver's own linearisation of the
//! real-time right-hand side for the Bogoliubov frequencies.
//!
//!     mf <out_dir>
use cvode::{Cvode, Method, Task};
use nvector::SerialVector;
use qf_exciton_p1::rng::SplitMix64;
use std::f64::consts::PI;
use std::fmt::Write as _;
use std::fs;
use std::sync::Arc;

const M: usize = 16;
const NN: usize = M * M;
const L: f64 = 16.0;
const MU: f64 = 0.25;
const DD: f64 = 1.0;

#[derive(Clone, Copy, PartialEq)]
enum Kern {
    B,
    C,
    BBug,
}

fn mfreq(i: usize) -> i32 {
    if i > M / 2 {
        i as i32 - M as i32
    } else {
        i as i32
    }
}

fn u_of_k(kern: Kern, k: f64) -> f64 {
    let k0 = 2.0 * PI * 3.0 / L;
    let b = if k > 0.0 { 4.0 * PI * (1.0 - (-k * DD).exp()) / k } else { 4.0 * PI * DD };
    match kern {
        Kern::B => b,
        Kern::C => b - 28.0 * (-(k - k0) * (k - k0) / (2.0 * 0.2 * 0.2)).exp(),
        Kern::BBug => {
            if k > 0.0 {
                b
            } else {
                2.0 * b
            }
        }
    }
}

struct Setup {
    u: Vec<f64>,  // U(k) at grid index ix*M+iy
    k2: Vec<f64>, // k^2
    tc: Vec<f64>, // cos(2 pi j m / M), index j*M+m
    ts: Vec<f64>,
}

impl Setup {
    fn new(kern: Kern) -> Self {
        let mut u = vec![0.0; NN];
        let mut k2 = vec![0.0; NN];
        for i in 0..M {
            for j in 0..M {
                let kx = 2.0 * PI * mfreq(i) as f64 / L;
                let ky = 2.0 * PI * mfreq(j) as f64 / L;
                let k = (kx * kx + ky * ky).sqrt();
                u[i * M + j] = u_of_k(kern, k);
                k2[i * M + j] = k * k;
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
        Setup { u, k2, tc, ts }
    }

    /// 2D DFT of (re, im); forward `e^{-i...}`, inverse `e^{+i...}` with the `1/M²` normalisation.
    fn dft2(&self, re: &[f64], im: &[f64], inverse: bool) -> (Vec<f64>, Vec<f64>) {
        let sgn = if inverse { 1.0 } else { -1.0 };
        let mut tr = vec![0.0; NN];
        let mut ti = vec![0.0; NN];
        // along y (second index)
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
            for v in or.iter_mut() {
                *v *= f;
            }
            for v in oi.iter_mut() {
                *v *= f;
            }
        }
        (or, oi)
    }

    /// `H ψ = (-½∇² + U∗|ψ|² − μ) ψ` for complex `ψ = re + i im`.
    fn h_psi(&self, re: &[f64], im: &[f64]) -> (Vec<f64>, Vec<f64>) {
        let n: Vec<f64> = (0..NN).map(|i| re[i] * re[i] + im[i] * im[i]).collect();
        let zero = vec![0.0; NN];
        let (nr, ni) = self.dft2(&n, &zero, false);
        let ur: Vec<f64> = (0..NN).map(|i| self.u[i] * nr[i]).collect();
        let ui: Vec<f64> = (0..NN).map(|i| self.u[i] * ni[i]).collect();
        let (v, _) = self.dft2(&ur, &ui, true);
        let (pr, pi) = self.dft2(re, im, false);
        let tr: Vec<f64> = (0..NN).map(|i| 0.5 * self.k2[i] * pr[i]).collect();
        let ti: Vec<f64> = (0..NN).map(|i| 0.5 * self.k2[i] * pi[i]).collect();
        let (kr, ki) = self.dft2(&tr, &ti, true);
        let hr: Vec<f64> = (0..NN).map(|i| kr[i] + (v[i] - MU) * re[i]).collect();
        let hi: Vec<f64> = (0..NN).map(|i| ki[i] + (v[i] - MU) * im[i]).collect();
        (hr, hi)
    }

    /// Grand-potential density of a real field.
    fn omega(&self, psi: &[f64]) -> f64 {
        let zero = vec![0.0; NN];
        let n: Vec<f64> = psi.iter().map(|p| p * p).collect();
        let (nr, ni) = self.dft2(&n, &zero, false);
        let ur: Vec<f64> = (0..NN).map(|i| self.u[i] * nr[i]).collect();
        let ui: Vec<f64> = (0..NN).map(|i| self.u[i] * ni[i]).collect();
        let (v, _) = self.dft2(&ur, &ui, true);
        let (pr, pi) = self.dft2(psi, &zero, false);
        let tr: Vec<f64> = (0..NN).map(|i| 0.5 * self.k2[i] * pr[i]).collect();
        let ti: Vec<f64> = (0..NN).map(|i| 0.5 * self.k2[i] * pi[i]).collect();
        let (kr, _) = self.dft2(&tr, &ti, true);
        let mut e = 0.0;
        for i in 0..NN {
            e += psi[i] * kr[i] + 0.5 * n[i] * v[i] - MU * n[i];
        }
        e / NN as f64
    }
}

struct FlowOut {
    psi: Vec<f64>,
    converged: bool,
    tau: f64,
    steps: usize,
    error: Option<String>,
}

fn flow_imag(setup: &Arc<Setup>, psi0: &[f64], tau_max: f64) -> FlowOut {
    flow_imag_tol(setup, psi0, tau_max, 1e-12, 1e-14, 1e-12)
}

fn flow_imag_tol(setup: &Arc<Setup>, psi0: &[f64], tau_max: f64, rtol: f64, atol: f64, rate_tol: f64) -> FlowOut {
    let s = Arc::clone(setup);
    let rhs = move |_t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
        let zero = vec![0.0; NN];
        let (hr, _) = s.h_psi(y, &zero);
        for i in 0..NN {
            yd[i] = -hr[i];
        }
        Ok(())
    };
    let mut solver = match Cvode::builder(Method::Bdf)
        .rtol(rtol)
        .atol(atol)
        .max_steps(2_000_000)
        .build(rhs, 0.0, SerialVector::from_slice(psi0))
    {
        Ok(s) => s,
        Err(e) => {
            return FlowOut { psi: psi0.to_vec(), converged: false, tau: 0.0, steps: 0, error: Some(format!("build: {e:?}")) }
        }
    };
    let mut tau = 0.0;
    let mut psi = psi0.to_vec();
    while tau < tau_max {
        tau += 100.0;
        match solver.solve(tau, Task::Normal) {
            Ok((_, y)) => psi = y.to_vec(),
            Err(e) => {
                return FlowOut { psi, converged: false, tau, steps: solver.num_steps(), error: Some(format!("solve at tau={tau}: {e:?}")) }
            }
        }
        let zero = vec![0.0; NN];
        let (hr, _) = setup.h_psi(&psi, &zero);
        let rate = (0..NN).map(|i| (hr[i]).abs()).fold(0.0f64, f64::max);
        if rate < rate_tol {
            return FlowOut { psi, converged: true, tau, steps: solver.num_steps(), error: None };
        }
    }
    FlowOut { psi, converged: false, tau, steps: solver.num_steps(), error: Some("tau_max reached".into()) }
}

fn json_str(s: &Option<String>) -> String {
    match s {
        Some(m) => format!("\"{}\"", m.replace('\\', "\\\\").replace('"', "'")),
        None => "null".into(),
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let out = &args[1];
    fs::create_dir_all(out).ok();
    // Amendment A2 (docs/designs/EXCITON_FLUID_PHASE2_PREREG.md): repeat only the control flow of P2-c(ii) with relaxed
    // tolerances after the registered run failed with a CVODE convergence failure.
    if std::env::var("MF_MODE").as_deref() == Ok("ctrl_debug") {
        let rtol: f64 = std::env::var("MF_RTOL").ok().and_then(|v| v.parse().ok()).unwrap_or(1e-9);
        let atol: f64 = std::env::var("MF_ATOL").ok().and_then(|v| v.parse().ok()).unwrap_or(1e-11);
        let dtau: f64 = std::env::var("MF_DTAU").ok().and_then(|v| v.parse().ok()).unwrap_or(0.5);
        let setup_c = Arc::new(Setup::new(Kern::C));
        let n0_c = MU / u_of_k(Kern::C, 0.0);
        let mut rng = SplitMix64::new(777);
        let psi0: Vec<f64> = (0..NN).map(|_| n0_c.sqrt() * (1.0 + 1e-3 * rng.normal())).collect();
        let s = Arc::clone(&setup_c);
        let rhs = move |_t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
            let zero = vec![0.0; NN];
            let (hr, _) = s.h_psi(y, &zero);
            for i in 0..NN {
                yd[i] = -hr[i];
            }
            Ok(())
        };
        let mut solver = Cvode::builder(Method::Bdf)
            .rtol(rtol)
            .atol(atol)
            .max_steps(2_000_000)
            .build(rhs, 0.0, SerialVector::from_slice(&psi0))
            .expect("build");
        let mut tau = 0.0;
        for k in 0..400 {
            tau += dtau;
            match solver.solve(tau, Task::Normal) {
                Ok((_, y)) => {
                    let psi = y.to_vec();
                    let nbar = psi.iter().map(|p| p * p).sum::<f64>() / NN as f64;
                    let nmod = psi.iter().map(|p| (p * p - nbar).abs() / nbar).fold(0.0f64, f64::max);
                    let zero = vec![0.0; NN];
                    let (hr, _) = setup_c.h_psi(&psi, &zero);
                    let rate = hr.iter().map(|v| v.abs()).fold(0.0f64, f64::max);
                    if k % 4 == 0 {
                        eprintln!("tau={tau:8.2} steps={} omega={:.10e} mod={nmod:.3e} max|Hpsi|={rate:.3e}", solver.num_steps(), setup_c.omega(&psi));
                    }
                }
                Err(e) => {
                    eprintln!("FAIL at tau target {tau}: {e:?} steps={}", solver.num_steps());
                    break;
                }
            }
        }
        return;
    }
    if std::env::var("MF_MODE").as_deref() == Ok("ctrl_A2") {
        let rtol: f64 = std::env::var("MF_RTOL").ok().and_then(|v| v.parse().ok()).unwrap_or(1e-9);
        let atol: f64 = std::env::var("MF_ATOL").ok().and_then(|v| v.parse().ok()).unwrap_or(1e-11);
        let rate: f64 = std::env::var("MF_RATE").ok().and_then(|v| v.parse().ok()).unwrap_or(1e-8);
        let setup_c = Arc::new(Setup::new(Kern::C));
        let n0_c = MU / u_of_k(Kern::C, 0.0);
        let mut rng = SplitMix64::new(777);
        let psi0: Vec<f64> = (0..NN).map(|_| n0_c.sqrt() * (1.0 + 1e-3 * rng.normal())).collect();
        let t0 = std::time::Instant::now();
        let f = flow_imag_tol(&setup_c, &psi0, 2.0e4, rtol, atol, rate);
        let nbar = f.psi.iter().map(|p| p * p).sum::<f64>() / NN as f64;
        let nmod = f.psi.iter().map(|p| (p * p - nbar).abs() / nbar).fold(0.0f64, f64::max);
        let om = setup_c.omega(&f.psi);
        let omega0_c = -MU * MU / (2.0 * u_of_k(Kern::C, 0.0));
        let rep = format!(
            "{{\"mode\":\"ctrl_A2\",\"rtol\":{rtol:e},\"atol\":{atol:e},\"rate_tol\":{rate:e},\"converged\":{},\"tau\":{},\"steps\":{},\"max_rel_modulation\":{nmod:e},\"omega\":{om:.12e},\"omega_uniform\":{omega0_c:.12e},\"rel_below\":{:e},\"wall_s\":{:.1},\"error\":{}}}\n",
            f.converged, f.tau, f.steps, (omega0_c - om) / omega0_c.abs(), t0.elapsed().as_secs_f64(), json_str(&f.error));
        fs::write(format!("{out}/mf_report_A2.json"), &rep).unwrap();
        // also dump the final density profile for inspection
        let dens: Vec<String> = f.psi.iter().map(|p| format!("{:.10e}", p * p)).collect();
        fs::write(format!("{out}/mf_ctrl_A2_density.txt"), dens.join("\n")).unwrap();
        println!("{rep}");
        return;
    }
    let mut rep = String::from("{\n");

    // reference numbers (same formulas as the numpy script)
    let u0_b = u_of_k(Kern::B, 0.0);
    let n0_b = MU / u0_b;
    let omega0 = -MU * MU / (2.0 * u0_b);
    writeln!(rep, " \"U0_B\":{u0_b:.16e},\"n0_B\":{n0_b:.16e},\"omega0\":{omega0:.16e},").unwrap();

    // ---- P2-a: uniform minimiser, kernel B
    let setup_b = Arc::new(Setup::new(Kern::B));
    let mut runs = Vec::new();
    for seed in 1..=50u64 {
        let mut rng = SplitMix64::new(seed);
        let psi0: Vec<f64> = (0..NN).map(|_| 0.05 + 0.35 * rng.uniform()).collect();
        let f = flow_imag(&setup_b, &psi0, 2.0e4);
        let nmax = f.psi.iter().map(|p| (p * p - n0_b).abs() / n0_b).fold(0.0f64, f64::max);
        let om = setup_b.omega(&f.psi);
        let om_rel = ((om - omega0) / omega0).abs();
        runs.push(format!(
            "{{\"seed\":{seed},\"converged\":{},\"tau\":{},\"steps\":{},\"max_rel_dev\":{nmax:e},\"omega_rel_err\":{om_rel:e},\"error\":{}}}",
            f.converged, f.tau, f.steps, json_str(&f.error)
        ));
        eprintln!("[P2a] seed {seed}: converged={} tau={} steps={} dev={nmax:.3e} omega_err={om_rel:.3e} err={:?}", f.converged, f.tau, f.steps, f.error);
    }
    writeln!(rep, " \"P2a\":[{}],", runs.join(",")).unwrap();

    // ---- P2-d: planted bug (U(0) doubled), 5 starts
    let setup_bug = Arc::new(Setup::new(Kern::BBug));
    let mut bug = Vec::new();
    for seed in 1..=5u64 {
        let mut rng = SplitMix64::new(seed);
        let psi0: Vec<f64> = (0..NN).map(|_| 0.05 + 0.35 * rng.uniform()).collect();
        let f = flow_imag(&setup_bug, &psi0, 2.0e4);
        let nmax = f.psi.iter().map(|p| (p * p - n0_b).abs() / n0_b).fold(0.0f64, f64::max);
        bug.push(format!("{{\"seed\":{seed},\"max_rel_dev\":{nmax:e},\"converged\":{},\"error\":{}}}", f.converged, json_str(&f.error)));
        eprintln!("[P2d] seed {seed}: dev={nmax:.3e} converged={}", f.converged);
    }
    writeln!(rep, " \"P2d\":[{}],", bug.join(",")).unwrap();

    // ---- P2-b / P2-c(i): the solver's linearisation of the real-time right-hand side about the uniform state
    for (name, kern) in [("B", Kern::B), ("C", Kern::C)] {
        let st = Setup::new(kern);
        let n0 = MU / u_of_k(kern, 0.0);
        let psi_amp = n0.sqrt();
        let eps = 1e-6;
        // real-time rhs: psi_dot = -i H psi
        let rt = |re: &[f64], im: &[f64]| -> (Vec<f64>, Vec<f64>) {
            let (hr, hi) = st.h_psi(re, im);
            let fre: Vec<f64> = hi.clone();
            let fim: Vec<f64> = hr.iter().map(|v| -v).collect();
            (fre, fim)
        };
        let mut rows = Vec::new();
        for i in 0..M {
            for j in 0..M {
                if i == 0 && j == 0 {
                    continue;
                }
                let kx = 2.0 * PI * mfreq(i) as f64 / L;
                let ky = 2.0 * PI * mfreq(j) as f64 / L;
                let cosv: Vec<f64> =
                    (0..NN).map(|idx| (kx * (idx / M) as f64 + ky * (idx % M) as f64).cos()).collect();
                let norm: f64 = cosv.iter().map(|c| c * c).sum();
                let mut mat = [[0.0f64; 2]; 2]; // d(a,b)/dt = mat * (a,b)
                for (col, (da, db)) in [(1.0, 0.0), (0.0, 1.0)].iter().enumerate() {
                    let plus_re: Vec<f64> = (0..NN).map(|x| psi_amp + eps * da * cosv[x]).collect();
                    let plus_im: Vec<f64> = (0..NN).map(|x| eps * db * cosv[x]).collect();
                    let minus_re: Vec<f64> = (0..NN).map(|x| psi_amp - eps * da * cosv[x]).collect();
                    let minus_im: Vec<f64> = (0..NN).map(|x| -eps * db * cosv[x]).collect();
                    let (fpr, fpi) = rt(&plus_re, &plus_im);
                    let (fmr, fmi) = rt(&minus_re, &minus_im);
                    let (mut pr, mut pi) = (0.0, 0.0);
                    for x in 0..NN {
                        pr += cosv[x] * (fpr[x] - fmr[x]) / (2.0 * eps);
                        pi += cosv[x] * (fpi[x] - fmi[x]) / (2.0 * eps);
                    }
                    mat[0][col] = pr / norm;
                    mat[1][col] = pi / norm;
                }
                rows.push(format!(
                    "{{\"i\":{},\"j\":{},\"M11\":{:.12e},\"M12\":{:.12e},\"M21\":{:.12e},\"M22\":{:.12e}}}",
                    mfreq(i), mfreq(j), mat[0][0], mat[0][1], mat[1][0], mat[1][1]
                ));
            }
        }
        writeln!(rep, " \"lin_{name}\":[{}],", rows.join(",")).unwrap();
    }

    // ---- P2-c(ii): control flow from the uniform state plus noise
    let setup_c = Arc::new(Setup::new(Kern::C));
    let n0_c = MU / u_of_k(Kern::C, 0.0);
    let mut rng = SplitMix64::new(777);
    let psi0: Vec<f64> = (0..NN).map(|_| n0_c.sqrt() * (1.0 + 1e-3 * rng.normal())).collect();
    let f = flow_imag(&setup_c, &psi0, 2.0e4);
    let nbar = f.psi.iter().map(|p| p * p).sum::<f64>() / NN as f64;
    let nmod = f.psi.iter().map(|p| (p * p - nbar).abs() / nbar).fold(0.0f64, f64::max);
    let om = setup_c.omega(&f.psi);
    let omega0_c = -MU * MU / (2.0 * u_of_k(Kern::C, 0.0));
    writeln!(rep, " \"P2c_flow\":{{\"converged\":{},\"tau\":{},\"max_rel_modulation\":{nmod:e},\"omega\":{om:.12e},\"omega_uniform\":{omega0_c:.12e},\"rel_below\":{:e},\"error\":{}}}",
        f.converged, f.tau, (omega0_c - om) / omega0_c.abs(), json_str(&f.error)).unwrap();
    eprintln!("[P2c] flow: converged={} modulation={nmod:.3e} omega={om:.6e} uniform={omega0_c:.6e} err={:?}", f.converged, f.error);
    rep.push_str("}\n");
    fs::write(format!("{out}/mf_report.json"), &rep).unwrap();
    println!("written {out}/mf_report.json ({} bytes)", rep.len());
}
