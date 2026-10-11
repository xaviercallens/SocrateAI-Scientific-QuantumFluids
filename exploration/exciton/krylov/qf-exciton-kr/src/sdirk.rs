//! L-stable two-stage SDIRK2 (Alexander; gamma = 1 - 1/sqrt 2, stiffly accurate) with the embedded first-order estimate
//! `E = Y2 - y - h f(Y1)` (no extra right-hand-side evaluation), variable step. Stage equations
//! `Y - base - h gamma f(Y) = 0` are solved by inexact Newton with matrix-free GMRES (`sundials_core::gmres`, right
//! preconditioning, so the GMRES residual is the true residual). Jacobian-vector products: exact analytic action or
//! directional finite difference.
use crate::model::Model;
use sundials_core::gmres::{gmres_preconditioned, GmresConfig, GmresStatus};

pub const GAMMA: f64 = 0.292_893_218_813_452_5; // 1 - 1/sqrt(2)

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum PrecMode {
    /// identity
    None,
    /// Fourier-diagonal kinetic factor (1 + i s k^2/2)^-1 and pointwise reservoir factor (1 + s(gamma_R + R|psi|^2))^-1
    Kin,
    /// as `Kin` followed by the full pointwise 3x3 block inverse (I - s Jloc)^-1
    Block,
    /// `Block` with s -> -s (planted bug K-d)
    BadSign,
}

#[derive(Clone, Debug)]
pub struct Opts {
    pub rtol: f64,
    pub atol: f64,
    pub hmax: f64,
    pub hmin: f64,
    pub prec: PrecMode,
    pub exact_jv: bool,
    /// Newton convergence: wrms(delta) < kappa
    pub kappa: f64,
    /// inexact Newton forcing: GMRES absolute tolerance = eta * |G|_2
    pub eta: f64,
    pub restart: usize,
    pub max_restarts: usize,
    pub max_newton: usize,
    pub fixed_h: Option<f64>,
    pub max_steps: u64,
}

impl Default for Opts {
    fn default() -> Self {
        Opts {
            rtol: 1e-6,
            atol: 1e-9,
            hmax: 1e9,
            hmin: 1e-12,
            prec: PrecMode::Block,
            exact_jv: true,
            kappa: 0.05,
            eta: 0.05,
            restart: 20,
            max_restarts: 2,
            max_newton: 8,
            fixed_h: None,
            max_steps: u64::MAX,
        }
    }
}

#[derive(Clone, Debug, Default)]
pub struct Stats {
    pub steps: u64,
    pub rej_err: u64,
    pub rej_newton: u64,
    pub newton: u64,
    pub gmres: u64,
}

pub struct Stepper {
    pub t: f64,
    pub h: f64,
    pub stats: Stats,
}

fn norm2(v: &[f64]) -> f64 {
    v.iter().map(|x| x * x).sum::<f64>().sqrt()
}

fn wrms(v: &[f64], ewt: &[f64]) -> f64 {
    (v.iter().zip(ewt).map(|(x, w)| (x * w) * (x * w)).sum::<f64>() / v.len() as f64).sqrt()
}

/// solve the 3x3 system A x = rhs by Cramer
fn solve3(a: &[[f64; 3]; 3], rhs: [f64; 3]) -> [f64; 3] {
    let det = a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]);
    let id = 1.0 / det;
    let c = |col: usize| -> f64 {
        let mut mm = *a;
        for r in 0..3 {
            mm[r][col] = rhs[r];
        }
        (mm[0][0] * (mm[1][1] * mm[2][2] - mm[1][2] * mm[2][1]) - mm[0][1] * (mm[1][0] * mm[2][2] - mm[1][2] * mm[2][0])
            + mm[0][2] * (mm[1][0] * mm[2][1] - mm[1][1] * mm[2][0]))
            * id
    };
    [c(0), c(1), c(2)]
}

