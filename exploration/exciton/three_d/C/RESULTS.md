# Experiment C results (S^3), run 2026-10-11/12

Registered in `../PREREG.md`. Code: `run_C.py`, `analyse.py`. Records: `records.jsonl` (one L-BFGS start per line), `reference.json`.

## Geometry checks

- 600-cell: 120 vertices, unit norm to 4.4e-16, min chord 0.618033988749894 (expected 2 sin(pi/10) = 0.618033988749895).
- 24-cell: 24 vertices, min chord 1.000000000000000 (expected 1).

## Gate C1 (N = 120, 50 starts per kernel; reach 600-cell energy within 1e-8 relative)

| kernel | E_600 | success | lowest found | max rel dev of lowest from E_600 |
|---|---|---|---|---|
| gauss0.5 | 2933.909981 | 50/50 | 2933.909982 | 2.3e-10 |
| gauss1 | 1489.938885 | 0/50 (confirmed by the raised-cap rerun: converged to distinct local minima, see below) | 1489.938915 | 2.0e-08 |
| gauss2 | 583.5045188 | 0/50 | 583.5085428 | 6.9e-06 |
| gauss4 | 181.7114008 | 6/50 | 181.7114008 | 3.1e-16 |
| coulomb | 5796.576456 | 46/50 | 5796.576456 | 0.0e+00 |
| log | -1903.986315 | 48/50 | -1903.986315 | 0.0e+00 |

**Gate C1: FAIL** (threshold >= 45/50 for every kernel).

Starts finding energy below the 600-cell by > 1e-8 relative: 0.
Max |gradient| component over all 6000 records: 6.0e-05.

## N = 24 vs 24-cell (reported, not gated)

| kernel | E_24cell | starts at 24-cell energy (1e-8) | lowest found | lowest below 24-cell? |
|---|---|---|---|---|
| gauss0.5 | 107.7587819 | 50/50 | 107.7587819 | no |
| gauss1 | 50.05991298 | 25/50 | 50.05991298 | no |
| gauss2 | 14.55289895 | 7/50 | 14.55289895 | no |
| gauss4 | 1.783045837 | 0/50 | 1.787122026 | no |
| coulomb | 208.3373141 | 5/50 | 208.3373141 | no |
| log | -86.00445452 | 6/50 | -86.00445452 | no |

## Frustration scan, N = 12..48 even

For each (N, kernel): number of distinct minima energies (clustered within 1e-8 relative) and the fraction of the 50 starts reaching the lowest. `unique` = one distinct minimum. Cells show `n_distinct / frac_lowest`.

