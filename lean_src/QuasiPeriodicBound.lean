/-
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
-/
import Mathlib

open Finset

namespace QuasiPeriodicBound

variable {ι : Type*} [Fintype ι]

/-- quasi-periodic signal with amplitudes `a`, frequencies `ω`, phases `φ` -/
noncomputable def qp (a ω φ : ι → ℝ) (t : ℝ) : ℝ := ∑ k, a k * Real.cos (ω k * t + φ k)

theorem trig_sum_bound (a ω φ : ι → ℝ) (t : ℝ) : |qp a ω φ t| ≤ ∑ k, |a k| := by
  unfold qp
  refine (abs_sum_le_sum_abs _ _).trans (sum_le_sum fun k _ => ?_)
  rw [abs_mul]
  exact mul_le_of_le_one_right (abs_nonneg _) (Real.abs_cos_le_one _)

theorem increment_bound (a ω φ : ι → ℝ) (t τ : ℝ) :
    |qp a ω φ (t + τ) - qp a ω φ t| ≤ 2 * ∑ k, |a k| := by
  calc |qp a ω φ (t + τ) - qp a ω φ t| ≤ |qp a ω φ (t + τ)| + |qp a ω φ t| := abs_sub _ _
    _ ≤ ∑ k, |a k| + ∑ k, |a k| := add_le_add (trig_sum_bound a ω φ _) (trig_sum_bound a ω φ _)
    _ = 2 * ∑ k, |a k| := by ring

/-- Any mean of squared increments (sample times `ts`, lags `τs`, both arbitrary finite families) is bounded. -/
theorem msd_bound (a ω φ : ι → ℝ) {J : Type*} [Fintype J] [Nonempty J] (ts τs : J → ℝ) :
    (∑ j, (qp a ω φ (ts j + τs j) - qp a ω φ (ts j)) ^ 2) / Fintype.card J ≤ (2 * ∑ k, |a k|) ^ 2 := by
  have hcard : (0 : ℝ) < Fintype.card J := by exact_mod_cast Fintype.card_pos
  rw [div_le_iff₀ hcard]
  calc ∑ j, (qp a ω φ (ts j + τs j) - qp a ω φ (ts j)) ^ 2
      ≤ ∑ _j : J, (2 * ∑ k, |a k|) ^ 2 := by
        refine sum_le_sum fun j _ => ?_
        rw [← sq_abs]
        exact pow_le_pow_left₀ (abs_nonneg _) (increment_bound a ω φ _ _) 2
    _ = (2 * ∑ k, |a k|) ^ 2 * Fintype.card J := by rw [sum_const, card_univ, nsmul_eq_mul]; ring

/-- A linearly growing MSD exceeds the quasi-periodic bound beyond a finite lag. -/
theorem random_walk_exceeds (A c : ℝ) (hc : 0 < c) :
    ∀ τ, 4 * A ^ 2 / c < τ → (2 * A) ^ 2 < c * τ := by
  intro τ h
  have := (div_lt_iff₀ hc).mp h
  nlinarith

/-- Contrapositive used on the data: if some sample mean of squared increments exceeds `4 (Σ|aₖ|)²`, the residual
is not the quasi-periodic sum `qp a ω φ` (for ANY frequencies and phases with those amplitudes). -/
theorem not_qp_of_msd_large (a : ι → ℝ) {J : Type*} [Fintype J] [Nonempty J] (x : ℝ → ℝ) (ts τs : J → ℝ)
    (h : (2 * ∑ k, |a k|) ^ 2 < (∑ j, (x (ts j + τs j) - x (ts j)) ^ 2) / Fintype.card J) :
    ∀ ω φ : ι → ℝ, x ≠ qp a ω φ := by
  intro ω φ hx
  subst hx
  exact absurd (msd_bound a ω φ ts τs) (not_le.mpr h)

/-! ### The torus dipole at T = 0 is a relative equilibrium: constant separation -/

/-- With `α = 0` the plane/torus dipole law `|d|² = |d₀|² − 4αt` gives constant separation: the residual of a
single pair at T = 0 is the one-term, zero-frequency quasi-periodic signal, whose increments vanish. -/
theorem relative_equilibrium_dipole (d0sq : ℝ) :
    ∀ t : ℝ, (d0sq - 4 * (0 : ℝ) * t) = d0sq := by
  intro t; ring

example (t τ : ℝ) : qp (fun _ : Fin 1 => (1 : ℝ)) (fun _ => 0) (fun _ => 0) (t + τ)
    - qp (fun _ : Fin 1 => (1 : ℝ)) (fun _ => 0) (fun _ => 0) t = 0 := by
  simp [qp]

/-- Negative control: a signal with growing MSD is not quasi-periodic with amplitude 1 -- `x t = t`
(ballistic), sampled at `t = 0`, lag `3`: increment `3 > 2`. -/
example : ∀ ω φ : Fin 1 → ℝ, (fun t : ℝ => t) ≠ qp (fun _ : Fin 1 => (1 : ℝ)) ω φ := by
  refine not_qp_of_msd_large (fun _ : Fin 1 => (1 : ℝ)) (J := Fin 1) (fun t : ℝ => t) (fun _ => 0) (fun _ => 3) ?_
  simp
  norm_num

end QuasiPeriodicBound
