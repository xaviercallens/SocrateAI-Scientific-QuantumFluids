#!/usr/bin/env python3
"""Chapter 9, figure 5: the flow is locally supersonic long before the first vortex.
(a) log10 of the local Mach number M = |grad(theta) - v e_x| / sqrt(n) of OUR field at t = 20 tau (colour), with the M = 1 contour of ours (black) and of the deposited field (white, dashed);
(b) density and local sonic density j^(2/3) (j = n|u| the local flux, so that M > 1 exactly where n < j^(2/3): Ch09FlowPast.supersonic_iff) along the axis y = 0 at t = 20;
(c) the one-dimensional picture of Ch09FlowPast.bernoulli_min / barrier_height_bound: Bernoulli's function j^2/(2n^2) + n of a steady channel flow of flux j = 0.55, and the levels 1 + j^2/2 - V it must equal.
    nice .venv/bin/python -I book/figures/ch09_mach.py
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch09_render import *
import ch09_common as C
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

pr, po = C.load_ref(20.0), C.load_ours(20.0)
Mr, uxr, uyr, nr = C.mach(pr); Mo, uxo, uyo, no = C.mach(po)
R = json.load(open(Path(__file__).resolve().parent / "ch09_numbers.json"))

fig = plt.figure(figsize=(TEXTW, 4.0))
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.28], hspace=0.50, wspace=0.34, left=0.075, right=0.985, top=0.97, bottom=0.175)

# ---- (a) Mach map
ax = fig.add_subplot(gs[:, 0])
xl, yl = (68.0, 128.0), (-44.0, 44.0)
ix0, ix1 = int((xl[0] + 250) / C.DX), int((xl[1] + 250) / C.DX); iy0, iy1 = int((yl[0] + 125) / C.DX), int((yl[1] + 125) / C.DX)
cm = LinearSegmentedColormap.from_list("qfmach", [BLUE, "#6C9CC3", "#CFE0EE", PAPER, "#F0C69A", ORANGE, RED, "#4A1710"], N=256)
im = ax.imshow(np.log10(Mo[iy0:iy1, ix0:ix1]), origin="lower", extent=[xl[0], xl[1], yl[0], yl[1]], cmap=cm, norm=TwoSlopeNorm(vcenter=0.0, vmin=-1.0, vmax=0.85), interpolation="bilinear", aspect="equal")
X, Y = C.XX[iy0:iy1, ix0:ix1], C.YY[iy0:iy1, ix0:ix1]
ax.contour(X, Y, Mo[iy0:iy1, ix0:ix1], levels=[1.0], colors="black", linewidths=1.2)
ax.contour(X, Y, Mr[iy0:iy1, ix0:ix1], levels=[1.0], colors="white", linewidths=0.9, linestyles=[(0, (2.5, 2))])
obstacle_outline(ax, color=GREY, lw=0.7)
ax.plot([86.75], [0.0], marker="*", ms=8.5, color="white", mec="black", mew=0.7, zorder=6)
ax.annotate("first pair\n$t=24.25\\,\\tau$", xy=(86.75, 0), xytext=(76.0, 22), fontsize=7.6, ha="center", arrowprops=dict(arrowstyle="-", color="black", lw=0.6))
ax.annotate("", xy=(72, -38), xytext=(84, -38), arrowprops=dict(arrowstyle="-|>", color="black", lw=1.0)); ax.text(78, -41.0, "flow", ha="center", va="center", fontsize=7.8)
ax.text(100, -17.2, "obstacle", fontsize=7.4, color=GREY, ha="center")
style_map(ax, xl, yl, xticks=[80, 100, 120], yticks=[-40, -20, 0, 20, 40])
cax = fig.add_axes([0.095, 0.062, 0.34, 0.022]); cb = fig.colorbar(im, cax=cax, orientation="horizontal"); cb.set_ticks([-1, -0.5, 0, 0.5]); cb.set_ticklabels(["0.1", "0.3", "1", "3"]); cb.ax.tick_params(labelsize=7, length=2)
cb.set_label("local Mach number $M$", fontsize=7.8, labelpad=1)
ax.text(0.02, 0.985, "ours, $t=20\\,\\tau$\nblack: $M=1$ (ours), white: $M=1$ (deposited)", transform=ax.transAxes, fontsize=6.9, va="top", ha="left")
panel(ax, "a")

# ---- (b) axis profile
ax = fig.add_subplot(gs[0, 1])
jy = int(np.argmin(np.abs(C.y))); xa = C.x
n_ax = no[jy]; j_ax = n_ax * np.hypot(uxo[jy], uyo[jy]); s_loc = j_ax ** (2 / 3)
sel = (xa >= 66) & (xa <= 116)
ax.fill_between(xa[sel], n_ax[sel], s_loc[sel], where=(n_ax[sel] < s_loc[sel]), color="#F0C69A", lw=0, label="$n<j^{2/3}$: supersonic")
ax.plot(xa[sel], n_ax[sel], color=BLUE, lw=1.6, label="density $n$")
ax.plot(xa[sel], s_loc[sel], color=ORANGE, lw=1.3, label="local $j^{2/3}$, $j=n|u|$")
ax.axhline(0.55 ** (2 / 3), color=GREY, lw=0.8, ls="--"); ax.text(66.8, 0.55 ** (2 / 3) + 0.02, "$0.55^{2/3}$", fontsize=7.4, color=GREY, va="bottom")
ax.axvline(86.75, color=GREY, lw=0.6, ls=":"); ax.axvline(100, color=GREY, lw=0.6, ls=":")
ax.text(86.2, 1.13, "pair", rotation=90, fontsize=7.0, color=GREY, ha="right", va="top")
ax.text(100.6, 1.13, "centre", rotation=90, fontsize=7.0, color=GREY, ha="left", va="top")
ax.set_xlim(66, 116); ax.set_ylim(0, 1.15)
ax.set_xlabel(r"$x/\xi$ (on the axis $y=0$)"); ax.set_ylabel("density")
ax.legend(loc="lower left", fontsize=7.0, bbox_to_anchor=(0.0, 0.0), handlelength=1.4, labelspacing=0.25)
panel(ax, "b")

# ---- (c) hydraulics of a channel (Lean: bernoulli_min, barrier_height_bound)
ax = fig.add_subplot(gs[1, 1])
j = C.VFLOW; s = j ** (2 / 3); Vc = (1 - s) ** 2 * (s + 2) / 2
nn = np.linspace(0.07, 1.3, 600); f = j ** 2 / (2 * nn ** 2) + nn
ax.plot(nn[nn >= s], f[nn >= s], color=BLUE, lw=1.6, label="subsonic ($n>s$)")
ax.plot(nn[nn <= s], f[nn <= s], color=ORANGE, lw=1.6, label="supersonic ($n<s$)")
B = 1 + j ** 2 / 2
for V, col, ls_, lab in ((0.0, GREY, "-", r"$V=0$ (upstream)"), (Vc, RED, "--", rf"$V=V_c={Vc:.2f}$"), (C.V0, TEAL, "-", rf"$V=V_0={C.V0}$")):
    ax.axhline(B - V, color=col, lw=0.9, ls=ls_)
    if abs(V - Vc) < 1e-9: ax.text(1.29, B - V - 0.07, lab, color=col, fontsize=7.2, ha="right", va="top")
    elif V == 0.0: ax.text(0.02, B - V + 0.05, lab, color=col, fontsize=7.2, ha="left", va="bottom")
    else: ax.text(1.29, B - V + 0.05, lab, color=col, fontsize=7.2, ha="right", va="bottom")
ax.plot([s], [1.5 * s], "o", color=RED, ms=4.5, zorder=5); ax.annotate("sonic point $n=s=j^{2/3}$", xy=(s, 1.5 * s), xytext=(0.80, 1.85), fontsize=7.2, color=RED, ha="center", arrowprops=dict(arrowstyle="-", color=RED, lw=0.6))
ax.plot([1.0], [B], "s", color=GREY, ms=3.8, zorder=5)
ax.text(0.42, 0.62, "no steady state\nover a barrier $V_0>V_c$", fontsize=7.4, color=TEAL, ha="center", va="center")
ax.set_xlim(0.0, 1.32); ax.set_ylim(0, 3.1)
ax.set_xlabel("density $n$ ($j=0.55$)"); ax.set_ylabel(r"$j^2/(2n^2)+n$")
ax.legend(loc="upper right", fontsize=7.0, handlelength=1.4, labelspacing=0.25, bbox_to_anchor=(1.0, 1.0))
panel(ax, "c")
save(fig, "ch09_mach")
