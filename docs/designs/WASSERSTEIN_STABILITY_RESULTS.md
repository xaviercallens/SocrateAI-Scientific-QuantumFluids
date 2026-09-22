# Results: the cellular Wasserstein stability bound on the seven closed-loop pairs

Against `WASSERSTEIN_STABILITY_PREREG.md` (amendments A1–A3). Run 2026-09-22, `exploration/tda/wp_stability.py`
(`--cert-topk 200`), results in `data/generated/kinetic_tda/wp_stability_results.json` (run 1, with the
phase-space pair mean-normalised, kept as `wp_stability_results_run1_P1meannorm.json`); tables for the
paper by `wp_stability_report.py`; exploratory sweep `wp_stability_psweep.py` →
`wp_stability_psweep.json`. Paper: `paper/wasserstein_slack.pdf`.

## Controls

| # | Expected | Got | Verdict |
|---|---|---|---|
| C1 | union-find `H0` == GUDHI `H0`, random arrays × 4 periodicities, then all 12 real arrays | exact on all | **PASS** |
| C2 | toy: `‖f−g‖_1 = ‖f−g‖_2 = 5/2`, `W_1 = 5/2`, `W_2 = √(37/8)` (A1), `ℓ^∞` `W_1 = 7/4` | 2.5, 2.5, 2.5, 2.150581316760657, 1.75 | **PASS** (my hand `W_2` was wrong; A1) |
| C3 | raised strict-minimum pixel: slack exactly 9 (`p=1`), 3 (`p=2`); `W = δ` | 9.000, 3.000; `δ` reduced to half the neighbour gap as the prereg allowed (recorded) | **PASS** |
| C4 | T1's plan with T2's potentials rejected | max violation 0.898, primal 10.56 ≠ dual 21.60 | **PASS** |

## The seven pairs (theorem's metric: `ℓ_p` ground cost, full diagrams, all degrees)

| pair | ε (sup) | `H0` bars | `‖f−g‖_1` | `W_1` | `Z_1` | `S_1` | `V_1` | `‖f−g‖_2` | `W_2` | `Z_2` | `S_2` | `V_2` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | 2.0919 | 748 / 747 | 2.613e5 | 45.67 | 698.9 | 5720 | **374** | 364.9 | 1.470 | 20.13 | 248 | **18.1** |
| R2 | 2.1990 | 965 / 876 | 3.712e5 | 55.46 | 868.7 | 6690 | **427** | 476.4 | 1.513 | 21.95 | 315 | **21.7** |
| R3 | 2.3938 | 1324 / 1313 | 4.847e5 | 79.58 | 1291 | 6090 | **376** | 593.1 | 1.716 | 26.62 | 346 | **22.3** |
| T1 | 2.1764 | 788 / 985 | 1.990e6 | 103.0 | 794.9 | 19300 | **2500** | 1205 | 2.666 | 21.30 | 452 | **56.6** |
| T2 | 2.4303 | 985 / 1352 | 2.102e6 | 248.0 | 1109 | 8480 | **1900** | 1276 | 4.722 | 24.82 | 270 | **51.4** |
| S1 | 1.4848 | 505 / 788 | 1.695e6 | 285.5 | 530.4 | 5940 | **3200** | 1015 | 8.117 | 15.63 | 125 | **64.9** |
| P1 (raw) | 0.2878 | 2150 / 1623 | 9707 | 19.70 | 70.06 | 493 | **139** | 30.31 | 0.3871 | 1.645 | 78.3 | **18.4** |

`Z_p` = trivial bound (erase both diagrams); `S_p = ‖f−g‖_p / W_p` (slack); `V_p = ‖f−g‖_p / Z_p`, the bound
is informative iff `V_p < 1`. Part (ii) with `k=0`: `B^(ii,0)_1 / B^(i)_1 ∈ [0.74, 0.75]`, `B^(ii,0)_2 / B^(i)_2 ∈ [0.85, 0.87]`
on every pair. The six GP pairs reproduce the previous round's `ε` and `ℓ^∞` top-30 `W_1` to all printed digits.

## Verdicts

| # | Statement | Verdict |
|---|---|---|
| P1 | bound (i) and (ii, k=0) hold, `p = 1, 2` | holds on all 7 (pipeline check) |
| P2 | R1–R3: `V_1 ≥ 1` | **PASS** (374, 427, 376) |
| P3 | R1–R3: `V_2 ≥ 1` | **PASS** (18.1, 21.7, 22.3) → **kill of `closed_loop.pdf` §7.1 executed**: no Wasserstein stability theorem makes ξ/Δx = 4 vs 8 informative |
| P4 | phase-space pair: `V_1 < 1` | **FAIL** (`V_1 = 139`, `V_2 = 18.4`) — my prediction was wrong |
| P5 | T1, T2, S1 reported | `V_1 = 2500, 1900, 3200` |
| P6 | `S_1 ≥ 10` on every GP pair | **PASS** (5720 … 19300) |
| P7 | `ℓ^∞` top-30 `W_1` ≤ `ℓ_1` full `W_1` on every pair | **PASS** |

**Mechanism, measured.** `V_1 = (4NM/(n+m)) · (mean cell change / mean bar length)`: cells per bar 398–3244
on the GP pairs, mean `|Δρ|` per cell 0.25–0.50 `n₀` — the perturbation is dense (two different turbulent
trajectories, or two times), and the `ℓ_1` norm charges every cell. `V_2 / √V_1 = 0.94–1.56` on all seven,
the predicted `(cells/bar)^{1/p}` scaling. Exploratory `p`-sweep (`H0` only): min over `p ∈ {1,2,4,8,∞}` of
`V_p` is 2.1–4.0, never below 1. The bound is sharp only for sparse perturbations (C3: slack 9 = cells per
pixel).

**What the slack says.** `W_1 / Z_1 = 0.062–0.065` on the resolution pairs: the diagrams are within 7 % of
erasure of each other while the fields differ by a quarter of `n₀` per cell. Persistence is far more stable to
dense perturbations than any stability theorem of this family can certify.

## Certificates

28 degree-level certificates (`H0`, `H1`, `p = 1, 2`, 7 pairs), full-diagram scope where `n·m ≤ 10⁶` (R1, R2,
T1, S1 in `H0`), top-200 otherwise (A2). 22 at relative gap ≤ 1e-15 and violation ≤ 3e-16; 6 at the solver's
1e-7 feasibility tolerance (violations 7e-10 … 1.4e-7, dual simplex retry did not remove them). For those the
paper reports the rigorous certified gap after shifting `u` by `−δ` (`W^p ≥ Σu + Σv − Rδ`): worst 1.5e-4 relative (R1, p=2).

## Erratum found on the way (A3)

The previous round's phase-space certificate (`n, m = 5, 5`, `W_1 = 0.0632`) was computed on 5 points per
side; the correct `ℓ^∞` top-30 value on the raw arrays' full diagrams is **`W_1 = 0.6490389871651492`**. The
diagrams stage was correct (`d_B = 0.0325030850643` reproduced). Recorded in `CLOSED_LOOP_RESULTS.md`
and LEDGER (CLAIM-032 erratum). The published PDF is unchanged.

## Not done

No Lean for Thm 4.6; no `p`-sweep certification; no finite-temperature run (direction 2 stopped at its gate);
no Lean for the Fricke/`Γ₀(n)⁺` group theory (direction 3: verdict "shadow, not instance", see the paper §6.3).
