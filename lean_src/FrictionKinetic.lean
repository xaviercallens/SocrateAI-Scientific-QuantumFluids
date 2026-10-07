import Mathlib

/-!
# The kinetic reading of the friction law (docs/designs/FRICTION_LAW_THEORY_NOTE.md)

In the projected field the thermal bath is a finite set of modes `k ∈ K`. The drag coefficient `D` and the
Landau normal density `ρ_n` are sums over the same modes with the same nonnegative weight
`w k = (−∂n/∂ε) k²/2`, the drag carrying one extra factor `f k = c_g(k) σ_tr(k)` (group velocity times
transport cross-section):

  `D = Σ_k w k * f k`,   `ρ_n = Σ_k w k`.

What is proved here is exactly what the note claims and no more:

* `coeff_eq_weighted_mean` — the coefficient `α/(ρ_n/ρ)` is the `w`-weighted mean of `f` over the modes
  (times the kinematic factor `ρ/(ρ_s κ)`), so the law `α ∝ ρ_n` is an identity of the kinetic model for
  *any* bath and the coefficient is a property of `f`;
* `weighted_mean_mem_Icc` — that mean lies between the smallest and the largest `c_g σ_tr` over the bath, so the
  measured `0.232` is a value of `c_g σ_tr / κ` (times `ρ/ρ_s`) actually taken by some mode scale;
* `rayleigh_jeans_mean` — for a Rayleigh–Jeans bath with phonon dispersion the weights are equal and the mean is the
  plain arithmetic mean over the modes of the disk.

No claim about the value or the `k`-dependence of `σ_tr` is made; that is the measurement.
-/

namespace FrictionKinetic

open Finset BigOperators

variable {ι : Type*}

/-- The friction coefficient of the kinetic model: `α = D/(ρ_s κ)` with `D = Σ w f`. -/
noncomputable def alpha (K : Finset ι) (w f : ι → ℝ) (ρs κ : ℝ) : ℝ := (∑ k ∈ K, w k * f k) / (ρs * κ)

/-- The Landau normal density of the same bath: `ρ_n = Σ w`. -/
noncomputable def rhoN (K : Finset ι) (w : ι → ℝ) : ℝ := ∑ k ∈ K, w k

/-- `α / (ρ_n/ρ) = (ρ/(ρ_s κ)) · (Σ w f)/(Σ w)`: the friction law is an identity of the kinetic model,
and its coefficient is the weighted mean of `c_g σ_tr`. -/
theorem coeff_eq_weighted_mean (K : Finset ι) (w f : ι → ℝ) (ρ ρs κ : ℝ) (hρn : rhoN K w ≠ 0) (hρ : ρ ≠ 0) :
    alpha K w f ρs κ / (rhoN K w / ρ) = ρ / (ρs * κ) * ((∑ k ∈ K, w k * f k) / ∑ k ∈ K, w k) := by
  unfold alpha rhoN at *
  field_simp

/-- The weighted mean of `f` with nonnegative weights of positive total lies in `[min f, max f]` over the bath. -/
theorem weighted_mean_mem_Icc (K : Finset ι) (w f : ι → ℝ) (hw : ∀ k ∈ K, 0 ≤ w k) (hpos : 0 < ∑ k ∈ K, w k)
    (m M : ℝ) (hm : ∀ k ∈ K, m ≤ f k) (hM : ∀ k ∈ K, f k ≤ M) :
    (∑ k ∈ K, w k * f k) / (∑ k ∈ K, w k) ∈ Set.Icc m M := by
  constructor
  · rw [le_div_iff₀ hpos, Finset.mul_sum]
    exact Finset.sum_le_sum fun k hk => by rw [mul_comm]; exact mul_le_mul_of_nonneg_left (hm k hk) (hw k hk)
  · rw [div_le_iff₀ hpos, Finset.mul_sum]
    exact Finset.sum_le_sum fun k hk => by rw [mul_comm M]; exact mul_le_mul_of_nonneg_left (hM k hk) (hw k hk)

/-- Rayleigh–Jeans bath with phonon dispersion: every mode has the same weight `T/(2c²)`, and the coefficient is
the arithmetic mean of `c_g σ_tr` over the modes of the disk. -/
theorem rayleigh_jeans_mean (K : Finset ι) (f : ι → ℝ) (T c : ℝ) (hT : 0 < T) (hc : 0 < c) :
    (∑ k ∈ K, (T / (2 * c ^ 2)) * f k) / (∑ k ∈ K, (T / (2 * c ^ 2))) = (∑ k ∈ K, f k) / K.card := by
  have hw : (0 : ℝ) < T / (2 * c ^ 2) := by positivity
  rw [← Finset.mul_sum, Finset.sum_const, nsmul_eq_mul, mul_comm (K.card : ℝ), mul_div_mul_left _ _ hw.ne']

end FrictionKinetic
