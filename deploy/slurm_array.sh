#!/bin/bash
# UNTESTED. One array task per shape of E1/E2:  sbatch --array=0-5 deploy/slurm_array.sh
#SBATCH --job-name=dimlift
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=04:00:00
SHAPES=(square hexagon disc rect2 lshape annulus)
S=${SHAPES[$SLURM_ARRAY_TASK_ID]}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd exploration/exciton/dimlift
python3 dimlift.py results/e12_dip_${S}.jsonl dip $S 100 8 direct,lift1,lift2,slide
