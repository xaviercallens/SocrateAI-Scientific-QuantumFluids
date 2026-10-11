//! Edge study runner: multi-start gradient flows of N points in an open container.
//!
//!   edge <kernel> <container> <N> <rho> <n_rand> <n_patch> <case_idx> <out.jsonl> [ktrap] [threads]
//! area of a hard-wall container = N/rho; the trap uses `ktrap` and samples starts in a disk of area N/rho.
//! env QF_TABLE_DIR (gated kernels), QF_KAPPA (wall stiffness, default 1e5).
use qf_exciton_edge::flow::{relax, FlowOpts, FlowResult};
use qf_exciton_edge::geom::{self, Cont};
use qf_exciton_edge::kernel;
use qf_exciton_edge::linalg::min_eigenvalue;
use qf_exciton_edge::rng::SplitMix64;
use qf_exciton_edge::system::System;
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};

fn spacing(rho: f64) -> f64 {
    (2.0 / (3.0f64.sqrt() * rho)).sqrt()
}

fn random_start(cont: &Cont, n: usize, a: f64, rng: &mut SplitMix64) -> Vec<f64> {
    let mut x: Vec<f64> = Vec::with_capacity(2 * n);
    for _ in 0..n {
        let mut best = None;
        for _ in 0..10_000 {
            let (px, py) = cont.sample(rng);
            let ok = (0..x.len() / 2).all(|j| ((px - x[2 * j]).powi(2) + (py - x[2 * j + 1]).powi(2)).sqrt() >= 0.3 * a);
            if ok {
                best = Some((px, py));
                break;
            }
        }
        let (px, py) = best.unwrap_or_else(|| cont.sample(rng));
        x.push(px);
        x.push(py);
    }
    x
}

/// triangular-lattice patch: the N lattice points of largest depth for a random rotation and offset
fn patch_start(cont: &Cont, n: usize, a: f64, rng: &mut SplitMix64) -> Vec<f64> {
    let th = 2.0 * std::f64::consts::PI * rng.uniform();
    let (u, v) = (rng.uniform(), rng.uniform());
    patch_from(cont, n, a, th, u, v)
}

/// aligned patch start (amendment A5): orientation 0 or 30 degrees, offset at a high-symmetry point of the lattice
/// (site, two triangle centres, three bond midpoints), spacing x 1.0 or 0.94
fn aligned_start(cont: &Cont, n: usize, a: f64, i: usize) -> Vec<f64> {
    const OFF: [(f64, f64); 6] = [(0.0, 0.0), (1.0 / 3.0, 1.0 / 3.0), (2.0 / 3.0, 2.0 / 3.0), (0.5, 0.0), (0.0, 0.5), (0.5, 0.5)];
    let th = if i % 2 == 0 { 0.0 } else { std::f64::consts::PI / 6.0 };
    let (u, v) = OFF[(i / 2) % 6];
    let sc = if (i / 12) % 2 == 0 { 1.0 } else { 0.94 };
    patch_from(cont, n, a * sc, th, u, v)
}

fn patch_from(cont: &Cont, n: usize, a: f64, th: f64, u: f64, v: f64) -> Vec<f64> {
    let (c, s) = (th.cos(), th.sin());
    let h = 3.0f64.sqrt() / 2.0;
    let m = (6.0 * (n as f64).sqrt()) as i32 + 6;
    let mut pts: Vec<(f64, f64, f64)> = Vec::new();
    for i in -m..=m {
        for j in -m..=m {
            let lx = a * ((i as f64 + u) + 0.5 * (j as f64 + v));
            let ly = a * h * (j as f64 + v);
            let (x, y) = (c * lx - s * ly, s * lx + c * ly);
            pts.push((cont.depth(x, y), x, y));
        }
    }
    pts.sort_by(|p, q| q.0.partial_cmp(&p.0).unwrap());
    pts.iter().take(n).flat_map(|p| [p.1, p.2]).collect()
}

