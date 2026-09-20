/-
D4 (docs/OPENAI_NSE_LEVERAGE_FOR_QUANTUM_FLUIDS.md): the Madelung energy split.

WHAT IS PROVED. For a wavefunction written in amplitude-phase form
`psi = a * exp (i S)` with `a`, `S : E -> R` differentiable at `x`, and for every
direction `v`, the directional derivative of `psi` is
`exp (i S) * (da v + i a dS v)` and its squared modulus is
`(da v)^2 + a^2 (dS v)^2`. Summed over an orthonormal frame this is the pointwise
identity `|grad psi|^2 = |grad a|^2 + a^2 |grad S|^2`, i.e. the Gross-Pitaevskii
kinetic energy density splits into a quantum-pressure part (`a = sqrt rho`) and a
hydrodynamic part `rho |u|^2` with `u = (hbar/m) grad S`.

WHAT IS NOT PROVED. Nothing about dynamics, about the Madelung equations, about
vortex lines (where `S` is undefined and `a = 0`), or about bounded energy
implying anything on `sup |u|`. This is the algebraic identity only (Tier A, small).
The hypothesis `DifferentiableAt` on `a` and `S` is a genuine assumption and is
exactly what fails at a vortex core.
-/

import Mathlib

namespace QuantumFluids.Madelung

open Complex

/-- Amplitude-phase form `psi = a * exp (i S)`. -/
noncomputable def psi {E : Type*} (a S : E → ℝ) (x : E) : ℂ :=
  (a x : ℂ) * Complex.exp (Complex.I * (S x : ℂ))

/-- Pure algebra: the squared modulus of `exp (i theta) * (p + i a r)` is `p^2 + a^2 r^2`. -/
theorem normSq_phase_mul (θ p a r : ℝ) :
    ‖Complex.exp (Complex.I * (θ : ℂ)) * ((p : ℂ) + Complex.I * (a : ℂ) * (r : ℂ))‖ ^ 2
      = p ^ 2 + a ^ 2 * r ^ 2 := by
  have h1 : ‖Complex.exp (Complex.I * (θ : ℂ))‖ = 1 := by
    rw [mul_comm]; exact Complex.norm_exp_ofReal_mul_I θ
  have h2 : (p : ℂ) + Complex.I * (a : ℂ) * (r : ℂ) = ⟨p, a * r⟩ := by
    apply Complex.ext <;> simp
  rw [norm_mul, h1, one_mul, h2, Complex.sq_norm, Complex.normSq_mk]
  ring

section Calculus

variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- The line `t ↦ x + t v` has derivative `v` at `t = 0`. -/
private theorem hasDerivAt_line (x v : E) :
    HasDerivAt (fun t : ℝ => x + t • v) v 0 := by
  simpa using ((hasDerivAt_id (0 : ℝ)).smul_const v).const_add x

