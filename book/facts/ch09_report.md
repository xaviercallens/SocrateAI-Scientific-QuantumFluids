# Chapter 9 report: Flow Past an Obstacle: Reproducing a Published Experiment

Author: chapter-9 agent. Date of the last build: 2026-10-10. Everything below is under `book/` (paths relative to it) unless an absolute path is given.

## 1. Deliverables

| file | what it is |
|---|---|
| `chapters/ch09.tex` | the chapter (9 sections, 5 figures, 2 tables, 5 leanboxes, 2 rustboxes, 1 godfrinbox, 1 keybox, 1 honestbox, 3 exercises with hints, notes) |
| `figures/ch09_{wake,mach,force,census,birth}.py` and `.pdf` | the five figures (`.png` previews are written by the same scripts); `ch09_wake` is the phase/modulus field of the t = 50 wake |
| `figures/ch09_common.py`, `ch09_render.py` | shared numpy helpers (principal differences, plaquette census, port of the reference's detector, Mach map, ...) and matplotlib helpers (lining digits `lnum`, hyphen-minus because EB Garamond has no U+2212; `figstyle.py` is untouched) |
| `figures/ch09_birth_run.py` | numpy continuation of OUR t = 20 field to t = 25, sub-box stored every 0.1 tau (writes `/mnt/data/xdev-cache/qf-external/ch09/birth_t20_25.npz`; reproduces our Rust t = 25 snapshot to 1.2e-15) |
| `figures/ch09_numbers.py` -> `figures/ch09_numbers.json` | registry of every number of the chapter, recomputed from the raw files (22 top-level sections) |
| `figures/ch09_texnumbers.py` -> `figures/ch09_numbers.tex` | 221 macros `\cnine<Name>` generated from the JSON and nowhere else; `chapters/ch09.tex` does `\input{figures/ch09_numbers}` |
| `figures/ch09_fresh_run/{run_t1.out,run_t1.err,kwon_shin_force.csv}` | the output of the fresh `kwon_shin` run (t <= 1) shown in the second rustbox; read by `ch09_numbers.py` |
| `refs_ch09.bib` | 10 keys: KwonShin2026prr, KwonShin2026data, Raman1999, Kwon2015PRA, Kwon2016PRL, FrischPomeauRica1992, JosserandPomeauRica1999, Winiecki2000, Reeves2015, Kwak2023 (keys already in `refs.bib` are reused: Landau1941, Bogoliubov1947, Godfrin2021, GodfrinKrotscheck2022, Callens2026sw, Callens2026lib, PitaevskiiStringari2016, Donnelly1991) |
| `lean/Ch09_FlowPast.lean`, `lean/Ch09_FlowPast.compile.log` | the new Lean module (namespace `QuantumFluids.FlowPast`) and the log of its compile |
| `chapter_wrapper_ch09.tex` (+ `.aux .bbl .blg .log .out .toc .pdf`) | my standalone wrapper (`chapter_wrapper.tex` plus `refs_ch09`); the build files are by-products, nothing depends on them |

## 2. Compile status (standalone, from `book/`)

`lualatex -interaction=nonstopmode -halt-on-error chapter_wrapper_ch09.tex`, then `bibtex chapter_wrapper_ch09`, then lualatex twice (console output sent to the scratchpad, never to `<job>.out`).

* 26 pages: contents (2), the chapter (21 pages, the last one about one third full), a blank verso, bibliography (2).
* LaTeX errors: 0. Overfull boxes: 0 (the last build). Missing glyphs: 0. Undefined citations: 0. All five figure PDFs present.
* The only warning of substance is "There were undefined references": `ch03` (once), `ch05` (three times), `ch08` (once). They print as "??" in the standalone build and resolve in the book. Four Underfull hbox warnings (the worst, badness 10000, is one line of the `HeliumKinematics` paragraph that ends in a long unbreakable name and shows one wide inter-word gap) and four Underfull vbox warnings on float pages are cosmetic.
* Length: about 4 650 words of running text (inline formulas counted as words; boxes included; captions, tables and listings excluded) plus about 1 200 words in captions and tables; about 20 and a third book pages. So the prose is under the 5 000-word guideline while the pages are at its upper end (the five figures and the boxes take the room). If the editor wants fewer pages, the cheapest cuts are the second rustbox (fresh run) and the `HeliumKinematics` aside before "The initial field".
* The chapter shows 13 Lean statements in leanboxes (guideline: 2 to 5); each is used in the argument and explained in words.

## 3. What the chapter claims and does not claim

It reproduces the DEPOSITED numerical run of Kwon and Shin (Zenodo 20068724, the example case V0 = 0.9 mu, sigma = 20 xi, v = 0.55 c) with an independent scheme (explicit RK4, spectral, double precision, Rust `qf-pgpe::flow`) started from the deposited psi(0). It says in the first section that this is a computer experiment, that none of the laboratory experiments mentioned is reproduced, and that nothing in the chapter reproduces or tests a measurement of Henri Godfrin. The paper's own results (Strouhal number, drag coefficient, D_eff, Re_s = 2 transition) are quoted as the authors' and NOT reproduced. Godfrin is named in four places: the one-sentence statement above (FACTS section 2: neutron scattering on helium); the `godfrinbox` about the spectrum behind Landau's criterion (PRB 103, 104516 in the words of FACTS section 2 after the editor's correction, hence no point count; the review's paragraph on Landau's criterion, quoted in one fragment); the first "Proved" paragraph of the honestbox ("the library's Landau lemmas formalise a paragraph of the review of Godfrin and Krotscheck as inequalities between numbers, not as statements about a measured curve"); and the notes (the review and the 2021 spectrum are cited, nothing more). The aside on `HeliumKinematics` (equations 12 and 13 of the 2021 paper) says what the Lean theorems prove and that the resemblance to the ramp theorem is one of method.

