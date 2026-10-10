/-
Ch05_BogoliubovDispersion.lean -- NEW for the book "Quantum Fluids in Lean 4: a tribute to Henri Godfrin", chapter 5.

The Bogoliubov spectrum of a weakly interacting Bose gas (units hbar = 1),

      eps(k) = sqrt( c^2 k^2 + (k^2 / (2 m))^2 ),         c = sound speed, m = particle mass,

is the simplest dispersion relation that is linear at small k (a phonon) and quadratic at large k (a free
particle). This file proves, with no `sorry` and only the standard axioms:

  * basic facts: eps(0) = 0, eps >= 0, eps > 0 for k > 0, even in k, strictly increasing on [0, oo);
  * two-sided polynomial bounds for k >= 0
        phononDisp c a k - c a^2 k^5 / 2  <=  eps(k)  <=  phononDisp c a k,      a = 1 / (8 m^2 c^2),
    where `phononDisp c a k = c k (1 + a k^2)` is the low-k dispersion of `HeliumKinematics` (copied verbatim below);
  * the sound speed limit eps(k)/k -> c  and the curvature coefficient
        (eps(k)/(c k) - 1) / k^2  ->  a = 1/(8 m^2 c^2)  (> 0, anomalous dispersion)  as k -> 0+;
  * the Landau critical velocity of this spectrum, inf_{k>0} eps(k)/k, equals c (and is not attained);
  * the exact three-phonon statement: eps(k1) + eps(k2) < eps(k1 + k2) for all k1, k2 > 0 (no critical wave
    vector: the Bogoliubov spectrum is anomalous at every k), and the link to
    `QuantumFluids.HeliumKinematics.three_phonon_open_iff` through the low-k form with a = 1/(8 m^2 c^2) > 0;
  * the absolute error band |eps(k) - phononDisp c a k| <= c a^2 k^5 / 2 (the band the solver chapter draws);
  * the derivative-free form of "the group velocity exceeds the sound speed": eps(k) - c k is strictly increasing
    on [0, oo) (the ripples of a dispersive pulse outrun sound);
  * the universal form eps(k)/(c k) = sqrt(1 + (k/(2 m c))^2), and the Gross-Pitaevskii parameter dictionary
    (hbar = m = 1, c^2 = g n0): eps^2 = (1/2) k^2 ((1/2) k^2 + 2 g n0), the formula of the solver's known answer K5.

Scope: this is the MATHEMATICAL statement about the Bogoliubov formula. Gross-Pitaevskii theory has no roton and
this file says nothing about helium II.
-/
import Mathlib

open Filter Topology

namespace QuantumFluids.BogoliubovDispersion

/-! ## Definitions -/

/-- The Bogoliubov spectrum `sqrt (c² k² + (k²/(2m))²)`, with `hbar = 1`. -/
noncomputable def bogEps (c m k : ℝ) : ℝ := Real.sqrt (c ^ 2 * k ^ 2 + (k ^ 2 / (2 * m)) ^ 2)

/-- The curvature coefficient `α₂ = 1/(8 m² c²)` of the Bogoliubov spectrum (`ε ≈ c k (1 + α₂ k²)`). -/
noncomputable def alpha2 (c m : ℝ) : ℝ := 1 / (8 * m ^ 2 * c ^ 2)

/-- Verbatim copy of `QuantumFluids.HeliumKinematics.phononDisp`: `ε(k) = c k (1 + a k²)`. -/
def phononDisp (c a k : ℝ) : ℝ := c * k * (1 + a * k ^ 2)

/-! ## 1. Basic properties -/

theorem bogEps_sq (c m k : ℝ) :
    bogEps c m k ^ 2 = c ^ 2 * k ^ 2 + (k ^ 2 / (2 * m)) ^ 2 :=
  Real.sq_sqrt (by positivity)

theorem bogEps_zero (c m : ℝ) : bogEps c m 0 = 0 := by simp [bogEps]

