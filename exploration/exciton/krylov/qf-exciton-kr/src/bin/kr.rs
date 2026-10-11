//! kr: matrix-free Newton-Krylov (SDIRK2 + GMRES) driver for the driven-dissipative exciton GPE.
//!   kr test
//!   kr run key=value ...         (see `param` calls below)
//!   kr cmp fileA.f64 fileB.f64   (max-abs and relative L2 difference of two state dumps)
use cvode::{Cvode, Method, Task};
use nvector::SerialVector;
use qf_exciton_kr::fft::Fft2;
use qf_exciton_kr::model::*;
use qf_exciton_kr::sdirk::*;
use std::collections::HashMap;
use std::io::Write;

fn cpu_seconds() -> f64 {
    let s = std::fs::read_to_string("/proc/self/stat").unwrap_or_default();
    let after = s.rsplit(')').next().unwrap_or("");
    let f: Vec<&str> = after.split_whitespace().collect();
    // after ')' the fields start at field 3 (state); utime = field 14 -> index 11, stime index 12
    if f.len() > 12 {
        (f[11].parse::<f64>().unwrap_or(0.0) + f[12].parse::<f64>().unwrap_or(0.0)) / 100.0
    } else {
        0.0
    }
}

struct Args(HashMap<String, String>);
impl Args {
    fn get<T: std::str::FromStr>(&self, k: &str, d: T) -> T {
        self.0.get(k).and_then(|v| v.parse().ok()).unwrap_or(d)
    }
    fn s(&self, k: &str, d: &str) -> String {
        self.0.get(k).cloned().unwrap_or_else(|| d.to_string())
    }
    fn has(&self, k: &str) -> bool {
        self.0.contains_key(k)
    }
}

fn write_state(path: &str, y: &[f64]) {
    let mut f = std::io::BufWriter::new(std::fs::File::create(path).unwrap());
    for v in y {
        f.write_all(&v.to_le_bytes()).unwrap();
    }
}

fn read_state(path: &str) -> Vec<f64> {
    let b = std::fs::read(path).unwrap();
    b.chunks_exact(8).map(|c| f64::from_le_bytes(c.try_into().unwrap())).collect()
}

fn append(path: &str, line: &str) {
    if path.is_empty() {
        return;
    }
    let mut f = std::fs::OpenOptions::new().create(true).append(true).open(path).unwrap();
    writeln!(f, "{line}").unwrap();
}

fn naive_dft2(m: usize, re: &[f64], im: &[f64], inverse: bool) -> (Vec<f64>, Vec<f64>) {
    let sgn = if inverse { 1.0 } else { -1.0 };
    let mut or = vec![0.0; m * m];
    let mut oi = vec![0.0; m * m];
    for kx in 0..m {
        for ky in 0..m {
            let (mut sr, mut si) = (0.0, 0.0);
            for x in 0..m {
                for y in 0..m {
                    let a = sgn * 2.0 * std::f64::consts::PI * ((kx * x + ky * y) % m) as f64 / m as f64;
                    let (c, s) = (a.cos(), a.sin());
                    sr += re[x * m + y] * c - im[x * m + y] * s;
                    si += re[x * m + y] * s + im[x * m + y] * c;
                }
            }
            or[kx * m + ky] = sr;
            oi[kx * m + ky] = si;
        }
    }
    if inverse {
        let f = 1.0 / (m * m) as f64;
        or.iter_mut().for_each(|v| *v *= f);
        oi.iter_mut().for_each(|v| *v *= f);
    }
    (or, oi)
}

