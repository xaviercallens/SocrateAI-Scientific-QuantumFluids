/-
  Ch04_DosLink.lean -- NEW Lean written for Chapter 4 of the book "Quantum Fluids in Lean 4: a tribute to Henri Godfrin"
  (not part of the QuantumFluids library; it imports three of its modules).

  Why.  `PhononSeries` proves that the inverse series printed in Godfrin et al., PRB 103, 104516 (2021), inverts the dispersion relation
  and that `k^2 dk/de` equals an explicit polynomial; `PhononSpecificHeat` proves that the derivative of the term-by-term energy is the six
  closed forms of their Eq. (22).  The design note docs/designs/PHONON_SERIES_A_TO_L.md (section 6, item 1) records that the two are linked
  "by inspection": the brackets passed to `energyTerm` are retyped, not extracted from the polynomial; `kInv0Deriv` is typed in rather than
  computed as a derivative; the Bose integrals passed to `energyTerm` are retyped as well.  This file removes those retypings:

    kInv0_inverts                   the a1 = 0 case of `dispersion_kInv`: `kInv0` inverts k (1 + a2 k^2 + ... + a6 k^6) modulo e^8
    derivative_kPoly                Mathlib's formal derivative of `kInv0` (a polynomial in `X`) is `kInv0Deriv`
    dos_coeffs                      the coefficients of `kPoly^2 * derivative kPoly` in degrees 2..8 are exactly the brackets
    phonon_specific_heat_from_dos   Eq. (22) with the brackets read off that polynomial
    phonon_specific_heat_end_to_end ... and the six Bose integrals read off `mellin bose`, the odd zeta values being `riemannZeta 7, 9`
    energyMonomial_eq               the energy of a density-of-states monomial, written as the integral itself (a Mellin transform),
                                    equals `energyTerm` with the Bose integral `(mellin bose (n + 2)).re`  (T > 0)
    phonon_specific_heat_integral   Eq. (22) for the sum of those integrals, at T > 0

  NOT proved here: that the truncated density of states may stand for the true one under the integral (an asymptotic statement about a
  function), and anything about alpha_1 != 0.

  Compiled for the book with Lean 4.34.0-rc2 and the Mathlib of the project's Lake tree.  The three library modules were first compiled,
  unchanged, from lean_src/ into .olean files in a scratch directory that was then put on LEAN_PATH:
      lean --root=lean_src -o <dir>/BoseIntegral.olean lean_src/BoseIntegral.lean          (likewise PhononSeries, PhononSpecificHeat)
      LEAN_PATH=<LEAN_PATH of the Lake tree>:<dir>  lean book/lean/Ch04_DosLink.lean
  Result: exit code 0, no error, no `sorry`; the `#print axioms` lines at the end of the file give, for every declaration, a subset of
  {propext, Classical.choice, Quot.sound}.
-/
import Mathlib
import BoseIntegral
import PhononSeries
import PhononSpecificHeat

open Polynomial Real
open QuantumFluids.PhononSeries

namespace QuantumFluids.DosLink

section ring_part
variable {R : Type*} [CommRing R]

theorem kInv_zero (a2 a3 a4 a5 a6 e : R) :
    kInv 0 a2 a3 a4 a5 a6 e = kInv0 a2 a3 a4 a5 a6 e := by
  unfold kInv kInv0; ring

theorem kInv0_inverts (a2 a3 a4 a5 a6 e : R) (h : e ^ 8 = 0) :
    kInv0 a2 a3 a4 a5 a6 e * (1 + a2 * kInv0 a2 a3 a4 a5 a6 e ^ 2 + a3 * kInv0 a2 a3 a4 a5 a6 e ^ 3
      + a4 * kInv0 a2 a3 a4 a5 a6 e ^ 4 + a5 * kInv0 a2 a3 a4 a5 a6 e ^ 5
      + a6 * kInv0 a2 a3 a4 a5 a6 e ^ 6) = e := by
  have h0 := dispersion_kInv 0 a2 a3 a4 a5 a6 e h
  rw [kInv_zero] at h0
  simpa using h0

