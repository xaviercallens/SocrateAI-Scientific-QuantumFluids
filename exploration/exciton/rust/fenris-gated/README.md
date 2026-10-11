# fenris-gated

Edge/frustration design target for protocol item L6 of `paper/exciton_fluid_gated.tex`. The design, the gates and the dated
amendments are in `PREREG.md`; data are in `results/` (`table_all.csv`, `case_*.json`, `png/`, `states/`, `gates_*.json`).
This directory makes no claim about excitons: it computes classical stationary node arrangements of stated pair kernels.

## Rebuild

The relaxation engine is the author's `rusty-Fenris-CMRR` v0.1 (MIT, commit 6d0df125). It is not vendored. The crate's
`Cargo.toml` expects a patched scratch copy:

    git clone https://github.com/xaviercallens/rusty-Fenris-CMRR fenris-cmrr && cd fenris-cmrr && git checkout 6d0df125
    sed -i 's#\.\./rusty-SUNDIALS/crates#<path to rusty-SUNDIALS-c3>/crates#' Cargo.toml     # pinned v11.6.0, 5db8041
    patch -p1 < <this directory>/engine_patch.diff

then point the `cmrr` path in this `Cargo.toml` at it. `engine_patch.diff` adds a `Pair` kernel trait and
`optimize_kernel`; `optimize` (Yukawa) is bit-for-bit unchanged (gate L-b1). Tests: `cargo test --release` (gates a1, a2, a3,
b2). Planted bugs for gate L-d: `--features bug1|bug2|bug3`, driver `python/gate_d.sh`.

## Binaries and scripts

* `fg kern|energy|lattice|bessel|run` (`src/bin/fg.rs`): kernel values, energies, triangular-lattice energy, batch
  relaxation of many starts (one RAYON thread per process recommended).
* `python/geometry.py` containers; `python/gates.py` gates a4/a5, b1, c, f; `python/study.py` production and analysis
  (`primary`, `wall`, `size`, `sens`); `python/aggregate.py` tables and summary figure.
