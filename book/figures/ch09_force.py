#!/usr/bin/env python3
"""Chapter 9, figure 2: the force on the obstacle, deposited run against our Rust run.
(a) drag D = -F_x, reference to t = 100, ours to t = 50;  (b) F_ours - F_ref on a symmetric-log axis (the two velocity-ramp conventions, t <= 5, in red);
(c) the lift F_y of the deposited run (to t = 100) and F_y of our snapshots.
Data: reference Force/force_dt=0.02.txt, our kwon_shin_force.csv (Rust example kwon_shin), the convention runs ks_st_dt01 / ks_rust_dt005 (t <= 5), our snapshots.
    nice .venv/bin/python -I book/figures/ch09_force.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch09_render import *
import ch09_common as C

XQ = Path("/mnt/data/xdev-cache/qf-external")
t_ref, fx_ref, fy_ref, _ = C.load_ref_force()
t_o, F_o, F_r, dF = C.load_ours_force()
d_st = np.loadtxt(XQ / "ks_st_dt01" / "kwon_shin_force.csv", delimiter=",", skiprows=1)
tb = 24.25                                        # the first pair appears between 24.2 and 24.3 (ch09_birth.py)

fig = plt.figure(figsize=(TEXTW, 4.35))
gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 1.0], hspace=0.50, wspace=0.34, left=0.085, right=0.99, top=0.975, bottom=0.095)

# ---- (a) drag
ax = fig.add_subplot(gs[0, :])
ax.axvspan(50, 100, color="#EEE9DD", lw=0, zorder=0)
ax.plot(t_ref, -fx_ref, color=BLUE, lw=1.6, label="deposited run (Kwon & Shin)")
ax.plot(t_o, -F_o, color=ORANGE, lw=1.0, ls=(0, (4, 2)), label="ours: Rust, $\\Delta t=0.01$")
ax.axvline(tb, color=GREY, lw=0.7, ls=":")
ax.text(tb - 0.8, 0.5, "first vortex pair\n$t\\approx24.25\\,\\tau$", ha="right", va="bottom", fontsize=7.8, color=GREY)
ax.text(75, 0.5, "not reproduced:\nour run stops at $t=50$", ha="center", va="bottom", fontsize=7.8, color=GREY)
i_max = int(np.argmax(-fx_ref))
ax.annotate(f"max $D={-fx_ref[i_max]:.2f}$ at $t={t_ref[i_max]:.1f}$", xy=(t_ref[i_max], -fx_ref[i_max]), xytext=(52, 5.6), fontsize=7.8, color=BLUE,
            arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.6))
ax.set_xlim(0, 100); ax.set_ylim(0, 10.2)
ax.set_xlabel(r"$t/\tau$"); ax.set_ylabel(r"drag $D=-F_x$  ($\mu/\xi$)")
ax.legend(loc="upper left", fontsize=8)
panel(ax, "a")

# ---- (b) difference
ax = fig.add_subplot(gs[1, 0])
thr = 1e-6
ax.set_yscale("symlog", linthresh=thr, linscale=0.35)
ax.axhline(0, color=GREY, lw=0.5)
ax.plot(d_st[:, 0], d_st[:, 3], color=RED, lw=1.1, label="stage-time ramp ($t\\leq5$)")
ax.plot(t_o, dF, color=ORANGE, lw=1.4, label="step-end ramp (as the reference)")
ax.axvline(tb, color=GREY, lw=0.7, ls=":")
ax.axhline(0.0019 * 8.935, color=BLUE, lw=0.6, ls="--")
ax.text(1.0, 0.0019 * 8.935 * 1.35, "$0.19$ % of max $|F|$", fontsize=7.5, color=BLUE, va="bottom")
ax.set_xlim(0, 50); ax.set_ylim(-2e-2, 1e-1)
ax.set_yticks([-1e-2, -1e-4, 0, 1e-6, 1e-4, 1e-2]); ax.set_yticklabels(["$-10^{-2}$", "$-10^{-4}$", "0", "$10^{-6}$", "$10^{-4}$", "$10^{-2}$"], fontsize=7.8)
ax.set_xlabel(r"$t/\tau$"); ax.set_ylabel(r"$F_{\rm ours}-F_{\rm ref}$  ($\mu/\xi$)")
ax.legend(loc="lower right", fontsize=7.2, bbox_to_anchor=(1.0, 0.0))
panel(ax, "b")

# ---- (c) lift
ax = fig.add_subplot(gs[1, 1])
ax.axvspan(50, 100, color="#EEE9DD", lw=0, zorder=0)
ax.plot(t_ref, fy_ref * 1e4, color=BLUE, lw=1.0, label="deposited $F_y$")
tt = np.arange(5.0, 50.1, 5.0)
Fy = np.array([C.forces(C.load_ours(a))[1] for a in tt])
ax.plot(tt, Fy * 1e4, "o", color=ORANGE, ms=3.8, mec="white", mew=0.4, label="ours, from snapshots", zorder=5)
ax.axhline(0, color=GREY, lw=0.5)
ax.set_xlim(0, 100); ax.set_ylim(-4.2, 4.2)
ax.set_xlabel(r"$t/\tau$"); ax.set_ylabel(r"lift $F_y$  ($10^{-4}\,\mu/\xi$)")
ax.legend(loc="lower center", fontsize=7.2, bbox_to_anchor=(0.52, 0.0))
ax.text(0.04, 0.95, r"$|F_y|_{\max}/|F_x|_{\max}=4\times10^{-5}$", transform=ax.transAxes, fontsize=7.5, color=GREY, va="top")
panel(ax, "c")
save(fig, "ch09_force")
