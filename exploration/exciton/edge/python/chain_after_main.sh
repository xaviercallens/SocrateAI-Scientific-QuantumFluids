#!/bin/bash
# waits for the main plan to finish (or its budget log line), then runs the aligned stage (N=61,91) and the extra random stage
cd /home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/exploration/exciton/edge
while ps -eo cmd | grep -v grep | grep -q "run_study.py"; do sleep 10; done
export QF_TABLE_DIR=$PWD/results
B=/mnt/data/xdev-cache/exciton_edge_target/release/edge
cd python
python3 run_aligned.py $B ../results/runs ../results/runs_aligned 900 91 61
python3 run_extra.py $B ../results/runs ../results/runs_extra 1500
