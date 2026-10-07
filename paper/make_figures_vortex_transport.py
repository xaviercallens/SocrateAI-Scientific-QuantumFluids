#!/usr/bin/env python3
"""Figures of paper/vortex_transport.tex (peer review 1, item A), all from data on disk.
    .venv/bin/python paper/make_figures_vortex_transport.py   -> paper/figures/vt_*.pdf"""
from __future__ import annotations
import json, sys, glob
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]; T = ROOT / "data/generated/pgpe/transport"; FIG = ROOT / "paper/figures"; FIG.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "exploration/pgpe"))
plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8, "figure.dpi": 150})
C = {"blue": "#1f5fa8", "red": "#b23a2e", "green": "#2a7f4f", "grey": "#666666", "orange": "#d9822b"}

est = json.loads((T / "production_estimates.json").read_text())
temps = [("e0.60", 0.14), ("e0.70", 0.27), ("e0.80", 0.43)]

# ---- Fig. 1: alpha and alpha' against rho_n/rho ---------------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
rn = np.array([est[k]["rho_n"] for k, _ in temps]); al = np.array([est[k]["alpha_energy"] for k, _ in temps]); ale = np.array([est[k]["alpha_energy_se"] for k, _ in temps])
alr = np.array([est[k]["alpha_regression"] for k, _ in temps]); alre = np.array([est[k]["alpha_regression_se"] for k, _ in temps])
ax[0].errorbar(rn, al, ale, fmt="o", color=C["blue"], label=r"energy estimator")
ax[0].errorbar(rn * 1.03, alr, alre, fmt="s", mfc="none", color=C["green"], label=r"regression")
x = np.linspace(0, 0.11, 10); ax[0].plot(x, 0.24 * x, "--", color=C["grey"], lw=1, label=r"$0.24\,\rho_n/\rho$")
ax[0].axhline(4.1e-4, color=C["red"], lw=0.8, ls=":", label=r"$T=0$ floor")
ax[0].set_xlabel(r"$\rho_n/\rho$"); ax[0].set_ylabel(r"friction $\alpha$"); ax[0].set_xlim(0, 0.11); ax[0].set_ylim(0, 0.04); ax[0].legend(loc="upper left", frameon=False)
for (k, tt), xx, yy in zip(temps, rn, al):
    ax[0].annotate(rf"$T/T_{{\rm BKT}}={tt}$", (xx, yy), textcoords="offset points", xytext=(6, -12), fontsize=7, color=C["grey"])
raw = [(0.0, 1 - 0.9986, 0.0015)] + [(est[k]["rho_n"], 1 - est[k]["one_minus_alpha_prime"], est[k]["one_minus_alpha_prime_se"]) for k, _ in temps]
corr = [(0.027, -0.0060, 0.0015), (0.053, -0.0112, 0.0031), (0.094, -0.0055, 0.0106)]           # after the T = 0 pair-size baseline (CLAIM-082)
ax[1].errorbar([r[0] for r in raw], [r[1] for r in raw], [r[2] for r in raw], fmt="o", color=C["blue"], label=r"raw (box frame)")
ax[1].errorbar([r[0] * 1.03 for r in corr], [r[1] for r in corr], [r[2] for r in corr], fmt="s", mfc="none", color=C["orange"], label=r"after $T=0$ baseline")
ax[1].plot(x, x, "--", color=C["red"], lw=1, label=r"Iordanskii: $\alpha'=\rho_n/\rho$"); ax[1].axhline(0, color=C["grey"], lw=0.8, label=r"no transverse force")
ax[1].set_xlabel(r"$\rho_n/\rho$"); ax[1].set_ylabel(r"transverse coefficient $\alpha'$"); ax[1].set_xlim(-0.005, 0.11); ax[1].set_ylim(-0.03, 0.11); ax[1].legend(loc="upper left", frameon=False)
fig.tight_layout(); fig.savefig(FIG / "vt_fig1_alpha_alphaprime.pdf"); plt.close(fig)

# ---- Fig. 2: residual mean-square displacement against lag ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.6, 2.9))
lags = np.array([5, 10, 20, 40, 80, 120, 160, 240, 320, 400], float)
g1 = json.loads((T / "G1_result.json").read_text())["estimates"]
for (k, tt), col in zip(temps, (C["blue"], C["green"], C["orange"])):
    ms = np.array(est[k]["msd"], float); ok = np.isfinite(ms)
    ax.loglog(lags[ok], ms[ok], "o-", ms=3, color=col, label=rf"$T/T_{{\rm BKT}}={tt}$, $\gamma={est[k]['msd_exponent']:.2f}$")
