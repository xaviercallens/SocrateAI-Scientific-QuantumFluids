/-
  ScaleResolvedWinding.lean -- the winding number seen at scale R is the net topological charge
  inside R: a discrete Stokes theorem for phase windings, and its two corollaries, "a dipole is
  invisible from outside" and "a single core is seen as ±1 from any scale that encloses it".

  Thought experiment B of the round ("the small-pair trap"): a vortex and an antivortex a distance
  `a` apart. A loop around one of them sees winding ±1; any loop of size `R ≫ a` enclosing both sees
  0. So the causal variable is not "the number of vortices" but the winding resolved in scale, W(R),
  which is what a persistent-homology reading of the phase field tracks, and the BKT transition is the
  point where W(R) stops vanishing at large R.

  Model. A region is a finite family of plaquettes `p : Fin m`, each carrying four corner phases
  `θ p i`, `i : Fin 4`; the edge `(p, i)` runs from `θ p i` to `θ p (i+1)` (indices mod 4). Interior
  edges come in reversed pairs (the involution `σ`), boundary edges are the rest. Nothing is assumed
  about the geometry: this is the combinatorial content of "the faces of a region traverse every
  interior edge once in each direction", the same structure as `VortexWinding.Balanced`.

  * `winding_int`        : each plaquette's loop sum is `2π` times an integer (its charge);
  * `stokes`             : **oriented boundary sum = sum of plaquette loop sums**, provided no interior
                           edge sits at the branch point `π`;
  * `boundary_eq_charge` : the boundary sum is `2π` times the net charge inside;
  * `dipole_invisible`   : a region whose charges sum to zero (one +1, one -1, rest 0) has boundary
                           winding 0 -- whatever its size;
  * `single_core_visible`: a region containing exactly one charged plaquette (charge q) has boundary
                           winding q -- whatever its size.

  The scale R enters only through *which* plaquettes are inside: W(R) = Σ_{p inside R} q_p.

  Negative controls (scratch, not here): `stokes` without the no-cut hypothesis fails; a region whose
  interior pairing fixes an edge fails.

  NOT PROVED: that the boundary edges of a region form a single closed loop (so the boundary sum is
  what `loop_sum_eq_mul` computes for that loop) -- this is a statement about planar regions, and the
  theorem holds without it; the continuum limit.
-/
import VortexWinding

namespace QuantumFluids.ScaleResolvedWinding

open Real QuantumFluids.VortexWinding Finset

/-- A region of `m` plaquettes with an interior-edge pairing. -/
structure Region (m : ℕ) where
  /-- corner phases of plaquette `p` -/
  θ : Fin m → Fin 4 → ℝ
  /-- the interior edges -/
  interior : Finset (Fin m × Fin 4)
  /-- the reversal pairing on interior edges -/
  σ : Fin m × Fin 4 → Fin m × Fin 4
  σ_mem : ∀ e ∈ interior, σ e ∈ interior
  invol : ∀ e ∈ interior, σ (σ e) = e
  no_fix : ∀ e ∈ interior, σ e ≠ e
  rev_start : ∀ e ∈ interior, θ (σ e).1 (σ e).2 = θ e.1 (e.2 + 1)
  rev_end : ∀ e ∈ interior, θ (σ e).1 ((σ e).2 + 1) = θ e.1 e.2

variable {m : ℕ} (Rg : Region m)

/-- The principal phase step along edge `e`. -/
noncomputable def Region.step (e : Fin m × Fin 4) : ℝ := pdiff (Rg.θ e.1 e.2) (Rg.θ e.1 (e.2 + 1))

/-- The loop sum of plaquette `p`. -/
noncomputable def Region.winding (p : Fin m) : ℝ := ∑ i : Fin 4, Rg.step (p, i)

/-- The oriented sum over the boundary edges. -/
noncomputable def Region.boundarySum : ℝ := ∑ e ∈ Rg.interiorᶜ, Rg.step e

