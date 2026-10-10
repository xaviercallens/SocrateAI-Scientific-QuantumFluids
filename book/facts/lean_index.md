# Lean library index (auto-generated; statements truncated at `:=`)

Namespaces: 24 of the 37 modules live in `QuantumFluids.<Module>`; the other 13 do not (table in `facts/lean_namespaces.md`). Quote theorem names exactly as written here.

Total theorems/lemmas indexed: **310**


## BoseIntegral

```
The Bose integral behind the phonon specific heat of superfluid helium.

[G21] = Godfrin et al., Phys. Rev. B 103, 104516 (2021), Eq. (22): the phonon specific heat is a
series `C_V = A T³ + C T⁵ + D T⁶ + …` whose coefficients come from Bose integrals
`∫₀^∞ tⁿ/(eᵗ − 1) dt = Γ(n+1) ζ(n+1)`. The paper remarks that earlier published versions of this
series "contain errors". This file machine-checks the integral that fixes the leading (Debye)
coefficient `A`, and states the general Mellin identity from which every other coefficient follows.

Mathlib has `ζ(4) = π⁴/90` and the Gamma integral, but not the Bose integral; the bridge is
`hasSum_mellin` applied to `1/(eᵗ − 1) = Σₙ e^{-(n+1)t}`.

`mellin F s` is, by definition, `∫ t in Ioi 0, t^(s-1) • F t`, so `mellin bose 4` IS
`∫₀^∞ t³/(eᵗ − 1) dt`.
```

- `def bose`: `noncomputable def bose (t : ℝ) : ℂ`
- `theorem hasSum_bose`: `theorem hasSum_bose {t : ℝ} (ht : t ∈ Ioi (0 : ℝ)) : HasSum (fun n : ℕ => (1 : ℂ) * rexp (-((n : ℝ) + 1) * t)) (bose t)`
- `theorem hasSum_mellin_bose`: `theorem hasSum_mellin_bose {s : ℂ} (hs : 1 < s.re) : HasSum (fun n : ℕ => Complex.Gamma s * 1 / (((n : ℝ) + 1 : ℝ) : ℂ) ^ s) (mellin bose s)`
- `theorem mellin_bose_four`: `theorem mellin_bose_four : mellin bose 4 = (π : ℂ) ^ 4 / 15`
- `theorem bose_integral_nat`: `theorem bose_integral_nat {n : ℕ} (hn : 1 ≤ n) : mellin bose (n + 1) = (Nat.factorial n : ℂ) * riemannZeta (n + 1)`
- `theorem bose_integral_even`: `theorem bose_integral_even {k : ℕ} (hk : k ≠ 0) : mellin bose ((2 * k - 1 : ℕ) + 1) = (Nat.factorial (2 * k - 1) : ℂ) * ((-1) ^ (k + 1) * (2 : ℂ) ^ (2 * k - 1) * (π : ℂ) ^ (2 * k) * bernoulli (2 * k) / Nat.factorial (2 * k))`
- `def debyeEnergy`: `noncomputable def debyeEnergy (V kB hbar c I T : ℝ) : ℝ`
- `theorem debyeEnergy_eq`: `theorem debyeEnergy_eq (V kB hbar c T : ℝ) : debyeEnergy V kB hbar c (π ^ 4 / 15) T = π ^ 2 * V * (kB * T) ^ 4 / (30 * (hbar * c) ^ 3)`
- `theorem debye_specific_heat`: `theorem debye_specific_heat (V kB hbar c T : ℝ) : HasDerivAt (fun T => debyeEnergy V kB hbar c (π ^ 4 / 15) T) (2 * π ^ 2 * kB ^ 4 * V / (15 * c ^ 3 * hbar ^ 3) * T ^ 3) T`

## ChargeLattice

```
ChargeLattice.lean -- two cosmological charge lattices stated so that the kernel reads off the same
  distinction as `CompactBoson.lean`: the duality is a relabelling of the sectors; what the physics depends
  on is a function of the sector alone.

  Boundary note (added after a 2026-09-26 literature review): Moore's theorem N(D) = h(D) below is exact in the
  1/8-BPS K3 × T² setting this file states. It does NOT generalise unqualified to 1/4-BPS dyons on heterotic/T^6
  (a different setting): there, Dabholkar-Gaiotto-Nampuri (arXiv:hep-th/0702150) show the continuous-duality
  invariants alone "do not uniquely specify the state," an extra discrete invariant (gcd of the charges) is
  needed, and Sen (arXiv:0705.3874) shows the degeneracy further jumps across walls of marginal stability in
  moduli space. "Entropy is a function of the sector" is correct exactly as stated here (K3 × T², Moore's
  charges); it is not a general claim about every dyon-counting problem in string theory.

  Second boundary note (2026-09-26, same review): `disc_sl2_invariant` applies verbatim, with no new theorem,
  to a second physical setting -- the exact quarter-BPS D1-D5-P dyon lifted to 4D by an extra Kaluza-Klein-
  monopole charge. Sen's precision-counting review (arXiv:0708.1270, eq. 5.3.5-5.3.6) shows the exact
  microscopic degeneracy of that system is a function only of the T-duality invariants Q², P², Q·P of two
  charge vectors (Q, P) -- i.e. of Δ = Q²P² − (Q·P)², algebraically identical to D(p, q) above, with B taken
  to be the Narain bilinear form. `disc_sl2_invariant B hB hdet Q P` (this file, unchanged) already states
  Δ's SL(2, ℤ)-invariance for that instantiation; nothing further needed formalizing. What does NOT transfer:
  the class-number statement N(D) = h(D) above, since (per the first boundary note, Dabholkar-Gaiotto-Nampuri
  and Sen arXiv:0705.3874) Δ alone under-determines the state in this 4-charge setting -- no second Moore-style
  theorem is claimed. The historically prior Strominger-Vafa two-charge (hep-th/9601029) and Callan-Maldacena
  three-charge (hep-th/9602043) entropy formulas are explicitly OUT OF SCOPE for `disc`: their charge data
  (Q_H, Q_F, or Q1, Q5, n) is not a pair of vectors under one bilinear form, so no relabelling of `disc` covers
  them, and both formulas are leading-order Cardy approximations, not exact identities, by their own authors'
  statement.

  Part 1 -- the dyon charge lattice of type II on K3 × T² (Moore, "Arithmetic and attractors", 1998).
  A dyon is a pair (p, q) of vectors in an integral lattice Λ with a symme
```

- `def disc`: `def disc (p q : Λ) : ℤ`
- `theorem gram_pp`: `theorem gram_pp (hB : B.IsSymm) (a b : ℤ) (p q : Λ) : B (a • p + b • q) (a • p + b • q) = a ^ 2 * B p p + 2 * a * b * B p q + b ^ 2 * B q q`
- `theorem gram_pq`: `theorem gram_pq (hB : B.IsSymm) (a b c d : ℤ) (p q : Λ) : B (a • p + b • q) (c • p + d • q) = a * c * B p p + (a * d + b * c) * B p q + b * d * B q q`
- `theorem disc_sl2`: `theorem disc_sl2 (hB : B.IsSymm) (a b c d : ℤ) (p q : Λ) : disc B (a • p + b • q) (c • p + d • q) = (a * d - b * c) ^ 2 * disc B p q`
- `theorem disc_sl2_invariant`: `theorem disc_sl2_invariant (hB : B.IsSymm) {a b c d : ℤ} (hdet : a * d - b * c = 1) (p q : Λ) : disc B (a • p + b • q) (c • p + d • q) = disc B p q`
- `theorem disc_electric_magnetic_swap`: `theorem disc_electric_magnetic_swap (hB : B.IsSymm) (p q : Λ) : disc B q (-p) = disc B p q`
- `theorem disc_scale`: `theorem disc_scale (hB : B.IsSymm) (t : ℤ) (p q : Λ) : disc B (t • p) (t • q) = t ^ 4 * disc B p q`
- `theorem disc_zero_of_parallel`: `theorem disc_zero_of_parallel (hB : B.IsSymm) (k : ℤ) (p : Λ) : disc B p (k • p) = 0`
- `theorem area_sl2_invariant`: `theorem area_sl2_invariant (hB : B.IsSymm) {a b c d : ℤ} (hdet : a * d - b * c = 1) (p q : Λ) : Real.sqrt (-(disc B (a • p + b • q) (c • p + d • q) : ℝ)) = Real.sqrt (-(disc B p q : ℝ))`
- `def bpLambda`: `noncomputable def bpLambda {J : ℕ} (Λbare : ℝ) (q : Fin J → ℝ) (n : Fin J → ℤ) : ℝ`
- `def nucleate`: `def nucleate {J : ℕ} (n : Fin J → ℤ) (i : Fin J) : Fin J → ℤ`
- `theorem bp_step`: `theorem bp_step {J : ℕ} (Λbare : ℝ) (q : Fin J → ℝ) (n : Fin J → ℤ) (i : Fin J) : bpLambda Λbare q (nucleate n i) - bpLambda Λbare q n = -((n i : ℝ) - 1 / 2) * q i ^ 2`
- `theorem bp_step_neg_iff`: `theorem bp_step_neg_iff {J : ℕ} (Λbare : ℝ) (q : Fin J → ℝ) (n : Fin J → ℤ) (i : Fin J) (hq : q i ≠ 0) : bpLambda Λbare q (nucleate n i) < bpLambda Λbare q n ↔ 1 ≤ n i`
- `theorem bp_ge_bare`: `theorem bp_ge_bare {J : ℕ} (Λbare : ℝ) (q : Fin J → ℝ) (n : Fin J → ℤ) : bpLambda Λbare q 0 ≤ bpLambda Λbare q n`
- `theorem bp_min_at_zero`: `theorem bp_min_at_zero {J : ℕ} (Λbare : ℝ) (q : Fin J → ℝ) (hq : ∀ i, q i ≠ 0) (n : Fin J → ℤ) : bpLambda Λbare q n = bpLambda Λbare q 0 ↔ n = 0`
- `def kaloperV`: `noncomputable def kaloperV (X θ : ℝ) (N : ℤ) : ℝ`
- `theorem kaloper_step`: `theorem kaloper_step (X θ : ℝ) (N : ℤ) : kaloperV X θ N - kaloperV X θ (N + 1) = X * θ ^ 2 * (((1 : ℝ) - N) - 1 / 2)`
- `theorem kaloper_min`: `theorem kaloper_min (X θ : ℝ) (hX : 0 < X) (hθ : θ ≠ 0) (N : ℤ) : 0 ≤ kaloperV X θ N ∧ (kaloperV X θ N = 0 ↔ N = 1)`
- `theorem kaloper_terminates`: `theorem kaloper_terminates (X θ : ℝ) (N : ℤ) (hN : N ≤ 1) : kaloperV X θ (N + ((1 - N).toNat : ℤ)) = 0`

## CompactBoson

```
CompactBoson.lean -- the T-duality of the compact boson stated on its SECTORS, so that three things can be
  read off the kernel: the duality is a reindexing of the sector lattice; the product of the electric and
  magnetic dimensions does not depend on the radius; the self-dual radius is not where the vortex becomes
  marginal.

  Conventions (α' = 2, the CFT normalisation in which the self-dual radius is √2). For a compact boson of radius
  `R`, the primary of momentum `n` and winding `w` has
      h    = ½ (n/R + w R/2)²,   h̄ = ½ (n/R − w R/2)²,
      Δ    = h + h̄ = n²/R² + w² R²/4,     spin s = h − h̄ = n w.
  The electric (spin-wave, `e^{iθ}`) operator is (n, w) = (1, 0); the magnetic (vortex) operator is (0, 1).
  In the XY / superfluid dictionary Δ(1,0) = η/2 and Δ(0,1) = n_s λ_T² / 2, so `Δ(1,0)·Δ(0,1) = 1/4` is the
  relation `η · n_s λ_T² = 1` tested in rounds 2 and 3, and `Δ(0,1) = 2` is the Nelson–Kosterlitz condition
  `n_s λ_T² = 4`.

  * `dim_dual`            : Δ(n, w; R) = Δ(w, n; 2/R) -- T-duality exchanges momentum and winding sectors;
  * `spin_dual`           : the spin is invariant;
  * `partition_dual`      : the sector sum Σ_{(n,w)} F(Δ, s) is invariant under R ↦ 2/R -- because the duality is a
                            bijection of ℤ² (no summability hypothesis is needed: `Equiv.tsum_eq`);
  * `electric_mul_magnetic`: Δ(1,0)·Δ(0,1) = 1/4 for every R -- the duality-invariant product;
  * `selfDual_radius`     : Δ(1,0) = Δ(0,1) iff R = √2 (R > 0), where both equal 1/2;
  * `vortex_marginal_radius`: Δ(0,1) = 2 iff R = 2√2;
  * `bkt_not_selfDual`    : the two radii differ -- the transition set by the marginality of one sector is not the
                            fixed point of the exchange symmetry.

  What this module says, and only this: on the sector lattice the duality is a relabelling that preserves the
  spectrum; the physical thresholds are conditions on single sectors. Nothing about dynamics, nothing about K3
  surfaces, nothing about any particular fluid.
```

- `def dim`: `noncomputable def dim (R : ℝ) (n w : ℤ) : ℝ`
- `def spin`: `def spin (n w : ℤ) : ℤ`
- `theorem dim_dual`: `theorem dim_dual (R : ℝ) (hR : R ≠ 0) (n w : ℤ) : dim R n w = dim (2 / R) w n`
- `theorem spin_dual`: `theorem spin_dual (n w : ℤ) : spin n w = spin w n`
- `def swap`: `def swap : ℤ × ℤ ≃ ℤ × ℤ`
- `theorem partition_dual`: `theorem partition_dual (R : ℝ) (hR : R ≠ 0) (F : ℝ → ℤ → ℝ) : ∑' p : ℤ × ℤ, F (dim R p.1 p.2) (spin p.1 p.2) = ∑' p : ℤ × ℤ, F (dim (2 / R) p.1 p.2) (spin p.1 p.2)`
- `theorem dim_electric`: `theorem dim_electric (R : ℝ) : dim R 1 0 = 1 / R ^ 2`
- `theorem dim_magnetic`: `theorem dim_magnetic (R : ℝ) : dim R 0 1 = R ^ 2 / 4`
- `theorem electric_mul_magnetic`: `theorem electric_mul_magnetic (R : ℝ) (hR : R ≠ 0) : dim R 1 0 * dim R 0 1 = 1 / 4`
- `theorem eq_of_sq_eq_sq_pos`: `theorem eq_of_sq_eq_sq_pos {a b : ℝ} (ha : 0 < a) (hb : 0 < b) (h : a ^ 2 = b ^ 2) : a = b`
- `theorem selfDual_radius`: `theorem selfDual_radius {R : ℝ} (hR : 0 < R) : dim R 1 0 = dim R 0 1 ↔ R = Real.sqrt 2`
- `theorem selfDual_value`: `theorem selfDual_value : dim (Real.sqrt 2) 1 0 = 1 / 2 ∧ dim (Real.sqrt 2) 0 1 = 1 / 2`
- `theorem vortex_marginal_radius`: `theorem vortex_marginal_radius {R : ℝ} (hR : 0 < R) : dim R 0 1 = 2 ↔ R = 2 * Real.sqrt 2`
- `theorem bkt_not_selfDual`: `theorem bkt_not_selfDual : (2 * Real.sqrt 2 : ℝ) ≠ Real.sqrt 2`
- `theorem eta_at_bkt`: `theorem eta_at_bkt : dim (2 * Real.sqrt 2) 1 0 = 1 / 8`

## ContinuumWinding

```
ContinuumWinding.lean -- "Rome": the discrete winding number equals the continuum degree.

  `VortexWinding.lean` proves that the sampled loop sum of principal phase differences is an integer
  multiple of `2π`, and leaves open, explicitly, whether that integer is the TRUE topological charge of
  the continuum field ("a statement about sampling, not about the algorithm"). This file closes that
  gap for a closed loop of field values.

  * `pdiff_congr`          : the principal difference depends only on the two angles, not on the
                             representatives `arg` happens to return;
  * `sum_pdiff_telescope`  : when every true phase step is a principal value the loop sum telescopes to
                             the total phase change;
  * `discrete_eq_degree`   : for any continuous closed loop of ANGLES `γ : C(I, Real.Angle)` there is an
                             integer `w` (the degree: the total change of a continuous lift, divided by
                             `2π`) and a sampling threshold `n₀` such that, for every `n ≥ n₀` and every
                             choice of representatives of the `n` sampled angles, the discrete loop sum
                             is exactly `2π w`. The lift is Mathlib's path lifting through the covering
                             `ℝ → ℝ/2πℤ`; the threshold comes from Heine–Cantor;
  * `detector_correct`     : for a continuous, nowhere-vanishing, closed loop of FIELD VALUES
                             `c : C(I, ℂ)`, the phase-winding detector applied to `arg (c (i/n))`
                             returns `2π w` for all `n ≥ n₀`.

  What this settles: the number a GPE code computes around a plaquette is the degree of `ψ/|ψ|`
  along that plaquette's boundary, once the grid resolves the phase (no true step of size ≥ π). What
  a phase slip is in the continuum: the hypothesis `c t ≠ 0` failing -- a zero of `ψ` on the loop,
  where the angle loop, and with it the lift and the degree, cease to exist.

  NOT PROVED: any statement about the field OFF the loop (that the degree counts zeros inside, the
  argument principle) -- Mathlib's pinned version has no argument principle for general continuous
  maps, and the plaquette-additivity of `ScaleResolvedWinding.lean` is the discrete substitute; any
  quantitative link between the grid spacing and `n₀` (that needs a modulus of continuity of `ψ`).
```

- `theorem pdiff_congr`: `theorem pdiff_congr {a a' b b' : ℝ} (ha : (a : Real.Angle) = a') (hb : (b : Real.Angle) = b') : pdiff a b = pdiff a' b'`
- `theorem sum_pdiff_telescope`: `theorem sum_pdiff_telescope (Γ : ℕ → ℝ) (n : ℕ) (h : ∀ i < n, Γ (i + 1) - Γ i ∈ Set.Ioc (-π) π) : ∑ i ∈ Finset.range n, pdiff (Γ i) (Γ (i + 1)) = Γ n - Γ 0`
- `theorem degree_int`: `theorem degree_int (x y : ℝ) (h : (x : Real.Angle) = y) : ∃ w : ℤ, x - y = (w : ℝ) * (2 * π)`
- `def sample`: `noncomputable def sample (n i : ℕ) : I`
- `theorem sample_zero`: `theorem sample_zero (n : ℕ) : sample n 0 = 0`
- `theorem sample_self`: `theorem sample_self (n : ℕ) (hn : 0 < n) : sample n n = 1`
- `theorem sample_val`: `theorem sample_val (n i : ℕ) (hi : i ≤ n) (hn : 0 < n) : (sample n i : ℝ) = (i : ℝ) / n`
- `theorem dist_sample`: `theorem dist_sample (n i : ℕ) (hi : i < n) : dist (sample n (i + 1)) (sample n i) = 1 / n`
- `theorem discrete_eq_degree`: `theorem discrete_eq_degree (γ : C(I, Real.Angle)) (hclosed : γ 1 = γ 0) : ∃ w : ℤ, ∃ n₀ : ℕ, 0 < n₀ ∧ ∀ n ≥ n₀, ∀ θ : ℕ → ℝ, (∀ i ≤ n, (θ i : Real.Angle) = γ (sample n i)) → ∑ i ∈ Finset.range n, pdiff (θ i) (θ (i + 1)) = (w : ℝ) * (2 * π)`
- `theorem detector_correct`: `theorem detector_correct (c : C(I, ℂ)) (hne : ∀ t, c t ≠ 0) (hclosed : c 1 = c 0) : ∃ w : ℤ, ∃ n₀ : ℕ, 0 < n₀ ∧ ∀ n ≥ n₀, ∑ i ∈ Finset.range n, pdiff (Complex.arg (c (sample n i))) (Complex.arg (c (sample n (i + 1)))) = (w : ℝ) * (2 * π)`

## DissipativeVortexDynamics

