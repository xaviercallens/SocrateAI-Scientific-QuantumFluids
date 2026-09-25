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

**Reading.** The 16-pair arms did not test coarsening cleanly (one arm, and it failed D1), but they produced, by a
design error, the two branches of the ring thought experiment on our own torus: a protected winding-3 current that
outlives 1500 time units with its condensate displaced to k ≠ 0, and a winding-2 current that decays by phase
slips and heats the bath by the amount its energy predicts. Both are single runs; neither is a pre-registered
result; both are direct observations of the sector physics `TopologicalProtection.lean` is about.

## Part C — running

