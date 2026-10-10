"""Figure ch02_workprecision: what the Python module rusty_sundials.CvodeSolver does on problems with closed-form solutions.
 (a) work-precision on ten periods of the harmonic oscillator (non-stiff), Adams against BDF, 19 tolerances each;
 (b) cost against stiffness on the Prothero-Robinson problem y' = -lam (y - cos t) - sin t at rtol 1e-6;
 (c) amplitude of the oscillator against time: |(x, v)| - 1 for independent runs to each t (exact value 0);
 (d) the Adams defect: y' = -y, the module built before the fix (implicit Euler) against the current build.
Cost = number of calls of the user's right-hand side (includes the finite-difference Jacobian columns): machine independent.
Reads figures/ch02_numbers.json (key B_cvode, written by ch02_compute.py part B)."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
plt.rcParams["axes.unicode_minus"] = False
from matplotlib.ticker import FuncFormatter, NullFormatter

B = json.loads((Path(__file__).with_name("ch02_numbers.json")).read_text())["B_cvode"]
ADAMS, BDF = BLUE, RED

def logticks(ax, axis="y"):
    f = FuncFormatter(lambda v, p: (r"$10^{%d}$" % int(round(np.log10(v)))) if v > 0 else "")
    a = ax.yaxis if axis == "y" else ax.xaxis
    a.set_major_formatter(f); a.set_minor_formatter(NullFormatter())

fig = plt.figure(figsize=(TEXTW, 4.3))
axA = fig.add_axes([0.095, 0.585, 0.375, 0.365]); axB = fig.add_axes([0.590, 0.585, 0.375, 0.365])
axC = fig.add_axes([0.095, 0.085, 0.375, 0.365]); axD = fig.add_axes([0.590, 0.085, 0.375, 0.365])

# (a) oscillator work-precision
rows = B["oscillator"]["rows"]
for m, col, lab in (("adams", ADAMS, "Adams"), ("bdf", BDF, "BDF")):
    r = [x for x in rows if x["method"] == m and x["err"] is not None]
    axA.plot([x["nfe"] for x in r], [x["err"] for x in r], "o", color=col, ms=3.8, mec="white", mew=0.4, label=lab)
axA.set_xscale("log"); axA.set_yscale("log"); axA.set_xlim(4e2, 3e4); axA.set_ylim(5e-11, 1e-1)
axA.set_xlabel("right-hand-side evaluations"); axA.set_ylabel("error after ten periods", labelpad=1)
logticks(axA); logticks(axA, "x"); axA.legend(loc="upper right", fontsize=7.6, handletextpad=0.2); panel(axA, "a")

# (b) stiffness
pr = B["prothero_robinson"]["rows"]
for m, col, lab in (("adams", ADAMS, "Adams"), ("bdf", BDF, "BDF")):
    r = [x for x in pr if x["method"] == m]
    axB.plot([x["lam"] for x in r], [x["nfe"] for x in r], "-o", color=col, ms=3.8, lw=1.1, label=lab)
axB.set_xscale("log"); axB.set_yscale("log"); axB.set_xlim(0.6, 2e5); axB.set_ylim(150, 1.2e4)
axB.set_xlabel(r"stiffness $\lambda$ (problem on $0\leq t\leq10$)"); axB.set_ylabel("evaluations at rtol $10^{-6}$", labelpad=1)
logticks(axB, "x"); logticks(axB)
a5 = [x for x in pr if x["method"] == "adams" and x["lam"] == 1e5][0]["nfe"]; b5 = [x for x in pr if x["method"] == "bdf" and x["lam"] == 1e5][0]["nfe"]
axB.annotate("", xy=(1e5, b5), xytext=(1e5, a5), arrowprops=dict(arrowstyle="<->", color=GREY, lw=0.8, shrinkA=2, shrinkB=2))
axB.text(7e4, np.sqrt(a5 * b5), f"{a5/b5:.0f}$\\times$", fontsize=8, color=GREY, ha="right", va="center")
axB.legend(loc="upper left", fontsize=7.6, handletextpad=0.2); panel(axB, "b")

# (c) amplitude against time
A = B["amplitude_vs_time"]; t = np.array(A["t"]) / (2 * np.pi)
for key, col, ls, lw, lab in (("adams_0.001", ADAMS, "-", 1.5, "Adams"), ("bdf_0.001", BDF, "-", 1.5, "BDF"),
                              ("adams_1e-05", ADAMS, (0, (3, 1.5)), 1.0, None), ("bdf_1e-05", RED, (0, (3, 1.5)), 1.0, None)):
    v = 100 * (np.array([x if x is not None else np.nan for x in A[key]]) - 1.0)
    axC.plot(t, v, ls=ls, color=col, lw=lw, label=lab)
axC.axhline(0, color=GREY, lw=0.6)
axC.set_xlim(0, 10); axC.set_ylim(-2.6, 5.8); axC.set_xlabel("time (periods)"); axC.set_ylabel("amplitude change (%)", labelpad=1)
axC.text(6.6, 3.2, "Adams, rtol $10^{-3}$", color=ADAMS, fontsize=7.6, ha="center"); axC.text(6.2, -1.9, "BDF, rtol $10^{-3}$", color=BDF, fontsize=7.6, ha="center")
axC.text(9.9, 0.45, "dashed: rtol $10^{-5}$", color=GREY, fontsize=7.0, ha="right"); panel(axC, "c")

# (d) the Adams defect
st = B["decay_stale_venv_module"]["rows"]; fx = B["decay_adams_fix"]["rows"]
sa = [x for x in st if x["method"] == "adams"]; fa = [x for x in fx if x["method"] == "adams"]; fb = [x for x in fx if x["method"] == "bdf"]
axD.plot([x["nfe"] for x in sa], [x["relerr"] for x in sa], "-o", color=ADAMS, mfc="white", ms=4.2, lw=1.0, ls=(0, (3, 1.5)), label="Adams, build before the fix")
axD.plot([x["nfe"] for x in fa], [x["relerr"] for x in fa], "-o", color=ADAMS, ms=4.2, lw=1.2, label="Adams, current build")
axD.plot([x["nfe"] for x in fb], [x["relerr"] for x in fb], "-s", color=BDF, ms=3.8, lw=1.2, label="BDF, current build")
axD.set_xscale("log"); axD.set_yscale("log"); axD.set_xlim(1e2, 5e6); axD.set_ylim(5e-10, 3e-1)
axD.set_xlabel("right-hand-side evaluations"); axD.set_ylabel("relative error of $y(10)$", labelpad=1)
logticks(axD); logticks(axD, "x"); axD.legend(loc="lower right", fontsize=6.9, handletextpad=0.2, borderaxespad=0.1)
axD.text(0.47, 0.56, "$y'=-y$\nrtol $10^{-4}$ to $10^{-10}$", transform=axD.transAxes, fontsize=7.0, color=GREY, va="top", linespacing=1.2); panel(axD, "d")
save(fig, "ch02_workprecision")
