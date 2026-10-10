"""Figure ch04_bose: the six Bose integrals of Lean `PhononSpecificHeat.bose_integral_values` as initial-value problems solved by
rusty-SUNDIALS CVODE (Adams).  (a) the cumulative integrals F_m(x)/(m! zeta(m+1)); (b) the relative error against the closed forms
proved in Lean, as a function of the requested tolerance.  Data: ch04_cvode_results.npz / ch04_cvode_raw.json."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
from scipy.special import zeta

HERE = Path(__file__).resolve().parent
R = np.load(HERE/"ch04_cvode_results.npz"); raw = json.load(open(HERE/"ch04_cvode_raw.json"))
ms = [int(m) for m in R["ms"]]; xs = R["xs"]; cur = R["curves"]
closed = {3: r"$\pi^4/15$", 5: r"$8\pi^6/63$", 6: r"$720\,\zeta(7)$", 7: r"$8\pi^8/15$", 8: r"$40320\,\zeta(9)$", 9: r"$128\pi^{10}/33$"}
cols = [BLUE, TEAL, "#6E9A3A", GOLD, ORANGE, RED]

fig = plt.figure(figsize=(TEXTW, 2.6))
ax = fig.add_axes([0.075, 0.17, 0.43, 0.76]); bx = fig.add_axes([0.62, 0.17, 0.36, 0.76])
for i, m in enumerate(ms):
    ax.plot(xs, cur[:, i]/zeta(m + 1), color=cols[i], lw=1.4, label=r"$m=%d$:  %s" % (m, closed[m]))
    xp = m - 0.05                                                    # the integrand x^m/(e^x - 1) peaks near x = m
    ax.plot([xp], [0.0], marker="|", ms=7, color=cols[i], mew=1.4, clip_on=False)
ax.set_xlim(0, 40); ax.set_ylim(0, 1.04)
ax.set_xlabel(r"upper limit $x$"); ax.set_ylabel(r"$\int_0^x t^m/(e^t-1)\,\mathrm{d}t\;/\;m!\,\zeta(m+1)$")
ax.legend(loc="lower right", fontsize=7.2, title=r"limit proved in Lean", title_fontsize=7.4, handlelength=1.6, labelspacing=0.28)
ax.text(37.5, 0.64, "ticks: peak of the integrand\n$t^m/(e^t-1)$", fontsize=7.2, color=GREY, ha="right")
panel(ax, "a")
rt = [r["rtol"] for r in raw["A"]["runs"]]
for i, m in enumerate(ms):
    bx.plot(rt, [r["rel_err_vs_lean_closed_form"][str(m)] for r in raw["A"]["runs"]], "o-", color=cols[i], ms=3.0, lw=1.0)
bx.plot([1e-12, 1e-4], [1e-12, 1e-4], color=GREY, lw=0.8, ls=(0, (4, 2)), label="error = tolerance"); bx.legend(loc="lower right", fontsize=7.4)
bx.set_xscale("log"); bx.set_yscale("log"); bx.set_xlim(5e-13, 3e-4); bx.set_ylim(3e-15, 3e-3)
bx.set_xlabel("requested relative tolerance"); bx.set_ylabel("relative error vs. the Lean closed form")
bx.set_xticks([1e-12, 1e-10, 1e-8, 1e-6, 1e-4]); bx.set_xticklabels([r"$10^{-12}$", r"$10^{-10}$", r"$10^{-8}$", r"$10^{-6}$", r"$10^{-4}$"])
bx.set_yticks([1e-14, 1e-11, 1e-8, 1e-5]); bx.set_yticklabels([r"$10^{-14}$", r"$10^{-11}$", r"$10^{-8}$", r"$10^{-5}$"])
bx.minorticks_off(); bx.grid(True, which="major", axis="y"); panel(bx, "b")
save(fig, "ch04_bose")
