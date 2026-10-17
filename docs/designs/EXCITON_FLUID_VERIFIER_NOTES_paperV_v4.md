# Paper V version 4: hostile referee notes (pre-deposit, 2026-10-17)

Scope: `git diff c977fa7 4f56b35`, which covers `paper/exciton_fluid_gated_V_h1d.tex` (new), the edits in
`paper/exciton_fluid_gated_V.tex`, `paper/zenodo_metadata_exciton_gated_V.json` and `scripts/pack_exciton_gated_V.py`.

I checked these against the following sources:
- `exploration/exciton/three_d/H1d/`: RESULTS.md, summary.json, all 29 records (`certificate.UB_upper`), DEVIATIONS.md, PREREG.md and DESIGN.md;
- `H1ppp/RESULTS.md`;
- the two H1d reviews and their responses;
- LEDGER CLAIM-130;
- arXiv:2206.09876 abs page (fetched this session).

Nothing in the repository was edited except this file.

**Verdict: no BLOCKING item.**
- Every printed number is a valid bound in the conservative direction.
- The method paragraph is mathematically correct.
- The scope wording follows the revised RESULTS.md.
- The paper compiles cleanly.

The main defect is that stale version-3 sentences now contradict version 4. Three should be fixed before deposit (SF-1).

## 1. Numbers (all re-derived from records with exact Fractions)

UB values come from each record's `certificate.UB_upper` (the 256-bit upper end). B values come from H1''' K=50.
Lattice values come from summary.json.

| α | UB_upper (record) | paper | B | paper | margin 1−UB/min | paper | UB − record |
|---|---|---|---|---|---|---|---|
| π | 0.22428666410755588 | 0.2242866642 (up) | 0.223217819358967 | 0.2232178193 (down) | 3.13109% | 3.13% | −0.0072487 → 0.00724 (down) |
| 2 | 1.0116485640657997 | 1.0116485641 (up) | 1.01101824668405 | 1.0110182466 (down) | 0.414845% | 0.414% | |
| 4 | 0.073429356907592 | 0.07342935691 (up) | 0.0727564554394576 | 0.07275645543 (down) | 5.82076% | 5.82% | |
| 8 | 0.00041090208014604 | 0.0004109020802 (up) | 0.00039476028934256 | 0.0003947602893 (down) | 18.3490% | 18.3% | |

- min(FCC, BCC) column, h1d.tex:32–35: the values are correct to the printed digits. The α = π value 0.2315362662 is rounded up from …18415, which is harmless because it is a reference value, not a bound.
- V1 7.25e-8 is printed as 7.3e-8 and V2 0.706% as 0.71%. Both are rounded up, which is fine for "within" and "above".
- Abstract bracket [0.2232178, 0.2242867]: correct directions.
- Metadata numbers: identical to the paper's, and correct.
- 29/31 certified: 3 V1 + 4 V2 + 24 D3 = 31. The two failures, D3pi (8,48) and D3a8 (6,48), match the logs and summary.json.
- Prediction "α = 2 smallest margin": holds (0.414% < 3.13% < 5.82% < 18.3%).

## 2. Mathematics of the method paragraph (h1d.tex:6–19)

I re-derived it and found it correct.
- The Poisson step and folding are correct. Ĝ(y) = s^d Σ_k ĥ(s(k + y/m)) ≥ 0, and Ĝ(0) ≥ s^d ĥ(0) because ĥ ≥ 0. This gives ĥ(0) ≤ s^{-d} Σ G.
- For x ≠ 0, G(x) ≤ Γ(x). Also G(0) ≤ h(0) + Γ(0).
- Weak duality is correct. Σ_y λ(y) Ĝ(y) = Σ_x G(x) Σ_y λ(y) cos(2π⟨x,y⟩/m), because G is real and even (real positive-definite h is even).
  - The coefficient of G(0) is s^{-d} + Σλ − 1, which forces Σλ = 1 − s^{-d}. The paragraph has this.
  - The coefficients for x ≠ 0 are μ(x) ≥ 0, so UB = Γ(0) + Σ_{x≠0} μ Γ.
  - Signs and normalisation are as written.
- s > 1 is needed so that Σλ ≥ 0 is possible. Rationality of s is only an implementation convenience.
- The lemma summary (Gaussian damping, weak Poisson summation, radialisation) matches RESULTS.md and the results review's check.
- The scope is correctly limited to CdCI Prop. 2.2. The text says Cohn–Kumar's wider formulation is not claimed, and the post-registration status is stated.

## BLOCKING

None.

## SHOULD-FIX

**SF-1. Stale version-3 statements now contradict version 4.**

