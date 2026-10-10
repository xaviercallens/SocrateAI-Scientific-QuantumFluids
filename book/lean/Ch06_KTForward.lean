/-
  Ch06_KTForward.lean -- written for Chapter 6 of the book "Quantum Fluids in Lean 4".  NEW: this module is NOT part of the
  QuantumFluids library; it is compiled against the same pinned Mathlib (Lean 4.34.0-rc2) and nothing else.

  Why it exists.  `KTFlow.kt_invariant`, `kt_trapped` and `kt_fugacity_bounded` (lean_src/KTFlow.lean) assume that the Kosterlitz flow
      u' = 4 pi^3 y^2,   y' = (2 - pi/u) y,    u > 0
  holds for EVERY real l (`hu : forall l, HasDerivAt u ... l`, `hpos : forall l, 0 < u l`).  A renormalisation-group trajectory is a
  solution on l >= 0 only (l = ln(scale / microscopic scale)).  Part 2 below proves that on the superfluid side the library's
  hypotheses are met only by the line of fixed points:

      kt_eternal_trivial :  (hypotheses for all real l)  and  u 0 < pi/2   imply   y 0 = 0

  (backward in l, u' >= 4 pi^3 y(0)^2 > 0 while u <= u(0), so u would become negative at a finite negative l).  The library theorems
  are therefore true but, for u(0) < pi/2, say something only about fixed points.  Part 1 proves the same statements -- invariant,
  trapping, monotonicity, bounded fugacity -- under hypotheses on l >= 0 only, and adds the converse (escape below the separatrix):

      kt_escape        u(l) >= u(0) + 2 (f(pi/2) - H0) l                      for every solution on [0, infinity)
      kt_escape_time   if H0 < f(pi/2), u reaches pi/2 no later than l1 = (pi/2 - u(0)) / (2 (f(pi/2) - H0))
      kt_stiffness_vanishes   if H0 < f(pi/2), K = 1/u tends to 0
      kt_dichotomy     for u(0) < pi/2 and H0 != f(pi/2): K stays above 2/pi for ever, or falls to 2/pi in finite RG time.

  The definitions f, H, the lemma f_antitone and the proof patterns are those of lean_src/KTFlow.lean (this file cannot import it).
  NOT formalised: that non-trivial solutions on [0, infinity) exist (standard ODE theory; witnessed numerically in the chapter).
-/
import Mathlib

open Real

namespace QuantumFluids.KTForward

/-- `f(u) = 2u - pi log u`, the `u`-part of the invariant (as in `KTFlow`). -/
noncomputable def f (u : ℝ) : ℝ := 2 * u - π * log u

/-- The invariant (as in `KTFlow`). -/
noncomputable def H (u y : ℝ) : ℝ := f u - 2 * π ^ 3 * y ^ 2

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

/-- NEW. `f` has a strict global minimum on `(0, ∞)` at `π/2`:  `f(π/2) < f(u)` for `u ≠ π/2`
    (equivalent to `log x < x - 1` for `x = 2u/π ≠ 1`). -/
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

/-- NEW. The non-strict form: `f(π/2) ≤ f(u)` for every `u > 0`. -/
lemma f_ge_fc {u : ℝ} (hu : 0 < u) : f (π / 2) ≤ f u := by
  by_cases h : u = π / 2
  · rw [h]
  · exact (f_gt_fc hu h).le

/-! ## Part 1. The flow on `l ≥ 0` (hypotheses only for `l ≥ 0`) -/

section forward

variable (u y : ℝ → ℝ)
  (hu : ∀ l, 0 ≤ l → HasDerivWithinAt u (4 * π ^ 3 * (y l) ^ 2) (Set.Ici 0) l)
  (hy : ∀ l, 0 ≤ l → HasDerivWithinAt y ((2 - π / u l) * y l) (Set.Ici 0) l)
  (hpos : ∀ l, 0 ≤ l → 0 < u l)
include hu hy hpos

lemma hasDerivWithinAt_H (l : ℝ) (hl : 0 ≤ l) :
    HasDerivWithinAt (fun l => H (u l) (y l)) 0 (Set.Ici 0) l := by
  have h1 := ((hu l hl).const_mul 2).sub (((hu l hl).log (hpos l hl).ne').const_mul π)
  have h2 := ((hy l hl).pow 2).const_mul (2 * π ^ 3)
  have h := h1.sub h2
  have hfun : (fun l => H (u l) (y l)) =
      ((fun y => 2 * u y) - fun y => π * log (u y)) - fun l => 2 * π ^ 3 * (y ^ 2) l := by
    funext l; simp [H, f]
  rw [hfun]
  refine h.congr_deriv ?_
  have := (hpos l hl).ne'
  norm_num
  field_simp
  ring

/-- The invariant is exactly conserved along a solution on `[0, ∞)`. -/
theorem kt_invariant (l : ℝ) (hl : 0 ≤ l) : H (u l) (y l) = H (u 0) (y 0) := by
  have hcont : ContinuousOn (fun l => H (u l) (y l)) (Set.Icc 0 l) := fun x hx =>
    ((hasDerivWithinAt_H u y hu hy hpos x hx.1).continuousWithinAt).mono Set.Icc_subset_Ici_self
  exact constant_of_has_deriv_right_zero hcont
    (fun x hx => (hasDerivWithinAt_H u y hu hy hpos x hx.1).mono (Set.Ici_subset_Ici.mpr hx.1)) l ⟨hl, le_rfl⟩

lemma f_ge_H (l : ℝ) (hl : 0 ≤ l) : H (u 0) (y 0) ≤ f (u l) := by
  rw [← kt_invariant u y hu hy hpos l hl]; unfold H; nlinarith [pi_pos, sq_nonneg (y l), pow_pos pi_pos 3]

/-- The superfluid side is trapped: `K(l) > 2/π` for all `l ≥ 0`. -/
theorem kt_trapped (h0 : u 0 < π / 2) (hH : f (π / 2) < H (u 0) (y 0)) : ∀ l, 0 ≤ l → u l < π / 2 := by
  intro l hl
  by_contra hcon
  push Not at hcon
  have hc : ContinuousOn u (Set.Icc 0 l) := fun x hx =>
    ((hu x hx.1).continuousWithinAt).mono Set.Icc_subset_Ici_self
  obtain ⟨c, hcmem, hc'⟩ := intermediate_value_Icc hl hc ⟨h0.le, hcon⟩
  have := f_ge_H u y hu hy hpos c hcmem.1
  rw [hc'] at this
  linarith

omit hy hpos in
/-- `u` is monotone on `[0, ∞)` (the stiffness `K = 1/u` only decreases along the flow). -/
theorem u_monotoneOn : MonotoneOn u (Set.Ici 0) := by
  have hcont : ContinuousOn u (Set.Ici 0) := fun x hx => (hu x hx).continuousWithinAt
  refine monotoneOn_of_hasDerivWithinAt_nonneg (convex_Ici 0) hcont (f' := fun l => 4 * π ^ 3 * (y l) ^ 2) ?_ ?_
  · intro x hx
    rw [interior_Ici] at hx
    exact (hu x (le_of_lt hx)).mono interior_subset
  · intro x _
    positivity

/-- On the trapped side the fugacity never grows. -/
theorem kt_fugacity_bounded (h0 : u 0 < π / 2) (hH : f (π / 2) < H (u 0) (y 0)) (l : ℝ) (hl : 0 ≤ l) :
    y l ^ 2 ≤ y 0 ^ 2 := by
  have hmono : u 0 ≤ u l := u_monotoneOn u y hu (Set.mem_Ici.mpr le_rfl) (Set.mem_Ici.mpr hl) hl
  have htrap := kt_trapped u y hu hy hpos h0 hH l hl
  have hf : f (u l) ≤ f (u 0) := f_antitone (hpos 0 le_rfl) hmono htrap.le
  have hinv := kt_invariant u y hu hy hpos l hl
  unfold H at hinv
  have hp : 0 < 2 * π ^ 3 := by positivity
  nlinarith

/-- NEW. The planar flow reduces to a scalar autonomous ODE for `u` alone: `u' = 2 (f(u) - H₀)`. -/
theorem kt_scalar (l : ℝ) (hl : 0 ≤ l) :
    HasDerivWithinAt u (2 * (f (u l) - H (u 0) (y 0))) (Set.Ici 0) l := by
  have h := kt_invariant u y hu hy hpos l hl
  have e : 4 * π ^ 3 * (y l) ^ 2 = 2 * (f (u l) - H (u 0) (y 0)) := by
    rw [← h]; unfold H; ring
  rw [← e]; exact hu l hl

/-- NEW. A lower bound valid for every solution on `[0, ∞)`:  `u(l) ≥ u(0) + 2 (f(π/2) − H₀) l`.
    Below the separatrix (`H₀ < f(π/2)`) the slope is positive: the stiffness cannot be held. -/
theorem kt_escape (l : ℝ) (hl : 0 ≤ l) :
    u 0 + 2 * (f (π / 2) - H (u 0) (y 0)) * l ≤ u l := by
  set δ : ℝ := f (π / 2) - H (u 0) (y 0) with hδ
  have hcont : ContinuousOn (fun x => u x - 2 * δ * x) (Set.Ici 0) := fun x hx =>
    ((hu x hx).sub ((hasDerivWithinAt_id x (Set.Ici 0)).const_mul (2 * δ))).continuousWithinAt
  have hmono : MonotoneOn (fun x => u x - 2 * δ * x) (Set.Ici 0) := by
    refine monotoneOn_of_hasDerivWithinAt_nonneg (convex_Ici 0) hcont
      (f' := fun x => 4 * π ^ 3 * (y x) ^ 2 - 2 * δ * 1) ?_ ?_
    · intro x hx
      rw [interior_Ici] at hx
      exact ((hu x (le_of_lt hx)).sub ((hasDerivWithinAt_id x (Set.Ici 0)).const_mul (2 * δ))).mono interior_subset
    · intro x hx
      rw [interior_Ici] at hx
      have hx0 : 0 ≤ x := le_of_lt hx
      have hinv := kt_invariant u y hu hy hpos x hx0
      have hf := f_ge_fc (hpos x hx0)
      have hHx : H (u x) (y x) = f (u x) - 2 * π ^ 3 * y x ^ 2 := rfl
      linarith
  have h : u 0 - 2 * δ * 0 ≤ u l - 2 * δ * l := hmono (Set.mem_Ici.mpr le_rfl) (Set.mem_Ici.mpr hl) hl
  linarith

/-- NEW. Explicit escape time: below the separatrix `u` reaches `π/2` (i.e. `K` falls to `2/π`) no later than
    `l₁ = (π/2 − u 0) / (2 (f(π/2) − H₀))` (or at once, if it starts at or beyond `π/2`). -/
theorem kt_escape_time (hH : H (u 0) (y 0) < f (π / 2)) :
    ∃ l, 0 ≤ l ∧ π / 2 ≤ u l ∧
      l ≤ max 0 ((π / 2 - u 0) / (2 * (f (π / 2) - H (u 0) (y 0)))) := by
  set δ : ℝ := f (π / 2) - H (u 0) (y 0) with hδ
  have hδpos : 0 < δ := by rw [hδ]; linarith
  refine ⟨max 0 ((π / 2 - u 0) / (2 * δ)), le_max_left _ _, ?_, le_refl _⟩
  have h1 := kt_escape u y hu hy hpos (max 0 ((π / 2 - u 0) / (2 * δ))) (le_max_left _ _)
  have h2 : (π / 2 - u 0) / (2 * δ) ≤ max 0 ((π / 2 - u 0) / (2 * δ)) := le_max_right _ _
  have e : 2 * δ * ((π / 2 - u 0) / (2 * δ)) = π / 2 - u 0 := by field_simp
  have h3 : π / 2 - u 0 ≤ 2 * δ * max 0 ((π / 2 - u 0) / (2 * δ)) := by
    calc π / 2 - u 0 = 2 * δ * ((π / 2 - u 0) / (2 * δ)) := e.symm
      _ ≤ 2 * δ * max 0 ((π / 2 - u 0) / (2 * δ)) :=
        mul_le_mul_of_nonneg_left h2 (by linarith)
  linarith

/-- NEW. Below the separatrix the stiffness `K = 1/u` tends to `0`: the flow has no superfluid fixed point to go to. -/
theorem kt_stiffness_vanishes (hH : H (u 0) (y 0) < f (π / 2)) (ε : ℝ) (hε : 0 < ε) :
    ∃ L, 0 ≤ L ∧ ∀ l, L ≤ l → 1 / u l < ε := by
  set δ : ℝ := f (π / 2) - H (u 0) (y 0) with hδ
  have hδpos : 0 < δ := by rw [hδ]; linarith
  refine ⟨1 / (2 * δ * ε) + 1, by positivity, ?_⟩
  intro l hl
  have hl0 : 0 ≤ l := le_trans (by positivity) hl
  have h1 := kt_escape u y hu hy hpos l hl0
  have hu0 := hpos 0 le_rfl
  have hul := hpos l hl0
  have h3 : 1 / ε < u l := by
    have h4 : 1 / ε < 2 * δ * l := by
      have : 1 / (2 * δ * ε) < l := by linarith
      calc 1 / ε = 2 * δ * (1 / (2 * δ * ε)) := by field_simp
        _ < 2 * δ * l := mul_lt_mul_of_pos_left this (by positivity)
    linarith
  rw [div_lt_iff₀ hul]
  rw [div_lt_iff₀ hε] at h3
  linarith

/-- NEW. The dichotomy: starting on the superfluid side, off the separatrix, the stiffness either stays above
    `2/π` for ever or reaches it in finite RG time; the boundary is the level set `H = f(π/2)`. -/
theorem kt_dichotomy (h0 : u 0 < π / 2) (hne : H (u 0) (y 0) ≠ f (π / 2)) :
    (∀ l, 0 ≤ l → u l < π / 2) ∨ ∃ l, 0 ≤ l ∧ π / 2 ≤ u l := by
  rcases lt_or_gt_of_ne hne with h | h
  · right
    obtain ⟨l, hl, hle, _⟩ := kt_escape_time u y hu hy hpos h
    exact ⟨l, hl, hle⟩
  · left
    exact kt_trapped u y hu hy hpos h0 h

end forward

/-! ## Part 2. The library's hypotheses (all real `l`) leave only the line of fixed points on the superfluid side -/

section eternal

variable (u y : ℝ → ℝ)
  (hu : ∀ l, HasDerivAt u (4 * π ^ 3 * (y l) ^ 2) l)
  (hy : ∀ l, HasDerivAt y ((2 - π / u l) * y l) l)
  (hpos : ∀ l, 0 < u l)
include hu hy hpos

lemma hasDerivAt_H_global (l : ℝ) : HasDerivAt (fun l => H (u l) (y l)) 0 l := by
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

lemma kt_invariant_global (l : ℝ) : H (u l) (y l) = H (u 0) (y 0) := by
  have hd : Differentiable ℝ (fun l => H (u l) (y l)) := fun l => (hasDerivAt_H_global u y hu hy hpos l).differentiableAt
  exact is_const_of_deriv_eq_zero hd (fun l => (hasDerivAt_H_global u y hu hy hpos l).deriv) l 0

omit hy hpos in
lemma u_monotone_global : Monotone u :=
  monotone_of_deriv_nonneg (fun l => (hu l).differentiableAt)
    (fun l => by rw [(hu l).deriv]; positivity)

/-- NEW. With the library's hypotheses (the flow equations for EVERY real `l`, `u > 0` throughout), a solution that starts on the
    superfluid side has no fugacity: `y 0 = 0`.  Backward in `l` the slope of `u` is at least `c = 4 π³ y(0)²`, so `u` would be
    negative before `l = −u(0)/c`. -/
theorem kt_eternal_trivial (h0 : u 0 < π / 2) : y 0 = 0 := by
  by_contra hy0
  set c : ℝ := 4 * π ^ 3 * (y 0) ^ 2 with hc
  have hcpos : 0 < c := by
    have : 0 < (y 0) ^ 2 := by positivity
    rw [hc]; positivity
  have hmono := u_monotone_global u y hu
  -- for l ≤ 0:  u l ≤ u 0 < π/2, hence f (u l) ≥ f (u 0), hence u'(l) ≥ c
  have hder : ∀ l, l ≤ 0 → c ≤ 4 * π ^ 3 * (y l) ^ 2 := by
    intro l hl
    have hul : u l ≤ u 0 := hmono hl
    have hf : f (u 0) ≤ f (u l) := f_antitone (hpos l) hul h0.le
    have hinv := kt_invariant_global u y hu hy hpos l
    unfold H at hinv
    rw [hc]
    nlinarith
  have hg : MonotoneOn (fun x => u x - c * x) (Set.Iic 0) := by
    refine monotoneOn_of_hasDerivWithinAt_nonneg (convex_Iic 0) ?_ (f' := fun x => 4 * π ^ 3 * (y x) ^ 2 - c * 1) ?_ ?_
    · intro x _
      exact ((hu x).sub ((hasDerivAt_id x).const_mul c)).continuousAt.continuousWithinAt
    · intro x _
      exact ((hu x).sub ((hasDerivAt_id x).const_mul c)).hasDerivWithinAt
    · intro x hx
      rw [interior_Iic] at hx
      have := hder x (le_of_lt hx)
      linarith
  set l1 : ℝ := -(u 0 + 1) / c with hl1
  have hl1neg : l1 ≤ 0 := by
    rw [hl1]
    have : 0 ≤ (u 0 + 1) / c := by have := hpos 0; positivity
    have e : -(u 0 + 1) / c = -((u 0 + 1) / c) := by ring
    rw [e]; linarith
  have h := hg (Set.mem_Iic.mpr hl1neg) (Set.mem_Iic.mpr le_rfl) hl1neg
  have e2 : c * l1 = -(u 0 + 1) := by rw [hl1]; field_simp
  have : u l1 - c * l1 ≤ u 0 - c * 0 := h
  have := hpos l1
  nlinarith

end eternal

/-! ### Concrete instances and negative controls -/

/-- The hypotheses of Part 1 are met by the line of fixed points `u ≡ 1`, `y ≡ 0` (`H = f 1 = 2 > f(π/2)`), and `kt_trapped` applies. -/
example : ∀ l : ℝ, 0 ≤ l → (fun _ : ℝ => (1 : ℝ)) l < π / 2 := by
  intro l _
  have := pi_gt_three
  show (1 : ℝ) < π / 2
  linarith

/-- Negative control for `kt_eternal_trivial`: the conclusion `y 0 = 0` is false for the concrete point `(u, y) = (1, 1)`; this point
    carries the (forward) flow, which is why Part 1 is needed.  Here: `H(1, 1) = 2 − 2π³ < 0`, so it lies below the separatrix. -/
example : H 1 1 < f (π / 2) := by
  have hpi3 := pi_gt_three
  have hpi4 := pi_le_four
  have hlog := log_le_sub_one_of_pos (show (0 : ℝ) < π / 2 by positivity)
  have hfc : 0 ≤ f (π / 2) := by
    unfold f
    nlinarith [mul_le_mul_of_nonneg_left hlog pi_pos.le, mul_nonneg pi_pos.le (sub_nonneg.mpr hpi4)]
  have hH : H 1 1 = 2 - 2 * π ^ 3 := by simp [H, f]
  have h9 : 9 < π ^ 2 := by nlinarith
  have hcube : 1 < π ^ 3 := by nlinarith
  rw [hH]
  linarith

/-- Negative control: the minimum of `f` is strict, so `f_ge_fc` is not an equality: `f(π/2) < f(4)`. -/
example : f (π / 2) < f 4 :=
  f_gt_fc (by norm_num) (by intro h; have := pi_le_four; linarith)

end QuantumFluids.KTForward

#print axioms QuantumFluids.KTForward.f_antitone
#print axioms QuantumFluids.KTForward.f_gt_fc
#print axioms QuantumFluids.KTForward.f_ge_fc
#print axioms QuantumFluids.KTForward.hasDerivWithinAt_H
#print axioms QuantumFluids.KTForward.kt_invariant
#print axioms QuantumFluids.KTForward.f_ge_H
#print axioms QuantumFluids.KTForward.kt_trapped
#print axioms QuantumFluids.KTForward.u_monotoneOn
#print axioms QuantumFluids.KTForward.kt_fugacity_bounded
#print axioms QuantumFluids.KTForward.kt_scalar
#print axioms QuantumFluids.KTForward.kt_escape
#print axioms QuantumFluids.KTForward.kt_escape_time
#print axioms QuantumFluids.KTForward.kt_stiffness_vanishes
#print axioms QuantumFluids.KTForward.kt_dichotomy
#print axioms QuantumFluids.KTForward.hasDerivAt_H_global
#print axioms QuantumFluids.KTForward.kt_invariant_global
#print axioms QuantumFluids.KTForward.u_monotone_global
#print axioms QuantumFluids.KTForward.kt_eternal_trivial
