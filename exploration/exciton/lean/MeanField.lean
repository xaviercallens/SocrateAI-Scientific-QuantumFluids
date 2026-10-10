import Mathlib

/-!
# Mean-field statements used by the exciton-fluid study (Mathlib only)

* `uniform_minimises` (X6): for a translation-invariant, positive-semidefinite interaction on a finite abelian group
  (a discretised torus) the interaction energy `Σ_{x,y} n(x) n(y) U(x - y)` of a density with a given total mass is
  minimised by the uniform density.  Positive semidefiniteness of the kernel is a *hypothesis*; that completely
  monotone kernels are positive definite is classical (Schoenberg, Bernstein) and is tested numerically by the solver.
* `telescoping_integral`: `∫₀^R [g(t) - g(t + c)] dt = ∫₀^c g - ∫_R^{R+c} g`; with `g → 0` this is the identity behind
  the capacitor formula `Ũ(0) = π ∫₀^{d²} g` of the plan (appendix A.2).
* `bilayer_hartree`: for `g(t) = 2 t^(-1/2)` and `c = d²`, `∫₀^c g = 4 d` (`d > 0`).  With the polar-coordinate factor `π`
  and the limit `g → 0` (neither is formalised here) this is `Ũ(0) = 4π d` in units `e²/(4πε₀ε) = 1`, i.e. the paper's
  `g_H = 8πd` in Rydberg units.
* `variational_lower_bound` (X5, schema): a non-negative kinetic term and a pointwise lower bound on the potential
  give a lower bound on the expected energy of any normalised state.

Status: kernel-checked under Lean 4.34.1 / Mathlib d13f23b7 and under Lean 4.34.0-rc2 / Mathlib 85e3a25.  Independent
re-check by a separate instance of the same model: `VERIFICATION_BY_INSTANCE_2026-10-10.md` (VERIFIED WITH REMARKS; not
human review).  The section at the end of the file ("Verifier probes") was written and compiled by that instance and
integrated verbatim afterwards; it shows that the hypothesis `hU` is satisfiable and cannot be dropped.
`variational_lower_bound` is a schema (monotonicity of the integral for a probability measure); positive semidefiniteness
is a hypothesis of `uniform_minimises`.  Not part of the audited library `lean_src/`.
-/

open MeasureTheory

namespace MeanField

/-- X6. The uniform density minimises a positive-semidefinite translation-invariant interaction at fixed mass. -/
theorem uniform_minimises {G : Type*} [AddCommGroup G] [Fintype G] [DecidableEq G] [Nonempty G]
    (U : G → ℝ) (hU : ∀ f : G → ℝ, 0 ≤ ∑ x, ∑ y, f x * f y * U (x - y)) (n : G → ℝ) :
    (∑ x, ∑ y, ((∑ z, n z) / Fintype.card G) * ((∑ z, n z) / Fintype.card G) * U (x - y))
      ≤ ∑ x, ∑ y, n x * n y * U (x - y) := by
  set m : ℝ := (∑ z, n z) / Fintype.card G with hm
  have hcard : (Fintype.card G : ℝ) ≠ 0 := by exact_mod_cast Fintype.card_ne_zero
  have hf : ∑ y, (n y - m) = 0 := by
    rw [Finset.sum_sub_distrib, Finset.sum_const, Finset.card_univ, nsmul_eq_mul, hm]
    field_simp
    ring
  have hcol : ∀ y, ∑ x, U (x - y) = ∑ z, U z := fun y =>
    Fintype.sum_equiv (Equiv.subRight y) _ _ (fun x => rfl)
  have hrow : ∀ x, ∑ y, U (x - y) = ∑ z, U z := fun x =>
    Fintype.sum_equiv (Equiv.subLeft x) _ _ (fun y => rfl)
  -- expand `n x n y = m m + m f(y) + f(x) m + f(x) f(y)` with `f = n - m`
  have key : ∑ x, ∑ y, n x * n y * U (x - y) =
      (∑ x, ∑ y, m * m * U (x - y)) + (∑ x, ∑ y, (n x - m) * (n y - m) * U (x - y)) := by
    have e1 : ∀ x y, n x * n y * U (x - y) =
        m * m * U (x - y) + m * (n y - m) * U (x - y) + (n x - m) * m * U (x - y)
          + (n x - m) * (n y - m) * U (x - y) := fun x y => by ring
    simp_rw [e1, Finset.sum_add_distrib]
    have c1 : ∑ x, ∑ y, m * (n y - m) * U (x - y) = 0 := by
      rw [Finset.sum_comm]
      have : ∀ y, ∑ x, m * (n y - m) * U (x - y) = m * (n y - m) * ∑ z, U z := fun y => by
        rw [← Finset.mul_sum, hcol y]
      simp_rw [this]
      rw [← Finset.sum_mul, ← Finset.mul_sum, hf]
      ring
    have c2 : ∑ x, ∑ y, (n x - m) * m * U (x - y) = 0 := by
      have : ∀ x, ∑ y, (n x - m) * m * U (x - y) = (n x - m) * m * ∑ z, U z := fun x => by
        rw [← Finset.mul_sum, hrow x]
      simp_rw [this]
      rw [← Finset.sum_mul, ← Finset.sum_mul, hf]
      ring
    rw [c1, c2]
    ring
  rw [key]
  have := hU (fun x => n x - m)
  linarith

