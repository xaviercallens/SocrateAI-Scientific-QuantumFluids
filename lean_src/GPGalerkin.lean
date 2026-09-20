/-
D3 (docs/OPENAI_NSE_LEVERAGE_FOR_QUANTUM_FLUIDS.md): structure of the Fourier-Galerkin
Gross-Pitaevskii nonlinearity that is INDEPENDENT of the truncation set.

Setting. `G` is an additive commutative group (the lattice `Z^3` is the case of interest), `Λ` a
finite set of retained modes (the truncation; nothing below depends on which set), and
`ψ : G → ℂ` the mode amplitudes. The projected cubic nonlinearity is
  `N ψ k = Σ_{k1 + k3 = k + k2, all in Λ} ψ(k1) conj(ψ(k2)) ψ(k3)`.

WHAT IS PROVED, for every finite `Λ`:
 1. `pairing_eq_sum_normSq`: `Q ψ := Σ_{k∈Λ} conj(ψ k) · N ψ k = Σ_q |A_q|²` with
    `A_q = Σ_{a-b=q} ψ(a) conj(ψ(b))` (the Fourier transform of `|ψ|²`).
 2. `pairing_nonneg`, `pairing_im_zero`: `Q` is real and `Q ≥ 0`. This is the defocusing sign:
    the interaction energy is coercive, with no `1/α'`-type constant and no dependence on `Λ`.
 3. `mass_rate_zero`: for real dispersion `ω` and real coupling `g`, with `G_k = ω_k ψ_k + g N_k`,
    `Σ_k Im(conj(ψ_k) G_k) = 0`. This is the algebraic core of `d/dt Σ|ψ_k|² = 0` for
    `i ∂t ψ_k = G_k` (since `d/dt |ψ_k|² = 2 Im(conj(ψ_k) G_k)`).
 4. `kinetic_le_energy`: `Σ ω_k |ψ_k|² ≤ E` whenever `E = Σ ω_k|ψ_k|² + (g/2) Q`, `g ≥ 0`.

WHAT IS NOT PROVED (be explicit, per the audit discipline):
 - Conservation of `E` along the flow (needs `∂Q/∂conj(ψ_k) = N_k`, the Hamiltonian gradient
   identity). Item 4 is therefore an inequality between two functions of `ψ`; it bounds the kinetic
   part by the energy at any instant, and becomes a uniform-in-`Λ` a-priori bound only once
   conservation of `E` is added.
 - Anything about time evolution existence, `H^s` for `s > 1`, or `u = ∇S` (see MadelungSplit).
 - The comparison with real Katz-Pavlovic / Navier-Stokes is by contrast in prose only; nothing
   here is a statement about the Navier-Stokes enstrophy production factor.
-/

import Mathlib

namespace QuantumFluids.GPGalerkin

open Finset

variable {G : Type*} [AddCommGroup G] [DecidableEq G]

/-- Projected cubic nonlinearity on the retained set `Λ`. -/
noncomputable def nl (Λ : Finset G) (ψ : G → ℂ) (k : G) : ℂ :=
  ∑ k1 ∈ Λ, ∑ k2 ∈ Λ, ∑ k3 ∈ Λ,
    if k1 + k3 = k + k2 then ψ k1 * (starRingEnd ℂ) (ψ k2) * ψ k3 else 0

/-- The pairing `Q = Σ_k conj(ψ_k) N_k` (the quartic interaction sum). -/
noncomputable def pairing (Λ : Finset G) (ψ : G → ℂ) : ℂ :=
  ∑ k ∈ Λ, (starRingEnd ℂ) (ψ k) * nl Λ ψ k

/-- The summand `f (a, b) = ψ_a conj(ψ_b)`. -/
noncomputable def ff (ψ : G → ℂ) (p : G × G) : ℂ := ψ p.1 * (starRingEnd ℂ) (ψ p.2)

/-- Fourier transform of `|ψ|²` restricted to `Λ`: `A_q = Σ_{a-b=q} ψ_a conj(ψ_b)`. -/
noncomputable def dens (Λ : Finset G) (ψ : G → ℂ) (q : G) : ℂ :=
  ∑ p ∈ Λ ×ˢ Λ, if p.1 - p.2 = q then ff ψ p else 0

/-- The set of differences, containing every `q` with `A_q ≠ 0`. -/
noncomputable def diffs (Λ : Finset G) : Finset G :=
  (Λ ×ˢ Λ).image (fun p => p.1 - p.2)

