# Experiment D: hybrid 3D mesh (CM relax + 20 Lloyd) vs CVT alone (2026-10-11)

Code: `run_d.py` (records), `analyse_d.py` (summary). Records: `records_p0.jsonl`, `records_p1.jsonl` (30 seeds x 5 arms),
`summary_d.json`, logs `run_p*.log`. `dimlift/mesh3d.py` is imported unchanged (same `relax_cm`, `lloyd`, `tet_quality`).
Protocol as E3: periodic unit cube, N = 216 (E3 amendment A2), X0 = `default_rng(31337+s).random((216,3))`, seeds s = 0..29,
Delaunay of the 3x3x3 tiling restricted to the central cell, 1.5e5 Monte-Carlo samples per Lloyd iteration.

Arms: `hybrid` = CM relaxation (L-BFGS-B, maxiter 3000, E3 settings) then 20 Lloyd iterations; `cm_only`; `cvt20`, `cvt40`, `cvt80`
= Lloyd from the Poisson start, one chain, snapshots at 20/40/80 iterations.

## Gate D1 verdict
Gate: hybrid rho_p5 median >= CVT rho_p5 median **and** hybrid wins >= 20/30 paired seeds.

* **Verdict, corrected after review: MET against cvt20/cvt40 (the hybrid does more work there); NOT MET at matched cost (cvt80 is the cost-matched arm: CM stage ~60 s, hybrid ~82 s, cvt80 ~88 s; wins 10/30, difference -0.0055 +- 0.0045). "Equal total iterations" was never defined in PREREG.md and cvt40 as primary was chosen by the run's author before running, not registered; the git history cannot verify the timing.**
* Primary comparator cvt40 (the E3 CVT protocol): D1 MET. Medians 0.7057 vs 0.6690; wins 25/30.
* Against cvt20 (equal Lloyd-iteration count, CM stage free): met, wins 30/30.
* Against cvt80 (CVT given 4x the hybrid's Lloyd iterations): **not met**. Median 0.7057 vs 0.7119, wins 10/30.

The verdict therefore depends on the budget definition (see deviation 1). The honest summary: the hybrid beats CVT at 40
iterations, but CVT at 80 iterations is as good or slightly better, so the hybrid is a convergence accelerator at best, and the
CM stage is the expensive part (3000 gradient evaluations of an O(N^2) kernel, ~60 s per seed vs ~1.1 s per Lloyd iteration here).

## Paired differences in rho_p5 (hybrid minus comparator), mean +/- s.e., n = 30
| comparator | mean diff | s.e. | median diff | wins | one-sided sign p | min diff | dihedral p5 diff (deg) |
|---|---|---|---|---|---|---|---|
| cvt40 (primary) | +0.0370 | 0.0063 | +0.0394 | 25/30 | 1.6e-4 | -0.0418 | +3.20 +/- 0.38 |
| cvt20 | +0.1131 | 0.0074 | +0.1030 | 30/30 | <1e-8 | +0.0514 | +8.10 +/- 0.47 |
| cvt80 | -0.0055 | 0.0045 | -0.0077 | 10/30 | 0.98 | -0.0454 | +0.24 +/- 0.32 |
| cm_only | +0.0733 | 0.0050 | +0.0722 | 30/30 | <1e-8 | +0.0095 | +4.74 +/- 0.29 |

Excluding dev-exposed seed 0 (29 seeds), primary: +0.0371 +/- 0.0065, wins 24/29; conclusions unchanged for every comparator.

## Distributional and worst-case metrics (over 30 seeds)
| arm | rho_p5 median | rho_p5 worst seed | worst single-tet rho | dihedral p5 median (deg) | worst min dihedral (deg) | sliver frac (rho<0.3) median / worst |
|---|---|---|---|---|---|---|
| hybrid | 0.7057 | 0.6582 | 0.0143 | 39.24 | 0.73 | 0.0046 / 0.0084 |
| cm_only | 0.6331 | 0.5760 | 0.0268 | 34.96 | 1.36 | 0.0053 / 0.0104 |
| cvt20 | 0.5947 | 0.5444 | 0.0162 | 31.98 | 0.80 | 0.0097 / 0.0134 |
| cvt40 | 0.6690 | 0.6219 | 0.0288 | 36.57 | 1.44 | 0.0057 / 0.0106 |
| cvt80 | 0.7119 | 0.6835 | 0.0136 | 39.35 | 0.72 | 0.0054 / 0.0084 |

Worst-case single-tetrahedron quality is not improved by the hybrid (0.014 vs 0.029 for cvt40; all arms have near-degenerate
slivers in some seed); this is a tail statistic of ~1300 tetrahedra per seed and is noisy. The hybrid improves the bulk (p5)
and the sliver fraction, not the absolute worst element.

## Deviations and disclosures (dated 2026-10-11)
1. **Budget definition.** The registration says "equal total iterations" without defining the CM stage in Lloyd units. A literal
   count (CM L-BFGS reached maxiter = 3000 on the seed checked, so 3020 total) is infeasible (~1 s per Lloyd iteration, ~55 min per seed)
   and CM and Lloyd iterations are not the same cost. I fixed before running: primary comparator = cvt40 (E3's CVT setting, i.e. twice
   the hybrid's Lloyd iterations); cvt20 and cvt80 as sensitivity arms. This choice was mine, not registered; the cvt80 result shows
   the verdict is sensitive to it. No wall-clock-matched arm was run.
2. **Seeds not disjoint from dev seeds.** The registration says the 30 test seeds are disjoint from dev seeds; in E3 the registered
   set is seeds 0..29 and dev seed 0 (N = 216) lies inside it (dimlift/PREREG.md A2). I used seeds 0..29 to share E3's starts, and
   report the 29-seed analysis excluding seed 0 (no change). No other dev runs were made in D.
3. **Samples:** 1.5e5 MC samples per Lloyd iteration (E3 code), not 2e5 as in the E3 text (already disclosed in dimlift).
4. **Independent RNG streams:** CM start uses the E3 X0; hybrid and CVT Lloyd use separate streams `default_rng([31337+s, 1|2])`,
   so Lloyd Monte-Carlo noise is independent between arms (E3 shared one stream). CVT snapshots are one chain (cvt20 is a prefix of
   cvt40 and cvt80), so those three arms are correlated.
5. Machine shared with other jobs; timings are indicative only. CM relaxations hit maxiter 3000 (not converged to gtol), as in E3.
6. Not claimed: anything about conforming CAD meshes, grading, boundary recovery, or other N / k L; single N = 216, single kernel.