/-- The right-hand side of `density_of_states`, as a definition. -/
def dosRhs (a2 a3 a4 a5 a6 e : R) : R :=
  e ^ 2 - 5 * a2 * e ^ 4 - 6 * a3 * e ^ 5 + 7 * (4 * a2 ^ 2 - a4) * e ^ 6
    + 8 * (9 * a2 * a3 - a5) * e ^ 7
    - 3 * (55 * a2 ^ 3 - 30 * a2 * a4 - 15 * a3 ^ 2 + 3 * a6) * e ^ 8

theorem dos_eq (a2 a3 a4 a5 a6 e : R) (h : e ^ 9 = 0) :
    kInv0 a2 a3 a4 a5 a6 e ^ 2 * kInv0Deriv a2 a3 a4 a5 a6 e = dosRhs a2 a3 a4 a5 a6 e :=
  density_of_states a2 a3 a4 a5 a6 e h

theorem map_kInv0 {S : Type*} [CommRing S] (f : R →+* S) (a2 a3 a4 a5 a6 e : R) :
    f (kInv0 a2 a3 a4 a5 a6 e) = kInv0 (f a2) (f a3) (f a4) (f a5) (f a6) (f e) := by
  unfold kInv0; simp [map_ofNat f]

theorem map_kInv0Deriv {S : Type*} [CommRing S] (f : R →+* S) (a2 a3 a4 a5 a6 e : R) :
    f (kInv0Deriv a2 a3 a4 a5 a6 e) = kInv0Deriv (f a2) (f a3) (f a4) (f a5) (f a6) (f e) := by
  unfold kInv0Deriv; simp [map_ofNat f]

theorem map_dosRhs {S : Type*} [CommRing S] (f : R →+* S) (a2 a3 a4 a5 a6 e : R) :
    f (dosRhs a2 a3 a4 a5 a6 e) = dosRhs (f a2) (f a3) (f a4) (f a5) (f a6) (f e) := by
  unfold dosRhs; simp [map_ofNat f]

end ring_part

/-- The inverse series with the dispersion coefficients as constant polynomials, evaluated at `X`. -/
noncomputable def kPoly (a2 a3 a4 a5 a6 : ℝ) : ℝ[X] :=
  kInv0 (C a2) (C a3) (C a4) (C a5) (C a6) X

theorem derivative_kPoly (a2 a3 a4 a5 a6 : ℝ) :
    derivative (kPoly a2 a3 a4 a5 a6) = kInv0Deriv (C a2) (C a3) (C a4) (C a5) (C a6) X := by
  unfold kPoly kInv0 kInv0Deriv
  simp [derivative_pow, C_ofNat]
  ring

/-- The density-of-states polynomial `k(e)^2 * dk/de`, with `dk/de` the formal derivative. -/
noncomputable def dosPoly (a2 a3 a4 a5 a6 : ℝ) : ℝ[X] :=
  kPoly a2 a3 a4 a5 a6 ^ 2 * derivative (kPoly a2 a3 a4 a5 a6)

theorem dosRhs_poly (a2 a3 a4 a5 a6 : ℝ) :
    dosRhs (C a2) (C a3) (C a4) (C a5) (C a6) (X : ℝ[X]) =
      X ^ 2 - C (5 * a2) * X ^ 4 - C (6 * a3) * X ^ 5 + C (7 * (4 * a2 ^ 2 - a4)) * X ^ 6
        + C (8 * (9 * a2 * a3 - a5)) * X ^ 7
        - C (3 * (55 * a2 ^ 3 - 30 * a2 * a4 - 15 * a3 ^ 2 + 3 * a6)) * X ^ 8 := by
  unfold dosRhs
  simp only [map_mul, map_sub, map_add, map_pow, C_ofNat]

