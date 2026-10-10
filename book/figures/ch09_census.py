#!/usr/bin/env python3
"""Chapter 9, figure 3: how many vortices?  (a) counts against time: the deposited file (its own detector), the same detector run on our snapshots,
and the exact census of non-zero plaquettes (ours; the reference's census coincides at t = 10,...,50).  (b, c) the deposited fields at t = 40 and 50:
the exact census (filled circles, counter-clockwise gold / clockwise cyan) and the detector's loops (black squares, half-width 2 xi).
Numbers: figures/ch09_numbers.json (ch09_numbers.py); fields recomputed here.
    nice .venv/bin/python -I book/figures/ch09_census.py
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch09_render import *
import ch09_common as C
from matplotlib.patches import Rectangle

R = json.load(open(Path(__file__).resolve().parent / "ch09_numbers.json"))["census"]
t5 = np.array(R["times"]); n_file = np.array(R["reference_rule_in_file"]); n_rule = np.array(R["ours_with_reference_rule"]); n_exact = np.array(R["ours_exact_census"])
tr = np.array(R["reference_counts_to_t100"]["t"]); nr = np.array(R["reference_counts_to_t100"]["n"])
ref_exact = {float(k): v for k, v in R["reference_exact_census"].items()}

fig = plt.figure(figsize=(TEXTW, 4.25))
gs = fig.add_gridspec(2, 2, height_ratios=[0.95, 1.05], hspace=0.42, wspace=0.12, left=0.085, right=0.99, top=0.975, bottom=0.085)
ax = fig.add_subplot(gs[0, :])
ax.axvspan(50.5, 100, color="#EEE9DD", lw=0, zorder=0)
ax.plot(tr, nr, "-s", color=BLUE, ms=4.2, lw=1.0, mfc=BLUE, label="deposited file (its own detector)", zorder=3)
ax.plot(t5, n_rule, "o", color=ORANGE, ms=6.2, mfc="none", mew=1.2, label="same detector, our snapshots", zorder=4)
ax.plot(t5, n_exact, "D", color=TEAL, ms=4.4, label="exact census, ours (non-zero plaquettes)", zorder=5)
tx = np.array(sorted(ref_exact))
ax.plot(tx, [ref_exact[a] for a in tx], "D", mfc="none", color=TEAL, ms=8.0, mew=0.9, zorder=6, label="exact census, deposited fields")
ax.text(80, 1.0, "no field deposited\nbeyond $t=50$", ha="center", va="bottom", fontsize=7.8, color=GREY)
ax.annotate("4 counted,\n14 present", xy=(40, 14), xytext=(31.0, 15.2), fontsize=7.8, color=TEAL, arrowprops=dict(arrowstyle="-", color=TEAL, lw=0.6), ha="center")
ax.annotate("one vortex\ncounted twice", xy=(30, 3), xytext=(20.5, 8.0), fontsize=7.8, color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.6), ha="center")
ax.annotate("7 against 6", xy=(45, 6.6), xytext=(56.5, 3.4), fontsize=7.8, color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.6), ha="center")
ax.set_xlim(0, 100); ax.set_ylim(-0.8, 27)
ax.set_xlabel(r"$t/\tau$"); ax.set_ylabel("number of vortices")
ax.legend(loc="upper left", fontsize=7.2, ncol=2, columnspacing=1.2, handletextpad=0.5, borderaxespad=0.2)
panel(ax, "a")

for col, T, lab in ((0, 40.0, "b"), (1, 50.0, "c")):
    a_ = fig.add_subplot(gs[1, col])
    p = C.load_ref(T)
    cs = C.rule_candidates(p); census = C.charged(p)
    n = np.abs(p) ** 2
    xl, yl = (76.0, 96.0), (-12.0, 12.0)
    ix0, ix1 = int((xl[0] + 250) / C.DX), int((xl[1] + 250) / C.DX); iy0, iy1 = int((yl[0] + 125) / C.DX), int((yl[1] + 125) / C.DX)
    for c in cs:
        if c["counted"]:
            a_.add_patch(Rectangle((c["x"] - 2, c["y"] - 2), 4, 4, fill=False, ec="black", lw=0.7, zorder=3))
            a_.plot(c["x"], c["y"], "x", color="black", ms=4.2, mew=0.9, zorder=4)
    charge_markers(a_, census, size=34, lw=0.6, edge="black")
    style_map(a_, xl, yl, xticks=[80, 85, 90, 95], yticks=[-10, 0, 10], ylabel=(col == 0))
    if col == 1: a_.set_yticklabels([])
    a_.axhline(0, color=GREY, lw=0.4, ls=":", zorder=1)
    nacc = sum(c["counted"] for c in cs)
    a_.set_title(f"$t={T:.0f}\\,\\tau$: ${nacc}$ counted, ${len(census)}$ present", fontsize=8.2, pad=3)
    panel(a_, lab)
fig.text(0.54, 0.012, r"$x/\xi$", ha="center", fontsize=10)
for a_ in fig.axes[1:]: a_.set_xlabel("")
save(fig, "ch09_census")
