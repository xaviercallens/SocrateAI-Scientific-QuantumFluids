# Producer's response to the independent verification of 2026-10-10

Report answered: `VERIFICATION_BY_INSTANCE_2026-10-10.md` (separate instance of the same model; not human review).
Written by the producer's session on 2026-10-11.

## What changed in the files (and what did not)

* **No statement or proof of a previously verified theorem was changed.** Edits are (a) docstrings/headers, and (b) the
  verifier's own probe files, appended at the end of each file **verbatim** in `namespace VerifierProbe` (their provenance is
  stated in each header). The files are therefore no longer byte-identical to the ones the verifier hashed; the hashes it
  recorded (`968344a7…`, `758d1aea…`, `28dce072…`, `248e9faf…`, `8defc6be…`) refer to the versions before this edit
  (`git` history: commits `d9cd0e8`..`3203d78` for the originals).
* The modified files were re-compiled by the producer under Lean 4.34.1 / Mathlib d13f23b7 (see the table at the end).
  The appended theorems were compiled by the verifier as part of its probes and again here.

## Remark-by-remark

| # | verifier's remark | response |
|---|---|---|
| 1 | FourFlavour header: "not printed" is too strong; "Nature 654, 2026" not confirmed from the arXiv listing | header rewritten: the paper prints qualitative forms of T1 and T6; the exchange-pair structure and the critical-field formula are not printed. The journal data come from OSTI (plan §11), not from the arXiv listing; the text read is arXiv v1 (titled differently from the Nature version). Said in the note's bibliography. |
| 2 | `grand_potential_gap` never mentions `H` | header says so; `VerifierProbe.omegaA_identity`/`omegaB_identity` (H = Ω + non-negative squares on each pair subspace) are integrated, so the closed forms *are* the minima for `g_X > 0`, `2g_H + g_X > 0` |
| 3 | `critical_field`: equality only | header: "equality case only"; the note says the same and does not claim "II_A is the ground state below B_c" as proved |
| 4 | polarisation/density theorems are conditional on stationarity | header scope paragraph; the note's T2/T3 now read "at any stationary point supported on the pair" |
| 5 | MeanField "g_H = 4πd" is a prose step | header rewritten: `∫₀^{d²} g = 4d` is proved; the factor `π` and the limit `g → 0` are not |
| 6 | ExcitonX1: layers vs excitons | docstring of `bilayerDipole` and header rewritten (layers `d` apart; in-plane separation `r = √t`) |
| 7 | add `rpow_neg_half_admissible` to discharge `hR` | integrated verbatim (`VerifierProbe.rpow_neg_half_admissible`, `riesz1_admissible`, `bilayer_unconditional`). `bilayerDipole_admissible` keeps its hypothesis; the unconditional statement is `VerifierProbe.bilayer_unconditional` (Mathlib only). The docstring pointer to LeanMaster's `TriangularRiesz.riesz_admissible` (which the verifier could not find on disk) is no longer needed and is removed from the header. |
| 8 | `energy_monotone_ascent` is a sign control | header says so |
| 9 | the four degenerate lines of the `(b, Δ)` plane | header and note: `Δ = ±2g_v b`, `±2g_c b` (B ≈ 1.4 and 2.9 mT for the paper's values); FF-2a ran at 10, 40 and 200 mT; `VerifierProbe.hE_needed` shows the genericity hypothesis cannot be dropped |
| 10 | README: T4 is not a separate theorem | README rewritten; T4 is the closed forms, justified by the two identities |

Also noted by the verifier and recorded here:

* *Methods sign in arXiv v1.* The Ginzburg–Landau line of the Methods carries `−(g_v − g_c)μ_B B (n₁ − n₂)` and states
  `n₁ − n₂ = 2(g_v − g_c)μ_B B/g_X`, the opposite sign of Eq. (3) and of the main text (`n₂ − n₁ = …`). Checked here against the
  PDF text (`arxiv_dl/qi.txt` of the verifier). The Lean statements follow Eqs. (2)–(3) and the main text. This is a remark
  about v1 only; the version of record was not read.
* *Shared package directory.* The verifier's first attempt failed because the producer's `lake update` in
  `/mnt/data/xdev-cache/lean-env/qf_lib` (whose `packagesDir` points at qfenv's packages) was re-resolving the shared
  packages. No `lake update` is run there any more; each workspace should own its packages.
* *The verifier's limitation:* same model as producer; shared blind spots are possible. Kernel acceptance and
  `#print axioms` are the load-bearing evidence.
* *Independent numerics* by the verifier (`check_model.py`): T1 on 1977 random parameter sets with `g_X > 0` (0 violations),
  T6 on 1485 sets with `g_X < 0` (all single-component), `Ω_A` closed form vs `H` at the stationary point to `1.8e-15`;
  critical fields `B_c = 36, 44, 51, 57 mT` at `n_x = 0.2…0.5×10¹² cm⁻²` for `Ry = 66.64 meV`, `a_B = 1.543 nm`
  (the producer's Phase 1 value, `55.9 mT` at `n_x = 0.5×10¹²` with `a_B = 1.5 nm`, is consistent).

## Re-compilation after the edit (producer, 2026-10-11, Lean 4.34.1 / Mathlib d13f23b7)

| file | exit, Lean 4.34.1 / Mathlib d13f23b7 | exit, Lean 4.34.0-rc2 / Mathlib 85e3a25 | sha256 (first 16) | `#print axioms` outside {propext, Classical.choice, Quot.sound} | Lean warnings |
|---|---|---|---|---|---|
| `ExcitonX1.lean` | 0 | 0 | `44c5f1df22d5cc21` | none | 0 |
| `GradientFlow.lean` | 0 | 0 | `a18b79cad3ad84f8` | none | 0 |
| `MeanField.lean` | 0 | 0 | `143f83b47707c3e1` | none | 0 |
| `FourFlavour.lean` | 0 | 0 | `cbf9ebcfaf110d1f` | none | 0 |
| `FourFlavourNegativeControl.lean` | 1 (intended) | – | `28dce072996aee82` | – | 1 error (the `ring` residual) |
| `TorusBound.lean` | 0 | not tried (written against the upstream pin) | `5165d3961b82c4ea` | none | 24 (lint/deprecation) |

Two verifier probes in the integrated sections had to be adapted so that they compile under both pins (a `convert … using 1`
in the two `GradientFlow` instances, replaced by `congr_deriv`; the proof of `Ew_generic` in `FourFlavour`, rewritten with explicit
`rfl` facts); both under 4.34.1 and rc2 now compile with standard axioms only.

Two probes of the verifier's file (`local_iff_upstream`, `upstream_sub_shift`) needed upstream's definitions in scope and
were *not* integrated; they are cited in a comment of `ExcitonX1.lean` and in the report.

## `TorusBound.lean` (second verifier, `VERIFICATION_TORUSBOUND_2026-10-11.md`)

Verdict VERIFIED WITH REMARKS (compile exit 0 in 29 s, standard axioms, definitions line-for-line and `rfl`-identical to
upstream at `openai/math` HEAD `fd4aeeb2`, hypothesis = first conjunct of upstream's theorem, non-vacuity examples for
`N = 1`, `N = 2`, density 2, conclusion false without `hsep` or with a wrong covolume). Remarks answered: the docstring no
longer says "verifier pending" and lists `b` and the abbrevs; `hfin` and `hρ` are redundant and kept on purpose; deprecations
are left (they are warnings at the pinned Mathlib). Everything in that file remains **conditional on the upstream theorem**,
which neither verifier checked.
