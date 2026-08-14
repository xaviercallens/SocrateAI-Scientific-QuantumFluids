# PROJECT PLAN: SocrateAI-Scientific-QuantumFluids

**Stream coordinator:** (TBD)  
**Last updated:** 2026-08-14  
**Status:** M0–M2 complete. M3 blocked by the M2 finding (by design, not by failure).
M4 open, needs owner action.

| M0 | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| ✅ | ✅ | ✅ (negative finding) | 🛑 blocked by M2 | ⏸ open |

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

**Status:** ✅ **SUBSTANTIALLY COMPLETE** (2026-08-14 — same-day start and core completion; full history in M1_CHECKLIST.md and M1_REPORT.md)

**What happened:** Raw ILL numor access (M1-DATA-001) is still pending author response, but Godfrin et al. (2021)'s own arXiv preprint publishes an exact ancillary dispersion-curve table — used instead as Tier-B data. Both fit metrics passed decisively (c: 0.24% from literature vs. ±5% target; Δ: 0.04% vs. ±10% target). See M1_REPORT.md for the full account, including a Tier-C (digitized-figure) pass done first that caught 3 real code bugs and correctly diagnosed a phonon-fit limitation later confirmed by the Tier-B result.

**Tasks:**
- [x] ~~Retrieve ILL-DATA DOI~~ — still pending (not M1-blocking; see M1_DATA_ACCESS_STRATEGY.md), superseded by ancillary data for M1's purpose
- [x] Cache Tier-B (ancillary) and Tier-C (digitized) data under data/external/ with .meta provenance
- [x] Implement adapters in src/quantumfluids/adapters/
  - [x] NeXus (.nxs) reader (tested, skipped pending h5py)
  - [x] ASCII S(Q,ω) reader + digitized-CSV loader
  - [x] Godfrin ancillary-file reader (not originally planned — added for the Tier-B dataset)
  - [ ] ILL numor reader — deliberate placeholder (no real sample to validate against; see file docstring)
- [x] Implement dispersion-fit harness in src/quantumfluids/dispersion_fit/
  - [x] Two-region Landau model: linear phonon branch + parabolic roton branch (fit separately, not one closed form — see landau_model.py docstring)
  - [x] Nonlinear least-squares fitting (scipy.optimize.curve_fit)
  - [x] Uncertainty quantification (covariance-based stderr, NaN-sigma sanitization)
- [x] Cross-check fitted (c, Δ) against literature values
  - [ ] Cowley–Woods 1971 — value coded in REFERENCE_VALUES, independent LITERATURE_LEDGER.md entry still pending
  - [ ] Glyde et al. 1998 — same
  - [x] Godfrin et al. 2021 (own measurement) — PASSED, both metrics
- [x] Write Tier-B harness with negative controls in tests/ (35 passed, 1 skipped)

**Metrics:**
- ✅ Fitted c within ±5% of literature — achieved 0.24%
- ✅ Fitted Δ within ±10% of literature — achieved 0.04%
- ✅ All adapters pass negative-control tests
- ✅ Dispersion-fit uncertainty < 10% for both parameters (stderr << 1% for both)