/// apply the preconditioner M^-1 ~ (I - s J)^-1 at state `y`
pub fn apply_prec(model: &Model, mode: PrecMode, y: &[f64], om: f64, s_step: f64, u: &[f64], out: &mut [f64]) {
    model.nprec.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    let nn = model.nn;
    if mode == PrecMode::None {
        out.copy_from_slice(u);
        return;
    }
    let s = if mode == PrecMode::BadSign { -s_step } else { s_step };
    let (ur, rest) = u.split_at(nn);
    let (ui, ur_res) = rest.split_at(nn);
    let mut pr = ur.to_vec();
    let mut pi = ui.to_vec();
    model.fft.fft2(&mut pr, &mut pi, false);
    for i in 0..nn {
        let d = 0.5 * s * model.k2[i];
        let den = 1.0 + d * d;
        let (c, dd) = (1.0 / den, d / den);
        let (a, b) = (pr[i], pi[i]);
        pr[i] = a * c + b * dd;
        pi[i] = b * c - a * dd;
    }
    model.fft.fft2(&mut pr, &mut pi, true);
    let p = &model.par;
    match mode {
        PrecMode::Kin => {
            out[..nn].copy_from_slice(&pr);
            out[nn..2 * nn].copy_from_slice(&pi);
            for i in 0..nn {
                let n = y[i] * y[i] + y[nn + i] * y[nn + i];
                out[2 * nn + i] = ur_res[i] / (1.0 + s * (p.gamma_r + p.r * n));
            }
        }
        _ => {
            for i in 0..nn {
                let j = model.jloc(y, i, om);
                let mut a = [[0.0; 3]; 3];
                for r in 0..3 {
                    for c in 0..3 {
                        a[r][c] = if r == c { 1.0 } else { 0.0 } - s * j[r][c];
                    }
                }
                let x = solve3(&a, [pr[i], pi[i], ur_res[i]]);
                out[i] = x[0];
                out[nn + i] = x[1];
                out[2 * nn + i] = x[2];
            }
        }
    }
}

impl Stepper {
    pub fn new(h0: f64) -> Stepper {
        Stepper { t: 0.0, h: h0, stats: Stats::default() }
    }

    /// inexact Newton on `Y - base - s f(Y) = 0`
    fn stage(&mut self, model: &Model, om: f64, opts: &Opts, base: &[f64], s: f64, guess: &[f64], ewt: &[f64]) -> Result<Vec<f64>, String> {
        let ny = model.ny;
        let mut y = guess.to_vec();
        let mut dn_prev = f64::INFINITY;
        for it in 0..opts.max_newton {
            self.stats.newton += 1;
            let f = model.rhs_vec(&y, om);
            let g: Vec<f64> = (0..ny).map(|i| y[i] - base[i] - s * f[i]).collect();
            let gn = norm2(&g);
            let b: Vec<f64> = g.iter().map(|v| -v).collect();
            let mut dx = vec![0.0; ny];
            if gn > 0.0 {
                let ynorm = norm2(&y);
                let yc = y.clone();
                let fc = f.clone();
                let exact = opts.exact_jv;
                let matvec = |v: &[f64], out: &mut [f64]| {
                    if exact {
                        model.jv(&yc, v, out, om);
                    } else {
                        let vn = norm2(v);
                        if vn == 0.0 {
                            out.iter_mut().for_each(|o| *o = 0.0);
                        } else {
                            let eps = 1.4901161193847656e-8 * (1.0 + ynorm) / vn;
                            let yp: Vec<f64> = (0..ny).map(|i| yc[i] + eps * v[i]).collect();
                            let fp = model.rhs_vec(&yp, om);
                            for i in 0..ny {
                                out[i] = (fp[i] - fc[i]) / eps;
                            }
                        }
                    }
                    for i in 0..ny {
                        out[i] = v[i] - s * out[i];
                    }
                };
                let cfg = GmresConfig { max_restarts: opts.max_restarts, restart: opts.restart, tol: (opts.eta * gn).max(1e-300) };
                let ident = |v: &[f64], o: &mut [f64]| o.copy_from_slice(v);
                let yc2 = y.clone();
                let prec = |v: &[f64], o: &mut [f64]| apply_prec(model, opts.prec, &yc2, om, s, v, o);
                let status = gmres_preconditioned(matvec, &b, &mut dx, &cfg, ident, prec);
                match status {
                    GmresStatus::Converged { iters, .. } => self.stats.gmres += iters as u64,
                    GmresStatus::MaxItersReached { res_norm } => {
                        self.stats.gmres += ((opts.max_restarts + 1) * opts.restart) as u64;
                        if !(res_norm < 0.5 * gn) {
                            return Err("gmres stalled".into());
                        }
                    }
                }
            }
            for i in 0..ny {
                y[i] += dx[i];
            }
            let dn = wrms(&dx, ewt);
            if !dn.is_finite() {
                return Err("non-finite".into());
            }
            if dn < opts.kappa {
                return Ok(y);
            }
            if it > 0 && dn > 2.0 * dn_prev {
                return Err("newton diverging".into());
            }
            dn_prev = dn;
        }
        Err("newton: max iterations".into())
    }

