"""Figure ch04_asymptotic: the series continues to every order and is asymptotic, not convergent.  Exact-rational coefficients c_p of
ch04_series_ext.py (for alpha_2, alpha_3, alpha_4 of the paper, exact fractions; the first six agree with the closed forms of Lean to
1e-15).  (a) relative error of the partial sum through T^p against the CVODE value of the model; (b) the root test
(|c_p|/p!)^(1/p), whose limit is 1/(hbar c |u_c| / k_B), with u_c the critical value of u(k) nearest to the origin (a complex pair)."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
from scipy.special import gammaln
import ch04_common as cc

HERE = Path(__file__).resolve().parent
D = np.load(HERE/"ch04_analysis.npz"); N = json.load(open(HERE/"ch04_numbers.json"))
cp = dict(zip(D["cp_p"], D["cp_v"])); Tc = list(D["T_lin"]); Y = D["Y_lin"]
ps = np.arange(3, 41)
def partial(T, pm): return sum(cp[q]*T**(q - 3) for q in cp if q <= pm)/cp[3]
cols = {0.2: BLUE, 0.3: TEAL, 0.5: ORANGE, 0.8: RED}

fig = plt.figure(figsize=(TEXTW, 2.7))
ax = fig.add_axes([0.085, 0.16, 0.45, 0.77]); bx = fig.add_axes([0.655, 0.16, 0.33, 0.77])
for t, col in cols.items():
    exact = Y[Tc.index(t)]
    err = np.array([abs(partial(t, p)/exact - 1) for p in ps])
    ax.plot(ps, err, "-", color=col, lw=1.3, label=r"$T=%.1f$ K" % t)
    k = int(np.argmin(err)); ax.plot([ps[k]], [err[k]], "o", color=col, ms=5, mfc="white", mew=1.4, zorder=5)
ax.axvspan(2.5, 9.5, color=GOLD, alpha=0.12, lw=0); ax.text(6.0, 2.5e3, "Eq. $(22)$\n(proved)", fontsize=7.4, color="#7a5a10", ha="center", va="top")
ax.set_yscale("log"); ax.set_xlim(2.5, 40.5); ax.set_ylim(1e-11, 1e5)
ax.set_xlabel(r"order $p$ of the last term kept ($T^p$)"); ax.set_ylabel(r"$|\,\mathrm{partial\ sum}\,/\,C_V^{\rm model}-1\,|$")
ax.set_yticks([1e-8, 1e-5, 1e-2, 1e1, 1e4]); ax.set_yticklabels([r"$10^{-8}$", r"$10^{-5}$", r"$10^{-2}$", r"$10$", r"$10^{4}$"])
from matplotlib.lines import Line2D
hs, ls = ax.get_legend_handles_labels()
hs.append(Line2D([0], [0], marker="o", ls="none", mfc="white", mec=GREY, mew=1.3, ms=5)); ls.append("best truncation")
ax.legend(hs, ls, loc="lower right", ncol=2, fontsize=7.0, handlelength=1.5, labelspacing=0.3, columnspacing=0.9, borderaxespad=0.15)
ax.grid(True, which="major", axis="y"); panel(ax, "a")
pp = np.array([p for p in sorted(cp) if p >= 8])
rt = np.array([(abs(cp[p])/np.exp(gammaln(p + 1)))**(1.0/p) for p in pp])
bx.plot(pp, rt, "o", color=BLUE, ms=3.0)
pred = N["root_test"]["predicted"]
bx.axhline(pred, color=RED, lw=1.1, ls=(0, (4, 2)))
bx.text(60, pred + 0.006, r"$1/(\hbar c\,|u_c|/k_B)=%.3f\ \mathrm{K^{-1}}$" % pred, fontsize=7.2, color=RED, ha="right", va="bottom")
bx.set_xlim(8, 61); bx.set_ylim(0.15, 0.27)
bx.set_xlabel(r"order $p$"); bx.set_ylabel(r"$(|c_p|/p!)^{1/p}\ \ (\mathrm{K^{-1}})$"); panel(bx, "b")
save(fig, "ch04_asymptotic")
