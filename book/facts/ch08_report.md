# Chapter 8 report: Two-Dimensional Fermi Liquids: Zero Sound and the Roton Mode

Author's report to the editor, 2026-10-10.  Everything below was done under `book/` (plus scratch in the session scratchpad and
data under `/mnt/data/xdev-cache/book_ch08/`); nothing was committed, pushed, deposited or sent; `figstyle.py`, `qfbook.sty`,
`refs.bib` and the other chapters were not touched.

## 1. Deliverables

| file | what |
|---|---|
| `chapters/ch08.tex` | the chapter: 9 numbered sections + Exercises + Notes; 5 figures, 3 tables, 6 Lean boxes (9 statements), 2 Rust boxes, 1 Godfrin box, 1 key box, 1 honest box; about 5 700 words of prose + 600 words of captions; **20 book pages** (standalone count, ToC and bibliography excluded; the chapter sets looser float parameters at its start and restores the LaTeX defaults at its end; if you need to cut, the Vlasov table and the solver-notes paragraph of section 8.5 are the least essential) |
| `chapter_wrapper_ch08.tex`, `refs_ch08.bib` | my wrapper (`\bibliography{refs,refs_ch08}`) and the bib: `Godfrin2010` (new, verified), `MouhotVillani2011` (new, verified), `Bedrossian2026` (**identical to the entry in `refs_ch10.bib`**; `build_refs.py` keeps the first) |
| `figures/ch08_{zerosound,window,timedomain,fermisurface,vlasov}.{py,pdf,png}` | the five figures and their scripts |
| `figures/ch08_numbers.json` | every number the chapter quotes (keys: `zerosound`, `window`, `timedomain`, `fermisurface`, `vlasov`, `python_module_stale_venv`, `python_module_5db8041`, `cvode_output_spacing_sweep`) |
| `figures/ch08_numbers.tex`, `figures/ch08_numbers_tex.py` | the number macros: every measured/computed number in the text is `\ceightV{key}`, generated from the JSON (an undefined key is a LaTeX error); the only numerals typed by hand are definitions (F values, grids, tolerances), exact fractions, citations |
| `figures/ch08_theory.py`, `ch08_style.py` | closed forms (checked numerically, see section 4); `ch08_style.py` is now only a shim (`from figstyle import *; save8 = save`) since your figstyle fix; all five figure scripts were RE-RUN after that fix and the PNGs inspected (true minus signs, lining digits, no empty boxes) |
| `figures/ch08_kinetic_run.py`, `ch08_solver_sweep.py`, `ch08_wheel_check.py`, `ch08_make_all.sh` | batch driver of the CVODE runs, solver-defect sweeps, module check, and the documented pipeline order |
| `figures/ch08_statsline.txt` | the driver's own STATS line quoted verbatim in the rustbox (`\lstinputlisting`) |
| `figures/ch08_lean.json`, `figures/ch08_lean_compile.log` | compile result of the new Lean module |
| `rust/ch08_kinetic/` (new), `rust/ch08_vlasov/` (rewritten) | the two drivers (path dependencies on `/home/xavkal/xdev/rusty-SUNDIALS-c3`, commit `5db8041fd2e3840defcff2b4a8c26c1cbb2467fd`, crates `cvode` 6.4.0 and `qf-vlasov1d`); build with `CARGO_TARGET_DIR=/mnt/data/xdev-cache/cargo-target-book8` |
| `lean/Ch08_ZeroSound2D.lean` | the new Lean module (namespace `QuantumFluids.ZeroSound2D`) |
| scratch: `ch08_build1..15.*`, `ch08_test1.*`, `chapter_wrapper_ch08_test.tex` in `book/` | LaTeX build files of fresh jobnames and one float-parameter test (rm/mv are denied to me); safe to delete. The final PDF is `ch08_build15.pdf` |

## 2. Compile status

