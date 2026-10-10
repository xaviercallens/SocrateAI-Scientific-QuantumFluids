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


/-! ## Book audit (appended by book/facts/lean_audit.py to a scratch copy; not part of the library) -/
open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let locals := env.checked.get.constants.foldStage2
    (fun (acc : Array (Name × ConstantInfo)) n ci => acc.push (n, ci)) #[]
  let userName (n : Name) : Name := (privateToUserName? n).getD n
  let isNamed (n : Name) : Bool := !(userName n).isInternal
  let namedThms := locals.filter (fun (n, ci) => ci.isTheorem && isNamed n)
  let namedDefs := locals.filter (fun (n, ci) => (ci matches .defnInfo _) && isNamed n)
  let axDecls := locals.filter (fun (_, ci) => ci matches .axiomInfo _)
  let thmNames : NameSet := namedThms.foldl (fun s (n, _) => s.insert n) {}
  let mut union : NameSet := {}
  let mut rows : Array String := #[]
  for (n, _) in locals do
    let axs ← collectAxioms n
    for a in axs do union := union.insert a
    if thmNames.contains n then
      let line ← match (← findDeclarationRanges? n) with
        | some r => pure (toString r.range.pos.line)
        | none => pure "-1"
      rows := rows.push s!"QFAUDIT|THM|{userName n}|{line}|{", ".intercalate (axs.toList.map toString)}"
  IO.println s!"QFAUDIT|SUMMARY|{locals.size}|{namedThms.size}|{namedDefs.size}|{axDecls.size}|{union.contains ``sorryAx}|{", ".intercalate (union.toList.map toString)}"
  for (n, _) in axDecls do IO.println s!"QFAUDIT|AXIOMDECL|{n}"
  for r in rows do IO.println r
