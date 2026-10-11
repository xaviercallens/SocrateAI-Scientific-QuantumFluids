//! Modified Bessel functions K0, K1 of real argument x > 0 by the trapezoid rule on
//! `K_nu(x) = int_0^inf exp(-x cosh t) cosh(nu t) dt`. The integrand is analytic in the strip |Im t| < pi/2, so the
//! trapezoid error is about exp(-2 pi^2 / (x h^2)) for large x and exp(-pi^2 / h) for small x; h is chosen so that
//! both are below 1e-17.

/// `(K0(x), K1(x))`.
pub fn k01(x: f64) -> (f64, f64) {
    debug_assert!(x > 0.0);
    let h = (0.6 / x.sqrt()).min(0.25);
    let ex = (-x).exp();
    let (mut s0, mut s1) = (0.5, 0.5);
    let mut j = 1usize;
    loop {
        let t = j as f64 * h;
        let ch = t.cosh();
        let a = x * (ch - 1.0);
        if a > 45.0 {
            break;
        }
        let e = (-a).exp();
        s0 += e;
        s1 += e * ch;
        j += 1;
    }
    (ex * h * s0, ex * h * s1)
}
