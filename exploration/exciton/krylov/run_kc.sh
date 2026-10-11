#!/bin/bash
# K-c: cost versus M (3 repetitions each); waits for run_kabd.sh
KR=/mnt/data/xdev-cache/cargo-target-exciton-kr/release/kr
R=$(dirname "$0")/results
while [ ! -e $R/kabd.done ]; do sleep 10; done
for M in 8 16 32 64; do
  L=$M; S=$(python3 -c "print(0.1875*$M)")
  for rep in 1 2 3; do
    echo "load: $(cat /proc/loadavg)" >> $R/kc_load.txt
    $KR run M=$M L=$L SIGMA=$S V0=0.5 SEED=1 TEND=20 RTOL=1e-7 ATOL=1e-10 TAG=Kc_kr_M${M}_r$rep OUT=$R/kc.jsonl > /dev/null 2>&1
  done
done
for M in 8 16; do
  L=$M; S=$(python3 -c "print(0.1875*$M)")
  for tol in "1e-10 1e-12" "1e-7 1e-10"; do
    set -- $tol
    for rep in 1 2 3; do
      echo "load: $(cat /proc/loadavg)" >> $R/kc_load.txt
      $KR run M=$M L=$L SIGMA=$S V0=0.5 SEED=1 SOLVER=cvode TEND=20 RTOL=$1 ATOL=$2 TAG=Kc_cvode_M${M}_rtol$1_r$rep OUT=$R/kc.jsonl > /dev/null 2>&1
    done
  done
done
echo done > $R/kc.done
