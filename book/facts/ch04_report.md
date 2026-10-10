# Chapter 4 — "The Specific Heat of Helium-4 and Godfrin's Series": author's report

Author's session 2026-10-09/10.  Nothing outside `book/` and the session scratchpad was written.  No commit, no push, no deposit, no external message.
(`rm`/`mv`/`setsid` were never used; one denied `rm` attempt was redone without deletion.)

## 1. Files produced

| file | content |
|---|---|
| `chapters/ch04.tex` | the chapter: about 5 400 words of prose (no code, maths, tables or captions) plus about 550 words of captions; 6 figures, 1 table, 4 Lean boxes (3 of the library + 1 new), 2 solver boxes, `godfrinbox`, `honestbox`, 3 exercises, notes; 22.3 pages in the book format (PDF pages 9–31 of my stand-alone build, last page one third full) |
| `figures/ch04_dispersion.{py,pdf,png}` | Fig. 4.1: measured phonon branch, Debye line and the paper's polynomial; the same data divided by ħck and k² (intercept α₂, slope α₃, curvature α₄) |
| `figures/ch04_bose.{py,pdf,png}` | Fig. 4.2: the six Bose integrals by CVODE (cumulative curves; error against the Lean closed forms versus tolerance) |
| `figures/ch04_ladder.{py,pdf,png}` | Fig. 4.3: the solver against the proved series (a ladder of residuals whose slopes are those of the next term; panel b: what the data alone determine) |
| `figures/ch04_heatmap.{py,pdf,png}` | Fig. 4.4 (**the visually striking one**): which wavevectors carry the specific heat, as a function of T, from the measured table; the phonon ridge and the roton switch |
| `figures/ch04_budget.{py,pdf,png}` | Fig. 4.5: Eq. (22) against the integral of the measured dispersion, and the split of the error into truncation and model error |
| `figures/ch04_asymptotic.{py,pdf,png}` | Fig. 4.6: the series is asymptotic (partial-sum error to order 40; root test of the coefficients to order 60) |
| `figures/ch04_common.py`, `ch04_series_ext.py` | constants, closed forms, loaders for the two open ancillary tables; exact-rational reversion and coefficients to T^20 |
| `figures/ch04_cvode_compute.py` | **all CVODE runs** (parts A Bose integrals, B model dispersion, C measured table); refuses to run with the stale module (see §5); writes `ch04_cvode_raw.json`, `ch04_cvode_results.npz` |
| `figures/ch04_crosschecks.py` → `ch04_crosschecks.json` | 30-digit mpmath references of the subtracted model integral at 7 temperatures; SciPy quadrature of the measured table |
| `figures/ch04_solver_probe.py` → `ch04_solver_probe_{fixed,venv}.json` | probes of the fixed build and of the stale venv build (§5) |
| `figures/ch04_analysis.py` → `figures/ch04_numbers.json`, `ch04_analysis.npz` | post-processing; **`ch04_numbers.json` is the single source of every computed number of the text** (it also embeds the two probe files, the Lean run record and the certificate counts) |
| `figures/ch04_numbers_tex.py` → `figures/ch04_numbers.tex` | writes the `\cfv{key}` macros (189 distinct keys used in the chapter; an undefined key is a LaTeX error, so no number can be typed by hand and drift) |
| `figures/ch04_lean_record.py` → `ch04_lean_runs.json`, `ch04_negctl_L54.txt`, `ch04_negctl_D15121.txt` | copies from the compile logs what the chapter quotes |
| `figures/ch04_numbers_dispersion.json`, `ch04_numbers_heatmap.json` | numbers written by the two figure scripts and merged into `ch04_numbers.json` |
| `refs_ch04.bib` | 3 new entries: Phillips1970, Greywall1978, BenderOrszag1999 |
| `lean/Ch04_DosLink.lean` | **NEW Lean** (§6) |
| `lean/Ch04_NegativeControl_L54.lean`, `lean/Ch04_NegativeControl_D15121.lean` | two files that are **MEANT TO FAIL** (negative controls quoted in §4.4; their headers say so; please exclude them from audits of theorem files, as for `Ch02_NegativeControl.lean`) |
| `facts/ch04_lean_logs/` | compile logs: the three library modules (exit 0), `DosLink5.log` (the final new file, exit 0, no warning), the earlier failed attempts `DosLink2/3.log` and the intermediate `DosLink4.log` (exit 0, 6 linter warnings, same proofs), the two negative controls, `sympy_derivation_output.txt`, and the two helper scripts that compiled them |

