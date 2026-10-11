#!/bin/bash
# continuation of run_ke_heavy.sh split over two slots: this script runs G64a then F64 (the R32 run of run_ke_heavy.sh was already running)
KR=/mnt/data/xdev-cache/cargo-target-exciton-kr/release/kr
R=$(dirname "$0")/results
run() {
  tag=$1; shift
  $KR run M=$1 L=$2 SIGMA=$3 V0=$4 SEED=$5 RTOL=$6 ATOL=$7 TEND=200000 TRACK=1 STOP=1e-8 TAG=$tag OUT=$R/ke.jsonl LOG=$R/ke_$tag.log STATE=$R/ke_$tag.f64 "${@:8}" > $R/ke_$tag.out 2>&1
}
run Ke_G64a_V0.5_s1 64 64 12 0.5 1 1e-4 1e-7
run Ke_F64_V0.5_s1 64 64 3 0.5 1 1e-4 1e-7
echo done > $R/ke_heavy_b.done
