#!/usr/bin/env python3
"""T = 0 control for alpha': translation speed of a single vortex pair versus its separation (compressibility /
Jones-Roberts correction to the point-vortex speed). imprint_v2 into a uniform condensate, evolve 60 time units,
track; report measured centre speed / torus point-vortex prediction, i.e. the apparent 1 - alpha' at T = 0 for each d.
-> data/generated/pgpe/transport/pair_speed_T0.json
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from vortex_transport import detect, imprint_v2
from transport_estimators import pv_velocity, unwrap

ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / "data/generated/pgpe/transport/pair_speed_T0.json"
s = PGPE(N=128, L=64.0); L = s.L; res = {}
for d in (3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0):
    t0 = time.time(); c0 = np.zeros((128, 128), complex); c0[0, 0] = 128 ** 2
    pos = np.mod(np.array([[30.13 + d / 2, 20.31], [30.13 - d / 2, 20.31]]), L); q = np.array([1, -1])
    c = imprint_v2(s, c0, pos, q); last = pos.copy(); R = [pos.copy()]; T = [0.0]; ok = True
    for k in range(60):
        c = s.run(c, 1.0); dp, dq = detect(s, c); cur = []
        for i in range(2):
            cand = np.nonzero(dq == q[i])[0]
            if not len(cand): ok = False; break
            dd = dp[cand] - last[i]; dd -= L * np.round(dd / L); j = int(np.argmin(np.hypot(dd[:, 0], dd[:, 1]))); cur.append(dp[cand[j]])
        if not ok: break
        last = np.array(cur); R.append(last.copy()); T.append(k + 1.0)
    T = np.array(T); U = unwrap(np.array(R), L); m = T >= 10          # skip imprint transient
    centre = U[:, 0] + U[:, 1]; disp = centre[m][-1] - centre[m][0]; dt = T[m][-1] - T[m][0]
    v_meas = 0.5 * disp / dt
    v_pred = np.mean([0.5 * (pv_velocity(np.mod(U[k], L), q, L)[0] + pv_velocity(np.mod(U[k], L), q, L)[1]) for k in np.nonzero(m)[0]], axis=0)
    dsep = U[:, 0] - U[:, 1]; dsep = np.hypot(dsep[:, 0], dsep[:, 1])
    ratio = float(np.dot(v_meas, v_pred) / np.dot(v_pred, v_pred))
    res[str(d)] = {"one_minus_alpha_prime_T0": ratio, "v_meas": float(np.hypot(*v_meas)), "v_pred": float(np.hypot(*v_pred)), "plane_1_over_d": 1 / d,
                   "d_first": float(dsep[m][0]), "d_last": float(dsep[-1]), "tracked_to": float(T[-1]), "seconds": round(time.time() - t0, 1)}
    print(d, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in res[str(d)].items()}, flush=True)
    OUT.write_text(json.dumps(res, indent=1))
