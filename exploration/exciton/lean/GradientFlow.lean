import Mathlib

/-!
# The energy is non-increasing along a gradient flow (the invariant monitored as "L2" in Phase 1)

For a differentiable `f` on a real inner-product space and a curve `γ` with `γ' = -∇f(γ)`, the function `t ↦ f (γ t)`
has derivative `-‖∇f(γ t)‖² ≤ 0`, hence is antitone.  The N-particle experiments of
`docs/designs/EXCITON_FLUID_PHASE1_PREREG.md` integrate exactly such a flow with rusty-SUNDIALS CVODE and check this
inequality at the chunk ends (a numerical solution may violate it only by its tolerance).

Status: kernel-checked under Lean 4.34.0-rc2 / Mathlib 85e3a25; producer: the session that wrote the Phase 1
pre-registration; verifier pending.  Mathlib only; not part of the audited library `lean_src/`.
-/

namespace GradientFlow

open InnerProductSpace

theorem deriv_energy {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
    {f : E → ℝ} {γ : ℝ → E} (hf : ∀ x, DifferentiableAt ℝ f x)
    (hγ : ∀ t, HasDerivAt γ (-(gradient f (γ t))) t) (t : ℝ) :
    HasDerivAt (fun s => f (γ s)) (-(‖gradient f (γ t)‖ ^ 2)) t := by
  have h1 : HasGradientAt f (gradient f (γ t)) (γ t) := (hf (γ t)).hasGradientAt
  have h2 : HasDerivAt (f ∘ γ) ((toDual ℝ E (gradient f (γ t))) (-(gradient f (γ t)))) t :=
    h1.hasFDerivAt.comp_hasDerivAt t (hγ t)
  have e : (toDual ℝ E (gradient f (γ t))) (-(gradient f (γ t))) = -(‖gradient f (γ t)‖ ^ 2) := by
    rw [toDual_apply_apply, inner_neg_right, real_inner_self_eq_norm_sq]
  rw [e] at h2
  exact h2

theorem energy_antitone {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
    {f : E → ℝ} {γ : ℝ → E} (hf : ∀ x, DifferentiableAt ℝ f x)
    (hγ : ∀ t, HasDerivAt γ (-(gradient f (γ t))) t) : Antitone (fun t => f (γ t)) := by
  refine antitone_of_deriv_nonpos (fun t => (deriv_energy hf hγ t).differentiableAt) (fun t => ?_)
  rw [(deriv_energy hf hγ t).deriv]
  exact neg_nonpos.mpr (sq_nonneg _)

/-- Negative control: with the sign of the flow reversed (a gradient *ascent*) the energy is non-decreasing, so a
monitor for "non-increasing" would rightly fail on it. -/
theorem energy_monotone_ascent {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
    {f : E → ℝ} {γ : ℝ → E} (hf : ∀ x, DifferentiableAt ℝ f x)
    (hγ : ∀ t, HasDerivAt γ (gradient f (γ t)) t) : Monotone (fun t => f (γ t)) := by
  have hd : ∀ t, HasDerivAt (fun s => f (γ s)) (‖gradient f (γ t)‖ ^ 2) t := by
    intro t
    have h1 : HasGradientAt f (gradient f (γ t)) (γ t) := (hf (γ t)).hasGradientAt
    have h2 : HasDerivAt (f ∘ γ) ((toDual ℝ E (gradient f (γ t))) (gradient f (γ t))) t :=
      h1.hasFDerivAt.comp_hasDerivAt t (hγ t)
    have e : (toDual ℝ E (gradient f (γ t))) (gradient f (γ t)) = ‖gradient f (γ t)‖ ^ 2 := by
      rw [toDual_apply_apply, real_inner_self_eq_norm_sq]
    rw [e] at h2
    exact h2
  refine monotone_of_deriv_nonneg (fun t => (hd t).differentiableAt) (fun t => ?_)
  rw [(hd t).deriv]
  exact sq_nonneg _

end GradientFlow

#print axioms GradientFlow.energy_antitone
#print axioms GradientFlow.energy_monotone_ascent
