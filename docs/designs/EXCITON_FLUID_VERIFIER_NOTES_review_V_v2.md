# Hostile review: paper V, version 2 (uncommitted H1' additions), 2026-10-12

Reviewer: independent agent. The scope is the uncommitted diff of `paper/exciton_fluid_gated_V.tex` and
`paper/exciton_fluid_gated_V_round2.tex` against HEAD 49e242d, plus the compiled PDF (pdftotext, built 21:20:05,
after both .tex files). The sources checked were `exploration/exciton/three_d/H1p/{PREREG.md (A1, A2), DEV_NOTES.md,
RESULTS.md, records/*_K40.json}`, `docs/designs/EXCITON_FLUID_VERIFIER_NOTES_review_H1prime.md` and git log.
arXiv:1603.09684v6 was read through alphaXiv (pp. 1-6, 11, 20, 23-29). No repo file except this one was edited.

## Verdict

There is one BLOCKING item: a v1 sentence that v2 makes false, with a one-line fix. Every number and hash in the new text
checks out, with one exception (SHOULD-FIX 4). The other items are missing caveats and stale cross-references.

## BLOCKING

1. **A v1 sentence is now false.** `exciton_fluid_gated_V_round2.tex:130` still says "and the $d=3$ gap has no value in
   this paper". In v2 the paper does give d = 3 values: Sec. 6 has 0.2232178249 at α = π and the gaps at α = 2, 4, 8.
   The "Note added in version 2" (:135-138) comes after it in the same paragraph, but it does not retract the sentence.
   Suggested fix: "and H1 gives no $d=3$ value (see Sec.~\ref{sec:h1p} for version~2)".

## SHOULD-FIX

1. **The abstract overstates the H1' reading.** `exciton_fluid_gated_V.tex:61-62` says "numerically, two-point bounds do
   not settle the 3D question at any $\alpha$ tested". That is a statement about the LP *optimum*. The run has only primal
   solutions with K ≤ 40, a Gaussian times polynomial ansatz and a scanned β. It has no dual or upper bound on the
   optimum, and K = 50 was not run (RESULTS.md: "whether K = 40 is converged was not tested"). The body (:236-237)
   correctly says "at $K\le40$ and with the best lattice as reference"; the abstract drops both qualifiers. Suggested
   fix: "numerically (K ≤ 40, best lattice as reference), our two-point LP values fall short at every α tested".
2. **Caveats from RESULTS.md / the H1' review are missing from Sec. 6.**
   - (a) **The α = 2 reference assumption.** RESULTS.md says: "at α = 2 (G = 4.8e-3) the reading assumes no non-lattice
     state lies more than about 0.4 % below BCC, which we have not checked". The paper only says "with the best lattice
     as reference".
   - (b) **The V3 "8 digits" claim is fragile.** RESULTS.md says: "at 35x, V3's residual 5.1e-10 could mean an excess of
     order 2e-8, comparable to its window". The paper (:235) says "$d=1$ and $d=3$ match the printed 8 digits" without
     this.
   - (c) **K = 40 convergence was not tested** (K = 50 not registered).
   - (d) **The β-selection bias** (the maximum value is chosen among accepted solutions, so the most-violating one is
     favoured; RESULTS Deviation 0) and the α = 8 β optimum not being bracketed. Both are minor, but they belong
     alongside the K = 30 disclosure.
   - (e) **The review sentence claims too much.** :239-241 says the review's "corrections ... are applied". The review's
     item 5(c) (the α = 2 assumption) is applied in RESULTS.md but not in the paper. Either add (a) or narrow the
     sentence.
3. **The keybox "What was pre-registered"** (`exciton_fluid_gated_V.tex:84-88`) lists round 1 and round 2 only, and says
   "All gates, restart counts and thresholds were fixed before the runs". H1' (PREREG d668109, A1 83a3500, A2 968dd32)
   is not listed. A2's 1e-7 acceptance and two-sided windows were set after H1's outcomes were known, though before any
   H1' run; this is disclosed in RESULTS Deviation 0 but not in the keybox. Add an H1' entry with that caveat.
