# Chapter 2 — "Two Languages: Lean 4 and rusty-SUNDIALS": author's report

Author's session 2026-10-09/10. Nothing outside `book/` and the session scratchpad was written, except that the editor copied my Python-module build to `/mnt/data/xdev-cache/rs_py_5db8041` (after my message to him).
No commit, no push, no deposit.

## 1. Files produced

| file | content |
|---|---|
| `chapters/ch02.tex` | the chapter: about 5 800 words of prose (no code, captions or maths) plus 500 words of captions; 5 figures, 1 table, 7 code boxes (4 Lean, 3 Python), honestbox, 3 exercises, notes |
| `figures/ch02_stability.{py,pdf,png}` | Fig. 1: regions of absolute stability of Adams–Moulton (orders 3–6) and BDF (1–5), computed by a root test on a grid (visually striking) |
| `figures/ch02_workprecision.{py,pdf,png}` | Fig. 2: CVODE through the Python module on problems with closed forms (work–precision, stiffness scan, amplitude of the oscillator, the Adams defect before/after) |
| `figures/ch02_planewave.{py,pdf,png}` | Fig. 3: the exact plane wave against numpy/Rust IF-RK4 and CVODE; order test; cost; norm drift |
| `figures/ch02_bridge.{py,pdf,png}`, `ch02_rates.{pdf,png}` (same script) | Fig. 4: aliasing geometry — engine's cubic term against a literal transcription of `GPGalerkin.nl` (visually striking); Fig. 5: rates of mass and momentum, and drifts |
| `figures/ch02_compute.py` | all computations (parts env, A–E), writes `figures/ch02_numbers.json` |
| `figures/ch02_snippets.py`, `ch02_snippets_output.txt` | the code boxes of the chapter and their output |
| `figures/ch02_listings.py` | `splice` / `check`: keeps the 7 marked Python listings of `ch02.tex` verbatim copies of their sources (`check` passes) |
| `figures/ch02_numbers.json` | every number of the text (keys `env`, `A_order`, `B_cvode`, `C_planewave`, `D_invariants`, `E_bridge`, `F_stability`) |
| `lean/Ch02_Primer.lean` | NEW Lean: types/propositions, `Float` versus `ℝ`, a `linear_combination` certificate |
| `lean/Ch02_Galerkin.lean` | NEW Lean: exact plane wave of the Galerkin system, momentum-rate identity, no additive momentum on a torus |
| `lean/Ch02_NegativeControl.lean` | a file that is **MEANT to fail** (two false statements; its compiler output is quoted in the chapter). Please exclude it from any audit or appendix listing, or list it as an expected failure |
| `facts/ch02_lean_logs/*.compile.log` | compiler output of the three files, and of the first draft of the primer (with `sorryAx`) |
| `refs_ch02.bib` | 7 new entries (§6) |
| `rust/ch02_build_py.sh` | how the Python module of rusty-SUNDIALS was built (about 3 minutes, writes nothing to the checkout) |
| `chapter_wrapper_ch02.tex` | my private wrapper (ignored by `.gitignore`); my build products are `ch02_build.*` in `book/` (jobname `ch02_build`; `rm` is denied to me, please ignore them) |

## 2. Compile status

* **LaTeX** (LuaLaTeX, `lualatex -interaction=nonstopmode -jobname=ch02_build chapter_wrapper_ch02.tex`, bibtex between, three passes): **0 errors**; one overfull box of 0.66 pt; no missing glyph; no font warning; all five figures present. Undefined references only to material outside the chapter: `\cref{ch04}`, `\cref{ch10}`, `Appendix~\ref{appA}`. Standalone layout: 21 book pages (PDF pages 3–23 of `ch02_build.pdf`: chapter opener, text, five floats on `[tp]` pages with some white space, honestbox, exercises, notes); about 1 page above the target — the editor can drop Fig. 5 or Exercise 2 if the book needs the room.
* **Lean** (`cd OpenAINavierStokesEuler/NavierStokesAndEuler && nice lake env lean <file>`, Lean 4.34.0-rc2): `Ch02_Primer.lean` exit 0; `Ch02_Galerkin.lean` exit 0, 0 errors, 0 warnings (two linters are switched off at the top of the file), no `sorry`; `Ch02_NegativeControl.lean` fails by design (2 errors, quoted in the chapter). Files compiled exactly as they are now (sha256 `Ch02_Primer` f4b024cf…, `Ch02_Galerkin` 187ec1da…, `Ch02_NegativeControl` 862a6b2d…).
* **Axioms.** `Ch02_Galerkin.lean`: all ten audited declarations depend on exactly `[propext, Classical.choice, Quot.sound]`. `Ch02_Primer.lean`: `and_swap'` none; `two_add_two`, `tenth_plus_fifth` the three; `one_add_nilpotent_inv` `[propext, Quot.sound]`. **No new axiom, no `sorryAx`.**
* **The editor's citation check** (`facts/make_appA.py`, `scan_chapters`, run read-only on `ch02.tex` only): 16 declarations cited, **0 problems**, 12 leanbox copies, all `identical` (3 statements of `GPGalerkin`, 3 of `Ch02_Primer`, 6 of `Ch02_Galerkin`; the boxes are titled `new: Ch02\_Primer` / `new: Ch02\_Galerkin`, which `canon()` resolves to `book/lean`).
* **Listings.** The Python boxes and their outputs are generated from `ch02_snippets.py`, `ch02_compute.py::lean_nl` and `ch02_snippets_output.txt` (`python3 book/figures/ch02_listings.py check` passes). Non-ASCII characters in all Lean listings are inside the set covered by the editor's `qf_unicode_lst.tex` (I looked at the pages: order of characters is correct).

