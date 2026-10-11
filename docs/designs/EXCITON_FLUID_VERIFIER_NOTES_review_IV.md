# Hostile review of paper/exciton_fluid_gated_IV.tex (Gated exciton fluids IV)

Verdict: the headline conclusions (all three gates not met; no E1 benefit; E2 gate not met; E3 CM worse than CVT at p5) reproduce from raw records.
No number in the paper is wrong beyond rounding. There are no blocking scientific errors; there are process blockers (uncommitted data) and several
major wording/omission issues to fix before the permanent deposit.

## What I re-did
- Re-ran analyse.py on a copy of results/: output identical to committed summary.json (json equality True).
- Recomputed from raw jsonl: per-method counts, escaped, analysis_error, euler_ok; paired differences; fixed-wall-only best-energy fractions; E3 paired stats.
- Timestamps: A1 commit fa8ac03 17:39:06, first registered record file born 17:39:18 (OK). A2 commit 1cbf233 17:41:19, e3 jsonl born 17:41:25 (OK).
  A3 commit 599e7ad 19:46:27, disc rerun born 19:46:33; square (17:39-17:46) and hexagon (17:46-17:52) finished ~2 h before A3 (OK).
- A3 behaviour-preservation: re-ran dimlift.one with current code for square seeds 0-5 x {direct,lift1,lift2} (18 runs): E, evals, escaped, n_non6 bit-identical to stored.
  So the claim "square ... predate A3 and are unaffected" holds for the square. (Hexagon not re-run; 6 edges, same code path as square; likely identical.)

## Numbers checked and found correct
Failures (7/8 square; lift1/lift2 2/4 L-shape, 1/3 rect2; none elsewhere); eval ratios 6-17; E2 means and SEs (all nine); Q change 0-40%;
E3: medians 0.199/0.633/0.677, frac<0.3 12.06%/0.53%/0.53%, CM-CVT p5 = -0.0450 +- 0.0072, 3/30 wins; N=216, 30 seeds.
"best-of-m lower than lifted mean in all nine" true for lift1 and lift2 (18/18). Failure rule applied identically in analyse.py to all methods (direct/slide never fail).

## BLOCKING (process, fix before deposit)
B1. Data not committed. git status: all of results/e12_dip_{disc,rect2,lshape,annulus}.jsonl and e12_g3_*.jsonl are untracked; summary.json and e12_progress.txt are modified;
    the paper, PDF, figs_companion4/, companion4_figures.py are untracked. The paper says "Records are in results/". Commit (and tag) before the DOI.
B2. "the review of this paper ... [is] in docs/designs/": no such file exists (only review_III / note / companion). Either add this report there or drop the clause.

## MAJOR
M1. E2 sentence "it is met on one (square, within one and a half standard errors of the boundary)" is wrong/misleading. Square mean -2.23 +- 1.50: it is 0.15 SE from the
    -2 threshold and 1.49 SE from zero. The intended statement is "met by the point estimate but not distinguishable from no change at 1.5 SE". Rewrite.
M2. "Fraction of starts reaching the best energy" is vacuous as computed. analyse.py takes `best` over all methods including slide, which is lower by construction, so
    frac_best_of_all is 0.00 for direct and both lifts on 5 of 9 cases and the registered gate piece "fraction not lower" is trivially true there (0>=0).
    Restricting to fixed-wall methods (my recomputation): direct/lift1/lift2 = annulus .43/.40/.53, disc .50/.40/.33, hexagon .03/.07/.10, lshape 0/.07/.10, rect2 .03/0/.03,
    square .23/.27/.17, g3-disc .43/.37/.27, g3-hex .07/.03/0, g3-square .27/.17/.13. The paper's conclusion survives (no consistent gain) but the sentence must be backed by
    the fixed-wall metric, and summary.json's numbers should not be quoted for it. Also the registered "number of distinct minima" is recorded in the prereg but never reported
    (fixed-wall distinct minima direct/lift1/lift2: e.g. rect2 23/15/13, lshape 20/23/15, g3-square 13/18/11).
M3. Unamended deviation from PREREG: E3 CVT uses 1.5e5 MC samples per Lloyd iteration (mesh3d.py ns=150000); PREREG says 200k and A2 does not mention changing it. The paper states 1.5e5 without
    flagging the deviation, and says A2 is only "N=216". Add a disclosure (direction: the noisier CVT, if anything, handicaps CVT, so the negative CM result is not helped).
