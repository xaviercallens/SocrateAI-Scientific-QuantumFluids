# H1d — rigorous upper bounds on the two-point (Cohn–Kumar LP) bound for Gaussian energy (design, 2026-10-17)

Successor of H1''' (`../H1ppp/`, CLAIM-129), whose certified *lower* bounds B cannot show that two-point bounds fail to reach
the lattice energy (review item B2): that needs an *upper* bound on the LP optimum. Owner's choice 2026-10-17 ("dual-certificate
round").

## Literature gate (2026-10-17)

Read, via alphaXiv full-text extraction:
- Cohn & de Courcy-Ireland, arXiv:1603.09684 **v6**, pp. 1, 3–7, 9, 11, 13, 15, 19, 23, 25, 27, 29. Prop. 2.2 (LP bound:
  "every subset of R^n with density ρ has lower f-energy at least ρ ĥ(0) − h(0)" for h continuous, positive definite,
  integrable, h ≤ f off 0); Table 1.1 (n = 3: LP bound "0.22321782 . . ." = "numerically optimizing the auxiliary function",
  record "0.23153532 . . ."); §8, Lemma 8.3, which they describe as "using the distribution δ_0 + ρ − ρχ_r as a feasible point
  in the dual to the linear programming bound" (a crude dual, used for an energy *upper* bound on configurations, not on the
  LP bound). No upper bound on the LP bound itself in d = 3 is given in the pages read.
- R. Li, *Dual linear programming bounds for sphere packing via discrete reductions*, arXiv:2206.09876 **v3**, pp. 1–3, 8–9,
  11–15, 18, 20. Method: restrict f to Z^d (scaled), fold mod m, solve the finite dual LP, verify an exact rational dual point;
  proves the **Cohn–Elkies (sphere packing)** LP bound is not sharp for d = 3, 4, 5 (Thm 6.1: d = 3 bound > 0.18398089 with
  m = 53, r = √89). Sphere packing only; energy is not treated in the pages read.
- Two alphaXiv searches (dual LP bounds / Gaussian core / not sharp / energy) returned sphere-packing duals (Li; Cohn–
  Triantafillou via 2206.09876's account; de Courcy-Ireland–Dostert–Viazovska d = 6; arXiv:2607.11319 d = 36) and nothing on a
  dual for the Gaussian-energy LP in d = 3.

Conclusion: rigorous upper bounds on the Gaussian-energy LP bound in d = 3 appear not to be published; the energy adaptation
of Li's reduction below is ours (derivation to be checked by the reviewer). If a reader knows prior work, the claim reduces to
an independent computation.

## The reduction (energy version)

Class 𝓗: h : R^d → R continuous, radial, with |h(x)|, |ĥ(x)| ≤ C(1+|x|)^{-d-δ} (so Poisson summation holds pointwise with
absolutely convergent sums), ĥ ≥ 0, and h(x) ≤ g(x) := e^{-α|x|²} for x ≠ 0. LP(α) := sup_{h∈𝓗} ĥ(0) − h(0) (density 1).
The CdCI numerical functions and our H1'' / H1''' functions (Gaussian × polynomial) are in 𝓗. Whether the supremum over the
wider class of Prop. 2.2 (no decay assumption) can exceed LP(α) is not addressed.

Fix rational s > 1, integer m ≥ 2. For x ∈ Z_m^d put G(x) = Σ_{n∈Z^d, n≡x} h(n/s) and Γ(x) = Σ_{n≡x, n≠0} g(n/s).
1. Ĝ(y) := Σ_x G(x) e^{-2πi⟨x,y⟩/m} = Σ_n h(n/s) e^{-2πi⟨n,y⟩/m} = s^d Σ_{k∈Z^d} ĥ(s(k + y/m)) ≥ 0 (Poisson).
2. Ĝ(0) = s^d Σ_k ĥ(sk) ≥ s^d ĥ(0), so ĥ(0) ≤ s^{-d} Σ_x G(x).
3. For x ≢ 0 every n ≡ x is nonzero: G(x) ≤ Γ(x). For x ≡ 0: G(0) = h(0) + Σ_{n∈mZ^d∖0} h(n/s) ≤ h(0) + Γ(0).
4. Hence ĥ(0) − h(0) ≤ s^{-d} Σ_x G(x) − G(0) + Γ(0).
5. Weak duality: let λ ≥ 0 on Z_m^d, even, with Σ_y λ(y) = 1 − s^{-d}, and μ(x) := s^{-d} + Σ_y λ(y) cos(2π⟨x,y⟩/m) ≥ 0 for
   x ≠ 0. Then for every G, s^{-d} Σ_x G(x) − G(0) = Σ_{x≠0} μ(x) G(x) − Σ_y λ(y) Ĝ(y) (coefficient of G(0): s^{-d} − 1 =
   −Σλ; of G(x), x ≠ 0: s^{-d} = μ(x) − Σ_y λ(y)cos(…)). With G ≤ Γ off 0, μ ≥ 0, λ ≥ 0, Ĝ ≥ 0:
   **LP(α) ≤ UB := Γ(0) + Σ_{x≠0} μ(x) Γ(x).**
Sanity: λ = (1 − s^{-d})δ_0 gives μ ≡ 1 and UB = energy of (1/s)Z^d (density s^d). (Corrected 2026-10-17 after the
pre-run review, minor 1: for a density-1 sublattice L ⊂ (1/s)Z^d with s^d integer and mZ^d ⊆ sL, the choice is λ = s^{-d} on
the dual group *minus 0*, giving UB = E(L); the earlier wording "normalised indicator" was wrong. The code does not use this.)

Computation (`dual.py`): signed-permutation orbits; float LP (HiGHS) for λ with μ ≥ ε = 1e-8; then certify: λ → rationals
(clip at 0, exact renormalisation), μ and UB in arb (cosine matrix contraction; theta sums Γ = Π θ(x_i) − [x = 0] with a rigorous
geometric tail bound); μ > 0 checked as balls. Any (s, m) gives a valid UB; the minimum over a registered ladder is reported.

## Development (non-gate parameters only: d = 1 α = 2; d = 2 α = 2; d = 3 α = 1, 1.5, 3, 6)

- d = 1, α = 2 (LP sharp, = E_Z): certified UB − E_Z = 1.3e-8 … 5.6e-8 relative for (s, m) from (2, 8) to (8, 128), i.e.
  the ε-buffer cost; never below E_Z.
- d = 2, α = 2: UB − E_A2 = 0.69%, 0.77%, 0.42%, 0.33% at (2,16), (3,24), (4,32), (4,48) — slow convergence (A2 is not
  in a rational grid).
- d = 3: UB/min(FCC,BCC) − 1 at (4, 24): −5.4e-6 (α=1), −3.1e-4 (α=1.5), −1.5e-2 (α=3), −4.0e-2 (α=6); larger α needs
  larger s. α = 1, (4, 24): certified UB [4.568569262229 ± 9.6e-13] in 6 s, equal to the float value.
