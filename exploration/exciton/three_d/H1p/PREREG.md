# H1' — certified two-point LP bounds for the Gaussian energy, validated on published values (pre-registration, 2026-10-12)

Directory `three_d/H1p/`. Successor of H1 (`../PREREG_round2.md`, results `../H1/RESULTS.md`), which stopped at its sanity
gate because sampled constraints cannot certify f <= g and f̂ >= 0 at the 1e-8 level. Owner's choice (2026-10-12):
re-scope as validation with rigorous certificates.

## Literature (read before registering)

Cohn & de Courcy-Ireland, *The Gaussian core model in high dimensions*, arXiv:1603.09684 (v6), Table 1.1, α = π, ρ = 1:
"the numerically optimized linear programming bound" and "the lowest energy currently known" are

| n | LP bound | current record |
|---|---|---|
| 1 | 0.08643481... | 0.08643481... |
| 2 | 0.15959526... | 0.15959526... |
| 3 | 0.22321782... | 0.23153532... |

So the question H1 registered at α = π in d = 3 ("gap < 1e-6 or > 1e-3?") is already answered in print: the two-point
bound is about 3.6 % below the record. H1' therefore does not claim that gap as a finding. Its purposes are (i) to make our
LP code reproduce published numbers, as known-answer controls, with **rigorous** certificates; (ii) to give certified
d = 3 bounds at α ∈ {2, 4, 8}, where we found no published value (we did not search exhaustively; if one exists, it is a
further control, not a discovery). The paper's proof of the bound (its Proposition 2.2, Cohn–Kumar) applies to arbitrary
configurations of density ρ; our earlier derivation (`../H1/RESULTS.md` §1) was periodic only. Whether rigorous versions
of these LP values are already published was not checked.

## Bound and certificate

Fourier convention f̂(y) = ∫ f(x) e^{-2πi x·y} dx; g(x) = e^{-α|x|²}; unit density. Proposition 2.2 of 1603.09684 with
h = f: if f is continuous, integrable, radial, f̂ >= 0, and f(x) <= g(x) for x != 0, then every configuration of density 1
has lower g-energy >= f̂(0) − f(0).

**Multiplicative slack (used for certification).** If f <= (1 + τ) g for all x != 0, then f/(1+τ) satisfies the hypothesis,
so the energy is >= (f̂(0) − f(0)) / (1 + τ). The certified bound is B = (f̂(0) − f(0)) / (1 + τ), with τ >= 0 rigorously
established.

**Ansatz** (as in H1): f̂(y) = Σ_k c_k φ_k(y/√β), φ_k(y) = e^{-π|y|²} L_k^{(d/2−1)}(2π|y|²), k = 0..K; then
f(x) = β^{d/2} Σ_k (−1)^k c_k φ_k(√β x). With t = 2π|y|²/β and u = 2πβ|x|²:
f̂ = e^{-t/2} Q(t), Q(t) = Σ c_k L_k(t); f = β^{d/2} e^{-u/2} R(u), R(u) = Σ (−1)^k c_k L_k(u).

**Certification procedure (all steps exact or interval-rigorous):**
1. The LP is solved in double precision exactly as in H1 (`../H1/lp_bound.py`, HiGHS via scipy, grids and cutting planes
   unchanged), giving floating coefficients c and a β. β is snapped to β = (α/π)·b with b a rational with denominator
   <= 1000 before the final solve.
2. c is converted to exact rationals (Python `fractions.Fraction` of the doubles). The Laguerre coefficients are rational
   (a = d/2 − 1 ∈ {−1/2, 0, 1/2}), so Q and R have exact rational monomial coefficients (sympy `Poly` over QQ).
3. **f̂ >= 0:** minimum of Q on [0, ∞) located by exact real-root isolation of Q' (sympy, QQ), Q evaluated exactly at the
   isolating intervals' endpoints and refined to width 1e-30; sign at infinity from the leading coefficient. If
   min Q < 0, set c_0 ← c_0 + δ with δ = −min Q + 1e-30 (rational), which adds δ to Q and δ to R (L_0 = 1). Then re-verify
   by exact Sturm count: Q has no root in [0, ∞) or only roots where Q >= 0 is proved (Q + δ > 0 strictly).
