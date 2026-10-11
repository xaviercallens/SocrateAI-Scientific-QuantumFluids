# Verification of exploration/exciton/krylov (Newton-Krylov SDIRK2+GMRES), 2026-10-11

Verifier worked from raw ka1/ka2/kb/kc/kd/ke/diag .jsonl, *.log, *_cmp_*.json, PREREG.md, git history, model.rs, evaluate.py.
No repo file edited. I also ran `kr test` (fast unit test).

## (a) VERDICT

Overall: the package is honest and its numbers reproduce from raw files (I found no arithmetic discrepancy with summary.json).
All amendments precede the runs they announce. No gate was loosened to turn a fail into a pass. Two registered gates
fail and one is not met; all are disclosed in summary.json and in the amendments. No blocking item. Majors are about what
may be CLAIMED (limit cycle, K-d as a test, speed-up).

### Blocking
None.

### Major
M1. "Limit cycle" is a reading, not a result. Established: a persistent, non-decaying, nearly periodic pulsation of
    n_center (about 0.005 to 2.1, sampled) and residual (4e-3 to 2e-2), period 956 (M16) / 966 (M32) / 969 (M64), 14 cycles
    at M64 and 39-40 cycles at M32/M16 (to t=40000). M64 and M32 waveforms agree after t>=1000 to rms 0.08 in n_center (my
    calculation, 141 common samples), although the initial noise realisations differ (noise is per grid point). Not established:
    (i) no independent integrator (CVODE at M=16, L=64 is permitted by the binary but was not run; ETD has no run at this
    geometry); (ii) D2 (rtol 1e-6) reached only t=500, i.e. before the first pulsation peak at t~1400, so tolerance
    independence of the pulsation itself is untested (over t<=500 D2 and D1 agree to <=1.3e-2 absolute in n_center: 5.1748/5.1753,
    5.8308/5.8331, 3.9507/3.9513, 2.2725/2.2599, 1.3274/1.3239); (iii) no Newton solve for the (unstable) fixed point and
    no linear stability analysis, so "Hopf" or "limit cycle" is untested; (iv) single seed, single V0, single L (64);
    (v) A4 text says "amplitude does not decay" from samples every 100 time units; the sampled peak heights (1.73-2.07) vary
    with a 2900-unit pattern which is the aliasing of period ~966 against the 100-unit sampling, not a physical modulation.
    Supporting circumstantial evidence (my reading, not registered): G32 (same sigma/L) converges but through a slowly damped
    oscillation (n_center 5.96, 0.36, 1.33, 0.86, 1.09, ... 1.0004; residual 8.7e-2 -> 4e-8; t to 1e-8 grows G8 4700, G16 6800, G32 16500),
    which is what a near-marginal mode crossing at L between 32 and 64 would look like. Artefact vs physics: the resolution
    (h=4,2,1) and noise independence argue against a spatial-discretisation or noise artefact; the pulsation is produced by
    the same integrator at the same rtol 1e-4 in all three, with step sizes 0.07-0.4 (>> smaller than the period), so a
    time-truncation origin is unlikely but not excluded without an rtol or integrator change on the pulsating phase.
    Wording that is safe: "the solver does not converge to a stationary state at G64a V0=0.5; the density pulsates with period
    ~970 at M=16, 32, 64 at rtol 1e-4 for 14-40 cycles; whether this is a physical limit cycle was not tested independently".

M2. K-d1/K-d3/K-d4 passed in a regime where they could hardly fail (A2 says so itself). K-d1 margin is 1.508 vs 1.5 (168490/111740),
    and badsign's excess comes from 50% more Newton iterations (167609 vs 111740), not from GMRES per Newton; `none` and `kin`
    show the same GMRES total as badsign (167610, 167476). K-d3 (BUG=jac) is bit-identical in counts at t=20 and within 0.02% in
    Newton count at h~10 (K-d'); it is detected only by the unit test (`kr test`: planted-bug jv vs FD relative difference
    1.547e-2, I re-ran it; value not archived in results/). Reason: the flipped term is only dgain*(a,b) in jv, the preconditioner
    uses the correct jloc, and Newton convergence is controlled by the true residual. So the "planted Jacobian bug" never changes
    a trajectory in this problem. Say: "Jacobian bug caught by the finite-difference unit test; harmless to the Newton solve".

