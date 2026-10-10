"""Figure ch02_planewave: the exact plane wave of the projected GP equation (Lean: planeState_solves_galerkin) against three integrators.
 (a) error of the two IF-RK4 engines (numpy, Rust) against psi0 exp(-i w t), N = 32, L = 16, g = 1, mode m = 3, three steps dt;
 (b) order of the IF-RK4 step measured against a CVODE reference (Adams, rtol 1e-12) of the same right-hand side: the Rust example
     of the registered test (data/generated/pgpe/bench/cvode_order.json, re-run) and the same test through the Python module;
 (c) cost against accuracy on the plane wave, N = 16: IF-RK4 (4 right-hand sides per step) against CVODE Adams and BDF;
 (d) drift of the norm (the quantity whose rate Lean proves to vanish) along a flow with interacting modes, N = 16, t = 5.
Reads figures/ch02_numbers.json (keys A_order, C_planewave, D_invariants)."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
plt.rcParams["axes.unicode_minus"] = False
from matplotlib.ticker import FuncFormatter, NullFormatter

d = json.loads((Path(__file__).with_name("ch02_numbers.json")).read_text())
A, C, D = d["A_order"], d["C_planewave"], d["D_invariants"]
ADAMS, BDF, RK4 = BLUE, RED, TEAL

def logticks(ax, axis="y"):
    f = FuncFormatter(lambda v, p: (r"$10^{%d}$" % int(round(np.log10(v)))) if v > 0 else "")
    a = ax.yaxis if axis == "y" else ax.xaxis
    a.set_major_formatter(f); a.set_minor_formatter(NullFormatter())

fig = plt.figure(figsize=(TEXTW, 4.3))
axA = fig.add_axes([0.095, 0.585, 0.375, 0.365]); axB = fig.add_axes([0.590, 0.585, 0.375, 0.365])
axC = fig.add_axes([0.095, 0.085, 0.375, 0.365]); axD = fig.add_axes([0.590, 0.085, 0.375, 0.365])

# (a) engines against the exact solution
t = np.array(C["times"]); shade = {"dt=0.02": "#8FC1C1", "dt=0.01": TEAL, "dt=0.005": "#16403F"}
for key, col in shade.items():
    sr = C["engine_series"][key]
    axA.plot(t[1:], np.array(sr["numpy_err"])[1:], "-", color=col, lw=1.4, label=f"numpy, $\\Delta t={key[3:]}$")
    axA.plot(t[1:], np.array(sr["rust_err"])[1:], "o", color=col, ms=3.4, mfc="white", mew=0.9)
axA.plot([], [], "o", color=GREY, mfc="white", mew=0.9, ms=3.4, label="Rust, same steps")
tt = np.array([0.45, 11.0]); axA.plot(tt, 1.1246e-9 * tt, ":", color=GREY, lw=0.8)
axA.set_xscale("log"); axA.set_yscale("log"); axA.set_xlim(0.4, 12.5); axA.set_ylim(1e-11, 2e-5)
axA.set_xlabel("time $t$"); axA.set_ylabel("max error of $\\psi$", labelpad=1); logticks(axA); axA.set_xticks([0.5, 1, 2, 5, 10]); axA.set_xticklabels(["0.5", "1", "2", "5", "10"])
axA.legend(loc="upper left", fontsize=6.7, handletextpad=0.3, borderaxespad=0.1); panel(axA, "a")
axA.text(12.0, 2.2e-11, "dotted: slope 1 (a phase error\ngrowing in proportion to $t$)", fontsize=6.9, color=GREY, va="center", ha="right", linespacing=1.15)

# (b) order
dts = np.array([p[0] for p in A["dt_error_rust"]]); er = np.array([p[1] for p in A["dt_error_rust"]])
ep = np.array([p[1] for p in A["python_route"]["dt_error"]])
axB.loglog(dts, er, "o", color=RK4, ms=5, label=f"Rust engine: order {A['fitted_order_lsq_all5']:.3f}")
axB.loglog(dts, ep, "s", color=ORANGE, ms=4, mfc="white", mew=1.0, label=f"numpy engine: order {A['python_route']['fitted_order_lsq_all5']:.3f}")
g = np.array([0.0022, 0.05]); axB.loglog(g, er[2] * (g / dts[2]) ** 4, "-", color=GREY, lw=0.8)
axB.text(0.0042, 1.2e-9, "slope 4", color=GREY, fontsize=7.4, rotation=37)
axB.set_xlabel("step $\\Delta t$"); axB.set_ylabel("error against CVODE reference", labelpad=1)
axB.set_xlim(0.0022, 0.05); axB.set_ylim(8e-10, 4e-4); logticks(axB)
axB.set_xticks([0.0025, 0.005, 0.01, 0.02, 0.04]); axB.set_xticklabels(["0.0025", "0.005", "0.01", "0.02", "0.04"]); axB.xaxis.set_minor_formatter(NullFormatter())
axB.legend(loc="upper left", fontsize=7.0, handletextpad=0.3, borderaxespad=0.1); panel(axB, "b")

# (c) cost against accuracy on the plane wave
cv = C["cvode_N16"]["rows"]
for m, col, mk, lab in (("adams", ADAMS, "o", "CVODE Adams"), ("bdf", BDF, "s", "CVODE BDF")):
    r = [x for x in cv if x["method"] == m]
    axC.plot([x["nfe"] for x in r], [x["err"] for x in r], "-" + mk, color=col, ms=4.2, lw=1.0, label=lab)
e16 = C["engine_N16"]
axC.plot([x["nfe_equivalent"] for x in e16], [x["err"] for x in e16], "-^", color=RK4, ms=4.6, lw=1.0, label="IF-RK4 ($4$ per step)")
axC.set_xscale("log"); axC.set_yscale("log"); axC.set_xlim(5e2, 1.2e4); axC.set_ylim(3e-10, 3e-2)
axC.set_xlabel("right-hand-side evaluations"); axC.set_ylabel("max error of $\\psi$ at $t=10$", labelpad=1)
logticks(axC); logticks(axC, "x"); axC.legend(loc="upper right", fontsize=6.9, handletextpad=0.3, borderaxespad=0.1); panel(axC, "c")

# (d) drift of the norm
rows = D["rows"]
def pts(sel):
    return [(x["nfe"], x["dN_over_N_signed"]) for x in rows if sel(x) and x.get("nfe") is not None]
rk = [(4 * D["t_end"] / x["dt"], x["dN_over_N_signed"]) for x in rows if x.get("engine") == "rust"]
for m, col, mk in (("adams", ADAMS, "o"), ("bdf", BDF, "s")):
    p = pts(lambda x: x.get("method") == m)
    for n, v in p:
        axD.plot([n], [abs(v)], mk, color=col, ms=5, mfc=(col if v < 0 else "white"), mew=1.0)
    axD.plot([n for n, v in p], [abs(v) for n, v in p], "-", color=col, lw=0.8, alpha=0.7)
for n, v in rk:
    axD.plot([n], [abs(v)], "^", color=RK4, ms=5.2, mfc=(RK4 if v < 0 else "white"), mew=1.0)
axD.plot([n for n, v in rk], [abs(v) for n, v in rk], "-", color=RK4, lw=0.8, alpha=0.7)
axD.set_xscale("log"); axD.set_yscale("log"); axD.set_xlim(4e2, 8e3); axD.set_ylim(5e-13, 5e-4)
axD.set_xlabel("right-hand-side evaluations"); axD.set_ylabel("$|\\Delta N|/N$ at $t=5$", labelpad=1)
logticks(axD); logticks(axD, "x")
axD.plot([], [], "o", color=ADAMS, label="Adams"); axD.plot([], [], "s", color=BDF, label="BDF"); axD.plot([], [], "^", color=RK4, label="IF-RK4")
axD.plot([], [], "o", color=GREY, label="norm lost"); axD.plot([], [], "o", color=GREY, mfc="white", label="norm gained")
axD.legend(loc="upper right", fontsize=6.6, handletextpad=0.3, borderaxespad=0.1, ncol=1); panel(axD, "d")
save(fig, "ch02_planewave")
