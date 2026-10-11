#!/bin/bash
# waits for the wallhalfrsa production to finish (log polling), then runs edgecmp, sens, size, gate L-c
R=/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/exploration/exciton/rust/fenris-gated
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
until [ "$(grep -c 'secs=' $R/results/wallrsa_full.log)" -ge 40 ]; do sleep 15; done
cd $R/python
python3 study.py edgecmp --workers 2 > $R/results/edgecmp.log 2>&1
python3 study.py sens --workers 2 > $R/results/sens.log 2>&1
python3 study.py size --workers 2 > $R/results/size.log 2>&1
python3 gates.py c > $R/results/gate_c.log 2>&1
echo QUEUE_DONE > $R/results/queue.done