| N | gauss0.5 | gauss1 | gauss2 | gauss4 | coulomb | log |
|---|---|---|---|---|---|---|
| 12 | 1 / 1.00 | 1 / 1.00 | 2 / 0.80 | 2 / 0.92 | 2 / 0.96 | 2 / 0.96 |
| 14 | 1 / 1.00 | 1 / 1.00 | 1 / 1.00 | 1 / 1.00 | 1 / 1.00 | 1 / 1.00 |
| 16 | 2 / 0.56 | 1 / 1.00 | 1 / 1.00 | 1 / 1.00 | 1 / 1.00 | 1 / 1.00 |
| 18 | 2 / 0.48 | 3 / 0.56 | 1 / 1.00 | 1 / 1.00 | 1 / 1.00 | 1 / 1.00 |
| 20 | 4 / 0.52 | 1 / 1.00 | 1 / 1.00 | 1 / 1.00 | 1 / 1.00 | 1 / 1.00 |
| 22 | 2 / 0.98 | 2 / 0.40 | 2 / 0.82 | 2 / 0.76 | 3 / 0.22 | 3 / 0.38 |
| 24 | 1 / 1.00 | 2 / 0.50 | 2 / 0.14 | 2 / 0.98 | 2 / 0.10 | 2 / 0.12 |
| 26 | 4 / 0.70 | 3 / 0.60 | 2 / 0.92 | 3 / 0.38 | 3 / 0.34 | 3 / 0.24 |
| 28 | 1 / 1.00 | 1 / 1.00 | 2 / 0.86 | 2 / 0.92 | 2 / 0.90 | 2 / 0.56 |
| 30 | 7 / 0.14 | 5 / 0.26 | 6 / 0.14 | 4 / 0.22 | 1 / 1.00 | 2 / 0.94 |
| 32 | 9 / 0.16 | 5 / 0.62 | 5 / 0.48 | 7 / 0.08 | 6 / 0.06 | 7 / 0.06 |
| 34 | 2 / 0.98 | 2 / 0.96 | 1 / 1.00 | 2 / 0.98 | 1 / 1.00 | 1 / 1.00 |
| 36 | 7 / 0.76 | 3 / 0.84 | 3 / 0.88 | 6 / 0.28 | 6 / 0.34 | 6 / 0.38 |
| 38 | 3 / 0.64 | 4 / 0.48 | 4 / 0.16 | 7 / 0.34 | 5 / 0.38 | 5 / 0.30 |
| 40 | 12 / 0.20 | 11 / 0.74 | 5 / 0.54 | 5 / 0.46 | 7 / 0.20 | 7 / 0.32 |
| 42 | 7 / 0.26 | 9 / 0.14 | 4 / 0.82 | 2 / 0.98 | 3 / 0.88 | 3 / 0.90 |
| 44 | 4 / 0.94 | 4 / 0.88 | 3 / 0.94 | 2 / 0.98 | 2 / 0.98 | 1 / 1.00 |
| 46 | 6 / 0.36 | 4 / 0.40 | 3 / 0.58 | 7 / 0.02 | 5 / 0.02 | 5 / 0.40 |
| 48 | 5 / 0.58 | 3 / 0.56 | 2 / 0.56 | 9 / 0.08 | 11 / 0.16 | 5 / 0.36 |

Smallest N (in 12..48 even) with more than one distinct minimum found by 50 random starts:

- gauss0.5: 16 (all such N: [16, 18, 20, 22, 26, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48])
- gauss1: 18 (all such N: [18, 22, 24, 26, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48])
- gauss2: 12 (all such N: [12, 22, 24, 26, 28, 30, 32, 36, 38, 40, 42, 44, 46, 48])
- gauss4: 12 (all such N: [12, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48])
- coulomb: 12 (all such N: [12, 22, 24, 26, 28, 32, 36, 38, 40, 42, 44, 46, 48])
- log: 12 (all such N: [12, 22, 24, 26, 28, 30, 32, 36, 38, 40, 42, 46, 48])

## Interpretation (measured, no theorem claimed)

- Gate C1 **FAILS as registered**: only gauss0.5 (50/50), coulomb (46/50) and log (48/50) reach the 600-cell energy in >= 90 % of starts. gauss4 reaches it in 6/50; gauss1 and gauss2 in 0/50.
- No start ever went below the 600-cell energy (consistent with the proved universal optimality). The failures are search failures (local minima / near-flat valleys), not a contradiction of the theorem.
- gauss4 (N=120): 44/50 starts end ~1.0e-3 above E_600 in a different local minimum; 6 reach the 600-cell exactly.
- gauss2 (N=120): all 50 starts end 6.9e-6..8.4e-6 above E_600, |grad|max ~3e-7, CONVERGENCE flags. A scratch re-start check (not in records) from one such end point stayed 7.27e-6 above after 6 further L-BFGS restarts. This is a family of near-degenerate local minima or valleys too flat for L-BFGS; the two cases are not distinguished here.
- gauss1 (N=120): all 50 runs hit the 8000-iteration cap with |grad|max ~1e-5, ending 2.0e-8..3.1e-8 above E_600: slowly creeping, not converged. Smooth kernels have tiny high-harmonic weights, so at the 1e-8 threshold C1 is partly a conditioning test. gauss0.5 passes with a distance of ~2e-10 after 8000 iterations (also not fully converged, |grad| ~ 3e-6).
- 24-cell (N=24): reached by 50/50 (gauss0.5), 25/50 (gauss1), 7/50 (gauss2), 0/50 (gauss4), 5/50 (coulomb), 6/50 (log). For gauss4 the 24-cell energy (1.783046) is lower than the lowest energy found (1.787122) and was never reached; whether it is a local minimum for a=4 was not tested.
- Frustration: more than one distinct minimum already at N=12 for gauss2, gauss4, coulomb, log (80-96 % of starts reach the lowest), at N=16 for gauss0.5, N=18 for gauss1. For coulomb/log N=14..20 are unique; from N=22 on non-uniqueness is common but non-monotone in N (N=30, 34, 44 near-unique for some kernels). Counts of distinct minima are lower bounds (50 starts, 1e-8 clustering; incomplete convergence on smooth Gaussians can split or merge minima).