```
DissipativeVortexDynamics.lean -- the dissipative point-vortex model behind the friction, transverse-force
  and Einstein-relation measurements (docs/designs/PGPE_FRICTION_PREREG.md amendment A1,
  PGPE_ALPHAPRIME_PREREG.md, PGPE_EINSTEIN_PREREG.md).

  Model (hbar = m = 1, circulation 2 pi, normal fluid at rest): a vortex of charge q moves at
      v = (1 - alpha') v_s  -  alpha q  z x v_s,
  v_s the superfluid velocity induced at its position by the other vortices. With the vortex Hamiltonian H
  (plane: -sum q_i q_j ln r_ij^2; torus: the Weiss-McWilliams sum) one has v_s,i = -(q_i/2) z x grad_i H, so the
  whole configuration obeys   r' = A(grad H) - (alpha/2) grad H   with A pointwise skew (it contains alpha').

  1. `energy_dissipation`: for ANY such flow, d/dt H(r(t)) = -gamma |grad H|^2, whatever the skew part.
     Consequences used by the analysis: (i) alpha = -(dH/dt) / (2 sum_i |v_s,i|^2) is an estimator of the
     longitudinal friction valid for any number of vortices on the plane or the torus; (ii) it does not depend
     on alpha' -- longitudinal and transverse coefficients are measured by orthogonal observables.
  2. Plane dipole, in coordinates: |d|^2 = |d_0|^2 - 4 alpha t (`dipole_sq_law`), lifetime below
     |d_0|^2/(4 alpha) (`dipole_lifetime_bound`), and the centre moves at speed (1 - alpha')/|d| perpendicular to
     the pair axis (`centre_velocity_identity`): the translation speed measures alpha', the shrinking alpha.
  3. `wind_stall`: in a closed box the pair's impulse goes to the phonons, whose drift u reduces the drive:
     d' = -2 alpha (1/d - w (d_0 - d)), w = 2 pi rho_s/(rho_n L^2). When w d_0^2 > 4 the right-hand side has
     two positive zeros a < b (a + b = d_0, a b = 1/w) and the pair NEVER gets below b: it stalls instead of
     annihilating. The pre-registered wind hypothesis W predicts b from measured rho_n with no free parameter.

  Elementary calculus; nothing here is new mathematics (the gradient-flow structure of dissipative vortex
  motion is classical: Ambegaokar-Halperin-Nelson-Siggia 1980; Kurzke-Melcher-Moser-Spirn 2009 for the
  mixed flow). What is formal is that the estimators used on the data are identities of the model.
```

- `theorem energy_dissipation`: `theorem energy_dissipation (H : X → ℝ) (gradH : X → X) (hH : ∀ x, HasGradientAt H (gradH x) x) (A : X → X) (hA : ∀ v, inner ℝ v (A v) = 0) (γ : ℝ) (r : ℝ → X) (hr : ∀ t, HasDerivAt r (A (gradH (r t)) - γ • gradH (r t)) t) (t : ℝ) : HasDerivAt (fun t => H (r t)) (-γ * ‖gradH (r t)‖ ^ 2) t`
- `theorem energy_antitone`: `theorem energy_antitone (H : X → ℝ) (gradH : X → X) (hH : ∀ x, HasGradientAt H (gradH x) x) (A : X → X) (hA : ∀ v, inner ℝ v (A v) = 0) {γ : ℝ} (hγ : 0 ≤ γ) (r : ℝ → X) (hr : ∀ t, HasDerivAt r (A (gradH (r t)) - γ • gradH (r t)) t) : Antitone (fun t => H (r t))`
- `theorem dissipation_indep_of_skew`: `theorem dissipation_indep_of_skew (H : X → ℝ) (gradH : X → X) (hH : ∀ x, HasGradientAt H (gradH x) x) (A B : X → X) (hA : ∀ v, inner ℝ v (A v) = 0) (hB : ∀ v, inner ℝ v (B v) = 0) (γ : ℝ) (r s : ℝ → X) (hr : ∀ t, HasDerivAt r (A (gradH (r t)) - γ • gradH (r t)) t) (hs : ∀ t, HasDerivAt s (B (gradH (`
- `def r2`: `noncomputable def r2 (t : ℝ) : ℝ`
- `theorem r2_hasDerivAt`: `theorem r2_hasDerivAt (t : ℝ) (ht : t ∈ Icc (0 : ℝ) T) : HasDerivAt (r2 px py mx my) (-4 * α) t`
- `theorem dipole_sq_law`: `theorem dipole_sq_law (t : ℝ) (ht : t ∈ Icc (0 : ℝ) T) : r2 px py mx my t = r2 px py mx my 0 - 4 * α * t`
- `theorem dipole_lifetime_bound`: `theorem dipole_lifetime_bound (hα : 0 < α) (hT : 0 ≤ T) : T < r2 px py mx my 0 / (4 * α)`
- `theorem centre_velocity_identity`: `theorem centre_velocity_identity (t : ℝ) (ht : t ∈ Icc (0 : ℝ) T) : ∃ cx' cy' : ℝ, HasDerivAt (fun s => (px s + mx s) / 2) cx' t ∧ HasDerivAt (fun s => (py s + my s) / 2) cy' t ∧ cx' * (py t - my t) - cy' * (px t - mx t) = 1 - α' ∧ cx' * (px t - mx t) + cy' * (py t - my t) = 0 ∧ (cx' ^ 2 + cy' ^ 2) `
- `theorem wind_stall`: `theorem wind_stall {a b c : ℝ} (ha : 0 < a) (hab : a < b) (hc : 0 < c) (d : ℝ → ℝ) (hd : ∀ t, HasDerivAt d (-c * (d t - a) * (d t - b) / d t) t) (h0 : b ≤ d 0) : ∀ t, 0 ≤ t → b ≤ d t`
- `theorem stall_of_drive_sign`: `theorem stall_of_drive_sign {a b c : ℝ} (hab : a < b) (hc : 0 < c) (g : ℝ → ℝ) (hg : ∀ x, a < x → x < b → g x < 0) (d : ℝ → ℝ) (hd : ∀ t, HasDerivAt d (-c * g (d t)) t) (h0 : b ≤ d 0) : ∀ t, 0 ≤ t → b ≤ d t`

## DualLength

```
The dual length of a quantum fluid (design memo docs/designs/DUAL_SCALE_QUANTUM_FLUID.md; CLAIM-024).

For a fluid with excitation energy `ε(k)`, sound speed `c` and `hc := ħc`, define

    ℓ(k) := ε(k)² / (hc² k³).

`ℓ` is measurable: `ε` is what neutron scattering reports and `c` is the `k → 0` slope.
This file proves, for the Bogoliubov dispersion `ε² = (hc·k)² + (hc·k²/ks)²` with
`ks = 2mc/ħ`:

  * `dualLength_bogoliubov` : ℓ = 1/k + k/ks²  — the `R + α'/R` form, with `R = 1/k`, `α' = 1/ks²`;
  * `ell_dual_invariant`    : ℓ is invariant under the involution `k ↦ ks²/k`, which exchanges
                              the phonon and free-particle terms;
  * `ell_ge`, `ell_eq_iff`  : ℓ ≥ 2/ks, with equality exactly at the self-dual point `k = ks`;
  * `dualLength_phonon`, `dualLength_free` : the two limits are exactly `1/k` and `k/ks²`;
  * `not_bogoliubov_of_lt`  : a MEASURED ℓ below `2/ks` refutes the Bogoliubov form at that `k`.
    This is the lemma the He-II measurement uses (measured ℓ/(2/ks) = 0.047 at the roton).

NOT claimed: anything about string theory or T-duality (the shape is AM-GM on two positive terms);
anything about the real ⁴He dispersion, which is measured data, not a theorem; any dynamical statement.
```

- `def dualLength`: `noncomputable def dualLength (hc k epsSq : ℝ) : ℝ`
- `def bogoliubovSq`: `noncomputable def bogoliubovSq (hc ks k : ℝ) : ℝ`
- `def ell`: `noncomputable def ell (ks k : ℝ) : ℝ`
- `theorem dualLength_phonon`: `theorem dualLength_phonon {hc k : ℝ} (hhc : hc ≠ 0) (hk : k ≠ 0) : dualLength hc k ((hc * k) ^ 2) = 1 / k`
- `theorem dualLength_free`: `theorem dualLength_free {hc ks k : ℝ} (hhc : hc ≠ 0) (hk : k ≠ 0) (hks : ks ≠ 0) : dualLength hc k ((hc * k ^ 2 / ks) ^ 2) = k / ks ^ 2`
- `theorem dualLength_bogoliubov`: `theorem dualLength_bogoliubov {hc ks k : ℝ} (hhc : hc ≠ 0) (hk : k ≠ 0) (hks : ks ≠ 0) : dualLength hc k (bogoliubovSq hc ks k) = ell ks k`
- `theorem dual_involutive`: `theorem dual_involutive {ks k : ℝ} (hk : k ≠ 0) (hks : ks ≠ 0) : ks ^ 2 / (ks ^ 2 / k) = k`
- `theorem ell_dual_invariant`: `theorem ell_dual_invariant {ks k : ℝ} (hk : k ≠ 0) (hks : ks ≠ 0) : ell ks (ks ^ 2 / k) = ell ks k`
- `theorem ell_ge`: `theorem ell_ge {ks k : ℝ} (hk : 0 < k) (hks : 0 < ks) : 2 / ks ≤ ell ks k`
- `theorem ell_eq_iff`: `theorem ell_eq_iff {ks k : ℝ} (hk : 0 < k) (hks : 0 < ks) : ell ks k = 2 / ks ↔ k = ks`
- `theorem not_bogoliubov_of_lt`: `theorem not_bogoliubov_of_lt {hc ks k epsSq : ℝ} (hhc : hc ≠ 0) (hk : 0 < k) (hks : 0 < ks) (hmeas : dualLength hc k epsSq < 2 / ks) : epsSq ≠ bogoliubovSq hc ks k`
- `theorem ell_ge_iff_envelope`: `theorem ell_ge_iff_envelope {hc ks k epsSq : ℝ} (hhc : hc ≠ 0) (hk : 0 < k) (hks : 0 < ks) : 2 / ks ≤ dualLength hc k epsSq ↔ 2 * hc ^ 2 / ks * k ^ 3 ≤ epsSq`
- `theorem bogoliubov_envelope`: `theorem bogoliubov_envelope {hc ks k : ℝ} (hhc : hc ≠ 0) (hk : 0 < k) (hks : 0 < ks) : 2 * hc ^ 2 / ks * k ^ 3 ≤ bogoliubovSq hc ks k`
- `theorem dualLength_feynman`: `theorem dualLength_feynman {hc ks k S : ℝ} (hhc : hc ≠ 0) (hk : k ≠ 0) (hks : ks ≠ 0) (hS : S ≠ 0) : dualLength hc k ((hc * k ^ 2 / (ks * S)) ^ 2) = k / (ks ^ 2 * S ^ 2)`
- `theorem feynman_ge_iff`: `theorem feynman_ge_iff {ks k S : ℝ} (_hk : 0 < k) (hks : 0 < ks) (hS : 0 < S) : 2 / ks ≤ k / (ks ^ 2 * S ^ 2) ↔ S ^ 2 ≤ k / (2 * ks)`
- `theorem not_bogoliubov_of_structure_factor`: `theorem not_bogoliubov_of_structure_factor {hc ks k S epsSq : ℝ} (hhc : hc ≠ 0) (hk : 0 < k) (hks : 0 < ks) (hS : 0 < S) (hfeyn : epsSq ≤ (hc * k ^ 2 / (ks * S)) ^ 2)        -- Feynman's variational bound (hpeak : k / (2 * ks) < S ^ 2) :                      -- measured: S above the dual-scale bound`

## Duality

```
=============================================================================
MATHESIS — Duality/SelfDual.lean
The Abstract Self-Dual Bound and Its First Instances (Rung 0 + Rung 1)
=============================================================================

Status  : DRAFT pending human audit (Mathesis L4.4).
Rules   : zero `axiom` declarations (L4.1); every claim kernel-checked or
          explicitly commented as TARGET; footprint audited at end of file.
Purpose : "One theorem, many instances." The programme's dual-scale bound
          (Reff_ge_sqrt), the finite-Fourier support balance, the EOQ
          inventory bound, and the Kramers–Wannier critical point are all
          instances of two elementary facts about products and duals:

            (multiplicative)  C ≤ x·y            →  √C ≤ max(x,y)
            (additive twin)   2·√(x·y) ≤ x + y   (AM–GM, two terms)
            (fixed point)     x = C/x  ↔  x = √C     (x > 0)

          Physics enters only through WHICH product is conserved; the
          mathematics of the bound is domain-free. That is the precise
          sense in which the dual-scale principle "generalizes".

Integration note (QuantumFluids):
  This Duality module is imported by Mathesis (Stream 0). QuantumFluids
  applies it to the quantum-fluid case: the conserved product is
  R · (α'/R) = α' (roton gap × length scale → kinematic viscosity).
  See docs/ROSETTA_ROW.md for term mapping.

=============================================================================
```

- `theorem sqrt_le_max_of_le_mul`: `theorem sqrt_le_max_of_le_mul {C x y : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y) (h : C ≤ x * y) : Real.sqrt C ≤ max x y`
- `theorem min_le_sqrt_of_mul_le`: `theorem min_le_sqrt_of_mul_le {C x y : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y) (h : x * y ≤ C) : min x y ≤ Real.sqrt C`
- `theorem sqrt_between_duals`: `theorem sqrt_between_duals {C x y : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y) (h : x * y = C) : min x y ≤ Real.sqrt C ∧ Real.sqrt C ≤ max x y`
- `theorem two_sqrt_mul_le_add`: `theorem two_sqrt_mul_le_add {x y : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y) : 2 * Real.sqrt (x * y) ≤ x + y`
- `theorem self_dual_fixed_point`: `theorem self_dual_fixed_point {C x : ℝ} (hC : 0 < C) (hx : 0 < x) : x = C / x ↔ x = Real.sqrt C`
- `theorem Reff_ge_sqrt_of_selfDual`: `theorem Reff_ge_sqrt_of_selfDual {α R : ℝ} (hα : 0 < α) (hR : 0 < R) : Real.sqrt α ≤ max R (α / R)`
- `theorem sqrt_le_max_of_le_mul_nat`: `theorem sqrt_le_max_of_le_mul_nat {a b N : ℕ} (h : N ≤ a * b) : Real.sqrt (N : ℝ) ≤ max (a : ℝ) (b : ℝ)`
- `theorem eoq_lower_bound`: `theorem eoq_lower_bound {D K h Q : ℝ} (hD : 0 < D) (hK : 0 < K) (hh : 0 < h) (hQ : 0 < Q) : 2 * Real.sqrt (D * K * h / 2) ≤ D * K / Q + h * Q / 2`
- `theorem bogoliubov_dual_form`: `theorem bogoliubov_dual_form {c ks k : ℝ} (hks : 0 < ks) (hk : 0 < k) : c ^ 2 * k ^ 2 + c ^ 2 * k ^ 4 / ks ^ 2 = c ^ 2 * k ^ 3 / ks * (k / ks + ks / k)`
- `theorem bogoliubov_selfdual_bound`: `theorem bogoliubov_selfdual_bound {c ks k : ℝ} (hks : 0 < ks) (hk : 0 < k) : 2 * c ^ 2 * k ^ 3 / ks ≤ c ^ 2 * k ^ 2 + c ^ 2 * k ^ 4 / ks ^ 2`
- `theorem sinh_selfDual_coupling`: `theorem sinh_selfDual_coupling {K : ℝ} (hK : 0 < K) (hfix : Real.sinh (2 * K) * Real.sinh (2 * K) = 1) : K = Real.log (1 + Real.sqrt 2) / 2`

## EinsteinRelation

```
EinsteinRelation.lean -- companion of docs/designs/PGPE_EINSTEIN_PREREG.md.

  The stochastic point-vortex model adds to the dissipative dipole law `d' = −2α d/|d|²` an isotropic noise of
  diffusion constant `D` on the separation vector (`D = 2η`, η the diffusion constant of one vortex). Its
  Fokker–Planck probability current for a density `p` is `J = b p − D ∇p`, `b = −2α d/|d|²`.

  * `zero_flux_iff`: the Kosterlitz–Thouless pair distribution `p = |d|^{−K}` carries zero current at every
    separation if and only if `D K = 2α`. So the three quantities measured by the programme -- the friction α
    (shrinking of a pair), the diffusion D (random walk of the separation) and the stiffness K (current
    correlators, or the pair-size exponent) -- are tied by one identity, and the pre-registered ratio
    `2α/(D K)` equals 1 exactly when the vortex gas can be in detailed-balance equilibrium at stiffness K.
  * `einstein_vortex`: with `K = 2π ρ/T` and `D = 2η` this is `η = α T/(2π ρ)` (hbar = m = k_B = 1), the
    relation proposed for test by Mehdi, Hope, Szigeti and Bradley (2022).
  * `flux_gibbs`: the same statement for any one-dimensional potential, `μ E' ρ + D ρ' = (μ − D/T) E' ρ` for
    `ρ = e^{−E/T}`.

  Textbook statistical mechanics (Einstein 1905); the content is that the test statistic of the
  pre-registration is an identity of the model, with the equilibrium law it presupposes made explicit.
```

- `def p`: `noncomputable def p (K x y : ℝ) : ℝ`
- `theorem hasDerivAt_p_x`: `theorem hasDerivAt_p_x (K x y : ℝ) (h : x ^ 2 + y ^ 2 ≠ 0) : HasDerivAt (fun x => p K x y) (-K * x / (x ^ 2 + y ^ 2) * p K x y) x`
- `theorem hasDerivAt_p_y`: `theorem hasDerivAt_p_y (K x y : ℝ) (h : x ^ 2 + y ^ 2 ≠ 0) : HasDerivAt (fun y => p K x y) (-K * y / (x ^ 2 + y ^ 2) * p K x y) y`
- `def Jx`: `noncomputable def Jx (α D K x y : ℝ) : ℝ`
- `def Jy`: `noncomputable def Jy (α D K x y : ℝ) : ℝ`
- `theorem Jx_eq`: `theorem Jx_eq (α D K x y : ℝ) : Jx α D K x y = (D * K - 2 * α) * (x / (x ^ 2 + y ^ 2) * p K x y)`
- `theorem Jy_eq`: `theorem Jy_eq (α D K x y : ℝ) : Jy α D K x y = (D * K - 2 * α) * (y / (x ^ 2 + y ^ 2) * p K x y)`
- `theorem zero_flux_iff`: `theorem zero_flux_iff (α D K : ℝ) : (∀ x y : ℝ, x ^ 2 + y ^ 2 ≠ 0 → Jx α D K x y = 0 ∧ Jy α D K x y = 0) ↔ D * K = 2 * α`
- `theorem einstein_vortex`: `theorem einstein_vortex (α η ρ T : ℝ) (hρ : 0 < ρ) (hT : 0 < T) : (∀ x y : ℝ, x ^ 2 + y ^ 2 ≠ 0 → Jx α (2 * η) (2 * π * ρ / T) x y = 0 ∧ Jy α (2 * η) (2 * π * ρ / T) x y = 0) ↔ η = α * T / (2 * π * ρ)`
- `theorem flux_gibbs`: `theorem flux_gibbs (E : ℝ → ℝ) (E' μ D T x : ℝ) (hT : T ≠ 0) (hE : HasDerivAt E E' x) : ∃ ρ' : ℝ, HasDerivAt (fun x => exp (-E x / T)) ρ' x ∧ μ * E' * exp (-E x / T) + D * ρ' = (μ - D / T) * E' * exp (-E x / T)`

## Fricke

