/-
  Sol06_KTGeneralC.lean -- written for the solution of Exercise 1 of Chapter 6 (Appendix C of the book "Quantum Fluids in Lean 4").
  NEW: this module is NOT part of the QuantumFluids library; it is compiled against the same pinned Mathlib (Lean 4.34.0-rc2) and nothing else.

  The question.  The Kosterlitz flow of the chapter is  u' = 4 pi^3 y^2,  y' = (2 - pi/u) y.  The coefficient 4 pi^3 depends on how the
  fugacity y is normalised.  What changes in the trapping theorem if 4 pi^3 is replaced by another constant c > 0?

  The answer, proved here for solutions on l >= 0 (the hypotheses of book/lean/Ch06_KTForward.lean, with 4 pi^3 replaced by c):
    * the invariant becomes  Hc c u y = f u - (c/2) y^2  (kt_invariant);
    * the trapping theorem holds with H replaced by Hc c, and NOTHING else changes: the threshold u = pi/2 (K = 2/pi) and the conclusion
      are the same (kt_trapped, kt_fugacity_bounded);
    * the scalar reduction u' = 2 (f(u) - Hc(0)) and the escape bound have the same form for every c (kt_scalar, kt_escape);
    * the reason: y -> s y maps the flow with coefficient c onto the flow with coefficient c / s^2 and Hc c onto Hc (c/s^2)
      (rescale_flow, Hc_rescale); only the region of initial data {Hc c > f(pi/2)} is drawn differently in the (u, y) plane.
  The proofs follow book/lean/Ch06_KTForward.lean (definitions f, f_antitone, f_gt_fc and the proof patterns are restated, not imported).
-/
import Mathlib

open Real

namespace QuantumFluids.KTGeneralC

/-- `f(u) = 2u - pi log u` (as in `KTFlow` and `Ch06_KTForward`). -/
noncomputable def f (u : ℝ) : ℝ := 2 * u - π * log u

/-- The invariant of the flow `u' = c y^2`, `y' = (2 - pi/u) y`. For `c = 4 pi^3` it is the `H` of `KTFlow`. -/
noncomputable def Hc (c u y : ℝ) : ℝ := f u - c / 2 * y ^ 2

/-- For `c = 4 pi^3` the invariant is the one of the library and of the chapter. -/
theorem Hc_four_pi_cube (u y : ℝ) : Hc (4 * π ^ 3) u y = f u - 2 * π ^ 3 * y ^ 2 := by
  unfold Hc; ring

/-- `f` is non-increasing on `(0, π/2]` (as in `KTFlow`). -/
lemma f_antitone {a b : ℝ} (ha : 0 < a) (hab : a ≤ b) (hb : b ≤ π / 2) : f b ≤ f a := by
  have hb0 : 0 < b := ha.trans_le hab
  have hx : 0 < a / b := div_pos ha hb0
  have hlog : log (a / b) ≤ a / b - 1 := log_le_sub_one_of_pos hx
  rw [log_div ha.ne' hb0.ne'] at hlog
  have h1 : (1 - a / b) * (π - 2 * b) ≥ 0 :=
    mul_nonneg (by rw [sub_nonneg, div_le_one hb0]; exact hab) (by linarith)
  have h2 : (1 - a / b) * (π - 2 * b) = π - π * (a / b) - 2 * b + 2 * a := by
    field_simp; ring
  unfold f; nlinarith [pi_pos]

/-- `f` has a strict global minimum on `(0, ∞)` at `π/2` (as in `Ch06_KTForward`). -/
lemma f_gt_fc {u : ℝ} (hu : 0 < u) (hne : u ≠ π / 2) : f (π / 2) < f u := by
  have hx : 0 < 2 * u / π := by positivity
  have hx1 : 2 * u / π ≠ 1 := by
    intro h
    apply hne
    field_simp at h
    linarith
  have h := log_lt_sub_one_of_pos hx hx1
  have h2 : log (2 * u / π) = log 2 + log u - log π := by
    rw [log_div (by positivity) pi_pos.ne', log_mul two_ne_zero hu.ne']
  have h3 : log (π / 2) = log π - log 2 := log_div pi_pos.ne' two_ne_zero
  have h4 : π * (2 * u / π - 1) = 2 * u - π := by field_simp
  have h5 : π * (log 2 + log u - log π) < 2 * u - π := by
    calc π * (log 2 + log u - log π) = π * log (2 * u / π) := by rw [h2]
      _ < π * (2 * u / π - 1) := mul_lt_mul_of_pos_left h pi_pos
      _ = 2 * u - π := h4
  unfold f
  rw [h3]
  linarith [h5]

lemma f_ge_fc {u : ℝ} (hu : 0 < u) : f (π / 2) ≤ f u := by
  by_cases h : u = π / 2
  · rw [h]
  · exact (f_gt_fc hu h).le