/-- Telescoping of a translated integral. -/
theorem telescoping_integral {g : ℝ → ℝ} {c R : ℝ} (hc : 0 ≤ c) (hR : 0 ≤ R)
    (hg : IntervalIntegrable g volume 0 (R + c)) :
    ∫ t in (0 : ℝ)..R, (g t - g (t + c)) = (∫ t in (0 : ℝ)..c, g t) - ∫ t in R..(R + c), g t := by
  have hRc : (0 : ℝ) ≤ R + c := by linarith
  have h0R : IntervalIntegrable g volume 0 R :=
    hg.mono_set (by
      rw [Set.uIcc_of_le hR, Set.uIcc_of_le hRc]
      exact Set.Icc_subset_Icc le_rfl (by linarith))
  have hcd : IntervalIntegrable g volume c (R + c) :=
    hg.mono_set (by
      rw [Set.uIcc_of_le (by linarith), Set.uIcc_of_le hRc]
      exact Set.Icc_subset_Icc hc le_rfl)
  have h0c : IntervalIntegrable g volume 0 c :=
    hg.mono_set (by
      rw [Set.uIcc_of_le hc, Set.uIcc_of_le hRc]
      exact Set.Icc_subset_Icc le_rfl (by linarith))
  have hshift : IntervalIntegrable (fun t => g (t + c)) volume 0 R := by
    have h2 : IntervalIntegrable (fun t => g (t + c)) volume (0 - c) (R + c - c) := hg.comp_add_right c
    have hsub : Set.uIcc (0 : ℝ) R ⊆ Set.uIcc (0 - c) (R + c - c) := by
      rw [Set.uIcc_of_le hR, Set.uIcc_of_le (by linarith)]
      exact Set.Icc_subset_Icc (by linarith) (by linarith)
    exact h2.mono_set hsub
  rw [intervalIntegral.integral_sub h0R hshift, intervalIntegral.integral_comp_add_right g c, zero_add]
  exact intervalIntegral.integral_interval_sub_interval_comm h0R hcd h0c

/-- The Hartree coefficient of two interlayer dipoles: `∫₀^{d²} 2 t^(-1/2) dt = 4 d`. -/
theorem bilayer_hartree {d : ℝ} (hd : 0 < d) :
    ∫ t in (0 : ℝ)..d ^ 2, 2 * t ^ (-(1 / 2 : ℝ)) = 4 * d := by
  rw [intervalIntegral.integral_const_mul, integral_rpow (Or.inl (by norm_num))]
  have h1 : (d ^ 2) ^ (-(1 / 2 : ℝ) + 1) = d := by
    rw [show -(1 / 2 : ℝ) + 1 = 1 / 2 by norm_num, ← Real.sqrt_eq_rpow, Real.sqrt_sq hd.le]
  have h0 : (0 : ℝ) ^ (-(1 / 2 : ℝ) + 1) = 0 := by
    rw [show -(1 / 2 : ℝ) + 1 = 1 / 2 by norm_num]
    exact Real.zero_rpow (by norm_num)
  rw [h1, h0]
  ring

/-- X5 (schema): a non-negative kinetic term and a pointwise lower bound `c` on the potential bound the expected
energy of every normalised state. -/
theorem variational_lower_bound {Ω : Type*} [MeasurableSpace Ω] (μ : Measure Ω) [IsProbabilityMeasure μ]
    {T U : Ω → ℝ} {c : ℝ} (hT : ∀ ω, 0 ≤ T ω) (hU : ∀ ω, c ≤ U ω)
    (hTi : Integrable T μ) (hUi : Integrable U μ) :
    c ≤ ∫ ω, (T ω + U ω) ∂μ := by
  have h : ∀ ω, c ≤ T ω + U ω := fun ω => by linarith [hT ω, hU ω]
  have := integral_mono (integrable_const c) (hTi.add hUi) h
  simpa using this

end MeanField

#print axioms MeanField.uniform_minimises
#print axioms MeanField.telescoping_integral
#print axioms MeanField.bilayer_hartree
#print axioms MeanField.variational_lower_bound


/-! ## ===== Verifier probes (independent instance) ===== -/

namespace VerifierProbe
open MeasureTheory

/-- Indicator of `0`: the simplest positive-semidefinite translation-invariant kernel. -/
def indU {G : Type*} [AddCommGroup G] [DecidableEq G] (z : G) : ℝ := if z = 0 then 1 else 0

