# Hostile review: paper V version 3 (H1'' + H1''') before the Zenodo deposit

Reviewer: independent instance, 2026-10-17. Scope: commits 162dfc3, c24530e, ca68477, 04964e5 (`git diff 4bc6bcc..HEAD`),
`paper/exciton_fluid_gated_V.tex`, `paper/exciton_fluid_gated_V_h1pp.tex`, `paper/zenodo_metadata_exciton_gated_V.json`,
`LEDGER.md` CLAIM-129, `exploration/exciton/three_d/H1ppp/*`, `../H1pp/*`, `../H1p/*`. I did not edit any repository file except
this one. My scratch scripts were in the session scratchpad (`recheck/recert2.py`, `recheck/k60.py`); the core of the
re-certification is in the appendix so it can be committed.

**Verdict: do not deposit as is. Two BLOCKING items.** (1) The frozen certificate code is unsound in one specific way, and one
of the five H1''' records (V3, K = 60) is **not a valid certificate as recorded**. The other four H1''' records and all 14 H1''
records pass my independent re-check, so the gate and the alpha = 2, 4, 8 numbers are right. The paper still has to say this.
(2) The headline reading "two-point bounds at this degree do not decide ... now certified" does not follow from certified
*lower* bounds.

Every number in the new text, RESULTS.md, the metadata and CLAIM-129 matches the records (item 1 of the brief). The only
deviations are the rounding issues listed under MINOR.

---

## BLOCKING

### B1. The certificate code misses negative regions of f̂; the V3 K = 60 certificate is invalid as recorded

**Where:** `exploration/exciton/three_d/H1ppp/rig3.py:271-281` (and the identical `../H1pp/rig2.py`). Affected text:
`paper/exciton_fluid_gated_V_h1pp.tex:12-17, 29-40, 50-53`; `H1ppp/RESULTS.md` table row "V3 | 60"; metadata
"K=60 gives 0.2232178245"; CLAIM-129 "K=60 (reported) B=0.223217824549473".

**What is wrong.** At an LP optimum Q has near-double roots: pairs of simple real roots a few double-precision ulps apart, with
Q < 0 strictly between them. `certify()` builds its f̂-check intervals from **float-rounded** root-ball endpoints (`lo_`, `hi_` =
`float(mid) ± float(rad)`, not rounded outward). It tests the sign of each gap at a **float** midpoint and checks only the root
balls themselves, whose widths are about 1e-24. When the two roots of a pair round to the same or adjacent floats, the gap test
`hi > lo and Q(mid) < 0` is false, and the negative well between them is never checked. A second, smaller hole:
`prove_upper_enc` (`rig3.py:381-398`) uses a float midpoint `m` with radius `(a1-a0)/2·(1+1e-12)`. That does not cover the
box once the box is narrower than about 1e-4·m, because the midpoint rounding error of about 1e-16·m is then larger than the
1e-12 inflation.

