/-
  Ch04_NegativeControl_D15121.lean
  This file is MEANT TO FAIL.  It is a negative control quoted in Chapter 4 of the book "Quantum Fluids in Lean 4: a tribute to Henri Godfrin":
  a proof checker that cannot reject a wrong statement proves nothing.  Please exclude it from audits of theorem files.
  It imports a library module (compiled from lean_src/ into an .olean file placed on LEAN_PATH, as for Ch04_DosLink.lean) and states one
  of its theorems with a single integer changed.

  Here: `PhononSpecificHeat.phonon_specific_heat` with the integer 15120 of the coefficient D replaced by 15121, proved by the proof of the true theorem.
  Expected result (exit code 1): `unsolved goals` after `field_simp` and `ring` (a polynomial identity in V, kB, T, hbar, c, pi, a2..a6, z7, z9 that
  does not hold; the first line of the error is in book/figures/ch04_negctl_D15121.txt).
-/
import PhononSpecificHeat

open Real
namespace QuantumFluids.PhononSpecificHeat

/-- NEGATIVE CONTROL (must fail): the capstone with the integer 15120 of the coefficient D replaced by 15121. -/
theorem phonon_specific_heat_D15121 (V kB hbar c a2 a3 a4 a5 a6 z7 z9 T : ℝ) (hh : hbar ≠ 0) (hc : c ≠ 0) :
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
      + -(15121 * (a3 * kB ^ 7 * V * z7)) / (π ^ 2 * c ^ 6 * hbar ^ 6) * T ^ 6
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
