# Exciton fluids, Phase 2 (nonlocal-kernel mean field): results, as registered

Date: 2026-10-11 (night). Pre-registration: `docs/designs/EXCITON_FLUID_PHASE2_PREREG.md` (committed before any run, with its
independent reference numbers `exploration/exciton/results/phase2/reference.json`; amendments A1–A3 recorded in that file, A1
before the run, A2 and A3 after the registered run, with their reasons). Program: `exploration/exciton/rust/qf-exciton-p1/src/bin/mf.rs`
(rusty-SUNDIALS tree `996aaf0706e1`, CVODE BDF, finite-difference dense Jacobian; the field is a 16×16 grid, 256 unknowns).
Evaluation: `exploration/exciton/python/phase2_summarise.py` → `results/phase2/summary.json`. Raw record: `results/phase2/mf_report.json`.

## Outcome

| gate | what | result | numbers |
|---|---|---|---|
| P2-a | kernel B (bilayer, `Ũ ≥ 0`): 50 random starts flow to the uniform state | **PASS** | 50/50 converged by `τ = 100` (1093–1133 BDF steps); worst `max|n−n₀|/n₀ = 1.8×10⁻¹⁴` (gate `1e-8`); worst `|Ω−Ω₀|/|Ω₀| = 1.6×10⁻¹⁵` (gate `1e-10`) |
| P2-b | kernel B: the solver's own linearisation reproduces the Bogoliubov spectrum on all 255 nonzero wavenumbers | **PASS** | worst `|ω−ω_ref|/ω_ref = 5.8×10⁻¹¹` (gate `1e-6`); worst `|Re λ| = 2.4×10⁻¹¹` (gate `1e-8`); no unstable mode |
| P2-c(i) | kernel C (negative Fourier band): linearisation vs formula `ω² = ε(ε+2n₀Ũ)`, sign pattern | **PASS** | worst relative error of `ω²` `6.3×10⁻⁹` (gate `1e-6`); 16 unstable modes in the solver and in the formula, at the same wavenumbers (`|k| = 1.11, 1.18, 1.24`), no sign mismatch |
| P2-c(ii) | kernel C: the flow from uniform + noise develops a modulation `≥ 0.1` and ends below `Ω₀` by `≥ 10⁻³` | **FAILED AS REGISTERED** | CVODE `ConvFailure` in the first chunk; the returned state is the initial one (modulation `5.8×10⁻³`, `Ω` above `Ω₀`) |
| P2-d | planted bug (`Ũ(0)` doubled) must violate P2-a | **PASS** (the gate bites) | density deviation `0.5` on all 5 starts |

`all_pass = false`: the registered Phase 2 test is **not passed** as a whole.

## What happened in P2-c(ii), and what it means

1. *Registered run.* `ConvFailure` in the first chunk of the flow (`τ ≤ 100`); because the chunk is lost on failure the
   returned field is the starting one, which is why the recorded modulation is only the noise (`5.8×10⁻³`).
2. *Amendment A2* (relaxed tolerances, same seed): the **same** failure (42 193 steps, same returned state). Not a tolerance
   effect.
3. *Amendment A3* (diagnostic in chunks of `Δτ = 0.5`, exploratory; `results/phase2/mf_debug_trace.txt`): `Ω` decreases monotonically
   from the start, the modulation grows exponentially at about `0.12` per unit `τ` from `10⁻³`, passes `0.1` near `τ ≈ 38`
   (`Ω` below `Ω₀` by `7×10⁻⁴`, relative; by `2×10⁻³` at `τ = 42.5`), reaches `4.5` at `τ ≈ 56` (`Ω` about twice `Ω₀`), and
   then the integration runs away (`ConvFailure` in the chunk ending at `τ = 58`, after 42 625 steps).
4. *Cause (analytic).* With the registered depth 28 the grand-canonical functional of kernel C at fixed `μ` is **unbounded below**:
   a stripe of Gaussian profile has interaction energy density `½ n̄² F(w)`, `F(w) = Ũ(0) + 2 Σ_{m≥1} Ũ(m k₀) e^{−m²k₀²w²}`,
   and `min_w F = −19.0` over the harmonics representable on the grid (`−15.5` with `m ≤ 8`); so `Ω → −∞` as `n̄` grows and
   no stationary state exists. My own check in amendment A1 (a cosine profile only) was incomplete. In this kernel family
   there is no bounded, linearly unstable control at fixed `μ`: `min_w F < 0` already for depth ≳ 18 while linear instability
   needs depth > 24.8.
5. *Reading.* The failure is a flaw of the **control as designed**, not of the solver and not of the Lean statement. The
   content of the gate (the uniform state of a kernel with a negative Fourier band is not the minimiser; a modulation grows;
   `Ω` falls below `Ω₀`) is met before the run-away and is *a fortiori* true (no minimum exists). The gate is recorded as failed
   because the registered procedure did not produce that evidence. A bounded control (fixed-mass flow, or a regularising term)
   was not run.

## What Phase 2 supports

* The Lean statement `MeanField.uniform_minimises` and the Bogoliubov spectrum are consistent with the solver on the bilayer
  kernel (P2-a, P2-b) to `10⁻¹⁰`–`10⁻¹⁴`, and the same linear instrument detects a negative Fourier band (P2-c(i)); the
  planted bug is caught (P2-d).
* It does **not** test anything about excitons beyond this bare kernel: no screening, no exchange, no temperature, no
  correlations. A mean-field state is not the quantum fluid.
* CVODE (dense, finite-difference Jacobian) integrates a 256-unknown stiff relaxation to `10⁻¹²` in about 1100 steps and
  fails, as it should, on a functional without a minimum.

## Files

`exploration/exciton/results/phase2/{reference.json, mf_report.json, mf_report_A2.json, mf_run_log.txt, mf_debug_trace.txt, summary.json}`;
program `exploration/exciton/rust/qf-exciton-p1/src/bin/mf.rs` (modes: registered run; `MF_MODE=ctrl_A2`; `MF_MODE=ctrl_debug`).
