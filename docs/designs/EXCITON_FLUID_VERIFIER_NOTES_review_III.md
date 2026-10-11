# Referee report: paper/exciton_fluid_gated_III.tex (pre-deposit), 2026-10-11

Method: every number re-derived from summary.json, ke/diag logs, table_all.csv, gates_*.json, PREREG.md amendments, git history,
both figure scripts and PNGs. Paper not edited. Line numbers refer to exciton_fluid_gated_III.tex.
Overall: most numbers reproduce. The paper's main honesty features (pulsation worded as "pulsation", no "limit cycle"; weak K-d; failed K-d'; wall design
failure) are in good shape. But there are 2 blocking-grade items, several majors, and a set of number/attribution slips.

## BLOCKING

B1. "Each amendment was committed before the runs it announces" (l.54-55, l.125) is false for Fenris A4 (and A5.3).
    - Fenris A4 (RSA starts; the production design) is first present in commit 7974b13 (13:09), the same commit that adds all 44
      wallhalfrsa production cases and A5. `git show 081352e:.../PREREG.md` has only A1-A3; `sample_rsa` count in study.py at 081352e is 0.
    - A4's own header says "after 2 uniform-start wallhalf cases and 4 square cases with the new start" (PREREG.md l.170), i.e. the
      design change and 4 RSA test runs preceded the amendment text; PREREG body was never re-committed before production.
    - The verifier's "commit sequence ... 7974b13" glossed this. Fix: say "A1-A3 (Fenris) and A1-A6 (Krylov) precede their runs; Fenris A4
      was written after a 4-case RSA test and committed together with the production results; A5 during analysis".
B2. "No gate was loosened to turn a failure into a pass" (l.55) is too strong. Counter-examples in the record:
    Fenris A1 rewrote the a4 criterion after it failed (relative -> 1e-8(|U|+1e-3)); A2.5 added an absolute floor to a1 after it failed;
    A2 set CVODE rtol 1e-2 (validated by new gate L-f); Krylov K-e2 stopping rule changed twice while the run was live (A3 CPU cap
    at t~8000, A4 hand stop at t=15000, 7.5% of the registered 2e5 horizon); K-d' invented after K-d could not fail; K-a1 t=16000 rtol 1e-4 (A1).
    These are defensible (harness faults, documented) but "no gate loosened" is not a statement the files support. Say "criteria were changed
    by dated amendments, listed here: ...".

## MAJOR

M1. "Defects sit at the wall" / abstract "most defects lie at the wall" (l.46, l.171-172, metadata description) is not supported against the
    obvious null (fraction of nodes near the wall).
    - table_all.csv, wallhalfrsa: n_deep_mean (nodes at wall distance >=3) vs n_defect_deep_mean. Annulus, maze: 0 deep nodes, L-shape 3.3: the
      statement is vacuous (every node is within 3 of a wall). Density ratio defect/node in the deep region: hexagon 0.88, triangle 1.38,
      L-shape 1.64 (no wall concentration at all), disc 0.14, rect 0.14-0.48, square 0.49.
    - Using the paper's own criterion (<1.5 spacings), "most" is false for 5 of 11 shapes: square 0.30-0.42, rect1.25 0.34-0.39,
      rect1.5 0.33-0.45, rect2 0.40-0.43, L-shape 0.45-0.49. Only the <3 criterion (66-100%) gives "most".
    - Fix: state per-shape fractions against the node fraction in the same band, or delete "most defects lie at the wall" from abstract/metadata.
M2. Sensitivity bullet (l.183-185): "within a few per cent of the primary values" is wrong. sens vs primary mean non-6 counts:
    square gated D/d=10 18.88 vs 16.25 (+16%); square Yukawa 18.0 vs 20.1 (-11%); hexagon Yukawa 8.67 vs 7.83 (+11%); square gated D/d=3 +6%,
    hexagon gated D/d=3 +6%. |psi6| differences up to 0.06 (0.692 vs 0.753). Changing kernel parameters moves counts by as much as
    the between-kernel effect that the paper calls "little". Also (kernel params differ), so this is a parameter sensitivity, not a wall one;
    wall-spacing sensitivity is not run (stated in Limits, good).
M3. "Shape dominates, kernel matters little" (l.165-170): between-shape SD 6.3 is dominated by the annulus/hexagon/rect2 extremes.
    In the middle (disc 20, square 16-20, maze 17-18, rect1.25 16-17, rect1.5 13-17, L-shape 15-18) the kernel range (up to 4.5) exceeds gaps
    between neighbouring shapes; no sampling error bars are given (24 starts, per-start SD of the count is several units, SE ~ 0.7-1,
    comparable to the 0.79 within-shape SD). Qualify to "extremes ordered by shape; mid-range shapes not resolved against kernel".
