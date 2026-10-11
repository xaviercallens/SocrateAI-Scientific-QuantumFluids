import Mathlib

/-!
# Formalisation of Theorem 1 of `docs/designs/EXCITON_FLUID_GATE_IMAGE_CM.md`
## (the dual-gated bilayer dipole kernel is completely monotone in `r²`)

Written 2026-10-11 (second pass of the exciton-fluid programme; see `VERIFICATION_GatedKernel.md` in this directory for the
exact compile command, the axiom audit and the list of what is proved and what is not).  Lean 4.34.1 / Mathlib v4.34.1.
Exploration material: not part of the audited library `lean_src/`.  Standalone file (imports `Mathlib` only).

## What is proved (no `sorry`, no new axiom, no hypothesis on the Poisson identity)

* **T1, trigonometric core.**  `trig_core`, `trig_core_sq`, `trig_core_nonneg`:
  `2 - cos 2a - cos 2b - 2 cos(b-a) + 2 cos(a+b) = 2 (1 - cos(b-a)) (1 + cos(a+b)) = 2 (sin a - sin b)^2 ≥ 0`.
  Image-charge bookkeeping: `image_plane_top`, `image_plane_bottom` (on each grounded plane the image multiset of a
  charge coincides, by an explicit bijection of `ℤ`, with the direct multiset, for any even kernel), and the Gaussian
  corollaries `gGreen_top`, `gGreen_bottom` (the Gaussian lattice Green function vanishes on both planes).
* **T2, positivity of the Laplace measure.**  `gsum_poisson` is the Poisson-summation identity for the *shifted* Gaussian
  lattice sum, DERIVED from Mathlib's `Complex.tsum_exp_neg_quadratic` (not assumed).  `Sexc_poisson`: the neutral
  combination `S(s) = Σ_n [signs]·e^{-s a²}` equals `(π/s)^{1/2} P⁻¹ Σ_m e^{-π²m²/(P²s)} S_m`; `Sexc_nonneg`: `S(s) ≥ 0`
  for all `s > 0`, all `h₁ + h₂ > 0` and all layer heights; `Sm_zero`: `S_0 = 0`.  Summability is proved
  (`summable_gsum_term`, `summable_wgt_cos`, `summable_gauss`), not assumed.
* **T3, complete monotonicity in the library's own convention.**  `AdmissiblePotential` is a verbatim copy of
  upstream's definition (as in `ExcitonX1.lean`: smooth on `(0,∞)`, non-negative, `(-1)^r g^(r) ≥ 0`).
  `lap_admissible` is the easy direction of Bernstein's theorem: the Laplace transform of a non-negative density with
  `∫ e^{-st} μ(s) ds < ∞` for all `t > 0` is admissible (differentiation under the integral sign, all orders).
  `muExc_laplaceData` proves that the density `μ(s) = (π s)^{-1/2} S(s)` satisfies those hypotheses (it is bounded:
  `muExc_bounded`; measurable: `muExc_continuousOn`).  `gatedKernel_admissible`: its Laplace transform is admissible.
  `Uimg_eq_lap`: the image series itself (`Uimg`, a single absolutely convergent series over `n`, with the five image
  offsets of `V_ee + V_hh - 2 V_eh` grouped; `Uimg_summable`: it is absolutely convergent, so `tsum` is not
  silently `0`) equals that Laplace transform for every `t > 0` (termwise Gamma-integral
  representation of `(t + a²)^{-1/2}`, interchange of sum and integral justified by an explicit `O(n⁻²)` bound).
  `imageSeries_admissible`: **the image series `t ↦ Uimg t` is `AdmissiblePotential`**, i.e. completely monotone on `(0, ∞)`.

## What is NOT proved here (see also the note's "does not settle" list)

* The statement is about the idealised model of the note: perfect grounded metal planes, a homogeneous dielectric,
  point charges in the layers, the Coulomb kernel `1/R` (units `e²/4πε₀ε = 1`).  Non-ideal (dielectric-interface) gates,
  finite in-plane screening of the gates and quantum states are outside the statement.
* The Cohn-Kumar theorem and Bernstein's *converse* direction (completely monotone ⇒ Laplace transform) are not used or
  proved; the note's phrase "by Bernstein's theorem this is exactly the hypothesis of Cohn-Kumar" refers to the
  *easy* direction proved here (`lap_admissible`), which is all that the representation needs.
* The positivity `S(s) ≥ 0` and the admissibility hold for *all* real layer heights `z_e, z_h`, not only for layers
  strictly between the gates; the physical reading (images, signs of the planes) is meaningful only for
  `-h₂ < z_e, z_h < h₁`.  Nothing in the proof uses the betweenness.
* The identification of `Uimg` with "the Green function of the box" is by the explicit image formula of the note
  (units, signs and positions are stated in the docstring of `Uimg` and in `image_plane_top/bottom`); no PDE/Green-function
  uniqueness argument is formalised.

## Negative controls (meant to fail, and do)

`wrong_sign_not_nonneg`, `wrong_sign_not_identity` (the same identity with `-2 cos(a+b)`), `unneutral_not_nonneg`
(dropping the `V_hh` term, i.e. a non-neutral combination, is not non-negative: `a = b = π/2`).
-/

open Real MeasureTheory Set Filter Topology
open scoped ContDiff

namespace GatedKernel



/-! ## T1 -/

theorem trig_core (a b : ℝ) :
    2 - cos (2 * a) - cos (2 * b) - 2 * cos (b - a) + 2 * cos (a + b)
      = 2 * (1 - cos (b - a)) * (1 + cos (a + b)) := by
  rw [cos_two_mul, cos_two_mul, cos_sub, cos_add]
  have ha := sin_sq_add_cos_sq a
  have hb := sin_sq_add_cos_sq b
  nlinarith [ha, hb]

theorem trig_core_sq (a b : ℝ) :
    2 * (1 - cos (b - a)) * (1 + cos (a + b)) = 2 * (sin a - sin b) ^ 2 := by
  rw [cos_sub, cos_add]
  have ha := sin_sq_add_cos_sq a
  have hb := sin_sq_add_cos_sq b
  nlinarith [ha, hb]

theorem trig_core_nonneg (a b : ℝ) :
    0 ≤ 2 - cos (2 * a) - cos (2 * b) - 2 * cos (b - a) + 2 * cos (a + b) := by
  rw [trig_core, trig_core_sq]; positivity

theorem wrong_sign_not_nonneg :
    ¬ ∀ a b : ℝ, 0 ≤ 2 - cos (2 * a) - cos (2 * b) - 2 * cos (b - a) - 2 * cos (a + b) := by
  intro h
  have := h 0 0
  norm_num at this

theorem wrong_sign_not_identity :
    ¬ ∀ a b : ℝ, 2 - cos (2 * a) - cos (2 * b) - 2 * cos (b - a) - 2 * cos (a + b)
      = 2 * (1 - cos (b - a)) * (1 - cos (a + b)) := by
  intro h
  have := h 0 0
  norm_num at this

/-! ## image bookkeeping -/

theorem image_plane_top {f : ℝ → ℝ} (hf : ∀ x, f (-x) = f x) (P h1 z0 : ℝ) :
    ∃ σ : ℤ ≃ ℤ, ∀ n : ℤ, f (h1 - 2 * h1 + z0 - P * n) = f (h1 - z0 - P * (σ n : ℤ)) := by
  refine ⟨Equiv.neg ℤ, fun n => ?_⟩
  rw [← hf (h1 - 2 * h1 + z0 - P * n)]
  congr 1
  simp; ring

theorem image_plane_bottom {f : ℝ → ℝ} (hf : ∀ x, f (-x) = f x) (h1 h2 z0 : ℝ) :
    ∃ σ : ℤ ≃ ℤ, ∀ n : ℤ,
      f (-h2 - 2 * h1 + z0 - (2 * (h1 + h2)) * n) = f (-h2 - z0 - (2 * (h1 + h2)) * (σ n : ℤ)) := by
  refine ⟨⟨fun n => -n - 1, fun n => -n - 1, fun n => by ring, fun n => by ring⟩, fun n => ?_⟩
  rw [← hf (-h2 - 2 * h1 + z0 - (2 * (h1 + h2)) * n)]
  congr 1
  simp only [Equiv.coe_fn_mk]
  push_cast; ring

/-- Gaussian lattice sum over the `n`-th period image. -/
noncomputable def gsum (s P c : ℝ) : ℝ := ∑' n : ℤ, exp (-s * (c - P * n) ^ 2)

noncomputable def gGreen (s h1 h2 z z0 : ℝ) : ℝ :=
  gsum s (2 * (h1 + h2)) (z - z0) - gsum s (2 * (h1 + h2)) (z - 2 * h1 + z0)

theorem gGreen_top (s h1 h2 z0 : ℝ) : gGreen s h1 h2 h1 z0 = 0 := by
  obtain ⟨σ, hσ⟩ := image_plane_top (f := fun x => exp (-s * x ^ 2)) (fun x => by simp) (2 * (h1 + h2)) h1 z0
  unfold gGreen gsum
  have : ∑' n : ℤ, exp (-s * (h1 - 2 * h1 + z0 - 2 * (h1 + h2) * n) ^ 2)
      = ∑' n : ℤ, exp (-s * (h1 - z0 - 2 * (h1 + h2) * n) ^ 2) := by
    rw [← σ.tsum_eq (fun n => exp (-s * (h1 - z0 - 2 * (h1 + h2) * n) ^ 2))]
    exact tsum_congr (fun n => by simpa using hσ n)
  rw [show h1 - z0 = h1 - z0 from rfl, show h1 - 2 * h1 + z0 = h1 - 2 * h1 + z0 from rfl, this]
  simp

theorem gGreen_bottom (s h1 h2 z0 : ℝ) : gGreen s h1 h2 (-h2) z0 = 0 := by
  obtain ⟨σ, hσ⟩ := image_plane_bottom (f := fun x => exp (-s * x ^ 2)) (fun x => by simp) h1 h2 z0
  unfold gGreen gsum
  have : ∑' n : ℤ, exp (-s * (-h2 - 2 * h1 + z0 - 2 * (h1 + h2) * n) ^ 2)
      = ∑' n : ℤ, exp (-s * (-h2 - z0 - 2 * (h1 + h2) * n) ^ 2) := by
    rw [← σ.tsum_eq (fun n => exp (-s * (-h2 - z0 - 2 * (h1 + h2) * n) ^ 2))]
    exact tsum_congr (fun n => by simpa using hσ n)
  rw [this]
  simp


