/-
  ZeroSound.lean -- when does a Fermi liquid support undamped zero sound?

  Landau's collisionless kinetic equation for a Fermi liquid with a single Landau parameter `F` (= F₀ˢ)
  has a collective mode of phase velocity `s · v_F` when  `1 + F · Ω(s) = 0`, with Ω the angular average
  of the free response.  The mode is undamped iff `s > 1` (outside the particle-hole continuum); for
  `s < 1` it is Landau-damped -- the same mechanism as in a plasma, with `F` in place of `1/k²`.

  * 3D (bulk ³He):      Ω(s) = 1 - (s/2) log((s+1)/(s-1)),  condition  (s/2) log((s+1)/(s-1)) - 1 = 1/F.
  * 2D (³He monolayer): Ω(s) = 1 - s/√(s²-1).

  PROVED: in both dimensions an undamped root `s > 1` exists **iff** `F > 0`; in 2D the root is explicit,
  `s = (1+F)/√(1+2F)`.  This is textbook physics (Baym & Pethick, *Landau Fermi-Liquid Theory*); what is
  new is only that it is machine-checked.  The 2D case is included because the neutron-scattering
  measurement of a zero-sound-like mode by Godfrin et al., Nature 483, 576 (2012), is on a 2D film, where
  the logarithmic 3D formula does not apply.

  NOT proved: uniqueness of the 3D root (needs strict monotonicity); anything about `F₁ˢ`, finite
  temperature, or the damped branch `s < 1`.
-/
import Mathlib

open Real Set

namespace QuantumFluids.ZeroSound

/-- `g(s) = (s/2) log((s+1)/(s-1)) - 1`; the 3D zero-sound condition is `g s = 1/F`. -/
noncomputable def g3 (s : ℝ) : ℝ := s / 2 * log ((s + 1) / (s - 1)) - 1

theorem g3_pos {s : ℝ} (hs : 1 < s) : 0 < g3 s := by
  have h1 : 0 < s - 1 := by linarith
  have hx : 0 < 2 / (s - 1) := by positivity
  have h := lt_log_one_add_of_pos hx
  have e1 : 1 + 2 / (s - 1) = (s + 1) / (s - 1) := by field_simp; ring
  have e2 : 2 * (2 / (s - 1)) / (2 / (s - 1) + 2) = 2 / s := by field_simp; ring
  rw [e1, e2] at h
  unfold g3
  have : s / 2 * (2 / s) < s / 2 * log ((s + 1) / (s - 1)) :=
    mul_lt_mul_of_pos_left h (by linarith)
  have e3 : s / 2 * (2 / s) = 1 := by field_simp
  linarith

theorem g3_le {s : ℝ} (hs : 1 < s) : g3 s ≤ 1 / (s - 1) := by
  have h1 : 0 < s - 1 := by linarith
  have hy : 0 < (s + 1) / (s - 1) := by positivity
  have h := log_le_sub_one_of_pos hy
  have e1 : (s + 1) / (s - 1) - 1 = 2 / (s - 1) := by field_simp; ring
  rw [e1] at h
  unfold g3
  have : s / 2 * log ((s + 1) / (s - 1)) ≤ s / 2 * (2 / (s - 1)) :=
    mul_le_mul_of_nonneg_left h (by linarith)
  have e2 : s / 2 * (2 / (s - 1)) - 1 = 1 / (s - 1) := by field_simp; ring
  linarith

theorem g3_ge {s : ℝ} (hs : 1 < s) : 1 / 2 * log (2 / (s - 1)) - 1 ≤ g3 s := by
  have h1 : 0 < s - 1 := by linarith
  have hmono : log (2 / (s - 1)) ≤ log ((s + 1) / (s - 1)) :=
    log_le_log (div_pos two_pos h1) (by gcongr; linarith)
  have hnn : 0 ≤ log ((s + 1) / (s - 1)) :=
    log_nonneg (by rw [le_div_iff₀ h1]; linarith)
  unfold g3
  nlinarith

