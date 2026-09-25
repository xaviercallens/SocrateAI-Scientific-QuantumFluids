/-
  ChargeLattice.lean -- two cosmological charge lattices stated so that the kernel reads off the same
  distinction as `CompactBoson.lean`: the duality is a relabelling of the sectors; what the physics depends
  on is a function of the sector alone.

  Part 1 -- the dyon charge lattice of type II on K3 × T² (Moore, "Arithmetic and attractors", 1998).
  A dyon is a pair (p, q) of vectors in an integral lattice Λ with a symmetric ℤ-bilinear form B
  (for K3 × T², Λ = II_{3,19} ⊕ ... ; we keep Λ abstract). The S-duality SL(2, ℤ) acts on the pair by
  (p, q) ↦ (a p + b q, c p + d q). Moore's discriminant
      D(p, q) = B(p,q)² − B(p,p) B(q,q)
  is what the horizon area depends on: A/4π = √(−D) in the supergravity approximation, and
  log dim H_BPS = π √(−D) + ⋯. The attractor mechanism fixes the K3 complex structure from (p, q) alone
  (Ω ∝ q − τ̄ p, τ = (p·q + √D)/p²) -- the moduli are OUTPUTS of the sector.
  * `disc_sl2_invariant`: D(a p + b q, c p + d q) = (a d − b c)² D(p, q); with a d − b c = 1 the discriminant
    is invariant. The duality permutes charge vectors inside a level set of D; the entropy reads the level set.
    Moore's count of U-duality-inequivalent dyons at fixed D is the class number h(D): the level set is
    not a single orbit, so D is a coarser invariant than the orbit -- the same map, different sectors, same
    physics.
  * `disc_scale`: D(t p, t q) = t⁴ D(p, q) -- the charge-scaling that the Strominger–Vafa asymptotics uses.
  * `disc_zero_of_parallel`: D(p, k p) = 0 -- a dyon whose electric and magnetic charges are parallel has no
    horizon in this approximation (the "small black hole"); parallelism is a sector property.

  Part 2 -- the flux-sector lattice of the cosmological constant (Bousso–Polchinski 2000; Kaloper 2025).
  With J four-form fluxes of charges q_i and integer quanta n_i,
      Λ(n) = Λ_bare + ½ Σ_i n_i² q_i².
  A membrane nucleation lowers one n_i by 1 and Λ by (n_i − ½) q_i². Kaloper's single dark top form has
  V(N) = ½ X ((1 − N) θ̂)², minimised exactly at the CP-invariant sector N = 1.
  * `bp_step`: the exact change of Λ under one nucleation of flux i.
  * `bp_step_neg_iff`: it lowers Λ iff n_i ≥ 1 -- the discharge sequence is monotone while the quanta are
    positive, which is why the Brown–Teitelboim/Bousso–Polchinski random walk moves inward.
  * `bp_min_at_zero`: with all q_i ≠ 0, Λ(n) ≥ Λ(0) with equality iff n = 0 -- the bare value is the floor of
    the lattice; the observed value is selected on the lattice, not produced by the lattice.
  * `kaloper_step`, `kaloper_min`, `kaloper_terminates`: each nucleation lowers V by X θ̂² (θ_dark − ½ θ̂) with
    θ_dark = (1 − N) θ̂ ; V is minimised at N = 1 where it vanishes; starting from N ≤ 1, after exactly 1 − N
    nucleations V = 0 -- the "discretely evanescent" dark energy ends at the CP-invariant sector.

  What this module says, and only this: on both lattices the observable (entropy; vacuum energy) is a function of
  the integer sector; the duality (Part 1) reindexes the lattice and preserves the function; the dynamics
  (Part 2) is a walk on the lattice whose steps and end point are fixed by the sector. Nothing here is a
  cosmological number, nothing is a claim about K3 surfaces beyond the algebra of the charge form, and nothing
  transfers a coupling from a superfluid. Whether the universe's Λ or a black hole's entropy IS such a function
  is the physical hypothesis the cited papers make; the module states what follows if it is.
-/
import Mathlib

namespace QuantumFluids.ChargeLattice

/-! ### Part 1 -- the dyon charge lattice and Moore's discriminant -/

section Dyon

variable {Λ : Type*} [AddCommGroup Λ] (B : LinearMap.BilinForm ℤ Λ)

/-- Moore's discriminant of a dyon `(p, q)`: `D = B(p,q)² − B(p,p) B(q,q)`. The horizon area is `√(−D)`. -/
def disc (p q : Λ) : ℤ := B p q ^ 2 - B p p * B q q

