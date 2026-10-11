//! Gate L-a (a1: kernel derivatives, a2: Model force/Hessian, a3: table vs series), L-b2 (1D chain closed form),
//! and the K0/K1 spot values. Thresholds are those of PREREG.md.
use fenris_gated::bessel::k01;
use fenris_gated::{Gated, KernelSpec, Phys, Raw, YukawaRaw};

use cmrr::Model;

fn specs() -> Vec<KernelSpec> {
    vec![
        KernelSpec::Ungated { d: 0.5 },
        KernelSpec::Gated { d: 0.5, dd: 1.5 },
        KernelSpec::Gated { d: 0.5, dd: 5.0 },
        KernelSpec::Yukawa { kappa: 1.5 },
    ]
}

#[test]
fn a1_kernel_derivatives_match_finite_differences() {
    for spec in specs() {
        let k = spec.build(1.0, true);
        for &r in &[0.03, 0.1, 0.3, 1.0, 2.0, 5.0] {
            let h = 1e-5 * r;
            let (u, du, d2u) = k.pair(r);
            let _ = u;
            let fd1 = (k.pair(r + h).0 - k.pair(r - h).0) / (2.0 * h);
            let fd2 = (k.pair(r + h).1 - k.pair(r - h).1) / (2.0 * h);
            assert!((fd1 - du).abs() <= 1e-6 * du.abs().max(1e-12), "{spec:?} r={r} U': {fd1} vs {du}");
            assert!((fd2 - d2u).abs() <= 1e-6 * d2u.abs().max(1e-12), "{spec:?} r={r} U'': {fd2} vs {d2u}");
        }
    }
}

fn lcg(seed: &mut u64) -> f64 {
    *seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
    ((*seed >> 11) as f64 / (1u64 << 53) as f64) * 2.0 - 1.0
}

#[test]
fn a2_model_force_and_hessian_match_finite_differences() {
    for spec in specs() {
        let mut s = 7u64;
        let fixed: Vec<f64> = (0..6).flat_map(|k| [k as f64 * 0.9, -0.8]).collect();
        let y: Vec<f64> = (0..8)
            .flat_map(|k| [(k % 4) as f64 * 0.9 + 0.25 * lcg(&mut s), (k / 4) as f64 * 0.9 + 0.25 * lcg(&mut s)])
            .collect();
        let model = Model { pot: spec.build(1.0, true), fixed };
        let m = y.len();
        let mut f = vec![0.0; m];
        model.force(&y, &mut f);
        let h = 1e-6;
        for c in 0..m {
            let (mut yp, mut ym) = (y.clone(), y.clone());
            yp[c] += h;
            ym[c] -= h;
            let fd = -(model.energy(&yp) - model.energy(&ym)) / (2.0 * h);
            assert!((fd - f[c]).abs() <= 1e-6 * (1.0 + f[c].abs()), "{spec:?} F[{c}]: {fd} vs {}", f[c]);
        }
        let hess = model.hessian(&y);
        let (mut fp, mut fm) = (vec![0.0; m], vec![0.0; m]);
        for c in 0..m {
            let (mut yp, mut ym) = (y.clone(), y.clone());
            yp[c] += h;
            ym[c] -= h;
            model.force(&yp, &mut fp);
            model.force(&ym, &mut fm);
            for r in 0..m {
                let fd = -(fp[r] - fm[r]) / (2.0 * h);
                let an = hess[r * m + c];
                assert!((fd - an).abs() <= 1e-5 * (1.0 + an.abs()), "{spec:?} H[{r},{c}]: {fd} vs {an}");
            }
        }
    }
}

#[test]
fn a3_table_matches_series() {
    for &(d, dd) in &[(0.5, 1.5), (0.5, 5.0), (1.0, 3.0), (1.0, 10.0)] {
        let g = Gated::new(d, dd, true);
        let mut s = 99u64;
        let (mut e0, mut e1, mut e2) = (0.0f64, 0.0f64, 0.0f64);
        for _ in 0..2000 {
            let r = 0.02 + (0.5 * (lcg(&mut s) + 1.0)) * (3.0 * dd - 0.02);
            let a = g.series(r);
            let b = g.eval(r);
            e0 = e0.max((a.0 - b.0).abs() / (1.0 + a.0.abs()));
            e1 = e1.max((a.1 - b.1).abs() / (1.0 + a.1.abs()));
            e2 = e2.max((a.2 - b.2).abs() / (1.0 + a.2.abs()));
        }
        eprintln!("table-vs-series d={d} D={dd}: max rel err U {e0:.2e} U' {e1:.2e} U'' {e2:.2e}");
        assert!(e0 <= 1e-10 && e1 <= 1e-8 && e2 <= 1e-6, "d={d} D={dd}: {e0} {e1} {e2}");
    }
}

#[test]
fn bessel_spot_values() {
    // reference values (Abramowitz & Stegun / mpmath)
    let cases = [
        (0.1, 2.427069024702017, 9.853844780870606),
        (1.0, 0.42102443824070834, 0.6019072301972346),
        (10.0, 1.778006231616765e-5, 1.864877345382558e-5),
    ];
    for (x, k0, k1) in cases {
        let (a, b) = k01(x);
        assert!(((a - k0) / k0).abs() < 1e-13, "K0({x}) {a} vs {k0}");
        assert!(((b - k1) / k1).abs() < 1e-13, "K1({x}) {b} vs {k1}");
    }
}

#[test]
fn b2_chain_closed_form_yukawa() {
    // E(N+1) - E(N) for N free nodes at unit spacing on a line, kappa = 1.5 (tends to -ln(1 - e^-kappa)).
    let kappa = 1.5;
    let k = Phys::new(YukawaRaw { kappa }, 20.0 / kappa, 1.0);
    let model = |n: usize| {
        let y: Vec<f64> = (0..n).flat_map(|i| [i as f64, 0.0]).collect();
        let m = Model { pot: std::sync::Arc::new(Phys::new(YukawaRaw { kappa }, 20.0 / kappa, 1.0)), fixed: vec![] };
        m.energy(&y)
    };
    let _ = k;
    let n = 60;
    let inc = model(n + 1) - model(n);
    let exact = -(1.0 - (-kappa as f64).exp()).ln();
    let rel = ((inc - exact) / exact).abs();
    eprintln!("1D chain increment {inc:.15} vs closed form {exact:.15}, rel {rel:.2e}");
    assert!(rel <= 1e-7, "{rel}");
}

#[test]
fn raw_kernels_positive_and_decreasing() {
    let g = Gated::new(0.5, 1.5, true);
    let mut prev = f64::INFINITY;
    for i in 1..400 {
        let r = 0.02 * i as f64;
        let v = g.v(r);
        assert!(v > 0.0 && v < prev, "r={r} v={v}");
        prev = v;
    }
}
