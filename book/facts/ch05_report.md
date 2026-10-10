# Chapter 5 report — "Phonons, Rotons and the Dispersion Relation"

(author's report to the editor; written 2026-10-10; final: the Lean recompile and the CVODE job both finished and are folded in)

## 1. Files

| file | what |
|---|---|
| `chapters/ch05.tex` | the chapter (≈ 8 800 words of source incl. boxes/captions; 23 pages in the standalone wrapper, of which Figs 1.2 and 1.5 each sit alone on a `[tp]` float page, plus the bibliography) |
| `figures/ch05_numbers.json`, `ch05_numbers.tex` | every number quoted in the text (macro `\cfiveV{key}`; an undefined key prints `??key??` and a package warning) |
| `figures/ch05_curve.py/.pdf/.png` | Fig. 1: ⁴He dispersion (published table), Landau line, phase velocity, phonon window |
| `figures/ch05_thresholds.py/.pdf/.png` | Fig. 2: the three three-phonon thresholds, series versus table |
| `figures/ch05_solver_fig.py` → `ch05_solver.pdf`, `ch05_universal.pdf` | Figs. 3 and 4 (solver validation; spectral map and universal collapse) |
| `figures/ch05_rings.py/.pdf/.png`, `ch05_rings_data.npz` | Fig. 5: dispersive ring wave and group velocity |
| `figures/ch05_dispersion_run.py`, `ch05_common.py`, `ch05_results.npz`, `ch05_run_log.json` | the Rust-engine runs R1–R4 and the fit (big series in `/mnt/data/xdev-cache/book_ch05/`) |
| `figures/ch05_cvode.py`, `ch05_cvode_new.json`, `ch05_cvode_old.json`, `ch05_cvode_table.tex` | the CVODE referee (results in §4; `ch05_cvode_quick.json` is a smoke test, unused) |
| `figures/ch05_helium.py` | the published table, all table-derived numbers, the pressure series |
| `figures/ch05_numbers.py` | assembles the JSON and the `.tex` macro/table files |
| `figures/ch05_pressure_table.tex`, `ch05_cvode_table.tex` | generated tables |
| `lean/Ch05_BogoliubovDispersion.lean` (+ `.compile.log`) | NEW Lean module, namespace `QuantumFluids.BogoliubovDispersion` |
| `refs_ch05.bib` | 13 new entries (see §5) |
| `figures/ch05_measure.py` | inherited from the interrupted session; **superseded and unused** (docstring says so). The `*_quick.*` files are smoke-test outputs, not used. |

## 2. Compile

`cd book; lualatex -interaction=nonstopmode -jobname=ch05_build chapter_wrapper_ch05.tex` (twice, `bibtex ch05_build` between; wrapper `chapter_wrapper_ch05.tex` is git-ignored): zero errors, zero overfull boxes, no missing glyphs, no undefined number key (`??key??`), no undefined citation. The only warnings are the cross-chapter `\cref{ch02,ch03,ch04,ch06,ch08,ch09}` (the labels exist in those chapters; they resolve at integration) and five harmless underfull boxes (long `\Lthm` names). The pages of the standalone PDF (28, two of them blank pages produced by the wrapper's contents/bibliography) were inspected as images, including every figure, table and Lean/Python/Rust box; the last two wording edits (Section 1.5.6) were checked in the extracted text only.

## 3. Lean

* New module `book/lean/Ch05_BogoliubovDispersion.lean` (340 lines; 24 theorems, 3 definitions): **final compile on this machine, Lean 4.34.0-rc2 / Mathlib of the OpenAI tree via `lake env lean` (under the heavy-job lock): exit 0, no errors, no warnings, no `sorry`; 15 `#print axioms` lines, every one `[propext, Classical.choice, Quot.sound]`** (log: `lean/Ch05_BogoliubovDispersion.compile.log`; the 3918 s in its last line are almost all lock waiting).
  History: the version inherited from the interrupted session had 3 errors (two failing proofs; `sorryAx` in `alpha2_limit`, `landau_velocity_eq`, `landau_velocity_sInf`); fixed here (proof of `alpha2_limit`'s lower bound rewritten; `sound_lt_phase_velocity` rewritten with a `calc`), `push_neg` replaced by `push Not` (deprecation), four theorems added (`abs_bogEps_sub_phononDisp_le`, `phase_velocity_universal`, `bogEps_sq_gp`, `bogEps_sub_sound_strictMonoOn`), and `sound_line_le` restated without its unused hypotheses.
* **New axioms: none.**
* Library statements shown (verbatim from `lean_src/HeliumKinematics.lean`): `phononDisp`, `three_phonon_open_iff`, `seriesDisp`, `symmetric_split_excess`. Cited by `\Lthm`: `tof_eq12_eq_eq13`, `tofEnergy_rescale`, `landau_velocity_parabolic_zero`, `landau_velocity_ge_of_above_sound_line`, `three_phonon_excess`, `phase_velocity_excess`, `group_velocity_excess`, `two_roton_momentum_le`, `two_roton_parallel`, `two_roton_antiparallel` (all exist; HeliumKinematics audit: exit 0, standard axioms).
* **For the editor's automatic check**: my new module is not in `lean_src`; it is cited as `\Lthm{BogoliubovDispersion}{name}` and its leanboxes are titled `{BogoliubovDispersion (new)}`. `facts/appA_citation_check.md` (regenerated at 00:56) resolves all my `\Lthm` citations and finds my five leanbox statements of the new module and the four of `HeliumKinematics` *identical* to the sources. File name `Ch05_BogoliubovDispersion`, namespace `QuantumFluids.BogoliubovDispersion` (FACTS §5). The editor's appendix generator describes the module as 24 theorems, 3 definitions (private lemmas excluded) and 15 `#print axioms` lines, which matches the file.

## 4. Solver

Engine: `qf_pgpe` (Rust), `PYTHONPATH=/mnt/data/xdev-cache/qf_ext`. Runs (all hbar = m = n0 = 1): R1 N=128, L=64, g=1, dt=0.02, T=300, 3208 modes fitted at once from a random pulse of size 1e-6 (65 s run + 12 s fit under load 10–36); R2 g=2 (N=64, 796 modes); R3 dt ladder 0.04…0.005 (same pulse); R4 single-mode amplitude test; rings (N=128, t=9). The whole heavy script ran 176 s once it got the lock (the queue wait was ~30 min).
**CVODE** (`figures/ch05_cvode.py`, run under the lock on 2026-10-10 01:02, 3 minutes once the lock was free; `ch05_cvode_new.json`, `ch05_cvode_old.json`; log of the run in the scratchpad `cvode_run2.log`). Two builds of the Python module `rusty_sundials`:
  * *current build*: rusty-SUNDIALS commit 5db8041, sha256 `0bdb1b4a504fb4817738c483f797e6a109b99121b666f1e51ad8e05c2fb996d7`. The run imported `.../scratchpad/rs_py/rusty_sundials.so` (recorded in the JSON as `rusty_sundials_file`), a **byte-identical copy** (same sha256, verified) of the editor's `/mnt/data/xdev-cache/rs_py_5db8041/rusty_sundials.so`; I used my own copy because the editor's directory appeared (00:16) after my job had been queued, and re-queuing would have cost the queue place. The script's docstring and §8 give the editor's path.
  * *older build*: the module of the project venv, `.venv/lib/python3.12/site-packages/rusty_sundials/` (`rusty_sundials_py-6.0.0`), shared library `rusty_sundials.cpython-312-x86_64-linux-gnu.so` dated 2026-09-26 15:00:05, sha256 `9fbd09e985c2faf0ae858d8229e2b38eb7ef5b6c7bb2324f948c16f7c7cc81a5` (recorded in `ch05_numbers.json`; the JSON's `rusty_sundials_file` is the package `__init__.py` of that directory); the Adams-order fix of the library history (`fix(cvode): implement LLNL cvSetAdams so Adams reaches orders 2-12`, #63) was merged on 2026-09-28, i.e. the venv module predates it. Used on purpose, only for the old/new comparison.
  * *Results, current build*, box N=16, L=16 (49 modes, 98 unknowns; the software paper's reference box), T=20, η=1e-4, atol=1e-3·rtol: rtol 1e-4/1e-6/1e-8/1e-10 → 6229/6948/8313/10158 right-hand-side evaluations, 4.9/5.4/7.0/7.6 s, max |Δω|/ω_Bog against the fine (Δt/4) engine run 7.8e-4/2.7e-5/2.7e-7/3.3e-9, max record difference 7.7e-2/1.6e-3/1.8e-5/8.0e-7. The engine at Δt=0.01 differs from its own Δt/4 run by 5.3e-7 (0.26 s); with the fourth-order law the Δt/4 run itself is wrong by ≈ 2.1e-9, which is why 3.3e-9 is the floor of the comparison (the chapter says this). The fitted frequencies of this short record (1.3–6.4 periods per mode) differ from Bogoliubov's formula by up to 3.3e-4 in *both* records (checked: the maximum is at k = 0.555, 1.8 periods), so the difference between the records is unaffected.
  * *Small box* N=8, T=4 (13 modes, 26 unknowns): current 599/718/992 evaluations, errors 3.8e-4/1.7e-5/3.5e-7; older 1361/9730/91519 evaluations (0.7/8.3/85.7 s), errors 1.9e-2/1.7e-3/1.7e-4 (ratios of cost 2/14/92; cost grows ×7 and ×9 and error falls ×11 and ×10 per hundredfold tightening: the first-order signature).
  * *Scaling* (rtol 1e-6, T=2): 26 unknowns 365 evaluations 0.19 s; 98 unknowns 710, 0.51 s; 394 unknowns 2291, 9.4 s. The main run (6 418 unknowns, T=300) was not attempted through this interface.
  * Timings are wall times on the shared, loaded machine; indicative only.

## 5. Verification of external facts (how)

* **Godfrin et al. 2021 (arXiv v1 source, `data/external/godfrin_papers/.../2020-Dispersion-paper-v6d.tex`)** was read for: the time-of-flight formulas (Eq. 12/13), the calibration at Δ_R = 0.7418(10) meV (Stirling) and the sentence that energies should be corrected proportionally, the composition of the published table (ultrasound < 0.15, combined 0.15–0.3, neutron > 0.3 Å⁻¹; caption of its Table I), the SVP series set (c = 238.3, α₂ = 1.55, α₃ = −4.04, α₄ = 2.30; valid k < 0.5), α₂ = 1.55(1) Å² (Rugar–Foster, α₁ = 0), the anomalous → normal change near 20 bar (20.4 bar in the DMBT-corrected analysis), the energy resolution 0.07 meV FWHM at E_i = 3.52 meV and the Gaussian resolution function, the 384 × 241 detector pixels, "more than 70" values per bin, the relative systematic energy uncertainty 2.1e-3, the roton/maxon parameters (Δ_R = 0.7418, k_R = 1.918, μ_R = 0.141; Δ_M = 1.191, k_M = 1.103, μ_M = −0.545), the sound-velocity table (ultrasound column used for c(P)), and the phrase "clearly very far from the experimental result" (about the Bijl–Feynman spectrum; quoted verbatim). **All of this is the arXiv v1 text; none of it was compared with the PRB version of record.** The chapter says so once. Numbers computed from the table by my scripts reproduce the paper's fitted values (maxon 1.1907 meV, roton 0.7419 meV at 1.917 Å⁻¹, μ_R 0.141, μ_M −0.548).
* **Godfrin–Krotscheck review (arXiv:2206.06039, source read)**: roton name "historical", incipient localisation; Feynman–Cohen suggested neutrons; Palevsky et al. 1957 first evidence; Landau-criterion paragraph; "ghost phonon"/plateau paragraph (paraphrased, not quoted).
* **Table licence**: `DispersionP0allRange.txt.meta` says "arXiv non-exclusive distribution licence"; `godfrin_papers/MANIFEST.md` says CC BY 4.0 for the ancillary files. The editor should confirm on the arXiv abstract page before the figures are deposited. EDITOR 2026-10-10: confirmed — the arXiv abstract page of 2012.09067 carries the CC BY 4.0 licence (link "Rights to this article" → creativecommons.org/licenses/by/4.0/); the ancillary files are part of that submission. Figures and numbers derived from the table are used with attribution; the table itself is not redistributed in the book's source archive.
* **New citations (all in `refs_ch05.bib`)**, checked on 2026-10-10 with Crossref (WebFetch of `api.crossref.org/works/<doi>`): Feynman 1954 (Phys. Rev. 94, 262–277), Feynman & Cohen 1956 (102, 1189–1204), Rugar & Foster 1984 (PRB 30, 2595–2602, title "Accurate measurement of low-energy phonon dispersion in liquid ⁴He"), Cowley & Woods 1971 (Can. J. Phys. 49, 177–200), Glyde 2017 (Rep. Prog. Phys. 81, 014501), Dalfovo et al. 1999 (RMP 71, 463–512), Maris 1977 (RMP 49, 341–359), Santos–Shlyapnikov–Lewenstein 2003 (PRL 90, 250403), Palevsky et al. 1957 (Phys. Rev. 108, 1346–1347, "Excitation of rotons in helium II by cold neutrons"). By web search: Landau 1947 (J. Phys. USSR 11, 91, title "On the theory of superfluidity of helium II"; volume/first page as in the reference lists of Godfrin et al. and Godfrin–Krotscheck; I give only the first page), Chomaz et al. 2018 (Nature Phys. 14, 442–446, doi 10.1038/s41567-018-0054-7), Glyde 1994 book (from the reference list of Godfrin et al.). `Callens2026prereg` is a programme document (docs/designs/PGPE_BKT_PREREG.md). Keys reused from `refs.bib`: Godfrin2021, GodfrinKrotscheck2022, Landau1941, Bogoliubov1947, PitaevskiiStringari2016, Callens2026sw.
* **Programme documents used**: PGPE_BKT_PREREG.md amendment A1 (K5 failed by factors 5, 2.5, 1.2; cause: condensate phase), RETRACTIONS.md R2 and LEDGER CLAIM-024 (dual length; ×21 at the roton at SVP), the software paper `paper/qf_pgpe_software.tex` (lines 99–101: the CVODE reference at N=16, L=16, 49 modes, t=1 "depends on a fix of the library (the Adams order was stuck at one)"; without it the solver "collapses its step" and fails after about 10^6 evaluations — the chapter quotes only the seven-word phrase and paraphrases the rest; crate agreement 1e-10 over 20 time units), `exploration/godfrin/three_phonon_threshold.py/.json` (cross-check of my thresholds: 0.404/0.455/0.566 series, 0.453 table — identical).

## 6. What I could not verify / deliberately left out

* The sentence that the first neutron evidence for the roton came in 1957 and that Feynman and Cohen suggested neutrons rests on the Godfrin–Krotscheck review (attributed to it in the text); the Palevsky title/pages were checked, the priority claim was not independently checked.
* The two "textbook" statements (Landau's derivation of the critical velocity; Feynman's relation as an upper bound; BdG spectrum with a non-local interaction) are standard physics, not tied to a file.
* The explanation offered for the failure of the two-frequency fit at long wavelength and ε = 0.1 (near-resonant harmonics) is flagged in the text as untested.
* I did **not** draw or discuss the 2Δ_R line or the plateau energy against the table (an unresolved item of `docs/FOR_GODFRIN.md`); the plateau appears only through the paper's/review's statements and the Lean two-roton lemma. The mention of `plateau_excess_calibration_invariant` was removed for the same reason.
* Exercise 3's example `nV(k) = 1 − 3k² e^{−k²}` is my own; its numbers (maxon ω ≈ 0.350 at k ≈ 0.56, roton ω ≈ 0.304 at k ≈ 0.84, min ω/k ≈ 0.349) are computed in `ch05_numbers.py`; stability (ω² > 0 for all k) is asserted there.

## 7. Things the editor must check

1. Floats are `[tp]` (not `[t]`) because Fig. 1 and Fig. 3 are taller than the default top fraction; change if the book style fixes this globally.
2. Chapter-local macros (prefix `cfive`): `\cfiveV`, `\cfivepath`, `\cfiveAng` (all `\providecommand`). `\input{figures/ch05_numbers.tex}` is inside the chapter file. The earlier `\cfiveNew` and its `\directlua` helper are gone (replaced by the editor's `\Lthm`).
3. `\cref` targets of other chapters: `ch02`, `ch03`, `ch04`, `ch06`, `ch08`, `ch09` (all used as plain chapter references).
4. Exercise numbers are literal ("Exercise 1/2/3"), not `\ref`s (a `\label` after `\paragraph` printed the section number).
5. The CVODE results of the "current build" depend on a build of the Python module that is not the one in the shared venv (see §4); the chapter says so, and says that the venv module was run on purpose for the old/new comparison. If the venv module is rebuilt from a tree with the fix, the "older build" table and the sentences that use it (Section 1.5.6) must be regenerated or dropped.
6. Numbers in the text come from `ch05_numbers.json`/`.tex`; the CVODE sentences contain a few qualitative statements about those numbers ("the last two rows are below ...", "of the order of the last difference"): they were checked against the real results above and must be rechecked if the job is rerun.
7. Bibliography: `refs_ch05.bib` has 13 entries. Compared with the editor's `refs_all.bib` (60 entries, file dated 2026-10-09 23:52): 12 of my 13 keys are already in it (identical, except `Landau1947`, `Glyde2017`, `Glyde1994`, where the `refs_all.bib` versions carry extra `note` fields and, for `Glyde1994`, another publisher string; **use the `refs_all.bib` versions**; `Glyde1994` is also in `refs_ch01.bib`, so loading both per-chapter files together gives a repeated key); **`Callens2026prereg` (the programme's pre-registration document, cited for the failure of the known answer K5) is not in `refs_all.bib` and must be added**, otherwise the citation prints `[?]`.

## 8. How to rebuild everything (from `book/figures`; `PY=../../.venv/bin/python`)

```
# table-derived figures and numbers (seconds)
$PY ch05_curve.py; $PY ch05_thresholds.py
# solver: heavy, take the lock; ~3 minutes once the lock is free (R1-R4)
flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice env PYTHONPATH=/mnt/data/xdev-cache/qf_ext OMP_NUM_THREADS=1 $PY ch05_dispersion_run.py
$PY ch05_solver_fig.py            # Figs 3-4 (uses ch05_results.npz; the spectral map is cached in ch05_map.npz, rebuilt from /mnt/data/xdev-cache/book_ch05/series_R1.npz if present)
PYTHONPATH=/mnt/data/xdev-cache/qf_ext $PY ch05_rings.py      # Fig 5 (first run writes ch05_rings_data.npz, ~10 s)
# CVODE referee: heavy; the 'new' run needs the fixed Python module FIRST on the path
flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice env PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext OMP_NUM_THREADS=1 $PY ch05_cvode.py --tag new
flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice env PYTHONPATH=/mnt/data/xdev-cache/qf_ext OMP_NUM_THREADS=1 $PY ch05_cvode.py --tag old      # the stale venv module, on purpose
$PY ch05_numbers.py               # ch05_numbers.json, ch05_numbers.tex, ch05_pressure_table.tex, ch05_cvode_table.tex
cd .. && lualatex -interaction=nonstopmode -jobname=ch05_build chapter_wrapper_ch05.tex; bibtex ch05_build; lualatex ... ; lualatex ...
# Lean (new module)
cd /home/xavkal/xdev/OpenAINavierStokesEuler/NavierStokesAndEuler && nice lake env lean /home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/book/lean/Ch05_BogoliubovDispersion.lean
```

## 9. Consistency with Chapter 1 (editor's request of 2026-10-10)

The roton/maxon numbers quoted in the text and drawn in Fig. 1 are the table's own extrema, the same as in `figures/ch01_numbers.json`: roton 0.7413 meV (8.60 K) at 1.920 Å⁻¹, maxon 1.1914 meV at 1.114 Å⁻¹, Landau velocity 57.89 m/s at 1.966 Å⁻¹ (ratio 0.243 to c = 238.3 m/s; Chapter 1's 0.2425 uses c = 238.70 m/s fitted to the table's first rows). The only quantity that differs is the height of the phase-velocity maximum: 5.4 per cent here (normalised by the ultrasonic c = 238.3 m/s quoted in the paper) against 5.25 per cent in Chapter 1 (normalised by 238.70 m/s); the chapter says so in Section 2 (5.3 per cent when normalised by the 238.5 m/s the table itself gives at 0.01 Å⁻¹; the first rows are rounded to 0.1 µeV). The local polynomial fits of the paper's type (roton 0.7419 meV at 1.9174 Å⁻¹, μ_R = 0.141; maxon 1.1907 meV at 1.1055 Å⁻¹, μ_M = −0.548) are used only for the effective masses. The text says 1727 rows, 34 with an uncertainty, author-processed, not raw; it never says "about 50 points" and never lists the authors of the 2021 paper (key `Godfrin2021` from `refs.bib`).

## 10. Corrections made in the final pass (so that nothing stale survives)

* The main run has **6 418** unknowns (3 209 retained modes × 2), not 1 594 (that was the N=64 smoke-test box); now a macro (`unkMain`). Also macro-ised: `3208` time series, the 26-/98-unknown boxes, 2.1e-3, 1.054, 3.19.
* The chapter first said that the software paper "reports that the first Hamiltonian system run through CVODE's Adams method ... exposed a defect". The paper does not say "first Hamiltonian system"; the text now follows the paper's own wording (the same N=16 comparison "depends on a fix of the library (the Adams order was stuck at one)").
* "the comparison of the Feynman curve with the measured one is in the paper itself" was weakened to what the paper says: the Bijl–Feynman spectrum "is clearly very far from the experimental result" (verbatim, line 988 of the arXiv v1 source).
* CVODE paragraphs rewritten after the real results: the sentence "until the difference reaches the level of the engine's own time-step error" was wrong (the difference goes below the production-step error down to the error of the Δt/4 reference run); the scaling paragraph no longer attributes the cost to the list conversion alone (the numpy right-hand side and the growing number of evaluations dominate).
* The numbers script refuses a CVODE JSON marked `dry_run` (used once to test the table layout; those files were overwritten by the real run).
