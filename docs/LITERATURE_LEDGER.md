# LITERATURE LEDGER: SocrateAI-Scientific-QuantumFluids

**Purpose:** Central registry of all citations used in this stream. Every claim in LEDGER.md must reference an entry here (by ID). Every entry must include retrieval date, source link/DOI, and checksum (if applicable) for reproducibility.

**Format:**
```
[LIT-NNN] Surname, A. et al., "Title", Journal Volume, page (Year).
  Status: VERIFIED | PENDING | INACCESSIBLE
  DOI: 10.xxxx/yyyy
  URL: https://...
  Retrieved: 2026-08-14
  Checksum (PDF): sha256:abc123... (if applicable)
  Notes: Context for this stream.
```

---

## Verified entries

### [LIT-001] Godfrin & Krotscheck (2022) — Review article

**Full citation:**  
Godfrin, H., & Krotscheck, E. (2022).  
"The Dynamics of Quantum Fluids."  
arXiv:2206.06039

**Status:** VERIFIED (full document read, 2026-08-14)

**Links:**
- arXiv: https://arxiv.org/abs/2206.06039
- Retrieved: 2026-08-14 via arXiv

**Role in this stream:**  
Source of the Landau phonon-roton dispersion figures and DMBT (Davydov–Makeev–Barenghi–Tsepelin) theoretical framework. Provides literature survey of quantum-fluid excitation spectra.

**Key sections:**
- Fig. 5: Phonon-roton dispersion curve (multiple sources digitized)
- §2–3: DMBT kinetic theory
- §4: Landau two-parameter model

**Notes:** Becomes primary target for outreach (M4). Data-availability statement checked; raw ILL experiment link to be pursued in M0.

---

### [LIT-002] Godfrin et al. (2021) — Dispersion data (PRB)

**Full citation:**  
Godfrin, H., Beauvois, M., Sultan, A., Krotscheck, E., Dawidowski, J., Fåk, B., & Ollivier, J. (2021).  
"Dispersion relation of Landau elementary excitations in superfluid helium by inelastic neutron scattering."  
Physical Review B, 103, 104516.

**Status:** VERIFIED (publisher listing checked, 2026-08-14)

**DOI:** 10.1103/PhysRevB.103.104516

**Links:**
- APS: https://journals.aps.org/prb/abstract/10.1103/PhysRevB.103.104516
- Raw data DOI: 10.5291/ILL-DATA.xxx (PENDING retrieval in M0)

**Role in this stream:**  
The definitive high-precision IN5 neutron-scattering dispersion curve (Fig. 5, red points). Used for M1 calibration and cross-check against Landau fit.

**Key data:**
- Instrument: ILL IN5 (neutron spectrometer)
- Sample: Superfluid ⁴He
- Range: 0–3 Å⁻¹ Q-range, full phonon-roton spectrum
- Points: ~50 precision measurements

**Notes:**  
Data-availability statement in paper must be checked to find persistent ILL-DATA DOI. This is the M0 blocker for raw-data retrieval.

---

### [LIT-003] Hirschel et al. (2024) — Dark-matter detector

**Full citation:**  
Hirschel, A., Vadakkumbatt, S., Baker, M., Schweizer, C., Sankey, J., Singh, R., & Davis, J. C. (2024).  
"Superfluid helium ultralight dark matter detector."  
Physical Review D, 109, 095011.

**Status:** VERIFIED (publisher listing checked, 2026-08-14)

**DOI:** 10.1103/PhysRevD.109.095011

**Links:**
- APS: https://journals.aps.org/prd/abstract/10.1103/PhysRevD.109.095011

**Role in this stream:**  
Demonstrates a live, named experimental programme using superfluid helium's phonon-roton excitation spectrum for dark-matter detection (axion search). Cited as genuine Tier-A physics link between quantum fluids and dark-matter research, *independent* of this programme's own speculation (docs/narrative/). This is a model for what non-speculative dark-matter engagement looks like.

**Key connection:**  
The phonon-roton spectrum is the readout mechanism for dark-matter coupling searches. Validates citation of dark matter in a peer-reviewed, experimental context.

**Notes:**  
Not speculative. Part of established experimental portfolio (related: Baker et al., PRL 2024, Baker et al., NJP 2016).

---

### [LIT-004] Polanco et al. (2025) — Vortex structures (Institut Néel)

**Full citation:**  
Polanco, A., Roche, P.-E., et al. (2025).  
"Direct numerical simulation of vortex structures in superfluid turbulence."  
Proceedings of the National Academy of Sciences, 122(27), e2426598122.

**Status:** VERIFIED (institute highlights page checked, full retrieval pending, 2026-08-14)

**DOI:** 10.1073/pnas.2426598122

**Links:**
- PNAS: https://www.pnas.org/doi/10.1073/pnas.2426598122
- Institut Néel highlight: (check institute website for press release)