/-- `hU` is satisfiable: it holds for `indU` on every finite abelian group. -/
theorem hU_indicator {G : Type*} [AddCommGroup G] [Fintype G] [DecidableEq G] (f : G → ℝ) :
    0 ≤ ∑ x : G, ∑ y : G, f x * f y * indU (x - y) := by
  have h : ∀ x : G, ∑ y : G, f x * f y * indU (x - y) = f x * f x := by
    intro x
    rw [Finset.sum_eq_single x]
    · simp [indU]
    · intro y _ hy
      have hne : x - y ≠ 0 := sub_ne_zero.mpr (Ne.symm hy)
      simp [indU, hne]
    · intro hx; exact absurd (Finset.mem_univ x) hx
  simp_rw [h]
  exact Finset.sum_nonneg (fun x _ => mul_self_nonneg (f x))

/-- Instance of `uniform_minimises`: the uniform density minimises `Σ n(x)²` at fixed mass (Cauchy-Schwarz). -/
theorem uniform_minimises_instance {G : Type*} [AddCommGroup G] [Fintype G] [DecidableEq G] [Nonempty G]
    (n : G → ℝ) :
    (∑ x : G, ∑ y : G, ((∑ z : G, n z) / Fintype.card G) * ((∑ z : G, n z) / Fintype.card G) * indU (x - y))
      ≤ ∑ x : G, ∑ y : G, n x * n y * indU (x - y) :=
  MeanField.uniform_minimises indU hU_indicator n

/-- A kernel on `Fin 2` that is NOT positive semidefinite: `U 0 = 0`, `U 1 = 1`. -/
def Ubad (z : Fin 2) : ℝ := ((z : ℕ) : ℝ)

theorem Ubad_not_psd : ¬ (∀ f : Fin 2 → ℝ, 0 ≤ ∑ x, ∑ y, f x * f y * Ubad (x - y)) := by
  intro h
  have h' := h ![1, -1]
  have e1 : ((0 : Fin 2) - 1) = 1 := by decide
  have e2 : ((1 : Fin 2) - 0) = 1 := by decide
  have e3 : ((0 : Fin 2) - 0) = 0 := by decide
  have e4 : ((1 : Fin 2) - 1) = 0 := by decide
  norm_num [Fin.sum_univ_two, e1, e2, e3, e4, Ubad] at h'

/-- Without `hU` the conclusion of `uniform_minimises` is false: uniform energy 1/2 > energy 0 of `(1, 0)`. -/
theorem conclusion_fails_for_Ubad :
    ¬ ((∑ x : Fin 2, ∑ y : Fin 2, ((∑ z : Fin 2, (![1, 0] : Fin 2 → ℝ) z) / (Fintype.card (Fin 2) : ℝ)) *
          ((∑ z : Fin 2, (![1, 0] : Fin 2 → ℝ) z) / (Fintype.card (Fin 2) : ℝ)) * Ubad (x - y))
      ≤ ∑ x : Fin 2, ∑ y : Fin 2, (![1, 0] : Fin 2 → ℝ) x * (![1, 0] : Fin 2 → ℝ) y * Ubad (x - y)) := by
  intro h
  have e1 : ((0 : Fin 2) - 1) = 1 := by decide
  have e2 : ((1 : Fin 2) - 0) = 1 := by decide
  have e3 : ((0 : Fin 2) - 0) = 0 := by decide
  have e4 : ((1 : Fin 2) - 1) = 0 := by decide
  norm_num [Fin.sum_univ_two, e1, e2, e3, e4, Ubad] at h

/-- `telescoping_integral` has satisfiable hypotheses: `g t = 2 t^(-1/2)` is interval integrable at 0. -/
theorem telescoping_instance (R c : ℝ) (hR : 0 ≤ R) (hc : 0 ≤ c) :
    ∫ t in (0 : ℝ)..R, ((fun t : ℝ => 2 * t ^ (-(1 / 2 : ℝ))) t - (fun t : ℝ => 2 * t ^ (-(1 / 2 : ℝ))) (t + c)) =
      (∫ t in (0 : ℝ)..c, (fun t : ℝ => 2 * t ^ (-(1 / 2 : ℝ))) t) -
        ∫ t in R..(R + c), (fun t : ℝ => 2 * t ^ (-(1 / 2 : ℝ))) t :=
  MeanField.telescoping_integral (g := fun t : ℝ => 2 * t ^ (-(1 / 2 : ℝ))) hc hR
    ((intervalIntegral.intervalIntegrable_rpow' (by norm_num : (-1 : ℝ) < -(1 / 2))).const_mul 2)

end VerifierProbe

#print axioms VerifierProbe.hU_indicator
#print axioms VerifierProbe.uniform_minimises_instance
#print axioms VerifierProbe.Ubad_not_psd
#print axioms VerifierProbe.conclusion_fails_for_Ubad
#print axioms VerifierProbe.telescoping_instance
