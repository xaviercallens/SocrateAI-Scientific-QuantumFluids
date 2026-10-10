/-
Ch03_PointVortexPair.lean -- NEW for the book chapter 3 ("From the wave function to the fluid").
Not part of the QuantumFluids library.

The reduced model against which the Gross-Pitaevskii vortex pair is compared in the chapter: point vortices in the
plane, the velocity induced at `z` by a vortex of circulation `Γ` at `w` being `i Γ / (2π conj(z - w))`
(the complex-plane form of  u = (Γ/2π) ẑ × (x - x_w) / |x - x_w|²).

  * `induced_mul_conj`, `induced_perp`, `norm_induced`:
        (induced velocity) * conj(z - w) = i Γ / (2π).  Two facts at once: the velocity is perpendicular to the line
        joining the two points, and its size is |Γ| / (2π |z - w|).
  * `pair_velocities_equal` : a vortex of circulation -Γ at z₁ and one of circulation +Γ at z₂ induce the same
        velocity on each other: a vortex-antivortex pair translates rigidly.
  * `separation_const`      : along any differentiable motion obeying the two induced-velocity equations the
        separation z₁ - z₂ is constant (for charges ±1 this is the conservation of the dipole moment Σ q z).
  * `pair_speed_quantum`    : for one quantum of circulation Γ = κ = 2πħ/m the speed of the pair is ħ/(m d).

NOT PROVED here: that the Gross-Pitaevskii vortex obeys this law (Helmholtz-Kirchhoff, textbook; the chapter tests
it with the solver); anything about the periodic box, the uniform flow of the torus, or more than two vortices.
-/
import Mathlib

namespace QuantumFluids.Ch03PointVortexPair

open Complex

/-- Velocity, as the complex number `u + i v`, induced at `z` by a point vortex of circulation `Γ` at `w`. -/
noncomputable def induced (Γ : ℝ) (z w : ℂ) : ℂ :=
  Complex.I * (Γ : ℂ) / (2 * (Real.pi : ℂ) * (starRingEnd ℂ) (z - w))

/-- Cancellation of a common non-zero factor, used to simplify `induced Γ z w * conj (z - w)`. -/
theorem cancel_aux (a b c : ℂ) (hb : b ≠ 0) (hc : c ≠ 0) : a / (b * c) * c = a / b := by
  field_simp

/-- **The induced velocity times the conjugate separation is purely imaginary and has a fixed modulus.** -/
theorem induced_mul_conj (Γ : ℝ) {z w : ℂ} (h : z ≠ w) :
    induced Γ z w * (starRingEnd ℂ) (z - w) = ((Γ / (2 * Real.pi) : ℝ) : ℂ) * Complex.I := by
  have hd : z - w ≠ 0 := sub_ne_zero.mpr h
  have hc : (starRingEnd ℂ) (z - w) ≠ 0 := (map_ne_zero (starRingEnd ℂ)).mpr hd
  have hb : (2 * (Real.pi : ℂ)) ≠ 0 :=
    mul_ne_zero two_ne_zero (Complex.ofReal_ne_zero.mpr Real.pi_ne_zero)
  unfold induced
  rw [cancel_aux _ _ _ hb hc]
  push_cast
  ring

/-- The induced velocity is perpendicular to the line joining the two points. -/
theorem induced_perp (Γ : ℝ) {z w : ℂ} (h : z ≠ w) :
    (induced Γ z w * (starRingEnd ℂ) (z - w)).re = 0 := by
  rw [induced_mul_conj Γ h]
  simp only [Complex.mul_re, Complex.ofReal_re, Complex.ofReal_im, Complex.I_re, Complex.I_im]
  ring

