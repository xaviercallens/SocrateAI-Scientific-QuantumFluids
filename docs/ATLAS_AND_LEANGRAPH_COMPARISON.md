# Comparison with Meta's ATLAS, and a run of LeanMaster's LeanGraph

**Date:** 2026-09-20. Both tools were run/inspected locally; nothing here is taken from their READMEs alone.

## 1. ATLAS (facebookresearch/atlas-lean)

**What it is — and is not.** ATLAS is *Autoformalized Textbook Library At Scale*: a Lean 4 **corpus**
of textbook mathematics produced by Meta's AutoformBot pipeline (companion paper arXiv:2605.29955). It
is not a tool that generates Lean for us; the generator is the separate `autoform-bot` harness. So
"use ATLAS to generate Lean 4" is not available as such — what *is* possible, and done here, is to
search the corpus for overlap and compare it with this library. Inspected copy: `v1/` at commit
`e8b31c5` (2026-08-24), 2653 Lean files across 27 textbooks.

**It cannot be imported.** ATLAS v1 pins `leanprover/lean4:v4.29.0`; this library is on 4.34.0-rc2.
That is the same version-skew wall that blocked reuse of the OpenAI tree until both were aligned
(`MadelungNSE.lean`). Reuse would mean re-proving against our pin.

**Overlap with quantum fluids: none.** Zero hits for Madelung, Gross–Pitaevskii, superfluid,
Bogoliubov. (An apparent 372 hits for "Schr" are *Schreier*, from the buildings chapters — checked,
not Schrödinger.) Adjacent material exists: Laplacian (38 files), divergence (24), Parseval/Plancherel
(51), heat equation (17).

**One genuine point of contact — and it is complementary, not overlapping.**
`ComplexVariables/code/Lecture13.lean` proves `ClosedCurve.windingNumber_intValued`: the **continuum**
winding number of a closed curve is an integer (1316 lines, no `sorry`). Our
`VortexWinding.loop_sum_eq_mul` is the **discrete** statement — the sum of principal-branch phase
differences around a sampled loop is an integer multiple of 2π — plus the failure case at a phase step
of exactly π, which has no continuum analogue. The theorem that would *connect* the two is exactly
open target #1 of our paper (the sampling theorem). ATLAS supplies one end of that bridge.

**Integrity profile, measured.**

| | ATLAS v1 | this library |
|---|---|---|
| Lean files | 2653 | 12 |
| files containing `sorry` | **874 (33 %)**, 3579 occurrences | **0** |
| custom `axiom` declarations | 2 | 0 |
| independent second-kernel check | not reported | every module (Comparator + nanoda) |
| self-reported, PDE textbook | 105 statements, 81.9 % pass, faithfulness 4.08/5, proof-integrity 4.2/5 | — |

This is not a criticism of ATLAS, whose stated goal is *scale* with automated scoring, and which
reports its own pass rates openly. It is the clearest available statement of the trade: an
autoformalization corpus is broad and one-third unfinished; a hand-audited library is tiny and closed
under its own checks. They are different instruments.

## 2. LeanGraph (from SocrateAI-Scientific-Agora-LeanMaster)

No "LeanManager"/LeanMaster **MCP server** is connected to this session, and none is configured for
this project (the only MCP configured locally is `elenchus-solvers`, for the Elenchus project). What
LeanMaster does ship and what was run is its `leangraph` dependency analyser.

**Result on this library: 91 declarations (88 theorems, 3 definitions), 64 proof-dependency edges,
logical DAG = True.**

**A defect found in LeanGraph, reproducibly.** Run on the repository as-is it reports *152* proof
edges and **"cycles detected"**, listing essentially the entire library as one dependency cycle. That
is impossible — Lean's kernel rejects circular proofs and the build passes. The cause: LeanGraph's
extractor is textual, and it counts each generated `#print axioms X` line as a dependency on `X`.
Stripping those lines from a scratch copy gives 64 edges and DAG = True. **88 spurious edges, one per
audit line.** Also false positives: "unused import `DualLength → Mathlib`" (the file uses `field_simp`,
`positivity`; a text scan cannot see tactic use).

Reported back to LeanMaster as a fair return for their audit of our v1.1.0 tag. The general point is
the one `RETRACTIONS.md` makes from the other side: a regex over source is not the kernel, and the
two must not be confused — an analyser that can declare a kernel-accepted library cyclic needs its
verdict checked before it is believed.
