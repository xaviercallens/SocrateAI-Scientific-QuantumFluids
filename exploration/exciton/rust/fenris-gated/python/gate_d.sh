#!/bin/bash
# L-d: planted bugs. Each build must fail at least one of a1/a2 (cargo test) or a4 (independent image-sum check).
D=/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/exploration/exciton/rust/fenris-gated
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
out=$D/results/gate_d.txt; : > $out
for b in bug1 bug2 bug3; do
  T=/mnt/data/xdev-cache/fg-target-$b
  echo "=== $b: cargo test (a1,a2,a3) ===" >> $out
  (cd $D && CARGO_TARGET_DIR=$T cargo test --release --offline -j1 --features $b 2>&1 | grep -E "^test |test result: .* [1-9][0-9]* (passed|failed)" >> $out)
  echo "=== $b: python a4/a5 (independent image sum) ===" >> $out
  (cd $D && CARGO_TARGET_DIR=$T cargo build --release --offline -j1 --features $b --bin fg 2>&1 | tail -1 >> $out)
  (cd $D/python && python3 gates.py a --fg $T/release/fg 2>&1 | grep -E "a4_pass|a5_pass|a4_image_sum_max|a4_integral_max" >> $out)
done
echo DONE >> $out
