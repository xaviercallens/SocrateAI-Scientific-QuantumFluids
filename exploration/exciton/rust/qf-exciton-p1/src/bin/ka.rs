//! Known-answer gates KA-1a/b/c, KA-2, KA-3 (Rust side), KA-4 of the Phase 1 pre-registration.
//!
//!     ka <reference.json> <out_dir>
use qf_exciton_p1::kernel::{by_id, Kernel};
use qf_exciton_p1::lattice::{e_lat, lattice_t, random_start, spacing};
use qf_exciton_p1::torus::Torus;
use qf_exciton_p1::util::{json_f64, json_f64_from, json_pos, rel_err};
use std::fmt::Write as _;
use std::fs;

const GL_X: [f64; 4] = [0.1834346424956498, 0.5255324099163290, 0.7966664774136267, 0.9602898564975363];
const GL_W: [f64; 4] = [0.3626837833783620, 0.3137066458778873, 0.2223810344533745, 0.1012285362903763];

fn gl_panel<F: Fn(f64) -> f64>(f: &F, a: f64, b: f64) -> f64 {
    let (c, h) = (0.5 * (a + b), 0.5 * (b - a));
    let mut s = 0.0;
    for k in 0..4 {
        s += GL_W[k] * (f(c + h * GL_X[k]) + f(c - h * GL_X[k]));
    }
    s * h
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let reference = fs::read_to_string(&args[1]).expect("reference.json");
    let out_dir = &args[2];
    fs::create_dir_all(out_dir).ok();
    let mut report = String::new();
    writeln!(report, "{{").unwrap();

    // ---- KA-1a: sum' r^-3 on the unit-spacing triangular lattice
    let c_ref = json_f64(&reference, "KA1_constant_float").unwrap();
    let rho = 2.0 / 3.0f64.sqrt();
    let mut rows = Vec::new();
    let mut errs = Vec::new();
    for r in [200.0, 400.0, 800.0] {
        let s: f64 = lattice_t(1.0, r).iter().map(|&t| t.powf(-1.5)).sum();
        let tailv = 2.0 * std::f64::consts::PI * rho / r;
        let v = s + tailv;
        let e = rel_err(v, c_ref);
        errs.push(e);
        rows.push(format!("{{\"R\":{r},\"sum\":{s:.15},\"with_tail\":{v:.15},\"rel_err\":{e:e}}}"));
    }
    let pass_1a = errs[2] <= 1e-6 && errs[2] <= errs[0];
    writeln!(report, " \"KA1a\":{{\"reference\":{c_ref:.15},\"rows\":[{}],\"pass\":{pass_1a}}},", rows.join(",")).unwrap();

    // ---- KA-1b: Gaussian closed form (Jacobi theta)
    let (k1, rc1) = by_id("K1").unwrap();
    let pos = json_pos(&reference, "K1_theta_closed_form").unwrap();
    let mut rows = Vec::new();
    let mut pass_1b = true;
    for r in [0.5, 1.5] {
        let want = json_f64_from(&reference, &format!("{r:?}"), pos).unwrap();
        let got = e_lat(&k1, r, rc1);
        let e = rel_err(got, want);
        pass_1b &= e <= 1e-13;
        rows.push(format!("{{\"rho\":{r},\"rust\":{got:.16},\"theta\":{want:.16},\"rel_err\":{e:e}}}"));
    }
    writeln!(report, " \"KA1b\":{{\"rows\":[{}],\"pass\":{pass_1b}}},", rows.join(",")).unwrap();

    // ---- KA-1c: e_lat of K1-K4, N1 against reference.json
    let mut rows = Vec::new();
    let mut pass_1c = true;
    let cases: [(&str, [f64; 2]); 5] =
        [("K1", [0.5, 1.5]), ("K2", [0.5, 1.5]), ("K3", [0.1, 0.5]), ("K4", [0.1, 0.5]), ("N1", [1.0, 4.0])];
    for (id, rhos) in cases {
        let (k, rc) = by_id(id).unwrap();
        for r in rhos {
            let want = json_f64(&reference, &format!("{id}@{r:?}")).unwrap();
            let got = e_lat(&k, r, rc);
            let e = rel_err(got, want);
            pass_1c &= e <= 1e-12;
            rows.push(format!("{{\"case\":\"{id}@{r}\",\"rust\":{got:.16},\"reference\":{want:.16},\"rel_err\":{e:e}}}"));
        }
    }
    writeln!(report, " \"KA1c\":{{\"rows\":[{}],\"pass\":{pass_1c}}},", rows.join(",")).unwrap();

    // ---- KA-2: Hartree integral of the undamped bilayer kernel (d = 1) = 4 pi
    let k6 = Kernel::Bilayer { d: 1.0, eps: 0.0 };
    let f = |r: f64| k6.g(r * r) * r;
    let mut edges = vec![0.0, 0.5, 1.0];
    let mut e = 2.0;
    while e < 400.0 {
        edges.push(e);
        e *= 2.0;
    }
    edges.push(400.0);
    let mut s = 0.0;
    for w in edges.windows(2) {
        s += gl_panel(&f, w[0], w[1]);
    }
    let tail = 2.0 * ((400.0f64 * 400.0 + 1.0).sqrt() - 400.0);
    let integral = 2.0 * std::f64::consts::PI * (s + tail);
    let err2 = rel_err(integral, 4.0 * std::f64::consts::PI);
    writeln!(report, " \"KA2\":{{\"integral\":{integral:.15},\"four_pi\":{:.15},\"rel_err\":{err2:e},\"pass\":{}}},",
        4.0 * std::f64::consts::PI, err2 <= 1e-10).unwrap();

    // ---- KA-4: sandwich table of K6
    let pos = json_pos(&reference, "sandwich_K6_eH_over_elat").unwrap();
    let mut rows = Vec::new();
    let mut pass_4 = true;
    for rd2 in [1e-3, 1e-2, 0.1, 0.3, 1.0, 3.0] {
        let key = format!("{rd2:?}");
        let want = json_f64_from(&reference, &key, pos).unwrap();
        let (k, rc) = by_id("K6").unwrap();
        let el = e_lat(&k, rd2, 400.0f64.max(rc));
        let ratio = 2.0 * std::f64::consts::PI * rd2 / el;
        let er = rel_err(ratio, want);
        pass_4 &= er <= 1e-6;
        rows.push(format!("{{\"rho_d2\":{rd2},\"rust\":{ratio:.12},\"reference\":{want:.12},\"rel_err\":{er:e}}}"));
    }
    writeln!(report, " \"KA4\":{{\"rows\":[{}],\"pass\":{pass_4}}},", rows.join(",")).unwrap();

    // ---- KA-3 (Rust side): analytic Hessian vs finite difference of the force; configs dumped for numpy
    let ids = [("K1", 0.5), ("K2", 0.5), ("K3", 0.1), ("K4", 0.1), ("K5", 0.1), ("K6", 0.1), ("N1", 1.0)];
    let mut ka3 = Vec::new();
    let mut dump = String::from("[\n");
    let mut pass_3 = true;
    let mut all_neg_detected = true;
    for (ci, (id, rho)) in ids.iter().enumerate() {
        let (k, rc) = by_id(id).unwrap();
        let a = spacing(*rho);
        let (lx, ly) = (6.0 * a, 3.0 * 3.0f64.sqrt() * a);
        let tail = k.tail_per_particle(*rho, rc);
        let t = Torus::new(lx, ly, 36, k.clone(), rc, tail);
        let n2 = 72;
        for s in 0..5u64 {
            let x = random_start(&t, 0.3 * a, 7000 + 10 * ci as u64 + s).expect("start");
            let e = t.energy(&x);
            let mut f = vec![0.0; n2];
            t.force(&x, &mut f);
            let mut h = vec![0.0; n2 * n2];
            t.hessian(&x, &mut h);
            // central differences of the force
            let step = 1e-5 * a;
            let mut maxdiff = 0.0f64;
            let mut maxdiff_neg = 0.0f64;
            let hmax = h.iter().fold(0.0f64, |m, &v| m.max(v.abs()));
            let (mut fp, mut fm) = (vec![0.0; n2], vec![0.0; n2]);
            for c in 0..n2 {
                let mut xp = x.clone();
                let mut xm = x.clone();
                xp[c] += step;
                xm[c] -= step;
                t.force(&xp, &mut fp);
                t.force(&xm, &mut fm);
                for r in 0..n2 {
                    let fd = -(fp[r] - fm[r]) / (2.0 * step); // d(-F)/dx = Hessian
                    maxdiff = maxdiff.max((h[c * n2 + r] - fd).abs());
                    maxdiff_neg = maxdiff_neg.max((-h[c * n2 + r] - fd).abs());
                }
            }
            let rel = maxdiff / hmax;
            let rel_neg = maxdiff_neg / hmax;
            pass_3 &= rel <= 1e-6;
            all_neg_detected &= rel_neg > 1e-6;
            ka3.push(format!(
                "{{\"kernel\":\"{id}\",\"rho\":{rho},\"seed\":{},\"hess_fd_rel\":{rel:e},\"hess_signflip_rel\":{rel_neg:e}}}",
                7000 + 10 * ci as u64 + s
            ));
            let xs: Vec<String> = x.iter().map(|v| format!("{v:.17e}")).collect();
            let fs_: Vec<String> = f.iter().map(|v| format!("{v:.17e}")).collect();
            if !(ci == 0 && s == 0) {
                dump.push_str(",\n");
            }
            write!(dump, "{{\"kernel\":\"{id}\",\"rho\":{rho},\"lx\":{lx:.17e},\"ly\":{ly:.17e},\"n\":36,\"rc\":{rc},\"tail\":{tail:.17e},\"x\":[{}],\"e\":{e:.17e},\"f\":[{}]}}",
                xs.join(","), fs_.join(",")).unwrap();
        }
    }
    dump.push_str("\n]\n");
    fs::write(format!("{out_dir}/ka3_configs.json"), dump).unwrap();
    writeln!(report, " \"KA3_rust_side\":{{\"rows\":[{}],\"pass\":{pass_3},\"planted_sign_flip_detected\":{all_neg_detected}}}", ka3.join(",\n")).unwrap();
    writeln!(report, "}}").unwrap();
    fs::write(format!("{out_dir}/ka_report.json"), &report).unwrap();
    println!("{report}");
}
