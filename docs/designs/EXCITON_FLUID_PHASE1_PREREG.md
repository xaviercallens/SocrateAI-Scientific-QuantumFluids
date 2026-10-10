# Exciton fluids, Phase 1: pre-registration (classical N-particle flows and the four-flavour flow on rusty-SUNDIALS)

**Status: REGISTERED BEFORE ANY EXPERIMENT WAS RUN.** Date 2026-10-10. Owner's instruction: "go for phase 1 on
rusty-sundials". Parent: `docs/designs/EXCITON_FLUID_LEAN_SOLVER_PLAN.md` (commit `d9cd0e8`, §5 WP4 and WP6, §6 gates
KA-1, KA-2, EX-1, EX-2, FF-2, S0). The independent reference numbers below were produced by
`exploration/exciton/python/phase1_reference.py` (numpy, mpmath) before the Rust code existed; they are in
`exploration/exciton/results/phase1/reference.json`.

Rules (the programme's): gates are fixed here and are not changed after results are seen; a change is an *amendment*
with its date and reason; results are read *as registered*, failures included; anything run beyond this document is
labelled exploratory. Nothing here proves or disproves the upstream theorem: finite numerical searches can fail to
falsify it, no more.

## 0. Identity of the instruments

| item | value |
|---|---|
| solver | rusty-SUNDIALS tree `996aaf0706e1` = release v11.6.0 = commit `5db8041` (clean clone `~/xdev/rusty-SUNDIALS-c3`, path dependencies as in `book/rust/`); crates `cvode`, `nvector` |
| integrator | `cvode::Cvode`, `Method::Bdf` (orders 1–5), analytic Jacobian where stated; `rtol = 1e-10`, `atol = 1e-12` (positions) |
| language, toolchain | Rust, rustc 1.97.1, release build, `CARGO_TARGET_DIR` on `/mnt/data/xdev-cache` |
| independent check | numpy float64 and mpmath, in `exploration/exciton/python/` |
| code | `exploration/exciton/rust/qf-exciton-p1/` (written after this document is committed) |
| Lean | `exploration/exciton/lean/` (producer: this session; verifier pending); Phase 1 uses its statements as known answers only |

## 1. Quantities and units

`t = r²`; a kernel is `g(t)`; the pair energy is `g(|Δ|²)`. For `N` points in a rectangular torus
`L_x × L_y` (periodic images summed, **including** the images of a point with itself, as in the periodic extension that
the theorem is applied to) the energy per particle is
`E = (1/2N) Σ_{(i,j,m) ≠ (i,i,0)} g(|x_i − x_j + L∘m|²)`.
`e_lat(ρ) = ½ Σ_{a ∈ A_ρ∖0} g(|a|²)`, `A_ρ` the triangular lattice of density `ρ` (nearest-neighbour distance
`a = (2/(√3 ρ))^{1/2}`). The upstream energy counts **ordered** pairs, hence twice these quantities; every comparison
below uses the unordered convention on both sides. The registered inequality is `E ≥ e_lat(ρ)`.

## 2. Kernels and cases

| id | `g(t)` | completely monotone | summed | cutoff `r_c` |
|---|---|---|---|---|
| K1 | `exp(−t)` | yes | exactly | 6.5 |
| K2 | `exp(−√t)/√t` | yes | exactly | 42 |
| K3 | `t^(−3/2) exp(−0.02 t)` | yes (product of CM) | exactly | 46 |
| K4 | `2[t^(−1/2) − (t+1)^(−1/2)] exp(−0.02 t)` | yes (X1, product of CM) | exactly | 46 |
| K5 | `t^(−3/2)` | yes | truncated + tail | 60 |
| K6 | `2[t^(−1/2) − (t+1)^(−1/2)]` | yes (X1) | truncated + tail | 60 |
| N1 | `exp(−t²)` | **no** (control) | exactly | 2.8 |

"Exactly" means the neglected terms are below `1e-18` relative; K5 and K6 carry the constant continuum tail
`πρ/r_c` and `2πρ(√(r_c²+1) − r_c)` respectively, identical for lattice and configurations (so differences are
unaffected). K5 and K6 are **secondary**: the truncated kernel is not completely monotone, and their gates are relaxed.

| kernel | densities `ρ` | tori |
|---|---|---|
| K1, K2 | 0.5, 1.5 | T36c, T36s; T64c at the first density |
| K3, K4 | 0.1, 0.5 | T36c, T36s; T64c at the first density |
| K5, K6 | 0.1 | T36c |
| N1 | 1.0, 4.0 | T36c, T36s |

T36c: `L_x = 6a`, `L_y = 3√3 a`, `N = 36` (commensurate: the triangular lattice fits, `E = e_lat` exactly).
T64c: `8a × 4√3 a`, `N = 64`. T36s: square torus `L = (36/ρ)^{1/2}`, `N = 36` (incommensurate, frustrated).

## 3. Gates

### Instrument gates

* **S0-a.** `cargo test --locked --release -p cvode` on the pinned tree: all tests pass (includes `adams_order`, `tight_tolerance`).
* **S0-b.** `y' = −y`, `t ∈ [0, 10]`, `atol = 1e-14`: Adams at `rtol = 1e-10` ≤ 1000 RHS evaluations and max relative error
  ≤ 1e-8 (the pre-fix first-order build needs about 2·10⁶ evaluations, CLAIM-109); BDF at `rtol = 1e-8` max relative error ≤ 1e-5.
* **KA-3 (cross-language).** At 5 random configurations per kernel on T36c, the Rust energy equals the numpy
  independent implementation to relative 1e-12, the force to 1e-10 of its maximum, and the analytic Hessian equals a
  central finite difference of the force to relative 1e-6 (max-norm).

### Known answers

* **KA-1a.** `Σ′ r⁻³` over the triangular lattice of unit spacing, direct sum to `R = 200, 400, 800` plus the continuum
  tail `2πρ/R` (`ρ = 2/√3`): within `1e-6` relative of `11.0341757349148` at `R = 800`, and the error at 800 ≤ the error at 200.
* **KA-1b.** `e_lat(K1; 0.5, 1.5)` equals the Jacobi-theta closed form to `1e-13` relative.
* **KA-1c.** `e_lat` of K1–K4 and N1 at the registered densities equals `reference.json` to `1e-12` relative.
* **KA-2.** `∫ V d²r` of K6 (`d = 1`) by composite Gauss–Legendre on `[0, 400]` plus the analytic tail equals `4π` to `1e-10`.
* **KA-4.** `e_H/e_lat` for K6 (`e_H = 2πρ`) at `ρd² = 10⁻³, 10⁻², 0.1, 0.3, 1, 3` equals `reference.json`
  (`sandwich_K6_eH_over_elat`) to `1e-6` relative. (The 3-significant-digit table of the plan's Appendix B used a short
  cutoff; its first entry, 43.8, is to be corrected to the converged 44.7.)

### Experiment gates (classical flows, WP4)

For each (kernel, ρ, torus) batch: 200 random starts, then, on commensurate tori only, up to 200 basin-hopping
perturbations of the best configuration. `ε_viol` is `1e-10` for K1–K4 and N1, `1e-6` for K5–K6.

* **EX-1a (no violation).** Over all runs of a completely monotone kernel, `min E/e_lat − 1 ≥ −ε_viol`.
* **EX-1b (attainment, commensurate tori).** Some run reaches `E/e_lat − 1 ≤ 1e-9` (K1–K4) or `1e-6` (K5, K6). If not
  reached, the result is "not attained by this search", not a failure of the inequality.
* **EX-1c (frustration, incommensurate tori).** Reported: `min E/e_lat − 1` on T36s (expected positive); the same
  no-violation bound applies.
* **EX-2 (hypotheses are needed).** For N1 at both densities, some run has `E/e_lat ≤ 0.99`. (Reference upper bounds
  from triangular cluster crystals: ratio `0.669` at `ρ = 1`, `0.661` at `ρ = 4`; `reference.json`.)
* **L2 (energy monitor).** Along every trajectory sampled at chunk ends, `E` never increases by more than `1e-9`
  relative. Reported: the number of violations (expected 0).
* **NEG (planted bugs; the gates must bite).** On the recorded K1@0.5 T36c batch: (i) with `e_lat` doubled
  (ordered-pair convention), EX-1a must FAIL; (ii) with `e_lat` halved, EX-1b must FAIL; (iii) a Hessian with one
  sign flipped must FAIL KA-3.

### Four-flavour flow (WP6, solver side)

Model and parameters: `docs/designs/EXCITON_FLUID_LEAN_SOLVER_PLAN.md` §3.4, values in `reference.json`
(`four_flavour`; `g_H = 8πd` with `d = 2 nm`, `a_B = 1.5 nm`, `g_X = 1`, `Δ = 1 μeV`, `g_c = 3`, `g_v = 6`, `n_x = 0.5·10¹² cm⁻²`).
Imaginary-time flow `ψ̇_i = −ψ_i (E_i − μ + (g_H + g_X)N − g_X n_{p(i)})`, `n_i = ψ_i²`, `p = (1,0,3,2)`, CVODE BDF,
`rtol = 1e-12`, `atol = 1e-16`, `τ_max = 5·10⁴`.

* **FF-2a.** At `B = 0.01, 0.04, 0.2 T`, 200 random positive starts (`ψ_i ∈ U(0.01, 0.15)`): every converged final state
  has its support inside one pair (T1); on support {0,1}, `n₁ − n₀` and `N` equal `n1_minus_n0_IIA` and `N_A` (relative
  1e-9); on {2,3}, `n₂ − n₃` and `N` equal `n2_minus_n3_IIB` and `N_B` (relative 1e-9).
* **FF-2b.** The field at which the grand potentials of the converged II_A and II_B states are equal (bisection) equals
  `B_c` of `reference.json` to relative `1e-8`.
* **FF-2c (informational).** Continuation upward in `B` from II_A with a seed `ψ₂ = 1e-6`: the field at which the state
  leaves {0,1} is within 5 % of the closed-form spinodal `spinodal_IIA_b_Ry` (0.725 T). Not gated beyond this.
* **FF-L2.** `Ω` non-increasing along every flow (same tolerance as L2).

## 4. Procedure details fixed in advance

* Random numbers: SplitMix64; run `s` of case `c` uses seed `1000·c + s` (`c` = index in the order of §2's tables).
* Starts: uniform in the torus; sequential rejection if the minimum-image distance to a placed point is below `0.3a`
  (up to `10⁴` attempts).
* Flow: `ẋ = −∇(N E)`; CVODE BDF; analytic Jacobian (the Hessian of §1's energy), checked by KA-3; integrate in chunks of
  `Δτ = 5` up to `τ_max = 2000`; stop when `max|F| < 1e-9` and the energy change over the last chunk is below
  `1e-14 |E|`. Runs that do not converge by `τ_max` count in every gate with their final energy.
* Basin hopping: displace 6 random particles by `N(0, (0.35a)²)`, re-minimise; 200 trials; the best configuration is
  updated after each trial; every trial's energy counts.
* All run records are written (one JSON line per run); summaries are computed from the records by a separate script.

## 5. What would mean what

A run below `e_lat` by more than `ε_viol` is, in order of suspicion: (1) a normalisation or density slip (ordered
pairs, `a`), (2) a truncation/summation defect (K5, K6 first), (3) a solver defect (compare with KA-3 and the L2
monitor), (4) an error upstream or a hypothesis the physics does not meet. Only after (1)–(3) are excluded would it be
reported as a candidate counterexample, with the configuration, and sent to the owner. A pass says only that this
search found nothing.

## 6. Not in Phase 1

Mean-field PDE solvers (`qf-gpe2d`/`qf-pgpe` extensions: Phase 2), Lean verification of the new files (second
server), the Hugging Face layer, any driven-dissipative model, ARKode, and any comparison with experimental data.

## 7. Amendments

**A1 (2026-10-10, after the instrument and known-answer gates, before any EX or FF run).** KA-1a failed as registered
(relative errors 1.8e-4, 1.0e-4, 5.4e-5 at `R = 200, 400, 800`, halving with `R`). Cause: the lattice enumeration of
both the numpy reference and the Rust crate looped `|m|, |k| ≤ R/a + 3`, which misses the caps `|y| > (√3/2) R` of the
disk; the two implementations, written by the same hand, shared the slip, and only the closed-form number exposed it.
Both were corrected (`k` to `R/(a√3/2)`, `m` to `R/a + |k|/2`), `reference.json` was regenerated, and the gates were
re-run unchanged. Effect on the references: the exactly summable `e_lat` values changed by less than `2e-16` relative
(the neglected points lie where the kernels are below `1e-14`); the K6 sandwich table changed by at most `3.0e-4`
relative (`ρd² = 10⁻³`: unchanged, 44.71; 0.01: 14.19 → 14.19; 0.1: 4.643 → 4.642; 0.3: 2.867 → 2.867; 1: 1.873 → 1.872;
3: 1.444 → 1.444). The plan's Appendix B table used a short cutoff; its `10⁻³` entry (43.8) is corrected to 44.7 there.
Gates, tolerances and procedures are unchanged. Lesson recorded: two implementations by one author are not independent
of that author's blind spots; a closed-form known answer is.
