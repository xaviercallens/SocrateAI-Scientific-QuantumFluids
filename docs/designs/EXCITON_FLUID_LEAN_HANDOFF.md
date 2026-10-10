# Handoff: Lean 4 work for the exciton-fluid study (for the LeanMaster / AutoevolveAI session)

Status: brief, 2026-10-10. Written in the QuantumFluids repo (`docs/designs/EXCITON_FLUID_LEAN_HANDOFF.md`) for the
session that produced `contrib/openai_math_corollaries/` (LeanMaster v3.48.0). It is self-contained. The reasons for
every item are in `docs/designs/EXCITON_FLUID_LEAN_SOLVER_PLAN.md` (the plan); read its §3.2–3.4 first.

**Who does what.** QuantumFluids (physics, rusty-SUNDIALS solver, book) is on one machine with a tight root disk;
you have the pinned upstream stack (Lean 4.34.1, Mathlib `d13f23b7`, openai/math `adc7f124`, unchanged at `fd4aeeb2`).
Lean work that needs upstream definitions belongs to you; QuantumFluids consumes the statements verbatim and the
results as JSON. Producer ≠ verifier applies, as in your contribution.

**Not asked of you:** any claim about the physics; any outreach; a merge into LeanMaster's own library; Tier A labels
(the contribution stays "external, separate toolchain, conditional on upstream").

---

## 1. What already exists, proved elsewhere (verify it, do not trust it)

Written and compiled by the session that wrote the plan, in the **QuantumFluids pin** (Lean 4.34.0-rc2, Mathlib
`85e3a25`), `#print axioms` ⊆ {propext, Classical.choice, Quot.sound}, no `sorry`, one negative control that fails as
intended. **Producer: that session. Verifier: you.** Files (sha256 in the QuantumFluids repo at the commit that adds
this brief):

| file (`exploration/exciton/lean/`) | content |
|---|---|
| `ExcitonX1.lean` | `antitone_signed_iteratedDeriv`; **`admissible_sub_shift`** (g admissible, c > 0 ⇒ `t ↦ g t − g (t + c)` admissible); `admissible_const_mul`; `bilayerDipole_admissible` (given `riesz 1` admissible); `gem4_not_admissible` (`exp (−t²)`, negative control). Uses a local verbatim copy of `AdmissiblePotential`. |
| `FourFlavour.lean` | the four-flavour model of Qi et al. (Nature 654, 2026), Eqs. 2–3, as a quadratic energy on four non-negative densities; `support_in_one_pair` (T1), `intravalley_polarisation`, `IIA_polarisation`, `IIB_polarisation`, `intravalley_density` (T2, T3), `grand_potential_gap`, `critical_field` (T5), `single_component_of_neg_gX` (T6). Mathlib-only. |
| `FourFlavourNegativeControl.lean` | `IIA_polarisation_wrong_sign`: **meant to fail** (`ring` leaves `−g_c` against `+g_c`). |

Mathlib naming churn I met: `ENat.natCast_lt_top` (here) vs `ENat.coe_lt_top` (other versions); `push_neg` is deprecated
in favour of `push Not` in the QuantumFluids pin.

## 2. Tasks, in order

**H1 — port and re-verify (S).** Compile `ExcitonX1.lean` and `FourFlavour.lean` under your pinned stack
(`scripts/lean_pinned.py`). In `ExcitonX1.lean` replace the local `AdmissiblePotential` by
`OAI.TriangularUniversal.AdmissiblePotential` (it is a verbatim copy; add `example : ExcitonX1.AdmissiblePotential g ↔
OAI.TriangularUniversal.AdmissiblePotential g := Iff.rfl` first, as a guard). Record `#print axioms`, runtime, and that
the negative control fails. Report any statement you would change.

**H2 — the bilayer kernel as a corollary of D1 and the upstream theorem (S–M).** In a new file next to
`Triangular/Riesz.lean`:

```lean
import Triangular.Riesz
import Triangular.AnyDensity
namespace TriangularExciton
open OAI.AtomicTriangular TriangularRiesz TriangularDensity

/-- Direct interaction of two interlayer excitons, units e²/(4π ε₀ ε) = 1, t = r². -/
noncomputable def bilayer (d : ℝ) : ℝ → ℝ := fun t => 2 * (riesz 1 t - riesz 1 (t + d ^ 2))

theorem bilayer_admissible {d : ℝ} (hd : d ≠ 0) : AdmissiblePotential (bilayer d)            -- X1 + D1 (s = 1)
theorem triangular_bilayer_optimal {d : ℝ} (hd : d ≠ 0) (C : Set Plane) (hC : LocallyFinite C)
    (hdens : DensityOne C) : latticeEnergy (bilayer d) ≤ energy (bilayer d) C                  -- upstream theorem
theorem bilayer_any_density {d : ℝ} (hd : d ≠ 0) {ρ : ℝ} (hρ : 0 < ρ) (C : Set Plane)
    (hC : LocallyFinite C) (hdens : DensityRho ρ C) :
    ∑' a : {x : Plane // x ∈ A ∧ x ≠ 0}, ENNReal.ofReal (bilayer d (ρ⁻¹ * ‖a.val‖ ^ 2)) ≤ energy (bilayer d) C  -- D2
theorem latticeEnergy_bilayer_lt_top (d : ℝ) : latticeEnergy (bilayer d) < ⊤                  -- non-vacuity
```

Non-vacuity proof idea: for `t > 0`, `t^(−1/2) − (t + c)^(−1/2) ≤ (c/2) t^(−3/2)` (tangent line of the convex
`x ↦ x^(−1/2)`; Bernoulli with exponent −1/2), so `bilayer d ≤ d² · riesz 3` pointwise and D1b (s = 3 > 2) applies.
Negative control: `bilayer` with the sign of the shift reversed is not admissible (the statement
`¬ AdmissiblePotential (fun t => g (t + c) - g t)` for strictly decreasing `g`).

**H3 — a normalisation check you are best placed to do (S).** The upstream energy counts **ordered pairs**. State, as a
lemma next to `riesz_lattice_homogeneous`, `latticeEnergy g = 2 * (e_pair)` where `e_pair = ½ Σ_{a ≠ 0} g(‖a‖²)`
is the physical energy per particle. A factor 2 here is the single most likely slip in everything downstream.

**H4 — optional, hard: Yukawa and Keldysh (M–L).** `t ↦ e^(−κ√t)/√t` is completely monotone. Your D3 estimate
(~50 %, Bernstein/Faà di Bruno absent) stands. Route if attempted: `e^(−u√t) = ∫₀^∞ e^(−st) (u/(2√π)) s^(−3/2) e^(−u²/4s) ds`
(Lévy density), then `ProbabilityTheory.iteratedDeriv_mgf`-style differentiation under the integral for a finite
positive measure, then `∫_κ^∞ du`. Skip if the route is not visible within one session; **X1 already covers every
exciton–exciton kernel built from an admissible single-layer potential** and Keldysh can be taken as a hypothesis
(`AdmissiblePotential (keldysh r₀)`) to be discharged later.

**H5 — periodic configurations (L; the riskiest new item).** Needed to turn the infinite-plane theorem into a statement
about N bosons on a torus:

```lean
/-- N points per cell, repeated along the lattice ℤ v₁ + ℤ v₂. -/
def periodic (P : Finset Plane) (v₁ v₂ : Plane) : Set Plane :=
  {x | ∃ p ∈ P, ∃ m n : ℤ, x = p + (m : ℝ) • v₁ + (n : ℝ) • v₂}
-- hypotheses: LinearIndependent ℝ ![v₁, v₂]; translates of distinct points are distinct (N points per cell)
theorem periodic_locallyFinite ...                                   : LocallyFinite (periodic P v₁ v₂)
theorem periodic_density ...  : DensityRho (P.card / |v₁ 0 * v₂ 1 - v₁ 1 * v₂ 0|) (periodic P v₁ v₂)
theorem periodic_energy ...   : energy g (periodic P v₁ v₂) =
    (P.card : ℝ≥0∞)⁻¹ * ∑ p ∈ P, ∑' q : {q // q ∈ periodic P v₁ v₂ ∧ q ≠ p}, ENNReal.ofReal (g (‖p - q.val‖ ^ 2))
theorem torus_lower_bound ...  -- from `periodic_density`, `periodic_energy` and D2: the per-cell energy ≥ the lattice energy at that density
```

Fallback if `periodic_energy` is too heavy: state `torus_lower_bound` *conditionally* on `periodic_energy`
(hypothesis), and say so in the file header. The physical consequence (the quantum ground-state energy per particle of
N bosons on a torus with the periodised kernel is ≥ the lattice energy, because the kinetic energy is ≥ 0) is a one-line
step and is stated in the plan (§3.3, C1); you do not need to model operators.

