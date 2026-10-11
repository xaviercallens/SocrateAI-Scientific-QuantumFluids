//! ETDRK4 study driver; gates of docs/designs/EXCITON_FLUID_ETD_PREREG.md.
//!     etd <mode> <out_dir> [args...]      (key=value arguments are options)
use qf_exciton_etd::*;
use std::collections::HashMap;
use std::fmt::Write as _;
use std::fs;
use std::io::Write as _;
use std::sync::Arc;
use std::time::Instant;

struct Args {
    pos: Vec<String>,
    kv: HashMap<String, String>,
}
impl Args {
    fn new() -> Args {
        let mut pos = vec![];
        let mut kv = HashMap::new();
        for a in std::env::args().skip(1) {
            if let Some((k, v)) = a.split_once('=') {
                kv.insert(k.to_string(), v.to_string());
            } else {
                pos.push(a);
            }
        }
        Args { pos, kv }
    }
    fn f(&self, k: &str, d: f64) -> f64 {
        self.kv.get(k).map(|v| v.parse().unwrap()).unwrap_or(d)
    }
    fn u(&self, k: &str, d: usize) -> usize {
        self.kv.get(k).map(|v| v.parse().unwrap()).unwrap_or(d)
    }
    fn s(&self, k: &str, d: &str) -> String {
        self.kv.get(k).cloned().unwrap_or_else(|| d.to_string())
    }
}

fn geom(name: &str) -> (usize, f64) {
    match name {
        "G8" => (8, 1.5),
        "G16" => (16, 3.0),
        "G32" => (32, 6.0),
        _ => panic!("geometry {name}"),
    }
}

fn append(path: &str, line: &str) {
    let mut f = fs::OpenOptions::new().create(true).append(true).open(path).unwrap();
    writeln!(f, "{line}").unwrap();
    println!("{line}");
}

fn write_f64(path: &str, y: &[f64]) {
    let mut b = Vec::with_capacity(y.len() * 8);
    for v in y {
        b.extend_from_slice(&v.to_le_bytes());
    }
    fs::write(path, b).unwrap();
}
fn read_f64(path: &str) -> Option<Vec<f64>> {
    let b = fs::read(path).ok()?;
    Some(b.chunks_exact(8).map(|c| f64::from_le_bytes(c.try_into().unwrap())).collect())
}

fn jget(line: &str, key: &str) -> f64 {
    let pat = format!("\"{key}\":");
    let i = line.find(&pat).unwrap_or_else(|| panic!("key {key}")) + pat.len();
    let rest = &line[i..];
    let end = rest.find(|c: char| c == ',' || c == '}').unwrap();
    rest[..end].trim().parse().unwrap()
}

/// frame frequency of the uniform steady state at density n0 (g n0 + g_R gamma/R)
fn frame_for(par: &Par, n0: f64) -> f64 {
    par.g * n0 + par.gr * par.gamma / par.r
}

fn par_with_n0(n0: f64) -> Par {
    let mut p = Par::reg();
    p.p = p.gamma * (n0 + p.gamma_r / p.r);
    p
}

fn model(m: usize, dx: f64, sigma: f64, v0: f64, par: Par, om: f64) -> Model {
    Model::new(m, dx, par, gate(m, dx, v0, sigma), om)
}

fn bug_par(mut p: Par, bug: usize) -> Par {
    if bug == 1 {
        p.r_psi = 2.0 * p.r;
    }
    p
}

fn opts_of(a: &Args) -> Opts {
    let mut o = Opts::by_name(&a.s("scheme", "etd"));
    let b = a.u("bug", 0);
    if b == 2 || b == 3 {
        o.bug = b as u8;
    }
    o
}

