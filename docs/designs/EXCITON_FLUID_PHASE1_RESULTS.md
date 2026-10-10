# Exciton fluids, Phase 1 (N-particle tests on rusty-SUNDIALS CVODE): results, as registered

Date: 2026-10-11 (night). Pre-registration: `docs/designs/EXCITON_FLUID_PHASE1_PREREG.md` (committed as `d249544` with its
independent reference numbers `results/phase1/reference.json` **before any run**; amendments A1 and A2 appended there, A1 after
a registered gate failed, A2 after the first results and before the remaining batches were read). Instruments:
`exploration/exciton/rust/qf-exciton-p1/` on rusty-SUNDIALS tree `996aaf0706e1` (release v11.6.0, `5db8041`), Rust 1.97.1;
independent references in `exploration/exciton/python/`. Evaluation: `exploration/exciton/python/phase1_summarise.py` →
`results/phase1/summary.json`, from the run records `results/phase1/runs/` (one JSON line per run, 2860 runs,
21 cases). Everything below is read from those files.

## 0. Verdict in one paragraph

All instrument and known-answer gates pass after one registered failure (KA-1a: a lattice-enumeration slip shared by the numpy
reference and the Rust code, found because a closed-form constant did not agree; amendment A1). Of the experiment gates, EX-1a
(no violation of the bound), EX-2 (the non-completely-monotone control goes below the lattice), L2 (energy monitor) and NEG
(planted bugs are caught) pass everywhere; EX-1b (attainment on commensurate tori) is met in 8 of 9 cases and **fails as
registered for K1 at ρ = 1.5 on T36c** (best +5.9×10⁻⁹ against 10⁻⁹: the registered flow length τ_max = 2000 is too short for the
soft modes; an exploratory longer flow reaches +1.1×10⁻¹⁵). The four-flavour flows (FF-2a/b/c, FF-L2) pass. The budget of K2–K4
was reduced by amendment A2 (60 starts, lower cutoffs); K5 and K6 were not run. Passing says that this search found no
violation of the theorem on tori of N = 36 and 64 points; it does not prove it.

## 1. Instrument gates

| gate | registered | result |
|---|---|---|
| S0-a | `cargo test -p cvode`: all tests pass | 22/22 pass |
| S0-b | `y' = −y`, t ∈ [0,10]: Adams at rtol 1e-10 ≤ 1000 RHS evaluations and error ≤ 1e-8; BDF at rtol 1e-8 error ≤ 1e-5 | Adams: 400 evaluations, error 9.8e-10; BDF rtol 1e-8: error 3.1e-7 |
| KA-3 | Rust vs independent numpy: energy 1e-12, force 1e-10, analytic Hessian vs finite difference of the force 1e-6 | numpy side: energy ≤ 5.2e-14, force ≤ 6.4e-16; Rust side: Hessian vs FD ≤ 5.0e-9; a planted sign flip in the Hessian gives relative error 2.0 (detected) |

## 2. Known answers

| gate | registered | result |
|---|---|---|
| KA-1a | Σ′ r⁻³ over the unit triangular lattice vs 6ζ(3/2)L(3/2,χ₋₃) = 11.0341757349…, within 1e-6 at R = 800 and monotone in R | **FAILED first** (see below); after amendment A1: 6.0e-7, 4.9e-8, 1.3e-8 at R = 200, 400, 800: pass |
| KA-1b | e_lat(K1; 0.5, 1.5) vs the Jacobi-theta closed form, 1e-13 | 5.5e-16, 1.1e-15: pass |
| KA-1c | e_lat of K1–K4, N1 vs `reference.json`, 1e-12 | worst 7.2e-15 (registered cutoffs); 2.3e-13 at the cutoffs of amendment A2: pass |
| KA-2 | ∫V d²r of K6 (d = 1) = 4π, 1e-10 | 8.1e-13: pass |
| KA-4 | e_H/e_lat for K6 at ρd² = 10⁻³…3 vs `reference.json`, 1e-6 | worst 8.8e-14: pass. Values 44.7, 14.2, 4.64, 2.87, 1.87, 1.44; the plan's first entry 43.8 (short cutoff) is corrected to 44.7 |

**KA-1a, as registered, failed, and why.** The relative errors were 1.8×10⁻⁴, 1.0×10⁻⁴, 5.4×10⁻⁵ at R = 200, 400, 800: they
halved with R instead of falling like the tail. The lattice enumeration of *both* the numpy reference and the Rust code looped
over |m|, |k| ≤ R/a + 3 and so missed the caps |y| > (√3/2)R of the disk. Two implementations by the same author shared the slip;
the closed-form constant exposed it. Both were corrected (ranges k ≤ R/(a√3/2), m ≤ R/a + |k|/2), `reference.json` regenerated,
and the gates re-run unchanged (amendment A1). The exactly summable references changed by less than 2×10⁻¹⁶, the sandwich
table by at most 3×10⁻⁴.

