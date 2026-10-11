#!/usr/bin/env python3
"""Krylov figure for companion paper III from exploration/exciton/krylov/results. Usage: companion3_fig_krylov.py <repo_root> <out_dir>
CVODE reference timings (M=8: 1.40 s, M=16: 90.5 s, rtol 1e-10) are the values listed in summary.json (K-c); typed here."""
import json, sys, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
BL, OR, VI, INK, GR, SURF = "#2a78d6", "#eb6834", "#6250d6", "#2b2b2b", "#9a9a98", "#fcfcfb"
plt.rcParams.update({"font.size": 8.5, "axes.edgecolor": GR, "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "grid.color": "#e6e6e3", "grid.linewidth": 0.5,
    "font.family": "DejaVu Sans", "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})
R = f"{ROOT}/exploration/exciton/krylov/results"
S = json.load(open(f"{R}/summary.json"))
kc = S["K-c"]["kr"]
Ms = sorted(int(m) for m in kc)
cpu = [kc[str(m)]["cpu_median"] for m in Ms]
def trace(name):
    t, n = [], []
    for l in open(f"{R}/{name}"):
        l = l.strip()
        if l.startswith("{") and '"n_center"' in l:
            d = json.loads(l); t.append(d["t"]); n.append(d["n_center"])
    return np.array(t), np.array(n)
fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
a = ax[0]
a.loglog(Ms, cpu, "o-", color=BL, label="Newton--Krylov (SDIRK2)")
a.loglog([8, 16], [1.40, 90.5], "s-", color=OR, label="CVODE dense BDF")
a.loglog(Ms, cpu[0] * (np.array(Ms) / 8.0) ** 2, color=GR, ls="--", lw=0.8, label="$M^2$")
a.loglog(Ms, cpu[0] * (np.array(Ms) / 8.0) ** 3, color=GR, ls=":", lw=0.8, label="$M^3$")
a.set_xticks(Ms); a.set_xticklabels([str(m) for m in Ms]); a.minorticks_off()
a.set_xlabel("grid $M\\times M$"); a.set_ylabel("CPU seconds, $t=20$ (KR rtol $10^{-7}$, CVODE $10^{-10}$)"); a.grid(True)
a.legend(frameon=False, fontsize=7); a.set_title("(a) cost (K-c, transient, one seed)", fontsize=8, loc="left")
a = ax[1]
t5, n5 = trace("ke_Ke_G64a_V0.5_s1.log"); t2, n2 = trace("ke_Ke_G64a_V0.25_s1.log")
a.semilogy(t2, np.maximum(n2, 1e-4), color=BL, label="$V_0=0.25$ (stationary)")
a.semilogy(t5, np.maximum(n5, 1e-4), color=OR, label="$V_0=0.5$ (not converged)")
a.set_xlabel("$t$"); a.set_ylabel("density at gate centre"); a.grid(True); a.legend(frameon=False, fontsize=7)
a.set_title("(b) $64\\times64$ grid, $\\sigma=12$, one seed (every 100 time units)", fontsize=8, loc="left")
fig.tight_layout(); fig.savefig(f"{OUT}/fig_krylov.pdf"); fig.savefig(f"{OUT}/fig_krylov.png", dpi=170)
print(Ms, cpu, len(t5), len(t2))
