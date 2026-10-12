# F1: alpha-homotopy on S^3 against the proved 600-cell (2026-10-12)

Pre-registration: `../PREREG_round2.md` section F1 (commit 51a85b1, not edited). Code: `run_F1.py` (homotopy + F1b control),
`analyse_F1.py` (gates; full output in `analysis_output.md`). Records: `records_N120.jsonl` (150 = 3 a x 50 seeds),
`records_N24.jsonl` (150). Reference: Experiment C (`../C/records.jsonl`). Nothing here is a theorem; negatives are kept.

## Verdicts

| Gate | Verdict | Numbers |
|---|---|---|
| F1a (N = 120, >= 45/50 within 1e-8 of E_600 and min chord within 1e-6 of 2 sin(pi/10), each a in {1, 2, 4}) | **FAIL at every a** | homotopy 0/50 (a = 1), 0/50 (a = 2), 6/50 (a = 4) |
| F1b (plain L-BFGS with restarts at the homotopy's gradient-evaluation budget must NOT reach >= 45/50 at a in {2, 4}) | **FAIL at a = 4** (plain reaches 50/50; "the homotopy has no merit"); holds at a = 2 only trivially (both 0/50) | plain equal compute 0/50, 0/50, 50/50 |
| Stop rule (F1a fails at every a) | **applies** (registered for T1/T2; extended to round-1 B as our reading): the 3D structure searches of this programme (B, T2, T1) are read as "no counterexample found with an unreliable search" | |
| Control 2 (N = 24) | homotopy reaches the 24-cell energy 50/50 at every a, never below it | see below |

## N = 120

| a | homotopy hits (E and chord) | plain, equal compute | C plain (same seeds) | homotopy end, rel. excess over E_600 (misses) | homotopy gradient evaluations min/mean/max |
|---|---|---|---|---|---|
| 1 | 0/50 | 0/50 | 0/50 | 1.7e-8 .. 2.4e-8 | 61 557 / 69 714 / 73 383 |
| 2 | 0/50 | 0/50 | 0/50 | 7.0e-6 .. 8.2e-6 | 78 398 / 88 013 / 95 421 |
| 4 | 6/50 | 50/50 | 6/50 | 7.9e-4 .. 1.1e-3 | 80 168 / 91 118 / 101 005 |

Where the ladder fails (all 150 ladders, `analysis_output.md`): median relative excess over E_600(a) is 3.0e-11 at a0 = 0.25,
1.4e-10 at 0.5, 2.1e-8 at 1, 7.4e-6 at 2, 1.0e-3 at 4, i.e. the same order as C's trapped plain runs at a = 1, 2, 4
(C: 2.0-3.1e-8, ~7e-6, ~1e-3).
The a0 = 0.25 state where L-BFGS stops is not the 600-cell (`supp_rung_chords.py`, seed 0, `supp_rung_chords_s0.{json,log}`: min chord
0.237 vs 0.618, distance-spectrum deviation 0.38), and it is not a local minimum: `supp_hessian.py` (`supp_hessian.log`,
seed 0, Hessian on (S^3)^120 by central differences of the gradient, h = 1e-4 and 1e-5) finds 83 negative eigenvalues (the
reviewer's independent computation: 74), lowest -1.8e-6, tangent gradient 1.2e-5; a fresh L-BFGS restart from it stops after
17 iterations having lowered E ~ 4445 by 7e-11. L-BFGS stops on its relative-reduction test at a stall point near the
floating-point resolution of E, so the registered "convergence at a0" is not reachable in double precision with this energy.
The trapped plain a = 4 endpoint (seed 0, same script) is a strict local minimum: no negative eigenvalue, exactly 6 zero modes
(rotations of S^3) at h = 1e-5. Rungs at the 8000-iteration cap (C's setting, kept): 6-10 of 17 per a = 4
ladder (mean 7.8); every ladder caps at a = 0.5 .. 1.

The six a = 4 homotopy hits (seeds 9, 10, 17, 20, 46, 49) share no seed with C's six hits (12, 15, 21, 32, 34, 42). Each ladder
is on the trapped branch at a = 2.83 (~1e-4 above) and drops to the 600-cell only at a = 3.36 (seeds 9, 49) or a = 4 (the
others): late escapes, not branch-following.

F1b restarts at a = 4: 1 916 of 5 790 completed restart runs reach E_600 (33%); all runs including the first: 1 922 / 5 840.
The budget-truncated last run of each seed (50 runs) is not counted; counting them as misses gives 1916/5840 = 0.328 against
0.331 (hit runs average 633 iterations, misses 827, so dropping slow truncated runs slightly inflates the rate).

### Is C's 6/50 at a = 4 reproducible, and is it representative? (unregistered checks)

* Reproduction: the first run of every F1b control starts from C's point (same seed formula, same RNG draw). It reaches the
  600-cell at exactly C's six seeds (outcome agreement 50/50); its final energy agrees with C's to <= 5.5e-12 absolute
  (3.1e-14 relative) at 48 seeds (`analysis_output.md`, last lines of the N = 120 section); the
  other two (seeds 11, 44) end in different trapped minima, 8.6e-3 and 1.5e-2 apart in absolute energy. At a = 1 and a = 2 the
  first-run energies differ from C's by up to 9e-6 and 6e-4 (iteration-capped or flat landscape), outcomes identical (all
  misses). Cause: `run_F1.py` evaluates the same energy through the Gram matrix (asserted equal to 1e-12 before every run);
  floating-point paths diverge in a flat landscape. Tested: C's own `minimise()` re-run at seeds 11, 44, 16
  reproduces C's records exactly (`supp_C_evaluator.py`, `supp_C_evaluator.log`).
* Representativeness: plain L-BFGS (C's settings, F1 evaluator) from fresh starts reaches the 600-cell in 12/40
  (`fresh_plain_a4.py`, rng 777001, `fresh_plain_a4.log`) and 26/100 (`cseeds_plain_a4.py`, C's seed formula at indices 50-149,
  never used by C, `cseeds_plain_a4.log`).
* Fisher's exact test, two-sided, C's 6/50 against: F1b restart runs 1916/5790, p = 0.0012; 12/40, p = 0.061; 26/100,
  p = 0.058; the two fresh checks pooled 38/140, p = 0.032.
* Reading: C's 6/50 is a correct record of what is very probably a low draw (the 26/100 check was added after seeing 12/40;
  neither is below 0.05 alone; the restart comparison and the pooled one are); the per-start success rate of plain L-BFGS at a = 4 is about 0.27-0.33.
  Paper V's round-1 section C now says so.

## N = 24 (control 2)

| a | homotopy at E_24cell (E and chord = 1) | E-only | below E_24cell | plain, equal compute | C plain (same seeds) |
|---|---|---|---|---|---|
| 1 | 44/50 | 50/50 | 0 | 50/50 | 25/50 |
| 2 | 50/50 | 50/50 | 0 | 47/50 | 7/50 |
| 4 | 50/50 | 50/50 | 0 | 27/50 | 0/50 |

The six a = 1 chord misses are at the 24-cell energy to 1e-8 with minimum chord 1-2e-6 from 1 (incomplete convergence, not a
different configuration). The homotopy helps at N = 24 (a configuration known not to be universally optimal) and not at N = 120.

## Deviations

1. Evaluator: `run_F1.py` replaces C's energy/gradient by an equivalent Gram-matrix form (about 5x faster), asserted equal to
   1e-12 (energy relative, gradient absolute) at N = 24, 120 and four a before every run.
2. Interruption: the launching session was compacted after seeds 0-5 of N = 120 (all three a). Seeds 6-49 were resumed with
   the same code (`run_N120_s6-50.log`), appending to the same records file. A first resume oversubscribed BLAS (load ~59) and
   was killed after about 8 minutes, before writing any record; the relaunch used OMP_NUM_THREADS=1, 5 processes. By the time of
   the interruption F1a had already failed at every a (6 misses each > 5 allowed).
3. Unregistered supplementary checks: `supp_rung_chords.py` (one ladder with chords recorded), `supp_hessian.py`,
   `supp_C_evaluator.py`, `fresh_plain_a4.py`, `cseeds_plain_a4.py`, the C-reproduction comparison and the rung-by-rung tables
   in `analyse_F1.py`. None changes a verdict.
4. Iteration cap: the registration says "L-BFGS re-converged at each rung" and sets no cap. `run_F1.py` used C's optimiser
   settings including maxiter = 8000 (an unregistered choice). 6-10 of 17 rungs per ladder hit it (every ladder at every rung
   from a = 0.5 to 1; 9 ladders already at a0). The F1a verdict is for the homotopy as implemented with this cap.
