#!/bin/bash
# Chapter 3: compile, against the pinned Mathlib (OpenAI tree's) and the library's own built oleans, the three
# modules whose standalone audit in facts/audit failed only because their imports (VortexWinding, QuantizedCirculation)
# are top-level modules of the QuantumFluids lake build (oleans in qf-lake), not of the OpenAI tree.
TREE=/home/xavkal/xdev/OpenAINavierStokesEuler/NavierStokesAndEuler
SRC=/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/lean_src
OUT=/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/book/facts/ch03_audit
LEAN=/mnt/data/home/xavkal/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin/lean
LP="$(cd $TREE && lake env printenv LEAN_PATH):/mnt/data/home/xavkal/xavkal-tools/qf-lake/build/lib/lean"
$LEAN --version > $OUT/lean_version.txt 2>&1
for m in "$@"; do
  s=$(date +%s)
  LEAN_PATH="$LP" flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice $LEAN $SRC/$m.lean > $OUT/$m.log 2>&1
  echo "exit=$? seconds=$(( $(date +%s) - s ))" >> $OUT/$m.log
done
echo finished > $OUT/DONE_$(echo "$@" | tr ' ' '_')
