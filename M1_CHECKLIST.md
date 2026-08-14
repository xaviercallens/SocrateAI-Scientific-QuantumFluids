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
- **Status:** NOT STARTED
- **Task:** Parse ILL binary numor format
- **Requirements:**
  - Read instrument metadata (beamline, sample, geometry)
  - Extract (Q, ω, intensity) grid
  - Handle errors gracefully
- **Tests:** tests/test_ill_numor.py
  - Happy path: valid numor → correct shape, values
  - Negative control: corrupted header → error
  - Negative control: missing file → error

### 2.2 NeXus Reader (`src/quantumfluids/adapters/nexus_reader.py`)
- **Status:** NOT STARTED
- **Task:** Parse HDF5 NeXus structure for inelastic neutron scattering
- **Requirements:**
  - Standard NeXus entry point paths
  - Extract Q, ω, S(Q,ω) datasets
  - Preserve metadata (sample, instrument)
- **Tests:** tests/test_nexus_reader.py
  - Happy path: valid .nxs → correct extraction
  - Negative control: axis swap → error
  - Negative control: missing dataset → error

### 2.3 ASCII Reader (`src/quantumfluids/adapters/ascii_sqw.py`)
- **Status:** NOT STARTED
- **Task:** Parse plain-text S(Q,ω) data (space/comma-separated)
- **Requirements:**
  - Auto-detect delimiter
  - Column header parsing (Q, omega, S, dS)
  - Skip comments (#)
- **Tests:** tests/test_ascii_sqw.py
  - Happy path: valid ASCII → correct arrays
  - Negative control: malformed columns → error
  - Negative control: NaN in critical columns → error or flag

### 2.4 Adapter Registry & Testing
- **Status:** NOT STARTED
- **Task:** Consolidate adapters in `src/quantumfluids/adapters/__init__.py`
- **Negation Controls (LL-2 inheritance):**
  - Axis swap detection
  - Metadata consistency checks
  - NaN/inf handling policy

---

## Phase 3: Dispersion-Fit Implementation

### 3.1 Landau Model (`src/quantumfluids/dispersion_fit/landau_model.py`)
- **Status:** NOT STARTED
- **Task:** Implement two-parameter Landau model
- **Physics:**
  ```
  E(q) = c·q + Δ·(1 + (q/q_m)²)^{1/3}
  ```
  where:
  - c: sound velocity
  - Δ: roton gap
  - q_m: roton momentum (~1.9 Å⁻¹ in ⁴He)
- **Implementation:**
  - Nonlinear least-squares fit (scipy.optimize.curve_fit)
  - Parameter bounds (c > 0, Δ > 0)
  - Covariance matrix → confidence intervals

### 3.2 Fitting Harness (`src/quantumfluids/dispersion_fit/fit_dispersion.py`)
- **Status:** NOT STARTED
- **Task:** End-to-end fit workflow
- **Steps:**
  1. Load S(Q,ω) data via adapters
  2. Identify roton peak (ω vs. Q) manually or auto-detect
  3. Extract phonon branch (low-Q, low-ω) and roton branch (high-Q)
  4. Fit c to phonon region
  5. Fit Δ, q_m to roton region
  6. Compute residuals and uncertainties

### 3.3 Visualization & Analysis
- **Status:** NOT STARTED
- **Task:** Plotting harness for fit results
- **Outputs:**
  - E(q) experimental points + fitted curve
  - Residuals (experiment - model)
  - Comparison to literature (Cowley–Woods, Glyde, etc.)

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
  Source          c (m/s)    Δ (meV)
  Cowley-Woods    238 ± 2    8.65 ± 0.05
  Glyde 1998      239 ± 1    8.63 ± 0.03
  Godfrin 2021    238.2 ± 0.5 8.64 ± 0.02
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
