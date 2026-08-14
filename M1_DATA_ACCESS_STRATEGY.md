# M1 Data Access Strategy

**Original blocking issue:** Godfrin et al. 2021 raw experimental data (ILL-DATA DOI) not web-indexed  
**Status update (2026-08-14): no longer M1-blocking.** Godfrin et al.
(2021)'s own arXiv preprint (2012.09067) publishes an exact ancillary
dispersion-curve table (`DispersionP0allRange.txt`), which was retrieved
directly and used as Tier-B data — both M1 fit metrics passed decisively
(see M1_REPORT.md Part 1). The raw ILL numor request below remains worth
pursuing for **M2/M3** (which may need full S(Q,ω) intensity data, not
just the extracted ω(Q) curve the ancillary file provides) and for **M4**
(relationship-building ahead of outreach), but M1's own objective is met
without it. The pathways below are unchanged and still valid for that
ongoing, now-lower-priority purpose.

---

## Investigation Results

**Paper:** H. Godfrin et al., PRB 103:104516 (2021)  
**DOI:** 10.1103/PhysRevB.103.104516  
**Experiment:** IN5 (ILL beamline), superfluid ⁴He, multiple pressures  
**Data Status:** Restricted — "available upon request" model

### Why Not Web-Indexed?

1. **ILL Data Portal (doi.ill.fr)** — Does NOT publicly index all experimental datasets
2. **Proposal-Level Storage** — Raw data archived under proposal codes (9-0X-XXXX format), accessible via:
   - Direct ILL staff access
   - Researcher institutional affiliation
   - Author request/collaboration

3. **Publication Model** — PRB paper includes supplementary *processed* data (arXiv ancillary files), not raw numeror files

---

## Access Pathways (Priority Order)

### Pathway 1: Direct Author Contact (HIGHEST PRIORITY)

**Target:** H. Godfrin (corresponding author), Institut Néel, CNRS, Grenoble

**Contact Info:**
- Affiliation: Institut Néel, CNRS & Université Grenoble Alpes
- Email: henry.godfrin@neel.cnrs.fr (LIKELY)
- Webpage: https://www.neel.cnrs.fr/ (search for Godfrin)

**Message Template:**
```
Subject: Data Access Request — Godfrin et al. PRB 103:104516 (2021)

Dear Dr. Godfrin,

We are reproducing your dispersion-relation measurements for the SocrateAI-Scientific-QuantumFluids project, which aims to express quantum-fluid physics in a dual-scale regularization framework.

We seek access to the raw IN5 neutron-scattering data (numor files or processed NeXus format) from your PRB 103:104516 publication (2021). This data is essential for our M1 milestone: reproducing the Landau two-parameter fit (c, Δ) as a calibration exercise.

Could you provide:
1. The persistent ILL-DATA DOI (10.5291/ILL-DATA.xxxxx)
2. Guidance on accessing raw numor files (format preferences)
3. Any processed S(Q,ω) datasets you would recommend for benchmarking

We will cite your work prominently and can provide our results for comparison.

Thank you for your time.

Best regards,
Xavier Callens
SocrateAI-Scientific-QuantumFluids Project
```

**Timeline:** 1-2 weeks response expected (academic email response time)

---

### Pathway 2: ILL Data Portal Direct Search

**URL:** https://doi.ill.fr/  
**Search Strategy:**
1. Filter by: Beamline = IN5
2. Filter by: Proposal Year = 2019-2020 (likely proposal cycle for 2021 publication)
3. Search: Authors = "Godfrin" OR "Beauvois" OR "Ollivier"
4. Look for DOI format: 10.5291/ILL-DATA.9-0X-XXXX

**If Found:**
- DOI directly accessible (may require registration)
- Can request institutional affiliation or guest account

**If Not Found:**
- Email data-portal@ill.fr with citation and authors
- Reference: PRB 103:104516, IN5 beamline, 2019-2020 cycle

---

### Pathway 3: Secondary Contacts at ILL

**Personnel:**
- **B. Fåk** (co-author, IN5 beamline scientist) — bernard.fak@ill.fr
- **J. Ollivier** (co-author, ILL staff) — jerome.ollivier@ill.fr
- **ILL Data Portal Team** — data-portal@ill.fr

**Advantage:** ILL staff can expedite access and explain archive structure

---

### Pathway 4: Fallback — Digitize Fig. 5 (Tier C)

**If data is completely inaccessible after 4 weeks:**

1. **Extract Fig. 5 data** from Godfrin & Krotscheck (2022) review (LIT-001, OPEN ACCESS)
   - Fig. 5 shows phonon-roton curve with multiple literature sources
   - Include: Cowley–Woods 1971, Glyde et al. 1998, Godfrin et al. 2021
   - Red points = Godfrin et al. 2021 (the target dataset)

2. **Digitize using:**
   - WebPlotDigitizer (online tool) or Engauge Digitizer
   - Extract (Q, ω) coordinates from figure
   - Assign uncertainties (±10% on ω, ±5% on Q from visual inspection)

3. **Label as Tier C:**
   - data/derived/godfrin_2021_digitized_fig5.csv
   - Add metadata: "Digitized from Godfrin & Krotscheck 2022 Fig. 5; see LITERATURE_LEDGER [LIT-001]"
   - Use for fitting calibration only (not for publication claims)

4. **Proceed with M1 objectives:**
   - Reproduce Landau fit on digitized data
   - Validate against literature (Cowley–Woods, Glyde)
   - Document limitations ("Tier C steering data, digitized")

---

## Timeline & Contingency

| Week | Action | Status |
|------|--------|--------|
| **Aug 14–21** | Contact H. Godfrin + ILL data portal | ⏳ IN PROGRESS |
| **Aug 21–28** | Await response (1-2 week turnaround) | PENDING |
| **Aug 28** | Decision point: data approved OR fallback activated | DECISION |
| **Aug 28 – Sep 10** | Phase 2 adapters (works with either raw or digitized data) | TBD |
| **Sep 10 – 30** | Fitting + validation (same regardless of data source) | TBD |

---

## M1 Flexibility

**Key insight:** Adapters and Landau fitting harness work with either:
- **Raw IN5 numor files** (if ILL access granted) → Full Tier B validation
- **Digitized Fig. 5 data** (if access denied) → Tier C calibration, can still reproduce published results

**No go/no-go decision** needed until Aug 28. Phase 2 can start in parallel.

---

## Related: M4 Outreach

**Alignment:** This data access request naturally leads into M4 (Godfrin correspondence):
- Current message: "We're reproducing your data for calibration"
- Follow-up (M3): "Our W4 experiment results, how do they compare?"
- Outcome: Natural collaboration pipeline (M4 objective)

**See:** docs/GODFRIN_CORRESPONDENCE.md for outreach log template

---

## Success Criteria

✅ ILL-DATA DOI retrieved and data accessible, OR  
✅ Fallback (digitized Fig. 5) prepared and M1 proceeds on schedule

**Target:** Unblock Phase 2 (adapters) by August 28, 2026

---

**Created:** 2026-08-14  
**Status:** Awaiting author response (~1 week expected)  
**Owner:** M1 phase coordinator