```
Fricke.lean -- the group-theoretic core of the "Fricke / K3" gate of `paper/wasserstein_slack.tex` §6.3,
  and NOTHING more.

  Background (Dolgachev, alg-geom/9502005, Thm 7.1): the mirror moduli space of degree-2n polarized K3
  surfaces is `H/Γ₀(n)⁺`, where `Γ₀(n)⁺` is `Γ₀(n)` extended by the Fricke involution
  `F = (0, -1/√n; √n, 0)`, `t ↦ -1/(n t)`. An external review placed this project's dual-length
  involution `k ↦ ks²/k` (`DualLength.lean`) with that involution. The gate's verdict, argued in the
  paper: it is the SAME involution (restrict `F` to the imaginary axis) WITHOUT the group `Γ₀(n)` -- a
  shadow, not an instance. This file proves the group-theoretic facts that verdict rests on, as
  group theory, with no physics attached:

  * `W_mul_W`        : the integer Fricke matrix `W = (0, -1; n, 0)` squares to the scalar `-n`, so it
                       acts projectively as an involution;
  * `fricke_normalizes` : for every `A ∈ Γ₀(n)` (Mathlib's `Gamma0 n ≤ SL(2,ℤ)`) there is `B ∈ Γ₀(n)`
                       with `W * A = B * W` -- `W` normalizes `Γ₀(n)`, which is what makes `Γ₀(n)⁺`
                       a group in which `Γ₀(n)` has index 2 (the explicit `B` is `conj`);
  * `conj_conj`      : the induced map on `Γ₀(n)` is itself an involution;
  * `fricke_on_axis` : the Möbius action of `W` sends `i·y` to `i·(1/(n y))`;
  * `axis_eq_dual`, `ell_axis_invariant` : with `n = 1/ks²` the axis map is exactly `DualLength`'s
                       `k ↦ ks²/k`, and the dual length `ell ks` is invariant under it;
  * `axis_fixed_iff` : its unique positive fixed point is `1/√n` (`= ks`).

  NOT proved, NOT claimed: anything about K3 surfaces, lattice polarisations, period maps or mirror
  symmetry (Dolgachev's theorem is far beyond the pinned Mathlib); anything about helium. That the
  wavenumber line of a Bose gas carries no `Γ₀(n)` action is the paper's point, and it is not a
  theorem -- it is the absence of a structure.
```

- `def W`: `def W (n : ℤ) : Matrix (Fin 2) (Fin 2) ℤ`
- `theorem W_mul_W`: `theorem W_mul_W (n : ℤ) : W n * W n = (-n) • (1 : Matrix (Fin 2) (Fin 2) ℤ)`
- `def conj`: `def conj (n : ℤ) (g : Matrix (Fin 2) (Fin 2) ℤ) (c' : ℤ) : Matrix (Fin 2) (Fin 2) ℤ`
- `theorem W_mul_eq`: `theorem W_mul_eq (n : ℤ) (g : Matrix (Fin 2) (Fin 2) ℤ) (c' : ℤ) (hc : g 1 0 = n * c') : W n * g = conj n g c' * W n`
- `theorem det_conj`: `theorem det_conj (n : ℤ) (g : Matrix (Fin 2) (Fin 2) ℤ) (c' : ℤ) (hc : g 1 0 = n * c') : (conj n g c').det = g.det`
- `theorem conj_apply_one_zero`: `theorem conj_apply_one_zero (n : ℤ) (g : Matrix (Fin 2) (Fin 2) ℤ) (c' : ℤ) : conj n g c' 1 0 = n * (-(g 0 1))`
- `theorem conj_conj`: `theorem conj_conj (n : ℤ) (g : Matrix (Fin 2) (Fin 2) ℤ) (c' : ℤ) (hc : g 1 0 = n * c') : conj n (conj n g c') (-(g 0 1)) = g`
- `theorem mem_Gamma0_iff_dvd`: `theorem mem_Gamma0_iff_dvd (n : ℕ) [NeZero n] (A : SL(2, ℤ)) : A ∈ Gamma0 n ↔ (n : ℤ) ∣ A 1 0`
- `theorem fricke_normalizes`: `theorem fricke_normalizes (n : ℕ) [NeZero n] (A : SL(2, ℤ)) (hA : A ∈ Gamma0 n) : ∃ B : SL(2, ℤ), B ∈ Gamma0 n ∧ W n * (A : Matrix (Fin 2) (Fin 2) ℤ) = (B : Matrix (Fin 2) (Fin 2) ℤ) * W n`
- `theorem fricke_on_axis`: `theorem fricke_on_axis (n y : ℝ) (hn : n ≠ 0) (hy : y ≠ 0) : ((0 : ℂ) * (Complex.I * y) + (-1)) / ((n : ℂ) * (Complex.I * y) + 0) = Complex.I * (1 / (n * y))`
- `def axis`: `noncomputable def axis (n y : ℝ) : ℝ`
- `theorem axis_involutive`: `theorem axis_involutive {n y : ℝ} (hn : n ≠ 0) (hy : y ≠ 0) : axis n (axis n y) = y`
- `theorem axis_eq_dual`: `theorem axis_eq_dual {ks : ℝ} (hks : ks ≠ 0) (k : ℝ) : axis (1 / ks ^ 2) k = ks ^ 2 / k`
- `theorem ell_axis_invariant`: `theorem ell_axis_invariant {ks k : ℝ} (hk : k ≠ 0) (hks : ks ≠ 0) : QuantumFluids.DualLength.ell ks (axis (1 / ks ^ 2) k) = QuantumFluids.DualLength.ell ks k`
- `theorem axis_fixed_iff`: `theorem axis_fixed_iff {n y : ℝ} (hn : 0 < n) (hy : 0 < y) : axis n y = y ↔ y = 1 / Real.sqrt n`

## FrictionKinetic

```

```

- `def alpha`: `noncomputable def alpha (K : Finset ι) (w f : ι → ℝ) (ρs κ : ℝ) : ℝ`
- `def rhoN`: `noncomputable def rhoN (K : Finset ι) (w : ι → ℝ) : ℝ`
- `theorem coeff_eq_weighted_mean`: `theorem coeff_eq_weighted_mean (K : Finset ι) (w f : ι → ℝ) (ρ ρs κ : ℝ) (hρn : rhoN K w ≠ 0) (hρ : ρ ≠ 0) : alpha K w f ρs κ / (rhoN K w / ρ) = ρ / (ρs * κ) * ((∑ k ∈ K, w k * f k) / ∑ k ∈ K, w k)`
- `theorem weighted_mean_mem_Icc`: `theorem weighted_mean_mem_Icc (K : Finset ι) (w f : ι → ℝ) (hw : ∀ k ∈ K, 0 ≤ w k) (hpos : 0 < ∑ k ∈ K, w k) (m M : ℝ) (hm : ∀ k ∈ K, m ≤ f k) (hM : ∀ k ∈ K, f k ≤ M) : (∑ k ∈ K, w k * f k) / (∑ k ∈ K, w k) ∈ Set.Icc m M`
- `theorem rayleigh_jeans_mean`: `theorem rayleigh_jeans_mean (K : Finset ι) (f : ι → ℝ) (T c : ℝ) (hT : 0 < T) (hc : 0 < c) : (∑ k ∈ K, (T / (2 * c ^ 2)) * f k) / (∑ k ∈ K, (T / (2 * c ^ 2))) = (∑ k ∈ K, f k) / K.card`

## GPGalerkin

```
D3 (docs/OPENAI_NSE_LEVERAGE_FOR_QUANTUM_FLUIDS.md): structure of the Fourier-Galerkin
Gross-Pitaevskii nonlinearity that is INDEPENDENT of the truncation set.

Setting. `G` is an additive commutative group (the lattice `Z^3` is the case of interest), `Λ` a
finite set of retained modes (the truncation; nothing below depends on which set), and
`ψ : G → ℂ` the mode amplitudes. The projected cubic nonlinearity is
  `N ψ k = Σ_{k1 + k3 = k + k2, all in Λ} ψ(k1) conj(ψ(k2)) ψ(k3)`.

WHAT IS PROVED, for every finite `Λ`:
 1. `pairing_eq_sum_normSq`: `Q ψ := Σ_{k∈Λ} conj(ψ k) · N ψ k = Σ_q |A_q|²` with
    `A_q = Σ_{a-b=q} ψ(a) conj(ψ(b))` (the Fourier transform of `|ψ|²`).
 2. `pairing_nonneg`, `pairing_im_zero`: `Q` is real and `Q ≥ 0`. This is the defocusing sign:
    the interaction energy is coercive, with no `1/α'`-type constant and no dependence on `Λ`.
 3. `mass_rate_zero`: for real dispersion `ω` and real coupling `g`, with `G_k = ω_k ψ_k + g N_k`,
    `Σ_k Im(conj(ψ_k) G_k) = 0`. This is the algebraic core of `d/dt Σ|ψ_k|² = 0` for
    `i ∂t ψ_k = G_k` (since `d/dt |ψ_k|² = 2 Im(conj(ψ_k) G_k)`).
 4. `kinetic_le_energy`: `Σ ω_k |ψ_k|² ≤ E` whenever `E = Σ ω_k|ψ_k|² + (g/2) Q`, `g ≥ 0`.

WHAT IS NOT PROVED (be explicit, per the audit discipline):
 - Conservation of `E` along the flow (needs `∂Q/∂conj(ψ_k) = N_k`, the Hamiltonian gradient
   identity). Item 4 is therefore an inequality between two functions of `ψ`; it bounds the kinetic
   part by the energy at any instant, and becomes a uniform-in-`Λ` a-priori bound only once
   conservation of `E` is added.
 - Anything about time evolution existence, `H^s` for `s > 1`, or `u = ∇S` (see MadelungSplit).
 - The comparison with real Katz-Pavlovic / Navier-Stokes is by contrast in prose only; nothing
   here is a statement about the Navier-Stokes enstrophy production factor.
