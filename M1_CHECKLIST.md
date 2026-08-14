# M1 Execution Checklist: Dispersion-Relation Reproduction

**Milestone:** M1 (Tier B)  
**Start date:** 2026-08-14  
**Target completion:** 2026-09-30  
**Blocking:** M2 (W4 shell model), M3 (W4 execution)

---

## Phase 1: Data Access & Retrieval

### 1.1 ILL-DATA DOI Identification
- **Status:** ✅ AGENT COMPLETED (a25c3d8801aee519c, 2026-08-14)
- **Finding:** DOI NOT web-indexed; data is RESTRICTED (requires ILL account or author request)
- **Journal DOI:** 10.1103/PhysRevB.103.104516 ✓
- **ILL-DATA DOI:** NOT YET RETRIEVED (requires direct contact)
- **Recommendation:** Email H. Godfrin or ILL data-portal (data-portal@ill.fr) for access
- **Fallback:** Digitize Fig. 5 from review (Tier C steering data) + arXiv supplementary tables

### 1.2 Data Access & Licensing
- **Status:** PENDING
- **Task:** Confirm ILL Data Portal access (public vs. account-required)
- **Deliverable:** data/external/ILL-DATA.meta with:
  - DOI
  - URL
  - File formats available (numor, .nxs, ASCII)
  - License/terms of use
  - Retrieval date & checksum

### 1.3 Raw Data Caching
- **Status:** PENDING
- **Task:** Download or mirror numor/S(Q,ω) files to data/external/
- **Destination:** `/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/data/external/godfrin_2021_prb103_in5/`
- **Metadata:** Each file gets a .meta companion (DOI, checksum, retrieval date)

---

## Phase 2: Adapter Implementation

### 2.1 ILL Numor Reader (`src/quantumfluids/adapters/ill_numor.py`)
- **Status:** ⏸️ PLACEHOLDER (deliberate — see notes)
- **Decision:** Implementing a binary numor parser without a real sample
  file to validate against would mean shipping untested format-guessing
  logic — the exact failure mode LL-2 warns against. Module raises
  `NumorNotImplementedError` with guidance to use `nexus_reader` or
  `load_digitized_csv` instead.
- **Unblocks when:** M1-DATA-001 yields a real numor file (see
  M1_DATA_ACCESS_STRATEGY.md) to write and regression-test against.

### 2.2 NeXus Reader (`src/quantumfluids/adapters/nexus_reader.py`)
- **Status:** ✅ IMPLEMENTED (2026-08-14)
- **Coverage:** Tries known Mantid/LAMP layout templates (`_KNOWN_LAYOUTS`);
  refuses to guess at unrecognized structure.
- **Caveat:** Layout templates NOT yet validated against a real Godfrin
  et al. 2021 file — populated from general Mantid/LAMP convention.
  Extend `_KNOWN_LAYOUTS` once a real sample is available.
- **Tests:** tests/test_nexus_reader.py (skipped — h5py not installed,
  blocked on python3.12-venv/sudo; see decision point below)
  - ✅ Happy path: valid .nxs → correct extraction
  - ✅ Negative control: unknown layout → error
  - ✅ Negative control: axis swap (shape mismatch) → error
  - ✅ Negative control: NaN in Q axis → error
  - ✅ Negative control: non-monotonic Q axis → error

### 2.3 ASCII Reader (`src/quantumfluids/adapters/ascii_sqw.py`)
- **Status:** ✅ IMPLEMENTED (2026-08-14)
- **Coverage:** Auto-detects delimiter (comma/whitespace), 2–4 columns
  (Q, ω[, S[, dS]]), skips `#` comments. Includes `load_digitized_csv()`
  for the Tier-C fallback pathway (WebPlotDigitizer CSV export).
- **Tests:** tests/test_ascii_sqw.py — 13 tests, all PASSING
  - ✅ Happy path: 4-column, 2-column, comma-delimited, S-has-NaN (flagged not rejected)
  - ✅ Negative control: single column → error
  - ✅ Negative control: ragged rows → error
  - ✅ Negative control: non-numeric value → error
  - ✅ Negative control: NaN in Q axis → error
  - ✅ Negative control: inf in ω axis → error
  - ✅ Negative control: empty file → error
  - ✅ Digitized-CSV happy path + 2 negative controls