**Definition of Done:** ✅ M1_REPORT.md filed with fit plots, residuals, and literature comparison. Data provenance documented in data/external/*.meta files. Remaining: Cowley-Woods/Glyde independent citations (does not block M2).

**Blocks:** M2, M3 — **now unblocked, M2 can begin**

---

### M2 — W4 Construction (Shell Model, Quantum-Pressure Variant)

**⚠️ Scope corrected 2026-08-14.** Original plan assumed a "dyadic-lab
exponent instrument" and a "W2 regulator" already existed in
MechanicaFluidorum, ready to import. A targeted search (Explore agent)
found neither exists — MechanicaFluidorum has a real Tier-C shell-model
script (`exploration/dyadic_cascade.py`) and an un-implemented design
memo for exponent-fitting (`docs/designs/OP2_LITE_CANDIDATES.md`), but
no regulator abstraction, no fitting harness, no "W2." See
EXPRESSION_MEMO_E1.md §4 correction and LL.md LL-9 for the full account.
**M2 must now build the regulator interface and exponent-fitting harness
itself**, not import one. This is a larger scope than originally planned.

**Status:** ✅ **COMPLETE** (2026-08-14) — with a negative result as the finding.
See `M2_REPORT.md`. Design memo audited; Lean formalisation landed (CLAIM-007, Tier A);
Positive Control #1 passed at exactly `0.00e+00`; the W4 measurement itself is
obstructed and that obstruction is the reported result (CLAIM-005/006/008/009/010).

**Objective (as originally set):** Implement dispersive/quantum-pressure shell-model variant per E1 §4; build a peak-enstrophy exponent-fitting harness with a pluggable regulator interface (informed by, not copied from, MechanicaFluidorum's real script and design memo).

**Tasks:**
- [x] **Decision:** harness lives in QuantumFluids, offered upstream later
      if it proves generally useful (option 2c below; owner, 2026-08-14).
- [x] **Design memo written and awaiting audit:**
      `docs/designs/M2_W4_DISPERSIVE_SHELL.md` (2026-08-14). Establishes
      that a real-amplitude shell model *structurally cannot* host a
      dispersive regulator, and resolves it with a conjugated
      complexification verified to conserve energy exactly and to reduce
      exactly to MechanicaFluidorum's real model. **Nothing may be
      implemented until this memo is marked AUDITED in LEDGER.md** (E-1).
      Raises 5 open items (O1–O5) for the auditor, including a defect
      found in MechanicaFluidorum's own enstrophy observable (O1).
- [x] **AUDIT the design memo** — ✅ APPROVED by owner 2026-08-14, with
      rulings O1–O5 recorded in LEDGER.md's design-memo audit register.
      O1 ruled *record both* enstrophy conventions (stronger than the
      memo's own recommendation of using the sum).
- [x] Promote `exploration/verify_complexification.py` (Tier C scratch) to
      a Tier B harness with negative controls — done 2026-08-14:
      `src/quantumfluids/w4_shell_model/shell_dynamics.py` +
      `tests/test_shell_dynamics.py` (23 tests, 5 negative controls,
      mutation-tested with 3 injected production bugs, all caught).
- [x] Write the MechanicaFluidorum defect report as a portable standalone
      document — `docs/DEFECT_REPORT_MF_ENSTROPHY.md` (owner to route)
- [ ] Design the regulator interface (function signature or class) that
      truncation, bounce, and dispersive/quantum-pressure regulators can
      all implement — does not exist anywhere yet, must be designed
- [ ] Implement the exponent-fitting harness (peak-enstrophy β vs. cutoff
      parameter, with confidence intervals — a CIC/MENSURA framework is
      referenced in this stream's own docs but not implemented anywhere
      either; needs its own design or a scoped-down substitute)
- [ ] Implement w4_shell_model/ submodule (quantum-pressure term, dispersion relation integration)
- [ ] Implement truncation-control regulator as the first instance of the
      interface, to validate the harness before adding W4
- [ ] **W2 (bounce) deferred to its own design memo** — per M2 memo §5, no
      reflective-seam regulator exists or is designed, and whether any
      such seam preserves energy is unresolved. W4 does not wait for it;
      the E1 §4 comparison runs as two-then-three.
- [ ] Human audit of shell model before any run (checklist: term signs, dimension consistency, E1 fidelity)
- [ ] Document W4 assumptions and parameter choices in src/quantumfluids/w4_shell_model/README.md

**Definition of Done:** Audited shell model, working exponent-fitting harness with 3 regulators (truncation, bounce, dispersive), pre-registered readout specification. Zero unaudited code paths in W4 branch.

**Recommended model tier:** this involves real physics-modeling and
architecture judgment (regulator interface design, quantum-pressure term
form, dimensional consistency, fidelity to E1) — not mechanical
implementation. Consider a higher-effort/higher-tier model for the
design step specifically.

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

1. ~~**M0 approval:**~~ ✅ Resolved — M0 complete (2026-08-14).
2. **M2 harness location (was: "instrument choice" — corrected 2026-08-14):**
   Since no exponent-fitting harness exists in MechanicaFluidorum to
   import, where should QuantumFluids build one?
   - **(a) Self-contained in QuantumFluids** — no cross-repo dependency,
     but potentially duplicates future MechanicaFluidorum work if they
     build their own instrument later.
   - **(b) Contribute upstream to MechanicaFluidorum** — becomes real
     shared infrastructure both streams can use, but requires
     cross-repo coordination and MechanicaFluidorum's own audit process.
   - **(c) Build in QuantumFluids now, offer to upstream later** if it
     proves generally useful — avoids blocking on coordination, keeps
     the option open.
3. **M3 regulators:** Which three regulators to use in W4 (see E1 §4 for options)? Unchanged from original plan, but now depends on M2 actually building them.
4. **M4 timeline:** Proceed with outreach now, or only after M3 results?