theorem dos_coeffs (a2 a3 a4 a5 a6 : ℝ) :
    (dosPoly a2 a3 a4 a5 a6).coeff 2 = 1 ∧
    (dosPoly a2 a3 a4 a5 a6).coeff 3 = 0 ∧
    (dosPoly a2 a3 a4 a5 a6).coeff 4 = -5 * a2 ∧
    (dosPoly a2 a3 a4 a5 a6).coeff 5 = -6 * a3 ∧
    (dosPoly a2 a3 a4 a5 a6).coeff 6 = 7 * (4 * a2 ^ 2 - a4) ∧
    (dosPoly a2 a3 a4 a5 a6).coeff 7 = 8 * (9 * a2 * a3 - a5) ∧
    (dosPoly a2 a3 a4 a5 a6).coeff 8 = -3 * (55 * a2 ^ 3 - 30 * a2 * a4 - 15 * a3 ^ 2 + 3 * a6) := by
  -- work in the quotient ring ℝ[X] / (X^9), where `e = X` is nilpotent of order 9
  have h9 : (Ideal.Quotient.mk (Ideal.span {(X : ℝ[X]) ^ 9}) X) ^ 9 = 0 := by
    rw [← map_pow, Ideal.Quotient.eq_zero_iff_mem]
    exact Ideal.mem_span_singleton_self _
  have key := dos_eq (Ideal.Quotient.mk (Ideal.span {(X : ℝ[X]) ^ 9}) (C a2))
    (Ideal.Quotient.mk (Ideal.span {(X : ℝ[X]) ^ 9}) (C a3))
    (Ideal.Quotient.mk (Ideal.span {(X : ℝ[X]) ^ 9}) (C a4))
    (Ideal.Quotient.mk (Ideal.span {(X : ℝ[X]) ^ 9}) (C a5))
    (Ideal.Quotient.mk (Ideal.span {(X : ℝ[X]) ^ 9}) (C a6))
    (Ideal.Quotient.mk (Ideal.span {(X : ℝ[X]) ^ 9}) X) h9
  have hmk : Ideal.Quotient.mk (Ideal.span {(X : ℝ[X]) ^ 9}) (dosPoly a2 a3 a4 a5 a6)
      = Ideal.Quotient.mk (Ideal.span {(X : ℝ[X]) ^ 9}) (dosRhs (C a2) (C a3) (C a4) (C a5) (C a6) X) := by
    unfold dosPoly
    rw [derivative_kPoly, map_mul, map_pow]
    unfold kPoly
    rw [map_kInv0, map_kInv0Deriv, map_dosRhs]
    exact key
  have hd : (X : ℝ[X]) ^ 9 ∣ dosPoly a2 a3 a4 a5 a6 - dosRhs (C a2) (C a3) (C a4) (C a5) (C a6) X := by
    rw [← Ideal.mem_span_singleton]
    exact Ideal.Quotient.eq.mp hmk
  have hc : ∀ d < 9, (dosPoly a2 a3 a4 a5 a6).coeff d
      = (dosRhs (C a2) (C a3) (C a4) (C a5) (C a6) (X : ℝ[X])).coeff d := by
    intro d hd'
    have h0 := X_pow_dvd_iff.mp hd d hd'
    rw [coeff_sub, sub_eq_zero] at h0
    exact h0
  rw [hc 2 (by norm_num), hc 3 (by norm_num), hc 4 (by norm_num), hc 5 (by norm_num), hc 6 (by norm_num),
    hc 7 (by norm_num), hc 8 (by norm_num), dosRhs_poly]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;> simp only [coeff_sub, coeff_add, coeff_C_mul, coeff_X_pow] <;> norm_num


open QuantumFluids.PhononSpecificHeat QuantumFluids.BoseIntegral