* `lualatex -interaction=nonstopmode -jobname=ch08_build15 chapter_wrapper_ch08.tex`, `bibtex ch08_build15`, twice more: **0 errors, 0 overfull boxes, no missing glyphs, all figures present**.  The only warnings are the two undefined `\cref{ch05}` (the other chapters are not in a standalone build).  Standalone, the chapter prints as "Chapter 1".
* Lean: `cd /home/xavkal/xdev/OpenAINavierStokesEuler/NavierStokesAndEuler && flock <lock> nice lake env lean book/lean/Ch08_ZeroSound2D.lean` (Lean 4.34.0-rc2, that tree's Mathlib): exit 0 (twice, two independent runs), the only output lines are the nine `#print axioms` lines, **all `[propext, Classical.choice, Quot.sound]`**, no error, no warning, no `sorry` (the word appears once, in the header comment).  CPU 36 s; 57 min wall because of the queue on the shared lock.  First attempt had one error (a superfluous `nlinarith` after `field_simp` closed the goal in `pole_weight`); fixed, statements unchanged.
* Float placement: figures and tables use `[tp]`, not `[t]`: with `[t]` the large figures cannot sit at the top of a page (more than 70 % of the text height) and all five were queued to the end of the chapter; one short Lean box (`maxwellian_mode`) is `[unbreakable]`.
* `\Lthm{ZeroSound2D}{...}` cites the NEW module (not in `lean_src`): your automatic checker will report "unknown module" for these (and for the leanbox titled `Ch08\_ZeroSound2D (new in this book)`); the printed name `QuantumFluids.ZeroSound2D.<name>` is the true namespace.  I checked every leanbox statement myself against its source (whitespace-normalised): 9 of 9 identical (4 library: `zero_sound_2d_iff`, `g3`, `zero_sound_iff`, `maxwellian_mode`; 5 new: `omega2`, `s0`, `zero_sound_2d_unique`, `pole_fraction`, `ph_gap`).

## 3. Facts about Godfrin's work: what I verified, and how

FACTS section 2 was the base.  I added the following from the **abstracts of the two papers**, read from the raw HTML of the publisher records mirrored by the University at Buffalo research portal (`researchconnect.buffalo.edu`, pages for "Observation of a roton collective mode in a two-dimensional Fermi liquid" and "Observation of zero-sound at atomic wave-vectors in a monolayer of liquid 3He"; abstract block and `citation_*` meta tags extracted by a script, not through a summarising tool; a WebFetch of the same pages gave the same text; Crossref has no abstract field for the Nature DOI):

* Nature 483(7391), 576-579, 29 March 2012, doi:10.1038/nature10919, authors as in FACTS; abstract (quotes in the chapter are exact words from it): "essentially incoherent", "unexpected collective behaviour", the collective mode "reappears as a well defined excitation at momentum transfers larger than twice the Fermi momentum", "monolayer of liquid 3He", "dynamic many-body theory".
* J. Low Temp. Phys. 158(1-2), 147-154 (2010), doi:10.1007/s10909-009-9952-5, H. Godfrin, M. Meschke, H.-J. Lauter, H. M. Böhm, E. Krotscheck, M. Panholzer; abstract: monolayer of 3He on graphite preplated with a monolayer of solid 4He; the zero-sound mode "above a particle-hole band", "very close to the particle-hole band" at low wave vectors "contrarily to bulk 3He", entering the band and "strongly broadened by Landau damping", and at high wave vectors "reappears beyond the particle-hole band as a well defined excitation, with a dispersion relation quite similar to that of superfluid 4He".
* **Discrepancy with FACTS section 2**: FACTS says "(a few atomic layers on a substrate)"; both abstracts say "monolayer" (of 3He; the 4He pre-plating is a further layer).  The chapter says "monolayer" and quotes the abstracts.  Please decide whether FACTS section 2 should be amended.
* Not re-checked: "far longer lived in 2D than in the bulk liquid" (FACTS section 2, news item); attributed in the chapter to "the programme's notes, from the neutron-sources news item".
* Citations checked against the raw Crossref JSON (2026-10-10): Godfrin et al., JLTP 158(1-2), 147-154, doi:10.1007/s10909-009-9952-5 (authors Godfrin, Meschke, Lauter, Böhm, Krotscheck, Panholzer; online Oct 2009, print Jan 2010, cited as 2010); Mouhot-Villani, Acta Math. 207(1), 29-201 (2011), doi:10.1007/s11511-011-0068-9; Godfrin et al., Nature 483(7391), 576-579, doi:10.1038/nature10919 (7 authors as in FACTS).  Bedrossian, arXiv:2609.16801, "Formalization of Landau damping in the Vlasov-Poisson equations in Lean", submitted 15 September 2026: arXiv abstract page (WebFetch summary), same entry as in `refs_ch10.bib`.
* `refs_ch08.bib`: isotopes are braced in titles (`{$^3$He}`), notes reduced to the DOI.  `Godfrin2012b` (Sultan et al.) is not cited by this chapter.
* No claim about Godfrin's person, opinions or the library's relation to him; no numbers from the data; the film's Landau parameters are stated as unknown (LEDGER CLAIM-030/031 read; `docs/designs/ZERO_SOUND_LANDAU_DAMPING_PROPOSAL.md` read).
* Unsourced general reasoning, to be kept or cut at your discretion: "a single adsorbed layer holds very little matter ... so the scattering signal is small" (section 8.1).

## 4. Physics derived here and how each statement was checked

All are derived in the text; each was also checked numerically (script in parentheses):

* closed form of the structure factor `S(s) = s sqrt(1-s^2) / (pi[(1+F)^2-(1+2F)s^2])` equals `Im Omega/(pi|1+F Omega|^2)` to 1.1e-15 (`ch08_zerosound.py`, key `sum_rule_2d`);
* pole weight `W = F/(1+2F)^{3/2}`, f-sum rule `int s S ds = 1/4` for F in {-0.9,...,15} to 6.3e-15, continuum alone `1/(4(1+2F)^2)` for F>0 and `1/4` for F<=0;
* time domain: `m(t) = J0(t)` at F=0, `2 J1(t)/t` at F=-1/2, the pole+cut formula (8.10) for any F, the kick signal = sine transform of S: each compared with the CVODE integration (errors 4e-9 .. 1e-6; `ch08_timedomain.py`);
* conserved form `E = <|nu|^2> + F|<nu>|^2` (drift 3e-8 .. 2e-6), growth rate 1/sqrt(3) at F=-2 (fit 0.577350 vs 0.577350), envelope slopes -1/2 (F=0) and -3/2;
* kinematic window of the free gas (Lean, plus figure); `F* = 3+2 sqrt 3` and `q_c = 2k_F(s0-1)` closed forms.
* Maxwellian root at k=0.5: my mpmath root equals the programme's certified root (1.415661888604536, -0.153359466909605) to 4.4e-16.

## 5. Where every quoted number comes from

`figures/ch08_numbers.json` (written by the scripts listed in the deliverables table); macro families in `ch08_numbers.tex`:
`s0_*, s3_*, qc_*, W_*, frac_*, amp_*` closed forms (`zerosound.roots_2d/3d`); `contErr*, contRes*` Davidenko continuation by CVODE vs closed form / 40-digit mpmath root; `errU_*, errK_*, edrift_*, stepsU_*` BDF runs vs closed forms (`timedomain.uniform_IC / kick_IC`); `fitW_*, fitA_*, omegaFit*` pole fits; `expo_*` envelope slopes; `tol_*`, `sweep*`, `mod_*` solver notes; `vm*`, `vf*`, `fs*`, `cons*` Vlasov (`vlasov.*`); `growth*` F=-2 run; `reconF*` Fermi-circle reconstruction vs nodes.  Timing is quoted only with the machine caveat (load average read between 11.9 and 34.9; the same F=0 job took 7.1 s and 12.7 s in two runs of one batch; F=4 took 15.9, 46.5 and 13.6 s on three occasions).

## 6. Solver provenance and defects found

* All CVODE results: the Rust crate `cvode` 6.4.0 of `/home/xavkal/xdev/rusty-SUNDIALS-c3` at commit 5db8041 (path dependency, no local modifications to `crates/cvode` or `crates/qf-vlasov1d`), **BDF**, analytic Jacobian, rtol 1e-8, atol 1e-10 (N=64 half-circle nodes).  No production number uses a Python `CvodeSolver`.
* Python modules (`ch08_wheel_check.py`, recorded with `rusty_sundials.__file__`): the venv module (`.venv/.../rusty_sundials/rusty_sundials.cpython-312-x86_64-linux-gnu.so`, dated 2026-09-26) fails with "too many error test failures at one step" at rtol 1e-8 and 1e-10 on N=32, t=0.5, and its Adams errors scale as sqrt(rtol) (1.9e-4, 1.9e-5, 1.9e-6); the editor's build `/mnt/data/xdev-cache/rs_py_5db8041/rusty_sundials.so` (commit 5db8041) passes the same tests with both methods (errors 1.7e-7 .. 1.7e-10).  The chapter text says this (section 8.5).
* **Defect of the Adams option of the crate at 5db8041, not understood and not investigated**: on the undamped linear system of the chapter the Adams method is accurate for a single call to t=60 or for output spacings 0.01, 1, 5, 10, 20, 60, but gives 3.3e-3 (analytic Jacobian) or 4.7e-2 (differenced) at spacing 0.1 with N=4, and errors 11 / 0.19 / 4e-4 at rtol 1e-6 / 1e-8 / 1e-10 at N=64, spacing 0.1; BDF stays within 3e-8 .. 1.2e-6 for all spacings (`ch08_solver_sweep.py`, key `cvode_output_spacing_sweep`).  Possibly worth an issue upstream; I contacted nobody.
* Vlasov: `qf-vlasov1d` driver rewritten (two backgrounds, edge-displaced degenerate initial state, signed series); first draft used the Rust peak-spacing estimator whose rate for the weakly damped degenerate run came out positive (+8.3e-5 at k=0.5); replaced by least-squares fits; rates below ~1e-4 are not claimed (told in the honest box).  Weak-damping formula used for the theory curve and for |gamma| at k=0.3 (the continued root is noise-limited there: 2.4e-9 vs 1.2e-9).

## 7. Things the editor must check or may want to change

1. Page count: 20 chapter pages in the standalone build (target 14-20); it depends on the float parameters (`\topfraction` etc. are set at the start of `ch08.tex` and reset at its end; with the LaTeX defaults the chapter needs 21 pages).  Cuts that cost least if you need room: Table 1.3, the second half of the solver notes in section 8.5.
2. `\Lthm{ZeroSound2D}` and the `Ch08\_ZeroSound2D` leanbox title will be flagged by the citation checker (new module, see section 2).
3. Duplicate bib key `Bedrossian2026` with `refs_ch10.bib` (same content).
4. FACTS section 2 "a few atomic layers" vs "monolayer" (section 3 above).
5. Cross-references used: `\cref{ch05}` only.
6. CLAIM-030/031 are cited by number in the text (read from `LEDGER.md`); the statement that the "Pomeranchuk is Penrose" formalisation was stopped at the literature gate is from CLAIM-030.  The chapter does not claim a stability theorem; the energy-conservation argument of section 8.6/Exercise 3 is elementary and is not in the library.
7. Accident: while rendering pages I wrote PNGs `p-01..p-25.png` into `scratchpad/pages1/`, which belongs to another author (I had assumed the name was free); no book file is affected.
8. Machine-dependent items: figure scripts need `/mnt/data/xdev-cache/cargo-target-book8/release/{ch08_kinetic,ch08_vlasov}` and the data under `/mnt/data/xdev-cache/book_ch08/`; `ch08_make_all.sh` documents the order (about an hour on the loaded machine).
9. I did not run `facts/make_appA.py` (it rewrites shared files).