M4. A3 text says the vectorisation "does not alter any value the algorithm computes" and that two disc seeds matched. My comparison of the 76 slow-harness disc records with the
    rerun: direct 20/20 and slide 19/19 bit-identical, but lifted runs differ in every case in eval count and in 15/37 in final energy (up to 0.12 in E, different minima; mean
    lift1 170.2344 old vs 170.2247 new). The change is not bit-preserving for the 2000-edge disc (floating-point re-association amplified by chaotic L-BFGS), only statistically
    equivalent. For the square (4 edges) it IS bit-preserving (18/18). So: the paper's statement about square/hexagon is fine, but the A3 sentence should read "numerically equivalent up to
    rounding; trajectories of lifted runs on many-edge containers can differ", and the 76 discarded records are a useful replicate to mention (their means agree within noise).
M5. E3 reporting is selective about the metric. Registered gate metric (p5 radius ratio) favours CVT, but on worst-case metrics that matter for meshes CM is better by median over 30 seeds:
    min radius ratio 0.112 vs 0.086, min dihedral 5.9 deg vs 4.4 deg (CVT better on p5 dihedral 36.8 vs 35.0). The "What this does and does not show" bullet "CM relaxation is ... not better than CVT as
    measured" and the abstract "slightly worse" omit this. Report both; the gate verdict itself is unaffected.
M6. Fairness caveat for E1 that should be stated (it goes in the safe direction, which strengthens the conclusion): (i) eval ratio understates wall-clock cost (secs ratio lift/direct 12-30x
    vs eval ratio 6-17; lift2 on g3 7x vs 6x), so equal-evals control gives direct fewer restarts than equal time; (ii) lifted means exclude failed runs, whereas escaped runs
    have spuriously low energies (e.g. square seed 0 lift2: E=190.21 with 2 nodes escaped, seed 3 lift1: 185.53 with 4 escaped); excluding them is correct but a failed attempt still costs its full
    compute and is not penalised in the equal-compute comparison; (iii) the bootstrap best-of-m from only 30 direct energies cannot go below the sample minimum (conservative for the control).
    The paper's fairness is fine; say why. Also say that failures concentrate on shapes with corners and arise in the harness' final unpenalised polish after projecting to 0.02 from the wall (nodes
    slip between wall nodes), i.e. they measure the harness, not the heuristic.

## MINOR
m1. Figure: placed above the title, no caption, no label; text cites "Fig. panel a". The orange squares are the best-of-m control for lift1 only (lift2's m differs, e.g. disc 6 vs 7, g3 6 vs 12) and
    carry no error bar; error bars on blue/purple are unpaired hypot SEs. Panel labels vs data are otherwise correct (a: E_lift - E_direct, sign convention checked on dip-square: lift1 -0.0088,
    lift2 -0.0021; b: values equal E2 numbers; c: 30 starts, 3 positive). Add a caption.
m2. Gate wording: paper's E1 gate omits the registered conjunct "fraction reaching best energy not lower", "for k=1 or k=2" and that the gate is defined on the six dip shapes only (g3 cases are extra). Quote PREREG exactly.
m3. E2: dE is not reported. Mean dE>0 on disc (+0.0102) and annulus (+0.0025), i.e. the sliding minimum is on average HIGHER than the fixed-wall one on 2 of 9 cases, so "lower by construction"
    holds only for global minima. (The 4000-gon circle discretisation offset is 9e-5, too small to explain it.) State this.
m4. Explanation "sliding changes the boundary coordination, hence Q" is stated as fact, not tested; also PREREG expected Q unchanged where wall coordination unchanged - say that this expectation
    was not borne out (Q changes in 33-40% of square/L-shape/g3-square).
m5. "The numbers in this paper are generated by analyse.py": the E3 mean difference 0.045 +- 0.007 is not an analyse.py output (only the win count and medians are); the figure script prints the mean but not the SE. Add it to analyse.py or reword.
m6. A1 says development runs on square seeds 0-5 were "not used in any result", but seeds 0-5 are among the registered 30 square starts and A1 tuned sigma (0.3->0.1), kappa, margin on them. Similarly seed 0 of E3 was seen (A2 says so; paper does not). One sentence each.
m7. g3-hexagon lift2 is significantly WORSE than direct in a paired comparison (mean +0.031, t=-2.95); "no benefit" is correct, "no harm" is not implied. Optional mention.
m8. Equal-compute logic uses unpaired SE; paired SEs are similar, no gate decision changes (paired t for lift better than direct max +1.1).
m9. Pronouns: only "Our own analysis" (line 46); acceptable given the AI disclosure, but it is a note written in French by the same author/AI; consider "the project note".
m10. Scope statements ("say nothing about excitons, string theory or the universal-optimality theorem", "not tested" items) are properly hedged; no overclaim found. "Both relaxations are far better than Poisson" is fine.
