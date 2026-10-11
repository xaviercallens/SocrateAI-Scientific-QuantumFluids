# Exciton fluids, ETDRK4 for the driven-dissipative model: results

Date 2026-10-11. Pre-registration: `EXCITON_FLUID_ETD_PREREG.md` (committed before the first run; amendments A1-A3 are dated and
each was committed before the runs it announces). Code: `exploration/exciton/rust/qf-exciton-etd/` (pure-Rust radix-2 FFT, own
ETDRK4; the pinned rusty-SUNDIALS v11.6.0 `cvode`/`nvector` crates, commit `5db8041`, path dependency, are used only for the CVODE
comparisons; the pinned tree is unmodified). Raw results: `exploration/exciton/rust/qf-exciton-etd/results/*.jsonl`. All runs on a
machine whose load average was 4-11 on 8 cores (sibling workflow running), one thread per run; wall times are therefore
upper-ish and noisy (the same CVODE configuration was timed at 1.8, 2.2 and 2.5 s).

## Summary, one line per gate

| gate | outcome | one-line reason |
|---|---|---|
| unit test | passed | FFT vs naive DFT 2.7e-15; contour phi-functions vs direct formula 1e-17; uniform fixed point kept to 2e-12 over 1000 steps; (u(h)-u)/h vs dd.rs-type right-hand side linear in h |
| T-a steady states | **PASS** | above: 13 of 13 runs, worst `\|n-10\|/10` 2.8e-13, `\|omega-0.5\|` 1.1e-13; below: 10 of 10, `max\|psi\|` 2e-18 |
| T-b order 4 | **FAIL** (both `G8`, `G16`) | ratios 2.2, 2.9, 4.5, 7.2 not in [12, 20]; stiff-order reduction, demonstrated by control |
| T-c stability limit | measured; both registered hypotheses fail as stated | limit 0.54-0.64 at the registered point (hits a kinetic resonance), 0.0034 at `R n / gamma_R = 5` |
| T-d(i) records, `t = 4000`, `h = 0.05` | **FAIL** for `V0 = 0.5, 1.0` (0 of 10 seeds each), pass for `V0 = 0, 0.25` | difference is ETD time-step error: converges to the record as `h -> 0` |
| T-d(ii) records, `t = 16000` | 2 of 4 pass (`V0 = 0, 0.25`); `V0 = 0.5, 1.0` fail by factor 2-3.6 on relative mean n | at `h = 0.0125` the `V0 = 0.5` state agrees to 5e-9 |
| T-d(iii) `G16` vs reviewer's digits | **PASS** 3 of 3 | shifts 0.0463, 0.0767, 0.1065 vs 0.046, 0.077, 0.107; `n_center` 5.844, 2.377, 0.1000 vs 5.84, 2.38, 0.10 |
| T-e(i) FFT scaling | **PASS** | cost / (`M^2 log2 M^2`) = 1.00, 0.81, 0.73, 0.71, 0.77 for `M = 8 ... 128` |
| T-e(ii) time to residual 1e-7, `G8` | ETD 7.7 s, CVODE 227 s (29x), same stationarity time `t = 7400` | hypothesis ">= 10x" met on this machine/load |
| T-f(i) planted bugs | B1, B2, B3 all caught (B2 only by the non-stiff control) | correct code fails T-b, so the registered B2 gate alone did not discriminate |
| T-f(ii) R n n_R not in L | quantified | error at fixed `h` grows weakly with density; the stability bound is what bites |
| T-g work-precision | ETD cheaper above `E ~ 1e-9`, comparable at `E ~ 1e-10` | see Sec. 6 |

## 1. T-a (steady states)

`V = 0`, `P = 21`, `h = 0.1`, `t = 12000`, frame 0.5, `M = 8` seeds 1-10 and `M = 16` seeds 1-3: `|mean n - 10|/10 <= 2.8e-13`,
`|mean n_R - 0.1|/0.1 <= 1.3e-14`, `std n / 10 <= 2.9e-15`, `|omega - 0.5| <= 1.1e-13` (gate 1e-10). Below threshold
(`P = 16`, `t = 4000`, seeds 1-10): `max|psi| <= 2.1e-18`, `|n_R - 0.08|/0.08 <= 5.2e-16`. This tests the code, not the order: a
constant state is a fixed point of ETDRK4 by construction (the unit test checks this).

## 2. T-b (temporal order): failed, and why

