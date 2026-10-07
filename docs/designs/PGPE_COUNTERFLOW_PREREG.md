# Pre-registration: the self-generated counterflow of a vortex pair in a closed box (direction R2-01 / D1)

Filed 2026-10-07 09:00, **before the L = 96 control (W2 of amendment A1) has been read** — its two runs are
integrating. This document fixes what is done in each outcome of W2, so that the campaign that follows is
pre-registered whichever way the control falls. Selection: `RESEARCH_DIRECTIONS_2026-10-07.md` (autoresearch round 2,
rank 1). Lean companion: `DissipativeVortexDynamics.wind_stall` (plane), to be extended to the torus drive.

## The hypothesis (W, restated quantitatively)

A pair of separation `d` in a box of side `L` at normal fraction `ρ_n/ρ` carries the impulse `P(d) = 2πρ_s d·p(d/L)`,
with `p` the torus momentum factor (measured at T = 0: 0.96–0.99 for `d/L ≤ 0.19`). As the pair shrinks, the shed
impulse becomes a drift `u = [P(d₀) − P(d)]/(ρ_n L²)` of the normal component along the pair's motion; the friction
acts on the relative velocity, `ḋ = −2α[v_pair(d) − u]`, with `v_pair(d)` the torus pair speed (`≈ 1/d`). The pair
stalls where `v_pair(b) = u(b)`, which for the plane forms is `(d₀ − b)b = C_L ≡ ρ_n L²/(2πρ_s)`; a stall exists iff
`d₀²/4 > C_L`. At T/T_BKT = 0.14 (`ρ_n/ρ = 0.027`): `C_64 = 18.1`, `C_96 = 40.7`, `C_128 = 72.4`.

## Outcome of W2 and what follows

W2 (registered in A1): single pair, `d₀ = 12`, T/T_BKT = 0.14, L = 96, two runs of 4000 time units. **Supported**
if the late `d²` slope is at least 50 % of the early one or the pair annihilates (no stall: `d₀²/4 = 36 < 40.7`);
**refuted** if both pairs stall near the L = 64 separation (`b ≈ 9–10`). Either way the two runs are reported in the
paper with Figure 3.

- **If W2 supports W:** the campaign below runs (C1–C5).
- **If W2 refutes W:** the stall is not the box's. W is withdrawn as a mechanism for these runs; the campaign below
  does not run; the paper's Section 4 is rewritten as a reported observation with the refuting control; the next
  campaign is the friction law (`PGPE_FRICTION_LAW_PREREG.md`, D7/R2-04), with the microcanonical-bottleneck
  question (R2-05) second.
- **If the two W2 runs disagree** (one stalls, one does not): W2 is inconclusive; two more L = 96 runs are added
  before anything else, and the rule above is applied to the four.

### Amendment W2-A (2026-10-07 23:35, filed before runs 3 and 4 are read; they end ≈ 00:30)

Runs 1 and 2 disagreed (run 1 meets the no-stall criterion, run 2 does not; CLAIM-090), so runs 3 and 4 were
launched at 20:48. "The rule applied to the four" is made explicit now, since a 2–2 split is possible:

- **≥ 3 of 4 meet the criterion → SUPPORTED** (no stall at L = 96): the counterflow campaign below runs.
- **≤ 1 of 4 meets it → REFUTED**: the box mechanism is withdrawn as written; the friction-law campaign runs.
- **2–2 → INCONCLUSIVE at this sample size**: the binary control cannot decide a graded effect. The paper reports
  the split and the parameter-free wind-equation comparison without claiming support. The friction-law campaign
  (independent of W) runs first; the stall map runs second, and its C1 (a graded criterion over eleven cells) is
  then the decisive test of W, with the kill conditions as written.

If one of the four runs fails (tracking lost, crash), the rule is applied to the three: 3 meet → supported,
0 meet → refuted, otherwise inconclusive. The evaluation is `exploration/pgpe/evaluate_w2.py`; the night
workflow `scripts/night_publish_v2.py` applies exactly this rule and fills the paper's pending sentences from
templates written before the data (one per outcome).

## Campaign (conditional), frozen now

Single pairs, corrected imprint, raw detection with sub-grid refinement, 4000 time units, positions, total field
momentum and band momentum `P_{|k|>1}` saved every time unit; occupation spectrum `n_k` saved every 100 time units.

| cell | L | d₀ | d₀²/4 | C_L | predicted |
|---|---|---|---|---|---|
| 1–4 | 64 | 8, 10, 12, 14 | 16, 25, 36, 49 | 18.1 | no stall, stall, stall, stall |
| 5–7 | 96 | 12, 14, 16 | 36, 49, 64 | 40.7 | no stall, stall, stall |
| 8–9 | 128 | 16, 20 | 64, 100 | 72.4 | no stall, stall |
| 10–11 | 64 at T/T_BKT = 0.27 (`ρ_n/ρ = 0.053`, `C_64 = 36.8`) | 10, 14 | 25, 49 | 36.8 | no stall, stall |

Two runs per cell (seeds), 22 runs; estimated 60 CPU-hours.

- **C1 (stall map).** A run "stalls" if it does not annihilate within 4000 time units and its late `d²` slope
  (t ∈ [2000, 4000]) is below 25 % of the early one (t ∈ [100, 600]) in magnitude, or positive. Prediction: at
  least 9 of the 11 cells behave as the table says (both seeds).
- **C2 (stall separation).** In the stalled cells, the mean separation over the last 1000 time units is within
  ±1.5 of the torus-corrected prediction (plane `b` corrected by the measured `p(d/L)` and torus pair speed).
- **C3 (the wind seen directly).** `P_{|k|>1}` along the initial impulse against the impulse shed, slope in
  [0.4, 1.2] in every run; and the occupation anisotropy `Σ_{|k|>1} k_∥ n_k` grows with the impulse shed.
- **C4 (temperature).** Cells 10–11 behave as predicted (the stall criterion moves with `ρ_n`).
- **C5 (relaxation, report only).** Whether the stalled state persists to 4000 or decays — by vortex nucleation
  as imposed counterflow does (Krstulovic & Brachet 2011), or otherwise.
- **Verdict.** C1 ∧ C3 → the counterflow mechanism is established for closed classical fields; C2 then calibrates
  the law. C1 failing (≤ 7 cells) → W refuted as a quantitative law even if W2 supported it qualitatively.
  Kill: any cell with `d₀²/4 < 0.6 C_L` that stalls, or any with `d₀²/4 > 1.6 C_L` that annihilates, in both seeds.

Known answers: the T = 0 control of A1 (no shrink, momentum constant) and the zero-impulse pairs at each temperature
(steady shrinking). Limits: one cutoff, `mg = 1`; the normal component is the classical phonon bath.