/-- **Eq. (22) from the density-of-states polynomial.**  The same statement as `phonon_specific_heat`, but with the
brackets `g_n` *computed* as the coefficients of `k(e)^2 * k'(e)` instead of retyped. -/
theorem phonon_specific_heat_from_dos (V kB hbar c a2 a3 a4 a5 a6 z7 z9 T : ℝ) (hh : hbar ≠ 0) (hc0 : c ≠ 0) :
    HasDerivAt (fun T =>
        energyTerm V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 2) 2 (π ^ 4 / 15) T
      + energyTerm V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 4) 4 (8 * π ^ 6 / 63) T
      + energyTerm V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 5) 5 (720 * z7) T
      + energyTerm V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 6) 6 (8 * π ^ 8 / 15) T
      + energyTerm V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 7) 7 (40320 * z9) T
      + energyTerm V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 8) 8 (128 * π ^ 10 / 33) T)
      ( 2 * π ^ 2 * kB ^ 4 * V / (15 * c ^ 3 * hbar ^ 3) * T ^ 3
      + -(40 * (π ^ 4 * a2 * kB ^ 6 * V)) / (21 * (c ^ 5 * hbar ^ 5)) * T ^ 5
      + -(15120 * (a3 * kB ^ 7 * V * z7)) / (π ^ 2 * c ^ 6 * hbar ^ 6) * T ^ 6
      + 224 * π ^ 6 * kB ^ 8 * V * (4 * a2 ^ 2 - a4) / (15 * c ^ 7 * hbar ^ 7) * T ^ 7
      + 1451520 * kB ^ 9 * V * z9 * (9 * a2 * a3 - a5) / (π ^ 2 * c ^ 8 * hbar ^ 8) * T ^ 8
      + -(640 * (π ^ 8 * kB ^ 10 * V * (55 * a2 ^ 3 - 30 * a2 * a4 - 15 * a3 ^ 2 + 3 * a6)))
          / (11 * (c ^ 9 * hbar ^ 9)) * T ^ 9) T := by
  obtain ⟨g2, -, g4, g5, g6, g7, g8⟩ := dos_coeffs a2 a3 a4 a5 a6
  rw [g2, g4, g5, g6, g7, g8]
  exact phonon_specific_heat V kB hbar c a2 a3 a4 a5 a6 z7 z9 T hh hc0

/-- **Eq. (22), end to end.**  Nothing is retyped: the brackets are coefficients of `k^2 * k'`, and the six Bose
integrals are the real parts of the Mellin transforms `mellin bose 4, 6, 7, 8, 9, 10`; the two odd zeta values are
`ζ(7)` and `ζ(9)` themselves. -/
theorem phonon_specific_heat_end_to_end (V kB hbar c a2 a3 a4 a5 a6 T : ℝ) (hh : hbar ≠ 0) (hc0 : c ≠ 0) :
    HasDerivAt (fun T =>
        energyTerm V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 2) 2 (mellin bose 4).re T
      + energyTerm V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 4) 4 (mellin bose 6).re T
      + energyTerm V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 5) 5 (mellin bose 7).re T
      + energyTerm V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 6) 6 (mellin bose 8).re T
      + energyTerm V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 7) 7 (mellin bose 9).re T
      + energyTerm V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 8) 8 (mellin bose 10).re T)
      ( 2 * π ^ 2 * kB ^ 4 * V / (15 * c ^ 3 * hbar ^ 3) * T ^ 3
      + -(40 * (π ^ 4 * a2 * kB ^ 6 * V)) / (21 * (c ^ 5 * hbar ^ 5)) * T ^ 5
      + -(15120 * (a3 * kB ^ 7 * V * (riemannZeta 7).re)) / (π ^ 2 * c ^ 6 * hbar ^ 6) * T ^ 6
      + 224 * π ^ 6 * kB ^ 8 * V * (4 * a2 ^ 2 - a4) / (15 * c ^ 7 * hbar ^ 7) * T ^ 7
      + 1451520 * kB ^ 9 * V * (riemannZeta 9).re * (9 * a2 * a3 - a5) / (π ^ 2 * c ^ 8 * hbar ^ 8) * T ^ 8
      + -(640 * (π ^ 8 * kB ^ 10 * V * (55 * a2 ^ 3 - 30 * a2 * a4 - 15 * a3 ^ 2 + 3 * a6)))
          / (11 * (c ^ 9 * hbar ^ 9)) * T ^ 9) T := by
  obtain ⟨b4, b6, b7, b8, b9, b10⟩ := bose_integral_values
  have r4 : (mellin bose 4).re = π ^ 4 / 15 := by
    rw [b4]
    have h : ((π : ℂ) ^ 4 / 15) = ((π ^ 4 / 15 : ℝ) : ℂ) := by push_cast; ring
    rw [h, Complex.ofReal_re]
  have r6 : (mellin bose 6).re = 8 * π ^ 6 / 63 := by
    rw [b6]
    have h : (8 * (π : ℂ) ^ 6 / 63) = ((8 * π ^ 6 / 63 : ℝ) : ℂ) := by push_cast; ring
    rw [h, Complex.ofReal_re]
  have r7 : (mellin bose 7).re = 720 * (riemannZeta 7).re := by
    rw [b7]; simp
  have r8 : (mellin bose 8).re = 8 * π ^ 8 / 15 := by
    rw [b8]
    have h : (8 * (π : ℂ) ^ 8 / 15) = ((8 * π ^ 8 / 15 : ℝ) : ℂ) := by push_cast; ring
    rw [h, Complex.ofReal_re]
  have r9 : (mellin bose 9).re = 40320 * (riemannZeta 9).re := by
    rw [b9]; simp
  have r10 : (mellin bose 10).re = 128 * π ^ 10 / 33 := by
    rw [b10]
    have h : (128 * (π : ℂ) ^ 10 / 33) = ((128 * π ^ 10 / 33 : ℝ) : ℂ) := by push_cast; ring
    rw [h, Complex.ofReal_re]
  rw [r4, r6, r7, r8, r9, r10]
  exact phonon_specific_heat_from_dos V kB hbar c a2 a3 a4 a5 a6 (riemannZeta 7).re (riemannZeta 9).re T hh hc0


