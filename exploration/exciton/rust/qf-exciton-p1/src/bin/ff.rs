//! WP6 solver side: the four-flavour imaginary-time flow (FF-2a/b/c, FF-L2).
//!
//!     ff <reference.json> <out_dir>
use qf_exciton_p1::ff::{flow, FfParams};
use qf_exciton_p1::rng::SplitMix64;
use qf_exciton_p1::util::{json_f64, json_f64_from, json_pos, rel_err};
use std::fmt::Write as _;
use std::fs;

fn support(n: &[f64; 4], thr: f64) -> [bool; 4] {
    [n[0] > thr, n[1] > thr, n[2] > thr, n[3] > thr]
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let reference = fs::read_to_string(&args[1]).unwrap();
    let out = &args[2];
    fs::create_dir_all(out).ok();
    let p = FfParams::paper();
    let mut rep = String::from("{\n");
    // parameters vs reference
    let pos = json_pos(&reference, "four_flavour").unwrap();
    let chk = [
        ("gH", p.gh),
        ("mu", p.mu),
        ("n_x", p.nx),
    ];
    let mut prm = Vec::new();
    for (k, v) in chk {
        let want = json_f64_from(&reference, k, pos).unwrap();
        prm.push(format!("\"{k}\":{{\"rust\":{v:.15e},\"reference\":{want:.15e}}}"));
    }
    writeln!(rep, " \"params\":{{{}}},", prm.join(",")).unwrap();

    // ---- FF-2a
    let mut blocks = Vec::new();
    let mut pass_a = true;
    let mut any_bad_support = 0usize;
    let mut total_viol = 0usize;
    for (bi, bt) in [0.01f64, 0.04, 0.2].iter().enumerate() {
        let b = p.b_ry(*bt);
        let (na, nb, da, db, _oa, _ob) = p.closed_forms(b);
        let mut n_iia = 0;
        let mut n_iib = 0;
        let mut n_other = 0;
        let mut worst = 0.0f64;
        let mut n_unconv = 0;
        let mut omegas_a = Vec::new();
        let mut omegas_b = Vec::new();
        for s in 0..200u64 {
            let mut rng = SplitMix64::new(50_000 + 1000 * bi as u64 + s);
            let psi0 = [0.01 + 0.14 * rng.uniform(), 0.01 + 0.14 * rng.uniform(), 0.01 + 0.14 * rng.uniform(), 0.01 + 0.14 * rng.uniform()];
            let r = flow(&p, b, psi0, 5.0e4).expect("flow");
            total_viol += r.omega_violations;
            if !r.converged {
                n_unconv += 1;
                continue;
            }
            let sup = support(&r.n, 1e-9);
            let a_only = !sup[2] && !sup[3];
            let b_only = !sup[0] && !sup[1];
            if sup[0] && sup[1] && a_only {
                n_iia += 1;
                let nn = r.n[0] + r.n[1];
                worst = worst.max(rel_err(r.n[1] - r.n[0], da)).max(rel_err(nn, na));
                omegas_a.push(r.omega);
            } else if sup[2] && sup[3] && b_only {
                n_iib += 1;
                let nn = r.n[2] + r.n[3];
                worst = worst.max(rel_err(r.n[2] - r.n[3], db)).max(rel_err(nn, nb));
                omegas_b.push(r.omega);
            } else {
                n_other += 1;
                if !(a_only || b_only) {
                    any_bad_support += 1;
                }
            }
        }
        pass_a &= worst <= 1e-9 && any_bad_support == 0;
        blocks.push(format!(
            "{{\"B_T\":{bt},\"n_IIA\":{n_iia},\"n_IIB\":{n_iib},\"n_other_single_or_empty\":{n_other},\"n_unconverged\":{n_unconv},\"worst_rel_err\":{worst:e}}}"
        ));
    }
    writeln!(rep, " \"FF2a\":{{\"blocks\":[{}],\"cross_pair_supports\":{any_bad_support},\"pass\":{pass_a}}},", blocks.join(",")).unwrap();

    // ---- FF-2b: grand potentials of the converged II_A and II_B states, bisection for equality
    let omega_diff = |bt: f64| -> f64 {
        let b = p.b_ry(bt);
        let (na, nb, _, _, _, _) = p.closed_forms(b);
        let _ = (na, nb);
        let sa = (na / 2.0).sqrt();
        let sb = (nb / 2.0).sqrt();
        let ra = flow(&p, b, [sa, sa, 0.0, 0.0], 5.0e4).expect("A");
        let rb = flow(&p, b, [0.0, 0.0, sb, sb], 5.0e4).expect("B");
        ra.omega - rb.omega
    };
    let (mut lo, mut hi) = (0.001f64, 0.2f64);
    let (mut flo, mut fhi) = (omega_diff(lo), omega_diff(hi));
    assert!(flo < 0.0 && fhi > 0.0, "bracket: {flo} {fhi}");
    for _ in 0..50 {
        let mid = 0.5 * (lo + hi);
        let fm = omega_diff(mid);
        if fm < 0.0 {
            lo = mid;
            flo = fm;
        } else {
            hi = mid;
            fhi = fm;
        }
        if hi - lo < 1e-13 {
            break;
        }
    }
    let _ = (flo, fhi);
    let bc_num = 0.5 * (lo + hi);
    let bc_ref_ry = json_f64(&reference, "b_c_Ry").unwrap();
    let bc_cf = p.b_critical();
    let err_b = rel_err(p.b_ry(bc_num), bc_ref_ry);
    writeln!(rep, " \"FF2b\":{{\"B_c_numeric_T\":{bc_num:.10},\"B_c_closed_form_T\":{:.10},\"b_c_ref_Ry\":{bc_ref_ry:.12e},\"b_c_rust_closed_form_Ry\":{bc_cf:.12e},\"rel_err_vs_reference\":{err_b:e},\"pass\":{}}},",
        bc_cf * p.ry_uev / p.mub_uev_per_t, err_b <= 1e-8).unwrap();

    // ---- FF-2c: continuation of II_A with a seed in flavour 2, find the field where the support leaves {0,1}
    let spin_ref = json_f64(&reference, "spinodal_IIA_b_Ry").unwrap();
    let mut b_t = 0.05f64;
    let mut psi = {
        let (na, _, _, _, _, _) = p.closed_forms(p.b_ry(b_t));
        let s = (na / 2.0).sqrt();
        [s, s, 1e-6, 0.0]
    };
    let mut left = None;
    while b_t < 1.5 {
        let b = p.b_ry(b_t);
        let r = flow(&p, b, psi, 2.0e5).expect("cont");
        if r.n[2] > 1e-6 || r.n[3] > 1e-6 {
            left = Some(b_t);
            break;
        }
        psi = [r.psi[0], r.psi[1], 1e-6, 0.0];
        b_t += 0.01;
    }
    let ff2c = match left {
        Some(bt) => {
            let b = p.b_ry(bt);
            format!("{{\"field_leaves_IIA_T\":{bt:.3},\"closed_form_spinodal_T\":{:.4},\"ratio\":{:.4},\"within_5pct\":{}}}",
                spin_ref * p.ry_uev / p.mub_uev_per_t, b / spin_ref, (b / spin_ref - 1.0).abs() <= 0.05)
        }
        None => "{\"field_leaves_IIA_T\":null}".to_string(),
    };
    writeln!(rep, " \"FF2c\":{ff2c},").unwrap();
    writeln!(rep, " \"FF_L2_omega_violations\":{total_viol}").unwrap();
    rep.push_str("}\n");
    fs::write(format!("{out}/ff_report.json"), &rep).unwrap();
    println!("{rep}");
}
