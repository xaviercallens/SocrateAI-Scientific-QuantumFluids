# Pre-registration: a projected Gross–Pitaevskii (classical-field) solver, its known answers, and the BKT gate

Direction 2 of `paper/wasserstein_slack.pdf` §6.2, which stopped at "this project has no finite-temperature
solver". This document opens that gate the only honest way: build the solver, validate it against known
answers that have nothing to do with BKT, cross-check its integrator against an independent one
(rusty-SUNDIALS, the owner's pure-Rust CVODE), and only then look at the transition. Committed before the
solver is written. Changes after this commit are dated amendments.

## 0. What is being built, and why these tools

**Model.** The projected Gross–Pitaevskii equation (PGPE) on a 2D periodic box, in units ħ = m = 1,
healing length and sound speed set by `g` and the mean density:

    i ∂ₜψ = P[ −½∇²ψ + g|ψ|²ψ ],      P = projector onto |k| ≤ k_cut  (sharp cutoff in Fourier space).

This is the classical-field method of Simula–Blakie (PRL 96, 020404, 2006) and Foster–Blakie–Davis
(PRA 81, 023623, 2010) for exactly this question: a PGPE trajectory started from a random high-energy
state thermalises (the field is ergodic) and samples the microcanonical ensemble of the coherent region;
temperature and chemical potential are *measured* from the trajectory, not imposed.

**Integrator.** Fourier pseudo-spectral, with the linear part `−½k²` treated exactly by an integrating
factor and the nonlinear part by RK4 (IF-RK4 / "ETD-RK4", the scheme LeanFlow's `RustDyadicSolver`
already uses for the shell model, `crates/leanflow-solver/src/lib.rs`), dealiased by the projector itself
(the cutoff `k_cut ≤ (2/3)·k_max` makes the cubic term alias-free).

**Independent integrator (the cross-check).** The same ODE system — the `2·N_modes` real components of
the projected Fourier amplitudes — integrated by **rusty-SUNDIALS** CVODE (Adams–Moulton, non-stiff,
adaptive order and step; `crates/rusty-sundials-py`, `CvodeSolver(method="adams")`) from the same initial
state to the same time, on a small grid. The two integrators share only the right-hand side function.
This is the *use* of the solver capability asked for: not speed, but a second, independently written,
adaptive integrator whose error control is not ours.

**What is NOT built.** A stochastic (SPGPE) reservoir; a trap; 3D; a Rust port of the PGPE step (a
LeanFlow "complex scalar field" engine is the natural follow-up PR and is recorded as such, not done here).

## 1. Known answers (controls) — all must pass before any thermal run is looked at

| # | Statement | Criterion |
|---|---|---|
| K1 | **Norm** `N = Σ|c_k|²` conserved by IF-RK4 over the full run | relative drift `≤ 1e-8` at `dt = 0.005` (report the drift; it is the time-stepping error of a symplectic-like scheme, not exactly zero) |
| K2 | **Energy** `E = Σ ½k²|c_k|² + (g/2)∫|ψ|⁴` conserved | relative drift `≤ 1e-6`; drift must scale as `dt⁴` between `dt` and `dt/2` (ratio `16 ± 3`) |
| K3 | **Momentum** `P = Σ k|c_k|²` conserved | `≤ 1e-10` absolute (exact for the projected scheme up to roundoff, because the projector and the cubic term commute with translations) |
| K4 | **Exact solution**: a single plane wave `ψ = √n₀ e^{i(k·x − ωt)}`, `ω = ½k² + g n₀`, reproduced | phase error `≤ 1e-9` after `t = 10` |
| K5 | **Bogoliubov dispersion**: a small perturbation on a uniform state oscillates at `ω² = ½k²(½k² + 2 g n₀)` | frequency from the FFT of the mode amplitude within `0.5 %` for three `k` values, amplitude `1e-3 √n₀` |
| K6 | **Cross-check**: IF-RK4 vs rusty-SUNDIALS Adams on a `16×16` grid from the same random initial state to `t = 5` | `max_k |c_k^{RK4} − c_k^{CVODE}| ≤ 10·(rtol·‖c‖)` with `rtol = 1e-8`; **and** the two disagree by more than that if one of them is deliberately run with `rtol = 1e-3` (negative control: the comparison can fail) |
| K7 | **Thermalisation / equipartition**: after the transient, the high-`k` modes of the coherent region satisfy the classical equipartition `⟨|c_k|²⟩ (½k² − μ + 2 g n) ≈ k_B T` with one `(T, μ)` pair; the temperature from a fit over `k ∈ [0.6, 1.0] k_cut` agrees with the temperature from `[0.4, 0.6] k_cut` | agreement within `10 %`; this is the classical-field analogue of a thermometer reading the same on two scales |

Stop rule: any K failing is a bug or a wrong scheme; no thermal ensemble is analysed until K1–K7 pass.

## 2. The thermal sweep and the BKT gate (pre-registered observables)

Box `L = 64 ξ₀` (`ξ₀` the healing length at the mean density `n₀ = 1`), grid `128²`, `k_cut = 2/3 k_max`
(so about 5 800 modes in the coherent region), `g n₀ = 1`. Twelve total energies `E/N` spanning the
range from a nearly pure condensate to a nearly incoherent gas, three seeds each; each trajectory
`t ∈ [0, 1500]` at `dt = 0.01` (the compute budget of this machine: about 6 min per trajectory, 36
trajectories on 8 cores), samples every `Δt = 10` after `t = 500` (transient discarded; the K7 thermometer
must be stationary over the sampling window, checked by comparing the two halves of the window to within
5 %).

Observables per sample:

* `T`, `μ` from K7's equipartition fit; the condensate fraction `|c₀|²/N`;
* the **first-order correlation** `g₁(r) = ⟨ψ*(0)ψ(r)⟩/n` along the axes (azimuthal average);
* the **vortex count** `N_v` and the **pair-unbinding statistic**: vortices located by the phase-winding
  detector proved correct in `lean_src/VortexWinding.lean` (`quantumfluids` package, winding of the
  principal phase around each plaquette); a vortex is *paired* if its nearest opposite-sign neighbour is
  closer than `ξ_T = 1/√(gn)`·(pre-set factor 3) and no same-sign vortex is closer — the fraction of
  unpaired vortices `f_free`;
* the **superfluid fraction** `n_s/n` from the momentum-space current correlators of the classical
  field, `J = Im(ψ*∇ψ)`, split into longitudinal and transverse parts: in linear response
  `⟨|J_L(k)|²⟩ → n T` and `⟨|J_T(k)|²⟩ → n_n T` as `k → 0`, so `n_s/n = 1 − lim_{k→0} ⟨|J_T|²⟩/⟨|J_L|²⟩`,
  taken from the smallest three `|k|` shells. This is the standard classical-field estimator (used by
  Foster–Blakie–Davis and by Prokof'ev–Svistunov's classical-field studies); the primary text of
  Foster–Blakie–Davis is paywalled and was **not** read, so the estimator is cited as standard, not by
  their equation number.

Predictions:

| # | Statement | Criterion |
|---|---|---|
| B1 | `g₁(r)` decays **algebraically** at low `T` (fit `r^{−η}` with `η < 1/4`) and **exponentially** at high `T` (fit `e^{−r/ℓ}` with `ℓ < L/4`), with a crossover at some `T_×` | reported; the two regimes must both be seen within the sweep, else the sweep is too narrow and is widened *before* any transition value is read (that widening is an amendment) |
| B2 | `f_free` rises from `≈ 0` to `> 0.5` across the same `T_×` (within one energy step) | PASS/FAIL |
| B3 | **Nelson–Kosterlitz universal jump**: at the transition `n_s λ_T² = 4` (`λ_T² = 2π/T` in these units). The crossing of `n_s(T)·λ_T²` with `4` gives `T_BKT`; prediction: `T_BKT` lies within one energy step of `T_×` from B1/B2 | PASS/FAIL |
| B4 | **Prokof'ev–Ruebenacker–Svistunov**: `n λ_T² = ln(ξ/ g̃)` with `ξ = 380 ± 3`, `g̃ = g` (m = ħ = 1), i.e. `n λ_T² = ln(380)` at the transition. With `n` the coherent-region density, prediction: the measured `n λ²_T` at `T_BKT` lies within `20 %` of `ln(380/g)` | PASS/FAIL, **reported with the caveat** that the classical field with a cutoff is not the quantum gas; a 20 % agreement is the level Foster–Blakie–Davis-type comparisons reach, and a failure here is a statement about the cutoff dependence, to be quantified by repeating one energy at `k_cut = 0.5 k_max` (pre-set) |
| B5 | Finite-size: repeating the transition energy at `L = 32 ξ₀` shifts `T_BKT` by less than one energy step | reported |

Kill: if B1 shows only one regime after widening once, or if K7's thermometer is not stationary at any
energy, the sweep is reported as "no equilibrium classical-field ensemble reached" and no BKT number is
quoted. A B4 failure is *not* a kill; it is the measured cutoff dependence, reported.

## 3. What would count as leverage of the three solver repositories, honestly

* **rusty-SUNDIALS** — used (K6) as the independent integrator. If the Python binding cannot be built on
  this machine (pyo3 0.20 against Python 3.13 is a known incompatibility), the cross-check is done with
  `scipy.integrate.solve_ivp(method="DOP853")` instead and this is written down as such; a PR adding a
  numpy-array RHS path to `rusty-sundials-py` (its current callback converts Python lists on every RHS
  call, prohibitive above a few thousand unknowns) is the concrete improvement to propose.
* **LeanFlow (DualScale solver)** — the IF-RK4 step is the same scheme as its `step_etd_rk4`; the
  follow-up PR is a `ComplexField2D` engine (rustfft, cutoff projector, the K1–K5 tests as Rust tests).
  Not done in this round.
* **QuantumFluids' own Lean** — `VortexWinding.lean` is the correctness proof of the vortex detector used
  for B2; nothing new is claimed for it.

## 4. Not in this round

No Lean for the PGPE (a Hamiltonian ODE on a finite mode set is `GPGalerkin.lean`'s object; its
invariants K1–K3 are theorems there for the *unprojected* Galerkin truncation and the projector does
not change them — the equality of the two is a one-line remark, not a new theorem). No SPGPE. No 3D.
No claim about helium films: the Bishop–Reppy jump is the same universal number, but the data class
here is a weakly interacting Bose gas.
