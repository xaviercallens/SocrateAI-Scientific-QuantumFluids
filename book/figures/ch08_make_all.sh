#!/bin/bash
# Chapter 8: regenerate every number, figure and macro of chapters/ch08.tex, in dependency order.
# Documented, not meant to be run unattended: the Lean step and the batches queue behind the shared heavy-job lock
# (/mnt/data/xdev-cache/tmp/qf_heavy.lock), and on the shared machine (load 12-35) the whole chain took about an hour of wall time.
# Large/regenerable data live under /mnt/data/xdev-cache/book_ch08/ ; Rust targets under /mnt/data/xdev-cache/cargo-target-book8.
set -e
BOOK=/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/book
PY=/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/.venv/bin/python
export CARGO_TARGET_DIR=/mnt/data/xdev-cache/cargo-target-book8

# 1. the two Rust drivers (path dependencies on rusty-SUNDIALS commit 5db8041fd2e3840defcff2b4a8c26c1cbb2467fd, crates cvode 6.4.0 and qf-vlasov1d)
( cd $BOOK/rust/ch08_kinetic && nice cargo build --release --offline )
( cd $BOOK/rust/ch08_vlasov  && nice cargo build --release --offline )

# 2. raw runs (data to /mnt/data/xdev-cache/book_ch08/{kinetic,vlasov})
mkdir -p /mnt/data/xdev-cache/book_ch08/vlasov
nice $PY $BOOK/figures/ch08_kinetic_run.py                         # CVODE (BDF/Adams) on the Landau kinetic equation: 20 jobs, stats.json
nice $CARGO_TARGET_DIR/release/ch08_vlasov /mnt/data/xdev-cache/book_ch08/vlasov   # qf-vlasov1d: scans, series, snapshots

# 3. figures and numbers (each script merges its own key into figures/ch08_numbers.json)
nice $PY $BOOK/figures/ch08_zerosound.py       # fig 1 + Davidenko continuation by CVODE ('cont' subcommand) + sum rule
nice $PY $BOOK/figures/ch08_window.py          # fig 5
nice $PY $BOOK/figures/ch08_timedomain.py      # fig 2
nice $PY $BOOK/figures/ch08_fermisurface.py    # fig 3
nice $PY $BOOK/figures/ch08_vlasov.py          # fig 4 (about 1-6 min: mpmath roots, fits)
nice $PY $BOOK/figures/ch08_solver_sweep.py    # Adams/BDF output-spacing sweep (N = 4), analytic and differenced Jacobian
nice $PY $BOOK/figures/ch08_wheel_check.py     # the stale venv module of rusty_sundials ...
PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext nice $PY $BOOK/figures/ch08_wheel_check.py   # ... and the editor's build of 5db8041

# 4. Lean: compile the new module (one Lean process at a time; about 40 s of CPU) and copy the log to figures/ch08_lean_compile.log
#    cd /home/xavkal/xdev/OpenAINavierStokesEuler/NavierStokesAndEuler && flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice lake env lean $BOOK/lean/Ch08_ZeroSound2D.lean
#    then edit figures/ch08_lean.json (axioms_text, cpu seconds) by hand from that log.

# 5. the number macros quoted by the chapter, then the chapter itself
( cd $BOOK/figures && $PY ch08_numbers_tex.py )
cd $BOOK
lualatex -interaction=nonstopmode -jobname=ch08_buildN chapter_wrapper_ch08.tex && bibtex ch08_buildN && lualatex -interaction=nonstopmode -jobname=ch08_buildN chapter_wrapper_ch08.tex && lualatex -interaction=nonstopmode -jobname=ch08_buildN chapter_wrapper_ch08.tex
