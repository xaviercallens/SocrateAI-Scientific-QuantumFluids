# H1''' results (PREREG.md; code frozen at 1e50f4b; evaluation `evaluate3.py`, see DEVIATIONS.md; gate on K = 50)

Run history: the 5 runs were launched together 2026-10-16 19:41 (`launch.sh`, single-threaded, 5 in parallel) and all finished
without interruption by 2026-10-17 05:53 (machine up since 2026-10-13 10:13, `uptime -s`); no relaunch, so the checkpoint/resume
path of rig3 was never exercised in a registered run. Solve times 5.3 h (V3 K=60) to 10.2 h (H4); certification 1-5 s each.
Rounds used: 18, 18, 18, 19, 13 (V3 K50, V3 K60, H2, H4, H8; cap 25). All five certificates completed; no bound exceeds a
lattice energy (no VOID).

| case | K | certified B (lower end of arb ball) | B(K) - B(K=40, H1'') | reference | verdict |
|---|---|---|---|---|---|
| V3 (d=3, a=pi) | **50** | 0.223217819358967 | +2.99e-8 | published 0.22321782 (CdCI Table 1.1); B - ref = -6.4e-10; window lower edge 0.22321781 | **pass (gate)** |
| V3 (d=3, a=pi) | 60 | 0.223217824549473 | +3.51e-8 | B - ref = +4.5e-9 | pass (reported, not a gate) |
| H2 (d=3, a=2) | 50 | 1.01101824668405 | +1.76e-8 | min(FCC, BCC) = E_BCC 1.0158628160 | G = 4.77e-3 > 1e-3 |
| H4 (d=3, a=4) | 50 | 0.0727564554394576 | +1.80e-8 | E_FCC 0.0779676710 | G = 6.68e-2 > 1e-3 |
| H8 (d=3, a=8) | 50 | 0.00039476028934256 | +4.36e-10 | E_FCC 0.000503241302 | G = 0.2156 > 1e-3 |

Certificate parameters (records/*.json, `certificate`): tau = 3.6e-14 (V3 K50), 1.8e-16 (V3 K60), 3.7e-14 (H2), 1.1e-13 (H4),
1.8e-16 (H8); Gaussian-lift delta <= 1.7e-28; lambda used 6, 3, 8, 3, 5 (the registered ladder; V3 K50 and H2 needed a
second/third lambda after the first failed the fhat check). The certification loss tau x B is <= 1e-14 in every case.

**Registered outcome: the V3 gate passes at K = 50 (margin 9.4e-9 above the window's lower edge), so the H2/H4/H8 results at
K = 50 are registered results: G > 1e-3 at alpha = 2, 4, 8.** These are rigorous lower bounds (interval-certified Cohn-Kumar
two-point bounds as stated in CdCI Prop. 2.2) on the energy of any configuration of unit density in R^3 for the Gaussian
exp(-alpha r^2), and they lie 0.48%, 6.7% and 21.6% below the best lattice: the two-point bound at this degree does not decide
whether FCC/BCC is optimal at alpha = 2, 4, 8, now certified rather than only numerical (H1').

Prediction (PREREG.md): "V3 passes, G > 1e-3 at all three, B's within 1e-6 relative of the H1' numerical values." First two
parts hold. The third holds for V3 (-2.5e-8), H2 (-4.0e-8), H4 (+4.4e-9) and **fails for H8** (-8.3e-6 relative: H1' numerical
0.000394763557 at K=40 vs certified 0.000394760289 at K=50). The H1' value is an uncertified LP objective with residual
violation 9.8e-11 in f - g; at B ~ 4e-4 that residual is 2.5e-7 relative, and the LP objective's slack can be a large multiple
of the residual (H1' RESULTS: up to 35x), so the H1' value overshot. This is a failed prediction about a numerical value, not a
failed gate; it does not affect the G reading (G = 21.6% either way).

**On the H1'' V3 failure (CLAIM-128).** B(V3) rises monotonically with K: 0.2232177895 (K=40), 0.2232178194 (K=50),
0.2232178245 (K=60); increments 3.0e-8 then 5.2e-9. The K=40 shortfall of 3.05e-8 is therefore accounted for by truncation in K:
the same method, rows, b and gcut certify a value inside the window at K=50 and above the published 8-digit value at K=60. The
other H1'' candidates (snapped b = 17/20, gcut row margin, a published value that overshoots) were not tested and are not
needed to explain the gap; the K=60 value being above 0.22321782 is consistent with the published digits being truncated
("0.22321782...") rather than rounded. The H1'' registered outcome stands as a gate failure; this round does not change it.

What this does not show: nothing about K -> infinity (B is not known to have converged: the K=50 -> 60 increment is 5e-9);
nothing about bounds beyond two-point (three-point / SDP bounds can be much stronger); nothing about alpha other than 2, pi, 4, 8;
the b values are the H1' snapped optima, not re-optimised at K=50, so the bounds are valid but may not be the best two-point
bounds at this K. K=60 was run only for V3.
