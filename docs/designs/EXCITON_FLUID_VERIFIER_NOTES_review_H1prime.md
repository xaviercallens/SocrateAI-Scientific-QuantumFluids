# Hostile review: H1' (exploration/exciton/three_d/H1p/), 2026-10-12

Reviewer: independent agent. No repo file other than this one was edited. Reviewed at HEAD 350bc74. All recomputations
were single-threaded (OMP_NUM_THREADS=1); scratch scripts were kept outside the repo.

## Verdict

No BLOCKING issue. Registration order is clean. Every number in RESULTS.md was recomputed and matches, with one
exception (a residual figure). The literature values are verified against the paper. The independent lattice sums match.
The spot-check of residual violations matches to 1e-17. Five SHOULD-FIX items concern one wrong figure and wording
that overstates the result.

## BLOCKING

None.

## SHOULD-FIX

1. **Wrong figure.** RESULTS.md:22 says "V1 α = 1: 5.2e-10". The residual is max(f − g, −f̂). records/V1a_K40.json
   gives max_f_minus_g = 5.236e-10 and max_neg_fhat = 6.161e-10, so the value is **6.2e-10**.

2. **"Reproduces ... to their printed 8 digits" is false for d = 2.** RESULTS.md:45-46 and the commit message of
   350bc74 ("reproduced to 8 digits") make this claim. B(V2, K = 40) = 0.1595952701 truncates to 0.15959527. The
   published value is 0.15959526..., so the 8th digit differs. The A2 gate window (PREREG.md:139) was widened to
   0.15959527 + 1e-8, so the gate passes as registered. The wording should instead say "within the registered windows
   (|B − published| ≲ 1e-8)". d = 1 and d = 3 do match to 8 digits (0.08643481, 0.22321782).

3. **The size of the slack is understated.** RESULTS.md:10-11 says each value "can exceed the true LP optimum by about
   that much", that is, by about the residual violation. The run's own data contradict this. Any valid LP bound is at
   most E_A2, yet B(V2) exceeds E_A2(π) by 3.1e-9 with a residual of 8.9e-11, a factor of about 35. In d = 1, α = 1,
   where the LP is sharp at E_Z, B − E_Z = 1.09e-9 with a residual of 6.2e-10. The excess is a lattice-sum of
   pointwise violations and can be many times the maximum residual. Suggested fix: report the excess as "observed up
   to ~35× the residual (V2)". Note that at that ratio, V3's residual of 5.1e-10 would allow an excess of about 2e-8,
   which is of the same order as the V3 window half-width. The gate on B is unaffected. The "8 digits" reading is
   weakened.

4. **Prior knowledge at gate parameters is not disclosed in RESULTS.**
   - The V1 K = 30 runs are bit-identical reruns of H1's published results (H1/run.log):
     - V1a: 0.7726372068319629 at β = 0.13316.
     - V1b: 0.08643481149488239 at β = 1.09545, viol 4.089e-8. H1 rejected this value at 5e-9.
   - So those outcomes were known before A2.
   - A2's 1e-7 acceptance (PREREG.md:132-134) was set after seeing H1's α = π full-setting violations (2.1e-8 to
     4.6e-8, H1/RESULTS.md:98). A2 discloses this only partly: "H1 used 5e-9, which none of its α = π solutions met".
   - Mitigation, checked in log_V1b_K40.txt: the gate used K = 40, which was not known in advance. All three K = 40
     full β candidates for V1b lie within 3e-9 relative of E_Z. The V1b pass therefore does not depend on the 1e-7
     threshold, even though the chosen solution's 9.97e-8 sits only 0.3% under it.
   - Suggested fix: state both facts in RESULTS § Deviations.

