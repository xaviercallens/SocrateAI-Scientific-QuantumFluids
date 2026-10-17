# H1d verifier notes: mathematics and certificate code (hostile referee, 2026-10-17)

Scope: `exploration/exciton/three_d/H1d/` at commit 4e596f0, covering DESIGN.md, PREREG.md, dual.py, run_h1d.py and evaluate.py.
Not read: records/ and logs/, because the gate runs are still in flight. Nothing in the repository was run or edited. All
numerical checks below use NON-gate parameters only. The scratch scripts are in the session scratchpad under `h1dcheck/`:
`brute.py`, `ineq.py`, `sanity.py`.

**Verdict: no BLOCKING item.** The reduction is correct. The certificate code computes exactly the quantity in DESIGN.md, and
an independent brute-force recomputation agrees with certify() to all printed digits. The gate logic reports the right end
of the ball. The other findings are one strengthening, one gating-order defect and some wording issues.

## 1. The reduction (DESIGN.md, steps 1-5)

- **Step 1 (Poisson).** Put f(x) = h(x/s), so that f̂(ξ) = s^d ĥ(sξ). Then Σ_n f(n) e^{-2πi n·ξ} = Σ_k f̂(ξ + k). At
  ξ = y/m this gives Ĝ(y) = s^d Σ_k ĥ(s(k + y/m)), so the formula and the factor s^d are correct. Under the stated class
  (h continuous; |h| and |ĥ| both O((1+|x|)^{-d-δ})) pointwise Poisson summation holds (Stein-Weiss, Ch. VII, Cor. 2.6).
  ĥ is real because h is radial (even), so Ĝ ≥ 0 holds as a real inequality.
- **Step 2.** All terms are ≥ 0, so Ĝ(0) ≥ s^d ĥ(0). Correct.
- **Step 3.** For x ≢ 0, every n ≡ x is nonzero, so G ≤ Γ. For x ≡ 0, G(0) = h(0) + Σ_{n∈mZ^d∖0} h(n/s) ≤ h(0) + Γ(0).
  Both are correct, and the direction is right: −h(0) ≤ −G(0) + Γ(0).
