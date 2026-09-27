# Results, round 3: two thermometers (Part A), coarsening after a 16-pair intervention (Part D), L = 128 (Part C)

Pre-registration `PGPE_R3_PREREG.md`. Data `data/generated/pgpe/r3/`, log `r3.log`, analysis `exploration/pgpe/analyze_r3.py`,
calibration `vortex_thermometer_cal.json` (N = 4–24) and `vortex_thermometer_cal_large.json` (N = 26–40).
Status (2026-09-25 21:55): Parts A and D complete (9 runs); Part C running (launched 21:41, ≈ 7 h).

## Calibration extension (kill rule: closure within 10 % at every size used)

N = 18: 1.193, 20: 1.197, 22: 1.206, 26: 1.199, 28: 1.190, 36: 1.207 (set 1.2) — all PASS; N = 24, 32, 40: see `cal_extend*.log`.

## Part A — two thermometers on the V and P arms (complete)

Controls C1–C3 of round 2 hold by construction (same code, same seeds); energy drift ≤ 2.1×10⁻⁷ on all six runs.

| base | P1: `T_v > 1.5 T_b` in block 1 | P2: Spearman(\|T_v − T_b\|, block) < −0.7 | P3: bath loss ≈ flow gain (≤ 30 %) | P4: P-arm E_inc within 15 % |
|---|---|---|---|---|
| e = 0.60 | **hot, unreadable** (all 10 samples at β_WM < 0.3): counts as PASS by the pre-set rule | not evaluable (0 readable blocks) | **PASS**: −57.3 vs +67.2 (15 %) | PASS |
| e = 0.90 s11 | **PASS**: T_v = 2.91 vs T_b = 0.386 (×7.5) | **FAIL**: ρ = −0.56 (15 readable) | **PASS**: −50.6 vs +54.5 (7 %) | **FAIL** |
| e = 0.90 s12 | **PASS**: T_v = 2.22 vs T_b = 0.399 (×5.6) | **FAIL**: ρ = −0.47 (15 readable) | **PASS**: −40.8 vs +55.2 (26 %) | PASS |

Composite: P1 all ✓, P3 all ✓, P2 (two of three) ✗, P4 (all) ✗.

**Block series (e = 0.90).** T_v: s11 2.91, 1.80, 3.32, 2.56, 2.85, 2.21, 2.62, 2.20, 2.69, 2.20, 2.19, 2.30, 2.06, 2.17,
1.92; s12 2.22, 3.14, 2.86, 2.77, 2.78, 2.37, 2.37, 2.50, 2.52, 2.46, 2.17, 2.22, 2.98, 2.23, 2.07. T_b stays in
0.37–0.41 throughout. N_v 13–19 (s11), 11–17 (s12). The vortex temperature drifts down (≈ 2.9 → 1.9 over 1500 time
units) but with block-to-block scatter of ±0.4, so the pre-set monotonicity strength (ρ < −0.7) is not reached; the
sign is the predicted one on both bases.

**Reading.** With our own calibrated instrument and block by block: the injected label carries a temperature 5–8×
the bath's on the e = 0.90 bases and an unreadably hot one (β_v ≈ 0) at e = 0.60; the bath's energy loss is the
flow field's gain within 7–26 % on all three bases. What is not established as written: the *rate* of approach
(P2), and the phonon control's flow energy stayed within 15 % on two bases but not on s11 (its thermal pairs, 3–8
of them, move its incompressible energy by more than that; see below).

**P4 detail.** Recorded after the verdict: the P arm at e = 0.90 s11 carries a fluctuating number of thermal pairs;
its E_inc runs 31.1 → 25.3 (block 1 → 6), a 19 % excursion against the 15 % allowed, with N_v between 3.2 and 8.2; the other P arms stay within 7–8 %. The criterion was set for
"no injected flow", which holds in the sense that E_inc(P) stays at the 25–30 level against 55–85 for V; the
relative threshold was too tight for a small, fluctuating baseline. Reported as FAIL as written.

## Part D — 16-pair intervention (complete; see amendment R3-A1)

Imprint check: 32 imprinted, 32/40/36 detected (thermal pairs included), neutral on all three. Energy drift ≤ 2.2×10⁻⁷.