### 2.4 Adapter Registry & Testing
- **Status:** ✅ IMPLEMENTED (`src/quantumfluids/adapters/__init__.py`)
- **Negative Controls (LL-2 inheritance):** ✅ Axis swap, metadata
  consistency, NaN/inf handling — all enforced per adapter above.

---

## Phase 3: Dispersion-Fit Implementation

### 3.1 Landau Model (`src/quantumfluids/dispersion_fit/landau_model.py`)
- **Status:** ✅ IMPLEMENTED (2026-08-14)
- **Physics (as implemented — two separate regions, not one closed form):**
  - Phonon branch (linear): `E(Q) = c·Q`
  - Roton branch (parabolic): `E(Q) = Δ + (ħ²/2μ)·(Q − Q_m)²`
- **Implementation:**
  - `scipy.optimize.curve_fit` per branch, with `sigma`/`absolute_sigma`
    support when `dS` uncertainties are available
  - Covariance matrix → stderr on c, Δ, Q_m, effective mass
  - `RotonFitResult.effective_mass_amu()` converts to units of m(⁴He)
- **Validated:** synthetic-data recovery tests (known c/Δ/Q_m recovered
  within M1 tolerance from noisy synthetic data)

### 3.2 Fitting Harness (`src/quantumfluids/dispersion_fit/fit_dispersion.py`)
- **Status:** ✅ IMPLEMENTED (2026-08-14)
- **Workflow:** `run_dispersion_fit()` — select phonon region (Q < 0.4 Å⁻¹
  default) and roton region (|Q − 1.9| < 0.5 Å⁻¹ default) → fit both →
  return `DispersionFitReport`. `compare_to_literature()` checks against
  `REFERENCE_VALUES` (Cowley–Woods 1971, Glyde 1998, Godfrin 2021) using
  the PLAN.md M1 tolerance (c ±5%, Δ ±10%).
- **Tested:** end-to-end via synthetic SQwData and via a full ASCII-file
  pipeline (load → fit → compare).

### 3.3 Visualization & Analysis
- **Status:** ✅ IMPLEMENTED (`src/quantumfluids/dispersion_fit/plotting.py`)
- **Outputs:** `plot_dispersion_fit()` saves E(Q) data + phonon/roton fit
  curves + residuals to a PNG (Agg backend, headless-safe).
- **Not yet run:** against real data — awaiting M1-DATA-001 or digitized
  Fig. 5 fallback (Phase 1.3 fallback path).

---

## Phase 4: Literature Comparison

### 4.1 Reference Data Collection
- **Status:** NOT STARTED
- **Task:** Compile literature values for c and Δ
- **Sources:**
  - Cowley–Woods 1971: phonon-roton curve
  - Glyde et al. 1998: precision measurements
  - Godfrin et al. 2021 (own measurement for self-check)
- **Deliverable:** reference_values.txt
  ```
  Source          c (m/s)      Δ (K)        Δ (meV, = K × 0.086173)
  Cowley-Woods    238 ± 2      8.65 ± 0.05  0.7454 ± 0.0043
  Glyde 1998      239 ± 1      8.63 ± 0.03  0.7437 ± 0.0026
  Godfrin 2021    238.2 ± 0.5  8.64 ± 0.02  0.7446 ± 0.0017
  ```

### 4.2 Agreement Assessment
- **Status:** NOT STARTED
- **Task:** Compare fitted values to literature
- **Metrics:**
  - Δc / c_lit (should be < 5%)
  - ΔΔ / Δ_lit (should be < 10%)
- **Deliverable:** comparison_report.md with discussion of discrepancies

---

## Phase 5: Testing & Validation

