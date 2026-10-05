# Literature review, October 2026: eight themes, a local vector database, and what changes

Date 2026-10-05. Eight parallel reviews (alphaXiv full texts, Crossref/OpenAlex records for pre-arXiv classics),
each with a quota of pre-2000 and pre-1985 papers. Manifests, PDFs and the vector database live outside the repo,
on the large disk: `/mnt/data/home/xavkal/quantumfluids-data/litdb/` (`manifests/`, `pdfs/`, `chroma/`). Tool:
`scripts/litdb.py` (`fetch`, `ingest`, `query`, `stats`; run with `litdb/venv/bin/python`).

## What is in the database

| theme (manifest) | papers | pre-2000 | pre-1985 | gaps |
|---|---|---|---|---|
| `bkt_theory_finite_size` | 70 | 39 | 17 | 8 |
| `vortex_dynamics_friction` | 75 | 23 | 11 | 8 |
| `cfield_2d_bose_gas` | 96 | 21 | 10 | 8 |
| `onsager_point_vortex_2dqt` | 112 | 33 | 17 | 7 |
| `coarsening_quench_kz` | 102 | 35 | 6 | 8 |
| `helium_films_dynamic_kt` | 113 | 66 | 36 | 8 |
| `stiffness_response_theory` | 87 | 38 | 24 | 8 |
| `rigorous_and_formalized_physics` | 113 | 33 | 16 | 7 |
| `seed_prior_reviews` | 5 | 0 | 0 | 0 |

773 manifest entries, 643 distinct titles; 288 before 2000, 137 before 1985, oldest 1876 (Kirchhoff, secondary).
**382 distinct arXiv ids, all 382 verified against the arXiv API by title match — no mismatch, none not found.**
387 PDFs (746 MB; two open links returned 404). Collection `qf_literature`: 27 831 entries = 773 paper cards
(summary, key numbers, open questions, relevance) + 62 gap entries + 26 996 full-text chunks, embedded locally
(ONNX MiniLM-L6-v2, cosine). Papers without an open PDF (most pre-arXiv classics) are present as cards only, written
from the abstract or from the citing paper; each card records how it was verified and how deeply it was read.

Limits, stated: read depth is "abstract" for roughly three quarters of the entries; pre-arXiv classics were
verified through DOI records (Crossref/OpenAlex), not publisher pages; reviewers' own inferences are marked as such
in the cards. A handful of seed papers could not be verified and were left out rather than entered from memory.

## Findings that change statements already made in this repository

1. **The flow invariant has been tested before.** Prokof'ev & Svistunov (2002) checked the size independence of
   the Kosterlitz invariant in the classical lattice |ψ|⁴ model (L = 64–512), and Thamm et al. (PRL 2025) in 1D
   Bose–Hubbard. `KTFlow.lean` remains the first *formal* statement; no "first test" of the invariant is to be
   claimed numerically.
2. **Our "29 % excess" of `nλ²` at BKT is probably the Rayleigh–Jeans ultraviolet logarithm.** The
   classical-to-quantum conversion of Prokof'ev, Ruebenacker & Svistunov (2001, Eqs. 10–12) applied to a sharp
   cutoff gives `n_cλ² = ln(380/g̃) + ln(E_cut/T)` (re-derived here: the ideal-gas tails differ by
   `(mT/2π) ln(T/E_cut)`). For `k_cut = π`: `T_BKT = 0.811`, `nλ² = 7.75`, against the measured 0.821 and 7.65.
   Caveats: `mg = 1` is not small; Heinen & Gasenzer (2023) find 260 ± 12 instead of 380. Becomes hypothesis H09.
   `causal_topology.tex` says the excess is "still not measured" — to be amended if H09's test passes.
3. **The single box-scale pair has precedents.** Chu & Williams (2001) predicted a post-quench stiffness
   depression from surviving large pairs and asked for simulations; Fiory, Hebard & Glaberson (1983) saw resistance
   from a single free vortex. Our CLAIM-069 diagnosis is the conservative-dynamics, finite-box instance; cite both.
4. **The charge structure factor is named.** An et al. (arXiv:2608.17012) measure a "topological charge structure
   factor" in steady holographic turbulence. Our claim narrows to its time-resolved use in a closed system.
5. **Friction pre-registration needs three corrections before production** (`PGPE_FRICTION_PREREG.md`):
   the plane dipole law is used where the torus law applies (Zhu 2023; `d₀/L` up to 0.25); a product-ansatz dipole
   radiates (Rorai, Sreenivasan & Fisher 2013), which explains the excluded pilot's outward drift; mobility may
   grow as `ln d` (Nam et al. 2012), which criterion F1's window [1.5, 2.5] cannot separate from `d²`. Published
   friction-law coefficients have been wrong before (Miot on Lin–Xin): re-derive in our units.
6. **Weiss–McWilliams "non-ergodicity" is an ensemble artefact** (Esler 2017): the torus thermometer calibration
   should fix the vortex polarisation. Affects `vortex_thermometer_canonical.py` (round 3) — recorded, not redone.
7. **The k = 0 normal-density estimator is identically zero in our runs** (fixed total momentum), so only the
   `k → 0⁺` current-correlator form is meaningful; no microcanonical fixed-winding formula for `n_s` exists in
   the literature (Foster 2010 applies the grand-canonical one unchanged).
8. **Formalization moved fast in 2026** (Landau damping, 2D Galerkin Navier–Stokes, De Giorgi–Nash–Moser
   formalised by agents in days to weeks). A Lean theorem alone is no longer a durable contribution; theorems tied
   to measured data are. No machine-checked statement on BKT, the Coulomb gas or vortices was found outside this
   repository.

## The gaps that became hypotheses

See `exploration/autoresearch/hypotheses.json` (ten hypotheses, each with its literature support) and
`docs/designs/AUTORESEARCH_SELECTION_2026-10.md` for the selection.