**Evidence.**
- Near-double roots of Q in every H1''' record (scratch `roots.py`). Example, V3 K=50:
  `[9.639716476409986967155419 +/- 1.76e-25] [9.639716476409992296225937 +/- 2.53e-26] gap 5.3e-15`. There are 10 to 13 such
  pairs per record, with gaps of 1.8e-15 to 5e-12.
- V3 K = 60: the record has `delta = 0.0` (no lift) and `lam_used = 3`. Exact rational evaluation of Q at the exact midpoint of
  each pair (scratch `k60.py`) gives **13 negative wells, none checked by rig3**:
  ```
  neg well between [9.6397162378822756068 +/- 7.54e-21] and [9.6397162378822773832 +/- 3.57e-20]: Q(exact mid)=-2.670e-32; ... gap-interval checked by rig3: False
  ...
  neg well between [181.87099022064006704 +/- 3.04e-18] and [181.87099022064009546 +/- 1.72e-18]: Q(exact mid)=-3.124e-02; ... checked by rig3: False
  neg well between [210.54087886749556446 +/- 3.84e-18] and [210.54087886749559288 +/- 4.93e-18]: Q(exact mid)=-9.891e+03; ... checked by rig3: False
  negative wells: 13
  ```
  Q < 0 at an exact rational point means f̂ < 0 there. Prop. 2.2's hypothesis (h positive definite) **fails** for the
  recorded K = 60 function, so `certified: true` in `records/V3_K60.json` is wrong.
- I re-certified independently (appendix). Box radii cover each box exactly, root balls are converted to floats with outward
  rounding, overlapping padded balls are merged into clusters, every cluster is checked, and so is every inter-cluster gap
  where Q < 0 at an exact rational point. I used each record's own `tau0`, `lam_used` and `delta`:
  ```
  H1ppp/V3_K50  recert B_lower [0.22321781935896701972 +/- 4.32e-21] | record [0.223217819358967019715 | record delta OK
  H1ppp/V3_K60  recert B_lower [0.22321782454947327902 +/- 3.14e-21] | record [0.223217824549473279023 | RECORD DELTA FAILS (check failed near 9.639716237882276: [+/- 2.14e-31]); delta=1e-25 proves
  H1ppp/H2_K50  recert B_lower [1.0110182466840527323 +/- 4.32e-20]  | record [1.011018246684052732343 | record delta OK
  H1ppp/H4_K50  recert B_lower [0.072756455439457619829 +/- 8.76e-23]| record [0.072756455439457619828 | record delta OK
  H1ppp/H8_K50  recert B_lower [0.00039476028934255962642 +/- 2.56e-26] | record [0.000394760289342559626 | record delta OK
  H1pp/V3_K40   recert B_lower [0.22321778947320024283 +/- 4.90e-21] | record [0.223217789473200242825 | record delta OK
  ```
  All 14 H1'' records (V1a/V1b/V2/V3/H2/H4/H8 × K30/K40) also give "record delta OK", with B equal to the record to 20 digits.
  So: **the gate (V3 K = 50) and the registered alpha = 2, 4, 8 results are valid certified bounds.** The tiny positive lift
  that rig3 happened to choose covers the unchecked wells, but rig3 never proved this; my re-check did. **V3 K = 60 is valid
  only with a lift (delta = 1e-25 suffices), and B is unchanged to 20 digits.** The numbers survive. The claim "certified by
  the frozen code" does not, for K = 60.
- My re-check reuses rig3's `make_encloser`, which I read (`rig3.py:360-378`: Taylor shift plus a rigorous exponential
  remainder; correct), and flint's `complex_roots`, which returns real roots with an exactly zero imaginary part.

**Fix.**
1. Add a disclosure paragraph to `exciton_fluid_gated_V_h1pp.tex` (after the table) and to `H1ppp/RESULTS.md` (as a deviation
   or post-hoc finding), for example: "A hostile review found that the frozen certificate code (rig2/rig3) does not check
   f̂ ≥ 0 between near-double roots of Q whose enclosures round to the same or adjacent doubles. It also uses float box
   midpoints that do not cover narrow boxes exactly. An independent re-check with exact covering and outward-rounded root
   enclosures (`H1ppp/recertify.py`) confirms all H1'' certificates and the H1''' K = 50 certificates with their recorded
   lifts. The V3 K = 60 record (lift δ = 0) is **not** a valid certificate as recorded, because f̂ < 0 on 13 sub-ulp intervals.
   With δ = 10^-25 it is, and B is unchanged to 20 digits."
2. Commit the re-check script (appendix) and its output. Do not edit the frozen `rig3.py` or the records. Mark V3 K = 60 in
   `summary.json`/RESULTS as "certified after re-check (lift added)".
3. In the method paragraph (`h1pp.tex:12-17`), make clear that "certified" now rests on the frozen certificate plus the
   independent re-check.

### B2. Certified lower bounds cannot show that two-point bounds "do not decide" the question