// ------------------------------------------------------------------ test
fn mode_test(out: &str) {
    let m = 8;
    let nn = m * m;
    let md = model(m, 1.0, 1.5, 0.5, Par::reg(), 0.5);
    let mut rng = SplitMix64(99);
    let re: Vec<f64> = (0..nn).map(|_| rng.uniform() - 0.5).collect();
    let im: Vec<f64> = (0..nn).map(|_| rng.uniform() - 0.5).collect();
    // FFT vs naive DFT
    let (nr, ni) = dft2_naive(m, &re, &im, false);
    let (mut fr, mut fi) = (re.clone(), im.clone());
    let (mut br, mut bi) = (vec![0.0; m], vec![0.0; m]);
    md.fft.fft2(&mut fr, &mut fi, false, &mut br, &mut bi);
    let d_fft = (0..nn).map(|i| (fr[i] - nr[i]).abs().max((fi[i] - ni[i]).abs())).fold(0.0f64, f64::max);
    md.fft.fft2(&mut fr, &mut fi, true, &mut br, &mut bi);
    let d_inv = (0..nn).map(|i| (fr[i] - re[i]).abs().max((fi[i] - im[i]).abs())).fold(0.0f64, f64::max);
    // kinetic: plane wave exp(i kx x), kx = 2 pi 1/8: -1/2 lap -> k^2/2
    let kx = 2.0 * std::f64::consts::PI / m as f64;
    let (mut pr, mut pi) = (vec![0.0; nn], vec![0.0; nn]);
    for x in 0..m {
        for y in 0..m {
            pr[x * m + y] = (kx * x as f64).cos();
            pi[x * m + y] = (kx * x as f64).sin();
        }
    }
    let (kr, ki) = md.kin(&pr, &pi);
    let d_kin = (0..nn).map(|i| (kr[i] - 0.5 * kx * kx * pr[i]).abs().max((ki[i] - 0.5 * kx * kx * pi[i]).abs())).fold(0.0f64, f64::max);
    // phi coefficients: contour vs direct at |z| = 2.5 and exact limits at z = 0
    let z = (-1.7f64, 1.8f64);
    let ph = phi_contour(z, 0.3);
    let cmul = |a: (f64, f64), b: (f64, f64)| (a.0 * b.0 - a.1 * b.1, a.0 * b.1 + a.1 * b.0);
    let ez = (z.0.exp() * z.1.cos(), z.0.exp() * z.1.sin());
    let z2 = cmul(z, z);
    let z3 = cmul(z2, z);
    let div = |a: (f64, f64), b: (f64, f64)| {
        let d = b.0 * b.0 + b.1 * b.1;
        ((a.0 * b.0 + a.1 * b.1) / d, (a.1 * b.0 - a.0 * b.1) / d)
    };
    let t = cmul(ez, (4.0 - 3.0 * z.0 + z2.0, -3.0 * z.1 + z2.1));
    let f1 = div((-4.0 - z.0 + t.0, -z.1 + t.1), z3);
    let t = cmul(ez, (-2.0 + z.0, z.1));
    let f2 = div((2.0 + z.0 + t.0, z.1 + t.1), z3);
    let t = cmul(ez, (4.0 - z.0, -z.1));
    let f3 = div((-4.0 - 3.0 * z.0 - z2.0 + t.0, -3.0 * z.1 - z2.1 + t.1), z3);
    let d_phi = [(f1.0 * 0.3 - ph.f1.0).abs(), (f1.1 * 0.3 - ph.f1.1).abs(), (f2.0 * 0.3 - ph.f2.0).abs(), (f2.1 * 0.3 - ph.f2.1).abs(), (f3.0 * 0.3 - ph.f3.0).abs(), (f3.1 * 0.3 - ph.f3.1).abs()].iter().cloned().fold(0.0f64, f64::max);
    let p0 = phi_contour((0.0, 0.0), 0.3);
    let d_zero = [(p0.q.0 - 0.15).abs(), (p0.f1.0 - 0.05).abs(), (p0.f2.0 - 0.05).abs(), (p0.f3.0 - 0.05).abs(), p0.f1.1.abs(), p0.q.1.abs()].iter().cloned().fold(0.0f64, f64::max);
    // consistency: L u + N(u) (spectral, Stepper nonlin) vs rhs_real; uses a step of size tiny: (u(h)-u)/h
    let y = state_uniform(m, 10.0, 0.1, 0.1, 7);
    let mut yd = vec![0.0; 3 * nn];
    md.rhs_real(&y, &mut yd, md.om, true);
    let cons = |h: f64| {
        let y1 = run_fixed(&md, Opts::etd(), h, &y, h);
        (0..3 * nn).map(|i| ((y1[i] - y[i]) / h - yd[i]).abs()).fold(0.0f64, f64::max)
    };
    let d_cons = cons(1e-5);
    let d_cons2 = cons(1e-6);
    let scale = yd.iter().map(|v| v.abs()).fold(0.0f64, f64::max);
    // exact fixed point: uniform state preserved
    let mut yu = vec![0.0; 3 * nn];
    for i in 0..nn {
        yu[i] = 10f64.sqrt();
        yu[2 * nn + i] = 0.1;
    }
    let mut mu = model(m, 1.0, 1.5, 0.0, Par::reg(), 0.5);
    mu.om = 0.5;
    let y2 = run_fixed(&mu, Opts::etd(), 0.1, &yu, 100.0);
    let d_fix = y2.iter().zip(&yu).map(|(a, b)| (a - b).abs()).fold(0.0f64, f64::max);
    let line = format!(
        "{{\"gate\":\"unit\",\"fft_vs_naive\":{d_fft:.3e},\"ifft_roundtrip\":{d_inv:.3e},\"plane_wave_kinetic\":{d_kin:.3e},\"phi_contour_vs_direct\":{d_phi:.3e},\"phi_z0\":{d_zero:.3e},\"rhs_consistency_abs_h1e-5\":{d_cons:.3e},\"rhs_consistency_abs_h1e-6\":{d_cons2:.3e},\"rhs_scale\":{scale:.3e},\"uniform_fixed_point_100\":{d_fix:.3e}}}"
    );
    append(&format!("{out}/unit.jsonl"), &line);
}

