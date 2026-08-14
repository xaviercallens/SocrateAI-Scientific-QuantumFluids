# CLAIM LEDGER: SocrateAI-Scientific-QuantumFluids

**Purpose:** Track all empirical/theoretical claims made in this stream. Every claim must have:
1. A clear statement
2. Evidentiary tier (A=citation-verified, B=unit-testable, C=narrative/speculation)
3. Status (PENDING, VERIFIED, DISPUTED, RETRACTED)
4. Source references (LITERATURE_LEDGER.md entry or unit test ID)
5. Date filed and last-updated timestamp

---

## Template entry

```
[CLAIM-001] [TIER-A] [PENDING]
Statement: "The Landau two-parameter form (c, Δ) fits the Godfrin et al. 2021 
           dispersion data to within ±5% on phonon branch."
Source: LITERATURE_LEDGER.md#Godfrin2021, test:dispersion_fit::test_landau_fit
Filed: 2026-08-14
Updated: 2026-08-14
Notes: Blocking M1 definition-of-done.
```

---

## Current claims

```
[CLAIM-001] [TIER-C] [VERIFIED]
Statement: "Fitting the roton branch (Landau parabolic form) to a hand-digitized
           version of Fig. 5 (Godfrin & Krotscheck 2022, [LIT-001], representing
           Godfrin et al. 2021 [LIT-002] data) recovers Delta = 0.7306 +/- 0.0040 meV
           and Q_m = 1.9192 +/- 0.0044 Angstrom^-1, within 1.9% and 0.3% of the
           literature values respectively."
Source: M1_REPORT.md, data/derived/godfrin_2021_fit_results.json,
        test:test_dispersion_fit.py::test_roton_fit_recovers_known_delta_and_qm
Filed: 2026-08-14
Updated: 2026-08-14
Notes: Tier C (digitized fallback data, not raw instrument data — see
       M1_DATA_ACCESS_STRATEGY.md). Validates landau_model.fit_roton_branch
       against real published curve shape, not just synthetic round-trip data.
```

```
[CLAIM-002] [TIER-C] [VERIFIED]
Statement: "The phonon-branch fit (linear form) applied to the same digitized
           Fig. 5 data does NOT recover the literature sound velocity
           c = 1.568 meV*Angstrom (238 m/s); fitted c = 1.10-1.15 meV*Angstrom
           across phonon_q_max in [0.2, 0.6], a stable ~27% deficit."
Source: M1_REPORT.md ("Why the roton fit succeeds and the phonon fit does not")
Filed: 2026-08-14
Updated: 2026-08-14
Notes: Attributed to near-origin visual-reading precision limits of hand
       digitization, not a defect in fit_phonon_branch (which the roton-branch
       success and synthetic recovery tests both support). Filed as a genuine
       negative finding — no adjustment was made to force agreement. Awaiting
       M1-DATA-001 (raw/reduced instrument data) to re-test on Tier-B data.
```

```
[CLAIM-003] [TIER-B] [VERIFIED]
Statement: "Fitting the Landau phonon (linear) and roton (parabolic) forms
           to Godfrin et al. (2021)'s own published dispersion-curve table
           ([LIT-002], arXiv:2012.09067 ancillary file DispersionP0allRange.txt)
           recovers c = 1.5716 +/- 0.0003 meV*Angstrom (0.24% from literature,
           window Q<0.05 Angstrom^-1) and Delta = 0.7442 +/- 0.0005 meV
           (0.04% from literature, window |Q-1.9|<0.2 Angstrom^-1) -- both
           within the M1 tolerance (c +/-5%, Delta +/-10%; PLAN.md)."
Source: M1_REPORT.md Part 1, data/derived/godfrin_2021_ancillary_fit_results.json,
        data/external/godfrin_2021_arxiv_ancillary/DispersionP0allRange.txt.meta,
        test:test_godfrin_ancillary.py (10 tests)
Filed: 2026-08-14
Updated: 2026-08-14
Notes: Tier B — author-published, exact tabulated data, not raw ILL numor
       (M1-DATA-001 still open) but a legitimate substitute for M1's stated
       objective. Supersedes CLAIM-002 (Tier-C phonon-fit failure) for
       practical purposes; CLAIM-002's root-cause diagnosis was confirmed
       correct by this result's fit-window sensitivity scan. M1 milestone
       objective (PLAN.md) met.
```

---

## Claim status history

| Claim ID | Status → | Date | Notes |
|---|---|---|---|
| CLAIM-001 | PENDING → VERIFIED | 2026-08-14 | Roton branch fit, digitized Fig. 5 |
| CLAIM-002 | PENDING → VERIFIED | 2026-08-14 | Confirmed negative finding: phonon branch fit fails on digitized data; root cause documented in M1_REPORT.md |
| CLAIM-003 | PENDING → VERIFIED | 2026-08-14 | Both c and Delta recovered within tolerance on Tier-B author-published data; CLAIM-002's diagnosis confirmed correct |

---

## Governance notes

- Claims start PENDING on filing.
- Tier-A claims require successful literature retrieval + citation in LITERATURE_LEDGER.md.
- Tier-B claims require passing unit test (referenced in LEDGER entry).
- Tier-C claims are narrative only; no verification required, but must be explicitly labeled (docs/narrative/).
- Disputes are recorded in LEDGER and logged with rationale.
- Retractions are never deleted; status changed to RETRACTED with explanation.
