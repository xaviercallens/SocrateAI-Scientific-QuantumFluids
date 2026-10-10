//! The triangular lattice of density `rho` and its energy.
use crate::kernel::Kernel;
use crate::rng::SplitMix64;
use crate::torus::Torus;

/// Nearest-neighbour distance of the triangular lattice of density `rho`.
pub fn spacing(rho: f64) -> f64 {
    (2.0 / (3.0f64.sqrt() * rho)).sqrt()
}

/// Squared distances of the nonzero lattice points with `|a| ≤ rmax` (spacing `a`).
///
/// Amendment A1: the first version enumerated `|m|, |k| ≤ rmax/a + 3` and missed the caps `|y| > (√3/2) rmax`; the
/// closed-form KA-1a caught it.
pub fn lattice_t(a: f64, rmax: f64) -> Vec<f64> {
    let h = 3.0f64.sqrt() / 2.0;
    let kmax = (rmax / (a * h)) as i32 + 2;
    let mut out = Vec::new();
    for k in -kmax..=kmax {
        let centre = -0.5 * k as f64;
        let m_lo = (centre - rmax / a).floor() as i32 - 1;
        let m_hi = (centre + rmax / a).ceil() as i32 + 1;
        for m in m_lo..=m_hi {
            if m == 0 && k == 0 {
                continue;
            }
            let x = a * (m as f64 + 0.5 * k as f64);
            let y = a * h * k as f64;
            let t = x * x + y * y;
            if t <= rmax * rmax {
                out.push(t);
            }
        }
    }
    out
}

/// `e_lat = ½ Σ g(|a|²)` over nonzero lattice points `|a| ≤ rc`, plus the kernel's continuum tail.
pub fn e_lat(kernel: &Kernel, rho: f64, rc: f64) -> f64 {
    let a = spacing(rho);
    let s: f64 = lattice_t(a, rc).iter().map(|&t| kernel.g(t)).sum();
    0.5 * s + kernel.tail_per_particle(rho, rc)
}

/// The perfect triangular configuration in the rectangle `nx·a × ny·√3 a` (`2 nx ny` points).
pub fn triangular_config(nx: usize, ny: usize, a: f64) -> Vec<f64> {
    let h = 3.0f64.sqrt() * a;
    let mut x = Vec::with_capacity(4 * nx * ny);
    for iy in 0..ny {
        for ix in 0..nx {
            x.push(ix as f64 * a);
            x.push(iy as f64 * h);
            x.push(ix as f64 * a + 0.5 * a);
            x.push(iy as f64 * h + 0.5 * h);
        }
    }
    x
}

/// Uniform random configuration with a hard-core rejection at `rmin` (minimum-image distance).
pub fn random_start(t: &Torus, rmin: f64, seed: u64) -> Option<Vec<f64>> {
    let mut rng = SplitMix64::new(seed);
    let mut x: Vec<f64> = Vec::with_capacity(2 * t.n);
    let mut attempts = 0usize;
    while x.len() < 2 * t.n {
        attempts += 1;
        if attempts > 10_000 * t.n {
            return None;
        }
        let px = rng.uniform() * t.lx;
        let py = rng.uniform() * t.ly;
        let mut ok = true;
        for k in 0..(x.len() / 2) {
            let mut dx = px - x[2 * k];
            let mut dy = py - x[2 * k + 1];
            dx -= t.lx * (dx / t.lx).round();
            dy -= t.ly * (dy / t.ly).round();
            if dx * dx + dy * dy < rmin * rmin {
                ok = false;
                break;
            }
        }
        if ok {
            x.push(px);
            x.push(py);
        }
    }
    Some(x)
}

/// Basin-hopping perturbation: 6 random particles displaced by `N(0, sigma²)`.
pub fn perturb(t: &Torus, x: &[f64], sigma: f64, seed: u64) -> Vec<f64> {
    let mut rng = SplitMix64::new(seed);
    let mut y = x.to_vec();
    for _ in 0..6 {
        let i = (rng.next_u64() % t.n as u64) as usize;
        y[2 * i] += sigma * rng.normal();
        y[2 * i + 1] += sigma * rng.normal();
    }
    y
}
