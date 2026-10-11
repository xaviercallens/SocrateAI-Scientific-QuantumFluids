//! `fg kern <spec> r...`            raw and shifted kernel values (series and table)
//! `fg energy <spec> fixed free`    E_ff + E_fb for a given configuration (physical units)
//! `fg run <spec> fixed starts out [ftol]`   relax every start with the patched CMRR engine
//!
//! Spec: `ungated:d`, `gated:d:D`, `yukawa:kappa` (lengths in units of the boundary spacing).
//! Files: `fixed` has one `x y` per line; `starts` has a first line `nstarts nfree` then nstarts*nfree `x y` lines.
use std::fmt::Write as _;
use std::fs;
use std::sync::Arc;
use std::time::Instant;

use cmrr::{optimize_kernel, Model, NodeStatus, Outcome, Params};
use fenris_gated::{Gated, KernelSpec, Raw};

fn read_xy(path: &str) -> Vec<[f64; 2]> {
    fs::read_to_string(path)
        .unwrap_or_else(|e| panic!("{path}: {e}"))
        .lines()
        .filter(|l| !l.trim().is_empty())
        .map(|l| {
            let v: Vec<f64> = l.split_whitespace().map(|t| t.parse().unwrap()).collect();
            [v[0], v[1]]
        })
        .collect()
}

fn flat(p: &[[f64; 2]]) -> Vec<f64> {
    p.iter().flat_map(|q| [q[0], q[1]]).collect()
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let spec = KernelSpec::parse(&a[2]).expect("kernel spec");
    match a[1].as_str() {
        "kern" => {
            let k = spec.build(1.0, true);
            for t in &a[3..] {
                let r: f64 = t.parse().unwrap();
                let (u, du, d2u) = k.pair(r);
                let mut line = format!("{r:.17e} {u:.17e} {du:.17e} {d2u:.17e}");
                if let KernelSpec::Gated { d, dd } = spec {
                    let g = Gated::new(d, dd, true);
                    let s = g.series(r);
                    let tb = g.eval(r);
                    write!(line, " series {:.17e} {:.17e} {:.17e} table {:.17e} {:.17e} {:.17e}", s.0, s.1, s.2, tb.0, tb.1, tb.2).unwrap();
                    let _ = g.v(r);
                }
                println!("{line}");
            }
        }
        "energy" => {
            let fixed = flat(&read_xy(&a[3]));
            let free = flat(&read_xy(&a[4]));
            let m = Model { pot: spec.build(1.0, true), fixed };
            println!("{:.17e}", m.energy(&free));
        }
        "run" => {
            let fixed_xy = read_xy(&a[3]);
            let ftol: f64 = a.get(6).map_or(1e-9, |s| s.parse().unwrap());
            let text = fs::read_to_string(&a[4]).unwrap();
            let mut lines = text.lines();
            let hdr: Vec<usize> = lines.next().unwrap().split_whitespace().map(|t| t.parse().unwrap()).collect();
            let (ns, nf) = (hdr[0], hdr[1]);
            let mut out = String::new();
            let model = Model { pot: spec.build(1.0, true), fixed: flat(&fixed_xy) };
            for s in 0..ns {
                let mut pos: Vec<[f64; 2]> = fixed_xy.clone();
                let mut st = vec![NodeStatus::BoundaryFixed; fixed_xy.len()];
                for _ in 0..nf {
                    let v: Vec<f64> = lines.next().unwrap().split_whitespace().map(|t| t.parse().unwrap()).collect();
                    pos.push([v[0], v[1]]);
                    st.push(NodeStatus::InternalFree);
                }
                let params = Params { ftol_rel: ftol, ..Params::new(1.0) };
                let t0 = Instant::now();
                let rep = optimize_kernel(&mut pos, &st, &params, &move |ell| spec.build(ell, true));
                let secs = t0.elapsed().as_secs_f64();
                match rep {
                    Ok(r) => {
                        let free = flat(&pos[fixed_xy.len()..]);
                        let e = model.energy(&free);
                        writeln!(
                            out,
                            "start {s} converged {} fmax_rel {:.6e} unclump {} cvode_steps {} rhs {} fallback {} ell {:.12} secs {:.2} energy {:.17e}",
                            (r.outcome == Outcome::Converged) as u8,
                            r.max_free_force_rel,
                            r.unclump_steps,
                            r.cvode_steps,
                            r.rhs_evals,
                            r.cvode_order1_fallback as u8,
                            r.length_scale,
                            secs,
                            e
                        )
                        .unwrap();
                        for p in &pos[fixed_xy.len()..] {
                            writeln!(out, "{:.17e} {:.17e}", p[0], p[1]).unwrap();
                        }
                    }
                    Err(e) => {
                        writeln!(out, "start {s} error {e}").unwrap();
                    }
                }
            }
            let _ = Arc::new(0);
            fs::write(&a[5], out).unwrap();
        }
        o => panic!("unknown command {o}"),
    }
}
