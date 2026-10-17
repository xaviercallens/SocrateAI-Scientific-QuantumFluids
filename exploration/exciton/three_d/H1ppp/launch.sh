#!/bin/bash
# H1''' runs (PREREG.md). Safe to relaunch after a kill: run_h1pp.py resumes from records/ckpt/ and skips finished cases.
cd "$(dirname "$0")"; mkdir -p logs
export OMP_NUM_THREADS=1
printf "%s\n" "V3 50" "V3 60" "H2 50" "H4 50" "H8 50" |
  xargs -P 5 -L 1 bash -c '../../../../.venv/bin/python -u run_h1pp.py $0 $1 >> logs/$0_K$1.log 2>&1; echo "DONE $0 K$1" >> logs/done.txt'
echo ALLDONE >> logs/done.txt