The diff added v4 text but left three v3 sentences that state, in the present tense, that the non-sharpness is not certified.
- `paper/exciton_fluid_gated_V.tex:66–67` (abstract): "that two-point bounds cannot do better remains numerical."
  Fix: change it to "...remained numerical in version~3." This also makes the next sentence ("Version 4 adds the missing direction") read as a resolution.
- `paper/exciton_fluid_gated_V_h1pp.tex:65–68`: "which we did not compute. That statement remains numerical, as in version~2 (...)".
  Fix: append after the parenthesis: "\emph{Version~4 supplies this upper bound (Sec.~\ref{sec:h1d}).}" Alternatively, change "remains" to "remained, in version~3,".
- `paper/exciton_fluid_gated_V.tex:285–286` (bullet "Version~3"): "that two-point bounds cannot settle these cases is not certified (it would need a dual certificate)".
  Fix: change it to "...was not certified in version~3 (it needs a dual certificate, which version~4 supplies)".

The historical sentences about version 2 can stay as they are: lines 60–62, 252–256 and 281–282, and the metadata's v2/v3 paragraphs. They are explicitly about earlier versions. The metadata's v3 paragraph says "remains numerical (it would need a dual certificate)". Change it to "remained numerical in version 3" for the same reason (`paper/zenodo_metadata_exciton_gated_V.json:6`).

**SF-2. Abstract headline is unscoped.** `exciton_fluid_gated_V.tex:69–71` reads "the two-point bound provably cannot prove FCC or BCC optimal there".
- The bullet (line 288–289) and the metadata say "in the form of CdCI's Prop. 2.2".
- The abstract does not say this. It also does not say that the full Prop. 2.2 class relies on a post-registration lemma (PREREG: "Not claimed: anything about functions outside 𝓗").

Fix: change it to "so the two-point bound (in the form of~\cite[Prop.~2.2]{CdCI16}) provably cannot prove FCC or BCC optimal there". Optionally add "(the registered class assumed decay; a lemma added after registration removes that assumption)". Add the same scope note to the bullet at line 288–290: "(registered for a decaying class; extended to Prop. 2.2's class by a post-registration lemma, Sec.~\ref{sec:h1d})".

**SF-3. Evaluator-fix disclosure is incomplete in the paper.** `h1d.tex:45–47` says the fix was made "before evaluation, when 21 of the 31 records existed".
- DEVIATIONS.md item 1 also states that "the D3pi (8, 48) solver failure was already in the log, and per-grid log lines had been seen".
- It also states that the fix added the 1e-12 relative-margin requirement.
- "Before evaluation" without these facts suggests that the outcomes were unknown.

Fix: change it to "...when 21 of the 31 records existed, one solver failure had been logged and per-grid values had been seen in the logs (\texttt{H1d/DEVIATIONS.md}); the fix (any VOID gates all $d=3$ cases; a $10^{-12}$ relative margin required) only tightens the criterion."

