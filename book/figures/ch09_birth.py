#!/usr/bin/env python3
"""Chapter 9, figure 4: the birth of the first vortex pair, from the 0.1-tau continuation of OUR t = 20 field (ch09_birth_run.py; it reproduces the Rust t = 25
snapshot to 1e-15).  (a) density along the axis y = 0 at five times; (b) the minimum density of the sub-box (left, log) and the number of charged plaquettes
(right); (c) the largest principal phase step on any edge of the sub-box, in units of pi; (d-f) density (log scale, cubic interpolation) just before, just after
and 0.6 tau after the birth, with the plaquettes of non-zero winding.
    nice .venv/bin/python -I book/figures/ch09_birth.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch09_render import *
import ch09_common as C
from scipy import ndimage
from matplotlib.colors import LogNorm

d = np.load("/mnt/data/xdev-cache/qf-external/ch09/birth_t20_25.npz")
tb, box, bx0, by0 = d["t"], d["box"], int(d["x0"]), int(d["y0"])
xs = C.x[bx0:bx0 + box.shape[2]]; ys = C.y[by0:by0 + box.shape[1]]
jax = int(np.argmin(np.abs(ys)))

def pdm(a, b):
    dd = (b - a + np.pi) % (2 * np.pi) - np.pi
    return np.where(dd == -np.pi, np.pi, dd)
def charges(psi):
    th = np.angle(psi); sx = pdm(th[:, :-1], th[:, 1:]); sy = pdm(th[:-1, :], th[1:, :])
    s = sx[:-1, :] + sy[:, 1:] - sx[1:, :] - sy[:, :-1]
    return np.rint(s / (2 * np.pi)).astype(int), max(np.abs(sx).max(), np.abs(sy).max()) / np.pi
nmin = np.array([np.abs(b).min() ** 2 for b in box]); ncharged = np.array([np.count_nonzero(charges(b)[0]) for b in box]); estep = np.array([charges(b)[1] for b in box])
k_before = int(np.where(ncharged > 0)[0][0]) - 1; t_b0, t_b1 = tb[k_before], tb[k_before + 1]

fig = plt.figure(figsize=(TEXTW, 3.85))
gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.2], hspace=0.62, wspace=0.52, left=0.085, right=0.925, top=0.965, bottom=0.095)

# ---- (a) axis profiles
ax = fig.add_subplot(gs[0, 0])
times = (20.0, 22.0, 23.0, 24.0, 24.2)
cols = ["#9EC1DD", "#6C9CC3", "#3D77A6", BLUE, RED]
for tq, c in zip(times, cols):
    k = int(np.argmin(np.abs(tb - tq)))
    ax.semilogy(xs, np.abs(box[k][jax]) ** 2, color=c, lw=1.2, label=f"{tq:g}")
ax.axvline(86.75, color=GREY, lw=0.6, ls=":"); ax.axvline(100, color=GREY, lw=0.6, ls=":")
ax.text(86.2, 1.6e-4, "pair", rotation=90, fontsize=7.2, color=GREY, ha="right", va="bottom")
ax.text(100.6, 1.6e-4, "centre", rotation=90, fontsize=7.2, color=GREY, ha="left", va="bottom")
ax.set_xlim(66, 112); ax.set_ylim(3e-5, 2.5)
logticks(ax, "y", [1e-4, 1e-3, 1e-2, 1e-1, 1])
ax.set_xlabel(r"$x/\xi$"); ax.set_ylabel(r"$|\psi|^2$ on the axis")
ax.legend(title=r"$t/\tau$", fontsize=6.8, title_fontsize=7.2, loc="lower left", ncol=1, labelspacing=0.2, borderaxespad=0.2, handlelength=1.2)
panel(ax, "a")

# ---- (b) minimum density and charged plaquettes
ax = fig.add_subplot(gs[0, 1])
ax.axvspan(t_b0, t_b1, color="#F2D9C0", lw=0)
ax.semilogy(tb, nmin, color=BLUE, lw=1.4)
ax.set_xlim(20, 25); ax.set_ylim(3e-5, 0.2)
logticks(ax, "y", [1e-4, 1e-3, 1e-2, 1e-1])
ax.set_xlabel(r"$t/\tau$"); ax.set_ylabel(r"$\min|\psi|^2$ in the sub-box", color=BLUE, fontsize=8.8)
ax2 = ax.twinx(); ax2.spines["right"].set_visible(True)
ax2.step(tb, ncharged, where="post", color=ORANGE, lw=1.3); ax2.set_ylim(-0.1, 6.0); ax2.set_yticks([0, 2]); ax2.tick_params(axis="y", colors=ORANGE, labelsize=8)
ax.tick_params(axis="y", colors=BLUE)
ax.text(24.15, 1.5e-1, "charged\nplaquettes", color=ORANGE, fontsize=7.4, ha="right", va="top")
panel(ax, "b")

# ---- (c) the largest phase step
ax = fig.add_subplot(gs[0, 2])
ax.axvspan(t_b0, t_b1, color="#F2D9C0", lw=0)
ax.plot(tb, estep, color=TEAL, lw=1.4)
ax.axhline(1.0, color=RED, lw=0.8, ls="--")
ax.text(20.1, 1.015, r"$\pi$ (the branch cut)", color=RED, fontsize=7.4, va="bottom")
ax.set_xlim(20, 25); ax.set_ylim(0, 1.12)
ax.set_xlabel(r"$t/\tau$"); ax.set_ylabel(r"largest phase step$/\pi$", fontsize=8.8)
panel(ax, "c")

# ---- (d-f) density maps
xl, yl = (83.0, 91.0), (-3.5, 3.5)
i0, i1 = int((xl[0] - xs[0]) / C.DX), int((xl[1] - xs[0]) / C.DX); j0, j1 = int((yl[0] - ys[0]) / C.DX), int((yl[1] - ys[0]) / C.DX)
up = 8
cm = density_cmap()
for col, (tq, lab) in enumerate(((24.2, "d"), (24.3, "e"), (24.9, "f"))):
    a_ = fig.add_subplot(gs[1, col])
    k = int(np.argmin(np.abs(tb - tq))); psi = box[k]
    sub = psi[j0 - 2:j1 + 2, i0 - 2:i1 + 2]
    re = ndimage.zoom(sub.real, up, order=3, mode="nearest"); im = ndimage.zoom(sub.imag, up, order=3, mode="nearest")
    n = (re ** 2 + im ** 2)[2 * up: -2 * up, 2 * up: -2 * up]
    im_ = a_.imshow(n, origin="lower", extent=[xl[0], xl[1], yl[0], yl[1]], cmap=cm, norm=LogNorm(vmin=1e-4, vmax=1.0), interpolation="bilinear", aspect="equal")
    q, _ = charges(psi)
    cen = [(xs[i] + C.DX / 2, ys[j] + C.DX / 2, int(q[j, i])) for j, i in np.argwhere(q != 0)]
    charge_markers(a_, cen, size=40, lw=0.7, edge="black")
    style_map(a_, xl, yl, xticks=[84, 87, 90], yticks=[-2, 0, 2], xlabel=True, ylabel=(col == 0))
    if col > 0: a_.set_yticklabels([])
    a_.set_title(f"$t={tb[k]:.1f}\\,\\tau$", fontsize=8.4, pad=3)
    panel(a_, lab)
cax = fig.add_axes([0.945, 0.095, 0.014, 0.40]); cb = fig.colorbar(im_, cax=cax); cb.ax.tick_params(labelsize=6.8, length=2); cb.set_label(r"$|\psi|^2$", fontsize=8, labelpad=1)
cb.set_ticks([1e-4, 1e-3, 1e-2, 1e-1, 1]); cb.set_ticklabels([r"$10^{-4}$", r"$10^{-3}$", r"$10^{-2}$", r"$10^{-1}$", r"$1$"])
save(fig, "ch09_birth")
