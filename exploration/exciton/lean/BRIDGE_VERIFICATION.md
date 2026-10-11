# Bridge verification: gated kernel x upstream universal-energy-minimum theorem (2026-10-11)

What was done (one session, not a human review):

* Source: `openai/math` at `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` (HEAD at clone time; `Universal.lean` sha256 prefix 35765ec2deda6020).
* The 227 Lean files of the import closure of `OAI.Analysis.Triangular.Energy.Universal` (about 66 000 lines) were compiled one by
  one with `lean -R` against the pinned Mathlib v4.34.1 of the `qfenv` environment (Lean 4.34.1), in dependency order, with a
  4-way parallel scheduler (not `lake`; the upstream `lakefile.lean` requires many unrelated packages). All 227 succeeded; every
  compile log is empty (no warning, no error, no `sorry` message).
* `GatedKernel.lean` was compiled as a module; `GatedKernelBridge.lean` imports it and the upstream theorem.
* `#print axioms` (printed by the bridge file): both `gated_kernel_triangular_minimal` and
  `OAI.AtomicTriangular.universal_energy_minimum` depend on exactly `[propext, Classical.choice, Quot.sound]`.

## The bridge theorem
`gated_kernel_triangular_minimal`: for all `h1 h2` with `0 < h1 + h2`, all real `ze zh`, every locally finite density-one
configuration `C` of the plane, the covolume-one triangular lattice satisfies `latticeEnergy g ≤ energy g C` and
`latticeEnergy g = energy g A` for `g t = Uimg t h1 h2 ze zh` (the image-series kernel of two grounded planes).

## What this is not
* Not a check of statement fidelity: whether `LocallyFinite`, `DensityOne`, `energy`, `latticeEnergy`, `AdmissiblePotential` render
  the Cohn-Kumar conjecture is a human reading task (an AI audit exists in `triangular-universal-optimality-lean`).
* Not a reproduction of upstream's own build system or of the Comparator run; not a human review of the AI-generated proof.
* Energies count ordered pairs; density is one in upstream's normalisation (rescale lengths for other densities).
* Ideal grounded planes, classical configurations; nothing on boundaries or quantum effects.
