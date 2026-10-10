# Exciton fluids: Lean 4 × rusty-SUNDIALS × a September 2026 optimality theorem

Technical note: `paper/exciton_fluid_phase1.tex` (Zenodo, concept DOI 10.5281/zenodo.23289026). Plan and handoff:
`docs/designs/EXCITON_FLUID_LEAN_SOLVER_PLAN.md`, `EXCITON_FLUID_LEAN_HANDOFF.md`. Pre-registrations and results:
`docs/designs/EXCITON_FLUID_PHASE{1,2}_{PREREG,RESULTS}.md`. Lean alignment: `docs/designs/LEAN_TOOLCHAIN_ALIGNMENT_v4_34_1.md`.

| directory | content |
|---|---|
| `lean/` | `ExcitonX1`, `FourFlavour`, `MeanField`, `GradientFlow`, `TorusBound` (conditional on the upstream theorem), a negative control that fails by design, README, and the verification reports of two separate model instances with the producer's response |
| `python/` | independent references (`phase1_reference.py`, `phase2_reference.py`, written and run **before** the Rust code), the numpy cross-check (`phase1_crosscheck.py`), the gate evaluators (`phase1_summarise.py`, `phase2_summarise.py`) and the generator of every number of the note (`phase1_paper_numbers.py`) |
| `rust/qf-exciton-p1/` | the instruments on rusty-SUNDIALS CVODE (path dependencies on a clean clone of tag v11.6.0, commit `5db8041`): `s0`, `ka`, `ex1`, `ff`, `polish` (exploratory), `mf` (Phase 2) |
| `results/phase1/`, `results/phase2/` | reference numbers, reports of every gate, `summary.json`, the run records (`phase1/runs/`: one JSON line per run) and the exploratory longer flows |

## Reproduce

```
# instruments (the Cargo.toml path dependencies point to ~/xdev/rusty-SUNDIALS-c3 at 5db8041; adjust)
cd exploration/exciton/rust/qf-exciton-p1 && CARGO_TARGET_DIR=<scratch> cargo build --release
# Phase 1: s0, ka, ex1 <runs_dir> [case prefixes...] (QF_AMEND=A2 for K2-K4, QF_THREADS, QF_NSTART), ff, polish <runs_dir> <case>
# gates and numbers
python3 exploration/exciton/python/phase1_summarise.py exploration/exciton/results/phase1/runs exploration/exciton/results/phase1/summary.json
python3 exploration/exciton/python/phase2_summarise.py exploration/exciton/results/phase2/mf_report.json \
        exploration/exciton/results/phase2/reference.json exploration/exciton/results/phase2/summary.json
python3 exploration/exciton/python/phase1_paper_numbers.py        # paper/exciton_numbers.tex, exciton_cases_table.tex
# Lean (Lean 4.34.1 / Mathlib v4.34.1), one file at a time
lake env lean exploration/exciton/lean/TorusBound.lean
```

## Known defects of the records

* `min_dist` in the run records of `ex1` is a placeholder (0); only `min_dist_start` is a measurement.
* K5 and K6 were not run; K2–K4 were run under amendment A2 (60 starts, lower cutoffs).
* Phase 2's control (P2-c(ii)) failed as registered; the reason (an unbounded functional) is recorded in
  `docs/designs/EXCITON_FLUID_PHASE2_RESULTS.md`.
