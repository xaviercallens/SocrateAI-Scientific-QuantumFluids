#!/usr/bin/env python3
"""Lighter run of the canonical calibration (fewer sweeps), unbuffered, as a fallback for the full run."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vortex_thermometer_canonical import calibrate, metropolis, read_beta, ROOT
rng = np.random.default_rng(2019); out = {}
for n_pairs in (2, 3, 4, 5, 6, 8):
    print(f"N = {2*n_pairs}", flush=True)
    betas = [-0.6, -0.3, 0.0, 0.3, 0.6, 1.0, 1.5, 2.0, 3.0]
    cal = calibrate(n_pairs, betas, rng, sweeps=1500, burn=400)
    b = np.array([c["beta"] for c in cal]); e = np.array([c["E_mean"] for c in cal]); v = np.array([c["E_var"] for c in cal])
    dEdb = np.gradient(e, b); fd = [(float(bb), float(x), float(-y)) for bb, x, y in zip(b[1:-1], dEdb[1:-1], v[1:-1])]
    Es = metropolis(n_pairs, 1.2, rng, sweeps=1200, burn=300); b_read = read_beta(cal, float(Es.mean()))
    out[str(2*n_pairs)] = {"cal": cal, "fluct_identity_(beta,dE/dbeta,-Var)": fd, "closure_beta0": 1.2, "closure_read": b_read,
                           "closure_PASS": bool(np.isfinite(b_read) and abs(b_read - 1.2) / 1.2 <= 0.10)}
    print(f"  closure: set 1.2 read {b_read:.3f} -> {'PASS' if out[str(2*n_pairs)]['closure_PASS'] else 'FAIL'}", flush=True)
    (ROOT / "data/generated/pgpe/vortex_thermometer_cal_fast.json").write_text(json.dumps(out, indent=1))