/-- The energy of the density-of-states monomial `g uⁿ` written as an integral:
`V/(2π²) · g · ħc · ∫₀^∞ u^(n+1) / (e^(β u) − 1) du` with `β = ħc / (k_B T)`, the integral being Mathlib's
Mellin transform of `u ↦ bose (β u)` at `n + 2`. -/
noncomputable def energyMonomial (V kB hbar c g : ℝ) (n : ℕ) (T : ℝ) : ℝ :=
  V / (2 * π ^ 2) * g * (hbar * c) *
    (mellin (fun u : ℝ => bose (hbar * c / (kB * T) * u)) ((n : ℂ) + 2)).re

theorem energyMonomial_eq (V kB hbar c g : ℝ) (n : ℕ) {T : ℝ} (hbc : 0 < hbar * c) (hkT : 0 < kB * T) :
    energyMonomial V kB hbar c g n T
      = energyTerm V kB hbar c g n (mellin bose ((n : ℂ) + 2)).re T := by
  have hh : hbar ≠ 0 := left_ne_zero_of_mul hbc.ne'
  have hc : c ≠ 0 := right_ne_zero_of_mul hbc.ne'
  have hk : kB ≠ 0 := left_ne_zero_of_mul hkT.ne'
  have hT : T ≠ 0 := right_ne_zero_of_mul hkT.ne'
  have hβ : 0 < hbar * c / (kB * T) := div_pos hbc hkT
  unfold energyMonomial energyTerm
  rw [mellin_comp_mul_left bose _ hβ, smul_eq_mul]
  have hexp : (-((n : ℂ) + 2)) = -(((n + 2 : ℕ) : ℂ)) := by push_cast; ring
  have hcpow : ((hbar * c / (kB * T) : ℝ) : ℂ) ^ (-((n : ℂ) + 2))
      = (((hbar * c / (kB * T)) ^ (n + 2))⁻¹ : ℝ) := by
    rw [hexp, Complex.cpow_neg, Complex.cpow_natCast]
    norm_cast
  have hq : ((hbar * c / (kB * T)) ^ (n + 2))⁻¹ = (kB * T) ^ (n + 2) / (hbar * c) ^ (n + 2) := by
    rw [div_pow, inv_div]
  have hbc' : hbar * c ≠ 0 := hbc.ne'
  have hp : π ≠ 0 := Real.pi_ne_zero
  rw [hcpow, Complex.re_ofReal_mul, hq]
  field_simp
  ring


