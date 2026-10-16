# H1'' results (PREREG.md; code frozen at b1d2de5, evaluation `evaluate.py`, gate on K = 40)

Run history: 14 runs launched 2026-10-13 03:42; a machine reboot (boot time 10:14, `uptime -s`) killed the 7 running jobs after ~6.5 h
(only H8 K=40 had finished; dead logs in `logs_killed_by_reboot/`); 6 K=30 jobs had not yet started. The 13 unfinished runs were relaunched from scratch with
`launch_resume.sh` (same code, same parameters, no checkpointing) and all finished 2026-10-14. No result was
selected between the two launches.

| case | K=40 B (certified) | reference | verdict |
|---|---|---|---|
| V1a (d=1, a=1) | 0.772637204826132 | E_Z 0.772637204826652, rel gap 6.7e-13 | pass |
| V1b (d=1, a=pi) | 0.0864348112113391 | E_Z 0.086434811213308, rel gap 2.3e-11 | pass |
| V2 (d=2, a=pi) | 0.159595266956366 | window 0.15959526 - 1e-8; E_A2 - B = 7.6e-12 | pass |
| V3 (d=3, a=pi) | 0.2232177894732 | 0.22321782 (Cohn-de Courcy-Ireland); B - ref = -3.05e-8 | **FAIL** (tolerance 1e-8) |
| H2, H4, H8 | 1.01101823, 0.07275644, 0.00039476 | G = 0.48%, 6.7%, 21.6% | gated: not registered results |

**Registered outcome: gate V3 failed, so the H1'' (alpha = 2, 4, 8) claim is NOT obtained.** The H-case numbers
above are reported as "gated" only. All 14 certificates completed; no bound exceeded a lattice energy (no VOID).
K=30 values are lower than K=40 for V2, V3, H2, H4, H8, but HIGHER for V1a and V1b (closer to E_Z), so the
K-dependence is not uniformly monotone. The cause of the V3 shortfall (3.05e-8 below the published 8-digit value)
is undetermined. Untested candidates: K=40 truncation; the published value being a non-rigorous numerical optimum
that may slightly overshoot; the fixed snapped b = 17/20; the gcut = 1e-12 row margin. Certification loss
(tau x B ~ 1e-13) is far too small to explain it. Re-running at larger K is a new pre-registration, not a repair of this one.
