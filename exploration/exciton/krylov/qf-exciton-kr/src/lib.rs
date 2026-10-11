//! Matrix-free implicit solver for the Phase 3 driven-dissipative GPE of `exploration/exciton/rust/qf-exciton-p1/src/bin/dd.rs`
//! (same equations and parameters) on an M x M periodic grid, any power-of-two M.
//!
//! * [`fft`]: radix-2 2-D FFT for any power-of-two size.
//! * [`model`]: right-hand side, exact Jacobian action, observables, initial states.
//! * [`sdirk`]: L-stable SDIRK2 with embedded error estimate, Newton-Krylov stage solves (GMRES of the pinned sundials-core),
//!   structure-exploiting block preconditioner.
pub mod fft;
pub mod model;
pub mod sdirk;
