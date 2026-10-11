//! Raw kernels, the shifted-force truncation and the unit scaling expected by the engine.

use std::sync::Arc;

use crate::bessel::k01;
use cmrr::Pair;

/// A pair kernel in physical units: value and first two derivatives, untruncated.
pub trait Raw: Send + Sync {
    fn v(&self, r: f64) -> f64;
    fn dv(&self, r: f64) -> f64;
    fn d2v(&self, r: f64) -> f64;
}

/// `1/r - 1/sqrt(r^2 + d^2)` (ungated bilayer dipole, per-exciton normalisation).
#[derive(Clone, Copy, Debug)]
pub struct Ungated {
    pub d: f64,
}

impl Raw for Ungated {
    fn v(&self, r: f64) -> f64 {
        let s = (r * r + self.d * self.d).sqrt();
        self.d * self.d / (r * s * (s + r))
    }
    fn dv(&self, r: f64) -> f64 {
        let s = (r * r + self.d * self.d).sqrt();
        let sr = self.d * self.d / (s + r); // s - r
        -sr * (s * s + s * r + r * r) / (r * r * s * s * s)
    }
    fn d2v(&self, r: f64) -> f64 {
        let s2 = r * r + self.d * self.d;
        let s = s2.sqrt();
        2.0 / (r * r * r) + 1.0 / (s2 * s) - 3.0 * r * r / (s2 * s2 * s)
    }
}

/// `exp(-kappa r)/r` (the CMRR control).
#[derive(Clone, Copy, Debug)]
pub struct YukawaRaw {
    pub kappa: f64,
}

impl Raw for YukawaRaw {
    fn v(&self, r: f64) -> f64 {
        (-self.kappa * r).exp() / r
    }
    fn dv(&self, r: f64) -> f64 {
        -(-self.kappa * r).exp() * (self.kappa * r + 1.0) / (r * r)
    }
    fn d2v(&self, r: f64) -> f64 {
        let k = self.kappa;
        (-k * r).exp() * (k * k * r * r + 2.0 * k * r + 2.0) / (r * r * r)
    }
}

/// Gated bilayer dipole kernel, symmetric grounded gates at `z = +-D/2`, electron and hole layers at `z = -+d/2`.
///
/// Laplace/image representation (note `docs/designs/EXCITON_FLUID_GATE_IMAGE_CM.md`): after Poisson summation
/// `U(r) = (4/D) sum_{k>=1} (1 - cos(2 pi k d/D)) K0(2 pi k r/D)` (the mode sum of the Laplace measure
/// `mu(s) ds`, `U(r) = int exp(-s r^2) mu(s) ds`), with the normalisation of [`Ungated`] (`D -> infinity`
/// gives `1/r - 1/sqrt(r^2+d^2)`). `U'(r) = -(4/D) sum (1-cos) q K1(q r)`,
/// `U''(r) = (4/D) sum (1-cos) q^2 [K0(q r) + K1(q r)/(q r)]` with `q = 2 pi k/D`.
///
/// `v`, `dv`, `d2v` use a quintic Hermite table of the regular part `R = U - 1/r` (built from the series itself)
/// on `[R_LO, r_tab]`, the series elsewhere. The table interpolant is used consistently for `v`, `dv`, `d2v`.
#[derive(Clone, Debug)]
pub struct Gated {
    pub d: f64,
    pub dd: f64,
    r_tab: f64,
    table: Vec<[f64; 3]>, // R, R', R'' on the grid R_LO + i*H
    use_table: bool,
}

const R_LO: f64 = 0.02;
const H_TAB: f64 = 0.01;

impl Gated {
    pub fn new(d: f64, dd: f64, use_table: bool) -> Gated {
        assert!(d > 0.0 && dd > d, "need 0 < d < D");
        let r_tab = 3.0 * dd;
        let mut g = Gated { d, dd, r_tab, table: Vec::new(), use_table: false };
        if use_table {
            let n = ((r_tab - R_LO) / H_TAB).ceil() as usize + 1;
            let mut t = Vec::with_capacity(n + 1);
            for i in 0..=n {
                let r = R_LO + i as f64 * H_TAB;
                let (u, du, d2u) = g.series(r);
                t.push([u - 1.0 / r, du + 1.0 / (r * r), d2u - 2.0 / (r * r * r)]);
            }
            g.table = t;
            g.use_table = true;
            g.r_tab = R_LO + n as f64 * H_TAB;
        }
        g
    }