## 2. Status

* **LaTeX.**  Stand-alone builds, LuaLaTeX, three passes with bibtex between, fresh jobnames, output in the scratchpad (not in `book/`):
  (i) my wrapper = the official `chapter_wrapper.tex` plus stub chapters carrying `\label{ch01..ch10}` (so that `\cref{ch02}`, `\cref{ch05}`, … resolve) and `\bibliography{refs,refs_ch04}`: **0 errors, 0 undefined references/citations, 0 overfull boxes, no missing glyph**;
  (ii) the official wrapper itself (`\def\chap{chapters/ch04}\input{chapter_wrapper}`): **0 errors**, no overfull box; warnings only for the three citations of `refs_ch04.bib` (the wrapper loads `refs.bib` only) and `\cref{ch02}`, `\cref{ch05}` (other chapters).
  All six figures present and re-generated after the editor's `figstyle.py` fix (no boxes for the minus sign, lining digits; see §8 item 6 for a limitation I found).
* **Lean.**  The three library modules compile (exit 0, 28 s / 67 s / 43 s on the loaded machine): `BoseIntegral` and `PhononSpecificHeat` depend on {propext, Classical.choice, Quot.sound}, `PhononSeries` on {propext, Quot.sound}; these agree with `facts/lean_audit.md`.  The new file `lean/Ch04_DosLink.lean`: exit 0, 49 s, **0 errors, 0 warnings, no `sorry`/`sorryAx`**; axioms in §6.  The editor's audit driver compiled it independently (`facts/audit/book_Ch04_DosLink.json`, 2026-10-10 01:46: exit 0, 39 s, 0 errors, 0 warnings, 13 theorems, 4 definitions, 0 user axioms, footprint {Classical.choice, Quot.sound, propext}) and both negative controls failed as expected (`facts/audit/book_Ch04_NegativeControl_*.json`: `ring failed, ring expressions not equal`; `unsolved goals`).
* **Editor's citation checker** (`facts/make_appA.py`: `parse_decls`, `scan_chapters`, imported and run read-only on a copy of `ch04.tex`): 20 declarations cited, **0 problems**; 12 leanbox copies: 11 `identical`, 1 `abridged/marked` (the right-hand side of `phonon_specific_heat_end_to_end`, a marked ellipsis: it repeats the six closed forms of `phonon_specific_heat` shown in the box above).
* **Length.**  About 5 400 words of prose (target 5 000–7 500) but 22.3 pages (target ≈ 14–20): the page count is driven by 6 figures, 4 Lean boxes, 2 solver boxes and the honest box.  If pages must be saved, in order of least loss: §4.5.3 (0.5 p), the two negative-control listings (0.3 p), Fig. 4.2 with §4.5.1 (1.4 p), the second half of §4.6.4.

## 3. Where every number of the text comes from

Every computed number is a macro `\cfv{key}`; the key is defined in `figures/ch04_numbers.tex`, generated from `figures/ch04_numbers.json` by `ch04_numbers_tex.py`.  Groups:

| text | key prefix | JSON key / source |
|---|---|---|
| §4.1 specific heat at 0.1, 0.2 K, ratio, C/T³ at 0.1 and 0.5 K, ratio deviation | `cv-*`, `cvT3-*` | `measured_cvode.paper_table_at`, `paper_cv_over_T3`: the paper's own table `Cv-and-Entropy.txt` (open ancillary file) |
| table facts: 1727 numeric rows, spacing 0.002 Å⁻¹ up to 3.44 Å⁻¹ and 0.05 Å⁻¹ beyond (4 steps differ from 0.002; one placeholder row `-- -- --` near 3.44–3.45 is skipped), 34 rows with an uncertainty | `n-rows`, `grid-until`, `grid-coarse`, `n-err-rows` | `dispersion` (counted by `ch04_dispersion.py` in `DispersionP0allRange.txt`; the file in `data/external/godfrin_papers/2021_godfrin_landau-dispersion-thermo-he4_anc/` is byte-identical, sha256 `59ca6ea7…`, to the one in `data/external/godfrin_2021_arxiv_ancillary/`) |
| c, V, α₂, α₃, α₄ | `c`, `V`, `a2`… | the arXiv source `2020-Dispersion-paper-v6d.tex` (lines 152, 183, 1396 of `data/external/godfrin_papers/2021_godfrin_landau-dispersion-thermo-he4_src/`); the "printed" values of A…L are on line 1398 of the same file and lines 232–238 of `Supplemental-v2.tex` |
| A, C, D, E, K, L computed / printed; max difference 0.18 % | `A-val`… `coef-maxdiff` | `coefficients`, `coefficients_max_rel_diff_to_printed` (closed forms of Eq. (22) in `ch04_common.py::coeffs_SI`) |
| θ = ħc/k_B, kT, median k, λ, q90 | `theta`, `kT`, `med-k-*`, `lambda-*`, `q90-k-*` | `constants`, `heatmap` |
| Fig. 4.1 numbers (maxon, roton, rms 0.67 µeV, max 2.2 µeV, +7.6 % at 1 Å⁻¹) | `maxon-*`, `roton-*`, `rms-ueV`, `maxdev-ueV`, `poly-dev-1` | `dispersion` |
| exact rationals g₄…g₈, c₁₀, c₁₁, rA-* | `c10`, `c11`, `rA-*`, `rat-maxdiff` | `exact_rational` (Python `fractions`, `ch04_series_ext.py`); the g_n fractions in §4.4 are typed from `exact_rational.g_n` |
| §4.5 solver-build story (stale module versus fixed build) | `old-*`, `new-*`, `probe-*`, `rs-*` | `solver_probe_stale_venv`, `solver_probe_fixed`, `solver_module` |
| Bose integrals by CVODE | `bose-*` | `bose_cvode` (`ch04_cvode_raw.json`, part A) |
| model dispersion, mpmath references, subtraction trick, ladder slopes, recovery of coefficients, numerical controls | `model-*`, `raw8-*`, `sub8-*`, `slope-*`, `ratio-*`, `floor-*`, `rec-*`, `ctl-*` | `model_cvode`, `ladder`, `coefficient_recovery`, `negative_controls_numerical`, `ch04_crosschecks.json` |
| reproduction of the paper's table; uncertainty column | `repro-*`, `paper-unc-*` | `measured_cvode`, `paper_uncertainty_table` |
| error budget, share outside 0.5 Å⁻¹, crossing temperature | `bud-*`, `share05-*`, `T-cross` | `budget`, `heatmap`, `measured_cvode.T_phonon_equals_roton_interp` |
| asymptotics: best orders, p*, envelope fit, critical point, root test | `best-*`, `err9-*`, `pstar-*`, `fit-*`, `uc-*`, `root-*` | `asymptotic`, `critical_point`, `root_test` |
| certificate sizes (42; 202, 156, 116, 82, 58, 40) | `cert-*` | `lean_certificate_monomials`: monomials of the polynomial multiplying `h` in each `linear_combination` of `lean_src/PhononSeries.lean`, counted by `ch04_analysis.py` |
| sympy run time (32 s), Lean toolchain (4.34.0-rc2), commit (5db8041) | `sympy-seconds`, `lean-toolchain`, `rs-commit-short` | `text_constants` |