theorem summable_gauss {γ : ℝ} (hγ : 0 < γ) : Summable (fun m : ℤ => exp (-γ * (m : ℝ) ^ 2)) := by
  have h := (summable_jacobiTheta₂_term_iff 0 (Complex.I * ((γ / π : ℝ) : ℂ))).2 (by
    simp; positivity)
  have h2 : (fun m : ℤ => jacobiTheta₂_term m 0 (Complex.I * ((γ / π : ℝ) : ℂ)))
      = fun m : ℤ => ((exp (-γ * (m : ℝ) ^ 2) : ℝ) : ℂ) := by
    funext m
    unfold jacobiTheta₂_term
    push_cast
    have : (π : ℂ) ≠ 0 := by exact_mod_cast pi_ne_zero
    congr 1
    field_simp
    ring_nf
    simp [Complex.I_sq]
  rw [h2] at h
  exact Complex.summable_ofReal.1 h

theorem summable_gauss_lin {γ : ℝ} (hγ : 0 < γ) (β : ℝ) :
    Summable (fun m : ℤ => exp (-γ * (m : ℝ) ^ 2 + β * m)) := by
  have h := (summable_jacobiTheta₂_term_iff (-(Complex.I * ((β / (2 * π) : ℝ) : ℂ)))
    (Complex.I * ((γ / π : ℝ) : ℂ))).2 (by simp; positivity)
  have h2 : (fun m : ℤ => jacobiTheta₂_term m (-(Complex.I * ((β / (2 * π) : ℝ) : ℂ)))
        (Complex.I * ((γ / π : ℝ) : ℂ)))
      = fun m : ℤ => ((exp (-γ * (m : ℝ) ^ 2 + β * m) : ℝ) : ℂ) := by
    funext m
    unfold jacobiTheta₂_term
    push_cast
    have : (π : ℂ) ≠ 0 := by exact_mod_cast pi_ne_zero
    congr 1
    field_simp
    ring_nf
    simp [Complex.I_sq]
    ring
  rw [h2] at h
  exact Complex.summable_ofReal.1 h

theorem summable_gsum_term {s P : ℝ} (hs : 0 < s) (hP : P ≠ 0) (c : ℝ) :
    Summable (fun n : ℤ => exp (-s * (c - P * n) ^ 2)) := by
  have h := (summable_gauss_lin (γ := s * P ^ 2) (by positivity) (2 * s * c * P)).mul_left (exp (-s * c ^ 2))
  refine h.congr (fun n => ?_)
  rw [← exp_add]; congr 1; ring

theorem gsum_nonneg (s P c : ℝ) : 0 ≤ gsum s P c := tsum_nonneg (fun _ => (exp_pos _).le)