M3. K-d' (A2) gates FAIL for two of the six variants, per the gate as written (|d shift|<=1e-7, |d n_center|<=1e-6 or non-null error):
    PREC=none: d_shift 9.9e-7, residual 4.1e-6 at the t=2e5 cap, 23.0 GMRES/Newton, 41784 Newton failures, 1415 CPU s vs 62 s;
    PREC=badsign: d_shift 2.0e-7, d_nc 3.6e-6, converged (resid 8.2e-9, t=7500), 10.6 GMRES/Newton, 1142 CPU s.
    The `badsign` fail is at the tolerance-noise level (seed spread 5e-8) so it says "gate too tight", while `none` is a real
    non-convergence. Reported as pass=false in summary.json; the failure is not a solver bug but must be quoted as a failed gate.
    Positive result of the same test: block 1.026 and kin 1.054 GMRES per Newton; the 3x3 block buys little over the kin
    preconditioner (CPU 62 vs 72 s); the preconditioner matters by a factor of 18-23 in CPU at large steps.

M4. Speed claims. K-c is a transient run (t=20 from the noisy initial state, rtol 1e-7, TRACK=0), single seed, noise-limited steps
    (~1000 steps/unit time), not the stationary-state workflow. At M=8 KR is 5x (rtol 1e-10) to 8x (rtol 1e-7) SLOWER than CVODE
    dense (7.22 vs 1.40 / 0.91 s); at M=16 3.4x (vs 90.5 s) to 4.9x (vs 132.4 s) faster. CVODE at rtol 1e-7 being slower than at
    rtol 1e-10 at M=16 is an anomaly (load/Newton failures), not explained. Real gain is for stationary states: G16 62.5 s
    (CVODE extrapolated hours, never run).

### Minor
m1. A3 was written "while G64a was running" at t~8000 and replaced the 2e5 cap by a CPU cap; A4 (at t=12000) replaced it by a
    hand stop at t>=15000. Neither can have changed the outcome (the gate was not met under any of the three rules, D1 runs went to
    t=40000). Hand stop at 15000 is registered (A4, committed 13:52 while the run was at t~12000).
m2. G64a V0=1.0 was started (13:24) and killed at t~100 to free a CPU slot (disclosed in A3); V0=0.25 was run (stationary).
    K-e2 allowed the extra V0 only "if the first finishes", so these are extras; V0=1.0 is simply missing.
m3. K-a3 tolerances are against the reviewer's PRINTED digits (2-4 digits); the passes (d_shift up to 4.7e-4 of 6e-4 at G16 V0=1)
    are rounding-level. The ETD note agrees (0.0463, 0.0767, 0.1065).
m4. K-e3: R64 used band-limited initial noise; the white-noise check was done only for R32 (|d shift| 9.5e-10). Declared in
    advance in PREREG. d(64-32)/d(32-16) = 0.251, i.e. second order in h (Richardson limit ~0.07683).
m5. K-b tests order at t=4 starting on the slaved manifold (no stiff transient); it does not probe stiff order reduction (the
    ETD note found exactly that for ETD). Error ratios are 3.56, 3.89, 3.98, 4.00 (second order), gate on the finest three.
m6. K-c exponent is still steepening: local slopes 1.89, 2.18, 2.35 (M 8-16, 16-32, 32-64). Steps differ by run
    (27933, 27550, 22143, 23093) because the geometry GM changes the physical problem with M; cost per step is the cleaner scaling
    (0.258, 0.973, 5.50, 26.9 ms/step: exponents 1.91, 2.50, 2.29). Load average 4-8 on 8 cores; the 3 repetitions are timing-only
    repeats of one deterministic run (identical step counts), not seeds.
m7. D2 log: CPU 610 s at t=300 while A6 says ~45 min wall, so the run was CPU-starved by about 4x; harmless but wall times in the
    amendments are not CPU times.
m8. `REPORT.md` was registered but not produced (A6 says so); summary.json is the only record. The ETD note quotes ke.jsonl.
m9. The code changed after the first runs only by a unit-test addition (3b) and an env-guarded debug print (commits 3716404 and 88839ce);
    default RTOL was changed 1e-6 -> 1e-7 in the 8187b9b..3716404 interval, the smoke runs at the old default were discarded (A1).