/-- **Directional derivative of an amplitude-phase wavefunction.** -/
theorem hasDerivAt_psi_line (a S : E → ℝ) (x v : E)
    (ha : DifferentiableAt ℝ a x) (hS : DifferentiableAt ℝ S x) :
    HasDerivAt (fun t : ℝ => psi a S (x + t • v))
      (Complex.exp (Complex.I * (S x : ℂ)) *
        ((fderiv ℝ a x v : ℝ) + Complex.I * (a x : ℂ) * (fderiv ℝ S x v : ℝ))) 0 := by
  have hl := hasDerivAt_line x v
  have hx : x + (0 : ℝ) • v = x := by simp
  have ha' : HasDerivAt (fun t : ℝ => a (x + t • v)) (fderiv ℝ a x v) 0 :=
    ha.hasFDerivAt.comp_hasDerivAt_of_eq (0 : ℝ) hl (by simp)
  have hS' : HasDerivAt (fun t : ℝ => S (x + t • v)) (fderiv ℝ S x v) 0 :=
    hS.hasFDerivAt.comp_hasDerivAt_of_eq (0 : ℝ) hl (by simp)
  have hexp : HasDerivAt (fun t : ℝ => Complex.exp (Complex.I * ((S (x + t • v) : ℝ) : ℂ)))
      (Complex.exp (Complex.I * (S x : ℂ)) * (Complex.I * (fderiv ℝ S x v : ℝ))) 0 := by
    have h0 : HasDerivAt (fun t : ℝ => Complex.I * ((S (x + t • v) : ℝ) : ℂ))
        (Complex.I * (fderiv ℝ S x v : ℝ)) 0 :=
      (hS'.ofReal_comp).const_mul Complex.I
    have := h0.cexp
    simpa using this
  have h2 := (ha'.ofReal_comp).mul hexp
  have e : (fun t : ℝ => psi a S (x + t • v)) =
      (fun y : ℝ => ((a (x + y • v) : ℝ) : ℂ)) *
        (fun t : ℝ => Complex.exp (Complex.I * ((S (x + t • v) : ℝ) : ℂ))) := by
    funext t; rfl
  rw [e]
  refine h2.congr_deriv ?_
  simp only [zero_smul, add_zero]
  ring

/-- **Madelung split, directional form.** For every direction `v`, the squared modulus of
the directional derivative of `psi = a exp(iS)` is `(da v)^2 + a^2 (dS v)^2`. -/
theorem norm_sq_deriv_psi (a S : E → ℝ) (x v : E)
    (ha : DifferentiableAt ℝ a x) (hS : DifferentiableAt ℝ S x) :
    ‖deriv (fun t : ℝ => psi a S (x + t • v)) 0‖ ^ 2
      = (fderiv ℝ a x v) ^ 2 + (a x) ^ 2 * (fderiv ℝ S x v) ^ 2 := by
  rw [(hasDerivAt_psi_line a S x v ha hS).deriv]
  exact normSq_phase_mul (S x) _ _ _

end Calculus

/-- **Madelung split, gradient form, on `R^n`.** Summing the directional identity over the
coordinate frame: `sum_i |d_i psi|^2 = sum_i (d_i a)^2 + a^2 sum_i (d_i S)^2`, that is
`|grad psi|^2 = |grad a|^2 + a^2 |grad S|^2`. -/
theorem madelung_gradient_split {n : ℕ} (a S : EuclideanSpace ℝ (Fin n) → ℝ)
    (x : EuclideanSpace ℝ (Fin n))
    (ha : DifferentiableAt ℝ a x) (hS : DifferentiableAt ℝ S x) :
    ∑ i : Fin n, ‖deriv (fun t : ℝ => psi a S (x + t • EuclideanSpace.single i 1)) 0‖ ^ 2
      = ∑ i : Fin n, (fderiv ℝ a x (EuclideanSpace.single i 1)) ^ 2
        + (a x) ^ 2 * ∑ i : Fin n, (fderiv ℝ S x (EuclideanSpace.single i 1)) ^ 2 := by
  simp only [norm_sq_deriv_psi a S x _ ha hS, Finset.sum_add_distrib, Finset.mul_sum]

/-- **Kinetic-energy density split with physical constants.** With `rho = a^2` and superfluid
velocity components `u_i = (hbar/m) d_i S`, the kinetic energy density
`(hbar^2/2m) |grad psi|^2` equals the quantum-pressure term `(hbar^2/2m) |grad a|^2`
plus the hydrodynamic term `(m/2) rho |u|^2`. -/
theorem kinetic_density_split (ħ m a ga gS : ℝ) (hm : m ≠ 0) :
    ħ ^ 2 / (2 * m) * (ga ^ 2 + a ^ 2 * gS ^ 2)
      = ħ ^ 2 / (2 * m) * ga ^ 2 + m / 2 * a ^ 2 * (ħ / m * gS) ^ 2 := by
  field_simp

end QuantumFluids.Madelung

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.Madelung.normSq_phase_mul
#print axioms QuantumFluids.Madelung.hasDerivAt_line
#print axioms QuantumFluids.Madelung.hasDerivAt_psi_line
#print axioms QuantumFluids.Madelung.norm_sq_deriv_psi
#print axioms QuantumFluids.Madelung.madelung_gradient_split
#print axioms QuantumFluids.Madelung.kinetic_density_split
