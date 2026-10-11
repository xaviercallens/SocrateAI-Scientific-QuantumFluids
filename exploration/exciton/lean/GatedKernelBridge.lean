import GatedKernel
import OAI.Analysis.Triangular.Energy.Universal

/-!
# Bridge: the gated dual-plane dipole kernel meets the hypothesis of upstream's universal-optimality theorem

Written 2026-10-11 (SocrateAI-Scientific-QuantumFluids).  Lean 4.34.1 / Mathlib v4.34.1.

This file imports (i) `GatedKernel.lean` of this repository (the image series `Uimg` of
`V_ee + V_hh - 2 V_eh` between two grounded planes is `AdmissiblePotential`), and (ii) the upstream theorem

    OAI.AtomicTriangular.universal_energy_minimum :
      AdmissiblePotential g → LocallyFinite C → DensityOne C →
      latticeEnergy g ≤ energy g C ∧ latticeEnergy g = energy g A

from `openai/math` at commit `fd4aeeb2` (an AI-generated, unrefereed development; the theorem is stated and proved in
Lean there).  Their `AdmissiblePotential` and ours are definitionally the same predicate, so the instance is one line.

## What this does NOT claim

* Nothing about the *correctness of the upstream statement as a rendering of the Cohn-Kumar conjecture*: that is a human
  reading task (definitions `LocallyFinite`, `DensityOne`, `energy`, `latticeEnergy`, `AdmissiblePotential`).
* Energies are in `[0, ∞]` and count ordered pairs, as upstream (the physical energy per particle is half).
* Density is one in upstream's normalisation: lengths are measured in units of `ρ^{-1/2}`.  For another physical
  density `ρ` take `h1, h2` in those units (`U_{λh}(λ r) = U_h(r)/λ`); no extra rescaling lemma is needed.
* Ideal grounded metal planes, point charges, classical configurations; no boundaries, no quantum effects.
-/

open OAI GatedKernel

/-- **The triangular lattice minimises the gated-kernel energy among all locally finite density-one configurations**,
conditional only on upstream's `universal_energy_minimum` (and the axioms it uses). -/
theorem gated_kernel_triangular_minimal {h1 h2 : ℝ} (ze zh : ℝ) (hP : 0 < h1 + h2)
    (C : Set AtomicTriangular.Plane) (hC : AtomicTriangular.LocallyFinite C)
    (hd : AtomicTriangular.DensityOne C) :
    AtomicTriangular.latticeEnergy (fun t => Uimg t h1 h2 ze zh) ≤
        AtomicTriangular.energy (fun t => Uimg t h1 h2 ze zh) C ∧
      AtomicTriangular.latticeEnergy (fun t => Uimg t h1 h2 ze zh) =
        AtomicTriangular.energy (fun t => Uimg t h1 h2 ze zh) AtomicTriangular.A :=
  AtomicTriangular.universal_energy_minimum _ C (imageSeries_admissible ze zh hP) hC hd

#print axioms gated_kernel_triangular_minimal
#print axioms OAI.AtomicTriangular.universal_energy_minimum
