# Chapter 7 report: Friction, Diffusion and the Dissipative Vortex

Author: chapter-7 subagent. Date of last build: 2026-10-10. Nothing was committed, pushed, deposited or sent.

## 1. Status

* `chapters/ch07.tex` compiles alone (`chapter_wrapper_ch07.tex`, LuaLaTeX + bibtex, three passes): exit 0, **zero errors, zero overfull boxes, no missing glyphs, all 5 figures present**. The only warnings are the unresolved `\cref{ch02,ch03,ch04,ch05,ch06}` (expected in a single-chapter build).
* Length: 22 chapter pages (the 26-page PDF is 2 TOC + 22 chapter + 2 bibliography); about 6 400 words of prose plus 660 words of captions. This is about 2 pages over the 14-20 target (code boxes and 5 figures). Cut candidates if the editor needs space: the `einstein_vortex` and `weighted_mean_mem_Icc` statements, the second Rust box, Figure 1.2.
* Required elements: opening from measurements (Moon 2015, Neely 2024); physics; Lean part; CVODE and qf-pgpe computations compared quantitatively with the Lean statements; 5 figures (Fig. 1.3, the thermal field with flow portrait, is the striking one); `godfrinbox`; `honestbox`; three exercises with hints; notes and further reading.
* **Lean statements shown: 11, plus a few definitions (the brief says 2-5).** The chapter is about three library modules plus a new one; the editor may prune.
* Layout choices local to the chapter (restored at its end): `\raggedbottom`, `\widowpenalty=\clubpenalty=10000`; five code boxes are `[unbreakable]`. Voice: plural/impersonal ("we").

## 2. Files (all under `book/`)

* `chapters/ch07.tex` is **generated**: `figures/ch07_template_p1.tex`, `_p2.tex`, `_p3.tex` + `figures/ch07_numbers.json` -> `.venv/bin/python figures/ch07_build_tex.py`. It substitutes every number token from the JSON, copies Lean excerpts from `lean_src/` or `book/lean/` by line range and Python excerpts from `# BOOK-BEGIN/END` blocks, and **checks that every listing line occurs verbatim in its source** (passes). Edit the templates, not `ch07.tex`, or forget the builder.
* Figures (script, PDF, PNG): `ch07_dipole` (CVODE), `ch07_imprint`, `ch07_fields`, `ch07_friction`, `ch07_failures` (CVODE), `ch07_kicks` (figure **unused**; its numbers feed Table 1.2). Number-only scripts: `ch07_bath.py`, `ch07_xcheck.py`, `ch07_cvode_probe.py`. Run machinery: `ch07_pairrun.py`, `ch07_pairrun_driver.sh`, `ch07_pairrun_finalize.py` (fallback, not needed), `ch07_common.py`.
* `figures/ch07_numbers.json` (keys: `fig_dipole fig_imprint fig_fields fig_friction fig_kicks fig_failures bath estimator_crosscheck cvode_stale_probe derived_checks text_numbers`; `text_numbers` holds the 157 tokens printed in the text).
* `lean/Ch07_DissipativePairs.lean` (NEW, 7 theorems, namespace `QuantumFluids.DissipativePairs`, not in the library) and `facts/ch07_lean_axioms.txt` (audit log).
* `refs_ch07.bib`, `chapter_wrapper_ch07.tex` (+ `chapter_wrapper_ch07dbg.tex`, overfull-rule debugging).
* Data outside `book/`: `/mnt/data/xdev-cache/book_ch07/` (run checkpoint and final `ch07_pairrun_e060_d10_s7.npz`, imprint maps cache, logs; a test finalisation `*_e060_partial.npz` is a leftover and unused).

Rebuild: `export PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext; cd book/figures; ../../.venv/bin/python ch07_dipole.py` (same for `ch07_imprint.py ch07_failures.py ch07_kicks.py`; `ch07_fields.py e060_d10_s7`; `ch07_friction.py e060_d10_s7`), then `ch07_build_tex.py`, then lualatex/bibtex/lualatex/lualatex on `chapter_wrapper_ch07.tex`.

## 3. Solver provenance

