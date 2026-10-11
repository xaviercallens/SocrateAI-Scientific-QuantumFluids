//! Pair kernels for the L6 edge/frustration design study, in the form needed by the (patched) fenris-cmrr engine.
//!
//! Units: the boundary node spacing is 1. `d` is the interlayer distance, `dd` the gate separation `D`.
//! All kernels are normalised so that the ungated bilayer is `1/r - 1/sqrt(r^2 + d^2)`, i.e. the exciton-exciton
//! kernel `V_ee + V_hh - 2 V_eh` of the note divided by two.

pub mod bessel;
pub mod kernels;

pub use kernels::{Gated, KernelSpec, Phys, Raw, Ungated, YukawaRaw};