    /// advance `y` (in the frame rotating at `om`) from `self.t` to `t_end`
    pub fn advance(&mut self, model: &Model, y: &mut Vec<f64>, om: f64, t_end: f64, opts: &Opts) -> Result<(), String> {
        let ny = model.ny;
        let mut h_keep = self.h;
        while self.t < t_end * (1.0 - 1e-15) - 1e-300 {
            if self.stats.steps >= opts.max_steps {
                return Err("max_steps".into());
            }
            let mut h = match opts.fixed_h {
                Some(hf) => hf,
                None => self.h.min(opts.hmax),
            };
            let clipped = self.t + h >= t_end - 1e-13 * t_end.abs().max(1.0);
            if clipped {
                h = t_end - self.t;
                if h <= 0.0 {
                    break;
                }
            } else {
                h_keep = h;
            }
            let s = h * GAMMA;
            let ewt: Vec<f64> = y.iter().map(|v| 1.0 / (opts.rtol * v.abs() + opts.atol)).collect();
            let y1 = match self.stage(model, om, opts, y, s, y, &ewt) {
                Ok(v) => v,
                Err(e) => {
                    self.stats.rej_newton += 1;
                    if opts.fixed_h.is_some() || h * 0.25 < opts.hmin {
                        return Err(format!("stage 1 at t={}: {e}", self.t));
                    }
                    self.h = h * 0.25;
                    continue;
                }
            };
            let f1: Vec<f64> = (0..ny).map(|i| (y1[i] - y[i]) / s).collect();
            let base2: Vec<f64> = (0..ny).map(|i| y[i] + h * (1.0 - GAMMA) * f1[i]).collect();
            let y2 = match self.stage(model, om, opts, &base2, s, &y1, &ewt) {
                Ok(v) => v,
                Err(e) => {
                    self.stats.rej_newton += 1;
                    if opts.fixed_h.is_some() || h * 0.25 < opts.hmin {
                        return Err(format!("stage 2 at t={}: {e}", self.t));
                    }
                    self.h = h * 0.25;
                    continue;
                }
            };
            if opts.fixed_h.is_some() {
                y.copy_from_slice(&y2);
                self.t += h;
                self.stats.steps += 1;
                continue;
            }
            let e: Vec<f64> = (0..ny).map(|i| y2[i] - y[i] - h * f1[i]).collect();
            let err = wrms(&e, &ewt);
            if std::env::var("QF_DEBUG").is_ok() && self.stats.steps % 2000 == 0 {
                let nn = model.nn;
                let part = |lo: usize, hi: usize| (e[lo..hi].iter().zip(&ewt[lo..hi]).map(|(x, w)| (x * w).powi(2)).sum::<f64>() / ny as f64).sqrt();
                eprintln!("t={:.4} h={:.3e} err={:.3e} a={:.3e} b={:.3e} r={:.3e}", self.t, h, err, part(0, nn), part(nn, 2 * nn), part(2 * nn, ny));
            }
            let fac = (0.9 * err.max(1e-10).powf(-0.5)).clamp(0.2, 4.0);
            if err <= 1.0 {
                y.copy_from_slice(&y2);
                self.t += h;
                self.stats.steps += 1;
                self.h = if clipped { h_keep * fac.min(1.0) } else { h * fac };
            } else {
                self.stats.rej_err += 1;
                self.h = h * fac.min(0.9);
                if self.h < opts.hmin {
                    return Err(format!("step size below hmin at t={}", self.t));
                }
            }
        }
        Ok(())
    }
}
