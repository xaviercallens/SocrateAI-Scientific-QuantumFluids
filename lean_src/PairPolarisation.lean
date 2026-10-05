/-
  PairPolarisation.lean -- companion of docs/designs/PGPE_DIELECTRIC_PREREG.md (finite-k dielectric relation).

  For `N` vortex-antivortex pairs, `p i` the `+` and `m i` the `−` member, `d i = p i − m i`, the vortex charge
  density at wavevector `k` is `rho k = Σ_i (e^{i k·p_i} − e^{i k·m_i})`.

  * `norm_rho_le_pairs`: `‖rho k‖ ≤ ‖k‖ Σ ‖d_i‖` -- hence `≤ ‖k‖ N a` for pairs of size at most `a`.
  * `rho_polarisation`: when `|k·d_i| ≤ 1` for every pair,
        ‖rho k − i Σ_i (k·d_i) e^{i k·m_i}‖ ≤ Σ_i (k·d_i)² ≤ ‖k‖² Σ ‖d_i‖².
    The charge density of bound pairs is `i k·P(k)`, `P(k) = Σ d_i e^{i k·m_i}` the Fourier component of the
    polarisation density, up to an explicit second-order remainder. This is the dictionary between vortex
    positions and the dielectric response at finite wavevector that the pre-registration tests.
  * `response_ceiling`: the point-vortex transverse response `(2π)²‖rho‖²/‖k‖²` of bound pairs is at most
    `(2π)² (Σ‖d_i‖)²`, a bound that does not depend on `k`: a response above it at wavevector `k` certifies
    that the configuration is not a gas of pairs of the assumed sizes (the box-scale-charge signature of
    PGPE_ONSAGER_RESULTS.md, now with the bound-pair contribution made explicit).

  Self-contained (does not import MatchingScreening.lean, which proves the matching form of the first bound).
-/
import Mathlib

open Complex Finset

namespace PairPolarisation

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- plane wave `e^{i⟪k, r⟫}` -/
noncomputable def wave (k r : E) : ℂ := exp (I * ((inner ℝ k r : ℝ) : ℂ))

/-- charge density of `N` pairs -/
noncomputable def rho {N : ℕ} (k : E) (p m : Fin N → E) : ℂ := ∑ i, (wave k (p i) - wave k (m i))

lemma norm_wave (k r : E) : ‖wave k r‖ = 1 := Complex.norm_exp_I_mul_ofReal _

/-- one pair: `e^{ik·p} − e^{ik·m} = e^{ik·m}(e^{i k·(p − m)} − 1)` -/
lemma pair_factor (k p m : E) :
    wave k p - wave k m = wave k m * (exp (I * ((inner ℝ k (p - m) : ℝ) : ℂ)) - 1) := by
  unfold wave
  rw [mul_sub, mul_one, ← Complex.exp_add, inner_sub_right]
  congr 2
  push_cast; ring

lemma norm_pair_le (k p m : E) : ‖wave k p - wave k m‖ ≤ ‖k‖ * ‖p - m‖ := by
  rw [pair_factor, norm_mul, norm_wave, one_mul]
  calc ‖exp (I * ((inner ℝ k (p - m) : ℝ) : ℂ)) - 1‖ ≤ ‖(inner ℝ k (p - m) : ℝ)‖ :=
        Real.norm_exp_I_mul_ofReal_sub_one_le
    _ = |inner ℝ k (p - m)| := Real.norm_eq_abs _
    _ ≤ ‖k‖ * ‖p - m‖ := abs_real_inner_le_norm _ _

/-- The charge density of pairs is bounded by `‖k‖` times the total pair length. -/
theorem norm_rho_le_pairs {N : ℕ} (k : E) (p m : Fin N → E) :
    ‖rho k p m‖ ≤ ‖k‖ * ∑ i, ‖p i - m i‖ := by
  unfold rho
  rw [mul_sum]
  exact (norm_sum_le _ _).trans (sum_le_sum fun i _ => norm_pair_le k _ _)

/-- Pairs of size at most `a`: `‖rho k‖ ≤ ‖k‖ N a`. -/
theorem norm_rho_le_of_size {N : ℕ} (k : E) (p m : Fin N → E) {a : ℝ} (ha : ∀ i, ‖p i - m i‖ ≤ a) :
    ‖rho k p m‖ ≤ ‖k‖ * (N * a) := by
  refine (norm_rho_le_pairs k p m).trans (mul_le_mul_of_nonneg_left ?_ (norm_nonneg k))
  calc ∑ i, ‖p i - m i‖ ≤ ∑ _i : Fin N, a := sum_le_sum fun i _ => ha i
    _ = N * a := by rw [sum_const, card_univ, Fintype.card_fin, nsmul_eq_mul]

