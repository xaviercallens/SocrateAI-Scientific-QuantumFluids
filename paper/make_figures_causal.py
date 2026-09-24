#!/usr/bin/env python3
"""Figures for causal_topology.tex from data/generated/pgpe/r2/*.json (round 2, Part I: arms V / P / 0 per base).
Run: ../.venv/bin/python make_figures_causal.py  -> figures/causal_intervention.pdf"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
R2 = ROOT / "data/generated/pgpe/r2"
OUT = Path(__file__).resolve().parent / "figures"; OUT.mkdir(exist_ok=True)
BASES = ["e0.60_s11_t4000", "e0.90_s11_t4000", "e0.90_s12_t4000"]
ARMS = {"V": ("vortices", "#b2182b"), "P": ("phonons", "#2166ac"), "0": ("untouched", "#4d4d4d")}
PANELS = [("cond", "condensate fraction"), ("T", "thermometer $T$"), ("Q", "dipole matching $Q$"), ("n_v", r"$\langle N_v\rangle$")]

fig, axes = plt.subplots(len(PANELS), len(BASES), figsize=(11, 9), sharex=True)
for j, base in enumerate(BASES):
    for arm, (label, color) in ARMS.items():
        f = R2 / f"I_{base}_{arm}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        t = [b["t0"] + 50 for b in d["blocks"]]
        for i, (key, _) in enumerate(PANELS):
            axes[i, j].plot(t, [b[key] for b in d["blocks"]], "-o", ms=3, color=color, label=label)
    axes[0, j].set_title(base.replace("_t4000", "").replace("_", " "))
    axes[-1, j].set_xlabel("$t$ (block centre)")
    for i, (_, ylab) in enumerate(PANELS):
        axes[i, j].axvspan(100, 300, color="0.9", zorder=0)
        if j == 0:
            axes[i, j].set_ylabel(ylab)
axes[0, 0].legend(frameon=False, fontsize=8)
fig.suptitle("Round 2, Part I: the same energy as vortices (V) or phonons (P); shaded = pre-registered window", fontsize=10)
fig.tight_layout()
fig.savefig(OUT / "causal_intervention.pdf")
print("wrote", OUT / "causal_intervention.pdf")
