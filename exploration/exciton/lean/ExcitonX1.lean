import Mathlib

/-!
# X1: differencing preserves complete monotonicity (exciton-fluid study, 2026-10-10)

Status: kernel-checked under Lean 4.34.0-rc2 / Mathlib 85e3a25 (the QuantumFluids pin); `#print axioms` of every theorem
is a subset of {propext, Classical.choice, Quot.sound}; no unproved goals.  Producer: the session that wrote
`docs/designs/EXCITON_FLUID_LEAN_SOLVER_PLAN.md`.  **Verifier: pending** (a separate instance, ideally in the
upstream environment Lean 4.34.1 / Mathlib d13f23b7, where `AdmissiblePotential` is
`OAI.TriangularUniversal.AdmissiblePotential`; replace the local copy below by `open OAI.TriangularUniversal`).
This file is exploration material, not part of the audited library `lean_src/`.

* `admissible_sub_shift`: if `g` is admissible (smooth, non-negative, completely monotone on `(0, ∞)`) and `c > 0`, then
  `t ↦ g t - g (t + c)` is admissible.  With `g = t^(-1/2)` and `c = d²` this is the direct interaction of two
  interlayer excitons separated by `d` in a bilayer (`bilayerDipole_admissible`, given the Riesz case `s = 1`, which is
  `TriangularRiesz.riesz_admissible` of the LeanMaster contribution).
* `gem4_not_admissible`: negative control, `exp (-t²)` (cluster-crystal kernel) is not admissible.
* Mathlib naming churn: `ENat.natCast_lt_top` was `ENat.coe_lt_top` in other Mathlib versions.
-/

open Filter Topology

namespace ExcitonX1

/-- Verbatim copy of upstream's `OAI.TriangularUniversal.AdmissiblePotential` (statement only). -/
def AdmissiblePotential (g : ℝ → ℝ) : Prop :=
  ContDiffOn ℝ (⊤ : ℕ∞) g (Set.Ioi 0) ∧
  (∀ t : ℝ, 0 < t → 0 ≤ g t) ∧
  ∀ (r : ℕ) (t : ℝ), 0 < t → 0 ≤ (-1 : ℝ) ^ r * iteratedDeriv r g t

/-- For admissible `g`, each `h_r = (-1)^r g^(r)` is non-increasing on `(0, ∞)`: its derivative is `-h_{r+1} ≤ 0`. -/
theorem antitone_signed_iteratedDeriv {g : ℝ → ℝ} (hg : AdmissiblePotential g) (r : ℕ) :
    AntitoneOn (fun t => (-1 : ℝ) ^ r * iteratedDeriv r g t) (Set.Ioi 0) := by
  obtain ⟨h1, -, h3⟩ := hg
  have hopen : IsOpen (Set.Ioi (0 : ℝ)) := isOpen_Ioi
  have hU : UniqueDiffOn ℝ (Set.Ioi (0 : ℝ)) := hopen.uniqueDiffOn
  have hle : (r : WithTop ℕ∞) ≤ ((⊤ : ℕ∞) : WithTop ℕ∞) := by exact_mod_cast le_top
  have hlt : (r : WithTop ℕ∞) < ((⊤ : ℕ∞) : WithTop ℕ∞) := by
    have h : ((r : ℕ∞) : WithTop ℕ∞) < ((⊤ : ℕ∞) : WithTop ℕ∞) := WithTop.coe_lt_coe.2 (ENat.natCast_lt_top r)
    simpa using h
  have hcont : ContinuousOn (iteratedDeriv r g) (Set.Ioi 0) := by
    have := h1.continuousOn_iteratedDerivWithin hle hU
    exact this.congr (fun x hx => (iteratedDerivWithin_of_isOpen hopen hx).symm)
  have hdiff : DifferentiableOn ℝ (iteratedDeriv r g) (Set.Ioi 0) := by
    have := h1.differentiableOn_iteratedDerivWithin hlt hU
    exact this.congr (fun x hx => (iteratedDerivWithin_of_isOpen hopen hx).symm)
  refine antitoneOn_of_deriv_nonpos (convex_Ioi 0) (continuousOn_const.mul hcont) ?_ ?_
  · rw [interior_Ioi]
    exact (differentiableOn_const _).mul hdiff
  · intro x hx
    rw [interior_Ioi] at hx
    have hd : DifferentiableAt ℝ (iteratedDeriv r g) x := hdiff.differentiableAt (hopen.mem_nhds hx)
    rw [deriv_const_mul _ hd, ← iteratedDeriv_succ]
    have h := h3 (r + 1) x hx
    have e : (-1 : ℝ) ^ (r + 1) * iteratedDeriv (r + 1) g x = -((-1 : ℝ) ^ r * iteratedDeriv (r + 1) g x) := by
      ring
    rw [e] at h
    linarith