M4. K-d' "badsign deviation at tolerance-noise level, gate too tight" (l.126-127) contradicts the paper's own numbers: K-e0 rtol 1e-4 vs 1e-6
    differs by 6e-9; seed spread 5e-8; kin/jac/fd deviate 3e-8-8e-9; badsign is 2.0e-7 (4x seed spread, 30x rtol effect) and its
    n_center deviation 3.6e-6 is 3.6x its gate. Report both K-d' failures as failures; do not argue the badsign one away.
M5. Misattributions to paper II (verified in the .tex of I and II): (a) "Paper II found dense CVODE, 43 ms per step at 768 unknowns" (l.65):
    it is in paper I (exciton_fluid_gated.tex l.165) and ETD note; (b) "box-area artefact reported in paper II" (l.120): it is in
    paper I (exciton_fluid_gated.tex l.243); paper II has no such statement. Paper II itself is described correctly
    (DOI 10.5281/zenodo.23297479 matches zenodo_record_exciton_gated_II.json; ETDRK4, "has no error control" in II l.285; it also says the Krylov
    work was unfinished).
M6. Numbers typed from verifier reports that are not committed: table header "(verifier's recomputation from the raw records)", rms 0.08
    (l.110; I reproduced 0.080 on 141 common samples, relative to a signal rms ~0.97, i.e. 8%; but no script/output of it is in the repo),
    and l.59 "All numbers are read from committed files". verify_krylov.md / verify2_fenris.md live only in the scratchpad (`git ls-files | grep verify`: nothing
    relevant). Either commit the verifier reports/scripts or reword. The "independent" verifier is an AI instance (the metadata says "independent
    instances"; the abstract/body say "independent hostile verifier" without saying AI) - say so in the body.
M7. Periods "956, 966, 969 at M=16,32,64 to t=40000" (l.109-110): M=64 only reached t=15000 (14 cycles); 40000 applies to M=16,32. Also the
    M=16 waveform does not match M=32 (rms 0.71 over t 1000-15000, amplitude max 1.77 vs 2.14 vs 2.07); only M32-M64 agree. And "oscillates between
    0.005 and 2.07" (l.108) holds only for t>=2000: figure (b) shows 3.4 at t~1400 and 8e-4 at t~1900 (summary uses t>=2000). State the window.
M8. Gate failure scope: K-e2 was registered as "residual <1e-7 within t=2e5"; the run was stopped at t=15000 (7.5% of horizon). The paper's
    "registered gate failed" is "not demonstrated by t=15000 and a persistent pulsation seen". l.90-91 does say stopped by hand,
    but the failbox/abstract headline does not carry the horizon. The D1 runs to 40000 are other grids.
M9. Speed claim wording: abstract "slower than dense CVODE at 8x8 and faster at 16x16" omits that it is one t=20 transient, one seed,
    rtol 1e-7 vs CVODE 1e-10 (KR error ~1e-6 vs CVODE-reference; K-a2 9e-7) and that CVODE rtol 1e-7 repeats at 16x16 scatter 108-135 s.
    Add "transient t=20" in the abstract. (The stationary-state advantage, G8 14.5 s vs CVODE 227 s in the ETD note, is real but omitted.)
    Cost exponent: M=8..64 also changes L=M, sigma=0.1875M (run_kc.sh), so M^2.15 is cost vs number of unknowns^1.07 at fixed h; per-step exponents
    1.91/2.50/2.29 (steps 27933/27550/22143/23093 differ). The local slopes (1.9, 2.2, 2.35) are correctly given; the abstract's single "M^2.15"
    reads as an asymptotic law; say "no asymptotic claim".

## MINOR (number / wording slips)

m1. l.88 K-e "15-600 CPU s": K-e0/e1/e3 range 7.35 s (G8 V0.25) to 2076 s (R64); G32 594 s; R64 2076 s (K-e3 itself). Correct to "7-2100 s".
m2. l.178 "standard deviation of Q up to 0.7 within a case": production max Q_std = 1.29 (rect1.25 gated D/d=10), maze 1.15-1.28.
m3. l.178 "disc -1.5": mean is -1.63. Hexagon -4.0, triangle -3.5, annulus -4.65, maze +5.74 ok.
m4. l.181 "hexagon (0.04-0.78)": at N=100 production the hexagon range is 0.04-0.38; 0.78 is the N=200 size series. Mixed groups.
    "mostly 1/24": 21 of 44 cases are 0.04 (1/24); median 0.085 ok.
m5. l.166 L-shape gated D/d=10 = 16.2 (16.15 -> table) vs paper 16.1. Rectangle 1.25 (17.2/16.3/16.3/17.3) is omitted from the list.
m6. l.140-144 L-c "1.3e-14 relative": max over the 8 cases is 1.5e-14 (gated 1.5 N3). L-b "5 of 6" is listed under "all pass": the failing test
    fails equally on the unpatched tree (gate_b3_original...), PREREG calls b3 "reported", b2 passed at 8.8e-8 vs threshold 1e-7 - say b3 is
    a reported 5/6 not a pass, and name the failing test.
m7. Size series (l.173-175, fig panel b): N=200 uses 20 starts (not 24), no error bars; "mostly wall-localised scaling" does not fit the disc
    (20.0 -> 33.4 = x1.67 > sqrt2). Cover caption (a) "24 RSA starts each" ok for N=100 only.
m8. l.76-77 K-a1: unaligned full-state rel L2 is 0.94 (summary K-a1_fullstate_kr_vs_cvode.rel_l2); the 1.2e-6 is after a U(1)
    phase alignment. State that. The t=16000 comparison is of stationary states under frame tracking (A1), not of trajectories.
m9. K-d3 "caught only by a unit test": the unit-test value (1.5e-2) is not archived in results/ (verifier M2, not fixed). K-d1: badsign's 1.508x comes from
    50% more Newton iterations (167609 vs 111740), not more GMRES per Newton; none/kin cost the same GMRES total. Minor, still worth a clause.
m10. K-e3 relies on R64 with band-limited initial noise; white-noise check only at R32 (verifier m4, not mentioned).
m11. K-d' row (l.86): "block, kin, jac, fd" - block is the reference run, not one of the six variants (kin, jac, fd, rhs, badsign, none); rhs (shift
    differs by 8.4) omitted. "4 of 6" counts rhs as a pass.