**Where:** `paper/exciton_fluid_gated_V_h1pp.tex:48-50` ("Version 2's numerical statement --- two-point bounds at this degree
do not settle the three-dimensional Gaussian-core question at α=2,4,8 --- now holds with rigorous bounds");
`exciton_fluid_gated_V.tex:270-272` ("Version 3 ... certifies those gaps ... They restate a known limitation of two-point
bounds with certificates"); metadata ("two-point bounds at this degree do not decide the 3D Gaussian-core question there, now
with rigorous bounds"); `H1ppp/RESULTS.md:24-25` ("does not decide ... now certified rather than only numerical");
CLAIM-129 ("two-point bounds at this degree do not decide FCC/BCC optimality, now certified").

**What is wrong.** A certified B is a valid *lower* bound: it shows that the optimal two-point bound is **at least** B. "Two-point
bounds at degree 50 do not decide" is a claim that the optimal two-point bound at that degree, over all admissible f and all
b, is **below** the lattice energy. That needs an *upper* bound on the LP optimum, i.e. a certified dual solution. None was
computed. The b values were not even re-optimised (`h1pp.tex:55-56` concedes this). What the run certifies is that **these
particular** functions give bounds 0.48 %, 6.7 % and 21.6 % below the best lattice. The H1'' pre-registration's reading
("G > 1e-3 at all three α → two-point bounds insufficient at these α (certified)") had this logical gap built in. The registered
reading cannot be stated as a certified conclusion.

**Fix.** Replace those passages with wording like: "certified lower bounds that lie 0.48 %, 6.7 % and 21.6 % below the best
lattice. Certification makes the bounds rigorous. It does not make the insufficiency of two-point bounds rigorous, which would
need a certified upper bound on the LP optimum (a dual certificate) that we did not compute. That two-point bounds do not
settle these cases remains a numerical statement (H1', and CdCI Table 1.1 at α = π)." In "What this does and does not show",
replace "certifies those gaps" and "restate a known limitation ... with certificates" with "certifies the bound values; the
gaps remain an upper bound on the true two-point gap at this degree, and the limitation itself is not certified." Make the
same change in the metadata, RESULTS.md and CLAIM-129. Add a sentence saying the registered reading in H1''/PREREG.md
overstated what a lower bound can show.

---

## SHOULD-FIX

### S1. "accounted for by truncation in K" and "not needed" overclaim

**Where:** `h1pp.tex:51-53`; `H1ppp/RESULTS.md:35-38`; metadata ("so the K=40 shortfall is accounted for by truncation");
CLAIM-129.

**Evidence.** H1' at the **same K = 40 and the same b = 0.85** (H1 code, same K semantics: `../H1/lp_bound.py:143-156`, c_K = 0
for even K, effective degree 39) gave 0.22321782493 (`H1p/records/V3_K40.json`). That is 3.55e-8 *above* H1'''s certified K = 40
value 0.22321778947 and essentially equal to the K = 60 certified value. H1'''s own K = 40 LP objective is already low
(`H1pp/records/V3_K40.json` `bound_hp = 0.22321778947332832`), so the shortfall sits in the H1'' **formulation** (for example
the R ≤ −10^-12 rows on [u1, ∞) and the top-coefficient margin), not in certification. Two explanations remain and are not
separated: (a) H1' overshot by 3.5e-8, about 70× its residual (H1p RESULTS observed up to 35×); (b) H1'''s gcut/tail restriction
costs about 3e-8 at K = 40 and is compensated by raising K. Note that at b = 17/20, κ < 0 and f ≤ g beyond u1 allows
R ≤ e^{κu}β^{-3/2} ≈ 0.016 β^{-3/2} at u1, so "R < 0" is a real restriction. The monotone rise with K shows that raising K
*suffices*. It does not show truncation is *the* cause, and the gcut candidate is not "not needed".

**Fix.** "B(V3) rises monotonically with K; raising K alone, with b, rows and gcut fixed, brings the certified value into the
window. This does not identify the cause of the K = 40 shortfall: H1''s uncertified K = 40 value at the same b was already at
0.2232178249, so the H1'' formulation (tail/gcut rows, snapped b) may cost as much as degree does. These candidates were not
tested."

### S2. "consistent with the published digits being truncated" does not discriminate

**Where:** `h1pp.tex:52-53`; `H1ppp/RESULTS.md:38-39`.

**Evidence.** K = 60 gives 0.2232178245495. To 8 decimals that **rounds** to 0.22321782 as well, since it is below
0.223217825. The observation is therefore consistent with rounding too and tells us nothing about truncation. CdCI print
every table entry with a trailing ellipsis ("0.22321782 . . ."), which suggests truncation by notation, but the data do not
test it.

**Fix.** Delete the sentence, or say: "K = 60 exceeds 0.22321782 by 4.5e-9. This is compatible with the printed value
whether it was truncated or rounded."

### S3. Reviews of H1'' and H1''' claimed to be in the repository

**Where:** `exciton_fluid_gated_V.tex:282` ("the reviews (... in version 3 H1'' and H1''') are in the repository").

**Evidence.** `git ls-files | grep -i 'VERIFIER\|review' | grep -i h1` returns only
`docs/designs/EXCITON_FLUID_VERIFIER_NOTES_review_H1prime.md`. Commit 25eecce applied "H1'' review fixes", but no review
file for H1'' was committed.

**Fix.** Commit the H1'' review notes and this file before packing, or change the sentence to name what actually exists.

### S4. "What was pre-registered" box not updated for version 3

**Where:** `exciton_fluid_gated_V.tex:89-98` (keybox). It lists version 2 (H1') only.

**Fix.** Add: "Version 3: H1'' (`three_d/H1pp/PREREG.md`, b1d2de5) and H1''' (`three_d/H1ppp/PREREG.md`, 1e50f4b; evaluator
replaced mid-run, 162dfc3, see DEVIATIONS.md)."

### S5. "polynomial degree 40/50" versus effective degree 39/49

**Where:** abstract `exciton_fluid_gated_V.tex:63-64` ("at polynomial degree 40 ... at degree 50"); bullet `:270`
("polynomial degree 50"). The method text (`h1pp.tex:8`) correctly says "odd effective degree 39 at K = 40". The records
have `K_eff = 49` (and 59).

**Fix.** "at K = 40 (effective polynomial degree 39) ... at K = 50 (degree 49)", or use "K = 40/50" throughout.

### S6. "our LP code ... version 3 certifies at K = 50" conflates two codes

**Where:** `exciton_fluid_gated_V.tex:266`. The H1 code (`H1/lp_bound.py`) is still uncertified. Version 3 uses a different code
(`rig2/rig3.py`, `hp_lp.py`). Also `:248`: "version 3 supplies it" should carry the B1 qualification.

**Fix.** "... and our original LP code is not certified at the 10^-8 level (version 2 reproduces published values numerically
with it; version 3 uses a new, interval-certified construction, Sec. ...)."

### S7. Uncertifiable later rounds not mentioned

**Where:** `H1ppp/RESULTS.md`, `h1pp.tex:17`. In V3 K50 and H2 K50, rounds 14-17, and in H4 K50, rounds 14-18, the certificate
failed (`RuntimeError('fhat check failed for every lam')`). The reported B is from round 13 (H8: round 11; V3 K60: round 17).
This is allowed by the registration ("best certified B over rounds"), and the LP objective did not change after round 9-12.
It is still a material fact about how fragile the certificate is.

**Fix.** One sentence: "In three of the five runs the last 4-5 rounds' vectors could not be certified (f̂ check failed for every
λ); the reported values are from rounds 13, 17, 13, 13, 11. By then the LP objective had stopped changing."

