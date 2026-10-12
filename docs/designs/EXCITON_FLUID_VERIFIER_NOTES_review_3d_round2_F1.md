# Adversarial review: 3D round 2, F1 only (2026-10-12)

Scope: F1 (alpha-homotopy on S^3) only. Materials read: `exploration/exciton/three_d/PREREG_round2.md` section F1 (identical
to commit 51a85b1; `git diff 51a85b1 HEAD` on the file is empty), `F1/run_F1.py`, `F1/analyse_F1.py`, `F1/analysis_output.md`,
`F1/RESULTS.md`, `F1/records_N120.jsonl`, `F1/records_N24.jsonl`, `F1/fresh_plain_a4.{py,log}`, `F1/cseeds_plain_a4.{py,log}`,
`F1/supp_rung_chords.py` and `supp_rung_chords_s0.{json,log}`, `F1/run_N120_s6-50.log`, `C/run_C.py`, `C/records.jsonl`,
`C/reference.json`, `paper/exciton_fluid_gated_V_round2.tex` lines 1-66 and 118-128, `paper/exciton_fluid_gated_V.tex` lines
50-56, 115-124 and 205-213, `exploration/exciton/python/companion5_round2.py` lines 1-70, `paper/figs_companion5/fig_round2.png`.

Method: independent scripts in my scratchpad. I rebuilt the 600-cell and 24-cell myself, not through `run_C.cell600`; my E_600
agrees with `C/reference.json` to <= 6e-13 relative. All runs used OMP_NUM_THREADS=1 and each took under 10 min. I did not
re-run the full F1. Short re-runs:
(i) N = 24, seeds 0, 1, 3 at a = 1, 2, 4 (9 full jobs);
(ii) N = 120, a = 4, homotopy plus first plain run for seed 0 (first session) and seed 9 (resumed session);
(iii) C's own evaluator (`run_C.minimise`) at a = 4 for seeds 11, 44 and 16;
(iv) Riemannian Hessians (central finite differences of the projected gradient, 360 tangent directions, h = 1e-4 and 1e-5) at
the a0 = 0.25 state of seed 0, at the 600-cell for a = 0.25, and at the plain endpoints of seed 0 for a = 4 and a = 2.

---

## BLOCKING

**B1. The tex's mechanism ("a family of nearby minima") is contradicted. The a0 = 0.25 state is a stall point with
negative curvature, not a minimum.**
`exciton_fluid_gated_V_round2.tex:35-38`: "already at $a_0=0.25$ the converged state is $3\times10^{-11}$ above $E_{600}$ and
yet is not the 600-cell (... seed 0: converged, minimum chord $0.237$ ...) ... The soft kernel does not select the 600-cell; it
selects a family of nearby minima that the ladder then follows." `RESULTS.md:30` says "The converged a0 = 0.25 state". I
reproduced the seed-0 a0 state bit for bit (rel. excess 3.7455e-11, min chord 0.23746, message "RELATIVE REDUCTION OF F").
Its Riemannian Hessian has **74 negative eigenvalues** (lowest -1.13e-6, stable between h = 1e-4 and h = 1e-5), 3 near zero
and 283 positive, and a tangent gradient norm of 4.1e-6. A genuine minimum would show 6 zero modes (SO(4)) and nothing
negative. So the state is not a minimum. Restarting L-BFGS from it, 7 times with fresh memory, gives 1-27 iterations each and
no change (rel. excess 3.745e-11 -> 3.743e-11, chord 0.2375 -> 0.2374). Cause: the descent available per step,
|g|^2/(2L) ~ (4e-6)^2/56 ~ 3e-13, is below the double-precision resolution of E ~ 4445 (eps*E ~ 1e-12). The relative-reduction
test therefore stops L-BFGS on round-off.
For contrast, the 600-cell at a = 0.25 has 130 Hessian eigenvalues with |w| < 1e-8: the landscape is flat at this resolution
in about 124 directions beyond the rotations.
The supported reading is narrower. At a0 = 0.25, L-BFGS in double precision cannot resolve the energy differences that would
select the 600-cell. It stalls at a far-off configuration with negative curvature. "Converged" there means the optimiser
stopped, not that a minimum was reached. "Family of nearby minima" must go. "Nearby" is true only in energy; the distance
spectrum deviates by 0.38.
Where "trapped minimum" is correct: the plain endpoint at a = 4 (seed 0, rel. excess 1.04e-3) has 0 negative and exactly 6
near-zero eigenvalues, so it is a strict local minimum. At a = 2 (seed 0, 7.3e-6) there are 2 small negative eigenvalues
(-2.5e-8, about 25x the finite-difference noise), so it is borderline. This also bears on the F1a failure itself. The
registered method's first step, "L-BFGS to convergence" at a0 = 0.25, is not attainable with this energy formulation in
double precision. That is a design limitation the paper should state, not a property of the kernel.
(Context, outside F1: the C section's "distinct local minima" at a = 1, from the 150 000-iteration rerun, was not checked
with a Hessian. It should be, or worded as "stall points".)