// ------------------------------------------------------------------ T-a
fn mode_a(out: &str, a: &Args) {
    let bug = a.u("bug", 0);
    let h = a.f("h", 0.1);
    let tag = if bug > 0 { format!("f_bug{bug}_a") } else { "a".to_string() };
    let opts = opts_of(a);
    let cases: Vec<(&str, usize, usize)> = if bug > 0 { vec![("above", 8, 3)] } else { vec![("above", 8, 10), ("above", 16, 3), ("below", 8, 10)] };
    for (label, m, ns) in cases {
        for seed in 1..=ns as u64 {
            let (p, n0, nr0, t_end) = if label == "above" { (21.0, 10.0, 0.1, 12000.0) } else { (16.0, 0.25, 0.0, 4000.0) };
            let mut par = bug_par(Par::reg(), bug);
            par.p = p;
            let md = model(m, 1.0, 1.5 * m as f64 / 8.0, 0.0, par, 0.5);
            let y0 = state_uniform(m, n0, nr0, 1e-3, seed);
            let t0 = Instant::now();
            let y = run_fixed(&md, opts, h, &y0, t_end);
            let o = observe(&md, &y);
            let pass = if label == "above" {
                (o.mean_n - 10.0).abs() / 10.0 <= 1e-10 && (o.mean_nr - 0.1).abs() / 0.1 <= 1e-10 && o.std_n / 10.0 <= 1e-10 && (o.omega - 0.5).abs() <= 1e-10
            } else {
                o.max_psi <= 1e-6 && (o.mean_nr - 0.08).abs() / 0.08 <= 1e-8
            };
            let line = format!(
                "{{\"gate\":\"T-a\",\"bug\":{bug},\"case\":\"{label}\",\"M\":{m},\"seed\":{seed},\"h\":{h},\"t\":{t_end},\"scheme\":\"{}\",{},\"pass\":{pass},\"seconds\":{:.2}}}",
                a.s("scheme", "etd"),
                obs_json(&o),
                t0.elapsed().as_secs_f64()
            );
            append(&format!("{out}/{tag}.jsonl"), &line);
        }
    }
}

// ------------------------------------------------------------------ T-b
fn cvode_ref(out: &str, name: &str, md: &Arc<Model>, y0: &[f64], t_end: f64, rtol: f64, atol: f64) -> (Vec<f64>, usize, f64) {
    let path = format!("{out}/{name}.f64");
    if let Some(y) = read_f64(&path) {
        return (y, 0, 0.0);
    }
    let f = cvode_flow(md, y0, t_end, rtol, atol, t_end, |_, _| false);
    assert!(f.error.is_none(), "cvode: {:?}", f.error);
    write_f64(&path, &f.y);
    (f.y, f.steps, f.seconds)
}

