//! Driven-dissipative GPE with incoherent reservoir (same equations as dd.rs of qf-exciton-p1).
//! State layout `[a (NN), b (NN), r (NN)]`, psi = a + i b, r = n_R.
//!   psi' = -i (K psi + (V + g|psi|^2 + g_R n_R) psi) + 1/2 (R n_R - gamma) psi + i Om psi,   K = -1/2 lap (spectral)
//!   n_R' = P - (gamma_R + R |psi|^2) n_R
use crate::fft::Fft2;
use std::sync::atomic::{AtomicU64, Ordering};
use std::f64::consts::PI;

#[derive(Clone, Copy, Debug)]
pub struct Par {
    pub g: f64,
    pub gr: f64,
    pub gamma: f64,
    pub gamma_r: f64,
    pub r: f64,
    pub r_psi: f64, // R as seen by the psi equation (equal to r unless a bug is planted)
    pub p: f64,
}

impl Par {
    pub fn reg() -> Par {
        Par { g: 0.04, gr: 1.0, gamma: 0.1, gamma_r: 200.0, r: 1.0, r_psi: 1.0, p: 21.0 }
    }
}

pub struct SplitMix64(pub u64);
impl SplitMix64 {
    pub fn next_u64(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }
    pub fn uniform(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 / (1u64 << 53) as f64
    }
}

pub struct Model {
    pub m: usize,
    pub nn: usize,
    pub ny: usize,
    pub l: f64,
    pub h: f64,
    pub sigma: f64,
    pub k2: Vec<f64>,
    pub v: Vec<f64>,
    pub par: Par,
    pub fft: Fft2,
    pub nrhs: AtomicU64,
    pub njv: AtomicU64,
    pub nprec: AtomicU64,
    /// planted bug in the analytic Jacobian action (K-d): sign of the n_R coupling term in the psi rows flipped
    pub jac_bug: bool,
}

pub fn mfreq(i: usize, m: usize) -> i32 {
    if i > m / 2 {
        i as i32 - m as i32
    } else {
        i as i32
    }
}

/// Gaussian gate centred on node (m/2, m/2), periodic minimum image, physical width `sigma`, grid spacing `h`.
pub fn gate(m: usize, h: f64, v0: f64, sigma: f64) -> Vec<f64> {
    let mut v = vec![0.0; m * m];
    let mm = m as f64;
    for x in 0..m {
        for y in 0..m {
            let dx = (x as f64 - mm / 2.0).abs();
            let dy = (y as f64 - mm / 2.0).abs();
            let dx = dx.min(mm - dx) * h;
            let dy = dy.min(mm - dy) * h;
            v[x * m + y] = v0 * (-(dx * dx + dy * dy) / (2.0 * sigma * sigma)).exp();
        }
    }
    v
}

impl Model {
    pub fn new(m: usize, l: f64, sigma: f64, v0: f64, par: Par) -> Model {
        let h = l / m as f64;
        let mut k2 = vec![0.0; m * m];
        for i in 0..m {
            for j in 0..m {
                let kx = 2.0 * PI * mfreq(i, m) as f64 / l;
                let ky = 2.0 * PI * mfreq(j, m) as f64 / l;
                k2[i * m + j] = kx * kx + ky * ky;
            }
        }
        Model {
            m,
            nn: m * m,
            ny: 3 * m * m,
            l,
            h,
            sigma,
            k2,
            v: gate(m, h, v0, sigma),
            par,
            fft: Fft2::new(m),
            nrhs: AtomicU64::new(0),
            njv: AtomicU64::new(0),
            nprec: AtomicU64::new(0),
            jac_bug: false,
        }
    }

    /// `K psi = -1/2 lap psi` for psi = (re, im)
    pub fn kin(&self, re: &[f64], im: &[f64], kr: &mut [f64], ki: &mut [f64]) {
        kr.copy_from_slice(re);
        ki.copy_from_slice(im);
        self.fft.fft2(kr, ki, false);
        for i in 0..self.nn {
            kr[i] *= 0.5 * self.k2[i];
            ki[i] *= 0.5 * self.k2[i];
        }
        self.fft.fft2(kr, ki, true);
    }