struct Rec {
    kind: &'static str,
    run: usize,
    seed: u64,
    res: Result<FlowResult, String>,
    e_int: f64,
    e_wall: f64,
    viol: f64,
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 9 {
        eprintln!("usage: edge <kernel> <container> <N> <rho> <n_rand> <n_patch> <case_idx> <out.jsonl> [ktrap] [threads]");
        std::process::exit(2);
    }
    let kid = a[1].clone();
    let cid = a[2].clone();
    let n: usize = a[3].parse().unwrap();
    let rho: f64 = a[4].parse().unwrap();
    let n_rand: usize = a[5].parse().unwrap();
    let n_patch: usize = a[6].parse().unwrap();
    let case_idx: u64 = a[7].parse().unwrap();
    let out_path = a[8].clone();
    let ktrap: f64 = a.get(9).map(|s| s.parse().unwrap()).unwrap_or(0.0);
    let threads: usize = a.get(10).map(|s| s.parse().unwrap()).unwrap_or(2);
    let n_aligned: usize = a.get(11).map(|s| s.parse().unwrap()).unwrap_or(0);
    let rand_offset: usize = a.get(12).map(|s| s.parse().unwrap()).unwrap_or(0); // extra random batches (A6): run index offset
    let kappa: f64 = std::env::var("QF_KAPPA").ok().map(|s| s.parse().unwrap()).unwrap_or(1e5);
    let area = n as f64 / rho;
    let pair = kernel::by_id(&kid).unwrap();
    let cont = geom::by_id(&cid, area, ktrap).unwrap();
    let sys = Arc::new(System::new(n, pair, cont, kappa));
    let a0 = spacing(rho);
    let opts = FlowOpts { chunk: 10.0, tau_max: 2000.0, fmax_tol: 1e-4, de_tol: 1e-9, rtol: 1e-8, atol: 1e-10 };
    let popts = FlowOpts::default();
    let total = n_rand + n_patch + n_aligned;
    let next = AtomicUsize::new(0);
    let recs: Mutex<Vec<Rec>> = Mutex::new(Vec::new());
    std::thread::scope(|sc| {
        for _ in 0..threads {
            sc.spawn(|| loop {
                let r = next.fetch_add(1, Ordering::SeqCst);
                if r >= total {
                    break;
                }
                let (kind, run, seed) = if r < n_rand {
                    ("rand", r + rand_offset, case_idx * 1_000_003 + (r + rand_offset) as u64)
                } else if r < n_rand + n_patch {
                    ("patch", r - n_rand, case_idx * 1_000_003 + 500_000 + (r - n_rand) as u64)
                } else {
                    ("aligned", r - n_rand - n_patch, case_idx * 1_000_003 + 900_000 + (r - n_rand - n_patch) as u64)
                };
                let mut rng = SplitMix64::new(seed);
                let x0 = match kind {
                    "rand" => random_start(&sys.cont, n, a0, &mut rng),
                    "patch" => patch_start(&sys.cont, n, a0, &mut rng),
                    _ => aligned_start(&sys.cont, n, a0, run),
                };
                let res = relax(&sys, &x0, &opts);
                let (e_int, e_wall, viol) = match &res {
                    Ok(f) => (sys.e_int(&f.x), sys.e_wall(&f.x), sys.cont.max_violation(&f.x)),
                    Err(_) => (f64::NAN, f64::NAN, f64::NAN),
                };
                recs.lock().unwrap().push(Rec { kind, run, seed, res, e_int, e_wall, viol });
            });
        }
    });
    let mut recs = recs.into_inner().unwrap();
    recs.sort_by(|p, q| (p.kind, p.run).cmp(&(q.kind, q.run)));
    let mut out = std::fs::File::create(&out_path).unwrap();
    let case = format!("{kid}_{cid}_N{n}");
    for r in &recs {
        match &r.res {
            Ok(f) => writeln!(
                out,
                "{{\"rec\":\"run\",\"case\":\"{case}\",\"kind\":\"{}\",\"run\":{},\"seed\":{},\"n\":{n},\"rho\":{rho},\"e_total\":{:.16e},\"e_int\":{:.16e},\"e_wall\":{:.16e},\"max_viol\":{:.3e},\"fmax\":{:.3e},\"converged\":{},\"tau\":{},\"rhs\":{},\"wall_s\":{:.3},\"l2_viol\":{}}}",
                r.kind, r.run, r.seed, f.e, r.e_int, r.e_wall, r.viol, f.fmax, f.converged, f.tau, f.rhs_evals, f.wall_s, f.l2_violations
            )
            .unwrap(),
            Err(e) => writeln!(out, "{{\"rec\":\"error\",\"case\":\"{case}\",\"kind\":\"{}\",\"run\":{},\"seed\":{},\"msg\":{:?}}}", r.kind, r.run, r.seed, e).unwrap(),
        }
    }
    // polish: the best 5 distinct screened configurations are re-relaxed with the tight registered tolerances
    let mut order: Vec<usize> = (0..recs.len()).filter(|&i| recs[i].res.is_ok()).collect();
    order.sort_by(|&p, &q| recs[p].res.as_ref().unwrap().e.partial_cmp(&recs[q].res.as_ref().unwrap().e).unwrap());
    let mut picked: Vec<usize> = Vec::new();
    for &i in &order {
        let e = recs[i].res.as_ref().unwrap().e;
        if picked.iter().any(|&j| (recs[j].res.as_ref().unwrap().e - e).abs() <= 1e-5 * e.abs().max(1e-12)) {
            continue;
        }
        picked.push(i);
        if picked.len() >= 3 {
            break;
        }
    }
    let pol: Mutex<Vec<(usize, Result<FlowResult, String>)>> = Mutex::new(Vec::new());
    let nextp = AtomicUsize::new(0);
    std::thread::scope(|sc| {
        for _ in 0..threads {
            sc.spawn(|| loop {
                let k = nextp.fetch_add(1, Ordering::SeqCst);
                if k >= picked.len() {
                    break;
                }
                let i = picked[k];
                let x0 = recs[i].res.as_ref().unwrap().x.clone();
                let r = relax(&sys, &x0, &popts);
                pol.lock().unwrap().push((i, r));
            });
        }
    });
    let mut pol = pol.into_inner().unwrap();
    pol.sort_by(|p, q| {
        let ep = p.1.as_ref().map(|f| f.e).unwrap_or(f64::INFINITY);
        let eq = q.1.as_ref().map(|f| f.e).unwrap_or(f64::INFINITY);
        ep.partial_cmp(&eq).unwrap()
    });
    let mut rank = 0;
    for (i, r) in &pol {
        let rec = &recs[*i];
        match r {
            Ok(f) => {
                let n2 = 2 * n;
                let mut h = vec![0.0; n2 * n2];
                sys.hessian(&f.x, &mut h);
                let lmin = min_eigenvalue(&h, n2);
                let xs: Vec<String> = f.x.iter().map(|v| format!("{:.16e}", v)).collect();
                writeln!(
                    out,
                    "{{\"rec\":\"polished\",\"case\":\"{case}\",\"rank\":{rank},\"kind\":\"{}\",\"run\":{},\"e_screen\":{:.16e},\"e_total\":{:.16e},\"e_int\":{:.16e},\"e_wall\":{:.16e},\"max_viol\":{:.3e},\"fmax\":{:.3e},\"converged\":{},\"tau\":{},\"rhs\":{},\"wall_s\":{:.3},\"lambda_min\":{:.6e},\"x\":[{}]}}",
                    rec.kind, rec.run, rec.res.as_ref().unwrap().e, f.e, sys.e_int(&f.x), sys.e_wall(&f.x), sys.cont.max_violation(&f.x), f.fmax, f.converged, f.tau, f.rhs_evals, f.wall_s, lmin, xs.join(",")
                )
                .unwrap();
            }
            Err(e) => writeln!(out, "{{\"rec\":\"polish_error\",\"case\":\"{case}\",\"run\":{},\"msg\":{:?}}}", rec.run, e).unwrap(),
        }
        rank += 1;
    }
}
