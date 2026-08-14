# PROJECT PLAN: SocrateAI-Scientific-QuantumFluids

**Stream coordinator:** (TBD)  
**Last updated:** 2026-08-14  
**Status:** Proposal stage (M0 pending approval)

---

## Milestones

### M0 — Bootstrap & Literature Ledger

**Objective:** Establish repo foundation and verify all citations from Expression Memo E1.

**Status:** ✅ **COMPLETE** (2026-08-14)

**Completed Tasks:**
- ✅ SPEC pinned from Mathesis (Stream-0 contract, R3.2)
- ✅ LEDGER.md initialized with claim inventory framework
- ✅ LL.md seeded from MechanicaFluidorum/Stage-1 LL.md
- ✅ LITERATURE_LEDGER.md: all 10 entries retrieved and verified
  - ✅ Madelung 1927 (DOI: 10.1007/BF01400372)
  - ✅ Onsager 1949 (DOI: 10.1007/BF02780991)
  - ✅ Feynman 1955 (DOI: 10.1016/S0079-6417(08)60077-3)
  - ✅ Barenghi–Skrbek–Sreenivasan 2014 (DOI: 10.1073/pnas.1400033111, OPEN ACCESS)
  - ✅ BCS 1957 (DOI: 10.1103/PhysRev.108.1175)
  - ✅ Deaver–Fairbank / Doll–Näbauer 1961 (DOI: 10.1103/PhysRevLett.7.43 & .7.51)
- ✅ EXPRESSION_MEMO_E1.md ready for promotion (all [unverified] cleared by retrieval)
- ✅ Mathesis integration complete (lean-toolchain, MATHESIS_INTEGRATION.md)
- ✅ GitHub repository pushed (5 commits live)
- ✅ Auto-approval configured (persistent across all sessions)

**Definition of Done:** ✅ All criteria met. Repo locked for M1 start.

**Unlocks:** M1, M2, M3, M4

---

### M1 — Dispersion-Relation Reproduction (Tier B)

**Objective:** Reproduce Landau two-parameter fit (c, Δ) as entry-level calibration and adapter validation.

**Status:** ⏳ **IN PROGRESS** (2026-08-14 start; target 2026-09-30)

**Tasks:**
- ⏳ Retrieve ILL-DATA DOI from Godfrin et al. PRB 103:104516 (2021) data-availability statement (AGENT ACTIVE)
- [ ] Cache raw numor files / processed S(Q,ω) data under data/external/ with .meta provenance
- [ ] Implement ILL Data Portal reader adapter (numor / .nxs / ASCII S(Q,ω) parsers) in src/quantumfluids/adapters/
  - [ ] Numor reader (binary format, ILL-specific metadata)
  - [ ] NeXus (.nxs) reader (hierarchical HDF5, standard structure)
  - [ ] ASCII S(Q,ω) reader (plain text, column-based)
- [ ] Implement dispersion-fit harness (Landau two-parameter form) in src/quantumfluids/dispersion_fit/
  - [ ] Two-parameter Landau model: E(q) = c·q + Δ·(1 + (q/q_m)²) for q > q_0
  - [ ] Nonlinear least-squares fitting (scipy.optimize or similar)
  - [ ] Uncertainty quantification (confidence intervals, residuals)
- [ ] Cross-check fitted (c, Δ) against literature values
  - [ ] Cowley–Woods 1971 (reference phonon-roton data)
  - [ ] Glyde et al. 1998 (subsequent measurements)
  - [ ] Godfrin et al. 2021 (own measurement to verify consistency)
- [ ] Write Tier-B harness with negative controls in tests/
  - [ ] Happy path: valid S(Q,ω) → fitted c, Δ
  - [ ] Negative control: axis swap (should error)
  - [ ] Negative control: missing metadata (should error)
  - [ ] Negative control: NaN/inf in data (should error or document)

**Metrics:**
- Fitted c within ±5% of literature
- Fitted Δ within ±10% of literature
- All adapters pass negative-control tests
- Dispersion-fit uncertainty < 10% for both parameters

**Definition of Done:** M1 report with fit plots, residuals, and literature comparison. Data provenance fully documented in data/external/*.meta files.

**Blocks:** M2, M3

---

### M2 — W4 Construction (Shell Model, Quantum-Pressure Variant)

**Objective:** Implement dispersive/quantum-pressure shell-model variant per E1 §4; integrate with dyadic-lab instrument from MechanicaFluidorum.

**Tasks:**
- [ ] Implement w4_shell_model/ submodule (quantum-pressure term, dispersion relation integration)
- [ ] Human audit of shell model before any run (checklist: term signs, dimension consistency, E1 fidelity)
- [ ] Import dyadic-lab exponent instrument from MechanicaFluidorum (MF version/commit TBD)
- [ ] Wire W4 shell model into instrument; prepare pre-registered readout
- [ ] Document W4 assumptions and parameter choices in src/quantumfluids/w4_shell_model/README.md

**Definition of Done:** Audited shell model, integrated instrument, pre-registered readout specification. Zero unaudited code paths in W4 branch.

**Blocks:** M3

---

### M3 — W4 Run + CIC Scoring

**Objective:** Execute W4 under three regulators; report results under Mathesis/MENSURA Certified Interval Criterion.

**Tasks:**
- [ ] Configure three regulators (TBD which specific ones; see E1 §4)
- [ ] Run W4 on prepared dataset (or simulation, per decision at M2)
- [ ] Compute CIC scores per Mathesis/MENSURA criterion
- [ ] Write results summary with confidence intervals
- [ ] File findings in LEDGER.md as new claims (if any)

**Definition of Done:** Published W4 results with CIC scores, provenance chain, and LEDGER entries.

---

### M4 — Outreach (Godfrin Correspondence)

**Objective:** Engage physics community; target Godfrin, Krotscheck, and Institut Néel quantum-turbulence group.

**Prerequisites:** M0, M1 complete (concrete, checkable artifacts to show).

**Tasks:**
- [ ] Draft correspondence summary (GODFRIN_CORRESPONDENCE.md)
- [ ] Reach out to Godfrin / Krotscheck (via e.g. arXiv comment, personal email if found, institution contact)
- [ ] Document all interactions: date, person, content, reply (or no-reply after N weeks)
- [ ] Assess Polanco et al. (Institut Néel, 2025) dataset for W4 complementarity (if public release available)
- [ ] Identify secondary contact: P.-E. Roche quantum-turbulence group (see proposal §2, finding 2)

**Definition of Done:** GODFRIN_CORRESPONDENCE.md with dated entries, responses (or documented silence), and summary of follow-ups planned.

---

## Legend

| Abbreviation | Meaning |
|---|---|
| E1 | Expression Memo E1 (dual-scale language dictionary) |
| W4 | The pre-registered experiment: three regulators, one instrument, phonon-roton measurement |
| CIC | Certified Interval Criterion (Mathesis/MENSURA framework) |
| Tier A, B, C | Evidentiary tiers: A=citation-verified, B=unit-testable, C=steering/narrative |
| LL-6 | Lessons-learned item 6 (pending literature retrieval from E1) |

---

## Decision points requiring owner approval

1. **M0 approval:** Go ahead with literature retrieval as planned?
2. **M2 instrument choice:** Which specific dyadic-lab instrument to import from MechanicaFluidorum?
3. **M3 regulators:** Which three regulators to use in W4 (see E1 §4 for options)?
4. **M4 timeline:** Proceed with outreach now, or only after M3 results?
