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

(none yet)
