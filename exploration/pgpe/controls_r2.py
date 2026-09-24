#!/usr/bin/env python3
"""Controls C1-C3 of docs/designs/PGPE_R2_PREREG.md Part I."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from observables import vortices
from round2 import quadrupole_config, imprint, heat

ROOT = Path(__file__).resolve().parents[2]; SW = ROOT / "data/generated/pgpe/sweep"
s = PGPE(N=128, L=64.0)
pos, q = quadrupole_config(s.L)
res = {}
# C1: imprint on the uniform state; detected set == imprinted set (positions to within one plaquette, charges exact)
cu = imprint(s, s.uniform(1.0), pos, q)
dpos, dq = vortices(s, cu)
match = len(dq) == len(q)
if match:
    for (x, y), qq in zip(pos, q):
        d = np.hypot(*(((dpos - [x, y]) + s.L / 2) % s.L - s.L / 2).T)
        j = np.argmin(d); match &= bool(d[j] <= s.dx and dq[j] == qq)
res["C1"] = {"n_detected": int(len(dq)), "n_imprinted": int(len(q)), "PASS": bool(match)}
# C1b (amendment R2-A1): the vortex-count negative control is insensitive (a violated sum q x = 0 gives a sub-2pi phase
# jump along one boundary, not a vortex). Measure periodicity directly: the jump must be 0 for the configuration and
# 2 pi D / L for one vortex displaced by D in x (theta_1 quasi-periodicity).
from round2 import theta1


def phase_at(Z, P, Q):
    ph = np.ones_like(Z)
    for (xj, yj), qj in zip(P, Q):
        u = theta1(np.pi * (Z - (xj + 1j * yj)) / s.L); u = u / abs(u); ph *= u if qj > 0 else np.conj(u)
    return ph


xs = np.linspace(0, s.L, 200, endpoint=False) + 0.1
jumps = {}
for nm, P in [("good", pos), ("bad", pos + np.array([[3.0, 0]] + [[0, 0]] * 7))]:
    jy = np.abs(np.angle(phase_at(xs + 1j * s.L, P, q) / phase_at(xs + 0j, P, q))).max()
    jx = np.abs(np.angle(phase_at(s.L + 1j * xs, P, q) / phase_at(0 + 1j * xs, P, q))).max()
    jumps[nm] = (float(jy), float(jx))
res["C1b"] = {"good_jumps": jumps["good"], "bad_jumps": jumps["bad"], "bad_predicted": 2 * np.pi * 3 / s.L,
              "PASS": bool(max(jumps["good"]) < 1e-9 and abs(jumps["bad"][0] - 2 * np.pi * 3 / s.L) < 1e-6)}
# C2, C3 on each base
k1 = 2 * np.pi / s.L
for name in ["e0.90_s11_t4000", "e0.90_s12_t4000", "e0.60_s11_t4000"]:
    c0 = np.load(SW / f"{name}_final.npy")
    cV = imprint(s, c0, pos, q)
    cP = heat(s, c0, s.energy(cV), np.random.default_rng(7))
    N0 = s.norm(c0)
    res[name] = {"E0": s.energy(c0) / N0, "E_V": s.energy(cV) / N0, "E_P": s.energy(cP) / N0,
                 "C2_relE": abs(s.energy(cV) - s.energy(cP)) / s.energy(cV), "C2_normdiff": abs(s.norm(cV) - s.norm(cP)) / N0,
                 "C3_PV": float(np.linalg.norm(s.momentum(cV)) / N0 / k1), "C3_PP": float(np.linalg.norm(s.momentum(cP)) / N0 / k1),
                 "nv_base": int(len(vortices(s, c0)[1])), "nv_V": int(len(vortices(s, cV)[1])), "nv_P": int(len(vortices(s, cP)[1]))}
    r = res[name]; r["PASS"] = bool(r["C2_relE"] <= 1e-4 and r["C2_normdiff"] <= 1e-10 and r["C3_PV"] <= 0.05 and r["C3_PP"] <= 0.05)
print(json.dumps(res, indent=1))
(ROOT / "data/generated/pgpe/r2_controls.json").write_text(json.dumps(res, indent=1))
