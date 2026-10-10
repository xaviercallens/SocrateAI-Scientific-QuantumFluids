#!/bin/bash
# Heavy part of figure ch10_estimator: the registered synthetic gate G0 (known alpha = 0.02), run by the rusty-SUNDIALS example `g0_scan`
# (Rust estimators + Rust Langevin generator, seeds 0..7, deterministic) and by the numpy/Rust cross-check on identical tracks.
# ONE acquisition of the shared heavy-job lock covers the three runs (~8 min of CPU on an idle core).
#   bash book/figures/ch10_run_estimator.sh
BOOK=/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/book
RAW=$BOOK/figures/ch10_raw
LOCK=/mnt/data/xdev-cache/tmp/qf_heavy.lock
G0=/home/xavkal/xdev/rusty-SUNDIALS-c3/target/release/examples/g0_scan
PY=/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/.venv/bin/python
mkdir -p $RAW
( cd /home/xavkal/xdev/rusty-SUNDIALS-c3 && git rev-parse HEAD && git log -1 --format=%cd ) > $RAW/rusty_sundials_rev.txt
export BOOK RAW G0 PY
flock $LOCK nice bash -c '
echo "lock acquired $(date) ; $(uptime)" > $RAW/progress.txt
( time $G0 8 --eta-scan ) > $RAW/g0_eta_scan.txt 2> $RAW/g0_eta_scan.time; echo "eta scan done $(date)" >> $RAW/progress.txt
( time $G0 8 ) > $RAW/g0_noise_scan.txt 2> $RAW/g0_noise_scan.time; echo "noise scan done $(date)" >> $RAW/progress.txt
( time env PYTHONPATH=/mnt/data/xdev-cache/qf_ext $PY $BOOK/figures/ch10_cross_impl.py ) > $RAW/cross_impl.txt 2> $RAW/cross_impl.time; echo "cross-impl done $(date) ; $(uptime)" >> $RAW/progress.txt
'