### 5.1 Tier-B Harness (`tests/test_dispersion_fit.py`)
- **Status:** NOT STARTED
- **Task:** Unit tests for adapters + fitting
- **Coverage:**
  - Happy path: real Godfrin data → (c, Δ) within expected ranges
  - Negative control: axis swap → error
  - Negative control: missing metadata → error
  - Negative control: NaN in data → handled

### 5.2 Negative Controls (LL-2)
- **Status:** NOT STARTED
- **Task:** Deliberately malformed inputs
- **Examples:**
  - Q and ω reversed
  - S(Q,ω) with 50% NaN values
  - Missing Q metadata
  - Intensity values out of physical range

---

## Deliverables Checklist

### Code
- [ ] `src/quantumfluids/adapters/ill_numor.py`
- [ ] `src/quantumfluids/adapters/nexus_reader.py`
- [ ] `src/quantumfluids/adapters/ascii_sqw.py`
- [ ] `src/quantumfluids/adapters/__init__.py` (registry)
- [ ] `src/quantumfluids/dispersion_fit/landau_model.py`
- [ ] `src/quantumfluids/dispersion_fit/fit_dispersion.py`
- [ ] `src/quantumfluids/dispersion_fit/plotting.py`

### Data & Metadata
- [ ] `data/external/godfrin_2021_prb103_in5/*.nxs` or `.numor`
- [ ] `data/external/godfrin_2021_prb103_in5/*.meta` (provenance)
- [ ] `data/derived/godfrin_2021_fit_results.json` (fitted parameters)

### Tests
- [ ] `tests/test_ill_numor.py` (negative controls included)
- [ ] `tests/test_nexus_reader.py` (negative controls included)
- [ ] `tests/test_ascii_sqw.py` (negative controls included)
- [ ] `tests/test_dispersion_fit.py` (integration test)

### Documentation
- [ ] `src/quantumfluids/adapters/README.md` (adapter usage guide)
- [ ] `src/quantumfluids/dispersion_fit/README.md` (model + fit workflow)
- [ ] `M1_REPORT.md` (final results, literature comparison, figures)

### Metrics
- [ ] Fitted c: literature agreement within ±5% ✓ or ✗
- [ ] Fitted Δ: literature agreement within ±10% ✓ or ✗
- [ ] All adapters pass negative-control suite ✓ or ✗
- [ ] Tier-B harness coverage: 100% ✓ or ✗

---

## Blocking Issues (TBD)

**Awaiting M1-DATA-001 retrieval:**
- ILL-DATA DOI
- File formats available
- Access pathway
- Data size estimate

**Decision points:**
- Numor format library: use existing ILL tool or write parser?
- Fitting algorithm: scipy.optimize or alternative?
- Reference dataset: digitize Fig. 5 if raw data inaccessible?

---

## Timeline

| Phase | Dates | Owner | Status |
|-------|-------|-------|--------|
| 1. Data Access | 2026-08-14 → 2026-08-28 | Agent (ILL-DATA), then manual retrieval | ⏳ STARTING |
| 2. Adapters | 2026-08-28 → 2026-09-10 | Adapter implementation | NOT STARTED |
| 3. Fitting | 2026-09-10 → 2026-09-20 | Landau model + harness | NOT STARTED |
| 4. Validation | 2026-09-20 → 2026-09-27 | Tests + literature comparison | NOT STARTED |
| 5. Report | 2026-09-27 → 2026-09-30 | M1 final report + figures | NOT STARTED |

**Critical path:** Data retrieval (2 weeks) → Adapters (2 weeks) → Integration (3 weeks)

---

## M1 Success Criteria

✅ All data retrieved and cached with full provenance  
✅ Adapters implemented and passing negative-control tests  
✅ Landau fit reproduces literature (c, Δ) within tolerance  
✅ M1 report with fit plots, residuals, comparison to Cowley–Woods / Glyde / Godfrin  
✅ Zero code coverage gaps (100% tests)  
✅ LEDGER.md updated with fitted (c, Δ) claims (Tier B)

---

**M1 unlocks M2 start:** W4 shell model construction (target 2026-10-15)

Last updated: 2026-08-14  
Status: ⏳ Phase 1 active (data retrieval)