    /// Direct mode sum, `(U, U', U'')`. Terms stop when `q r > 40`.
    pub fn series(&self, r: f64) -> (f64, f64, f64) {
        let two_pi_over_d = 2.0 * std::f64::consts::PI / self.dd;
        let (mut u, mut du, mut d2u) = (0.0, 0.0, 0.0);
        let mut k = 1usize;
        loop {
            let q = two_pi_over_d * k as f64;
            let x = q * r;
            if x > 40.0 {
                break;
            }
            let w = 1.0 - (two_pi_over_d * self.d * k as f64).cos();
            let (k0, k1) = k01(x);
            u += w * k0;
            du -= w * q * k1;
            d2u += w * q * q * (k0 + k1 / x);
            k += 1;
        }
        let pref = 4.0 / self.dd;
        (pref * u, pref * du, pref * d2u)
    }

    /// Table interpolant (falls back to the series outside the table).
    pub fn eval(&self, r: f64) -> (f64, f64, f64) {
        if !self.use_table || r < R_LO || r >= self.r_tab {
            return self.series(r);
        }
        let x = (r - R_LO) / H_TAB;
        let i = (x.floor() as usize).min(self.table.len() - 2);
        let s = x - i as f64;
        let (a, b) = (&self.table[i], &self.table[i + 1]);
        let h = H_TAB;
        let (s2, s3, s4, s5) = (s * s, s * s * s, s * s * s * s, s * s * s * s * s);
        // quintic Hermite basis and derivatives
        let h0 = 1.0 - 10.0 * s3 + 15.0 * s4 - 6.0 * s5;
        let h1 = s - 6.0 * s3 + 8.0 * s4 - 3.0 * s5;
        let h2 = 0.5 * s2 - 1.5 * s3 + 1.5 * s4 - 0.5 * s5;
        let h3 = 10.0 * s3 - 15.0 * s4 + 6.0 * s5;
        let h4 = -4.0 * s3 + 7.0 * s4 - 3.0 * s5;
        let h5 = 0.5 * s3 - s4 + 0.5 * s5;
        let g0 = -30.0 * s2 + 60.0 * s3 - 30.0 * s4;
        let g1 = 1.0 - 18.0 * s2 + 32.0 * s3 - 15.0 * s4;
        let g2 = s - 4.5 * s2 + 6.0 * s3 - 2.5 * s4;
        let g3 = 30.0 * s2 - 60.0 * s3 + 30.0 * s4;
        let g4 = -12.0 * s2 + 28.0 * s3 - 15.0 * s4;
        let g5 = 1.5 * s2 - 4.0 * s3 + 2.5 * s4;
        let c0 = -60.0 * s + 180.0 * s2 - 120.0 * s3;
        let c1 = -36.0 * s + 96.0 * s2 - 60.0 * s3;
        let c2 = 1.0 - 9.0 * s + 18.0 * s2 - 10.0 * s3;
        let c3 = 60.0 * s - 180.0 * s2 + 120.0 * s3;
        let c4 = -24.0 * s + 84.0 * s2 - 60.0 * s3;
        let c5 = 3.0 * s - 12.0 * s2 + 10.0 * s3;
        let rv = a[0] * h0 + h * a[1] * h1 + h * h * a[2] * h2 + b[0] * h3 + h * b[1] * h4 + h * h * b[2] * h5;
        let rd = (a[0] * g0 + h * a[1] * g1 + h * h * a[2] * g2 + b[0] * g3 + h * b[1] * g4 + h * h * b[2] * g5) / h;
        let rdd = (a[0] * c0 + h * a[1] * c1 + h * h * a[2] * c2 + b[0] * c3 + h * b[1] * c4 + h * h * b[2] * c5) / (h * h);
        (rv + 1.0 / r, rd - 1.0 / (r * r), rdd + 2.0 / (r * r * r))
    }
}