fn mode_b(out: &str, a: &Args) {
    let gname = a.pos[2].clone();
    let (m, sigma) = geom(&gname);
    let t_end = a.f("t", 10.0);
    let bug = a.u("bug", 0);
    let opts = opts_of(a);
    let sname = a.s("scheme", "etd");
    let mut par = Par::reg();
    // amendment A1: reservoir-decay control (stiffness scan); gr = 200 is the registered model
    let gr = a.f("gr", 200.0);
    let gtag = if gr == 200.0 { String::new() } else { par.gamma_r = gr; par.p = par.gamma * (10.0 + gr / par.r); format!("_gr{gr}") };
    let mref = Arc::new(model(m, 1.0, sigma, 0.5, par, 0.5));
    let y0 = state_uniform(m, 10.0, 0.1, 1e-3, 1);
    let (yr, st, sec) = cvode_ref(out, &format!("ref_{gname}_t{t_end}{gtag}_r12"), &mref, &y0, t_end, 1e-12, 1e-14);
    let (yr2, st2, sec2) = cvode_ref(out, &format!("ref_{gname}_t{t_end}{gtag}_r11"), &mref, &y0, t_end, 1e-11, 1e-13);
    let e_ref = err_max_rel(&yr2, &yr);
    eprintln!("ref steps {st} {sec:.1}s ; ref2 steps {st2} {sec2:.1}s ; e_ref {e_ref:.3e}");
    let hs: Vec<f64> = match sname.as_str() {
        "lawk" | "etdk" => vec![0.01, 0.005, 0.0025, 0.00125],
        _ => vec![0.2, 0.1, 0.05, 0.025, 0.0125],
    };
    let md = model(m, 1.0, sigma, 0.5, bug_par(par, bug), 0.5);
    let mut errs = vec![];
    for &h in &hs {
        let t0 = Instant::now();
        let y = run_fixed(&md, opts, h, &y0, t_end);
        let e = err_max_rel(&y, &yr);
        errs.push(e);
        append(&format!("{out}/b.jsonl"), &format!("{{\"gate\":\"T-b\",\"geom\":\"{gname}\",\"scheme\":\"{sname}\",\"gamma_R\":{gr},\"bug\":{bug},\"h\":{h},\"t\":{t_end},\"E\":{e:.6e},\"e_ref\":{e_ref:.3e},\"seconds\":{:.3}}}", t0.elapsed().as_secs_f64()));
    }
    let mut nvalid = 0;
    let mut allin = true;
    let mut ratios = String::new();
    for i in 0..errs.len() - 1 {
        let r = errs[i] / errs[i + 1];
        let valid = errs[i + 1] >= 50.0 * e_ref;
        if valid {
            nvalid += 1;
            if !(12.0..=20.0).contains(&r) {
                allin = false;
            }
        }
        write!(ratios, "{{\"h_coarse\":{},\"ratio\":{r:.4},\"valid\":{valid}}},", hs[i]).unwrap();
    }
    let pass = allin && nvalid >= 3;
    append(&format!("{out}/b.jsonl"), &format!("{{\"gate\":\"T-b\",\"summary\":true,\"geom\":\"{gname}\",\"scheme\":\"{sname}\",\"gamma_R\":{gr},\"bug\":{bug},\"ratios\":[{}],\"n_valid\":{nvalid},\"pass\":{pass}}}", ratios.trim_end_matches(',')));
}

// ------------------------------------------------------------------ T-c
fn mode_c(out: &str, a: &Args) {
    let sname = a.pos[2].clone();
    let n0 = a.f("n0", 10.0);
    let dx = a.f("dx", 1.0);
    let m = a.u("M", 8);
    let tag = a.s("tag", "c");
    let t_end = a.f("t", 200.0);
    let hmin = a.f("hmin", 0.01);
    let par = par_with_n0(n0);
    let om = frame_for(&par, n0);
    let sigma = 1.5 * dx * m as f64 / 8.0;
    let md = model(m, dx, sigma, 0.5, par, om);
    let y0 = state_uniform(m, n0, par.gamma / par.r, 1e-3, 1);
    let opts = Opts::by_name(&sname);
    let steps_for = |h: f64| (t_end / h).ceil() as usize;
    let nl = (par.r + par.g) * n0;
    let kmax = std::f64::consts::PI.powi(2) / (dx * dx);
    // reference: ETD with a step that is converged against its half
    let mut href = 0.0125;
    let mut yref;
    loop {
        let n = steps_for(href);
        let y1 = run_fixed(&md, Opts::etd(), t_end / n as f64, &y0, t_end);
        let n2 = steps_for(href / 2.0);
        let y2 = run_fixed(&md, Opts::etd(), t_end / n2 as f64, &y0, t_end);
        let e = err_max_rel(&y1, &y2);
        yref = y2;
        if e.is_finite() && e < 1e-4 {
            break;
        }
        href /= 2.0;
        assert!(href > 1e-5, "no converged reference");
    }
    let mut fails = vec![];
    let mut first: Option<f64> = None;
    for j in 0..=32 {
        let h0 = hmin * 2f64.powf(j as f64 / 4.0);
        let n = steps_for(h0);
        let h = t_end / n as f64;
        let mut st = Stepper::new(&md, opts, h);
        let mut u = md.to_spec(&y0);
        let mut blown = false;
        let mut done = 0;
        while done < n && !blown {
            let c = (n - done).min(500);
            st.advance(&mut u, c);
            done += c;
            let o = observe(&md, &md.to_real(&u));
            if !o.finite || o.max_psi * o.max_psi > 1e4 {
                blown = true;
            }
        }
        let y = md.to_real(&u);
        let e = if blown { f64::INFINITY } else { err_max_rel(&y, &yref) };
        let class = if blown { "blown" } else if e <= 0.05 { "stable" } else { "inaccurate" };
        if class != "stable" {
            fails.push(h0);
            if first.is_none() {
                first = Some(h0);
            }
        }
        append(&format!("{out}/{tag}.jsonl"), &format!("{{\"gate\":\"T-c\",\"scheme\":\"{sname}\",\"n0\":{n0},\"dx\":{dx},\"M\":{m},\"hmin\":{hmin},\"h\":{h:.6e},\"h_grid\":{h0:.6e},\"class\":\"{class}\",\"E\":{},\"href\":{href}}}", if e.is_finite() { format!("{e:.4e}") } else { "null".into() }));
    }
    let hf = first.unwrap_or(f64::INFINITY);
    let last_stable = (0..=32).map(|j| hmin * 2f64.powf(j as f64 / 4.0)).filter(|h| *h < hf).fold(0.0f64, f64::max);
    let fl: Vec<String> = fails.iter().map(|h| format!("{h:.4}")).collect();
    append(
        &format!("{out}/{tag}.jsonl"),
        &format!("{{\"gate\":\"T-c\",\"summary\":true,\"scheme\":\"{sname}\",\"n0\":{n0},\"dx\":{dx},\"M\":{m},\"h_first\":{},\"h_last_stable_below\":{last_stable:.4},\"nonlinear_rate\":{nl},\"kmax_freq\":{kmax:.4},\"fail_set\":[{}]}}", if hf.is_finite() { format!("{hf:.5}") } else { "null".into() }, fl.join(",")),
    );
}