---

## MINOR

- M1. `h1pp.tex:34` "(10 h at most)": the wall time was 19:41 to 05:53 = 10.2 h, and H4 `solve_s` = 36 699 s = 10.19 h. Write
  "about 10 h".
- M2. `H1ppp/RESULTS.md:5` "certification 1-5 s": the records give 1.37 to 5.36 s (V3 K60 5.36). Write "1.4-5.4 s".
- M3. CLAIM-129: "Prediction 'within 1e-6 of H1'' numerical values'": this should say H1' (the doubled prime reads as H1'').
- M4. `h1pp.tex:1` comment "Numbers: ... H1pp/summary.json": the section also uses H1ppp/summary.json.
- M5. `H1ppp/run_h1pp.py:1-2` docstring is stale ("K in 40 30", "Gates are evaluated by evaluate.py"). The driver also adds
  skip-if-record-exists logic (lines 29-31) beyond "rig3 = rig2 + ckpt". It is harmless, but PREREG's "only" is not literal.
- M6. Energy convention: CdCI Definition 1.1 sums over **ordered** pairs x ≠ y divided by the number of points (a lattice has
  Σ_{x∈Λ∖0}). The lattice sums and E_Z here use the same convention (`H1pp/evaluate.py:16-17`; V1 agrees with E_Z to 6.7e-13),
  so everything is consistent. The phrase "Gaussian energy per point" (`h1pp.tex:47`) should still say "in the convention of
  [CdCI, Def. 1.1] (ordered pairs)", because physics readers expect ½Σ.
