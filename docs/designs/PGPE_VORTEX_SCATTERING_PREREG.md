# Pre-registration: the vortex–phonon transport cross-section σ(k) from T = 0 scattering, and the friction law it predicts

Filed 2026-10-09 ≈ 08:30 (the file was written before the scan was launched at 08:32:04; the git commit followed seconds later, at 08:32), **before any run of the scan below has finished**. Follows `PGPE_FRICTION_LAW_RESULTS.md` (CLAIM-096/097: α = 0.054 T at three cutoffs, c = α/(ρ_n/ρ) not a vortex property)
and the constraint stated in `friction_law.tex` §4: if the drag is a sum over independent Bogoliubov modes, a cutoff-independent α requires the vortex's transport cross-section
to fall faster than 1/k for kξ ≳ 2, whereas the Born law σ_∥ = κ²k/8c² (Sonin 1997) grows with k.

## Literature gate (2026-10-09)

Two searches of the alphaXiv preprint index (2.5 M papers) for numerical Gross–Pitaevskii measurements of σ_∥(k)/σ_⊥(k) of a vortex beyond the Born regime found: the analytic Born/Aharonov–Bohm
treatments (Pitaevskii 1959, Iordanskii 1964, Sonin 1997, cond-mat/9606099), a Klein–Gordon (acoustic-metric) superradiance study of vortices (gr-qc/0503089), Bogoliubov scattering by disorder
(0802.4366), vortex–wave collisions (2510.01973, not read in full), and mutual-friction work in dissipative GPE (2605.25915, 1412.0706). **No direct measurement of σ(k) of a GP vortex at kξ ≳ 1 was found.**
This is a screen of one index, not a proof of novelty; the paper will say so and cite what was read.

## Instrument (exploration/pgpe/vortex_wave_scattering.py)

