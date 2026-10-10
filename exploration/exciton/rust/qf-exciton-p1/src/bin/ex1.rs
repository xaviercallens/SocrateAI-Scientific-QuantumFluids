//! WP4 experiments (EX-1, EX-2): gradient flows of N points in a torus on rusty-SUNDIALS CVODE.
//!
//!     ex1 <out_dir> [case-id-substring] ...      env QF_THREADS (default 4)
use qf_exciton_p1::flow::{relax, FlowOpts, FlowResult};
use qf_exciton_p1::kernel::{active, amended};
use qf_exciton_p1::lattice::{e_lat, perturb, random_start, spacing, triangular_config};
use qf_exciton_p1::torus::Torus;
use std::fs;
use std::io::Write;
use std::sync::{Arc, Mutex};

#[derive(Clone)]
struct Case {
    index: u64,
    kernel: &'static str,
    rho: f64,
    torus: &'static str, // T36c, T36s, T64c
}

impl Case {
    fn id(&self) -> String {
        format!("{}_{}_{}", self.kernel, self.rho, self.torus)
    }
}

fn registered_cases() -> Vec<Case> {
    let spec: [(&str, [f64; 2], bool); 7] = [
        ("K1", [0.5, 1.5], true),
        ("K2", [0.5, 1.5], true),
        ("K3", [0.1, 0.5], true),
        ("K4", [0.1, 0.5], true),
        ("K5", [0.1, 0.0], false),
        ("K6", [0.1, 0.0], false),
        ("N1", [1.0, 4.0], false),
    ];
    let mut v = Vec::new();
    let mut idx = 0u64;
    for (k, rhos, with64) in spec {
        for (ri, rho) in rhos.iter().enumerate() {
            if *rho == 0.0 {
                continue;
            }
            let tori: Vec<&'static str> = match k {
                "K5" | "K6" => vec!["T36c"],
                _ => {
                    if with64 && ri == 0 {
                        vec!["T36c", "T36s", "T64c"]
                    } else {
                        vec!["T36c", "T36s"]
                    }
                }
            };
            for t in tori {
                v.push(Case { index: idx, kernel: k, rho: *rho, torus: t });
                idx += 1;
            }
        }
    }
    v
}

fn build_torus(c: &Case) -> (Torus, f64, usize, usize, bool) {
    let (k, rc) = active(c.kernel).unwrap();
    let a = spacing(c.rho);
    let (lx, ly, n, nx, ny, comm) = match c.torus {
        "T36c" => (6.0 * a, 3.0 * 3.0f64.sqrt() * a, 36, 6, 3, true),
        "T64c" => (8.0 * a, 4.0 * 3.0f64.sqrt() * a, 64, 8, 4, true),
        _ => {
            let l = (36.0 / c.rho).sqrt();
            (l, l, 36, 0, 0, false)
        }
    };
    let tail = k.tail_per_particle(c.rho, rc);
    (Torus::new(lx, ly, n, k, rc, tail), a, nx, ny, comm)
}

