//! Phase 1 of `docs/designs/EXCITON_FLUID_LEAN_SOLVER_PLAN.md` (pre-registration:
//! `docs/designs/EXCITON_FLUID_PHASE1_PREREG.md`).
//!
//! * [`kernel`]: pair kernels `g(t)`, `t = r²`, with exact first and second derivatives.
//! * [`torus`]: periodic energy, force and Hessian of N points in a rectangular torus (images summed, self-images included).
//! * [`flow`]: gradient flow `ẋ = −∇E` integrated by rusty-SUNDIALS CVODE (BDF) with the analytic Jacobian.
//! * [`ff`]: the four-flavour mean-field model of Qi et al. (Nature 654, 2026) and its imaginary-time flow.
pub mod ff;
pub mod flow;
pub mod kernel;
pub mod lattice;
pub mod rng;
pub mod torus;
pub mod util;
