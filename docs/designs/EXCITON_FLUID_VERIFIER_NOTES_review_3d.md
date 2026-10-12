# Independent hostile review of 3D round 1 and L3 (2026-10-12)

Reviewer: a fresh agent instance with no access to the run agents' transcripts; brief: recompute headline numbers from raw
records, check verdict wording against the registered gates, look for overclaims and hidden issues. Report condensed by the
author from the reviewer's hand-back (the reviewer's own words are kept where quoted).

## Blocking (all fixed before commit e528c18 / this paper)
1. **C1 gauss1**: all 50 N=120 runs hit the 8000-iteration cap (gmax up to 6.0e-5), ending 2.0e-8..3.1e-8 above E600 against a
   1e-8 threshold. "Treating gauss1 as a search failure is unsupported. It is a non-converged optimiser." Fix applied: rerun with the
   cap at 150000 (`C/polish_gauss1.py`) and a coordinate check (`C/polish_gauss1_coords.py`): the runs converge to distinct local
   minima (min chord 0.50 vs 0.618), so the failure stands, now on converged runs; wording changed from "inconclusive" to
   "search failure in a flat landscape". Overall C1 FAIL unchanged (gauss2 0/50 converged, gauss4 6/50).
2. **D1 "MET" headline**: "Equal total iterations" never defined in PREREG; cvt40 as primary was the run author's post-hoc choice;
   "cvt80 costs about 88 s, so it is the cost-matched arm, and there D1 is NOT MET (wins 10/30, diff -0.0055 +- 0.0045)". Fix:
   verdict reworded "MET against cvt20/cvt40 (hybrid does more work); NOT MET at matched cost".
3. **L3_PREREG.md untracked in git** at run time; "registered before any L3 relaxation cannot be verified from git or timestamps".
   Fix: committed with the results, claim phrased as the author's attestation.

## Minor (disclosed in the RESULTS files and the paper)
* B1: "FAIL under the strictest reading"; median hit fraction 0.76 (N=2), 0.66 (N=4) would pass a pooled reading.
* B restart counts cut to 60/40/40 for N=8,12,16 (disclosed); N=16 PASS rests on 40 restarts per cell.
* A1: 5 Gaussian points (a <= 0.46) degenerate in double precision, passing there is vacuous; 24/29 non-degenerate.
* A reruns after a NaN bug, overlapping runs and a hang; buggy records retained in run0_buggy/.
* C seed formula: (N=120, kernel 0) and (N=20, kernel 1) share seeds (correlated streams; harmless for the claims).
* C ABNORMAL count 115 in RESULTS vs 114 in records (corrected).
* C gauss4 N=24: whether the 24-cell is a local minimum at a=4 untested.
* G2: wall-coordinate L-BFGS capped at 40 iterations, cap hit in 25-30 of 30 starts for rect2 and L-shape; "weak evidence".
* G1b R(0.75)=1.80 confounded by the all-nodes site rule; asterisk added.

## Overclaims
None found: no "3D solved", no human review claimed, no use of the unrefereed planar theorem; the only theorem cited is
Cohn-Kumar for the 600-cell as a comparator; the Poisson a*=pi statement is an exact classical identity, correctly labelled.

## Verified OK (recomputed independently by the reviewer)
A: 29 points x 300 starts = 8700 records; 0 starts below min(FCC,BCC); crossover a* = 3.14159265358987; Yukawa k* = 1.7179.
B: 9860 records, 145 cells; 49/58 pass for N<=4 with the 9 failures at 0.39-0.49; N=16 29/29; B2 0 cells below reference.
C: own 600-cell/24-cell construction within 1e-11 of reference.json; success counts 50/0/0/6/46/48 (N=120) and 50/25/7/0/5/6 (N=24);
no start below E600; gauss1 deviation 2.01e-8..3.05e-8, gauss2 6.9e-6..8.4e-6, gauss4 ~1.0e-3 for 44 starts.
D: 150 records; medians 0.7057/0.6331/0.5947/0.6690/0.7119; paired +0.0370+-0.0063 (25/30) vs cvt40, -0.0055+-0.0045 (10/30) vs cvt80,
+0.1131 vs cvt20, +0.0733 vs cm_only; 29-seed +0.0371+-0.0065, 24/29; worst rho 0.014 vs 0.029.
L3: escapes 0/288, 0/288, 0/288, 14/288 (10+2+1+1); accepted 284/283/286/267; R(w) 1.372, 1.802, 1.407, 1.172; G2 table matches
(cap counts 8, 25, 30, 30, 29, 2); max wall displacement 0.046.
