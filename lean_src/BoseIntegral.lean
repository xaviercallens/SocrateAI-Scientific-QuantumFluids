/-
The Bose integral behind the phonon specific heat of superfluid helium.

[G21] = Godfrin et al., Phys. Rev. B 103, 104516 (2021), Eq. (22): the phonon specific heat is a
series `C_V = A T³ + C T⁵ + D T⁶ + …` whose coefficients come from Bose integrals
`∫₀^∞ tⁿ/(eᵗ − 1) dt = Γ(n+1) ζ(n+1)`. The paper remarks that earlier published versions of this
series "contain errors". This file machine-checks the integral that fixes the leading (Debye)
coefficient `A`, and states the general Mellin identity from which every other coefficient follows.

Mathlib has `ζ(4) = π⁴/90` and the Gamma integral, but not the Bose integral; the bridge is
`hasSum_mellin` applied to `1/(eᵗ − 1) = Σₙ e^{-(n+1)t}`.

`mellin F s` is, by definition, `∫ t in Ioi 0, t^(s-1) • F t`, so `mellin bose 4` IS
`∫₀^∞ t³/(eᵗ − 1) dt`.
-/

import Mathlib

namespace QuantumFluids.BoseIntegral

open Real Set

/-- The Bose factor `1/(eᵗ − 1)`, complex-valued so that Mathlib's `mellin` applies. -/
noncomputable def bose (t : ℝ) : ℂ := ((1 / (rexp t - 1) : ℝ) : ℂ)

/-- `1/(eᵗ − 1) = Σₙ e^{-(n+1)t}` for `t > 0`: the geometric series behind Bose statistics. -/
theorem hasSum_bose {t : ℝ} (ht : t ∈ Ioi (0 : ℝ)) :
    HasSum (fun n : ℕ => (1 : ℂ) * rexp (-((n : ℝ) + 1) * t)) (bose t) := by
  have ht0 : 0 < t := ht
  have hr : rexp (-t) < 1 := by rw [Real.exp_lt_one_iff]; linarith
  have hr0 : 0 ≤ rexp (-t) := (Real.exp_pos _).le
  have hg := (hasSum_geometric_of_lt_one hr0 hr).mul_left (rexp (-t))
  have hterm : ∀ n : ℕ, rexp (-t) * rexp (-t) ^ n = rexp (-((n : ℝ) + 1) * t) := by
    intro n
    rw [← Real.exp_nat_mul, ← Real.exp_add]
    congr 1; ring
  have hgt : 1 < rexp t := Real.one_lt_exp_iff.mpr ht0
  have hval : rexp (-t) * (1 - rexp (-t))⁻¹ = 1 / (rexp t - 1) := by
    rw [Real.exp_neg]
    have h1 : rexp t ≠ 0 := (Real.exp_pos t).ne'
    have h2 : rexp t - 1 ≠ 0 := by linarith
    have h3 : 1 - (rexp t)⁻¹ ≠ 0 := by
      rw [sub_ne_zero]; intro h; rw [eq_comm, inv_eq_one] at h; linarith
    field_simp
  simp_rw [hterm] at hg
  rw [hval] at hg
  have hc := Complex.hasSum_ofReal.mpr hg
  simpa [bose] using hc

/-- **Mellin form of the Bose integral.** For `Re s > 1`,
`∫₀^∞ t^(s-1)/(eᵗ − 1) dt = Γ(s) · Σₙ 1/(n+1)^s`. -/
theorem hasSum_mellin_bose {s : ℂ} (hs : 1 < s.re) :
    HasSum (fun n : ℕ => Complex.Gamma s * 1 / (((n : ℝ) + 1 : ℝ) : ℂ) ^ s) (mellin bose s) := by
  refine hasSum_mellin (a := fun _ : ℕ => (1 : ℂ)) (p := fun n : ℕ => (n : ℝ) + 1)
    (fun i => Or.inr (by positivity)) (by linarith) (fun t ht => hasSum_bose ht) ?_
  simp only [norm_one]
  have := (Real.summable_one_div_nat_rpow.mpr hs)
  exact (summable_nat_add_iff 1).mpr this |>.congr (fun n => by push_cast; ring_nf)