/-- Rescaling the fugacity changes only the coefficient: `Hc (c / s^2) u (s y) = Hc c u y`. -/
theorem Hc_rescale (c s a b : ℝ) (hs : s ≠ 0) : Hc (c / s ^ 2) a (s * b) = Hc c a b := by
  unfold Hc
  have hs2 : s ^ 2 ≠ 0 := pow_ne_zero 2 hs
  have e : c / s ^ 2 / 2 * (s * b) ^ 2 = c / 2 * b ^ 2 := by
    rw [mul_pow, div_div, div_mul_eq_mul_div, div_eq_iff (mul_ne_zero hs2 two_ne_zero)]
    ring
  rw [e]

section forward

variable (c : ℝ) (u y : ℝ → ℝ)
  (hu : ∀ l, 0 ≤ l → HasDerivWithinAt u (c * (y l) ^ 2) (Set.Ici 0) l)
  (hy : ∀ l, 0 ≤ l → HasDerivWithinAt y ((2 - π / u l) * y l) (Set.Ici 0) l)
  (hpos : ∀ l, 0 ≤ l → 0 < u l)

omit hpos in
include hu hy in
/-- `y ↦ s y` maps a solution of the flow with coefficient `c` onto a solution of the flow with coefficient `c / s^2`. -/
theorem rescale_flow (s : ℝ) (hs : s ≠ 0) (l : ℝ) (hl : 0 ≤ l) :
    HasDerivWithinAt u (c / s ^ 2 * (s * y l) ^ 2) (Set.Ici 0) l ∧
      HasDerivWithinAt (fun x => s * y x) ((2 - π / u l) * (s * y l)) (Set.Ici 0) l := by
  have hs2 : s ^ 2 ≠ 0 := pow_ne_zero 2 hs
  constructor
  · refine (hu l hl).congr_deriv ?_
    rw [div_mul_eq_mul_div, eq_div_iff hs2]
    ring
  · exact ((hy l hl).const_mul s).congr_deriv (by ring)

include hu hy hpos

