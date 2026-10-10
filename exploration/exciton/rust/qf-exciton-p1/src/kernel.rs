//! Pair kernels `g(t)` of the squared distance `t = r²` and their derivatives.
//!
//! All the "CM" kernels are completely monotone in `t`; `Gem` is the non-CM control (cluster crystals).

/// `t^(-m/2) - (t+c)^(-m/2)` for odd `m ≥ 1`, without cancellation.
fn diff_pow(t: f64, c: f64, m: i32) -> f64 {
    let a = (t + c).sqrt();
    let b = t.sqrt();
    let amb = c / (a + b); // a - b
    let mut sum = 0.0;
    for k in 0..m {
        sum += a.powi(m - 1 - k) * b.powi(k);
    }
    amb * sum / (a.powi(m) * b.powi(m))
}

#[derive(Clone, Debug)]
pub enum Kernel {
    /// `exp(-alpha t)` (K1)
    Gauss { alpha: f64 },
    /// `exp(-kappa r)/r` (K2)
    Yukawa { kappa: f64 },
    /// `t^(-s/2) exp(-eps t)` (K3 with `s = 3`, `eps = 0.02`; K5 with `eps = 0`)
    Riesz { s: f64, eps: f64 },
    /// `2[t^(-1/2) - (t+d²)^(-1/2)] exp(-eps t)` (K4 with `eps = 0.02`; K6 with `eps = 0`), units e²/(4πε₀ε) = 1
    Bilayer { d: f64, eps: f64 },
    /// `exp(-a t²)` (N1, generalised exponential model of index 4)
    Gem { a: f64 },
}

impl Kernel {
    pub fn g(&self, t: f64) -> f64 {
        match *self {
            Kernel::Gauss { alpha } => (-alpha * t).exp(),
            Kernel::Yukawa { kappa } => {
                let r = t.sqrt();
                (-kappa * r).exp() / r
            }
            Kernel::Riesz { s, eps } => t.powf(-0.5 * s) * (-eps * t).exp(),
            Kernel::Bilayer { d, eps } => 2.0 * diff_pow(t, d * d, 1) * (-eps * t).exp(),
            Kernel::Gem { a } => (-a * t * t).exp(),
        }
    }

    /// `dg/dt`
    pub fn g1(&self, t: f64) -> f64 {
        match *self {
            Kernel::Gauss { alpha } => -alpha * (-alpha * t).exp(),
            Kernel::Yukawa { kappa } => {
                let r = t.sqrt();
                -(-kappa * r).exp() * (1.0 + kappa * r) / (2.0 * r * r * r)
            }
            Kernel::Riesz { s, eps } => {
                let p = 0.5 * s;
                self.g(t) * (-p / t - eps)
            }
            Kernel::Bilayer { d, eps } => {
                let c = d * d;
                let b = 2.0 * diff_pow(t, c, 1);
                let b1 = -diff_pow(t, c, 3);
                (b1 - eps * b) * (-eps * t).exp()
            }
            Kernel::Gem { a } => -2.0 * a * t * (-a * t * t).exp(),
        }
    }

    /// `d²g/dt²`
    pub fn g2(&self, t: f64) -> f64 {
        match *self {
            Kernel::Gauss { alpha } => alpha * alpha * (-alpha * t).exp(),
            Kernel::Yukawa { kappa } => {
                let r = t.sqrt();
                (-kappa * r).exp() * (kappa * kappa * r * r + 3.0 * kappa * r + 3.0) / (4.0 * r.powi(5))
            }
            Kernel::Riesz { s, eps } => {
                let p = 0.5 * s;
                let q = -p / t - eps;
                self.g(t) * (q * q + p / (t * t))
            }
            Kernel::Bilayer { d, eps } => {
                let c = d * d;
                let b = 2.0 * diff_pow(t, c, 1);
                let b1 = -diff_pow(t, c, 3);
                let b2 = 1.5 * diff_pow(t, c, 5);
                (b2 - 2.0 * eps * b1 + eps * eps * b) * (-eps * t).exp()
            }
            Kernel::Gem { a } => (4.0 * a * a * t * t - 2.0 * a) * (-a * t * t).exp(),
        }
    }

    /// Continuum tail per particle, `½ ρ ∫_{r>rc} φ(r) d²r`, for the undamped algebraic kernels (zero otherwise).
    pub fn tail_per_particle(&self, rho: f64, rc: f64) -> f64 {
        match *self {
            Kernel::Riesz { s, eps } if eps == 0.0 && s == 3.0 => std::f64::consts::PI * rho / rc,
            Kernel::Bilayer { d, eps } if eps == 0.0 => {
                2.0 * std::f64::consts::PI * rho * ((rc * rc + d * d).sqrt() - rc)
            }
            _ => 0.0,
        }
    }
}

/// The registered kernels by id.
pub fn by_id(id: &str) -> Option<(Kernel, f64)> {
    // (kernel, r_cut)
    Some(match id {
        "K1" => (Kernel::Gauss { alpha: 1.0 }, 6.5),
        "K2" => (Kernel::Yukawa { kappa: 1.0 }, 42.0),
        "K3" => (Kernel::Riesz { s: 3.0, eps: 0.02 }, 46.0),
        "K4" => (Kernel::Bilayer { d: 1.0, eps: 0.02 }, 46.0),
        "K5" => (Kernel::Riesz { s: 3.0, eps: 0.0 }, 60.0),
        "K6" => (Kernel::Bilayer { d: 1.0, eps: 0.0 }, 60.0),
        "N1" => (Kernel::Gem { a: 1.0 }, 2.8),
        _ => return None,
    })
}
