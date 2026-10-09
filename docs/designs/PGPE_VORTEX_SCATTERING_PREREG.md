# Pre-registration: the vortex–phonon transport cross-section σ(k) from T = 0 scattering, and the friction law it predicts

Filed 2026-10-09 09:40, **before the scan below is run**. Follows `PGPE_FRICTION_LAW_RESULTS.md` (CLAIM-096/097: α = 0.054 T at three cutoffs, c = α/(ρ_n/ρ) not a vortex property)
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
