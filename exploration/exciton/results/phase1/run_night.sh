#!/bin/bash
# Phase 1, remaining cases, amendment A2 for the long-range kernels (docs/designs/EXCITON_FLUID_PHASE1_PREREG.md, section 7)
export QF_THREADS=4
EX=/mnt/data/xdev-cache/target_exciton2/release/ex1
OUT=/mnt/data/xdev-cache/exciton_p1/runs
LOG=/mnt/data/xdev-cache/exciton_p1/ex1_night.log
echo "start $(date -u +%FT%TZ)" >> $LOG
# N1: the registered design (cheap)
nice -n 10 $EX $OUT N1_ >> $LOG 2>&1
# the long-range kernels under amendment A2
export QF_AMEND=A2
nice -n 10 $EX $OUT K4_ >> $LOG 2>&1
nice -n 10 $EX $OUT K2_0.5_T36s K2_1.5_ >> $LOG 2>&1
nice -n 10 $EX $OUT K3_ >> $LOG 2>&1
echo "finished $(date -u +%FT%TZ)" >> $LOG
