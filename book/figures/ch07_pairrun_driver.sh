#!/bin/bash
# Driver of ch07_pairrun.py: advances the run chunk by chunk, each chunk under the shared heavy-job lock (so that the siblings' Lean
# compiles can interleave), until the flag file done_<tag> exists.
#   bash ch07_pairrun_driver.sh TAG [extra ch07_pairrun.py arguments]
TAG="$1"; shift
ROOT=/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids
for i in $(seq 1 60); do
  flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice -n 10 env PYTHONPATH=/mnt/data/xdev-cache/qf_ext RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 \
    "$ROOT/.venv/bin/python" "$ROOT/book/figures/ch07_pairrun.py" --tag "$TAG" "$@" || { echo "chunk failed"; break; }
  [ -f "/mnt/data/xdev-cache/book_ch07/done_$TAG" ] && { echo "finished"; break; }
done
