//! Exploratory (not registered): continue the best configuration of a case with a much longer flow, to separate
//! "not attained by the registered stopping rule" from "not attained at all".
//!
//!     [QF_AMEND=A2] polish <runs_dir> <case-id> [tau_max]      e.g. polish runs K1_1.5_T36c 1e6
//! (QF_AMEND=A2 selects the amended cutoffs, as for ex1, for the cases that were run under amendment A2)
use qf_exciton_p1::flow::{relax, FlowOpts};
use qf_exciton_p1::kernel::active as by_id;
use qf_exciton_p1::lattice::{e_lat, spacing};
use qf_exciton_p1::torus::Torus;
use std::fs;
use std::sync::Arc;

fn parse_list(text: &str, key: &str) -> Vec<f64> {
    let pat = format!("\"{key}\":[");
    let i = text.find(&pat).expect("key") + pat.len();
    let j = text[i..].find(']').unwrap() + i;
    text[i..j].split(',').map(|s| s.trim().parse::<f64>().unwrap()).collect()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let dir = &args[1];
    let case = &args[2];
    let tau_max: f64 = args.get(3).map(|s| s.parse().unwrap()).unwrap_or(1.0e6);
    let text = fs::read_to_string(format!("{dir}/case_{case}.json")).unwrap();
    let parts: Vec<&str> = case.split('_').collect();
    let (kid, rho, tor) = (parts[0], parts[1].parse::<f64>().unwrap(), parts[2]);
    let (k, rc) = by_id(kid).unwrap();
    let a = spacing(rho);
    let (lx, ly, n) = match tor {
        "T36c" => (6.0 * a, 3.0 * 3.0f64.sqrt() * a, 36),
        "T64c" => (8.0 * a, 4.0 * 3.0f64.sqrt() * a, 64),
        _ => {
            let l = (36.0 / rho).sqrt();
            (l, l, 36)
        }
    };
    let tail = k.tail_per_particle(rho, rc);
    let torus = Arc::new(Torus::new(lx, ly, n, k.clone(), rc, tail));
    let elat = e_lat(&k, rho, rc);
    let x0 = parse_list(&text, "best_x");
    let e0 = torus.energy(&x0);
    let opts = FlowOpts { chunk: 500.0, tau_max, ..FlowOpts::default() };
    let r = relax(&torus, &x0, &opts).expect("relax");
    println!(
        "{{\"case\":\"{case}\",\"tau_max\":{tau_max},\"ratio_before\":{:.16e},\"ratio_after\":{:.16e},\"ratio_after_minus_1\":{:e},\"fmax\":{:e},\"converged\":{},\"tau_used\":{},\"steps\":{},\"wall_s\":{:.2}}}",
        e0 / elat, r.e / elat, r.e / elat - 1.0, r.fmax, r.converged, r.tau, r.steps, r.wall_s
    );
}