## Timeline check (git, +0200, 2026-10-11)
8187b9b 10:19:10 PREREG + code, before any trajectory. A1 3716404 10:23:58 (ka1_t4000.log 10:27, ka1.jsonl 10:32; ke_small 10:25): before
numbers. K-a/b/d result files 10:32-10:55. A2 4620ea5 10:56:09, after the K-d results (10:54-10:55), before K-d' (Kd2 logs 11:23-11:47).
Results committed 88839ce 11:49. A3 ffc6e41 13:34:41 (G64a V1.0 log 13:28; diagnostics scripts 13:34) before the D1 runs ended
(14:15, 14:21). A4 63d7489 13:52 (run at t~12000, D1 M32 running). A5 d9b3310 14:14. A6 + all results 03b9488 14:32 (PREREG mtime 14:22, D2 stop file 14:31).
Post-hoc amendments: none found; A2's disclosure of the K-d regime weakness is retrospective but precedes the extra tests.

## ETD note (docs/designs/EXCITON_FLUID_ETD_RESULTS.md Sec. 5)
Agrees with ke.jsonl: G8 residual 2e-9 (1.98e-9) at t=4700, 14.5 s CPU (14.46); G16 2e-9 (2.03e-9) at t=6800, 62.5 s (62.48);
omega V0=0.5 G16 0.5766598150851 (0.576659815085). Statement "KR reached a lower residual in about half the time of ETD" is
fair but compares stop criteria (KR stops at the first 100-unit checkpoint below 1e-8; ETD 1e-8 at t=13800, 125 s, different load).
The note does not mention G64a pulsation, K-d' failures, or the CVODE-faster-at-M=8 result; it should not claim more than "same order".

## (b) FACT SHEET (for a paper section)

Solver: two-stage SDIRK2 (L-stable, gamma=1-1/sqrt2), embedded 1st-order estimate, inexact Newton, GMRES(20) right-preconditioned
by Fourier-diagonal kinetic factor + pointwise 3x3 inverse; exact analytic Jv. Registered 2026-10-11 before the first trajectory.