Typed by hand (not macros), with their origin: dates 2026-09-21 (design note), 2026-09-26 (venv module build, file date), 2026-09-28 (`docs/CVODE_ADAMS_FIX.md`, dated in its title); the years 1970, 1978 (Greywall), 1980 (erratum), 2021, 2022 (checked on Crossref / `refs.bib`); `5000` (the assert threshold in `ch04_cvode_compute.py`); the grid and the interval descriptions of the runs (x ≤ 80, k_max = 2.5 Å⁻¹, 0.05…1.30 K in steps of 0.05, tolerances: copied from `ch04_cvode_compute.py`); the Bose-integral closed forms and the Bernoulli numbers (from `lean_src/PhononSpecificHeat.lean`); the exercise numbers 5, 28, 165, 1001 and the Exercise 1 series (validated with sympy; the formula of Exercise 2 through n = 4); the sentence "`exploration/godfrin/derive_cv_series.py` … `INVERSE SERIES: all 7 printed coefficients match`" (the output of my re-run, kept in `facts/ch04_lean_logs/sympy_derivation_output.txt`).

## 4. Citations

* Crossref-checked this session (title, authors, journal, volume, pages, year): Phillips–Waterfield–Hoffer, PRL 25, 1260–1262 (1970), doi:10.1103/PhysRevLett.25.1260; Greywall, PRB 18, 2127–2144 (1978), doi:10.1103/PhysRevB.18.2127, and its erratum PRB 21, 1329–1331 (1980), doi:10.1103/PhysRevB.21.1329; Bender–Orszag, *Advanced Mathematical Methods for Scientists and Engineers I*, Springer 1999, doi:10.1007/978-1-4757-3069-2.  No WebSearch/WebFetch; one direct Crossref query per DOI.
* From `refs.bib` (editor's): Godfrin2021 (authors, title, DOI: the editor's correction is in the entry), GodfrinKrotscheck2022, Landau1941, PitaevskiiStringari2016, Donnelly1991, Callens2026lib, Mathlib2020, deMoura2021, Hindmarsh2005.
* **Not re-checked**: that Donnelly's and Pitaevskii–Stringari's books discuss the quasiparticle picture in the way the "Notes" say (taken from FACTS §3 as textbook references); that Bender–Orszag treats optimal truncation (I cite it only as "for asymptotic series and the idea of optimal truncation"; the page or section is not given).
* About the paper: only what FACTS §2 allows, plus the facts of the open ancillary table (rows, grid, uncertainty column, ultrasound-based energies below 0.15 Å⁻¹ — the last from the arXiv source, `2020-Dispersion-paper-v6d.tex` lines 95 and 1209, not from the `.meta` file), plus, from the arXiv source: Eq. (2) is the dispersion series (the second displayed equation of `2020-Dispersion-paper-v6d.tex`, label `eq:dispfit`; the numbering of the version of record was not checked), the coefficient set, the molar volume and the speed of sound (cited above), and "a good fit for k < 0.5 Å⁻¹"; the remark that earlier published versions of the series contain errors is FACTS §2.  No authors named beyond "Godfrin and collaborators"; no statement about errata of the paper (rule); no mention of `docs/FOR_GODFRIN.md` or of any contact.
* Statements of the paper that I read and did **not** use: the quantitative claims about where the series fails (0.4 K deviation, 0.77 K crossing, ≤ 1 % uncertainty claim): the chapter gives my own computed numbers instead, labelled as such.

## 5. The solver build (finding that matters outside this chapter)

