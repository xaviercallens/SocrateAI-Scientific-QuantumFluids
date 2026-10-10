#!/bin/bash
# Build the Python module `rusty_sundials` (crate rusty-sundials-py) from the rusty-SUNDIALS checkout into a scratch directory.
# Nothing is written to the checkout: the cargo target directory is OUTDIR/target.  Used for Chapter 2 of the book.
#
# Why: the module installed in the programme's virtual environment (built 2026-09-26) has the pre-fix Adams method (implicit Euler,
# see rusty-SUNDIALS docs/CVODE_ADAMS_FIX.md); figures/ch02_compute.py refuses to run with it.
#
#   usage:  flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice book/rust/ch02_build_py.sh OUTDIR     (about 3 minutes on the shared machine)
#   then:   PYTHONPATH=OUTDIR/py:/mnt/data/xdev-cache/qf_ext  .venv/bin/python book/figures/ch02_compute.py
# The build of commit 5db8041 made for the book is kept, with its sha256, at /mnt/data/xdev-cache/rs_py_5db8041 (copy made by the editor).
set -e
SRC=${RS_ROOT:-/home/xavkal/xdev/rusty-SUNDIALS-c3}
OUT=${1:?usage: ch02_build_py.sh OUTDIR}
PY=${PYO3_PYTHON:-/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/.venv/bin/python}
mkdir -p "$OUT/target" "$OUT/py"
git -C "$SRC" rev-parse HEAD > "$OUT/commit.txt"
cd "$SRC"
CARGO_TARGET_DIR="$OUT/target" PYO3_PYTHON="$PY" cargo build --release --locked --offline -p rusty-sundials-py
cp "$OUT/target/release/librusty_sundials.so" "$OUT/py/rusty_sundials.so"
echo "built commit $(cat "$OUT/commit.txt"); module: $OUT/py/rusty_sundials.so"
