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
