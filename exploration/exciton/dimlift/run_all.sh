#!/bin/bash
# registered runs of dimlift/PREREG.md (E1, E2); two workers per shape, shapes sequentially
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p results
for k in dip g3; do
  for s in square hexagon disc rect2 lshape annulus; do
    if [ "$k" = g3 ] && [ "$s" != square ] && [ "$s" != hexagon ] && [ "$s" != disc ]; then continue; fi
    python3 dimlift.py results/e12_${k}_${s}.jsonl $k $s 30 2 direct,lift1,lift2,slide > results/e12_${k}_${s}.log 2>&1
    echo "done $k $s" >> results/e12_progress.txt
  done
done
echo ALLDONE >> results/e12_progress.txt
