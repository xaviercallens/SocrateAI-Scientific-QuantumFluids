#!/usr/bin/env python3
"""EXPLORATORY (not pre-registered): the vacuity ratio V_p = ||f-g||_p / Z_p and the slack S_p for
p in {1, 2, 4, 8} on the seven pairs, H0 only, primal assignment only (no certificate), to see whether
any p makes the Skraba-Turner bound informative on a dense perturbation. The pre-registered round
(wp_stability.py) is p = 1, 2 with certificates; this sweep is labelled exploratory in the paper."""
import json, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.argv = sys.argv[:1]
from wp_stability import load_pairs, gudhi_diagrams, cell_norm, wasserstein_degree, diag_cost, DATA

PS = (1, 2, 4, 8)
out = {}
for name, (f, g, per) in load_pairs().items():
    t0 = time.time()
    df, dg = gudhi_diagrams(f, per), gudhi_diagrams(g, per)
    X, Y = df[0][0], dg[0][0]
    row = {}
    for p in PS:
        B = cell_norm(f, g, per, p)
        r = wasserstein_degree(X, Y, df[0][1], dg[0][1], p, "lp", certify=False)
        W0 = r["cost_p"] ** (1 / p)
        Z = (np.sum(diag_cost(X, p, "lp") ** p)) ** (1 / p) + (np.sum(diag_cost(Y, p, "lp") ** p)) ** (1 / p)
        row[p] = {"B": B, "W0": W0, "Z0": Z, "S": B / W0, "V": B / Z}
    eps = float(np.abs(f - g).max())
    # p = infinity: bottleneck vs sup norm, Z_inf = max persistence/2 over both diagrams (l_inf ground)
    import gudhi
    dB = gudhi.bottleneck_distance(X, Y)
    Zinf = max((X[:, 1] - X[:, 0]).max(), (Y[:, 1] - Y[:, 0]).max()) / 2
    row["inf"] = {"B": eps, "W0": dB, "Z0": Zinf, "S": eps / dB, "V": eps / Zinf}
    out[name] = row
    print(name, " | ".join(f"p={p}: S={row[p]['S']:.3g} V={row[p]['V']:.3g}" for p in list(PS) + ["inf"]), f"{time.time()-t0:.0f}s", flush=True)
Path(DATA / "wp_stability_psweep.json").write_text(json.dumps(out, indent=1, default=float))
