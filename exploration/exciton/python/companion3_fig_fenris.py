#!/usr/bin/env python3
"""Fenris L6 figure for companion paper III, from exploration/exciton/rust/fenris-gated/results/table_all.csv.
Usage: companion3_fig_fenris.py <repo_root> <out_dir>"""
import csv, sys, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
BL, OR, VI, INK, GR, SURF, GN = "#2a78d6", "#eb6834", "#6250d6", "#2b2b2b", "#9a9a98", "#fcfcfb", "#2d8a5a"
plt.rcParams.update({"font.size": 8.5, "axes.edgecolor": GR, "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "grid.color": "#e6e6e3", "grid.linewidth": 0.5,
    "font.family": "DejaVu Sans", "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})
rows = list(csv.DictReader(open(f"{ROOT}/exploration/exciton/rust/fenris-gated/results/table_all.csv")))
def nn(r): return float(r["n5_mean"]) + float(r["n7_mean"]) + float(r["n_other_mean"])
def kern(r): return r["spec"].split(":")[0]
K = [("ungated", GR, "ungated"), ("gated", BL, "gated"), ("yukawa", OR, "Yukawa")]
prod = [r for r in rows if r["group"] == "wallhalfrsa"]
shapes = sorted({r["shape"] for r in prod}, key=lambda s: np.mean([nn(r) for r in prod if r["shape"] == s]))
fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.4), gridspec_kw={"width_ratios": [1.5, 1]})
a = ax[0]
for i, s in enumerate(shapes):
    for kname, c, lab in K:
        v = [nn(r) for r in prod if r["shape"] == s and kern(r) == kname]
        a.scatter([i + (0.0 if kname == "ungated" else 0.0)] * len(v), v, color=c, s=22 if kname != "gated" else 16,
                  alpha=0.9, marker="o" if kname != "gated" else "s", label=lab if i == 0 else None, zorder=3)
a.set_xticks(range(len(shapes))); a.set_xticklabels(shapes, rotation=40, ha="right")
a.set_ylabel("non-6-coordinated free nodes ($N\\approx100$)")
a.set_title("(a) mean of 24 starts; gated $D/d=3$ and $10$", fontsize=8, loc="left")
a.grid(True, axis="y"); a.legend(frameon=False, fontsize=7)
a = ax[1]
size = [r for r in rows if r["group"] == "size"]
for s, c in [("hexagon", GN), ("square", BL), ("disc", VI)]:
    y100 = np.mean([nn(r) for r in prod if r["shape"] == s and kern(r) == "ungated"])
    y200 = np.mean([nn(r) for r in size if r["shape"] == s and kern(r) == "ungated"])
    a.plot([100, 200], [y100, y200], "o-", color=c, label=s)
a.set_xlabel("$N_{\\rm free}$"); a.set_ylabel("non-6 free nodes, ungated")
a.set_title("(b) size series", fontsize=8, loc="left"); a.grid(True); a.legend(frameon=False, fontsize=7)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_fenris.pdf"); fig.savefig(f"{OUT}/fig_fenris.png", dpi=170)