4. **f <= (1 + τ) g:** with κ = (1 − α/(πβ))/2 = (1 − 1/b)/2 (rational), the condition is
   β^{d/2} R(u) <= (1 + τ) e^{κu} for u >= 0. Verified by interval arithmetic (mpmath `iv`, 60 digits; β^{d/2} and π
   enclosed rigorously) on [0, U] by adaptive bisection: a box [u0, u1] is accepted if the interval enclosure of
   (1 + τ) e^{κu} − β^{d/2} R(u) (centred form: value at the midpoint plus derivative enclosure times half-width) is >= 0;
   boxes are split until accepted or narrower than 1e-14 (then τ is increased: τ ← 2τ, restart; start τ = 1e-12;
   give up at τ = 1e-6 and report "not certified"). Tail u > U: if κ > 0, U >= (deg R)/κ and the envelope
   β^{d/2} Σ|r_m| u^m e^{−κu} (decreasing for u >= deg/κ) is <= 1 at U, checked in interval arithmetic; if κ <= 0, the
   leading coefficient of R is negative and R has no real root > U (exact Sturm), and U is chosen beyond the largest root.
5. B = (Q(0) − β^{d/2} R(0)) / (1 + τ), evaluated in interval arithmetic; the **lower end** of the interval is reported.

**Validity check (void condition):** in d = 1 the certified B must be <= E_Z(α) = 2 Σ_{n>=1} e^{−α n²} (computed in
60-digit arithmetic). B > E_Z is impossible for a correct certificate; it voids the run (bug), it is not a result.

## Settings

d ∈ {1, 2, 3}; K ∈ {30, 40, 50} (the best certified B over K is reported, each K reported); β scan as in H1
(b ∈ {0.5, 0.7, 0.85, 1, 1.2, 1.5, 2, 3}, extended one step at an edge; final candidates at full settings); grids,
cutting-plane rounds and LP tolerances exactly as in `../H1/lp_bound.py` and `../H1/run_h1.py` at commit of this file.
The H1 admissibility tolerance (5e-9 on sampled violations) is NOT used: admissibility is now the certificate itself.

## Gates (in order; a failed gate stops the later ones)

- **V1 (d = 1):** α ∈ {1, π}: 0 <= E_Z(α) − B <= 1e-8 · E_Z(α) (B certified). Known answer: the LP bound is sharp in
  d = 1 (Cohn–Kumar; Table 1.1).
- **V2 (d = 2, α = π):** B >= 0.15959526 − 1e-8 (published LP value, Table 1.1). Also reported: E_A2(π) − B with E_A2
  the triangular-lattice energy computed here.
- **V3 (d = 3, α = π):** B >= 0.22321782 − 1e-8 (published LP value). Reported: B − 0.22321782 and the gap to
  min(E_FCC, E_BCC)(π) = 0.231536266184.
- **H1' (d = 3, α ∈ {2, 4, 8}), only if V1–V3 pass:** certified B and relative gap G = (min(E_FCC, E_BCC) − B)/min(...).
  Reading as registered for H1: G < 1e-6 → "LP has a chance at that α"; G > 1e-3 at all α → "two-point bounds insufficient
  at these α"; else inconclusive. **Prediction (stated before running, from the α = π value):** G > 1e-3 at all three α.
  A certified B > min(E_FCC, E_BCC) would contradict the known lattice energies and voids the run.

Failure of V1, V2 or V3 is reported as a failure of our code against a known answer, with the numbers; nothing after it
is run. Every run, including failures, is kept (`records/`, logs committed with `git add -f`).

## Not claimed

No new mathematics: the bound is Cohn–Kumar's, the α = π values are published. The certificates are computer-assisted
(sympy exact arithmetic, mpmath interval arithmetic); neither library is formally verified. Hostile review before any
deposit.
