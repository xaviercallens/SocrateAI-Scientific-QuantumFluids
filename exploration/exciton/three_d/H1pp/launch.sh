#!/bin/bash
# H1'' gate runs (PREREG.md): K = 40 first, then K = 30; 7 in parallel, single-threaded.
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1
printf "%s\n" "V1a 40" "V1b 40" "V2 40" "V3 40" "H2 40" "H4 40" "H8 40" "V1a 30" "V1b 30" "V2 30" "V3 30" "H2 30" "H4 30" "H8 30" |
  xargs -P 7 -L 1 bash -c '../../../../.venv/bin/python -u run_h1pp.py $0 $1 > logs/$0_K$1.log 2>&1; echo "DONE $0 K$1" >> logs/done.txt'
echo ALLDONE >> logs/done.txt