    /// right-hand side in the frame rotating at `om`
    pub fn rhs(&self, y: &[f64], yd: &mut [f64], om: f64) {
        self.nrhs.fetch_add(1, Ordering::Relaxed);
        let nn = self.nn;
        let p = &self.par;
        let (re, rest) = y.split_at(nn);
        let (im, nr) = rest.split_at(nn);
        let mut kr = vec![0.0; nn];
        let mut ki = vec![0.0; nn];
        self.kin(re, im, &mut kr, &mut ki);
        for i in 0..nn {
            let n = re[i] * re[i] + im[i] * im[i];
            let w = self.v[i] + p.g * n + p.gr * nr[i];
            let hr = kr[i] + w * re[i];
            let hi = ki[i] + w * im[i];
            let gain = 0.5 * (p.r_psi * nr[i] - p.gamma);
            yd[i] = hi + gain * re[i] - om * im[i];
            yd[nn + i] = -hr + gain * im[i] + om * re[i];
            yd[2 * nn + i] = p.p - (p.gamma_r + p.r * n) * nr[i];
        }
    }

    pub fn rhs_vec(&self, y: &[f64], om: f64) -> Vec<f64> {
        let mut yd = vec![0.0; self.ny];
        self.rhs(y, &mut yd, om);
        yd
    }

    /// exact action of the Jacobian d rhs / d y at `y` on `dv`
    pub fn jv(&self, y: &[f64], dv: &[f64], out: &mut [f64], om: f64) {
        self.njv.fetch_add(1, Ordering::Relaxed);
        let nn = self.nn;
        let p = &self.par;
        let (a, rest) = y.split_at(nn);
        let (b, r) = rest.split_at(nn);
        let (da, drest) = dv.split_at(nn);
        let (db, dr) = drest.split_at(nn);
        let mut kr = vec![0.0; nn];
        let mut ki = vec![0.0; nn];
        self.kin(da, db, &mut kr, &mut ki);
        let sgn = if self.jac_bug { -1.0 } else { 1.0 };
        for i in 0..nn {
            let n = a[i] * a[i] + b[i] * b[i];
            let w = self.v[i] + p.g * n + p.gr * r[i];
            let gain = 0.5 * (p.r_psi * r[i] - p.gamma);
            let dn = 2.0 * (a[i] * da[i] + b[i] * db[i]);
            let dw = p.g * dn + p.gr * dr[i];
            let dgain = sgn * 0.5 * p.r_psi * dr[i];
            out[i] = ki[i] + w * db[i] + dw * b[i] + gain * da[i] + dgain * a[i] - om * db[i];
            out[nn + i] = -kr[i] - w * da[i] - dw * a[i] + gain * db[i] + dgain * b[i] + om * da[i];
            out[2 * nn + i] = -(p.gamma_r + p.r * n) * dr[i] - p.r * dn * r[i];
        }
    }

    /// pointwise 3x3 block `Jloc` of the Jacobian (everything except the kinetic term), row-major, per site:
    /// rows (a', b', r'), columns (a, b, r)
    pub fn jloc(&self, y: &[f64], i: usize, om: f64) -> [[f64; 3]; 3] {
        let nn = self.nn;
        let p = &self.par;
        let (a, b, r) = (y[i], y[nn + i], y[2 * nn + i]);
        let n = a * a + b * b;
        let w = self.v[i] + p.g * n + p.gr * r;
        let gain = 0.5 * (p.r_psi * r - p.gamma);
        let hp = 0.5 * p.r_psi;
        [
            [gain + 2.0 * p.g * a * b, w - om + 2.0 * p.g * b * b, p.gr * b + hp * a],
            [-w + om - 2.0 * p.g * a * a, gain - 2.0 * p.g * a * b, -p.gr * a + hp * b],
            [-2.0 * p.r * r * a, -2.0 * p.r * r * b, -(p.gamma_r + p.r * n)],
        ]
    }
}

pub fn state_uniform(nn: usize, n: f64, nr: f64, noise: f64, seed: u64) -> Vec<f64> {
    let mut rng = SplitMix64(seed);
    let mut y = vec![0.0; 3 * nn];
    for i in 0..nn {
        y[i] = n.sqrt() * (1.0 + noise * (2.0 * rng.uniform() - 1.0));
    }
    for i in 0..nn {
        y[nn + i] = n.sqrt() * noise * (2.0 * rng.uniform() - 1.0);
    }
    for i in 0..nn {
        y[2 * nn + i] = nr;
    }
    y
}