/-- Bilinearity spelled out on the S-duality image `(a p + b q, c p + d q)` -- the four Gram entries. -/
theorem gram_pp (hB : B.IsSymm) (a b : ℤ) (p q : Λ) :
    B (a • p + b • q) (a • p + b • q) = a ^ 2 * B p p + 2 * a * b * B p q + b ^ 2 * B q q := by
  have hs : B q p = B p q := hB.eq q p
  simp only [map_add, map_smul, LinearMap.add_apply, LinearMap.smul_apply, smul_eq_mul, hs]
  ring

theorem gram_pq (hB : B.IsSymm) (a b c d : ℤ) (p q : Λ) :
    B (a • p + b • q) (c • p + d • q)
      = a * c * B p p + (a * d + b * c) * B p q + b * d * B q q := by
  have hs : B q p = B p q := hB.eq q p
  simp only [map_add, map_smul, LinearMap.add_apply, LinearMap.smul_apply, smul_eq_mul, hs]
  ring

/-- **The discriminant is an S-duality invariant.** Under `(p, q) ↦ (a p + b q, c p + d q)`,
`D ↦ (a d − b c)² D`; for `SL(2, ℤ)` the factor is `1`. The duality relabels the dyons; the quantity the
horizon area and the BPS asymptotics depend on does not move. -/
theorem disc_sl2 (hB : B.IsSymm) (a b c d : ℤ) (p q : Λ) :
    disc B (a • p + b • q) (c • p + d • q) = (a * d - b * c) ^ 2 * disc B p q := by
  unfold disc
  rw [gram_pq B hB, gram_pp B hB, gram_pp B hB]
  ring

theorem disc_sl2_invariant (hB : B.IsSymm) {a b c d : ℤ} (hdet : a * d - b * c = 1) (p q : Λ) :
    disc B (a • p + b • q) (c • p + d • q) = disc B p q := by
  rw [disc_sl2 B hB, hdet]; ring

/-- The exchange `(p, q) ↦ (q, −p)` (the element `S` of `SL(2, ℤ)`, electric ↔ magnetic) preserves `D`. -/
theorem disc_electric_magnetic_swap (hB : B.IsSymm) (p q : Λ) : disc B q (-p) = disc B p q := by
  have h := disc_sl2_invariant B hB (a := 0) (b := 1) (c := -1) (d := 0) (by norm_num) p q
  simpa using h

/-- Charge scaling: `D(t p, t q) = t⁴ D(p, q)` -- the large-charge asymptotics of Strominger–Vafa. -/
theorem disc_scale (hB : B.IsSymm) (t : ℤ) (p q : Λ) : disc B (t • p) (t • q) = t ^ 4 * disc B p q := by
  have h := disc_sl2 B hB t 0 0 t p q
  simp only [zero_smul, add_zero, zero_add] at h
  rw [h]; ring

