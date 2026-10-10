//! Gradient flow `ẋ = −∇(N E)` of N points in a torus, integrated by rusty-SUNDIALS CVODE (BDF, analytic Jacobian).
use crate::torus::Torus;
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
    /// The registered values (pre-registration §4).
    fn default() -> Self {
        FlowOpts { chunk: 5.0, tau_max: 2000.0, fmax_tol: 1e-9, de_tol: 1e-14, rtol: 1e-10, atol: 1e-12 }
    }
}

#[derive(Clone, Debug)]
pub struct FlowResult {
    pub x: Vec<f64>,
    pub e: f64,
    pub fmax: f64,
    pub converged: bool,
    pub tau: f64,
    pub steps: usize,
    pub rhs_evals: usize,
    pub wall_s: f64,
    /// energy at the chunk ends (index 0 = start)
    pub energies: Vec<f64>,
    pub l2_violations: usize,
    pub l2_max_rel_increase: f64,
}

pub fn max_abs(v: &[f64]) -> f64 {
    v.iter().fold(0.0f64, |m, &a| m.max(a.abs()))
}

pub fn relax(torus: &Arc<Torus>, x0: &[f64], o: &FlowOpts) -> Result<FlowResult, String> {
    let t0 = Instant::now();
    let n2 = 2 * torus.n;
    let tr = Arc::clone(torus);
    let rhs = move |_t: f64, y: &[f64], ydot: &mut [f64]| -> Result<(), String> {
        tr.force(y, ydot);
        Ok(())
    };
    let trj = Arc::clone(torus);
    let mut hbuf = vec![0.0f64; n2 * n2];
    let jac = move |_t: f64, y: &[f64], j: &mut DenseMat| -> Result<(), String> {
        trj.hessian(y, &mut hbuf);
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
    let mut energies = vec![torus.energy(x0)];
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
        let e = torus.energy(&y);
        let e_prev = *energies.last().unwrap();
        energies.push(e);
        torus.force(&y, &mut f);
        fmax = max_abs(&f);
        if fmax < o.fmax_tol && (e - e_prev).abs() <= o.de_tol * e.abs() {
            converged = true;
            break;
        }
    }
    let mut x = solver.y().to_vec();
    torus.wrap(&mut x);
    let e = *energies.last().unwrap();
    let mut viol = 0usize;
    let mut maxinc = 0.0f64;
    for w in energies.windows(2) {
        let inc = (w[1] - w[0]) / w[0].abs().max(1e-300);
        if inc > 1e-9 {
            viol += 1;
        }
        if inc > maxinc {
            maxinc = inc;
        }
    }
    Ok(FlowResult {
        x,
        e,
        fmax,
        converged,
        tau,
        steps: solver.num_steps(),
        rhs_evals: solver.num_rhs_evals(),
        wall_s: t0.elapsed().as_secs_f64(),
        energies,
        l2_violations: viol,
        l2_max_rel_increase: maxinc,
    })
}