**SF-4. Keybox claim now false for H1d (and H1''').** `exciton_fluid_gated_V.tex:105` reads "All gates, restart counts and thresholds were fixed before the runs". H1d added a 1e-12 margin threshold during the runs (1ee1714). Fix: "...were fixed before the runs, except the evaluator changes listed above; deviations are dated...".

**SF-5. "29 of the 31 runs" attached to d=3.** `h1d.tex:26–27` reads "In $d=3$, six grids $(s,m)$ per $\alpha$ were registered; 29 of the 31 runs certified". This reads as 29 of 31 runs in d=3, but d=3 had 24 runs (22 certified). Fix: "...registered (24 runs; with the 7 validation runs, 31 in all); 29 of the 31 certified, and the two failures (...)".

**SF-6. Repository tag and packing state.**
- The metadata notes cite `git tag exciton-gated-5-v4`, but the tag does not exist yet (only `-v3`). Create it on the final commit before packing.
- `exploration/exciton/three_d/H1d/logs_launch.out` (0 bytes) is untracked. RESULTS.md cites its timestamp as evidence of the launch time. `pack_exciton_gated_V.py` uses `git status --short -- PREFIXES`, which lists untracked `??` files, so the manifest will carry a DIRTY warning.
- Fix: either commit the file, or record its mtime (09:33:31) in RESULTS/DEVIATIONS, which already happened, and keep it out of the prefix tree before packing.
- LEDGER CLAIM-130 still says "(not deposited)". Update it after deposit.

## MINOR

- **M-1, `h1d.tex:42–43`.** "The interval $[B,\mathrm{UB}]$ at $\alpha=\pi$ contains the numerically optimised value $0.22321782$". This is literally true, but the paper's own v3 section reports a certified K=60 lower bound of 0.2232178245 (after the lift re-check, h1pp.tex). That value exceeds 0.22321782 read as a number. CdCI print "0.22321782 . . ." (truncated digits), so there is no contradiction. Suggest: "is consistent with the truncated value $0.22321782\ldots$ of~\cite{CdCI16}". Optionally note that the K=60 value tightens B to 0.2232178245.
- **M-2, `h1d.tex:10`.** g is not defined in this section. v3 uses f for the auxiliary function and g for the kernel. Write "$h\le g=e^{-\alpha|x|^2}$ off $0$". Ĝ is also undefined; add "(its discrete Fourier transform on $\mathbb Z_m^d$)".
- **M-3, `h1d.tex:24–25`.** V2 is labelled "(not gated)", but PREREG makes V2 a consistency gate ("no VOID"); only tightness is not gated. The prediction sentence then says "V1, V2 pass". Fix: "V2 ($d=2$, $\alpha=\pi$, consistency gate): no VOID, pass; tightness reported, not gated: $0.71\%$ above $E_{A_2}$."
- **M-4, `h1d.tex:1`.** The header comment says the numbers come from summary.json. The α = 8 UB (0.0004109020802) comes from the record's `UB_upper`. summary.json's `UB_star` is the looser ball-string upper end, 0.000410902080227, which rounds to …0803. Both are valid. Write "summary.json and records/*.json (UB_upper)".
- **M-5, `h1d.tex:20`.** The literature search line "(CdCI, Li, two alphaXiv searches, one web search)" merges two sources. The author's gate (DESIGN.md) ran two alphaXiv searches. The web search and two further alphaXiv searches were the results reviewer's. Suggest "(ours and the results reviewer's: CdCI, Li, four alphaXiv searches, one web search)". The hedging itself is correct.
- **M-6, `zenodo_metadata_exciton_gated_V.json:6`.** "within 7.3e-8 of the exact value" leaves out "relative". The paper says "(relative)". Add it.
- **M-7, `exciton_fluid_gated_V.tex:315`.** The Li bibitem is correct: title, sole author Rupert Li, arXiv:2206.09876, v3 dated 6 Nov 2022. The journal version is Adv. Math. 460 (2024/25) 110043, doi:10.1016/j.aim.2024.110043. Suggest "R. Li, Dual linear programming bounds for sphere packing via discrete reductions, arXiv:2206.09876v3 (2022); \emph{Adv. Math.} 460 (2025) 110043 (journal version not read)". Note that arXiv lists the journal reference as "(2024)".
- **M-8, `exciton_fluid_gated_V.tex:88`.** "about $4\times10^{-6}$ below either pure lattice" is relative: (0.2315362662 − 0.23153532)/0.2315 = 4.1e-6. The absolute gap is 9.5e-7. Version 4 now prints both numbers in the same paper, so add "(relative)". This is pre-existing text.
- **M-9, `h1d.tex:48`.** For symmetry with the pre-run review, add that the results review found no blocking item (5 should-fix and 8 minor items applied).

## 3. Disclosures checked

| item | status |
|---|---|
| 2 solver failures named | present (h1d.tex:27–28; metadata) |
| not rerun | present |
| evaluator fix timing (21/31) | present; see SF-3 for what is missing |
| pre-run review | present (h1d.tex:45) |
| results review | present (h1d.tex:47–48) |
| process section reviews list | present (main.tex:300) |
| post-registration lemma separated | present in the section; missing in the abstract (SF-2) |
| "min(FCC,BCC)", not "best lattice" | yes, in all v4 text |
| α = π stated against the CKS/CdCI record | yes (h1d.tex:39–42, abstract, bullet, metadata) |
| "visible numerically before, certificate new" | yes (h1d.tex:43, metadata) |
| novelty hedged | yes (h1d.tex:20–22, metadata) |

## 4. Compile (scratch copy)

- Location: `.../scratchpad/v4rev/`, with all four tex files and `figs_companion5/`.
- `pdflatex` was run twice, with rc = 0 both times.
- Output: 15 pages, 737 790 bytes, the same size as the committed PDF.
- The final log has 0 warnings: no undefined references or citations, and no overfull or underfull boxes.
- Labels resolve: `sec:h1d` → Section 8, p. 12; `Li22` → [11].

---

## Response (author session, 2026-10-17)

All SHOULD-FIX applied: SF-1 stale v3 sentences now in past tense with a pointer to Sec. h1d (abstract, h1pp section, v3 bullet,
metadata); SF-2 abstract scope (Prop. 2.2 form; full class via the post-registration lemma); SF-3 evaluator-fix disclosure now
states the logged solver failure, seen per-grid values and the 1e-12 margin; SF-4 keybox exception for H1d; SF-5 run counts
split (d=3: 22 of 24); SF-6 tag created at deposit, logs_launch.out gitignored, CLAIM-130 updated after deposit.
Minor: M-1, M-2, M-3, M-4, M-5, M-6, M-8, M-9 applied. M-7 (journal reference for Li) not applied: I have not read the journal
version, so only arXiv v3 is cited.
