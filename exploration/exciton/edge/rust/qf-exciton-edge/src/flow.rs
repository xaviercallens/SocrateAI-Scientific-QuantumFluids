//! Gradient flow `x' = -grad E_total` on rusty-SUNDIALS CVODE (BDF, analytic Jacobian), chunked as in qf-exciton-p1.
use crate::system::System;
use cvode::{Cvode, DenseMat, Method, Task};
use nvector::SerialVector;
use std::sync::Arc;
use std::time::Instant;

#[derive(Clone, Debug)]
pub struct FlowOpts {
    pub chunk: f64,
    pub tau_max: f64,
    pub fmax_tol: f64,
    pub de_tol: f64,
    pub rtol: f64,
    pub atol: f64,
}
impl Default for FlowOpts {
    /// registered values (PREREG.md section 4)
    fn default() -> Self {
        FlowOpts { chunk: 10.0, tau_max: 4000.0, fmax_tol: 1e-9, de_tol: 1e-14, rtol: 1e-10, atol: 1e-12 }
    }
}

#[derive(Clone, Debug)]
pub struct FlowResult {
    pub x: Vec<f64>,
    pub e: f64,
    pub fmax: f64,
    pub converged: bool,
    pub tau: f64,
    pub rhs_evals: usize,
    pub wall_s: f64,
    pub l2_violations: usize,
}

pub fn max_abs(v: &[f64]) -> f64 {
    v.iter().fold(0.0f64, |m, &a| m.max(a.abs()))
}

pub fn relax(sys: &Arc<System>, x0: &[f64], o: &FlowOpts) -> Result<FlowResult, String> {
    let t0 = Instant::now();
    let n2 = 2 * sys.n;
    let s1 = Arc::clone(sys);
    let rhs = move |_t: f64, y: &[f64], ydot: &mut [f64]| -> Result<(), String> {
        s1.force(y, ydot);
        Ok(())
    };
    let s2 = Arc::clone(sys);
    let mut hbuf = vec![0.0f64; n2 * n2];
    let jac = move |_t: f64, y: &[f64], j: &mut DenseMat| -> Result<(), String> {
        s2.hessian(y, &mut hbuf);
        for c in 0..n2 {
            for r in 0..n2 {
                j.cols[c][r] = -hbuf[c * n2 + r];
            }
        }
        Ok(())
    };
    let mut solver = Cvode::builder(Method::Bdf)
        .rtol(o.rtol)
        .atol(o.atol)
        .max_steps(5_000_000)
        .jacobian(jac)
        .build(rhs, 0.0, SerialVector::from_slice(x0))
        .map_err(|e| format!("build: {e:?}"))?;
    let mut energies = vec![sys.e_total(x0)];
    let mut f = vec![0.0; n2];
    let mut tau = 0.0;
    let mut converged = false;
    let mut fmax = f64::INFINITY;
    while tau < o.tau_max {
        tau += o.chunk;
        let y = {
            let (_, y) = solver.solve(tau, Task::Normal).map_err(|e| format!("solve at tau={tau}: {e:?}"))?;
            y.to_vec()
        };
        let e = sys.e_total(&y);
        let e_prev = *energies.last().unwrap();
        energies.push(e);
        sys.force(&y, &mut f);
        fmax = max_abs(&f);
        if fmax < o.fmax_tol && (e - e_prev).abs() <= o.de_tol * e.abs().max(1e-300) {
            converged = true;
            break;
        }
    }
    let x = solver.y().to_vec();
    let e = sys.e_total(&x);
    let viol = energies.windows(2).filter(|w| (w[1] - w[0]) / w[0].abs().max(1e-300) > 1e-9).count();
    Ok(FlowResult { x, e, fmax, converged, tau, rhs_evals: solver.num_rhs_evals(), wall_s: t0.elapsed().as_secs_f64(), l2_violations: viol })
}
