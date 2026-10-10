#!/bin/bash
# Exploratory polish (not registered) for the cases not covered by run_polish.sh. Waits for the night run to finish.
until grep -q "finished" /mnt/data/xdev-cache/exciton_p1/ex1_night.log; do sleep 10; done
PO=/mnt/data/xdev-cache/target_exciton2/release/polish
RUNS=/mnt/data/xdev-cache/exciton_p1/runs
OUT=/mnt/data/xdev-cache/exciton_p1/polish2.jsonl
: > $OUT
export QF_AMEND=A2
for c in K2_1.5_T36s K3_0.1_T36c K3_0.1_T36s K3_0.5_T36c K3_0.5_T36s; do
  nice -n 10 $PO $RUNS $c 3e5 >> $OUT 2>/dev/null
done
echo done >> $OUT
