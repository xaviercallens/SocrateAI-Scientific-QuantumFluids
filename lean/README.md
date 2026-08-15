# Lean Implementation: SocrateAI-Scientific-QuantumFluids

**Status:** Prototype; depends on Mathesis (Stream 0) as mathematical command center.

**Toolchain:** Lean 4.33.0-rc2 (synchronized with Mathesis)

---

## Architecture

### Dependency Structure

```
QuantumFluids (this stream)
    └─ imports ─────→ Mathesis (Stream 0)
           ├─ Mathesis.Duality
           ├─ Mathesis.Scale.Reff
           └─ Mathesis.{other foundational modules}
```

### File Organization

```
lean/
├── lean-toolchain          (pinned to Mathesis version: v4.33.0-rc2)
├── QuantumFluids/          (this project's theorems)
│   ├── DualityInstance.lean  (QuantumFluids application of Mathesis.Duality)
│   ├── HealingLength.lean    (healing-length scale as Reff instance)
│   ├── W4Model.lean          (shell model definitions)
│   └── ExcitationSpectrum.lean (phonon-roton and excitation structures)
└── README.md               (this file)
```

---

## Importing from Mathesis

### Current Setup

**Location:** Mathesis repository is locally available at:
```
/home/xavkal/xdev/SocrateAI-Mathesis/lean/Mathesis/
```

**Remote:** https://github.com/xaviercallens/SocrateAI-Scientific-Mathesis

### Import Pattern

To import a Mathesis module in QuantumFluids:

```lean
import Mathesis.Duality
import Mathesis.Scale.Reff
```

The toolchain and Lean configuration will resolve these against the local Mathesis checkout.

### Dependency Management (Future)

When Lake is fully configured (TBD), the dependency structure will be:

```toml
[dependencies]
mathesis = {
  path = "../../SocrateAI-Mathesis/lean"
}
```

---

## Core Theorems (Mapped from Mathesis)

### Part A: Abstract Duality (Mathesis.Duality)

**File:** lean_src/Duality.lean (re-export of Mathesis proofs with quantum-fluid commentary)

- `sqrt_le_max_of_le_mul` — Self-dual bound (P1)
- `two_sqrt_mul_le_add` — AM–GM additive twin (A.4)
- `self_dual_fixed_point` — Fixed-point equivalence (A.5)
- `sinh_selfDual_coupling` — the fixed point of `sinh(2K)² = 1`. **Not** an Ising theorem: the file has no lattice and no partition function (Stream 0 `MX-C-0009`)

**Status:** Kernel-proved; audit: `#print axioms` yields only Classical.choice, propext, Quot.sound (per L4.1).

### Part B: QuantumFluids-Specific Instances (TBD)

**File:** lean/QuantumFluids/HealingLength.lean (TARGET T-QF1)

- Healing length ξ = ℏ/√(mα') as instance of Reff_ge_sqrt
- Roton gap Δ × ξ = √α' (self-dual scale)
- Quantized circulation Γ = n·ℏ/m as discrete pinning (P3)

**Status:** TARGET — awaiting M0 literature retrieval before formalization.

---

## Build & Verification

### Prerequisites

```bash
# Lean 4.33.0-rc2 (via elan or local install)
lean --version

# Lake (included with Lean 4)
lake --version
```

### Building QuantumFluids

```bash
# From the QuantumFluids root:
cd lean
lake build
```

### Verifying Proofs

```bash
# Check all Lean files:
lean lean/QuantumFluids/*.lean

# Or build and check:
lake build --check
```

### Axiom Audit

```bash
# Print axioms used by each theorem (should be empty or {Classical.choice, propext, Quot.sound}):
lean --eval 'Mathesis.Duality.sqrt_le_max_of_le_mul'
```

---

## Workflow: Mathesis as Command Center

### When Mathesis Updates

1. **Pull Mathesis changes:**
   ```bash
   cd /home/xavkal/xdev/SocrateAI-Mathesis
   git pull origin main
   ```

2. **Verify QuantumFluids still builds:**
   ```bash
   cd /home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/lean
   lake build
   ```

3. **If build fails:** Check git blame on the Mathesis commit and contact the Mathesis stream coordinator.

4. **If build succeeds:** Update ROSETTA_ROW.md with new Mathesis import versions.

### When QuantumFluids Adds New Theorems

1. **Draft in QuantumFluids/**.lean (e.g., HealingLength.lean)
2. **Mark claims as TARGET if they depend on Mathesis.** (see EXPRESSION_MEMO_E1.md §2)
3. **Human audit before kernel check** (PLAN.md M2 checklist)
4. **File in LEDGER.md once kernel-proved**

---

## Known Issues & TODOs

- [ ] Lake configuration not yet formalized (TBD after Mathesis stabilizes)
- [ ] QuantumFluids/HealingLength.lean — TARGET T-QF1, awaiting M0 literature retrieval
- [ ] QuantumFluids/W4Model.lean — Shell model formalization (M2, pre-audit)
- [ ] Exact-arithmetic harness for finite-lattice Ising identities (M3 action item)

---

## Cross-References

- **Parent project:** SocrateAI-Scientific-QuantumFluids (root README.md)
- **Mathesis command center:** /home/xavkal/xdev/SocrateAI-Mathesis/
- **Duality theorems:** lean_src/Duality.lean (re-export with comments)
- **MEMO_ROSETTA.md:** Cross-domain principle catalog (status of each Mathesis import)
- **EXPRESSION_MEMO_E1.md:** Physics grounding (maps E1.1–E1.4 to Lean theorems)

---

**Last updated:** 2026-08-14 (M0 bootstrap)  
**Status:** Ready for M0 literature retrieval; M1–M4 Lean formalization TBD
