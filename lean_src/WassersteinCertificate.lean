/-
  WassersteinCertificate.lean -- P6 of the closed-loop project
  (docs/designs/CLOSED_LOOP_PREREG.md, docs/designs/CLOSED_LOOP_RESULTS.md).

  The certificate used in `exploration/tda/loop_certificate_*.py`: a perfect matching `σ` (an explicit
  bijection between an "augmented" row set and column set -- real diagram points plus, on each side, one
  dedicated diagonal-projection slot per point on the OTHER side, exactly the construction in
  `docs/designs/CLOSED_LOOP_PLAN.md` §1.4 and its Python recipe) together with dual potentials `u, v`
  satisfying the feasibility inequalities `u i + v j ≤ C i j` everywhere. This is finite linear-
  programming weak duality -- general over ANY cost matrix and ANY finite index types, S-difficulty --
  and it is exactly what makes such a certificate valid: if `σ`'s cost equals `Σu + Σv`, `σ` is provably
  an optimal (minimum-cost) matching, no search over the other `(n+m)!` matchings required.

  Applied here to the eight-point-cycle toy example (`CLOSED_LOOP_PREREG.md`'s C1, hand-verified there,
  machine-verified in `exploration/tda/loop_controls.py`, and now machine-CHECKED at the kernel level
  here): `card_toy_certificate` proves the found matching is optimal, at cost exactly `7/4`. The negative
  control instantiates the broken potential from C3 (`ψ_{c'} = 1/2` instead of `1/4`) and shows it is NOT
  feasible, so it certifies nothing.

  NOT covered: the seven real Gross-Pitaevskii persistence-diagram pairs of `CLOSED_LOOP_RESULTS.md` use
  60×60 floating-point cost matrices built from real simulation data. Re-verifying those specific
  matrices inside the Lean kernel is not attempted here (their optimality was independently confirmed in
  Python by two solvers, `scipy.optimize.linear_sum_assignment` and `scipy.optimize.linprog`, agreeing to
  machine precision -- see that file). What is proved here is the general theorem that makes any such
  certificate valid in principle, checked on the one instance small and exact enough to write down by
  hand and decide in the kernel.
-/
import Mathlib

open Finset

namespace QuantumFluids.WassersteinCertificate

/-! ### The general certificate: finite LP weak duality for an assignment problem -/

variable {ι κ : Type*} [Fintype ι] [Fintype κ]

/-- **Weak duality.** For any cost `C`, any perfect matching `σ : ι ≃ κ`, and any potentials `u, v`
satisfying the feasibility inequalities everywhere, `Σu + Σv` is a lower bound for `σ`'s cost. -/
theorem weak_duality (C : ι → κ → ℝ) (u : ι → ℝ) (v : κ → ℝ)
    (hfeas : ∀ i j, u i + v j ≤ C i j) (σ : ι ≃ κ) :
    ∑ i, u i + ∑ j, v j ≤ ∑ i, C i (σ i) := by
  have hv : ∑ j, v j = ∑ i, v (σ i) :=
    (Fintype.sum_equiv σ (fun i => v (σ i)) v (fun _ => rfl)).symm
  rw [hv, ← sum_add_distrib]
  exact sum_le_sum fun i _ => hfeas i (σ i)

/-- **The certificate.** If in addition `σ`'s cost equals `Σu + Σv`, `σ` is an optimal (minimum-cost)
perfect matching: no other bijection does better. A matching plus a feasible, tight pair of potentials
proves optimality without searching the other matchings. -/
theorem certificate (C : ι → κ → ℝ) (u : ι → ℝ) (v : κ → ℝ)
    (hfeas : ∀ i j, u i + v j ≤ C i j) (σ : ι ≃ κ)
    (htight : ∑ i, C i (σ i) = ∑ i, u i + ∑ j, v j) (τ : ι ≃ κ) :
    ∑ i, C i (σ i) ≤ ∑ i, C i (τ i) := by
  rw [htight]; exact weak_duality C u v hfeas τ