pub struct Obs {
    pub mean_n: f64,
    pub mean_nr: f64,
    pub std_n: f64,
    pub omega: f64,
    pub resid: f64,
    pub norm2: f64,
    pub budget_rel: f64,
    pub n_center: f64,
    pub n_corner: f64,
    pub max_j: f64,
}

/// observables of dd.rs (lab frame, om = 0)
pub fn observe(model: &Model, y: &[f64]) -> Obs {
    let nn = model.nn;
    let m = model.m;
    let yd = model.rhs_vec(y, 0.0);
    let (re, rest) = y.split_at(nn);
    let (im, nr) = rest.split_at(nn);
    let n: Vec<f64> = (0..nn).map(|i| re[i] * re[i] + im[i] * im[i]).collect();
    let norm2: f64 = n.iter().sum();
    let mean_n = norm2 / nn as f64;
    let mean_nr = nr.iter().sum::<f64>() / nn as f64;
    let std_n = (n.iter().map(|v| (v - mean_n) * (v - mean_n)).sum::<f64>() / nn as f64).sqrt();
    let im_ov: f64 = (0..nn).map(|i| re[i] * yd[nn + i] - im[i] * yd[i]).sum();
    let omega = -im_ov / norm2;
    let mut r2 = 0.0;
    for i in 0..nn {
        let a = yd[i] - omega * im[i];
        let b = yd[nn + i] + omega * re[i];
        r2 += a * a + b * b;
    }
    let p = &model.par;
    let gain_budget = nn as f64 * p.p;
    let loss: f64 = (0..nn).map(|i| p.gamma_r * nr[i] + p.gamma * n[i]).sum();
    // current j = Im(conj(psi) grad psi), spectral gradient with the Nyquist frequency zeroed (as dd.rs)
    let mut pr = re.to_vec();
    let mut pi = im.to_vec();
    model.fft.fft2(&mut pr, &mut pi, false);
    let (mut ar, mut ai, mut br, mut bi) = (vec![0.0; nn], vec![0.0; nn], vec![0.0; nn], vec![0.0; nn]);
    for i in 0..m {
        for j in 0..m {
            let mut kx = 2.0 * PI * mfreq(i, m) as f64 / model.l;
            let mut ky = 2.0 * PI * mfreq(j, m) as f64 / model.l;
            if i == m / 2 {
                kx = 0.0;
            }
            if j == m / 2 {
                ky = 0.0;
            }
            let idx = i * m + j;
            ar[idx] = -kx * pi[idx];
            ai[idx] = kx * pr[idx];
            br[idx] = -ky * pi[idx];
            bi[idx] = ky * pr[idx];
        }
    }
    model.fft.fft2(&mut ar, &mut ai, true);
    model.fft.fft2(&mut br, &mut bi, true);
    let mut max_j: f64 = 0.0;
    for i in 0..nn {
        let jx = re[i] * ai[i] - im[i] * ar[i];
        let jy = re[i] * bi[i] - im[i] * br[i];
        max_j = max_j.max((jx * jx + jy * jy).sqrt());
    }
    Obs {
        mean_n,
        mean_nr,
        std_n,
        omega,
        resid: r2.sqrt() / norm2.sqrt(),
        norm2,
        budget_rel: (gain_budget - loss).abs() / gain_budget,
        n_center: n[(m / 2) * m + m / 2],
        n_corner: n[0],
        max_j,
    }
}

pub fn obs_json(o: &Obs) -> String {
    format!(
        "\"mean_n\":{:.17e},\"mean_nr\":{:.17e},\"std_n\":{:.6e},\"omega\":{:.17e},\"resid_rel\":{:.6e},\"norm2\":{:.17e},\"budget_rel\":{:.6e},\"n_center\":{:.12e},\"n_corner\":{:.12e},\"max_j\":{:.6e}",
        o.mean_n, o.mean_nr, o.std_n, o.omega, o.resid, o.norm2, o.budget_rel, o.n_center, o.n_corner, o.max_j
    )
}
