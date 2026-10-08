#!/usr/bin/env python3
"""Figures of paper/friction_law.tex, all from data on disk.
    .venv/bin/python exploration/pgpe/analyze_friction_law.py     (writes fl/friction_law_results.json)
    .venv/bin/python paper/make_figures_friction_law.py           -> paper/figures/fl_*.pdf"""
from __future__ import annotations
import glob, json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]; TR = ROOT / "data/generated/pgpe/transport"; FL = TR / "fl"; FIG = ROOT / "paper/figures"; FIG.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "exploration/pgpe"))
from analyze_transport import load, pair_separations
plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "legend.fontsize": 7.5, "figure.dpi": 150})
CUT = {2.09: ("#2a7f4f", "o", r"$k_c=2\pi/3$"), 3.14: ("#1f5fa8", "s", r"$k_c=\pi$"), 6.28: ("#b23a2e", "D", r"$k_c=2\pi$")}
res = json.loads((FL / "friction_law_results.json").read_text()); arms = res["arms"]
key = lambda a: round(a["kcut"], 2)

# ---- Fig. 1: alpha against T (collapse) and against rho_n (no collapse) -----------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.9))
Tx = np.linspace(0, 0.25, 10); a = res["H_T"]["a"]
ax[0].fill_between(Tx, (a - res["H_T"]["se"]) * Tx, (a + res["H_T"]["se"]) * Tx, color="#bbbbbb", alpha=0.5, lw=0)
ax[0].plot(Tx, a * Tx, "-", color="#666666", lw=1, label=rf"$\alpha={a:.3f}\,T$")
for ar in arms:
    c, m, lab = CUT[key(ar)]
    ax[0].errorbar(ar["T"], ar["alpha_energy"], ar["alpha_energy_se"], fmt=m, color=c, mfc=c if ar["n_runs"] >= 6 else "none", label=lab if ar is next(x for x in arms if key(x) == key(ar)) else None)
ax[0].set_xlabel(r"temperature $T$"); ax[0].set_ylabel(r"friction $\alpha$ (energy estimator)"); ax[0].set_xlim(0, 0.25); ax[0].set_ylim(0, 0.018); ax[0].legend(frameon=False, loc="upper left")
for ar in arms:
    c, m, lab = CUT[key(ar)]
    ax[1].errorbar(ar["rho_n"], ar["alpha_energy"], ar["alpha_energy_se"], fmt=m, color=c, mfc=c if ar["n_runs"] >= 6 else "none")
xs = np.linspace(0, 0.085, 10)
for k, (c, m, lab) in CUT.items():
    ck = res["FL2"]["c_by_cutoff"][str(k)]["c"]; ax[1].plot(xs, ck * xs, "-", color=c, lw=0.9, alpha=0.8)
    xl = min(0.0835, 0.0165 / ck); ax[1].annotate(rf"$c={ck:.2f}$", (xl, ck * xl), fontsize=7, color=c, ha="right", va="bottom", xytext=(-2, 3), textcoords="offset points")
ax[1].set_xlabel(r"normal fraction $\rho_n/\rho$ of the base state"); ax[1].set_ylabel(r"friction $\alpha$"); ax[1].set_xlim(0, 0.085); ax[1].set_ylim(0, 0.018)
fig.tight_layout(); fig.savefig(FIG / "fl_fig1_alpha_vs_T_and_rho.pdf"); plt.close(fig)

# ---- Fig. 2: the lever (rho_n/T against T per cutoff) and the coefficient c against k_c ------------------------------------
bases = {2.09: sorted(glob.glob(str(FL / "base_k2.094_N128_e0.*.json"))), 6.28: sorted(glob.glob(str(FL / "base_k6.283_N256_e*.json")))}
pi_pts = [(0.115, 0.027), (0.2198, 0.0534), (0.353, 0.0945)]
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
for k, fs in bases.items():
    pts = sorted((json.loads(Path(f).read_text())["T"], 1 - json.loads(Path(f).read_text())["ns_over_n"], json.loads(Path(f).read_text())["n_v"]) for f in fs)
    pts = [p for p in pts]
    c, m, lab = CUT[k]
    ax[0].plot([p[0] for p in pts if p[2] < 0.5], [p[1] for p in pts if p[2] < 0.5], m + "-", color=c, lw=0.8, ms=4, label=lab)
    ax[0].plot([p[0] for p in pts if p[2] >= 0.5], [p[1] for p in pts if p[2] >= 0.5], m, color=c, mfc="none", ms=4)
