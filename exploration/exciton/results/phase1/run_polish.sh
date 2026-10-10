#!/bin/bash
# Exploratory polish (not registered): longer flows from the best configuration of selected cases.
PO=/mnt/data/xdev-cache/target_exciton2/release/polish
RUNS=/mnt/data/xdev-cache/exciton_p1/runs
OUT=/mnt/data/xdev-cache/exciton_p1/polish.jsonl
: > $OUT
for c in K1_1.5_T36c K1_1.5_T36s K2_0.5_T36c K1_0.5_T36s; do
  nice -n 10 $PO $RUNS $c 3e5 >> $OUT 2>/dev/null
done
export QF_AMEND=A2
for c in K4_0.1_T36c K4_0.1_T36s K4_0.5_T36s K2_0.5_T36s K2_1.5_T36c K2_1.5_T36s; do
  nice -n 10 $PO $RUNS $c 3e5 >> $OUT 2>/dev/null
done
echo done >> $OUT