- **Step 4** follows from steps 2 and 3.
- **Step 5 (weak duality).** Because λ is real and even, Σ_y λ(y) e^{-2πi x·y/m} = Σ_y λ(y) cos(2π x·y/m) =: K(x) for every
  x. Hence Σ_y λ Ĝ = Σ_x G(x) K(x). Only G real is needed (h real); G even is not needed. Then
  Σ_{x≠0} μG − Σ_y λĜ = s^{-d} Σ_{x≠0} G − K(0) G(0) = s^{-d} Σ_x G − G(0), since K(0) = Σλ = 1 − s^{-d}.
  With μ ≥ 0 and G ≤ Γ (G may be negative; μG ≤ μΓ still holds), λ ≥ 0 and Ĝ ≥ 0, this gives
  **ĥ(0) − h(0) ≤ Γ(0) + Σ_{x≠0} μ(x)Γ(x)**. There is no missing factor of s^d or of orbit size. Density 1 enters only
  through Prop. 2.2 with ρ = 1, and the energy convention (Σ_{v≠0} g(v), ordered pairs, g = e^{-α r²}) matches theta_sum
  and the H1''/H1''' B values. For example, V3 B = 0.2232178193589670 equals the CdCI value 0.22321782.
- s does not have to be rational: any real s ≥ 1 works. Rationality is used only to make s^{-d} exact in arb.
- Numerical confirmation of the chain with explicit approximately-feasible h. These h come from H1/lp_bound GaussLP at K=20,
  with violations ≤ 1e-10. The identity in step 5 holds to a residual ≤ 1.3e-15. min Ĝ ≥ 0. s^{-d}ΣG − ĥ(0) ≥ 0, except
  −1.9e-12 in d=1, which is at the level of h's own 1e-10 infeasibility. ĥ(0) − h(0) ≤ certified UB on every grid:

  | d, α | ĥ(0)−h(0) | UB (s,m) |
  |---|---|---|
  | 1, 2 | 0.271341522177 | 0.2713415263 (2,8); 0.2713415306 (4,32); E_Z = 0.2713415222 |
  | 2, 2 | 0.602387712695 | 0.6065503 (2,8); 0.6049030 (4,32); E_A2 = 0.6023879 |
  | 3, 1.5 | 2.038638780367 | 2.0423462 (2,8); 2.0412013 (3,12); 2.0395208 (4,24); BCC = 2.0401454, FCC = 2.0411510 |

- **Sanity examples.** Example 1 is correct: λ = (1 − s^{-d})δ_0 gives μ ≡ 1 and UB = E((1/s)Z^d), checked to 30 digits.
  Example 2 is **wrong as worded**; see MINOR-1.

## 2. dual.py

All of the following are verified by brute force: plain loops over Z_m^d in mpmath (30 digits), orbits recomputed by
folding y ↦ sorted(min(y_i, m−y_i)), Γ by direct lattice sums, and μ at every x ≠ 0 (not only at orbit representatives).
The cases were d=1 (s,m) = (2,8) and (3,13) (odd m); d=2 (2,8) and (3,9); d=3 α=1 (2,8); and d=3 α=1.5 (2,7) and (3,12).

- orbits(): every orbit size equals the brute-force count (zero mismatches), including odd m and the b = m/2 cases.
- Sign folding: Σ_{y_i∈±b_i} e^{2πi x_i y_i/m} = w_b cos(2π x_i b_i/m) is real for each factor, so Σ_signs cos(2π x·y/m)
  = Π_i c(x_i, b_i). This is correct, and for b ∈ {0, m/2} there is a single residue with a real exponential.
- kernel_float(): the sum over d! permutations counts each distinct ordering d!/nd times, and the factor nd/d! corrects
  this. UB_float equals the brute-force UB to about 1e-16 in every case.
- certify() contraction: it computes μ(x) = s^{-d} + Σ_{b ordered folded} λ(orbit(b)) Π_i C[x_i, b_i]
  = s^{-d} + Σ_{y∈Z_m^d} λ(y) cos(2π x·y/m), with λ per point. The axis-by-axis index bookkeeping (pre = x-indices,
  post = b-indices) is correct. μ is constant on orbits because λ is, so checking representatives is enough. The brute-force
  minimum of μ over all points equals 1.0e-8, matching certify's min_mu.
- λ renormalisation is exact over Fractions, the assert checks Σ size·λ = 1 − s^{-d} exactly, and clipping makes λ ≥ 0.
  The conversion fmpq → arb is a ball enclosure, so it is rigorous even at the default 53-bit precision.
- _theta_arb tail. t0 = exp(−a2(mJ − |a|)²) bounds every term with |j| > J. Consider the j < −J branch, the worse one:
  the first omitted term is t0 · exp(−a2 m(2(mJ−a) + m)) ≤ t0 · exp(−2a2 m² J) ≤ t0 q, and each later ratio is
  ≤ exp(−a2 m²(2J+1)) ≤ q. The j > J branch is dominated term by term. So the tail is ≤ 2 t0 q/(1−q), which is valid.
  The term is added as arb(0, tail.upper()).
- Γ(0) = Π θ(0) − 1 excludes exactly n = 0, and the brute-force Γ agrees.
- α is used as a2 = α/s² (exact rational s²) in both gamma_float and certify, consistent with g(n/s) = e^{-α|n|²/s²}.
- UB accumulates Σ z_X μ_X Γ_X with integer orbit sizes, plus Γ(0). The brute-force UB matches certify's ball in every case:
  for d=3 α=1.5 (3,12), brute force gives 2.0412012608181188 and certify gives [2.041201260818 ± 2.7e-13].
- μ ≥ 0 uses arb's `>=`, which is true only when it is certain. One non-certifiable orbit makes the whole grid
  uncertified (run_h1d records certified = False), which is conservative.

## BLOCKING

None.

## SHOULD-FIX

- **SF-1. The "not addressed" caveat can be closed, and the result is then stronger.** UB also bounds the full Prop. 2.2 class:
  h continuous, integrable, ĥ ≥ 0, h ≤ g off 0, with no decay assumption and no radiality.
  Proof. Let h_ε = h · e^{-πε|x|²}. Then ĥ_ε = ĥ ∗ (Gaussian) ≥ 0, h_ε(0) = h(0), and h_ε ≤ g off 0: where h > 0, the
  factor only lowers h; where h ≤ 0, h_ε ≤ 0 < g. Also ĥ_ε(0) → ĥ(0), because ĥ is continuous and bounded. For f = h_ε(·/s):
  - f̂ ∈ L¹ (since ĥ ∈ L¹ for continuous positive definite integrable h), so the periodisation P = Σ_k f̂(·+k) is in L¹(T^d)
    and has Fourier coefficients f(n), by inversion.
  - Σ|f(n)| < ∞ (|h| ≤ h(0) times a Gaussian), so Σ_n f(n) e^{-2πi n·ξ} converges uniformly to a continuous F with F = P a.e.
  - Hence F ≥ 0 everywhere, and F ≥ f̂ everywhere by continuity. These are exactly steps 1 and 2. Steps 3-5 are unchanged.
  - For non-radial h, use λ even. Alternatively, radialise h, which preserves every condition and both ĥ(0) and h(0).

  Recommendation: replace "Whether the supremum over the wider class of Prop. 2.2 ... is not addressed" (DESIGN.md) and
  "Not claimed: anything about functions outside 𝓗" (PREREG.md) by this lemma, after checking it, or keep the narrower claim
  and say explicitly that it is a choice, not a gap.
- **SF-2. evaluate.py: a VOID in a D3 case does not gate the D3 cases already processed.** gates_ok is set to False only
  after a D3 VOID, so the "note" is added only to D3 rows that come after it in dict order (D3pi, D3a2, D3a4, D3a8). PREREG
  says D3 results are registered only if V1 and V2 pass *and no VOID* in any case. `validation_gates_pass` does end up
  False, but an earlier D3 row can still carry an un-annotated "UB < min(FCC,BCC)" verdict. Fix: compute the VOID flags for
  all cases first, then assign the notes. This matters only if a VOID occurs.

## MINOR

- **MINOR-1. Sanity example 2 (DESIGN.md) is wrong as worded.** The "normalised indicator of the dual group" including y = 0
  (λ = s^{-d}(1 − s^{-d}) on H^⊥) gives μ = s^{-d} + (1 − s^{-d})1_H, and UB = E(L) + s^{-d} Σ_{x∉H} Γ(x) > E(L).
  The correct statement is λ = s^{-d} on H^⊥ ∖ {0}, which gives μ = 1_H and UB = E(L). It also needs s^d ∈ Z and
  mZ^d ⊆ sL. Checked for d=1 (s,m) = (2,8) with L = Z, α=2: H^⊥∖0 gives 0.2713415221890152 = E_Z, and H^⊥ including 0
  gives 0.889. Also checked for d=2 (2,4) with L = Z²: 0.6163092660 = E_{Z²}. The code never uses this example.
- **MINOR-2.** The verdict "UB < min(FCC,BCC)" compares an arb upper end with float lattice sums from theta_sum. Those sums
  carry relative error of about 1e-15 and a tail estimate that is not enforced. The verdict is safe only if the margin
  UB_star_rel_minlat is far above 1e-13. Development margins are 5e-6 or more, but the margin should be quoted next to every
  verdict. A rigorous lattice sum (arb, with an explicit tail) would remove the issue.
- **MINOR-3.** ball_upper() parses the decimal ball string. That string is an enclosure (arb_get_str guarantees this), but
  parsing it at 50 digits rounds to nearest rather than upward. The effect is negligible (about 1e-50), but it would be
  cleaner to use `certificate.UB_upper` or to add one ulp. The parser would also crash on a pure-radius string such as
  "[+/- r]", which cannot happen at these magnitudes.
- **MINOR-4.** run_h1d stores `lambda_float_rounded` *before* the exact renormalisation. This is documented, but a
  re-verifier must repeat the renormalisation. Storing the renormalised λ (or tot) would make re-verification
  copy-and-check.
- **MINOR-5.** DESIGN.md says s must be rational and s > 1. Any real s ≥ 1 is valid (s = 1 gives λ = 0 and UB = E(Z^d)).
  Rationality is only an implementation convenience. Also, "G real/even": only G real is used.
- **MINOR-6.** In the class definition, "|h|, |ĥ| ≤ C(1+|x|)^{-d-δ}" plus continuity is the standard sufficient condition,
  so the statement is fine. Under SF-1 the decay hypothesis on ĥ becomes unnecessary.
