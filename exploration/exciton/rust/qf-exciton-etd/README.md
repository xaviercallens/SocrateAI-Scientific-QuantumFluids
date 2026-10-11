# qf-exciton-etd

ETDRK4 (Cox-Matthews, Kassam-Trefethen contour coefficients), Lawson RK4 and Krogstad ETDRK4 for the driven-dissipative exciton GPE
of `qf-exciton-p1/src/bin/dd.rs`. Pure-Rust FFT; pinned rusty-SUNDIALS `cvode` only for cross-checks.
Design: `docs/designs/EXCITON_FLUID_ETD_PREREG.md`; results: `docs/designs/EXCITON_FLUID_ETD_RESULTS.md`; raw output: `results/`.

    CARGO_TARGET_DIR=/mnt/data/xdev-cache/target_exciton_etd cargo build --release -j 2
    etd test  <out>                 # unit tests
    etd a <out> [bug=1]             # T-a
    etd b <out> G8|G16 [scheme=etd|law|lawk|etdk|krog] [bug=2|3] [gr=200]   # T-b
    etd c <out> <scheme> n0= dx= M= [hmin=] tag=                            # T-c
    etd d <out> i|ii|iii|hsweep|stat8 [v0= seeds= h= bug=3]                 # T-d
    etd e <out> scaling|etd|cvode                                           # T-e
    etd f2 <out> [n0= hs=]          # T-f(ii)
    etd g <out> [n0= hs= scheme=]   # T-g