/-- `Q` as a double sum over pairs, with the resonance condition `a + c = d + b`. -/
theorem pairing_eq_prod (Λ : Finset G) (ψ : G → ℂ) :
    pairing Λ ψ = ∑ p ∈ Λ ×ˢ Λ, ∑ r ∈ Λ ×ˢ Λ,
      if p.1 - p.2 = r.1 - r.2 then ff ψ p * (starRingEnd ℂ) (ff ψ r) else 0 := by
  unfold pairing nl ff
  simp only [Finset.sum_product, Finset.mul_sum, mul_ite, mul_zero, sub_eq_sub_iff_add_eq_add]
  conv_lhs => rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun a _ => ?_)
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun b _ => ?_)
  refine Finset.sum_congr rfl (fun d _ => ?_)
  refine Finset.sum_congr rfl (fun c _ => ?_)
  by_cases h : a + c = d + b <;> simp [h, map_mul] <;> ring

/-- `|A_q|²` as a double sum over pairs. -/
theorem dens_mul_conj (Λ : Finset G) (ψ : G → ℂ) (q : G) :
    dens Λ ψ q * (starRingEnd ℂ) (dens Λ ψ q) = ∑ p ∈ Λ ×ˢ Λ, ∑ r ∈ Λ ×ˢ Λ,
      if p.1 - p.2 = q ∧ r.1 - r.2 = q then ff ψ p * (starRingEnd ℂ) (ff ψ r) else 0 := by
  unfold dens
  rw [map_sum, Finset.sum_mul_sum]
  refine Finset.sum_congr rfl (fun p _ => Finset.sum_congr rfl (fun r _ => ?_))
  by_cases h1 : p.1 - p.2 = q <;> by_cases h2 : r.1 - r.2 = q <;> simp [h1, h2]

/-- **`Q = Σ_q |A_q|²`.** The quartic interaction sum is a sum of squared moduli, whatever `Λ`. -/
theorem pairing_eq_sum (Λ : Finset G) (ψ : G → ℂ) :
    pairing Λ ψ = ∑ q ∈ diffs Λ, dens Λ ψ q * (starRingEnd ℂ) (dens Λ ψ q) := by
  rw [pairing_eq_prod]
  simp_rw [dens_mul_conj]
  conv_rhs => rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun p hp => ?_)
  conv_rhs => rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun r hr => ?_)
  have hmem : p.1 - p.2 ∈ diffs Λ := Finset.mem_image.mpr ⟨p, hp, rfl⟩
  rw [Finset.sum_eq_single (p.1 - p.2)]
  · by_cases h : p.1 - p.2 = r.1 - r.2 <;> simp [h, eq_comm]
  · intro q _ hq
    have : ¬ (p.1 - p.2 = q) := fun h => hq h.symm
    simp [this]
  · intro hn; exact absurd hmem hn

/-- The real quartic interaction energy `Σ_q |A_q|²`. -/
noncomputable def pairingRe (Λ : Finset G) (ψ : G → ℂ) : ℝ :=
  ∑ q ∈ diffs Λ, Complex.normSq (dens Λ ψ q)

/-- `Q` is the real number `Σ_q |A_q|²`: in particular it is real. -/
theorem pairing_eq_ofReal (Λ : Finset G) (ψ : G → ℂ) :
    pairing Λ ψ = (pairingRe Λ ψ : ℂ) := by
  rw [pairing_eq_sum, pairingRe]
  push_cast
  exact Finset.sum_congr rfl (fun q _ => Complex.mul_conj _)

/-- **Defocusing sign.** The interaction energy is nonnegative for every truncation `Λ`. -/
theorem pairing_nonneg (Λ : Finset G) (ψ : G → ℂ) : 0 ≤ pairingRe Λ ψ :=
  Finset.sum_nonneg (fun q _ => Complex.normSq_nonneg _)

/-- `Q` has zero imaginary part. -/
theorem pairing_im_zero (Λ : Finset G) (ψ : G → ℂ) : (pairing Λ ψ).im = 0 := by
  rw [pairing_eq_ofReal]; simp

