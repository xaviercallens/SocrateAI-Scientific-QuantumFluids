# Exciton fluids, Phase 3 (driven-dissipative Gross–Pitaevskii with a gate): pre-registration

**Status: REGISTERED BEFORE ANY PHASE 3 RUN OF THE RUST PROGRAM.** Date 2026-10-11. Parents: `EXCITON_FLUID_PHASE1_PREREG.md`,
`EXCITON_FLUID_PHASE2_PREREG.md`. Independent reference numbers: `exploration/exciton/python/phase3_reference.py` (written and run
before the Rust program), `exploration/exciton/results/phase3/reference.json`.

Why this phase exists. The owner's brief (2026-10-11) asked for the *driven-dissipative* GPE of an exciton(-polariton)-like
condensate on rusty-SUNDIALS, with a gate "voltage" and a defect, stiff time scales, and ARKode. Phases 1 and 2 were conservative
gradient flows on CVODE; they did not do this. This phase does the part of the brief that can be done with what exists and says
plainly what it does not do (below).

## Model (dimensionless, `ħ = m = 1`)

Periodic square box `L = 16`, grid `16×16` (`h = 1`), spectral kinetic term, complex `ψ` and a real incoherent reservoir `n_R`:

```
i ∂_t ψ = [ −½∇² + V(x) + g|ψ|² + g_R n_R + (i/2)(R n_R − γ) ] ψ
  ∂_t n_R = P(x) − (γ_R + R|ψ|²) n_R
```

Parameters (fixed here, not tuned afterwards): `g = 0.04`, `g_R = 1.0`, `γ = 0.1`, `γ_R = 200`, `R = 1`. Uniform pump `P`; threshold
`P_th = γγ_R/R = 20`. Above threshold the uniform steady state is `n = P/γ − γ_R/R`, `n_R = γ/R`, rotating at
`ω = g n + g_R n_R + V`. Pump `P = 21` gives `n = 10`, `n_R = 0.1`, `ω = 0.5`. The gate is `V(x) = V₀ exp(−d²/(2σ²))`, `σ = 3`,
`d` the periodic distance from the box centre. The 768 real unknowns are `(Re ψ, Im ψ, n_R)`; the stiff ratio is `γ_R` against the
fastest kinetic frequency `≈ 9.9`.

