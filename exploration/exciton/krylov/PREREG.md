# Pre-registration: matrix-free Newton-Krylov solver for the driven-dissipative exciton GPE (gates K-a ... K-e)

Date 2026-10-11. Written and committed BEFORE the first trajectory of the new solver was run. What exists at this point: the code
(`qf-exciton-kr/`: `fft.rs`, `model.rs`, `sdirk.rs`, `bin/kr.rs`) and its unit test `kr test` (FFT against the naive DFT, exact uniform
fixed point, analytic Jacobian action against a central difference, 3x3 block against the Jacobian action): all passed
(max FFT difference 6e-14, `jv` relative 3e-11, `jloc` 9e-16). No trajectory, no timing, no stationary state has been computed.

Background: `paper/exciton_fluid_gated.tex` Sec. 4 (Cost), `docs/designs/EXCITON_FLUID_PHASE3_PREREG.md` (D-d), records in
`exploration/exciton/results/phase3/`, review `docs/designs/EXCITON_FLUID_GATED_REVIEW_2026-10-11.md` (M1).

## 1. The solver (fixed design)

Same equations and parameters as `dd.rs` (g = 0.04, g_R = 1, gamma = 0.1, gamma_R = 200, R = 1, P = 21; Gaussian gate centred on the
node (M/2, M/2), minimum image; spectral Laplacian with the dd.rs wavenumber convention, Nyquist frequency positive).
M x M periodic grid, box L, spacing h = L/M, any power-of-two M (radix-2 FFT). Right-hand side in the frame rotating at Omega.

* Scheme: two-stage SDIRK2 (Alexander, gamma = 1 - 1/sqrt 2, L-stable, stiffly accurate), embedded first-order estimate
  E = Y2 - y - h f(Y1), controller step factor 0.9 err^(-1/2) clamped to [0.2, 4], error norm weighted RMS with
  weights 1/(rtol |y| + atol), initial step 1e-3.
* Stage solves: inexact Newton (wrms(delta) < 0.05, at most 8 iterations; step quartered on failure), GMRES(20) with at most 2 restarts
  from `sundials_core::gmres::gmres_preconditioned` of the pinned tree (v11.6.0, 5db8041, not modified), right preconditioning,
  absolute tolerance 0.05 |G|_2. Jacobian-vector product: exact analytic action (default) or directional difference (`JV=fd`).
* Preconditioner (`PREC=block`, default): Fourier-diagonal factor (1 + i s k^2/2)^-1 for psi, followed by the exact pointwise 3x3
  inverse (I - s J_loc)^-1 (J_loc = every term of the Jacobian except the kinetic one), s = h gamma. `PREC=kin`: Fourier factor
  and the pointwise reservoir factor (1 + s (gamma_R + R|psi|^2))^-1 only (the structure named in the assignment). `PREC=none`.
  `PREC=badsign`: block with s -> -s.
* `TRACK=1` (stationarity runs and K-a observables): at the end of every chunk of 100 time units the frame frequency Omega is
  set to the fitted frequency omega of the state. This is a relabelling of the frame (a global phase) and does not change the physics;
  all reported observables (|psi|, n_R, omega, residual) are frame invariant. Runs compared dynamically (K-a2, K-b) use a fixed Omega = 0.5.
* CVODE dense (pinned crate) is used only for M = 8 and 16, as comparator. The kr binary refuses CVODE for M >= 32.
* Initial state, all runs: `psi = sqrt(10) (1 + 1e-3 xi)` + `1e-3 sqrt(10) i xi'`, `n_R = 0.1`, xi uniform in [-1, 1] pointwise,
  SplitMix64(seed) with the dd.rs call order, so for M = 8 the initial state is bit-identical to the D-d records.
* Default tolerances of all KR runs: rtol = 1e-7, atol = 1e-10 (K-b: see there). CVODE comparators: rtol = 1e-10, atol = 1e-12 (as D-d).
* Geometries. G8: M = 8, L = 8, sigma = 1.5 (the records). G16: M = 16, L = 16, sigma = 3 (the registered geometry of D-d,
  review M1). G32: M = 32, L = 32, sigma = 6. G64a: M = 64, L = 64, sigma = 12 (h = 1, same sigma/L = 0.1875).
  R16/32/64: L = 16, sigma = 3, M = 16, 32, 64 (h = 1, 0.5, 0.25: grid refinement of the kinetic term).
  F16/32/64: sigma = 3, h = 1, L = M = 16, 32, 64 (fixed gate, growing box).
