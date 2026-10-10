/-
  Ch07_DissipativePairs.lean  --  NEW, written for the book "Quantum Fluids in Lean 4: a tribute to Henri Godfrin", chapter 7.
  It is NOT part of the QuantumFluids library (the library's `DissipativeVortexDynamics.lean` is imported by nothing here).

  Two additions to `DissipativeVortexDynamics.lean`, in the same model (hbar = m = 1, circulation 2 pi, normal fluid at rest):
  a vortex of charge q moves at   v = (1 - alpha') v_s - alpha q z x v_s,   v_s the velocity induced by the other vortices.

  1. `corot_sq_law`.  Two vortices of the SAME sign (the kind of pair whose separation Moon et al., 2015, followed in an oblate
     condensate).  With d = p1 - p2 the model gives  d' = [2 (1 - alpha') z x d + 2 alpha d] / |d|^2,  hence
         d/dt |d|^2 = + 4 alpha,        |d|^2 = |d_0|^2 + 4 alpha t.
     It is the dipole law of the library with the opposite sign: friction makes an opposite-sign pair shrink and a same-sign
     pair spiral apart.  The proof is the proof of `dipole_sq_law`.

  2. `wind_stall_at_b`.  The reduced equation of hypothesis W (the phonon wind of a closed box), written as it is derived,
         d' = -2 alpha (1/d - w (d_0 - d)),            w = 2 pi rho_s / (rho_n L^2),
     has a stall point  b = [d_0 + sqrt(d_0^2 - 4/w)]/2  when w d_0^2 > 4, and a pair that starts at or above b never falls
     below it.  The library proves this for the factorised form  d' = -c (d - a)(d - b)/d  (`wind_stall`) and states the
     identification  a + b = d_0,  a b = 1/w  in a comment; here the identification is a theorem (`roots_spec`) and the
     statement is made about the equation as derived.  The fence argument of the library is repeated (`stall_fence`) so that
     this file compiles alone.  `wind_no_zero` is the other side of the criterion: for w d_0^2 < 4 the right-hand side has no
     zero, so there is nothing to stall at.  `stall_needs_start` is the negative control.

  WHAT THIS DOES NOT SHOW.  It does not show that hypothesis W describes the field: the control run in a larger box refuted it
  (chapter 7).  A theorem certifies an implication; whether the premise holds is measured.
-/
import Mathlib

open Set

namespace QuantumFluids.DissipativePairs

/-! ### 1. A pair of vortices of the same sign -/

section corot

