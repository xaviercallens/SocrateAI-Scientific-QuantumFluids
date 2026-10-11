/-
Copyright (c) 2026 Xavier Callens. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xavier Callens
-/
module

public import Mathlib.Analysis.Calculus.ContDiff.Operations
public import Mathlib.Analysis.Calculus.IteratedDeriv.Defs
public import Mathlib.Analysis.Calculus.IteratedDeriv.Lemmas
public import Mathlib.Analysis.SpecialFunctions.ExpDeriv

/-!
# Completely monotone functions

A function `f : ℝ → ℝ` is *completely monotone on a set `s`* if it is smooth on `s` and
`(-1)ⁿ f⁽ⁿ⁾ ≥ 0` on `s` for all `n`. The definition is phrased exactly like `AbsolutelyMonotoneOn`
(existence of a Taylor series with the sign-corrected terms nonnegative), so that no `UniqueDiffOn`
hypothesis is needed on every result.

## Main definitions

* `CompletelyMonotoneOn` — there is a Taylor series for `f` on `s` whose `n`th term at the
  all-ones tuple, multiplied by `(-1)ⁿ`, is nonnegative.

## Main results

* `CompletelyMonotoneOn.contDiffOn`, `CompletelyMonotoneOn.of_contDiff`,
  `CompletelyMonotoneOn.iff_iteratedDerivWithin_nonneg` (under `UniqueDiffOn`).
* `CompletelyMonotoneOn.add`, `CompletelyMonotoneOn.smul` — closure properties.
* `completelyMonotoneOn_exp_neg_mul` — `x ↦ exp (-(c * x))` for `c ≥ 0`.

## References

* [D. V. Widder, *The Laplace Transform*][widder1941]
-/

public section

open Set
open scoped ContDiff

/-- A function `f : ℝ → ℝ` is **completely monotone on a set `s`** if, heuristically, all iterated
derivatives satisfy `(-1)ⁿ f⁽ⁿ⁾ ≥ 0` on `s`. For technical reasons related to unique
differentiability, the precise definition is phrased as the existence of a Taylor series for `f` on
`s` whose `n`th term, evaluated at the all-ones tuple and multiplied by `(-1)ⁿ`, is nonnegative.
See `CompletelyMonotoneOn.iff_iteratedDerivWithin_nonneg` for the equivalence under
`UniqueDiffOn`. -/
def CompletelyMonotoneOn (f : ℝ → ℝ) (s : Set ℝ) : Prop :=
  ∃ p : ℝ → FormalMultilinearSeries ℝ ℝ ℝ,
    HasFTaylorSeriesUpToOn ∞ f p s ∧
    ∀ (n : ℕ) ⦃x : ℝ⦄, x ∈ s → 0 ≤ (-1 : ℝ) ^ n * p x n fun _ ↦ (1 : ℝ)

namespace CompletelyMonotoneOn

variable {f g : ℝ → ℝ} {s : Set ℝ}

/-- A completely monotone function on `s` is `C^∞` on `s`. -/
theorem contDiffOn (hf : CompletelyMonotoneOn f s) : ContDiffOn ℝ ∞ f s := by
  obtain ⟨_, hp, _⟩ := hf
  exact hp.contDiffOn

/-- A globally `C^∞` function whose signed iterated derivatives `(-1)ⁿ f⁽ⁿ⁾` are nonnegative on `s`
is completely monotone on `s`. The set `s` need *not* satisfy `UniqueDiffOn`. -/
theorem of_contDiff (hf : ContDiff ℝ ∞ f)
    (h : ∀ n : ℕ, ∀ x ∈ s, 0 ≤ (-1 : ℝ) ^ n * iteratedDeriv n f x) :
    CompletelyMonotoneOn f s := by
  refine ⟨ftaylorSeries ℝ f, (hf.ftaylorSeries).hasFTaylorSeriesUpToOn s, fun n x hx => ?_⟩
  have := h n x hx
  rw [iteratedDeriv_eq_iteratedFDeriv] at this
  exact this