* Observables: those of D-d (mean n, mean n_R, std n, omega, relative residual after fitting omega, n_center, n_corner, max |j|,
  budget residual) with the shift = omega - 0.5.

## 2. Gates

**K-0 (unit test, done, recorded above).** FFT vs DFT < 1e-12; |rhs| at the uniform state < 1e-12; `jv` vs central difference < 1e-7;
`jloc` vs `jv` < 1e-12.

**K-a (agreement with the CVODE records).**
* K-a1: G8, V0 = 0.5, seed 1, TRACK=1, run to t = 4000 and to t = 16000, compared with `results/phase3/d_V0.5.jsonl` (seed 1,
  t = 4000) and `results/phase3/exploratory/d_T16000.jsonl` (seed 1, t = 16000). Tolerances are tied to how much those CVODE states
  themselves still change between t = 4000 and t = 16000 (omega 9.6e-6, n_center 2.1e-3): at t = 4000 |d omega| <= 1e-6,
  |d n_center|, |d n_corner| <= 1e-4, |d std_n| <= 1e-5, relative d mean_n, d mean_nr <= 1e-6; at t = 16000 (stationary, resid
  1e-8 in the record) |d omega| <= 1e-7, |d n_center|, |d n_corner| <= 1e-5, relative d mean_n, d mean_nr <= 1e-7.
  Plus a CVODE rerun here (G8, seed 1, t = 4000, rtol 1e-10, atol 1e-12, state dumped) must reproduce the record to the same
  tolerances (check of the comparator itself), and the phase-aligned relative L2 difference of the full states KR vs CVODE-rerun
  <= 1e-5.
* K-a2: G16, V0 = 0.5, seed 1, Omega = 0.5 fixed, t = 100, KR (rtol 1e-7) vs CVODE dense (rtol 1e-10): relative L2 difference of the
  full state <= 1e-4, |d omega| <= 1e-5, |d n_center| <= 1e-4. KR also at rtol 1e-6 and 1e-8 (reported; the difference must decrease
  monotonically with rtol).
* K-a3 (stationary states, registered geometry; see K-e): reproduce the reviewer's solution (review M1, independent Newton solver):
  G16 shifts 0.046, 0.077, 0.107 and central densities 5.84, 2.38, 0.10 for V0 = 0.25, 0.5, 1.0, to the printed digits:
  |d shift| <= 6e-4, |d n_center| <= 0.01 (0.005 for V0 = 1). And G8 (0.04878, 0.08761, 0.14212; 7.068, 4.581, 1.493 from the same
  review table): |d shift| <= 2e-4, |d n_center| <= 5e-3.

**K-b (temporal order).** G8, V0 = 0.5, seed 1, Omega = 0.5 fixed, fixed steps h in {0.2, 0.1, 0.05, 0.025, 0.0125}, no step control,
t = 4 (the initial n_R = 0.1 is the slaved value, so no stiff transient), `RTOL=1e-12 ATOL=1e-14 ETA=1e-3 MAXNEWTON=20 KAPPA=0.05`,
reference CVODE dense rtol 1e-12, atol 1e-14, same t. Error = relative L2 of the full state. Gate: each of the three finest successive ratios
e(h)/e(h/2) in [3, 5].

**K-c (cost versus M).** KR with defaults, TRACK=0, Omega = 0.5, seed 1, V0 = 0.5, geometry GM (M = L, sigma = 0.1875 L) for
M = 8, 16, 32, 64, simulated time t = 20, three repetitions, median CPU time (from /proc/self/stat; wall time also recorded; machine
load recorded, 8 cores shared). CVODE dense for M = 8 and 16, t = 20, at rtol 1e-10/atol 1e-12 and at rtol 1e-7/atol 1e-10. Reported: CPU seconds per unit simulated time, steps,
GMRES iterations per stage, exponent p of seconds ~ M^p (least squares on log-log, M = 8..64, and separately 16..64). Gate: the
M = 64 run finishes t = 20 in under 1 hour CPU. No speed-up gate is asserted; the comparison with CVODE is reported as measured
(quoted baselines: 1.4 s for t = 20 at M = 8, 43 ms/step at M = 16).

**K-d (planted bugs).** G8, V0 = 0.5, seed 1, Omega = 0.5, t = 20, rtol 1e-7; reference = CVODE dense rtol 1e-10 at t = 20 and the
correct KR run.
* K-d1 `PREC=badsign`: must converge (no error) to the same state as the correct KR run (relative L2 <= 1e-6) with at least 1.5 x the
  GMRES iterations of `PREC=block`. `PREC=none` and `PREC=kin` are run and reported (no gate).