lemma hasDerivWithinAt_Hc (l : ℝ) (hl : 0 ≤ l) :
    HasDerivWithinAt (fun l => Hc c (u l) (y l)) 0 (Set.Ici 0) l := by
  have h1 := ((hu l hl).const_mul 2).sub (((hu l hl).log (hpos l hl).ne').const_mul π)
  have h2 := ((hy l hl).pow 2).const_mul (c / 2)
  have h := h1.sub h2
  have hfun : (fun l => Hc c (u l) (y l)) =
      ((fun y => 2 * u y) - fun y => π * log (u y)) - fun l => c / 2 * (y ^ 2) l := by
    funext l; simp [Hc, f]
  rw [hfun]
  refine h.congr_deriv ?_
  have := (hpos l hl).ne'
  norm_num
  field_simp
  ring

/-- The invariant `Hc c` is exactly conserved along a solution on `[0, ∞)`, for every `c`. -/
theorem kt_invariant (l : ℝ) (hl : 0 ≤ l) : Hc c (u l) (y l) = Hc c (u 0) (y 0) := by
  have hcont : ContinuousOn (fun l => Hc c (u l) (y l)) (Set.Icc 0 l) := fun x hx =>
    ((hasDerivWithinAt_Hc c u y hu hy hpos x hx.1).continuousWithinAt).mono Set.Icc_subset_Ici_self
  exact constant_of_has_deriv_right_zero hcont
    (fun x hx => (hasDerivWithinAt_Hc c u y hu hy hpos x hx.1).mono (Set.Ici_subset_Ici.mpr hx.1)) l ⟨hl, le_rfl⟩

lemma f_ge_Hc (hc : 0 ≤ c) (l : ℝ) (hl : 0 ≤ l) : Hc c (u 0) (y 0) ≤ f (u l) := by
  rw [← kt_invariant c u y hu hy hpos l hl]
  unfold Hc
  have : 0 ≤ c / 2 * y l ^ 2 := mul_nonneg (by linarith) (sq_nonneg _)
  linarith

/-- The trapping theorem for any coefficient `c ≥ 0`: only `H` is replaced by `Hc c`; the threshold `π/2` is unchanged. -/
theorem kt_trapped (hc : 0 ≤ c) (h0 : u 0 < π / 2) (hH : f (π / 2) < Hc c (u 0) (y 0)) :
    ∀ l, 0 ≤ l → u l < π / 2 := by
  intro l hl
  by_contra hcon
  push Not at hcon
  have hcu : ContinuousOn u (Set.Icc 0 l) := fun x hx =>
    ((hu x hx.1).continuousWithinAt).mono Set.Icc_subset_Ici_self
  obtain ⟨l', hlmem, hl'⟩ := intermediate_value_Icc hl hcu ⟨h0.le, hcon⟩
  have := f_ge_Hc c u y hu hy hpos hc l' hlmem.1
  rw [hl'] at this
  linarith

omit hy hpos in
/-- `u` is monotone on `[0, ∞)` when `c ≥ 0`. -/
theorem u_monotoneOn (hc : 0 ≤ c) : MonotoneOn u (Set.Ici 0) := by
  have hcont : ContinuousOn u (Set.Ici 0) := fun x hx => (hu x hx).continuousWithinAt
  refine monotoneOn_of_hasDerivWithinAt_nonneg (convex_Ici 0) hcont (f' := fun l => c * (y l) ^ 2) ?_ ?_
  · intro x hx
    rw [interior_Ici] at hx
    exact (hu x (le_of_lt hx)).mono interior_subset
  · intro x _
    exact mul_nonneg hc (sq_nonneg _)

/-- On the trapped side the fugacity never grows, for every `c > 0`. -/
theorem kt_fugacity_bounded (hc : 0 < c) (h0 : u 0 < π / 2) (hH : f (π / 2) < Hc c (u 0) (y 0))
    (l : ℝ) (hl : 0 ≤ l) : y l ^ 2 ≤ y 0 ^ 2 := by
  have hmono : u 0 ≤ u l :=
    u_monotoneOn c u y hu hc.le (Set.mem_Ici.mpr le_rfl) (Set.mem_Ici.mpr hl) hl
  have htrap := kt_trapped c u y hu hy hpos hc.le h0 hH l hl
  have hf : f (u l) ≤ f (u 0) := f_antitone (hpos 0 le_rfl) hmono htrap.le
  have hinv := kt_invariant c u y hu hy hpos l hl
  unfold Hc at hinv
  have h2 : c / 2 * y l ^ 2 ≤ c / 2 * y 0 ^ 2 := by linarith
  exact le_of_mul_le_mul_left h2 (by linarith)

/-- The scalar reduction `u' = 2 (f(u) - Hc(0))`: the same equation for every `c`. -/
theorem kt_scalar (l : ℝ) (hl : 0 ≤ l) :
    HasDerivWithinAt u (2 * (f (u l) - Hc c (u 0) (y 0))) (Set.Ici 0) l := by
  have h := kt_invariant c u y hu hy hpos l hl
  have e : c * (y l) ^ 2 = 2 * (f (u l) - Hc c (u 0) (y 0)) := by
    rw [← h]; unfold Hc; ring
  rw [← e]; exact hu l hl

/-- The escape bound `u(l) ≥ u(0) + 2 (f(π/2) − Hc(0)) l`, for every `c`. -/
theorem kt_escape (l : ℝ) (hl : 0 ≤ l) :
    u 0 + 2 * (f (π / 2) - Hc c (u 0) (y 0)) * l ≤ u l := by
  set δ : ℝ := f (π / 2) - Hc c (u 0) (y 0) with hδ
  have hcont : ContinuousOn (fun x => u x - 2 * δ * x) (Set.Ici 0) := fun x hx =>
    ((hu x hx).sub ((hasDerivWithinAt_id x (Set.Ici 0)).const_mul (2 * δ))).continuousWithinAt
  have hmono : MonotoneOn (fun x => u x - 2 * δ * x) (Set.Ici 0) := by
    refine monotoneOn_of_hasDerivWithinAt_nonneg (convex_Ici 0) hcont
      (f' := fun x => c * (y x) ^ 2 - 2 * δ * 1) ?_ ?_
    · intro x hx
      rw [interior_Ici] at hx
      exact ((hu x (le_of_lt hx)).sub ((hasDerivWithinAt_id x (Set.Ici 0)).const_mul (2 * δ))).mono interior_subset
    · intro x hx
      rw [interior_Ici] at hx
      have hx0 : 0 ≤ x := le_of_lt hx
      have hinv := kt_invariant c u y hu hy hpos x hx0
      have hf := f_ge_fc (hpos x hx0)
      have hHx : Hc c (u x) (y x) = f (u x) - c / 2 * y x ^ 2 := rfl
      linarith
  have h : u 0 - 2 * δ * 0 ≤ u l - 2 * δ * l := hmono (Set.mem_Ici.mpr le_rfl) (Set.mem_Ici.mpr hl) hl
  linarith

end forward

end QuantumFluids.KTGeneralC

#print axioms QuantumFluids.KTGeneralC.Hc_four_pi_cube
#print axioms QuantumFluids.KTGeneralC.f_antitone
#print axioms QuantumFluids.KTGeneralC.f_gt_fc
#print axioms QuantumFluids.KTGeneralC.f_ge_fc
#print axioms QuantumFluids.KTGeneralC.Hc_rescale
#print axioms QuantumFluids.KTGeneralC.rescale_flow
#print axioms QuantumFluids.KTGeneralC.hasDerivWithinAt_Hc
#print axioms QuantumFluids.KTGeneralC.kt_invariant
#print axioms QuantumFluids.KTGeneralC.f_ge_Hc
#print axioms QuantumFluids.KTGeneralC.kt_trapped
#print axioms QuantumFluids.KTGeneralC.u_monotoneOn
#print axioms QuantumFluids.KTGeneralC.kt_fugacity_bounded
#print axioms QuantumFluids.KTGeneralC.kt_scalar
#print axioms QuantumFluids.KTGeneralC.kt_escape