/-! ### Instantiated on the toy example of `CLOSED_LOOP_PREREG.md` C1
(Flattened into this same namespace, not a sub-namespace `ToyExample`: `scripts/regen_axiom_audit.py`
only reads a file's FIRST `namespace` line, the same limitation documented in `Villani.lean`.) -/

/-- Row/column 0,1,2 are the real points `a,b,c` / `a',b',c'`; 3,4,5 are each side's dedicated
diagonal-projection slot for the OTHER side's point of the same offset (row 3 = "`a'`'s diagonal slot",
etc.), exactly `exploration/tda/loop_certificate_R1.py`'s `build_cost_matrix`. `1000` stands in for the
`1e9` cross-use penalty: it is never approached by any feasible potential below. -/
noncomputable def C : Fin 6 → Fin 6 → ℝ :=
  ![![0, 1, 2, 3/2, 1000, 1000],
    ![1, 0, 3/2, 1000, 3/2, 1000],
    ![2, 1, 5/2, 1000, 1000, 3/2],
    ![3/2, 1000, 1000, 0, 0, 0],
    ![1000, 3/2, 1000, 0, 0, 0],
    ![1000, 1000, 1/4, 0, 0, 0]]

theorem C_eq (i j : Fin 6) : C i j = ![![0, 1, 2, 3/2, 1000, 1000],
    ![1, 0, 3/2, 1000, 3/2, 1000],
    ![2, 1, 5/2, 1000, 1000, 3/2],
    ![3/2, 1000, 1000, 0, 0, 0],
    ![1000, 3/2, 1000, 0, 0, 0],
    ![1000, 1000, 1/4, 0, 0, 0]] i j := rfl

/-- The dual potentials found by `exploration/tda/loop_certificate_R1.py`'s solver, re-derived here
as exact rationals and verified by `decide` below: `u 0..2 = φ_a,φ_b,φ_c` from
`docs/designs/CLOSED_LOOP_PREREG.md`'s C1 (`0, 1/2, 3/2`); `u 3..5 = 0` (the unused dummy-row slack). -/
noncomputable def u : Fin 6 → ℝ := ![0, 1/2, 3/2, 0, 0, 0]

/-- `v 0..2 = ψ_a',ψ_b',ψ_c'` from the same C1 (`0, -1/2, 1/4`); `v 3..5 = 0`. -/
noncomputable def v : Fin 6 → ℝ := ![0, -1/2, 1/4, 0, 0, 0]

/-- The matching found in `loop_certificate_R1.py`'s style: `a↔a'`, `b↔b'`, `c→Δ` (its own diagonal
slot, row 2 ↦ col 5), `c'→Δ` (row 5 ↦ col 2), the two remaining dummy rows to the two remaining dummy
columns (cost 0 either way). -/
def σfun : Fin 6 → Fin 6 := ![0, 1, 5, 3, 4, 2]

/-- The certified optimal matching, as an `Equiv`. Its bijectivity proof is inlined (not a separate
named theorem) so that `def σ` does not depend on a declaration the axiom-audit script would not know
to keep in a `sorry`-substituted challenge file (only `theorem`/`lemma` declarations are audited; a
`def` that names a helper theorem not itself on the audit list breaks when that theorem is dropped as
"unlisted" -- found and fixed while wiring this file into Comparator). -/
noncomputable def σ : Fin 6 ≃ Fin 6 := Equiv.ofBijective σfun (by decide)

theorem feasible : ∀ i j, u i + v j ≤ C i j := by
  intro i j; fin_cases i <;> fin_cases j <;> simp [C, u, v] <;> norm_num

theorem tight : ∑ i, C i (σ i) = ∑ i, u i + ∑ j, v j := by
  simp [Fin.sum_univ_succ, C, u, v, σ, Equiv.ofBijective, σfun]
  norm_num

/-- **The toy example is certified: `σ` (`a↔a'`, `b↔b'`, `c,c'→Δ`) is an OPTIMAL matching, of cost
exactly `7/4`** -- matching `docs/designs/CLOSED_LOOP_PREREG.md`'s hand-verified C1 and
`exploration/tda/loop_controls.py`'s machine-verified run, now checked by the Lean kernel. -/
theorem toy_certificate (τ : Fin 6 ≃ Fin 6) : ∑ i, C i (σ i) ≤ ∑ i, C i (τ i) :=
  certificate C u v feasible σ tight τ

theorem toy_cost_eq : ∑ i, C i (σ i) = 7 / 4 := by
  simp [Fin.sum_univ_succ, C, σ, Equiv.ofBijective, σfun]
  norm_num

/-! ### The negative control: C3's broken potential is infeasible -/

/-- `ψ_{c'} = 1/2` instead of `1/4` -- the broken potential of C1's negative control C3. -/
noncomputable def v_broken : Fin 6 → ℝ := ![0, -1/2, 1/2, 0, 0, 0]

/-- **C3 rejected**: the broken potential is not feasible, so `certificate` cannot be invoked with it
-- it proves nothing, exactly as `loop_controls.py`'s independent checker found (`ψ_c' = 0.5 > cost(c',
Δ) = 0.25`, i.e. row 5, column 2 here: `u 5 + v_broken 2 = 0 + 1/2 = 1/2 > 1/4 = C 5 2`). -/
theorem broken_infeasible : ¬ (∀ i j, u i + v_broken j ≤ C i j) := by
  intro h
  have := h 5 2
  simp [C, u, v_broken] at this
  norm_num at this

end QuantumFluids.WassersteinCertificate

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.WassersteinCertificate.weak_duality
#print axioms QuantumFluids.WassersteinCertificate.certificate
#print axioms QuantumFluids.WassersteinCertificate.C_eq
#print axioms QuantumFluids.WassersteinCertificate.feasible
#print axioms QuantumFluids.WassersteinCertificate.tight
#print axioms QuantumFluids.WassersteinCertificate.toy_certificate
#print axioms QuantumFluids.WassersteinCertificate.toy_cost_eq
#print axioms QuantumFluids.WassersteinCertificate.broken_infeasible