## 3. Experiment gates (classical flows)

Flow: ẋ = −∇(N E) under CVODE BDF, rtol 1e-10, atol 1e-12, analytic Hessian Jacobian, chunks Δτ = 5, τ_max = 2000, stop at
max|F| < 1e-9 and |ΔE| ≤ 1e-14|E|. Runs that did not converge count in every gate with their final energy.

| case | runs | converged | min(E/e_lat − 1) | #≤1e-9 | gate (as registered) | exploratory longer flow (not registered) |
|---|---|---|---|---|---|---|
| K1_0.5_T36c | 200 | 116 | 2.22e-16 | 90 | EX-1a pass; EX-1b attained | — |
| K1_0.5_T36s | 200 | 131 | 6.91e-03 | 0 | EX-1a pass; EX-1c frustration +6.91e-03 | 6.91e-03 |
| K1_0.5_T64c | 200 | 47 | 2.44e-15 | 46 | EX-1a pass; EX-1b attained | — |
| K1_1.5_T36c | 400 | 0 | 5.94e-09 | 0 | EX-1a pass; EX-1b **NOT attained** | 1.11e-15 |
| K1_1.5_T36s | 200 | 0 | 7.89e-07 | 0 | EX-1a pass; EX-1c frustration +7.89e-07 | 7.04e-07 |
| K2_0.5_T36c | 200 | 91 | -2.01e-14 | 84 | EX-1a pass; EX-1b attained | -4.44e-15 |
| K2_0.5_T36s | 60 | 38 | 3.00e-03 | 0 | EX-1a pass; EX-1c frustration +3.00e-03 | 3.00e-03 |
| K2_1.5_T36c | 60 | 45 | -1.05e-13 | 33 | EX-1a pass; EX-1b attained | -8.56e-14 |
| K2_1.5_T36s | 60 | 33 | 1.28e-03 | 0 | EX-1a pass; EX-1c frustration +1.28e-03 | 1.28e-03 |
| K3_0.1_T36c | 60 | 0 | 1.54e-11 | 5 | EX-1a pass; EX-1b attained | -5.00e-15 |
| K3_0.1_T36s | 60 | 0 | 8.62e-03 | 0 | EX-1a pass; EX-1c frustration +8.62e-03 | 8.61e-03 |
| K3_0.5_T36c | 60 | 39 | -2.74e-14 | 27 | EX-1a pass; EX-1b attained | -3.64e-14 |
| K3_0.5_T36s | 60 | 35 | 6.07e-03 | 0 | EX-1a pass; EX-1c frustration +6.07e-03 | 6.07e-03 |
| K4_0.1_T36c | 60 | 0 | 5.87e-10 | 1 | EX-1a pass; EX-1b attained | 0 |
| K4_0.1_T36s | 60 | 0 | 7.61e-03 | 0 | EX-1a pass; EX-1c frustration +7.61e-03 | 7.58e-03 |
| K4_0.5_T36c | 60 | 45 | 9.55e-15 | 27 | EX-1a pass; EX-1b attained | — |
| K4_0.5_T36s | 60 | 36 | 3.41e-03 | 0 | EX-1a pass; EX-1c frustration +3.41e-03 | 3.41e-03 |
| N1_1_T36c | 200 | 200 | -3.37e-01 | 200 | EX-2 pass (best E/e_lat = 0.6625) | — |
| N1_1_T36s | 200 | 200 | -3.29e-01 | 200 | EX-2 pass (best E/e_lat = 0.6706) | — |
| N1_4_T36c | 200 | 200 | -2.77e-01 | 200 | EX-2 pass (best E/e_lat = 0.7231) | — |
| N1_4_T36s | 200 | 200 | -2.76e-01 | 200 | EX-2 pass (best E/e_lat = 0.7240) | — |

Totals: 2860 runs, 1404 did not meet the convergence criterion within τ_max
(counted with their final energy); L2 violations: 0; solver errors: 0.

* **EX-1a** (no violation, ε = 1e-10) passes in all 17 completely monotone cases; the smallest value is −1.1×10⁻¹³ (K2 at ρ = 1.5,
  T36c), at the roundoff and cutoff level of the lattice sums (the A2 cutoffs neglect terms below 10⁻¹³ e_lat).