- M7. H8 prediction failure (`h1pp.tex:54-55`, "which overshot"): this is well supported (H1'''s certified K = 40 value
  0.000394759853 is also about 9e-6 below H1'), but "most likely overshot" is the defensible wording. The ratio 8.3e-6 / 2.5e-7
  = 33× is consistent with the "up to 35×" cited.
- M8. `git status`: `H1ppp/launch.sh` has an uncommitted mode change (644 → 755) and `records/ckpt/` is untracked (about 1 MB).
  Commit both or deliberately exclude them before tagging `exciton-gated-5-v3`, so that the source archive matches the tag.
- M9. The record versus lattice energy at α = π: v2 quotes CdCI's "current record 0.23153532..." (`exciton_fluid_gated_V.tex:215`),
  while our min(FCC, BCC) = 0.2315362662. This is **not an inconsistency**. The record is CKS's coexistence phase, 9.5e-7 below
  (4.1e-6 relative), as stated at `exciton_fluid_gated_V.tex:81-82` and `_round2.tex:89-90`. The v3 section could repeat it in
  one clause, since V3's VOID test uses min(FCC, BCC) and not the record. This does not matter at a 3.6 % gap.

---

## Checks that passed (brief items 1-5)

**1. Numbers** (`.venv/bin/python -I`, mpmath 40 digits, from `records/*.json` `certificate.B_lower` lower ends).
- V3: K40 0.2232177894732002, K50 0.223217819358967, K60 0.2232178245494733.
- B − 0.22321782: −3.0527e-8, −6.4103e-10, +4.5495e-9. Margin above the window edge: 9.359e-9 (paper 9.4e-9).
- Increments: +2.9886e-8 and +5.1905e-9.
- H2/H4/H8 K50: 1.011018246684053, 0.07275645543945762, 0.0003947602893425596. G = 0.00476892, 0.0668382, 0.215565.
  K50 − K40 = 1.7556e-8, 1.8e-8, 4.3609e-10.
- Relative deviation versus H1' K40: V3 −2.496e-8, H2 −3.958e-8, H4 +4.384e-9, H8 −8.277e-6.
- H8 residual 9.8e-11 / 3.95e-4 = 2.49e-7.
- τ: 3.6e-14, 1.8e-16, 3.7e-14, 1.1e-13, 1.8e-16. δ max 1.70e-28 (H4). λ used 6, 3, 8, 3, 5 (ladder λ0·2^j with λ0 = 3, 3, 2,
  3, 5). Rounds 18, 18, 18, 19, 13.
- Solve 5.32 h to 10.19 h. Lattice E's match `summary.json`.
- Every table entry in `h1pp.tex:38-43`, the abstract, the metadata and CLAIM-129 is a correct rounding.

**2. Registration.** K = 50/60, b (17/20, 106/79, 7/10, 29/99), gcut 1e-12, cap 25, λ ladder and gate window are as registered.
`diff H1pp/rig2.py H1ppp/rig3.py` shows only the ckpt additions (assert prune=False, state save/restore, point lists P_*).
`evaluate.py`, `rig.py` and `hp_lp.py` are byte-identical to H1pp. `evaluate3.py` applies the same window, G thresholds and VOID
test as `H1pp/evaluate.py:63-75` (it drops only the informational "B − 0.21736068" field). It was committed at 22:18:37, and the
first record appeared at 01:00. The evaluator deviation is disclosed in the paper (`h1pp.tex:31-33`) and in DEVIATIONS.md,
including that log values had been seen. The disclosure is complete and honest.

**3. Mathematics.** The ansatz and Fourier pairing are consistent: e^{-t/2}L_k^{(d/2−1)}(t) ↔ (−1)^k scaling, so
f = β^{d/2}e^{-u/2}ΣR. The lift's bound on f/g holds because λ ≥ 1/b ⇔ πλβ ≥ α. The bound formula
[Q(0)+δ−β^{d/2}R(0)−δ(λβ)^{d/2}]/(1+τ) is correct for Prop. 2.2 applied to f_tot/(1+τ). Step (a) (R < 0 beyond U, exact sign at
U, U ≥ 1.0001·max root + 1) is sound. Step (b) is sound apart from the midpoint-cover hole, which my re-check closes; no case
was affected. Step (c) has the hole described in B1. u1/gcut being floating-point is harmless because the check covers all of
[0, U].

**4. Literature.** I read arXiv:1603.09684 through alphaXiv's full-text extraction, partially: Definition 1.1, Table 1.1 with
the paragraph before it, and the statement of Prop. 2.2. I did not read the rest of the paper.
- Table 1.1 caption: "A comparison of our lower bound from Theorem 1.4 for energy in R^n when α = π and ρ = 1, the numerically
  optimized linear programming bound, and the lowest energy currently known".
- Row: "3 0.21736068 . . . 0.22321782 . . . 0.23153532 . . .".
- Prop. 2.2: "Let f : (0, ∞) → R be any function, and suppose h : R^n → R is continuous, positive definite, and integrable.
  If h(x) ≤ f(|x|) for all x ∈ R^n \ {0}, then every subset of R^n with density ρ has lower f-energy at least ρ ĥ(0) − h(0)."
- "published 0.22321782" is faithful, provided it is described, as the paper does elsewhere, as a numerically optimised and
  not certified value. "every unit-density configuration" matches "every subset of R^n with density ρ" (lower energy).

**5. LaTeX.** A copy compiled in the scratchpad (pdflatex ×2) with no errors, warnings, undefined references or overfull boxes:
13 pages. The remaining consistency issues are S3-S6 and M3.

---

## Appendix: re-certification core (scratch `recheck/recert2.py`; suggest committing as `H1ppp/recertify.py`)

```python
# imports rig3 read-only; for each record: exact-cover bisection, outward-rounded root balls, merged clusters
def prove(encs, cap, lo, hi, max_boxes=20_000_000):
    stack = [(lo, hi)]; n = 0
    while stack:
        a0, a1 = stack.pop(); m = (a0 + a1) / 2
        we = max(Fraction(a1) - Fraction(m), Fraction(m) - Fraction(a0))
        w = math.nextafter(float(we), math.inf) * (1 + 1e-12) + 1e-300; assert Fraction(w) >= we
        v = sum((e(m, w) for e in encs), arb(0)); n += 1
        if v < cap: continue
        if m in (a0, a1): raise RuntimeError(f"check failed near {m!r}")
        if n > max_boxes: raise RuntimeError("too many boxes")
        stack += [(a0, m), (m, a1)]
    return n
# flo/fhi: float endpoints from z.lower()/z.upper() as exact rationals, nudged outward with nextafter
# f/g part: prove([make_encloser(Ra, bd, -kappa)], 1 + tau0_record, 0.0, U) with U from fhi of R's roots, R(U) < 0 exact
# fhat part: clusters = merged [flo, fhi] of Q's real roots (clipped at 0); check = all clusters + every gap with
#   Q(exact rational midpoint) < 0; assert Q > 0 beyond the last cluster; prove -Q - delta e^{s t} < 0 on each check interval
#   with the record's lam_used and delta; B = (Q(0) + delta - bd R(0) - delta (lam beta)^{d/2}) / (1 + tau0 + lift)
```

---

## Response (author session, 2026-10-17)

- **B1 verified independently before acting.** I read `rig3.py:certify()` (float `lo_`/`hi_` edges, gap tested only when
  `hi > lo` at a float midpoint) and, with a separate script that rebuilds Q exactly from `best_coeffs_exact` and evaluates it
  at exact rationals between adjacent real roots, found 13 negative wells in V3 K60 (Q down to -9.891e3 at t = 210.54) and 11 in
  V3 K50 (covered there by the recorded lift). I read the re-check script, found no hole (exact box cover, outward rounding,
  clusters, constant sign in root-free gaps), committed it as `H1ppp/recertify.py` and ran it myself on all 19 records:
  output `H1ppp/recertify_output.txt`, identical to the review's. Disclosed in the paper (new paragraph + table footnote),
  RESULTS.md, DEVIATIONS.md item 3, metadata, CLAIM-129. Frozen code and records not edited.
- **B2 applied** everywhere (paper section and bullet, abstract, metadata, RESULTS.md, CLAIM-129): bound values certified;
  insufficiency of two-point bounds remains numerical; H1'' registered reading overstated.
- **S1, S2** applied (sufficient, not cause; truncation sentence replaced). **S3**: no H1'' review file exists; the paper now says
  its corrections were applied in 25eecce and the text was not saved, and this file is committed. **S4** keybox updated. **S5**
  K/degree wording. **S6** both sentences. **S7** one sentence in paper and RESULTS.
- **Minor:** M1, M2, M3 (ledger rewritten), M4, M6 (convention stated), M7 ("most likely"), M5 and M8 recorded in DEVIATIONS.md
  item 2 (frozen driver docstring left as is; ckpt/ deliberately not committed; launch.sh mode change committed), M9 one clause
  added in the reading.
