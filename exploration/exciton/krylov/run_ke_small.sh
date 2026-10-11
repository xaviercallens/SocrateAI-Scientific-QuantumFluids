#!/bin/bash
# K-e0, K-e1 and the cheap members of K-e4 (see PREREG.md, amendment A1: rtol 1e-4, atol 1e-7 unless stated)
KR=/mnt/data/xdev-cache/cargo-target-exciton-kr/release/kr
R=$(dirname "$0")/results
run() { # tag M L SIGMA V0 SEED RTOL ATOL [extra]
  tag=$1; shift
  $KR run M=$1 L=$2 SIGMA=$3 V0=$4 SEED=$5 RTOL=$6 ATOL=$7 TEND=200000 TRACK=1 STOP=1e-8 TAG=$tag OUT=$R/ke.jsonl LOG=$R/ke_$tag.log STATE=$R/ke_$tag.f64 "${@:8}" > $R/ke_$tag.out 2>&1
}
run Ke_G16_V0.25_s1 16 16 3 0.25 1 1e-4 1e-7
run Ke_G16_V1.0_s1 16 16 3 1.0 1 1e-4 1e-7
run Ke_G16_V0.5_s2 16 16 3 0.5 2 1e-4 1e-7
run Ke_G16_V0.5_s3 16 16 3 0.5 3 1e-4 1e-7
run Ke0_G16_V0.5_s1_rtol1e-6 16 16 3 0.5 1 1e-6 1e-9
for v in 0.25 0.5 1.0; do run Ke_G8_V${v}_s1 8 8 1.5 $v 1 1e-4 1e-7; done
run Ke_G32_V0.5_s1 32 32 6 0.5 1 1e-4 1e-7
run Ke_F32_V0.5_s1 32 32 3 0.5 1 1e-4 1e-7
echo done > $R/ke_small.done
