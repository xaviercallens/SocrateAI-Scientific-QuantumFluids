#!/bin/bash
# K-e3 control: R32 with the registered white noise (no NOISEBAND); starts when the R64 run has finished
KR=/mnt/data/xdev-cache/cargo-target-exciton-kr/release/kr
R=$(dirname "$0")/results
while [ ! -e $R/ke_heavy_a.done ]; do sleep 10; done
$KR run M=32 L=16 SIGMA=3 V0=0.5 SEED=1 RTOL=1e-4 ATOL=1e-7 TEND=200000 TRACK=1 STOP=1e-8 TAG=Ke_R32white_V0.5_s1 OUT=$R/ke.jsonl LOG=$R/ke_Ke_R32white_V0.5_s1.log STATE=$R/ke_Ke_R32white_V0.5_s1.f64 > $R/ke_Ke_R32white_V0.5_s1.out 2>&1
echo done > $R/ke_r32white.done
