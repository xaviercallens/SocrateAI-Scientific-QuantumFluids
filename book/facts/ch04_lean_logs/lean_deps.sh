#!/bin/bash
# Compile BoseIntegral, PhononSeries, PhononSpecificHeat (library sources, unchanged) to .olean files in the
# scratchpad so that chapter-4 Lean files can `import` them.  Mathlib comes from the OpenAI tree (read-only use).
set -u
SP=/mnt/data/xdev-cache/tmp/claude-1000/-home-xavkal-xdev-SocrateAI-Scientific-QuantumFluids/74574ea7-7320-4d9f-8911-de38b1699e5e/scratchpad/ch04
SRC=/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/lean_src
TREE=/home/xavkal/xdev/OpenAINavierStokesEuler/NavierStokesAndEuler
mkdir -p "$SP/oleans" "$SP/logs"
cd "$TREE"
export LEAN_PATH="$(lake env printenv LEAN_PATH):$SP/oleans"
LEAN=/mnt/data/home/xavkal/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin/lean
cd "$SRC"
for m in BoseIntegral PhononSeries PhononSpecificHeat; do
  s=$(date +%s)
  nice "$LEAN" --root="$SRC" -o "$SP/oleans/$m.olean" "$SRC/$m.lean" > "$SP/logs/$m.log" 2>&1
  rc=$?
  e=$(date +%s)
  echo "$m exit=$rc seconds=$((e-s))" >> "$SP/logs/summary.txt"
done
echo done >> "$SP/logs/summary.txt"
