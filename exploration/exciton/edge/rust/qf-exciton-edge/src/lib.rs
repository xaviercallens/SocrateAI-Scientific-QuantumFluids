//! Edge and frustration study (pre-registration `exploration/exciton/edge/PREREG.md`).
//!
//! * [`kernel`]: radial pair energies `phi(r)` with exact first and second derivatives (analytic dipole, Riesz-3 test kernel,
//!   piecewise-Chebyshev table of the smooth image part of the gated kernel).
//! * [`geom`]: containers (disk, convex polygons by hard wall as a quadratic penalty, harmonic trap).
//! * [`system`]: energy, force and Hessian of N points in a container, open geometry (no images).
//! * [`flow`]: gradient flow `x' = -grad` integrated by rusty-SUNDIALS CVODE (BDF, analytic Jacobian).
pub mod flow;
pub mod geom;
pub mod kernel;
pub mod linalg;
pub mod rng;
pub mod system;