* **EX-1b** (attainment ≤ 1e-9 on commensurate tori) is met in 8 of 9 cases. **K1 at ρ = 1.5 on T36c fails as registered**: best
  +5.9×10⁻⁹, none of the 400 runs converged by τ_max. The exploratory continuation of its best configuration reaches
  +1.1×10⁻¹⁵ at τ ≈ 41 500 (889 steps): "not attained by the registered stopping rule", not "not attained". For K3 and K4 at
  ρ = 0.1 (long-range, flat kernels) no run met the convergence criterion either, and 5/60 and 1/60 runs reached within 1e-9;
  the longer flow takes the best to 0 within roundoff.
* **EX-1c** (frustration on the incommensurate square torus): positive in all 8 cases, from +7.9×10⁻⁷ (K1, ρ = 1.5) to
  +8.6×10⁻³ (K3, ρ = 0.1). The longer flows change these by at most 11 %.
* **EX-2** (hypotheses are needed): all 800 runs of N1 end below the lattice energy; best E/e_lat = 0.663 (ρ = 1, T36c),
  0.671 (T36s), 0.723, 0.724 (ρ = 4). The reference upper bounds from triangular cluster crystals are 0.669 (ρ = 1) and 0.661
  (ρ = 4): at ρ = 4 the search did **not** find the best cluster crystal (it is not exhaustive; the gate requires only ≤ 0.99).
* **L2**: 0 violations in 2860 flows. **NEG**: with e_lat doubled (ordered-pair slip) EX-1a fails; with
  e_lat halved EX-1b fails; a sign-flipped Hessian is detected by KA-3. The gates bite.

## 4. Four-flavour flow (FF)

Model and parameters from `reference.json` (`g_H = 8πd`, d = 2 nm, a_B = 1.5 nm, g_X = 1, Δ = 1 μeV, g_c = 3, g_v = 6,
n_x = 0.5×10¹² cm⁻²); imaginary-time flow of the four amplitudes under CVODE BDF, rtol 1e-12, atol 1e-16.

* **FF-2a** pass: 600 random starts at B = 0.01, 0.04, 0.2 T, none unconverged, **0** supports across the two pairs (T1); polarisation
  and density of T2/T3 reproduced to 1.7×10⁻¹² (gate 1e-9).
* **FF-2b** pass: B_c = 0.0559014570 T from the equality of the grand potentials of the converged II_A and II_B states, equal to the
  closed form to 1.6×10⁻¹² (gate 1e-8).
* **FF-2c** (informational): continuation upward from II_A with a seed ψ₂ = 1e-6 leaves the pair at 0.730 T against the
  closed-form spinodal 0.7254 T (within 5 %). The large metastability window is a property of the mean-field model.
* **FF-L2**: Ω non-increasing along every flow, 0 violations.

## 5. Amendments

* **A1** (after KA-1a failed): the lattice-enumeration correction above.
* **A2** (2026-10-10 23:10, after K1 and K2@0.5/T36c, before the other K2–K4 results were read): the registered design for
  K2–K4 (5 batches each, 200 starts, up to 200 hops) would have taken about 25 CPU-hours on the loaded machine (one run 27–131 s);
  cutoffs reduced to r_c = 30 (K2) and 34 (K3, K4), 60 random starts and up to 60 hops per batch, no T64c for K2–K4, K5 and K6
  not run; KA-1c re-run at the reduced cutoffs (worst 2.3×10⁻¹³). K1, N1 and K2@0.5/T36c keep the registered design.

## 6. Notes and defects of the records

* The field `min_dist` of the run records is a **placeholder (always 0)**; only `min_dist_start` is a measurement. The final minimum
  distances were not recorded.
* K5 and K6 were not run (secondary kernels; compute budget). The statements that can be made about K2–K4 are limited to 60
  starts per batch and the A2 cutoffs.
* The exploratory longer flows (`polish`, `results/phase1/polish_exploratory_*.jsonl`) were run from the best configuration of each
  case, after the registered results were read; they are labelled exploratory everywhere.

## 7. What this does and does not show

Energies from the flow are upper bounds on the minimum energy of N points on the torus. That they equal the lattice energy to
roundoff on commensurate tori, never go below it for completely monotone kernels, lie above it on incommensurate tori, and go
well below it for a kernel that is not completely monotone, is what the theorem and its hypotheses predict; it is consistent
with a correct implementation (two independent implementations and a closed-form constant agree). It does not prove the theorem:
a local search from random starts at N ≤ 64 can only fail to find a counterexample.