/-- **Algebraic core of mass conservation.** For real dispersion `ω` and real coupling `g`,
with `G_k = ω_k ψ_k + g N_k`: `Σ_{k∈Λ} Im(conj(ψ_k) G_k) = 0`. Since
`d/dt |ψ_k|² = 2 Im(conj(ψ_k) G_k)` for `i ∂t ψ_k = G_k`, this is `d/dt Σ|ψ_k|² = 0`
for every truncation `Λ`. -/
theorem mass_rate_zero (Λ : Finset G) (ψ : G → ℂ) (ω : G → ℝ) (g : ℝ) :
    ∑ k ∈ Λ, ((starRingEnd ℂ) (ψ k) * ((ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k)).im = 0 := by
  have h1 : ∀ k, ((starRingEnd ℂ) (ψ k) * ((ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k)).im
      = g * ((starRingEnd ℂ) (ψ k) * nl Λ ψ k).im := by
    intro k
    have : (starRingEnd ℂ) (ψ k) * ((ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k)
        = ((ω k * Complex.normSq (ψ k) : ℝ) : ℂ) + (g : ℂ) * ((starRingEnd ℂ) (ψ k) * nl Λ ψ k) := by
      push_cast
      rw [Complex.normSq_eq_conj_mul_self]
      ring
    rw [this]; simp
  simp_rw [h1]
  rw [← Finset.mul_sum, ← Complex.im_sum]
  have := pairing_im_zero Λ ψ
  unfold pairing at this
  rw [this, mul_zero]

/-- **Kinetic part bounded by the energy, uniformly in `Λ`.** If
`E = Σ ω_k |ψ_k|² + (g/2) Q` with `g ≥ 0`, then `Σ ω_k |ψ_k|² ≤ E`. Combined with conservation
of `E` (NOT proved here) this is a truncation-independent a-priori bound. -/
theorem kinetic_le_energy (Λ : Finset G) (ψ : G → ℂ) (ω : G → ℝ) (g E : ℝ) (hg : 0 ≤ g)
    (hE : E = ∑ k ∈ Λ, ω k * Complex.normSq (ψ k) + g / 2 * pairingRe Λ ψ) :
    ∑ k ∈ Λ, ω k * Complex.normSq (ψ k) ≤ E := by
  have := pairing_nonneg Λ ψ
  rw [hE]
  nlinarith

/-! ## Hamiltonian gradient identity (algebraic core of energy conservation) -/

/-- `N_k = Σ_b ψ_b A_{k-b}`: the nonlinearity as a convolution with the density transform. -/
theorem nl_eq_dens (Λ : Finset G) (ψ : G → ℂ) (k : G) :
    nl Λ ψ k = ∑ b ∈ Λ, ψ b * dens Λ ψ (k - b) := by
  unfold nl dens ff
  simp only [Finset.sum_product, Finset.mul_sum, mul_ite, mul_zero]
  conv_lhs => arg 2; intro k1; rw [Finset.sum_comm]
  conv_lhs => rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun k3 _ => ?_)
  refine Finset.sum_congr rfl (fun k1 _ => ?_)
  refine Finset.sum_congr rfl (fun k2 _ => ?_)
  have hc : (k1 + k3 = k + k2) ↔ (k1 - k2 = k - k3) := (sub_eq_sub_iff_add_eq_add).symm
  by_cases h : k1 - k2 = k - k3
  · have h' := hc.mpr h
    simp [h, h']; ring
  · have h' : ¬ (k1 + k3 = k + k2) := fun hh => h (hc.mp hh)
    simp [h, h']

/-- `A_{-q} = conj(A_q)`: the density transform of a real density is Hermitian. -/
theorem dens_neg (Λ : Finset G) (ψ : G → ℂ) (q : G) :
    dens Λ ψ (-q) = (starRingEnd ℂ) (dens Λ ψ q) := by
  unfold dens ff
  simp only [Finset.sum_product, map_sum, apply_ite (starRingEnd ℂ), map_zero, map_mul,
    Complex.conj_conj]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun a _ => Finset.sum_congr rfl (fun b _ => ?_))
  have hc : (b - a = -q) ↔ (a - b = q) := by
    rw [← neg_sub a b, neg_inj]
  by_cases h : a - b = q
  · simp [h, hc.mpr h, mul_comm]
  · simp [h, mt hc.mp h]

/-- Polarised density transform: the first variation of `A_q` in direction `δ`. -/
noncomputable def densVar (Λ : Finset G) (ψ δ : G → ℂ) (q : G) : ℂ :=
  ∑ p ∈ Λ ×ˢ Λ, if p.1 - p.2 = q then δ p.1 * (starRingEnd ℂ) (ψ p.2)
      + ψ p.1 * (starRingEnd ℂ) (δ p.2) else 0

/-- Sum over `q` collapses to a sum over pairs. -/
theorem sum_densVar (Λ : Finset G) (ψ δ : G → ℂ) :
    ∑ q ∈ diffs Λ, (starRingEnd ℂ) (dens Λ ψ q) * densVar Λ ψ δ q
      = ∑ p ∈ Λ ×ˢ Λ, (starRingEnd ℂ) (dens Λ ψ (p.1 - p.2)) *
          (δ p.1 * (starRingEnd ℂ) (ψ p.2) + ψ p.1 * (starRingEnd ℂ) (δ p.2)) := by
  unfold densVar
  simp_rw [Finset.mul_sum]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun p hp => ?_)
  have hmem : p.1 - p.2 ∈ diffs Λ := Finset.mem_image.mpr ⟨p, hp, rfl⟩
  rw [Finset.sum_eq_single (p.1 - p.2)]
  · simp
  · intro q _ hq
    have : ¬ (p.1 - p.2 = q) := fun h => hq h.symm
    simp [this]
  · intro hn; exact absurd hmem hn

/-- **Hamiltonian gradient identity (polarised).** For every truncation `Λ`, state `ψ` and
perturbation `δ`:  `Σ_q 2 Re(conj(A_q) · dA_q[δ]) = 4 Re Σ_k conj(δ_k) N_k`. That is
`d Q[δ] = 4 Re⟨δ, N(ψ)⟩`, i.e. `N = ∂Q/∂conj(ψ)` up to the factor. -/
theorem grad_identity (Λ : Finset G) (ψ δ : G → ℂ) :
    ∑ q ∈ diffs Λ, 2 * ((starRingEnd ℂ) (dens Λ ψ q) * densVar Λ ψ δ q).re
      = 4 * (∑ k ∈ Λ, (starRingEnd ℂ) (δ k) * nl Λ ψ k).re := by
  rw [← Finset.mul_sum, ← Complex.re_sum, sum_densVar]
  -- split the pair sum into T1 + T2
  simp_rw [mul_add, Finset.sum_add_distrib]
  set T1 := ∑ p ∈ Λ ×ˢ Λ, (starRingEnd ℂ) (dens Λ ψ (p.1 - p.2)) * (δ p.1 * (starRingEnd ℂ) (ψ p.2)) with hT1
  set T2 := ∑ p ∈ Λ ×ˢ Λ, (starRingEnd ℂ) (dens Λ ψ (p.1 - p.2)) * (ψ p.1 * (starRingEnd ℂ) (δ p.2)) with hT2
  -- T2 = conj T1 (swap the pair, use Hermiticity of A)
  have hT2c : T2 = (starRingEnd ℂ) T1 := by
    rw [hT1, hT2, map_sum]
    simp only [Finset.sum_product]
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl (fun a _ => Finset.sum_congr rfl (fun b _ => ?_))
    have := dens_neg Λ ψ (b - a)
    rw [neg_sub] at this
    simp only [map_mul, Complex.conj_conj]
    rw [← this]
    ring
  -- T1 = Σ_k δ_k conj(N_k)
  have hT1n : T1 = ∑ k ∈ Λ, δ k * (starRingEnd ℂ) (nl Λ ψ k) := by
    rw [hT1]
    simp only [Finset.sum_product]
    refine Finset.sum_congr rfl (fun a _ => ?_)
    rw [nl_eq_dens, map_sum, Finset.mul_sum]
    refine Finset.sum_congr rfl (fun b _ => ?_)
    rw [map_mul]; ring
  have hre : (T1 + T2).re = 2 * T1.re := by
    rw [hT2c]; simp [Complex.add_re]; ring
  rw [hre, hT1n]
  have : (∑ k ∈ Λ, δ k * (starRingEnd ℂ) (nl Λ ψ k)).re
      = (∑ k ∈ Λ, (starRingEnd ℂ) (δ k) * nl Λ ψ k).re := by
    have h : ∑ k ∈ Λ, δ k * (starRingEnd ℂ) (nl Λ ψ k)
        = (starRingEnd ℂ) (∑ k ∈ Λ, (starRingEnd ℂ) (δ k) * nl Λ ψ k) := by
      rw [map_sum]; refine Finset.sum_congr rfl (fun k _ => ?_); simp [map_mul]
    rw [h]; simp
  rw [this]; ring

/-- **Algebraic core of energy conservation.** With `G_k = ω_k ψ_k + g N_k` (real `ω`, `g`) and
the flow direction `δ_k = -i G_k`, the first variation of `E = Σ ω|ψ|² + (g/2) Q` vanishes:
`Σ_k 2 ω_k Re(conj(ψ_k) δ_k) + (g/2) Σ_q 2 Re(conj(A_q) dA_q[δ]) = 0`.
Only the algebraic identity is proved here; identifying it with `dE/dt` needs the chain rule for
the (polynomial) map `t ↦ ψ(t)`, which is not formalised. -/
theorem energy_rate_zero (Λ : Finset G) (ψ : G → ℂ) (ω : G → ℝ) (g : ℝ) :
    ∑ k ∈ Λ, 2 * ω k * ((starRingEnd ℂ) (ψ k) *
        (-Complex.I * ((ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k))).re
      + g / 2 * ∑ q ∈ diffs Λ, 2 * ((starRingEnd ℂ) (dens Λ ψ q) *
          densVar Λ ψ (fun k => -Complex.I * ((ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k)) q).re = 0 := by
  set Gf : G → ℂ := fun k => (ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k with hG
  rw [grad_identity]
  set δ : G → ℂ := fun k => -Complex.I * Gf k with hδ
  -- termwise: 2 ω Re(conj ψ δ) + 2 g Re(conj δ N) = 2 Re(conj δ G)
  have key : ∀ k, 2 * ω k * ((starRingEnd ℂ) (ψ k) * δ k).re
      + g / 2 * (4 * ((starRingEnd ℂ) (δ k) * nl Λ ψ k).re)
      = 2 * ((starRingEnd ℂ) (δ k) * Gf k).re := by
    intro k
    have h1 : ((starRingEnd ℂ) (ψ k) * δ k).re = ((starRingEnd ℂ) (δ k) * ψ k).re := by
      rw [← Complex.conj_re ((starRingEnd ℂ) (δ k) * ψ k)]
      congr 1; simp [mul_comm]
    have h2 : ((starRingEnd ℂ) (δ k) * Gf k)
        = (ω k : ℂ) * ((starRingEnd ℂ) (δ k) * ψ k) + (g : ℂ) * ((starRingEnd ℂ) (δ k) * nl Λ ψ k) := by
      simp only [hG]; ring
    rw [h1, h2]
    simp [Complex.add_re]
    ring
  have hz : ∀ k, ((starRingEnd ℂ) (δ k) * Gf k).re = 0 := by
    intro k
    have : (starRingEnd ℂ) (δ k) * Gf k = Complex.I * (Complex.normSq (Gf k) : ℂ) := by
      rw [Complex.normSq_eq_conj_mul_self]; simp [hδ, map_mul]; ring
    rw [this]; simp
  have hs : ∑ k ∈ Λ, 2 * ω k * ((starRingEnd ℂ) (ψ k) * δ k).re
      + g / 2 * (4 * (∑ k ∈ Λ, (starRingEnd ℂ) (δ k) * nl Λ ψ k).re) = 0 := by
    rw [Complex.re_sum, Finset.mul_sum, Finset.mul_sum, ← Finset.sum_add_distrib]
    refine Finset.sum_eq_zero (fun k _ => ?_)
    rw [key k, hz k]; ring
  exact hs

end QuantumFluids.GPGalerkin

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.GPGalerkin.pairing_eq_prod
#print axioms QuantumFluids.GPGalerkin.dens_mul_conj
#print axioms QuantumFluids.GPGalerkin.pairing_eq_sum
#print axioms QuantumFluids.GPGalerkin.pairing_eq_ofReal
#print axioms QuantumFluids.GPGalerkin.pairing_nonneg
#print axioms QuantumFluids.GPGalerkin.pairing_im_zero
#print axioms QuantumFluids.GPGalerkin.mass_rate_zero
#print axioms QuantumFluids.GPGalerkin.kinetic_le_energy
#print axioms QuantumFluids.GPGalerkin.nl_eq_dens
#print axioms QuantumFluids.GPGalerkin.dens_neg
#print axioms QuantumFluids.GPGalerkin.sum_densVar
#print axioms QuantumFluids.GPGalerkin.grad_identity
#print axioms QuantumFluids.GPGalerkin.energy_rate_zero
