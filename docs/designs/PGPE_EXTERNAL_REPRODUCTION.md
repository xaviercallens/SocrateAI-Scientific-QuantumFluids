# External reproduction log — what the quantum-fluid solvers of this programme reproduce of other people's published results

Rule: an entry states the reference (DOI, licence), what was compared, with what scheme, the numbers, **and what did not agree**. Nothing here is a claim about a result that was not run.

## 1. Kwon & Shin, flow past a penetrable obstacle (Phys. Rev. Research 2026; Zenodo 10.5281/zenodo.20068724, CC-BY-4.0)

**Reference.** GPU code (CuPy, pseudo-spectral split-step with RK4 linear half-steps, complex64) and one complete run: V₀ = 0.9, σ = 20 ξ, obstacle at x = 100 ξ, flow v = 0.55 reached in 0.1 τ, box 500 × 250 ξ on 1000 × 500 points, dt = 0.01, absorbing layers (γ₀ = 0.1, widths 50 and 40 ξ), ψ snapshots at t = 0, 10, …, 50, the force on the obstacle every 0.1 τ to t = 100, vortex counts every 5 τ to t = 50.
**Model recovered from the code** (`QUANTUM_FLUID_DATASETS_SURVEY_2026-10-09.md`): ∂ₜψ = v(t)∂ₓψ − (i + Γ)[−½∇² + |ψ|² − 1]ψ − iVψ.
**Scheme here (independent of the reference):** explicit RK4 on the full right-hand side, spectral derivatives, double precision, dt = 0.01, **started from the reference's own t = 0 field** (so ground-state preparation is not tested). Implemented twice: numpy (`exploration/external/kwon_shin_reproduction.py`) and Rust (`qf-pgpe::flow`, example `kwon_shin`).

| comparison | result |
|---|---|
| force on the obstacle, t ≤ 0.3 | max \|F − F_ref\| = **1.13×10⁻⁶** (6×10⁻⁶ of max \|F\|), numpy and Rust identical |
| the same with `v` read at RK4 stage times instead of the reference's step-end convention | constant offset **3.5×10⁻³** created during the 0.1 τ ramp (an O(dt) artefact of the reference: Σ v(iΔt)Δt overshoots ∫v dt by 0.00275 ξ) |
| force, t ≤ 10 (numpy, 1000 steps) | max \|F − F_ref\| = **2.2×10⁻⁴** at t = 7.8 (4×10⁻⁵ of max \|F\| = 5.45), growing smoothly (5×10⁻⁶ at t = 1, 6×10⁻⁵ at t = 3, 1.5×10⁻⁴ at t = 5) and decreasing after t ≈ 8 |
| ψ(t = 10) against the reference snapshot (numpy) | relative L2 distance **2.2×10⁻⁴**, max \|Δψ\| = 1.2×10⁻³ |
| Rust at t = 10 | running (same scheme as numpy; to be appended) |

**Reading.** The smooth, monotone growth of the difference is what a systematic discretisation difference looks like (the reference's splitting is second order and its arithmetic single precision; ours is fourth order in time and double): it is not the chaotic divergence of a shedding wake, which in the reference sets in later (vortices first counted at t = 25). Agreement at the 10⁻⁴ level in ψ over 10 τ, for two different schemes, supports the recovered model and the reference run.
**Not tested / not agreeing.** (i) t > 10: ψ snapshots at 20–50 and the vortex counts (0, 0, 0, 0, 0, 2, 3, 2, 4, 6, 7 at t = 0…50) are not yet compared; the wake becomes unstable, so a pass criterion must be statistical (counts, first-shedding time), not pointwise. (ii) The ground state (imaginary-time) is not reproduced. (iii) **Speed:** the Rust engine is not faster than numpy on this 1000 × 500 problem (≈ 0.8 against ≈ 0.9 s per RK4 step single-threaded, both on a loaded machine); the advantage of the square power-of-two engine does not carry over. This size is the natural first GPU/TPU target.
