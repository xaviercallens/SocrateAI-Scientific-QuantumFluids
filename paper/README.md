# Papers

**Newest (September 2026):**
- `cosmology_sectors.tex` — *Sectors in the sky* (proposal: what 'the sector is the cause' says about wave dark matter, flux-lattice
  dark energy and the K3 charge lattice; three Lean identities; transfer rule printed; no cosmological number). Build: `latexmk -pdf cosmology_sectors.tex`.
- `duality_sector.tex` — *Duality is a structure; the sector is the cause* (T-duality on the compact-boson sectors,
  machine-checked; the measured invariant; when a self-dual point is physical). Build: `latexmk -pdf duality_sector.tex`.
- `sector_temperature.tex` — *Topological sectors carry their own temperature* (proposal: hypothesis F, the mediant
  theorem, the torus vortex thermometer, external tests on Gauthier 2019 and Christodoulou 2021 data). Build: `latexmk -pdf sector_temperature.tex`.
- `causal_topology.tex` — *Does topology causally influence physics? Winding numbers as difference-makers in a
  two-dimensional Bose gas* (thought experiments, the 28-theorem chain, the energy-matched intervention).
  Figures: `.venv/bin/python make_figures_causal.py`. Build: `latexmk -pdf causal_topology.tex`.
- `astro_topological_measurement.tex` — *Topological charge as a measurement principle for astrophysical U(1)
  phase fields* (methods paper: five principles with their diagnostics, three settings, protocol,
  pre-registration template; no astrophysical number claimed). Build: `latexmk -pdf astro_topological_measurement.tex`.

**Library paper:** `quantumfluids_lean4.tex` — *Formalizing quantum-fluid structure in Lean 4: a machine-checked
library, what the formalization caught, and what it could not* (September 2026). Build: `latexmk -pdf quantumfluids_lean4.tex`.

**Superseded:** `quantumfluids_tdual.tex` — the earlier report. Its shell-model measurement-programme
material (M3) remains valid, but its sections on the second invariant and the dual length present as
findings two results since withdrawn (`../RETRACTIONS.md`). Kept for the record; do not cite as current.

---

# Paper: T-dual–motivated dispersive regulator for a dyadic shell model

## Build

```bash
# figures (regenerated from the repository's own modules; ~10 min total)
PYTHONPATH=../src python3 make_figures.py            # or: liouville | degeneracy | scatter

# paper
latexmk -pdf quantumfluids_tdual.tex
```

Produces `quantumfluids_tdual.pdf` (10 pp, A4).

## What this paper is

A **mixed positive/negative report**. It is deliberately not written as a
success story, because the stream's measurement programme failed and the
failure is the more transferable result.

**Stands** (analytic / formal / deterministic):
- structural obstruction: a real-amplitude shell model cannot host a dispersive regulator
- conjugated complexification: exact energy conservation, exact reduction to the real model
- **Liouville property** — the complexified flow is volume-preserving, the real one is not
- conserving-seam criterion `Re(conj(v_N)²·v_{N+1}) = 0`, and the GPE-like family it admits
- eight Lean theorems, axiom footprint `[propext, Classical.choice, Quot.sound]`
- bit-exact reproduction of the sibling implementation; ⁴He dispersion fit to 0.2–0.33%

**Retracted** (measurement):
- exponents for τ and for the excess delay — failed pre-registered criteria
- the ordinal "dispersion delays thermalization" — single-sample artifact
- the small-D sign reversal — below ensemble scatter
- equipartition percentages — ensemble CV 25–84%

**Novelty explicitly withdrawn**: the thermalization phenomenon is known
(absolute equilibrium; established for shell models by Thalabard–Turkington
and others), so §6 connects rather than claims.

## Provenance

Every number traces to the repository: `LEDGER.md` (claims with retraction
status), `docs/LITERATURE_LEDGER.md` (citations, each verified), the
`docs/designs/` pre-registrations, and the archived run outputs in
`exploration/`.