## 4. Where every number comes from

Every number printed through a `\cnine...` macro is in `figures/ch09_numbers.json` (written by `ch09_numbers.py`, formatted by `ch09_texnumbers.py`; rerun both after any change). Sections of the JSON and their inputs:

| JSON section | input | used for |
|---|---|---|
| `dataset` | the Zenodo zip (`/mnt/data/xdev-cache/qf-external/20068724/Vortex-shedding-PRR-data-1.0.0.zip`: README, `input/*.json`, `spec.txt`, `src/gpe_dynamics/*.py`) | model constants V0, sigma, x_obs, v_f, t_ramp, grid, dt, damping layers |
| `paper_quoted_not_reproduced` | arXiv:2602.03518v1 read through alphaXiv on 2026-10-10 | v_c 0.18, v_th 0.33, Re_s 2, window 2000-10000 tau, fringe numbers 25/20/3 xi (the paper's Eq. (2)); equation numbers (1), (2), (5), (7) |
| `damping` | formula of `crates/qf-pgpe/src/flow.rs` evaluated on the grid | Gamma = 2.4e-6 at the obstacle centre, at most 1.7e-5 inside its 1/e^2 disc |
| `initial_field` | numpy re-derivation vs `extracted/psi_time_0.0.npy` | bit-for-bit in 90 %, residues, stopping rule met at step 1 |
| `force`, `lift`, `ramp` | `extracted/force_dt=0.02.txt` (deposited force), `ks_rust_t50/kwon_shin_force.csv` (ours), and `ks_st_dt01`, `ks_st_dt005`, `ks_rust_dt005` (convention runs, t <= 5), all under `/mnt/data/xdev-cache/qf-external/` | Table 1.1, Figure 1.3, ramp offsets and sensitivity, plateau, time-shift fit |
| `psi`, `psi_density_diff_rms_range` | `extracted/psi_time_{10..50}.npy` vs `ks_rust_t50/snap/` | relative L2 distances, gauge-fixed distances, shares near the obstacle |
| `census`, `winding_checks`, `rule`, `symmetry` | the six deposited and ten own snapshots, `extracted/vortex.txt`, the port `exploration/external/ks_vortex_count.py` (asserted equal to the opened-up copy in `ch09_common.rule_candidates`) | Table 1.2, Figure 1.4, 25 of 26 plaquettes identical, marginal vortex at t = 45, mirror pairs |
| `supersonic`, `sonic_threshold`, `axis_t20_ours` | snapshots at t = 5, 10, 15, 20 | Mach map, area 378.0 vs 379.5 xi^2, Bernoulli threshold covering 99 % |
| `birth`, `bernoulli` | `birth_t20_25.npz` | Figure 1.5, first pair at 24.2-24.3 tau, pair separations 0.5, 1.5, 2.5 xi, Madelung check (correlation 0.99999) |
| `lean_numbers` | arithmetic on the Lean statements | s = 0.671, V_c = 0.144, V0/V_c = 6.2, j where V_c = V0 is 0.017 |
| `fresh_run` | `figures/ch09_fresh_run/` | second rustbox |
| `production_run` | `ks_rust_t50/ks_rust_t50.out` | 5000 steps, 2741 s, 46 minutes |
| `provenance` | | python/numpy/scipy versions, `cvode_solver_used: false`, build of the binary |

Numbers typed by hand in `chapters/ch09.tex` (not macros), with their justification:

* model constants of the deposited run and of the code (V0 = 0.9, sigma = 20, x_obs = 100, v_f = 0.55, t_acc = 0.1, grid 1000 x 500, spacing 0.5, dt = 0.01, Gamma0 = 0.1, layers 50 and 40 xi, scale 15 xi, force interior |x| < 200, |y| < 85): all in `dataset`; the detector's constants (density below 0.2, disc of 5 xi, merge radius 3 xi, loop half-width 2 xi, steps of 0.3 pi dropped, threshold 0.9 pi) are those of the reference's `src/gpe_dynamics/vortex_GPU.py::vortex_detect` as ported in `exploration/external/ks_vortex_count.py` (the JSON section `rule` holds the threshold 0.9 pi and the results);
* analytic values: (2/sigma) V0 exp(-1/2) = 0.055; the disc within 40 xi is 4.0 % of the 500 x 250 box; sqrt(0.1) = 0.32; a = v_f/t_acc = 5.5, h = 0.01, n = 10; u_c^2 = 2/3 + v^2/3 (Josserand et al.);
* values read from the deposited `vortex.txt` and checked in this session: the detector's count rises to 20 at t = 70 and then stays between 12 and 17 up to t = 100; the two count columns of that file are equal;
* "thirteen healing lengths" (13.25), "half a healing length" (0.5), "t = 24.2" and "24.9": all from `birth`; "more than thirteen time units" = 24.25 - 10.7.

## 5. What was verified, and how

Literature and records (this session unless stated):

* arXiv:2602.03518v1 (alphaXiv full text): the fringe-region formula and its numbers (gamma0 = 0.1, w_x = 25 xi, w_y = 20 xi, d = 3 xi); v_c = 0.18 c_s0 and v_th = 0.33 c_s0 for V0/mu = 0.9, sigma/xi = 20; Re_s = 2; the averaging window 2000 to 10000 tau; the local Landau criterion as their Eq. (5); Appendix A (the perturbative threshold exceeds v_c and the neglected quantum pressure "plays a crucial role in triggering vortex shedding"); "phase accumulation and phase slip" as the dipole mechanism; the domain (-350, 150) x (-125, 125) in obstacle coordinates, equal to the deposited box shifted by x_obs = 100.
* arXiv:physics/9901055 (Josserand, Pomeau, Rica; alphaXiv): "vortices are nucleated when the flow becomes locally (at the edge of the disk) supersonic", and the critical velocity v_c^2 = (2/3) rho_0 + (1/3) v_inf^2 from the vanishing of d(rho v)/dv; the Bernoulli relation rho = rho_0 + (v_inf^2 - |grad phi|^2)/2 is their Eq. (5).
* arXiv:2206.06039 (Godfrin and Krotscheck, alphaXiv, pages 3 and 4): the exact fragment quoted in the godfrinbox, "The linearity of the dispersion relation at low wave vectors is essential for this to happen", and the Bose-gas remark (paraphrased, not quoted); IN5 appears in the review's Figure 3.
* Zenodo record 20068724 (WebFetch of zenodo.org/records/20068724): creators Junhwan Kwon and Yong-il Shin, version v1.0.0, 7 May 2026, licence "Creative Commons Attribution 4.0 International". The archive's `CITATION.cff` gives the same two names; its README says "Code is released under the MIT License. Processed data are intended to be reusable with attribution under CC BY 4.0" (the chapter's wording follows the README).
* Phys. Rev. Research 8(2), 023246 (2026), doi 10.1103/wlft-tc8w: volume, issue, article number and date (5 June 2026) read on journals.aps.org through WebFetch. The numbers quoted from the paper are those of arXiv v1; the version of record was not read (the chapter says so).
* Web search (this session): Josserand-Pomeau-Rica, Physica D 134, 111 (1999); Winiecki et al., J. Phys. B 33, 4069 (2000); Reeves et al., PRL 114, 155302 (2015); Kwak, Jung, Shin, PRA 107, 023310 (2023); Raman et al., PRL 83, 2502 (1999); Kwon, Seo, Shin, PRA 92, 033613 (2015); Kwon, Kim, Seo, Shin, PRL 117, 245301 (2016); Frisch, Pomeau, Rica, PRL 69, 1644 (1992), title "Transition to dissipation in a model of superflow".
* `docs/designs/PGPE_EXTERNAL_REPRODUCTION.md` (the sentence "this is the signature of a perturbation amplified by the unstable wake"), `paper/qf_pgpe_software.tex` line 187 ("The force separates from the reference once the wake exists") and `LEDGER.md` CLAIM-103 and CLAIM-106 were read to quote or paraphrase them correctly.

