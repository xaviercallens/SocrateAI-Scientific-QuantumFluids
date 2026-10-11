#!/usr/bin/env python3
"""Figures of the companion paper (II). Everything is read from committed result files; the only typed numbers are the
ETD work-precision rows, copied from docs/designs/EXCITON_FLUID_ETD_RESULTS.md (Sec. 2 and 6), marked below.
Usage: companion_figures.py <repo_root> <out_dir>"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.special import k0

ROOT, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
BL, OR, VI, INK, GR, SURF = "#2a78d6", "#eb6834", "#6250d6", "#2b2b2b", "#9a9a98", "#fcfcfb"
plt.rcParams.update({"font.size": 8.5, "axes.edgecolor": GR, "axes.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "xtick.color": INK, "ytick.color": INK, "text.color": INK,
                     "axes.labelcolor": INK, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
                     "grid.color": "#e6e6e3", "grid.linewidth": 0.5, "font.family": "DejaVu Sans",
                     "mathtext.fontset": "dejavusans"})

# ---- data -----------------------------------------------------------------------------------------------------
W = json.load(open(f"{ROOT}/exploration/exciton/results/wigner/analysis.json"))
lam = W["Lambda_min_over_nu"]
Ds = ["1.2", "1.5", "2.0", "3.0", "5.0", "10.0", "20.0", "inf"]
Dx = [1.2, 1.5, 2, 3, 5, 10, 20, 40]
Lmin = [lam[k]["Lambda_min"] for k in Ds]
E = json.load(open(f"{ROOT}/exploration/exciton/edge/results/analysis/summary.json"))
cases = {c["case"]: c for c in E["cases"]}

def Eedge(case):
    c = cases[case]
    return c["e_total"] - c["n"] * c["e_lat"]

def Ugated(r, DoD):          # symmetric gates at +-D/2, layers at -+d/2 (d = 1): Poisson series, period 2D
    D = DoD
    k = np.arange(1, 400)[:, None]
    return (8.0 / D) * ((1 - np.cos(2 * np.pi * k / D)) * k0(2 * np.pi * k * r[None, :] / D)).sum(0)

# ---- cover (4 panels) -------------------------------------------------------------------------------------------
fig, ax = plt.subplots(2, 2, figsize=(7.4, 5.6))
a = ax[0, 0]
r = np.linspace(0.25, 8, 400)
a.plot(r, 2 / r - 2 / np.sqrt(r * r + 1), color=GR, lw=1.4, label="ungated")
for D, c in [(10, BL), (3, OR)]:
    a.plot(r, Ugated(r, D), color=c, lw=1.4, label=f"gated, $D/d={D}$")
a.set_yscale("log"); a.set_xlabel("$r/d$"); a.set_ylabel("$U(r)\\,\\epsilon/e^2$ (units $1/d$)")
a.set_title("(a) gated kernel (machine-checked CM)", fontsize=8, loc="left")
a.legend(frameon=False, fontsize=7.5); a.grid(True)
a = ax[0, 1]
a.plot(Dx, Lmin, "o-", color=BL, lw=1.4, ms=4)
a.axhline(48.7, color=GR, lw=0.8, ls="--"); a.text(1.25, 56, "ungated 48.7", fontsize=7.5, color=GR)
a.set_xscale("log"); a.set_yscale("log"); a.set_xlabel("gate separation $D/d$ (40 = no gates)")
a.set_ylabel("minimum $\\Lambda=d/a_M$")
a.set_title("(b) harmonic crystal threshold", fontsize=8, loc="left"); a.grid(True)
a = ax[1, 0]
Ns = np.array([19, 37, 61, 91])
for ker, c, lab in [("dip", BL, "ungated"), ("g3", OR, "gated $D/d=3$")]:
    for shp, mk in [("square", "o"), ("rect31", "s"), ("tri", "^")]:
        ns = [n for n in Ns if f"{ker}_{shp}_N{n}" in cases]
        y = [Eedge(f"{ker}_{shp}_N{n}") / np.sqrt(n) for n in ns]
        a.plot(ns, y, marker=mk, color=c, lw=0.9, ms=4, alpha=0.9, label=f"{lab}, {shp}" if True else None)
a.set_xlabel("$N$"); a.set_ylabel("$E_{\\rm edge}/\\sqrt{N}$ (hard walls, $\\rho_0=0.5/d^2$)")
a.set_title("(c) edge energy, hard walls (classical)", fontsize=8, loc="left")
a.legend(frameon=False, fontsize=6, ncol=2); a.grid(True)
a = ax[1, 1]
h = np.array([0.2, 0.1, 0.05, 0.025, 0.0125])
etd = np.array([4.7e-5, 2.1e-5, 7.2e-6, 1.6e-6, 2.2e-7])      # ETD_RESULTS Sec. 2, G8, gamma_R=200
krog = np.array([9.1e-6, 1.5e-6, 3.6e-7, 9.2e-8, 1.5e-8])
a.loglog(h, etd, "o-", color=BL, lw=1.4, ms=4, label="ETDRK4 (Cox-Matthews)")
a.loglog(h, krog, "s-", color=OR, lw=1.4, ms=4, label="Krogstad variant")
a.loglog(h, etd[-1] * (h / h[-1]) ** 4, color=GR, ls="--", lw=0.8, label="order 4")
a.loglog(h, etd[-1] * (h / h[-1]) ** 2, color=GR, ls=":", lw=0.8, label="order 2")
a.set_xlabel("$h$"); a.set_ylabel("error at $t=10$"); a.legend(frameon=False, fontsize=7); a.grid(True)
a.set_title("(d) ETDRK4, $\\gamma_R=200$", fontsize=8, loc="left")
from matplotlib.ticker import NullFormatter, ScalarFormatter
for q in (ax[0,1], ax[1,1]):
    q.xaxis.set_minor_formatter(NullFormatter()); q.yaxis.set_minor_formatter(NullFormatter())
ax[0,1].set_xticks([1.2,2,5,10,40]); ax[0,1].set_xticklabels(["1.2","2","5","10","40"])
ax[0,1].set_yticks([50,100,250]); ax[0,1].set_yticklabels(["50","100","250"])
ax[1,1].set_xticks([0.0125,0.025,0.05,0.1,0.2]); ax[1,1].set_xticklabels(["0.0125","0.025","0.05","0.1","0.2"])
fig.tight_layout()
fig.savefig(f"{OUT}/fig_cover.pdf"); fig.savefig(f"{OUT}/fig_cover.png", dpi=170)
plt.close(fig)

# ---- edge detail ----------------------------------------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
for i, (ker, ttl) in enumerate([("dip", "ungated dipole kernel"), ("g3", "gated, $D/d=3$")]):
    a = ax[i]
    for n, c in zip([19, 37, 61, 91], [VI, BL, OR, INK]):
        xs, ys = [], []
        for s, ar in [("square", 1), ("rect32", 1.5), ("rect21", 2), ("rect31", 3)]:
            k = f"{ker}_{s}_N{n}"
            if k in cases:
                xs.append(ar); ys.append(Eedge(k) / np.sqrt(n))
        if xs:
            a.plot(xs, ys, "o-", color=c, ms=4, lw=1.2, label=f"$N={n}$")
    a.set_xlabel("aspect ratio of the rectangle"); a.set_ylabel("$E_{\\rm edge}/\\sqrt{N}$")
    a.set_title(ttl, fontsize=8, loc="left"); a.grid(True); a.legend(frameon=False, fontsize=7)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_edge_aspect.pdf"); fig.savefig(f"{OUT}/fig_edge_aspect.png", dpi=170)
plt.close(fig)

# ---- ETD work-precision (T-g, copied from ETD_RESULTS Sec. 6) -------------------------------------------------
fig, a = plt.subplots(figsize=(3.6, 3.0))
etd_wp = [(5.7e-5, 0.008), (8.8e-6, 0.032), (2.7e-7, 0.12), (2.7e-8, 0.36), (2.2e-9, 0.76), (2.0e-10, 1.8)]
cv_wp = [(1.5e-4, 0.85), (7.8e-6, 0.9), (1.9e-7, 1.45), (4.3e-9, 2.15)]    # midpoints of the quoted wall-time ranges
a.loglog([e for e, _ in etd_wp], [t for _, t in etd_wp], "o-", color=BL, label="ETDRK4")
a.loglog([e for e, _ in cv_wp], [t for _, t in cv_wp], "s-", color=OR, label="CVODE (dense BDF)")
a.set_xlabel("error $E$"); a.set_ylabel("wall time (s), $t=20$, $8\\times8$"); a.legend(frameon=False, fontsize=7); a.grid(True)
a.invert_xaxis()
fig.tight_layout(); fig.savefig(f"{OUT}/fig_etd_wp.pdf"); fig.savefig(f"{OUT}/fig_etd_wp.png", dpi=170)
print("ok", Lmin)
