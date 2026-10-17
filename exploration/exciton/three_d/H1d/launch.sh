#!/bin/bash
# H1d runs (PREREG.md). Safe to relaunch after a kill: run_h1d.py skips (case, s, m) whose record exists.
cd "$(dirname "$0")"; mkdir -p logs
{
  for g in "2 8" "4 32" "8 128"; do echo "V1 $g"; done
  for g in "4 32" "4 48" "6 72" "8 96"; do echo "V2 $g"; done
  for c in D3pi D3a2 D3a4 D3a8; do for g in "4 24" "5 30" "6 36" "5 40" "6 48" "8 48"; do echo "$c $g"; done; done
} | xargs -P 3 -L 1 bash -c '../../../../.venv/bin/python -u run_h1d.py $0 $1 $2 >> logs/$0.log 2>&1; echo "DONE $0 s$1 m$2" >> logs/done.txt'
echo ALLDONE >> logs/done.txt
