#!/usr/bin/env python3
"""Field-level figures for paper/vortex_transport.tex v2 (peer review 1, item A; style of the Nature Physics
mixed-phase-space paper: density/phase maps, trajectory portraits, a phase portrait of the stalled pair).
Short dedicated runs (minutes): nothing here enters a pre-registered verdict.
    .venv/bin/python paper/make_field_maps_vortex_transport.py -> paper/figures/vt_fig0_fields.pdf, vt_fig6_portrait.pdf"""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[1]; FIG = ROOT / "paper/figures"; T = ROOT / "data/generated/pgpe/transport"
sys.path.insert(0, str(ROOT / "exploration/pgpe"))
from pgpe import PGPE
from round2 import imprint
from vortex_transport import imprint_v2, detect
from transport_estimators import antiparallel
from analyze_transport import load, pair_separations
plt.rcParams.update({"font.size": 8, "axes.labelsize": 8, "figure.dpi": 150})

s = PGPE(N=128, L=64.0); L = s.L; x = np.arange(s.N) * s.dx
# ---- panel a/b: sound launched by the old and the corrected imprint (T = 0, single pair d = 10), t = 20 ---------------
c0 = np.zeros((128, 128), complex); c0[0, 0] = 128 ** 2
pos = np.array([[32.13 + 5, 32.31], [32.13 - 5, 32.31]]); q = np.array([1, -1])
maps = {}
for lab, fn in (("old imprint", imprint), ("corrected imprint", imprint_v2)):
    c = s.run(fn(s, c0, pos, q), 20.0); maps[lab] = np.abs(s.psi(c)) ** 2 - 1.0
# ---- panel c/d: thermal state, two antiparallel pairs, density + phase with the tracked trajectories over 300 units ----
cb = np.load(ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000_final.npy"); rng = np.random.default_rng(3)
pa, qa = antiparallel(L, 10.0, rng); c = imprint_v2(s, cb, pa, qa); last = pa.copy(); traj = [pa.copy()]
rho0 = np.abs(s.psi(c)) ** 2; th0 = np.angle(s.psi(c))
for k in range(300):
    c = s.run(c, 1.0); dp, dq = detect(s, c); cur = last.copy()
    for i in range(4):
        cand = np.nonzero(dq == qa[i])[0]; d = dp[cand] - last[i]; d -= L * np.round(d / L); j = int(np.argmin(np.hypot(d[:, 0], d[:, 1])))
        if np.hypot(*d[j]) <= 3.0: cur[i] = dp[cand[j]]
    traj.append(cur.copy()); last = cur
traj = np.array(traj); rho1 = np.abs(s.psi(c)) ** 2; th1 = np.angle(s.psi(c))

fig, ax = plt.subplots(2, 3, figsize=(7.2, 4.6))
nrm = TwoSlopeNorm(vcenter=0.0, vmin=-0.08, vmax=0.08)
for a, lab in zip(ax[0, :2], maps):
    im = a.imshow(maps[lab].T, origin="lower", extent=[0, L, 0, L], cmap="RdBu_r", norm=nrm); a.set_title(rf"$T=0$, {lab}: $\rho-1$ at $t=20$", fontsize=8)
    a.plot(pos[:, 0], pos[:, 1], "k.", ms=3)
fig.colorbar(im, ax=ax[0, :2], fraction=0.025, pad=0.02, label=r"$\rho-1$")
a = ax[0, 2]; a.imshow(rho0.T, origin="lower", extent=[0, L, 0, L], cmap="viridis", vmin=0, vmax=1.4); a.set_title(r"thermal state ($T/T_{\rm BKT}=0.14$), $\rho$ at $t=0$", fontsize=8)
a.plot(pa[qa > 0, 0], pa[qa > 0, 1], "o", mfc="none", mec="w", ms=5); a.plot(pa[qa < 0, 0], pa[qa < 0, 1], "s", mfc="none", mec="w", ms=5)
a = ax[1, 0]; a.imshow(th0.T, origin="lower", extent=[0, L, 0, L], cmap="twilight"); a.set_title(r"phase at $t=0$", fontsize=8)
a = ax[1, 1]; a.imshow(rho1.T, origin="lower", extent=[0, L, 0, L], cmap="viridis", vmin=0, vmax=1.4); a.set_title(r"$\rho$ at $t=300$ with the tracked paths", fontsize=8)
for i in range(4):
    u = traj[:, i].copy(); jump = np.hypot(*np.diff(u, axis=0).T) > L / 2; u[1:][jump] = np.nan
    a.plot(u[:, 0], u[:, 1], "-", color="w" if qa[i] > 0 else "orange", lw=0.8)
a = ax[1, 2]; a.imshow(th1.T, origin="lower", extent=[0, L, 0, L], cmap="twilight"); a.set_title(r"phase at $t=300$", fontsize=8)
for a in ax.ravel():
    a.set_xticks([0, 32, 64]); a.set_yticks([0, 32, 64]); a.set_xlabel(r"$x/\xi$"); a.set_ylabel(r"$y/\xi$")
fig.tight_layout(); fig.savefig(FIG / "vt_fig0_fields.pdf"); plt.close(fig)

# ---- phase portrait of the stalled single pairs: separation against phonon-band momentum, coloured by time -----------
fig, ax = plt.subplots(1, 2, figsize=(7.0, 3.0))
sm = lambda y, w=50: np.convolve(y, np.ones(w) / w, mode="same")
for k, sd in enumerate((1, 2)):
    t, R, qq, z, meta = load(T / f"W1_e0.60_dipole_d12_s{sd}.npz"); d = pair_separations(R, qq, L)[0]
    P0 = z["P"][0] / np.hypot(*z["P"][0]); ph = sm(z["P_hi"] @ P0); dd = sm(d)
    sc = ax[k].scatter(dd[60:-60], ph[60:-60], c=t[60:-60], s=2, cmap="plasma")
    dgrid = np.linspace(7, 12.5, 50); ax[k].plot(dgrid, 2 * np.pi * 0.973 * (d[:20].mean() - dgrid) + ph[60:80].mean(), "k--", lw=0.8, label=r"$P_{|k|>1}=2\pi\rho_s(d_0-d)$")
    ax[k].axvline(10.2, color="grey", ls=":", lw=0.8); ax[k].set_xlabel(r"pair separation $d$"); ax[k].set_ylabel(r"phonon-band momentum $P_{|k|>1}$"); ax[k].set_title(f"single pair, run {sd}", fontsize=8); ax[k].legend(frameon=False, fontsize=7)
fig.colorbar(sc, ax=ax, fraction=0.02, pad=0.02, label="time")
fig.savefig(FIG / "vt_fig6_portrait.pdf", bbox_inches="tight"); plt.close(fig)
print("written vt_fig0_fields.pdf, vt_fig6_portrait.pdf")