theorem continuousOn_gsum {P : ℝ} (hP : 0 < P) (c : ℝ) :
    ContinuousOn (fun s => gsum s P c) (Ioi (0 : ℝ)) := by
  intro s hs
  have hs' : 0 < s := hs
  have h : ContinuousOn (fun s => gsum s P c) (Ici (s / 2)) := by
    unfold gsum
    refine continuousOn_tsum (u := fun n : ℤ => exp (-(s / 2) * (c - P * n) ^ 2))
      (fun n => by fun_prop) (summable_gsum_term (by positivity) hP.ne' c) ?_
    intro n x hx
    rw [Real.norm_of_nonneg (exp_pos _).le]
    apply exp_le_exp.2
    have hx' : s / 2 ≤ x := hx
    nlinarith [sq_nonneg (c - P * n)]
  exact (h.continuousAt (Ici_mem_nhds (by linarith))).continuousWithinAt



/-! ## Poisson summation -/

theorem gsum_poisson {s P : ℝ} (hs : 0 < s) (hP : 0 < P) (c : ℝ) :
    gsum s P c = √(π / s) / P *
      ∑' m : ℤ, exp (-(π ^ 2 / (P ^ 2 * s)) * (m : ℝ) ^ 2) * cos (2 * π * m * c / P) := by
  set a : ℝ := s * P ^ 2 / π with ha_def
  set b : ℝ := s * c * P / π with hb_def
  set γ : ℝ := π ^ 2 / (P ^ 2 * s) with hγ_def
  set θ : ℝ := 2 * π * c / P with hθ_def
  have hpi : 0 < π := pi_pos
  have ha : 0 < a := by positivity
  have hγ : 0 < γ := by positivity
  have h := Complex.tsum_exp_neg_quadratic (a := (a : ℂ)) (by simpa using ha) (b := (b : ℂ))
  have hsum : Summable (fun m : ℤ => ((exp (-γ * (m : ℝ) ^ 2) : ℝ) : ℂ) * Complex.exp (-Complex.I * θ * m)) := by
    refine Summable.of_norm_bounded (summable_gauss hγ) (fun m => ?_)
    rw [norm_mul, Complex.norm_real, Real.norm_of_nonneg (exp_pos _).le]
    have : ‖Complex.exp (-Complex.I * θ * m)‖ = 1 := by
      rw [Complex.norm_exp]; simp
    rw [this, mul_one]
  have hC : ((gsum s P c : ℝ) : ℂ) = ((√(π / s) / P : ℝ) : ℂ) *
      ∑' m : ℤ, ((exp (-γ * (m : ℝ) ^ 2) : ℝ) : ℂ) * Complex.exp (-Complex.I * θ * m) := by
    have hL : ((gsum s P c : ℝ) : ℂ) = Complex.exp (-(s : ℂ) * c ^ 2) *
        ∑' n : ℤ, Complex.exp (-π * (a : ℂ) * n ^ 2 + 2 * π * (b : ℂ) * n) := by
      unfold gsum
      rw [Complex.ofReal_tsum, ← tsum_mul_left]
      refine tsum_congr (fun n => ?_)
      rw [← Complex.exp_add, Complex.ofReal_exp]
      congr 1
      simp only [ha_def, hb_def]
      push_cast
      have : (π : ℂ) ≠ 0 := by exact_mod_cast pi_ne_zero
      field_simp
      ring
    rw [hL, h]
    have hsq : (1 : ℂ) / (a : ℂ) ^ (1 / 2 : ℂ) = ((√(π / s) / P : ℝ) : ℂ) := by
      have e1 : ((a : ℂ)) ^ (1 / 2 : ℂ) = ((a ^ (1 / 2 : ℝ) : ℝ) : ℂ) := by
        rw [Complex.ofReal_cpow ha.le]; push_cast; rfl
      rw [e1, ← Complex.ofReal_one, ← Complex.ofReal_div]
      congr 1
      rw [← Real.sqrt_eq_rpow, one_div, ← Real.sqrt_inv, ha_def]
      have : (s * P ^ 2 / π)⁻¹ = (π / s) / P ^ 2 := by field_simp
      rw [this, Real.sqrt_div' _ (by positivity), Real.sqrt_sq hP.le]
    rw [hsq, ← mul_assoc, mul_comm (Complex.exp _), mul_assoc, ← tsum_mul_left]
    congr 1
    refine tsum_congr (fun n => ?_)
    rw [Complex.ofReal_exp, ← Complex.exp_add, ← Complex.exp_add]
    congr 1
    simp only [ha_def, hb_def, hγ_def, hθ_def]
    push_cast
    have : (π : ℂ) ≠ 0 := by exact_mod_cast pi_ne_zero
    have hs' : (s : ℂ) ≠ 0 := by exact_mod_cast hs.ne'
    have hP' : (P : ℂ) ≠ 0 := by exact_mod_cast hP.ne'
    field_simp
    ring_nf
    simp [Complex.I_sq]
  have hre := congrArg Complex.re hC
  rw [Complex.ofReal_re, Complex.re_ofReal_mul, Complex.re_tsum hsum] at hre
  rw [hre]
  congr 1
  refine tsum_congr (fun m => ?_)
  rw [Complex.re_ofReal_mul]
  congr 1
  rw [show (-Complex.I * (θ : ℂ) * (m : ℂ)) = (((-θ * m : ℝ)) : ℂ) * Complex.I by push_cast; ring,
    Complex.exp_ofReal_mul_I_re, hθ_def]
  rw [← cos_neg]; congr 1; ring



/-! ## T2: positivity of the Laplace density -/

/-- the Gaussian weight of the `m`-th Fourier mode. -/
noncomputable def wgt (s P : ℝ) (m : ℤ) : ℝ := exp (-(π ^ 2 / (P ^ 2 * s)) * (m : ℝ) ^ 2)

/-- the trigonometric factor `S_m` of the note, `α = 2πm/P`, `a = α (z_e - h₁)`, `b = α (z_h - h₁)`. -/
noncomputable def Sm (P h1 ze zh : ℝ) (m : ℤ) : ℝ :=
  2 - cos (2 * (2 * π * m / P * (ze - h1))) - cos (2 * (2 * π * m / P * (zh - h1)))
    - 2 * cos (2 * π * m / P * (zh - h1) - 2 * π * m / P * (ze - h1))
    + 2 * cos (2 * π * m / P * (ze - h1) + 2 * π * m / P * (zh - h1))

/-- `S(s)`: the Gaussian lattice sum with the signs of `V_ee + V_hh - 2 V_eh`. -/
noncomputable def Sexc (s h1 h2 ze zh : ℝ) : ℝ :=
  gGreen s h1 h2 ze ze + gGreen s h1 h2 zh zh - 2 * gGreen s h1 h2 zh ze

theorem Sm_nonneg (P h1 ze zh : ℝ) (m : ℤ) : 0 ≤ Sm P h1 ze zh m := by
  unfold Sm; exact trig_core_nonneg _ _

theorem Sm_zero (P h1 ze zh : ℝ) : Sm P h1 ze zh 0 = 0 := by
  simp [Sm]
  norm_num

theorem summable_wgt_cos {s P : ℝ} (hs : 0 < s) (hP : 0 < P) (c : ℝ) :
    Summable (fun m : ℤ => wgt s P m * cos (2 * π * m * c / P)) := by
  have hγ : 0 < π ^ 2 / (P ^ 2 * s) := by positivity
  refine Summable.of_norm_bounded (summable_gauss hγ) (fun m => ?_)
  unfold wgt
  rw [norm_mul, Real.norm_of_nonneg (exp_pos _).le]
  calc _ ≤ exp (-(π ^ 2 / (P ^ 2 * s)) * (m : ℝ) ^ 2) * 1 :=
        mul_le_mul_of_nonneg_left (abs_cos_le_one _) (exp_pos _).le
    _ = _ := mul_one _

/-- `S` written with the six Gaussian lattice sums (no positivity needed). -/
theorem Sexc_eq_gsum (s h1 h2 ze zh : ℝ) : Sexc s h1 h2 ze zh =
    2 * gsum s (2 * (h1 + h2)) 0 - gsum s (2 * (h1 + h2)) (ze - 2 * h1 + ze)
      - gsum s (2 * (h1 + h2)) (zh - 2 * h1 + zh) - 2 * gsum s (2 * (h1 + h2)) (zh - ze)
      + 2 * gsum s (2 * (h1 + h2)) (zh - 2 * h1 + ze) := by
  unfold Sexc gGreen
  simp only [sub_self]
  ring

/-- Poisson form of the neutral exciton sum:  `S(s) = (π/s)^{1/2} P⁻¹ Σ_m e^{-π²m²/(P²s)} S_m`
(with `P = 2(h₁+h₂)`). Derived from Mathlib's `Complex.tsum_exp_neg_quadratic`; no hypothesis. -/
theorem Sexc_poisson {s h1 h2 : ℝ} (ze zh : ℝ) (hs : 0 < s) (hP : 0 < h1 + h2) :
    Sexc s h1 h2 ze zh = √(π / s) / (2 * (h1 + h2)) *
      ∑' m : ℤ, wgt s (2 * (h1 + h2)) m * Sm (2 * (h1 + h2)) h1 ze zh m := by
  set P : ℝ := 2 * (h1 + h2) with hPdef
  have hP' : 0 < P := by positivity
  have hs0 := summable_wgt_cos hs hP' 0
  have hs1 := summable_wgt_cos hs hP' (ze - 2 * h1 + ze)
  have hs2 := summable_wgt_cos hs hP' (zh - 2 * h1 + zh)
  have hs3 := summable_wgt_cos hs hP' (zh - ze)
  have hs4 := summable_wgt_cos hs hP' (zh - 2 * h1 + ze)
  have H := ((((hs0.hasSum.mul_left 2).sub hs1.hasSum).sub hs2.hasSum).sub
    (hs3.hasSum.mul_left 2)).add (hs4.hasSum.mul_left 2)
  have hfun : (fun m : ℤ => wgt s P m * Sm P h1 ze zh m) =
      fun m : ℤ => (2 * (wgt s P m * cos (2 * π * m * 0 / P))
        - wgt s P m * cos (2 * π * m * (ze - 2 * h1 + ze) / P)
        - wgt s P m * cos (2 * π * m * (zh - 2 * h1 + zh) / P)
        - 2 * (wgt s P m * cos (2 * π * m * (zh - ze) / P))
        + 2 * (wgt s P m * cos (2 * π * m * (zh - 2 * h1 + ze) / P))) := by
    funext m
    unfold Sm
    have e1 : 2 * π * m * (ze - 2 * h1 + ze) / P = 2 * (2 * π * m / P * (ze - h1)) := by ring
    have e2 : 2 * π * m * (zh - 2 * h1 + zh) / P = 2 * (2 * π * m / P * (zh - h1)) := by ring
    have e3 : 2 * π * m * (zh - ze) / P
        = 2 * π * m / P * (zh - h1) - 2 * π * m / P * (ze - h1) := by ring
    have e4 : 2 * π * m * (zh - 2 * h1 + ze) / P
        = 2 * π * m / P * (ze - h1) + 2 * π * m / P * (zh - h1) := by ring
    rw [e1, e2, e3, e4]
    simp only [mul_zero, zero_div, cos_zero]
    ring
  rw [hfun, H.tsum_eq]
  have : Sexc s h1 h2 ze zh = 2 * gsum s P 0 - gsum s P (ze - 2 * h1 + ze)
      - gsum s P (zh - 2 * h1 + zh) - 2 * gsum s P (zh - ze) + 2 * gsum s P (zh - 2 * h1 + ze) :=
    Sexc_eq_gsum s h1 h2 ze zh
  rw [this, gsum_poisson hs hP', gsum_poisson hs hP', gsum_poisson hs hP', gsum_poisson hs hP',
    gsum_poisson hs hP']
  unfold wgt
  ring

/-- **T2.** `S(s) ≥ 0` for every `s > 0` and every gate/layer placement with `h₁ + h₂ > 0`. -/
theorem Sexc_nonneg {s h1 h2 : ℝ} (ze zh : ℝ) (hs : 0 < s) (hP : 0 < h1 + h2) :
    0 ≤ Sexc s h1 h2 ze zh := by
  rw [Sexc_poisson ze zh hs hP]
  refine mul_nonneg (by positivity) (tsum_nonneg (fun m => ?_))
  exact mul_nonneg (exp_pos _).le (Sm_nonneg _ _ _ _ _)



/-! ## Laplace transforms of non-negative densities -/

/-- Verbatim copy of upstream's `OAI.TriangularUniversal.AdmissiblePotential` (as in `ExcitonX1.lean`). -/
def AdmissiblePotential (g : ℝ → ℝ) : Prop :=
  ContDiffOn ℝ (⊤ : ℕ∞) g (Set.Ioi 0) ∧
  (∀ t : ℝ, 0 < t → 0 ≤ g t) ∧
  ∀ (r : ℕ) (t : ℝ), 0 < t → 0 ≤ (-1 : ℝ) ^ r * iteratedDeriv r g t

theorem pow_exp_le (r : ℕ) {a s : ℝ} (ha : 0 < a) (hs : 0 ≤ s) :
    s ^ r * exp (-(s * a)) ≤ (r.factorial : ℝ) * (2 / a) ^ r * exp (-(s * (a / 2))) := by
  have hx : 0 ≤ s * (a / 2) := by positivity
  have h1 := Real.pow_div_factorial_le_exp (s * (a / 2)) hx r
  have hf : (0 : ℝ) < r.factorial := by exact_mod_cast r.factorial_pos
  have h2 : (s * (a / 2)) ^ r ≤ r.factorial * exp (s * (a / 2)) := by
    rw [div_le_iff₀ hf] at h1; linarith
  have h3 : s ^ r = (2 / a) ^ r * (s * (a / 2)) ^ r := by
    rw [← mul_pow]; congr 1; field_simp
  have h4 : exp (-(s * a)) = exp (-(s * (a / 2))) * exp (-(s * (a / 2))) := by
    rw [← exp_add]; congr 1; ring
  calc s ^ r * exp (-(s * a)) = (2 / a) ^ r * ((s * (a / 2)) ^ r * exp (-(s * (a / 2)))) * exp (-(s * (a / 2))) := by
        rw [h3, h4]; ring
    _ ≤ (2 / a) ^ r * ((r.factorial * exp (s * (a / 2))) * exp (-(s * (a / 2)))) * exp (-(s * (a / 2))) := by
        gcongr
    _ = _ := by
        have : exp (s * (a / 2)) * exp (-(s * (a / 2))) = 1 := by rw [← exp_add]; simp
        calc _ = (2 / a) ^ r * (r.factorial * (exp (s * (a / 2)) * exp (-(s * (a / 2))))) * exp (-(s * (a / 2))) := by ring
          _ = _ := by rw [this]; ring

section Laplace

variable {μ : ℝ → ℝ}

/-- `(-1)^r`-signed `r`-th moment Laplace transform `t ↦ ∫_0^∞ (-s)^r e^{-st} μ(s) ds`. -/
noncomputable def lap (μ : ℝ → ℝ) (r : ℕ) (t : ℝ) : ℝ :=
  ∫ s in Ioi (0 : ℝ), (-s) ^ r * (exp (-(s * t)) * μ s)

structure LaplaceData (μ : ℝ → ℝ) : Prop where
  nonneg : ∀ s, 0 < s → 0 ≤ μ s
  meas : AEStronglyMeasurable μ (volume.restrict (Ioi (0 : ℝ)))
  integrable : ∀ t, 0 < t → IntegrableOn (fun s => exp (-(s * t)) * μ s) (Ioi (0 : ℝ))

theorem LaplaceData.int_pow (h : LaplaceData μ) (r : ℕ) {t : ℝ} (ht : 0 < t) :
    IntegrableOn (fun s => (-s) ^ r * (exp (-(s * t)) * μ s)) (Ioi (0 : ℝ)) := by
  have hC := (h.integrable (t / 2) (by positivity)).const_mul ((r.factorial : ℝ) * (2 / t) ^ r)
  refine Integrable.mono' hC ?_ ?_
  · exact (by fun_prop : Continuous fun s : ℝ => (-s) ^ r).aestronglyMeasurable.mul
      ((by fun_prop : Continuous fun s : ℝ => exp (-(s * t))).aestronglyMeasurable.mul h.meas)
  · refine (ae_restrict_iff' measurableSet_Ioi).2 (Eventually.of_forall fun s hs => ?_)
    have hs' : 0 < s := hs
    have hm := h.nonneg s hs'
    rw [norm_mul, norm_pow, norm_neg, Real.norm_of_nonneg hs'.le, norm_mul,
      Real.norm_of_nonneg (exp_pos _).le, Real.norm_of_nonneg hm]
    calc s ^ r * (exp (-(s * t)) * μ s) = (s ^ r * exp (-(s * t))) * μ s := by ring
      _ ≤ ((r.factorial : ℝ) * (2 / t) ^ r * exp (-(s * (t / 2)))) * μ s :=
          mul_le_mul_of_nonneg_right (pow_exp_le r ht hs'.le) hm
      _ = _ := by ring

theorem LaplaceData.hasDerivAt (h : LaplaceData μ) (r : ℕ) {t0 : ℝ} (ht0 : 0 < t0) :
    HasDerivAt (lap μ r) (lap μ (r + 1) t0) t0 := by
  have hmeas : ∀ (k : ℕ) (t : ℝ), AEStronglyMeasurable
      (fun s => (-s) ^ k * (exp (-(s * t)) * μ s)) (volume.restrict (Ioi (0 : ℝ))) := fun k t =>
    (by fun_prop : Continuous fun s : ℝ => (-s) ^ k).aestronglyMeasurable.mul
      ((by fun_prop : Continuous fun s : ℝ => exp (-(s * t))).aestronglyMeasurable.mul h.meas)
  set C : ℝ := ((r + 1).factorial : ℝ) * (2 / (t0 / 2)) ^ (r + 1) with hC
  have hint := (h.integrable (t0 / 2 / 2) (by positivity)).const_mul C
  have hbd : ∀ᵐ s ∂(volume.restrict (Ioi (0 : ℝ))), ∀ x ∈ Metric.ball t0 (t0 / 2),
      ‖(-s) ^ (r + 1) * (exp (-(s * x)) * μ s)‖ ≤ C * (exp (-(s * (t0 / 2 / 2))) * μ s) := by
    refine (ae_restrict_iff' measurableSet_Ioi).2 (Eventually.of_forall fun s hs x hx => ?_)
    have hs' : 0 < s := hs
    have hm := h.nonneg s hs'
    have hx' : t0 / 2 < x := by
      have := (Metric.mem_ball.1 hx); rw [Real.dist_eq, abs_lt] at this; linarith
    rw [norm_mul, norm_pow, norm_neg, Real.norm_of_nonneg hs'.le, norm_mul,
      Real.norm_of_nonneg (exp_pos _).le, Real.norm_of_nonneg hm]
    have e1 : exp (-(s * x)) ≤ exp (-(s * (t0 / 2))) := by
      apply exp_le_exp.2; nlinarith
    calc s ^ (r + 1) * (exp (-(s * x)) * μ s)
        = (s ^ (r + 1) * exp (-(s * x))) * μ s := by ring
      _ ≤ (s ^ (r + 1) * exp (-(s * (t0 / 2)))) * μ s := by gcongr
      _ ≤ (C * exp (-(s * (t0 / 2 / 2)))) * μ s :=
          mul_le_mul_of_nonneg_right (pow_exp_le (r + 1) (by positivity) hs'.le) hm
      _ = _ := by ring
  have hdf : ∀ᵐ s ∂(volume.restrict (Ioi (0 : ℝ))), ∀ x ∈ Metric.ball t0 (t0 / 2),
      HasDerivAt (fun t : ℝ => (-s) ^ r * (exp (-(s * t)) * μ s))
        ((-s) ^ (r + 1) * (exp (-(s * x)) * μ s)) x := by
    refine Eventually.of_forall fun s x _ => ?_
    have h1 : HasDerivAt (fun t : ℝ => -(s * t)) (-(s * 1)) x :=
      ((hasDerivAt_id x).const_mul s).neg
    have h2 := (h1.exp).mul_const (μ s) |>.const_mul ((-s) ^ r)
    convert h2 using 1
    ring
  have key := hasDerivAt_integral_of_dominated_loc_of_deriv_le
    (μ := volume.restrict (Ioi (0 : ℝ)))
    (F := fun t s => (-s) ^ r * (exp (-(s * t)) * μ s))
    (F' := fun t s => (-s) ^ (r + 1) * (exp (-(s * t)) * μ s))
    (bound := fun s => C * (exp (-(s * (t0 / 2 / 2))) * μ s))
    (s := Metric.ball t0 (t0 / 2)) (Metric.ball_mem_nhds _ (by positivity))
    (Eventually.of_forall fun t => hmeas r t) (h.int_pow r ht0) (hmeas (r + 1) t0)
    hbd hint hdf
  exact key.2

theorem lap_iteratedDeriv (h : LaplaceData μ) (r : ℕ) :
    ∀ t : ℝ, 0 < t → iteratedDeriv r (lap μ 0) t = lap μ r t := by
  induction r with
  | zero => intro t _; simp
  | succ r ih =>
    intro t ht
    rw [iteratedDeriv_succ]
    have hev : iteratedDeriv r (lap μ 0) =ᶠ[𝓝 t] lap μ r :=
      Filter.eventually_of_mem (isOpen_Ioi.mem_nhds ht) (fun x hx => ih x hx)
    rw [hev.deriv_eq]
    exact (h.hasDerivAt r ht).deriv

theorem lap_contDiffOn (h : LaplaceData μ) :
    ∀ (n : ℕ) (r : ℕ), ContDiffOn ℝ n (lap μ r) (Ioi (0 : ℝ)) := by
  intro n
  induction n with
  | zero =>
    intro r
    refine contDiffOn_zero.2 ?_
    exact fun t ht => (h.hasDerivAt r ht).continuousAt.continuousWithinAt
  | succ n ih =>
    intro r
    have hc : ((n + 1 : ℕ) : WithTop ℕ∞) = (n : WithTop ℕ∞) + 1 := by push_cast; rfl
    rw [hc, contDiffOn_succ_iff_deriv_of_isOpen isOpen_Ioi]
    refine ⟨fun t ht => (h.hasDerivAt r ht).differentiableAt.differentiableWithinAt, ?_, ?_⟩
    · intro hn
      exact absurd hn (by exact_mod_cast WithTop.coe_ne_top)
    · refine (ih (r + 1)).congr (fun t ht => ?_)
      exact (h.hasDerivAt r ht).deriv

/-- **Bernstein, the easy direction, in the library's convention.**  The Laplace transform of a non-negative
density with `∫ e^{-st} μ(s) ds < ∞` for all `t > 0` is `AdmissiblePotential`. -/
theorem lap_admissible (h : LaplaceData μ) : AdmissiblePotential (lap μ 0) := by
  refine ⟨?_, ?_, ?_⟩
  · have : ContDiffOn ℝ (⊤ : ℕ∞) (lap μ 0) (Ioi (0 : ℝ)) := by
      rw [show ((⊤ : ℕ∞) : WithTop ℕ∞) = ∞ from rfl]
      exact contDiffOn_infty.2 (fun n => lap_contDiffOn h n 0)
    exact this
  · intro t ht
    unfold lap
    refine setIntegral_nonneg measurableSet_Ioi (fun s hs => ?_)
    have := h.nonneg s hs
    simp only [pow_zero, one_mul]
    positivity
  · intro r t ht
    rw [lap_iteratedDeriv h r t ht]
    unfold lap
    rw [← integral_const_mul]
    refine setIntegral_nonneg measurableSet_Ioi (fun s hs => ?_)
    have := h.nonneg s hs
    have e : (-1 : ℝ) ^ r * ((-s) ^ r * (exp (-(s * t)) * μ s)) = s ^ r * (exp (-(s * t)) * μ s) := by
      rw [← mul_assoc, ← mul_pow]; simp
    rw [e]
    have : 0 < s := hs
    positivity

end Laplace


/-! ## T3: the Laplace density is a legitimate Bernstein density, so its Laplace transform is admissible -/

/-- the Laplace density `μ(s) = (π s)^{-1/2} S(s)` of the note. -/
noncomputable def muExc (s h1 h2 ze zh : ℝ) : ℝ := (√(π * s))⁻¹ * Sexc s h1 h2 ze zh

theorem Sm_le_eight (P h1 ze zh : ℝ) (m : ℤ) : Sm P h1 ze zh m ≤ 8 := by
  unfold Sm
  have := neg_one_le_cos (2 * (2 * π * m / P * (ze - h1)))
  have := neg_one_le_cos (2 * (2 * π * m / P * (zh - h1)))
  have := neg_one_le_cos (2 * π * m / P * (zh - h1) - 2 * π * m / P * (ze - h1))
  have := cos_le_one (2 * π * m / P * (zh - h1) - 2 * π * m / P * (ze - h1))
  have := cos_le_one (2 * (2 * π * m / P * (ze - h1)))
  have := cos_le_one (2 * (2 * π * m / P * (zh - h1)))
  have := cos_le_one (2 * π * m / P * (ze - h1) + 2 * π * m / P * (zh - h1))
  linarith

theorem muExc_nonneg {s h1 h2 : ℝ} (ze zh : ℝ) (hs : 0 < s) (hP : 0 < h1 + h2) :
    0 ≤ muExc s h1 h2 ze zh := by
  unfold muExc
  exact mul_nonneg (inv_nonneg.2 (Real.sqrt_nonneg _)) (Sexc_nonneg ze zh hs hP)

theorem muExc_poisson {s h1 h2 : ℝ} (ze zh : ℝ) (hs : 0 < s) (hP : 0 < h1 + h2) :
    muExc s h1 h2 ze zh = 1 / (s * (2 * (h1 + h2))) *
      ∑' m : ℤ, wgt s (2 * (h1 + h2)) m * Sm (2 * (h1 + h2)) h1 ze zh m := by
  unfold muExc
  rw [Sexc_poisson ze zh hs hP]
  have hpos : 0 < π * s := by positivity
  have hsq : √(π / s) = √(π * s) / s := by
    have : π / s = (π * s) / s ^ 2 := by field_simp
    rw [this, Real.sqrt_div' _ (by positivity), Real.sqrt_sq hs.le]
  have hne : √(π * s) ≠ 0 := (Real.sqrt_pos.2 hpos).ne'
  rw [hsq]
  field_simp

theorem gsum_anti {s : ℝ} (hs : 1 ≤ s) {P : ℝ} (hP : 0 < P) (c : ℝ) :
    gsum s P c ≤ gsum 1 P c := by
  unfold gsum
  refine (summable_gsum_term (by linarith) hP.ne' c).tsum_le_tsum (fun n => ?_)
    (summable_gsum_term one_pos hP.ne' c)
  apply exp_le_exp.2
  nlinarith [sq_nonneg (c - P * n)]

theorem muExc_le_large {s h1 h2 : ℝ} (ze zh : ℝ) (hs : 1 ≤ s) (hP : 0 < h1 + h2) :
    muExc s h1 h2 ze zh ≤ 2 * gsum 1 (2 * (h1 + h2)) 0
      + 2 * gsum 1 (2 * (h1 + h2)) (zh - 2 * h1 + ze) := by
  have hP' : 0 < 2 * (h1 + h2) := by positivity
  have hS : Sexc s h1 h2 ze zh ≤ 2 * gsum 1 (2 * (h1 + h2)) 0
      + 2 * gsum 1 (2 * (h1 + h2)) (zh - 2 * h1 + ze) := by
    rw [Sexc_eq_gsum]
    have h0 := gsum_anti hs hP' 0
    have h4 := gsum_anti hs hP' (zh - 2 * h1 + ze)
    have := gsum_nonneg s (2 * (h1 + h2)) (ze - 2 * h1 + ze)
    have := gsum_nonneg s (2 * (h1 + h2)) (zh - 2 * h1 + zh)
    have := gsum_nonneg s (2 * (h1 + h2)) (zh - ze)
    linarith
  have hS0 := Sexc_nonneg (s := s) ze zh (by linarith) hP
  unfold muExc
  have hinv : (√(π * s))⁻¹ ≤ 1 := by
    apply inv_le_one_of_one_le₀
    rw [show (1 : ℝ) = √1 by simp]
    apply Real.sqrt_le_sqrt
    nlinarith [pi_gt_three]
  calc (√(π * s))⁻¹ * Sexc s h1 h2 ze zh ≤ 1 * Sexc s h1 h2 ze zh :=
        mul_le_mul_of_nonneg_right hinv hS0
    _ ≤ _ := by linarith

/-- constant `Σ_m e^{γ₀} e^{-γ₀ m²}`, `γ₀ = π²/P²`. -/
noncomputable def Kconst (P : ℝ) : ℝ :=
  ∑' m : ℤ, exp (π ^ 2 / P ^ 2) * exp (-(π ^ 2 / P ^ 2) * (m : ℝ) ^ 2)

theorem muExc_le_small {s h1 h2 : ℝ} (ze zh : ℝ) (hs : 0 < s) (hs1 : s ≤ 1) (hP : 0 < h1 + h2) :
    muExc s h1 h2 ze zh ≤ 8 * Kconst (2 * (h1 + h2)) / ((2 * (h1 + h2)) * (π ^ 2 / (2 * (h1 + h2)) ^ 2)) := by
  set P : ℝ := 2 * (h1 + h2) with hPdef
  have hP' : 0 < P := by positivity
  set γ0 : ℝ := π ^ 2 / P ^ 2 with hγ0
  have hγ0pos : 0 < γ0 := by positivity
  set γ : ℝ := π ^ 2 / (P ^ 2 * s) with hγ
  have hγeq : γ = γ0 / s := by rw [hγ, hγ0]; field_simp
  have hγge : γ0 ≤ γ := by
    rw [hγeq, le_div_iff₀ hs]; nlinarith
  have hc : Summable (fun m : ℤ => exp γ0 * exp (-γ0 * (m : ℝ) ^ 2)) :=
    (summable_gauss hγ0pos).mul_left _
  have hterm : ∀ m : ℤ, wgt s P m * Sm P h1 ze zh m ≤
      8 * exp (-γ) * (exp γ0 * exp (-γ0 * (m : ℝ) ^ 2)) := by
    intro m
    have hpos : 0 < 8 * exp (-γ) * (exp γ0 * exp (-γ0 * (m : ℝ) ^ 2)) := by positivity
    by_cases hm : m = 0
    · subst hm; rw [Sm_zero]; simpa using hpos.le
    · have h1m : (1 : ℝ) ≤ (m : ℝ) ^ 2 := by
        have : (1 : ℤ) ≤ m ^ 2 := by
          have := Int.one_le_abs hm
          nlinarith [sq_abs m]
        exact_mod_cast this
      have hw : wgt s P m ≤ exp (-γ) * (exp γ0 * exp (-γ0 * (m : ℝ) ^ 2)) := by
        unfold wgt
        rw [← hγ, ← exp_add, ← exp_add]
        apply exp_le_exp.2
        nlinarith [mul_nonneg (sub_nonneg.2 hγge) (sub_nonneg.2 h1m)]
      calc wgt s P m * Sm P h1 ze zh m ≤ (exp (-γ) * (exp γ0 * exp (-γ0 * (m : ℝ) ^ 2))) * 8 :=
            mul_le_mul hw (Sm_le_eight _ _ _ _ _) (Sm_nonneg _ _ _ _ _) (by positivity)
        _ = _ := by ring
  have hnn : ∀ m : ℤ, 0 ≤ wgt s P m * Sm P h1 ze zh m := fun m =>
    mul_nonneg (exp_pos _).le (Sm_nonneg _ _ _ _ _)
  have hsumT : Summable (fun m : ℤ => wgt s P m * Sm P h1 ze zh m) :=
    Summable.of_nonneg_of_le hnn hterm (hc.mul_left _)
  have hT : ∑' m : ℤ, wgt s P m * Sm P h1 ze zh m ≤ 8 * exp (-γ) * Kconst P := by
    calc _ ≤ ∑' m : ℤ, 8 * exp (-γ) * (exp γ0 * exp (-γ0 * (m : ℝ) ^ 2)) :=
          hsumT.tsum_le_tsum hterm (hc.mul_left _)
      _ = _ := by rw [tsum_mul_left]; rfl
  have hK : 0 ≤ Kconst P := tsum_nonneg (fun _ => by positivity)
  rw [muExc_poisson ze zh hs hP, ← hPdef]
  have hu : (1 / s) * exp (-γ) ≤ 1 / γ0 := by
    set u : ℝ := 1 / s with hu
    have : γ = γ0 * u := by rw [hγeq, hu]; ring
    rw [this]
    have h1 := Real.add_one_le_exp (γ0 * u)
    have hex : exp (-(γ0 * u)) * exp (γ0 * u) = 1 := by rw [← exp_add]; simp
    have hu0 : 0 ≤ u := by positivity
    rw [le_div_iff₀ hγ0pos]
    calc u * exp (-(γ0 * u)) * γ0 = (γ0 * u) * exp (-(γ0 * u)) := by ring
      _ ≤ exp (γ0 * u) * exp (-(γ0 * u)) := by
          apply mul_le_mul_of_nonneg_right _ (exp_pos _).le; linarith
      _ = 1 := by rw [mul_comm, hex]
  calc 1 / (s * P) * ∑' m : ℤ, wgt s P m * Sm P h1 ze zh m
      ≤ 1 / (s * P) * (8 * exp (-γ) * Kconst P) :=
        mul_le_mul_of_nonneg_left hT (by positivity)
    _ = (1 / P) * (8 * Kconst P) * ((1 / s) * exp (-γ)) := by field_simp
    _ ≤ (1 / P) * (8 * Kconst P) * (1 / γ0) :=
        mul_le_mul_of_nonneg_left hu (by positivity)
    _ = 8 * Kconst P / (P * γ0) := by field_simp



theorem muExc_bounded {h1 h2 : ℝ} (ze zh : ℝ) (hP : 0 < h1 + h2) :
    ∃ M : ℝ, ∀ s : ℝ, 0 < s → muExc s h1 h2 ze zh ≤ M := by
  refine ⟨max (2 * gsum 1 (2 * (h1 + h2)) 0 + 2 * gsum 1 (2 * (h1 + h2)) (zh - 2 * h1 + ze))
    (8 * Kconst (2 * (h1 + h2)) / ((2 * (h1 + h2)) * (π ^ 2 / (2 * (h1 + h2)) ^ 2))), fun s hs => ?_⟩
  rcases le_total s 1 with h | h
  · exact (muExc_le_small ze zh hs h hP).trans (le_max_right _ _)
  · exact (muExc_le_large ze zh h hP).trans (le_max_left _ _)

theorem muExc_continuousOn {h1 h2 : ℝ} (ze zh : ℝ) (hP : 0 < h1 + h2) :
    ContinuousOn (fun s => muExc s h1 h2 ze zh) (Ioi (0 : ℝ)) := by
  have hP' : 0 < 2 * (h1 + h2) := by positivity
  have g := fun c => continuousOn_gsum hP' c
  have hS : ContinuousOn (fun s => Sexc s h1 h2 ze zh) (Ioi (0 : ℝ)) := by
    have : (fun s => Sexc s h1 h2 ze zh) = fun s =>
        2 * gsum s (2 * (h1 + h2)) 0 - gsum s (2 * (h1 + h2)) (ze - 2 * h1 + ze)
          - gsum s (2 * (h1 + h2)) (zh - 2 * h1 + zh) - 2 * gsum s (2 * (h1 + h2)) (zh - ze)
          + 2 * gsum s (2 * (h1 + h2)) (zh - 2 * h1 + ze) := by
      funext s; exact Sexc_eq_gsum s h1 h2 ze zh
    rw [this]
    exact ((((continuousOn_const.mul (g _)).sub (g _)).sub (g _)).sub
      (continuousOn_const.mul (g _))).add (continuousOn_const.mul (g _))
  have hsq : ContinuousOn (fun s : ℝ => (√(π * s))⁻¹) (Ioi (0 : ℝ)) := by
    refine ContinuousOn.inv₀ (Real.continuous_sqrt.comp_continuousOn
      (continuousOn_const.mul continuousOn_id)) (fun s hs => ?_)
    have : 0 < s := hs
    exact (Real.sqrt_pos.2 (by positivity)).ne'
  exact hsq.mul hS

theorem muExc_laplaceData {h1 h2 : ℝ} (ze zh : ℝ) (hP : 0 < h1 + h2) :
    LaplaceData (fun s => muExc s h1 h2 ze zh) := by
  obtain ⟨M, hM⟩ := muExc_bounded ze zh hP
  refine ⟨fun s hs => muExc_nonneg ze zh hs hP,
    (muExc_continuousOn ze zh hP).aestronglyMeasurable measurableSet_Ioi, fun t ht => ?_⟩
  refine Integrable.mono' ((exp_neg_integrableOn_Ioi 0 ht).const_mul M) ?_ ?_
  · exact (continuous_exp.comp (by fun_prop : Continuous fun s : ℝ => -(s * t))).aestronglyMeasurable.mul
      ((muExc_continuousOn ze zh hP).aestronglyMeasurable measurableSet_Ioi)
  · refine (ae_restrict_iff' measurableSet_Ioi).2 (Eventually.of_forall fun s hs => ?_)
    have hs' : 0 < s := hs
    rw [norm_mul, Real.norm_of_nonneg (exp_pos _).le,
      Real.norm_of_nonneg (muExc_nonneg ze zh hs' hP)]
    calc exp (-(s * t)) * muExc s h1 h2 ze zh ≤ exp (-(s * t)) * M :=
          mul_le_mul_of_nonneg_left (hM s hs') (exp_pos _).le
      _ = M * exp (-t * s) := by rw [mul_comm, show -t * s = -(s * t) by ring]

/-- **T3 (proved part).**  The Laplace transform of the density `μ(s) = (πs)^{-1/2} S(s)` is `AdmissiblePotential`
in the library's convention (smooth, non-negative, completely monotone on `(0,∞)`), for every `h₁ + h₂ > 0`
and every pair of layer heights. -/
theorem gatedKernel_admissible {h1 h2 : ℝ} (ze zh : ℝ) (hP : 0 < h1 + h2) :
    AdmissiblePotential (lap (fun s => muExc s h1 h2 ze zh) 0) :=
  lap_admissible (muExc_laplaceData ze zh hP)



/-! ## T3, the interchange: the image series equals the Laplace transform -/

/-- one Gaussian-times-`(πs)^{-1/2}` atom: its Laplace integral is `(t + x²)^{-1/2}`. -/
noncomputable def atom (t x s : ℝ) : ℝ := (√(π * s))⁻¹ * exp (-(s * (t + x ^ 2)))

theorem atom_form {t x s : ℝ} (hs : 0 < s) :
    atom t x s = (√π)⁻¹ * (s ^ (1 / 2 - 1 : ℝ) * exp (-((t + x ^ 2) * s))) := by
  unfold atom
  rw [Real.sqrt_mul pi_pos.le, mul_inv, show (1 / 2 - 1 : ℝ) = -(1 / 2) by norm_num,
    Real.rpow_neg hs.le, ← Real.sqrt_eq_rpow]
  rw [show -((t + x ^ 2) * s) = -(s * (t + x ^ 2)) by ring]
  ring

theorem integrableOn_atom {t : ℝ} (x : ℝ) (ht : 0 < t) : IntegrableOn (atom t x) (Ioi (0 : ℝ)) := by
  have hb : 0 < t + x ^ 2 := by positivity
  have h := (integrableOn_rpow_mul_exp_neg_mul_rpow (p := 1) (s := -(1 / 2 : ℝ)) (b := t + x ^ 2)
    (by norm_num) one_pos hb).const_mul (√π)⁻¹
  refine IntegrableOn.congr_fun h (fun s hs => ?_) measurableSet_Ioi
  have hs' : 0 < s := hs
  rw [atom_form hs', Real.rpow_one, show (1 / 2 - 1 : ℝ) = -(1 / 2) by norm_num]
  simp only [neg_mul]

theorem integral_atom {t : ℝ} (x : ℝ) (ht : 0 < t) :
    ∫ s in Ioi (0 : ℝ), atom t x s = (√(t + x ^ 2))⁻¹ := by
  have hr : 0 < t + x ^ 2 := by positivity
  have h := Real.integral_rpow_mul_exp_neg_mul_Ioi (a := 1 / 2) (r := t + x ^ 2) (by norm_num) hr
  rw [setIntegral_congr_fun measurableSet_Ioi (fun s hs => atom_form (show 0 < s from hs)),
    integral_const_mul, h, Real.Gamma_one_half_eq]
  have hp : (√π) ≠ 0 := (Real.sqrt_pos.2 pi_pos).ne'
  rw [one_div, Real.inv_rpow hr.le, ← Real.sqrt_eq_rpow]
  field_simp

theorem atom_sub_norm_integral {t : ℝ} (x y : ℝ) (ht : 0 < t) :
    ∫ s in Ioi (0 : ℝ), ‖atom t x s - atom t y s‖ = |(√(t + x ^ 2))⁻¹ - (√(t + y ^ 2))⁻¹| := by
  have hx := integrableOn_atom x ht
  have hy := integrableOn_atom y ht
  have key : ∀ x y : ℝ, x ^ 2 ≤ y ^ 2 →
      ∫ s in Ioi (0 : ℝ), ‖atom t x s - atom t y s‖ = (√(t + x ^ 2))⁻¹ - (√(t + y ^ 2))⁻¹ := by
    intro x y hxy
    have hx := integrableOn_atom x ht
    have hy := integrableOn_atom y ht
    rw [setIntegral_congr_fun measurableSet_Ioi (g := fun s => atom t x s - atom t y s)
      (fun s hs => by
        have hs' : 0 < s := hs
        have : atom t y s ≤ atom t x s := by
          unfold atom
          apply mul_le_mul_of_nonneg_left _ (inv_nonneg.2 (Real.sqrt_nonneg _))
          apply exp_le_exp.2
          nlinarith
        simp only [Real.norm_eq_abs]
        exact abs_of_nonneg (sub_nonneg.2 this)),
      integral_sub hx hy, integral_atom x ht, integral_atom y ht]
  rcases le_total (x ^ 2) (y ^ 2) with h | h
  · rw [key x y h, abs_of_nonneg]
    have : (√(t + x ^ 2)) ≤ √(t + y ^ 2) := Real.sqrt_le_sqrt (by linarith)
    have hp : 0 < √(t + x ^ 2) := Real.sqrt_pos.2 (by positivity)
    exact sub_nonneg.2 (inv_anti₀ hp this)
  · have := key y x h
    rw [show ∫ s in Ioi (0 : ℝ), ‖atom t x s - atom t y s‖
        = ∫ s in Ioi (0 : ℝ), ‖atom t y s - atom t x s‖ from
        setIntegral_congr_fun measurableSet_Ioi (fun s _ => by rw [norm_sub_rev]), this,
      abs_sub_comm, abs_of_nonneg]
    have : (√(t + y ^ 2)) ≤ √(t + x ^ 2) := Real.sqrt_le_sqrt (by linarith)
    have hp : 0 < √(t + y ^ 2) := Real.sqrt_pos.2 (by positivity)
    exact sub_nonneg.2 (inv_anti₀ hp this)



/-! ### absolute summability of the neutral combination -/

theorem kdiff_le {t P c c' : ℝ} (ht : 0 < t) (hP : 0 < P) (n : ℤ)
    (hn : 2 * (|c| + |c'|) + 1 ≤ P * |(n : ℝ)|) :
    |(√(t + (c - P * n) ^ 2))⁻¹ - (√(t + (c' - P * n) ^ 2))⁻¹|
      ≤ 12 * |c' - c| / P ^ 2 * |(n : ℝ)| ^ (-(2 : ℝ)) := by
  set N : ℝ := |(n : ℝ)| with hN
  have hPN : 1 ≤ P * N := by
    have := abs_nonneg c; have := abs_nonneg c'; linarith
  have hNpos : 0 < N := by
    by_contra h
    rw [not_lt] at h
    nlinarith
  set x := c - P * n with hx
  set y := c' - P * n with hy
  have hax : t + x ^ 2 > 0 := by positivity
  have hby : t + y ^ 2 > 0 := by positivity
  set a := √(t + x ^ 2) with ha
  set b := √(t + y ^ 2) with hb
  have ha2 : a ^ 2 = t + x ^ 2 := Real.sq_sqrt hax.le
  have hb2 : b ^ 2 = t + y ^ 2 := Real.sq_sqrt hby.le
  have hapos : 0 < a := Real.sqrt_pos.2 hax
  have hbpos : 0 < b := Real.sqrt_pos.2 hby
  have hPn : |P * (n : ℝ)| = P * N := by rw [abs_mul, abs_of_pos hP]
  have hxlow : P * N / 2 ≤ |x| := by
    have h1 : |P * (n : ℝ)| ≤ |c| + |x| := by
      have : P * (n : ℝ) = c - x := by rw [hx]; ring
      rw [this]; exact abs_sub _ _
    have := abs_nonneg c'
    linarith
  have hylow : P * N / 2 ≤ |y| := by
    have h1 : |P * (n : ℝ)| ≤ |c'| + |y| := by
      have : P * (n : ℝ) = c' - y := by rw [hy]; ring
      rw [this]; exact abs_sub _ _
    have := abs_nonneg c
    linarith
  have haq : P * N / 2 ≤ a := hxlow.trans (Real.abs_le_sqrt (by linarith [sq_nonneg x]))
  have hbq : P * N / 2 ≤ b := hylow.trans (Real.abs_le_sqrt (by linarith [sq_nonneg y]))
  have hid : a⁻¹ - b⁻¹ = (y ^ 2 - x ^ 2) / (a * b * (a + b)) := by
    rw [← sub_eq_zero]
    field_simp
    nlinarith [ha2, hb2]
  have hnum : |y ^ 2 - x ^ 2| ≤ |c' - c| * (3 * (P * N)) := by
    have e : y ^ 2 - x ^ 2 = (c' - c) * (c + c' - 2 * (P * n)) := by rw [hx, hy]; ring
    rw [e, abs_mul]
    apply mul_le_mul_of_nonneg_left _ (abs_nonneg _)
    have h1 : |c + c' - 2 * (P * (n : ℝ))| ≤ |c + c'| + |2 * (P * (n : ℝ))| := abs_sub _ _
    have h2 : |c + c'| ≤ |c| + |c'| := abs_add_le _ _
    have h3 : |2 * (P * (n : ℝ))| = 2 * (P * N) := by rw [abs_mul, hPn, abs_two]
    have := abs_nonneg c; have := abs_nonneg c'
    linarith
  have hden : (P * N / 2) * (P * N / 2) * (P * N / 2 + P * N / 2) ≤ a * b * (a + b) := by
    have : 0 ≤ P * N / 2 := by positivity
    gcongr
  rw [hid, abs_div, abs_of_pos (by positivity : 0 < a * b * (a + b))]
  rw [div_le_iff₀ (by positivity)]
  have hrp : N ^ (-(2 : ℝ)) = (N ^ 2)⁻¹ := by rw [Real.rpow_neg hNpos.le, Real.rpow_two]
  rw [hrp]
  have hX : 0 ≤ 12 * |c' - c| / P ^ 2 * (N ^ 2)⁻¹ := by positivity
  calc |y ^ 2 - x ^ 2| ≤ |c' - c| * (3 * (P * N)) := hnum
    _ = 12 * |c' - c| / P ^ 2 * (N ^ 2)⁻¹ *
          ((P * N / 2) * (P * N / 2) * (P * N / 2 + P * N / 2)) := by
        field_simp; ring
    _ ≤ _ := mul_le_mul_of_nonneg_left hden hX

theorem kdiff_summable {t P : ℝ} (ht : 0 < t) (hP : 0 < P) (c c' : ℝ) :
    Summable (fun n : ℤ => |(√(t + (c - P * n) ^ 2))⁻¹ - (√(t + (c' - P * n) ^ 2))⁻¹|) := by
  have hg := (Real.summable_abs_int_rpow (b := 2) one_lt_two).mul_left (12 * |c' - c| / P ^ 2)
  refine Summable.of_norm_bounded_eventually hg ?_
  rw [Filter.eventually_cofinite]
  set K := 2 * (|c| + |c'|) + 1 with hK
  set M : ℤ := ⌈K / P⌉ with hM
  refine (Set.finite_Icc (-M) M).subset (fun n hn => ?_)
  by_contra hnot
  apply hn
  have hnabs : M < |n| := by
    rw [Set.mem_Icc, ← abs_le] at hnot
    exact not_le.1 hnot
  have h1 : (M : ℝ) < |(n : ℝ)| := by
    have : ((M : ℤ) : ℝ) < ((|n| : ℤ) : ℝ) := by exact_mod_cast hnabs
    simpa [Int.cast_abs] using this
  have h2 : K / P ≤ M := Int.le_ceil _
  have h3 : K ≤ P * |(n : ℝ)| := by
    have : K / P < |(n : ℝ)| := lt_of_le_of_lt h2 h1
    rw [div_lt_iff₀ hP] at this
    linarith
  rw [Real.norm_eq_abs, abs_abs]
  exact kdiff_le ht hP n h3

/-! ### the image series and its termwise Laplace representation -/

/-- `(t + (c - P n)²)^{-1/2}`: one term of the image series (in-plane distance² `t`, vertical offset `c - P n`). -/
noncomputable def kk (t P c : ℝ) (n : ℤ) : ℝ := (√(t + (c - P * n) ^ 2))⁻¹

/-- The image series of the exciton--exciton kernel `V_ee + V_hh - 2 V_eh` for grounded planes at `z = h₁` and
`z = -h₂` (period `P = 2(h₁+h₂)`), at `t = r²`, summed over `n` with the five distinct image offsets grouped
(direct and image, `ee`, `hh`, `eh`) so that the series is absolutely convergent. -/
noncomputable def Uimg (t h1 h2 ze zh : ℝ) : ℝ :=
  ∑' n : ℤ, (2 * kk t (2 * (h1 + h2)) 0 n - kk t (2 * (h1 + h2)) (ze - 2 * h1 + ze) n
    - kk t (2 * (h1 + h2)) (zh - 2 * h1 + zh) n - 2 * kk t (2 * (h1 + h2)) (zh - ze) n
    + 2 * kk t (2 * (h1 + h2)) (zh - 2 * h1 + ze) n)

noncomputable def Fn (t P c0 c1 c2 c3 c4 : ℝ) (n : ℤ) (s : ℝ) : ℝ :=
  2 * atom t (c0 - P * n) s - atom t (c1 - P * n) s - atom t (c2 - P * n) s
    - 2 * atom t (c3 - P * n) s + 2 * atom t (c4 - P * n) s

theorem Fn_integrable {t : ℝ} (ht : 0 < t) (P c0 c1 c2 c3 c4 : ℝ) (n : ℤ) :
    Integrable (Fn t P c0 c1 c2 c3 c4 n) (volume.restrict (Ioi (0 : ℝ))) := by
  have h0 := integrableOn_atom (c0 - P * n) ht
  have h1 := integrableOn_atom (c1 - P * n) ht
  have h2 := integrableOn_atom (c2 - P * n) ht
  have h3 := integrableOn_atom (c3 - P * n) ht
  have h4 := integrableOn_atom (c4 - P * n) ht
  exact ((((h0.const_mul 2).sub h1).sub h2).sub (h3.const_mul 2)).add (h4.const_mul 2)

theorem Fn_integral {t : ℝ} (ht : 0 < t) (P c0 c1 c2 c3 c4 : ℝ) (n : ℤ) :
    ∫ s in Ioi (0 : ℝ), Fn t P c0 c1 c2 c3 c4 n s =
      2 * kk t P c0 n - kk t P c1 n - kk t P c2 n - 2 * kk t P c3 n + 2 * kk t P c4 n := by
  have h0 := integrableOn_atom (c0 - P * n) ht
  have h1 := integrableOn_atom (c1 - P * n) ht
  have h2 := integrableOn_atom (c2 - P * n) ht
  have h3 := integrableOn_atom (c3 - P * n) ht
  have h4 := integrableOn_atom (c4 - P * n) ht
  have i01 : Integrable (fun s => 2 * atom t (c0 - P * n) s - atom t (c1 - P * n) s)
      (volume.restrict (Ioi (0 : ℝ))) := (h0.const_mul 2).sub h1
  have i012 : Integrable (fun s => 2 * atom t (c0 - P * n) s - atom t (c1 - P * n) s
      - atom t (c2 - P * n) s) (volume.restrict (Ioi (0 : ℝ))) := i01.sub h2
  have i0123 : Integrable (fun s => 2 * atom t (c0 - P * n) s - atom t (c1 - P * n) s
      - atom t (c2 - P * n) s - 2 * atom t (c3 - P * n) s) (volume.restrict (Ioi (0 : ℝ))) :=
    i012.sub (h3.const_mul 2)
  unfold Fn kk
  rw [integral_add i0123 (h4.const_mul 2), integral_sub i012 (h3.const_mul 2), integral_sub i01 h2,
    integral_sub (h0.const_mul 2) h1, integral_const_mul, integral_const_mul, integral_const_mul,
    integral_atom _ ht, integral_atom _ ht, integral_atom _ ht, integral_atom _ ht, integral_atom _ ht]

theorem Fn_norm_integral_le {t : ℝ} (ht : 0 < t) (P c0 c1 c2 c3 c4 : ℝ) (n : ℤ) :
    ∫ s in Ioi (0 : ℝ), ‖Fn t P c0 c1 c2 c3 c4 n s‖ ≤
      2 * |kk t P c0 n - kk t P c3 n| + |kk t P c1 n - kk t P c4 n| + |kk t P c2 n - kk t P c4 n| := by
  have h0 := integrableOn_atom (c0 - P * n) ht
  have h1 := integrableOn_atom (c1 - P * n) ht
  have h2 := integrableOn_atom (c2 - P * n) ht
  have h3 := integrableOn_atom (c3 - P * n) ht
  have h4 := integrableOn_atom (c4 - P * n) ht
  have d03 : Integrable (fun s => ‖atom t (c0 - P * n) s - atom t (c3 - P * n) s‖)
      (volume.restrict (Ioi (0 : ℝ))) := (h0.sub h3).norm
  have d14 : Integrable (fun s => ‖atom t (c1 - P * n) s - atom t (c4 - P * n) s‖)
      (volume.restrict (Ioi (0 : ℝ))) := (h1.sub h4).norm
  have d24 : Integrable (fun s => ‖atom t (c2 - P * n) s - atom t (c4 - P * n) s‖)
      (volume.restrict (Ioi (0 : ℝ))) := (h2.sub h4).norm
  have hpt : ∀ s, ‖Fn t P c0 c1 c2 c3 c4 n s‖ ≤
      2 * ‖atom t (c0 - P * n) s - atom t (c3 - P * n) s‖
        + ‖atom t (c1 - P * n) s - atom t (c4 - P * n) s‖
        + ‖atom t (c2 - P * n) s - atom t (c4 - P * n) s‖ := by
    intro s
    simp only [Fn, Real.norm_eq_abs]
    set u := atom t (c0 - P * n) s - atom t (c3 - P * n) s
    set v := atom t (c1 - P * n) s - atom t (c4 - P * n) s
    set w := atom t (c2 - P * n) s - atom t (c4 - P * n) s
    have e : 2 * atom t (c0 - P * n) s - atom t (c1 - P * n) s - atom t (c2 - P * n) s
        - 2 * atom t (c3 - P * n) s + 2 * atom t (c4 - P * n) s = 2 * u - v - w := by
      simp only [u, v, w]; ring
    rw [e]
    have h1 : |2 * u - v - w| ≤ |2 * u - v| + |w| := abs_sub _ _
    have h2 : |2 * u - v| ≤ |2 * u| + |v| := abs_sub _ _
    have h3 : |2 * u| = 2 * |u| := by rw [abs_mul, abs_two]
    linarith
  have i1 : Integrable (fun s => 2 * ‖atom t (c0 - P * n) s - atom t (c3 - P * n) s‖)
      (volume.restrict (Ioi (0 : ℝ))) := d03.const_mul 2
  have i2 : Integrable (fun s => 2 * ‖atom t (c0 - P * n) s - atom t (c3 - P * n) s‖
      + ‖atom t (c1 - P * n) s - atom t (c4 - P * n) s‖) (volume.restrict (Ioi (0 : ℝ))) := i1.add d14
  have i3 : Integrable (fun s => 2 * ‖atom t (c0 - P * n) s - atom t (c3 - P * n) s‖
      + ‖atom t (c1 - P * n) s - atom t (c4 - P * n) s‖
      + ‖atom t (c2 - P * n) s - atom t (c4 - P * n) s‖) (volume.restrict (Ioi (0 : ℝ))) := i2.add d24
  calc ∫ s in Ioi (0 : ℝ), ‖Fn t P c0 c1 c2 c3 c4 n s‖
      ≤ ∫ s in Ioi (0 : ℝ), (2 * ‖atom t (c0 - P * n) s - atom t (c3 - P * n) s‖
        + ‖atom t (c1 - P * n) s - atom t (c4 - P * n) s‖
        + ‖atom t (c2 - P * n) s - atom t (c4 - P * n) s‖) :=
        integral_mono (Fn_integrable ht P c0 c1 c2 c3 c4 n).norm i3 hpt
    _ = _ := by
        rw [integral_add i2 d24, integral_add i1 d14, integral_const_mul,
          atom_sub_norm_integral _ _ ht, atom_sub_norm_integral _ _ ht,
          atom_sub_norm_integral _ _ ht]
        rfl

theorem Fn_tsum {t s : ℝ} (hs : 0 < s) {P : ℝ} (hP : 0 < P) (c0 c1 c2 c3 c4 : ℝ) :
    ∑' n : ℤ, Fn t P c0 c1 c2 c3 c4 n s =
      (√(π * s))⁻¹ * exp (-(s * t)) *
        (2 * gsum s P c0 - gsum s P c1 - gsum s P c2 - 2 * gsum s P c3 + 2 * gsum s P c4) := by
  have hatom : ∀ x : ℝ, atom t x s = (√(π * s))⁻¹ * exp (-(s * t)) * exp (-s * x ^ 2) := by
    intro x
    unfold atom
    rw [show -(s * (t + x ^ 2)) = -(s * t) + -s * x ^ 2 by ring, exp_add]
    ring
  have H := ((((summable_gsum_term hs hP.ne' c0).hasSum.mul_left 2).sub
    (summable_gsum_term hs hP.ne' c1).hasSum).sub (summable_gsum_term hs hP.ne' c2).hasSum).sub
    ((summable_gsum_term hs hP.ne' c3).hasSum.mul_left 2) |>.add
    ((summable_gsum_term hs hP.ne' c4).hasSum.mul_left 2)
  have H2 := H.mul_left ((√(π * s))⁻¹ * exp (-(s * t)))
  have hfun : (fun n : ℤ => Fn t P c0 c1 c2 c3 c4 n s) = fun n : ℤ =>
      (√(π * s))⁻¹ * exp (-(s * t)) *
        (2 * exp (-s * (c0 - P * n) ^ 2) - exp (-s * (c1 - P * n) ^ 2) - exp (-s * (c2 - P * n) ^ 2)
          - 2 * exp (-s * (c3 - P * n) ^ 2) + 2 * exp (-s * (c4 - P * n) ^ 2)) := by
    funext n
    simp only [Fn, hatom]
    ring
  rw [hfun, H2.tsum_eq]
  unfold gsum
  ring

theorem Uimg_eq_lap {t h1 h2 : ℝ} (ze zh : ℝ) (ht : 0 < t) (hP : 0 < h1 + h2) :
    Uimg t h1 h2 ze zh = lap (fun s => muExc s h1 h2 ze zh) 0 t := by
  set P : ℝ := 2 * (h1 + h2) with hPdef
  have hP' : 0 < P := by positivity
  set c1 : ℝ := ze - 2 * h1 + ze
  set c2 : ℝ := zh - 2 * h1 + zh
  set c3 : ℝ := zh - ze
  set c4 : ℝ := zh - 2 * h1 + ze
  have hI : ∀ n : ℤ, Integrable (Fn t P 0 c1 c2 c3 c4 n) (volume.restrict (Ioi (0 : ℝ))) :=
    fun n => Fn_integrable ht P 0 c1 c2 c3 c4 n
  have hsum : Summable (fun n : ℤ => ∫ s in Ioi (0 : ℝ), ‖Fn t P 0 c1 c2 c3 c4 n s‖) := by
    refine Summable.of_nonneg_of_le (fun n => integral_nonneg (fun s => norm_nonneg _))
      (fun n => Fn_norm_integral_le ht P 0 c1 c2 c3 c4 n) ?_
    exact (((kdiff_summable ht hP' 0 c3).mul_left 2).add (kdiff_summable ht hP' c1 c4)).add
      (kdiff_summable ht hP' c2 c4)
  have key := integral_tsum_of_summable_integral_norm hI hsum
  unfold Uimg lap
  calc ∑' n : ℤ, (2 * kk t P 0 n - kk t P c1 n - kk t P c2 n - 2 * kk t P c3 n + 2 * kk t P c4 n)
      = ∑' n : ℤ, ∫ s in Ioi (0 : ℝ), Fn t P 0 c1 c2 c3 c4 n s :=
        tsum_congr (fun n => (Fn_integral ht P 0 c1 c2 c3 c4 n).symm)
    _ = ∫ s in Ioi (0 : ℝ), ∑' n : ℤ, Fn t P 0 c1 c2 c3 c4 n s := key
    _ = ∫ s in Ioi (0 : ℝ), (-s) ^ 0 * (exp (-(s * t)) * muExc s h1 h2 ze zh) := by
        refine setIntegral_congr_fun measurableSet_Ioi (fun s hs => ?_)
        have hs' : 0 < s := hs
        rw [Fn_tsum hs' hP' 0 c1 c2 c3 c4, muExc, Sexc_eq_gsum]
        ring

/-- The grouped series defining `Uimg` is a genuinely convergent (indeed absolutely convergent) series: `tsum` is
not silently `0` by non-summability. -/
theorem Uimg_summable {t h1 h2 : ℝ} (ze zh : ℝ) (ht : 0 < t) (hP : 0 < h1 + h2) :
    Summable (fun n : ℤ => 2 * kk t (2 * (h1 + h2)) 0 n - kk t (2 * (h1 + h2)) (ze - 2 * h1 + ze) n
      - kk t (2 * (h1 + h2)) (zh - 2 * h1 + zh) n - 2 * kk t (2 * (h1 + h2)) (zh - ze) n
      + 2 * kk t (2 * (h1 + h2)) (zh - 2 * h1 + ze) n) := by
  set P : ℝ := 2 * (h1 + h2) with hPdef
  have hP' : 0 < P := by positivity
  set c1 : ℝ := ze - 2 * h1 + ze
  set c2 : ℝ := zh - 2 * h1 + zh
  set c3 : ℝ := zh - ze
  set c4 : ℝ := zh - 2 * h1 + ze
  have hsum : Summable (fun n : ℤ => ∫ s in Ioi (0 : ℝ), ‖Fn t P 0 c1 c2 c3 c4 n s‖) := by
    refine Summable.of_nonneg_of_le (fun n => integral_nonneg (fun s => norm_nonneg _))
      (fun n => Fn_norm_integral_le ht P 0 c1 c2 c3 c4 n) ?_
    exact (((kdiff_summable ht hP' 0 c3).mul_left 2).add (kdiff_summable ht hP' c1 c4)).add
      (kdiff_summable ht hP' c2 c4)
  refine Summable.of_norm_bounded hsum (fun n => ?_)
  rw [← Fn_integral ht P 0 c1 c2 c3 c4 n]
  exact norm_integral_le_integral_norm _

theorem admissible_congr {f g : ℝ → ℝ} (h : AdmissiblePotential f)
    (hfg : ∀ t : ℝ, 0 < t → f t = g t) : AdmissiblePotential g := by
  obtain ⟨h1, h2, h3⟩ := h
  refine ⟨h1.congr (fun t ht => (hfg t ht).symm), fun t ht => (hfg t ht) ▸ h2 t ht, ?_⟩
  intro r t ht
  have hev : f =ᶠ[𝓝 t] g :=
    Filter.eventually_of_mem (isOpen_Ioi.mem_nhds ht) (fun x hx => hfg x hx)
  rw [← hev.iteratedDeriv_eq r]
  exact h3 r t ht

/-- **T3 (full).**  The image-series kernel of the dual-gated bilayer, `t ↦ Uimg t h₁ h₂ z_e z_h`, is
`AdmissiblePotential` (smooth, non-negative, completely monotone on `(0, ∞)`) for every `h₁ + h₂ > 0` and all
layer heights. -/
theorem imageSeries_admissible {h1 h2 : ℝ} (ze zh : ℝ) (hP : 0 < h1 + h2) :
    AdmissiblePotential (fun t => Uimg t h1 h2 ze zh) :=
  admissible_congr (gatedKernel_admissible ze zh hP)
    (fun _ ht => (Uimg_eq_lap ze zh ht hP).symm)


/-! ## Negative control 3: neutrality matters -/

/-- Dropping the `V_hh` term (a non-neutral combination `V_ee - 2 V_eh`) is not non-negative mode by mode:
at `a = b = π/2` the factor is `-2`. -/
theorem unneutral_not_nonneg :
    ¬ ∀ a b : ℝ, 0 ≤ (1 - cos (2 * a)) - 2 * (cos (b - a) - cos (a + b)) := by
  intro h
  have := h (π / 2) (π / 2)
  have e1 : 2 * (π / 2) = π := by ring
  have e2 : π / 2 - π / 2 = 0 := by ring
  have e3 : π / 2 + π / 2 = π := by ring
  rw [e1, e2, e3, cos_pi, cos_zero] at this
  norm_num at this

end GatedKernel

/-! ## Axiom audit -/
#print axioms GatedKernel.trig_core
#print axioms GatedKernel.trig_core_nonneg
#print axioms GatedKernel.image_plane_top
#print axioms GatedKernel.image_plane_bottom
#print axioms GatedKernel.gGreen_top
#print axioms GatedKernel.gGreen_bottom
#print axioms GatedKernel.gsum_poisson
#print axioms GatedKernel.Sexc_poisson
#print axioms GatedKernel.Sexc_nonneg
#print axioms GatedKernel.lap_admissible
#print axioms GatedKernel.gatedKernel_admissible
#print axioms GatedKernel.Uimg_eq_lap
#print axioms GatedKernel.Uimg_summable
#print axioms GatedKernel.imageSeries_admissible
#print axioms GatedKernel.wrong_sign_not_nonneg
#print axioms GatedKernel.wrong_sign_not_identity
#print axioms GatedKernel.unneutral_not_nonneg