impl Raw for Gated {
    fn v(&self, r: f64) -> f64 {
        self.eval(r).0
    }
    fn dv(&self, r: f64) -> f64 {
        self.eval(r).1
    }
    fn d2v(&self, r: f64) -> f64 {
        self.eval(r).2
    }
}

/// Shifted-force truncation at `rc` and a unit scale `ell` (engine coordinates are physical / ell).
pub struct Phys<K: Raw> {
    pub k: K,
    pub rc: f64,
    pub ell: f64,
    vc: f64,
    dvc: f64,
}

impl<K: Raw> Phys<K> {
    pub fn new(k: K, rc: f64, ell: f64) -> Self {
        let (vc, dvc) = (k.v(rc), k.dv(rc));
        Phys { k, rc, ell, vc, dvc }
    }
    /// Shifted-force `(U, U', U'')` at physical distance `r`.
    pub fn phys_pair(&self, r: f64) -> (f64, f64, f64) {
        if r >= self.rc {
            return (0.0, 0.0, 0.0);
        }
        (self.k.v(r) - self.vc - (r - self.rc) * self.dvc, self.k.dv(r) - self.dvc, self.k.d2v(r))
    }
}

impl<K: Raw> Pair for Phys<K> {
    fn pair(&self, r: f64) -> (f64, f64, f64) {
        let (u, du, d2u) = self.phys_pair(r * self.ell);
        (u, du * self.ell, d2u * self.ell * self.ell)
    }
    fn cutoff(&self) -> f64 {
        self.rc / self.ell
    }
    fn dv_ref(&self, r: f64) -> f64 {
        self.k.dv(r * self.ell) * self.ell
    }
    fn d2v_ref(&self, r: f64) -> f64 {
        self.k.d2v(r * self.ell) * self.ell * self.ell
    }
}

/// Which kernel, in units of the boundary spacing.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum KernelSpec {
    Ungated { d: f64 },
    Gated { d: f64, dd: f64 },
    Yukawa { kappa: f64 },
}

impl KernelSpec {
    pub fn parse(s: &str) -> Result<KernelSpec, String> {
        let p: Vec<&str> = s.split(':').collect();
        let f = |i: usize| -> Result<f64, String> {
            p.get(i).ok_or_else(|| format!("kernel spec {s}: missing field"))?.parse::<f64>().map_err(|e| e.to_string())
        };
        match p[0] {
            "ungated" => Ok(KernelSpec::Ungated { d: f(1)? }),
            "gated" => Ok(KernelSpec::Gated { d: f(1)?, dd: f(2)? }),
            "yukawa" => Ok(KernelSpec::Yukawa { kappa: f(1)? }),
            o => Err(format!("unknown kernel {o}")),
        }
    }

    /// Cutoff in physical units: Yukawa `20/kappa` (CMRR default), gated `6 D` (`U ~ exp(-2 pi r/D)`, `exp(-37)`),
    /// ungated none (`1e4`: the energy is then the complete pair sum of the finite cluster).
    pub fn rc(&self) -> f64 {
        match *self {
            KernelSpec::Ungated { .. } => 1.0e4,
            KernelSpec::Gated { dd, .. } => 6.0 * dd,
            KernelSpec::Yukawa { kappa } => 20.0 / kappa,
        }
    }

    /// Kernel in engine units for scale `ell` (use `ell = 1` for physical units).
    pub fn build(&self, ell: f64, use_table: bool) -> Arc<dyn Pair> {
        let rc = self.rc();
        match *self {
            KernelSpec::Ungated { d } => Arc::new(Phys::new(Ungated { d }, rc, ell)),
            KernelSpec::Gated { d, dd } => Arc::new(Phys::new(Gated::new(d, dd, use_table), rc, ell)),
            KernelSpec::Yukawa { kappa } => Arc::new(Phys::new(YukawaRaw { kappa }, rc, ell)),
        }
    }
}
