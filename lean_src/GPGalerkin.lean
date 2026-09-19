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

end QuantumFluids.GPGalerkin

#print axioms QuantumFluids.GPGalerkin.pairing_eq_sum
#print axioms QuantumFluids.GPGalerkin.pairing_nonneg
#print axioms QuantumFluids.GPGalerkin.pairing_im_zero
#print axioms QuantumFluids.GPGalerkin.mass_rate_zero
#print axioms QuantumFluids.GPGalerkin.kinetic_le_energy