// ------------------------------------------------------------------ T-d
fn d_files(v0: f64) -> (String, String) {
    let base = "/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/exploration/exciton/results/phase3";
    let tag = if v0 == 0.0 { "0".to_string() } else if v0 == 1.0 { "1.0".to_string() } else { format!("{v0}") };
    let long = if v0 == 0.5 { format!("{base}/exploratory/d_T16000.jsonl") } else { format!("{base}/exploratory/d_T16000_V{tag}.jsonl") };
    (format!("{base}/d_V{tag}.jsonl"), long)
}

fn cmp_obs(o: &Obs, rec: &str, tight: bool) -> (bool, String) {
    let dom = (o.omega - jget(rec, "omega")).abs();
    let dnc = (o.n_center - jget(rec, "n_center")).abs();
    let dnk = (o.n_corner - jget(rec, "n_corner")).abs();
    let dmn = (o.mean_n - jget(rec, "mean_n")).abs() / jget(rec, "mean_n");
    let dmr = (o.mean_nr - jget(rec, "mean_nr")).abs() / jget(rec, "mean_nr");
    let dsd = (o.std_n - jget(rec, "std_n")).abs();
    let (to, tn, tm, ts) = if tight { (1e-7, 1e-5, 1e-7, f64::INFINITY) } else { (1e-6, 1e-4, 1e-6, 1e-5) };
    let pass = dom <= to && dnc <= tn && dnk <= tn && dmn <= tm && dmr <= tm && dsd <= ts;
    (pass, format!("\"d_omega\":{dom:.3e},\"d_n_center\":{dnc:.3e},\"d_n_corner\":{dnk:.3e},\"d_mean_n\":{dmn:.3e},\"d_mean_nr\":{dmr:.3e},\"d_std_n\":{dsd:.3e}"))
}