/-- **X1.** Differencing preserves complete monotonicity. -/
theorem admissible_sub_shift {g : ℝ → ℝ} (hg : AdmissiblePotential g) {c : ℝ} (hc : 0 < c) :
    AdmissiblePotential (fun t => g t - g (t + c)) := by
  have hanti := antitone_signed_iteratedDeriv hg
  obtain ⟨h1, h2, h3⟩ := hg
  have hshift : ContDiffOn ℝ (⊤ : ℕ∞) (fun t => g (t + c)) (Set.Ioi 0) := by
    refine h1.comp (contDiffOn_id.add contDiffOn_const) ?_
    intro t ht
    simp only [Set.mem_Ioi] at ht ⊢
    linarith
  refine ⟨h1.sub hshift, ?_, ?_⟩
  · intro t ht
    have h0 := hanti 0
    simp only [pow_zero, one_mul, iteratedDeriv_zero] at h0
    exact sub_nonneg.2 (h0 (Set.mem_Ioi.2 ht) (Set.mem_Ioi.2 (by linarith)) (by linarith))
  · intro r t ht
    have hle : (r : WithTop ℕ∞) ≤ ((⊤ : ℕ∞) : WithTop ℕ∞) := by exact_mod_cast le_top
    have hg_at : ContDiffAt ℝ r g t := (h1.contDiffAt (Ioi_mem_nhds ht)).of_le hle
    have hs_at : ContDiffAt ℝ r (fun z => g (z + c)) t := (hshift.contDiffAt (Ioi_mem_nhds ht)).of_le hle
    have hsub : iteratedDeriv r (fun t => g t - g (t + c)) t =
        iteratedDeriv r g t - iteratedDeriv r g (t + c) := by
      have h := iteratedDeriv_sub hg_at hs_at
      rw [iteratedDeriv_comp_add_const] at h
      exact h
    rw [hsub, mul_sub]
    have h := hanti r (Set.mem_Ioi.2 ht) (Set.mem_Ioi.2 (by linarith)) (by linarith : t ≤ t + c)
    simp only at h
    linarith

/-- Non-negative multiples of admissible potentials are admissible. -/
theorem admissible_const_mul {g : ℝ → ℝ} (hg : AdmissiblePotential g) {a : ℝ} (ha : 0 ≤ a) :
    AdmissiblePotential (fun t => a * g t) := by
  obtain ⟨h1, h2, h3⟩ := hg
  refine ⟨contDiffOn_const.mul h1, fun t ht => mul_nonneg ha (h2 t ht), ?_⟩
  intro r t ht
  have hle : (r : WithTop ℕ∞) ≤ ((⊤ : ℕ∞) : WithTop ℕ∞) := by exact_mod_cast le_top
  have hg_at : ContDiffAt ℝ r g t := (h1.contDiffAt (Ioi_mem_nhds ht)).of_le hle
  have h := iteratedDeriv_const_mul (n := r) a hg_at
  have e : iteratedDeriv r (fun t => a * g t) t = a * iteratedDeriv r g t := h
  rw [e]
  have := mul_nonneg ha (h3 r t ht)
  calc (0 : ℝ) ≤ a * ((-1 : ℝ) ^ r * iteratedDeriv r g t) := this
    _ = (-1 : ℝ) ^ r * (a * iteratedDeriv r g t) := by ring

noncomputable def riesz (s : ℝ) : ℝ → ℝ := fun t => t ^ (-(s / 2))

/-- Direct interaction of two interlayer excitons (units `e²/4πε₀ε = 1`, `t = r²`). Needs the Riesz case `s = 1` (D1). -/
noncomputable def bilayerDipole (d : ℝ) : ℝ → ℝ := fun t => 2 * (riesz 1 t - riesz 1 (t + d ^ 2))

theorem bilayerDipole_admissible {d : ℝ} (hd : d ≠ 0) (hR : AdmissiblePotential (riesz 1)) :
    AdmissiblePotential (bilayerDipole d) := by
  have hc : 0 < d ^ 2 := by positivity
  exact admissible_const_mul (admissible_sub_shift hR hc) (a := 2) (by norm_num)


/-! ## Negative control: the generalised-exponential kernel `exp (-t²)` (cluster crystals) is NOT admissible -/

theorem gem4_not_admissible : ¬ AdmissiblePotential (fun t : ℝ => Real.exp (-(t ^ 2))) := by
  intro h
  have h2 := h.2.2 2 (1 / 2) (by norm_num)
  have h1 : ∀ t : ℝ, HasDerivAt (fun t : ℝ => Real.exp (-(t ^ 2))) (-(2 * t) * Real.exp (-(t ^ 2))) t := by
    intro t
    have hp : HasDerivAt (fun x : ℝ => -(x ^ 2)) (-(2 * t)) t :=
      ((hasDerivAt_pow 2 t).neg).congr_deriv (by norm_num)
    exact hp.exp.congr_deriv (by ring)
  have hd1 : deriv (fun t : ℝ => Real.exp (-(t ^ 2))) = fun t => -(2 * t) * Real.exp (-(t ^ 2)) := by
    funext t
    exact (h1 t).deriv
  have h3 : HasDerivAt (fun t : ℝ => -(2 * t) * Real.exp (-(t ^ 2)))
      (-2 * Real.exp (-(1 / 2 : ℝ) ^ 2) + (-(2 * (1 / 2 : ℝ))) * (-(2 * (1 / 2 : ℝ)) * Real.exp (-((1 / 2 : ℝ) ^ 2))))
      (1 / 2) := by
    have hl : HasDerivAt (fun t : ℝ => -(2 * t)) (-2) (1 / 2) :=
      (((hasDerivAt_id' (1 / 2 : ℝ)).const_mul (2 : ℝ)).neg).congr_deriv (by norm_num)
    exact hl.mul (h1 (1 / 2))
  have hval : iteratedDeriv 2 (fun t : ℝ => Real.exp (-(t ^ 2))) (1 / 2) = -Real.exp (-(1 / 4 : ℝ)) := by
    rw [iteratedDeriv_succ, iteratedDeriv_one, hd1, h3.deriv]
    have e1 : ((1 / 2 : ℝ) ^ 2) = 1 / 4 := by norm_num
    simp only [e1]
    ring
  rw [hval] at h2
  have hpos := Real.exp_pos (-(1 / 4 : ℝ))
  norm_num at h2
  linarith

end ExcitonX1

#print axioms ExcitonX1.antitone_signed_iteratedDeriv
#print axioms ExcitonX1.admissible_sub_shift
#print axioms ExcitonX1.admissible_const_mul
#print axioms ExcitonX1.bilayerDipole_admissible
#print axioms ExcitonX1.gem4_not_admissible
