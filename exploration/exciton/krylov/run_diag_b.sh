#!/bin/bash
# D1 M=16 after the D1 M=32 run has been recorded (the second half of run_diag.sh split over two slots)
KR=/mnt/data/xdev-cache/cargo-target-exciton-kr/release/kr
R=$(dirname "$0")/results
while ! grep -q Diag_D1_M32 $R/diag.jsonl 2>/dev/null; do sleep 10; done
$KR run M=16 L=64 SIGMA=12 V0=0.5 SEED=1 RTOL=1e-4 ATOL=1e-7 TEND=40000 TRACK=1 STOP=1e-8 TAG=Diag_D1_M16 OUT=$R/diag.jsonl LOG=$R/diag_D1_M16.log STATE=$R/diag_D1_M16.f64 > /dev/null 2>&1
echo done > $R/diag_b.done
