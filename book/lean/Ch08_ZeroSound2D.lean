/-
Ch08_ZeroSound2D.lean -- NEW for the book "Quantum Fluids in Lean 4: a tribute to Henri Godfrin", chapter 8.

Three small additions around `ZeroSound.lean` (which proves: an undamped zero-sound root exists iff the Landau
parameter F is positive, in 2D and 3D, with the explicit 2D root s = (1+F)/sqrt(1+2F)).  Everything here is
elementary; the point is that it is machine-checked and that each statement is the mathematical core of a sentence
used in the chapter.

  1. Free-fermion kinematics (any real inner-product space, so 2D and 3D at once; hbar = 1).
       `ph_energy_window`   a particle-hole pair created at momentum transfer q out of a Fermi sea of radius kF
                            carries an energy in  [ (q^2 - 2 kF q)/(2m) , (q^2 + 2 kF q)/(2m) ];
       `ph_gap`             for q > 2 kF the lower edge is strictly positive: the continuum has a gap;
       `ph_edge_attained`   for q >= 2 kF the lower edge is attained by an actual particle-hole pair.
     This is the mathematics behind the number "twice the Fermi momentum" in the abstract of Godfrin et al.,
     Nature 483, 576 (2012).  It is a statement about the FREE Fermi gas, not about the helium film.
  2. `zero_sound_2d_unique`   the 2D root of 1 + F * Omega2(s) = 0 with s > 1 is unique (and F > 0): it is s0 F.
  3. `omega2_hasDerivAt`, `pole_weight`, `pole_fraction`
     The weight of the zero-sound pole in the density response is 1/(F^2 Omega2'(s0)) = F/(1+2F)^(3/2); four times
     s0 times this weight equals 1 - 1/(1+2F)^2.  (That this weight is the delta-function strength in the dynamic
     structure factor, and that the total first moment is 1/4 in the units of the chapter, are textbook residue and
     f-sum-rule statements that are NOT formalised here; only the algebra of the closed forms is.)

No `sorry`; standard axioms only (see the `#print axioms` lines at the end).
-/
import Mathlib

open Real

namespace QuantumFluids.ZeroSound2D

/-! ## 1. The particle-hole window of a free Fermi gas -/

/-- **Particle-hole window.**  For a hole momentum `k` inside the Fermi sphere (`‖k‖ ≤ kF`) and a momentum
transfer `q`, the transferred energy `(‖k+q‖² - ‖k‖²)/(2m)` lies between `(‖q‖² - 2 kF ‖q‖)/(2m)` and
`(‖q‖² + 2 kF ‖q‖)/(2m)`.  (Cauchy-Schwarz: `|⟪k,q⟫| ≤ kF ‖q‖`.) -/
theorem ph_energy_window {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    {m kF : ℝ} (hm : 0 < m) (k q : E) (hk : ‖k‖ ≤ kF) :
    (‖q‖ ^ 2 - 2 * kF * ‖q‖) / (2 * m) ≤ (‖k + q‖ ^ 2 - ‖k‖ ^ 2) / (2 * m) ∧
      (‖k + q‖ ^ 2 - ‖k‖ ^ 2) / (2 * m) ≤ (‖q‖ ^ 2 + 2 * kF * ‖q‖) / (2 * m) := by
  have h1 : ‖k + q‖ ^ 2 = ‖k‖ ^ 2 + 2 * inner ℝ k q + ‖q‖ ^ 2 := norm_add_sq_real k q
  have h2 : |inner ℝ k q| ≤ ‖k‖ * ‖q‖ := abs_real_inner_le_norm k q
  have h3 : ‖k‖ * ‖q‖ ≤ kF * ‖q‖ := mul_le_mul_of_nonneg_right hk (norm_nonneg q)
  obtain ⟨h4, h5⟩ := abs_le.mp h2
  have hm2 : 0 < 2 * m := by positivity
  constructor
  · have h : ‖q‖ ^ 2 - 2 * kF * ‖q‖ ≤ ‖k + q‖ ^ 2 - ‖k‖ ^ 2 := by nlinarith
    exact div_le_div_of_nonneg_right h hm2.le
  · have h : ‖k + q‖ ^ 2 - ‖k‖ ^ 2 ≤ ‖q‖ ^ 2 + 2 * kF * ‖q‖ := by nlinarith
    exact div_le_div_of_nonneg_right h hm2.le

/-- **The gap above `2 kF`.**  If `‖q‖ > 2 kF` then every particle-hole pair at momentum transfer `q` has
strictly positive energy, at least `‖q‖ (‖q‖ - 2 kF) / (2m)`. -/
theorem ph_gap {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    {m kF : ℝ} (hm : 0 < m) (hkF : 0 ≤ kF) (k q : E) (hk : ‖k‖ ≤ kF) (hq : 2 * kF < ‖q‖) :
    0 < ‖q‖ * (‖q‖ - 2 * kF) / (2 * m) ∧
      ‖q‖ * (‖q‖ - 2 * kF) / (2 * m) ≤ (‖k + q‖ ^ 2 - ‖k‖ ^ 2) / (2 * m) := by
  have hqpos : 0 < ‖q‖ := by linarith
  have hm2 : 0 < 2 * m := by positivity
  refine ⟨by positivity, ?_⟩
  have hw := (ph_energy_window hm k q hk).1
  have e : ‖q‖ * (‖q‖ - 2 * kF) = ‖q‖ ^ 2 - 2 * kF * ‖q‖ := by ring
  rw [e]
  exact hw

/-- **The lower edge is attained.**  For `‖q‖ ≥ 2 kF` (and `q ≠ 0`) the hole `k = -(kF/‖q‖) q` lies on the Fermi
sphere, the particle `k + q` lies outside or on it, and the transferred energy equals the lower edge. -/
theorem ph_edge_attained {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    {kF : ℝ} (hkF : 0 ≤ kF) (q : E) (hq0 : q ≠ 0) (hq : 2 * kF ≤ ‖q‖) :
    ∃ k : E, ‖k‖ = kF ∧ kF ≤ ‖k + q‖ ∧ ‖k + q‖ ^ 2 - ‖k‖ ^ 2 = ‖q‖ ^ 2 - 2 * kF * ‖q‖ := by
  have hqpos : 0 < ‖q‖ := norm_pos_iff.mpr hq0
  have hc : 0 ≤ kF / ‖q‖ := by positivity
  have hkq : ‖-(kF / ‖q‖) • q‖ = kF := by
    rw [norm_smul, norm_neg, Real.norm_of_nonneg hc]
    field_simp
  have hsum : -(kF / ‖q‖) • q + q = (1 - kF / ‖q‖) • q := by
    rw [sub_smul, one_smul, neg_smul]
    abel
  have hnorm : ‖-(kF / ‖q‖) • q + q‖ = ‖q‖ - kF := by
    rw [hsum, norm_smul, Real.norm_eq_abs]
    have h1 : 0 ≤ 1 - kF / ‖q‖ := by
      rw [sub_nonneg, div_le_one hqpos]; linarith
    rw [abs_of_nonneg h1]
    field_simp
  refine ⟨-(kF / ‖q‖) • q, hkq, ?_, ?_⟩
  · rw [hnorm]; linarith
  · rw [hnorm, hkq]; ring

/-! ## 2. Uniqueness of the 2D zero-sound root -/

/-- The 2D free response above the continuum (`s > 1`), as in `ZeroSound.lean`: `Ω₂(s) = 1 - s/√(s²-1)`. -/
noncomputable def omega2 (s : ℝ) : ℝ := 1 - s / √(s ^ 2 - 1)

/-- The explicit 2D root `s₀(F) = (1+F)/√(1+2F)`. -/
noncomputable def s0 (F : ℝ) : ℝ := (1 + F) / √(1 + 2 * F)

/-- **The 2D zero-sound root is unique.**  Any `s > 1` with `1 + F Ω₂(s) = 0` has `F > 0` and equals `s₀ F`.
Together with `QuantumFluids.ZeroSound.zero_sound_2d_iff` (existence iff `F > 0`) this says: for `F > 0` there is
exactly one undamped zero-sound root, for `F ≤ 0` there is none. -/
theorem zero_sound_2d_unique {F s : ℝ} (hs : 1 < s) (h : 1 + F * omega2 s = 0) :
    0 < F ∧ s = s0 F := by
  have hpos : 0 < s ^ 2 - 1 := by nlinarith
  have hr : 0 < √(s ^ 2 - 1) := Real.sqrt_pos.mpr hpos
  have hr2 : √(s ^ 2 - 1) ^ 2 = s ^ 2 - 1 := Real.sq_sqrt hpos.le
  have hlt : √(s ^ 2 - 1) < s := by nlinarith
  have hratio : 1 < s / √(s ^ 2 - 1) := by rw [lt_div_iff₀ hr]; linarith
  have hω : omega2 s < 0 := by unfold omega2; linarith
  have hF : 0 < F := by
    by_contra hF
    rw [not_lt] at hF
    nlinarith [mul_nonneg_of_nonpos_of_nonpos hF hω.le]
  refine ⟨hF, ?_⟩
  -- from the equation:  F * s = (1 + F) * r
  have h1 : F * s = (1 + F) * √(s ^ 2 - 1) := by
    unfold omega2 at h
    field_simp at h
    linarith
  have h1sq : (F * s) ^ 2 = ((1 + F) * √(s ^ 2 - 1)) ^ 2 := by rw [h1]
  rw [mul_pow, mul_pow, hr2] at h1sq
  have h2 : s ^ 2 * (1 + 2 * F) = (1 + F) ^ 2 := by linear_combination (-1 : ℝ) * h1sq
  have hq0 : 0 < 1 + 2 * F := by linarith
  have hq : 0 < √(1 + 2 * F) := Real.sqrt_pos.mpr hq0
  have hq2 : √(1 + 2 * F) ^ 2 = 1 + 2 * F := Real.sq_sqrt hq0.le
  unfold s0
  rw [eq_div_iff hq.ne']
  have h3 : (s * √(1 + 2 * F)) ^ 2 = (1 + F) ^ 2 := by rw [mul_pow, hq2]; exact h2
  exact (sq_eq_sq₀ (by positivity) (by linarith)).mp h3

/-- `s₀² - 1 = F²/(1+2F)`: the identity at the heart of the proof of `zero_sound_2d_iff`. -/
theorem s0_sq_sub_one {F : ℝ} (hF : 0 < F) : s0 F ^ 2 - 1 = F ^ 2 / (1 + 2 * F) := by
  have hq0 : 0 < 1 + 2 * F := by linarith
  have hq : 0 < √(1 + 2 * F) := Real.sqrt_pos.mpr hq0
  have hq2 : √(1 + 2 * F) ^ 2 = 1 + 2 * F := Real.sq_sqrt hq0.le
  unfold s0
  rw [div_pow, hq2]
  field_simp
  ring

/-- `s₀ > 1` for `F > 0`. -/
theorem one_lt_s0 {F : ℝ} (hF : 0 < F) : 1 < s0 F := by
  have hq0 : 0 < 1 + 2 * F := by linarith
  have hq : 0 < √(1 + 2 * F) := Real.sqrt_pos.mpr hq0
  unfold s0
  rw [lt_div_iff₀ hq, one_mul, Real.sqrt_lt' (by linarith)]
  nlinarith

/-! ## 3. The weight of the zero-sound pole -/

/-- The derivative of the 2D free response: `Ω₂'(s) = 1/((s²-1) √(s²-1))` for `s > 1`. -/
theorem omega2_hasDerivAt {s : ℝ} (hs : 1 < s) :
    HasDerivAt omega2 (1 / ((s ^ 2 - 1) * √(s ^ 2 - 1))) s := by
  have hpos : 0 < s ^ 2 - 1 := by nlinarith
  have hr : 0 < √(s ^ 2 - 1) := Real.sqrt_pos.mpr hpos
  have hr2 : √(s ^ 2 - 1) ^ 2 = s ^ 2 - 1 := Real.sq_sqrt hpos.le
  have h1 : HasDerivAt (fun x : ℝ => x ^ 2 - 1) (2 * s) s := by
    have := (hasDerivAt_pow 2 s).sub_const 1
    simpa using this
  have h2 : HasDerivAt (fun x : ℝ => √(x ^ 2 - 1)) (2 * s / (2 * √(s ^ 2 - 1))) s :=
    h1.sqrt hpos.ne'
  have h3 := ((hasDerivAt_id' s).div h2 hr.ne').const_sub 1
  have e : 1 / ((s ^ 2 - 1) * √(s ^ 2 - 1)) =
      -((1 * √(s ^ 2 - 1) - s * (2 * s / (2 * √(s ^ 2 - 1)))) / √(s ^ 2 - 1) ^ 2) := by
    rw [hr2]
    field_simp
    nlinarith [hr2]
  unfold omega2
  rw [e]
  exact h3

/-- **Pole weight.**  With `s₀ = s0 F` the root, the residue weight `1/(F² Ω₂'(s₀))` equals
`F / ((1+2F) √(1+2F))`, i.e. `F/(1+2F)^(3/2)`. -/
theorem pole_weight {F : ℝ} (hF : 0 < F) :
    1 / (F ^ 2 * deriv omega2 (s0 F)) = F / ((1 + 2 * F) * √(1 + 2 * F)) := by
  have hs := one_lt_s0 hF
  rw [(omega2_hasDerivAt hs).deriv, s0_sq_sub_one hF]
  have hq0 : 0 < 1 + 2 * F := by linarith
  have hq : 0 < √(1 + 2 * F) := Real.sqrt_pos.mpr hq0
  have hq2 : √(1 + 2 * F) ^ 2 = 1 + 2 * F := Real.sq_sqrt hq0.le
  have hsq : √(F ^ 2 / (1 + 2 * F)) = F / √(1 + 2 * F) := by
    rw [Real.sqrt_div (by positivity), Real.sqrt_sq hF.le]
  rw [hsq]
  field_simp

/-- **The pole carries the fraction `1 - 1/(1+2F)²` of the first moment.**  In the chapter's units the total
first moment (f-sum rule) is `1/4` and the pole contributes `s₀ · weight`; this is the algebraic identity
`4 s₀ / (F² Ω₂'(s₀)) = 1 - 1/(1+2F)²`.  It tends to `1` as `F → ∞` and to `0` like `4F` as `F → 0⁺`. -/
theorem pole_fraction {F : ℝ} (hF : 0 < F) :
    4 * s0 F * (1 / (F ^ 2 * deriv omega2 (s0 F))) = 1 - 1 / (1 + 2 * F) ^ 2 := by
  rw [pole_weight hF]
  have hq0 : 0 < 1 + 2 * F := by linarith
  have hq : 0 < √(1 + 2 * F) := Real.sqrt_pos.mpr hq0
  have hqq : √(1 + 2 * F) * √(1 + 2 * F) = 1 + 2 * F := Real.mul_self_sqrt hq0.le
  unfold s0
  have e : 4 * ((1 + F) / √(1 + 2 * F)) * (F / ((1 + 2 * F) * √(1 + 2 * F))) =
      4 * (1 + F) * F / ((1 + 2 * F) * (√(1 + 2 * F) * √(1 + 2 * F))) := by
    field_simp
  rw [e, hqq]
  field_simp
  ring

end QuantumFluids.ZeroSound2D

#print axioms QuantumFluids.ZeroSound2D.ph_energy_window
#print axioms QuantumFluids.ZeroSound2D.ph_gap
#print axioms QuantumFluids.ZeroSound2D.ph_edge_attained
#print axioms QuantumFluids.ZeroSound2D.zero_sound_2d_unique
#print axioms QuantumFluids.ZeroSound2D.s0_sq_sub_one
#print axioms QuantumFluids.ZeroSound2D.one_lt_s0
#print axioms QuantumFluids.ZeroSound2D.omega2_hasDerivAt
#print axioms QuantumFluids.ZeroSound2D.pole_weight
#print axioms QuantumFluids.ZeroSound2D.pole_fraction