/-- Under `UniqueDiffOn`, a Taylor witness for a completely monotone function agrees with
`iteratedDerivWithin`, so the signed derivative is nonnegative on `s`. -/
theorem iteratedDerivWithin_nonneg (hf : CompletelyMonotoneOn f s) (hs : UniqueDiffOn ℝ s)
    (n : ℕ) {x : ℝ} (hx : x ∈ s) : 0 ≤ (-1 : ℝ) ^ n * iteratedDerivWithin n f s x := by
  obtain ⟨p, hp, hp_nn⟩ := hf
  have heq : p x n = iteratedFDerivWithin ℝ n f s x :=
    hp.eq_iteratedFDerivWithin_of_uniqueDiffOn (mod_cast le_top) hs hx
  rw [iteratedDerivWithin_eq_iteratedFDerivWithin, ← heq]
  exact hp_nn n hx

/-- Under `UniqueDiffOn`, a function is completely monotone on `s` iff it is `C^∞` on `s` with
every signed iterated derivative `(-1)ⁿ f⁽ⁿ⁾` within `s` nonnegative. -/
theorem iff_iteratedDerivWithin_nonneg (hs : UniqueDiffOn ℝ s) :
    CompletelyMonotoneOn f s ↔
      ContDiffOn ℝ ∞ f s ∧
        ∀ n : ℕ, ∀ x ∈ s, 0 ≤ (-1 : ℝ) ^ n * iteratedDerivWithin n f s x := by
  refine ⟨fun hf => ⟨hf.contDiffOn, fun n x hx => hf.iteratedDerivWithin_nonneg hs n hx⟩, ?_⟩
  rintro ⟨hcont, hnn⟩
  refine ⟨ftaylorSeriesWithin ℝ f s, hcont.ftaylorSeriesWithin hs, fun n x hx => ?_⟩
  have := hnn n x hx
  rw [iteratedDerivWithin_eq_iteratedFDerivWithin] at this
  exact this

/-! ### Closure properties -/

/-- The sum of two completely monotone functions is completely monotone. -/
theorem add (hf : CompletelyMonotoneOn f s) (hg : CompletelyMonotoneOn g s) :
    CompletelyMonotoneOn (f + g) s := by
  obtain ⟨p, hp, hp_nn⟩ := hf
  obtain ⟨q, hq, hq_nn⟩ := hg
  refine ⟨p + q, hp.add hq, fun n x hx => ?_⟩
  have e : ((p + q) x n) (fun _ ↦ (1 : ℝ)) = p x n (fun _ ↦ (1 : ℝ)) + q x n (fun _ ↦ (1 : ℝ)) :=
    rfl
  rw [e, mul_add]
  exact add_nonneg (hp_nn n hx) (hq_nn n hx)

/-- A nonnegative scalar multiple of a completely monotone function is completely monotone. -/
theorem smul {c : ℝ} (hf : CompletelyMonotoneOn f s) (hc : 0 ≤ c) :
    CompletelyMonotoneOn (c • f) s := by
  obtain ⟨p, hp, hp_nn⟩ := hf
  set T : ℝ →L[ℝ] ℝ := c • ContinuousLinearMap.id ℝ ℝ with hT
  have hcomp : (T ∘ f) = c • f := by ext x; simp [hT, smul_eq_mul]
  refine ⟨_, hcomp ▸ hp.continuousLinearMap_comp T, fun n x hx => ?_⟩
  simp only [ContinuousLinearMap.compContinuousMultilinearMap_coe, Function.comp_apply, hT,
    smul_apply, ContinuousLinearMap.id_apply, smul_eq_mul]
  have := mul_nonneg hc (hp_nn n hx)
  calc (0 : ℝ) ≤ c * ((-1 : ℝ) ^ n * p x n fun _ ↦ (1 : ℝ)) := this
    _ = _ := by ring

end CompletelyMonotoneOn

/-- `x ↦ exp (-(c * x))` is completely monotone for `c ≥ 0`. -/
theorem completelyMonotoneOn_exp_neg_mul {c : ℝ} (hc : 0 ≤ c) (s : Set ℝ) :
    CompletelyMonotoneOn (fun x => Real.exp (-(c * x))) s := by
  have hf : ContDiff ℝ ∞ (fun x : ℝ => Real.exp (-(c * x))) := by fun_prop
  refine CompletelyMonotoneOn.of_contDiff hf fun n x _ => ?_
  have h1 : (fun x : ℝ => Real.exp (-(c * x))) = fun x => Real.exp ((-c) * x) := by
    ext x; ring_nf
  rw [h1, iteratedDeriv_exp_const_mul]
  have : (-1 : ℝ) ^ n * ((-c) ^ n * Real.exp (-c * x)) = c ^ n * Real.exp (-c * x) := by
    rw [← mul_assoc, ← mul_pow]; simp
  rw [this]
  positivity