`G8`, `t = 10`, error `E` (max-norm over the 3M^2 unknowns divided by `||y_ref||_2`) against CVODE at rtol 1e-12
(`e_ref = 3.8e-10` for `G8`, `8.4e-11` for `G16`):

| `h` | 0.2 | 0.1 | 0.05 | 0.025 | 0.0125 |
|---|---|---|---|---|---|
| ETD `G8` | 4.7e-5 | 2.1e-5 | 7.2e-6 | 1.6e-6 | 2.2e-7 |
| ETD `G16` | 1.1e-5 | 5.3e-6 | 1.9e-6 | 4.2e-7 | 5.9e-8 |
| KROG `G8` (exploratory) | 9.1e-6 | 1.5e-6 | 3.6e-7 | 9.2e-8 | 1.5e-8 |
| KROG `G16` | 8.5e-6 | 1.5e-6 | 3.3e-7 | 6.6e-8 | 9.5e-9 |

Successive ratios: ETD `G8` 2.25, 2.90, 4.49, 7.22; `G16` 1.97, 2.82, 4.47, 7.21; KROG `G8` 6.1, 4.2, 3.9, 6.0, `G16` 5.7, 4.5, 5.1,
7.0. The gate (every valid ratio in [12, 20]) fails for both. `LAW` (Lawson RK4, full linear part) is worse: unstable at
`h = 0.2`, `E = 0.6, 0.3, 0.1, 0.01`.