m12. Fenris verifier #3 (requested RESULTS note absent) is disclosed (l.191-192) - OK. Cargo.toml depends on a scratchpad path (README steps);
    reproducibility sentence at l.208 mentions it - OK.

## Figures
- fig_krylov (a): y-axis label says "rtol 1e-7", but the CVODE curve is the rtol 1e-10 data (1.40 s, 90.5 s) typed in the script
  (summary.json K-c has them, so the typing is unnecessary; the paper's "copied from the verifier's recomputation" l.60-61 is also not
  accurate: they are in summary.json). Legend does not state CVODE rtol. The two-point CVODE line against M^2/M^3 invites extrapolation.
- fig_krylov (b): matches data (150 samples, V0=0.5 to t=15000; V0=0.25 stops 7300). y floor clipped at 1e-4. The transient at t<2000 (3.4 peak,
  8e-4 dip) is visible but excluded from the quoted 0.005-2.07 range.
- fig_fenris: values match table_all.csv (verified shape ordering and size endpoints 7.9->3.5, 19.8->25.4, 20.0->33.4). No error bars; N=200 point has 20 starts;
  the two gated kernels share one marker (caption says so).

## Confirmed OK (reproduced)
K-a1/K-a2/K-b numbers; K-c medians 7.22/26.81/121.85/620.9, exponent 2.146, local slopes 1.89/2.19/2.35, 3.4-4.9x; K-d counts (1.508, 2.58);
K-d' table (10.6/1142 s, 23.0/1415 s, 4e-6); K-e3 0.0766598/0.0767908/0.0768237; K-e4 slopes and ratios 0.69/0.55/0.51; 12.5% and 8.8%;
G64a: 14 peaks, period 969, 0.0047-2.066 (t>=2000), omega 0.5607-0.5745, resid 4e-3-2e-2, 7761 CPU s; D1 M32/M16 39/40 peaks, 966/956; D2 stopped t=500;
V0=0.25 resid 2.2e-9 at 7300, shift 0.0447. Fenris: 44 cases, 1056/1031/0 escaped, 1054 PD, 90 non-strict, 0 Euler failures,
all 36 means, 6.3/0.79 (6.6/0.91 ddof=1), median 0.085 and 18, primary stop (0-5 of 24 survive; 23/24 ungated square), wallhalf 10-11/24 escaped,
0/96 RSA square, L-f 2.9e-9. Paper does not use "limit cycle" anywhere (good; committed PREREG/commit message do). No gendered pronouns. Paper I DOI and title match.

## Verdict
Do not deposit until B1, B2 are reworded and M1, M2, M4, M5, m1, m2 are corrected; M3, M6-M9 should be fixed in the same pass (all wording/number edits, no new runs needed).
