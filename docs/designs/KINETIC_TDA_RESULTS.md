# Results against the pre-registration `KINETIC_TDA_PREREG.md`

Order of events is verifiable from `git log`: pre-registration `b274fdb` (07:27), amendment A1 before any
code, amendments A2/A3 `dee61eb` (07:49, A3 before any D3 data), then the code and these results.
Every criterion is reported, including those that failed. Post-hoc diagnostics are labelled as such and
never convert a failure into a pass.

## Scorecard

**25 criteria and predictions: 14 met, 11 not.** Of the 11: three were defects in my own criteria or
measurement design (K1 rounding, D3 seed, K3 field-on control threshold); one is unexplained (mass drift);
two were free-streaming formulas misapplied to the interacting plasma (Run C, K3b); five were wrong
predictions about what persistence would detect (D1 ×3, D3 ×2).

| Item | Criterion (as pre-registered) | Outcome | |
|---|---|---|---|
| K1 | certified ball, radius ≤ 1e-30 | radius < 3e-40, exactly one zero | **pass** |
| K1 | midpoint "rounds to" 1.4156, −0.1533 | rounds to 1.4157, −0.1534 (literature values are truncations) | **FAIL — my wording (A2)** |
| K1 neg. control | wrong-γ ball must not certify | not certified | **pass** |
| K2 Run A | γ within 2 %, ω within 1 % | 0.14 %, 0.03 % | **pass** |
| K2 Run B | same at k = 0.4, and miss k = 0.5 by > 20 % | 0.36 %, 0.02 %; misses by 57 % | **pass** |
| K2 Run C | largest \|E₁\| max in (25,45) within 5 % of T_R = 33.51 | 36.50 (8.9 %) | **FAIL** |
| K2 | mass drift < 1e-10 | 6.7e-10 | **FAIL** (by 7×; energy drift 3.5e-7, no threshold set) |
| K3a | ballistic echo vs closed form ≤ 1e-3 of peak | 2.0e-9; peak at 15.00 | **pass** |
| K3b | field-on echo time within 5 % of 15.0 | 16.40 (9.3 %); amplitude 2.08× ballistic | **FAIL** |
| K3 neg. control | no 2nd pulse: < 1 % of peak | field off 2e-12 **pass**; field on 1.5 % | **FAIL (field on)** |
| K4 | `phase_mixing`, `transport_solution`, `maxwellian_mode` | proved; neg. controls rejected | **pass** (subsumed by Bedrossian, A1) |
| H5 | `zero_sound_iff` | proved; `0 ≤ F` variant rejected | **pass** |
| H5-2D | `zero_sound_2d_iff`, root (1+F)/√(1+2F) | proved as derived by hand; variant rejected | **pass** |
| D0 | P-D0a: T(ρ) vs V(−ρ) agree to 1e-12 | exactly 0 on both fields (81 and 985 pairs) | **pass** |
| D0 | P-D0b: T vs T must differ | 81 vs 116; 985 vs 1772 | **pass** |
| D1 | pooled precision ≥ 0.95 | 0.871 | **FAIL** |
| D1 | pooled recall ≥ 0.90 | 0.433 | **FAIL** |
| D1 prediction | recall ≥ 0.97 for vortices with nearest neighbour > 2 ξ | 0.512 (n = 555) | **FAIL — my prediction was wrong** |
| D1 prediction | recall ≤ 0.6 for nearest neighbour < 1 ξ | 0.287 (n = 94) | holds |
| D1 neg. control | sound-only frame (0 winding vortices, density 0.18–1.60 n₀): 0 detections | 0 of 506 minima | **pass** |
| D3 | two-stream growth rate within 5 % of certified 0.225844 | 0.18656 (17.4 %) | **FAIL — my measurement design** |
| D3 prediction | S1: exactly 1 hole at t = 60 | 29 (1 at saturation, t = 38) | **FAIL** |
| D3 prediction | S2: exactly 2 holes at first saturation peak | 4, depths 0.84, 0.17, 0.17, 0.17 | **FAIL** |
| D3 neg. control | Maxwellian at t = 50: 0 holes | 0 | **pass** |

I missed the mass-drift failure when first reading the Run A output and caught it while compiling this
table: 6.7e-10 against a threshold of 1e-10. The cause is almost certainly the zero-fill outside
[−v_max, v_max] in the spline step (f(±6) ≈ 6e-9); I have not verified that, so it is a guess, and the
failure stands.

## The pattern in the kinetic failures