The failure is not a coding error. Evidence: T-a and the unit test; the kinetic-only variants (`ETDK`, `LAWK`) have `E = 1.3e-9`,
`2.7e-9` at `h = 0.01` (well below ETD's 2.2e-7 at `h = 0.0125`); and the A1 control, same code and same test with the reservoir
decay `gamma_R` changed (`P = gamma(10 + gamma_R)` so `n = 10` is unchanged), `G8`:

| `gamma_R` | ratios `E(2h)/E(h)`, `h = 0.2 -> 0.0125` (ETD) | KROG |
|---|---|---|
| 2 | unstable at 0.2; 19.9, 17.3, 10.2 (the last two are at the reference floor) | unstable at 0.2; 14.7, 15.2, 12.0 |
| 20 | 7.6, 10.9, 13.3, 14.6 | 8.0, 9.5, 11.8, 13.6 |
| 200 (registered) | 2.2, 2.9, 4.5, 7.2 | 6.1, 4.2, 3.9, 6.0 |

The order approaches 4 as `h gamma_R` falls (at `h = 0.0125`, `h gamma_R` is 0.025, 0.25, 2.5): this is the stiff-order reduction of
the Cox-Matthews scheme, a known property of ETDRK4 for stiff linear parts (Hochbruck and Ostermann, SIAM J. Numer. Anal. 2005; cited
from memory, not re-read in this work). The measured consequence for this model: at the registered stiffness `gamma_R = 200` the
step must be `h gamma_R <~ 0.5` (`h <~ 0.0025`) to see order 4, which is inside the regime where CVODE's accuracy per cost wins
(Sec. 6). Krogstad's variant lowers the error by 5-15x at `h = 0.0125` but does not restore order 4 in the same range.

## 3. T-c (stability limit, measured)

`G8`, `V0 = 0.5`, `t = 200`; "stable" = finite and `E <= 0.05` against converged ETD (`h_ref` 0.0125 or smaller, checked against
`h_ref/2`); "inaccurate" = finite, `E > 0.05`; "blown" = non-finite or `max|psi|^2 > 1e4`. `h_first` is the smallest failing grid step
(`h = hmin 2^{j/4}`). `nl = (R + g) n0`, `w_k = pi^2/dx^2`.

| scheme | `n0` | `dx` | `M` | `h_first` (class) | first blown | `h_first nl` | `h_first w_k` |
|---|---|---|---|---|---|---|---|
| ETD | 10 | 1 | 8, 16, 32 | 0.64 (inaccurate) | 0.9-1.08 | 6.7 | 6.3 (`= 2 pi`) |
| ETD | 10 | 0.5 | 8 | 0.16 (inaccurate) | 1.5 | 1.7 | 6.3 |
| ETD | 10 | 0.25 | 8 | 0.16 (inaccurate) | 0.76 | 1.7 | 25.3 (`= 8 pi`) |
| ETD | 50 | 1 | 8 | 0.27 (inaccurate) | 0.32 | 14.0 | 2.7 |
| ETD | 200 | 1 | 8 | 0.045 (inaccurate) | 0.22 | 9.4 | 0.45 |
| ETD | 1000 | 1 | 8 | 0.0034 (blown) | 0.0034 | 3.5 | 0.03 |
| LAWK | 10 | 1 | 8, 16, 32 | 0.0141 (blown) | 0.0141 | 0.15 | |
| LAWK | 50, 200, 1000 | 1 | 8 | 0.0119, 0.0080, 0.0024 (blown) | same | | |
| ETDK | 10 | 1 | 8 | 0.0141 (blown) | 0.0141 | | |
| LAW | 10 | 1 | 8 | 0.01 (inaccurate at every scanned h) | 0.028 | | |
| KROG | 10 | 1 | 8, 16 | 0.64 (inaccurate) | 1.28 | | |
| KROG | 50, 200, 1000 | 1 | 8 | 0.23, 0.027, 0.0034 | | | |

Findings.
* Registered prediction met: ETD at the registered point has `h_first = 0.64` (the last stable step below it is 0.54), 32-37 times
  the IMEX module's limit 0.01707; `LAWK` has `h_first = 0.0141 <= 0.021`. `LAWK` and `ETDK` follow `h <= 2.785/(gamma_R + R n0)`
  within the grid (0.0133, 0.0111, 0.0070, 0.0023 for `n0 = 10, 50, 200, 1000`; measured 0.0141, 0.0119, 0.0080, 0.0024): the
  RK4 real-axis limit applied to the explicit reservoir rate, as expected.
* ETD's limit does not depend on `gamma_R` (it is in the exponent) but on three things, none of which was an unconditional
  win: (a) at `n0 = 10` a **kinetic resonance at `h w_k = 2 pi n`** (`n = 1` for `dx = 1, 0.5`; `n = 4` for `dx = 0.25`) produces
  non-converged states (`E ~ 0.15`) at isolated steps, with blow-up above about `h w_k ~ 10`; independent of `M` (8, 16, 32 give the
  same numbers); (b) at higher density the limit is nonlinear: 14, 9.4, 3.5 in units of `1/((R + g) n0)`; (c) **at `n0 = 1000`
  (`R n0 / gamma_R = 5`) the limit is 0.0034, five times below the IMEX module's 0.01707.** The comparison "ETD is much better than
  the IMEX module" is true at `n0 = 10`-200 and false there.
* Registered hypotheses, as stated: **H-N** fails (the `n0` clause needs `h_first nl` within a factor 3: 6.7 ... 14 ... 3.5 has ratio
  4.0; the `dx` clause needs `h_first` within a factor 2: 0.64 vs 0.16 is 4). **H-K** fails (`h_first w_k` = 6.3, 6.3, 25.3 has
  ratio 4.0, registered tolerance 3), though the values are `2 pi`, `2 pi`, `8 pi`. Neither mechanism alone describes the data; the
  limit is the smaller of a kinetic resonance and a nonlinear bound. The resonance mechanism is a description of what was measured
  (failing steps at multiples of `2 pi / w_k`), not a derivation.
* BDF has no step limit of this kind; CVODE's mean step in T-g is 0.039 (rtol 1e-4, 507 steps for `t = 20`), 0.030 (1e-6), 0.016
  (1e-8), 0.0083 (1e-10): the same range in which ETD runs at comparable errors, so the comparison is cost per step, not stability.

## 4. T-d (agreement with records)

(i) `G8`, seeds 1-10, `h = 0.05`, `t = 4000`, same initial states as the CVODE records. Relative to the record (worst seed):

| `V0` | `d omega` | `d n_center` | `d n_corner` | `d std_n` | gate |
|---|---|---|---|---|---|
| 0 | 3.0e-13 | 1.7e-7 | 2.4e-7 | 1.1e-7 | pass 10/10 |
| 0.25 | 1.1e-8 | 1.2e-5 | 9.9e-6 | 5.0e-6 | pass 10/10 |
| 0.5 | 1.3e-7 | 4.4e-5 | 8.0e-5 | 2.3e-5 | **fail** 0/10 (`std_n` > 1e-5) |
| 1.0 | 3.9e-6 | 3.2e-4 | 1.1e-3 | 2.7e-4 | **fail** 0/10 (`omega` > 1e-6, `n_corner` > 1e-4, `std_n`) |

The differences are the same to 2 digits for every seed: not noise. Diagnostic D1 (seed 1, `t = 4000`, ETD): with
`h = 0.1, 0.05, 0.025, 0.0125`, `|d omega|` to the record is 4.0e-7, 1.3e-7, 2.7e-8, 4.2e-9 (`V0 = 0.5`) and 1.1e-5, 3.9e-6,
8.8e-7, 1.2e-7 (`V0 = 1`): the ETD state converges to the CVODE record, so the record is the accurate one and the registered
`h = 0.05` is too coarse for this gate. At `h = 0.0125` seed 1 satisfies every registered tolerance for both `V0`
(`V0 = 1`: `d std_n = 8.9e-6`, `d n_corner = 8.0e-6`). That is a post-hoc check on one seed at four times the cost; it does not
turn the gate into a pass. KROG at the same steps is not more accurate for `omega` here (5.9e-8 at 0.0125 vs 4.2e-9).

(ii) `t = 16000`, seed 1: `V0 = 0, 0.25` pass; `V0 = 0.5` fails on relative `d mean_n = 1.9e-7` (gate 1e-7; `|d omega| = 6.2e-8`,
`d n_center = 1.3e-6` pass); `V0 = 1` fails on `d mean_n = 3.6e-7`, `d mean_nr = 1.8e-7`, `|d omega| = 1.15e-7`.
Diagnostic D2: ETD does not decay below a **residual floor** at `h = 0.05` (3.2e-9, 6.8e-9, 1.3e-8 for `V0 = 0.25, 0.5, 1`, equal
at `t = 16000` and `t = 100000`; its budget residual there is 5.3e-8, 9.8e-8, 1.5e-7, against 1e-13 in the CVODE record): the discrete relative
equilibrium differs from the continuous one at the 1e-7 level. At `h = 0.0125`, `V0 = 0.5`, `t = 40000`: residual 1.2e-10, budget
1.6e-9 (62 times below the `h = 0.05` value, i.e. `h^3`), and the state differs from the `t = 16000` record by `d omega = 1.7e-9`, relative `d mean_n = 4.9e-9`, `d n_center = 3.2e-8`
(all inside the registered tolerances by a factor 20). The residual floor scales like `h^2.9`.

(iii) `G16`, `h = 0.05`, run to residual `<= 1e-8`: `V0 = 0.25`: `t = 7750`, shift 0.046295, `n_center = 5.8440`; `V0 = 0.5`:
`t = 13800`, 0.07666, 2.3767; `V0 = 1`: `t = 31750`, 0.10653, 0.10004. Against the printed digits of the independent solution in the
review (M1): `|d shift| = 3.0e-4, 3.4e-4, 4.7e-4` (<= 6e-4), `|d n_center| = 4.0e-3, 3.3e-3, 4.2e-5` (<= 0.01, 0.01, 0.005): **pass**.
Against the Krylov package's result file (read only, `ke.jsonl`): `V0 = 0.5` `omega` 0.5766598150851 (KR) vs 0.5766598666 (ETD),
`n_center` 2.376691 vs 2.376692. There is no long-horizon CVODE record at `G16`, so no CVODE comparison is claimed there; the only
CVODE `G16` comparison is the T-b state at `t = 10` (Sec. 2: `E = 5.9e-8` at `h = 0.0125`).

## 5. T-e (cost)

(i) `h = 0.05`, `V0 = 0.5`, `sigma = 3M/16`, best of 3 of 200 steps (loaded machine):

| `M` | 8 | 16 | 32 | 64 | 128 |
|---|---|---|---|---|---|
| ms per step | 0.109 | 0.472 | 2.12 | 9.90 | 50.3 |
| s per unit time | 0.0022 | 0.0094 | 0.042 | 0.20 | 1.01 |
| ratio to `M^2 log2 M^2` | 1.00 | 0.81 | 0.73 | 0.71 | 0.77 |

Gate (ratio in [0.5, 2]): pass. (Per step: 16 two-dimensional FFTs of the complex fields; the nonlinear evaluation is 4 FFT2.)

(ii) Time to the D-d residual `1e-7` at `G8`, `V0 = 0.5`, seed 1, residual checked every 50 time units. ETD `h = 0.1`:
`t = 7400`, **7.7 s**. CVODE dense (rtol 1e-10, atol 1e-12, the dd.rs flow, rerun here): `t = 7400`, **227 s**, 265231 steps
(factor 29). CVODE at rtol 1e-6 did not reach 1e-7 within `t = 20000` (466 s). The registered records: 182.7 s to `t = 4000`
(residual 7.6e-5), 464.8 s to `t = 16000` (1e-8). At `G16`, ETD `h = 0.05`: `t = 11450`, 105 s (residual 1e-8 at `t = 13800`, 125 s);
no CVODE run was made (Phase 3 record: 43 ms per step, i.e. the extrapolated 6 s per unit time is hours). Krylov package
(its `ke.jsonl`, read only; pseudo-transient tolerances with frame tracking, rtol 1e-4): `G8` residual 2e-9 at `t = 4700`, 14.5 s
CPU; `G16` residual 2e-9 at `t = 6800`, 62.5 s CPU. So at `G16` the Krylov solver reached a lower residual in about half
the wall time of ETD (different load conditions; frame tracking is not a luxury ETD lacks by construction, I just did not use it),
and at `G8` the two are the same order. ETD is faster than CVODE dense by 1-2 orders of magnitude here; it is not faster than
the Krylov solver in this test.

## 6. T-f and T-g

**T-f(i), planted bugs.** B1 (`R` doubled in the psi equation): T-a above fails on 3 of 3 seeds (`n = 171.6`, `omega = 6.9`, budget
0.28). B3 (`k^2/4` in `L`): T-b `E = 0.071` independent of `h` (ratios 1.0); T-d(i) `d omega = 2.7e-3`, `d n_center = 1.2` on 3 of 3
seeds. B2 (`f2` where `f3` belongs): `E ~ 2e-2` independent of `h`, ratios 0.9-1.1 at the registered stiffness; but the correct
code also fails T-b, so the registered gate does not discriminate B2 by pass/fail; the `gamma_R = 2` control does: B2 gives ratios
2.4, 2.05, 2.02, 2.01 against 19.9, 17.3 for the correct code. All three bugs are therefore caught, B2 only via the A1 control.

**T-f(ii), `R n n_R` not in `L`.** `G8`, `t = 2`, ETD error `E` (CVODE rtol 1e-12):

| `n0` (`R n0 / gamma_R`) | `h = 0.02` | 0.01 | 0.005 | 0.0025 | 0.00125 | 0.000625 |
|---|---|---|---|---|---|---|
| 10 (0.05) | 9.3e-8 | 1.1e-8 | 1.0e-9 | | | |
| 50 (0.25) | 2.8e-7 | 3.5e-8 | 3.2e-9 | | | |
| 200 (1) | 8.5e-7 | 3.7e-8 | 2.1e-9 | | | |
| 1000 (5) | blown | blown | blown | 2.4e-7 | 2.4e-8 | 1.7e-9 |

At fixed `h = 0.02` the error grows like roughly `n0^0.7` (9.3e-8, 2.8e-7, 8.5e-7 for 10, 50, 200); the cost of the missing term is
not a large error constant but the stability bound of Sec. 3. The error constants `E/h^4` (0.6-1.6 at `n0 = 10`, 1.8-5 at 50,
3.4-5 at 200, 6e3-1.1e4 at 1000, where `h` is also much smaller) are not constant in `h` (order 3-3.5), so no `(R n0)^p` law is
claimed. `LAW` (full linear part) has `E/h^4` of 3.5e4 to 2.5e7: the Lawson form is unsuitable here. `KROG` at `n0 = 1000`: 6.8e-7,
4.1e-8, 2.5e-9 (worse than ETD by 1.5-2.8x on this item).

**T-g, work-precision** (`G8`, `V0 = 0.5`, `t = 20` unless stated; CVODE wall times vary 1.8-2.5 s over repeats at rtol 1e-10):

| solver | setting | steps | `E` | wall (s) |
|---|---|---|---|---|
| ETD | `h = 0.2` | 100 | 5.7e-5 | 0.008 |
| ETD | 0.05 | 400 | 8.8e-6 | 0.032 |
| ETD | 0.0125 | 1600 | 2.7e-7 | 0.12 |
| ETD | 0.00625 | 3200 | 2.7e-8 | 0.36 |
| ETD | 0.003125 | 6400 | 2.2e-9 | 0.76 |
| ETD | 0.0015625 | 12800 | 2.0e-10 | 1.8 |
| CVODE | rtol 1e-4 | 507 | 1.5e-4 | 0.63-1.1 |
| CVODE | 1e-6 | 668 | 7.8e-6 | 0.76-1.0 |
| CVODE | 1e-8 | 1277 | 1.9e-7 | 1.3-1.6 |
| CVODE | 1e-10 | 2415 | 4.3e-9 | 1.8-2.5 |
| KROG (exploratory) | 0.05 / 0.0125 | 400 / 1600 | 1.6e-6 / 3.8e-8 | 0.047 / 0.18 |

At `E ~ 1e-5` ETD is 20-30 times cheaper, at `E ~ 2e-7` 10 times, at `E ~ 3e-9` about 2.5 times, and at `E ~ 2e-10` its cost
(1.8 s) equals CVODE's at rtol 1e-10 which is 20x less accurate; the reference (CVODE rtol 1e-12, 2383 steps for `t = 10`) cost
1.8 s. So ETD is **worse than BDF at accuracies below about 1e-9 on this problem** (stiff-order reduction: `E` falls like `h^3`
rather than `h^4`, with a large constant), and the step count relative to CVODE's grows as the accuracy tightens (0.6x at `E ~ 1e-5`: 400 vs 668; 1.3x at 2e-7: 1600 vs 1277;
2.6x at 3e-9: 6400 vs 2415), against a 8-12 times cheaper step (about 0.08 ms against 0.5-1 ms). At `n0 = 1000` (`t = 20`): ETD `h = 0.0025` 8000 steps, `E = 1.0e-5`, 0.81 s; `h = 0.00125`, `E = 2.4e-7`, 1.24 s;
`h = 0.000625`, `E = 7.2e-9`, 2.5 s; CVODE rtol 1e-6 `E = 3.9e-5`, 0.87 s; 1e-8 `E = 9.9e-7`, 1.7 s; 1e-10 `E = 2.1e-8`, 3.7 s: ETD is only
about 1.5-2 times cheaper there. For larger `M` the dense Jacobian of CVODE grows like `M^6` per factorization against ETD's
`M^2 log M`, so the advantage over dense BDF widens (not measured here for CVODE beyond `M = 16`; the Phase 3 record: 43 ms per step).

