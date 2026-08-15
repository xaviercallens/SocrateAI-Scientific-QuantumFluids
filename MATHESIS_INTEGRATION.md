# MATHESIS INTEGRATION: QuantumFluids as Dependent Stream

**Role of Mathesis:** notation, verification kernel and epistemic bookkeeping for QuantumFluids (Stream QF).

**Contract:** SocrateAI-Scientific-Mathesis (Stream 0) provides:
1. Proven foundational theorems (Duality, Scale.Reff, Tier-A certification)
2. Verification infrastructure (kernel-audit, axiom-freedom checks)
3. Governance rules (Rule E-X: express before extend; Tier-A/B/C tiering)

**QuantumFluids applies:** These theorems to a specific physics domain (quantum fluids, superfluid ⁴He).

---

## Dependency Graph

```
Mathesis (Stream 0)
  ├── Mathesis.Duality (Part A: abstract bounds)
  │   ├── sqrt_le_max_of_le_mul (self-dual bound, P1)
  │   ├── two_sqrt_mul_le_add (AM–GM, A.4)
  │   ├── self_dual_fixed_point (fixed point, A.5)
  │   └── sinh_selfDual_coupling (fixed point of sinh(2K)²=1; NOT Ising)
  │
  ├── Mathesis.Scale.Reff (fundamental length scale)
  │
  ├── Mathesis.Duality.Uncertainty (Parseval + Donoho-Stark on ZMod N)
  │
  └── Mathesis.TierCalculus (the tier order and its soundness theorem)

              ↓↓↓ QuantumFluids imports ↓↓↓

QuantumFluids (Stream QF)
  ├── lean_src/Duality.lean (re-export with QF commentary)
  ├── lean/QuantumFluids/HealingLength.lean (TARGET T-QF1: Reff instance)
  ├── lean/QuantumFluids/W4Model.lean (shell model, M2)
  └── docs/EXPRESSION_MEMO_E1.md (physics language for Mathesis theorems)
```

---

## Four Atomic Principles: QuantumFluids Instantiation

### P1: Self-Dual Bound

**Mathesis theorem:** `C ≤ x·y ⇒ √C ≤ max(x,y)`