**B2. "Seven to nine of the 17 rungs" is wrong.** `exciton_fluid_gated_V_round2.tex:38-39`. From `records_N120.jsonl`, the
a = 4 ladders have **6 to 10** capped rungs (nit >= 8000), mean 7.84. `RESULTS.md:31` and `:72` correctly say 6-10. The tex
kept the seeds-0-5 figure suggested by the earlier review (S8 there), which the full data no longer support.

**B3. "1.4e-12 at 48 seeds" is wrong and has no file behind it.** `exciton_fluid_gated_V_round2.tex:50` and `RESULTS.md:40`:
"its final energy agrees with C's to <= 1.4e-12 at 48 seeds". Recomputed |E_firstrun - E_C| at a = 4: the largest of the 48
is **5.5e-12** (seed 16), then 3.0e-12 (seed 49), 1.48e-12 (seed 25), 1.39e-12 (seed 3). So only 44 seeds are within
1.4e-12. In relative terms the maximum is 3.0e-14. `analysis_output.md` prints only the overall maximum (1.5e-02), and no
file prints 1.4e-12. Fix: "to <= 6e-12 (absolute; 3e-14 relative) at 48 seeds", and print it from `analyse_F1.py`. The other
two seeds are correct: 11 and 44 differ by 8.56e-3 and 1.45e-2, both trapped. The stated cause, the Gram-matrix evaluator,
is supported: C's own evaluator re-run on seeds 11, 44 and 16 reproduces C's records bit for bit (same E, same nit 983,
1455, 874). Say so. At present it is asserted, not shown.

**B4. An unregistered choice is presented as registered: the 8000-iteration rung cap.** The pre-registration says "start
at a0 = 0.25 (L-BFGS to convergence, same seeds as C), then ... (L-BFGS re-converged at each rung, warm start)". It sets no
iteration cap and does not say "C's optimiser settings". The text says otherwise:
- `RESULTS.md:72`: "The registered rung-cap was C's 8000 iterations; 6-10 of 17 rungs hit it. Not changed."
- `exciton_fluid_gated_V_round2.tex:39`: "so the soft rungs are not fully converged; the registered settings were kept."
- `tex:23`: "warm-started and with C's optimiser settings", written as part of the design.
The cap was an implementation choice inherited from C (`run_F1.py:23` "identical to C"). It means the registered "re-converged
at each rung" was not done: every one of the 150 ladders hits the cap at every rung from a = 0.5 to 1, and 9 ladders hit it
already at a0. This must be listed as a deviation in `RESULTS.md` "Deviations" and the tex "Round 2 deviations" paragraph.
The F1a verdict must say it applies to the homotopy as implemented, with an 8000-iteration cap per rung. Given B1, raising
the cap would probably not rescue the soft end, but that has not been tested, so do not imply it.
(The round-1 C section, `exciton_fluid_gated_V.tex:119`, does call 8000 "the registered 8 000-iteration cap" for C. That
registration does not carry over to F1's "re-converged".)

**B5. Some of the deposit's evidence is not in the repository.** `git status` / `git ls-files` show these as untracked:
`F1/RESULTS.md`, `F1/analysis_output.md`, `F1/records_N120.jsonl` (all of F1a/F1b at N = 120) and `F1/cseeds_plain_a4.py`.
`F1/cseeds_plain_a4.log` (the only record of 26/100) and `F1/run_N120_s6-50.log` (the resume log cited in RESULTS deviation
2) are git-ignored by `.gitignore:67 *.log` and need `git add -f`, as was done for `fresh_plain_a4.log`. The figure script's
docstring (`companion5_round2.py:2`) says "Reads only committed records". That is false until `records_N120.jsonl` is
committed. Commit all of these before the deposit is built.

---

## SHOULD-FIX

**S1. The figure caption miscounts the escapes.** `exciton_fluid_gated_V_round2.tex:14`: "the band reaches the floor at
$a\ge3.36$, where 6 ladders escape to the 600-cell". At a = 3.36 only 2 ladders are at the 600-cell (seeds 9 and 49, rel.
excess 1.1e-15 and 1.6e-15); the other four drop at a = 4. Write "2 ladders at a = 3.36, 6 by a = 4". The F1 prose
(`tex:41`, "the last one or two rungs") is correct.