* The `rusty_sundials` module of the project's `.venv` (file date 2026-09-26) has the pre-fix Adams method (implicit Euler with a Milne error estimate; `docs/CVODE_ADAMS_FIX.md`, 2026-09-28).  On the Debye integral to x = 70 at rtol 1e-6 it returns a relative error 6.5e-4 after 15 532 calls (649 × the tolerance); the fixed build, 2.8e-7 after 260 calls.  Its BDF gave up ("too many error test failures at one step") on 38 of 160 end points of the six Bose integrals; the fixed build never.  (`figures/ch04_solver_probe_venv.json`, `…_fixed.json`.)
* All results of the chapter come from the stable build you named: `/mnt/data/xdev-cache/rs_py_5db8041/rusty_sundials.so`, commit `5db8041fd2e3840defcff2b4a8c26c1cbb2467fd`, sha256 `0bdb1b4a504fb4817738c483f797e6a109b99121b666f1e51ad8e05c2fb996d7` (equal to `sha256.txt`); recorded in `ch04_numbers.json` → `solver_module` (file, sha256, commit, probe result).  `ch04_cvode_compute.py::check_module` asserts it before computing: Adams on y' = −y to t = 10 at rtol 1e-8 must need < 5 000 right-hand-side calls (fixed build: 511 calls, error 2.0e-7), and the sha256 must equal the recorded one; run with the venv module the script exits.  An older queued job that did start with the stale module exited by the assert without overwriting data (checked).
* A first full set of runs with the stale module (plausible but wrong; with it a runaway job made about 8 million right-hand-side calls and its Python process grew to ≈ 12 GB, about 1.5 kB per call, apparently retention in the Python binding, which I did not investigate) was discarded; every number was recomputed.  The chapter tells this (§4.5, honest box).
* All CVODE runs use Adams.  The right-hand sides are Python callbacks, so the timings in the text include that overhead and are not a solver benchmark (machine caveat in the text: shared 8-core machine, load average 18–20 during the runs).

## 6. New Lean: `lean/Ch04_DosLink.lean`

