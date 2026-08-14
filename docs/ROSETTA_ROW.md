# ROSETTA ROW: Term Synchronization with Mathesis

**Purpose:** Maintain alignment between this stream's physics terminology and the Mathesis (Stream 0) formal definitions. Acts as a cross-reference catalog to prevent semantic drift.

**Format:** For each term used in QuantumFluids, record:
- Physics term (this stream)
- Mathesis formal definition (if applicable)
- Cross-reference (file, theorem, lemma)
- Status (SYNCED, PENDING, DIVERGENT)

---

## Active synchronization

### Duality (macro ↔ micro)

**Physics term:** Hydrodynamic–excitation duality in quantum fluids

**Mathesis formal name:** Mathesis.Duality (see SocrateAI-Scientific-Mathesis/src/duality.lean, Theorem T1)

**Link:** In superfluid helium, the macroscopic density-velocity field (hydrodynamic view) corresponds to a quantized excitation gas (micro view). The Madelung transform mediates this correspondence.

**Cross-reference:** EXPRESSION_MEMO_E1.md §2, LITERATURE_LEDGER.md [LIT-001, LIT-005]

**Status:** PENDING (awaiting Mathesis pin of duality theorem version)

---

### Scale (Reff — effective regularization length)

**Physics term:** Roton gap Δ as scale-separator in quantum pressure

**Mathesis formal name:** Mathesis.Scale.Reff (regularization effective length scale)

**Link:** In quantum fluids, the roton energy gap Δ provides a length scale ξ = ℏ/√(2mΔ) that separates phonon-dominated (long-wavelength) from roton-dominated (short-wavelength) regimes. This mirrors the role of Reff in the dual-scale program.

**Cross-reference:** EXPRESSION_MEMO_E1.md §3, LITERATURE_LEDGER.md [LIT-001]

**Status:** PENDING (awaiting Mathesis pin of Reff definition version)

---

### Tier-A evidentiary standard

**Physics term:** Citation-verified claim

**Mathesis formal name:** Mathesis.Verified (protocol for Tier-A claims)

**Link:** All claims in LEDGER.md marked TIER-A must have a LITERATURE_LEDGER.md entry with retrieval date and DOI/URL.

**Cross-reference:** SPEC.md, LEDGER.md, LITERATURE_LEDGER.md

**Status:** SYNCED (inherited from Mathesis contract R3.2)

---

### Tier-B evidentiary standard

**Physics term:** Unit-testable, reproducible claim

**Mathesis formal name:** Mathesis.Testable (protocol for Tier-B claims)

**Link:** All Tier-B claims must have corresponding tests in tests/ directory with negative controls.

**Cross-reference:** LL.md LL-2 (negative controls required), PLAN.md M1

**Status:** SYNCED (inherited from Mathesis contract R3.2)

---

### Tier-C evidentiary standard

**Physics term:** Narrative, exploratory, non-verifiable

**Mathesis formal name:** Mathesis.Narrative (quarantined speculation)

**Link:** Tier-C content lives in docs/narrative/ only. No claims-in-LEDGER. Clearly labeled as non-peer-reviewed.

**Cross-reference:** docs/narrative/ directory policy, LL.md LL-4

**Status:** SYNCED (inherited from Mathesis contract R3.2)

---

## Pending synchronization (awaiting Mathesis updates)

| Term | Mathesis reference | Status | ETA |
|---|---|---|---|
| Duality (hydrodynamic ↔ excitation) | Mathesis.Duality::T1 | PENDING | M0 end |
| Scale.Reff (roton gap ↔ regularization) | Mathesis.Scale.Reff | PENDING | M0 end |
| Madelung transform | Mathesis.? | PENDING | M1 |
| Quantum pressure (dual-scale view) | Mathesis.Scale.? | PENDING | M2 |

---

## Divergences flagged

*None yet.*

---

## Relation to MEMO_ROSETTA.md

This page synchronizes **terminology** across Mathesis and QuantumFluids.

For the broader **cross-domain catalog** of how the dual-scale principles (P1–P4) manifest across physics, mathematics, and industry, see **[MEMO_ROSETTA.md](MEMO_ROSETTA.md)**, which records:
- The four atomic principles (P1: self-dual bound, P2: Sym² lock, P3: discrete pins continuous, P4: bounce)
- Instantiations in Finite Fourier analysis, Ising model, Quantum Fluids, Quantum Hall metrology, Discrete geometry, Number theory, String T-duality, Operations research (EOQ), and K3 arithmetic
- Kernel-proved theorems with `#print axioms` certificates
- Pending targets (T-DS, T-KW2, T-QF1)
- Change Request CR-1 (the √|disc| refinement)

---

## How to maintain this catalog

1. When a term is introduced in EXPRESSION_MEMO_E1.md or PLAN.md, add a row here.
2. Flag status as PENDING until Mathesis equivalent is located.
3. After M0 (literature verification), update all statuses to SYNCED or DIVERGENT.
4. If DIVERGENT, file an issue in the Mathesis repo and notify the stream coordinator.
5. For broad cross-domain patterns, file a row in MEMO_ROSETTA.md per Rule E-X (express before extend).
