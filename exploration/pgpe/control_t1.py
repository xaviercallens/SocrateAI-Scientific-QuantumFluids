#!/usr/bin/env python3
"""Control C-T1 of PGPE_BKT_PREREG.md amendment A2: the dipole-matching ratio Q must read bound dipoles as
Q < 0.2 and independent random charges as Q in [0.85, 1.15]."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from observables import dipole_matching

s = PGPE(N=16, L=64.0)                       # only s.L is used
rng = np.random.default_rng(7)
c = rng.random((50, 2)) * s.L; ang = rng.random(50) * 2 * np.pi
dip = np.vstack([c, (c + np.column_stack([np.cos(ang), np.sin(ang)])) % s.L])
qd = np.r_[np.ones(50, int), -np.ones(50, int)]
_, _, Qd = dipole_matching(s, dip, qd, rng, n_null=20)
pr = rng.random((100, 2)) * s.L; qr = np.r_[np.ones(50, int), -np.ones(50, int)]
Qr = np.mean([dipole_matching(s, pr, rng.permutation(qr), rng, n_null=20)[2] for _ in range(20)])
res = {"Q_dipoles": Qd, "Q_random_mean20": float(Qr), "PASS": bool(Qd < 0.2 and 0.85 <= Qr <= 1.15)}
print(res)
Path(__file__).resolve().parents[2].joinpath("data/generated/pgpe/control_t1.json").write_text(json.dumps(res, indent=1))