**H6 — uniform minimiser from positive definiteness (S).** Elementary, no Fourier transform needed:

```lean
theorem uniform_minimises {G : Type*} [AddCommGroup G] [Fintype G] [DecidableEq G] (U : G → ℝ)
    (hU : ∀ f : G → ℝ, 0 ≤ ∑ x, ∑ y, f x * f y * U (x - y)) (n : G → ℝ) :
    (∑ x, ∑ y, ((∑ z, n z) / Fintype.card G) * ((∑ z, n z) / Fintype.card G) * U (x - y))
      ≤ ∑ x, ∑ y, n x * n y * U (x - y)
```
(write `n = n̄ + f` with `Σ f = 0`; the cross term is a constant times `Σ f`.) That "completely monotone ⇒ positive
definite" is classical (Schoenberg 1938 / Bernstein) and is **not** claimed here; the solver tests it numerically.

**H7 — optional certified numerics (M).** With the BAOCert pattern (integer tables, `decide +kernel`, soundness theorem,
tampered-table control): a kernel-checked enclosure of the known answer `Σ′_{a ∈ A₁∖0} ‖a‖^(−3)` for the
nearest-neighbour-unit triangular lattice, expected `11.0341757349…` (`= 6 ζ(3/2) L(3/2, χ₋₃)`; independent mpmath
value in the plan, Appendix B), by exact shell sums plus a tail bound from antitone comparison with the area
integral. Value: a Lean-checked number that the Rust solver's lattice sum must reproduce (mechanism L3).

## 3. Gates and discipline

* No `sorry`, no new axioms, no `native_decide`; `#print axioms` ⊆ {propext, Classical.choice, Quot.sound} for every
  named result; planted controls kept (`ctl_sorry`/`ctl_axiom` style) and flagged by the audit.
* Every file's header says what is conditional on `OAI.AtomicTriangular.universal_energy_minimum`.
* Statement fidelity: for H2 and H5, name the CKMRV/physics statement each definition corresponds to and add a short
  `audit/exciton/statement_fidelity.md` in your format. The producer's own audit is not independent; say so.
* Numbering: **your D3 (CKMRV Definition 1.3 at every density, vacancy non-minimiser) is unrelated to anything here.**
  The plan's lemmas are X1–X6 and the four-flavour theorems T1–T6; please keep those labels in cross-references.
  (X1 = `admissible_sub_shift`; X2 = Laplace/Yukawa, H4; X3 = Fourier positivity, replaced by H6's hypothesis form;
  X4 = periodic extension, H5; X5 = variational lower bound; X6 = uniform minimiser, H6.)

## 4. What to return

1. The new `.lean` files, their `compile_*.json` (rc, seconds, `#print axioms` output) in your audit layout.
2. A `verification.md` by a separate instance for `ExcitonX1.lean`/`FourFlavour.lean` (H1) and for H2.
3. An updated `MANIFEST.json` entry list (or the hashes), the toolchain/Mathlib pins, and the runtime and RAM seen.
4. A one-paragraph note of anything that did not go: statement you would change, lemma that turned out false.
5. Do **not** merge into LeanMaster's `main` or cut a release without the owner's word; a branch or a PR is enough.

## 5. The solver-side contract (so that the Lean outputs can be consumed)

QuantumFluids will quote only statements listed in a manifest (name, file, sha256 of the statement text, axioms),
and will export certificates for mechanism L3 in the BAOCert convention: `{"kernel", "params", "D" (common
denominator), "lo": [ints], "hi": [ints], "claim"}`; the Lean side checks them with `decide +kernel`. The first
planned certificate is the commensurate-torus one of the plan (§3.3, last bullet): the solver's energy (an upper
bound) against the upstream lower bound at the same density. The rusty-SUNDIALS MCP server you already use
(`scripts/mcp_sundials_client.py`) is the untrusted cross-check; note that its "ERROR FAIL" lines went to stdout until
PR #63 Part B (not yet merged in `main`), which corrupts the MCP stream on a failing solve.

## 6. Resources

Your note says other sessions' builds filled RAM and swap. Build only the closure of
`OAI.Analysis.Triangular.Energy.Universal` and `OAI.NumberTheory.DirichletL.LatticeSummability` (as in your
`REPRODUCE.md`); H1, H2, H3, H6 are short compiles; H5 and H7 are the expensive ones. QuantumFluids can re-run the
Mathlib-only files (`FourFlavour.lean`) locally in about two minutes.