/-- A dyon with parallel electric and magnetic charges has `D = 0`: no horizon area at this order. -/
theorem disc_zero_of_parallel (hB : B.IsSymm) (k : ℤ) (p : Λ) : disc B p (k • p) = 0 := by
  unfold disc
  have hs : B p (k • p) = k * B p p := by simp [map_smul]
  have hs' : B (k • p) (k • p) = k ^ 2 * B p p := by
    have := gram_pp B hB k 0 p p
    simpa using this
  rw [hs, hs']; ring

/-- Over the reals (the supergravity regime `−D > 0`) the horizon area `√(−D)` is the same for every dyon in
an `SL(2, ℤ)` orbit. -/
theorem area_sl2_invariant (hB : B.IsSymm) {a b c d : ℤ} (hdet : a * d - b * c = 1) (p q : Λ) :
    Real.sqrt (-(disc B (a • p + b • q) (c • p + d • q) : ℝ)) = Real.sqrt (-(disc B p q : ℝ)) := by
  rw [disc_sl2_invariant B hB hdet]

end Dyon

/-! ### Part 2 -- the flux-sector lattice of the vacuum energy -/

section Flux

/-- Bousso–Polchinski: `Λ(n) = Λ_bare + ½ Σ_i n_i² q_i²` over `J` four-form fluxes. -/
noncomputable def bpLambda {J : ℕ} (Λbare : ℝ) (q : Fin J → ℝ) (n : Fin J → ℤ) : ℝ :=
  Λbare + (1 / 2) * ∑ i, ((n i : ℝ) ^ 2 * q i ^ 2)

/-- One membrane nucleation of flux `i` lowers `n_i` by one and leaves the other quanta alone. -/
def nucleate {J : ℕ} (n : Fin J → ℤ) (i : Fin J) : Fin J → ℤ := Function.update n i (n i - 1)

/-- **The step**: `Λ(nucleate n i) − Λ(n) = −(n_i − ½) q_i²`. -/
theorem bp_step {J : ℕ} (Λbare : ℝ) (q : Fin J → ℝ) (n : Fin J → ℤ) (i : Fin J) :
    bpLambda Λbare q (nucleate n i) - bpLambda Λbare q n = -((n i : ℝ) - 1 / 2) * q i ^ 2 := by
  unfold bpLambda nucleate
  have hsum : ∑ j, (((Function.update n i (n i - 1)) j : ℝ) ^ 2 * q j ^ 2)
      = ∑ j, ((n j : ℝ) ^ 2 * q j ^ 2) + ((((n i : ℝ) - 1) ^ 2 - (n i : ℝ) ^ 2) * q i ^ 2) := by
    rw [← Finset.sum_erase_add _ _ (Finset.mem_univ i), ← Finset.sum_erase_add _ _ (Finset.mem_univ i)]
    have h1 : ∑ j ∈ Finset.univ.erase i, (((Function.update n i (n i - 1)) j : ℝ) ^ 2 * q j ^ 2)
        = ∑ j ∈ Finset.univ.erase i, ((n j : ℝ) ^ 2 * q j ^ 2) := by
      refine Finset.sum_congr rfl (fun j hj => ?_)
      rw [Function.update_of_ne (Finset.ne_of_mem_erase hj)]
    rw [h1, Function.update_self]
    push_cast
    ring
  rw [hsum]; ring

/-- The nucleation lowers `Λ` iff the flux quantum was positive. -/
theorem bp_step_neg_iff {J : ℕ} (Λbare : ℝ) (q : Fin J → ℝ) (n : Fin J → ℤ) (i : Fin J) (hq : q i ≠ 0) :
    bpLambda Λbare q (nucleate n i) < bpLambda Λbare q n ↔ 1 ≤ n i := by
  have hstep := bp_step Λbare q n i
  have hq2 : 0 < q i ^ 2 := by positivity
  constructor
  · intro h
    have : -((n i : ℝ) - 1 / 2) * q i ^ 2 < 0 := by linarith
    have hn : (1 / 2 : ℝ) < n i := by
      by_contra hc
      push Not at hc
      have : 0 ≤ -((n i : ℝ) - 1 / 2) * q i ^ 2 := by nlinarith
      linarith
    have : (0 : ℤ) < n i := by exact_mod_cast (show (0 : ℝ) < n i by linarith)
    omega
  · intro h
    have hn : (1 : ℝ) ≤ n i := by exact_mod_cast h
    have : -((n i : ℝ) - 1 / 2) * q i ^ 2 < 0 := by nlinarith
    linarith

/-- The bare value is the floor of the flux lattice: `Λ(n) ≥ Λ(0)`. -/
theorem bp_ge_bare {J : ℕ} (Λbare : ℝ) (q : Fin J → ℝ) (n : Fin J → ℤ) :
    bpLambda Λbare q 0 ≤ bpLambda Λbare q n := by
  unfold bpLambda
  have : (0 : ℝ) ≤ ∑ i, ((n i : ℝ) ^ 2 * q i ^ 2) := Finset.sum_nonneg (fun i _ => by positivity)
  simp only [Pi.zero_apply, Int.cast_zero, ne_eq, OfNat.ofNat_ne_zero, not_false_eq_true, zero_pow,
    zero_mul, Finset.sum_const_zero, mul_zero, add_zero]
  linarith

/-- With every charge non-zero, the floor is attained only at the zero sector. -/
theorem bp_min_at_zero {J : ℕ} (Λbare : ℝ) (q : Fin J → ℝ) (hq : ∀ i, q i ≠ 0) (n : Fin J → ℤ) :
    bpLambda Λbare q n = bpLambda Λbare q 0 ↔ n = 0 := by
  constructor
  · intro h
    unfold bpLambda at h
    simp only [Pi.zero_apply, Int.cast_zero, ne_eq, OfNat.ofNat_ne_zero, not_false_eq_true, zero_pow,
      zero_mul, Finset.sum_const_zero, mul_zero, add_zero] at h
    have hsum : ∑ i, ((n i : ℝ) ^ 2 * q i ^ 2) = 0 := by linarith
    have hterm := (Finset.sum_eq_zero_iff_of_nonneg (fun i _ => by positivity)).1 hsum
    funext i
    have hi := hterm i (Finset.mem_univ i)
    have hq2 : q i ^ 2 ≠ 0 := pow_ne_zero 2 (hq i)
    have : ((n i : ℝ)) ^ 2 = 0 := by
      rcases mul_eq_zero.1 hi with h1 | h1
      · exact h1
      · exact absurd h1 hq2
    have : (n i : ℝ) = 0 := pow_eq_zero_iff (n := 2) (by norm_num) |>.1 this
    exact_mod_cast this
  · rintro rfl; rfl

/-- Kaloper's dark top form: `V(N) = ½ X ((1 − N) θ̂)²`, the CP-violating phase in sector `N` being
`θ_dark = (1 − N) θ̂`. -/
noncomputable def kaloperV (X θ : ℝ) (N : ℤ) : ℝ := (1 / 2) * X * (((1 : ℝ) - N) * θ) ^ 2

/-- Each nucleation `N ↦ N + 1` lowers `V` by `X θ̂² (θ_dark − ½ θ̂)` with `θ_dark = (1 − N) θ̂`. -/
theorem kaloper_step (X θ : ℝ) (N : ℤ) :
    kaloperV X θ N - kaloperV X θ (N + 1) = X * θ ^ 2 * (((1 : ℝ) - N) - 1 / 2) := by
  unfold kaloperV; push_cast; ring

/-- `V ≥ 0`, and `V = 0` exactly at the CP-invariant sector `N = 1` (for `X θ̂² ≠ 0`). -/
theorem kaloper_min (X θ : ℝ) (hX : 0 < X) (hθ : θ ≠ 0) (N : ℤ) :
    0 ≤ kaloperV X θ N ∧ (kaloperV X θ N = 0 ↔ N = 1) := by
  unfold kaloperV
  refine ⟨by positivity, ?_⟩
  constructor
  · intro h
    have hX' : X ≠ 0 := ne_of_gt hX
    have : (((1 : ℝ) - N) * θ) ^ 2 = 0 := by
      rcases mul_eq_zero.1 h with h1 | h1
      · rcases mul_eq_zero.1 h1 with h2 | h2
        · norm_num at h2
        · exact absurd h2 hX'
      · exact h1
    have h0 : ((1 : ℝ) - N) * θ = 0 := pow_eq_zero_iff (n := 2) (by norm_num) |>.1 this
    rcases mul_eq_zero.1 h0 with h2 | h2
    · have : (N : ℝ) = 1 := by linarith
      exact_mod_cast this
    · exact absurd h2 hθ
  · rintro rfl; norm_num

/-- **The discharge terminates at the CP-invariant sector**: from `N ≤ 1`, after exactly `1 − N` nucleations
the dark energy is zero. -/
theorem kaloper_terminates (X θ : ℝ) (N : ℤ) (hN : N ≤ 1) :
    kaloperV X θ (N + ((1 - N).toNat : ℤ)) = 0 := by
  have h : ((1 - N).toNat : ℤ) = 1 - N := Int.toNat_of_nonneg (by omega)
  rw [h]
  unfold kaloperV
  have : N + (1 - N) = 1 := by ring
  rw [this]; norm_num

end Flux

end QuantumFluids.ChargeLattice

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.ChargeLattice.gram_pp
#print axioms QuantumFluids.ChargeLattice.gram_pq
#print axioms QuantumFluids.ChargeLattice.disc_sl2
#print axioms QuantumFluids.ChargeLattice.disc_sl2_invariant
#print axioms QuantumFluids.ChargeLattice.disc_electric_magnetic_swap
#print axioms QuantumFluids.ChargeLattice.disc_scale
#print axioms QuantumFluids.ChargeLattice.disc_zero_of_parallel
#print axioms QuantumFluids.ChargeLattice.area_sl2_invariant
#print axioms QuantumFluids.ChargeLattice.bp_step
#print axioms QuantumFluids.ChargeLattice.bp_step_neg_iff
#print axioms QuantumFluids.ChargeLattice.bp_ge_bare
#print axioms QuantumFluids.ChargeLattice.bp_min_at_zero
#print axioms QuantumFluids.ChargeLattice.kaloper_step
#print axioms QuantumFluids.ChargeLattice.kaloper_min
#print axioms QuantumFluids.ChargeLattice.kaloper_terminates