theorem bogEps_nonneg (c m k : ℝ) : 0 ≤ bogEps c m k := Real.sqrt_nonneg _

theorem bogEps_pos {c m k : ℝ} (hc : 0 < c) (hk : 0 < k) : 0 < bogEps c m k :=
  Real.sqrt_pos.mpr (by positivity)

theorem bogEps_neg (c m k : ℝ) : bogEps c m (-k) = bogEps c m k := by
  simp only [bogEps, neg_sq]

/-- For `k ≥ 0`: `ε(k) = k · sqrt (c² + k²/(4m²))`, i.e. the phase velocity `ε/k` is `sqrt (c² + k²/(4m²))`. -/
theorem bogEps_eq_mul {c m k : ℝ} (hm : 0 < m) (hk : 0 ≤ k) :
    bogEps c m k = k * Real.sqrt (c ^ 2 + k ^ 2 / (4 * m ^ 2)) := by
  have h : c ^ 2 * k ^ 2 + (k ^ 2 / (2 * m)) ^ 2 = k ^ 2 * (c ^ 2 + k ^ 2 / (4 * m ^ 2)) := by
    field_simp; ring
  unfold bogEps
  rw [h, Real.sqrt_mul (sq_nonneg k), Real.sqrt_sq hk]

/-- **ε is strictly increasing on `[0, ∞)`.** -/
theorem bogEps_strictMonoOn {c m : ℝ} (hc : 0 < c) (hm : 0 < m) :
    StrictMonoOn (bogEps c m) (Set.Ici 0) := by
  intro a ha b hb hab
  have ha' : (0 : ℝ) ≤ a := ha
  have hab2 : a ^ 2 < b ^ 2 := by nlinarith
  have h1 : a ^ 2 / (2 * m) < b ^ 2 / (2 * m) := by gcongr
  have h2 : (a ^ 2 / (2 * m)) ^ 2 < (b ^ 2 / (2 * m)) ^ 2 :=
    pow_lt_pow_left₀ h1 (by positivity) (by norm_num)
  have h3 : c ^ 2 * a ^ 2 < c ^ 2 * b ^ 2 := mul_lt_mul_of_pos_left hab2 (by positivity)
  exact Real.sqrt_lt_sqrt (by positivity) (by linarith)

/-! ## 2. Two-sided bounds: the phonon branch and its first curvature correction -/

/-- The sound line is a lower bound: `c k ≤ ε(k)` (for every real `c`, `m`, `k`: it is `|c k| ≤ √(…)`). -/
theorem sound_line_le (c m k : ℝ) : c * k ≤ bogEps c m k := by
  have h : (c * k) ^ 2 ≤ c ^ 2 * k ^ 2 + (k ^ 2 / (2 * m)) ^ 2 := by
    nlinarith [sq_nonneg (k ^ 2 / (2 * m))]
  exact le_trans (le_abs_self _) (Real.abs_le_sqrt h)

private lemma eps_arg {c m k : ℝ} (hc : 0 < c) (hm : 0 < m) :
    c ^ 2 * k ^ 2 + (k ^ 2 / (2 * m)) ^ 2 = (c * k) ^ 2 * (1 + 2 * (alpha2 c m * k ^ 2)) := by
  unfold alpha2; field_simp; ring

/-- **Upper bound: `ε(k) ≤ c k (1 + α₂ k²)` with `α₂ = 1/(8 m² c²)`**, i.e. `ε ≤ phononDisp c α₂ k`. -/
theorem bogEps_le_phononDisp {c m k : ℝ} (hc : 0 < c) (hm : 0 < m) (hk : 0 ≤ k) :
    bogEps c m k ≤ phononDisp c (alpha2 c m) k := by
  have ha : 0 < alpha2 c m := by unfold alpha2; positivity
  unfold bogEps phononDisp
  rw [Real.sqrt_le_iff]
  refine ⟨by positivity, ?_⟩
  rw [eps_arg hc hm]
  have : (c * k) ^ 2 * (1 + 2 * (alpha2 c m * k ^ 2)) ≤ (c * k) ^ 2 * (1 + alpha2 c m * k ^ 2) ^ 2 := by
    apply mul_le_mul_of_nonneg_left _ (sq_nonneg _)
    nlinarith [sq_nonneg (alpha2 c m * k ^ 2)]
  calc _ ≤ _ := this
    _ = _ := by ring

