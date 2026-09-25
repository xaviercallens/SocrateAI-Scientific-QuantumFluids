/-
  CompactBoson.lean -- the T-duality of the compact boson stated on its SECTORS, so that three things can be
  read off the kernel: the duality is a reindexing of the sector lattice; the product of the electric and
  magnetic dimensions does not depend on the radius; the self-dual radius is not where the vortex becomes
  marginal.

  Conventions (α' = 2, the CFT normalisation in which the self-dual radius is √2). For a compact boson of radius
  `R`, the primary of momentum `n` and winding `w` has
      h    = ½ (n/R + w R/2)²,   h̄ = ½ (n/R − w R/2)²,
      Δ    = h + h̄ = n²/R² + w² R²/4,     spin s = h − h̄ = n w.
  The electric (spin-wave, `e^{iθ}`) operator is (n, w) = (1, 0); the magnetic (vortex) operator is (0, 1).
  In the XY / superfluid dictionary Δ(1,0) = η/2 and Δ(0,1) = n_s λ_T² / 2, so `Δ(1,0)·Δ(0,1) = 1/4` is the
  relation `η · n_s λ_T² = 1` tested in rounds 2 and 3, and `Δ(0,1) = 2` is the Nelson–Kosterlitz condition
  `n_s λ_T² = 4`.

  * `dim_dual`            : Δ(n, w; R) = Δ(w, n; 2/R) -- T-duality exchanges momentum and winding sectors;
  * `spin_dual`           : the spin is invariant;
  * `partition_dual`      : the sector sum Σ_{(n,w)} F(Δ, s) is invariant under R ↦ 2/R -- because the duality is a
                            bijection of ℤ² (no summability hypothesis is needed: `Equiv.tsum_eq`);
  * `electric_mul_magnetic`: Δ(1,0)·Δ(0,1) = 1/4 for every R -- the duality-invariant product;
  * `selfDual_radius`     : Δ(1,0) = Δ(0,1) iff R = √2 (R > 0), where both equal 1/2;
  * `vortex_marginal_radius`: Δ(0,1) = 2 iff R = 2√2;
  * `bkt_not_selfDual`    : the two radii differ -- the transition set by the marginality of one sector is not the
                            fixed point of the exchange symmetry.

  What this module says, and only this: on the sector lattice the duality is a relabelling that preserves the
  spectrum; the physical thresholds are conditions on single sectors. Nothing about dynamics, nothing about K3
  surfaces, nothing about any particular fluid.
-/
import Mathlib

namespace QuantumFluids.CompactBoson

/-- Scaling dimension of the (momentum `n`, winding `w`) primary at radius `R`. -/
noncomputable def dim (R : ℝ) (n w : ℤ) : ℝ := (n : ℝ) ^ 2 / R ^ 2 + (w : ℝ) ^ 2 * R ^ 2 / 4

/-- Conformal spin `h − h̄ = n w`. -/
def spin (n w : ℤ) : ℤ := n * w

/-- **T-duality on sectors**: exchanging momentum and winding while sending `R ↦ 2/R` preserves the dimension. -/
theorem dim_dual (R : ℝ) (hR : R ≠ 0) (n w : ℤ) : dim R n w = dim (2 / R) w n := by
  unfold dim
  field_simp
  ring

/-- The spin is symmetric under the exchange. -/
theorem spin_dual (n w : ℤ) : spin n w = spin w n := by
  unfold spin; ring

/-- The duality as a bijection of the sector lattice. -/
def swap : ℤ × ℤ ≃ ℤ × ℤ := Equiv.prodComm ℤ ℤ

/-- **The sector sum is duality-invariant**, for any weight `F` of the dimension and the spin: the sum over
`(n, w)` of `F (dim R n w) (spin n w)` equals the sum over `(n, w)` of `F (dim (2/R) n w) (spin n w)`. This is
`Equiv.tsum_eq` applied to `swap`; no convergence hypothesis is needed, because reindexing a sum by a bijection
is an identity of `tsum` whether or not the series converges. -/
theorem partition_dual (R : ℝ) (hR : R ≠ 0) (F : ℝ → ℤ → ℝ) :
    ∑' p : ℤ × ℤ, F (dim R p.1 p.2) (spin p.1 p.2) = ∑' p : ℤ × ℤ, F (dim (2 / R) p.1 p.2) (spin p.1 p.2) := by
  rw [← swap.tsum_eq (fun p : ℤ × ℤ => F (dim (2 / R) p.1 p.2) (spin p.1 p.2))]
  refine tsum_congr (fun p => ?_)
  simp only [swap, Equiv.prodComm_apply, Prod.fst_swap, Prod.snd_swap]
  rw [dim_dual R hR p.1 p.2, spin_dual]

/-- The electric (spin-wave) dimension. -/
theorem dim_electric (R : ℝ) : dim R 1 0 = 1 / R ^ 2 := by unfold dim; norm_num

/-- The magnetic (vortex) dimension. -/
theorem dim_magnetic (R : ℝ) : dim R 0 1 = R ^ 2 / 4 := by unfold dim; norm_num

/-- **The electric–magnetic product is independent of the radius**: `Δ(1,0)·Δ(0,1) = 1/4`. In the superfluid
dictionary this is `η · n_s λ_T² = 1`. -/
theorem electric_mul_magnetic (R : ℝ) (hR : R ≠ 0) : dim R 1 0 * dim R 0 1 = 1 / 4 := by
  rw [dim_electric, dim_magnetic]
  field_simp

/-- Positive square roots are determined by their squares. -/
theorem eq_of_sq_eq_sq_pos {a b : ℝ} (ha : 0 < a) (hb : 0 < b) (h : a ^ 2 = b ^ 2) : a = b := by
  have hprod : (a - b) * (a + b) = 0 := by linear_combination h
  rcases mul_eq_zero.1 hprod with h1 | h1
  · linarith
  · linarith

/-- The **self-dual radius**: `Δ(1,0) = Δ(0,1)` iff `R = √2` (for `R > 0`), and there both equal `1/2`. -/
theorem selfDual_radius {R : ℝ} (hR : 0 < R) : dim R 1 0 = dim R 0 1 ↔ R = Real.sqrt 2 := by
  rw [dim_electric, dim_magnetic]
  have h2 : Real.sqrt 2 ^ 2 = 2 := Real.sq_sqrt (by norm_num)
  have hs : 0 < Real.sqrt 2 := Real.sqrt_pos.2 (by norm_num)
  constructor
  · intro h
    have hR2 : R ^ 2 ≠ 0 := by positivity
    have h4 : R ^ 2 * R ^ 2 = 4 := by field_simp at h; linarith
    have hR2' : R ^ 2 = 2 := by
      have hprod : (R ^ 2 - 2) * (R ^ 2 + 2) = 0 := by linear_combination h4
      rcases mul_eq_zero.1 hprod with h1 | h1
      · linarith
      · nlinarith [sq_nonneg R]
    exact eq_of_sq_eq_sq_pos hR hs (by rw [hR2', h2])
  · rintro rfl
    rw [h2]; norm_num

theorem selfDual_value : dim (Real.sqrt 2) 1 0 = 1 / 2 ∧ dim (Real.sqrt 2) 0 1 = 1 / 2 := by
  rw [dim_electric, dim_magnetic, Real.sq_sqrt (by norm_num)]; norm_num

/-- The **vortex-marginality radius**: `Δ(0,1) = 2` iff `R = 2√2` (for `R > 0`). This is the BKT condition. -/
theorem vortex_marginal_radius {R : ℝ} (hR : 0 < R) : dim R 0 1 = 2 ↔ R = 2 * Real.sqrt 2 := by
  rw [dim_magnetic]
  have h2 : Real.sqrt 2 ^ 2 = 2 := Real.sq_sqrt (by norm_num)
  have hs : 0 < Real.sqrt 2 := Real.sqrt_pos.2 (by norm_num)
  have hc : (2 * Real.sqrt 2) ^ 2 = 8 := by rw [mul_pow, h2]; norm_num
  constructor
  · intro h
    exact eq_of_sq_eq_sq_pos hR (by positivity) (by rw [hc]; linarith)
  · rintro rfl
    rw [hc]; norm_num

/-- **BKT is not at the self-dual point**: the vortex-marginality radius is twice the self-dual radius. -/
theorem bkt_not_selfDual : (2 * Real.sqrt 2 : ℝ) ≠ Real.sqrt 2 := by
  have hs : 0 < Real.sqrt 2 := Real.sqrt_pos.2 (by norm_num)
  intro h; linarith

/-- At the vortex-marginality radius the electric dimension is `1/8`, i.e. `η = 1/4`: Nelson–Kosterlitz. -/
theorem eta_at_bkt : dim (2 * Real.sqrt 2) 1 0 = 1 / 8 := by
  rw [dim_electric, mul_pow, Real.sq_sqrt (by norm_num)]; norm_num

end QuantumFluids.CompactBoson

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.CompactBoson.dim_dual
#print axioms QuantumFluids.CompactBoson.spin_dual
#print axioms QuantumFluids.CompactBoson.partition_dual
#print axioms QuantumFluids.CompactBoson.dim_electric
#print axioms QuantumFluids.CompactBoson.dim_magnetic
#print axioms QuantumFluids.CompactBoson.electric_mul_magnetic
#print axioms QuantumFluids.CompactBoson.eq_of_sq_eq_sq_pos
#print axioms QuantumFluids.CompactBoson.selfDual_radius
#print axioms QuantumFluids.CompactBoson.selfDual_value
#print axioms QuantumFluids.CompactBoson.vortex_marginal_radius
#print axioms QuantumFluids.CompactBoson.bkt_not_selfDual
#print axioms QuantumFluids.CompactBoson.eta_at_bkt