* **CVODE**: every `CvodeSolver` result (`ch07_dipole.py`, `ch07_failures.py`) was run with the fixed build `/mnt/data/xdev-cache/rs_py_5db8041/rusty_sundials.so`, sha256 `0bdb1b4a...96d7` (equals `sha256.txt`), commit `5db8041fd2e3840defcff2b4a8c26c1cbb2467fd` (`git describe`: v11.5.0-6-g5db8041; the text says "six commits after v11.5.0", **not** "v11.6.0"). `ch07_common.cvode_env` probes Adams on y'=-y (rtol 1e-8, atol 1e-14) and refuses the stale module: fixed build 511 RHS calls, the shared `.venv` module 237 022 (printed in Section 1.4, stored under `cvode_stale_probe`). The earlier "BDF aborts" and "Adams less accurate" statements were artefacts of the stale build and were removed. Results: |d|^2 law to 1.8-2.9e-8 (dipoles) and 4.6e-6-1.1e-5 (same-sign pairs); centre displacement to 2.1e-5; work-precision numbers in the text.
* **qf-pgpe**: `/mnt/data/xdev-cache/qf_ext/qf_pgpe.so` (built 2026-10-09 22:03, sha256 `41abff9a...2995`, recorded in `fig_friction.qf_pgpe_module`). Fresh run: base state `data/generated/pgpe/sweep/e0.60_s11_t4000_final.npy`, `imprint_v2`, d0=10, seed 7, 1500 time units in 5 chunks of 100-500 under `flock`, 928 s in total at load average 7-18 on one thread; energy drift 6.8e-8; all four vortices tracked throughout.
* **Estimator cross-check** (`ch07_xcheck.py`): `qf_pgpe.analyse_tracks` against `exploration/pgpe/transport_estimators.analyse_tracks` on the 8 archived tracks: max relative difference 1.1e-14 (all values and errors; the point estimates agree to 6e-16); Python 29 s, Rust 1.2 s at load 14.4.
* Timing claims in the text carry the shared-machine caveat.

## 4. Lean

* Quoted, verbatim from `lean_src/`: `DissipativeVortexDynamics` (energy_dissipation [statement, proof abridged], dipole_sq_law, centre_velocity_identity, wind_stall + negative control; r2_hasDerivAt, dipole_lifetime_bound, dissipation_indep_of_skew named), `EinsteinRelation` (zero_flux_iff, einstein_vortex), `FrictionKinetic` (alpha, rhoN, coeff_eq_weighted_mean, weighted_mean_mem_Icc; rayleigh_jeans_mean named), `QuasiPeriodicBound` (msd_bound, not_qp_of_msd_large named).
* **New Lean** (declared new in the text): `book/lean/Ch07_DissipativePairs.lean`: `corot_sq_law` (same-sign pair, d^2 = d0^2 + 4 alpha t), `wind_stall_at_b`, `wind_no_zero`, plus `r2_hasDerivAt`, `roots_spec`, `stall_fence`, `stall_needs_start`. Compiled with Lean 4.34.0-rc2 and the pinned Mathlib (OpenAI tree, no `lake update`): exit 0, no error, no `sorry`; own `#print axioms` lines: **propext, Classical.choice, Quot.sound** for all seven.
* Axioms of every quoted library theorem: the three library modules carry no `#print axioms` lines, so scratch copies with one line per theorem were compiled on 2026-10-09 (log in `facts/ch07_lean_axioms.txt`): all standard three, no `sorry`.
* **For the editor:** `\Lthm{DissipativePairs}{corot_sq_law|wind_no_zero|wind_stall_at_b}` are not in `lean_src/` (expected); `\Lthm` prints them as `QuantumFluids.DissipativePairs.*`. Line references quoted in captions were checked (`DissipativeVortexDynamics.lean` 88-96, `Ch07_DissipativePairs.lean` 41-51).

## 5. Where the numbers come from

