# SocrateAI-Scientific-QuantumFluids

**Quantum Fluids as the Realized Instance of Dual-Scale Regularization**

[![Status](https://img.shields.io/badge/Status-Proposal-yellow)]() [![Mathesis Dependent](https://img.shields.io/badge/Depends%20on-Mathesis%20Stream%200-blue)]()

---

## Overview

This stream expresses established quantum-fluid physics in the dual-scale regularization language (Tier A/B, citation-verified) and runs the W4 pre-registered experiment (three regulators, one instrument). The work is grounded in published experimental data and outreach to the physics community.

**Key documents:**
- **[SPEC.md](SPEC.md)** — Specification and contract (pinned from Mathesis Stream 0)
- **[PLAN.md](PLAN.md)** — Milestones M0–M4 with tasks and definitions of done
- **[LEDGER.md](LEDGER.md)** — Claim inventory (Tier A/B/C tracking)
- **[LL.md](LL.md)** — Lessons learned (inheritance + new insights)

---

## Quick start

### M0: Bootstrap & Literature Ledger (Current)

Get started by reviewing and retrieving literature:

```bash
# Check literature retrieval status
grep -A2 "Status: PENDING" docs/LITERATURE_LEDGER.md

# Run verification script
bash scripts/verify.sh
```

**Blocking items:** [LIT-005] through [LIT-010] (see LITERATURE_LEDGER.md for retrieval paths)

### M1: Dispersion-Relation Reproduction

After M0, set up the data pipeline and dispersion-fit tools:

```bash
# (TBD: Instructions for M1 setup)
```

---

## Repository structure

```
.
├── SPEC.md                          # Contract (pinned from Mathesis)
├── PLAN.md                          # Milestones & task list
├── LEDGER.md                        # Claim inventory (Tier A/B/C)
├── LL.md                            # Lessons learned
├── docs/
│   ├── EXPRESSION_MEMO_E1.md        # Dictionary (dual-scale language)
│   ├── ROSETTA_ROW.md               # Term sync with Mathesis
│   ├── LITERATURE_LEDGER.md         # Citation registry (retrieval-verified)
│   ├── GODFRIN_CORRESPONDENCE.md    # Outreach log
│   └── narrative/                   # Dark-matter speculation (Tier C, quarantined)
├── lean_src/                        # Lean theorems (imports Mathesis)
├── src/quantumfluids/
│   ├── adapters/                    # Data readers (numor, .nxs, ASCII S(Q,ω))
│   ├── w4_shell_model/              # Dispersive shell model (quantum pressure)
│   └── dispersion_fit/              # Phonon-roton fit tools (Landau 2-param)
├── data/
│   ├── external/                    # Cached open datasets (FAIR licensed)
│   │   └── *.meta                   # Provenance (DOI, retrieval date, checksum)
│   └── derived/                     # Reductions from this stream
├── tests/                           # Tier-B harnesses (negative controls mandatory)
└── scripts/verify.sh                # Gate 1 (tests) + Gate 2 (Lean imports)
```

---

## Key constraints

- **No well-posedness claims about Navier–Stokes** (quarantined under MF obstruction O5)
- **ξ→0 limit not claimed solved** (mathematical difficulty recognized)
- **Dark matter only in named experimental programs** (speculation confined to docs/narrative/)
- **All Tier-A claims citation-verified** (LITERATURE_LEDGER.md is authoritative)

---

## Milestones

| Milestone | Status | Objective | Blocking |
|-----------|--------|-----------|----------|
| **M0** | Proposal | Bootstrap repo; verify literature | M1, M2 |
| **M1** | TBD | Reproduce Landau fit (c, Δ); validate adapters | M2, M3 |
| **M2** | TBD | Implement W4 shell model; integrate instrument | M3 |
| **M3** | TBD | Run W4 under three regulators; CIC score | — |
| **M4** | TBD | Outreach (Godfrin, Institut Néel); engagement | — |

---

## Getting help

- **Questions about this stream?** Check [PLAN.md](PLAN.md) §"Decision points requiring owner approval"
- **Literature retrieval stuck?** See [LITERATURE_LEDGER.md](docs/LITERATURE_LEDGER.md#retrieval-summary-m0-progress)
- **Outreach strategy?** Read [GODFRIN_CORRESPONDENCE.md](docs/GODFRIN_CORRESPONDENCE.md)

---

## References

**Key literature:**

- Godfrin & Krotscheck (2022). "The Dynamics of Quantum Fluids." arXiv:2206.06039 [LIT-001]
- Godfrin et al. (2021). "Dispersion relation of Landau elementary excitations in superfluid helium by inelastic neutron scattering." Phys. Rev. B 103, 104516. [LIT-002]
- Hirschel et al. (2024). "Superfluid helium ultralight dark matter detector." Phys. Rev. D 109, 095011. [LIT-003]

See [LITERATURE_LEDGER.md](docs/LITERATURE_LEDGER.md) for the full registry.

---

**Stream coordinator:** (TBD)  
**Last updated:** 2026-08-14  
**License:** See SocrateAI-Scientific-Mathesis for license terms.