| Gate | Registered criterion | Outcome | Numbers | Caveats |
|---|---|---|---|---|
| K-0 | FFT vs DFT <1e-12; jv vs FD <1e-7; jloc <1e-12 | PASS | FFT 6.4e-14 (M32), jv 3.1e-11, jloc 8.9e-16 | planted-bug jv differs 1.5e-2 |
| K-a1 | G8 V0=0.5 seed1 vs CVODE records at t=4000 (|domega|<=1e-6, |dn_c|,|dn_corner|<=1e-4, ...) and t=16000 (1e-7, 1e-5); CVODE rerun reproduces record; phase-aligned full state <=1e-5 | PASS | t=4000: domega 1.0e-8, dn_c 9.7e-6, dn_corner 2.2e-5, state 1.2e-6; CVODE rerun identical to record (diff 0); t=16000: domega 2e-11, dn_c 2.2e-9 | t=16000 uses rtol 1e-4 (A1 pseudo-transient); t=4000 run 417 CPU s (1.04e6 steps) vs CVODE rerun 121 s |
| K-a2 | G16 t=100 Omega=0.5, KR rtol 1e-7 vs CVODE 1e-10: rel L2<=1e-4, domega<=1e-5, dn_c<=1e-4; monotone in rtol | PASS | rel L2 9.1e-6 / 9.2e-7 / 1.2e-7 for rtol 1e-6 / 1e-7 / 1e-8; dn_c 1.1e-4 / 9.3e-6 / 4.1e-7; CPU 64 / 189 / 436 s vs CVODE 549 s | rtol 1e-6 exceeds the dn_c gate (gate applies to 1e-7) |
| K-a3 | reproduce reviewer's shifts and n_center (G16, G8) | PASS 6/6 | G16 shifts 0.04630, 0.07666, 0.10653; n_c 5.844, 2.377, 0.1000; G8 0.048776, 0.087610, 0.142123 | reference only has 2-4 printed digits |
| K-b | G8 fixed steps h=0.2..0.0125, t=4, ratios of 3 finest in [3,5] | PASS | err 1.06e-3, 2.98e-4, 7.66e-5, 1.92e-5, 4.81e-6; ratios 3.56, 3.89, 3.98, 4.00 | slaved initial state: no stiff transient |
| K-c | M=64, t=20 under 1 h CPU (A1: 2 h); report exponent | PASS (10.4 min) | median CPU 7.22, 26.81, 121.85, 620.9 s for M=8,16,32,64; exponent 2.15 (8-64), 2.27 (16-64); CVODE 1.40 s (M8), 90.5 s (M16) at rtol 1e-10 | transient, rtol 1e-7, 1 seed, 3 timing repeats, load 4-8/8; KR slower than CVODE at M=8 |
| K-d1 | badsign converges, same state (<=1e-6), >=1.5x GMRES | PASS (marginal) | state 2.4e-8; GMRES 168490 vs 111740 = 1.508 | none/kin same cost; regime where precond cannot matter (A2) |
| K-d2 | BUG=rhs differs from CVODE >1e-2 | PASS | rel L2 2.58 | |
| K-d3 | BUG=jac same state or error | PASS (vacuous) | 7.4e-12, identical counts | caught only by unit test |
| K-d4 | JV=fd same state | PASS | 3.2e-14, cost 6.5 vs 7.2 s | |
| K-d' (A2) | variants none/kin/badsign/jac/fd end at reference (<=1e-7, <=1e-6) or error; rhs differs >=1e-3 | 4 of 6 PASS, none and badsign FAIL | GMRES/Newton: block 1.03, kin 1.05, jac 1.03, fd 1.03, badsign 10.6, none 23.0; CPU 62, 72, 50, 55, 1142, 1415 s; d_shift none 9.9e-7 (resid 4.1e-6 at t=2e5), badsign 2.0e-7; rhs 8.4 | |
| K-e0 (A1) | rtol 1e-4 vs 1e-6 same stationary state (<=1e-7, <=1e-6) | PASS | d_shift 6.2e-9, d_nc 2.2e-7; CPU 62 vs 553 s | one case (G16 V0=0.5) |
| K-e1 | six runs residual <1e-7; seeds 2,3 shifts within 1e-6 | PASS | residual 1.8e-9 to 9.0e-9, t_reached 2900-11000; seed spread 5.0e-8 | stop rule 1e-8 checked every 100 units |
| K-e2 | G64a V0=0.5 residual <1e-7 in 2e5 units (A3: CPU cap; A4: stopped t>=15000) | NOT MET | residual 4.0e-3 to 2.0e-2 for t>2000; n_center 0.005 to 2.07; omega 0.5607-0.5745; 14 peaks, period ~969; D1 M32/M16 same to t=40000 (39/40 peaks, 966/956) | hand-stopped at 15000 CPU 7761 s; limit-cycle label untested independently (M1) |
| K-e2 extra | G64a V0=0.25 | stationary, resid 2.2e-9 at t=7300 | shift 0.044675, n_c 4.910 | V0=1.0 abandoned at t~100 |
| K-e3 | shift R64 closer to R32 than R32 to R16 | PASS | 0.0766598, 0.0767908, 0.0768237; diffs 1.31e-4, 3.29e-5 (ratio 4.0); white-noise R32 d_shift 9.5e-10 | R64 white noise not run |
| K-e4 | report shift vs L, no gate | measured | fixed sigma=3, L=16,32,64: 0.07666, 0.01513, 0.003537, slope -2.22 (pairs -2.34, -2.10); shift/box-avg 0.694, 0.548, 0.512. Fixed sigma/L, L=8,16,32: 0.08761, 0.07666, 0.06988 (slope -0.16, not size independent, falls 12.5% then 8.8%); V0=0.25 L=8,16,64: 0.04878, 0.04630, 0.04467 | L=64 at V0=0.5 pulsates: no shift; sampled omega mean 0.567 (shift ~0.067) not a stationary value |
| D1 (A3) | no gate: is pulsation present at M=32, 16? | present | see K-e2 | |
| D2 (A3,A5,A6) | no gate: rtol 1e-6, M=32 | stopped t=500 | follows D1 to 1.3e-2 in n_center for t<=500 | cannot show persistence at tighter rtol |

One-line claims the data support: second order in time; agrees with CVODE to 1e-6 (full state) at rtol 1e-7; reproduces the CVODE
G8 records at t=4000 and t=16000 to the registered tolerances and the reviewer's digits; stationary G8/G16/G32 states to residual <1e-7
in 15-600 CPU s with seed independence 5e-8; grid-refinement second order in h; cost per step grows ~M^2.2.
Claims it does NOT support: speed-up over CVODE at M=8 (opposite), stability of G64a stationary state, "limit cycle" as established.