fn mode_d(out: &str, a: &Args) {
    let part = a.pos[2].clone();
    let h = a.f("h", 0.05);
    let bug = a.u("bug", 0);
    let opts = opts_of(a);
    let tag = if bug > 0 { format!("f_bug{bug}_d") } else { "d".to_string() };
    let v0s: Vec<f64> = match a.kv.get("v0") {
        Some(v) => vec![v.parse().unwrap()],
        None => vec![0.0, 0.25, 0.5, 1.0],
    };
    let seeds = a.u("seeds", 10);
    match part.as_str() {
        "i" | "ii" => {
            for &v0 in &v0s {
                let (f4, f16) = d_files(v0);
                let recs = fs::read_to_string(if part == "i" { f4 } else { f16 }).unwrap();
                let lines: Vec<&str> = recs.lines().collect();
                let t_end = if part == "i" { 4000.0 } else { 16000.0 };
                let ns = if part == "i" { seeds } else { 1 };
                for seed in 1..=ns as u64 {
                    let md = model(8, 1.0, 1.5, v0, bug_par(Par::reg(), bug), 0.5);
                    let y0 = state_uniform(8, 10.0, 0.1, 1e-3, seed);
                    let t0 = Instant::now();
                    let y = run_fixed(&md, opts, h, &y0, t_end);
                    let o = observe(&md, &y);
                    let (pass, diffs) = cmp_obs(&o, lines[seed as usize - 1], part == "ii");
                    append(&format!("{out}/{tag}_{part}.jsonl"), &format!("{{\"gate\":\"T-d({part})\",\"bug\":{bug},\"V0\":{v0},\"seed\":{seed},\"h\":{h},\"t\":{t_end},{},{diffs},\"pass\":{pass},\"seconds\":{:.2}}}", obs_json(&o), t0.elapsed().as_secs_f64()));
                }
            }
        }
        "hsweep" => {
            // amendment A2 (D1): step-size convergence of the t=4000 state against the CVODE record and against itself
            for &v0 in &[0.5, 1.0] {
                let (f4, _) = d_files(v0);
                let recs = fs::read_to_string(f4).unwrap();
                let rec = recs.lines().next().unwrap();
                for sname in ["etd", "krog"] {
                    let hs = [0.1, 0.05, 0.025, 0.0125];
                    let md = model(8, 1.0, 1.5, v0, Par::reg(), 0.5);
                    let y0 = state_uniform(8, 10.0, 0.1, 1e-3, 1);
                    let ys: Vec<Vec<f64>> = hs.iter().map(|&h| run_fixed(&md, Opts::by_name(sname), h, &y0, 4000.0)).collect();
                    for (i, &h) in hs.iter().enumerate() {
                        let o = observe(&md, &ys[i]);
                        let (_, diffs) = cmp_obs(&o, rec, false);
                        let self_e = err_max_rel(&ys[i], &ys[3]);
                        append(&format!("{out}/d_hsweep.jsonl"), &format!("{{\"gate\":\"T-d(D1)\",\"V0\":{v0},\"scheme\":\"{sname}\",\"h\":{h},\"t\":4000,\"omega\":{:.12},\"n_center\":{:.9},\"std_n\":{:.9},{diffs},\"E_vs_finest_same_scheme\":{self_e:.3e}}}", o.omega, o.n_center, o.std_n));
                    }
                }
            }
        }
        "stat8" => {
            let v0s: Vec<f64> = match a.kv.get("v0") {
                Some(v) => vec![v.parse().unwrap()],
                None => vec![0.25, 0.5, 1.0],
            };
            for &v0 in &v0s {
                let md = model(8, 1.0, 1.5, v0, Par::reg(), 0.5);
                let h = a.f("h", 0.05);
                let mut u = md.to_spec(&state_uniform(8, 10.0, 0.1, 1e-3, 1));
                let mut st = Stepper::new(&md, Opts::etd(), h);
                let chunk = (50.0 / h).round() as usize;
                let tol = a.f("tol", 1e-12);
                let mut t = 0.0;
                let mut o;
                loop {
                    st.advance(&mut u, chunk);
                    t += 50.0;
                    o = observe(&md, &md.to_real(&u));
                    if o.resid <= tol || t >= a.f("cap", 100000.0) {
                        break;
                    }
                }
                let (_, f16) = d_files(v0);
                let rec = fs::read_to_string(f16).unwrap();
                let rec = rec.lines().next().unwrap();
                let (_, diffs) = cmp_obs(&o, rec, true);
                append(&format!("{out}/d_stat8.jsonl"), &format!("{{\"gate\":\"T-d(D2)\",\"V0\":{v0},\"h\":{h},\"t_reached\":{t},{},{diffs},\"record_t16000_mean_n\":{:.12e}}}", obs_json(&o), jget(rec, "mean_n")));
            }
        }
        "iii" => {
            let refs = [(0.25, 0.046, 5.84, 0.01), (0.5, 0.077, 2.38, 0.01), (1.0, 0.107, 0.10, 0.005)];
            for &(v0, shift, nc, tol_nc) in &refs {
                if let Some(v) = a.kv.get("v0") {
                    if (v.parse::<f64>().unwrap() - v0).abs() > 1e-9 {
                        continue;
                    }
                }
                let md = model(16, 1.0, 3.0, v0, Par::reg(), 0.5);
                let mut u = md.to_spec(&state_uniform(16, 10.0, 0.1, 1e-3, 1));
                let mut st = Stepper::new(&md, opts, h);
                let chunk = (50.0 / h).round() as usize;
                let cap = a.f("cap", 150000.0);
                let t0 = Instant::now();
                let mut t = 0.0;
                let mut o;
                let mut k = 0;
                loop {
                    st.advance(&mut u, chunk);
                    t += 50.0;
                    k += 1;
                    o = observe(&md, &md.to_real(&u));
                    if k % 100 == 0 {
                        eprintln!("G16 V0={v0} t={t} resid={:.3e} omega={:.8}", o.resid, o.omega);
                    }
                    if o.resid <= 1e-8 || t >= cap || !o.finite {
                        break;
                    }
                }
                let ds = (o.omega - 0.5 - shift).abs();
                let dn = (o.n_center - nc).abs();
                let pass = ds <= 6e-4 && dn <= tol_nc && o.resid <= 1e-8;
                append(&format!("{out}/d_iii.jsonl"), &format!("{{\"gate\":\"T-d(iii)\",\"V0\":{v0},\"h\":{h},\"t_reached\":{t},{},\"shift\":{:.6},\"shift_ref\":{shift},\"d_shift\":{ds:.3e},\"n_center_ref\":{nc},\"d_n_center\":{dn:.3e},\"pass\":{pass},\"seconds\":{:.1}}}", obs_json(&o), o.omega - 0.5, t0.elapsed().as_secs_f64()));
            }
        }
        _ => panic!("part"),
    }
}

