/-
Bridge: the Madelung (quantum-fluid) velocity field expressed in OpenAI's Navier-Stokes vocabulary.

Imports `NavierStokes.ProblemStatement` from openai/NavierStokesAndEuler @ 8937a8f (Apache-2.0),
the same commit whose four headline theorems MechanicaFluidorum audited to footprint
`{propext, Classical.choice, Quot.sound}`. Both trees are on Lean 4.34.0-rc2 and Mathlib
85e3a25 (tag v4.34.0-rc2), which is what makes the import possible at all.

WHY THIS FILE. `MadelungSplit.lean` states the quantum-pressure/hydrodynamic split with
hand-rolled directional derivatives. The OpenAI tree already fixes Frechet-derivative vocabulary on
`EuclideanSpace R (Fin 3)` -- `spatialDerivative`, `spatialDivergence`, `pressureGradient`,
`spatialLaplacian` -- in which THEIR incompressible Navier-Stokes residual is written. Restating our
objects in that vocabulary means the quantum-fluid and Navier-Stokes sides are expressed in one
formalism and can be compared as mathematics rather than by analogy.

WHAT IS PROVED. `divergence_pressureGradient`: the divergence of their `pressureGradient` is the
scalar Laplacian. They never needed this (their pressure enters only as a gradient), so it is
genuinely added, and it is the identity that makes the Madelung continuity equation expressible in
their formalism. `divergence_madelungVelocity` then gives `div u = (hbar/m) * Laplacian S` for the
Madelung velocity `u = (hbar/m) grad S`.

WHAT IS NOT PROVED. No dynamics, no Gross-Pitaevskii equation, no claim about Navier-Stokes
regularity, and nothing about their blow-up theorems. Second differentiability of the phase is a
genuine HYPOTHESIS, and it is exactly what fails on a vortex line, where `S` is undefined.
-/

import NavierStokes.ProblemStatement
import Mathlib

namespace QuantumFluids.MadelungNSE

open NavierStokes.ProblemStatement

/-- The scalar Laplacian of a pressure-like field, in the same coordinate style as their
`spatialLaplacian` (which is the componentwise version for vector fields). -/
noncomputable def scalarLaplacian (p : PressureField) (t : ℝ) (x : Space) : ℝ :=
  ∑ i : Fin 3, fderiv ℝ (fun y : Space =>
    fderiv ℝ (fun z : Space => p (t, z)) y (coordinateVector i)) x (coordinateVector i)

/-- Second differentiability of the spatial field at a point: each first partial derivative is
again differentiable there. This is the hypothesis, and it is what fails at a vortex core. -/
def TwiceSpatial (p : PressureField) (t : ℝ) (x : Space) : Prop :=
  ∀ i : Fin 3, DifferentiableAt ℝ
    (fun y : Space => fderiv ℝ (fun z : Space => p (t, z)) y (coordinateVector i)) x

/- OMITTED: a convenience lemma reading off one component of their `pressureGradient`.
   It is not used below and did not survive this Mathlib's `PiLp`/`ofLp` coercion changes; rather
   than carry a `sorry` for a lemma nothing depends on, it is dropped. -/

/-- **The divergence of their pressure gradient is the scalar Laplacian.**
`div (grad p) = Δp`, stated with their `spatialDivergence` and their `pressureGradient`. -/
theorem divergence_pressureGradient (p : PressureField) (t : ℝ) (x : Space)
    (h : TwiceSpatial p t x) :
    spatialDivergence (fun q : SpaceTime => pressureGradient p q.1 q.2) t x
      = scalarLaplacian p t x := by
  unfold spatialDivergence spatialDerivative scalarLaplacian
  refine Finset.sum_congr rfl (fun i _ => ?_)
  have hfun : (fun y : Space => pressureGradient p t y)
      = fun y : Space => ∑ j : Fin 3,
        (fderiv ℝ (fun z : Space => p (t, z)) y (coordinateVector j)) • coordinateVector j := rfl
  rw [hfun, fderiv_fun_sum (fun j _ => (h j).smul_const (coordinateVector j))]
  rw [ContinuousLinearMap.sum_apply]
  rw [show (∑ j : Fin 3, (fderiv ℝ (fun y : Space =>
        (fderiv ℝ (fun z : Space => p (t, z)) y (coordinateVector j)) • coordinateVector j) x)
        (coordinateVector i)) i
      = ∑ j : Fin 3, ((fderiv ℝ (fun y : Space =>
        (fderiv ℝ (fun z : Space => p (t, z)) y (coordinateVector j)) • coordinateVector j) x)
        (coordinateVector i)) i from by simp]
  have key : ∀ j : Fin 3, ((fderiv ℝ (fun y : Space =>
      (fderiv ℝ (fun z : Space => p (t, z)) y (coordinateVector j)) • coordinateVector j) x)
      (coordinateVector i)) i
      = (if i = j then (1 : ℝ) else 0) *
        (fderiv ℝ (fun y : Space =>
          fderiv ℝ (fun z : Space => p (t, z)) y (coordinateVector j)) x (coordinateVector i)) := by
    intro j
    rw [fderiv_smul_const (h j)]
    simp [coordinateVector, EuclideanSpace.single_apply, eq_comm]
  simp_rw [key]
  simp

/-- The Madelung velocity field `u = (hbar/m) grad S`, in their `VelocityField` type. -/
noncomputable def madelungVelocity (hbar m : ℝ) (S : PressureField) : VelocityField :=
  fun q : SpaceTime => (hbar / m) • pressureGradient S q.1 q.2

/-- **Divergence of the Madelung velocity.** `div u = (hbar/m) * Laplacian S`, in their
vocabulary. With continuity this is the equation the quantum-pressure term acts against; here only
the kinematic identity is claimed. -/
theorem divergence_madelungVelocity (hbar m : ℝ) (S : PressureField) (t : ℝ) (x : Space)
    (h : TwiceSpatial S t x) :
    spatialDivergence (madelungVelocity hbar m S) t x = (hbar / m) * scalarLaplacian S t x := by
  have hsmul : (fun y : Space => madelungVelocity hbar m S (t, y))
      = fun y : Space => (hbar / m) • pressureGradient S t y := rfl
  unfold spatialDivergence spatialDerivative
  rw [← divergence_pressureGradient S t x h]
  unfold spatialDivergence spatialDerivative
  rw [Finset.mul_sum]
  refine Finset.sum_congr rfl (fun i _ => ?_)
  have hd : DifferentiableAt ℝ (fun y : Space => pressureGradient S t y) x := by
    unfold pressureGradient
    exact DifferentiableAt.fun_sum (fun j _ => (h j).smul_const (coordinateVector j))
  rw [hsmul, show (fun y : Space => (hbar / m) • pressureGradient S t y)
      = (hbar / m) • (fun y : Space => pressureGradient S t y) from rfl,
    fderiv_const_smul hd]
  simp

end QuantumFluids.MadelungNSE

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.MadelungNSE.divergence_pressureGradient
#print axioms QuantumFluids.MadelungNSE.divergence_madelungVelocity