Purpose: design note `docs/designs/PHONON_SERIES_A_TO_L.md` §6 item 1 ("the link between `density_of_states` and `phonon_specific_heat` is by inspection") — closed here, together with the retyped Bose integrals and `kInv0Deriv`.  Imports `BoseIntegral`, `PhononSeries`, `PhononSpecificHeat`; namespace `QuantumFluids.DosLink`; 13 theorems, 4 definitions (279 lines).
Statements (shown in the chapter): `kPoly`, `derivative_kPoly` (Mathlib's formal derivative of `kPoly` is `kInv0Deriv`), `dosPoly`, `dos_coeffs` (the coefficients of `k²·k'` in degrees 2…8 are the brackets g₂…g₈, with g₃ = 0), `phonon_specific_heat_end_to_end` (Eq. (22) with the brackets read off `dosPoly`, the six Bose integrals read off `mellin bose`, the odd zeta values `riemannZeta 7`, `riemannZeta 9`); also in the file, cited by name: `energyMonomial`, `energyMonomial_eq` (the energy of a monomial written as a Mellin integral equals `energyTerm`, T > 0), `phonon_specific_heat_integral`.
Proof of `dos_coeffs`: `density_of_states` applied in the quotient ring ℝ[X]/(X⁹) (`Ideal.Quotient.mk`), then `Polynomial.X_pow_dvd_iff`.
Compile (Lean 4.34.0-rc2, the OpenAI tree's Mathlib read-only; library modules compiled unchanged into scratch .olean files put on `LEAN_PATH`; see `facts/ch04_lean_logs/lean_deps.sh`, `lean_check.sh`): exit 0, 49 s, **no error, no warning, no `sorry`**.
`#print axioms` (7 lines at the end of the file; log `facts/ch04_lean_logs/DosLink5.log`): `kInv0_inverts` {propext, Quot.sound}; `derivative_kPoly`, `dos_coeffs`, `phonon_specific_heat_from_dos`, `phonon_specific_heat_end_to_end`, `energyMonomial_eq`, `phonon_specific_heat_integral`: {propext, Classical.choice, Quot.sound}.  No user axiom.
What it does **not** prove (said in the chapter): that the truncated density of states may stand for the true one under the integral (asymptotic validity), α₁ ≠ 0, anything about the measured curve.
History: DosLink1/2 failed (a missing `open Real` made `π` an auto-bound variable; `simp` rewriting `C (5*a2)` into `C 5 * C a2`; `ring` closing no goals); DosLink3 failed in `energyMonomial_eq` (`sorryAx`); DosLink4 compiled with six linter warnings (redundant hypotheses); DosLink5 removes them (same proofs; hypotheses derived inside the proof) and is the file installed.
Negative controls (`Ch04_NegativeControl_*.lean`): both fail as quoted (`ring failed … ⊢ -(a2 ^ 3 * e ^ 8 * 3) = 0`, exit 1, 111 s; `unsolved goals`, exit 1, 225 s).

## 7. What I could not verify, and what the chapter says about it

* The formulas checked are those of the arXiv source (`2020-Dispersion-paper-v6d.tex` and `Supplemental-v2.tex`); the version of record of PRB 103, 104516 was **not** compared (stated in §4.4 and in the honest box).
* The chapter does not compare with calorimetry (not in the open files).
* Why my reproduction of the paper's tabulated specific heat differs by up to 2.6e-3 (total) / 3.6e-3 (phonon column) rather than 1e-4: not tracked down (candidates named in the text: interpolation, the ultrasound-based region below 0.15 Å⁻¹).  The differences are below the table's own uncertainty column (0.86 % at 0.7 K).
* The α₂ units: the arXiv source prints `α₂ = 1.55 Å⁻²` on line 1396 (the design note §6 item 4 records this); the chapter writes Å², the unit that dimensional analysis requires, and makes **no** claim about a misprint (rule on errata).

## 8. For the editor to check

1. `chapters/ch04.tex` starts with `\input{figures/ch04_numbers.tex}`: the file (generated; 189 keys used) must stay in `figures/`.  It also defines `\cfkB`, `\cfAng`, `\cfK` with `\providecommand`.
2. Bibliography: add `refs_ch04.bib` to the book's `\bibliography{…}` (3 entries, no duplicates with `refs.bib` or the other `refs_ch*.bib`).
3. Cross-references: `\cref{ch05}` (twice), `\cref{ch02}` (once) in the text; they resolve only in the full book.  Other chapters reference only `\cref{ch04}`.
4. New Lean `lean/Ch04_DosLink.lean` should be listed as new in Appendix A (cited as `\Lthm{DosLink}{…}`; the checker's alias `DosLink → Ch04_DosLink` resolves; printed names `QuantumFluids.DosLink.…` are the true namespace).  The two `Ch04_NegativeControl_*.lean` files are meant to fail.
5. Unicode in listings: all 18 non-ASCII characters of my listings (e.g. ℝ ∧ ≠ ↦ … ħ) are already in `qf_unicode_lst.tex`; re-run `make_appA.py` after integration anyway (the new Lean file adds none that are not in the table).
6. **figstyle limitation found.**  With matplotlib 3.11.1, `Text.draw` passes `mtext=None` to the renderer for **multi-line** strings, so the `lnum` font feature set in your `figstyle.py` is not applied to them: digits in a multi-line string stay old-style (a "0" looks like an "o").  I avoided it in `ch04_asymptotic.py` ("Eq. $(22)$" in mathtext).  Strings that mix `$…$` with plain digits have the same defect (mathtext ignores the feature); in `ch04_dispersion.py` the rms value is written inside the math part.  Other chapters may be affected.
7. `docs/designs/PHONON_SERIES_A_TO_L.md` is cited by the chapter; the repository path is relied upon.
8. The chapter names the programme rule LL-15 and the design note's "process lapse" (check not pre-registered): both are in the design note; I did not open `LL.md` again.

## 9. Process notes (failures, kept for the record)

* A first set of CVODE runs with the stale module was discarded (§5).  A retry-with-end-point-nudging idea for the BDF give-ups did not work and was dropped when the fixed build removed the give-ups.
* A reference mismatch at T = 0.02 K (3e-5) was a grid defect (0.02 K was not in the temperature list); fixed by adding it.
* The first draft said the derivation check had a pre-registered outcome rule; it had not (design note: process lapse); the chapter now says so.
* Drafts that attributed to the paper statements beyond FACTS §2 (0.4 K, 0.77 K, ≤ 1 %) were removed.
* "within x per cent" statements whose rounding could understate the true value were re-worded (ratio 7.88: "1.4 per cent below 2³"; recovery of coefficients; slopes "within about 0.15").
* In the numbers file the label of the integration method of the measured table was a stale `"bdf"` (all runs are Adams); corrected, no number changed.
