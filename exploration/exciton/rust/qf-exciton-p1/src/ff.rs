//! The four-flavour mean-field model of Qi et al. (Nature 654, 2026; arXiv:2603.15443), Eqs. (2)-(3), and its
//! imaginary-time flow on rusty-SUNDIALS CVODE.
//!
//! `H(n) = Σ (E_i − μ) n_i + (g_H + g_X)/2 (Σ n_i)² − g_X (n₀n₁ + n₂n₃)`, `n_i = ψ_i²`, flavours
//! `0..3 = KK, K'K', KK', K'K`.  Units: Rydberg (67 meV) and Bohr radius (1.5 nm) of the paper.
use cvode::{Cvode, DenseMat, Method, Task};
use nvector::SerialVector;
use std::f64::consts::PI;

pub const PARTNER: [usize; 4] = [1, 0, 3, 2];

#[derive(Clone, Debug)]
pub struct FfParams {
    pub gh: f64,
    pub gx: f64,
    pub delta: f64,
    pub gc: f64,
    pub gv: f64,
    pub mu: f64,
    pub ry_uev: f64,
    pub mub_uev_per_t: f64,
    pub nx: f64,
}

impl FfParams {
    /// The values quoted in the arXiv v1 (phenomenological `g_X`, `Δ`), `n_x = 0.5·10¹² cm⁻²`, `μ` set so that
    /// the intervalley phase at `B = 0` has total density `n_x`.
    pub fn paper() -> Self {
        let ry = 67e3;
        let mub = 57.88;
        let ab = 1.5;
        let d = 2.0;
        let gh = 8.0 * PI * d / ab;
        let gx = 1.0;
        let delta = 1.0 / ry;
        let nx = 0.5e12 * 1e-14 * ab * ab;
        let mu = nx * (2.0 * gh + gx) / 2.0;
        FfParams { gh, gx, delta, gc: 3.0, gv: 6.0, mu, ry_uev: ry, mub_uev_per_t: mub, nx }
    }

    /// `μ_B B` in Rydberg for `B` in tesla.
    pub fn b_ry(&self, b_tesla: f64) -> f64 {
        self.mub_uev_per_t * b_tesla / self.ry_uev
    }

    pub fn energies(&self, b: f64) -> [f64; 4] {
        [
            (self.gv - self.gc) * b - self.delta,
            -(self.gv - self.gc) * b - self.delta,
            -(self.gc + self.gv) * b,
            (self.gc + self.gv) * b,
        ]
    }

    pub fn omega(&self, b: f64, n: &[f64; 4]) -> f64 {
        let e = self.energies(b);
        let nn: f64 = n.iter().sum();
        let lin: f64 = (0..4).map(|i| (e[i] - self.mu) * n[i]).sum();
        lin + 0.5 * (self.gh + self.gx) * nn * nn - self.gx * (n[0] * n[1] + n[2] * n[3])
    }

    /// `h_i = ∂H/∂n_i`
    fn h(&self, b: f64, n: &[f64; 4]) -> [f64; 4] {
        let e = self.energies(b);
        let nn: f64 = n.iter().sum();
        let a = self.gh + self.gx;
        let mut out = [0.0; 4];
        for i in 0..4 {
            out[i] = e[i] - self.mu + a * nn - self.gx * n[PARTNER[i]];
        }
        out
    }

    /// Closed forms of the plan (§3.4): `(N_A, N_B, n₁−n₀ in II_A, n₂−n₃ in II_B, Ω_A, Ω_B)`.
    pub fn closed_forms(&self, b: f64) -> (f64, f64, f64, f64, f64, f64) {
        let d = 2.0 * self.gh + self.gx;
        let na = 2.0 * (self.mu + self.delta) / d;
        let nb = 2.0 * self.mu / d;
        let da = 2.0 * (self.gv - self.gc) * b / self.gx;
        let db = 2.0 * (self.gc + self.gv) * b / self.gx;
        let oa = -(self.mu + self.delta).powi(2) / d - ((self.gv - self.gc) * b).powi(2) / self.gx;
        let ob = -self.mu.powi(2) / d - ((self.gc + self.gv) * b).powi(2) / self.gx;
        (na, nb, da, db, oa, ob)
    }