variable (x1 y1 x2 y2 : ℝ → ℝ) (α α' : ℝ)

/-- squared separation of the two vortices -/
noncomputable def r2 (t : ℝ) : ℝ := (x1 t - x2 t) ^ 2 + (y1 t - y2 t) ^ 2

variable {x1 y1 x2 y2 α α'} {T : ℝ}
  (hx1 : ∀ t ∈ Icc (0 : ℝ) T, HasDerivAt x1
    ((-(1 - α') * (y1 t - y2 t) + α * (x1 t - x2 t)) / r2 x1 y1 x2 y2 t) t)
  (hy1 : ∀ t ∈ Icc (0 : ℝ) T, HasDerivAt y1
    (((1 - α') * (x1 t - x2 t) + α * (y1 t - y2 t)) / r2 x1 y1 x2 y2 t) t)
  (hx2 : ∀ t ∈ Icc (0 : ℝ) T, HasDerivAt x2
    (((1 - α') * (y1 t - y2 t) - α * (x1 t - x2 t)) / r2 x1 y1 x2 y2 t) t)
  (hy2 : ∀ t ∈ Icc (0 : ℝ) T, HasDerivAt y2
    ((-(1 - α') * (x1 t - x2 t) - α * (y1 t - y2 t)) / r2 x1 y1 x2 y2 t) t)
  (hpos : ∀ t ∈ Icc (0 : ℝ) T, r2 x1 y1 x2 y2 t ≠ 0)
include hx1 hy1 hx2 hy2 hpos

/-- `d/dt |d|² = +4α`, whatever `α'`. -/
theorem r2_hasDerivAt (t : ℝ) (ht : t ∈ Icc (0 : ℝ) T) : HasDerivAt (r2 x1 y1 x2 y2) (4 * α) t := by
  have hx := ((hx1 t ht).sub (hx2 t ht)).pow 2
  have hy := ((hy1 t ht).sub (hy2 t ht)).pow 2
  have h := hx.add hy
  have hne := hpos t ht
  unfold r2 at hne ⊢
  refine h.congr_deriv ?_
  simp only [r2, Pi.sub_apply]
  field_simp
  ring

/-- The `d²` law of a same-sign pair on the whole interval of existence: the separation GROWS. -/
theorem corot_sq_law (t : ℝ) (ht : t ∈ Icc (0 : ℝ) T) :
    r2 x1 y1 x2 y2 t = r2 x1 y1 x2 y2 0 + 4 * α * t := by
  have key : ∀ x ∈ Icc (0 : ℝ) T, HasDerivAt (fun s => r2 x1 y1 x2 y2 s - 4 * α * s) 0 x := fun x hx => by
    have h := (r2_hasDerivAt hx1 hy1 hx2 hy2 hpos x hx).sub ((hasDerivAt_id x).const_mul (4 * α))
    refine h.congr_deriv ?_
    ring
  have hc : ContinuousOn (fun s => r2 x1 y1 x2 y2 s - 4 * α * s) (Icc 0 T) :=
    fun x hx => (key x hx).continuousAt.continuousWithinAt
  have := constant_of_has_deriv_right_zero hc
    (fun x hx => (key x ⟨hx.1, hx.2.le⟩).hasDerivWithinAt) t ht
  simp only [mul_zero, sub_zero] at this
  linarith

end corot

/-! ### 2. The phonon-wind equation of hypothesis W -/

section wind

/-- The larger root `b` of `w x² − w d₀ x + 1 = 0`: the stall point. -/
noncomputable def stallPoint (w d0 : ℝ) : ℝ := (d0 + Real.sqrt (d0 ^ 2 - 4 / w)) / 2

/-- The smaller root `a`. -/
noncomputable def lowerRoot (w d0 : ℝ) : ℝ := (d0 - Real.sqrt (d0 ^ 2 - 4 / w)) / 2

/-- For `w d₀² > 4` the two roots are real, ordered, positive, with `a + b = d₀` and `a b = 1/w`. -/
theorem roots_spec {w d0 : ℝ} (hw : 0 < w) (hd0 : 0 < d0) (h4 : 4 < w * d0 ^ 2) :
    0 < lowerRoot w d0 ∧ lowerRoot w d0 < stallPoint w d0 ∧
      lowerRoot w d0 + stallPoint w d0 = d0 ∧ lowerRoot w d0 * stallPoint w d0 = 1 / w := by
  have h4w : 4 / w < d0 ^ 2 := by rw [div_lt_iff₀ hw]; linarith
  have hpos4 : 0 < 4 / w := by positivity
  have hs : 0 < Real.sqrt (d0 ^ 2 - 4 / w) := Real.sqrt_pos.mpr (by linarith)
  have hsq : Real.sqrt (d0 ^ 2 - 4 / w) ^ 2 = d0 ^ 2 - 4 / w := Real.sq_sqrt (by linarith)
  have hslt : Real.sqrt (d0 ^ 2 - 4 / w) < d0 := (Real.sqrt_lt' hd0).mpr (by linarith)
  refine ⟨?_, ?_, ?_, ?_⟩
  · unfold lowerRoot; linarith
  · unfold lowerRoot stallPoint; linarith
  · unfold lowerRoot stallPoint; ring
  · unfold lowerRoot stallPoint
    have e : (d0 - Real.sqrt (d0 ^ 2 - 4 / w)) / 2 * ((d0 + Real.sqrt (d0 ^ 2 - 4 / w)) / 2)
        = (d0 ^ 2 - Real.sqrt (d0 ^ 2 - 4 / w) ^ 2) / 4 := by ring
    rw [e, hsq]; ring

/-- The fence argument of `DissipativeVortexDynamics.stall_of_drive_sign` (same statement, same proof), repeated so that
this file compiles alone: a drive `g` that is negative on `(a, b)` cannot carry a solution from `b` down below `b`. -/
theorem stall_fence {a b c : ℝ} (hab : a < b) (hc : 0 < c) (g : ℝ → ℝ) (hg : ∀ x, a < x → x < b → g x < 0)
    (d : ℝ → ℝ) (hd : ∀ t, HasDerivAt d (-c * g (d t)) t) (h0 : b ≤ d 0) :
    ∀ t, 0 ≤ t → b ≤ d t := by
  intro t ht
  by_contra hlt
  push Not at hlt
  set ε := min ((b - d t) / 2) ((b - a) / 2) with hε
  have hεpos : 0 < ε := lt_min (by linarith) (by linarith)
  have hε1 : ε ≤ (b - d t) / 2 := min_le_left _ _
  have hε2 : ε ≤ (b - a) / 2 := min_le_right _ _
  have hfence : ∀ ⦃x⦄, x ∈ Icc (0 : ℝ) t → (fun s => -d s) x ≤ (fun _ => -(b - ε)) x := by
    refine image_le_of_deriv_right_lt_deriv_boundary (f' := fun s => -(-c * g (d s)))
      (B' := fun _ => 0) (fun x _ => (hd x).neg.continuousAt.continuousWithinAt)
      (fun x _ => (hd x).neg.hasDerivWithinAt) (show -d 0 ≤ -(b - ε) by linarith)
      (fun x => hasDerivAt_const x _) ?_
    intro x _ hx
    have hx' : -d x = -(b - ε) := hx
    have hdx : d x = b - ε := by linarith
    have hneg : g (d x) < 0 := hg _ (by rw [hdx]; linarith) (by rw [hdx]; linarith)
    have : 0 < -c * g (d x) := by nlinarith
    show -(-c * g (d x)) < 0
    linarith
  have h' : -d t ≤ -(b - ε) := hfence ⟨ht, le_refl t⟩
  linarith

/-- The stall of the wind equation AS DERIVED: for `w d₀² > 4`, a pair that starts at or above
`b = [d₀ + √(d₀² − 4/w)]/2` never falls below `b`. -/
theorem wind_stall_at_b {α w d0 : ℝ} (hα : 0 < α) (hw : 0 < w) (hd0 : 0 < d0) (h4 : 4 < w * d0 ^ 2)
    (d : ℝ → ℝ) (hd : ∀ t, HasDerivAt d (-(2 * α) * (1 / d t - w * (d0 - d t))) t)
    (h0 : stallPoint w d0 ≤ d 0) : ∀ t, 0 ≤ t → stallPoint w d0 ≤ d t := by
  obtain ⟨ha, hab, hsum, hprod⟩ := roots_spec hw hd0 h4
  refine stall_fence (a := lowerRoot w d0) (b := stallPoint w d0) (c := 2 * α) hab (by positivity)
    (fun x => 1 / x - w * (d0 - x)) ?_ d hd h0
  intro x hax hxb
  have hx : 0 < x := lt_trans ha hax
  have h1 : 0 < (x - lowerRoot w d0) * (stallPoint w d0 - x) := mul_pos (by linarith) (by linarith)
  have e : (x - lowerRoot w d0) * (stallPoint w d0 - x)
      = x * (lowerRoot w d0 + stallPoint w d0) - x ^ 2 - lowerRoot w d0 * stallPoint w d0 := by ring
  rw [e, hsum, hprod] at h1
  have h2 : 1 / w < x * (d0 - x) := by nlinarith
  have h3 : 1 < x * (d0 - x) * w := (div_lt_iff₀ hw).mp h2
  show 1 / x - w * (d0 - x) < 0
  have h5 : 1 / x < w * (d0 - x) := by rw [div_lt_iff₀ hx]; nlinarith
  linarith

/-- The other side of the criterion: for `w d₀² < 4` the right-hand side of the wind equation never vanishes
(it stays on the side of shrinking), so there is no stall point. -/
theorem wind_no_zero {w d0 : ℝ} (hw : 0 < w) (h4 : w * d0 ^ 2 < 4) {x : ℝ} (hx : 0 < x) :
    0 < 1 / x - w * (d0 - x) := by
  have h1 : w * (x * (d0 - x)) ≤ w * (d0 ^ 2 / 4) := by
    apply mul_le_mul_of_nonneg_left _ hw.le
    nlinarith [sq_nonneg (x - d0 / 2)]
  have h2 : w * (d0 - x) < 1 / x := by rw [lt_div_iff₀ hx]; nlinarith
  linarith

/-- Negative control: the hypothesis `b ≤ d 0` cannot be dropped -- the constant solution at the lower root `a`
solves the wind equation and stays strictly below `b`. -/
theorem stall_needs_start {α w d0 : ℝ} (hw : 0 < w) (hd0 : 0 < d0) (h4 : 4 < w * d0 ^ 2) :
    (∀ t : ℝ, HasDerivAt (fun _ : ℝ => lowerRoot w d0)
        (-(2 * α) * (1 / lowerRoot w d0 - w * (d0 - lowerRoot w d0))) t) ∧
      lowerRoot w d0 < stallPoint w d0 := by
  obtain ⟨ha, hab, hsum, hprod⟩ := roots_spec hw hd0 h4
  refine ⟨fun t => ?_, hab⟩
  have hb : d0 - lowerRoot w d0 = stallPoint w d0 := by linarith
  have e : 1 / lowerRoot w d0 - w * (d0 - lowerRoot w d0) = 0 := by
    rw [hb]
    have hb0 : 0 < stallPoint w d0 := lt_trans ha hab
    rw [sub_eq_zero, div_eq_iff ha.ne']
    have : w * (lowerRoot w d0 * stallPoint w d0) = 1 := by rw [hprod]; field_simp
    nlinarith
  rw [e, mul_zero]
  exact hasDerivAt_const t _

end wind

end QuantumFluids.DissipativePairs

#print axioms QuantumFluids.DissipativePairs.r2_hasDerivAt
#print axioms QuantumFluids.DissipativePairs.corot_sq_law
#print axioms QuantumFluids.DissipativePairs.roots_spec
#print axioms QuantumFluids.DissipativePairs.stall_fence
#print axioms QuantumFluids.DissipativePairs.wind_stall_at_b
#print axioms QuantumFluids.DissipativePairs.wind_no_zero
#print axioms QuantumFluids.DissipativePairs.stall_needs_start
