# H1d deviations from the registered design

1. **evaluate.py (2026-10-17 ~10:00, runs in flight, evaluator not yet run on gate records).** Pre-run math/code review
   (docs/designs/EXCITON_FLUID_VERIFIER_NOTES_H1d_math.md, should-fix 2): a VOID in one D3 case only annotated later D3 cases,
   while PREREG says any VOID gates all D3 results. Fixed: notes are applied after all cases. Minor 2 of the same review: the
   "UB < min(FCC,BCC)" verdict now requires a relative margin of 1e-12 (arb upper end vs float lattice sums) and quotes the
   margin. No criterion was loosened. When the fix was committed (09:59:54) 21 of the 31 records existed (all V1, V2; D3pi 5 of 6; D3a2 5 of 6; D3a4 4 of 6; D3a8
   none), the D3pi (8, 48) solver failure was already in the log, and per-grid log lines had been seen. The fix only tightens
   the criterion (any VOID now gates all D3; a 1e-12 margin is required), so it cannot favour the observed outcome.
2. **Launch time.** RESULTS.md first gave the launch as 09:20; it was 09:33:31, after the freeze commit (09:33:26). Corrected
   after the results review (docs/designs/EXCITON_FLUID_VERIFIER_NOTES_H1d_results.md, SF-1). No gate parameter was run before
   the freeze (only dev/DEV_s4_m24.json, α = 1).
