# Exciton fluids, exponential integrator (ETDRK4) for the driven-dissipative model: pre-registration

Date 2026-10-11. **Written and committed BEFORE any run of the new integrator.** At the time of writing nothing exists in
`exploration/exciton/rust/qf-exciton-etd/` except this design; no trajectory, no timing, no step-size limit has been computed.

Origin: peer-review response `EXCITON_FLUID_GATED_PEER_REVIEW_RESPONSE.md` §2.3 ("ETDRK4 ... worthwhile comparison; the nonlinear
rate term R|psi|^2 n_R is not in the linear part, so ETD is not unconditionally better ... when the gate drives R|psi|^2 close
to gamma_R"). Model, parameters and the records to be compared with: `EXCITON_FLUID_PHASE3_PREREG.md`,
`exploration/exciton/rust/qf-exciton-p1/src/bin/dd.rs`, `exploration/exciton/results/phase3/`. Not touched here: the Lean, Wigner,
open-boundary and Krylov packages of the sibling workflow (read-only use of their published result files only).

## 1. Integrator (fixed design)

**Model** (exactly dd.rs): `i psi_t = [-1/2 lap + V + g|psi|^2 + g_R n_R + i/2 (R n_R - gamma)] psi`,
`n_R,t = P - (gamma_R + R|psi|^2) n_R`, `g = 0.04, g_R = 1, gamma = 0.1, gamma_R = 200, R = 1, P = 21`; periodic `M x M` grid,
lattice spacing `dx = 1` (so `L = M`) except where a gate says otherwise; spectral Laplacian with the dd.rs wavenumbers
(`i > M/2 -> i - M`, Nyquist positive); Gaussian gate `V0 exp(-d^2/(2 sigma^2))`, centre node `(M/2, M/2)`, minimum image;
initial state of dd.rs (`state_uniform`: SplitMix64 call order re, im, then `n_R`), integration in the frame rotating at
`omega_f = 0.5` unless stated, all observables (mean n, mean n_R, std n, omega, relative residual, budget, n_center, n_corner)
computed as in dd.rs `observe` on the laboratory-frame equation. The step is gauge covariant and the frame is built in as an exact
phase rotation (see below).

**Splitting.** State `u = (psi_hat, nR_hat)`, Fourier space. Linear part, diagonal:
`L_psi(k) = -i k^2/2 + i omega_f` (the `i omega_f` is the rotating frame and is part of the registered flow of dd.rs, treated
exactly), `L_R = -gamma_R`. Nonlinear part, pseudo-spectral in real space (no dealiasing, like dd.rs):
`N_psi = [-i(V + g|psi|^2 + g_R n_R) + (R_psi n_R - gamma)/2] psi`, `N_R = P - R|psi|^2 n_R`. (`-gamma/2` is in `N`, as the
assignment names only the kinetic and reservoir parts as linear.) `n_R` is stored as a complex field with Hermitian spectrum; its real
space value is the real part.

**Schemes** (all with one step size `h`, constant, no error control):
* `ETD`: ETDRK4 of Cox and Matthews (J. Comput. Phys. 176, 430, 2002) with the contour-integral evaluation of Kassam and Trefethen
  (SIAM J. Sci. Comput. 26, 1214, 2005): the coefficients `Q, f1, f2, f3` (the `h`-scaled phi-function combinations) are the mean of
  the integrand over 32 points of a circle of radius 1 around `h L(k)`, evaluated mode by mode. Stages
  `a = E2 u + Q N(u)`, `b = E2 u + Q N(a)`, `c = E2 a + Q(2N(b) - N(u))`, `u+ = E u + f1 N(u) + 2 f2 (N(a)+N(b)) + f3 N(c)`,
  `E = e^{hL}`, `E2 = e^{hL/2}`.
* `LAW`: Lawson (integrating factor) RK4, linear part `L` as above (comparison only).
* `LAWK`: Lawson RK4 with the **kinetic part only** in the exponential, i.e. `L_R = 0` and `-gamma_R n_R` in `N_R` (the variant the
  assignment asks for as a comparison).
* `ETDK`: ETDRK4 with the kinetic part only (extra comparison to separate the effect of the reservoir decay in `L`).

**Implementation choice.** Pure Rust with its own radix-2 FFT (no dependency for the integrator itself). The pinned
`cvode`/`nvector` crates (path dependency, rusty-SUNDIALS v11.6.0, tree `996aaf0706e1` = commit `5db8041`) are used only for the
CVODE (BDF, dense) cross-checks, with a right-hand side re-written in real variables (the dd.rs layout) in the crate. The pinned
tree is not modified. One compute thread per run, two jobs at most.

## 2. Gates

Error metric (that of dd.rs D-e): `E = max|y - y_ref| / ||y_ref||_2` over the `3 M^2` real unknowns (rotating frame, same frame in
both). The reference uncertainty `e_ref` is the same metric between the CVODE references at `rtol 1e-12, atol 1e-14` and
`rtol 1e-11, atol 1e-13`.

**T-a (steady states).** `V = 0`, `P = 21`, `h = 0.1`, `ETD`, frame 0.5, `t = 12000` (the slowest decaying mode is `2.4e-3`,
`e^{-28} = 4e-13`), `M = 8` seeds 1..10 and `M = 16` seeds 1..3. Pass: `|mean n - 10| / 10`, `|mean n_R - 0.1| / 0.1`,
`std n / 10`, `|omega - 0.5|` all `<= 1e-10`. Below threshold (`P = 16`, `psi = 0.5(1 + 1e-3 xi)`, `n_R = 0`, `t = 4000`, `M = 8`,
seeds 1..10): `max|psi| <= 1e-6`, `|n_R - 0.08| / 0.08 <= 1e-8`. (The fixed point of ETDRK4 is exact for a constant
state; the gate tests the code, not the order.)

**T-b (temporal order).** `V0 = 0.5`, `P = 21`, seed 1, frame 0.5, uniform state plus `1e-3` noise, `t_end = 10`;
geometries `G8` (`M = 8`, `sigma = 1.5`) and `G16` (`M = 16`, `sigma = 3`); `h in {0.2, 0.1, 0.05, 0.025, 0.0125}`; `ETD`.
Reference: pinned CVODE at `rtol 1e-12, atol 1e-14`. Pass: every successive ratio `E(2h)/E(h)` whose smaller error is at least
`50 e_ref` lies in `[12, 20]`, and at least three such ratios exist for each geometry. (Report: `LAW`, `LAWK`, `ETDK` orders, not
gated; `LAWK` uses `h in {0.01, 0.005, 0.0025, 0.00125}` because of its stability limit.)

**T-c (stability limit, measured).** Geometry `G8`, `V0 = 0.5`, seed 1, `t = 200`, uniform-plus-noise start. Reference run:
`ETD` with `h = 0.0125`. A run at step `h` is **stable** if all values are finite and `E <= 0.05` against that reference at
`t = 200`; **blown up** if non-finite or `max|psi|^2 > 1e4`; otherwise "inaccurate". Scan `h = 0.01 * 2^{j/4}`,
`j = 0..32` (to `h = 2.56`), schemes `ETD`, `LAW`, `LAWK`, `ETDK`. Report the set of failing `h`, `h_first` = smallest failing step,
and the largest stable step below it. Dependence sweeps (each at `M = 8` unless stated, same test, `ETD` and `LAWK`):
(i) uniform density `n0 in {10, 50, 200, 1000}` via `P = 0.1 (n0 + 200)`, frame `g n0 + 0.1`, with the nonlinear rate
`(R + g) n0` and the ratio `R n0 / gamma_R`; (ii) lattice spacing `dx in {1, 0.5, 0.25}` (`L = 8 dx`, `sigma = 1.5 dx`, this changes
the model's spacing, it is a probe, not a record), maximum kinetic frequency `pi^2/dx^2`; (iii) `M in {8, 16, 32}`, `dx = 1`.
*Two competing hypotheses, registered:* **H-N** the limit is set by the nonlinear rate: `h_first * (R + g) n0` is within a factor 3
of constant across (i), and `h_first` is independent of `dx` within a factor 2 across (ii); **H-K** the limit is set by the
kinetic frequency (resonance of the exact phase with the step, `h * pi^2/dx^2 ~ pi`): `h_first * pi^2/dx^2` within a factor 3 of
constant across (ii). Either, both or neither may hold; the result is stated as measured. *Prediction on the registered
point:* `ETD` at `n0 = 10, dx = 1` has `h_first >= 5 * 0.01707` (the IMEX module's limit of D-e) and `LAWK` has
`h_first <= 2.785/gamma_R * 1.5 = 0.021` (RK4 real-axis limit for the explicit decay). The comparison with BDF is a cost comparison,
not a step limit (adaptive BDF has none in this sense): see T-g.

**T-d (agreement with the registered records).** (i) `G8`, `V0 in {0, 0.25, 0.5, 1.0}`, seeds 1..10, `h = 0.05`, `ETD`, `t = 4000`,
against `results/phase3/d_V*.jsonl` (same initial states by construction): for every seed `|d omega| <= 1e-6`,
`|d n_center|, |d n_corner| <= 1e-4`, relative `d mean_n, d mean_nr <= 1e-6`, `|d std_n| <= 1e-5` (the tolerances are those the
Krylov package registered for the same records: they are tied to how much the CVODE states themselves differ from the exact
trajectory). (ii) `G8`, seed 1, `t = 16000`, against `results/phase3/exploratory/d_T16000*.jsonl` (`V0 = 0.5`: `omega =
0.587610, n_center = 4.5808`): `|d omega| <= 1e-7`, `|d n_center|, |d n_corner| <= 1e-5`, relative `d mean_n, d mean_nr <=
1e-7`. (iii) `G16` (`M = 16`, `sigma = 3`, the registered geometry), `V0 in {0.25, 0.5, 1.0}`, seed 1, `h = 0.05`, run to
the D-d residual `<= 1e-8` (cap `t = 150000`), compared with the printed values of the independent solution quoted in
`EXCITON_FLUID_GATED_REVIEW_2026-10-11.md` (M1): shifts `omega - 0.5 = 0.046, 0.077, 0.107` and `n_center = 5.84, 2.38, 0.10`:
`|d shift| <= 6e-4`, `|d n_center| <= 0.01` (`0.005` for `V0 = 1`; the printed digits). No CVODE record exists at `G16`
for these horizons (cost: hours); a comparison with the Krylov package's files is made only if they exist when the run ends and is
labelled as such.

**T-e (cost).** (i) wall time per step of `ETD` versus `M in {8, 16, 32, 64, 128}` (`dx = 1`, `V0 = 0.5`, `sigma = 3M/16`,
`h = 0.05`, 200 steps after 20 warm-up steps, best of 3, release build, one thread): pass if the per-step time ratio between
`M` and `M = 8` divided by the ratio of `M^2 log2(M^2)` lies in `[0.5, 2]` for every `M` (FFT scaling). (ii) wall time to reach the
D-d stationarity residual `1e-7` (residual evaluated every 50 time units) at `G8, V0 = 0.5, seed 1`, `ETD h = 0.1`, versus a CVODE
(dense, rtol 1e-10, atol 1e-12, the dd.rs flow) rerun on the same machine in the same session, and the registered numbers of the
records (`d_V0.5.jsonl`: 182.7 s to `t = 4000`, residual 7.6e-5, not reaching 1e-7; `exploratory/`: 464.8 s to `t = 16000`,
residual 1e-8). Hypothesis (not gated): `ETD` is at least 10 times faster than CVODE dense at `G8`. At `G16` the CVODE time is not
re-measured (the Phase 3 record is 43 ms per step, 2854 steps for `t = 20` at 1e-10, i.e. about 6 s per unit time);
the `ETD` time to residual `1e-7` is reported and the CVODE figure is an extrapolation, labelled as such.

**T-f (planted bugs, and what ETD cannot do).** (i) Bugs, each run through the gate named: **B1** `R` doubled in the `psi`
equation only (the D-g bug): must violate T-a (above); **B2** the final combination uses `f2` where `f3` belongs: must violate
T-b (ratios outside `[12, 20]`); **B3** the kinetic factor `k^2/2` replaced by `k^2/4` in `L` only: must violate T-b (error not
decreasing with `h`) and T-d(i). A bug is "caught" if the named gate fails. A correct run passes all three gates (T-a, T-b, T-d).
(ii) The term `R|psi|^2 n_R` is not in `L`: for `n0 in {10, 50, 200, 1000}` (`R n0 / gamma_R = 0.05, 0.25, 1, 5`), `G8`-like grid
(`M = 8`, `V0 = 0.5`, `sigma = 1.5`), seed 1, `t = 2`, error `E` of `ETD` and `LAW` and `LAWK` at `h in {0.02, 0.01, 0.005}`
against CVODE `rtol 1e-12`, and the empirical error constant `E/h^4`. No threshold: this quantifies the loss of accuracy; if the
error constant grows with `R n0` as `(R n0)^p` the exponent `p` is stated, not assumed.

**T-g (work-precision, reported, not gated).** `G8`, `V0 = 0.5`, seed 1, `t = 20`: for `ETD` at `h in {0.2, 0.1, 0.05, 0.025,
0.0125}` and for CVODE at `rtol in {1e-4, 1e-6, 1e-8, 1e-10}` (`atol = 1e-2 rtol`): `E`, steps, right-hand-side evaluations if
available, wall time. This is the place where `ETD` may be worse than BDF; stated whichever way it comes out.

## 3. What is not claimed

No claim about excitons or any experiment; the model is the dimensionless one of Phase 3. No claim that ETDRK4 is the best
integrator for the problem: it is compared with CVODE dense (and, when the files exist, the Krylov SDIRK2) on one parameter set,
on grids up to `128 x 128` for cost only, with a hand-chosen contour (32 points, radius 1). A result in which `ETD` is worse is a
result.

## 4. Amendments

(none yet; every deviation after a result is seen is a dated amendment below)
