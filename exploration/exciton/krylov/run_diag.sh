#!/bin/bash
# diagnostics D1, D2 of amendment A3
KR=/mnt/data/xdev-cache/cargo-target-exciton-kr/release/kr
R=$(dirname "$0")/results
$KR run M=32 L=64 SIGMA=12 V0=0.5 SEED=1 RTOL=1e-4 ATOL=1e-7 TEND=40000 TRACK=1 STOP=1e-8 TAG=Diag_D1_M32 OUT=$R/diag.jsonl LOG=$R/diag_D1_M32.log STATE=$R/diag_D1_M32.f64 > /dev/null 2>&1
$KR run M=16 L=64 SIGMA=12 V0=0.5 SEED=1 RTOL=1e-4 ATOL=1e-7 TEND=40000 TRACK=1 STOP=1e-8 TAG=Diag_D1_M16 OUT=$R/diag.jsonl LOG=$R/diag_D1_M16.log STATE=$R/diag_D1_M16.f64 > /dev/null 2>&1
$KR run M=32 L=64 SIGMA=12 V0=0.5 SEED=1 RTOL=1e-6 ATOL=1e-9 TEND=20000 TRACK=1 STOP=1e-8 TAG=Diag_D2_M32_rtol1e-6 OUT=$R/diag.jsonl LOG=$R/diag_D2_M32.log STATE=$R/diag_D2_M32.f64 > /dev/null 2>&1
echo done > $R/diag.done
