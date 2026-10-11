# L3 results: wall-spacing scan with RSA starts (G1) and engine-level sliding walls (G2)

Pre-registration: `L3_PREREG.md` (written before any registered run; amendment A1 is disclosure only). Data:
`results_L3/g1_*.json`, `results_L3/g2_*.json` (per start), `results_L3/l3_summary.json`; code `python/l3_{lib,run,analyse}.py`.
Engine: fresh clone of rusty-Fenris-CMRR 6d0df125 at `/mnt/data/xdev-cache/fenris-l3` (README sed + `engine_patch.diff`,
rusty-SUNDIALS-c3 5db8041), `fenris-gated` sources unchanged in `/mnt/data/xdev-cache/fg-l3`, target dir
`/mnt/data/xdev-cache/target_fenris_l3`. The clone was never pushed. Not run: the cargo test-suite of the clone (the
build itself succeeded; gates a/b/c/d of L6 were not repeated).
No claim about excitons.

## G1: wall spacing scan, RSA starts (6 shapes x 2 kernels x 24 starts per w; N_free ~ 100)

| w | escaped / starts | worst cell | accepted | confines (G1a) | R(w) [95% CI] | defect share within 1.5 of wall | concentration appears (G1b) |
|---|---|---|---|---|---|---|---|
| 0.5  | 0/288  | 0 %   | 284 | yes | 1.37 [1.33, 1.42] | 0.56 (cells 0.36-0.69) | no (R < 1.5) |
| 0.75 | 0/288  | 0 %   | 283 | yes | 1.80 [1.74, 1.86] | 0.73 (cells 0.59-0.86) | yes* |
| 1.0  | 0/288  | 0 %   | 286 | yes | 1.41 [1.36, 1.46] | 0.58 (cells 0.34-0.70) | no (R < 1.5) |
| 1.25 | 14/288 (4.9 %) | hexagon ungated 10/24 (42 %) | 267 | no (cell > 25 %) | 1.17 [1.11, 1.24] (survivor-biased) | 0.48 | not evaluated |

* G1a: **the registered wall at w = 1.0 confines with RSA starts (0 of 288 escaped)**, as does w = 0.5 and 0.75. The L6 headline
  "a bare fixed-node wall at the mean spacing does not confine" was therefore a property of the uniform random starts, not of
  the wall spacing. Leakage appears at w = 1.25 (hexagon ungated 10/24, annulus ungated 2/24, disc ungated 1/24, hexagon
  gated 1/24). The saddle mechanism itself was not tested.
* G1b: defects concentrate at the wall at every confining w (R > 1; defect share 0.56-0.73 against a node share 0.41), but
  the registered threshold R >= 1.5 is met only at w = 0.75. Caveat: w = 0.75 uses all wall nodes as triangulation sites
  (denser than the lattice), which also changes coordinations; the raw n_non6 at w = 0.75 (28.4) exceeds w = 0.5 (16.3)
  and w = 1.0 (19.7) by an amount that is largely this bookkeeping, and R(0.75) shares that confounding. The honest
  statement is: wall concentration is present for every w that confines (R 1.4-1.8), its size depends on the wall model.
* G1c (descriptive): paired n_non6 minus w = 0.5: +12.1 +- 0.3 (0.75), +3.4 +- 0.3 (1.0), +0.1 +- 0.5 (1.25). Not
  interpretable as physics because of the site rule above.
* About 1-2 % of non-escaped starts per w were not accepted (strict force or Hessian criterion), counted in the table.
  Statistics are over accepted states only (selection effect, as in L6).

## G2: engine-level sliding walls (w = 0.5; N_free 60; 30 RSA starts; corners fixed)

Delta = n_non6(fixed-wall minimum) - n_non6(after sliding); positive means fewer defects with sliding.

| shape | ungated: Delta +- s.e. (pairs; changed) | gated D=1.5: Delta +- s.e. (pairs; changed) |
|---|---|---|
| square  | -0.13 +- 0.09 (30; 2) | -0.13 +- 0.09 (30; 2) |
| hexagon | -0.03 +- 0.03 (30; 1) |  0.00 +- 0.00 (30; 0) |
| disc    |  0.00 +- 0.00 (30; 0) |  0.00 +- 0.00 (29; 0) |
| rect2   | -0.14 +- 0.17 (29; 3) | -0.07 +- 0.12 (30; 3) |
| lshape  | +0.23 +- 0.23 (30; 8) |  0.00 +- 0.15 (28; 4) |
| annulus |  0.00 +- 0.00 (20; 0) |  0.00 +- 0.00 (19; 0) |

* **G2 fails for both kernels**: 0 of 6 shapes reach Delta >= 2 (gate needs 3). Mean wall displacement is <= 0.05 (in units
  of node spacing 1), energy drops by <= 0.05 per state, Q unchanged except 3 ungated L-shape states, 0 Euler failures,
  0 non-conforming.
* The sliding wall does not produce any systematic defect-count change at the engine level: at w = 0.5 the equispaced
  wall is already almost a stationary wall configuration (the free nodes see no tangential force worth moving the wall).
  The sign of the few changes is mixed (more defects on square, fewer on L-shape), consistent with dimlift E2 (square
  -2.2 +- 1.5 there, i.e. more defects) only in sign for the square; magnitudes differ by an order of magnitude, as the
  protocols differ (E2: joint minimisation from the RSA start; L3: continuation from the fixed-wall minimum, same basin
  unless the continuation hops).
* Convergence caveat: L-BFGS in the wall coordinates hit the 40-iteration cap (gradient > 1e-5) in 8/30 (ungated square),
  25/29 (ungated rect2), 30/30 (ungated L-shape), 30/30 (gated rect2), 29/30 (gated L-shape), 2/20 (ungated annulus)
  starts; they are included (registered); converged-only subsets give the same picture (in `l3_summary.json`). The
  reduced landscape is nearly flat and the remaining gradients are small. The second-order condition in the wall
  coordinates was not checked.
* A different protocol (joint minimisation from the start, wall-node randomisation, a thermal/moving wall, a deliberately
  incommensurate wall) was not run and might behave differently; the claim here is limited to continuation from the
  fixed-wall minimum at w = 0.5.

## Not run / limits
Yukawa and D/d = 10 kernels, N_free ~ 200+, wall spacings below 0.5, static saddle check of confinement, the cargo test
suite and the L6 gates on the fresh clone, Hessian in the wall coordinates, any comparison of E_fixed across w.


## Review corrections (2026-10-12)
* `yes*` at w = 0.75: confounded by the all-wall-nodes site rule, which is not comparable across w (see amendment A1).
* L3_PREREG.md was untracked when the runs were made; its registration time cannot be verified from git or timestamps and rests on the author's attestation. It is committed together with these results.
* G2: the wall-coordinate L-BFGS hit its 40-iteration cap in 25-30 of 30 starts for rect2 and L-shape (counts 8, 25, 30, 30, 29, 2 across the six shapes), so 'G2 fails' is correct against the gate but weak evidence about sliding walls for those shapes.