private lemma aux_t {t : ℝ} (ht : 0 ≤ t) (hL : 0 ≤ 1 + t - t ^ 2 / 2) :
    (1 + t - t ^ 2 / 2) ^ 2 ≤ 1 + 2 * t := by
  have h4 : t ≤ 4 := by
    by_contra h
    push Not at h
    nlinarith
  nlinarith [mul_nonneg (pow_nonneg ht 3) (sub_nonneg.mpr h4)]

/-- **Lower bound: `c k (1 + α₂ k² - α₂² k⁴/2) ≤ ε(k)`.** Together with the upper bound this pins the
curvature coefficient: the error of `phononDisp c α₂` is `O(k⁵)`. -/
theorem phononDisp_sub_le_bogEps {c m k : ℝ} (hc : 0 < c) (hm : 0 < m) (hk : 0 ≤ k) :
    phononDisp c (alpha2 c m) k - c * (alpha2 c m) ^ 2 * k ^ 5 / 2 ≤ bogEps c m k := by
  have ha : 0 < alpha2 c m := by unfold alpha2; positivity
  set t := alpha2 c m * k ^ 2 with ht
  have ht0 : 0 ≤ t := by positivity
  have hform : phononDisp c (alpha2 c m) k - c * (alpha2 c m) ^ 2 * k ^ 5 / 2
      = (c * k) * (1 + t - t ^ 2 / 2) := by
    unfold phononDisp; rw [ht]; ring
  rw [hform]
  by_cases hL : 0 ≤ 1 + t - t ^ 2 / 2
  · have hsq : ((c * k) * (1 + t - t ^ 2 / 2)) ^ 2 ≤ c ^ 2 * k ^ 2 + (k ^ 2 / (2 * m)) ^ 2 := by
      rw [eps_arg hc hm, ← ht, mul_pow]
      exact mul_le_mul_of_nonneg_left (aux_t ht0 hL) (sq_nonneg _)
    exact le_trans (le_abs_self _) (Real.abs_le_sqrt hsq)
  · push Not at hL
    have : (c * k) * (1 + t - t ^ 2 / 2) ≤ 0 :=
      mul_nonpos_of_nonneg_of_nonpos (by positivity) hL.le
    exact le_trans this (bogEps_nonneg _ _ _)

/-! ## 3. The sound speed and the anomalous-dispersion coefficient -/