/-- **`∫₀^∞ t³/(eᵗ − 1) dt = π⁴/15`.** This is `Γ(4) ζ(4) = 6 · π⁴/90`, the Bose integral behind the
Debye `T³` law and hence behind the leading coefficient `A = 2π²k_B⁴V/(15c³ħ³)` of [G21] Eq. (22). -/
theorem mellin_bose_four : mellin bose 4 = (π : ℂ) ^ 4 / 15 := by
  have h := hasSum_mellin_bose (s := 4) (by norm_num)
  have hG : Complex.Gamma 4 = 6 := by
    rw [show (4 : ℂ) = ((3 : ℕ) : ℂ) + 1 by norm_num, Complex.Gamma_nat_eq_factorial]
    norm_num [Nat.factorial]
  have hpow : ∀ n : ℕ, (((n : ℝ) + 1 : ℝ) : ℂ) ^ (4 : ℂ) = ((n : ℂ) + 1) ^ 4 := by
    intro n
    rw [show (4 : ℂ) = ((4 : ℕ) : ℂ) by norm_num, Complex.cpow_natCast]
    push_cast; ring
  have hterm : ∀ n : ℕ, Complex.Gamma 4 * 1 / (((n : ℝ) + 1 : ℝ) : ℂ) ^ (4 : ℂ)
      = 6 * (1 / ((n : ℂ) + 1) ^ 4) := by
    intro n; rw [hG, hpow]; ring
  have hz : riemannZeta 4 = ∑' n : ℕ, 1 / (n : ℂ) ^ 4 := by
    have := zeta_nat_eq_tsum_of_gt_one (k := 4) (by norm_num)
    simpa using this
  have hsumm : Summable (fun n : ℕ => 1 / (n : ℂ) ^ 4) := by
    have := (Complex.summable_one_div_nat_cpow (p := 4)).mpr (by norm_num)
    refine this.congr (fun n => ?_)
    rw [show (4 : ℂ) = ((4 : ℕ) : ℂ) by norm_num, Complex.cpow_natCast]
  have hshift : ∑' n : ℕ, 1 / (n : ℂ) ^ 4 = ∑' n : ℕ, 1 / ((n : ℂ) + 1) ^ 4 := by
    rw [hsumm.tsum_eq_zero_add]; simp
  rw [← h.tsum_eq]
  simp_rw [hterm]
  rw [tsum_mul_left, ← hshift, ← hz, riemannZeta_four]
  ring

/-! ## From the integral to the coefficient `A` of [G21] Eq. (22)

For a pure phonon branch `ε = ħck` the substitution `x = ħck/k_BT` turns the internal energy
`(V/2π²) ∫ ε k² /(e^{ε/k_BT} − 1) dk` into `(V/2π²) (k_BT)⁴/(ħc)³ · ∫₀^∞ x³/(eˣ − 1) dx`. With the
value `π⁴/15` proved above, the energy is `π² V (k_BT)⁴ / (30 (ħc)³)`. The substitution itself is
not formalised here; what is checked is everything after it. -/

/-- Phonon internal energy after the substitution, with the Bose integral `I` left symbolic. -/
noncomputable def debyeEnergy (V kB hbar c I T : ℝ) : ℝ :=
  V / (2 * π ^ 2) * (kB * T) ^ 4 / (hbar * c) ^ 3 * I

/-- With `I = π⁴/15` the prefactor collapses to `π² V / 30`. -/
theorem debyeEnergy_eq (V kB hbar c T : ℝ) :
    debyeEnergy V kB hbar c (π ^ 4 / 15) T = π ^ 2 * V * (kB * T) ^ 4 / (30 * (hbar * c) ^ 3) := by
  unfold debyeEnergy
  have : π ≠ 0 := Real.pi_ne_zero
  field_simp
  ring

/-- **The Debye coefficient.** `C_V = dE/dT = A T³` with `A = 2π² k_B⁴ V / (15 c³ ħ³)`, exactly
the coefficient **A** printed in [G21] Eq. (22). -/
theorem debye_specific_heat (V kB hbar c T : ℝ) :
    HasDerivAt (fun T => debyeEnergy V kB hbar c (π ^ 4 / 15) T)
      (2 * π ^ 2 * kB ^ 4 * V / (15 * c ^ 3 * hbar ^ 3) * T ^ 3) T := by
  have hfun : (fun T => debyeEnergy V kB hbar c (π ^ 4 / 15) T)
      = fun T => (π ^ 2 * V * kB ^ 4 / (30 * (hbar * c) ^ 3)) * T ^ 4 := by
    funext x; rw [debyeEnergy_eq]; ring
  rw [hfun]
  have h := (hasDerivAt_pow 4 T).const_mul (π ^ 2 * V * kB ^ 4 / (30 * (hbar * c) ^ 3))
  refine h.congr_deriv ?_
  by_cases hh : hbar = 0
  · subst hh; simp
  by_cases hc : c = 0
  · subst hc; simp
  field_simp
  ring

end QuantumFluids.BoseIntegral

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.BoseIntegral.hasSum_bose
#print axioms QuantumFluids.BoseIntegral.hasSum_mellin_bose
#print axioms QuantumFluids.BoseIntegral.mellin_bose_four
#print axioms QuantumFluids.BoseIntegral.debyeEnergy_eq
#print axioms QuantumFluids.BoseIntegral.debye_specific_heat