theorem continuousOn_g3 {a b : ℝ} (ha : 1 < a) : ContinuousOn g3 (Icc a b) := by
  unfold g3
  have hne : ∀ x ∈ Icc a b, x - 1 ≠ 0 := fun x hx => by have := hx.1; intro h; linarith
  have hne' : ∀ x ∈ Icc a b, (x + 1) / (x - 1) ≠ 0 := fun x hx => by
    have := hx.1
    have h1 : 0 < x - 1 := by linarith
    have : 0 < (x + 1) / (x - 1) := div_pos (by linarith) h1
    exact this.ne'
  refine ContinuousOn.sub (ContinuousOn.mul (by fun_prop) (ContinuousOn.log ?_ hne')) continuousOn_const
  exact ContinuousOn.div (by fun_prop) (by fun_prop) hne

/-- **Undamped zero sound in 3D exists iff the interaction is repulsive.** -/
theorem zero_sound_iff (F : ℝ) : (∃ s, 1 < s ∧ g3 s = 1 / F) ↔ 0 < F := by
  constructor
  · rintro ⟨s, hs, h⟩
    have := g3_pos hs
    rw [h] at this
    exact one_div_pos.mp this
  · intro hF
    obtain ⟨c, hc⟩ : ∃ c, c = 1 / F := ⟨_, rfl⟩
    have hcpos : 0 < c := by rw [hc]; positivity
    obtain ⟨lo, hlo⟩ : ∃ lo, lo = 1 + 2 * exp (-(2 * (c + 2))) := ⟨_, rfl⟩
    obtain ⟨hi, hhi⟩ : ∃ hi, hi = 1 + 2 / c := ⟨_, rfl⟩
    rw [← hc]
    have hlo1 : 1 < lo := by have := exp_pos (-(2 * (c + 2))); linarith
    have hhi1 : 1 < hi := by
      have : 0 < 2 / c := by positivity
      linarith
    have hexp : exp (-(2 * (c + 2))) ≤ 1 / c := by
      rw [exp_neg, inv_eq_one_div]
      apply one_div_le_one_div_of_le hcpos
      have := add_one_le_exp (2 * (c + 2))
      linarith
    have hle : lo ≤ hi := by
      have : 2 * exp (-(2 * (c + 2))) ≤ 2 / c := by
        have : 2 / c = 2 * (1 / c) := by ring
        rw [this]; linarith
      linarith
    have hglo : c ≤ g3 lo := by
      have h := g3_ge hlo1
      have e : 2 / (lo - 1) = exp (2 * (c + 2)) := by
        have h1 : lo - 1 = 2 * (exp (2 * (c + 2)))⁻¹ := by rw [hlo, exp_neg]; ring
        have := exp_pos (2 * (c + 2))
        rw [h1]; field_simp
      rw [e, log_exp] at h
      linarith
    have hghi : g3 hi ≤ c := by
      have h := g3_le hhi1
      have e : 1 / (hi - 1) = c / 2 := by
        have h1 : hi - 1 = 2 / c := by rw [hhi]; ring
        rw [h1, one_div_div]
      rw [e] at h
      linarith
    obtain ⟨s, hs, hgs⟩ := intermediate_value_Icc' hle (continuousOn_g3 (b := hi) hlo1) ⟨hghi, hglo⟩
    exact ⟨s, lt_of_lt_of_le hlo1 hs.1, hgs⟩

/-- **Undamped zero sound in 2D exists iff the interaction is repulsive**, and the root is explicit. -/
theorem zero_sound_2d_iff (F : ℝ) :
    (∃ s, 1 < s ∧ 1 + F * (1 - s / √(s ^ 2 - 1)) = 0) ↔ 0 < F := by
  constructor
  · rintro ⟨s, hs, h⟩
    have hpos : 0 < s ^ 2 - 1 := by nlinarith
    have hsq : 0 < √(s ^ 2 - 1) := sqrt_pos.mpr hpos
    have hlt : √(s ^ 2 - 1) < s := by
      rw [sqrt_lt' (by linarith)]; linarith
    have hr : 1 < s / √(s ^ 2 - 1) := by rw [lt_div_iff₀ hsq]; linarith
    by_contra hF
    rw [not_lt] at hF
    nlinarith [mul_nonneg_of_nonpos_of_nonpos hF (by linarith : 1 - s / √(s ^ 2 - 1) ≤ 0)]
  · intro hF
    exact ⟨(1 + F) / √(1 + 2 * F), (zero_sound_2d_root hF).1, (zero_sound_2d_root hF).2⟩
where
  zero_sound_2d_root {F : ℝ} (hF : 0 < F) :
      1 < (1 + F) / √(1 + 2 * F) ∧
        1 + F * (1 - (1 + F) / √(1 + 2 * F) / √(((1 + F) / √(1 + 2 * F)) ^ 2 - 1)) = 0 := by
    have hq0 : 0 < 1 + 2 * F := by linarith
    have hq : 0 < √(1 + 2 * F) := sqrt_pos.mpr hq0
    have hq2 : √(1 + 2 * F) ^ 2 = 1 + 2 * F := sq_sqrt hq0.le
    have h1 : 1 < (1 + F) / √(1 + 2 * F) := by
      rw [lt_div_iff₀ hq, one_mul, sqrt_lt' (by linarith)]; nlinarith
    refine ⟨h1, ?_⟩
    have e : ((1 + F) / √(1 + 2 * F)) ^ 2 - 1 = (F / √(1 + 2 * F)) ^ 2 := by
      rw [div_pow, div_pow, hq2]; field_simp; ring
    rw [e, sqrt_sq (by positivity)]
    field_simp
    ring

end QuantumFluids.ZeroSound

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.ZeroSound.g3_pos
#print axioms QuantumFluids.ZeroSound.g3_le
#print axioms QuantumFluids.ZeroSound.g3_ge
#print axioms QuantumFluids.ZeroSound.continuousOn_g3
#print axioms QuantumFluids.ZeroSound.zero_sound_iff
#print axioms QuantumFluids.ZeroSound.zero_sound_2d_iff