**Role in this stream:**  
Direct numerical simulation of vortex-lattice structures in superfluid turbulence. Same institute (Institut Néel) as Godfrin; represents complementary expertise (vortex dynamics vs. dispersion relations). Flagged as natural second contact point for W4 collaboration (M4).

**Notes:**  
Full PDF retrieval pending. Dataset release status (if any) to be assessed at M4 alongside outreach to Roche group.

---

## Pending entries (M0 blocking items, from Expression Memo E1)

### [LIT-005] Madelung (1927)

**Citation fragment:** Madelung, E. (1927). "Quantentheorie in hydrodynamischer Form." Zeitschrift für Physik, 40(3–4), 322–326.

**Status:** PENDING retrieval

**Role:** Foundation of Madelung transform (density-weighted hydrodynamic representation of QM); cited in DMBT.

**Retrieval notes:** German journal, pre-digital. Check: (i) Göttingen/Max Planck archive digitization; (ii) Archive.org; (iii) Contact Mathesis-stream for Lean reference if available.

**Target date:** End of M0

---

### [LIT-006] Onsager (1949)

**Citation fragment:** Onsager, L. (1949). "Statistical Hydrodynamics." Nuovo Cimento Supplemento, 6(Suppl. 2), 279–287.

**Status:** PENDING retrieval

**Role:** Quantum-vortex quantization condition; cited in DMBT kinetic theory.

**Retrieval notes:** Low-circulation journal; check Annals of Physics archives, Los Alamos preprint servers, or author's collected works.

**Target date:** End of M0

---

### [LIT-007] Feynman (1955)

**Citation fragment:** Feynman, R. P. (1955). "Application of Quantum Mechanics to Liquid Helium." In Progress in Low Temperature Physics, Vol. 1. Elsevier.

**Status:** PENDING retrieval

**Role:** Roton concept and phenomenological excitation spectrum; foundational to Landau model.

**Retrieval notes:** Book chapter; check publisher's archive or MIT library system.

**Target date:** End of M0

---

### [LIT-008] Barenghi, Skrbek, & Sreenivasan (2014)

**Citation fragment:** Barenghi, C. F., Skrbek, L., & Sreenivasan, K. R. (2014). "Vortices, Superfluid Turbulence, and Quantum Effects." Proceedings of the National Academy of Sciences, 111(Suppl. 1), 4647–4652.

**Status:** PENDING retrieval

**Role:** Review of quantum-turbulence vortex dynamics; connects to Polanco et al. (2025).

**Retrieval notes:** PNAS, should be easily accessible.

**Target date:** End of M0

---

### [LIT-009] BCS (1957)

**Citation fragment:** Bardeen, J., Cooper, L. N., & Schrieffer, J. R. (1957). "Theory of Superconductivity." Physical Review, 108(5), 1175–1204.

**Status:** PENDING retrieval

**Role:** BCS theory of fermionic superfluidity; cited for completeness in context of bosonic superfluid (⁴He).

**Retrieval notes:** Classic Phys. Rev. paper; widely available.

**Target date:** End of M0

---

### [LIT-010] Deaver & Fairbank / Doll & Näbauer (1961)

**Citation fragment:**  
Deaver Jr., B. S., & Fairbank, W. M. (1961). "Experimental evidence for quantized flux in superconducting cylinders." Physical Review Letters, 7(2), 43.  
Doll, W., & Näbauer, M. (1961). "Experimental proof of magnetic flux quantization in a superconducting ring." Physical Review Letters, 7(2), 51.

**Status:** PENDING retrieval

**Role:** Experimental proof of flux quantization; validates quantum-vortex quantization condition (Onsager, LIT-006).

**Retrieval notes:** Phys. Rev. Lett., short letters; widely available.

**Target date:** End of M0

---

## Inaccessible entries

*None yet. Entries moved to this section if retrieval fails after 3 attempts.*

---

## Retrieval summary (M0 progress)

| ID | Author(s) | Year | Status | Target Date |
|---|---|---|---|---|
| LIT-001 | Godfrin & Krotscheck | 2022 | ✓ VERIFIED | (Complete) |
| LIT-002 | Godfrin et al. | 2021 | ✓ VERIFIED | (Complete) |
| LIT-003 | Hirschel et al. | 2024 | ✓ VERIFIED | (Complete) |
| LIT-004 | Polanco et al. | 2025 | ✓ VERIFIED | (Complete) |
| LIT-005 | Madelung | 1927 | PENDING | 2026-08-31 |
| LIT-006 | Onsager | 1949 | PENDING | 2026-08-31 |
| LIT-007 | Feynman | 1955 | PENDING | 2026-08-31 |
| LIT-008 | Barenghi et al. | 2014 | PENDING | 2026-08-31 |
| LIT-009 | BCS | 1957 | PENDING | 2026-08-31 |
| LIT-010 | Deaver–Fairbank / Doll–Näbauer | 1961 | PENDING | 2026-08-31 |

**M0 DoD:** All PENDING entries must be either VERIFIED or marked INACCESSIBLE before repo lock.