// ------------------------------------------------------------------ T-e
fn mode_e(out: &str, a: &Args) {
    let part = a.pos[2].clone();
    match part.as_str() {
        "scaling" => {
            let h = 0.05;
            let mut base = 0.0;
            for m in [8usize, 16, 32, 64, 128] {
                let md = model(m, 1.0, 3.0 * m as f64 / 16.0, 0.5, Par::reg(), 0.5);
                let y0 = state_uniform(m, 10.0, 0.1, 1e-3, 1);
                let mut st = Stepper::new(&md, Opts::etd(), h);
                let mut u = md.to_spec(&y0);
                st.advance(&mut u, 20);
                let mut best = f64::INFINITY;
                for _ in 0..3 {
                    let t0 = Instant::now();
                    st.advance(&mut u, 200);
                    best = best.min(t0.elapsed().as_secs_f64() / 200.0);
                }
                if m == 8 {
                    base = best;
                }
                let nn = (m * m) as f64;
                let fft_ratio = (nn * nn.log2()) / (64.0 * 64f64.log2());
                let ratio = best / base / fft_ratio;
                let ok = u.0[0].iter().all(|v| v.is_finite());
                append(&format!("{out}/e_scaling.jsonl"), &format!("{{\"gate\":\"T-e(i)\",\"M\":{m},\"h\":{h},\"seconds_per_step\":{best:.4e},\"seconds_per_unit_time\":{:.4e},\"ratio_to_NlogN\":{ratio:.3},\"finite\":{ok}}}", best / h));
            }
        }
        "etd" => {
            let (gname, h) = (a.s("geom", "G8"), a.f("h", 0.1));
            let (m, sigma) = geom(&gname);
            let md = model(m, 1.0, sigma, a.f("v0", 0.5), Par::reg(), 0.5);
            let mut u = md.to_spec(&state_uniform(m, 10.0, 0.1, 1e-3, 1));
            let mut st = Stepper::new(&md, Opts::etd(), h);
            let chunk = (50.0 / h).round() as usize;
            let t0 = Instant::now();
            let mut t = 0.0;
            let (mut t7, mut s7, mut t8, mut s8) = (None, 0.0, None, 0.0);
            while t < a.f("cap", 60000.0) {
                st.advance(&mut u, chunk);
                t += 50.0;
                let o = observe(&md, &md.to_real(&u));
                if t7.is_none() && o.resid <= 1e-7 {
                    t7 = Some(t);
                    s7 = t0.elapsed().as_secs_f64();
                }
                if o.resid <= 1e-8 {
                    t8 = Some(t);
                    s8 = t0.elapsed().as_secs_f64();
                    break;
                }
            }
            append(&format!("{out}/e_etd.jsonl"), &format!("{{\"gate\":\"T-e(ii)\",\"solver\":\"etd\",\"geom\":\"{gname}\",\"h\":{h},\"t_1e-7\":{},\"seconds_1e-7\":{s7:.2},\"t_1e-8\":{},\"seconds_1e-8\":{s8:.2}}}", t7.map(|v| v.to_string()).unwrap_or("null".into()), t8.map(|v| v.to_string()).unwrap_or("null".into())));
        }
        "cvode" => {
            let rtol = a.f("rtol", 1e-10);
            let md = Arc::new(model(8, 1.0, 1.5, 0.5, Par::reg(), 0.5));
            let y0 = state_uniform(8, 10.0, 0.1, 1e-3, 1);
            let obs_model = model(8, 1.0, 1.5, 0.5, Par::reg(), 0.5);
            let mut t7 = None;
            let mut s7 = 0.0;
            let t0 = Instant::now();
            let f = cvode_flow(&md, &y0, a.f("cap", 20000.0), rtol, rtol * 1e-2, 50.0, |t, y| {
                let o = observe(&obs_model, y);
                if t7.is_none() && o.resid <= 1e-7 {
                    t7 = Some(t);
                    s7 = t0.elapsed().as_secs_f64();
                }
                o.resid <= 1e-7
            });
            append(&format!("{out}/e_cvode.jsonl"), &format!("{{\"gate\":\"T-e(ii)\",\"solver\":\"cvode\",\"geom\":\"G8\",\"rtol\":{rtol:e},\"t_1e-7\":{},\"seconds_1e-7\":{s7:.2},\"steps\":{},\"total_seconds\":{:.2},\"error\":{}}}", t7.map(|v| v.to_string()).unwrap_or("null".into()), f.steps, f.seconds, f.error.map(|e| format!("\"{e}\"")).unwrap_or("null".into())));
        }
        _ => panic!("part"),
    }
}