## 7. What ETD cannot do here, and where it is worse (summary of the measurements)

1. At the registered stiffness (`gamma_R = 200`) it does not show order 4 until `h gamma_R <~ 0.5`: the registered T-b gate fails,
   and accuracy `<~ 1e-9` costs as much as BDF (Sec. 2, 6).
2. Its step-size limit is not the unconditional one the word "exponential" suggests: kinetic resonances at `h w_k = 2 pi n` and, when
   `R|psi|^2` is a multiple of `gamma_R`, a limit of about `3.5 / ((R + g) n0)`, below the IMEX module's 0.01707 at `n0 = 1000`.
3. Its discrete stationary state carries a time-step error (residual floor `~ h^3`, 7e-9 at `h = 0.05`; the pre-registered D-d(ii)
   residual 1e-7 is reachable, 1e-8 only with a smaller step), so a gate such as D-d(i), budget `1e-8`, needs a smaller step than 0.05 (by the `h^3` scaling above, about 0.02: an extrapolation, not a run).
4. It has no error control (fixed step, choice by hand); CVODE and the Krylov solver adapt.
5. It does not beat the Krylov package (`G16`, time to a residual of 1e-8-2e-9: 62 s vs 125 s) in this comparison, which is not
   like-for-like (frame tracking, tolerances, load).
6. Not tested: noise, 3D, non-periodic boundaries, `V0` large enough that `|psi|^2` approaches `gamma_R` at the gate (the registered
   gate cannot do that: the corner density is 12-13 for `V0 <= 1`), a Hochbruck-Ostermann stiff-order-4 exponential scheme (not
   implemented; Krogstad's, which has stiff order 3 by the literature I recall, lowers the error 5-15x but is not order 4 either).

## 8. Caveats

One model, one parameter set; one initial seed for T-b, T-c, T-f(ii), T-g (seeds 1-10 only in T-a and T-d(i)); `t = 200` for the
stability test (a weakly unstable mode growing at a rate below `~0.03` would not be seen); the `n0` and `dx` sweeps change the
pump and the lattice spacing, so they are probes of the integrator, not Phase 3 records; the contour (32 points, radius 1) was not
varied; timings under load 4-11 on 8 cores; the CVODE `G16` long record does not exist and was not made; the comparison with the
Krylov package uses the numbers in its committed result files without re-running it.
