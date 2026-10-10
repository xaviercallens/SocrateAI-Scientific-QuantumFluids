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
| C | `Ũ_B(k) − 28 exp(−(k − k₀)²/(2·0.2²))`, `k₀ = 2π·3/L = 1.1781` | control: a negative Fourier band (not completely monotone) |

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

## Amendments

**A1 (written into this file 2026-10-10 about 23:16, 36 seconds after `363475b` and before the run started; committed only with the results, `3203d78`, 2026-10-11 00:09; the registered depth in `363475b` was 40).** The control depth was first written as 40. At that depth `½Ũ(0) + ¼Ũ(k₀) < 0`, so a fully
modulated density has an energy density `∝ n̄²` with a negative coefficient: the grand-canonical functional is unbounded below and
the flow would collapse. The depth is `28`, for which `Ũ_C(k₀) = −20.6`: `2n₀Ũ_C(k₀) = −0.82 < −ε_{k₀} = −0.69` (unstable) and
`½Ũ(0) + ¼Ũ(k₀) = 1.1 > 0` (bounded). `reference.json` regenerated; no result had been produced.

**A2 (2026-10-11 00:10, after the registered run; its record is `exploration/exciton/results/phase2/mf_report.json`).**
The registered run gave P2-a, P2-b, P2-c(i) and P2-d as registered (see the results note), but **P2-c(ii) failed as
registered**: the imaginary-time flow of kernel C from uniform + noise ended with a CVODE convergence failure
(`Solver(ConvFailure)`) in the first chunk (`τ ≤ 100`), at a density modulation of `5.8×10⁻³` (gate `≥ 0.1`). That failure stays
on record as the registered result. Because it is a solver-side failure, not a statement about the model, the control flow is
repeated, as an *amended re-run* and labelled as such, with relaxed tolerances `rtol = 1e-9`, `atol = 1e-11` and stopping
criterion `max|Hψ| < 1e-8` (the other gates are not re-run); the gate P2-c(ii) is applied unchanged. Environment variable
`MF_MODE=ctrl_A2` of the same binary; record `mf_report_A2.json`.

**A3 (2026-10-11 00:30, after the A2 re-run, which gave the same failure: 42 193 steps, same state, so it is not a tolerance
matter).** A diagnostic run of the control flow in chunks of `Δτ = 0.5` (exploratory, `MF_MODE=ctrl_debug`, same noise seed,
`rtol = 1e-9`, `atol = 1e-11`; log `results/phase2/mf_debug_trace.txt`) shows what happened: `Ω` decreases monotonically, the density
modulation grows exponentially from `1e-3` at a rate of about `0.12` per unit `τ`, reaches `0.1` near `τ ≈ 38` (with `Ω` below
`Ω₀` by `7×10⁻⁴`, relative) and `4.5` at `τ ≈ 56` (`Ω` about twice `Ω₀`), after which the flow runs away and CVODE
fails (`ConvFailure` in the chunk ending at `τ = 58`). The failure is therefore **physical, not numerical**, and it is a flaw of the control as registered: at fixed `μ`
the grand-canonical functional of kernel C is *unbounded below*. For a stripe of Gaussian profile `c_m = n̄ e^{−m²k₀²w²/2}` the
interaction energy density is `½ n̄² F(w)`, `F(w) = Ũ(0) + 2 Σ_{m≥1} Ũ(m k₀) e^{−m² k₀² w²}`, and
`min_w F = −19.0 < 0` for depth 28 over the harmonics representable on the grid (`m ≤ 2`; `−15.5` when the sum is taken to `m ≤ 8`), so `Ω → −∞` as `n̄` grows. Amendment A1's check
(a cosine profile, `½Ũ(0) + ¼Ũ(k₀) > 0`) was incomplete. Over this kernel family no bounded, linearly unstable control exists at
fixed `μ`: `min_w F` is negative for depth ≳ 18 (`−0.5` at 18, `−3.9` at 20, grid harmonics) while linear instability needs depth > 24.8.

Consequences, stated before they are written up: (i) the gate P2-c(ii) **stays FAILED AS REGISTERED** (the registered run and
the A2 re-run both fail); (ii) the diagnostic is exploratory evidence that the *content* of the gate — the uniform state of a
kernel with a negative Fourier band is not the minimiser, a modulation grows from noise and `Ω` drops below `Ω₀` by more than
`1e-3` — is met before the run-away, and the analytic argument above is stronger (the functional has no minimum); (iii) a
bounded control would need a fixed-mass flow or a regularising term, which is outside Phase 2 and is not run here.