// ------------------------------------------------------------------ T-f(ii): nonlinear-rate sweep
fn mode_f2(out: &str, a: &Args) {
    let t_end = a.f("t", 2.0);
    for n0 in [10.0, 50.0, 200.0, 1000.0] {
        if let Some(v) = a.kv.get("n0") {
            if (v.parse::<f64>().unwrap() - n0).abs() > 1e-9 {
                continue;
            }
        }
        let par = par_with_n0(n0);
        let om = frame_for(&par, n0);
        let md = Arc::new(model(8, 1.0, 1.5, 0.5, par, om));
        let y0 = state_uniform(8, n0, 0.1, 1e-3, 1);
        let t0 = Instant::now();
        let f = cvode_flow(&md, &y0, t_end, 1e-12, 1e-14, t_end, |_, _| false);
        let f2 = cvode_flow(&md, &y0, t_end, 1e-11, 1e-13, t_end, |_, _| false);
        let e_ref = err_max_rel(&f2.y, &f.y);
        eprintln!("n0={n0}: cvode {:.1}s steps {} e_ref {e_ref:.2e} err {:?}", t0.elapsed().as_secs_f64(), f.steps, f.error);
        let hs: Vec<f64> = a.s("hs", "0.02,0.01,0.005").split(',').map(|v| v.parse().unwrap()).collect();
        for sname in ["etd", "law", "lawk", "etdk", "krog"] {
            for &h in &hs {
                let y = run_fixed(&md, Opts::by_name(sname), h, &y0, t_end);
                let e = err_max_rel(&y, &f.y);
                append(&format!("{out}/f2.jsonl"), &format!("{{\"gate\":\"T-f(ii)\",\"n0\":{n0},\"R_n0_over_gammaR\":{},\"scheme\":\"{sname}\",\"h\":{h},\"t\":{t_end},\"E\":{},\"E_over_h4\":{},\"e_ref\":{e_ref:.2e}}}", par.r * n0 / par.gamma_r, if e.is_finite() { format!("{e:.4e}") } else { "null".into() }, if e.is_finite() { format!("{:.4e}", e / h.powi(4)) } else { "null".into() }));
            }
        }
    }
}

// ------------------------------------------------------------------ T-g work-precision
fn mode_g(out: &str, a: &Args) {
    let t_end = a.f("t", 20.0);
    let n0 = a.f("n0", 10.0);
    let par = par_with_n0(n0);
    let md = Arc::new(model(8, 1.0, 1.5, 0.5, par, frame_for(&par, n0)));
    let y0 = state_uniform(8, n0, 0.1, 1e-3, 1);
    let f = cvode_flow(&md, &y0, t_end, 1e-12, 1e-14, t_end, |_, _| false);
    let yr = f.y;
    let hs: Vec<f64> = a.s("hs", "0.2,0.1,0.05,0.025,0.0125").split(',').map(|v| v.parse().unwrap()).collect();
    let sch = a.s("scheme", "etd");
    for &h in &hs {
        let t0 = Instant::now();
        let y = run_fixed(&md, Opts::by_name(&sch), h, &y0, t_end);
        let sec = t0.elapsed().as_secs_f64();
        append(&format!("{out}/g.jsonl"), &format!("{{\"gate\":\"T-g\",\"n0\":{n0},\"solver\":\"{sch}\",\"h\":{h},\"steps\":{},\"E\":{:.4e},\"seconds\":{sec:.4}}}", (t_end / h).round(), err_max_rel(&y, &yr)));
    }
    for rtol in [1e-4, 1e-6, 1e-8, 1e-10] {
        let f = cvode_flow(&md, &y0, t_end, rtol, rtol * 1e-2, t_end, |_, _| false);
        append(&format!("{out}/g.jsonl"), &format!("{{\"gate\":\"T-g\",\"n0\":{n0},\"solver\":\"cvode\",\"rtol\":{rtol:e},\"steps\":{},\"E\":{:.4e},\"seconds\":{:.4}}}", f.steps, err_max_rel(&f.y, &yr), f.seconds));
    }
}

fn main() {
    let a = Args::new();
    let (mode, out) = (a.pos[0].as_str(), a.pos[1].as_str());
    fs::create_dir_all(out).ok();
    match mode {
        "test" => mode_test(out),
        "a" => mode_a(out, &a),
        "b" => mode_b(out, &a),
        "c" => mode_c(out, &a),
        "d" => mode_d(out, &a),
        "e" => mode_e(out, &a),
        "f2" => mode_f2(out, &a),
        "g" => mode_g(out, &a),
        _ => panic!("mode"),
    }
}
