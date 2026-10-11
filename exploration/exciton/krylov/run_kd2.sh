#!/bin/bash
# K-d' (amendment A2) then the heavy K-e runs; waits for run_ke_small.sh
KR=/mnt/data/xdev-cache/cargo-target-exciton-kr/release/kr
R=$(dirname "$0")/results
while [ ! -e $R/ke_small.done ]; do sleep 10; done
G="M=16 L=16 SIGMA=3 V0=0.5 SEED=1 RTOL=1e-4 ATOL=1e-7 TEND=200000 TRACK=1 STOP=1e-8"
for v in "none:Kd2_precnone:none:exact" "kin:Kd2_prekin:none:exact" "badsign:Kd2_badsign:none:exact" "block:Kd2_bugjac:jac:exact" "block:Kd2_fd:none:fd" "block:Kd2_bugrhs:rhs:exact"; do
  IFS=: read prec tag bug jv <<< "$v"
  $KR run $G PREC=$prec BUG=$bug JV=$jv TAG=$tag OUT=$R/kd2.jsonl LOG=$R/${tag}.log > /dev/null 2>&1
done
echo done > $R/kd2.done