/-- **Integrality.** Each plaquette loop sum is `2π` times an integer. -/
theorem winding_int (p : Fin m) : ∃ q : ℤ, Rg.winding p = (q : ℝ) * (2 * π) := by
  refine ⟨- ∑ i : Fin 4, toIocDiv VortexWinding.two_pi_pos (-π) (Rg.θ p (i + 1) - Rg.θ p i), ?_⟩
  unfold Region.winding Region.step
  simp_rw [pdiff_eq, zsmul_eq_mul]
  rw [Finset.sum_sub_distrib, Finset.sum_sub_distrib]
  have hshift : ∑ i : Fin 4, Rg.θ p (i + 1) = ∑ i : Fin 4, Rg.θ p i :=
    Fintype.sum_equiv (Equiv.addRight 1) _ _ (fun _ => rfl)
  rw [hshift, sub_self, zero_sub, ← Finset.sum_mul]
  push_cast
  ring

/-- Interior edges cancel in reversed pairs, provided none sits at the branch point. -/
theorem interior_sum_eq_zero (hcut : ∀ e ∈ Rg.interior, Rg.step e ≠ π) :
    ∑ e ∈ Rg.interior, Rg.step e = 0 := by
  refine Finset.sum_involution (fun e _ => Rg.σ e) ?_ ?_ (fun e he => Rg.σ_mem e he) (fun e he => Rg.invol e he)
  · intro e he
    have h := cut_free_of_ne_pi (hcut e he)
    unfold Region.step
    rw [Rg.rev_start e he, Rg.rev_end e he]
    linarith
  · intro e he _
    exact Rg.no_fix e he

/-- **Discrete Stokes for windings.** The oriented boundary sum equals the sum of the plaquette loop
sums, provided no interior edge sits at the branch point. -/
theorem stokes (hcut : ∀ e ∈ Rg.interior, Rg.step e ≠ π) :
    Rg.boundarySum = ∑ p : Fin m, Rg.winding p := by
  have hall : ∑ e : Fin m × Fin 4, Rg.step e = ∑ p : Fin m, Rg.winding p := by
    unfold Region.winding; rw [Fintype.sum_prod_type]
  rw [← hall, ← Finset.sum_add_sum_compl Rg.interior, interior_sum_eq_zero Rg hcut, zero_add]
  rfl

/-- **The boundary sum is `2π` times the net charge inside.** -/
theorem boundary_eq_charge (hcut : ∀ e ∈ Rg.interior, Rg.step e ≠ π) (q : Fin m → ℤ)
    (hq : ∀ p, Rg.winding p = (q p : ℝ) * (2 * π)) :
    Rg.boundarySum = ((∑ p, q p : ℤ) : ℝ) * (2 * π) := by
  rw [stokes Rg hcut, Finset.sum_congr rfl (fun p _ => hq p), ← Finset.sum_mul]
  push_cast; rfl

/-- **A dipole is invisible from outside.** If the charges inside sum to zero, the boundary winding
is zero, whatever the size of the region. -/
theorem dipole_invisible (hcut : ∀ e ∈ Rg.interior, Rg.step e ≠ π) (q : Fin m → ℤ)
    (hq : ∀ p, Rg.winding p = (q p : ℝ) * (2 * π)) (hneutral : ∑ p, q p = 0) :
    Rg.boundarySum = 0 := by
  rw [boundary_eq_charge Rg hcut q hq, hneutral]; simp

/-- **A single core is seen at every scale.** If exactly one plaquette `p₀` carries charge `q₀` and all
others are neutral, the boundary winding is `q₀`, whatever the size of the region. -/
theorem single_core_visible (hcut : ∀ e ∈ Rg.interior, Rg.step e ≠ π) (q : Fin m → ℤ)
    (hq : ∀ p, Rg.winding p = (q p : ℝ) * (2 * π)) (p₀ : Fin m) (hothers : ∀ p ≠ p₀, q p = 0) :
    Rg.boundarySum = (q p₀ : ℝ) * (2 * π) := by
  rw [boundary_eq_charge Rg hcut q hq]
  congr 2
  rw [Finset.sum_eq_single p₀ (fun p _ hp => hothers p hp) (fun h => absurd (Finset.mem_univ p₀) h)]

end QuantumFluids.ScaleResolvedWinding

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.ScaleResolvedWinding.winding_int
#print axioms QuantumFluids.ScaleResolvedWinding.interior_sum_eq_zero
#print axioms QuantumFluids.ScaleResolvedWinding.stokes
#print axioms QuantumFluids.ScaleResolvedWinding.boundary_eq_charge
#print axioms QuantumFluids.ScaleResolvedWinding.dipole_invisible
#print axioms QuantumFluids.ScaleResolvedWinding.single_core_visible