## 3. The finding that matters outside this chapter: the shared virtual environment's `rusty_sundials` is stale

`.venv/.../rusty_sundials` was built on 2026-09-26 and has the **pre-fix Adams method** (implicit Euler: `Method::Adams` never left order 1 until the repair documented in rusty-SUNDIALS `docs/CVODE_ADAMS_FIX.md`, dated 2026-09-28). Evidence (`figures/ch02_numbers.json`, keys `B_cvode.decay_stale_venv_module` and `decay_adams_fix`; y' = −y, t = 10, atol 1e-14), RHS calls / relative error at rtol 1e-4, 1e-6, 1e-8, 1e-10:
stale module 2 386 / 6.5e-2, 23 750 / 6.4e-3, 237 022 / 6.4e-4, 2 214 597 / 6.9e-5 (the "unfixed" column of the repair document);
current build 168 / 5.9e-4, 359 / 1.9e-5, 511 / 2.0e-7, 616 / 1.7e-9. The stale module's BDF also differs from the current source (e.g. 335 against 246 calls at rtol 1e-4).
The editor has copied my build to `/mnt/data/xdev-cache/rs_py_5db8041` (commit `5db8041fd2e3840defcff2b4a8c26c1cbb2467fd`, sha256 `0bdb1b4a…fb996d7`, identical to my scratchpad copy; I verified). `ch02_compute.py` refuses to run with a module whose Adams path takes more than 5 000 RHS evaluations on y' = −y, and records the module path and sha256 in `ch02_numbers.json` (`env`).
Run with `PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext`. All parts A–E were re-run with the stable path after the last edit of the scripts (2026-10-10, 00:50–00:57); the numbers are identical to those of the earlier runs, which used the scratchpad copy of the same binary (same sha256) — counts and errors are deterministic, wall times are not used in the chapter. Part F (stability figure) does not use the module.

## 4. Where every number of the text comes from

| text | source |
|---|---|
| §1: momentum drift 8.54 (8.5358 at dt 0.005, 8.5358 at 0.01), norm 4.2e-10, plane wave 7.0e-10; N=64, L=32, t=20, random state of energy 3 per particle | `data/generated/pgpe/known_answers.json` (stored first run; the configuration is in `exploration/pgpe/known_answers.py`); `docs/designs/PGPE_BKT_PREREG.md`, Amendment A1 ("1 % of P", the 2/3 rule, date 2026-09-22) |
| §1/§3: pre-registration sentence that K1–K3 are theorems of `GPGalerkin` | `docs/designs/PGPE_BKT_PREREG.md` §4; checked against `lean_src/GPGalerkin.lean`: mass and energy algebraic cores only, no momentum (`grep -i momentum lean_src/*.lean` finds nothing about `nl`) |
| §2: 37 modules, 310 theorems/lemmas, 413 declarations, Lean 4.34.0-rc2 | `facts/make_appA.py` docstring, `facts/lean_index.md`, `facts/lean_audit.md` |
| §2: outputs `2 : ℕ`, `[0, 1, 4, 9, 16, 25]`, `0.300000`, `false`, axiom lines, negative-control errors, the `sorryAx` line | `facts/ch02_lean_logs/` |
| §3: statements of `nl`, `pairing_eq_sum`, `mass_rate_zero`; "all thirteen theorems depend on the three axioms" | `lean_src/GPGalerkin.lean` (verbatim); `facts/audit/GPGalerkin.log`; new statements: `lean/Ch02_Galerkin.lean` |
| §4: Adams 1–12, BDF 1–5, Newton + dense LU of I−γJ for both, finite-difference Jacobian (n extra RHS calls), weights 1/(rtol\|y\|+atol), Nordsieck array, BDF order rule "simple heuristic" | `rusty-SUNDIALS-c3/crates/cvode/src/{constants,solver,step,nordsieck}.rs` (read); Python API `crates/rusty-sundials-py/src/lib.rs` (read) |
| §4: Rust step 4.3/4.2/2.7/2.5 faster than numpy (N = 64…512), 2013 four-core CPU with external load | `paper/sw_numbers.tex`, `paper/qf_pgpe_software.tex` (quoted, not repeated) |
| §4: ≈3 200 modes at 128², 330 MB | `PGPE_BKT_PREREG.md` Amendment A1; 6 400² × 8 bytes = 328 MB is arithmetic |
| §4: Adams defect, repair date 2026-09-28, "fails after about 10^6 evaluations" | `rusty-SUNDIALS/docs/CVODE_ADAMS_FIX.md`, `paper/qf_pgpe_software.tex` §3, header of `crates/qf-pgpe/tests/cvode_crosscheck.rs` |
| §4 box: 1549 / 5217 calls, 3.76e-7 / 2.53e-6 | `figures/ch02_snippets_output.txt` |
| §5: stability intercepts −6.00/−3.00/−1.84/−1.18, angles 90/90/86.0/73.4/51.8 | `ch02_numbers.json`, key `F_stability` (coefficients asserted against their order conditions in exact rational arithmetic by `ch02_stability.py`). EDITOR 2026-10-10: the intercepts were grid-limited (step 0.02: order 5 printed −1.82, true −1.8367); the script now bisects (−6.0000, −3.0000, −1.8367, −1.1842), confirmed by an independent dense root-condition scan; the angles were confirmed by an independent boundary-locus computation (86.032°, 73.352°, 51.840°); "textbook values" removed from the caption (not checked against the page) |
| §5: 19 tolerances, cheapest runs below 1e-8 (1 880 vs 12 769), rtol 1e-5 (704, 4.1e-5) vs 1e-6 (3 327, 5.0e-4), 255→5 565 vs 470→418 (13×), amplitude +4.9 % / −1.1 %, +0.004 % / −0.043 %, 11 of 19 | key `B_cvode` (`oscillator`, `prothero_robinson`, `amplitude_vs_time`); stale/fixed: `decay_*` |
| §6: errors 1.8e-7 / 1.1e-8 / 7.0e-10 (ratios 15.9, 16.0), numpy–Rust difference 4e-14, norm drift 7e-12, g = 0: 1.1e-14, K4 at N = 64: 7.0e-10 | key `C_planewave` (`engine_series`, `K4_registered`, `free_g0`); box output `ch02_snippets_output.txt` |
| §6: order 3.999 (Rust route; output identical to `data/generated/pgpe/bench/cvode_order.json`), 3.997 (Python route), ratios 15.99/16.00/16.00/15.97, 482 evaluations in 95 steps, 0.8 % | key `A_order` |
| §6: CVODE on the 16×16 plane wave (1 530 / 788 / 701 / 1 143; BDF 2 364) and IF-RK4 (≈3 400, interpolated) | key `C_planewave.cvode_N16`, `engine_N16` |
| §6: norm drifts of IF-RK4, Adams, BDF on the order-test state | key `D_invariants` |
| §7: 7.85e-16 / 1.15e-3 (4 modes) / 0.153 (348 of 357); rates; Q = 1.403114631989707 against Σ\|A_q\|² = 1.4031146319897068; drifts at t = 10, 20 | key `E_bridge`; box output `ch02_snippets_output.txt` |
| Exercise 2 counts (5 270, 431; "maximum steps exceeded (300) at t=1.77") | run in the session (not stored in the JSON; the 5 270 and 431 are in `B_cvode.prothero_robinson`); reproduce with the code of the exercise |

## 5. Claims I could not verify, or verified only partly (the editor should look)

* The numpy transcription `lean_nl` of `GPGalerkin.nl` is a hand transcription; it is tested by the identity `Q = Σ|A_q|²` (`pairing_eq_sum`) to 16 digits and by the vanishing of the two rates of the literal definition, not by a machine.
* The chapter calls the K2 control "energy drift ∝ Δt⁴" (as in the registered table) and says the Rust port tests the order against CVODE; the software paper calls the same Rust test "K2". I kept the two apart in the text.
* The *cause* of the saturation of the Adams cost on the stiff problem (fallback to orders 1–2?) is **not traced**; the chapter says so (the Python API does not report the order).
* "BDF dissipates on oscillations" is stated as a measured fact (19 of 19 runs) plus a general reference to Hairer–Wanner II; I did not check the book page.
* Nothing is claimed about the C SUNDIALS library (defaults, behaviour); only the Rust source was read.
* The momentum drift at the one-half cutoff (Fig. 5b) mixes truncation error and edge-mode aliasing: not separated (the chapter says so).
* "Float is the machine's double-precision number" is from my knowledge of Lean, not from a documentation check; the printed outputs are real.
* The agreement of the computed A(α) angles (90°, 90°, 86.0°, 73.4°, 51.8°) and of the real-axis intercepts (−6, −3, −1.8, −1.2) with "the textbook values" is from my memory of Hairer–Wanner (not checked against the page); the computation itself is self-contained and its inputs were asserted against their order conditions.
* The 0–3 Å⁻¹ range in the Godfrin box is attributed to "the programme's reading" as in FACTS §2.
* The date: the chapter says the first run of the controls was "recorded in an amendment dated 22 September 2026" (A1); the run itself may be earlier the same day or before.

## 6. External facts and references checked on the web (2026-10-09/10; WebSearch)

* Prothero & Robinson, Math. Comp. 28 (125), 145–162 (1974) — AMS page found.
* Orszag, J. Atmos. Sci. 28 (6), 1074 (1971) — title, volume and page seen in several citing sources; they attribute the two-thirds rule to it. DOI not checked.
* Dahlquist, BIT 3, 27–43 (1963) — seen (Springer page).
* Hairer, Nørsett, Wanner, *Solving ODEs I* (Springer Series in Computational Mathematics 8, 2nd rev. ed., 1993) and Hairer, Wanner, *Solving ODEs II* (SCM 14, 2nd rev. ed., 1996) — Springer / catalogue pages found.
* *Theorem Proving in Lean 4* (Avigad, de Moura, Kong, Ullrich) and *Mathematics in Lean* (Avigad, Massot; the author list differs between versions) — online books, consulted 2026-10-09.
These are the entries of `refs_ch02.bib`; everything else cited is in `refs.bib`.

## 7. For the editor

1. `\cref{ch04}`, `\cref{ch10}`, `Appendix~\ref{appA}` resolve only in the full book.
2. `refs.bib` entry `Godfrin2021`: the title contains `superfluid $^4$He`, which BibTeX lowercases to "$^4$he" in the printed bibliography. Protect it: `$^4${He}`. (Not my file.)
3. `lean_src/GPGalerkin.lean`: the header comment is out of date (it names `pairing_eq_sum_normSq`, the theorem is `pairing_eq_sum`; it says conservation of E is NOT proved although `grad_identity` and `energy_rate_zero` — the algebraic core, as their own doc comments say — are in the file). The chapter quotes the theorem doc comments, not the header.
4. `docs/designs/PGPE_BKT_PREREG.md` §4 says K1–K3 are theorems of `GPGalerkin`: only the algebraic cores of K1 and K2 are, K3 was not. The chapter says so (text and honestbox). `lean/Ch02_Galerkin.lean` now supplies the momentum statement (`momentum_rate_zero`; could be upstreamed to the library).
5. The stale `rusty_sundials` in `.venv` — §3. Chapters that call `CvodeSolver("adams", …)` (ch04 does; ch06, ch07 take the method as a variable) must rerun with the new module; BDF counts also differ slightly between the two builds.
6. Figures use a log-tick formatter without `\mathdefault`: EB Garamond has no U+2212, so matplotlib's default log formatter prints a missing-glyph box in the exponent of `10^{-4}` (`axes.unicode_minus=False` does not help for log axes). `figstyle.py` could install the same formatter for every chapter.
7. `Ch02_NegativeControl.lean` fails by design (see §1).
8. Standalone page count above; figure floats are `[tp]`.

## 8. Reproduce

```
cd /home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids
export PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext
flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice .venv/bin/python book/figures/ch02_compute.py        # about 3 minutes of CPU
.venv/bin/python book/figures/ch02_snippets.py > book/figures/ch02_snippets_output.txt
python3 book/figures/ch02_listings.py check
for f in stability workprecision planewave bridge; do .venv/bin/python book/figures/ch02_$f.py; done    # stability: 4 minutes on a loaded machine
cd /home/xavkal/xdev/OpenAINavierStokesEuler/NavierStokesAndEuler && for f in Primer Galerkin NegativeControl; do nice lake env lean /home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/book/lean/Ch02_$f.lean; done
cd /home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/book && lualatex -interaction=nonstopmode -jobname=ch02_build chapter_wrapper_ch02.tex   # bibtex ch02_build, then twice more
```
