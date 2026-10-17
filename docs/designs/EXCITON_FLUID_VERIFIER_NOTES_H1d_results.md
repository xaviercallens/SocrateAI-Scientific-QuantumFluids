# H1d verifier notes: results, records, claims (hostile referee, 2026-10-17)

Scope: `exploration/exciton/three_d/H1d/` at dd67a12 (RESULTS.md, summary.json, records/*.json, logs/, DEVIATIONS.md,
evaluate.py), LEDGER.md CLAIM-130 (line 959), the H1''/H1''' lower-bound records, and git history 4e596f0..dd67a12.
Nothing in the repository was edited except this file. Scratch scripts are in the session scratchpad under `h1drev/`:
`reverify.py` (independent certificate check), `lattices.py` (FCC/BCC/Z/A2 energies), `lemma83.py` (CdCI Lemma 8.3 check).

**Verdict: no BLOCKING item.** All 29 certified UB values were reproduced independently, and min μ > 0 holds at every point
of every grid. The reduction and the post-registration lemma are correct. The literature gate holds as far as I could
read. There are several wording and rounding defects and one factual error in the run timeline. Fix these before deposit.

## 1. Independent re-verification (all 29 certified records, not only the requested three)

Method (`reverify.py`; it does not import dual.py):
- λ is read from `lambda_float_rounded` (Fractions, all ≥ 0). Each λ is expanded to **every** y ∈ Z_m^d by the folding
  y ↦ sorted(min(y_i, m − y_i)). The orbit sizes are recounted by brute force and match `orbit_sizes` in all 29 records.
- λ is renormalised exactly as Fractions, and Σ_y λ(y) = 1 − s^{-d} is asserted. The factor (target/tot − 1) is |·| ≤ 3.4e-14.
- μ(x) = s^{-d} + Σ_y λ(y) Π_i cos(2π x_i y_i/m) is computed at **every** x ∈ Z_m^d with arb (256 bits). The method is three
  m×m cosine-matrix products on the full m^d tensor, unfolded with no weights w_b and no permutation kernel. The separable
  form needs λ even in each coordinate separately, which holds because λ is invariant under signed permutations. As a
  check, μ was also computed in plain mpmath (60 digits) with the full cos(2π x·y/m) sum over all 110 592 y. This was done
  at the minimising x and at two random x for each of the five m=24/48 best-grid records, and it agrees with the arb value
  to 20 digits.
- Γ(x) = Π θ(x_i) − [x=0], with θ(a) = Σ_{|n|≤400, n≡a} e^{-α n²/s²}. The tail bound is 2e^{-a2(N+1)²}/(1−e^{-a2(N+1)}),
  which is < 1e-100. α = π is taken from arb.pi().
- UB = Γ(0) + Σ_{x≠0} μ(x)Γ(x) is summed over the full grid.

Results (UB is my value; every one lies inside the record's `UB_ball`):

| record | min μ (all points) | my UB | record UB_ball |
|---|---|---|---|
| D3a2 (6,48) | 9.99996e-9 at (18,18,11) | 1.0116485640648532 | [1.01164856406 ± 5.80e-12] |
| D3pi (6,48) | 9.99990e-9 | 0.2242866641072033 | [0.224286664107 ± 5.56e-13] |
| D3a4 (8,48) | 9.99989e-9 | 0.0734293569071188 | [0.073429356907 ± 5.92e-13] |
| D3a8 (8,48) | 9.99993e-9 | 0.000410902079959902 | [0.000410902080 ± 2.27e-13] |
| D3a8 (4,24) | 9.99999708e-9 | 0.000485582906749546 | [0.0004855829067 ± 9.30e-14] |
| the other 24 (V1, V2, all D3) | 9.9999e-9 … 1.0e-8, all provably > 0 | inside the record ball in all 24 | |

Independent lattice energies at density 1 (`lattices.py`: Jacobi theta in mpmath at 50 digits). FCC = 2^{-1/3}D3, with
(θ3³+θ4³)/2 − 1. BCC = 2^{1/3}(Z³ ∪ Z³+½), with θ3³+θ2³ − 1.

| α | FCC | BCC | min | 1 − UB*/min (UB* = record upper end) | (UB*−B)/B |
|---|---|---|---|---|---|
| π | 0.2315362661841479 | equal (FCC* = BCC, α = π self-dual) | — | 0.031310871 | 0.00478835 |
| 2 | 1.017616895908993 | 1.015862816034718 | BCC | 0.0041484459 | 0.000623448 |
| 4 | 0.07796767103070266 | 0.07889601370735761 | FCC | 0.05820764 | 0.00924868 |
| 8 | 0.0005032413015592802 | 0.0006026980498848334 | FCC | 0.18348896 | 0.0408901 |

E_Z(π) = 0.08643481121330801 and E_A2(π) = 0.1595952669639284 (direct double sum). These agree with evaluate.py/H1 lp_bound
to 16 digits. **The core claim, certified UB* < min(FCC, BCC) at α = π, 2, 4, 8, is confirmed**, with margins of 4e-3 or
more relative, far above any float issue (review H1d_math MINOR-2 is moot).

Sanity check that the result is not trivially implied by published bounds: CdCI Lemma 8.3 (LP ≤ ρ∫_{|x|>r} f with
vol B_r = 1/ρ) gives 0.490, 1.325, 0.264 and 0.0256 at α = π, 2, 4, 8. All four are above min(FCC, BCC), so the result is
not implied by Lemma 8.3.

## 2. Mathematics

- **The reduction (steps 1–5)** was re-derived and is correct. It matches the pre-run review. The convention also matches
  the sources: CdCI Definition 1.1 (v6, p. 1) counts ordered pairs, a lattice has energy Σ_{x∈Λ∖0} f(|x|), and
  f = e^{-αt²} gives Θ_Λ(αi/π) − 1 (p. 2). This is the convention used by theta_sum, by H1''' B and by my lattice sums.
  CKS (0911.2169v2, Table I) uses f(s) = V/2, so their n = 3 value 0.11576766 doubles to CdCI's 0.23153532.
- **Post-registration lemma** (RESULTS.md:143–150): correct. Each step was checked:
  - h_ε ≤ g off 0.
  - ĥ_ε = ĥ ∗ φ_ε ≥ 0 and ĥ_ε ∈ L¹.
  - ĥ_ε(0) = ∫h e^{-πε|x|²} → ĥ(0) by dominated convergence.
  - ĥ ∈ L¹ for integrable, continuous h with ĥ ≥ 0. This is standard (Stein–Weiss Ch. I, Cor. 1.26); cite it.
  - P ∈ L¹(T^d) has Fourier coefficients f(−n), so P = Σ f(n)e^{-2πin·ξ} a.e.
  - Σ|f(n)| ≤ h(0)Σe^{-πε|n|²/s²} < ∞, so the series converges uniformly to a continuous F.
  - F ≥ f̂ everywhere, by continuity.
  - Real positive-definite h is even, so F is real.
  - Radialisation preserves every hypothesis.

  The proof is fine as a sketch. Write "|h_ε(x)| ≤ h(0)e^{-πε|x|²}" explicitly, because RESULTS writes "|h| ≤ h(0)", which
  alone does not give summability.
- **Which "two-point bound"?** RESULTS:128 and CLAIM-130 say "the Cohn–Kumar two-point (LP) bound". The original Cohn–Kumar
  statement (math/0607446v2, Prop. 9.3, p. 137) has a **wider** class than CdCI Prop. 2.2: h = ĝ with g ∈ L¹, g ≥ 0, h not
  assumed integrable, and objective ρ·liminf_{t→0} g(t) − h(0) (periodic configurations). The lemma as written covers only
  CdCI Prop. 2.2 ("as CdCI define it", RESULTS:150), so the headline name and the proved scope differ slightly. The gap
  closes in one line. For such h, h_ε = h·e^{-πε|x|²} is continuous, integrable and positive definite, with ĥ_ε = g ∗ φ_ε
  and h_ε ≤ f off 0. Then liminf_{ε→0} ĥ_ε(0) = liminf ∫g φ_ε ≥ liminf_{t→0} g(t), because g ≥ 0 and φ_ε is an approximate
  identity. So the CK objective is ≤ sup over the Prop. 2.2 class ≤ UB. → SHOULD-FIX 3.
- **Reading of "UB < min lattice"**: "no admissible h reaches min(FCC, BCC), so the two-point bound cannot prove FCC/BCC
  optimal" is the correct logical reading. Two caveats are missing (SHOULD-FIX 2):
  - (a) At α = π (density 1 with the self-dual Gaussian) FCC and BCC are **not** the putative ground state. CKS 0911.2169v2
    (p. 3, Table I) gives "pc₁" = phase coexistence between D₃ and D₃* for 0.99899854 ≤ ρ ≤ 1.00100312, with energy below
    both lattices. So "cannot prove FCC/BCC optimal at α = π" is vacuous. The meaningful α = π statement is the one about
    the CKS record, and RESULTS does make it.
  - (b) "best lattice" (RESULTS:121 column header, :129; PREREG:70) assumes that min(FCC, BCC) is the minimum over all 3D
    lattices at these α. I know of no proof of that for general α, and RESULTS cites none. Say "min(E_FCC, E_BCC)" (or "the
    best known lattices").

  Under the (α ↔ density) scaling, density ρ = (π/α)^{3/2} = 1.97, 0.70 and 0.25 for α = 2, 4, 8. These are outside the
  coexistence window, and BCC (α = 2) and FCC (α = 4, 8) are the putative ground states there. So for α = 2, 4, 8 the
  statement is meaningful.
- **CKS record at α = π.** CdCI Table 1.1 (v6, p. 5) attributes the record to "[15] or the expectation bound", and [15] is
  CKS 0911.2169. CKS Table I calls it "pc₁ … phase coexistence between D₃ and D₃*". So "Cohn–Kumar–Schürmann coexistence
  state" (RESULTS:131) is accurate. Note that it is a two-phase coexistence (Maxwell construction), not a single periodic
  configuration.
- **Novelty framing.** The non-sharpness in d = 3 at α = π was already visible **numerically** in CdCI Table 1.1 (LP
  0.22321782… vs record 0.23153532…, a 3.6% gap), and at α = 2, 4, 8 in H1'/H1''' (their numerical LP optima are below the
  lattices). What is new is the **rigorous** upper bound. RESULTS should say this in one sentence (SHOULD-FIX 2).

## 3. Literature (read in this session, via alphaXiv full-text extraction)

- Cohn & de Courcy-Ireland, arXiv:1603.09684 **v6**, pp. 1–8, 11–12, 18, 24, 26, 28–29 were read.
  - Prop. 2.2 (p. 7) reads, quoted: "suppose h : R^n → R is continuous, positive definite, and integrable. If h(x) ≤ f(|x|)
    for all x ∈ R^n \ {0}, then every subset of R^n with density ρ has lower f-energy at least ρ ĥ(0) − h(0)."
  - Table 1.1 (p. 5) gives n = 3: "0.22321782 . . ." (LP bound) and "0.23153532 . . ." (record, "from [15] or the
    expectation bound").
  - §10 (p. 28) says "Many problems remain open, most notably determining the true asymptotics for minimal energy and for
    the linear programming bound".
  - No rigorous upper bound on the d = 3 LP bound appears in the pages read.
- Cohn & Kumar, math/0607446 **v2** §9, pp. 135–145 were read.
  - Prop. 9.3 is the wider-class statement quoted above.
  - Conjecture 9.4 covers n ∈ {2, 8, 24}.
  - Prop. 9.6 (n = 1, sharp).
  - No d = 3 non-sharpness statement appears.
- Cohn, Kumar & Schürmann, arXiv:0911.2169 **v2**, pp. 1–7 were read. They report numerical ground states, Table I and the
  coexistence. There are no LP bounds.
- R. Li, arXiv:2206.09876 **v3**, pp. 1–5, 8–9, 11, 13–15, 19–20 were read.
  - The paper covers sphere packing only.
  - Thm 6.1 (p. 11) reads: "The 3-dimensional Cohn-Elkies linear programming bound is greater than 0.18398089."
  - §10 lists open problems (convergence as m, r → ∞, lifting duals) and does not mention energy.
  - **Not read:** the journal version (Adv. Math., ScienceDirect S0001870824005590), which may differ from v3.
- Searches: two alphaXiv discovery searches ("rigorous upper bound on the LP bound for Gaussian energy / not sharp, d = 3";
  "dual LP bound for energy minimization … FCC/BCC") and one web search (extended mode) returned only sphere-packing duals:
  Li; de Courcy-Ireland–Dostert–Viazovska 2211.09044 (d = 6); 2607.11319 (d = 36); and fibered packings 2607.25254, which
  was not read. They also returned unrelated Gaussian-core papers (2503.22895 and 2511.03353, titles/abstracts only). I found
  **no** published rigorous upper bound on the Gaussian-energy LP bound in d = 3. This is absence of evidence from a limited
  search. The wording in DESIGN.md and CLAIM-130 ("appear not to be published", "found no prior energy version") is
  appropriately hedged. Keep it hedged.

## 4. Numbers, rounding, disclosures

All numbers in RESULTS.md and CLAIM-130 were checked against summary.json, the logs, the records and my recomputation.

## BLOCKING

None.

## SHOULD-FIX

1. **Wrong launch time** (RESULTS.md:103, "launch.sh 2026-10-17 09:20 to 10:42"). The freeze commit 4e596f0 is at
   09:33:26. `logs_launch.out` was created at 09:33:31, the first records at 09:33:32 (V1), and D3pi_s4_m24 at 09:33:39.
   "09:20" would put the launch **before** the freeze, which is exactly what a reader checks first. The filesystem evidence
   says the launch came after the freeze. Fix: "09:33 (5 s after the freeze commit 4e596f0) to 10:42". Commit
   `logs_launch.out` (currently untracked, 0 bytes) as evidence, or cite its mtime. On gate parameters before the freeze:
   - dual.py was last modified at 09:21:50, and its `__pycache__` at 09:21:51.
   - The only pre-freeze record is dev/DEV_s4_m24.json (d = 3, α = 1, 09:33:04), which is not a gate parameter.
   - The DESIGN dev list (d = 1 α = 2; d = 2 α = 2; d = 3 α = 1, 1.5, 3, 6) contains no gate parameters.

   I cannot exclude untracked interactive runs, and nothing points to any.
2. **Missing caveats on the headline reading** (RESULTS.md:121 header, :128–132; CLAIM-130 "-> the two-point bound cannot
   prove FCC/BCC optimal at these alpha"; PREREG.md:70 wording carried over):
   - (a) Replace "best lattice" with "min(E_FCC, E_BCC)" (no proof that FCC/BCC are the best lattices at these α is cited).
   - (b) Add: "At α = π (density 1) FCC and BCC are not the putative ground state: CKS 0911.2169 report FCC/BCC phase
     coexistence (energy 0.23153532 < 0.23153627); the informative α = π statement is UB* < the CKS record."
   - (c) Add: "The gap itself was already apparent numerically (CdCI Table 1.1 at α = π; H1'/H1''' at α = 2, 4, 8). What is
     new is a rigorous certificate."
3. **Name versus proved scope** (RESULTS.md:128 "Cohn–Kumar two-point (linear-programming) bound" vs :150 "as CdCI define
   it"; CLAIM-130 "Cohn-Kumar two-point (LP) bound"). Either say "the two-point bound of CdCI Prop. 2.2 (Cohn–Kumar)", or
   add the one-line extension to CK Prop. 9.3's wider class (h = ĝ, g ∈ L¹, g ≥ 0, objective ρ liminf_{t→0} g − h(0)) given
   in §2. In both cases mark it post-registration, like the existing lemma.
4. **Lower bounds rounded up** (RESULTS.md:123, :125, :126, column "B (certified lower, H1''')"). The certified values are
   0.2232178193589670…, 0.07275645543945762… and 0.0003947602893425596…, but the table prints 0.223217819359,
   0.0727564554395 and 0.000394760289343. All three are rounded **up**, so as printed they are not lower bounds. Fix: write
   0.223217819358, 0.0727564554394 and 0.000394760289342 (α = 2, 1.01101824668, is correct). The interval endpoints at
   RESULTS:132–133 are correctly rounded down.
5. **DEVIATIONS.md:5 is incomplete about what existed when the evaluator was changed** ("Per-grid log lines (D3pi, D3a2
   partial) had been seen"). At commit 1ee1714 (09:59:54) the following records and logs existed:
   - all of V1/V2;
   - D3pi complete, including the (8,48) HiGHS failure logged at 09:56;
   - D3a2 5/6 (all but (8,48));
   - **D3a4 4/6** ((4,24), (5,30), (6,36), (5,40), written 09:50–09:54).

   The change cannot have been tuned: the 1e-12 margin tightens the criterion, and the realised margins are ≥ 4.1e-3. State
   what existed, not only what was seen: "at the time of the fix, records existed for V1, V2, D3pi (5 + 1 failure), D3a2 5/6
   and D3a4 4/6; per-grid log lines for D3pi and D3a2 had been read."

## MINOR

1. RESULTS.md:107, "the certified UB equals the float LP value to ~1e-13 relative". This is false for the small-energy
   cases: (UB_true − UB_float)/UB is up to 2.9e-11 (D3a8 (6,36)) and 2.2e-12 (D3a8 (5,40)). The recorded certify() balls
   have radius up to 5.8e-12 absolute (5.5e-10 relative for D3a8 (8,48)), because certify runs at 53-bit arb precision.
   Say "to within the certificate's ball radius (≤ 6e-12 absolute)".
2. Margins and widths should be rounded in the conservative direction:
   - "0.415%" (RESULTS:124, CLAIM-130) is 0.41484% → "0.414%".
   - "0.00725 below the CdCI record" (RESULTS:130) is 0.0072487 → "0.00724".
   - The sandwich widths "0.062%" and "0.92%" (true 0.06234% and 0.9249%) should round up → "0.063%" and "0.93%".
3. The upper bound at α = 8 differs between files: CLAIM-130 gives 0.0004109020802, RESULTS:126/:133 give 0.000410902080227
   and 0.0004109020803. All are valid upper bounds, because the true certified upper end is 0.00041090208014604. Use one
   value. Rounding up from the ball string gives 0.0004109020803.
4. RESULTS:106 "every certified grid has min μ = 1.0e-8 (the ε buffer)". The true minima over all points are
   9.9999e-9 … 1.0000e-8, e.g. 9.99989e-9 for D3a4 (8,48). Write "min μ ≈ 1e-8 (the ε buffer; ≥ 9.9998e-9), provably > 0".
5. In RESULTS:148, write |h_ε(x)| ≤ h(0)e^{-πε|x|²}, and cite the L¹ fact (Stein–Weiss Ch. I Cor. 1.26).
6. The V1 and V2 table values RESULTS:114–115 (0.0864348174800, 0.160722743990) are truncated from the ball strings, i.e.
   slightly below the ball upper ends (by about 2.5e-14 and 1.6e-13). This is harmless for gates, but for consistency
   print the upper end rounded up (0.0864348174801, 0.160722743991).
7. The LEDGER entry says "Hostile review of results pending". Update it to point to this file once the fixes are applied.
8. DESIGN.md and PREREG.md: PREREG.md:93 still says "Not claimed: anything about functions outside 𝓗". RESULTS now claims
   the wider class through the post-registration lemma. That is correctly labelled post-registration, but the paper text
   must keep the registered claim (class 𝓗) and the extension visibly separate.

## What was checked and found correct

- All 29 certificates were independently reproduced, as described in §1.
- Gate logic: V1 passes (7.25e-8 ≤ 1e-6), V2 is consistent, and there is no VOID. Every UB lies above the matching B (V1b
  K40, V2 K40, V3/H2/H4/H8 K50). All four B records were re-confirmed by H1ppp/recertify_output.txt ("record delta OK").
  V3 K60, which is defective, is not used.
- The 31 = 3 + 4 + 24 registered runs: 29 certified and 2 RuntimeErrors (HiGHS status 15, D3pi (8,48) and D3a8 (6,48), both
  in the logs). Missing grids can only make UB* more conservative, so taking the minimum over the ladder is valid.
- The prediction (α = 2 has the smallest margin; D3pi is below the CdCI record) holds. The non-monotonicity example
  (1.01187 > 1.01165) is correct.
- Runs were uninterrupted (done.txt ends with ALLDONE). summary.json (10:42:50) post-dates every record. The evaluator diff
  1ee1714 only tightens the verdict criterion and fixes the VOID-gating order.

---

## Response (author session, 2026-10-17)

- SF-1 verified (git log: 4e596f0 09:33:26; logs_launch.out 09:33:31; first record 09:33:32); RESULTS corrected, DEVIATIONS item 2.
- SF-2 applied: "min(FCC, BCC)" throughout, no best-lattice claim; at α = π the statement is UB* below the CKS record; "gap
  visible numerically before, certificate is new".
- SF-3 applied by narrowing the name: "LP bound in the form of CdCI Prop. 2.2"; Cohn–Kumar Prop. 9.3's wider formulation
  explicitly not claimed.
- SF-4 applied (B rounded down). SF-5: I counted the records with mtime before 09:59:54 myself (21 of 31) and listed them in
  DEVIATIONS item 1.
- Minor: float/certified agreement ≤ 3e-11; conservative rounding of margins and widths; α=8 UB printed consistently
  (0.000410902080147 / …0802, both upper); "min μ ≈ 1e-8, provably > 0"; V1/V2 rounded up; ledger updated; registered claim
  and post-registration lemma kept separate; lemma now writes out |h_ε| ≤ h(0)e^{-πε|x|²} and cites Stein–Weiss I.1.26.
