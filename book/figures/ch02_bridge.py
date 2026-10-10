"""Figures ch02_bridge and ch02_rates: where a theorem about the Galerkin nonlinearity (QuantumFluids.GPGalerkin.nl, on the group Z^2) and the
engine's FFT-based nonlinearity (on the periodic grid Z_N^2) are the same function, and where they are not.
 ch02_bridge  (a),(b)  retained modes (index plane, N = 32) coloured by |engine - literal nl| / max|nl| on a random state; dotted: the periodic images of the
                       'reach' disc (radius 3R) of the triple sums k1 - k2 + k3; shaded: modes that the images cover (aliased).
 ch02_rates   (a)      the instantaneous rates of mass and of momentum (Lean: mass_rate_zero, momentum_rate_zero) for the literal nl and for the engine;
              (b)      drift of the invariants along an IF-RK4 run from one smooth random state, two cutoffs.
Reads figures/ch02_numbers.json (key E_bridge, written by ch02_compute.py part E)."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
plt.rcParams["axes.unicode_minus"] = False
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Circle, Rectangle
from matplotlib.ticker import FuncFormatter, NullFormatter

def logticks(ax, axis="y"):
    # EB Garamond has no U+2212: format the exponent through mathtext of the maths font, not through \mathdefault
    f = FuncFormatter(lambda v, p: (r"$10^{%d}$" % int(round(np.log10(v)))) if v > 0 else "")
    a = ax.yaxis if axis == "y" else ax.xaxis
    a.set_major_formatter(f); a.set_minor_formatter(NullFormatter())

E = json.loads((Path(__file__).with_name("ch02_numbers.json")).read_text())["E_bridge"]
N = E["N"]; cases = E["cases"]
cm = LinearSegmentedColormap.from_list("qfdiff", ["#F2D9A8", ORANGE, RED, "#3B1410"])
norm = Normalize(vmin=-4.0, vmax=-0.5)

# ------------------------------------------------------------------------------------------------ geometry of the aliasing
fig = plt.figure(figsize=(TEXTW, 3.0))
axA = fig.add_axes([0.075, 0.13, 0.395, 0.74]); axB = fig.add_axes([0.545, 0.13, 0.395, 0.74])
cax = fig.add_axes([0.955, 0.22, 0.012, 0.56])

def geometry(ax, case, letter, title):
    R = case["R_index"]; Lam = np.array(case["Lam"]); d = np.array(case["log10_reldiff"])
    ax.add_patch(Rectangle((-N / 2, -N / 2), N, N, fill=False, ec=GREY, lw=0.7, ls=(0, (4, 2))))     # Nyquist box
    ax.add_patch(Circle((0, 0), R, fill=False, ec=BLUE, lw=0.8))                                      # retained disc
    for cx, cy in ((N, 0), (-N, 0), (0, N), (0, -N)):                                                 # periodic images of the reach disc
        ax.add_patch(Circle((cx, cy), 3 * R, fill=False, ec=GOLD, lw=0.9, ls=(0, (1, 1.6))))
    gx, gy = np.meshgrid(np.linspace(-R, R, 400), np.linspace(-R, R, 400))                            # modes covered by the images
    inside = gx ** 2 + gy ** 2 <= R ** 2
    cover = np.zeros_like(inside)
    for cx, cy in ((N, 0), (-N, 0), (0, N), (0, -N), (N, N), (N, -N), (-N, N), (-N, -N)):
        cover |= (gx - cx) ** 2 + (gy - cy) ** 2 <= (3 * R) ** 2
    ax.contourf(gx, gy, (inside & cover).astype(float), levels=[0.5, 1.5], colors=[ORANGE], alpha=0.16)
    same = d < -12
    ax.scatter(Lam[same, 0], Lam[same, 1], s=5.5, color=BLUE, lw=0, zorder=3)
    sc = ax.scatter(Lam[~same, 0], Lam[~same, 1], s=15, c=d[~same], cmap=cm, norm=norm, lw=0.3, ec="#3B1410", zorder=4)
    ax.set_xlim(-N / 2 - 2.2, N / 2 + 2.2); ax.set_ylim(-N / 2 - 2.2, N / 2 + 2.2); ax.set_aspect("equal")
    ax.set_xticks([-16, -8, 0, 8, 16]); ax.set_yticks([-16, -8, 0, 8, 16])
    ax.set_xlabel(r"$n_x$"); ax.set_ylabel(r"$n_y$", labelpad=1); panel(ax, letter)
    ax.set_title(title, fontsize=8.6, pad=3)
    return sc

geometry(axA, cases["half_full"], "a", r"cutoff $k_{\mathrm{cut}}=\frac{1}{2} k_{\max}$  ($4R=N$)")
sc = geometry(axB, cases["twothirds_full"], "b", r"cutoff $k_{\mathrm{cut}}=\frac{2}{3} k_{\max}$  ($4R>N$)")
cb = fig.colorbar(sc, cax=cax); cb.set_label(r"$\log_{10}\,|\Delta N|/\max|N|$", fontsize=8); cb.ax.tick_params(labelsize=7.5)
ca, cb2 = cases["half_full"], cases["twothirds_full"]
axA.text(0, -10.4, f"{ca['n_modes_differing_1e-12']} of {ca['n_modes']} modes differ (max {ca['max_abs_diff_over_max_nl']:.0e})", fontsize=7.0, color=RED, va="top", ha="center")
axB.text(0, -12.7, f"{cb2['n_modes_differing_1e-12']} of {cb2['n_modes']} modes differ (max {cb2['max_abs_diff_over_max_nl']:.2f})", fontsize=7.0, color=RED, va="top", ha="center")
save(fig, "ch02_bridge")

# ------------------------------------------------------------------------------------------------ rates and drifts
fig = plt.figure(figsize=(TEXTW, 2.6))
axC = fig.add_axes([0.085, 0.27, 0.40, 0.66]); axD = fig.add_axes([0.605, 0.18, 0.37, 0.75])
names = [("half_interior", "$\\frac{1}{2} k_{\\max}$,\nedge modes\nempty"), ("half_full", "$\\frac{1}{2} k_{\\max}$,\nall modes"), ("twothirds_full", "$\\frac{2}{3} k_{\\max}$,\nall modes")]
floor = 1e-19
for i, (key, lab) in enumerate(names):
    r = cases[key]["rates"]
    v = lambda x: max(x, floor)
    axC.plot([i - 0.17], [v(r["engine"]["mass_rate_over_scale"])], "s", color=TEAL, ms=5.2, mfc=TEAL, label="mass rate, engine" if i == 0 else None)
    axC.plot([i], [v(r["engine"]["momentum_rate_over_scale"])], "o", color=RED, ms=5.6, label="momentum rate, engine" if i == 0 else None)
    axC.plot([i + 0.17], [v(r["lean_nl"]["momentum_rate_over_scale"])], "o", color=BLUE, ms=5.2, mfc="white", mew=1.1,
             label="momentum rate, literal nl" if i == 0 else None)
axC.axhline(1.1e-16, color=GREY, lw=0.7, ls=(0, (3, 2)))
axC.text(2.45, 1.6e-16, "double-precision\nrounding", fontsize=6.6, color=GREY, va="bottom", ha="right")
axC.set_yscale("log"); axC.set_ylim(1e-19, 1e-1); axC.set_xlim(-0.5, 2.5)
axC.set_xticks(range(3)); axC.set_xticklabels([n[1] for n in names], fontsize=7.4)
axC.set_ylabel("rate / sum of the terms", fontsize=8.6, labelpad=1)
axC.legend(loc="center left", bbox_to_anchor=(0.0, 0.50), fontsize=6.8, handletextpad=0.3, borderaxespad=0.1)
logticks(axC); axC.set_yticks([1e-19, 1e-16, 1e-13, 1e-10, 1e-7, 1e-4, 1e-1])
panel(axC, "a")

for key, col, lab in (("half", BLUE, r"$\frac{1}{2} k_{\max}$"), ("twothirds", RED, r"$\frac{2}{3} k_{\max}$")):
    rows = np.array(E["drift"][key]["rows_t_dN_dE_dP"])[1:]
    axD.plot(rows[:, 0], rows[:, 3], "-", color=col, lw=1.5, label=f"momentum, {lab}")
rows = np.array(E["drift"]["half"]["rows_t_dN_dE_dP"])[1:]
axD.plot(rows[:, 0], rows[:, 1], "-", color=TEAL, lw=1.1, label="norm (both cutoffs)")
axD.plot(rows[:, 0], rows[:, 2], "--", color=GOLD, lw=1.1, label="energy (both cutoffs)")
axD.set_yscale("log"); axD.set_xlim(0, 20); axD.set_ylim(1e-11, 1e-4)
axD.set_xlabel("time $t$"); axD.set_ylabel("relative drift", labelpad=1)
axD.legend(loc="upper left", fontsize=6.8, handlelength=1.5, borderaxespad=0.1); logticks(axD); panel(axD, "b")
save(fig, "ch02_rates")