```

- `def nl`: `noncomputable def nl (Λ : Finset G) (ψ : G → ℂ) (k : G) : ℂ`
- `def pairing`: `noncomputable def pairing (Λ : Finset G) (ψ : G → ℂ) : ℂ`
- `def ff`: `noncomputable def ff (ψ : G → ℂ) (p : G × G) : ℂ`
- `def dens`: `noncomputable def dens (Λ : Finset G) (ψ : G → ℂ) (q : G) : ℂ`
- `def diffs`: `noncomputable def diffs (Λ : Finset G) : Finset G`
- `theorem pairing_eq_prod`: `theorem pairing_eq_prod (Λ : Finset G) (ψ : G → ℂ) : pairing Λ ψ = ∑ p ∈ Λ ×ˢ Λ, ∑ r ∈ Λ ×ˢ Λ, if p.1 - p.2 = r.1 - r.2 then ff ψ p * (starRingEnd ℂ) (ff ψ r) else 0`
- `theorem dens_mul_conj`: `theorem dens_mul_conj (Λ : Finset G) (ψ : G → ℂ) (q : G) : dens Λ ψ q * (starRingEnd ℂ) (dens Λ ψ q) = ∑ p ∈ Λ ×ˢ Λ, ∑ r ∈ Λ ×ˢ Λ, if p.1 - p.2 = q ∧ r.1 - r.2 = q then ff ψ p * (starRingEnd ℂ) (ff ψ r) else 0`
- `theorem pairing_eq_sum`: `theorem pairing_eq_sum (Λ : Finset G) (ψ : G → ℂ) : pairing Λ ψ = ∑ q ∈ diffs Λ, dens Λ ψ q * (starRingEnd ℂ) (dens Λ ψ q)`
- `def pairingRe`: `noncomputable def pairingRe (Λ : Finset G) (ψ : G → ℂ) : ℝ`
- `theorem pairing_eq_ofReal`: `theorem pairing_eq_ofReal (Λ : Finset G) (ψ : G → ℂ) : pairing Λ ψ = (pairingRe Λ ψ : ℂ)`
- `theorem pairing_nonneg`: `theorem pairing_nonneg (Λ : Finset G) (ψ : G → ℂ) : 0 ≤ pairingRe Λ ψ`
- `theorem pairing_im_zero`: `theorem pairing_im_zero (Λ : Finset G) (ψ : G → ℂ) : (pairing Λ ψ).im = 0`
- `theorem mass_rate_zero`: `theorem mass_rate_zero (Λ : Finset G) (ψ : G → ℂ) (ω : G → ℝ) (g : ℝ) : ∑ k ∈ Λ, ((starRingEnd ℂ) (ψ k) * ((ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k)).im = 0`
- `theorem kinetic_le_energy`: `theorem kinetic_le_energy (Λ : Finset G) (ψ : G → ℂ) (ω : G → ℝ) (g E : ℝ) (hg : 0 ≤ g) (hE : E = ∑ k ∈ Λ, ω k * Complex.normSq (ψ k) + g / 2 * pairingRe Λ ψ) : ∑ k ∈ Λ, ω k * Complex.normSq (ψ k) ≤ E`
- `theorem nl_eq_dens`: `theorem nl_eq_dens (Λ : Finset G) (ψ : G → ℂ) (k : G) : nl Λ ψ k = ∑ b ∈ Λ, ψ b * dens Λ ψ (k - b)`
- `theorem dens_neg`: `theorem dens_neg (Λ : Finset G) (ψ : G → ℂ) (q : G) : dens Λ ψ (-q) = (starRingEnd ℂ) (dens Λ ψ q)`
- `def densVar`: `noncomputable def densVar (Λ : Finset G) (ψ δ : G → ℂ) (q : G) : ℂ`
- `theorem sum_densVar`: `theorem sum_densVar (Λ : Finset G) (ψ δ : G → ℂ) : ∑ q ∈ diffs Λ, (starRingEnd ℂ) (dens Λ ψ q) * densVar Λ ψ δ q = ∑ p ∈ Λ ×ˢ Λ, (starRingEnd ℂ) (dens Λ ψ (p.1 - p.2)) * (δ p.1 * (starRingEnd ℂ) (ψ p.2) + ψ p.1 * (starRingEnd ℂ) (δ p.2))`
- `theorem grad_identity`: `theorem grad_identity (Λ : Finset G) (ψ δ : G → ℂ) : ∑ q ∈ diffs Λ, 2 * ((starRingEnd ℂ) (dens Λ ψ q) * densVar Λ ψ δ q).re = 4 * (∑ k ∈ Λ, (starRingEnd ℂ) (δ k) * nl Λ ψ k).re`
- `theorem energy_rate_zero`: `theorem energy_rate_zero (Λ : Finset G) (ψ : G → ℂ) (ω : G → ℝ) (g : ℝ) : ∑ k ∈ Λ, 2 * ω k * ((starRingEnd ℂ) (ψ k) * (-Complex.I * ((ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k))).re + g / 2 * ∑ q ∈ diffs Λ, 2 * ((starRingEnd ℂ) (dens Λ ψ q) * densVar Λ ψ (fun k => -Complex.I * ((ω k : ℂ) * ψ k + (g : ℂ) *`

## HeliumKinematics

```
Kinematic and consistency identities behind the analysis of neutron-scattering data on superfluid
helium-4, formalised from statements made in

  [G21] Godfrin, Beauvois, Sultan, Krotscheck, Dawidowski, Fak, Ollivier, Phys. Rev. B 103, 104516
        (2021), arXiv:2012.09067   (equation numbers below are those of the arXiv version);
  [GK22] Godfrin & Krotscheck, "The Dynamics of Quantum Fluids", arXiv:2206.06039.

These are the relations an experimental analysis leans on without proving: which decays are
kinematically open, what a recalibration can and cannot change, and the geometry and thermodynamic
identities that turn time-of-flight channels into a dispersion curve. None is new physics. The
point of checking them is that several are stated in prose only, two published formulas in the
preprint are misprinted (see docs/FOR_GODFRIN.md), and the authors themselves note that earlier
published series for the specific heat "contain errors".

NOT formalised here: the specific-heat series coefficients (they need the Bose integrals
`∫ x^n/(e^x-1) = Γ(n+1) ζ(n+1)`), the Landau roton asymptotics, and anything about S(Q,ω).
```

- `def phononDisp`: `def phononDisp (c a k : ℝ) : ℝ`
- `theorem three_phonon_excess`: `theorem three_phonon_excess (c a k₁ k₂ : ℝ) : phononDisp c a (k₁ + k₂) - phononDisp c a k₁ - phononDisp c a k₂ = 3 * c * a * k₁ * k₂ * (k₁ + k₂)`
- `theorem three_phonon_open_iff`: `theorem three_phonon_open_iff {c a k₁ k₂ : ℝ} (hc : 0 < c) (h₁ : 0 < k₁) (h₂ : 0 < k₂) : phononDisp c a k₁ + phononDisp c a k₂ ≤ phononDisp c a (k₁ + k₂) ↔ 0 ≤ a`
- `def seriesDisp`: `def seriesDisp (c α₂ α₃ α₄ k : ℝ) : ℝ`
- `theorem symmetric_split_excess`: `theorem symmetric_split_excess (c α₂ α₃ α₄ k : ℝ) : seriesDisp c α₂ α₃ α₄ k - 2 * seriesDisp c α₂ α₃ α₄ (k / 2) = c * k ^ 3 * (3 / 4 * α₂ + 7 / 8 * α₃ * k + 15 / 16 * α₄ * k ^ 2)`
- `theorem phase_velocity_excess`: `theorem phase_velocity_excess (c α₂ α₃ α₄ k : ℝ) (hk : k ≠ 0) : seriesDisp c α₂ α₃ α₄ k / k - c = c * k ^ 2 * (α₂ + α₃ * k + α₄ * k ^ 2)`
- `theorem group_velocity_excess`: `theorem group_velocity_excess (c α₂ α₃ α₄ k : ℝ) : HasDerivAt (seriesDisp c α₂ α₃ α₄) (c + c * k ^ 2 * (3 * α₂ + 4 * α₃ * k + 5 * α₄ * k ^ 2)) k`
- `theorem two_roton_momentum_le`: `theorem two_roton_momentum_le {k₁ k₂ : V} {kR : ℝ} (h₁ : ‖k₁‖ = kR) (h₂ : ‖k₂‖ = kR) : ‖k₁ + k₂‖ ≤ 2 * kR`
- `theorem two_roton_parallel`: `theorem two_roton_parallel (k₁ : V) : ‖k₁ + k₁‖ = 2 * ‖k₁‖`
- `theorem two_roton_antiparallel`: `theorem two_roton_antiparallel (k₁ : V) : ‖k₁ + (-k₁)‖ = 0`
- `def tofEnergy`: `def tofEnergy (Ei r : ℝ) : ℝ`
- `theorem tofEnergy_rescale`: `theorem tofEnergy_rescale (lam Ei r : ℝ) : tofEnergy (lam * Ei) r = lam * tofEnergy Ei r`
- `theorem plateau_excess_calibration_invariant`: `theorem plateau_excess_calibration_invariant {lam : ℝ} (hlam : 0 < lam) (Ei r rR : ℝ) : 2 * tofEnergy (lam * Ei) rR < tofEnergy (lam * Ei) r ↔ 2 * tofEnergy Ei rR < tofEnergy Ei r`
- `theorem tof_eq12_eq_eq13`: `theorem tof_eq12_eq_eq13 {m v tel tin ts : ℝ} (h₁ : tel - ts ≠ 0) (h₂ : tin - ts ≠ 0) : (1 / 2) * m * (v * (tel - ts)) ^ 2 * (1 / (tel - ts) ^ 2 - 1 / (tin - ts) ^ 2) = tofEnergy ((1 / 2) * m * v ^ 2) ((tel - ts) / (tin - ts))`
- `theorem landau_velocity_parabolic_zero`: `theorem landau_velocity_parabolic_zero {a : ℝ} (ha : 0 < a) {v : ℝ} (hv : 0 < v) : ∃ k : ℝ, 0 < k ∧ a * k ^ 2 / k < v`
- `theorem landau_velocity_ge_of_above_sound_line`: `theorem landau_velocity_ge_of_above_sound_line {ε : ℝ → ℝ} {c k : ℝ} (hk : 0 < k) (h : c * k ≤ ε k) : c ≤ ε k / k`
- `def abrahamP`: `def abrahamP (A₁ A₂ A₃ ρ₀ ρ : ℝ) : ℝ`
- `theorem abraham_sound_speed_sq`: `theorem abraham_sound_speed_sq (A₁ A₂ A₃ ρ₀ ρ : ℝ) : HasDerivAt (abrahamP A₁ A₂ A₃ ρ₀) (A₁ + 2 * A₂ * (ρ - ρ₀) + 3 * A₃ * (ρ - ρ₀) ^ 2) ρ`
- `theorem debye_mode_count`: `theorem debye_mode_count (kD : ℝ) : (1 / (2 * Real.pi ^ 2)) * ∫ k in (0 : ℝ)..kD, k ^ 2 = kD ^ 3 / (6 * Real.pi ^ 2)`

## KTFlow

```
KTFlow.lean -- the Kosterlitz renormalisation-group flow: an exact conserved quantity, and the trapping of the
  superfluid side at the universal stiffness.

  Kosterlitz (J. Phys. C 7, 1046 (1974)) flow for the stiffness `K` and vortex fugacity `y`, written for
  `u = 1/K` (KT units, universal value `K = 2/π`):
      du/dl = 4π³ y²,        dy/dl = (2 − π/u) y.
  * `kt_invariant`: `H(u, y) = 2u − π log u − 2π³ y²` is constant along EVERY solution with `u > 0` -- exactly,
    not only near the fixed point (the textbook hyperbolas are its quadratic approximation at `(π/2, 0)`).
  * `kt_trapped`: if the flow starts on the superfluid side (`u(0) < π/2`, i.e. `K(0) > 2/π`) with
    `H > f(π/2)`, `f(u) = 2u − π log u`, then `u(l) < π/2` for all `l ≥ 0`: the renormalised stiffness never
    falls below the universal value `2/π` -- the inequality behind the Nelson–Kosterlitz jump.
  * `kt_fugacity_bounded`: on that side the fugacity never grows, `y(l)² ≤ y(0)²` for `l ≥ 0`, and the stiffness
    only decreases (`u` is monotone).
  * `kt_units`: `K > 2/π` in KT units is `2πK > 4` in this programme's convention `K = n_s λ_T² = 2π n_s/T`
    (`CompactBoson.lean`, the ladder's `n_s λ² = 4` criterion).
  Novelty scouted 2026-10-05: no Lean (Mathlib, Physlib, LeSca) formalisation of the KT flow was found. The
  physics is textbook; what is formal here is that the conserved quantity is exact and that the trapping
  follows from it plus continuity, with no linearisation.
```

- `def f`: `noncomputable def f (u : ℝ) : ℝ`
- `def H`: `noncomputable def H (u y : ℝ) : ℝ`
- `lemma f_antitone`: `lemma f_antitone {a b : ℝ} (ha : 0 < a) (hab : a ≤ b) (hb : b ≤ π / 2) : f b ≤ f a`
- `lemma hasDerivAt_H`: `lemma hasDerivAt_H (l : ℝ) : HasDerivAt (fun l => H (u l) (y l)) 0 l`
- `theorem kt_invariant`: `theorem kt_invariant (l : ℝ) : H (u l) (y l) = H (u 0) (y 0)`
- `lemma f_ge_H`: `lemma f_ge_H (l : ℝ) : H (u 0) (y 0) ≤ f (u l)`
- `theorem kt_trapped`: `theorem kt_trapped (h0 : u 0 < π / 2) (hH : f (π / 2) < H (u 0) (y 0)) : ∀ l, 0 ≤ l → u l < π / 2`
- `theorem u_monotone`: `theorem u_monotone : Monotone u`
- `theorem kt_fugacity_bounded`: `theorem kt_fugacity_bounded (h0 : u 0 < π / 2) (hH : f (π / 2) < H (u 0) (y 0)) (l : ℝ) (hl : 0 ≤ l) : y l ^ 2 ≤ y 0 ^ 2`
- `theorem kt_units`: `theorem kt_units (K : ℝ) : 2 / π < K ↔ 4 < 2 * π * K`

## LevelRankDuality

```
LevelRankDuality.lean -- a seventh cross-domain case: level-rank duality of Chern-Simons/WZW theories,
  U(N)_K <-> U(K)_N (Naculich-Schnitzer 2007, DOI 10.1088/1126-6708/2007/06/023; Hsin-Seiberg 2016,
  DOI 10.1007/JHEP09(2016)095), stated at the level of its combinatorial skeleton.

  Background. The integrable highest-weight primaries of U(N) at level K are labelled by Young diagrams
  fitting in an N-row, K-column box; level-rank duality relabels U(N)_K's primaries by U(K)_N's via
  transposition of that box (an N x K box <-> a K x N box). This is the SECTOR of a further duality in
  the fractional-quantum-Hall/Chern-Simons setting already touched by `QHFricke.lean` (Lutken-Ross's
  Gamma_0(2) on the Hall conductivity plane) -- a DIFFERENT duality, acting on a different sector (the
  finite set of anyon/primary labels, not the Chern integer), in the "organisation, not cause" slot: it
  is a proved finite relabelling of a label set that decides no physics and causes no transition. Son's
  2015 particle-vortex duality at nu = 1/2 (Phys. Rev. X 5, 031027) and Seiberg-Senthil-Wang-Witten's
  2016 duality web (Annals Phys. 374, 395) are the field-theoretic (non-topological, non-rigorous) layer
  ABOVE this; level-rank duality is their rigorously-established topological limit once matter is gapped
  and integrated out.

  What this module proves: the finite combinatorial skeleton only -- that a Young diagram fits in an
  a-row, b-column box iff its transpose fits in a b-row, a-column box, packaged as an `Equiv` between
  the two (finite) label sets, using Mathlib's own `YoungDiagram.transpose`/`transposeOrderIso`
  (no re-derivation). What it does NOT prove -- and no elementary Lean tactic could, without affine-Lie-
  algebra representation theory or modular-tensor-category machinery Mathlib does not have -- is the
  actual physical content of level-rank duality: that the modular S,T matrices (hence the Verlinde
  fusion coefficients, `RCFTDuality.lean`'s object) match across the two theories. This module states
  only the LABEL bijection; the S,T-matrix identification is prose, exactly as `RCFTDuality.lean`'s
  su(2) level-1 identification and `SectorDuality.lean`'s Z_N-Fourier-is-Kramers-Wannier identification
  are prose, not something the type checker verifies.

  * `inBox`                : a Young diagram fits in `a` rows and `b` columns;
  * `inBox_transpose_iff`  : `mu` fits in an `a x b` box iff `mu.transpose` fits in a `b x a` box;
  * `levelRankRelabeling`  : the induced bijection between the two (sub)sets of Young diagrams -- the
              
```

- `def inBox`: `def inBox (a b : ℕ) (μ : YoungDiagram) : Prop`
- `theorem inBox_transpose_iff`: `theorem inBox_transpose_iff (a b : ℕ) (μ : YoungDiagram) : inBox a b μ ↔ inBox b a μ.transpose`
- `def levelRankRelabeling`: `def levelRankRelabeling (a b : ℕ) : { μ : YoungDiagram // inBox a b μ } ≃ { μ : YoungDiagram // inBox b a μ }`

## MadelungNSE

```
Bridge: the Madelung (quantum-fluid) velocity field expressed in OpenAI's Navier-Stokes vocabulary.

Imports `NavierStokes.ProblemStatement` from openai/NavierStokesAndEuler @ 8937a8f (Apache-2.0),
the same commit whose four headline theorems MechanicaFluidorum audited to footprint
`{propext, Classical.choice, Quot.sound}`. Both trees are on Lean 4.34.0-rc2 and Mathlib
85e3a25 (tag v4.34.0-rc2), which is what makes the import possible at all.

WHY THIS FILE. `MadelungSplit.lean` states the quantum-pressure/hydrodynamic split with
hand-rolled directional derivatives. The OpenAI tree already fixes Frechet-derivative vocabulary on
`EuclideanSpace R (Fin 3)` -- `spatialDerivative`, `spatialDivergence`, `pressureGradient`,
`spatialLaplacian` -- in which THEIR incompressible Navier-Stokes residual is written. Restating our
objects in that vocabulary means the quantum-fluid and Navier-Stokes sides are expressed in one
formalism and can be compared as mathematics rather than by analogy.

WHAT IS PROVED. `divergence_pressureGradient`: the divergence of their `pressureGradient` is the
scalar Laplacian. They never needed this (their pressure enters only as a gradient), so it is
genuinely added, and it is the identity that makes the Madelung continuity equation expressible in
their formalism. `divergence_madelungVelocity` then gives `div u = (hbar/m) * Laplacian S` for the
Madelung velocity `u = (hbar/m) grad S`.

WHAT IS NOT PROVED. No dynamics, no Gross-Pitaevskii equation, no claim about Navier-Stokes
regularity, and nothing about their blow-up theorems. Second differentiability of the phase is a
genuine HYPOTHESIS, and it is exactly what fails on a vortex line, where `S` is undefined.
```

- `def scalarLaplacian`: `noncomputable def scalarLaplacian (p : PressureField) (t : ℝ) (x : Space) : ℝ`
- `def TwiceSpatial`: `def TwiceSpatial (p : PressureField) (t : ℝ) (x : Space) : Prop`
- `theorem divergence_pressureGradient`: `theorem divergence_pressureGradient (p : PressureField) (t : ℝ) (x : Space) (h : TwiceSpatial p t x) : spatialDivergence (fun q : SpaceTime => pressureGradient p q.1 q.2) t x = scalarLaplacian p t x`
- `def madelungVelocity`: `noncomputable def madelungVelocity (hbar m : ℝ) (S : PressureField) : VelocityField`
- `theorem divergence_madelungVelocity`: `theorem divergence_madelungVelocity (hbar m : ℝ) (S : PressureField) (t : ℝ) (x : Space) (h : TwiceSpatial S t x) : spatialDivergence (madelungVelocity hbar m S) t x = (hbar / m) * scalarLaplacian S t x`

## MadelungSplit

```
D4 (docs/OPENAI_NSE_LEVERAGE_FOR_QUANTUM_FLUIDS.md): the Madelung energy split.

WHAT IS PROVED. For a wavefunction written in amplitude-phase form
`psi = a * exp (i S)` with `a`, `S : E -> R` differentiable at `x`, and for every
direction `v`, the directional derivative of `psi` is
`exp (i S) * (da v + i a dS v)` and its squared modulus is
`(da v)^2 + a^2 (dS v)^2`. Summed over an orthonormal frame this is the pointwise
identity `|grad psi|^2 = |grad a|^2 + a^2 |grad S|^2`, i.e. the Gross-Pitaevskii
kinetic energy density splits into a quantum-pressure part (`a = sqrt rho`) and a
hydrodynamic part `rho |u|^2` with `u = (hbar/m) grad S`.

WHAT IS NOT PROVED. Nothing about dynamics, about the Madelung equations, about
vortex lines (where `S` is undefined and `a = 0`), or about bounded energy
implying anything on `sup |u|`. This is the algebraic identity only (Tier A, small).
The hypothesis `DifferentiableAt` on `a` and `S` is a genuine assumption and is
exactly what fails at a vortex core.
```

- `def psi`: `noncomputable def psi {E : Type*} (a S : E → ℝ) (x : E) : ℂ`
- `theorem normSq_phase_mul`: `theorem normSq_phase_mul (θ p a r : ℝ) : ‖Complex.exp (Complex.I * (θ : ℂ)) * ((p : ℂ) + Complex.I * (a : ℂ) * (r : ℂ))‖ ^ 2 = p ^ 2 + a ^ 2 * r ^ 2`
- `theorem hasDerivAt_line`: `theorem hasDerivAt_line (x v : E) : HasDerivAt (fun t : ℝ => x + t • v) v 0`
- `theorem hasDerivAt_psi_line`: `theorem hasDerivAt_psi_line (a S : E → ℝ) (x v : E) (ha : DifferentiableAt ℝ a x) (hS : DifferentiableAt ℝ S x) : HasDerivAt (fun t : ℝ => psi a S (x + t • v)) (Complex.exp (Complex.I * (S x : ℂ)) * ((fderiv ℝ a x v : ℝ) + Complex.I * (a x : ℂ) * (fderiv ℝ S x v : ℝ))) 0`
- `theorem norm_sq_deriv_psi`: `theorem norm_sq_deriv_psi (a S : E → ℝ) (x v : E) (ha : DifferentiableAt ℝ a x) (hS : DifferentiableAt ℝ S x) : ‖deriv (fun t : ℝ => psi a S (x + t • v)) 0‖ ^ 2 = (fderiv ℝ a x v) ^ 2 + (a x) ^ 2 * (fderiv ℝ S x v) ^ 2`
- `theorem madelung_gradient_split`: `theorem madelung_gradient_split {n : ℕ} (a S : EuclideanSpace ℝ (Fin n) → ℝ) (x : EuclideanSpace ℝ (Fin n)) (ha : DifferentiableAt ℝ a x) (hS : DifferentiableAt ℝ S x) : ∑ i : Fin n, ‖deriv (fun t : ℝ => psi a S (x + t • EuclideanSpace.single i 1)) 0‖ ^ 2 = ∑ i : Fin n, (fderiv ℝ a x (EuclideanSpace`
- `theorem kinetic_density_split`: `theorem kinetic_density_split (ħ m a ga gS : ℝ) (hm : m ≠ 0) : ħ ^ 2 / (2 * m) * (ga ^ 2 + a ^ 2 * gS ^ 2) = ħ ^ 2 / (2 * m) * ga ^ 2 + m / 2 * a ^ 2 * (ħ / m * gS) ^ 2`

## MatchingScreening

```
MatchingScreening.lean -- the vortex-charge structure factor certifies a long vortex-antivortex matching.

  Context: `docs/designs/PGPE_ONSAGER_RESULTS.md`. The negative-stiffness states of round 3 differ from the
  healthy ones by an O(1) residual of the vortex charge density at the longest wavelengths of the box,
  `rho_q(k) = Σ_{+} e^{i k·r} - Σ_{-} e^{i k·r}`, and the transverse current those vortices drive,
  `|v_T(k)| = 2π |rho_q(k)| / |k|`, accounts for the measured one (Pearson 0.996, post hoc). The reading
  given there -- "about one vortex-antivortex pair separated by a distance comparable to L" -- is turned
  here into a theorem that holds for EVERY configuration, with no model of the vortex gas:

  * `norm_rho_le_matching`: for any pairing `σ` of the N positive to the N negative vortices,
      ‖rho_q(k)‖ ≤ ‖k‖ · Σ_i ‖p_i - m_{σ i}‖.
    Hence the cheapest pairing -- the optimal transport cost W₁ between the two sign populations -- is at
    least ‖rho_q(k)‖ / ‖k‖ (`matching_lower_bound`); and some pair is at least that long divided by N
    (`exists_long_pair`). With |rho_q(k₁)|² ≈ 1 at |k₁| = 2π/L, every pairing has total length ≥ L/(2π).
  * `norm_rho_le_matching_torus`: the same on the torus, with each separation replaced by any lattice-shifted
    representative (so: the minimum-image distance), for k in the reciprocal lattice (⟪k, t⟫ ∈ 2πℤ).
  * `pointVortex_transverse` / `pointVortex_norm_sq`: the Fourier-side velocity of point vortices,
    v̂ = 2π i rho (-k₂, k₁)/|k|², is transverse (k·v̂ = 0) with |v̂|² = (2π)²|rho|²/|k|² -- the formula
    behind the post-hoc vortex-only transverse current.

  Together with `WassersteinCertificate.lean` (a dual-feasible certificate is an UPPER bound on the optimal
  matching cost's optimality gap, and certifies a matching optimal) this brackets the matching cost from
  both sides. Elementary; no claim of new mathematics: the content is that the diagnostic is geometry.
```

- `lemma norm_exp_sub_exp_le`: `lemma norm_exp_sub_exp_le (a b : ℝ) : ‖exp (I * (a : ℂ)) - exp (I * (b : ℂ))‖ ≤ |a - b|`
- `def wave`: `noncomputable def wave (k r : E) : ℂ`
- `def rho`: `noncomputable def rho {N : ℕ} (k : E) (p m : Fin N → E) : ℂ`
- `lemma norm_wave_sub_le`: `lemma norm_wave_sub_le (k r s : E) : ‖wave k r - wave k s‖ ≤ ‖k‖ * ‖r - s‖`
- `theorem norm_rho_le_matching`: `theorem norm_rho_le_matching {N : ℕ} (k : E) (p m : Fin N → E) (σ : Fin N ≃ Fin N) : ‖rho k p m‖ ≤ ‖k‖ * ∑ i, ‖p i - m (σ i)‖`
- `theorem matching_lower_bound`: `theorem matching_lower_bound {N : ℕ} (k : E) (hk : k ≠ 0) (p m : Fin N → E) (σ : Fin N ≃ Fin N) : ‖rho k p m‖ / ‖k‖ ≤ ∑ i, ‖p i - m (σ i)‖`
- `theorem exists_long_pair`: `theorem exists_long_pair {N : ℕ} (hN : 0 < N) (k : E) (hk : k ≠ 0) (p m : Fin N → E) (σ : Fin N ≃ Fin N) : ∃ i, ‖rho k p m‖ / (N * ‖k‖) ≤ ‖p i - m (σ i)‖`
- `lemma wave_add_period`: `lemma wave_add_period (k r t : E) (n : ℤ) (ht : inner ℝ k t = 2 * Real.pi * n) : wave k (r + t) = wave k r`
- `theorem norm_rho_le_matching_torus`: `theorem norm_rho_le_matching_torus {N : ℕ} (k : E) (p m : Fin N → E) (σ : Fin N ≃ Fin N) (t : Fin N → E) (ht : ∀ i, ∃ n : ℤ, inner ℝ k (t i) = 2 * Real.pi * n) : ‖rho k p m‖ ≤ ‖k‖ * ∑ i, ‖p i - (m (σ i) + t i)‖`
- `def vhat`: `noncomputable def vhat (k₁ k₂ : ℝ) (r : ℂ) : ℂ × ℂ`
- `theorem pointVortex_transverse`: `theorem pointVortex_transverse (k₁ k₂ : ℝ) (r : ℂ) : (k₁ : ℂ) * (vhat k₁ k₂ r).1 + (k₂ : ℂ) * (vhat k₁ k₂ r).2 = 0`
- `theorem pointVortex_norm_sq`: `theorem pointVortex_norm_sq (k₁ k₂ : ℝ) (hk : k₁ ^ 2 + k₂ ^ 2 ≠ 0) (r : ℂ) : ‖(vhat k₁ k₂ r).1‖ ^ 2 + ‖(vhat k₁ k₂ r).2‖ ^ 2 = (2 * Real.pi) ^ 2 * ‖r‖ ^ 2 / (k₁ ^ 2 + k₂ ^ 2)`
- `lemma rho_one_pair`: `lemma rho_one_pair : rho (E`

## PairPolarisation

```
PairPolarisation.lean -- companion of docs/designs/PGPE_DIELECTRIC_PREREG.md (finite-k dielectric relation).

  For `N` vortex-antivortex pairs, `p i` the `+` and `m i` the `−` member, `d i = p i − m i`, the vortex charge
  density at wavevector `k` is `rho k = Σ_i (e^{i k·p_i} − e^{i k·m_i})`.

  * `norm_rho_le_pairs`: `‖rho k‖ ≤ ‖k‖ Σ ‖d_i‖` -- hence `≤ ‖k‖ N a` for pairs of size at most `a`.
  * `rho_polarisation`: when `|k·d_i| ≤ 1` for every pair,
        ‖rho k − i Σ_i (k·d_i) e^{i k·m_i}‖ ≤ Σ_i (k·d_i)² ≤ ‖k‖² Σ ‖d_i‖².
    The charge density of bound pairs is `i k·P(k)`, `P(k) = Σ d_i e^{i k·m_i}` the Fourier component of the
    polarisation density, up to an explicit second-order remainder. This is the dictionary between vortex
    positions and the dielectric response at finite wavevector that the pre-registration tests.
  * `response_ceiling`: the point-vortex transverse response `(2π)²‖rho‖²/‖k‖²` of bound pairs is at most
    `(2π)² (Σ‖d_i‖)²`, a bound that does not depend on `k`: a response above it at wavevector `k` certifies
    that the configuration is not a gas of pairs of the assumed sizes (the box-scale-charge signature of
    PGPE_ONSAGER_RESULTS.md, now with the bound-pair contribution made explicit).

  Self-contained (does not import MatchingScreening.lean, which proves the matching form of the first bound).
```

- `def wave`: `noncomputable def wave (k r : E) : ℂ`
- `def rho`: `noncomputable def rho {N : ℕ} (k : E) (p m : Fin N → E) : ℂ`
- `lemma norm_wave`: `lemma norm_wave (k r : E) : ‖wave k r‖ = 1`
- `lemma pair_factor`: `lemma pair_factor (k p m : E) : wave k p - wave k m = wave k m * (exp (I * ((inner ℝ k (p - m) : ℝ) : ℂ)) - 1)`
- `lemma norm_pair_le`: `lemma norm_pair_le (k p m : E) : ‖wave k p - wave k m‖ ≤ ‖k‖ * ‖p - m‖`
- `theorem norm_rho_le_pairs`: `theorem norm_rho_le_pairs {N : ℕ} (k : E) (p m : Fin N → E) : ‖rho k p m‖ ≤ ‖k‖ * ∑ i, ‖p i - m i‖`
- `theorem norm_rho_le_of_size`: `theorem norm_rho_le_of_size {N : ℕ} (k : E) (p m : Fin N → E) {a : ℝ} (ha : ∀ i, ‖p i - m i‖ ≤ a) : ‖rho k p m‖ ≤ ‖k‖ * (N * a)`
- `theorem rho_polarisation`: `theorem rho_polarisation {N : ℕ} (k : E) (p m : Fin N → E) (hk : ∀ i, |inner ℝ k (p i - m i)| ≤ 1) : ‖rho k p m - I * ∑ i, ((inner ℝ k (p i - m i) : ℝ) : ℂ) * wave k (m i)‖ ≤ ∑ i, (inner ℝ k (p i - m i)) ^ 2`
- `theorem remainder_le`: `theorem remainder_le {N : ℕ} (k : E) (p m : Fin N → E) : ∑ i, (inner ℝ k (p i - m i)) ^ 2 ≤ ‖k‖ ^ 2 * ∑ i, ‖p i - m i‖ ^ 2`
- `theorem response_ceiling`: `theorem response_ceiling {N : ℕ} (k : E) (hk : k ≠ 0) (p m : Fin N → E) : (2 * Real.pi) ^ 2 * ‖rho k p m‖ ^ 2 / ‖k‖ ^ 2 ≤ (2 * Real.pi) ^ 2 * (∑ i, ‖p i - m i‖) ^ 2`

## PhaseMixing

```
PhaseMixing.lean -- free transport forgets its initial density: the linear, field-free core of
  Landau damping.

  CONTEXT, so this is not mistaken for more than it is.  J. Bedrossian, *Formalization of Landau damping
  in the Vlasov-Poisson equations in Lean*, arXiv:2609.16801 (2026), formalizes the nonlinear
  Mouhot-Villani theorem.  What is below is a corollary of Mathlib's Riemann-Lebesgue lemma and is
  subsumed by that work.  It is here because the closed form `maxwellian_mode` is the known answer that
  this repository's Vlasov solver and plasma-echo test are validated against
  (src/quantumfluids/kinetic, pre-registration K3a), and a known answer should be a checked one.

  * `transport_solution`  -- f(t,x,v) = e^{ik(x - vt)} g(v) solves  ∂ₜf + v ∂ₓf = 0.
  * `phase_mixing`        -- its density mode  ∫ g(v) e^{-ikvt} dv → 0  as t → ∞, for k ≠ 0, with NO
                             regularity assumed on g (if g is not integrable the integral is 0 by
                             convention and the statement is vacuous; for integrable g it is the content).
  * `maxwellian_mode`     -- for the unit Maxwellian the mode is exactly e^{-k²t²/2}: Gaussian, not
                             exponential, decay -- free streaming is not Landau damping.
```

- `theorem transport_solution`: `theorem transport_solution (k v : ℝ) (gv : ℂ) (t x : ℝ) : HasDerivAt (fun t => cexp ((k * (x - v * t) : ℝ) * I) * gv) (-(v : ℂ) * ((k : ℂ) * I * (cexp ((k * (x - v * t) : ℝ) * I) * gv))) t ∧ HasDerivAt (fun x => cexp ((k * (x - v * t) : ℝ) * I) * gv) ((k : ℂ) * I * (cexp ((k * (x - v * t) : ℝ) * I) `
- `theorem phase_mixing`: `theorem phase_mixing (g : ℝ → ℂ) {k : ℝ} (hk : k ≠ 0) : Tendsto (fun t : ℝ => ∫ v : ℝ, cexp (-((k * v * t : ℝ) : ℂ) * I) * g v) atTop (𝓝 0)`
- `theorem maxwellian_mode`: `theorem maxwellian_mode (k t : ℝ) : ∫ v : ℝ, cexp (-((k * v * t : ℝ) : ℂ) * I) * ((rexp (-v ^ 2 / 2) / √(2 * π) : ℝ) : ℂ) = cexp (-((k * t) ^ 2 / 2 : ℝ))`

## PhononSeries

```
PhononSeries.lean -- the algebra behind the phonon specific-heat series of
  Godfrin, Beauvois, Sultan, Krotscheck, Dawidowski, Faak, Ollivier, PRB 103, 104516 (2021), Eq. (22).

  GENERATED by exploration/godfrin/gen_phonon_series_lean.py -- the `linear_combination` certificates are
  computed by computer algebra and CHECKED here by the kernel; nothing is trusted from the generator.

  Setting: an arbitrary commutative ring `R` with an element `e` such that `e ^ 8 = 0` (resp. `e ^ 9 = 0`).
  Taking R = A[[u]]/(u^8) this is exactly "equality of power series up to O(u^8)", without any analysis.

  * `dispersion_kInv`      -- the inverse series PRINTED in the paper (alpha_1 general, through (w/c)^7,
                              including the coefficient eta) really does invert
                              eps = c k (1 + a1 k + ... + a6 k^6)  modulo e^8.
  * `density_of_states`    -- for alpha_1 = 0:  k^2 dk/de  =  e^2 - 5 a2 e^4 - 6 a3 e^5 + 7(4 a2^2 - a4) e^6
                              + 8(9 a2 a3 - a5) e^7 - 3(55 a2^3 - 30 a2 a4 - 15 a3^2 + 3 a6) e^8   modulo e^9.
                              These are, up to the Bose-integral factors, the brackets in C, D, E, K, L.

  NOT proved here: that the term-by-term integral is an asymptotic expansion of the true C_V (a Watson-lemma
  statement about the real dispersion curve), and the assembly with `BoseIntegral.bose_integral_nat`.
```

- `def kInv`: `def kInv (a1 a2 a3 a4 a5 a6 e : R) : R`
- `def kPow2`: `def kPow2 (a1 a2 a3 a4 a5 a6 e : R) : R`
- `theorem kPow2_eq`: `theorem kPow2_eq (a1 a2 a3 a4 a5 a6 e : R) (h : e ^ 8 = 0) : kInv a1 a2 a3 a4 a5 a6 e * kInv a1 a2 a3 a4 a5 a6 e = kPow2 a1 a2 a3 a4 a5 a6 e`
- `def kPow3`: `def kPow3 (a1 a2 a3 a4 a5 a6 e : R) : R`
- `theorem kPow3_eq`: `theorem kPow3_eq (a1 a2 a3 a4 a5 a6 e : R) (h : e ^ 8 = 0) : kPow2 a1 a2 a3 a4 a5 a6 e * kInv a1 a2 a3 a4 a5 a6 e = kPow3 a1 a2 a3 a4 a5 a6 e`
- `def kPow4`: `def kPow4 (a1 a2 a3 a4 a5 a6 e : R) : R`
- `theorem kPow4_eq`: `theorem kPow4_eq (a1 a2 a3 a4 a5 a6 e : R) (h : e ^ 8 = 0) : kPow3 a1 a2 a3 a4 a5 a6 e * kInv a1 a2 a3 a4 a5 a6 e = kPow4 a1 a2 a3 a4 a5 a6 e`
- `def kPow5`: `def kPow5 (a1 a2 a3 a4 a5 a6 e : R) : R`
- `theorem kPow5_eq`: `theorem kPow5_eq (a1 a2 a3 a4 a5 a6 e : R) (h : e ^ 8 = 0) : kPow4 a1 a2 a3 a4 a5 a6 e * kInv a1 a2 a3 a4 a5 a6 e = kPow5 a1 a2 a3 a4 a5 a6 e`
- `def kPow6`: `def kPow6 (a1 a2 a3 a4 a5 a6 e : R) : R`
- `theorem kPow6_eq`: `theorem kPow6_eq (a1 a2 a3 a4 a5 a6 e : R) (h : e ^ 8 = 0) : kPow5 a1 a2 a3 a4 a5 a6 e * kInv a1 a2 a3 a4 a5 a6 e = kPow6 a1 a2 a3 a4 a5 a6 e`
- `def kPow7`: `def kPow7 (a1 a2 a3 a4 a5 a6 e : R) : R`
- `theorem kPow7_eq`: `theorem kPow7_eq (a1 a2 a3 a4 a5 a6 e : R) (h : e ^ 8 = 0) : kPow6 a1 a2 a3 a4 a5 a6 e * kInv a1 a2 a3 a4 a5 a6 e = kPow7 a1 a2 a3 a4 a5 a6 e`
- `theorem dispersion_kInv`: `theorem dispersion_kInv (a1 a2 a3 a4 a5 a6 e : R) (h : e ^ 8 = 0) : kInv a1 a2 a3 a4 a5 a6 e * (1 + a1 * kInv a1 a2 a3 a4 a5 a6 e + a2 * kInv a1 a2 a3 a4 a5 a6 e ^ 2 + a3 * kInv a1 a2 a3 a4 a5 a6 e ^ 3 + a4 * kInv a1 a2 a3 a4 a5 a6 e ^ 4 + a5 * kInv a1 a2 a3 a4 a5 a6 e ^ 5 + a6 * kInv a1 a2 a3 a4 a5`
- `def kInv0`: `def kInv0 (a2 a3 a4 a5 a6 e : R) : R`
- `def kInv0Deriv`: `def kInv0Deriv (a2 a3 a4 a5 a6 e : R) : R`
- `def kSq0`: `def kSq0 (a2 a3 a4 a5 a6 e : R) : R`
- `theorem kSq0_eq`: `theorem kSq0_eq (a2 a3 a4 a5 a6 e : R) (h : e ^ 9 = 0) : kInv0 a2 a3 a4 a5 a6 e ^ 2 = kSq0 a2 a3 a4 a5 a6 e`
- `theorem density_of_states`: `theorem density_of_states (a2 a3 a4 a5 a6 e : R) (h : e ^ 9 = 0) : kInv0 a2 a3 a4 a5 a6 e ^ 2 * kInv0Deriv a2 a3 a4 a5 a6 e = e ^ 2 - 5 * a2 * e ^ 4 - 6 * a3 * e ^ 5 + 7 * (4 * a2 ^ 2 - a4) * e ^ 6 + 8 * (9 * a2 * a3 - a5) * e ^ 7 - 3 * (55 * a2 ^ 3 - 30 * a2 * a4 - 15 * a3 ^ 2 + 3 * a6) * e ^ 8`

## PhononSpecificHeat

```
PhononSpecificHeat.lean -- assembling the phonon specific-heat series of
  Godfrin et al., PRB 103, 104516 (2021), Eq. (22):

      C_V = A T^3 + C T^5 + D T^6 + E T^7 + K T^8 + L T^9        (alpha_1 = 0)

  Three ingredients, each proved elsewhere or here:
    1. the density of states  k^2 dk/du = sum_n g_n u^n  modulo u^9      (`PhononSeries.density_of_states`);
    2. the thermal integral   int_0^inf u^n / (exp(beta u) - 1) du = beta^-(n+1) n! zeta(n+1)
                                                                        (`thermal_bose_integral`, from
                                                                         `BoseIntegral.bose_integral_nat`);
    3. zeta(6), zeta(8), zeta(10) in closed form (Bernoulli numbers B6, B8, B10 evaluated here);
       zeta(7) and zeta(9) have no known closed form and stay symbolic -- which is WHY the paper's D and K
       carry an explicit zeta while A, C, E, L carry powers of pi.

  RESULT (`phonon_specific_heat`): the derivative of the term-by-term energy is exactly the six printed
  closed forms. All six printed coefficients are CONFIRMED; no discrepancy was found.

  NOT proved: that this term-by-term series is an asymptotic expansion of the specific heat computed from the
  full measured dispersion curve (upper limit -> infinity, roton branch neglected). That is an analytic
  statement about a measured function and is outside what a proof assistant can certify.
```

- `theorem bernoulli'_five`: `theorem bernoulli'_five : bernoulli' 5 = 0`
- `theorem bernoulli'_six`: `theorem bernoulli'_six : bernoulli' 6 = 1 / 42`
- `theorem bernoulli'_seven`: `theorem bernoulli'_seven : bernoulli' 7 = 0`
- `theorem bernoulli'_eight`: `theorem bernoulli'_eight : bernoulli' 8 = -1 / 30`
- `theorem bernoulli'_nine`: `theorem bernoulli'_nine : bernoulli' 9 = 0`
- `theorem bernoulli'_ten`: `theorem bernoulli'_ten : bernoulli' 10 = 5 / 66`
- `theorem riemannZeta_six`: `theorem riemannZeta_six : riemannZeta 6 = (π : ℂ) ^ 6 / 945`
- `theorem riemannZeta_eight`: `theorem riemannZeta_eight : riemannZeta 8 = (π : ℂ) ^ 8 / 9450`
- `theorem riemannZeta_ten`: `theorem riemannZeta_ten : riemannZeta 10 = (π : ℂ) ^ 10 / 93555`
- `theorem thermal_bose_integral`: `theorem thermal_bose_integral {n : ℕ} (hn : 1 ≤ n) {β : ℝ} (hβ : 0 < β) : mellin (fun u => bose (β * u)) (n + 1) = (β : ℂ) ^ (-((n : ℂ) + 1)) * ((Nat.factorial n : ℂ) * riemannZeta (n + 1))`
- `theorem bose_integral_values`: `theorem bose_integral_values : mellin bose 4 = (π : ℂ) ^ 4 / 15 ∧ mellin bose 6 = 8 * (π : ℂ) ^ 6 / 63 ∧ mellin bose 7 = 720 * riemannZeta 7 ∧ mellin bose 8 = 8 * (π : ℂ) ^ 8 / 15 ∧ mellin bose 9 = 40320 * riemannZeta 9 ∧ mellin bose 10 = 128 * (π : ℂ) ^ 10 / 33`
- `def energyTerm`: `noncomputable def energyTerm (V kB hbar c g : ℝ) (n : ℕ) (I T : ℝ) : ℝ`
- `theorem energyTerm_two`: `theorem energyTerm_two (V kB hbar c I T : ℝ) : energyTerm V kB hbar c 1 2 I T = debyeEnergy V kB hbar c I T`
- `theorem energyTerm_hasDerivAt`: `theorem energyTerm_hasDerivAt (V kB hbar c g : ℝ) (n : ℕ) (I T : ℝ) : HasDerivAt (fun T => energyTerm V kB hbar c g n I T) (V / (2 * π ^ 2) * g * I * kB ^ (n + 2) / (hbar * c) ^ (n + 1) * ((n + 2 : ℕ) * T ^ (n + 1))) T`
- `theorem phonon_specific_heat`: `theorem phonon_specific_heat (V kB hbar c a2 a3 a4 a5 a6 z7 z9 T : ℝ) (hh : hbar ≠ 0) (hc : c ≠ 0) : HasDerivAt (fun T => energyTerm V kB hbar c 1 2 (π ^ 4 / 15) T + energyTerm V kB hbar c (-5 * a2) 4 (8 * π ^ 6 / 63) T + energyTerm V kB hbar c (-6 * a3) 5 (720 * z7) T + energyTerm V kB hbar c (7 * `

## QHFricke

```
QHFricke.lean -- where the Fricke involution of `Fricke.lean` meets the quantum Hall modular group,
  and where it stops. Gate verdict 3 of `docs/designs/PGPE_BKT_PREREG.md` amendment A2.

  Background (Lütken–Ross, PRB 45, 11837 (1992); review arXiv:1008.5257): for the spin-polarised
  quantum Hall system the holomorphic part of the proposed emergent symmetry acting on the complex
  conductivity `σ = σ_xy + i σ_xx` (units e²/h) is `Γ₀(2)`, generated by `T : σ ↦ σ + 1` and
  `D = S T² S : σ ↦ σ/(1 − 2σ)`. Plateaux sit at rationals `p/q` with `q` odd; the delocalisation
  critical point between the `ν = 0` and `ν = 1` plateaux is `σ⊗ = (1+i)/2`.

  Proved here, as arithmetic of Möbius maps, with no physics attached:

  * `M_mem_Gamma0` / `M_mul_M` / `M_fixes_crit` : `M = (1, -1; 2, -1)` lies in `Γ₀(2)`, squares to `-1`
    (an elliptic element, order 2 in `PSL(2,ℤ)`), and fixes `σ⊗ = (1+i)/2`;
  * `gamma0_two_odd_den` : every matrix with even lower-left entry and determinant 1 sends an
    odd-denominator fraction to an odd-denominator fraction -- `Γ₀(2)` preserves the plateau class;
  * `fricke_crit` : the level-2 Fricke map `σ ↦ -1/(2σ)` sends `σ⊗` to `σ⊗ - 1 = T⁻¹ σ⊗`, so on the
    quotient `Γ₀(2)\H` it FIXES the critical point's orbit (with `fricke_on_axis`'s `i/√2`, one of the
    two fixed points of `w₂` on `X₀(2)`; that there are exactly two is classical and not proved here);
  * `fricke_plateau_not_plateau` : but the Fricke map sends every plateau `p/q` (`q` odd, `p ≠ 0`) to
    `-q/(2p)`, which equals NO fraction with an odd denominator. So `w₂` is not a symmetry of the
    Hall phase diagram: it exchanges the cusp class that carries the plateaux with the one that
    carries none.

  NOT proved, NOT claimed: that `Γ₀(2)` is the symmetry of real Hall samples (that is Lütken–Ross's
  physical proposal, supported by data they review, not a theorem); anything about K3 surfaces;
  anything about helium or BKT.
```

- `def mob`: `noncomputable def mob (a b c d : ℤ) (z : ℂ) : ℂ`
- `def crit`: `noncomputable def crit : ℂ`
- `def M`: `def M : SL(2, ℤ)`
- `theorem M_mem_Gamma0`: `theorem M_mem_Gamma0 : M ∈ Gamma0 2`
- `theorem M_mul_M`: `theorem M_mul_M : (M : Matrix (Fin 2) (Fin 2) ℤ) * M = -1`
- `theorem M_fixes_crit`: `theorem M_fixes_crit : mob 1 (-1) 2 (-1) crit = crit`
- `theorem gamma0_two_odd_den`: `theorem gamma0_two_odd_den (a b c d p q : ℤ) (hdet : a * d - b * c = 1) (hc : Even c) (hq : Odd q) : Odd (c * p + d * q)`
- `theorem fricke_crit`: `theorem fricke_crit : mob 0 (-1) 2 0 crit = crit - 1`
- `theorem fricke_plateau_not_plateau`: `theorem fricke_plateau_not_plateau (p q r s : ℤ) (hp : p ≠ 0) (hq : Odd q) (hs : Odd s) : (r : ℚ) / s ≠ -(q : ℚ) / (2 * p)`

## QuantizedCirculation

```
Quantized circulation: the defining property of a quantum fluid.

In a superfluid the velocity is a phase gradient, `u = (hbar/m) grad S`, so the circulation around a
closed loop is `(hbar/m)` times the total phase change. Because the wavefunction is single valued,
that phase change is a multiple of `2 pi`, and the circulation is therefore a multiple of

    kappa := h/m = 2 pi hbar / m          (the quantum of circulation)

This file proves that, in the discrete form in which it is actually computed from simulation or
experimental data: a loop of sample points, with the phase read at each. It is the statement that
`VortexWinding.loop_sum_eq_mul` was built for, and it is what makes a detected vortex a *quantized*
vortex rather than merely a phase defect.

WHAT IS PROVED
  * `circulation_quantized`  : around any closed loop of sample points, `Gamma = q * kappa`, `q` integer;
  * `circulation_eq_zero_iff`: the circulation vanishes exactly when the winding number does;
  * `abs_circulation_ge`     : a nonzero circulation has magnitude at least `kappa` -- there is no
                               fraction of a quantum;
  * `circulation_quantum_attained` : and `kappa` itself is attained, by an explicit four-point loop,
                               so the bound is sharp and not vacuous.

WHAT IS NOT PROVED: that the discrete loop sum equals the continuum line integral. That is a
statement about sampling a smooth phase (and it fails, by design, when a phase step reaches `pi` --
see `VortexWinding.pdiff_add_rev_eq_two_pi_iff`), not a statement about quantization.
```

- `def kappa`: `noncomputable def kappa (hbar m : ℝ) : ℝ`
- `def circulation`: `noncomputable def circulation (hbar m : ℝ) (S : ℕ → ℝ) (n : ℕ) : ℝ`
- `theorem circulation_quantized`: `theorem circulation_quantized (hbar m : ℝ) (S : ℕ → ℝ) (n : ℕ) (hclosed : S n = S 0) : ∃ q : ℤ, circulation hbar m S n = (q : ℝ) * kappa hbar m`
- `theorem circulation_eq_zero_iff`: `theorem circulation_eq_zero_iff (hbar m : ℝ) (hhbar : hbar ≠ 0) (hm : m ≠ 0) (S : ℕ → ℝ) (n : ℕ) : circulation hbar m S n = 0 ↔ ∑ i ∈ Finset.range n, pdiff (S i) (S (i + 1)) = 0`
- `theorem abs_circulation_ge`: `theorem abs_circulation_ge (hbar m : ℝ) (hhbar : 0 < hbar) (hm : 0 < m) (S : ℕ → ℝ) (n : ℕ) (hclosed : S n = S 0) (hne : circulation hbar m S n ≠ 0) : kappa hbar m ≤ |circulation hbar m S n|`
- `theorem pdiff_of_mem`: `theorem pdiff_of_mem {a b : ℝ} (h : b - a ∈ Set.Ioc (-π) π) : pdiff a b = b - a`
- `theorem pdiff_of_wrap`: `theorem pdiff_of_wrap {a b : ℝ} (h : b - a + 2 * π ∈ Set.Ioc (-π) π) : pdiff a b = b - a + 2 * π`
- `def quarterLoop`: `noncomputable def quarterLoop : ℕ → ℝ`
- `theorem circulation_quantum_attained`: `theorem circulation_quantum_attained (hbar m : ℝ) : circulation hbar m quarterLoop 4 = kappa hbar m`

## QuantumFluidsShell

```
Formalisation of the conjugated complexification's energy conservation.

Closes audit ruling O2 of docs/designs/M2_W4_DISPERSIVE_SHELL.md, which
accepted the complexification as a labelled deformation "carrying no Tier A
backing until it has its own Lean development".

Deliberately mirrors MechanicaFluidorum's real-model development
(lean_src/DyadicShell_Statements.lean: `shellB`, `sum_mul_shellB`,
`shellB_energy_conservation`) so the two can be compared line for line, and
against the SAME pinned Mathlib revision, so a theorem here is checked
against the same library every result in that stream's LEDGER was verified
against.

WHAT IS AND IS NOT PROVED HERE. This file proves the algebraic identity that
the complexified nonlinearity conserves the energy pairing exactly. That is
the single load-bearing claim under W4's model -- memo section 2b, and the
property that makes the complexification usable at all. It says nothing about
boundedness, blow-up, or the dispersive regulator's effect on any observable;
those are Tier B or open.
```

- `def shellBc`: `noncomputable def shellBc (k : ℕ → ℝ) : ℕ → (ℕ → ℂ) → ℂ | 0,     v => -((k 0 : ℂ) * (starRingEnd ℂ) (v 0) * v 1) | m + 1, v => (k m : ℂ) * (v m * v m) - (k (m + 1) : ℂ) * (starRingEnd ℂ) (v (m + 1)) * v (m + 2)`
- `def out`: `noncomputable def out (k : ℕ → ℝ) (v : ℕ → ℂ) (m : ℕ) : ℝ`
- `theorem re_conj_sq_mul`: `theorem re_conj_sq_mul (a b : ℂ) : ((starRingEnd ℂ) a * (starRingEnd ℂ) a * b).re = ((starRingEnd ℂ) b * a * a).re`
- `theorem sum_re_conj_mul_shellBc`: `theorem sum_re_conj_mul_shellBc (k : ℕ → ℝ) (v : ℕ → ℂ) : ∀ N : ℕ, ∑ n ∈ Finset.range (N + 1), ((starRingEnd ℂ) (v n) * shellBc k n v).re = -(out k v N) | 0 => by`
- `theorem shellBc_energy_conservation`: `theorem shellBc_energy_conservation (k : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hbc : v (N + 1) = 0) : ∑ n ∈ Finset.range (N + 1), ((starRingEnd ℂ) (v n) * shellBc k n v).re = 0`
- `theorem shellBc_real`: `theorem shellBc_real (k : ℕ → ℝ) (v : ℕ → ℂ) (hv : ∀ n, (v n).im = 0) (n : ℕ) : (shellBc k n v).im = 0`
- `def rtrace`: `noncomputable def rtrace (f : ℂ →ₗ[ℝ] ℂ) : ℝ`
- `theorem rtrace_add`: `theorem rtrace_add (f g : ℂ →ₗ[ℝ] ℂ) : rtrace (f + g) = rtrace f + rtrace g`
- `theorem rtrace_mulRight`: `theorem rtrace_mulRight (c : ℂ) : rtrace (LinearMap.mulRight ℝ c) = 2 * c.re`
- `theorem rtrace_mul_I`: `theorem rtrace_mul_I (d : ℝ) : rtrace (LinearMap.mulRight ℝ ((d : ℂ) * Complex.I)) = 0`
- `theorem rtrace_conj_mul`: `theorem rtrace_conj_mul (w : ℂ) : rtrace ((LinearMap.mulRight ℝ w).comp Complex.conjAe.toLinearMap) = 0`
- `theorem shell_divergence_zero`: `theorem shell_divergence_zero (d : ℝ) (w : ℂ) : rtrace ((LinearMap.mulRight ℝ w).comp Complex.conjAe.toLinearMap + LinearMap.mulRight ℝ ((d : ℂ) * Complex.I)) = 0`
- `theorem seam_conserves_iff`: `theorem seam_conserves_iff (k : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hk : k N ≠ 0) : (∑ n ∈ Finset.range (N + 1), ((starRingEnd ℂ) (v n) * shellBc k n v).re = 0) ↔ ((starRingEnd ℂ) (v N) * (starRingEnd ℂ) (v N) * v (N + 1)).re = 0`
- `theorem seam_zero_conserves`: `theorem seam_zero_conserves (k : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hk : k N ≠ 0) (hbc : v (N + 1) = 0) : ∑ n ∈ Finset.range (N + 1), ((starRingEnd ℂ) (v n) * shellBc k n v).re = 0`
- `theorem seam_gpe_conserves`: `theorem seam_gpe_conserves (k : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (μ : ℝ) (hk : k N ≠ 0) (hbc : v (N + 1) = Complex.I * (μ : ℂ) * (v N * v N)) : ∑ n ∈ Finset.range (N + 1), ((starRingEnd ℂ) (v n) * shellBc k n v).re = 0`

## QuasiPeriodicBound

```
QuasiPeriodicBound.lean -- companion of amendment E-A1 of docs/designs/PGPE_EINSTEIN_PREREG.md (criterion I2) and
  of docs/designs/LEVERAGE_DONG2026.md.

  A vortex configuration whose motion about the point-vortex prediction is a regular island (Dong et al., Nature
  Physics 2026, for the many-body quantum case; Modin-Viviani 2020, Theorem 8, for the torus dipole as a relative
  equilibrium) has quasi-periodic residual coordinates: finite trigonometric sums. The discriminant used on the
  data is the mean-square increment (MSD) against lag.

  * `trig_sum_bound`: a finite sum Σ aₖ cos(ωₖ t + φₖ) is bounded by Σ|aₖ| for every t.
  * `increment_bound`: its increments over any lag are bounded by 2 Σ|aₖ|.
  * `msd_bound`: hence every mean of squared increments (over any finite sample of times, any lags) is at most
    4 (Σ|aₖ|)²: the MSD of a quasi-periodic signal is bounded, uniformly in the lag.
  * `random_walk_exceeds`: a linearly growing MSD `c τ` with `c > 0` exceeds that bound for every lag beyond
    4 (Σ|aₖ|)²/c. Contrapositive of `msd_bound`: a residual whose MSD keeps growing is not a finite quasi-periodic
    sum of the given amplitudes -- the island reading is refuted by growth, never by a plateau.
  * `relative_equilibrium_dipole`: the torus dipole of the dissipative model with α = 0 has constant separation
    (the α = 0 case of `dipole_sq_law`, restated), so the separation of a single pair at T = 0 is the trivial
    quasi-periodic signal (one term, zero frequency): its MSD is identically zero -- gate G1 (iii), as a theorem.

  Elementary; the content is that the I2 decision rule is sound in one direction and silent in the other.
```

- `def qp`: `noncomputable def qp (a ω φ : ι → ℝ) (t : ℝ) : ℝ`
- `theorem trig_sum_bound`: `theorem trig_sum_bound (a ω φ : ι → ℝ) (t : ℝ) : |qp a ω φ t| ≤ ∑ k, |a k|`
- `theorem increment_bound`: `theorem increment_bound (a ω φ : ι → ℝ) (t τ : ℝ) : |qp a ω φ (t + τ) - qp a ω φ t| ≤ 2 * ∑ k, |a k|`
- `theorem msd_bound`: `theorem msd_bound (a ω φ : ι → ℝ) {J : Type*} [Fintype J] [Nonempty J] (ts τs : J → ℝ) : (∑ j, (qp a ω φ (ts j + τs j) - qp a ω φ (ts j)) ^ 2) / Fintype.card J ≤ (2 * ∑ k, |a k|) ^ 2`
- `theorem random_walk_exceeds`: `theorem random_walk_exceeds (A c : ℝ) (hc : 0 < c) : ∀ τ, 4 * A ^ 2 / c < τ → (2 * A) ^ 2 < c * τ`
- `theorem not_qp_of_msd_large`: `theorem not_qp_of_msd_large (a : ι → ℝ) {J : Type*} [Fintype J] [Nonempty J] (x : ℝ → ℝ) (ts τs : J → ℝ) (h : (2 * ∑ k, |a k|) ^ 2 < (∑ j, (x (ts j + τs j) - x (ts j)) ^ 2) / Fintype.card J) : ∀ ω φ : ι → ℝ, x ≠ qp a ω φ`
- `theorem relative_equilibrium_dipole`: `theorem relative_equilibrium_dipole (d0sq : ℝ) : ∀ t : ℝ, (d0sq - 4 * (0 : ℝ) * t) = d0sq`

## RCFTDuality

```
RCFTDuality.lean -- a sixth cross-domain case for the criterion of `duality_sector.tex`: the modular
  S-matrix of a rational conformal field theory (RCFT), sharper than `SectorDuality.lean`'s Z_N case.

  Background (Verlinde 1980; Rev. Mod. Phys. -- no, Verlinde 1988, Nucl. Phys. B300; proved from
  Moore-Seiberg's polynomial equations, Phys. Lett. B212 1988 and Commun. Math. Phys. 123 1989): the
  Verlinde formula N_ij^k = sum_m S_im S_jm S*_km / S_0m makes the modular S-matrix acting on the RCFT's
  primaries (the sectors) a duality. Fuchs (hep-th/9306162, eq. 4.1-4.2) states the exact identity
  S^2 = C = (ST)^3 for S unitary and symmetric, C the charge-conjugation matrix -- sharper than
  `SectorDuality.lean`'s finite-cyclic case, where Mathlib's UNnormalised `ZMod.dft` gives
  `dft (dft Phi) = N • Phi(-.)`, not the identity.

  S is a literal finite-abelian-group Fourier transform only in the "pointed" (simple-current) case,
  where the fusion ring is a group -- e.g. su(2) level 1 (Kac-Peterson/Fuchs eq. 7.7), two primaries
  (spin 0 and spin 1/2), fusing as Z_2, with S_jk = n^{-1/2} exp(2 pi i m j k / n) for n = 2: this is
  exactly the (unnormalised) Hadamard matrix, and its square is 2 * (the identity) -- since both
  primaries are self-conjugate, C = 1, so the UNITARY (normalised) S satisfies S^2 = 1 exactly, with
  none of the decoupled factor |Z_2| = 2 that `SectorDuality.kramersWannier_gauging_sq` carries.

  What this module proves: a single, decidable 2x2 integer-matrix identity. What it does NOT prove --
  and no elementary Lean tactic could -- is that this matrix IS the su(2) level-1 Kac-Peterson S-matrix;
  that identification is representation theory of affine Lie algebras (Fuchs's derivation), supplied
  here as physics input in this docstring, exactly as `SectorDuality.lean` already treats the
  Z_N-Fourier-transform-is-Kramers-Wannier identification as prose, not as a fact the type checker
  verifies. Nor does this module touch the general (non-abelian) case, where S is the Kac-Peterson
  Weyl-sum matrix and no elementary group Fourier transform underlies it at all.

  Self-dual point (reading, not a theorem): the free boson at the T-duality self-dual radius R = 1
  enhances to su(2) level 1. Pace-Chatterjee-Shao (arXiv:2412.18606, Fig. 4) show this point sits on a
  *continuous* line of RCFT fixed points (1 <= R <= sqrt 2), separating three gapped phases -- by the
  criterion of `duality_sector.tex`, a point like any other on a line of fixed points, the same verdict
  already reached for the compact boson's own self-dual radius an
```

- `def su2Level1_S`: `def su2Level1_S : Matrix (Fin 2) (Fin 2) ℤ`
- `theorem su2Level1_S_sq`: `theorem su2Level1_S_sq : su2Level1_S * su2Level1_S = (2 : ℤ) • (1 : Matrix (Fin 2) (Fin 2) ℤ)`
- `theorem su2Level1_S_symm`: `theorem su2Level1_S_symm : su2Level1_S.transpose = su2Level1_S`
- `theorem su2Level1_S_det`: `theorem su2Level1_S_det : su2Level1_S.det = -2`

## RipsFloor

```
The bridge lemma of workstream T (docs/designs/TDA_VORTEX_FLOOR.md §7).

A quantum fluid's vortices cannot sit closer than about the healing length. Workstream T reads that
as a FLOOR IN A PERSISTENCE DIAGRAM. This file proves the one step that licenses the reading, at the
level of the filtration's 1-skeleton, where it is elementary and can be checked honestly:

    no pair of distinct points is joined below the minimum separation,
    and the minimum separation is exactly the scale at which the first edge appears.

SCOPE, stated precisely. Persistent homology is NOT formalised here: no simplicial complex, no
homology functor, no persistence module, no stability theorem. What is proved is a statement about
the Vietoris-Rips GRAPH. The remaining step -- "an H0 class can die only at a scale where an edge
appears", which is immediate from the definition of the filtration -- is NOT formalised and is
carried as a stated assumption in the memo. Claiming this file proves a persistence result would be
exactly the kind of overreach the LeanMaster audit found elsewhere.
```

- `def Adj`: `def Adj (X : ι → E) (t : ℝ) (i j : ι) : Prop`
- `def Separated`: `def Separated (X : ι → E) (d : ℝ) : Prop`
- `theorem no_adj_of_lt`: `theorem no_adj_of_lt {X : ι → E} {d t : ℝ} (hsep : Separated X d) (ht : t < d) (i j : ι) : ¬ Adj X t i j`
- `theorem le_of_adj`: `theorem le_of_adj {X : ι → E} {d t : ℝ} (hsep : Separated X d) (h : ∃ i j, Adj X t i j) : d ≤ t`
- `theorem isLeast_edge_scale`: `theorem isLeast_edge_scale {X : ι → E} {d : ℝ} (hsep : Separated X d) {a b : ι} (hab : a ≠ b) (hd : dist (X a) (X b) = d) : IsLeast {t : ℝ | ∃ i j, Adj X t i j} d`
- `theorem separated_zero_of_not_injective`: `theorem separated_zero_of_not_injective {X : ι → E} : Separated X 0`

## ScaleResolvedWinding

```
ScaleResolvedWinding.lean -- the winding number seen at scale R is the net topological charge
  inside R: a discrete Stokes theorem for phase windings, and its two corollaries, "a dipole is
  invisible from outside" and "a single core is seen as ±1 from any scale that encloses it".

  Thought experiment B of the round ("the small-pair trap"): a vortex and an antivortex a distance
  `a` apart. A loop around one of them sees winding ±1; any loop of size `R ≫ a` enclosing both sees
  0. So the causal variable is not "the number of vortices" but the winding resolved in scale, W(R),
  which is what a persistent-homology reading of the phase field tracks, and the BKT transition is the
  point where W(R) stops vanishing at large R.

  Model. A region is a finite family of plaquettes `p : Fin m`, each carrying four corner phases
  `θ p i`, `i : Fin 4`; the edge `(p, i)` runs from `θ p i` to `θ p (i+1)` (indices mod 4). Interior
  edges come in reversed pairs (the involution `σ`), boundary edges are the rest. Nothing is assumed
  about the geometry: this is the combinatorial content of "the faces of a region traverse every
  interior edge once in each direction", the same structure as `VortexWinding.Balanced`.

  * `winding_int`        : each plaquette's loop sum is `2π` times an integer (its charge);
  * `stokes`             : **oriented boundary sum = sum of plaquette loop sums**, provided no interior
                           edge sits at the branch point `π`;
  * `boundary_eq_charge` : the boundary sum is `2π` times the net charge inside;
  * `dipole_invisible`   : a region whose charges sum to zero (one +1, one -1, rest 0) has boundary
                           winding 0 -- whatever its size;
  * `single_core_visible`: a region containing exactly one charged plaquette (charge q) has boundary
                           winding q -- whatever its size.

  The scale R enters only through *which* plaquettes are inside: W(R) = Σ_{p inside R} q_p.

  Negative controls (scratch, not here): `stokes` without the no-cut hypothesis fails; a region whose
  interior pairing fixes an edge fails.

  NOT PROVED: that the boundary edges of a region form a single closed loop (so the boundary sum is
  what `loop_sum_eq_mul` computes for that loop) -- this is a statement about planar regions, and the
  theorem holds without it; the continuum limit.
```

- `structure Region`: `structure Region (m : ℕ)`
- `def Region.step`: `noncomputable def Region.step (e : Fin m × Fin 4) : ℝ`
- `def Region.winding`: `noncomputable def Region.winding (p : Fin m) : ℝ`
- `def Region.boundarySum`: `noncomputable def Region.boundarySum : ℝ`
- `theorem winding_int`: `theorem winding_int (p : Fin m) : ∃ q : ℤ, Rg.winding p = (q : ℝ) * (2 * π)`
- `theorem interior_sum_eq_zero`: `theorem interior_sum_eq_zero (hcut : ∀ e ∈ Rg.interior, Rg.step e ≠ π) : ∑ e ∈ Rg.interior, Rg.step e = 0`
- `theorem stokes`: `theorem stokes (hcut : ∀ e ∈ Rg.interior, Rg.step e ≠ π) : Rg.boundarySum = ∑ p : Fin m, Rg.winding p`
- `theorem boundary_eq_charge`: `theorem boundary_eq_charge (hcut : ∀ e ∈ Rg.interior, Rg.step e ≠ π) (q : Fin m → ℤ) (hq : ∀ p, Rg.winding p = (q p : ℝ) * (2 * π)) : Rg.boundarySum = ((∑ p, q p : ℤ) : ℝ) * (2 * π)`
- `theorem dipole_invisible`: `theorem dipole_invisible (hcut : ∀ e ∈ Rg.interior, Rg.step e ≠ π) (q : Fin m → ℤ) (hq : ∀ p, Rg.winding p = (q p : ℝ) * (2 * π)) (hneutral : ∑ p, q p = 0) : Rg.boundarySum = 0`
- `theorem single_core_visible`: `theorem single_core_visible (hcut : ∀ e ∈ Rg.interior, Rg.step e ≠ π) (q : Fin m → ℤ) (hq : ∀ p, Rg.winding p = (q p : ℝ) * (2 * π)) (p₀ : Fin m) (hothers : ∀ p ≠ p₀, q p = 0) : Rg.boundarySum = (q p₀ : ℝ) * (2 * π)`

## SectorDuality

```
SectorDuality.lean -- the finite-cyclic-group counterpart of `CompactBoson`'s duality-as-reindexing
  statement: on a Z_N sector group, the duality *is* Mathlib's own discrete Fourier transform
  (`ZMod.dft`), and its defining property -- Fourier inversion, `ZMod.dft_dft` -- is exactly Savit's
  "duality is a Fourier/Poisson-resummation transform on the group of sectors" (Rev. Mod. Phys. 52,
  453, 1980) and Gaiotto-Kapustin-Seiberg-Willett's "the S-operation is a discrete Fourier transform
  ... via Poincaré duality between H^{q+1}(M,G) and H^{d-q-1}(M,Ĝ)" (arXiv:1412.5148), in the simplest
  nontrivial case G = Ĝ = Z_N. Nothing here is a new theorem of Fourier analysis -- `ZMod.dft_dft` is
  Mathlib's (David Loeffler's); what is new is stating three of its corollaries in the vocabulary the
  2026-09-26 literature review (`LITERATURE_REVIEW_SECTOR_LEAD.md`) asked for:

  * `sectorDuality_bijective`   : the duality is a bijection of sector-weighted data (a `LinearEquiv`
                                  is in particular an `Equiv` -- the same fact `CompactBoson.swap`
                                  states for Z, now for the finite cyclic case).
  * `sectorDuality_sq_ne_id`    : for N ≥ 2 the duality squared is NOT the identity on sector-weighted
                                  data -- Aasen-Mong-Fendley's "duality is not a symmetry in the
                                  traditional sense" (arXiv:1601.07185) and Shao's "away from the
                                  critical point Kramers-Wannier 'duality' is... a map from the
                                  high-temperature phase to the low-temperature phase" (TASI lectures,
                                  arXiv:2308.00747), read off `ZMod.dft_dft`'s own N•(reflection) shape.
  * `kramersWannier_gauging_sq` : the N = 2 (Ising / Kramers-Wannier) case of `ZMod.dft_dft`, spelled
                                  out: gauging a Z_2 sector symmetry twice returns TWICE the original
                                  weighting -- Choi-Córdova-Hsin-Lam-Shao's and Gaiotto-Kapustin-
                                  Seiberg-Willett's "gauging a non-anomalous Z_2 twice gives back the
                                  original theory" (up to the decoupled factor |G| = 2 the finite-sum
                                  identity actually produces).

  What this module does NOT claim: no anomaly-inflow / SPT-obstruction argument (Choi et al.'s and
  Hayashi-Tanizaki's actual theorems, which need cohomology this file does not touch) and no statement
  about which physical fixed points are forced to be transiti
```

- `theorem sectorDuality_bijective`: `theorem sectorDuality_bijective (N : ℕ) [NeZero N] : Function.Bijective (ZMod.dft (N`
- `theorem sectorDuality_sq_ne_id`: `theorem sectorDuality_sq_ne_id (N : ℕ) [NeZero N] (hN : 2 ≤ N) : (ZMod.dft (N`
- `theorem kramersWannier_gauging_sq`: `theorem kramersWannier_gauging_sq (Φ : ZMod 2 → ℂ) : (ZMod.dft (N`

## SectorTemperature

```
SectorTemperature.lean -- what "topological sectors carry their own temperature" means, exactly,
  and why a thermometer that averages over sectors cannot read "the" temperature of a mixed state.

  Round 2 of the PGPE programme found that two boxes with the same energy, one carrying an injected
  winding configuration and one not, read different temperatures. Thought experiment F says this is
  expected: the microcanonical entropy depends on the sector, S(E, W), so ∂S/∂E does too. This file
  makes the finite, discrete version of that statement a theorem, with no physics attached beyond the
  definitions.

  Setting. A finite set of microstates `Ω`, an energy level `ε : Ω → ℕ` (energies binned to integers),
  a sector label `w : Ω → ℤ` (a winding number). The sector count `n w E` is the number of microstates
  in sector `w` at energy `E`; the global count `N E` is the sum over sectors. The discrete inverse
  temperature of a sector is the ratio of its counts at adjacent energies, `n w (E+1) / n w E`
  (that is `exp(S_w(E+1) − S_w(E))`, Boltzmann's `exp(β)` for unit energy steps); the global one is
  `N (E+1) / N E`.

  * `count_sum`            : the global count is the sum of the sector counts;
  * `entropy_ge_sector`    : global entropy ≥ every sector entropy (log of counts);
  * `mediant_le`, `le_mediant`: **the global inverse temperature lies between the smallest and the
                             largest sector inverse temperature** (the mediant inequality for ratios
                             of nonnegative sums). In words: a thermometer that does not know the
                             sector reads a weighted mean of sector temperatures, and two states of the
                             same energy in different sectors need not, and in general do not, share
                             it. Equal energy does not imply equal temperature once a conserved label
                             exists.
  * `global_eq_sector_of_single` : if only one sector is populated at both energies, the global
                             reading is that sector's reading -- the case with no topology.
  * `sector_invariant`     : the sectors are invariant sets of any evolution that never lets a loop
                             step reach the branch point (from `TopologicalProtection`): the label is
                             conserved, so the restriction of the dynamics to a sector is well defined,
                             which is what gives `S(E, W)` a physical meaning.

  NOT PROVED, NOT CLAIMED: that the equipartition thermometer of the PGPE runs reads 
```

- `def sectorCount`: `def sectorCount (ε : Ω → ℕ) (w : Ω → ℤ) (W : ℤ) (E : ℕ) : ℕ`
- `def globalCount`: `def globalCount (ε : Ω → ℕ) (E : ℕ) : ℕ`
- `def sectors`: `def sectors (w : Ω → ℤ) : Finset ℤ`
- `theorem count_sum`: `theorem count_sum (ε : Ω → ℕ) (w : Ω → ℤ) (E : ℕ) : globalCount ε E = ∑ W ∈ sectors w, sectorCount ε w W E`
- `theorem sectorCount_le`: `theorem sectorCount_le (ε : Ω → ℕ) (w : Ω → ℤ) (W : ℤ) (E : ℕ) : sectorCount ε w W E ≤ globalCount ε E`
- `theorem entropy_ge_sector`: `theorem entropy_ge_sector (ε : Ω → ℕ) (w : Ω → ℤ) (W : ℤ) (E : ℕ) : Real.log (sectorCount ε w W E) ≤ Real.log (globalCount ε E)`
- `theorem mediant_le`: `theorem mediant_le {ι : Type*} (s : Finset ι) (a b : ι → ℝ) (r : ℝ) (hs : s.Nonempty) (hb : ∀ i ∈ s, 0 < b i) (h : ∀ i ∈ s, a i / b i ≤ r) : (∑ i ∈ s, a i) / (∑ i ∈ s, b i) ≤ r`
- `theorem le_mediant`: `theorem le_mediant {ι : Type*} (s : Finset ι) (a b : ι → ℝ) (r : ℝ) (hs : s.Nonempty) (hb : ∀ i ∈ s, 0 < b i) (h : ∀ i ∈ s, r ≤ a i / b i) : r ≤ (∑ i ∈ s, a i) / (∑ i ∈ s, b i)`
- `def sectorRatio`: `noncomputable def sectorRatio (ε : Ω → ℕ) (w : Ω → ℤ) (W : ℤ) (E : ℕ) : ℝ`
- `def globalRatio`: `noncomputable def globalRatio (ε : Ω → ℕ) (E : ℕ) : ℝ`
- `theorem globalRatio_mem`: `theorem globalRatio_mem (ε : Ω → ℕ) (w : Ω → ℤ) (E : ℕ) (r₁ r₂ : ℝ) (hne : (sectors w).Nonempty) (hpos : ∀ W ∈ sectors w, 0 < sectorCount ε w W E) (hlo : ∀ W ∈ sectors w, r₁ ≤ sectorRatio ε w W E) (hhi : ∀ W ∈ sectors w, sectorRatio ε w W E ≤ r₂) : r₁ ≤ globalRatio ε E ∧ globalRatio ε E ≤ r₂`
- `theorem global_eq_sector_of_single`: `theorem global_eq_sector_of_single (ε : Ω → ℕ) (w : Ω → ℤ) (W₀ : ℤ) (E : ℕ) (hsingle : ∀ x, w x = W₀) : globalRatio ε E = sectorRatio ε w W₀ E`
- `theorem sector_invariant`: `theorem sector_invariant (θ : ℝ → ℕ → ℝ) (n : ℕ) {t₀ t₁ : ℝ} (ht : t₀ ≤ t₁) (hcont : ∀ i ≤ n, Continuous (fun t => θ t i)) (hclosed : ∀ t, θ t n = θ t 0) (hslip : ∀ t ∈ Set.Icc t₀ t₁, ∀ i < n, VortexWinding.pdiff (θ t i) (θ t (i + 1)) ≠ Real.pi) (c : ℝ) (h₀ : loopSum θ n t₀ = c) : loopSum θ n t₁ = c`

## ShellHamiltonian

```
The second invariant of the complexified dyadic shell model (design memo
docs/designs/DUAL_SCALE_SECOND_INVARIANT.md, addendum A1; CLAIM-023).

With `w_n = 2^(-n/2) v_n` the model of `QuantumFluidsShell.lean` is a Hamiltonian
second-harmonic-generation chain. In the original variables the cubic functional
  `H(v) = Σ_n g_n · Im(conj(v_n)² v_{n+1})`,   `g_{n+1} · 2 k_n = g_n · k_{n+1}`   (e.g. `g_n = 2^(-n) k_n`)
is conserved by the truncated flow.

WHAT IS PROVED. The first variation of `H` along the vector field `shellBc` telescopes:
`Σ_{n≤N} g_n · dT_n = -(g_N k_{N+1}) · Im(conj(v_N)² conj(v_{N+1}) v_{N+2})`, hence vanishes when
`v_{N+2} = 0` (truncation at shell `N+1`). `dT_n` is the derivative of `T_n = Im(conj(v_n)² v_{n+1})`
in the direction `B`, written out by the product rule.

WHAT IS NOT PROVED. The chain-rule step identifying `dT_n` with `d/dt T_n` along a solution; the
dispersive (`D`) and GPE-seam (`μ`) extensions (checked as exact polynomial identities in
exploration/second_invariant/symbolic_check.py, not in Lean); any bound or regularity statement.
```

- `def dT`: `noncomputable def dT (k : ℕ → ℝ) (v : ℕ → ℂ) (n : ℕ) : ℝ`
- `def flux4`: `noncomputable def flux4 (v : ℕ → ℂ) (n : ℕ) : ℝ`
- `theorem im_core`: `theorem im_core (a b c d : ℂ) (p q r : ℝ) : (2 * (starRingEnd ℂ) b * (starRingEnd ℂ) ((p : ℂ) * (a * a) - (q : ℂ) * (starRingEnd ℂ) b * c) * c + (starRingEnd ℂ) b * (starRingEnd ℂ) b * ((q : ℂ) * (b * b) - (r : ℂ) * (starRingEnd ℂ) c * d)).im = 2 * p * ((starRingEnd ℂ) a * (starRingEnd ℂ) a * (starR`
- `theorem dT_zero`: `theorem dT_zero (k : ℕ → ℝ) (v : ℕ → ℂ) : dT k v 0 = -(k 1 * flux4 v 0)`
- `theorem dT_succ`: `theorem dT_succ (k : ℕ → ℝ) (v : ℕ → ℂ) (m : ℕ) : dT k v (m + 1) = 2 * k m * flux4 v m - k (m + 2) * flux4 v (m + 1)`
- `theorem sum_dT`: `theorem sum_dT (k g : ℕ → ℝ) (v : ℕ → ℂ) (hg : ∀ n, g (n + 1) * (2 * k n) = g n * k (n + 1)) : ∀ N : ℕ, ∑ n ∈ Finset.range (N + 1), g n * dT k v n = -(g N * k (N + 1) * flux4 v N) | 0 => by simp [dT_zero]; ring | N + 1 => by`
- `theorem hamiltonian_rate_zero`: `theorem hamiltonian_rate_zero (k g : ℕ → ℝ) (v : ℕ → ℂ) (hg : ∀ n, g (n + 1) * (2 * k n) = g n * k (n + 1)) (N : ℕ) (hbc : v (N + 2) = 0) : ∑ n ∈ Finset.range (N + 1), g n * dT k v n = 0`
- `theorem weights_ok`: `theorem weights_ok (k : ℕ → ℝ) (n : ℕ) : ((1 / 2 : ℝ) ^ (n + 1) * k (n + 1)) * (2 * k n) = ((1 / 2 : ℝ) ^ n * k n) * k (n + 1)`
- `theorem T_real`: `theorem T_real (v : ℕ → ℂ) (hv : ∀ n, (v n).im = 0) (n : ℕ) : ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im = 0`
- `theorem cubic_bound`: `theorem cubic_bound (c : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hc : ∀ n, |c n| ≤ 1) : |∑ n ∈ Finset.range (N + 1), c n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im| ≤ Real.sqrt (∑ n ∈ Finset.range (N + 2), Complex.normSq (v n)) * ∑ n ∈ Finset.range (N + 2), Complex.normSq (v n)`
- `theorem dispersive_norm_le`: `theorem dispersive_norm_le (q c : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (Hval : ℝ) (hc : ∀ n, |c n| ≤ 1) (hH : Hval = ∑ n ∈ Finset.range (N + 2), q n * Complex.normSq (v n) + ∑ n ∈ Finset.range (N + 1), c n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im) : ∑ n ∈ Finset.range (N + 2), q n * Co`

## SigmaRule

```
The sigma-rule instantiated: which dispersive order controls which norm, uniformly in the cutoff.

`ShellHamiltonian.dispersive_norm_le` gives, for the complexified dyadic model with dispersion
`omega_n` and graded weights `2^(-n)`,
    sum_n 2^(-n) omega_n |v_n|^2  <=  H + sqrt(S) * S,       S = sum |v_n|^2 = 2E,
with `H` and `S` conserved. This file identifies the controlled quantity for the two orders that
matter, on dyadic wavenumbers `k_n = 2^n`:

  * `sigma = 2` (quantum pressure, `omega_n = D k_n^2`): controls `D * sum k_n |v_n|^2`  -- an
    `H^{1/2}`-type norm. NOT the enstrophy.
  * `sigma = 3` (`omega_n = D k_n^3`): controls `D * sum k_n^2 |v_n|^2 = 2 D Omega` -- the enstrophy.

READ THE SCOPE BEFORE CITING THIS. The bound is uniform in the cutoff `N` at FIXED `D > 0`, and it
carries a factor `1/D`: dividing through gives `Omega <= (H + (2E)^{3/2}) / (2D)`, which diverges as
`D -> 0`. It therefore says NOTHING about the `D -> 0` limit. MechanicaFluidorum's own adjudication
(Q1/Q2, 2026-09-10) retired exactly this class of result for the Millennium question, on the grounds
that a bound whose constant blows up in the limit "proves absolutely nothing" about it. That verdict
applies here and is not contested: this file is a statement about what a dispersive regulator buys at
fixed strength, not a regularity result.

Nor is there any tension with Katz-Pavlovic finite-time blow-up for the inviscid REAL dyadic model:
for `D > 0` the dispersive term `-i D k_n^3 v_n` immediately leaves the reals, and on real data the
cubic part of `H` vanishes identically (`ShellHamiltonian.T_real`), so real blow-up solutions are not
solutions of this system at all.
```

- `def kdy`: `noncomputable def kdy (n : ℕ) : ℝ`
- `def gw`: `noncomputable def gw (n : ℕ) : ℝ`
- `theorem gw_mul_kdy`: `theorem gw_mul_kdy (n : ℕ) : gw n * kdy n = 1`
- `theorem gw_mul_kdy_pow`: `theorem gw_mul_kdy_pow (n s : ℕ) : gw n * kdy n ^ (s + 1) = kdy n ^ s`
- `theorem sigma_two_weight`: `theorem sigma_two_weight (D : ℝ) (n : ℕ) : gw n * (D * kdy n ^ 2) = D * kdy n`
- `theorem sigma_three_weight`: `theorem sigma_three_weight (D : ℝ) (n : ℕ) : gw n * (D * kdy n ^ 3) = D * kdy n ^ 2`
- `def enstrophy`: `noncomputable def enstrophy (v : ℕ → ℂ) (M : ℕ) : ℝ`
- `theorem enstrophy_le_sigma_three`: `theorem enstrophy_le_sigma_three (D : ℝ) (v : ℕ → ℂ) (N : ℕ) (Hval : ℝ) (hH : Hval = ∑ n ∈ Finset.range (N + 2), (gw n * (D * kdy n ^ 3)) * Complex.normSq (v n) + ∑ n ∈ Finset.range (N + 1), (gw n * kdy n) * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im) : 2 * D * enstrophy v (N + 2`
- `theorem halfNorm_le_sigma_two`: `theorem halfNorm_le_sigma_two (D : ℝ) (v : ℕ → ℂ) (N : ℕ) (Hval : ℝ) (hH : Hval = ∑ n ∈ Finset.range (N + 2), (gw n * (D * kdy n ^ 2)) * Complex.normSq (v n) + ∑ n ∈ Finset.range (N + 1), (gw n * kdy n) * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im) : ∑ n ∈ Finset.range (N + 2), (`

## TopologicalProtection

```
TopologicalProtection.lean -- why a winding number can act as a CAUSE: it is conserved by every
  evolution that avoids a phase slip, so it is a memory the dynamics cannot erase continuously.

  `VortexWinding.loop_sum_eq_mul` and `QuantizedCirculation` prove that the loop sum of principal phase
  differences is `2π` times an integer (quantization). Quantization alone does not make topology
  causal: an integer that could jump freely would carry no memory. What makes it causal is
  conservation. This file proves conservation, discrete and continuous:

  * `pdiff_shift`           : moving the two endpoint phases by `δa`, `δb` moves the principal
                              difference by `δb - δa`, as long as the result stays in `(-π, π]`;
  * `loop_sum_stable`       : a perturbation `δ` of the loop phases leaves the loop sum (hence the
                              winding number) unchanged, provided no edge is pushed through the branch
                              point -- the quantitative form of "small perturbations cannot change
                              topology";
  * `loop_sum_stable_of_small` : an explicit sufficient condition: every `|δ i| < ε` and every edge step
                              `|pdiff| < π - 2ε`;
  * `circulation_conserved` : the same for the superfluid circulation (a discrete Kelvin theorem whose
                              only ingredient is topology);
  * `loop_sum_const_of_no_slip` : **continuous-time protection.** For phases depending continuously on
                              time, if no edge step ever reaches the branch point `π` on `[t₀, t₁]`,
                              the loop sum at `t₁` equals the loop sum at `t₀`;
  * `slip_of_winding_change`: contrapositive: if the winding changed, some edge step hit `π` at some
                              intermediate time -- a phase slip (Anderson, RMP 38, 298 (1966)).
                              In the continuum limit, that is the passage of a zero of `ψ`, a vortex
                              core, across the loop.

  Negative control (in the scratch file of the round, not here): the stability statement is false
  without its hypothesis; `quarterLoop`-type examples show a winding change when one edge crosses `π`.

  NOT PROVED: the continuum limit (that a discrete edge step reaching `π` corresponds to a zero of a
  smooth `ψ` crossing the loop); anything about energy barriers or rates of phase slips.
```

- `theorem pdiff_shift`: `theorem pdiff_shift (a b da db : ℝ) (h : pdiff a b + (db - da) ∈ Set.Ioc (-π) π) : pdiff (a + da) (b + db) = pdiff a b + (db - da)`
- `theorem loop_sum_stable`: `theorem loop_sum_stable (θ δ : ℕ → ℝ) (n : ℕ) (hδ : δ n = δ 0) (h : ∀ i < n, pdiff (θ i) (θ (i + 1)) + (δ (i + 1) - δ i) ∈ Set.Ioc (-π) π) : ∑ i ∈ Finset.range n, pdiff (θ i + δ i) (θ (i + 1) + δ (i + 1)) = ∑ i ∈ Finset.range n, pdiff (θ i) (θ (i + 1))`
- `theorem loop_sum_stable_of_small`: `theorem loop_sum_stable_of_small (θ δ : ℕ → ℝ) (n : ℕ) (ε : ℝ) (hδ : δ n = δ 0) (hsmall : ∀ i ≤ n, |δ i| < ε) (hedge : ∀ i < n, |pdiff (θ i) (θ (i + 1))| < π - 2 * ε) : ∑ i ∈ Finset.range n, pdiff (θ i + δ i) (θ (i + 1) + δ (i + 1)) = ∑ i ∈ Finset.range n, pdiff (θ i) (θ (i + 1))`
- `theorem circulation_conserved`: `theorem circulation_conserved (hbar m : ℝ) (θ δ : ℕ → ℝ) (n : ℕ) (hδ : δ n = δ 0) (h : ∀ i < n, pdiff (θ i) (θ (i + 1)) + (δ (i + 1) - δ i) ∈ Set.Ioc (-π) π) : Circulation.circulation hbar m (fun i => θ i + δ i) n = Circulation.circulation hbar m θ n`
- `theorem continuousAt_pdiff`: `theorem continuousAt_pdiff {a b : ℝ} (h : pdiff a b ≠ π) : ContinuousAt (fun p : ℝ × ℝ => pdiff p.1 p.2) (a, b)`
- `def loopSum`: `noncomputable def loopSum (θ : ℝ → ℕ → ℝ) (n : ℕ) (t : ℝ) : ℝ`
- `theorem loop_sum_const_of_no_slip`: `theorem loop_sum_const_of_no_slip (θ : ℝ → ℕ → ℝ) (n : ℕ) {t₀ t₁ : ℝ} (ht : t₀ ≤ t₁) (hcont : ∀ i ≤ n, Continuous (fun t => θ t i)) (hclosed : ∀ t, θ t n = θ t 0) (hslip : ∀ t ∈ Set.Icc t₀ t₁, ∀ i < n, pdiff (θ t i) (θ t (i + 1)) ≠ π) : loopSum θ n t₁ = loopSum θ n t₀`
- `theorem slip_of_winding_change`: `theorem slip_of_winding_change (θ : ℝ → ℕ → ℝ) (n : ℕ) {t₀ t₁ : ℝ} (ht : t₀ ≤ t₁) (hcont : ∀ i ≤ n, Continuous (fun t => θ t i)) (hclosed : ∀ t, θ t n = θ t 0) (hchange : loopSum θ n t₁ ≠ loopSum θ n t₀) : ∃ t ∈ Set.Icc t₀ t₁, ∃ i < n, pdiff (θ t i) (θ t (i + 1)) = π`
- `def xyEnergy`: `noncomputable def xyEnergy (J : ℝ) (θ : ℕ → ℝ) (n : ℕ) : ℝ`
- `theorem cos_pdiff`: `theorem cos_pdiff (a b : ℝ) : Real.cos (pdiff a b) = Real.cos (b - a)`
- `theorem slip_energy_ge`: `theorem slip_energy_ge (J : ℝ) (hJ : 0 ≤ J) (θ : ℕ → ℝ) (n j : ℕ) (hj : j < n) (hπ : pdiff (θ j) (θ (j + 1)) = π) : -((n : ℝ) - 2) * J ≤ xyEnergy J θ n`
- `theorem mountain_pass`: `theorem mountain_pass (J : ℝ) (hJ : 0 ≤ J) (θ : ℝ → ℕ → ℝ) (n : ℕ) {t₀ t₁ : ℝ} (ht : t₀ ≤ t₁) (hcont : ∀ i ≤ n, Continuous (fun t => θ t i)) (hclosed : ∀ t, θ t n = θ t 0) (hchange : loopSum θ n t₁ ≠ loopSum θ n t₀) : ∃ t ∈ Set.Icc t₀ t₁, -((n : ℝ) - 2) * J ≤ xyEnergy J (θ t) n`
- `theorem twisted_loopSum`: `theorem twisted_loopSum (n : ℕ) (hn : 2 ≤ n) : ∑ i ∈ Finset.range n, pdiff (2 * π * i / n) (2 * π * (i + 1 : ℕ) / n) = 2 * π`
- `theorem twisted_energy`: `theorem twisted_energy (J : ℝ) (n : ℕ) : xyEnergy J (fun i => 2 * π * i / n) n = -(n : ℝ) * J * Real.cos (2 * π / n)`
- `theorem barrier_pos`: `theorem barrier_pos (J : ℝ) (hJ : 0 < J) (n : ℕ) (hn : 10 ≤ n) : xyEnergy J (fun i => 2 * π * i / n) n < -((n : ℝ) - 2) * J`

## Villani

```
Villani.lean -- a foundation for formalizing Cédric Villani's work, offered as a tribute.

  * `card_sq_ge` -- **Ollivier and Villani, "A curved Brunn-Minkowski inequality on the discrete
    hypercube", arXiv:1011.4779, Theorem 1, the K = 0 case.** For nonempty A, B in the Hamming cube
    {0,1}^N with midpoint set M, `#A * #B ≤ (#M)^2`. FULLY PROVED, no `sorry`, by the injection
    A×B ↪ M×M the paper's Section 3 describes: a canonical choice of which half of the differing
    coordinates of a pair (a,b) comes from `a`, together with the complementary choice, is
    recoverable from the resulting pair of midpoints.

  * The full Theorem 1, with the curvature term K = 1/(2N), is NOT attempted: its proof needs
    concentration of measure in the symmetric group (the paper's Lemma 4 and Proposition 5, via a
    quotienting argument), machinery not built here. See
    `docs/designs/ZERO_SOUND_LANDAU_DAMPING_PROPOSAL.md` §7 for the open-target list this belongs to.

  * `klDiv_nonincreasing_to_invariant` -- a three-line corollary of Mathlib's own
    `MeasureTheory.klDiv_comp_right_le` (the Data Processing Inequality for a Markov kernel), for a
    measure invariant under that kernel: the modern relative-entropy form of Boltzmann's H-theorem
    for a Markov chain. NOT presented as a contribution -- the mathematical content is entirely
    Mathlib's `klDiv_comp_right_le`. Included because it is the discrete skeleton of the entropy
    methods Villani surveys in "H-theorem and beyond" (Boltzmann's Legacy, EMS 2008), and it connects
    this file to `ZeroSound.lean`'s Fermi-liquid kinetic theory inside one project.

  Not attempted: the continuous collisional Boltzmann H-theorem, hypocoercivity, log-Sobolev and
  Talagrand inequalities, the Lott-Villani-Sturm curvature-dimension condition, and Landau damping
  (linear: see `ZeroSound.lean`; nonlinear: formalized, sorry-free, by J. Bedrossian,
  arXiv:2609.16801, which this file does not duplicate).
```

- `abbrev Cube`: `abbrev Cube (N : ℕ)`
- `def diff`: `def diff (a b : Cube N) : Finset (Fin N)`
- `def dist`: `def dist (a b : Cube N) : ℕ`
- `theorem mem_diff_iff`: `theorem mem_diff_iff {a b : Cube N} {i : Fin N} : i ∈ diff a b ↔ a i ≠ b i`
- `def IsMidpoint`: `def IsMidpoint (a b m : Cube N) : Prop`
- `def midpointSet`: `noncomputable def midpointSet (A B : Finset (Cube N)) : Finset (Cube N)`
- `def crossover`: `def crossover (c : Finset (Fin N)) (a b : Cube N) : Cube N`
- `theorem crossover_apply_mem`: `@[simp] theorem crossover_apply_mem {c : Finset (Fin N)} {a b : Cube N} {i : Fin N} (h : i ∈ c) : crossover c a b i = a i`
- `theorem crossover_apply_not_mem`: `@[simp] theorem crossover_apply_not_mem {c : Finset (Fin N)} {a b : Cube N} {i : Fin N} (h : i ∉ c) : crossover c a b i = b i`
- `theorem diff_crossover_left`: `theorem diff_crossover_left (c : Finset (Fin N)) (a b : Cube N) : diff (crossover c a b) a = diff a b \ c`
- `theorem diff_crossover_right`: `theorem diff_crossover_right {c : Finset (Fin N)} {a b : Cube N} (hc : c ⊆ diff a b) : diff (crossover c a b) b = c`
- `theorem dist_crossover_left`: `theorem dist_crossover_left (c : Finset (Fin N)) (a b : Cube N) : dist (crossover c a b) a = (diff a b \ c).card`
- `theorem dist_crossover_right`: `theorem dist_crossover_right {c : Finset (Fin N)} {a b : Cube N} (hc : c ⊆ diff a b) : dist (crossover c a b) b = c.card`
- `theorem isMidpoint_crossover`: `theorem isMidpoint_crossover {c : Finset (Fin N)} {a b : Cube N} (hc : c ⊆ diff a b) (h1 : 2 * c.card ≤ dist a b + 1) (h2 : dist a b ≤ 2 * c.card + 1) : IsMidpoint a b (crossover c a b)`
- `def takeHalf`: `def takeHalf (s : Finset (Fin N)) : Finset (Fin N)`
- `theorem takeHalf_subset`: `theorem takeHalf_subset (s : Finset (Fin N)) : takeHalf s ⊆ s`
- `theorem card_takeHalf`: `theorem card_takeHalf (s : Finset (Fin N)) : (takeHalf s).card = s.card / 2`
- `theorem takeHalf_card_bounds`: `theorem takeHalf_card_bounds (a b : Cube N) : 2 * (takeHalf (diff a b)).card ≤ dist a b + 1 ∧ dist a b ≤ 2 * (takeHalf (diff a b)).card + 1`
- `def encode`: `def encode (a b : Cube N) : Cube N × Cube N`
- `theorem encode_fst_isMidpoint`: `theorem encode_fst_isMidpoint (a b : Cube N) : IsMidpoint a b (encode a b).1`
- `theorem encode_snd_isMidpoint`: `theorem encode_snd_isMidpoint (a b : Cube N) : IsMidpoint a b (encode a b).2`
- `theorem encode_mem_midpointSet`: `theorem encode_mem_midpointSet {A B : Finset (Cube N)} {a b : Cube N} (ha : a ∈ A) (hb : b ∈ B) : (encode a b).1 ∈ midpointSet A B ∧ (encode a b).2 ∈ midpointSet A B`
- `theorem diff_crossover_crossover_compl`: `theorem diff_crossover_crossover_compl {c : Finset (Fin N)} {a b : Cube N} (hc : c ⊆ diff a b) : diff (crossover c a b) (crossover (diff a b \ c) a b) = diff a b`
- `theorem encode_injective`: `theorem encode_injective {a b a' b' : Cube N} (h : encode a b = encode a' b') : a = a' ∧ b = b'`
- `theorem card_sq_ge`: `theorem card_sq_ge (A B : Finset (Cube N)) : A.card * B.card ≤ (midpointSet A B).card * (midpointSet A B).card`
- `theorem klDiv_nonincreasing_to_invariant`: `theorem klDiv_nonincreasing_to_invariant (κ : Kernel 𝓧 𝓧) [IsMarkovKernel κ] (μ ν : Measure 𝓧) [IsFiniteMeasure μ] [IsFiniteMeasure ν] (hν : κ ∘ₘ ν = ν) : klDiv (κ ∘ₘ μ) ν ≤ klDiv μ ν`

## VortexWinding

```
Correctness of phase-winding vortex detection.

Every Gross-Pitaevskii / BEC simulation code that locates quantized vortices does so by summing
principal-branch phase differences around a small closed loop and rounding to a multiple of `2π`.
This module proves the two facts that algorithm rests on, and — more usefully — states the EXACT
condition under which it fails.

This is infrastructure, not a result. It is the correctness proof for the extractor in
`src/quantumfluids/tda/vortex_persistence.py`, whose docstring currently asserts these facts in
prose ("exact for a field resolved well enough that no true phase step exceeds pi"), and it applies
unchanged to any other code using the same standard method.

WHAT IS PROVED
  * `pdiff_sub_mem`        : the principal difference equals the true difference up to `2π ℤ`;
  * `loop_sum_eq_zsmul`    : around a CLOSED loop the sum of principal differences is exactly an
                             integer multiple of `2π` -- so "the winding number is an integer" is a
                             theorem, not a numerical accident;
  * `pdiff_antisymm`       : traversing an edge in the opposite direction negates the contribution,
                             PROVIDED the phase difference is not exactly `π`;
  * `pdiff_add_pdiff_pi`   : and when it IS exactly `π`, the two contributions sum to `2π`, not `0`.
                             This is the precise failure mode of the standard algorithm: at that
                             single phase difference, edge cancellation between neighbouring
                             plaquettes breaks and a spurious winding can appear.

WHAT IS NOT PROVED: that a given field is resolved well enough for the detected winding to equal the
true topological charge of the continuum field. That is a statement about sampling, not about the
algorithm, and it is exactly what the resolution controls in the design memo test empirically.
```

- `theorem two_pi_pos`: `theorem two_pi_pos : (0 : ℝ) < 2 * π`
- `def pdiff`: `noncomputable def pdiff (a b : ℝ) : ℝ`
- `theorem pdiff_mem`: `theorem pdiff_mem (a b : ℝ) : pdiff a b ∈ Set.Ioc (-π) π`
- `theorem pdiff_eq`: `theorem pdiff_eq (a b : ℝ) : pdiff a b = (b - a) - (toIocDiv two_pi_pos (-π) (b - a)) • (2 * π)`
- `theorem loop_sum_eq_mul`: `theorem loop_sum_eq_mul (θ : ℕ → ℝ) (n : ℕ) (hclosed : θ n = θ 0) : ∃ m : ℤ, ∑ i ∈ Finset.range n, pdiff (θ i) (θ (i + 1)) = (m : ℝ) * (2 * π)`
- `theorem pdiff_add_rev_eq`: `theorem pdiff_add_rev_eq (a b : ℝ) : ∃ m : ℤ, pdiff a b + pdiff b a = (m : ℝ) * (2 * π)`
- `theorem pdiff_add_rev`: `theorem pdiff_add_rev (a b : ℝ) : pdiff a b + pdiff b a = 0 ∨ pdiff a b + pdiff b a = 2 * π`
- `theorem pdiff_add_rev_eq_two_pi_iff`: `theorem pdiff_add_rev_eq_two_pi_iff (a b : ℝ) : pdiff a b + pdiff b a = 2 * π ↔ (pdiff a b = π ∧ pdiff b a = π)`
- `structure Balanced`: `structure Balanced {n : ℕ} (u v : Fin n → ℝ)`
- `theorem balanced_sum_eq_zero`: `theorem balanced_sum_eq_zero {n : ℕ} {u v : Fin n → ℝ} (B : Balanced u v) (hcut : ∀ i, pdiff (u i) (v i) + pdiff (v i) (u i) = 0) : ∑ i : Fin n, pdiff (u i) (v i) = 0`
- `theorem cut_free_of_ne_pi`: `theorem cut_free_of_ne_pi {a b : ℝ} (h : pdiff a b ≠ π) : pdiff a b + pdiff b a = 0`

## WassersteinCertificate

```
WassersteinCertificate.lean -- P6 of the closed-loop project
  (docs/designs/CLOSED_LOOP_PREREG.md, docs/designs/CLOSED_LOOP_RESULTS.md).

  The certificate used in `exploration/tda/loop_certificate_*.py`: a perfect matching `σ` (an explicit
  bijection between an "augmented" row set and column set -- real diagram points plus, on each side, one
  dedicated diagonal-projection slot per point on the OTHER side, exactly the construction in
  `docs/designs/CLOSED_LOOP_PLAN.md` §1.4 and its Python recipe) together with dual potentials `u, v`
  satisfying the feasibility inequalities `u i + v j ≤ C i j` everywhere. This is finite linear-
  programming weak duality -- general over ANY cost matrix and ANY finite index types, S-difficulty --
  and it is exactly what makes such a certificate valid: if `σ`'s cost equals `Σu + Σv`, `σ` is provably
  an optimal (minimum-cost) matching, no search over the other `(n+m)!` matchings required.

  Applied here to the eight-point-cycle toy example (`CLOSED_LOOP_PREREG.md`'s C1, hand-verified there,
  machine-verified in `exploration/tda/loop_controls.py`, and now machine-CHECKED at the kernel level
  here): `card_toy_certificate` proves the found matching is optimal, at cost exactly `7/4`. The negative
  control instantiates the broken potential from C3 (`ψ_{c'} = 1/2` instead of `1/4`) and shows it is NOT
  feasible, so it certifies nothing.

  NOT covered: the seven real Gross-Pitaevskii persistence-diagram pairs of `CLOSED_LOOP_RESULTS.md` use
  60×60 floating-point cost matrices built from real simulation data. Re-verifying those specific
  matrices inside the Lean kernel is not attempted here (their optimality was independently confirmed in
  Python by two solvers, `scipy.optimize.linear_sum_assignment` and `scipy.optimize.linprog`, agreeing to
  machine precision -- see that file). What is proved here is the general theorem that makes any such
  certificate valid in principle, checked on the one instance small and exact enough to write down by
  hand and decide in the kernel.
```

- `theorem weak_duality`: `theorem weak_duality (C : ι → κ → ℝ) (u : ι → ℝ) (v : κ → ℝ) (hfeas : ∀ i j, u i + v j ≤ C i j) (σ : ι ≃ κ) : ∑ i, u i + ∑ j, v j ≤ ∑ i, C i (σ i)`
- `theorem certificate`: `theorem certificate (C : ι → κ → ℝ) (u : ι → ℝ) (v : κ → ℝ) (hfeas : ∀ i j, u i + v j ≤ C i j) (σ : ι ≃ κ) (htight : ∑ i, C i (σ i) = ∑ i, u i + ∑ j, v j) (τ : ι ≃ κ) : ∑ i, C i (σ i) ≤ ∑ i, C i (τ i)`
- `def C`: `noncomputable def C : Fin 6 → Fin 6 → ℝ`
- `theorem C_eq`: `theorem C_eq (i j : Fin 6) : C i j = ![![0, 1, 2, 3/2, 1000, 1000], ![1, 0, 3/2, 1000, 3/2, 1000], ![2, 1, 5/2, 1000, 1000, 3/2], ![3/2, 1000, 1000, 0, 0, 0], ![1000, 3/2, 1000, 0, 0, 0], ![1000, 1000, 1/4, 0, 0, 0]] i j`
- `def u`: `noncomputable def u : Fin 6 → ℝ`
- `def v`: `noncomputable def v : Fin 6 → ℝ`
- `def σfun`: `def σfun : Fin 6 → Fin 6`
- `def σ`: `noncomputable def σ : Fin 6 ≃ Fin 6`
- `theorem feasible`: `theorem feasible : ∀ i j, u i + v j ≤ C i j`
- `theorem tight`: `theorem tight : ∑ i, C i (σ i) = ∑ i, u i + ∑ j, v j`
- `theorem toy_certificate`: `theorem toy_certificate (τ : Fin 6 ≃ Fin 6) : ∑ i, C i (σ i) ≤ ∑ i, C i (τ i)`
- `theorem toy_cost_eq`: `theorem toy_cost_eq : ∑ i, C i (σ i) = 7 / 4`
- `def v_broken`: `noncomputable def v_broken : Fin 6 → ℝ`
- `theorem broken_infeasible`: `theorem broken_infeasible : ¬ (∀ i j, u i + v_broken j ≤ C i j)`

## ZeroSound

```
ZeroSound.lean -- when does a Fermi liquid support undamped zero sound?

  Landau's collisionless kinetic equation for a Fermi liquid with a single Landau parameter `F` (= F₀ˢ)
  has a collective mode of phase velocity `s · v_F` when  `1 + F · Ω(s) = 0`, with Ω the angular average
  of the free response.  The mode is undamped iff `s > 1` (outside the particle-hole continuum); for
  `s < 1` it is Landau-damped -- the same mechanism as in a plasma, with `F` in place of `1/k²`.

  * 3D (bulk ³He):      Ω(s) = 1 - (s/2) log((s+1)/(s-1)),  condition  (s/2) log((s+1)/(s-1)) - 1 = 1/F.
  * 2D (³He monolayer): Ω(s) = 1 - s/√(s²-1).

  PROVED: in both dimensions an undamped root `s > 1` exists **iff** `F > 0`; in 2D the root is explicit,
  `s = (1+F)/√(1+2F)`.  This is textbook physics (Baym & Pethick, *Landau Fermi-Liquid Theory*); what is
  new is only that it is machine-checked.  The 2D case is included because the neutron-scattering
  measurement of a zero-sound-like mode by Godfrin et al., Nature 483, 576 (2012), is on a 2D film, where
  the logarithmic 3D formula does not apply.

  NOT proved: uniqueness of the 3D root (needs strict monotonicity); anything about `F₁ˢ`, finite
  temperature, or the damped branch `s < 1`.
```

- `def g3`: `noncomputable def g3 (s : ℝ) : ℝ`
- `theorem g3_pos`: `theorem g3_pos {s : ℝ} (hs : 1 < s) : 0 < g3 s`
- `theorem g3_le`: `theorem g3_le {s : ℝ} (hs : 1 < s) : g3 s ≤ 1 / (s - 1)`
- `theorem g3_ge`: `theorem g3_ge {s : ℝ} (hs : 1 < s) : 1 / 2 * log (2 / (s - 1)) - 1 ≤ g3 s`
- `theorem continuousOn_g3`: `theorem continuousOn_g3 {a b : ℝ} (ha : 1 < a) : ContinuousOn g3 (Icc a b)`
- `theorem zero_sound_iff`: `theorem zero_sound_iff (F : ℝ) : (∃ s, 1 < s ∧ g3 s = 1 / F) ↔ 0 < F`
- `theorem zero_sound_2d_iff`: `theorem zero_sound_2d_iff (F : ℝ) : (∃ s, 1 < s ∧ 1 + F * (1 - s / √(s ^ 2 - 1)) = 0) ↔ 0 < F`
