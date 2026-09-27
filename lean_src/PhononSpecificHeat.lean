/-
  PhononSpecificHeat.lean -- assembling the phonon specific-heat series of
  Godfrin et al., PRB 103, 104516 (2021), Eq. (22):

      C_V = A T^3 + C T^5 + D T^6 + E T^7 + K T^8 + L T^9        (alpha_1 = 0)

  Three ingredients, each proved elsewhere or here:
    1. the density of states  k^2 dk/du = sum_n g_n u^n  modulo u^9      (`PhononSeries.density_of_states`);
    2. the thermal integral   int_0^inf u^n / (exp(beta u) - 1) du = beta^-(n+1) n! zeta(n+1)
                                                                        (`thermal_bose_integral`, from
                                                                         `BoseIntegral.bose_integral_nat`);
    3. zeta(6), zeta(8), zeta(10) in closed form (Bernoulli numbers B6, B8, B10 evaluated here);
       zeta(7) and zeta(9) have no known closed form and stay symbolic -- which is WHY the paper's D and K
       carry an explicit zeta while A, C, E, L carry powers of pi.

  RESULT (`phonon_specific_heat`): the derivative of the term-by-term energy is exactly the six printed
  closed forms. All six printed coefficients are CONFIRMED; no discrepancy was found.

  NOT proved: that this term-by-term series is an asymptotic expansion of the specific heat computed from the
  full measured dispersion curve (upper limit -> infinity, roton branch neglected). That is an analytic
  statement about a measured function and is outside what a proof assistant can certify.
-/
import BoseIntegral
import PhononSeries

open Real

namespace QuantumFluids.PhononSpecificHeat

open QuantumFluids.BoseIntegral

/-! ### Bernoulli numbers beyond Mathlib's table (which stops at `bernoulli'_four`) -/

