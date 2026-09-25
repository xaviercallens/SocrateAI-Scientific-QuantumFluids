#!/usr/bin/env python3
"""Round 3: extend the canonical calibration to N = 18..24 (same script, same criterion), merging into vortex_thermometer_cal.json."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vortex_thermometer_canonical import calibrate, metropolis, read_beta, ROOT
P = ROOT / "data/generated/pgpe/vortex_thermometer_cal_large.json"; out = {}; rng = np.random.default_rng(2022)
for n_pairs in (13, 14, 16, 18, 20):
    print(f"N = {2*n_pairs}", flush=True)
    cal = calibrate(n_pairs, [-0.6, -0.3, 0.0, 0.3, 0.6, 1.0, 1.5, 2.0, 3.0], rng, sweeps=2000, burn=500)
    Es = metropolis(n_pairs, 1.2, rng, sweeps=3000, burn=800); b = read_beta(cal, float(Es.mean()))
    out[str(2*n_pairs)] = {"cal": cal, "closure_beta0": 1.2, "closure_read": b, "closure_PASS": bool(np.isfinite(b) and abs(b-1.2)/1.2 <= 0.10)}
    print(f"  closure: set 1.2 read {b:.3f} -> {'PASS' if out[str(2*n_pairs)]['closure_PASS'] else 'FAIL'}", flush=True)
    P.write_text(json.dumps(out, indent=1))