5. **K-dependence and ansatz caveats are missing from the verdicts.**
   - (a) The V3 pass depends on K = 40 being the gate K (registered in A2, so this is legitimate). B(V3, K = 30) =
     0.2232173547 lies **outside** the V3 window [0.22321781, 0.22321784] by 4.65e-7. RESULTS.md:26-27 gives the
     4.7e-7 difference but does not say that K = 30 would fail V3. It should.
   - (b) The H1' reading "two-point (LP) bounds are insufficient" (RESULTS.md:37-38) needs an *upper* bound on the LP
     optimum. A primal solution with K ≤ 40, a Gaussian times polynomial ansatz and a scanned β gives only a (slack-
     inflated) lower estimate of it. Changes from K = 30 to K = 40 (3e-7 relative) and the α = π agreement with the
     literature make convergence plausible, but no dual certificate exists. Say "numerically, at K ≤ 40" in the
     verdict sentence.
   - (c) The verdict also uses min(E_FCC, E_BCC) as the ground-state proxy. At α = 2 (G = 4.8e-3), a non-lattice state
     0.4% below BCC would change the reading. That is implausible, but it is not excluded. RESULTS.md:40-41 says
     "slightly below", which is an assumption.

## Minor

- RESULTS.md:41: "4e-6 lower" is relative. The absolute difference is 0.231536266 − 0.23153532 = 9.5e-7 (4.1e-6
  relative). Say "relative".
- RESULTS.md:26 and :41 call the record 0.23153532 "a coexistence phase". Table 1.1's caption attributes it to
  "[15] or the expectation bound" (Cohn–Kumar–Schürmann 2009). I did not read [15], so the "coexistence phase"
  description is unverified by me.
- The first 90 lines of PREREG.md still say "certified" in the title, at :21 ("certified d = 3 bounds") and in the gate
  text. They are superseded by A2 (:122-145), but a reader of the title is misled. Add a pointer in RESULTS.md's
  header, which partly exists, or in the README, rather than editing the registration.
- Selection bias in the β choice. run_h1.scan picks the maximum objective among accepted β. With non-rigorous slack,
  this favours the most-violating solution. In log_V1a_K40.txt the chosen B is 1.09e-9 above E_Z, while another
  accepted β gives 4.7e-11 *below* E_Z.
- H8 K = 40: the full best β (×0.2928) is the lowest of the three full candidates, so the optimum in β is not bracketed
  at FULL settings. A non-optimal β lowers B, which raises G, which favours the "insufficient" verdict. This is
  irrelevant at G = 0.216.
- PREREG.md:144 says the lattice energies are computed with `theta_sum`, "Z included". run_h1p.py:28 uses
  `E_Z_series` for Z. The value is identical to 1e-16 (checked).
- run_h1p.py:3 says stdout is "collected in run.log". In fact run.log holds only "done" and stage lines, and the
  RESULT lines are in log_*.txt. This is cosmetic.
- "single-threaded, 4-6 parallel jobs" (RESULTS.md:7) cannot be verified from committed files. run_h1p.py does not set
  OMP_NUM_THREADS.
- Dev discipline (A1, PREREG.md:118-120) cannot be fully verified:
  - dev_scan.py and newton_polish_proto.py are hard-coded to α = 2 (non-gate).
  - dev_one.py takes arbitrary arguments and no dev output was kept.
  - A1's own pre-check used ../H1/solutions/d1_alpha1.json, a gate parameter (V1a). It was disclosed as an inspection
    of an existing file and is not a run.

## Verified OK

