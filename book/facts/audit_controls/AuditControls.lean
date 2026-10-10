/- AuditControls.lean -- planted defects for the negative control of the book's axiom auditor (facts/lean_audit.py).
   NOT a book module and NOT part of the library: it contains a `sorry` and an axiom ON PURPOSE, so that the auditor can be seen to catch them.
   Run by:  python3 book/facts/lean_audit.py --controls   (needs only `import Lean`, a few seconds). -/
import Lean

namespace Controls

theorem clean (a b : Nat) : a + b = b + a := by omega                      -- `omega`: only the standard axioms
theorem uses_propext (p q : Prop) (h : p ↔ q) : p = q := propext h         -- propext
theorem uses_classical (p : Prop) : p ∨ ¬ p := Classical.em p               -- the three standard axioms
theorem planted_sorry : (1 : Nat) = 2 := sorry                             -- a hole shipped as a theorem
theorem inherits_sorry : (1 : Nat) + 0 = 2 := by simpa using planted_sorry -- a clean-looking proof that depends on the hole
axiom planted_axiom : (2 : Nat) = 3                                        -- an axiom declared by the module itself
theorem uses_planted_axiom : (2 : Nat) = 3 := planted_axiom
theorem by_native_decide : 123456 * 654321 = 80779853376 := by native_decide  -- the compiler is trusted: Lean.ofReduceBool
private theorem hidden_sorry : (3 : Nat) = 4 := sorry                       -- private declarations are not invisible to the auditor

end Controls
