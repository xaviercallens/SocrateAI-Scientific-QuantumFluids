# Verification of package 'etd' (hostile verifier)

Verdict: accept_with_fixes (no blocking problem).

Independent recomputation (own numpy ETDRK4, 64-point contour, scipy DOP853 rtol 1e-13 reference, own random start):
- T-b G8 gamma_R=200: ratios 2.25, 2.90, 4.49, 7.21 (worker 2.25, 2.90, 4.49, 7.22); E(h=0.2)=4.74e-5 (worker 4.69e-5).
- T-b G16: ratios 1.98, 2.82, 4.47, 7.21 (worker 1.97, 2.82, 4.47, 7.21).
- Control gamma_R=2 G8: 19.97, 16.7, 15.9 (worker 19.9, 17.3, 10.2; worker's last two sit at its reference floor, as disclosed).
- T-d(iii) G16 own code: V0=0.25 shift 0.046295, n_center 5.8440 (identical to worker); V0=0.5 shift 0.07666, n_center 2.376-2.377 at t=8000 (worker 0.07666, 2.3767).

Pre-registration: prereg commit 060526e (11:34:18) precedes all run files (first a.jsonl 11:43). A1-A3 committed before the runs they announce.
d_ii V0=1 row (mtime 11:57:17) post-dates A2 (11:56:34); A2 makes no claim about it. Pinned rusty-SUNDIALS tree at 5db8041, clean.
Commits touch only assigned paths.

Issues (non-blocking):
1. src/ was first committed with the results (396bec0), not before the runs; only the prereg was.
2. T-d(iii) tolerances (6e-4, 0.01) are about the rounding of the reviewer's 3-digit values: the PASS is a weak consistency check; the note does not say so.
3. T-c "stable" reference wording ("h_ref 0.0125 or smaller, checked against h_ref/2") differs from prereg (fixed h=0.0125); undeclared minor change.
4. Hochbruck-Ostermann attribution is from memory (disclosed); "not a coding error / is the stiff-order reduction" is stated more firmly than the gamma_R scan strictly proves (my independent code does reproduce the ratios, so coding error is excluded).
5. T-c summary row "limit 0.54-0.64" conflates last-stable and h_first.
6. Results live in crate/results/, not exploration/exciton/results/etd (allowed).
7. T-e(ii) CVODE 227 s not re-run by me; jsonl is consistent with the note. Krylov comparison flagged non-like-for-like.
No invented numbers found among those checked.