/-- Speed times separation is `|Γ| / (2π)`. -/
theorem norm_induced_mul (Γ : ℝ) {z w : ℂ} (h : z ≠ w) :
    ‖induced Γ z w‖ * ‖z - w‖ = |Γ| / (2 * Real.pi) := by
  have hpi := Real.pi_pos
  have hrhs : ‖(((Γ / (2 * Real.pi) : ℝ) : ℂ) * Complex.I)‖ = |Γ| / (2 * Real.pi) := by
    rw [norm_mul, Complex.norm_I, mul_one, Complex.norm_real, Real.norm_eq_abs, abs_div,
      abs_of_pos (by positivity : (0 : ℝ) < 2 * Real.pi)]
  have h2 : ‖induced Γ z w‖ * ‖z - w‖ = ‖(((Γ / (2 * Real.pi) : ℝ) : ℂ) * Complex.I)‖ := by
    rw [← RCLike.norm_conj (z - w), ← norm_mul, induced_mul_conj Γ h]
  exact h2.trans hrhs

/-- **The speed induced by a point vortex: `|Γ| / (2π d)`.** -/
theorem norm_induced (Γ : ℝ) {z w : ℂ} (h : z ≠ w) :
    ‖induced Γ z w‖ = |Γ| / (2 * Real.pi * ‖z - w‖) := by
  have hd : 0 < ‖z - w‖ := norm_pos_iff.mpr (sub_ne_zero.mpr h)
  have hpi := Real.pi_pos
  have h2 := norm_induced_mul Γ h
  rw [eq_div_iff (by positivity)]
  rw [eq_div_iff (by positivity)] at h2
  linarith

/-- **A vortex-antivortex pair translates rigidly**: the two induced velocities coincide. -/
theorem pair_velocities_equal (Γ : ℝ) (z₁ z₂ : ℂ) :
    induced (-Γ) z₁ z₂ = induced Γ z₂ z₁ := by
  unfold induced
  have hc : (starRingEnd ℂ) (z₂ - z₁) = -(starRingEnd ℂ) (z₁ - z₂) := by
    rw [← map_neg, neg_sub]
  rw [hc]
  push_cast
  ring

/-- **The separation of a vortex-antivortex pair is constant in time**, for any motion obeying the two
induced-velocity equations. -/
theorem separation_const (Γ : ℝ) (z₁ z₂ : ℝ → ℂ)
    (h₁ : ∀ t, HasDerivAt z₁ (induced (-Γ) (z₁ t) (z₂ t)) t)
    (h₂ : ∀ t, HasDerivAt z₂ (induced Γ (z₂ t) (z₁ t)) t) (t : ℝ) :
    z₁ t - z₂ t = z₁ 0 - z₂ 0 := by
  have hd : ∀ s, HasDerivAt (fun s => z₁ s - z₂ s) 0 s := by
    intro s
    have h := (h₁ s).sub (h₂ s)
    rw [pair_velocities_equal, sub_self] at h
    exact h
  exact is_const_of_deriv_eq_zero (fun s => (hd s).differentiableAt) (fun s => (hd s).deriv) t 0

/-- **Speed of a pair carrying one quantum of circulation**: with `Γ = κ = 2πħ/m` the speed is `ħ / (m d)`. -/
theorem pair_speed_quantum (ħ m : ℝ) (hħ : 0 < ħ) (hm : 0 < m) {z w : ℂ} (h : z ≠ w) :
    ‖induced (2 * Real.pi * ħ / m) z w‖ = ħ / (m * ‖z - w‖) := by
  have hd : 0 < ‖z - w‖ := norm_pos_iff.mpr (sub_ne_zero.mpr h)
  have hpi := Real.pi_pos
  have hΓ : 0 < 2 * Real.pi * ħ / m := by positivity
  rw [norm_induced _ h, abs_of_pos hΓ]
  field_simp

#print axioms induced_mul_conj
#print axioms induced_perp
#print axioms norm_induced_mul
#print axioms norm_induced
#print axioms pair_velocities_equal
#print axioms separation_const
#print axioms pair_speed_quantum

end QuantumFluids.Ch03PointVortexPair
