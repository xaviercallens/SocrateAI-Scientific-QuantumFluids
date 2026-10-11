#!/usr/bin/env python3
"""Figures of paper IV from exploration/exciton/dimlift/results (summary.json from analyse.py + e3 records).
Usage: companion4_figures.py <repo_root> <out_dir>"""
import json, sys, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
BL, OR, VI, INK, GR, SURF = "#2a78d6", "#eb6834", "#6250d6", "#2b2b2b", "#9a9a98", "#fcfcfb"
plt.rcParams.update({"font.size": 8.5, "axes.edgecolor": GR, "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "grid.color": "#e6e6e3", "grid.linewidth": 0.5,
    "font.family": "DejaVu Sans", "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})
R = f"{ROOT}/exploration/exciton/dimlift/results"
S = json.load(open(f"{R}/summary.json"))
cases = [k for k in S["e1"] if S["e1"][k]]
cases = sorted(cases, key=lambda k: (k.split("_")[0] != "dip", k))
lab = [k.replace("_", "-") for k in cases]
fig, ax = plt.subplots(1, 3, figsize=(7.6, 3.5), gridspec_kw={"width_ratios": [1.4, 1.1, 0.9]})
a = ax[0]; x = np.arange(len(cases))
for j, (m, c) in enumerate([("lift1", BL), ("lift2", VI)]):
    y = [-S["e1"][k]["gate"][m]["diff"] for k in cases]      # E_lift - E_direct (positive = lift worse)
    e = [S["e1"][k]["gate"][m]["se"] for k in cases]
    a.errorbar(x + (j - 0.5) * 0.25, y, yerr=e, fmt="o", color=c, ms=3.5, capsize=2, label=f"{m} - direct")
yc = [S["e1"][k]["methods"]["lift1"]["direct_bestofm_mean"] - S["e1"][k]["methods"]["direct"]["meanE"] for k in cases]
a.plot(x, yc, "s", color=OR, ms=4, label="direct best-of-m (equal compute) - direct")
a.axhline(0, color=GR, lw=0.7)
a.set_xticks(x); a.set_xticklabels(lab, fontsize=6, rotation=55, ha="right")
a.set_ylabel("mean final energy minus mean direct")
a.set_title("(a) E1: lifting vs. direct (positive = worse)", fontsize=8, loc="left"); a.legend(frameon=False, fontsize=5.5, loc="lower left"); a.grid(True, axis="y"); a.set_ylim(-0.065, 0.055)
a = ax[1]
y = [S["e2"][k]["dnon6_mean"] if S["e2"][k] else np.nan for k in cases]
e = [S["e2"][k]["dnon6_se"] or 0 if S["e2"][k] else 0 for k in cases]
a.errorbar(x, y, yerr=e, fmt="o", color=BL, capsize=2, ms=4)
a.axhline(0, color=GR, lw=0.7); a.axhline(-2, color=OR, lw=0.8, ls="--")
a.set_xticks(x); a.set_xticklabels(lab, fontsize=6, rotation=55, ha="right")
a.set_ylabel("change in non-6 free nodes (slide - fixed)")
a.set_title("(b) E2: sliding wall", fontsize=8, loc="left"); a.grid(True, axis="y")
a = ax[2]
by = {}
for l in open(f"{R}/e3_mesh3d.jsonl"):
    r = json.loads(l); by.setdefault(r["seed"], {})[r["method"]] = r
d = np.array([by[s]["cm"]["rho_p5"] - by[s]["cvt"]["rho_p5"] for s in by if len(by[s]) == 3])
a.hist(d, bins=12, color=BL, alpha=0.85)
a.axvline(0, color=OR, lw=1)
a.set_xlabel("rho_p5: CM minus CVT")
a.set_ylabel("starts"); a.set_title("(c) E3: 3D periodic sets", fontsize=8, loc="left")
fig.tight_layout(); fig.savefig(f"{OUT}/fig_dimlift.pdf"); fig.savefig(f"{OUT}/fig_dimlift.png", dpi=170)
print(len(cases), len(d), float(d.mean()))
