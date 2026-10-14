#!/bin/bash
# Resume after the 2026-10-13 10:14 reboot killed the first launch (PREREG.md code and parameters unchanged).
# H8 K=40 already finished (records/H8_K40.json); the other 13 runs restart from scratch (no checkpointing).
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1
printf "%s\n" "V1a 40" "V1b 40" "V2 40" "V3 40" "H2 40" "H4 40" "V1a 30" "V1b 30" "V2 30" "V3 30" "H2 30" "H4 30" "H8 30" |
  xargs -P 7 -L 1 bash -c '../../../../.venv/bin/python -u run_h1pp.py $0 $1 > logs/$0_K$1.log 2>&1; echo "DONE $0 K$1" >> logs/done.txt'
echo ALLDONE >> logs/done.txt
