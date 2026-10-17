# H1d deviations from the registered design

1. **evaluate.py (2026-10-17 ~10:00, runs in flight, evaluator not yet run on gate records).** Pre-run math/code review
   (docs/designs/EXCITON_FLUID_VERIFIER_NOTES_H1d_math.md, should-fix 2): a VOID in one D3 case only annotated later D3 cases,
   while PREREG says any VOID gates all D3 results. Fixed: notes are applied after all cases. Minor 2 of the same review: the
   "UB < min(FCC,BCC)" verdict now requires a relative margin of 1e-12 (arb upper end vs float lattice sums) and quotes the
   margin. No criterion was loosened. Per-grid log lines (D3pi, D3a2 partial) had been seen when this was written.
