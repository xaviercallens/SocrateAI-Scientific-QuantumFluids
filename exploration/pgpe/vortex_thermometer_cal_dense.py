#!/usr/bin/env python3
"""Dense, long-chain calibration around beta = 1.2 for the sizes where the fast closure failed (N = 6, 8):
decides between 'instrument wrong' and 'precision-limited'. Grid excludes 1.2 itself."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vortex_thermometer_canonical import calibrate, metropolis, read_beta, ROOT
rng = np.random.default_rng(2020); out = {}
for n_pairs in (3, 4):
    print(f"N = {2*n_pairs}", flush=True)
    cal = calibrate(n_pairs, [0.8, 1.0, 1.1, 1.3, 1.4, 1.6], rng, sweeps=6000, burn=1500)
    reads = []
    for rep in range(3):
        Es = metropolis(n_pairs, 1.2, rng, sweeps=6000, burn=1500); reads.append(read_beta(cal, float(Es.mean())))
        print(f"  closure rep {rep}: set 1.2 read {reads[-1]:.3f}", flush=True)
    out[str(2*n_pairs)] = {"cal": cal, "closure_reads": reads, "closure_mean": float(np.mean(reads)),
                           "closure_PASS": bool(abs(np.mean(reads) - 1.2) / 1.2 <= 0.10)}
    (ROOT / "data/generated/pgpe/vortex_thermometer_cal_dense.json").write_text(json.dumps(out, indent=1))
