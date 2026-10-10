# Scratch scripts of the study (copied verbatim)

`study_checks.py`, `study_checks2.py` and `study_gated_cm.py` are the throw-away scripts run while writing
`docs/designs/EXCITON_FLUID_LEAN_SOLVER_PLAN.md` (their numbers are its Appendix B). They were copied unmodified from the
session scratchpad and re-run on 2026-10-11: they reproduce the quoted values (Keldysh identity to 2e-31 at x = 0.1, 5e-32 and
4e-32 at x = 1, 5; the dual-gated kernels' derivative signs; the four-flavour table).

* `study_checks.py` prints an `e_H/e_lat` table with a short cutoff (43.79, 14.13, ...); it is **superseded** by the converged
  values of `results/phase1/reference.json` (44.7, 14.2, 4.64, 2.87, 1.87, 1.44; Phase 1 gate KA-4).
* `study_gated_cm.py` checks the sign pattern of `(-1)^k g^(k)` to order 5 at 7 values of `t` for gate distances 5, 7.5 and
  10 nm and `d = 2 nm`: evidence, not a proof.