| base | torus winding sector (imprint → final) | D1: power law, z ∈ [1.5, 2.0] | D2: bath cools then recovers |
|---|---|---|---|
| e = 0.60 | **(2, 0) → (0, 0)**: a winding-2 current that decayed by phase slips | not evaluable as pre-registered (non-zero sector); post hoc on [50, 1500]: power law z = 4.6 (R² = 0.77), exponential τ ≈ 1100 (R² = 0.95) | **PASS**: T_b 0.092 (base 0.115) → 0.149 |
| e = 0.90 s11 | (0, 0) → (0, 0) | **FAIL**: no decade-long window with R² ≥ 0.95; post hoc z = 3.4 (R² = 0.43) | **PASS**: 0.432 (base 0.443) → 0.480 |
| e = 0.90 s12 | **(1, −3) → (−3, 0) measured**: a winding-3 current, intact after 1500 | not evaluable as pre-registered | **PASS**: 0.390 (base 0.458) → 0.458 |

D1 (two of three): **FAIL**. D2 (all): **PASS**.

### What the two accidental sectors show (post hoc)

* **s12 — the persistent current (thought experiment A).** Final state: mean winding around the x-cycle −3.21,
  momentum P/N = −2.99 × 2π/L, and 29.5 % of the atoms in the mode k = (−3, 0)·2π/L while the k = 0 population is
  0.003 throughout: the "condensate fraction" of the earlier rounds reads zero because the whole condensate flows.
  E_inc plateaus at 248 ≈ 178 (the energy of a winding-3 superflow, ½ n (2π·3/L)² L²) + ≈ 70 (the vortex flow, the
  level s11 relaxes to). Sixteen vortices remain; the current does not decay. T_v reads 2.3 → 1.3 against T_b ≈ 0.42.
* **e = 0.60 — the current that decayed.** Winding 2 at the imprint, 0 at t = 1500: vortices crossing the torus
  changed the winding (the discrete `slip_of_winding_change`, seen). The current's energy, ≈ 79, plus the pair
  annihilations went to the bath: T_b rose from 0.092 to 0.149, ≈ 85 units over ≈ 1500 modes. E_inc 199 → 66.
  T_v stayed 4–10 against T_b ≈ 0.1 (ratio 40–100) for the whole run.
