/-
  Ch02_Primer.lean -- NEW Lean written for Chapter 2 of the book "Quantum Fluids in Lean 4"
  (not part of the QuantumFluids library; compiled against the pinned Mathlib, see the chapter report).

  (1) types, propositions and proofs in four lines;
  (2) Lean also runs programs: a computation on `Float` and a theorem about `ℝ` are different things;
  (3) `linear_combination` checks a certificate in a ring with a nilpotent element -- the pattern that the
      generated certificates of `QuantumFluids.PhononSeries` use at scale.
-/
import Mathlib

namespace QuantumFluids.Ch02Primer

/-! ## 1. Types, propositions, proofs -/

#check (2 : ℕ)
#check (2 + 2 = 4)
example : 2 + 2 = 4 := rfl

/-- A proposition is a type; a proof is an element of it. -/
theorem and_swap' (p q : Prop) (hp : p) (hq : q) : q ∧ p := ⟨hq, hp⟩

/-- The same kind of fact about real numbers, closed by a decision procedure for arithmetic. -/
theorem two_add_two : (2 : ℝ) + 2 = 4 := by norm_num

/-! ## 2. Programs and theorems -/

#eval (List.range 6).map (fun n => n ^ 2)
#eval (0.1 + 0.2 : Float)
#eval ((0.1 + 0.2 : Float) == 0.3)

/-- On the real numbers the same sum is exact. -/
theorem tenth_plus_fifth : (1 / 10 + 2 / 10 : ℝ) = 3 / 10 := by norm_num

/-! ## 3. A tactic that checks a certificate -/

/-- In any commutative ring with `e ^ 2 = 0`, `1 + e` is a unit with inverse `1 - e`.
`linear_combination (-1) * h` tells Lean: the goal minus (-1) times the hypothesis is a ring identity. -/
theorem one_add_nilpotent_inv {R : Type*} [CommRing R] (e : R) (h : e ^ 2 = 0) :
    (1 + e) * (1 - e) = 1 := by
  linear_combination (-1 : R) * h

end QuantumFluids.Ch02Primer

#print axioms QuantumFluids.Ch02Primer.and_swap'
#print axioms QuantumFluids.Ch02Primer.two_add_two
#print axioms QuantumFluids.Ch02Primer.tenth_plus_fifth
#print axioms QuantumFluids.Ch02Primer.one_add_nilpotent_inv
