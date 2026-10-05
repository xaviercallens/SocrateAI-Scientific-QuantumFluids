/-
  MatchingScreening.lean -- the vortex-charge structure factor certifies a long vortex-antivortex matching.

  Context: `docs/designs/PGPE_ONSAGER_RESULTS.md`. The negative-stiffness states of round 3 differ from the
  healthy ones by an O(1) residual of the vortex charge density at the longest wavelengths of the box,
  `rho_q(k) = Σ_{+} e^{i k·r} - Σ_{-} e^{i k·r}`, and the transverse current those vortices drive,
  `|v_T(k)| = 2π |rho_q(k)| / |k|`, accounts for the measured one (Pearson 0.996, post hoc). The reading
  given there -- "about one vortex-antivortex pair separated by a distance comparable to L" -- is turned
  here into a theorem that holds for EVERY configuration, with no model of the vortex gas:

  * `norm_rho_le_matching`: for any pairing `σ` of the N positive to the N negative vortices,
      ‖rho_q(k)‖ ≤ ‖k‖ · Σ_i ‖p_i - m_{σ i}‖.
    Hence the cheapest pairing -- the optimal transport cost W₁ between the two sign populations -- is at
    least ‖rho_q(k)‖ / ‖k‖ (`matching_lower_bound`); and some pair is at least that long divided by N
    (`exists_long_pair`). With |rho_q(k₁)|² ≈ 1 at |k₁| = 2π/L, every pairing has total length ≥ L/(2π).
  * `norm_rho_le_matching_torus`: the same on the torus, with each separation replaced by any lattice-shifted
    representative (so: the minimum-image distance), for k in the reciprocal lattice (⟪k, t⟫ ∈ 2πℤ).
  * `pointVortex_transverse` / `pointVortex_norm_sq`: the Fourier-side velocity of point vortices,
    v̂ = 2π i rho (-k₂, k₁)/|k|², is transverse (k·v̂ = 0) with |v̂|² = (2π)²|rho|²/|k|² -- the formula
    behind the post-hoc vortex-only transverse current.

  Together with `WassersteinCertificate.lean` (a dual-feasible certificate is an UPPER bound on the optimal
  matching cost's optimality gap, and certifies a matching optimal) this brackets the matching cost from
  both sides. Elementary; no claim of new mathematics: the content is that the diagnostic is geometry.
-/
import Mathlib

open Complex Finset

namespace MatchingScreening

/-- `e^{ia}` is 1-Lipschitz in `a`. -/
lemma norm_exp_sub_exp_le (a b : ℝ) :
    ‖exp (I * (a : ℂ)) - exp (I * (b : ℂ))‖ ≤ |a - b| := by
  have h : exp (I * (a : ℂ)) - exp (I * (b : ℂ)) = exp (I * (b : ℂ)) * (exp (I * ((a - b : ℝ) : ℂ)) - 1) := by
    rw [mul_sub, mul_one, ← Complex.exp_add]; congr 2; push_cast; ring
  rw [h, norm_mul, Complex.norm_exp_I_mul_ofReal, one_mul]
  simpa [Real.norm_eq_abs] using (Real.norm_exp_I_mul_ofReal_sub_one_le (x := a - b))

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- The plane-wave phase of a point, `e^{i⟪k, r⟫}`. -/
noncomputable def wave (k r : E) : ℂ := exp (I * ((inner ℝ k r : ℝ) : ℂ))

/-- The vortex charge density at wavevector `k` for `N` positive vortices at `p` and `N` negative at `m`. -/
noncomputable def rho {N : ℕ} (k : E) (p m : Fin N → E) : ℂ :=
  ∑ i, wave k (p i) - ∑ j, wave k (m j)

lemma norm_wave_sub_le (k r s : E) : ‖wave k r - wave k s‖ ≤ ‖k‖ * ‖r - s‖ := by
  unfold wave
  calc _ ≤ |inner ℝ k r - inner ℝ k s| := norm_exp_sub_exp_le _ _
    _ = |inner ℝ k (r - s)| := by rw [inner_sub_right]
    _ ≤ ‖k‖ * ‖r - s‖ := abs_real_inner_le_norm _ _

/-- Main bound: the charge density at `k` is controlled by ANY pairing's total length. -/
theorem norm_rho_le_matching {N : ℕ} (k : E) (p m : Fin N → E) (σ : Fin N ≃ Fin N) :
    ‖rho k p m‖ ≤ ‖k‖ * ∑ i, ‖p i - m (σ i)‖ := by
  have hre : rho k p m = ∑ i, (wave k (p i) - wave k (m (σ i))) := by
    unfold rho; rw [sum_sub_distrib, Equiv.sum_comp σ (fun j => wave k (m j))]
  rw [hre, mul_sum]
  exact (norm_sum_le _ _).trans (sum_le_sum fun i _ => norm_wave_sub_le k _ _)

/-- The optimal matching cost is at least `‖rho‖ / ‖k‖`. -/
theorem matching_lower_bound {N : ℕ} (k : E) (hk : k ≠ 0) (p m : Fin N → E) (σ : Fin N ≃ Fin N) :
    ‖rho k p m‖ / ‖k‖ ≤ ∑ i, ‖p i - m (σ i)‖ := by
  rw [div_le_iff₀ (norm_pos_iff.mpr hk), mul_comm]
  exact norm_rho_le_matching k p m σ

/-- In every pairing some pair is at least `‖rho‖ / (N ‖k‖)` long. -/
theorem exists_long_pair {N : ℕ} (hN : 0 < N) (k : E) (hk : k ≠ 0) (p m : Fin N → E)
    (σ : Fin N ≃ Fin N) : ∃ i, ‖rho k p m‖ / (N * ‖k‖) ≤ ‖p i - m (σ i)‖ := by
  by_contra h
  push Not at h
  have hlt : ∑ i, ‖p i - m (σ i)‖ < ∑ _i : Fin N, ‖rho k p m‖ / (N * ‖k‖) :=
    sum_lt_sum_of_nonempty (univ_nonempty_iff.mpr ⟨⟨0, hN⟩⟩) fun i _ => h i
  have hNne : (N : ℝ) ≠ 0 := by exact_mod_cast hN.ne'
  have heq : ∑ _i : Fin N, ‖rho k p m‖ / (N * ‖k‖) = ‖rho k p m‖ / ‖k‖ := by
    rw [sum_const, card_univ, Fintype.card_fin, nsmul_eq_mul]
    have : ‖k‖ ≠ 0 := norm_ne_zero_iff.mpr hk
    field_simp
  rw [heq] at hlt
  exact absurd (matching_lower_bound k hk p m σ) (not_le.mpr hlt)

/-- A lattice shift that `k` sees as a multiple of `2π` does not change the plane wave. -/
lemma wave_add_period (k r t : E) (n : ℤ) (ht : inner ℝ k t = 2 * Real.pi * n) :
    wave k (r + t) = wave k r := by
  unfold wave
  rw [inner_add_right, ht]
  have : I * (((inner ℝ k r + 2 * Real.pi * n : ℝ)) : ℂ) = I * ((inner ℝ k r : ℝ) : ℂ) + n * (2 * Real.pi * I) := by
    push_cast; ring
  rw [this, Complex.exp_add, Complex.exp_int_mul_two_pi_mul_I, mul_one]

/-- Torus version: each separation may be replaced by any representative shifted by a period `t i` of `k`
(so in particular by the minimum-image separation). -/
theorem norm_rho_le_matching_torus {N : ℕ} (k : E) (p m : Fin N → E) (σ : Fin N ≃ Fin N)
    (t : Fin N → E) (ht : ∀ i, ∃ n : ℤ, inner ℝ k (t i) = 2 * Real.pi * n) :
    ‖rho k p m‖ ≤ ‖k‖ * ∑ i, ‖p i - (m (σ i) + t i)‖ := by
  have hre : rho k p m = ∑ i, (wave k (p i) - wave k (m (σ i) + t i)) := by
    unfold rho; rw [sum_sub_distrib]
    congr 1
    calc ∑ j, wave k (m j) = ∑ i, wave k (m (σ i)) := (Equiv.sum_comp σ (fun j => wave k (m j))).symm
      _ = ∑ i, wave k (m (σ i) + t i) := sum_congr rfl fun i _ => by
          obtain ⟨n, hn⟩ := ht i; exact (wave_add_period k _ _ n hn).symm
  rw [hre, mul_sum]
  exact (norm_sum_le _ _).trans (sum_le_sum fun i _ => norm_wave_sub_le k _ _)

/-! ### The point-vortex velocity in Fourier space (k ∈ ℝ², k ≠ 0) -/

/-- `v̂ = 2π i rho (-k₂, k₁) / |k|²`, components as complex numbers. -/
noncomputable def vhat (k₁ k₂ : ℝ) (r : ℂ) : ℂ × ℂ :=
  (2 * Real.pi * I * r * (-k₂) / (k₁ ^ 2 + k₂ ^ 2), 2 * Real.pi * I * r * k₁ / (k₁ ^ 2 + k₂ ^ 2))

/-- The point-vortex flow is transverse: `k · v̂ = 0`. -/
theorem pointVortex_transverse (k₁ k₂ : ℝ) (r : ℂ) :
    (k₁ : ℂ) * (vhat k₁ k₂ r).1 + (k₂ : ℂ) * (vhat k₁ k₂ r).2 = 0 := by
  unfold vhat; simp only; ring

/-- `|v̂|² = (2π)² |rho|² / |k|²`. -/
theorem pointVortex_norm_sq (k₁ k₂ : ℝ) (hk : k₁ ^ 2 + k₂ ^ 2 ≠ 0) (r : ℂ) :
    ‖(vhat k₁ k₂ r).1‖ ^ 2 + ‖(vhat k₁ k₂ r).2‖ ^ 2 = (2 * Real.pi) ^ 2 * ‖r‖ ^ 2 / (k₁ ^ 2 + k₂ ^ 2) := by
  have hk' : (0 : ℝ) < k₁ ^ 2 + k₂ ^ 2 := lt_of_le_of_ne (by positivity) (Ne.symm hk)
  have hc : ((k₁ ^ 2 + k₂ ^ 2 : ℝ) : ℂ) = (k₁ : ℂ) ^ 2 + (k₂ : ℂ) ^ 2 := by push_cast; ring
  unfold vhat
  simp only [norm_div, norm_mul, norm_neg, Complex.norm_I, Complex.norm_real, Real.norm_eq_abs, ← hc,
    mul_one, Complex.norm_ofNat]
  rw [abs_of_pos hk', abs_of_pos Real.pi_pos]
  field_simp
  rw [sq_abs, sq_abs]; ring

/-! ### Concrete instance and negative control (E = ℝ, one pair) -/

/-- One `+` vortex at `1`, one `-` at `0`, `k = π`: `rho = e^{iπ} - 1 = -2`. -/
lemma rho_one_pair : rho (E := ℝ) (N := 1) Real.pi (fun _ => 1) (fun _ => 0) = -2 := by
  have h : I * ((Real.pi : ℝ) : ℂ) = (Real.pi : ℂ) * I := mul_comm _ _
  simp [rho, wave, h, Complex.exp_pi_mul_I]
  norm_num

/-- The bound holds on it with room (`2 ≤ π · 1`) ... -/
example : ‖rho (E := ℝ) (N := 1) Real.pi (fun _ => 1) (fun _ => 0)‖ ≤ ‖(Real.pi : ℝ)‖ * 1 := by
  rw [rho_one_pair, norm_neg, Real.norm_eq_abs, abs_of_pos Real.pi_pos]; norm_num
  linarith [Real.pi_gt_three]

/-- ... and the matching length cannot be dropped: a "pairing of length 0" bound is false here. -/
example : ¬ ‖rho (E := ℝ) (N := 1) Real.pi (fun _ => 1) (fun _ => 0)‖ ≤ ‖(Real.pi : ℝ)‖ * 0 := by
  rw [rho_one_pair, mul_zero]; norm_num

end MatchingScreening