theorem bernoulli'_five : bernoulli' 5 = 0 := by
  rw [bernoulli'_def]
  norm_num [Finset.sum_range_succ, Nat.choose, bernoulli'_zero, bernoulli'_one, bernoulli'_two,
    bernoulli'_three, bernoulli'_four]

theorem bernoulli'_six : bernoulli' 6 = 1 / 42 := by
  rw [bernoulli'_def]
  norm_num [Finset.sum_range_succ, Nat.choose, bernoulli'_zero, bernoulli'_one, bernoulli'_two,
    bernoulli'_three, bernoulli'_four, bernoulli'_five]

theorem bernoulli'_seven : bernoulli' 7 = 0 := by
  rw [bernoulli'_def]
  norm_num [Finset.sum_range_succ, Nat.choose, bernoulli'_zero, bernoulli'_one, bernoulli'_two,
    bernoulli'_three, bernoulli'_four, bernoulli'_five, bernoulli'_six]

theorem bernoulli'_eight : bernoulli' 8 = -1 / 30 := by
  rw [bernoulli'_def]
  norm_num [Finset.sum_range_succ, Nat.choose, bernoulli'_zero, bernoulli'_one, bernoulli'_two,
    bernoulli'_three, bernoulli'_four, bernoulli'_five, bernoulli'_six, bernoulli'_seven]

theorem bernoulli'_nine : bernoulli' 9 = 0 := by
  rw [bernoulli'_def]
  norm_num [Finset.sum_range_succ, Nat.choose, bernoulli'_zero, bernoulli'_one, bernoulli'_two,
    bernoulli'_three, bernoulli'_four, bernoulli'_five, bernoulli'_six, bernoulli'_seven,
    bernoulli'_eight]

theorem bernoulli'_ten : bernoulli' 10 = 5 / 66 := by
  rw [bernoulli'_def]
  norm_num [Finset.sum_range_succ, Nat.choose, bernoulli'_zero, bernoulli'_one, bernoulli'_two,
    bernoulli'_three, bernoulli'_four, bernoulli'_five, bernoulli'_six, bernoulli'_seven,
    bernoulli'_eight, bernoulli'_nine]

/-! ### Even zeta values -/

theorem riemannZeta_six : riemannZeta 6 = (π : ℂ) ^ 6 / 945 := by
  have h := riemannZeta_two_mul_nat (k := 3) (by norm_num)
  rw [bernoulli_eq_bernoulli'_of_ne_one (by norm_num), show 2 * 3 = 6 from rfl, bernoulli'_six] at h
  rw [show (6 : ℂ) = 2 * ((3 : ℕ) : ℂ) by norm_num, h]
  norm_num [Nat.factorial]
  ring

theorem riemannZeta_eight : riemannZeta 8 = (π : ℂ) ^ 8 / 9450 := by
  have h := riemannZeta_two_mul_nat (k := 4) (by norm_num)
  rw [bernoulli_eq_bernoulli'_of_ne_one (by norm_num), show 2 * 4 = 8 from rfl, bernoulli'_eight] at h
  rw [show (8 : ℂ) = 2 * ((4 : ℕ) : ℂ) by norm_num, h]
  norm_num [Nat.factorial]
  ring

theorem riemannZeta_ten : riemannZeta 10 = (π : ℂ) ^ 10 / 93555 := by
  have h := riemannZeta_two_mul_nat (k := 5) (by norm_num)
  rw [bernoulli_eq_bernoulli'_of_ne_one (by norm_num), show 2 * 5 = 10 from rfl, bernoulli'_ten] at h
  rw [show (10 : ℂ) = 2 * ((5 : ℕ) : ℂ) by norm_num, h]
  norm_num [Nat.factorial]
  ring

/-! ### The thermal integral at inverse temperature `β = ħc / k_B T` -/

/-- `∫₀^∞ uⁿ / (exp (β u) - 1) du = β^{-(n+1)} · n! · ζ(n+1)`. -/
theorem thermal_bose_integral {n : ℕ} (hn : 1 ≤ n) {β : ℝ} (hβ : 0 < β) :
    mellin (fun u => bose (β * u)) (n + 1)
      = (β : ℂ) ^ (-((n : ℂ) + 1)) * ((Nat.factorial n : ℂ) * riemannZeta (n + 1)) := by
  rw [mellin_comp_mul_left bose _ hβ, bose_integral_nat hn, smul_eq_mul]

/-- The six dimensionless integrals `∫₀^∞ t^{n+1}/(eᵗ-1) dt` that enter Eq. (22). -/
theorem bose_integral_values :
    mellin bose 4 = (π : ℂ) ^ 4 / 15 ∧ mellin bose 6 = 8 * (π : ℂ) ^ 6 / 63 ∧
    mellin bose 7 = 720 * riemannZeta 7 ∧ mellin bose 8 = 8 * (π : ℂ) ^ 8 / 15 ∧
    mellin bose 9 = 40320 * riemannZeta 9 ∧ mellin bose 10 = 128 * (π : ℂ) ^ 10 / 33 := by
  refine ⟨mellin_bose_four, ?_, ?_, ?_, ?_, ?_⟩
  · have h := bose_integral_nat (n := 5) (by norm_num)
    rw [show ((5 : ℕ) : ℂ) + 1 = 6 by norm_num, riemannZeta_six] at h
    rw [h]; norm_num [Nat.factorial]; ring
  · have h := bose_integral_nat (n := 6) (by norm_num)
    rw [show ((6 : ℕ) : ℂ) + 1 = 7 by norm_num] at h
    rw [h]; norm_num [Nat.factorial]
  · have h := bose_integral_nat (n := 7) (by norm_num)
    rw [show ((7 : ℕ) : ℂ) + 1 = 8 by norm_num, riemannZeta_eight] at h
    rw [h]; norm_num [Nat.factorial]; ring
  · have h := bose_integral_nat (n := 8) (by norm_num)
    rw [show ((8 : ℕ) : ℂ) + 1 = 9 by norm_num] at h
    rw [h]; norm_num [Nat.factorial]
  · have h := bose_integral_nat (n := 9) (by norm_num)
    rw [show ((9 : ℕ) : ℂ) + 1 = 10 by norm_num, riemannZeta_ten] at h
    rw [h]; norm_num [Nat.factorial]; ring

/-! ### Energy and specific heat, term by term -/

/-- Energy carried by the density-of-states monomial `g uⁿ`:
`V/(2π²) · ħc · g · (k_B T/ħc)^{n+2} · I`, with `I = ∫₀^∞ t^{n+1}/(eᵗ-1) dt`.
For `n = 2`, `g = 1` this is `BoseIntegral.debyeEnergy`. -/
noncomputable def energyTerm (V kB hbar c g : ℝ) (n : ℕ) (I T : ℝ) : ℝ :=
  V / (2 * π ^ 2) * g * I * kB ^ (n + 2) / (hbar * c) ^ (n + 1) * T ^ (n + 2)

theorem energyTerm_two (V kB hbar c I T : ℝ) :
    energyTerm V kB hbar c 1 2 I T = debyeEnergy V kB hbar c I T := by
  unfold energyTerm debyeEnergy; ring

theorem energyTerm_hasDerivAt (V kB hbar c g : ℝ) (n : ℕ) (I T : ℝ) :
    HasDerivAt (fun T => energyTerm V kB hbar c g n I T)
      (V / (2 * π ^ 2) * g * I * kB ^ (n + 2) / (hbar * c) ^ (n + 1) * ((n + 2 : ℕ) * T ^ (n + 1))) T := by
  unfold energyTerm
  exact (hasDerivAt_pow (n + 2) T).const_mul _

/-- **Eq. (22) of Godfrin et al., all six coefficients.** `z7`, `z9` stand for `ζ(7)`, `ζ(9)`
(see `bose_integral_values`); the brackets are those of `PhononSeries.density_of_states`. -/
theorem phonon_specific_heat (V kB hbar c a2 a3 a4 a5 a6 z7 z9 T : ℝ) (hh : hbar ≠ 0) (hc : c ≠ 0) :
    HasDerivAt (fun T =>
        energyTerm V kB hbar c 1 2 (π ^ 4 / 15) T
      + energyTerm V kB hbar c (-5 * a2) 4 (8 * π ^ 6 / 63) T
      + energyTerm V kB hbar c (-6 * a3) 5 (720 * z7) T
      + energyTerm V kB hbar c (7 * (4 * a2 ^ 2 - a4)) 6 (8 * π ^ 8 / 15) T
      + energyTerm V kB hbar c (8 * (9 * a2 * a3 - a5)) 7 (40320 * z9) T
      + energyTerm V kB hbar c (-3 * (55 * a2 ^ 3 - 30 * a2 * a4 - 15 * a3 ^ 2 + 3 * a6)) 8
          (128 * π ^ 10 / 33) T)
      ( 2 * π ^ 2 * kB ^ 4 * V / (15 * c ^ 3 * hbar ^ 3) * T ^ 3
      + -(40 * (π ^ 4 * a2 * kB ^ 6 * V)) / (21 * (c ^ 5 * hbar ^ 5)) * T ^ 5
      + -(15120 * (a3 * kB ^ 7 * V * z7)) / (π ^ 2 * c ^ 6 * hbar ^ 6) * T ^ 6
      + 224 * π ^ 6 * kB ^ 8 * V * (4 * a2 ^ 2 - a4) / (15 * c ^ 7 * hbar ^ 7) * T ^ 7
      + 1451520 * kB ^ 9 * V * z9 * (9 * a2 * a3 - a5) / (π ^ 2 * c ^ 8 * hbar ^ 8) * T ^ 8
      + -(640 * (π ^ 8 * kB ^ 10 * V * (55 * a2 ^ 3 - 30 * a2 * a4 - 15 * a3 ^ 2 + 3 * a6)))
          / (11 * (c ^ 9 * hbar ^ 9)) * T ^ 9) T := by
  have h := ((((((energyTerm_hasDerivAt V kB hbar c 1 2 (π ^ 4 / 15) T).add
    (energyTerm_hasDerivAt V kB hbar c (-5 * a2) 4 (8 * π ^ 6 / 63) T)).add
    (energyTerm_hasDerivAt V kB hbar c (-6 * a3) 5 (720 * z7) T)).add
    (energyTerm_hasDerivAt V kB hbar c (7 * (4 * a2 ^ 2 - a4)) 6 (8 * π ^ 8 / 15) T)).add
    (energyTerm_hasDerivAt V kB hbar c (8 * (9 * a2 * a3 - a5)) 7 (40320 * z9) T)).add
    (energyTerm_hasDerivAt V kB hbar c
      (-3 * (55 * a2 ^ 3 - 30 * a2 * a4 - 15 * a3 ^ 2 + 3 * a6)) 8 (128 * π ^ 10 / 33) T))
  refine h.congr_deriv ?_
  have hp : π ≠ 0 := Real.pi_ne_zero
  push_cast
  field_simp
  ring

end QuantumFluids.PhononSpecificHeat

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.PhononSpecificHeat.bernoulli'_five
#print axioms QuantumFluids.PhononSpecificHeat.bernoulli'_six
#print axioms QuantumFluids.PhononSpecificHeat.bernoulli'_seven
#print axioms QuantumFluids.PhononSpecificHeat.bernoulli'_eight
#print axioms QuantumFluids.PhononSpecificHeat.bernoulli'_nine
#print axioms QuantumFluids.PhononSpecificHeat.bernoulli'_ten
#print axioms QuantumFluids.PhononSpecificHeat.riemannZeta_six
#print axioms QuantumFluids.PhononSpecificHeat.riemannZeta_eight
#print axioms QuantumFluids.PhononSpecificHeat.riemannZeta_ten
#print axioms QuantumFluids.PhononSpecificHeat.thermal_bose_integral
#print axioms QuantumFluids.PhononSpecificHeat.bose_integral_values
#print axioms QuantumFluids.PhononSpecificHeat.energyTerm_two
#print axioms QuantumFluids.PhononSpecificHeat.energyTerm_hasDerivAt
#print axioms QuantumFluids.PhononSpecificHeat.phonon_specific_heat