    pub fn b_critical(&self) -> f64 {
        let d = 2.0 * self.gh + self.gx;
        (self.gx * self.delta * (2.0 * self.mu + self.delta) / (4.0 * self.gc * self.gv * d)).sqrt()
    }

    /// Closed-form spinodal of II_A in `μ_B B` (Rydberg): the empty flavour 2 acquires a negative effective level.
    pub fn b_spinodal_iia(&self) -> f64 {
        let d = 2.0 * self.gh + self.gx;
        (self.gx * self.mu + 2.0 * (self.gh + self.gx) * self.delta) / ((self.gc + self.gv) * d)
    }
}

#[derive(Clone, Debug)]
pub struct FfResult {
    pub psi: [f64; 4],
    pub n: [f64; 4],
    pub omega: f64,
    pub converged: bool,
    pub tau: f64,
    pub steps: usize,
    pub omega_violations: usize,
}

/// Imaginary-time flow `ψ̇_i = −ψ_i h_i` from `psi0` at field `b` (in Rydberg); registered tolerances.
pub fn flow(p: &FfParams, b: f64, psi0: [f64; 4], tau_max: f64) -> Result<FfResult, String> {
    let pr = p.clone();
    let rhs = move |_t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
        let n = [y[0] * y[0], y[1] * y[1], y[2] * y[2], y[3] * y[3]];
        let h = pr.h(b, &n);
        for i in 0..4 {
            yd[i] = -y[i] * h[i];
        }
        Ok(())
    };
    let pj = p.clone();
    let jac = move |_t: f64, y: &[f64], j: &mut DenseMat| -> Result<(), String> {
        let n = [y[0] * y[0], y[1] * y[1], y[2] * y[2], y[3] * y[3]];
        let h = pj.h(b, &n);
        let a = pj.gh + pj.gx;
        for c in 0..4 {
            for r in 0..4 {
                // d(-psi_r h_r)/d psi_c
                let mut v = 0.0;
                if r == c {
                    v -= h[r];
                }
                let dh = 2.0 * a * y[c] - if c == PARTNER[r] { 2.0 * pj.gx * y[c] } else { 0.0 };
                v -= y[r] * dh;
                j.cols[c][r] = v;
            }
        }
        Ok(())
    };
    let mut solver = Cvode::builder(Method::Bdf)
        .rtol(1e-12)
        .atol(1e-16)
        .max_steps(5_000_000)
        .jacobian(jac)
        .build(rhs, 0.0, SerialVector::from_slice(&psi0))
        .map_err(|e| format!("build: {e:?}"))?;
    let chunk = 100.0;
    let mut tau = 0.0;
    let mut converged = false;
    let n0 = [psi0[0].powi(2), psi0[1].powi(2), psi0[2].powi(2), psi0[3].powi(2)];
    let mut om_prev = p.omega(b, &n0);
    let mut viol = 0usize;
    let mut psi = psi0;
    while tau < tau_max {
        tau += chunk;
        let y = {
            let (_, y) = solver.solve(tau, Task::Normal).map_err(|e| format!("solve: {e:?}"))?;
            y.to_vec()
        };
        psi = [y[0], y[1], y[2], y[3]];
        let n = [psi[0].powi(2), psi[1].powi(2), psi[2].powi(2), psi[3].powi(2)];
        let om = p.omega(b, &n);
        if om > om_prev + 1e-9 * om_prev.abs() {
            viol += 1;
        }
        om_prev = om;
        let hh = p.h(b, &n);
        let rate = (0..4).map(|i| (psi[i] * hh[i]).abs()).fold(0.0f64, f64::max);
        if rate < 1e-14 {
            converged = true;
            break;
        }
    }
    let n = [psi[0].powi(2), psi[1].powi(2), psi[2].powi(2), psi[3].powi(2)];
    Ok(FfResult { psi, n, omega: p.omega(b, &n), converged, tau, steps: solver.num_steps(), omega_violations: viol })
}