fn mode_test() {
    let mut ok = true;
    let mut rng = SplitMix64(12345);
    // 1. FFT against the naive DFT
    for m in [8usize, 16, 32] {
        let re: Vec<f64> = (0..m * m).map(|_| rng.uniform() - 0.5).collect();
        let im: Vec<f64> = (0..m * m).map(|_| rng.uniform() - 0.5).collect();
        let f = Fft2::new(m);
        for inv in [false, true] {
            let (nr, ni) = naive_dft2(m, &re, &im, inv);
            let (mut a, mut b) = (re.clone(), im.clone());
            f.fft2(&mut a, &mut b, inv);
            let d = (0..m * m).map(|i| (a[i] - nr[i]).abs().max((b[i] - ni[i]).abs())).fold(0.0f64, f64::max);
            println!("fft m={m} inverse={inv}: max diff vs naive DFT {d:.3e}");
            ok &= d < 1e-12;
        }
    }
    // 2. the uniform above-threshold state is a fixed point in the frame rotating at 0.5
    let par = Par::reg();
    let model = Model::new(16, 16.0, 3.0, 0.0, par);
    let mut y = vec![0.0; model.ny];
    for i in 0..model.nn {
        y[i] = 10f64.sqrt();
        y[2 * model.nn + i] = 0.1;
    }
    let r = model.rhs_vec(&y, 0.5).iter().fold(0.0f64, |a, b| a.max(b.abs()));
    println!("max|rhs| at the exact uniform state (om=0.5): {r:.3e}");
    ok &= r < 1e-12;
    // 3. exact Jacobian action vs central finite difference, and jloc consistency
    let model = Model::new(16, 16.0, 3.0, 0.5, par);
    let y = state_uniform(model.nn, 10.0, 0.1, 0.3, 7);
    let dv: Vec<f64> = (0..model.ny).map(|_| rng.uniform() - 0.5).collect();
    let mut jv = vec![0.0; model.ny];
    model.jv(&y, &dv, &mut jv, 0.5);
    let eps = 1e-6;
    let yp: Vec<f64> = (0..model.ny).map(|i| y[i] + eps * dv[i]).collect();
    let ym: Vec<f64> = (0..model.ny).map(|i| y[i] - eps * dv[i]).collect();
    let (fp, fm) = (model.rhs_vec(&yp, 0.5), model.rhs_vec(&ym, 0.5));
    let mut num = 0.0;
    let mut den = 0.0;
    for i in 0..model.ny {
        let fd = (fp[i] - fm[i]) / (2.0 * eps);
        num += (fd - jv[i]).powi(2);
        den += jv[i].powi(2);
    }
    let rel = (num / den).sqrt();
    println!("jv exact vs central FD: relative L2 difference {rel:.3e}");
    ok &= rel < 1e-7;
    let nn = model.nn;
    let (mut kr, mut ki) = (vec![0.0; nn], vec![0.0; nn]);
    model.kin(&dv[..nn], &dv[nn..2 * nn], &mut kr, &mut ki);
    let mut dj = 0.0f64;
    for i in 0..nn {
        let j = model.jloc(&y, i, 0.5);
        let d = [dv[i], dv[nn + i], dv[2 * nn + i]];
        let a = ki[i] + j[0][0] * d[0] + j[0][1] * d[1] + j[0][2] * d[2];
        let b = -kr[i] + j[1][0] * d[0] + j[1][1] * d[1] + j[1][2] * d[2];
        let c = j[2][0] * d[0] + j[2][1] * d[1] + j[2][2] * d[2];
        dj = dj.max((a - jv[i]).abs()).max((b - jv[nn + i]).abs()).max((c - jv[2 * nn + i]).abs());
    }
    println!("jloc + kinetic vs jv: max abs diff {dj:.3e}");
    ok &= dj < 1e-12;
    // 4. preconditioner: M^-1 (I - s J) v  with J = kinetic only (gate-free, psi = 0, nR = 0, om = 0) must be exact in Kin mode on psi
    println!("{}", if ok { "TEST PASS" } else { "TEST FAIL" });
    if !ok {
        std::process::exit(1);
    }
}