/-- **Eq. (22) with the energy written as the integral.**  For `T > 0` the energy of each density-of-states monomial is
`energyMonomial` (Mathlib's Mellin transform of `u ↦ bose (β u)`), and the derivative of the sum is the six closed forms. -/
theorem phonon_specific_heat_integral (V kB hbar c a2 a3 a4 a5 a6 T : ℝ)
    (hh : 0 < hbar) (hc : 0 < c) (hk : 0 < kB) (hT : 0 < T) :
    HasDerivAt (fun T =>
        energyMonomial V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 2) 2 T
      + energyMonomial V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 4) 4 T
      + energyMonomial V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 5) 5 T
      + energyMonomial V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 6) 6 T
      + energyMonomial V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 7) 7 T
      + energyMonomial V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 8) 8 T)
      ( 2 * π ^ 2 * kB ^ 4 * V / (15 * c ^ 3 * hbar ^ 3) * T ^ 3
      + -(40 * (π ^ 4 * a2 * kB ^ 6 * V)) / (21 * (c ^ 5 * hbar ^ 5)) * T ^ 5
      + -(15120 * (a3 * kB ^ 7 * V * (riemannZeta 7).re)) / (π ^ 2 * c ^ 6 * hbar ^ 6) * T ^ 6
      + 224 * π ^ 6 * kB ^ 8 * V * (4 * a2 ^ 2 - a4) / (15 * c ^ 7 * hbar ^ 7) * T ^ 7
      + 1451520 * kB ^ 9 * V * (riemannZeta 9).re * (9 * a2 * a3 - a5) / (π ^ 2 * c ^ 8 * hbar ^ 8) * T ^ 8
      + -(640 * (π ^ 8 * kB ^ 10 * V * (55 * a2 ^ 3 - 30 * a2 * a4 - 15 * a3 ^ 2 + 3 * a6)))
          / (11 * (c ^ 9 * hbar ^ 9)) * T ^ 9) T := by
  have h := phonon_specific_heat_end_to_end V kB hbar c a2 a3 a4 a5 a6 T hh.ne' hc.ne'
  refine h.congr_of_eventuallyEq ?_
  filter_upwards [Ioi_mem_nhds hT] with t ht
  have ht' : 0 < t := ht
  have hbc : 0 < hbar * c := mul_pos hh hc
  have hkT : 0 < kB * t := mul_pos hk ht'
  have e2 := energyMonomial_eq V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 2) 2 hbc hkT
  have e4 := energyMonomial_eq V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 4) 4 hbc hkT
  have e5 := energyMonomial_eq V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 5) 5 hbc hkT
  have e6 := energyMonomial_eq V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 6) 6 hbc hkT
  have e7 := energyMonomial_eq V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 7) 7 hbc hkT
  have e8 := energyMonomial_eq V kB hbar c ((dosPoly a2 a3 a4 a5 a6).coeff 8) 8 hbc hkT
  norm_num at e2 e4 e5 e6 e7 e8
  rw [e2, e4, e5, e6, e7, e8]

end QuantumFluids.DosLink

-- axiom audit
#print axioms QuantumFluids.DosLink.kInv0_inverts
#print axioms QuantumFluids.DosLink.derivative_kPoly
#print axioms QuantumFluids.DosLink.dos_coeffs
#print axioms QuantumFluids.DosLink.phonon_specific_heat_from_dos
#print axioms QuantumFluids.DosLink.phonon_specific_heat_end_to_end
#print axioms QuantumFluids.DosLink.energyMonomial_eq
#print axioms QuantumFluids.DosLink.phonon_specific_heat_integral
