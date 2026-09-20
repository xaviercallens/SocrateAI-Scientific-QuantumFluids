# Literature gate on "TDA of the ⁴He dispersion curve" — **proposal withdrawn before implementation**

**Date:** 2026-09-20. **Status:** CLOSED. Nothing was built.
**Why this file exists:** `RETRACTIONS.md` records two results that were formalized, measured and
published before a literature check killed them. The check now runs *first*. This is the first
proposal it stopped, and it cost a search instead of a release.

## The proposal

Apply 0-dimensional sublevel-set persistent homology to the measured dispersion `ε(k)`: the roton is
a homology class born at `Δ_R`, dying when it merges at the maxon `Δ_M`; small-persistence pairs are
instrumental wiggles; the two-roton damping threshold `Δ_M = 2Δ_R` becomes the line `death = 2·birth`
in the persistence diagram; the stability theorem supplies a noise guarantee. Plus a database of
topological descriptors for quantum fluids.

## Verdict: it is a renaming, and the arithmetic says so

**For a function on an interval, 0-dim persistence of a minimum *is* the topographic prominence of the
corresponding peak.** Edelsbrunner & Morozov say so themselves (*Persistent Homology*, Handbook of
Discrete and Computational Geometry, 3rd ed., ch. 24): persistence "generalis[es] topographic
prominence to more general functions and to higher-dimensional features".

Checked here on the published SVP table (`exploration/godfrin/tda_gate_check.py`):

```
scipy.signal.peak_prominences on −ε   →  roton prominence = 0.4501 meV
Δ_M − Δ_R  from the same table        →                     0.4501 meV
```

The persistence of the roton is `Δ_M − Δ_R`, a difference of two numbers already tabulated in
[G21] Tables III and V at all seven pressures. A persistence diagram of `ε(k)` contains **no
information that his tables do not already contain**, and the derived "`d = 2b` line" is the
already-measured statement that `Δ_M` crosses `2Δ_R` near 20 bar.

## Prior art the proposal did not know about

| claim | status |
|---|---|
| sublevel persistence of a dispersion `E(k)`, with a persistence threshold to reject discretisation noise | **already published**: Leykam & Angelakis, *Photonic band structure design using persistent homology*, APL Photonics **6**, 030802 (2021), arXiv:2012.10598 — `H₀` of band minima, "moat bands" being the 2D analogue of a roton minimum |
| persistent homology of a Gross–Pitaevskii Bose gas with quantized vortices | **already published**: Spitz, Berges, Oberthaler, Wienhard, SciPost Phys. **11**, 060 (2021), arXiv:2001.02616 — alpha complexes on sublevel sets of `\|ψ\|`, `H₀`/`H₁`, self-similar scaling. **Our own refuted vortex-floor work (v1.2.0, CLAIM-T3) sits in this paper's territory and should cite it.** |
| PH as a spectral peak-picker with a stability guarantee | an existing genre (GC-IMS, Raman, gamma spectroscopy) |
| `Δ_M = 2Δ_R` crossing | measured and published: Beauvois, Dawidowski, Fåk, Godfrin, Krotscheck, Ollivier, Sultan, Phys. Rev. B **97**, 184520 (2018) — "the maxon energy exceeds the roton-roton decay threshold" |
| database of persistence diagrams for a class of physical systems | exists for nanoporous materials (Lee et al., Materials Cloud 2017.0001); **nothing found for fluids** |

## A physics objection that would have bitten

Where the point `(Δ_R, Δ_M)` is supposed to cross `d = 2b`, the sharp branch is repelled by the
two-roton continuum and flattens ("squaring", [G21] and Beauvois 2018). The `Δ_M` read off a fitted
curve is therefore model-dependent *exactly* in the regime the construction is about. A persistence
diagram does not remove that ambiguity — it inherits it.

## What survives, and is not pursued here

1. **First application to a measured neutron dispersion.** True but thin: a new application of a
   known method to a curve whose features are already tabulated.
2. **`S(Q,ω)` as a 2D object** — persistence of the intensity ridge, `H₁` of the multi-excitation
   continuum. Here prominence has **no** equivalent and the search found no prior work. This is the
   only part with real space. **It needs the 2D `S(Q,ω)` maps, which this repository does not have**
   (only a figure `.eps`). Pursuing it means asking Godfrin for the data, which is an M4 outreach
   question, not something to build against a curve we already hold.

**Conclusion.** No TDA work on `ε(k)` is undertaken. If the database is built later it should hold
vortex-configuration diagrams (citing Spitz et al.) and `S(Q,ω)` diagrams if that data is ever
obtained — not dispersion-curve diagrams, which would be prominence under another name.