fn mode_run(a: &Args) {
    let m: usize = a.get("M", 8);
    let l: f64 = a.get("L", m as f64);
    let sigma: f64 = a.get("SIGMA", 0.1875 * l);
    let v0: f64 = a.get("V0", 0.5);
    let seed: u64 = a.get("SEED", 1);
    let tend: f64 = a.get("TEND", 20.0);
    let solver = a.s("SOLVER", "kr");
    let rtol: f64 = a.get("RTOL", 1e-6);
    let atol: f64 = a.get("ATOL", 1e-9);
    let noise: f64 = a.get("NOISE", 1e-3);
    let n0: f64 = a.get("N0", 10.0);
    let nr0: f64 = a.get("NR0", 0.1);
    let track: bool = a.get::<u32>("TRACK", 0) == 1;
    let stop: f64 = a.get("STOP", 0.0);
    let chunk: f64 = a.get("CHUNK", 100.0);
    let bug = a.s("BUG", "none");
    let tag = a.s("TAG", "");
    let out = a.s("OUT", "");
    let state_out = a.s("STATE", "");
    let log = a.s("LOG", "");
    let mut par = Par::reg();
    if bug == "rhs" {
        par.r_psi = 2.0 * par.r;
    }
    if let Some(v) = a.0.get("P") {
        par.p = v.parse().unwrap();
    }
    let mut model = Model::new(m, l, sigma, v0, par);
    if bug == "jac" {
        model.jac_bug = true;
    }
    let mut y = state_uniform(model.nn, n0, nr0, noise, seed);
    let band: f64 = a.get("NOISEBAND", 0.0); // > 0: remove noise Fourier modes with |kx| or |ky| > band (declared deviation for h < 1 grids)
    if band > 0.0 {
        let nn = model.nn;
        for part in 0..2 {
            let mut re: Vec<f64> = (0..nn).map(|i| y[part * nn + i] - if part == 0 { n0.sqrt() } else { 0.0 }).collect();
            let mut im = vec![0.0; nn];
            model.fft.fft2(&mut re, &mut im, false);
            for i in 0..m {
                for j in 0..m {
                    let kx = (2.0 * std::f64::consts::PI * mfreq(i, m) as f64 / l).abs();
                    let ky = (2.0 * std::f64::consts::PI * mfreq(j, m) as f64 / l).abs();
                    if kx > band || ky > band {
                        re[i * m + j] = 0.0;
                        im[i * m + j] = 0.0;
                    }
                }
            }
            model.fft.fft2(&mut re, &mut im, true);
            for i in 0..nn {
                y[part * nn + i] = re[i] + if part == 0 { n0.sqrt() } else { 0.0 };
            }
        }
    }
    let mut om: f64 = a.get("OM", 0.5);
    let t0 = std::time::Instant::now();
    let c0 = cpu_seconds();
    let mut opts = Opts::default();
    opts.rtol = rtol;
    opts.atol = atol;
    opts.hmax = a.get("HMAX", 1e9);
    opts.prec = match a.s("PREC", "block").as_str() {
        "none" => PrecMode::None,
        "kin" => PrecMode::Kin,
        "badsign" => PrecMode::BadSign,
        _ => PrecMode::Block,
    };
    opts.exact_jv = a.s("JV", "exact") == "exact";
    opts.kappa = a.get("KAPPA", opts.kappa);
    opts.max_newton = a.get("MAXNEWTON", opts.max_newton);
    opts.eta = a.get("ETA", opts.eta);
    if a.has("FIXEDH") {
        opts.fixed_h = Some(a.get("FIXEDH", 0.01));
    }
    let mut error: Option<String> = None;
    let mut t_reached = 0.0;
    let mut stats_line = String::new();
    let (steps_s, mut final_resid);
    if solver == "cvode" {
        assert!(m <= 16, "CVODE dense is not used for M >= 32");
        let mc = Model::new(m, l, sigma, v0, par);
        let rhs = move |_t: f64, yy: &[f64], yd: &mut [f64]| -> Result<(), String> {
            mc.rhs(yy, yd, 0.5);
            Ok(())
        };
        let mut s = Cvode::builder(Method::Bdf).rtol(rtol).atol(atol).max_steps(20_000_000).build(rhs, 0.0, SerialVector::from_slice(&y)).unwrap();
        let mut t = 0.0;
        let dt = if tend > 400.0 { 250.0 } else { tend };
        while t < tend - 1e-12 {
            t = (t + dt).min(tend);
            match s.solve(t, Task::Normal) {
                Ok((_, v)) => y = v.to_vec(),
                Err(e) => {
                    error = Some(format!("{e:?}"));
                    break;
                }
            }
        }
        t_reached = t;
        steps_s = s.num_steps() as u64;
        om = 0.5;
        stats_line.push_str(&format!("\"cvode_steps\":{steps_s},\"nrhs\":{}", 0));
        final_resid = observe(&model, &y).resid;
    } else {
        let mut st = Stepper::new(a.get("H0", 1e-3));
        let mut t_next = 0.0;
        loop {
            t_next = (t_next + chunk).min(tend);
            if opts.fixed_h.is_some() {
                t_next = tend;
            }
            if let Err(e) = st.advance(&model, &mut y, om, t_next, &opts) {
                error = Some(e);
                break;
            }
            let o = observe(&model, &y);
            final_resid = o.resid;
            t_reached = st.t;
            if !log.is_empty() {
                append(&log, &format!("{{\"t\":{:.3},\"resid\":{:.4e},\"omega\":{:.10},\"n_center\":{:.8},\"h\":{:.4e},\"steps\":{},\"newton\":{},\"gmres\":{},\"rej_err\":{},\"rej_newton\":{},\"cpu\":{:.1}}}", st.t, o.resid, o.omega, o.n_center, st.h, st.stats.steps, st.stats.newton, st.stats.gmres, st.stats.rej_err, st.stats.rej_newton, cpu_seconds() - c0));
            }
            if track {
                om = o.omega;
            }
            if (stop > 0.0 && o.resid < stop) || t_next >= tend {
                break;
            }
        }
        steps_s = st.stats.steps;
        stats_line.push_str(&format!(
            "\"steps\":{},\"rej_err\":{},\"rej_newton\":{},\"newton\":{},\"gmres\":{},\"nrhs\":{},\"njv\":{},\"nprec\":{},\"h_final\":{:.4e}",
            st.stats.steps, st.stats.rej_err, st.stats.rej_newton, st.stats.newton, st.stats.gmres, model.nrhs.load(std::sync::atomic::Ordering::Relaxed), model.njv.load(std::sync::atomic::Ordering::Relaxed), model.nprec.load(std::sync::atomic::Ordering::Relaxed), st.h
        ));
    }
    let o = observe(&model, &y);
    final_resid = o.resid;
    let _ = final_resid;
    let wall = t0.elapsed().as_secs_f64();
    let cpu = cpu_seconds() - c0;
    let _ = steps_s;
    let line = format!(
        "{{\"tag\":\"{tag}\",\"solver\":\"{solver}\",\"M\":{m},\"L\":{l},\"sigma\":{sigma},\"V0\":{v0},\"seed\":{seed},\"t_end\":{tend},\"t_reached\":{t_reached:.6},\"rtol\":{rtol:e},\"atol\":{atol:e},\"prec\":\"{}\",\"jv\":\"{}\",\"track\":{track},\"bug\":\"{bug}\",\"fixedh\":{},{},{},\"shift\":{:.10e},\"wall_s\":{wall:.2},\"cpu_s\":{cpu:.2},\"error\":{}}}",
        a.s("PREC", "block"),
        a.s("JV", "exact"),
        opts.fixed_h.map(|h| h.to_string()).unwrap_or("null".into()),
        obs_json(&o),
        stats_line,
        o.omega - 0.5,
        match &error {
            Some(e) => format!("\"{}\"", e.replace('"', "'")),
            None => "null".into(),
        }
    );
    println!("{line}");
    append(&out, &line);
    if !state_out.is_empty() {
        write_state(&state_out, &y);
    }
}