Every exact known answer passed at or near rounding error: certified root, ballistic echo (2e-9),
free-streaming recurrence (t = 33.50, amplitude ratio 1.000 — post-hoc diagnostic
`k2c_posthoc_recurrence.py`). Both predictions that failed (Run C, K3b) were free-streaming formulas I
applied to the self-consistent plasma, and both were off by ≈ 9 %. The echo shift is converged
(`k3b_posthoc_convergence.py`: t = 16.400 at N_v = 512/Δt = 0.05 and at 1024/0.025; amplitude equal to
0.04 %), so it is physics: the dielectric response delays and amplifies the echo. This is known
(the Gould–O'Neil–Malmberg echo amplitude carries dielectric factors); I did not apply it when writing
the prediction. Practical rule adopted in `tests/test_kinetic.py`: test recurrence and echo timing with
the field **off**, where they are exact.

## D3: what failed and why (post-hoc, `d3_posthoc_growth.py`)

**Growth rate.** Either the certificate or the measurement was wrong, so both were tested. Direct
quadrature of D(iγ) — legitimate without continuation since Im ω > 0 — gives D = 8e-15 at the certified
γ = 0.225844 and D = −0.54 at the measured 0.18656: the certificate is right. The pre-registered seed of
1e-3 starts the field only two decades below saturation; the local growth rate slides
0.33 → 0.27 → 0.24 → 0.21 and never plateaus, so there was no linear phase to fit. Rerun with seed 1e-8:
plateau 0.22621, 0.22592, 0.22591, 0.22585; fit over [30, 60] = 0.22594, **0.04 %** from the certificate.
The solver is right; my measurement design was not. The failure stands as registered.

**Hole counts.** Two separate things went wrong, and neither is fixable by tuning a threshold.
(i) After saturation the trapped region filaments, and the filaments are deep: by t = 60 there are 29
minima deeper than 0.1·max f in S1, arriving in equal-depth pairs from the (x,v) → (−x,−v) symmetry. A
persistence threshold does not separate "hole" from "filament". (ii) In S2 at saturation the two holes
are physically equivalent, yet one scores depth 0.84 and the other 0.17: the beams leave a trough at
v ≈ 0 (f₀(0) ≈ 0.11·max f), the two holes are joined through it, and by the elder rule only one of them
keeps a large bar. Prominence is not hole depth when the holes sit in a common valley. By D0 — which we
verified exactly — the H₁ superlevel diagram carries the *same* numbers, so no other homological degree
rescues the count. **D3 as an instrument is refuted for this configuration.**

## D1: what failed and why (post-hoc, `d1_posthoc_why.py`)

At t = 10, **289 of 289** vortices have a density minimum below 0.1 n₀ within 1 ξ: the cores are there.
Their H₀ depths are: < 0.1 for 62, 0.1–0.3 for 52, 0.3–0.5 for 46, > 0.5 for 129. The state is strongly
compressible (density std 0.45 n₀; 15.5 % of the area below 0.5 n₀), so cores are joined by low-density
channels and lose their prominence — the same valley effect as in D3. And 142 of the 462 near-zero minima
belong to no vortex: deep sound-wave dips, which cost precision. The sensitivity grid confirms no
threshold pair rescues it (best recall 0.58, at precision 0.72–0.87). My prediction that isolated
vortices would be found ≥ 97 % of the time was wrong: isolation in *position* does not imply isolation
in the *sublevel-set topology*. **D1 is refuted as a usable detector for strongly compressible
turbulence.** Whether it works in a quiet condensate — the experimentally relevant case — is untested,
and would need its own pre-registration; it is not claimed.

## What the TDA part established

One thing: the duality control D0 holds exactly on real data (985 pairs, difference 0), and it has
teeth — it explains why switching homological degree could not have saved D1 or D3. Both
instruments failed for one reason: H₀ persistence measures depth relative to the *connecting saddle*,
and in both systems the objects of interest share a valley. These are the fourth and fifth TDA proposals in this
project to fail, and the first whose failure is understood mechanistically.

## Literature gates

- Kinetic: Bedrossian, arXiv:2609.16801 formalizes nonlinear Landau damping in Lean 4. K4 subsumed, K5
  dropped, my proposal's "out of reach" corrected by erratum. No prior *certified* enclosure of the
  Landau root found (absence of hits). Canosa (1973) is the numerical reference.
- TDA: D0 is the Symmetry Theorem of Cohen-Steiner–Edelsbrunner–Harer (2009) with the cubical duality of
  Bleile et al. (2022, §4.2 for the periodic case). D1 is prominence; prior art: Spitz et al. (2021) on a
  2D Bose gas (alpha complexes of low-density point clouds, no precision/recall against winding), Leykam
  et al. (2022) for solitons, Metz et al. (2021) CNN vortex detection. D3: nearest prior art Cao et al.
  (2026), sublevel PH for blobs/holes in gyrokinetic fields; nothing found on 1D1V Vlasov–Poisson.
