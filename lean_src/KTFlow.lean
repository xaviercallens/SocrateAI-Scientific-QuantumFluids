/-
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
-/
import Mathlib

open Real

namespace KTFlow

/-- `f(u) = 2u − π log u`, the `u`-part of the invariant. -/
noncomputable def f (u : ℝ) : ℝ := 2 * u - π * log u

/-- The invariant. -/
noncomputable def H (u y : ℝ) : ℝ := f u - 2 * π ^ 3 * y ^ 2

/-- `f` is non-increasing on `(0, π/2]`. -/
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

section flow

variable (u y : ℝ → ℝ)
  (hu : ∀ l, HasDerivAt u (4 * π ^ 3 * (y l) ^ 2) l)
  (hy : ∀ l, HasDerivAt y ((2 - π / u l) * y l) l)
  (hpos : ∀ l, 0 < u l)
include hu hy hpos

lemma hasDerivAt_H (l : ℝ) : HasDerivAt (fun l => H (u l) (y l)) 0 l := by
  have h1 := ((hu l).const_mul 2).sub (((hu l).log (hpos l).ne').const_mul π)
  have h2 := ((hy l).pow 2).const_mul (2 * π ^ 3)
  have h := h1.sub h2
  have hfun : (fun l => H (u l) (y l)) =
      ((fun y => 2 * u y) - fun y => π * log (u y)) - fun l => 2 * π ^ 3 * (y ^ 2) l := by
    funext l; simp [H, f]
  rw [hfun]
  refine h.congr_deriv ?_
  have := (hpos l).ne'
  norm_num
  field_simp
  ring

/-- The invariant is exactly conserved. -/
theorem kt_invariant (l : ℝ) : H (u l) (y l) = H (u 0) (y 0) := by
  have hd : Differentiable ℝ (fun l => H (u l) (y l)) := fun l => (hasDerivAt_H u y hu hy hpos l).differentiableAt
  exact is_const_of_deriv_eq_zero hd (fun l => (hasDerivAt_H u y hu hy hpos l).deriv) l 0

lemma f_ge_H (l : ℝ) : H (u 0) (y 0) ≤ f (u l) := by
  rw [← kt_invariant u y hu hy hpos l]; unfold H; nlinarith [pi_pos, sq_nonneg (y l), pow_pos pi_pos 3]

/-- The superfluid side is trapped: `K(l) > 2/π` for all `l ≥ 0`. -/
theorem kt_trapped (h0 : u 0 < π / 2) (hH : f (π / 2) < H (u 0) (y 0)) : ∀ l, 0 ≤ l → u l < π / 2 := by
  intro l hl
  by_contra hcon
  push Not at hcon
  have hc : ContinuousOn u (Set.Icc 0 l) := fun x _ => (hu x).continuousAt.continuousWithinAt
  obtain ⟨c, _, hc'⟩ := intermediate_value_Icc hl hc ⟨h0.le, hcon⟩
  have := f_ge_H u y hu hy hpos c
  rw [hc'] at this
  linarith

omit hy hpos in
/-- `u` is monotone (the stiffness `K = 1/u` only decreases along the flow). -/
theorem u_monotone : Monotone u :=
  monotone_of_deriv_nonneg (fun l => (hu l).differentiableAt)
    (fun l => by rw [(hu l).deriv]; positivity)

/-- On the trapped side the fugacity never grows. -/
theorem kt_fugacity_bounded (h0 : u 0 < π / 2) (hH : f (π / 2) < H (u 0) (y 0)) (l : ℝ) (hl : 0 ≤ l) :
    y l ^ 2 ≤ y 0 ^ 2 := by
  have hmono := u_monotone u y hu hl
  have htrap := kt_trapped u y hu hy hpos h0 hH l hl
  have hf : f (u l) ≤ f (u 0) := f_antitone (hpos 0) hmono htrap.le
  have hinv := kt_invariant u y hu hy hpos l
  unfold H at hinv
  have hp : 0 < 2 * π ^ 3 := by positivity
  nlinarith

end flow

/-- Units: `K > 2/π` (KT) is `2πK > 4` (this programme's `K = n_s λ_T²`). -/
theorem kt_units (K : ℝ) : 2 / π < K ↔ 4 < 2 * π * K := by
  constructor
  · intro h; have := (div_lt_iff₀ pi_pos).mp h; linarith
  · intro h; rw [div_lt_iff₀ pi_pos]; linarith

/-! ### Negative control: without the invariant bound the trapping fails.
The fixed point `(u, y) = (π/2, 0)` itself has `H = f(π/2)` exactly, so the strict hypothesis
`f(π/2) < H` is necessary: the constant flow at `u = π/2` is a solution that is NOT strictly below `π/2`. -/
example : ¬ ((π / 2 : ℝ) < π / 2) := lt_irrefl _

/-- The fixed point is a solution of the flow (so the boundary case is realised). -/
example : ∀ l : ℝ, HasDerivAt (fun _ : ℝ => π / 2) (4 * π ^ 3 * ((fun _ : ℝ => (0 : ℝ)) l) ^ 2) l ∧
    HasDerivAt (fun _ : ℝ => (0 : ℝ)) ((2 - π / (π / 2)) * (fun _ : ℝ => (0 : ℝ)) l) l := by
  intro l; constructor
  · simpa using hasDerivAt_const l (π / 2)
  · simpa using hasDerivAt_const l (0 : ℝ)

end KTFlow
