#!/bin/bash
# usage: lean_check.sh /abs/path/file.lean [outfile]
# Compile a chapter-4 Lean file against Mathlib (OpenAI tree, read-only) plus the scratch .olean files of
# BoseIntegral / PhononSeries / PhononSpecificHeat built by lean_deps.sh.
set -u
SP=/mnt/data/xdev-cache/tmp/claude-1000/-home-xavkal-xdev-SocrateAI-Scientific-QuantumFluids/74574ea7-7320-4d9f-8911-de38b1699e5e/scratchpad/ch04
TREE=/home/xavkal/xdev/OpenAINavierStokesEuler/NavierStokesAndEuler
FILE="$1"
OUT="${2:-$SP/logs/$(basename "$FILE" .lean).log}"
cd "$TREE"
export LEAN_PATH="$(lake env printenv LEAN_PATH):$SP/oleans"
LEAN=/mnt/data/home/xavkal/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin/lean
s=$(date +%s)
nice "$LEAN" "$FILE" > "$OUT" 2>&1
rc=$?
e=$(date +%s)
echo "exit=$rc seconds=$((e-s))" >> "$OUT"