**S2. Paper V section C overstates "shows".** `exciton_fluid_gated_V.tex:118`: "round~2 shows this is a low draw: 26/100
and 12/40 with fresh starts". The two numbers cited have two-sided Fisher p = 0.058 and 0.061 against 6/50. Neither is
significant at 0.05 on its own, and the 26/100 check was added after seeing 12/40 (`cseeds_plain_a4.py` docstring). The
strong evidence is the restart runs (1916/5790, p = 0.0012), and the pooled fresh checks give p = 0.032. Either cite those or
write "indicates". The F1 subsection's wording ("a correct record of a low draw") is acceptable, because it gives all four
p-values.

**S3. "The same excesses as C's trapped plain runs" holds only in order of magnitude.** `tex:37`; `RESULTS.md:28-29`.
Homotopy endpoint ranges against C's trapped ranges:

| a | homotopy endpoints | C trapped |
|---|---|---|
| 1 | 1.66-2.38e-8 | 2.01-3.05e-8 (median 2.48e-8) |
| 2 | 6.96-8.24e-6 | 6.90-8.41e-6 |
| 4 | 0.79-1.12e-3 | 0.95-1.15e-3 |

At a = 1 the homotopy is systematically lower, because C's runs are capped. Write "the same order (overlapping ranges)".

**S4. Panel (b) mixes criteria.** `companion5_round2.py` `frac()` tests energy only. At N = 24, a = 1 the homotopy bar shows
1.0, while the table and prose give 44/50 with the chord test. The dashed line is labelled "gate F1a: 45/50", but F1a includes
the chord test. The y-label ("at the target energy") is accurate, so this is minor. Add "energy only" to the caption, or use
E and chord for the bars. At N = 120 the two criteria coincide (verified: E-only = E+chord at every a).

**S5. The stop-rule scope adds B.** The registered text reads: "the 3D structure searches of this programme are declared
unreliable and T1/T2 are run only as 'no counterexample found ...'". `tex:60-61` and `RESULTS.md:15` extend this explicitly
to B, a round-1 search. That reading is defensible ("3D structure searches of this programme"). Say in one clause that
including B is the authors' reading of the rule. Make sure the round-1 B section and conclusion (`exciton_fluid_gated_V.tex:205-206`,
"a search whose reliability is itself measured") are consistent with "declared unreliable".

**S6. Use "stopped", not "converged", wherever L-BFGS ended on the relative-reduction test at soft a.** This follows from B1:
`tex:35-36` ("converged state", "converged"), `RESULTS.md:30`, and the `supp_rung_chords.py` description.

**S7. The F1b denominators exclude truncated runs.** The survivorship note is correct in direction. Measured: hit runs average
633 iterations and miss runs 827, so dropping the 50 slow truncated runs slightly inflates the rate. The size is bounded:
1916/5840 = 0.328 against 0.331. One sentence with the bound would close it.

---

## Checked and correct

- Pre-registration F1 unchanged since 51a85b1. Seeds use C's formula (1000N + s + 100000*kernel index) for all 150 N = 120
  records. No duplicate (a, seed) pairs, 150 records per N.
- F1a: homotopy hits (E within 1e-8 relative and min chord within 1e-6 of 2 sin(pi/10)) are 0/50, 0/50 and 6/50 at a = 1, 2,
  4. E-only gives the same counts. Verdict "FAIL at every a" follows the registered wording (>= 45/50 needed at each a).
- F1b: plain equal compute 0/50, 0/50, 50/50 (E and chord; all 50 a = 4 plain hits pass the chord test). The verdict "FAIL at
  a = 4; holds at a = 2 only trivially" and "has no merit by the registered criterion" match the registered sentence "If it
  does, the homotopy has no merit."
- Stop rule triggered as registered. Deviation statement "6 misses each, more than the 5 allowed" after seeds 0-5: the first
  18 records are seeds 0-5 for all a, with no hit among them.
- Six a = 4 homotopy hits: seeds 9, 10, 17, 20, 46, 49. C's hits: 12, 15, 21, 32, 34, 42. They are disjoint. All six ladders
  are 1.0-1.1e-4 above at a = 2.83. Seeds 9 and 49 are at the 600-cell at a = 3.36 (1.1e-15, 1.6e-15) and the other four only
  at a = 4. The "late escape" description is supported.
- Miss excess ranges: 1.66-2.38e-8, 6.96-8.24e-6, 7.87e-4 to 1.12e-3. Gradient evaluations (min/mean/max): 61 557/69 714/73 383,
  78 398/88 013/95 421, 80 168/91 118/101 005. The tex ranges 6.2-7.3, 7.8-9.5, 8.0-10.1 x 1e4 and 6.2-10.1 x 1e4 are correct.
