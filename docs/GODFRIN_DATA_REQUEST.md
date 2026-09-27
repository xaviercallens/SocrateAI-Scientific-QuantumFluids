# Draft data request for Henri Godfrin

**Status: DRAFT, for the owner to send personally. Not sent by me. Prepared 2026-09-22 at the owner's
request, given a personal contact route (through a family connection) independent of the institutional
hold described in `docs/FOR_GODFRIN.md` §0.**

Three separable asks, ordered by how little they cost him to answer. Each is real and specific, not a
general "do you have data" — every item below is something a public search already failed to find (see
`docs/designs/ZERO_SOUND_LANDAU_DAMPING_PROPOSAL.md` §§11–12 for the full search record), so nothing here
wastes his time re-deriving something we could have found ourselves.

---

## Suggested opening (a paragraph, not a cover letter)

> I've been running a small Lean 4 (machine-checked proof assistant) project that takes published
> derivations in condensed-matter papers and verifies them formally — catching the kind of slip that
> survives peer review because nobody re-derives an equation by hand. I ran it on your PRB 103, 104516
> (2021) specific-heat series, Eq. (22): all six coefficients A, C, D, E, K, L, and the printed inverse
> dispersion series, check out exactly. For a series whose predecessors (Phillips, Greywall) you note
> contain errors, that's a real confirmation, not a formality — worth having on record.
>
> Three small things came up along the way that only you (or your co-authors) can settle quickly.

## 1. Two apparent misprints — a one-line confirmation would resolve months of uncertainty

Found in the arXiv preprint (v1, 16 Dec 2020 — submitted the day before, so the *pre-referee* text).
We could not access the version of record (paywalled) to check whether these survived to print.

- **Eq. (25)**, normal-fluid density: as printed, the Bose factor is `e^x/(e^x − 1)`; the standard
  Landau formula needs `(e^x − 1)²`. Checkable against your own Table (ancillary
  `DispersionP0allRange.txt`): the printed equation gives 329 g/cm³ at T = 0.5 K against a liquid
  density of 0.145 g/cm³, where the tabulated value (1.2305×10⁻⁶ g/cm³) is correct.
- **Eq. (20)** carries what looks like a spurious `k_B` prefactor (dimensionally inconsistent as
  printed); the same slip appears in the Supplemental.
- Also: α₂ is given in Å⁻² in §VI but Å² in §II — presumably just a typo, dimensional analysis requires Å².

**The ask:** did these survive to the PRB version of record, or were they caught at proof stage? A
one-line answer settles it either way — we'd rather report nothing than report an already-fixed typo.

## 2. Landau parameters for the 2D ³He monolayer (the system in your Nature 2012 paper)

This is the one we actually need data for, and could not find published anywhere open.

**What we're looking for:** the areal-density-dependent Landau parameter `F₀ˢ` (ideally also `F₀ᵃ` and
the effective mass `m*/m`) for the two-dimensional ³He film on graphite pre-plated with a ⁴He monolayer
— the system of Godfrin, Meschke, Lauter, Sultan, Böhm, Krotscheck, Panholzer, *Nature* 483, 576
(2012), and (we believe) originally reported in Godfrin, Meschke, Lauter, Böhm, Krotscheck, Panholzer,
*J. Low Temp. Phys.* **158**, 147 (2010), "Observation of Zero-Sound at Atomic Wave-Vectors in a
Monolayer of Liquid ³He" — which we have not been able to access (paywalled, no open copy found).

**Why we're asking rather than searching harder:** we checked your 2022 review (arXiv:2206.06039,
*Dynamics of Quantum Fluids*) directly — it discusses the film qualitatively but has no table. We found
QMC effective-mass values (Boronat, Casulleras, Grau, Krotscheck, Springer, arXiv:cond-mat/0307493) but
no `F₀ˢ`/`F₀ᵃ`. We found `F₀ᵃ`, `F₁ˢ` values in Casey/Nyéki/Saunders/Hallock papers, but that system uses
a *different* substrate (graphite pre-plated with an HD bilayer, not ⁴He) — we did not want to assume
those transfer without your view on whether they do.

**The ask:** a table, a number at one or two areal densities with uncertainties, or simply a pointer to
where it's published (a copy of the 2010 JLTP paper would itself answer this) would let us build an
honest, fully certified (interval-arithmetic, not floating-point) zero-sound model for your actual
system — see `docs/designs/ZERO_SOUND_LANDAU_DAMPING_PROPOSAL.md` for what we'd do with it, not attached
unless he asks.

## 3. Optional, only if he has an opinion handy

Do the Royal Holloway group's 2D `F₀ᵃ(n)` values (different substrate: HD bilayer, not ⁴He) transfer to
his system, even approximately — or is the substrate difference expected to matter enough that they
shouldn't be used as a stand-in? We'd rather have his one-sentence judgment than guess.

---

## What to attach, if anything

- `paper/quantumfluids_lean4.tex` / `.pdf` — the confirmation of Eq. (22), §"Applying the library to
  published experimental work". Self-contained, does not require the reader to know Lean.
- Offer, not push, the three-phonon threshold numbers (§5a of `docs/FOR_GODFRIN.md`) and the ζ(7)/ζ(9)
  structural point (§5b) if the exchange continues — not needed for a first message.

## What NOT to include in a first message

- The Pitaevskii-plateau observation (`docs/FOR_GODFRIN.md` §2) — marginal significance (< 1σ except at
  the very last, already-flagged point), not worth leading with.
- Anything from the retracted dual-length / dual-scale work (`RETRACTIONS.md`) — it is ours, not his,
  and settled.
