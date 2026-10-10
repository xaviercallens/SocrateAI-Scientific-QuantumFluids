#!/usr/bin/env python3
"""Chapter 9, figure 1: the wake at t = 50 tau of the deposited run (Kwon & Shin, Zenodo 20068724) and of our Rust reproduction.
Hue = phase of psi (the book's cyclic map), brightness = density^1/2: a hole in the fluid is black.  Top: our field in the whole near wake
(spectral interpolation, 4x finer than the grid).  Bottom: the vortex region at 8x, reference, ours (with the reference's vortices as open rings),
and the density difference ours - reference.  Vortices = plaquettes of non-zero winding of the 0.5 xi grid (counter-clockwise charge).
    nice .venv/bin/python -I book/figures/ch09_wake.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch09_render import *
import ch09_common as C

T = 50.0
pr, po = C.load_ref(T), C.load_ours(T)
cr, co = C.charged(pr), C.charged(po)

fig = plt.figure(figsize=(TEXTW, 4.05))
gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.8], hspace=0.30, wspace=0.12, left=0.075, right=0.995, top=0.985, bottom=0.10)

# ---- (a) the whole near wake, ours
ax = fig.add_subplot(gs[0, :])
xl, yl = (44.0, 136.0), (-20.0, 20.0)
xf, yf, z = C.fourier_zoom(po, xl, yl, up=4)
ax.imshow(hue_density(z), origin="lower", extent=[xl[0], xl[1], yl[0], yl[1]], interpolation="bilinear", aspect="equal")
obstacle_outline(ax)
charge_markers(ax, co, size=22)
style_map(ax, xl, yl, xticks=[60, 80, 100, 120], yticks=[-20, 0, 20], xlabel=False)
panel(ax, "a")
ax.annotate("", xy=(52, 16.0), xytext=(66, 16.0), arrowprops=dict(arrowstyle="-|>", color="white", lw=1.2))
ax.text(59, 17.0, "flow", color="white", ha="center", va="bottom", fontsize=8)
ax.text(100, -12.0, "obstacle\n$V_0=0.9\\,\\mu,\\ \\sigma=20\\,\\xi$", color="white", ha="center", va="center", fontsize=7.3)
C.scale_bar(ax, 120, -17.5, length=10, label=r"$10\,\xi$", color="white")
ax.text(0.008, 0.035, f"ours, $t=50\\,\\tau$: ${len(co)}$ vortices (exact winding)", transform=ax.transAxes, color="white", ha="left", va="bottom", fontsize=8)

# ---- (b,c,d) the vortex region
xl2, yl2 = (76.0, 98.0), (-11.0, 11.0)
xr, yr, zr = C.fourier_zoom(pr, xl2, yl2, up=8)
xo, yo, zo = C.fourier_zoom(po, xl2, yl2, up=8)
axb = fig.add_subplot(gs[1, 0]); axc = fig.add_subplot(gs[1, 1]); axd = fig.add_subplot(gs[1, 2])
for a_, z_ in ((axb, zr), (axc, zo)):
    a_.imshow(hue_density(z_), origin="lower", extent=[xl2[0], xl2[1], yl2[0], yl2[1]], interpolation="bilinear", aspect="equal")
charge_markers(axb, cr, size=24)
charge_markers(axc, co, size=24)
charge_markers(axc, cr, filled=False, size=70, lw=0.9, edge="white", zorder=6)
axc.scatter([], [], s=70, facecolor="none", edgecolor="white", linewidths=0.9, label="reference")
dn = np.abs(zo) ** 2 - np.abs(zr) ** 2
vm = 0.03
im = axd.imshow(dn, origin="lower", extent=[xl2[0], xl2[1], yl2[0], yl2[1]], interpolation="bilinear", aspect="equal", cmap="RdBu_r", vmin=-vm, vmax=vm)
charge_markers(axd, cr, filled=False, size=34, lw=0.8, edge="#333333", zorder=6)
for a_, lab in ((axb, "b"), (axc, "c"), (axd, "d")):
    style_map(a_, xl2, yl2, xticks=[80, 90], yticks=[-10, 0, 10], ylabel=(a_ is axb))
    panel(a_, lab)
    if a_ is not axb: a_.set_yticklabels([])
axb.set_title("reference", fontsize=8.5, pad=3); axc.set_title("ours (rings: reference)", fontsize=8.5, pad=3); axd.set_title(r"$|\psi|^2_{\rm ours}-|\psi|^2_{\rm ref}$", fontsize=8.5, pad=3)
cax = axd.inset_axes([1.04, 0.0, 0.05, 1.0]); cb = fig.colorbar(im, cax=cax); cb.set_ticks([-0.03, 0, 0.03]); cb.set_ticklabels(["-0.03", "0", "0.03"]); cb.ax.tick_params(labelsize=7, length=2)
fig.text(0.5, 0.018, r"$x/\xi$", ha="center", fontsize=10)
for a_ in (axb, axc, axd): a_.set_xlabel("")
save(fig, "ch09_wake")