ms0 = np.array(g1["msd"], float); ok = np.isfinite(ms0); ax.loglog(lags[ok], ms0[ok], "x-", ms=4, color=C["red"], lw=0.8, label=r"$T=0$ (bounded)")
lg = np.array([20, 400.]); ax.loglog(lg, 0.012 * lg, ":", color=C["grey"], lw=1, label=r"slope 1")
ax.set_xlabel(r"lag $\tau$ (time units)"); ax.set_ylabel(r"$\langle|e|^2\rangle$ (residual MSD)"); ax.legend(frameon=False, loc="upper left")
fig.tight_layout(); fig.savefig(FIG / "vt_fig2_msd.pdf"); plt.close(fig)

# ---- Fig. 3: stalled single pairs against zero-impulse pairs; phonon-band momentum --------------------------------------
from analyze_transport import load, pair_separations
from transport_estimators import min_opposite_distance
sm = lambda y, w=25: np.convolve(y, np.ones(w) / w, mode="same")
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
for sd, col in ((1, C["blue"]), (2, C["green"])):
    t, R, q, z, meta = load(T / f"W1_e0.60_dipole_d12_s{sd}.npz"); d = pair_separations(R, q, 64.0)[0]
    ax[0].plot(t, sm(d), color=col, lw=1.0, label=rf"single pair, run {sd}")
    P0 = z["P"][0] / np.hypot(*z["P"][0]); ph = z["P_hi"] @ P0; lost = 2 * np.pi * 0.973 * (d[:20].mean() - d)
    ax[1].plot(t, sm(ph - ph[:20].mean()), color=col, lw=1.0, label=rf"run {sd}: phonon-band momentum $P_{{|k|>1}}$")
    ax[1].plot(t, sm(lost), color=col, lw=1.0, ls="--", label=rf"run {sd}: impulse shed, $2\pi\rho_s(d_0-d)$")
for f, col in zip(sorted(glob.glob(str(T / "G2_e0.60_antiparallel_d10_s*.npz"))), (C["orange"], C["red"])):
    t, R, q, z, meta = load(f); d = pair_separations(R, q, 64.0)
    close = np.array([min_opposite_distance(np.mod(R[k], 64.0), q, 64.0) < 4.0 for k in range(len(t))]); n_ok = int(np.argmax(close)) if close.any() else len(t)
    for i in range(2):
        grow = np.nonzero(d[i] > 11.0)[0]; n_i = min(n_ok, int(grow[0])) if len(grow) else n_ok      # the original pairing stops being the physical one at the exchange
        ax[0].plot(t[:n_i], sm(d[i])[:n_i], color=col, lw=0.9, alpha=0.9, label=("zero-impulse pairs (two runs, until partner exchange)" if (i == 0 and col == C["orange"]) else None))
# L = 96 controls (W2) and the parameter-free prediction of the wind model with the independently measured alpha
alpha = 0.0062
def w_ode(d0, Lb, rho_n, rho_s, t_end=4000.0, wind=True):
    Cc = 2 * np.pi * rho_s / (rho_n * Lb ** 2); d = d0; out = [d]; dt = 0.5
    for _ in range(int(t_end / dt)):
        d += dt * (-2 * alpha * (1 / d - (Cc * (d0 - d) if wind else 0.0))); out.append(max(d, 0.1))
    return np.arange(0, t_end + dt, dt)[:len(out)], np.array(out)
for f, col in zip(sorted(glob.glob(str(T / "W2_L96_e0.60_dipole_d12_s*.npz"))), (C["grey"], "#9c6b9c", "#5a7d9a", "#8a8a3a")):
    t, R, q, z, meta = load(f); d = pair_separations(R, q, 96.0)[0]
    ax[0].plot(t, sm(d), color=col, lw=0.9, ls="-.", label=(r"single pairs, $L=96$ (controls)" if f.endswith("s1.npz") else None))
