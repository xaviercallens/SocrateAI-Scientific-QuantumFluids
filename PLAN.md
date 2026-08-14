# PROJECT PLAN: SocrateAI-Scientific-QuantumFluids

**Stream coordinator:** (TBD)  
**Last updated:** 2026-08-14  
**Status:** Proposal stage (M0 pending approval)

---

## Milestones

### M0 — Bootstrap & Literature Ledger

**Objective:** Establish repo foundation and verify all citations from Expression Memo E1.

**Tasks:**
- [ ] SPEC pinned from Mathesis (Stream-0 contract, R3.2)
- [ ] LEDGER.md initialized with empty claim inventory
- [ ] LL.md seeded from MechanicaFluidorum/Stage-1 LL.md
- [ ] LITERATURE_LEDGER.md: every [LL-6 pending] item from E1 retrieved and dated
  - [ ] Madelung 1927
  - [ ] Onsager 1949
  - [ ] Feynman 1955
  - [ ] Barenghi–Skrbek–Sreenivasan PNAS 2014
  - [ ] BCS 1957
  - [ ] Deaver–Fairbank / Doll–Näbauer 1961
- [ ] EXPRESSION_MEMO_E1.md promoted to docs/; zero [unverified] tags remain

**Definition of Done:** LITERATURE_LEDGER.md has retrieval dates and DOI/URL for all items. E1 fully verified and migrated.

**Blocking:** M1, M2

---

### M1 — Dispersion-Relation Reproduction (Tier B)

**Objective:** Reproduce Landau two-parameter fit (c, Δ) as entry-level calibration and adapter validation.

**Tasks:**
- [ ] Retrieve ILL-DATA DOI for Godfrin et al. PRB 103, 104516 (2021) from paper's data-availability statement
- [ ] Cache raw numor files under data/external/ with .meta provenance
- [ ] Implement ILL Data Portal reader adapter (numor / .nxs / ASCII S(Q,ω) parsers) under src/quantumfluids/adapters/
- [ ] Implement dispersion-fit harness (Landau two-parameter form) under src/quantumfluids/dispersion_fit/
- [ ] Cross-check fitted (c, Δ) against literature values (Cowley–Woods 1971; Glyde et al. 1998)
- [ ] Write Tier-B harness with negative controls under tests/

**Metrics:**
- Fitted c within ±5% of literature
- Fitted Δ within ±10% of literature
- All adapters pass negative-control tests

**Definition of Done:** M1 report with fit plots, residuals, and literature comparison. Data provenance fully documented.

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
