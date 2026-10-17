# H1''' results (PREREG.md; code frozen at 1e50f4b; evaluation `evaluate3.py`, see DEVIATIONS.md; gate on K = 50)

Run history: the 5 runs were launched together 2026-10-16 19:41 (`launch.sh`, single-threaded, 5 in parallel) and all finished
without interruption by 2026-10-17 05:53 (machine up since 2026-10-13 10:13, `uptime -s`); no relaunch, so the checkpoint/resume
path of rig3 was never exercised in a registered run. Solve times 5.3 h (V3 K=60) to 10.2 h (H4); certification 1.4-5.4 s each.
Rounds used: 18, 18, 18, 19, 13 (V3 K50, V3 K60, H2, H4, H8; cap 25). All five certificates completed; no bound exceeds a
lattice energy (no VOID). In V3 K50, H2 and H4 the vectors of the last 4-5 rounds could not be certified ("fhat check
failed for every lam"); the reported values come from the best certified rounds 13, 17, 13, 13, 11 (V3 K50, V3 K60, H2, H4,
H8), by which point the LP objective had stopped changing (registered rule: best certified B over the rounds).

| case | K | certified B (lower end of arb ball) | B(K) - B(K=40, H1'') | reference | verdict |
|---|---|---|---|---|---|
| V3 (d=3, a=pi) | **50** | 0.223217819358967 | +2.99e-8 | published 0.22321782 (CdCI Table 1.1); B - ref = -6.4e-10; window lower edge 0.22321781 | **pass (gate)** |
| V3 (d=3, a=pi) | 60 | 0.223217824549473 | +3.51e-8 | B - ref = +4.5e-9 | reported, not a gate; **certified only after re-check with a lift, see below** |
| H2 (d=3, a=2) | 50 | 1.01101824668405 | +1.76e-8 | min(FCC, BCC) = E_BCC 1.0158628160 | G = 4.77e-3 > 1e-3 |
| H4 (d=3, a=4) | 50 | 0.0727564554394576 | +1.80e-8 | E_FCC 0.0779676710 | G = 6.68e-2 > 1e-3 |
| H8 (d=3, a=8) | 50 | 0.00039476028934256 | +4.36e-10 | E_FCC 0.000503241302 | G = 0.2156 > 1e-3 |

Certificate parameters (records/*.json, `certificate`): tau = 3.6e-14 (V3 K50), 1.8e-16 (V3 K60), 3.7e-14 (H2), 1.1e-13 (H4),
1.8e-16 (H8); recorded Gaussian-lift delta <= 1.7e-28 (V3 K60: 0 recorded, 1e-25 after the re-check below); lambda used 6, 3, 8, 3, 5 (the registered ladder; V3 K50 and H2 needed a
second/third lambda after the first failed the fhat check). The certification loss tau x B is <= 1e-14 in every case.

**Registered outcome: the V3 gate passes at K = 50 (margin 9.4e-9 above the window's lower edge), so the H2/H4/H8 results at
K = 50 are registered results: G > 1e-3 at alpha = 2, 4, 8.** These are rigorous lower bounds (interval-certified Cohn-Kumar
two-point bounds as stated in CdCI Prop. 2.2; energy convention of CdCI Def. 1.1, sum over ordered pairs per point) on the
lower energy of every unit-density configuration in R^3 for the Gaussian exp(-alpha r^2), lying 0.48%, 6.7% and 21.6% below
the best lattice. Certification makes these *bound values* rigorous. It does **not** make rigorous the statement that two-point
bounds at this degree cannot decide FCC/BCC optimality: that would need a certified *upper* bound on the LP optimum (a dual
certificate, with b also optimised), which was not computed. That statement remains numerical (H1'; CdCI Table 1.1 at alpha =
pi). The registered reading in ../H1pp/PREREG.md ("insufficient ... (certified)") overstated what a lower bound can show.

**Post-hoc finding (hostile review, docs/designs/EXCITON_FLUID_VERIFIER_NOTES_H1ppp.md, item B1).** The frozen certificate code
(rig2.py/rig3.py `certify()`) does not check fhat >= 0 between near-double real roots of Q (in the V3 records, pairs 1.8e-15 to 3e-14 apart, Q < 0
between them) when their enclosures round to the same or adjacent doubles, and its bisection uses float box midpoints that do
not exactly cover very narrow boxes. An independent re-check (`recertify.py`, output `recertify_output.txt`: exact box cover,
outward-rounded root enclosures merged into clusters, exact sign in every gap) confirms all 14 H1'' records and the four
H1''' K = 50 records with their recorded lambda and lift delta, B equal to the record to ~20 digits. **The V3 K = 60 record
(delta = 0) is not a valid certificate as recorded**: Q is negative at exact rational points in 13 sub-ulp wells (down to
-9.9e3 near t = 210.54), so fhat < 0 there; this was confirmed with a separate exact evaluation. With delta = 1e-25 it is
certified and B is unchanged to 20 digits. The frozen code and records are left unchanged; "certified" in this round rests on
the frozen certificate plus this re-check.

Prediction (PREREG.md): "V3 passes, G > 1e-3 at all three, B's within 1e-6 relative of the H1' numerical values." First two
parts hold. The third holds for V3 (-2.5e-8), H2 (-4.0e-8), H4 (+4.4e-9) and **fails for H8** (-8.3e-6 relative: H1' numerical
0.000394763557 at K=40 vs certified 0.000394760289 at K=50). Most likely the H1' value overshot (the H1'' certified K=40 value
0.000394759853 is also ~9e-6 below it): it is an uncertified LP objective with residual
violation 9.8e-11 in f - g; at B ~ 4e-4 that residual is 2.5e-7 relative, and the LP objective's slack can be a large multiple
of the residual (H1' RESULTS: up to 35x), so an overshoot of this size is plausible. This is a failed prediction about a numerical value, not a
failed gate; it does not affect the G reading (G = 21.6% either way).

**On the H1'' V3 failure (CLAIM-128).** B(V3) rises monotonically with K: 0.2232177895 (K=40), 0.2232178194 (K=50),
0.2232178245 (K=60); increments 3.0e-8 then 5.2e-9. Raising K alone, with b, rows and gcut fixed, brings the certified value
into the window: raising K is *sufficient*. This does not identify the *cause* of the K=40 shortfall: H1' at the same K=40 and
b = 17/20 gave an (uncertified) LP objective 0.2232178249, while the H1'' K=40 LP objective is already 0.2232177895, so the
H1'' formulation (tail rows R <= -1e-12 beyond u1, gcut, margins) may cost as much as the degree does; alternatively H1'
overshot by ~3.5e-8. These were not separated. K=60 exceeds 0.22321782 by 4.5e-9, which is compatible with the printed value
whether truncated or rounded. The H1'' registered outcome stands as a gate failure; this round does not change it.

What this does not show: nothing about K -> infinity (B is not known to have converged: the K=50 -> 60 increment is 5e-9);
nothing about bounds beyond two-point (three-point / SDP bounds can be much stronger); nothing about alpha other than 2, pi, 4, 8;
the b values are the H1' snapped optima, not re-optimised at K=50, so the bounds are valid but may not be the best two-point
bounds at this K. K=60 was run only for V3.