T = 0 PGPE (ħ = m = g = n = 1, c = 1, κ = 2π, ξ = 1), box L = 64, grid N = 128 (dx = ξ/2, k_cut = π). A vortex–antivortex pair at x = L/2 ∓ d₀/2, d₀ = 32 (a neutral saddle: each vortex sits midway between its
antivortex and the antivortex's image) in the uniform condensate, dressed with a travelling Bogoliubov wave along ±y (perpendicular to the separation):
ψ = ψ_pair (1 + ε [u e^{±iky} − v e^{∓iky}]), u, v the uniform-condensate Bogoliubov amplitudes, k = 2πm/L. A wave of momentum flux j along k̂ exerts on a vortex of circulation sign q the force
F = c σ_∥ j k̂ − q c σ_⊥ ẑ×j (Sonin 1997, Eq. 43); the Magnus balance v_i = q_i ẑ×F/(ρκ) gives: the two vortices drift in opposite x directions (the pair separation d_x changes at the rate
**ḋ_x = ∓ 2 c σ_∥ j/(ρκ)**) and, from σ_⊥, together along k̂ (**ẏ_c = ± c σ_⊥ j/(ρκ)**). j is the momentum of the same dressed field without vortices, divided by L².
Observables: the slopes of d_x(t) and of the centroid y_c(t) over t ∈ [50, 400], minus the same slopes of the **no-wave control** (ε = 0, same box); sub-grid vortex tracking as in the transport campaign.
The pair state carries a uniform counterflow ū = P_pair/L² = 0.049 along y (Galilean boost, the same in all runs, subtracted by the control).

Wave amplitudes are set per k to a **fixed peak velocity amplitude A_v = k ε (u + v) = 0.04** (density amplitude ≲ 5 %).

## What has already been seen (exploratory, NOT counted in any test below)

One probe at m = 4 (k = 0.393), ε = 0.05, ±y, 400 t.u.: control slopes d_x +1×10⁻⁵, y_c +0.0493; Δ(d_x slope) = −6.3×10⁻⁴ (+y), +6.7×10⁻⁴ (−y); j = 9.75×10⁻⁴;
σ_∥ = 2.04 and 2.15 (Born κ²k/8c² = 1.94); Δ(y_c slope) = ±2.4×10⁻⁴, σ_⊥ = 1.57 (Iordanskii point-vortex value κ/c = 6.28). **The point m = 4 is excluded from tests P2 and P4's fit to the
Born law; it is part of the scan and enters P4's integral as any other point.**

## Known-answer gates (instrument; all must pass before any physics statement)

- **KA1 (control).** No-wave control: |slope of d_x| ≤ 3×10⁻⁵, pair-separation drift over 400 t.u. ≤ 0.02. (Probe: 1.0×10⁻⁵.)
- **KA2 (direction oddness).** At every k, Δ(ḋ_x) for +y and −y have opposite signs and magnitudes within 25 % of each other; the estimate used is the mean of the two.
- **KA3 (quadratic scaling).** At m = 8 and m = 16, doubling A_v multiplies Δ(ḋ_x) by 4 ± 1 (the force is linear in j ∝ A_v²).
- **KA4 (Born limit).** σ_∥(k) at m = 1, 2, 3 (k = 0.098, 0.196, 0.295; Born 0.48, 0.97, 1.45) within **30 %** of κ²k/8c². (Honest limit: the Born condition κk/c ≪ 1 is only marginal at these k; a
  deviation larger than 30 % is reported as a measurement of the first correction, not as an instrument failure, **but the gate then counts as not passed** and P4 is read with that caveat.)

## Predictions (physics)

- **P1 (σ_∥ turns over).** σ_∥(k)/k decreases monotonically for k ≥ 1, and σ_∥(2.75)/2.75 ≤ 0.6 · σ_∥(0.49)/0.49. (The Born law makes σ_∥/k constant.)
- **P2 (σ_⊥ small).** σ_⊥(k) < 0.5 · κ/c = 3.14 at every k ≥ 0.2 — i.e. the transverse (Iordanskii) cross-section of the GP vortex is a fraction of the point-vortex value (the probe suggests 0.25; this
  prediction is made on the full k grid).
- **P3 (opposite-sign structure).** None registered: the k-dependence of σ_⊥ is reported.
- **P4 (decisive: the friction law from T = 0 data).** With the independent-mode form, Rayleigh–Jeans occupations n_k = T/ε_k, ε_k = (k² + k⁴/4)^{1/2}, c_g = dε/dk, ρ_s ≈ ρ (0.96–0.98 at the arms used):

  **α/T = (1/(ρ_s κ)) · (1/4π) ∫₀^{k_c} k³ c_g(k) σ_∥(k) / ε_k² dk**   (D = ½∫d²k/(2π)² (T/ε²) k² c_g σ_∥, α = D/(ρ_s κ); Lean `FrictionKinetic` for the identity).

  Evaluated at the coarse cutoff **k_c = 2π/3 = 2.09** (entirely inside the measured k range) with σ_∥ interpolated linearly in k between measured points, and compared with the measured **α/T = 0.0540 ± 0.0026 (six arms; coarse arm alone 0.049–0.056)**:
  - within **30 %** → **the friction law is explained by T = 0 scattering**: no thermal input beyond Rayleigh–Jeans occupations; this is the headline;
  - 30–60 % → partial: the independent-mode kinetic picture is qualitatively right and quantitatively incomplete (quote the ratio);
  - outside 60 % → the kinetic picture is **refuted** for this field (collective, non-independent dissipation); the scattering paper is then about σ(k), and the friction law is not explained.
  Secondary, report only: the same integral at k_c = π (the measured range ends at k = 2.75; the last 0.39 filled by the last measured σ_∥·(2.75/k)) and at 2π (filled the same way and, as a bound, by zero):
  the **cutoff independence** of the measured α/T predicts that the integral saturates by k ≈ 2; if the integrand keeps growing the measured independence is unexplained.
  The Born-law prediction at k_c = 2.09 is computed and recorded **before the scan** below (value filled by the script `predict_friction_from_sigma.py --born`; an order-of-magnitude contrast).
- **P5 (α′ cross-check, report only).** The analogous integral with σ_⊥ gives the predicted α′(k_c) = D′/(ρ_s κ) · (sign convention of Sonin Eq. 69); compared with the measured box-frame α′ (−0.005 to −0.03).

### Born-law prediction, recorded before the scan (`predict_friction_from_sigma.py --born`)

| k_c | α/T from σ_∥ = κ²k/8c² (Born, all k) | measured α/T |
|---|---|---|
| 2.09 | **0.214** | 0.049–0.056 |
| 3.14 | 0.678 | 0.054 (π, published) |
| 6.28 | 3.951 | 0.053–0.055 |

The Born law, extrapolated, overshoots by factors 4, 13, 73 and makes α/T grow as k_c²: if σ_∥ followed Born at k ≳ 1, P4 fails by a large factor. For orientation the exact Aharonov–Bohm
transport cross-section of a flux γ = k, σ = (2/k) sin²(πk), gives 0.028, 0.041, 0.072 (not a prediction of this field: the AB model has no core and no vortex motion).
**Consequence registered with P4:** a pass requires σ_∥ to fall below the Born law by about a factor 4 in the range k ≈ 1–2 that dominates the integral at k_c = 2.09.

## Scan (frozen)

m ∈ {1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28} (k = 0.098 … 2.75), directions ±y, A_v = 0.04, 400 t.u., N = 128, L = 64; control (ε = 0) once; KA3 repeats at m = 8, 16 with A_v = 0.08.
Total 1 + 26 + 4 = 31 runs at ≈ 9 min each. One seed (T = 0 is deterministic); the uncertainty on each σ is the half-difference of the two directions, floored at 5 % (KA2's tolerance).
**Stop rules:** a run in which a vortex is lost is dropped and repeated once with A_v halved (reported); if more than 3 of 26 runs are lost the scan is stopped and the instrument revised under an amendment.

## What would be concluded

Gates fail → the observable is not a clean measure of the force (e.g. wave–pair coupling beyond the Magnus balance); report and stop. Gates pass and P4 within 30 % → σ(k) of a GP vortex measured for the first time beyond Born, and the friction law predicted from it.
P1 fails → the temperature law's cutoff independence needs another explanation than a falling σ(k).

Limits stated now: T = 0 (no thermal dressing of the vortex), one box and one interaction strength (mg = 1), linear regime only, Rayleigh–Jeans occupations assumed, projected-field cutoff π (σ above k = 2.75 inferred, not measured).

## Results of the first scan (2026-10-09 10:20; `analyze_wave_scan.py` → `scan/wave_scan_results.json`) — as registered, no spin

All 31 runs completed (no vortex lost). **Gates: KA3 passes (amplitude doubling multiplies the force by 3.9 at m = 8 and 4.7 at m = 16). KA1 fails on its second clause**
(slope of d_x in the control 1.0×10⁻⁵ passes; the control separation changes by 0.132 over 400 t.u., clause ≤ 0.02 — the saddle at d₀ = L/2 drifts slowly; the control slope is subtracted in every estimate, but the registered clause is failed).
**KA2 fails at m = 28 only** (σ_∥ = 0.049 ± 0.008, at the noise floor; oddness holds at the other 12 wavenumbers). **KA4 fails**: σ_∥ at k = 0.098, 0.196, 0.295 is 1.56, 3.60, 2.83 against Born 0.48, 0.97, 1.45
(ratios 3.2, 3.7, 1.9). By the registered rule: *gates fail → the observable is not a clean measure of the isolated-vortex force; report and stop; revise the instrument under an amendment.*

σ_∥(k) (xi; Born in parentheses): 1.56 (0.48), 3.60 (0.97), 2.83 (1.45), 2.23 (1.94), 2.73 (2.91), 1.88 (3.88), 0.75 (4.85), 1.17 (5.81), 2.52 (6.78), 0.70 (7.75), 0.23 (9.69), 0.33 (11.6), 0.05 (13.6) at k = 0.098 … 2.75.
σ_⊥ = 2.1, 2.0, 1.1, 1.7, 2.0, 1.3, 0.8, 1.0, 1.6, 1.0, 0.3, 0.2, 0.2 (point-vortex Iordanskii κ/c = 6.28; **P2 passes**: max 2.04 < 3.14).
**P1 fails as written** (σ_∥/k is not monotone for k ≥ 1: 0.75, 1.17, 2.52, 0.70 at k = 0.98 … 1.57), although σ_∥ above k = 1.96 is 0.05–0.33, thirty to two hundred times below Born.
**P4 as registered: predicted α/T(k_c = 2.09) = 0.035 against the measured 0.054 (ratio 0.65, "partial 30–60 %") — but read with the gates failed, it is not a valid test.** Born would give 0.214.

**Diagnosis (hypothesis, to be tested, not asserted).** The pair sits in a periodic box: each vortex has its antivortex 32 away and four periodic images, and a continuous wave of wavenumber k is re-scattered between them. The relative amplitude of a scattered
wave at a neighbour is ~(σ/2πkr)^{1/2}, and its phase kr changes by 2π when k changes by 2π/32 = 0.196 — exactly twice the step of the scan at low k, so the scan **aliases** a lattice ripple. The non-monotone values (k = 0.98 … 1.57) and the large low-k values
(where kr ≈ 3 and the scattered wave is not small at the neighbour) are what that would produce. The high-k fall (k ≳ 1.96, where the scattered wave is weaker at the neighbours) may be the isolated-vortex behaviour.

## Amendment WS-A1 (2026-10-09 10:30) — filed before the follow-up runs

**Registered question L1 (is the ripple the lattice?).** Repeat the scan at m ∈ {4, 8, 10, 12, 14, 16, 20} with pair separations d₀ = 20, 24, 28 (control for each d₀; the d₀ = 32 data are the first scan), both directions, A_v = 0.04, 400 t.u. (45 runs).
- **L1 prediction:** at k = 0.98–1.57 (m = 10, 12, 14, 16) σ_∥ varies between the four d₀ by more than **30 %** (max/min − 1), i.e. the ripple is the lattice; at m ≥ 20 the variation is below 30 %.
- If L1 holds: **the isolated-vortex σ_∥(k) is estimated as the d₀-average at each k** (with the spread as its uncertainty); the amended **P4′** is P4 evaluated with the d₀-averaged σ_∥, and the verdict bands are unchanged (30 % / 60 %). The amendment is **retrospective in its motivation** (the lattice was suggested by the first scan) and is flagged as such; the first-scan values are kept in every table.
- If L1 fails (variation < 30 % at m = 10–16): the ripple is a property of the single-vortex response (e.g. core-bound resonances, Wood-type resonance of the core with the wave — cf. core-bound waves on a GP vortex, arXiv:2603.05505), not of the lattice, and the first-scan σ_∥(k) stands; the amendment then reads: gates KA1 (clause) and KA4 are failed for a reason other than the lattice, and the Born limit at k ≤ 0.3 fails *in the measurement*, which would be reported as such.
- **KA1 amended** (retrospective relaxation, flagged): the clause on the control's separation drift is dropped in favour of the slope clause that is used in the estimator (|slope of d_x| ≤ 3×10⁻⁵ in the control of every d₀).
- Known limits unchanged; additionally: d₀ ≠ 32 pairs translate along y at ~1/d₀ − 1/(L − d₀) (0.006–0.017), subtracted by the per-d₀ control.

## Results of the WS-A1 follow-up (2026-10-09 14:17; `analyze_wave_scan_d0.py` → `scan_d0/wave_scan_d0_results.json`) — as registered, no spin

All 45 runs completed. σ_∥ (ξ) by pair separation d₀ = 20, 24, 28, 32 (d₀ = 32 from the first scan):

| m | k | d₀=20 | 24 | 28 | 32 | mean | spread (max/min − 1) |
|---|---|---|---|---|---|---|---|
| 4 | 0.39 | 1.60 | 1.66 | 1.84 | 2.23 | 1.83 | 39 % |
| 8 | 0.79 | 0.69 | 2.40 | 2.44 | 1.88 | 1.85 | 252 % |
| 10 | 0.98 | 1.10 | 1.69 | 1.57 | 0.75 | 1.28 | 125 % |
| 12 | 1.18 | 1.44 | 1.36 | 1.70 | 1.17 | 1.42 | 45 % |
| 14 | 1.37 | 1.10 | 0.93 | 0.94 | 2.52 | 1.37 | 170 % |
| 16 | 1.57 | 0.71 | 0.63 | 0.35 | 0.70 | 0.60 | 103 % |
| 20 | 1.96 | 0.26 | 0.33 | 0.37 | 0.23 | 0.30 | 63 % |

Controls: |slope of d_x| = 6×10⁻⁶ – 2.5×10⁻⁵ (all below the 3×10⁻⁵ amended clause).

- **L1 as registered: FAILS** — its first clause holds (spread > 30 % at m = 10, 12, 14, 16: 125, 45, 170, 103 %) but its second does not (spread at m = 20 is 63 %, not < 30 %). The registered branches did not anticipate this mixed outcome (the "L1 holds → average" branch needs both clauses; the "L1 fails → ripple belongs to the vortex" branch was defined by spread < 30 % at m = 10–16, which did not occur).
  Reading: σ_∥(k) at a given k depends on the pair separation by factors of 1.4–3.5 for k ≤ 1.6, and still by 63 % at k = 1.96 where σ is small (0.23–0.37): **the periodic arrangement contaminates the single-vortex cross-section at every k measured**, and the d₀-mean is an estimate with an uncertainty of a factor ≈ 1.5–2 per point, not a single-vortex measurement.
- **P4′ (friction from the d₀-averaged σ_∥), as registered: PARTIAL (30–60 %).** Predicted α/T at k_c = 2.09: **0.0323** against the measured 0.054 (energy) / 0.060 (regression) (ratio 0.60 / 0.54). Envelope from the per-point minimum and maximum over d₀ (±20 % on the points not repeated): 0.022–0.043 at k_c = 2.09; 0.027–0.050 at π; 0.030–0.055 at 2π.
  Prediction at the other cutoffs (1/k tail beyond k = 2.75 assumed): 0.032 → 0.038 → 0.042 (k_c = 2.09, π, 2π), against the Born law's 0.21 → 0.68 → 3.95.
  **Two readings, kept apart:** (i) the **saturation** — the friction nearly independent of the cutoff (predicted +30 % from k_c = 2.1 to 6.3, measured +8 % / +10 %; Born ×18) — **is reproduced** by the T = 0 scattering data under the independent-mode kinetic picture, because σ_∥ falls above k ≈ 1.5 (0.3 ξ at k = 2); (ii) the **magnitude** is reproduced to 55–60 %, with an uncertainty band of ±40 % from the lattice spread that includes the lower measured value only at 2π: the independent-mode picture is qualitatively right and quantitatively incomplete (or the lattice-contaminated σ is low).
- P2 (σ_⊥ small) was read on the first scan (passes); not repeated here. P1 as registered failed on the first scan and is not redeemed by this follow-up (the d₀ spread is of the size of the ripple).

**What the follow-up does not establish:** an isolated-vortex σ(k). That needs a lattice-free measurement (a larger box with the pair far apart, and the same k grid) — Rust replication of this matrix (`wave_scan --d0 20,24,28`, ran 2026-10-09 14:20, an independent implementation agreeing with Python to 5×10⁻¹¹ on the d₀ = 32 matrix) and an L = 128 repetition are the next steps.

## Amendment WS-A2 (2026-10-09 ≈ 14:19; committed before the L = 128 runs were launched) — filed before any run of it; implementation: the Rust `wave_scan` (rusty-SUNDIALS, branch feat/qf-pgpe-reference; agrees with the Python instrument to 5×10⁻¹¹ on the d₀ = 32 matrix)

**Question.** Is the d₀-dependence of σ_∥ (39–252 % at k ≤ 1.6) the periodic arrangement? A box twice as large, with the pair twice as far apart, should shrink it: the amplitude of a scattered wave at a neighbour at distance r falls as (σ/2πkr)^{1/2}.
**Design.** L = 128, N = 256 (dx = ξ/2, k_cut = π, the same wave numbers as the L = 64 scan: m = 2 m₆₄), pair separations d₀ = 64 and 48, m ∈ {8, 16, 24, 32, 40, 48} (k = 0.393, 0.785, 1.178, 1.571, 1.963, 2.356), both directions, A_v = 0.04, 400 t.u., one control per d₀: 2 × (12 + 1) = 26 runs.
**Registered before the data:**
- **L2a (the ripple shrinks with the spacing).** At m = 16, 24, 32 (k = 0.79, 1.18, 1.57) the spread max/min − 1 of σ_∥ over the two d₀ is **< 50 %** (L = 64: 252, 45, 103 %); the mean over the two d₀ of the three points is the L = 128 estimate.
- **L2b (agreement with the L = 64 d₀-mean).** At every k in common (0.39, 0.79, 1.18, 1.57, 1.96) the L = 128 two-d₀ mean is within **40 %** of the L = 64 four-d₀ mean (1.83, 1.85, 1.42, 0.60, 0.30).
- **L2c (the fall).** σ_∥(k = 1.96) and σ_∥(2.36) are below 0.5 ξ (Born: 9.7, 11.6 ξ).
- **P4″.** The friction predicted from the L = 128 σ_∥ (the k = 0.39–2.36 points; the 1/k tail beyond; k < 0.39 filled from the L = 64 first scan) lies within **30 %** of the measured α/T = 0.054–0.060 at k_c = 2.09 (so 0.038–0.078).
**Conclusions registered:** L2a ∧ L2b → the L = 64 d₀-mean is a usable estimate and the lattice is the source of the ripple; L2a fails → the d₀-dependence is not the lattice (a response of the core or a resonance) and σ_∥(k) of an isolated vortex is not defined by this observable; L2a ∧ ¬L2b → the L = 64 means are biased by the lattice and only L = 128 numbers are quoted.
**Known now (not new information):** the L = 64 values and the Born baseline (0.214 / 0.678 / 3.95); the Rust replication of the L = 64 d₀ matrix is running (45 runs) and will be compared point by point with the Python one.