* K-d2 `BUG=rhs` (R doubled in the psi equation only, the D-g bug): the relative L2 difference to CVODE must exceed 1e-2, and the
  K-a2 gate (<= 1e-4) must fail. That is, the cross-check detects it.
* K-d3 `BUG=jac` (wrong sign of the n_R coupling in the analytic Jacobian action): outcome is either the same state as the correct
  run (relative L2 <= 1e-6, with more Newton or GMRES work) or an explicit non-null `error`; a silently different state fails the gate.
* K-d4 `JV=fd`: same state (<= 1e-6 relative L2), cost reported.

**K-e (stationary states to residual < 1e-7, scaling).** `TRACK=1`, stop when the D-d relative residual < 1e-8 (so that the
D-d criterion 1e-7 holds with margin; the record is the final state), maximum simulated time 2e5, seed 1 unless stated.
* K-e1: G16 for V0 in {0.25, 0.5, 1.0}; G8 for V0 in {0.25, 0.5, 1.0}. Gate: final residual < 1e-7 for all six; then K-a3.
  Seeds 2 and 3 for G16, V0 = 0.5 (seed independence: |d shift| <= 1e-6).
* K-e2: G64a, V0 = 0.5 (and V0 = 0.25, 1.0 only if the first finishes in < 6 h CPU). Gate: final residual < 1e-7 in at most 2e5 time
  units. Reported: shift, n_center, n_corner, the shift relative to the box average V0 2 pi sigma^2 / L^2 of the gate.
* K-e3 (grid refinement of the kinetic term): R16, R32, R64 at V0 = 0.5. Gate: the shift at R64 differs from R32 by less than the
  difference R32 vs R16 (monotone convergence), reported with the three numbers. For R32, R64 the initial noise is band-limited to
  |k_x|, |k_y| <= pi (the Nyquist band of the h = 1 grid; `NOISEBAND=3.14159`), declared in advance as the only change of the initial state
  because white noise at the h = 0.25 Nyquist (omega ~ 158) would make the controller resolve neutral modes whose amplitude is
  irrelevant to the stationary state; if affordable one white-noise R32 run is added to check that the stationary state is identical
  (|d shift| <= 1e-6).
* K-e4 (size dependence of the gate shift): families F16/F32/F64 (fixed sigma = 3) and G8/G16/G32/G64a (sigma/L fixed), V0 = 0.5.
  Reported: shift versus L and the log-log slope for each family. Reading registered in advance: for a fixed gate the shift falls like the box average
  (slope near -2, review M1); for fixed sigma/L the box average is size independent. Whether either holds is what is measured; no gate.

## 3. Rules

Deviations after the first run are written as dated amendments below, never edited above. Failed gates are reported as failed.
Results go in `results/` as JSON lines; the report is `REPORT.md`. KR runs are single-threaded; at most two run concurrently; the pinned
tree is untouched.

## Amendments

**A1 (2026-10-11, after the first smoke runs and the start of K-a1 t = 4000, before any K-a/K-b/K-c/K-d/K-e number was
produced).** Measured cost of the registered tolerance: with the first-order embedded estimate and rtol = 1e-7 the step is limited by
the neutral high-wavenumber noise (omega up to k^2/2 ~ 10 at h = 1) to h ~ 1e-3 .. 3e-3, i.e. about 1000 steps per unit time, 0.4 ms per step on G8
(t = 4000 takes about 25 min, t = 16000 on G16 would take hours). Two smoke runs of G8 and G16 with t = 20 at rtol = 1e-6/atol = 1e-9 (the
accidental first default of the driver; not the registered one) were discarded and are not used anywhere. Changes: (1) K-a1 t = 4000, K-a2, K-b, K-c, K-d
stay at rtol 1e-7/atol 1e-10 as registered. (2) The stationary-state runs (K-a1 at t = 16000, K-a3, all of K-e) use pseudo-transient
tolerances rtol = 1e-4, atol = 1e-7, `TRACK=1`: an implicit scheme has the exact fixed points of the right-hand side, so the stationary state does not depend on
the time accuracy of the approach; this is a hypothesis and is tested, not assumed: G16, V0 = 0.5, seed 1 is also run at rtol = 1e-6/atol = 1e-9
and the final states must agree to |d shift| <= 1e-7, |d n_center| <= 1e-6 (gate K-e0). (3) The wall-time limit of K-c M = 64 becomes 2 h CPU
(the same 1 h gate was a guess made before any step had been timed).

