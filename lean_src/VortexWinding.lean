/-
Correctness of phase-winding vortex detection.

Every Gross-Pitaevskii / BEC simulation code that locates quantized vortices does so by summing
principal-branch phase differences around a small closed loop and rounding to a multiple of `2π`.
This module proves the two facts that algorithm rests on, and — more usefully — states the EXACT
condition under which it fails.

This is infrastructure, not a result. It is the correctness proof for the extractor in
`src/quantumfluids/tda/vortex_persistence.py`, whose docstring currently asserts these facts in
prose ("exact for a field resolved well enough that no true phase step exceeds pi"), and it applies
unchanged to any other code using the same standard method.

WHAT IS PROVED
  * `pdiff_sub_mem`        : the principal difference equals the true difference up to `2π ℤ`;
  * `loop_sum_eq_zsmul`    : around a CLOSED loop the sum of principal differences is exactly an
                             integer multiple of `2π` -- so "the winding number is an integer" is a
                             theorem, not a numerical accident;
  * `pdiff_antisymm`       : traversing an edge in the opposite direction negates the contribution,
                             PROVIDED the phase difference is not exactly `π`;
  * `pdiff_add_pdiff_pi`   : and when it IS exactly `π`, the two contributions sum to `2π`, not `0`.
                             This is the precise failure mode of the standard algorithm: at that
                             single phase difference, edge cancellation between neighbouring
                             plaquettes breaks and a spurious winding can appear.

WHAT IS NOT PROVED: that a given field is resolved well enough for the detected winding to equal the
true topological charge of the continuum field. That is a statement about sampling, not about the
algorithm, and it is exactly what the resolution controls in the design memo test empirically.
-/

import Mathlib

namespace QuantumFluids.VortexWinding

open Real

/-- `2π > 0`, used throughout as the modulus. -/
theorem two_pi_pos : (0 : ℝ) < 2 * π := by positivity

/-- The principal-branch phase difference, the unique representative of `b - a` in `(-π, π]`. -/
noncomputable def pdiff (a b : ℝ) : ℝ := toIocMod two_pi_pos (-π) (b - a)

/-- `pdiff a b` lies in `(-π, π]`. -/
theorem pdiff_mem (a b : ℝ) : pdiff a b ∈ Set.Ioc (-π) π := by
  have h := toIocMod_mem_Ioc two_pi_pos (-π) (b - a)
  have e : -π + 2 * π = π := by ring
  rwa [e] at h

/-- **The principal difference is the true difference, modulo `2π`.** -/
theorem pdiff_eq (a b : ℝ) :
    pdiff a b = (b - a) - (toIocDiv two_pi_pos (-π) (b - a)) • (2 * π) := by
  rw [pdiff, toIocMod]

/-- **Loop quantization.** For any phases `θ` with `θ n = θ 0`, the sum of principal differences
around the loop is exactly an integer multiple of `2π`. This is why a numerically computed winding
number is an integer, and it is the fact every phase-winding vortex detector relies on. -/
theorem loop_sum_eq_mul (θ : ℕ → ℝ) (n : ℕ) (hclosed : θ n = θ 0) :
    ∃ m : ℤ, ∑ i ∈ Finset.range n, pdiff (θ i) (θ (i + 1)) = (m : ℝ) * (2 * π) := by
  refine ⟨- ∑ i ∈ Finset.range n, toIocDiv two_pi_pos (-π) (θ (i + 1) - θ i), ?_⟩
  have h : ∀ i, pdiff (θ i) (θ (i + 1))
      = (θ (i + 1) - θ i)
        - ((toIocDiv two_pi_pos (-π) (θ (i + 1) - θ i) : ℤ) : ℝ) * (2 * π) := by
    intro i; rw [pdiff_eq, zsmul_eq_mul]
  simp_rw [h]
  rw [Finset.sum_sub_distrib, Finset.sum_range_sub (fun i => θ i), hclosed, ← Finset.sum_mul]
  push_cast
  ring

/-- The sum of `pdiff` over an edge and its reverse is a multiple of `2π` lying in `(-2π, 2π]`. -/
theorem pdiff_add_rev_eq (a b : ℝ) :
    ∃ m : ℤ, pdiff a b + pdiff b a = (m : ℝ) * (2 * π) := by
  refine ⟨-(toIocDiv two_pi_pos (-π) (b - a) + toIocDiv two_pi_pos (-π) (a - b)), ?_⟩
  rw [pdiff_eq a b, pdiff_eq b a, zsmul_eq_mul, zsmul_eq_mul]
  push_cast
  ring

/-- **Edge cancellation, and its exact failure mode.** Traversing an edge in both directions either
cancels exactly, or contributes `2π`. The second case occurs precisely when both directions return
`π`, i.e. when the phase difference is exactly `π` — the one configuration in which the
contributions of two neighbouring plaquettes fail to cancel and a spurious winding can appear.
Stated as a disjunction because that is the whole truth; a bare antisymmetry claim would be false. -/
theorem pdiff_add_rev (a b : ℝ) :
    pdiff a b + pdiff b a = 0 ∨ pdiff a b + pdiff b a = 2 * π := by
  obtain ⟨m, hm⟩ := pdiff_add_rev_eq a b
  obtain ⟨l1, u1⟩ := pdiff_mem a b
  obtain ⟨l2, u2⟩ := pdiff_mem b a
  have hpi : (0 : ℝ) < π := pi_pos
  -- the sum lies in (-2π, 2π], and it is a multiple of 2π, so m is 0 or 1
  have hlo : -(2 * π) < (m : ℝ) * (2 * π) := by rw [← hm]; linarith
  have hhi : (m : ℝ) * (2 * π) ≤ 2 * π := by rw [← hm]; linarith
  have hm1 : (-1 : ℝ) < (m : ℝ) := by nlinarith
  have hm2 : (m : ℝ) ≤ 1 := by nlinarith
  have hcases : m = 0 ∨ m = 1 := by
    have a1 : (-1 : ℤ) < m := by exact_mod_cast hm1
    have a2 : m ≤ 1 := by exact_mod_cast hm2
    omega
  rcases hcases with h | h
  · left; rw [hm, h]; norm_num
  · right; rw [hm, h]; norm_num