Lean: see section 8. The editor's own checker (`facts/make_appA.py` functions `parse_decls`, `scan_chapters`, called read-only with its alias logic for `book/lean`) reports for `ch09.tex` (re-run after the last edit): 0 problems, 13 verbatim leanbox copies all "identical" (2 HeliumKinematics, 8 Ch09_FlowPast, 3 VortexWinding), and 20 declarations cited (the 13, plus `bernoulli_eq_iff`, `tof_eq12_eq_eq13`, `plateau_excess_calibration_invariant`, `cut_free_of_ne_pi`, `balanced_sum_eq_zero`, `kinetic_density_split` and chapter 5's `landau_velocity_eq`).

Solver: the t <= 1 run in the second rustbox was made for this chapter (`kwon_shin --t-end 1.0 --dt 0.01 --ramp step-end`, 100 steps, 67 s of CPU, 1169 s of the program's own wall-clock time and 24 min 35 s including the wait for the shared lock, load average 12.7 to 24.9 so that the job got 4 % of a core). The t = 50 run (5000 steps, 2741 s) is the programme's run of 2026-10-09; the chapter re-derives every number from its files and its first rows are identical to the fresh run's at the printed precision. Our t = 20 to 25 numpy continuation matches the Rust t = 25 snapshot to 1.2e-15.

Physics checked numerically: the Madelung identity -d theta/dt = R (correlation 0.99999, largest difference 4.2e-3 against rms 0.12); the Bernoulli threshold covers 99 % of the measured supersonic region at t = 20 (84, 88, 95 % at t = 5, 10, 15); the plaquette charges are integers to 3e-16 and sum to zero on all 16 snapshots; the largest principal step is 0.9993 pi (never exactly pi).

## 6. What could NOT be verified, and limits that the text states

* Whether the paper's description of its fringe region (25, 20, 3 xi) and the code's (layers 50 and 40 xi, scale 15 xi) are equivalent in some convention: not examined; the text says so and follows the code.
* The cause of the force plateau (ours is weaker than the deposited drag by 0.19 % of the maximum from t about 26 on): NOT identified. The candidates (single precision, splitting, the damping step treating Gamma <= 0.01 as unitary) are untested; a numpy port of the reference's own stepper in double and single precision would separate them.
* The unit difference of the detector's count at t = 45 (7 against 6): no deposited field exists at that time; "marginal vortex at 0.951 pi" is a plausible explanation, not a demonstration.
* The programme's registered tolerance 1e-5 for the force at t <= 10 is NOT met (4e-5).
* Nothing was run beyond t = 50; no GPU; the paper's Strouhal number, drag coefficient, Reynolds number and D_eff were not computed.
* The machine load during the production run was not recorded (stated in the text).
* That the released rusty-SUNDIALS v11.6.0 (PR #71, 6545abf per CLAIM-106) has the same tree as the worktree from which the binary was built (`/home/xavkal/xdev/rusty-SUNDIALS-c3`, commit 5db8041 on `feat/qf-pgpe-reproduction`, binary of 2026-10-09 21:23:35, after the last edit of `flow.rs` at 21:22:29): not re-checked. The chapter says "release v11.6.0" as the ledger does.
* Not read: the published version of the Kwon-Shin paper (only arXiv v1), and the Zenodo files other than those named above.

## 7. For the editor to check

1. `refs.bib`, key `KwonShin2026`: author "W. J. Kwon and Y. Shin" is wrong for this paper (Junhwan Kwon; the archive's `CITATION.cff` and the Zenodo record say Junhwan Kwon and Yong-il Shin; "W. J." is Woo Jin Kwon of the earlier experimental papers). The key is cited by `chapters/ch10.tex` (two places). My entries `KwonShin2026prr` (article, with volume, issue and article number) and `KwonShin2026data` (the Zenodo record, with the record's own title) are correct and could replace it.
2. The new module is `book/lean/Ch09_FlowPast.lean`, namespace `QuantumFluids.FlowPast`. I cite it as `\Lthm{FlowPast}{name}` (the editor's alias logic maps `FlowPast` to `Ch09_FlowPast`; `lean_ns.tex`, regenerated at 01:28, maps `FlowPast`, `Ch09_FlowPast` and `Ch09FlowPast` to `QuantumFluids.FlowPast`, so `\Lthm` prints `QuantumFluids.FlowPast.<name>`, which is also what its fallback printed in my builds). The three leanboxes of the new module are titled "Lean 4 FlowPast (new for this book)" through the `title` option (as in chapter 5), with the module argument `Ch09\_FlowPast (new)`, which the checker resolves.
3. Overlap with chapter 5: `Ch05_BogoliubovDispersion` proves `landau_velocity_eq` (infimum of the Bogoliubov phase velocity is exactly c, general c and m); my `landau_uniform_gp` is the case c = m = 1. The chapter says so and cites `\Lthm{BogoliubovDispersion}{landau_velocity_eq}` in a parenthesis at the end of the paragraph (placed mid-sentence, the unbreakable `QuantumFluids.BogoliubovDispersion.` prefix produced an 85 pt overfull box). Both modules define a `bogEps`, in different namespaces; no clash.
4. FACTS section 2(b) lists "Landau velocity" among the identities that `HeliumKinematics` takes from the 2021 PRB paper; the module's own header attributes the two Landau lemmas to [GK22] (the review, "the paragraph on the Landau criterion"). The chapter follows the module and the review's text (verified). The two Landau lemmas are described as inequalities between numbers, not as statements about a measured curve.
5. The chapter CORRECTS an earlier reading of the programme, in section 7 (bullet "It starts more than thirteen time units before any vortex exists"): the force difference changes sign at t about 10.7, has reached 82 % of its plateau when the first pair is born (t about 24.25), and is smooth and non-oscillating; so the readings "perturbation amplified by the unstable wake" (design note) and "the force separates from the reference once the wake exists" (software paper v2, published as 10.5281/zenodo.23269715) and "0.19 % of max after the wake forms" (LEDGER CLAIM-106) are not supported by the data. I did not touch those files (outside `book/`); correcting them (an erratum or a v3) is the owner's decision.
6. Numbering: standalone, the chapter is "Chapter 1"; all internal references use `\cref`. External references: `\cref{ch03}` (the GP equation), `\cref{ch05}` (the Bogoliubov dispersion and the cross-reference above), `\cref{ch05,ch08}` (Godfrin's neutron-scattering measurements on helium).
7. Leftovers I could not delete (no `rm`): `chapter_wrapper_ch09.*` build files in `book/`, `figures/ch09_*.png` previews. `figures/ch09_numbers.py` and the figure scripts read raw data under `/mnt/data/xdev-cache/qf-external/` (not in git); `ch09_numbers.json` is the durable record.
8. For Appendix A: the new module's axiom footprint is {propext, Classical.choice, Quot.sound} for all eight theorems; the chapter text states it together with the toolchain (Lean 4.34.0-rc2 and the matching Mathlib). The editor's own environment-level audit of the module (`facts/audit/book_Ch09_FlowPast.json`, generated 2026-10-10 01:29, found after my compile) agrees: exit 0, 0 errors, 0 warnings, 8 named theorems and 1 definition, `sorryAx` false, 0 user axioms, union of axioms {propext, Classical.choice, Quot.sound}.

## 8. New Lean (`lean/Ch09_FlowPast.lean`, 145 lines)

* Declarations: `def bogEps`, and theorems `bogEps_ge_sound`, `landau_uniform_gp`, `supersonic_iff`, `sonic_speed_threshold`, `bernoulli_min`, `bernoulli_eq_iff`, `barrier_height_bound`, `ramp_overshoot`. No `sorry`, no user axiom.
* Compile: `cd /home/xavkal/xdev/OpenAINavierStokesEuler/NavierStokesAndEuler && nice lake env lean /home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/book/lean/Ch09_FlowPast.lean`; Lean 4.34.0-rc2 with the OpenAI tree's Mathlib; exit 0, no error and no warning; 57 s wall, 29 s user, load about 13. It ran WITHOUT the `flock` queue because the queued copy of the same job had waited 52 minutes behind sibling authors and the run is under the one-minute threshold; the queued copy was cancelled. Log: `lean/Ch09_FlowPast.compile.log`. The file has not changed since that compile.
* Axioms of all eight theorems (`#print axioms`): `propext`, `Classical.choice`, `Quot.sound`. The definition `bogEps` depends on none.
* Scope (as the file header says): elementary statements about numbers and finite sums. The Bernoulli relation is a hypothesis of `barrier_height_bound`; nothing is derived from the Gross-Pitaevskii dynamics and nothing is about vortices.

## 9. Notices

* CVODE notice: not applicable. No chapter-9 script imports `rusty_sundials` or `qf_pgpe` or calls `CvodeSolver` (recorded as `cvode_solver_used: false` in the JSON); the only solver is the Rust example program `kwon_shin` of `qf-pgpe::flow`.
* No commit, push, deposit, external message, `lake update`, `rm`, `mv` or `setsid`. The first Lean compile of the module (41 minutes of queue) and the fresh `kwon_shin` run (t <= 1) went through `flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice`; the last Lean re-check (57 s) was run directly, as section 8 says. The 5000-step production run and the three convention runs (`ks_rust_dt005`, `ks_st_dt01`, `ks_st_dt005`) are the programme's runs of 2026-10-09 and were only read; the numpy continuation `birth_t20_25.npz` (made at 22:26 on 2026-10-09 by `ch09_birth_run.py`) is this chapter's own.
