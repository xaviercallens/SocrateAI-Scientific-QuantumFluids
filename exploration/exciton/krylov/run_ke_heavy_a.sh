#!/bin/bash
# waits for the R32 run to be recorded, then runs R64 (band-limited noise)
KR=/mnt/data/xdev-cache/cargo-target-exciton-kr/release/kr
R=$(dirname "$0")/results
while ! grep -q Ke_R32_V0.5_s1 $R/ke.jsonl; do sleep 10; done
$KR run M=64 L=16 SIGMA=3 V0=0.5 SEED=1 RTOL=1e-4 ATOL=1e-7 TEND=200000 TRACK=1 STOP=1e-8 NOISEBAND=3.14159 TAG=Ke_R64_V0.5_s1 OUT=$R/ke.jsonl LOG=$R/ke_Ke_R64_V0.5_s1.log STATE=$R/ke_Ke_R64_V0.5_s1.f64 > $R/ke_Ke_R64_V0.5_s1.out 2>&1
echo done > $R/ke_heavy_a.done