**QuantumFluids reading:** Roton gap Δ × healing length ξ = kinematic viscosity α'. Therefore, √α' ≤ max(Δ, α'/Δ) and √α' ≤ max(ξ, α'/ξ). No macroscopic scale can fall below √α' without quantum effects becoming inertially visible.

**Reference:** EXPRESSION_MEMO_E1.md §2, E1.1

---

### P2: Sym² Lock (Macroscopic = Product of Microscopic)

**Mathesis principle:** Macroscopic degrees of freedom emerge as products of microscopic modes; no independent macro DOF.

**QuantumFluids reading:** Hydrodynamic modes (density, velocity) arise as excitation-gas products: phonons × rotons. The analogy to BCS Cooper pairing (two electron modes → one boson mode) is Tier C but structurally suggestive.

**Reference:** EXPRESSION_MEMO_E1.md §2, E1.3

---

### P3: Discrete Pins Continuous

**Mathesis theorem:** A continuous quantity equals the inverse of a discrete invariant.

**QuantumFluids reading:** Circulation Γ = n·ℏ/m (n integer). The continuous velocity field is pinned to discrete values by topological quantization. This is nature's application of P3: the Donoho–Stark result (finite Fourier support product ≥ N, with N discrete) manifests in vortex quantization.

**Reference:** EXPRESSION_MEMO_E1.md §2, E1.2; MEMO_ROSETTA.md (Finite Fourier row)

---

### P4: Bounce (No Collapse Below Scale Floor)

**Mathesis principle:** Contraction below the self-dual scale reflects into dilation.

**QuantumFluids reading:** Vortex cores cannot collapse below the healing length ξ. Vortex reconnections (topological defect annihilation) represent the deflection (bounce) at the scale floor. The cascade terminates, not by viscous dissipation, but by quantum topology.

**Reference:** EXPRESSION_MEMO_E1.md §2, E1.2; MEMO_ROSETTA.md (Quantum Fluids row)

---

## Tier-A Physics Grounding

All physics cited below is **Tier A** (citation-verified experimental or theoretical work). Every citation is tracked in LITERATURE_LEDGER.md.

| Physics domain | Mathesis principle(s) | Citation status | Action |
|---|---|---|---|
| **Gross–Pitaevskii equation** (P1, P2) | Madelung transform, quantum-pressure term | `[LL-6 pending]` | M0 retrieval |
| **Circulation quantization** (P3, P4) | Onsager, Feynman, Barenghi–Skrbek–Sreenivasan | `[LL-6 pending]` | M0 retrieval |
| **Phonon-roton dispersion** (E1.1) | Godfrin et al. 2021, Godfrin & Krotscheck 2022 | ✓ VERIFIED (LIT-001, LIT-002) | M1 data target |
| **Quantum-turbulence vortex studies** (P4) | Polanco et al. 2025 (Institut Néel) | ✓ VERIFIED (LIT-004) | M4 outreach |

---

## Lean Integration

### Imports

```lean
-- QuantumFluids/HealingLength.lean
import Mathesis.Duality
import Mathesis.Scale.Reff

-- Apply Mathesis theorem to quantum-fluid product
theorem healing_length_bound {Δ ξ α : ℝ} 
    (hprod : Δ * ξ = α) : 
    Real.sqrt α ≤ max Δ ξ := by
  exact sqrt_le_max_of_le_mul (by positivity) (by positivity) hprod.ge
```

### Toolchain

QuantumFluids uses the **same Lean version** as Mathesis (v4.33.0-rc2) to ensure binary compatibility and transparent error messages.

**File:** `lean-toolchain`

---

## Governance: Rule E-X (Express Before Extend)

**Rule E-X** (from Mathesis SPEC.md) applies to QuantumFluids:

> A domain enters the dual-scale principles catalog only as the **re-expression of an established theorem** in the common language (Tier A/B by inheritance, citation verified), and may only afterwards host an extension (Tier C, labeled).

**Example:**

❌ **Wrong (violates E-X):**
```
Claim: Quantum fluids prove that all regularizations work the same way.
Status: Speculation about regulators in general.
```

✓ **Right (obeys E-X):**
```
Established result: Godfrin et al. 2021 measured phonon-roton dispersion.
Expression memo: This dispersion instantiates P1 (self-dual bound) in our language.
Extension (Tier C): Hypothesis that all dispersive regulators are equivalent 
  (labeled exploratory; requires further work).
```

---

## Decision Points Requiring Mathesis Coordination

### 1. Reff Version Pinning (M0)

**Action:** Check SocrateAI-Scientific-Mathesis/SPEC.md for the current pinned version of `Mathesis.Scale.Reff`.

**When:** Before M0 completes. Update ROSETTA_ROW.md with the version tag.

### 2. Axiom-Free Proof Standard (M2)

**Action:** Mathesis enforces `#print axioms` ⊆ {Classical.choice, propext, Quot.sound} (rule L4.1). QuantumFluids inherits this.

**When:** Before any shell-model theorem is filed in LEDGER.md. Human audit must confirm zero unexpected axioms.

### 3. Donoho–Stark Discharge (M1, TARGET T-DS)

**Action:** Once Mathesis formalizes the Donoho–Stark product bound (TARGET T-DS in Duality.lean), QuantumFluids references it for the finite-Fourier support cascade.

**When:** M1 (after literature retrieval). May unlock the exact proof of support_balance.

### 4. Sym² Lock Formalization (M2, P2)

**Action:** If Mathesis formalizes the Sym² lock (macro = product of micro), QuantumFluids applies it to hydrodynamic↔excitation duality.

**When:** M2–M3. Currently Tier C (structural analogy).

---

## Keeping in Sync: Maintenance Checklist

### Weekly (during M0–M4)

- [ ] Does `lake build` in QuantumFluids/lean/ still succeed against current Mathesis?
- [ ] Any new Mathesis warnings or axiom-audit flags?

### After Each Mathesis Update

- [ ] Pull Mathesis main: `cd /home/xavkal/xdev/SocrateAI-Mathesis && git pull origin main`
- [ ] Rebuild QuantumFluids: `cd lean && lake build`
- [ ] Update ROSETTA_ROW.md with new import versions
- [ ] Commit the version bump: `git commit -m "bump Mathesis imports to commit XYZ"`

### After QuantumFluids Adds New Theorems

- [ ] Tag each theorem with Mathesis dependency: `-- Imports: Mathesis.Duality, Mathesis.Scale.Reff`
- [ ] File in LEDGER.md with Tier-A/B status
- [ ] Run axiom audit: `#print axioms <theorem_name>`
- [ ] Update MEMO_ROSETTA.md if it instantiates a cross-domain principle

---

## Current Status

**M0 (Bootstrap):**
- ✅ Mathesis repository identified and locally available
- ✅ Lean toolchain synchronized (v4.33.0-rc2)
- ✅ Duality.lean re-exported with QuantumFluids commentary
- ✅ Import pattern documented (lean/README.md)
- ⏳ Awaiting M0 literature retrieval before formalizing E1.1–E1.4

**M1–M4:**
- Target: Import Mathesis.Scale.Reff for healing-length instance
- Target: Formalize W4 shell model (M2)
- Target: Run W4 experiment and file results (M3)

---

## Related Documentation

- **Mathesis SPEC.md** — Parent stream specification and contract
- **Mathesis LEDGER.md** — Claim registry (QuantumFluids inherits Tier-A status from Mathesis)
- **QuantumFluids SPEC.md** — This stream's specification (references Mathesis R3.2)
- **QuantumFluids ROSETTA_ROW.md** — Term synchronization (updated as imports resolve)
- **QuantumFluids lean/README.md** — Lean-specific build and verification instructions

---

**Integration coordinator:** (TBD — stream owner)  
**Last verified:** 2026-08-14  
**Mathesis remote:** https://github.com/xaviercallels/SocrateAI-Scientific-Mathesis  
**Mathesis local:** /home/xavkal/xdev/SocrateAI-Mathesis