* **s11 — the clean coarsening arm.** N_v 54 → 16 with a plateau near the thermal count; no power law over a decade;
  the condensate recovers 0.11 → 0.57 as E_inc falls 178 → 56 and T_b rises 0.432 → 0.480: the annihilation energy
  returns to the bath (Kanai–Guo's sound), closing the cycle that Part A opened.

**Post hoc, 2026-09-26: a second, real-space diagnostic on the same three runs.** Gauthier et al.'s 2019
Onsager-cluster order parameter (Science 364, 1264; the distance between the +1 and −1 vortex sub-populations'
own centroids, adapted for a periodic box — `observables.onsager_dipole`, `onsager_dipole_analysis.py`), applied
to the vortex positions already on disk, no new run: on **s12 (the persistent current)** it *rises* over the run,
block by block, 0.02 → 0.14 → 0.26 → 0.14–0.23 (noisy, but a clear upward trend from the first third to the rest);
on **s11 (clean coarsening)** it *falls*, 0.17–0.19 in the first third down to 0.02–0.08 by the end; on **e = 0.60
(the decaying current)** it stays high and noisy throughout (0.1–0.42), consistent with a small, fluctuating
vortex number rather than a clean trend. Reported, not predicted: the persistent-current arm's vortices become
*more* clustered by sign as the run proceeds, opposite to the coarsening arm's vortices becoming *less* so — a
plausible geometric signature of the sector organising the surviving sixteen vortices into the array a winding-3
superflow would carry, distinct from the mixing a decaying, sector-free population shows. Not pre-registered;
one run per case; not to be read as more than what it is.

**Reading.** The 16-pair arms did not test coarsening cleanly (one arm, and it failed D1), but they produced, by a
design error, the two branches of the ring thought experiment on our own torus: a protected winding-3 current that
outlives 1500 time units with its condensate displaced to k ≠ 0, and a winding-2 current that decays by phase
slips and heats the bath by the amount its energy predicts. Both are single runs; neither is a pre-registered
result; both are direct observations of the sector physics `TopologicalProtection.lean` is about.

## Part C — complete; admission failure at L = 128, C1/C2 void (resolved by Part C2 below)

**Timing (disclosure).** The prereg's "≈ 7 h wall" estimate was wrong in both directions: a same-evening scaling
re-estimate (grid ×4.6, duration ×2.7 vs. round 3 ⇒ ×12) predicted ≈ 22 h; the six runs actually finished after
≈ 13.6–13.8 h each (49069–49614 s), launched 2026-09-25 21:41, done 2026-09-26 ≈ 11:20–11:28. Energy drift
≤ 1.1×10⁻⁶ on all six — the integration itself is fine.

**Admission (A4: `R_L ≤ 1.25`, `R_T ≤ 1.1·R_L`): 2 of 6 pass.**

| e | seed | R_L | R_T | admitted | K | η | ηK−1 |
|---|---|---|---|---|---|---|---|
| 1.00 | 11 | 1.12 | 2.42 | **no** | −14.5 | 0.409 | −6.93 |
| 1.00 | 12 | 0.89 | 1.56 | **no** | −9.3 | 0.296 | −3.75 |
| 1.10 | 11 | 1.14 | 1.87 | **no** | −6.7 | 0.471 | −4.15 |
| 1.10 | 12 | 1.12 | **0.32** | yes | 7.51 | 0.171 | 0.284 |
| 1.20 | 11 | 0.98 | 1.23 | **no** | −2.3 | 0.535 | −2.23 |
| 1.20 | 12 | 1.10 | **0.38** | yes | 5.91 | 0.245 | 0.449 |

Four of six runs have `R_T` two to four times `R_L` — the transverse current fluctuations exceed the
longitudinal ones, giving a **negative** `K = n_s·2π/T` (unphysical for a superfluid, where `J_T` should not
exceed `J_L`). Block-by-block `T_b`, `cond` and `n_v` are flat over the sampled window in every run, admitted or
not (e.g. e = 1.00, s = 11: `T_b` 0.496→0.496, `n_v` 85.2→80.2) — **the runs are not still relaxing on the
timescale sampled; the anisotropy is a standing feature of the state reached, not a transient the window missed.**
The most likely explanation, not tested here: `t_tr = 3000` was carried over unchanged from the `L = 32/64`
rounds; the number of long-wavelength modes that set the transverse/longitudinal current split grows with the
box area, and their equipartition time may scale with `L`, so the same warm-up window that sufficed at `L ≤ 64`
may be too short at `L = 128`. This was not anticipated in the pre-registration and is recorded as a gap, not
patched here.

**C1 (duality-offset ratio).** Computed on the 2 admitted points only (`e = 1.10`: ηK−1 = 0.284; `e = 1.20`:
ηK−1 = 0.449), against the round-2 `L = 64` values (0.12, 0.20): ratio = 2.29. **FAIL as pre-registered**
(criterion: ratio ∈ [0.6, 1.0], a *shrinking* offset with `L`, per Hasenbusch). The offset *grew* instead of
shrinking. Given the admission failure just described and that each energy has only one surviving seed (no
within-energy averaging, unlike round 2's `n = 3` per point), **this result is reported, not trusted**: it is
equally consistent with a real finite-size surprise and with a biased subsample (whichever seed happened to
reach a more isotropic state at each energy is exactly the one admission keeps, which need not track the
finite-size trend the criterion was designed to see).
**C2 (T_BKT(128) ≤ T_BKT(64)).** No crossing of `K = 4` in the admitted range (`e = 1.10`: K = 7.5;
`e = 1.20`: K = 5.9, both above 4; `e = 1.00`'s two runs, which might have bracketed the crossing, are both
excluded). **Not bracketed — inconclusive**, not a pass or fail.

**Reading.** Part C does not, as run, extend the round-2 finite-size ladder to `L = 128`: the admission criterion
built for smaller boxes rejects two-thirds of the sample, and the two survivors give a same-direction offset
that goes the wrong way for the wrong reason (a subsample selected by isotropy, not by physics). The honest
verdict is **C1: FAIL as written; C2: not bracketed; both void pending a rerun with a longer equilibration
window at this box size** — recorded as a recommendation for a future round, not executed in this one (each
`L = 128` run costs ≈ 13.7 h; a rerun is a deliberate compute decision, not a default next step).

## Part C2 — rerun with doubled equilibration (amendment R3-A2): admission cured, C1 still fails

Pre-registered in amendment R3-A2 as **a diagnostic of the equilibration hypothesis, not a new physics claim**:
same six `(e, seed)` pairs, same admission rule, `t_tr` doubled `3000 → 6000` (`t_end = 7000`, same 1000-unit
sampling window); "if admission improves, C1/C2 are re-evaluated on the C2 data in place of C."

**Timing (disclosure).** Launched 2026-09-26 14:49; the prereg estimated ≈ 24 h per run; the six runs took
96041–97085 s (26.7–27.0 h), finishing 2026-09-27 ≈ 17:30–17:47 — a ≈ 11 % underestimate. Energy drift
1.2–1.8 × 10⁻⁶ on all six (kill rule `10⁻⁵` not triggered).

**Admission: 2 of 6 → 5 of 6.**

| e | seed | Part C: R_L / R_T / n_s/n / admitted | **C2**: R_L / R_T / n_s/n / admitted | C2: T | K | η | ηK−1 |
|---|---|---|---|---|---|---|---|
| 1.00 | 11 | 1.12 / 2.42 / −1.16 / no | 0.98 / 1.28 / −0.30 / **no** | 0.507 | −3.75 | 0.292 | — |
| 1.00 | 12 | 0.89 / 1.56 / −0.75 / no | 1.17 / 0.20 / +0.83 / **yes** | 0.504 | 10.29 | 0.136 | +0.404 |
| 1.10 | 11 | 1.14 / 1.87 / −0.64 / no | 1.13 / 0.23 / +0.80 / **yes** | 0.602 | 8.35 | 0.170 | +0.423 |
| 1.10 | 12 | 1.12 / 0.32 / +0.72 / yes | 1.03 / 0.29 / +0.72 / **yes** | 0.602 | 7.47 | 0.174 | +0.297 |
| 1.20 | 11 | 0.98 / 1.23 / −0.25 / no | 1.03 / 0.33 / +0.67 / **yes** | 0.688 | 6.15 | 0.227 | +0.396 |
| 1.20 | 12 | 1.10 / 0.38 / +0.65 / yes | 1.03 / 0.37 / +0.64 / **yes** | 0.694 | 5.80 | 0.220 | +0.274 |

**The equilibration hypothesis is confirmed for the admission failure.** Three of the four rejected runs
become physical and admitted (negative `n_s/n` → +0.67 to +0.83); the two runs admitted in Part C stay
admitted with essentially unchanged superfluid fraction (0.716 → 0.716, 0.654 → 0.640), a built-in control
that the longer warm-up changed what was unequilibrated and nothing else. **One run still fails** (e = 1.00,
s = 11): improved (`R_T` 2.42 → 1.28, `n_s/n` −1.16 → −0.30) but unphysical, with **exponential** correlation
decay in every block and condensate fraction 0.33 against 0.51 for the other seed at the same energy — a
different state, not merely a slower approach. Checked, not assumed: its final field carries **no net torus
winding** (`(W_x, W_y) = (0, 0)`, as do all twelve Part C and C2 final fields), so it is not a trapped
winding sector like Part D's. Its cause is **not diagnosed** here (candidates, untested: a longer
equilibration still, the lowest energy being the slowest to equilibrate; a metastable vortex-cluster state).

**C1 (re-evaluated on C2, per R3-A2): FAIL, now robustly.** Offsets `ηK−1` at `L = 128`: 0.404 (e = 1.00,
n = 1), 0.360 (e = 1.10, n = 2), 0.334 (e = 1.20, n = 2), against `L = 64`: 0.12, 0.12, 0.20. Ratio **2.50**
(criterion: ∈ [0.6, 1.0], a shrinking offset). The offset **grows** with `L` at every energy.

This **resolves the question Part C left open.** Part C's failure rested on two admitted runs and was "equally
consistent with a real finite-size surprise and with a biased subsample." C2 rules out the subsample
explanation: the seeds that *failed* admission in Part C and pass now give 0.40–0.42, the seeds that always
passed give 0.27–0.30, and *both* groups lie above the `L = 64` values. The growth is real in this model and
this estimator. Its *magnitude* is not well determined — the seed-to-seed spread within an energy (≈ 0.12) is
comparable to the `L = 64` offsets themselves — so "grows" is the finding, not "grows by 2.5×". What it means
is **not settled here**: the criterion encoded the expectation (Hasenbusch) that finite-size corrections to
`η·K = 1` shrink with `L`; a growing offset could instead reflect a systematic of the `η` extraction whose
fit window does not scale with `L`, or genuine logarithmic corrections near BKT at these vortex densities
(`n_v` 77–362). Separating these needs an `L`-scaled `η` fit and a third box size — recorded as open work,
not attempted in this round.

**C2 criterion (T_BKT(128) ≤ T_BKT(64)): not bracketed.** `K > 4` at all three energies (10.3, 7.9, 6.0); the
ladder's highest temperature (0.69) is below `T_BKT(64) = 0.821`. Inconclusive, as in Part C — reaching the
crossing needs higher `e`, not longer runs.

**Verdict.** Admission failure: **an equilibration artefact, now cured (5/6)**. C1: **FAIL, robust** — the
finite-size offset grows with `L`, and this is no longer attributable to selection. C2: **not bracketed**.
LEDGER CLAIM-065.