## Deviations and implementation notes (2026-10-11/12)

1. N range: every even N in 12..48 plus N=120 and N=24 inside the scan; 50 starts per kernel for each. Seeds: `1000*N + start + 100000*kernel_index`, numpy default_rng.
2. C1 operationalised as >= 45/50 starts with |E - E_600|/|E_600| <= 1e-8 for every kernel.
3. Unconstrained R^4 vectors normalised to S^3, scipy L-BFGS-B, analytic gradient (finite-difference checked). Final settings: maxiter 8000, maxcor 30, ftol 1e-17, gtol 1e-10. Earlier setting trials (maxiter 3000/ftol 1e-15; a trust-ncg Newton polish) were run on single test jobs only and discarded; records contain only final settings. The first launch oversubscribed BLAS threads, was killed and restarted with OMP_NUM_THREADS=1 and 2 worker processes.
4. Per-run `nit`, `msg`, `gmax` recorded. 62 gauss0.5 and 50 gauss1 runs hit the iteration cap (all gauss1 at N=120); 114 runs ended ABNORMAL (RESULTS originally said 115; recounted in review) (line-search), mostly gauss4; max |grad| component over 6000 records 6.0e-5. All are retained in the counts.
5. Energies are total pair sums over i<j (not per particle); d = Euclidean chord in R^4; Gaussian e^{-a d^2}, Coulomb 1/d, log = -log d.
6. 600-cell: 8 + 16 + 96 vertices, 96 from even permutations of (phi/2, 1/2, 1/(2phi), 0) with all sign choices; count 120 and min chord 2 sin(pi/10) verified.


## Review corrections (2026-10-12)
* gauss1 at N = 120 is INCONCLUSIVE, not a search failure: all 50 runs were cap-limited (8000 iterations), 2.0e-8..3.1e-8 above E_600 against a 1e-8 threshold. The overall C1 FAIL stands on gauss2 (0/50, converged, 7e-6 above) and gauss4 (6/50). Supplementary run: `polish_gauss1.py` (cap 150000), results below once complete.
* Seed formula 1000*N + start + 100000*kernel_index makes (N=120, kernel 0) and (N=20, kernel 1) share seeds: correlated, not independent, streams across kernels (harmless for the claims).
* gauss4 N=24: whether the 24-cell is a local minimum at a=4 was not tested.

## Supplementary run, resolved (2026-10-12)
* `polish_gauss1.py` (cap 150000, same 50 seeds): all 50 converge (ftol; 16640-66673 iterations, |grad|max <= 1.4e-6) to
  E in [1489.938908, 1489.938917], i.e. 1.5e-8..2.1e-8 relative above E_600 = 1489.938885. Still 0/50 within 1e-8.
* `polish_gauss1_coords.py` (starts 0 and 1, coordinates kept): minimum chord 0.497 and 0.504 against 0.618 for the 600-cell;
  maximum deviation of the sorted distance spectrum from the 600-cell's 0.22. **These are distinct local minima, not the
  600-cell with residual error.** gauss1 is therefore a genuine search failure, but with an energy landscape so flat that the
  best local minima lie within 2e-8 of the proved optimum: for a = 1 the kernel barely distinguishes configurations at N = 120.
* Verdict table updated accordingly; the earlier 'INCONCLUSIVE' label is withdrawn.
