# Verification of package fenris (L6) - verdict: accept_with_fixes

## Independent recomputation (own numpy/scipy code, ver.py in scratchpad; reads only the stored best-state npz)
Own shifted-force kernel (closed-form ungated; K0 mode sum for gated D=1.5, 400 modes), own wall (stored spacing-1 sites + midpoints), own Delaunay:
- square ungated, square gated D=1.5, hexagon ungated, kagomecut ungated, rect2 gated D=5: E_ff and E_fb agree with the worker to <= 1e-13 absolute; max|F| ~ 2-9e-11 (stationary); non-6 coordination count and Q = sum(6-c) agree exactly (19/19, 19/19, 7/7, 6/6, 7/7; Q -1, -1, -5, +2, -1).
- table_all.csv recomputed: 44 wallhalfrsa cases, 1056 starts, 1031 accepted, 0 escaped, 1054 PD, 942 strict, 90 accepted-not-strict; all Euler OK. Per-shape defect means match the report (all 36 numbers checked for 9 shapes x 4 kernels). Between-shape std 6.33 and within-shape 0.79 reproduce with ddof=0 (ddof=1: 6.64 / 0.91). Spearman 0.88-0.97 reproduces. Mean Q by shape reproduces. Median frac_best(1e-6)=0.085, median distinct=18 reproduce. Size series and sens numbers reproduce.

## Pre-registration integrity
PREREG committed 36f5dfd (11:41) before any run; only change to the original body is the removal of "(none yet)". Amendments A1-A5 are dated and each placed before the runs it affects (commit sequence 92436f6 -> d57dad6 -> 081352e -> 7974b13 -> 44cf49b/292b39a). No threshold was relaxed to hide a kernel failure (A1 a4 floor was a harness fault, shown to equal the omitted 2*pi*1e-6 piece; A2.5 a1 floor justified by table noise). Honest disclosure of the 12-of-44 primary stop, of the kagome first-pass failure, of N 400/600 not run.

## Problems
Major
1. Headline finding 1 ("the bare fixed-node wall at mean spacing does not confine") is not established. Amendment A4 itself shows that at w=0.5 the escapes came from the violent first part of the flow with uniform starts containing close pairs, and that RSA starts cured it (0/96). The w=1 wall was never rerun with RSA starts, so the w=1 escapes are confounded by the start distribution. The saddle/"interior pressure" mechanism in A3 is asserted, not tested (no w=1+RSA, no static saddle check). Must be restated as "w=1 with uniform random starts: 19-24 of 24 escaped; w=1 with RSA starts untested".
2. Scope of "geometry dominates, kernel barely matters" and of the defect counts: all production data use one wall model (fixed nodes at spacing 0.5, spacing-1 sites for triangulation, 7% nn mismatch) and 30-88 % of defects sit at that wall. Wall-spacing sensitivity is not run (listed "not run"), so the numbers are a property of the wall model as much as of shape. The caveat exists in the report but the summary's finding 3 states it unqualified.
3. The requested RESULTS file docs/designs/EXCITON_FLUID_L6_FENRIS_RESULTS.md, the docs/designs prereg and exploration/exciton/results/l6_fenris/ do not exist; everything lives under the crate (PREREG.md, README.md, results/). Assigned deliverable paths are unmet; results narrative exists only as amendment text and the worker's summary. Also Cargo.toml depends on a scratchpad path (not rebuildable from the repo without README steps).

Minor
4. Euler/Q "holds in 100 %" is a mathematical identity for any conforming triangulation; the gate tests the code, not the physics. "Q set by the boundary" is true only given k_b, which is itself state dependent (Q_std up to 0.7 within a case). Wording overstates.
5. "36-88 % of non-6 nodes within 1.5 of the wall": table gives 30-88 % (square 0.30-0.42, rect1.25 0.34). "0-3 at distance >=3": max case mean 3.25.
6. Sibling comparison: "their -1..-4" is wrong, edge_overlap.json shows sibling charges +6 (N37 gated D/d=3), -2, -1, -4.
7. "Commensurate shapes order better, incommensurate worse" rests on three shapes and one size ratio; square defect growth 17-20 -> 23-26 is roughly the sqrt(2) perimeter scaling, so "gets worse" is mostly wall-localised scaling. Interpretation, not demonstrated.
8. Statistics are over accepted starts only (86-96 per shape of 96; 25 starts dropped) - a mild selection effect, reported only as counts.
9. L-c has a single inside minimum per case (disclosed); L-d bug1 not caught by a2 (disclosed).

No invented numbers or citations found; no blocking issue.
