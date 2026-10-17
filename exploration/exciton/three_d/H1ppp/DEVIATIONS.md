# H1''' deviations from the registered design

1. **Evaluator (2026-10-16 ~22:20, runs in flight, no record written yet).** The frozen `evaluate.py` is an
   unmodified copy of `../H1pp/evaluate.py`: it reads only K = 40/30 records, so it cannot evaluate this round. Added
   `evaluate3.py`, which imports the frozen helpers (`B_of`, lattice energies) and applies the PREREG.md criteria
   unchanged (V3 window B >= 0.22321782 - 1e-8 at K = 50; G thresholds 1e-3 / 1e-6; VOID test at 1 + 1e-12)
   to K = 50 and K = 60, plus B(K=50) - B(K=40) from `../H1pp/records` and the K = 40/50/60 monotonicity flag.
   Disclosure: the per-round intermediate certified values in `logs/` had been looked at before this was written
   (V3 K = 50 round 6 certB 0.2232178192). No criterion was changed; the evaluator only reads records written by
   the frozen driver.

2. **Driver detail (noted by the review, M5).** `run_h1pp.py` also skips a case whose record exists (needed for relaunch), so
   "rig3 = rig2 + checkpointing only" holds for rig3.py but the driver has this extra logic; its docstring still says "K in 40 30".
   No case was skipped (no relaunch). `records/ckpt/` (intermediate state, ~1 MB) is not committed; the final records contain the
   certified coefficients.
3. **Post-hoc re-check (review item B1, 2026-10-17, after all records).** `recertify.py` added; V3 K = 60 is certified only
   with a lift added by the re-check (RESULTS.md). Frozen code and records unchanged.