- Restart runs at a = 4: 5 790 completed restarts with 1 916 hits (33.1%); including the first run, 5 840 and 1 922; 50
  truncated runs. Restarts per seed range from 99 to 129. At a = 1 there are 392 completed runs and 0 hits; at a = 2, 1 073
  and 0.
- C reproduction: the first-run outcomes agree with C at all 50 seeds (hits exactly at 12, 15, 21, 32, 34, 42). The two
  exceptions are seeds 11 and 44 (8.6e-3 and 1.5e-2). At a = 1 and a = 2 the maximum first-run difference is 9.0e-6 and
  6.1e-4 with identical outcomes. (The "48 seeds" bound itself is wrong; see B3.)
- Fisher's exact test, two-sided, 6/50 against: 1916/5790 gives p = 0.00123; 12/40 gives 0.0614; 26/100 gives 0.0578;
  38/140 gives 0.0321. All four as stated (scipy `fisher_exact`). Per-start rate 0.26-0.33, so "about 0.27-0.33" and "nearer
  0.3 than 0.12" are fair.
- `fresh_plain_a4.log` (12/40) and `cseeds_plain_a4.log` (26/100) match their scripts' outputs as quoted. I did not re-run
  them, being within budget but redundant. My re-runs (ii) reproduce the evaluator path bit for bit.
- N = 24 control: E-only 50/50 at every a; E+chord 44, 50, 50; never below the 24-cell (lowest rel. -> +2.8e-16). The six
  chord misses at a = 1 are seeds 3, 5, 6, 12, 37, 43, with chord 1.0-1.9e-6 below 1 and energy within 1.5e-14. Plain equal
  compute 50, 47, 27; C plain 25, 7, 0.
- Reproducibility and "same code" across the interruption: the N = 24 seeds 0, 1, 3 at all a, and N = 120 a = 4 seeds 0
  (first session) and 9 (resumed), re-run with the current `run_F1.py`, reproduce the records bit for bit (E, nfev,
  per-rung nit, restart counts, first plain run). `run_F1.py` mtime 08:22:46 precedes the end of `records_N24.jsonl` (08:26:40),
  and the N = 24 CPU time (448 s on 2 processes, about 3.7 min) fits a start after the last edit.
- Rung-by-rung medians (3.0e-11 at 0.25, 1.4e-10 at 0.5, 2.1e-8 at 1, 7.4e-6 at 2, 1.0e-3 at 4) match `analysis_output.md`.
  supp_rung_chords seed 0: min chord 0.237 at a0 and spectrum deviation 0.38. Every a = 4 ladder caps at every rung in
  [0.5, 1].
- Figure panel (a): the median line, the range band (floor 1e-13) and C's squares (6 at the floor for a = 4) match the
  records. Panel (b): bar heights match (N = 24: 1/1/1, 1.0/0.94/0.54, 0.50/0.14/0; N = 120: 0/0/0.12, 0/0/1.0, 0/0/0.12).
- Paper V abstract (`exciton_fluid_gated_V.tex:53`), "0, 0 and 6 of 50 seeds at a = 1,2,4, while plain restarts at equal
  compute reach it in 50/50 at a = 4": correct.
- CCEK 2007 (24-cell not universally optimal) is cited in paper V (`:124`, bibitem `:235`), and the memo records it as read
  in full, as the pre-registration required.

## Resolution (author, 2026-10-12)

- B1: mechanism rewritten ("stall point", not a minimum). Committed check `F1/supp_hessian.py` (+ log): 83 negative eigenvalues
  at the seed-0 a0 state (reviewer: 74, different finite-difference set-up; both stable in h), lowest -1.8e-6; restart stops after
  17 iterations, dE = -7e-11; the trapped a = 4 plain endpoint is a strict minimum with 6 zero modes. S6 applied with it.
- B2: "Six to ten of the 17 rungs (mean 7.8)".
- B3: "5.5e-12 absolute (3e-14 relative) at 48 seeds", now printed by `analyse_F1.py`; cause tested by `F1/supp_C_evaluator.py`
  (C's own code reproduces C's records exactly at seeds 11, 44, 16).
- B4: the 8000-iteration cap is listed as an unregistered choice in the tex method paragraph, the deviations and RESULTS.md;
  F1a verdict scoped to the homotopy as implemented with it.
- B5: all F1 records, scripts and logs committed (`git add -f` for the logs).
- S1 caption corrected (2 at a = 3.36, 4 at a = 4). S2: main tex now cites restarts 1916/5790 and pooled 38/140, "indicates".
  S3: "of the same order" with C's ranges. S4: caption states bars are energy-only and what the chord test removes. S5: stop-rule
  extension to B labelled as our reading; round-1 bullet made consistent. S7: 1916/5840 = 0.328 stated.
