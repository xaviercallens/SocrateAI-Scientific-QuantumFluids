/-
  Ch04_NegativeControl_L54.lean
  This file is MEANT TO FAIL.  It is a negative control quoted in Chapter 4 of the book "Quantum Fluids in Lean 4: a tribute to Henri Godfrin":
  a proof checker that cannot reject a wrong statement proves nothing.  Please exclude it from audits of theorem files.
  It imports a library module (compiled from lean_src/ into an .olean file placed on LEAN_PATH, as for Ch04_DosLink.lean) and states one
  of its theorems with a single integer changed.

  Here: `PhononSeries.density_of_states` with the integer 55 of the bracket of g_8 replaced by 54, proved with the certificate of the true theorem.
  Expected result (exit code 1): `ring failed, ring expressions not equal`, with the residue  -(a2 ^ 3 * e ^ 8 * 3) = 0
  (the quoted error is in book/figures/ch04_negctl_L54.txt).
-/
import PhononSeries

namespace QuantumFluids.PhononSeries

variable {R : Type*} [CommRing R]

/-- NEGATIVE CONTROL (must fail): `density_of_states` with `55` replaced by `54` in the bracket of `g_8`. -/
theorem density_of_states_L54 (a2 a3 a4 a5 a6 e : R) (h : e ^ 9 = 0) :
    kInv0 a2 a3 a4 a5 a6 e ^ 2 * kInv0Deriv a2 a3 a4 a5 a6 e
      = e ^ 2 - 5 * a2 * e ^ 4 - 6 * a3 * e ^ 5 + 7 * (4 * a2 ^ 2 - a4) * e ^ 6
        + 8 * (9 * a2 * a3 - a5) * e ^ 7
        - 3 * (54 * a2 ^ 3 - 30 * a2 * a4 - 15 * a3 ^ 2 + 3 * a6) * e ^ 8 := by
  rw [kSq0_eq a2 a3 a4 a5 a6 e h]
  unfold kSq0 kInv0Deriv
  linear_combination (2520*a2^6*e^5 - 1038*a2^5*e^3 - 2604*a2^4*a3*e^4 - 3192*a2^4*a4*e^5 + 363*a2^4*e - 1596*a2^3*a3^2*e^5 + 822*a2^3*a3*e^2 + 980*a2^3*a4*e^3 + 348*a2^3*a5*e^4 + 378*a2^3*a6*e^5 + 1003*a2^2*a3^2*e^3 + 1652*a2^2*a3*a4*e^4 - 190*a2^2*a3 + 1008*a2^2*a4^2*e^5 - 231*a2^2*a4*e - 72*a2^2*a5*e^2 - 79*a2^2*a6*e^3 + 826*a2*a3^3*e^4 + 1008*a2*a3^2*a4*e^5 - 231*a2*a3^2*e - 348*a2*a3*a4*e^2 - 180*a2*a3*a5*e^3 - 196*a2*a3*a6*e^4 - 202*a2*a4^2*e^3 - 220*a2*a4*a5*e^4 - 238*a2*a4*a6*e^5 + 18*a2*a5 + 20*a2*a6*e + 252*a3^4*e^5 - 92*a3^3*e^2 - 101*a3^2*a4*e^3 - 110*a3^2*a5*e^4 - 119*a3^2*a6*e^5 + 18*a3*a4 + 20*a3*a5*e + 22*a3*a6*e^2 + 10*a4^2*e + 22*a4*a5*e^2 + 24*a4*a6*e^3 + 12*a5^2*e^3 + 26*a5*a6*e^4 + 14*a6^2*e^5) * h

end QuantumFluids.PhononSeries
