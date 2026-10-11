#!/bin/bash
# K-e2 (G64a), K-e3 (R32, R64 with band-limited noise), K-e4 (F64); waits for run_kd2.sh (which waits for run_ke_small.sh)
KR=/mnt/data/xdev-cache/cargo-target-exciton-kr/release/kr
R=$(dirname "$0")/results
while [ ! -e $R/kd2.done ]; do sleep 10; done
run() { # tag M L SIGMA V0 SEED RTOL ATOL [extra]
  tag=$1; shift
  $KR run M=$1 L=$2 SIGMA=$3 V0=$4 SEED=$5 RTOL=$6 ATOL=$7 TEND=200000 TRACK=1 STOP=1e-8 TAG=$tag OUT=$R/ke.jsonl LOG=$R/ke_$tag.log STATE=$R/ke_$tag.f64 "${@:8}" > $R/ke_$tag.out 2>&1
}
run Ke_R32_V0.5_s1 32 16 3 0.5 1 1e-4 1e-7 NOISEBAND=3.14159
run Ke_G64a_V0.5_s1 64 64 12 0.5 1 1e-4 1e-7
run Ke_R64_V0.5_s1 64 16 3 0.5 1 1e-4 1e-7 NOISEBAND=3.14159
run Ke_F64_V0.5_s1 64 64 3 0.5 1 1e-4 1e-7
echo done > $R/ke_heavy.done