**A2 (2026-10-11, after the K-d results at t = 20 were evaluated, before any run of the extra tests below).** The registered K-d runs at
t = 20, rtol 1e-7 passed all four gates (d1: GMRES 168490 vs 111740 = 1.508x, just above the 1.5x threshold; d2: relative L2 to CVODE
2.58; d3: identical state, 7e-12; d4: 3e-14), but they do not test the preconditioner or the Jacobian action in the regime they are
for: with steps h ~ 1e-3 the Newton matrix I - s J is within 1e-3 of the identity and GMRES needs one iteration for every Newton iteration
with any preconditioner (GMRES iterations equal Newton iterations for `none`, `kin` and `block`), and the wrong-sign Jacobian
(`BUG=jac`) gave bit-for-bit the same counts as the correct one. Those four gates were therefore passed in a regime where they could
hardly fail and that is disclosed here. Extra test K-d' (new gates, same seed and parameters as the reference stationary run
`Ke_G16_V0.5_s1`, rtol 1e-4, atol 1e-7, `TRACK=1`, stop at residual 1e-8, steps grow to h ~ 10): variants `PREC=none`, `kin`, `badsign`, `BUG=jac`, `JV=fd`,
`BUG=rhs`. Gates: every variant except `BUG=rhs` ends at the reference state (|d shift| <= 1e-7, |d n_center| <= 1e-6) or reports a
non-null error; `BUG=rhs` ends at a state with |d shift| >= 1e-3 relative to the reference or reports an error. Reported (no gate): Newton
iterations, GMRES iterations per Newton iteration, CPU seconds, step counts for each variant, which show whether the structured
preconditioner matters at large steps.

**A3 (2026-10-11, written while G64a V0 = 0.5 was running, after 8000 of its time units, before it finished and before the diagnostics below were run).**
G64a, V0 = 0.5 (K-e2) shows no approach to a stationary state over t = 8000: the relative residual stays between 4e-3 and 1.7e-2 and the central
density oscillates between 0.01 and 2.4 with a period of about 1000 time units (log `results/ke_Ke_G64a_V0.5_s1.log`). The gate
"residual < 1e-7 within 2e5 time units" cannot be reached inside any CPU budget at this rate (about 800 time units per 10 minutes). Changes: (1) the 2e5 time
cap is replaced by a CPU cap of 4 h for this run; if the residual criterion is not met by then the K-e2 gate is reported as NOT MET, with the
oscillation described, not as a stationary state; (2) the extra G64a runs for V0 = 0.25 (finished, stationary) and V0 = 1.0 (started, stopped
by me at t ~ 100 to free a CPU slot, no result) were launched outside the "if the first finishes" condition of K-e2 and are reported as extras;
(3) diagnostics to separate physics from numerics, run with the G64a physical geometry (L = 64, sigma = 12, V0 = 0.5, seed 1, rtol 1e-4/atol 1e-7, TRACK=1,
stop at residual 1e-8 or t = 4e4): D1 on M = 32 (h = 2) and M = 16 (h = 4), D2 on M = 32 at rtol 1e-6/atol 1e-9 (t cap 2e4). No gate is attached; what is
read from them is only whether the slow oscillation of the central density and the non-decaying residual are present at other resolutions and tolerances.

**A4 (2026-10-11, G64a V0 = 0.5 at t = 12000, CPU 6945 s).** The central density of G64a V0 = 0.5 has now peaked 11 times with a period of
about 975 time units and an amplitude that does not decay (peaks at t = 1400, 2300, 3300, ..., 11100; residual 4e-3..1.5e-2 throughout). The same
pulsation is present at M = 32 and rtol 1e-4 (diagnostic D1, t = 10200: residual 1.1e-2). A process killed at the CPU cap writes no final record, and more cycles would not
change the reading, so the 4 h CPU cap of A3 is replaced by: the run is stopped by me at t >= 15000 (about 14 cycles); its record is the progress log
(t, residual, omega, n_center every 100 time units), no final state file exists. K-e2 is reported as NOT MET.

**A5 (2026-10-11, D2 at t = 100 after 141 CPU s).** The tolerance diagnostic D2 (M = 32, rtol 1e-6) costs about 1.4 CPU s per time unit at the start, so its t
cap of 2e4 is not affordable; it is stopped by me at t >= 2500 (two pulsation periods of the rtol-1e-4 runs: peaks at t ~ 1400 and 2300), and its record is the
progress log. Reading: the pulsation is counted as tolerance independent if the central density again peaks within +-150 time units of 1400 and 2300 with a similar range.