/-- Polarisation form with explicit remainder. -/
theorem rho_polarisation {N : ℕ} (k : E) (p m : Fin N → E)
    (hk : ∀ i, |inner ℝ k (p i - m i)| ≤ 1) :
    ‖rho k p m - I * ∑ i, ((inner ℝ k (p i - m i) : ℝ) : ℂ) * wave k (m i)‖
      ≤ ∑ i, (inner ℝ k (p i - m i)) ^ 2 := by
  have hterm : ∀ i, ‖(wave k (p i) - wave k (m i)) - I * (((inner ℝ k (p i - m i) : ℝ) : ℂ) * wave k (m i))‖
      ≤ (inner ℝ k (p i - m i)) ^ 2 := by
    intro i
    set x : ℝ := inner ℝ k (p i - m i) with hx
    have hfac : (wave k (p i) - wave k (m i)) - I * ((x : ℂ) * wave k (m i))
        = wave k (m i) * (exp (I * (x : ℂ)) - 1 - I * (x : ℂ)) := by
      rw [pair_factor]; ring
    rw [hfac, norm_mul, norm_wave, one_mul]
    have hnorm : ‖I * (x : ℂ)‖ = |x| := by simp
    have := Complex.norm_exp_sub_one_sub_id_le (x := I * (x : ℂ)) (by rw [hnorm]; exact hk i)
    rw [hnorm, sq_abs] at this
    exact this
  have hsum : rho k p m - I * ∑ i, ((inner ℝ k (p i - m i) : ℝ) : ℂ) * wave k (m i)
      = ∑ i, ((wave k (p i) - wave k (m i)) - I * (((inner ℝ k (p i - m i) : ℝ) : ℂ) * wave k (m i))) := by
    unfold rho
    rw [mul_sum]
    simp only [sum_sub_distrib]
  rw [hsum]
  exact (norm_sum_le _ _).trans (sum_le_sum fun i _ => hterm i)

/-- The remainder is second order in `‖k‖`. -/
theorem remainder_le {N : ℕ} (k : E) (p m : Fin N → E) :
    ∑ i, (inner ℝ k (p i - m i)) ^ 2 ≤ ‖k‖ ^ 2 * ∑ i, ‖p i - m i‖ ^ 2 := by
  rw [mul_sum]
  refine sum_le_sum fun i _ => ?_
  have h := abs_real_inner_le_norm k (p i - m i)
  calc (inner ℝ k (p i - m i)) ^ 2 = |inner ℝ k (p i - m i)| ^ 2 := (sq_abs _).symm
    _ ≤ (‖k‖ * ‖p i - m i‖) ^ 2 := pow_le_pow_left₀ (abs_nonneg _) h 2
    _ = ‖k‖ ^ 2 * ‖p i - m i‖ ^ 2 := by ring

/-- The point-vortex transverse response of bound pairs has a ceiling that does not depend on `k`. -/
theorem response_ceiling {N : ℕ} (k : E) (hk : k ≠ 0) (p m : Fin N → E) :
    (2 * Real.pi) ^ 2 * ‖rho k p m‖ ^ 2 / ‖k‖ ^ 2 ≤ (2 * Real.pi) ^ 2 * (∑ i, ‖p i - m i‖) ^ 2 := by
  have hkpos : 0 < ‖k‖ := norm_pos_iff.mpr hk
  have h := norm_rho_le_pairs k p m
  have hsq : ‖rho k p m‖ ^ 2 ≤ (‖k‖ * ∑ i, ‖p i - m i‖) ^ 2 := pow_le_pow_left₀ (norm_nonneg _) h 2
  rw [div_le_iff₀ (by positivity)]
  nlinarith [sq_nonneg (2 * Real.pi)]

/-! ### Concrete instance and negative control (E = ℝ, one pair of size 1, k = 1) -/

/-- `rho = e^{i} − 1` for the pair `p = 1`, `m = 0` at `k = 1`; the polarisation term is `i`. The remainder
bound `‖e^{i} − 1 − i‖ ≤ 1` holds ... -/
example : ‖rho (E := ℝ) (N := 1) 1 (fun _ => 1) (fun _ => 0)
    - I * ∑ i : Fin 1, ((inner ℝ (1 : ℝ) ((fun _ => (1 : ℝ)) i - (fun _ => (0 : ℝ)) i) : ℝ) : ℂ)
      * wave (1 : ℝ) ((fun _ => (0 : ℝ)) i)‖ ≤ ∑ i : Fin 1, (inner ℝ (1 : ℝ) ((fun _ => (1 : ℝ)) i - (fun _ => (0 : ℝ)) i)) ^ 2 :=
  rho_polarisation 1 _ _ (by intro i; simp)

/-- ... and the first-order term cannot be dropped: without it the "remainder" would have to bound `‖rho‖`
by a quantity of second order, which fails for a short pair (here `k = 1/2`: `‖e^{i/2} − 1‖ > 1/4`). -/
example : ¬ (‖Complex.exp (I * ((1 / 2 : ℝ) : ℂ)) - 1‖ ≤ (1 / 2 : ℝ) ^ 2) := by
  rw [Complex.norm_exp_I_mul_ofReal_sub_one]
  have e : (1 / 2 : ℝ) / 2 = 1 / 4 := by norm_num
  rw [e]
  have h : (1 / 4 : ℝ) - (1 / 4) ^ 3 / 6 < Real.sin (1 / 4) := Real.sin_gt_sub_cube (by norm_num)
  have hpos : 0 < Real.sin (1 / 4) := by
    have : (0 : ℝ) < 1 / 4 - (1 / 4) ^ 3 / 6 := by norm_num
    linarith
  rw [Real.norm_eq_abs, abs_of_pos (by positivity)]
  intro hle
  norm_num at h hle
  linarith

end PairPolarisation