4. **Wrong figure for the K = 30 miss.** :236 says "At $K=30$ the $d=3$ value would miss V3 by $4.7\times10^{-7}$". The
   V3 window is [0.22321781, 0.22321784] (PREREG A2: 0.22321782 − 1e-8). B(K = 30) = 0.2232173547129, so the miss is
   0.22321781 − 0.2232173547 = **4.55e-7**. 4.70e-7 is the K = 40 − K = 30 difference, and 4.65e-7 is the distance to
   0.22321782. RESULTS.md has the same conflation ("would fail V3 by 4.7e-7"). Write "by $4.6\times10^{-7}$" or "lies
   $4.7\times10^{-7}$ below the $K=40$ value, outside the window".
5. **The V2 window is described inaccurately.** The table says "(window $\pm10^{-8}$)" (:223). The registered window is
   [0.15959526 − 1e-8, 0.15959527 + 1e-8] = [0.15959525, 0.15959528] (PREREG A2). That is not ±1e-8 around the printed
   value, and the asymmetry is exactly what lets the d = 2 value pass. V3's window is not given at all. Give both
   intervals explicitly.
6. **The round-2 failbox has no forward pointer.** `exciton_fluid_gated_V_round2.tex:7-9` ("H1: ... was therefore not run
   in $d=3$") is historically correct, but a reader of the summary box is not told that v2 has a d = 3 run. Add
   "(version 2: see Sec.~\ref{sec:h1p})". Do the same in `exciton_fluid_gated_V.tex:200` ("What we can compute is the
   size of the two-point LP gap in $d=3$ (H1, \S\ref{sec:round2})"), which should also cite Sec. 6.
7. **The bibliography entry is preprint-only.** `\bibitem{CdCI16}` (:274) cites "arXiv:1603.09684 (v6, 2018)". The v6
   PDF is dated "February 21, 2018" and stamped "11 Apr 2018". I believe the paper appeared in Duke Math. J. (2018), but
   I did not verify this, so check it and add the journal reference if it holds. The key "CdCI16" next to "2018" is
   cosmetic. (Outside scope: the paper's CKS09 entry is arXiv-only, while 1603.09684 ref. [15] gives Phys. Rev. E 80
   (2009) 061116.)
8. **Provenance in the section header.** :206-207 cites "results 350bc74, review 6f5a1cb". The RESULTS.md the paper
   quotes (residual 6.2e-10, the d = 2 wording, the 35x slack) is the post-review version committed in 6f5a1cb, not
   350bc74. The code freeze 91b1a97 (the driver fix after A2, before any run) is not mentioned. Suggested fix: "results
   350bc74, revised after review in 6f5a1cb; code frozen at 91b1a97".

## Minor

- `exciton_fluid_gated_V.tex:214` says "a high-precision polish did not converge". DEV_NOTES item 3 tested a damped
  Newton prototype at K = 6 (it stalls or diverges). A1's Remez step at K + 1 contacts was found *ill-posed* (item 2) and
  was not run to non-convergence. The statement is acceptable as shorthand, and A2 uses the same words.
- The "What this does and does not show" section has no H1' bullet. The only mention is a parenthesis at :254. Optional.
- No "Overfull" or undefined-reference warnings in `exciton_fluid_gated_V.log`. The PDF renders Sec. 6, both tables,
  "Sec. 6" cross-references and [5] correctly. Changing `thebibliography{9}` to `{99}` is correct (there are now more
  than 9 items).

## Verified OK

- **Hashes (git log).**
  - d668109: PREREG, 19:35:52
  - 83a3500: A1, 19:38:43
  - 968dd32: A2 + run_h1p.py, 20:33:46
  - 350bc74: results, 21:07:32
  - 6f5a1cb: review + RESULTS fixes, 21:14:47
  - All five exist and match the roles the paper gives them (:206-207). "Amendment A2, committed before any gate run" is
    correct: run.log starts at 20:34:03 on code commit 91b1a97.
- **Literature (arXiv:1603.09684v6, p. 5, Table 1.1).**
  - "LP bound" at α = π, ρ = 1: 0.08643481..., 0.15959526..., 0.22321782... (n = 1, 2, 3).
  - "Current record" at n = 3: 0.23153532....
  - The caption reads "the numerically optimized linear programming bound, and the lowest energy currently known (from
    [15] or the expectation bound)".
  - Paper V :208-209 and round2 :136-137 quote these correctly. "numerically optimised" matches p. 4 ("numerically
    optimizing the auxiliary function in the linear programming bound").
  - Prop. 2.2 extends the bound to arbitrary configurations (p. 6: "Here we extend it to arbitrary configurations"), so
    :211-212 is correct.
  - Gap (0.23153532 − 0.22321782)/0.23153532 = 3.59 %, so "3.6%" is correct.
- **Table 1 (:221-224) against records/*_K40.json.**
  - V1a: B = 0.7726372059139668 → 0.7726372059; +1.41e-9 relative to E_Z = 0.7726372048267.
  - V1b: B = 0.08643481144375165 → 0.0864348114; +2.67e-9 relative.
  - V2: B = 0.1595952701091433 → 0.1595952701.
  - V3: B = 0.22321782493066636 → 0.2232178249.
  - All four have accepted_numerical = true.
- **Table 2 (:228-230) against H2/H4/H8_K40.json and RESULTS.**
  - B = 1.0110182867, 0.07275645512, 0.0003947635566.
  - E_FCC and E_BCC as printed.
  - Gaps recomputed: 4.769e-3, 6.684e-2, 0.2156, giving 4.8e-3, 6.7e-2, 0.216. The abstract's 0.48 %, 6.7 %, 21.6 % are
    consistent.
- **Reading paragraph.**
  - The d = 2 excess over E_A2 is 0.1595952701091 − 0.1595952669639 = 3.15e-9 ("3.1e-9").
  - V2 residual max(8.90e-11, 6.39e-11) = 8.9e-11 ("9e-11").
  - "d = 2 passes only through the registered window" agrees with RESULTS.md.
- **The DEV_NOTES claim at :213-214** ("controls f only up to x≈3; (f−g)/g reaches 3e43 at x=8") matches DEV_NOTES item 2
  ("touches g at ... x = 1, 2, 3", "2.9e43 at x = 8").
- **"not certified" / "numerical, non-rigorous" labelling** appears in the abstract (:60), the section title, :215 and
  :233 ("LP objectives, not bounds"). "New only in the sense that we did not find them published" matches RESULTS.md.
  Nothing is presented as certified or as new mathematics.
- **"we had not found this before registering H1"** (round2 :137-138) is consistent with the record: there is no mention
  of 1603.09684 or de Courcy-Ireland in PREREG_round2.md (51a85b1) or in H1/.
- **Process line (:265)** lists reviews for round 1, round 2, F1 and H1'. All four files exist in docs/designs/.
- **The v1 conclusion bullet edit (:254)** ("not certified at the $10^{-8}$ level (version~2: it reproduces published
  values numerically ...)") is accurate.

## Resolution (author, 2026-10-12)
B1 fixed (round2.tex: "H1 gives no d=3 value (see Sec. h1p, added in version 2)"). S1 abstract now "at polynomial degree <= 40
and with the best lattice as reference". S2 caveats added to Sec. 6 (alpha=2 reference, 35x slack for V3, K=50 not run,
beta selection, alpha=8 not bracketed). S3 keybox lists H1' with A2's post-hoc tolerance. S4 4.6e-7 (paper and RESULTS.md).
S5 both windows stated. S6 forward pointers added (failbox, holography section). S7 journal reference not verified, so the
bibitem stays arXiv-only. S8 provenance names 91b1a97 and "after review 6f5a1cb". Minor: polish wording made precise; H1'
bullet added to "What this does and does not show".
