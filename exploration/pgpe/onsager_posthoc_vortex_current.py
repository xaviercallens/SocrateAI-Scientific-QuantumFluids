#!/usr/bin/env python3
"""POST HOC (after PGPE_ONSAGER_PREREG.md's verdicts): how much of each run's transverse current R_T is the flow of
its point vortices? Parameter-free: |J_T(k)|^2 = n^2 (2 pi)^2 |rho_q(k)|^2 / k^2 with n = 1 (the mean density),
rho_q(k) = sum_j q_j exp(-i k.r_j), on the same shells |k| = 1, sqrt2, 2 (x 2pi/L) as observables.current_correlators,
normalised as R_T = J_T / (T L^2). Also counts 'free' vortices: those whose nearest opposite-sign vortex is farther
than r_f = 4 (8 grid cells; core size ~1). -> data/generated/pgpe/onsager_posthoc.json"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_r3 import whole_from_blocks

ROOT = Path(__file__).resolve().parents[2]; R3 = ROOT / "data/generated/pgpe/r3"
RUNS = json.loads((ROOT / "data/generated/pgpe/onsager_clusters.json").read_text())["runs"]
SHELLS = [(1, 0), (0, 1), (1, 1), (1, -1), (2, 0), (0, 2)]          # one of each +-k pair; |rho(-k)| = |rho(k)|
R_F = 4.0


def vortex_RT(pos, q, L, T):
    vals = {}
    for m in SHELLS:
        k = 2 * np.pi / L * np.array(m, float); k2 = (k ** 2).sum()
        rho2 = abs(np.sum(q * np.exp(-1j * pos @ k))) ** 2
        vals.setdefault(round(np.sqrt(m[0] ** 2 + m[1] ** 2), 4), []).append((2 * np.pi) ** 2 * rho2 / k2)
    return np.mean([np.mean(v) for v in vals.values()]) / (T * L ** 2)


def n_free(pos, q, L):
    d = pos[:, None, :] - pos[None, :, :]; d -= L * np.round(d / L)
    r = np.sqrt((d ** 2).sum(-1)); r[q[:, None] == q[None, :]] = np.inf
    return int(np.sum(r.min(axis=1) > R_F))


out = []
for run in RUNS:
    d = json.loads((R3 / f"{run['name']}.json").read_text()); w = whole_from_blocks(d); L = run["L"]
    z = np.load(R3 / f"{run['name']}_samples.npz", allow_pickle=True)
    rt = float(np.mean([vortex_RT(p, qq, L, w["T"]) for p, qq in zip(z["pos"], z["q"])]))
    nf = float(np.mean([n_free(p, qq, L) for p, qq in zip(z["pos"][::5], z["q"][::5])]))
    rec = {"part": run["part"], "name": run["name"], "class": run["class"], "R_T": w["R_T"], "R_L": w["R_L"], "R_T_vortex": rt, "n_free": nf, "n_v": run["n_v"]}
    out.append(rec); print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in rec.items()})
x = np.array([r["R_T_vortex"] for r in out]); y = np.array([r["R_T"] for r in out])
res = {"runs": out, "pearson_RT_vs_vortex": float(np.corrcoef(x, y)[0, 1]),
       "spearman_RT_vs_vortex": float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1])}
(ROOT / "data/generated/pgpe/onsager_posthoc.json").write_text(json.dumps(res, indent=1))
print({k: v for k, v in res.items() if k != "runs"})