fn record(c: &Case, stage: &str, idx: u64, seed: u64, n: usize, elat: f64, r: &Result<FlowResult, String>, rmin: f64) -> String {
    match r {
        Ok(f) => format!(
            "{{\"case\":\"{}\",\"kernel\":\"{}\",\"rho\":{},\"torus\":\"{}\",\"stage\":\"{stage}\",\"idx\":{idx},\"seed\":{seed},\"n\":{n},\"e\":{:.16e},\"e_lat\":{:.16e},\"ratio\":{:.16e},\"fmax\":{:e},\"converged\":{},\"tau\":{},\"steps\":{},\"rhs\":{},\"wall_s\":{:.3},\"l2_viol\":{},\"l2_max_inc\":{:e},\"min_dist\":{:.6},\"min_dist_start\":{:.6}}}",
            c.id(), c.kernel, c.rho, c.torus, f.e, elat, f.e / elat, f.fmax, f.converged, f.tau, f.steps, f.rhs_evals,
            f.wall_s, f.l2_violations, f.l2_max_rel_increase, 0.0, rmin
        ),
        Err(e) => format!(
            "{{\"case\":\"{}\",\"kernel\":\"{}\",\"rho\":{},\"torus\":\"{}\",\"stage\":\"{stage}\",\"idx\":{idx},\"seed\":{seed},\"n\":{n},\"error\":\"{}\"}}",
            c.id(), c.kernel, c.rho, c.torus, e.replace('"', "'")
        ),
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let out = args[1].clone();
    let filters: Vec<String> = args[2..].to_vec();
    fs::create_dir_all(&out).unwrap();
    let nthreads: usize = std::env::var("QF_THREADS").ok().and_then(|s| s.parse().ok()).unwrap_or(4);
    let opts = FlowOpts::default();
    for c in registered_cases() {
        let long_range = matches!(c.kernel, "K2" | "K3" | "K4");
        if amended() && long_range && c.torus == "T64c" {
            continue; // amendment A2
        }
        if !filters.is_empty() && !filters.iter().any(|f| c.id().contains(f.as_str())) {
            continue;
        }
        let (torus, a, nx, ny, commensurate) = build_torus(&c);
        let (k, rc) = active(c.kernel).unwrap();
        let elat = e_lat(&k, c.rho, rc);
        let n = torus.n;
        let torus = Arc::new(torus);
        // self-test: the perfect lattice has E = e_lat on the commensurate torus
        let selftest = if commensurate {
            let x = triangular_config(nx, ny, a);
            (torus.energy(&x) - elat).abs() / elat
        } else {
            f64::NAN
        };
        let tol_attain = if c.kernel == "K5" || c.kernel == "K6" { 1e-6 } else { 1e-9 };
        let rmin = 0.3 * a;
        eprintln!("[{}] N={n} a={a:.4} e_lat={elat:.10} selftest={selftest:e}", c.id());
        let lines: Arc<Mutex<Vec<String>>> = Arc::new(Mutex::new(Vec::new()));
        let best: Arc<Mutex<(f64, Vec<f64>)>> = Arc::new(Mutex::new((f64::INFINITY, Vec::new())));
        // QF_NSTART overrides the registered 200 starts (timing tests only; never used for registered runs)
        let default_start: u64 = if amended() && long_range { 60 } else { 200 };
        let nstart: u64 = std::env::var("QF_NSTART").ok().and_then(|v| v.parse().ok()).unwrap_or(default_start);
        let max_hops: u64 = if amended() && long_range { 60 } else { 200 };
        let next = Arc::new(Mutex::new(0u64));
        std::thread::scope(|sc| {
            for _ in 0..nthreads {
                let (torus, lines, best, next, opts, c) =
                    (Arc::clone(&torus), Arc::clone(&lines), Arc::clone(&best), Arc::clone(&next), opts.clone(), c.clone());
                sc.spawn(move || loop {
                    let s = {
                        let mut g = next.lock().unwrap();
                        if *g >= nstart {
                            break;
                        }
                        *g += 1;
                        *g - 1
                    };
                    let seed = 1000 * c.index + s;
                    let line = match random_start(&torus, rmin, seed) {
                        None => format!("{{\"case\":\"{}\",\"stage\":\"start\",\"idx\":{s},\"seed\":{seed},\"error\":\"no start\"}}", c.id()),
                        Some(x0) => {
                            let r = relax(&torus, &x0, &opts);
                            if let Ok(f) = &r {
                                let mut b = best.lock().unwrap();
                                if f.e < b.0 {
                                    *b = (f.e, f.x.clone());
                                }
                            }
                            record(&c, "start", s, seed, torus.n, elat, &r, rmin)
                        }
                    };
                    lines.lock().unwrap().push(line);
                });
            }
        });
        // basin hopping on commensurate tori until attained (up to 200 trials), in rounds of `nthreads`
        let mut hops = 0u64;
        if commensurate {
            while hops < max_hops {
                let (be, bx) = best.lock().unwrap().clone();
                if be / elat - 1.0 <= tol_attain {
                    break;
                }
                let round: Vec<u64> = (0..nthreads as u64).map(|j| hops + j).filter(|&h| h < max_hops).collect();
                std::thread::scope(|sc| {
                    for &h in &round {
                        let (torus, lines, best, opts, c, bx) =
                            (Arc::clone(&torus), Arc::clone(&lines), Arc::clone(&best), opts.clone(), c.clone(), bx.clone());
                        sc.spawn(move || {
                            let seed = 1000 * c.index + 500 + h;
                            let x0 = perturb(&torus, &bx, 0.35 * a, seed);
                            let r = relax(&torus, &x0, &opts);
                            if let Ok(f) = &r {
                                let mut b = best.lock().unwrap();
                                if f.e < b.0 {
                                    *b = (f.e, f.x.clone());
                                }
                            }
                            lines.lock().unwrap().push(record(&c, "hop", h, seed, torus.n, elat, &r, rmin));
                        });
                    }
                });
                hops += round.len() as u64;
            }
        }
        let (be, bx) = best.lock().unwrap().clone();
        let ls = lines.lock().unwrap();
        let mut f = fs::File::create(format!("{out}/runs_{}.jsonl", c.id())).unwrap();
        for l in ls.iter() {
            writeln!(f, "{l}").unwrap();
        }
        let xs: Vec<String> = bx.iter().map(|v| format!("{v:.17e}")).collect();
        fs::write(
            format!("{out}/case_{}.json", c.id()),
            format!(
                "{{\"case\":\"{}\",\"kernel\":\"{}\",\"rho\":{},\"torus\":\"{}\",\"n\":{n},\"a\":{a:.16},\"lx\":{:.16},\"ly\":{:.16},\"rc\":{rc},\"tail\":{:.16e},\"e_lat\":{elat:.16e},\"selftest_rel\":{selftest:e},\"best_e\":{be:.16e},\"best_ratio\":{:.16e},\"hops\":{hops},\"amendment\":\"{}\",\"nstart\":{nstart},\"best_x\":[{}]}}\n",
                c.id(), c.kernel, c.rho, c.torus, torus.lx, torus.ly, torus.tail, be / elat, if amended() { "A2" } else { "none" }, xs.join(",")
            ),
        )
        .unwrap();
        eprintln!("[{}] done: best ratio {:.12} ({} runs, {} hops)", c.id(), be / elat, ls.len(), hops);
    }
}
