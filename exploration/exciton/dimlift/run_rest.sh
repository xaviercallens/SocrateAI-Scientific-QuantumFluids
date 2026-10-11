#!/bin/bash
# remaining registered E1/E2 runs after amendment A3 (square and hexagon, dip, are done)
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
for ks in "dip disc" "dip rect2" "dip lshape" "dip annulus" "g3 square" "g3 hexagon" "g3 disc"; do
  set -- $ks
  python3 dimlift.py results/e12_$1_$2.jsonl $1 $2 30 4 direct,lift1,lift2,slide > results/e12_$1_$2.log 2>&1
  echo "done $1 $2" >> results/e12_progress.txt
done
echo ALLDONE >> results/e12_progress.txt
