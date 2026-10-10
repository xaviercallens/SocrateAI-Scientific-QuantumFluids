"""Figure ch04_ladder: the solver against the proved series.  The specific heat of the MODEL dispersion
eps = hbar c k (1 + a2 k^2 + a3 k^3 + a4 k^4) is computed by CVODE (BDF) from the thermal k-integral, with no series at all.
(a) |C_V/(A T^3) - partial sum of Eq. (22) through the term named on the line|: the lines should have the slope of the NEXT term;
    dashed: that next term.  The last line is not predicted by Lean (T^10 coefficient from exact rational arithmetic).
(b) What a numerical experiment can say about each coefficient:  |c_hat_p(T)/c_p - 1| with c_hat_p = (C_V - sum_{q<p} c_q T^q)/T^p."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
import ch04_common as cc

HERE = Path(__file__).resolve().parent
D = np.load(HERE/"ch04_analysis.npz"); N = json.load(open(HERE/"ch04_numbers.json"))
T = D["T_log"]; resid = D["resid"]; pred = D["pred"]; truncs = list(D["truncs"]); Y = D["Y_log"]
cp = dict(zip(D["cp_p"], D["cp_v"])); A = cp[3]
labels = {3: "A", 5: "A+C", 6: "A+C+D", 7: "A+…+E", 8: "A+…+K", 9: "A+…+L"}
cols = [GREY, BLUE, TEAL, "#6E9A3A", ORANGE, RED]
floor = float(D["floor"]); floor_T = D["floor_T"]; floor_err = D["floor_err"]

fig = plt.figure(figsize=(TEXTW, 3.05))
ax = fig.add_axes([0.085, 0.15, 0.44, 0.78]); bx = fig.add_axes([0.62, 0.15, 0.36, 0.78])
nextlab = {3: r"$C\,T^5$", 5: r"$D\,T^6$", 6: r"$E\,T^7$", 7: r"$K\,T^8$", 8: r"$L\,T^9$", 9: r"$c_{10}T^{10}$"}
for i, p in enumerate(truncs):
    r = np.maximum(resid[i], 1e-17)
    ax.plot(T, r, color=cols[i], lw=1.5, label=labels[p] + r"  $\to$  " + nextlab[p])
    ax.plot(T, pred[i], color=cols[i], lw=0.9, ls=(0, (3, 2)))
ax.fill_between(floor_T, 1e-17, np.maximum(floor_err, 1e-17), color=GREY, alpha=0.18, lw=0)
ax.plot(floor_T, floor_err, "s", color=GREY, ms=2.6)
ax.text(0.97, 1.7e-15, "grey: solver error vs. a 30-digit reference", fontsize=7.0, color=GREY, va="top", ha="right")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(0.005, 1.0); ax.set_ylim(2e-16, 30)
ax.set_xlabel("temperature  $T$ (K)"); ax.set_ylabel(r"$|C_V^{\rm CVODE}-\mathrm{partial\ sum}|\,/\,A\,T^3$")
ax.set_xticks([0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]); ax.set_xticklabels(["0.005", "0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1"], fontsize=7.6)
ax.set_yticks([1e-14, 1e-11, 1e-8, 1e-5, 1e-2]); ax.set_yticklabels([r"$10^{-14}$", r"$10^{-11}$", r"$10^{-8}$", r"$10^{-5}$", r"$10^{-2}$"])
ax.minorticks_off(); ax.grid(True, which="major", axis="y")
ax.legend(loc="upper left", fontsize=6.9, title="solid: residual after the terms kept;\ndashed: the next term", title_fontsize=6.9, handlelength=1.5, labelspacing=0.25, bbox_to_anchor=(0.0, 1.0))
panel(ax, "a")
# (b) coefficient recovery
for i, p in enumerate(truncs[1:], start=1):
    est = (A*T**3*Y - sum(cp[q]*T**q for q in cp if q < p and q <= 60))/T**p
    rel = np.abs(est/cp[p] - 1)
    names = {5: "C", 6: "D", 7: "E", 8: "K", 9: "L"}
    bx.plot(T, rel, color=cols[i], lw=1.4, label=names[p])
bx.set_xscale("log"); bx.set_yscale("log"); bx.set_xlim(0.005, 0.12); bx.set_ylim(1e-3, 30)
bx.set_xticks([0.005, 0.01, 0.02, 0.05, 0.1]); bx.set_xticklabels(["0.005", "0.01", "0.02", "0.05", "0.1"], fontsize=7.6)
bx.set_yticks([1e-3, 1e-2, 1e-1, 1, 10]); bx.set_yticklabels([r"$10^{-3}$", r"$10^{-2}$", r"$10^{-1}$", r"$1$", r"$10$"])
bx.set_xlabel("temperature  $T$ (K)"); bx.set_ylabel(r"$|\hat c_p(T)/c_p-1|$")
bx.minorticks_off(); bx.grid(True, which="major", axis="y"); bx.legend(loc="lower right", fontsize=7.4, ncol=5, handlelength=1.2, columnspacing=0.8, title="coefficient", title_fontsize=7.2)
panel(bx, "b")
save(fig, "ch04_ladder")