* From my own scripts (saved in the JSON): CVODE results; imprint control (archived G1 tracks + maps); fresh run; archived-ensemble re-analysis (`prod_e0.60_*`, `G2_e0.60_*` tracks); Table 1.1 (`production_estimates.json`); six-arm statistics (`transport/fl/friction_law_results.json`: alpha/T 0.0540+-0.0026, chi2 1.28/5; regression 0.0598+-0.0023; c by cutoff 0.31/0.232/0.102; common c chi2 76/5; spread 0.98; Born chi2 204/2); bath table numbers (`ch07_bath.py`); kicks (`island_I1_I2.json`); wind data (`W1_*`, `W2_L96_*`, `W2_result.json`: 1 of 4 meets, REFUTED); bias scan (Rust `g0_scan --eta-scan`, 8 seeds); pair speed (`pair_speed_T0.json`).
* Quoted from the ledger or the programme's papers, **not recomputed**: CLAIM-075 (four fits, window), CLAIM-078/079 (imprint diagnosis), CLAIM-080 (G2 window 0.00705+-0.00012), CLAIM-081/082 (alpha' values, fluid-frame +1 %/+0.4 %, baseline-subtracted alpha'), CLAIM-086 (exponents 1.24/1.10 on lags >= 100), CLAIM-097 (FL-A1 window and its 0.2/1.0 sigma), CLAIM-098 (2 of 12 seeds; independence of detection noise), T_BKT(L=64)=0.821 and "energy conserved to 1e-7..1e-6" (paper/vortex_transport.tex; the fresh run's own drift, 6.8e-8, is measured).
* Discrepancies found and how the chapter handles them (please keep in mind when merging):
  1. Ledger/results note quote the T=0 box-frame pair-speed ratio as 1.06 (d=6) and 1.49 (d=16); the saved `pair_speed_T0.json` gives 1.052 and 1.462. The chapter quotes the file and mentions both; the fluid-frame correction is attributed to the ledger ("not re-derived here"); I could not reproduce it from the file with u = 2 pi d / L^2.
  2. Bias at eta=1e-3: ledger says -18 %, the 4-decimal means give -18.5 %; the chapter prints -8.5, -18.5, -22 %.
  3. CLAIM-097 "0.2 sigma / 1.0 sigma" mixes the assumed and the actual error; attributed to the ledger.
  4. R_E errors in the ledger are eta-only (alpha held fixed); the chapter says so and notes that alpha's own error is 67 % at T/T_BKT = 0.43.
  5. Archived W1 pair 1 reaches 8.8-8.9, not 9.3 as in the paper text; the chapter uses the recomputed numbers (and W3 slopes 0.69/0.51 against the ledger's 0.68/0.52).
  6. Modin-Viviani: the ledger writes 2020 (arXiv); the bib entry is the survey in Arnold Math. J. 7 (2021), arXiv:2003.00716. The text only says "integrability of few-vortex flows" (the ledger notes that N = 4 on the torus is not covered).
  7. FACTS section 2 correction applied: no "about fifty points" for PRB 103, 104516.

## 6. Citations

* New keys in `refs_ch07.bib`: Moon2015, Neely2024, Mehdi2023, Shukla2014, ThoulessAoNiu1996, Sonin1997, Iordanskii1964, AHNS1980, Sergeev2023, KrstulovicBrachet2011, ModinViviani2021, WeissMcWilliams1991, Rorai2013, Grani2025. Other keys come from the shared `refs.bib` (Landau1941, Donnelly1991, Godfrin2021, Callens2026a/b/sw/lib, Hindmarsh2005, Davis2001, Blakie2008, KosterlitzThouless1973). **`WeissMcWilliams1991` and `AHNS1980` are also defined in `refs_ch01.bib`/`refs_ch06.bib`** (same content): BibTeX will warn about repeated entries when the files are merged; harmless.
* Verified earlier in the session from fetched abstracts/PDFs: the claims taken from Moon 2015, Neely 2024, Mehdi 2023, Thouless-Ao-Niu, Sonin, Iordanskii, Ambegaokar et al., Sergeev, Krstulovic-Brachet 2011, Rorai 2013, Grani 2025, Weiss-McWilliams. Re-read today in full: Shukla-Brachet-Pandit (arXiv:1412.0706): alpha' "smaller than alpha in magnitude, but nonzero", no error bars; T up to about 0.2 of their estimated T_BKT.
* **Not re-checked**: the coverage of Donnelly's book (cited as general reading), the exact "0.18 T_BKT" of the programme paper (not used in the chapter), Landau 1941 and the other shared-bib references beyond what the chapter says about them.

## 7. Process disclosures

* The first instrument of the programme failed its T=0 control and the chapter says so (Section 1.5); W2 is refuted; CLAIM-075 withdrawn; the reading alpha ~ rho_n with a vortex-owned coefficient and the "1.4 xi core size" withdrawn; Iordanskii prediction refuted at 18 sigma; Einstein relation undecided by the registered rule; energy-estimator bias.
* The fresh run is one seed, drawn once and not replaced. An **interim analysis at the checkpoint t = 1000** (made to test the pipeline while the last chunk waited for the lock) gave alpha_E = -0.0013; the finished run gives 0.0056 (the mean of the 8 archived runs over the same duration is 0.0057, sd 0.0020). Both are reported in the text; the t = 1000 values are reproducible from the final track (`fig_friction.fresh_run.first_1000`).
* A bug in my own chunked run script was fixed before the real run: the sample at a chunk edge was recorded twice (fixed with a skip on resume, tested on smoke runs).
* Items I could not do: nothing run on GPU; no external messages; no commits.