/-- **Sound speed limit.** `ε(k)/k → c` as `k → 0⁺`. -/
theorem sound_speed_limit {c m : ℝ} (hc : 0 < c) (hm : 0 < m) :
    Tendsto (fun k => bogEps c m k / k) (𝓝[>] 0) (𝓝 c) := by
  have hcont : Continuous fun k : ℝ => Real.sqrt (c ^ 2 + k ^ 2 / (4 * m ^ 2)) := by fun_prop
  have h0 : Real.sqrt (c ^ 2 + (0 : ℝ) ^ 2 / (4 * m ^ 2)) = c := by
    simp [Real.sqrt_sq hc.le]
  have ht : Tendsto (fun k : ℝ => Real.sqrt (c ^ 2 + k ^ 2 / (4 * m ^ 2))) (𝓝[>] 0) (𝓝 c) := by
    have := (hcont.tendsto 0).mono_left (nhdsWithin_le_nhds (s := Set.Ioi (0 : ℝ)))
    rwa [h0] at this
  refine ht.congr' ?_
  filter_upwards [self_mem_nhdsWithin] with k hk
  have hk' : (0 : ℝ) < k := hk
  rw [bogEps_eq_mul hm hk'.le]
  field_simp

/-- **The curvature coefficient is `α₂ = 1/(8 m² c²)`:**
`(ε(k)/(c k) − 1)/k² → 1/(8 m² c²)` as `k → 0⁺`. Since `α₂ > 0` the dispersion is anomalous
(upward curving), the sign condition of `HeliumKinematics.three_phonon_open_iff`. -/
theorem alpha2_limit {c m : ℝ} (hc : 0 < c) (hm : 0 < m) :
    Tendsto (fun k => (bogEps c m k / (c * k) - 1) / k ^ 2) (𝓝[>] 0) (𝓝 (alpha2 c m)) := by
  have hlow : Tendsto (fun k : ℝ => alpha2 c m - (alpha2 c m) ^ 2 * k ^ 2 / 2) (𝓝[>] 0) (𝓝 (alpha2 c m)) := by
    have hc' : Continuous fun k : ℝ => alpha2 c m - (alpha2 c m) ^ 2 * k ^ 2 / 2 := by fun_prop
    have := (hc'.tendsto 0).mono_left (nhdsWithin_le_nhds (s := Set.Ioi (0 : ℝ)))
    simpa using this
  refine tendsto_of_tendsto_of_tendsto_of_le_of_le' hlow tendsto_const_nhds ?_ ?_
  · filter_upwards [self_mem_nhdsWithin] with k hk
    have hk' : (0 : ℝ) < k := hk
    have h := phononDisp_sub_le_bogEps hc hm hk'.le
    unfold phononDisp at h
    have hck : 0 < c * k := by positivity
    have h1 : 1 + (alpha2 c m - alpha2 c m ^ 2 * k ^ 2 / 2) * k ^ 2 ≤ bogEps c m k / (c * k) := by
      rw [le_div_iff₀ hck]; nlinarith
    rw [le_div_iff₀ (by positivity : (0 : ℝ) < k ^ 2)]
    linarith
  · filter_upwards [self_mem_nhdsWithin] with k hk
    have hk' : (0 : ℝ) < k := hk
    have h := bogEps_le_phononDisp hc hm hk'.le
    unfold phononDisp at h
    have hck : 0 < c * k := by positivity
    have h2 : bogEps c m k / (c * k) ≤ 1 + alpha2 c m * k ^ 2 := by
      rw [div_le_iff₀ hck]; nlinarith
    rw [div_le_iff₀ (by positivity)]
    nlinarith

theorem alpha2_pos {c m : ℝ} (hc : 0 < c) (hm : 0 < m) : 0 < alpha2 c m := by
  unfold alpha2; positivity

/-! ## 4. Landau critical velocity -/

/-- Every phase velocity `ε(k)/k` of the Bogoliubov spectrum exceeds `c`, strictly. -/
theorem sound_lt_phase_velocity {c m k : ℝ} (hc : 0 < c) (hm : 0 < m) (hk : 0 < k) :
    c < bogEps c m k / k := by
  rw [bogEps_eq_mul hm hk.le, mul_div_cancel_left₀ _ hk.ne']
  have h1 : c ^ 2 < c ^ 2 + k ^ 2 / (4 * m ^ 2) := by
    have : 0 < k ^ 2 / (4 * m ^ 2) := by positivity
    linarith
  calc c = Real.sqrt (c ^ 2) := (Real.sqrt_sq hc.le).symm
    _ < Real.sqrt (c ^ 2 + k ^ 2 / (4 * m ^ 2)) := Real.sqrt_lt_sqrt (by positivity) h1

/-- **The Landau critical velocity of the Bogoliubov spectrum is the sound speed:**
`inf_{k>0} ε(k)/k = c` (`IsGLB`), and the infimum is not attained
(`sound_lt_phase_velocity`). For a free particle `ε = k²/(2m)` the same infimum is `0`
(`HeliumKinematics.landau_velocity_parabolic_zero`). -/
theorem landau_velocity_eq {c m : ℝ} (hc : 0 < c) (hm : 0 < m) :
    IsGLB ((fun k => bogEps c m k / k) '' Set.Ioi 0) c := by
  constructor
  · rintro _ ⟨k, hk, rfl⟩
    exact (sound_lt_phase_velocity hc hm hk).le
  · intro b hb
    by_contra hlt
    push Not at hlt
    have hev := (sound_speed_limit hc hm).eventually (gt_mem_nhds hlt)
    obtain ⟨k, hk, hkpos⟩ := (hev.and self_mem_nhdsWithin).exists
    have := hb ⟨k, hkpos, rfl⟩
    linarith

theorem landau_velocity_sInf {c m : ℝ} (hc : 0 < c) (hm : 0 < m) :
    sInf ((fun k => bogEps c m k / k) '' Set.Ioi 0) = c :=
  (landau_velocity_eq hc hm).csInf_eq ⟨_, ⟨1, by norm_num, rfl⟩⟩

/-! ## 5. Three-phonon processes: the exact statement and the link to `HeliumKinematics` -/

/-- **Exact collinear three-phonon statement for the Bogoliubov spectrum.** For all `k₁, k₂ > 0`,
`ε(k₁) + ε(k₂) < ε(k₁ + k₂)`: a phonon of wave number `k₁ + k₂` can always decay into collinear phonons
`k₁, k₂` energetically, at every wave number (no critical `k_c`; in helium a critical `k_c` exists because the real
dispersion bends over into the maxon). -/
theorem bogEps_superadditive {c m k₁ k₂ : ℝ} (hc : 0 < c) (hm : 0 < m) (h₁ : 0 < k₁) (h₂ : 0 < k₂) :
    bogEps c m k₁ + bogEps c m k₂ < bogEps c m (k₁ + k₂) := by
  have hs : 0 < k₁ + k₂ := by linarith
  rw [bogEps_eq_mul hm h₁.le, bogEps_eq_mul hm h₂.le, bogEps_eq_mul hm hs.le]
  have f1 : Real.sqrt (c ^ 2 + k₁ ^ 2 / (4 * m ^ 2)) < Real.sqrt (c ^ 2 + (k₁ + k₂) ^ 2 / (4 * m ^ 2)) := by
    apply Real.sqrt_lt_sqrt (by positivity)
    have : k₁ ^ 2 < (k₁ + k₂) ^ 2 := by nlinarith
    have : k₁ ^ 2 / (4 * m ^ 2) < (k₁ + k₂) ^ 2 / (4 * m ^ 2) := by gcongr
    linarith
  have f2 : Real.sqrt (c ^ 2 + k₂ ^ 2 / (4 * m ^ 2)) < Real.sqrt (c ^ 2 + (k₁ + k₂) ^ 2 / (4 * m ^ 2)) := by
    apply Real.sqrt_lt_sqrt (by positivity)
    have : k₂ ^ 2 < (k₁ + k₂) ^ 2 := by nlinarith
    have : k₂ ^ 2 / (4 * m ^ 2) < (k₁ + k₂) ^ 2 / (4 * m ^ 2) := by gcongr
    linarith
  nlinarith [mul_lt_mul_of_pos_left f1 h₁, mul_lt_mul_of_pos_left f2 h₂]

/-- Copy of `HeliumKinematics.three_phonon_excess` (proof identical). -/
theorem three_phonon_excess (c a k₁ k₂ : ℝ) :
    phononDisp c a (k₁ + k₂) - phononDisp c a k₁ - phononDisp c a k₂
      = 3 * c * a * k₁ * k₂ * (k₁ + k₂) := by
  unfold phononDisp; ring

/-- Copy of `HeliumKinematics.three_phonon_open_iff` (statement and proof identical): the sign of `a` decides. -/
theorem three_phonon_open_iff {c a k₁ k₂ : ℝ} (hc : 0 < c) (h₁ : 0 < k₁) (h₂ : 0 < k₂) :
    phononDisp c a k₁ + phononDisp c a k₂ ≤ phononDisp c a (k₁ + k₂) ↔ 0 ≤ a := by
  have hpos : 0 < 3 * c * k₁ * k₂ * (k₁ + k₂) := by positivity
  have key := three_phonon_excess c a k₁ k₂
  constructor
  · intro h
    have : 0 ≤ 3 * c * a * k₁ * k₂ * (k₁ + k₂) := by linarith
    by_contra hneg
    push Not at hneg
    nlinarith [mul_pos hpos (neg_pos.mpr hneg)]
  · intro ha
    have : 0 ≤ 3 * c * a * k₁ * k₂ * (k₁ + k₂) := by positivity
    linarith

/-- **The link.** The low-`k` form of the Bogoliubov spectrum is `phononDisp c α₂` with `α₂ = 1/(8m²c²) > 0`;
by `three_phonon_open_iff` (hypotheses `0 < c`, `0 < k₁`, `0 < k₂`) the collinear three-phonon channel is open,
and its energy excess is `3 c α₂ k₁ k₂ (k₁+k₂)` (`three_phonon_excess`). -/
theorem bogoliubov_lowk_three_phonon_open {c m k₁ k₂ : ℝ} (hc : 0 < c) (hm : 0 < m) (h₁ : 0 < k₁) (h₂ : 0 < k₂) :
    phononDisp c (alpha2 c m) k₁ + phononDisp c (alpha2 c m) k₂ ≤ phononDisp c (alpha2 c m) (k₁ + k₂) ∧
    phononDisp c (alpha2 c m) (k₁ + k₂) - phononDisp c (alpha2 c m) k₁ - phononDisp c (alpha2 c m) k₂
      = 3 * c * alpha2 c m * k₁ * k₂ * (k₁ + k₂) :=
  ⟨(three_phonon_open_iff hc h₁ h₂).mpr (alpha2_pos hc hm).le, three_phonon_excess c _ k₁ k₂⟩

/-! ## 6. The error band, the universal form, and the solver's parameter dictionary -/

/-- **Absolute error band of the low-`k` form.** `|ε(k) − c k (1 + α₂ k²)| ≤ c α₂² k⁵ / 2` for `k ≥ 0`
(an immediate consequence of the two-sided bounds). -/
theorem abs_bogEps_sub_phononDisp_le {c m k : ℝ} (hc : 0 < c) (hm : 0 < m) (hk : 0 ≤ k) :
    |bogEps c m k - phononDisp c (alpha2 c m) k| ≤ c * (alpha2 c m) ^ 2 * k ^ 5 / 2 := by
  have h1 := bogEps_le_phononDisp hc hm hk
  have h2 := phononDisp_sub_le_bogEps hc hm hk
  rw [abs_le]
  constructor <;> linarith

/-- **Short waves outrun sound.** The excess `ε(k) − c k` over the sound line is strictly increasing on `[0, ∞)`: for
`0 ≤ a < b`, `ε(b) − ε(a) > c (b − a)`. This is the derivative-free form of "the group velocity exceeds `c` at every
wave number", the reason the ripples of a localised pulse run ahead of the sound front. -/
theorem bogEps_sub_sound_strictMonoOn {c m : ℝ} (hc : 0 < c) (hm : 0 < m) :
    StrictMonoOn (fun k => bogEps c m k - c * k) (Set.Ici 0) := by
  intro a ha b _ hab
  have ha' : (0 : ℝ) ≤ a := ha
  have hb' : 0 < b := lt_of_le_of_lt ha' hab
  show bogEps c m a - c * a < bogEps c m b - c * b
  rw [bogEps_eq_mul hm ha', bogEps_eq_mul hm hb'.le]
  have f1 : Real.sqrt (c ^ 2 + a ^ 2 / (4 * m ^ 2)) < Real.sqrt (c ^ 2 + b ^ 2 / (4 * m ^ 2)) := by
    apply Real.sqrt_lt_sqrt (by positivity)
    have h1 : a ^ 2 < b ^ 2 := by nlinarith
    have h2 : a ^ 2 / (4 * m ^ 2) < b ^ 2 / (4 * m ^ 2) := by gcongr
    linarith
  have hnn : 0 ≤ a ^ 2 / (4 * m ^ 2) := by positivity
  have f0 : c ≤ Real.sqrt (c ^ 2 + a ^ 2 / (4 * m ^ 2)) := by
    calc c = Real.sqrt (c ^ 2) := (Real.sqrt_sq hc.le).symm
      _ ≤ Real.sqrt (c ^ 2 + a ^ 2 / (4 * m ^ 2)) := Real.sqrt_le_sqrt (by linarith)
  nlinarith [mul_pos hb' (sub_pos.mpr f1), mul_nonneg (sub_nonneg.mpr hab.le) (sub_nonneg.mpr f0)]

/-- **Universal form.** For `c, m, k > 0`: `ε(k)/(c k) = √(1 + (k/(2 m c))²)`. The phase velocity in units of the
sound speed depends on `k` only through `x = k/(2 m c)`; with `ħ` restored, `2 m c/ħ` is the one wave number of the
Bogoliubov problem. -/
theorem phase_velocity_universal {c m k : ℝ} (hc : 0 < c) (hm : 0 < m) (hk : 0 < k) :
    bogEps c m k / (c * k) = Real.sqrt (1 + (k / (2 * m * c)) ^ 2) := by
  rw [bogEps_eq_mul hm hk.le]
  have h : c ^ 2 + k ^ 2 / (4 * m ^ 2) = c ^ 2 * (1 + (k / (2 * m * c)) ^ 2) := by
    field_simp
    ring
  rw [h, Real.sqrt_mul (sq_nonneg c), Real.sqrt_sq hc.le]
  field_simp

/-- **The Gross–Pitaevskii dictionary** (units `ħ = m = 1`, mean density `n`, contact coupling `g ≥ 0`, so that
`c² = g n`): the squared Bogoliubov frequency is `ω² = ½ k² (½ k² + 2 g n)`, which is the formula the solver's
pre-registered known answer K5 is tested against. -/
theorem bogEps_sq_gp {g n k : ℝ} (hg : 0 ≤ g) (hn : 0 ≤ n) :
    bogEps (Real.sqrt (g * n)) 1 k ^ 2 = (1 / 2) * k ^ 2 * ((1 / 2) * k ^ 2 + 2 * (g * n)) := by
  rw [bogEps_sq, Real.sq_sqrt (mul_nonneg hg hn)]
  ring

end QuantumFluids.BogoliubovDispersion

#print axioms QuantumFluids.BogoliubovDispersion.bogEps_strictMonoOn
#print axioms QuantumFluids.BogoliubovDispersion.bogEps_le_phononDisp
#print axioms QuantumFluids.BogoliubovDispersion.phononDisp_sub_le_bogEps
#print axioms QuantumFluids.BogoliubovDispersion.sound_speed_limit
#print axioms QuantumFluids.BogoliubovDispersion.alpha2_limit
#print axioms QuantumFluids.BogoliubovDispersion.landau_velocity_eq
#print axioms QuantumFluids.BogoliubovDispersion.landau_velocity_sInf
#print axioms QuantumFluids.BogoliubovDispersion.bogEps_superadditive
#print axioms QuantumFluids.BogoliubovDispersion.bogoliubov_lowk_three_phonon_open
#print axioms QuantumFluids.BogoliubovDispersion.abs_bogEps_sub_phononDisp_le
#print axioms QuantumFluids.BogoliubovDispersion.phase_velocity_universal
#print axioms QuantumFluids.BogoliubovDispersion.bogEps_sub_sound_strictMonoOn
#print axioms QuantumFluids.BogoliubovDispersion.bogEps_sq_gp
#print axioms QuantumFluids.BogoliubovDispersion.sound_lt_phase_velocity
#print axioms QuantumFluids.BogoliubovDispersion.sound_line_le