- **Registration order (git):**
  - d668109 PREREG 19:35:52
  - 83a3500 A1 19:38:43
  - 1ec3fe7 dev/DEV_NOTES 19:50:20
  - 968dd32 A2 + run_h1p.py 20:33:46
  - 91b1a97 driver fix 20:33:56
  - run.log: "code commit 91b1a97, start 2026-10-12T20:34:03+02:00"
  - The results commit 350bc74 (21:07:32) adds only RESULTS, logs and records. `git diff 91b1a97 HEAD` on
    PREREG.md, run_h1p.py and H1/ is empty, and H1/lp_bound.py and run_h1.py are last changed in a693b54 (before
    H1'). The working tree is clean for H1p/ and H1/.
  - The 91b1a97 fix is correct: `scan` looks up `admissible` at call time, so the patched default is effective.
- **Stage order:** run.log shows V1 (both K) done before "stage 2 start 20:51:26" and V2/V3 done before "stage 3 start
  20:58:46", consistent with the stop rule.
- **Literature** (read via alphaXiv, arXiv:1603.09684v6, p. 5, Table 1.1): "LP bound" n=1 0.08643481..., n=2
  0.15959526..., n=3 0.22321782...; "Current record" n=3 0.23153532.... All match PREREG.md:14-16. Prop. 2.2 (p. 7)
  holds for "every subset of R^n with density ρ", and §2 says "Here we extend it to arbitrary configurations".
  PREREG.md:22-23 is correct.
- **Lattice energies.** These are my own mpmath direct sums with explicit unit-covolume bases, |n_i| ≤ 9-40,
  convergence checked:

  | α | E_Z | E_A2 | E_FCC | E_BCC |
  |---|---|---|---|---|
  | 1 | 0.7726372048266522 | | | |
  | π | 0.08643481121330801 | 0.1595952669639284 | 0.2315362661841479 | 0.2315362661841479 |
  | 2 | | | 1.017616895908993 | 1.015862816034718 |
  | 4 | | | 0.07796767103070266 | 0.07889601370735761 |
  | 8 | | | 0.0005032413015592802 | 0.0006026980498848334 |

  All agree with records/*.json to ≤ 1e-15.
- **RESULTS numbers recomputed from records** (all correct except SHOULD-FIX 1):
  - V1 relative differences: +1.41e-9 (α = 1) and +2.67e-9 (α = π).
  - V2 and V3 inside the A2 windows (PREREG.md:139-140).
  - E_A2 excess 3.15e-9.
  - α = π gap 3.5927% to the lattice and 3.5923% to the record.
  - G: 4.769e-3, 6.684e-2, 0.21556.
  - K = 40 minus K = 30: V3 4.70e-7, H2 3.3e-7, H4 3.1e-7, H8 3.0e-9.
  - Residuals: V1b 9.97e-8, V2 8.9e-11, V3 5.1e-10, H2 1.06e-9, H4 1.08e-10, H8 2.0e-10.
  - Stage bounds at :10 (≤ 1.1e-9 / ≤ 1e-7).
- **Gates versus A2 wording.**
  - V1, V2 and V3 pass at K = 40 under the exact two-sided windows.
  - The H1' prediction "G > 1e-3 at all three α" is met.
  - No B exceeds min(E_FCC, E_BCC), so the run is not void.
  - All K = 40 residuals are ≤ 1e-7, and the tail certificates are ok.
- **Spot-check of solution files.** I re-evaluated V3_K40, V2_K40 and V1b_K40 with lp_bound.GaussLP from the stored
  coefficients: a 4×10^6-point grid on (0, 24] for f − g and on [0, 24] for −f̂, plus bounded polishing of local
  maxima, plus an independent 50-digit mpmath Laguerre evaluation at the argmax.

  | Case | max(f − g) | max(−f̂) | B (recomputed) |
  |---|---|---|---|
  | V3 | 5.0961462e-10 (r = 2.782) | 7.6511129e-11 | 0.22321782493066636 |
  | V2 | 8.8958724e-11 | 6.3885082e-11 | 0.1595952701091433 |
  | V1b | 9.9717907e-8 | 6.3780299e-9 | 0.08643481144375165 |

  All values are identical to the stored ones.
- **"Not certified / numerical" labelling.** The phrase appears in the RESULTS title (:1), at :9, :45-46 and :50, and in
  the commit messages of 968dd32 and 350bc74. Nothing is presented as new. The α = π gap is credited to the
  literature (RESULTS.md:47), and the α = 2, 4, 8 values are flagged "not found published (search not exhaustive)". A
  quick alphaXiv search (Gaussian core model + LP bound) found no published d = 3 values at α = 2, 4, 8 either; this
  was not exhaustive.