tt, pw = w_ode(11.5, 64.0, 0.027, 0.973); ax[0].plot(tt + 120, pw, "k:", lw=1.2, label=r"wind model, $L=64$ (no free parameter)")
tt, pw = w_ode(11.5, 96.0, 0.0293, 0.9707); ax[0].plot(tt + 120, pw, "k--", lw=1.0, label=r"wind model, $L=96$")
tt, pf = w_ode(11.5, 64.0, 0.027, 0.973, wind=False); ax[0].plot(tt + 120, pf, color=C["grey"], ls=":", lw=1.0, label=r"free shrinking $d^2=d_0^2-4\alpha t$")
ax[0].set_xlabel("time"); ax[0].set_ylabel(r"pair separation $d$ (25-unit running mean)"); ax[0].set_ylim(4.5, 13); ax[0].set_xlim(0, 4000); ax[0].legend(frameon=False, loc="lower left", fontsize=6)
ax[1].axhline(0, color="k", lw=0.5); ax[1].set_xlabel("time"); ax[1].set_ylabel("momentum (running mean)"); ax[1].set_xlim(0, 4000); ax[1].legend(frameon=False, fontsize=6.5, loc="upper left")
fig.tight_layout(); fig.savefig(FIG / "vt_fig3_wind.pdf"); plt.close(fig)

# ---- Fig. 4: vortex-charge structure factor plateau against the matched-pair polarisability ---------------------------
prim = json.loads((ROOT / "data/generated/pgpe/dielectric/primary_C4.json").read_text())["runs"]
fig, ax = plt.subplots(figsize=(3.6, 2.9)); shells = [1, 2, 4, 5, 8, 9, 10, 13, 16]; L = 192.0
for (name, v), col in zip(prim.items(), (C["blue"], C["blue"], C["red"], C["green"], C["orange"], C["orange"])):
    k = np.sqrt(np.array(shells)) * 2 * np.pi / L; y = np.array([v["shells"][str(m)]["R_Tv"] for m in shells]) / v["D4_pred_from_matching"]
    ax.plot(k, y, "o-" if not v["box_scale_pair"] else "s--", ms=3, lw=0.8, color=col, label=name.replace("C3_L192_", "").replace("_", " ") + (" (box-scale pair)" if v["box_scale_pair"] else ""))
ax.axhline(1, color=C["grey"], lw=0.8); ax.axhspan(0.7, 1.3, color=C["grey"], alpha=0.1)
ax.set_xlabel(r"$k\xi$"); ax.set_ylabel(r"$\langle|\rho_q|^2\rangle/k^2$ over $\Sigma_{\rm pairs}d^2/2$"); ax.set_ylim(0, 1.6); ax.set_xlim(0, 0.14); ax.legend(frameon=False, fontsize=6.5, loc="upper right")
fig.tight_layout(); fig.savefig(FIG / "vt_fig4_structure_factor.pdf"); plt.close(fig)

# ---- Fig. 5: equilibration of the box-scale charge, two windows -----------------------------------------------------
rows = [("e1.00 s11*", 1.98, 0.07, -0.38, 0.81), ("e1.00 s12", 0.65, 0.08, 0.49, 0.77), ("e1.10 s11*", 3.38, 0.80, -0.96, 0.34), ("e1.10 s12", 0.74, 0.19, 0.41, 0.80), ("e1.20 s11", 0.55, 0.38, 0.56, 0.61), ("e1.20 s12", 0.44, 0.41, 0.73, 0.74)]
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6)); xs = np.arange(len(rows))
ax[0].bar(xs - 0.18, [r[1] for r in rows], 0.36, color=C["red"], label=r"$t\in[6000,7000]$"); ax[0].bar(xs + 0.18, [r[2] for r in rows], 0.36, color=C["blue"], label=r"$t\in[13\,500,14\,500]$")
ax[0].axhline(0.45, color=C["grey"], ls=":", lw=0.8); ax[0].set_yscale("log"); ax[0].set_ylabel(r"vortex transverse response $R_T^{\rm v}(k_1)$"); ax[0].set_xticks(xs); ax[0].set_xticklabels([r[0] for r in rows], rotation=30, fontsize=7); ax[0].legend(frameon=False)
ax[1].bar(xs - 0.18, [r[3] for r in rows], 0.36, color=C["red"]); ax[1].bar(xs + 0.18, [r[4] for r in rows], 0.36, color=C["blue"]); ax[1].axhline(0, color="k", lw=0.6)
ax[1].set_ylabel(r"$n_s/n$ (transverse estimator)"); ax[1].set_xticks(xs); ax[1].set_xticklabels([r[0] for r in rows], rotation=30, fontsize=7)
fig.tight_layout(); fig.savefig(FIG / "vt_fig5_equilibration.pdf"); plt.close(fig)
print("figures written:", sorted(p.name for p in FIG.glob("vt_*.pdf")))
