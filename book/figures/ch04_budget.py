"""Figure ch04_budget: Eq. (22) against the numerical integral of the measured dispersion, and where the error comes from.
(a) C_V/T^3 of the phonon part (k < k_M) in J mol^-1 K^-4: the integral of the measured table (CVODE), the paper's own table column,
    the exact integral of the polynomial model, and the partial sums of Eq. (22).
(b) three relative deviations: series vs. exact polynomial model (the series' own truncation error), polynomial model vs. measured
    table (the model error), series vs. measured table (the total); grey squares: the uncertainty column of the paper's table."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *

HERE = Path(__file__).resolve().parent
D = np.load(HERE/"ch04_analysis.npz"); N = json.load(open(HERE/"ch04_numbers.json"))
Tc = D["T_lin"]; C_ph = D["C_ph"]; C_poly = D["C_poly"]; paper_ph = D["paper_ph"]; paper_tot = D["paper_tot"]; paper_err = D["paper_err"]
cp = dict(zip(D["cp_p"], D["cp_v"]))
Tf = np.linspace(0.04, 1.05, 500)
def S(T, pmax): return sum(cp[q]*T**q for q in cp if q <= pmax)

fig = plt.figure(figsize=(TEXTW, 3.1))
ax = fig.add_axes([0.095, 0.15, 0.40, 0.78]); bx = fig.add_axes([0.61, 0.15, 0.375, 0.78])
shades = ["#B9D3D3", "#8FBABA", "#62A0A0", "#3A8787", "#256B6B", "#124444"]
names = ["A", "A+C", "A+C+D", "A+…+E", "A+…+K", "A+…+L"]
for (pm, nm, sh) in zip((3, 5, 6, 7, 8, 9), names, shades):
    ax.plot(Tf, S(Tf, pm)/Tf**3, color=sh, lw=0.9 if pm != 9 else 1.6, zorder=3)
ax.plot(Tc, C_poly/Tc**3, color=ORANGE, lw=1.2, ls=(0, (5, 2)), zorder=6)
ax.plot(Tc, C_ph/Tc**3, color=BLUE, lw=2.4, zorder=5)
ax.plot(Tc, paper_ph/Tc**3, "o", mfc="none", mec=GOLD, ms=4.2, mew=0.9, zorder=7)
ax.set_xlim(0, 1.0); ax.set_ylim(0.058, 0.092)
ax.set_xlabel("temperature  $T$ (K)"); ax.set_ylabel(r"$C_V^{\rm phonon}/T^3\ \ (\mathrm{J\,mol^{-1}K^{-4}})$")
# legend (lower left is free) and two direct labels
from matplotlib.lines import Line2D
hand = [Line2D([0], [0], color=BLUE, lw=2.4), Line2D([0], [0], marker="o", mfc="none", mec=GOLD, mew=0.9, ms=4.2, lw=0),
        Line2D([0], [0], color=ORANGE, lw=1.2, ls=(0, (5, 2))), Line2D([0], [0], color="#3A8787", lw=1.0)]
ax.legend(hand, ["measured table, $k<k_M$ (CVODE)", "paper's table, phonon column", "polynomial model, exact (CVODE)",
                 "partial sums of Eq. $(22)$: $A$, $A{+}C$, $\\dots$, $A{+}\\dots{+}L$\n(darker = more terms)"],
          loc="lower left", fontsize=6.8, handlelength=1.8, labelspacing=0.45, bbox_to_anchor=(0.0, 0.0))
ax.text(0.045, 0.0836, "$A$", fontsize=7.6, color="#5C8F8F", ha="left", va="bottom")
ax.text(0.975, 0.0913, "total including rotons:\noff scale above $0.6\\,$K", fontsize=6.8, color=GREY, ha="right", va="top")
panel(ax, "a")
e1 = np.abs(D["e_trunc"]); e2 = np.abs(D["e_model"]); e3 = np.abs(D["e_tot"])
bx.plot(Tc, e1, color=TEAL, lw=1.6, label="series vs. exact polynomial\n(truncation error)")
bx.plot(Tc, e2, color=ORANGE, lw=1.6, label="polynomial vs. measured\n(model error)")
bx.plot(Tc, e3, color=BLUE, lw=1.0, ls=(0, (3, 1.5)), label="series vs. measured (total)")
rel = paper_err/paper_tot; ok = ~np.isnan(rel)
bx.plot(Tc[ok], rel[ok], "s", color=GREY, ms=3.2, label="uncertainty column of the table")
bx.axhline(1e-2, color=GREY, lw=0.6, ls=":"); bx.text(0.995, 1.15e-2, "1 %", fontsize=7.2, color=GREY, ha="right", va="bottom")
bx.set_yscale("log"); bx.set_xlim(0.1, 1.0); bx.set_ylim(1e-8, 3.0)
bx.set_yticks([1e-8, 1e-6, 1e-4, 1e-2, 1]); bx.set_yticklabels([r"$10^{-8}$", r"$10^{-6}$", r"$10^{-4}$", r"$10^{-2}$", r"$1$"])
bx.set_xlabel("temperature  $T$ (K)"); bx.set_ylabel("relative deviation")
bx.legend(loc="lower right", fontsize=6.9, handlelength=1.8, labelspacing=0.35); bx.grid(True, which="major", axis="y"); panel(bx, "b")
save(fig, "ch04_budget")