ax[0].plot([p[0] for p in pi_pts], [p[1] for p in pi_pts], "s-", color=CUT[3.14][0], lw=0.8, ms=4, label=CUT[3.14][2])
ax[0].set_xlabel(r"temperature $T$"); ax[0].set_ylabel(r"normal fraction $\rho_n/\rho$"); ax[0].legend(frameon=False, loc="upper left"); ax[0].set_xlim(0.05, 0.4)
ks = sorted(float(k) for k in res["FL2"]["c_by_cutoff"]); cs = [res["FL2"]["c_by_cutoff"][str(k)] for k in ks]
ax[1].errorbar(ks, [x["c"] for x in cs], [x["se"] for x in cs], fmt="o", color="k", zorder=3, label=r"measured $c=\alpha/(\rho_n/\rho)$")
kk = np.linspace(1.8, 6.8, 20); ax[1].plot(kk, cs[1]["c"] * kk / 3.14, "--", color="#d9822b", lw=1, label=r"Born rival, $c\propto k_c$")
ax[1].plot(kk, np.full_like(kk, cs[1]["c"]), ":", color="#666666", lw=1, label=r"registered: $c$ cutoff-independent")
ax[1].set_xlabel(r"cutoff $k_c\xi$"); ax[1].set_ylabel(r"$c=\alpha/(\rho_n/\rho)$"); ax[1].set_ylim(0, 0.75); ax[1].legend(frameon=False, loc="upper right")
fig.tight_layout(); fig.savefig(FIG / "fl_fig2_lever_and_coefficient.pdf"); plt.close(fig)

# ---- Fig. 3: known answers: T = 0 pair at the three cutoffs ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.8, 2.7))
for f, lab, (c, m, _) in ((TR / "G1_T0_antiparallel_d10.npz", r"$k_c=\pi$", CUT[3.14]), (FL / "FL_third_T0_antiparallel_d10.npz", r"$k_c=2\pi/3$", CUT[2.09]), (FL / "FL_fine_T0_antiparallel_d10.npz", r"$k_c=2\pi$", CUT[6.28])):
    t, R, q, z, meta = load(f); d = pair_separations(R, q, 64.0)[0]; ax.plot(t, d, "-", color=c, lw=1, label=lab)
ax.set_xlabel("time"); ax.set_ylabel(r"pair separation $d$ ($T=0$)"); ax.legend(frameon=False, loc="upper left"); ax.set_ylim(9.4, 11.2)
fig.tight_layout(); fig.savefig(FIG / "fl_fig3_T0_known_answer.pdf"); plt.close(fig)

# ---- Fig. 4: separation of the thermal pairs with the energy-estimator decay, one example per cutoff --------------------------
fig, ax = plt.subplots(figsize=(3.8, 2.7))
for tag, base, lab, (c, m, _) in (("third", "base_k2.094_N128_e0.60", r"$2\pi/3$, $T=0.216$", CUT[2.09]), ("fine", "base_k6.283_N256_e0.95", r"$2\pi$, $T=0.127$", CUT[6.28])):
    for f in sorted(glob.glob(str(FL / f"FL_{tag}_{base}_antiparallel_d12_s*.npz")))[:3]:
        t, R, q, z, meta = load(f); d = pair_separations(R, q, 64.0)[0]; ok = np.isfinite(d) & (d < 14)
        ax.plot(t[ok], d[ok] ** 2, "-", color=c, lw=0.7, alpha=0.8, label=lab if f.endswith("s1.npz") else None)
ax.set_xlabel("time"); ax.set_ylabel(r"$d^2$ of the pair ($d_0=12$)"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(FIG / "fl_fig4_pair_decay.pdf"); plt.close(fig)
print("figures written:", sorted(p.name for p in FIG.glob("fl_*.pdf")))