/-- The non-cancelling case is exactly "both directions return `π`". -/
theorem pdiff_add_rev_eq_two_pi_iff (a b : ℝ) :
    pdiff a b + pdiff b a = 2 * π ↔ (pdiff a b = π ∧ pdiff b a = π) := by
  obtain ⟨l1, u1⟩ := pdiff_mem a b
  obtain ⟨l2, u2⟩ := pdiff_mem b a
  constructor
  · intro h
    exact ⟨by linarith, by linarith⟩
  · intro hab
    rw [hab.1, hab.2]; ring

/-! ## Vortex lines do not end: the oriented sum over a closed surface

`trace_lines` in `src/quantumfluids/tda/vortex_persistence.py` walks a vortex line from cube to cube,
which presupposes that a line entering a cube also leaves it — i.e. that the oriented windings of the
six faces sum to zero. That is the discrete form of `∇·ω = 0`. The proof is *not* homological: each
edge of the cube is traversed once in each direction by the two faces sharing it, so the raw phase
differences cancel in pairs.

The cancellation is exact only when no edge sits at the `π` branch cut (`pdiff_add_rev`), which is the
same hypothesis as everywhere else in this file. Below, a closed surface is modelled by its boundary
edges: a family of oriented edges in which every edge appears with both orientations. That covers the
cube and any other closed polyhedral surface, and keeps the combinatorics honest rather than hiding
it in an unproved indexing convention. -/

/-- An oriented edge list is *balanced* when a bijection `σ` pairs each entry with its reverse:
`σ` is an involution without fixed points sending edge `i = (a,b)` to an edge `(b,a)`. This is what
"the faces of a closed surface traverse every edge once in each direction" means combinatorially. -/
structure Balanced {n : ℕ} (u v : Fin n → ℝ) where
  /-- the pairing of each oriented edge with its reverse -/
  σ : Fin n → Fin n
  invol : ∀ i, σ (σ i) = i
  no_fix : ∀ i, σ i ≠ i
  rev_start : ∀ i, u (σ i) = v i
  rev_end : ∀ i, v (σ i) = u i

/-- **The oriented sum over a closed surface vanishes**, provided no edge sits at the branch cut.
Hence a vortex line entering a grid cube must leave it: lines do not end in the interior. -/
theorem balanced_sum_eq_zero {n : ℕ} {u v : Fin n → ℝ} (B : Balanced u v)
    (hcut : ∀ i, pdiff (u i) (v i) + pdiff (v i) (u i) = 0) :
    ∑ i : Fin n, pdiff (u i) (v i) = 0 := by
  have hpair : ∀ i, pdiff (u (B.σ i)) (v (B.σ i)) = - pdiff (u i) (v i) := by
    intro i
    rw [B.rev_start i, B.rev_end i]
    linarith [hcut i]
  have hswap : ∑ i : Fin n, pdiff (u i) (v i)
      = ∑ i : Fin n, pdiff (u (B.σ i)) (v (B.σ i)) := by
    refine (Fintype.sum_bijective B.σ ?_ _ _ (fun i => rfl)).symm
    exact Function.bijective_iff_has_inverse.mpr ⟨B.σ, B.invol, B.invol⟩
  have : ∑ i : Fin n, pdiff (u i) (v i) = - ∑ i : Fin n, pdiff (u i) (v i) := by
    conv_lhs => rw [hswap]
    simp_rw [hpair]
    rw [Finset.sum_neg_distrib]
  linarith

/-- The branch-cut hypothesis is exactly "no edge sits at a phase difference of `π`", by
`pdiff_add_rev_eq_two_pi_iff` of `QuantizedCirculation`; here it is stated directly so this file
stays self-contained. `pdiff_add_rev` shows the alternative is a defect of exactly `2π`. -/
theorem cut_free_of_ne_pi {a b : ℝ} (h : pdiff a b ≠ π) : pdiff a b + pdiff b a = 0 := by
  rcases pdiff_add_rev a b with h0 | h2
  · exact h0
  · exfalso
    obtain ⟨l1, u1⟩ := pdiff_mem a b
    obtain ⟨l2, u2⟩ := pdiff_mem b a
    exact h (by linarith)

end QuantumFluids.VortexWinding

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.VortexWinding.two_pi_pos
#print axioms QuantumFluids.VortexWinding.pdiff_mem
#print axioms QuantumFluids.VortexWinding.pdiff_eq
#print axioms QuantumFluids.VortexWinding.loop_sum_eq_mul
#print axioms QuantumFluids.VortexWinding.pdiff_add_rev_eq
#print axioms QuantumFluids.VortexWinding.pdiff_add_rev
#print axioms QuantumFluids.VortexWinding.pdiff_add_rev_eq_two_pi_iff
#print axioms QuantumFluids.VortexWinding.balanced_sum_eq_zero
#print axioms QuantumFluids.VortexWinding.cut_free_of_ne_pi