Parameter setup (disclosed): `g_R` and `γ_R` were chosen so that the reference's linearisation about the uniform state has no
unstable `k > 0` mode (largest real part `−2.4×10⁻³`); the linearisation is the 3×3 per-`k` matrix of `phase3_reference.py`. An
exploratory numpy/scipy BDF run of the gated problem (`V₀ ∈ {0, 0.5}`, scratch script outside the repository) was started before this
registration to check that the program is solvable on this grid; it had produced **no output** after about ten minutes
(scipy's finite-difference Jacobian on 768 unknowns is slow). No numerical result of the gated problem was seen before
registration; the solvability check is therefore the Rust program's own first run, which is the registered run.

## Gates

Solver for all flows: rusty-SUNDIALS CVODE (BDF, dense Newton) at `rtol = 1e-10`, `atol = 1e-12`, tree `996aaf0706e1`
(commit `5db8041`), `max_steps` 2·10⁶. Initial state of D-a/D-d: `ψ = √n (1 + 10⁻³ ξ)` with `ξ` uniform in `[−1, 1]` pointwise and
independent in the real and imaginary parts (seeds 1..10), `n_R = 0.1`, run to `t = 4000` (the slowest mode decays at `≈ 2.4×10⁻³`).

* **D-a (uniform steady states).** *Above* (`P = 21`, `V = 0`, ten seeds): final mean `n` within relative `1e-6` of `10`, mean `n_R`
  within `1e-6` of `0.1`, spatial standard deviation of `|ψ|²` ≤ `1e-6·n`, and `ω = −Im⟨ψ|ψ̇⟩/⟨ψ|ψ⟩` within `1e-6` of `0.5`.
  *Below* (`P = 16`, start `ψ = 0.5(1 + 10⁻³ξ)`, `n_R = 0`): `max|ψ| ≤ 1e-6`, `n_R` within relative `1e-8` of `P/γ_R = 0.08`.
* **D-b (linearisation).** The solver's right-hand side in the frame rotating at `ω = 0.5`, differentiated by central differences
  (`δ = 1e-6`) about the exact uniform state, is a 768×768 matrix; its eigenvalue multiset equals the union over the 256 wavevectors
  of the eigenvalues of the reference 3×3 matrices, sorted by (real, imaginary), to `1e-6` absolute (the matrix is written by the
  Rust program, the eigenvalues are computed in Python).
* **D-c (conservative limit).** `γ = R = 0`, `P = 0`, `n_R ≡ 0`, `V₀ = 0.5`, random smooth initial `ψ` (seed 1, amplitude
  `√10`, noise `10⁻²`), CVODE `rtol = 1e-11`: to `t = 20` the norm `Σ|ψ|²` and the energy `Σ[½k²|ψ̂|²/N + ½g|ψ|⁴ + V|ψ|²]`
  change by less than `1e-6` (relative).
* **D-d (gate sweep, pump budget, single frequency).** `V₀ ∈ {0, 0.25, 0.5, 1.0}`, `P = 21`, seeds 1..10, run to `t = 4000`.
  (i) the steady-state budget `Σ P = Σ(γ_R n_R + γ|ψ|²)` holds to relative `1e-8`; (ii) the state is stationary at one frequency:
  `‖ψ̇ + iωψ‖ ≤ 1e-7 √(Σ|ψ|²)` with `ω` defined as in D-a; (iii) *hypothesis (not a theorem)*: `0 < ω(V₀) − ω(0) < V₀` for
  `V₀ > 0` and `ω` increasing with `V₀`. Reported, not gated: `|ψ|²` at the gate centre and at the corner, the
  outward particle current, the maximum of `Re λ` of the rotating-frame linearisation about the numerical steady state.
  The local-density-approximation guess "density is pinned at `P/γ − γ_R/R` whatever the gate" is *not* registered, because a
  single locked frequency forbids it (the gate shifts the local frequency, so currents must flow).
* **D-e (the ARKode-style IMEX module).** `sundials-core::arkode::imex::ImexSolver` (ARS222) with the reservoir decay `−γ_R n_R`
  as `f^I` and everything else as `f^E`, tolerances `1e-12`; its implicit stage is a fixed-point iteration, which for a linear
  decay converges iff `h·γ_R·a_ii < 1` with `a_ii = 1 − 1/√2`, i.e. `h < 0.017071`. Prediction: one step from the uniform
  state with `h ∈ {0.005, 0.01, 0.0125}` succeeds with finite output, and with `h ∈ {0.02, 0.05}` it returns an error. A *silent
  non-finite* result at the larger steps is recorded as a defect of the module (not as a pass). For `h = 0.01` the trajectory to
  `t = 20` from the uniform state with `V₀ = 0.5` agrees with the CVODE reference of the same problem in max norm to `1e-3`
  of the state norm.
* **D-f (IMEX order).** Same module, `γ_R = 2` (non-stiff), `h = 0.04, 0.02, 0.01` to `t = 2`, against CVODE at `rtol = 1e-12`:
  successive error ratios lie in `[3, 5]` (second order).
* **D-g (planted bug).** The same program with `R` doubled in the `ψ` equation only must violate D-a (above) and the budget (D-d i).

## Not in this phase — and not claimed

* No Hugging Face materials data (no MoSe₂/WSe₂ structures, no defect lattice) and no GNN (MACE, ALIGNN) surrogate for binding
  energies: the gate `V(x)` is a Gaussian with a chosen amplitude; the parameters are dimensionless numbers, **not** those of a
  real heterostructure, and nothing here is compared with an experiment. Using a surrogate model for binding energies would need
  its own literature gate (validity for twisted or untwisted TMD bilayers) which has not been done.
* No claim that excitons Bose–Einstein condense; the model is the standard open-dissipative GPE with a reservoir, whose
  suitability for the experiment of Qi et al. (a dipolar-exciton ground state in an applied field) is a modelling choice, not a result.
* No new physics is claimed: the steady state and the linearisation are textbook (Wouters–Carusotto form). What is tested is the
  solver, the stiff treatment, and the ARKode-style module.
* One grid (`16×16`), one parameter set, no finite-size or resolution study, no 3D, no noise.

## Amendments

**A1 (2026-10-11, written before any run of the Rust program; the Rust binary had been written but not executed).** Two gaps found
while coding the D-e and D-f instruments, both pre-run: (i) the IMEX module's fixed-point loop continues while
`|Δz|/(atol + rtol|z|) > rtol`, so its effective absolute tolerance is `rtol·(atol + rtol|z|)`; with `rtol = atol = 1e-12` that is
below floating-point resolution and no step would converge for any `h`. The tolerances of D-e/D-f are therefore `rtol = atol = 1e-6`
(effective absolute tolerance `≈ 1e-12`); the predicted success/failure threshold `h < 0.017071` is unchanged. (ii) D-f did not
state the pump of the non-stiff variant: `P = 0.2`, all other parameters as in the model except `γ_R = 2`, initial state
`ψ = √10(1 + 10⁻³ξ)`, `n_R = 0.1`, `V₀ = 0.5`, rotating frame `ω = 0.5`, seed 1.