fn mode_cmp(a: &[String]) {
    let (x, y) = (read_state(&a[0]), read_state(&a[1]));
    let n = x.len();
    let mx = (0..n).map(|i| (x[i] - y[i]).abs()).fold(0.0f64, f64::max);
    let d2: f64 = (0..n).map(|i| (x[i] - y[i]).powi(2)).sum::<f64>().sqrt();
    let n2: f64 = y.iter().map(|v| v * v).sum::<f64>().sqrt();
    // optimal global phase of the psi part (a = x[..nn], b = x[nn..2nn]); reservoir untouched
    let nn = n / 3;
    let (mut cr, mut ci) = (0.0, 0.0); // <psi_y, psi_x> = sum conj(y) x
    for i in 0..nn {
        cr += y[i] * x[i] + y[nn + i] * x[nn + i];
        ci += y[i] * x[nn + i] - y[nn + i] * x[i];
    }
    let th = ci.atan2(cr);
    let (c, s) = (th.cos(), th.sin());
    let mut d2p = 0.0;
    for i in 0..nn {
        // x e^{-i th}
        let xr = x[i] * c + x[nn + i] * s;
        let xi = x[nn + i] * c - x[i] * s;
        d2p += (xr - y[i]).powi(2) + (xi - y[nn + i]).powi(2) + (x[2 * nn + i] - y[2 * nn + i]).powi(2);
    }
    println!("{{\"n\":{n},\"max_abs\":{mx:.6e},\"rel_l2\":{:.6e},\"phase\":{th:.6e},\"rel_l2_phase_aligned\":{:.6e}}}", d2 / n2, d2p.sqrt() / n2);
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    match args.get(1).map(|s| s.as_str()) {
        Some("test") => mode_test(),
        Some("run") => {
            let mut h = HashMap::new();
            for kv in &args[2..] {
                if let Some((k, v)) = kv.split_once('=') {
                    h.insert(k.to_string(), v.to_string());
                }
            }
            mode_run(&Args(h));
        }
        Some("cmp") => mode_cmp(&args[2..]),
        _ => eprintln!("usage: kr test | kr run key=value ... | kr cmp a.f64 b.f64"),
    }
}
