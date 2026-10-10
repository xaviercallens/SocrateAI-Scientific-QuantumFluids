# Exciton fluids, Phase 2 (mean field with a nonlocal kernel): pre-registration

**Status: REGISTERED BEFORE ANY PHASE 2 RUN.** Date 2026-10-10 (night). Parent: `docs/designs/EXCITON_FLUID_LEAN_SOLVER_PLAN.md` §5 WP5,
gates EX-3 and EX-4; Phase 1: `docs/designs/EXCITON_FLUID_PHASE1_PREREG.md`. Independent reference numbers:
`exploration/exciton/python/phase2_reference.py` (written and run before the Rust program), `results/phase2/reference.json`.

What is tested. The Lean statement `uniform_minimises` and the plan's §3.3 (C2): for a kernel with non-negative Fourier transform,
the Gross–Pitaevskii minimiser is uniform and the Bogoliubov spectrum is `ω_k² = ε_k(ε_k + 2 n₀ Ũ(k))`, `ε_k = k²/2` (`ħ = m = 1`).
The solver is rusty-SUNDIALS CVODE (BDF) on the pinned tree `996aaf0706e1`; a 16×16 field is 256 real unknowns, within the dense
Newton solver's reach (the plan's §3.5 constraint).

## Model

Periodic square box `L = 16`, grid `16×16` (`h = 1`), real or complex field `ψ`, spectral kinetic term (`k = 2πm/L`),
interaction by convolution in Fourier space: `(U∗n)(x) = L⁻² Σ_k Ũ(k) n̂_k e^{ikx}`. Chemical potential `μ = 0.25`.

| id | `Ũ(k)` | role |
|---|---|---|
| B | `4π(1 − e^{−kd})/k`, `d = 1`, `Ũ(0) = 4πd` | the bilayer direct kernel (completely monotone in `r²`, so `Ũ ≥ 0`) |
| C | `Ũ_B(k) − 40 exp(−(k − k₀)²/(2·0.2²))`, `k₀ = 2π·3/L = 1.1781` | control: a negative Fourier band (not completely monotone) |

Uniform state: `n₀ = μ/Ũ(0)`; grand-potential density `ω₀ = −μ²/(2Ũ(0))`.

## Gates

* **P2-a (uniform minimiser, kernel B).** Imaginary-time flow `ψ̇ = −(−½∇² + U∗|ψ|² − μ)ψ` from 50 random positive fields
  (`ψ ∈ U(0.05, 0.4)` pointwise, seeds 1..50), CVODE BDF `rtol = 1e-12`, `atol = 1e-14`, until `max|ψ̇| < 1e-12`
  or `τ = 2·10⁴`: every run ends with `max|n − n₀|/n₀ ≤ 1e-8` and a grand-potential density within `1e-10`
  (relative) of `ω₀`.
* **P2-b (Bogoliubov spectrum, kernel B).** For each of the 255 nonzero grid wavenumbers, the solver's linearisation (central
  differences of the real-time right-hand side `−i[(−½∇² + U∗|ψ|² − μ)ψ]` about `√n₀`, applied to `cos(k·x)` and `i cos(k·x)`) has
  frequencies within relative `1e-6` of `ω_k = √(ε_k(ε_k + 2n₀Ũ(k)))`, and zero real part within `1e-8`.
* **P2-c (control, kernel C).** (i) the same linearisation reproduces `ω_k²` of the formula to `1e-6` relative or absolute `1e-9`,
  with `ω_k² < 0` at (and only at) the wavenumbers where the formula predicts it; (ii) an imaginary-time flow from the uniform
  state plus noise of relative amplitude `1e-3` develops a density modulation, `max|n − n̄|/n̄ ≥ 0.1`, and ends with a grand
  potential below `ω₀` by at least `1e-3` relative.
* **P2-d (planted bug).** A kernel table with `Ũ(0)` multiplied by `2` must violate P2-a.

## Not in this phase

Dipole-gated kernels, finite temperature, vortices (`qf-pgpe`), real-time nonlinear dynamics, and any comparison with data.
