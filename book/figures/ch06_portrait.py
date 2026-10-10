"""Figure ch06_portrait: the Kosterlitz flow integrated with CVODE (rusty-SUNDIALS) against the Lean statements.
(a) Phase portrait in the plane (u = 1/K, y): level sets of the exact invariant H (thin grey; by KTFlow.kt_invariant they ARE the flow lines), the exact
    separatrix H = f(pi/2) (black) and its textbook linearisation (dashed), CVODE trajectories (blue: hypothesis of KTFlow.kt_trapped satisfied; red: below the
    separatrix; grey: starting beyond u = pi/2), and the points u* where trapped trajectories end.  (b) drift of H against the CVODE tolerance, Adams and BDF,
    and the negative control (a flow with a 5 % wrong coefficient).  (c) first-passage time to u = pi/2 below the separatrix: CVODE against the Lean bound
    l1 = (pi/2 - u0) / (2 (f(pi/2) - H0)) (Ch06_KTEscape.kt_escape_time).
Data: figures/ch06_flow_data.npz and ch06_flow_numbers.json (ch06_flow_compute.py)."""
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
from ch06_common import *
from matplotlib.patches import Polygon

HERE = Path(__file__).resolve().parent
D = np.load(HERE / "ch06_flow_data.npz"); R = json.loads((HERE / "ch06_flow_numbers.json").read_text())
pi = math.pi; UC = pi / 2
f = lambda u: 2 * u - pi * np.log(u)
FC = f(UC)
H = lambda u, y: f(u) - 2 * pi ** 3 * y ** 2
sep = lambda u: np.sqrt(np.maximum(f(u) - FC, 0) / (2 * pi ** 3))

fig = plt.figure(figsize=(TEXTW, 3.55))
gs = fig.add_gridspec(2, 5, width_ratios=[1, 1, 1, 0.16, 1.45], height_ratios=[1, 1], hspace=0.62, wspace=0.62, left=0.075, right=0.995, top=0.925, bottom=0.115)
axa = fig.add_subplot(gs[:, 0:3])

UM, YM = 2.45, 0.165
uu = np.linspace(0.30, UC, 400)
# regions
axa.fill_between(uu, 0, sep(uu), color=BLUE, alpha=0.07, lw=0, zorder=0)
axa.fill_between(uu, sep(uu), YM, color=RED, alpha=0.06, lw=0, zorder=0)
axa.fill_between([UC, UM], 0, YM, color=GREY, alpha=0.06, lw=0, zorder=0)
# level sets of H
ug = np.linspace(0.30, UM, 500); yg = np.linspace(0, YM, 400); UG, YG = np.meshgrid(ug, yg)
HG = H(UG, YG)
levels = [FC + x for x in (-1.0, -0.6, -0.35, -0.2, -0.1, -0.04, 0.04, 0.1, 0.2, 0.4, 0.7, 1.1, 1.6)]
axa.contour(UG, YG, HG, levels=levels, colors="#9A9A9A", linewidths=0.4, zorder=1)
# separatrix, linearised separatrix
axa.plot(uu, sep(uu), "-", color="#111111", lw=1.7, zorder=4)
ul = np.linspace(0.30, UC, 50); axa.plot(ul, (UC - ul) / pi ** 2, "--", color="#111111", lw=0.9, zorder=4)
# trajectories
n = int(D["n_traj"]); hyp = D["traj_hyp"]; btw = D["traj_between"]
for i in range(n):
    U, Y = D[f"traj{i}_U"], D[f"traj{i}_Y"]
    fam = R["family"][i]
    if fam["hypothesis"]:
        col = BLUE; lw = 0.9
    elif fam["u0"] < UC:
        col = RED; lw = 0.9
    else:
        col = GREY; lw = 0.9
    if btw[i]: col = TEAL; lw = 1.4
    m = (U <= UM) & (np.abs(Y) <= YM)
    axa.plot(U[m], Y[m], "-", color=col, lw=lw, zorder=5, solid_capstyle="round")
    # arrow near the middle of the visible part
    idx = np.nonzero(m)[0]
    if len(idx) > 4:
        j = idx[len(idx) // 2]; j2 = min(j + 1, len(U) - 1)
        if np.hypot(U[j2] - U[j], Y[j2] - Y[j]) > 1e-9:
            axa.annotate("", xy=(U[j2], Y[j2]), xytext=(U[j], Y[j]), arrowprops=dict(arrowstyle="-|>", color=col, lw=0.0, mutation_scale=6), zorder=6)
    if fam["hypothesis"] and np.isfinite(fam["u_star"]):
        axa.plot([fam["u_star"]], [0], "o", ms=2.8, mfc=BLUE, mec="white", mew=0.3, zorder=7, clip_on=False)
axa.plot([UC], [0], "*", ms=9, mfc=GOLD, mec="#111111", mew=0.6, zorder=8, clip_on=False)
axa.set_xlim(0.30, UM); axa.set_ylim(0, YM)
axa.set_xlabel("$u=1/K$"); axa.set_ylabel("fugacity $y$")
sec = axa.secondary_xaxis("top", functions=(lambda u: 2 * pi / np.maximum(u, 1e-9), lambda s_: 2 * pi / np.maximum(s_, 1e-9)))
sec.set_xlabel("$n_s\\lambda_T^2=2\\pi/u$", fontsize=9); sec.set_xticks([3, 4, 6, 10, 20]); sec.tick_params(labelsize=8)
panel(axa, "a")
axa.text(0.335, 0.006, "line of fixed points", fontsize=7.2, color=BLUE, ha="left", va="bottom")
axa.text(1.72, 0.157, "below the separatrix:\n$K\\to0$", fontsize=7.2, color=RED, ha="center", va="top")
axa.text(2.40, 0.03, "disordered side", fontsize=7.2, color=GREY, ha="right", va="center")
axa.annotate("exact separatrix\n$H=f(\\pi/2)$", xy=(1.18, sep(1.18)), xytext=(1.30, 0.108), fontsize=7.2, ha="left", va="bottom", arrowprops=dict(arrowstyle="-", lw=0.5, color="#111111"))
axa.annotate("$(\\pi/2,0)$", xy=(UC, 0), xytext=(1.30, 0.012), fontsize=7.2, ha="right", va="bottom", arrowprops=dict(arrowstyle="-", lw=0.5, color="#111111"))

# ------------------------------------------------------------------ (b) drift
axb = fig.add_subplot(gs[0, 4])
tol = R["tolerance"]
for method, col, mk in (("adams", BLUE, "o"), ("bdf", ORANGE, "s")):
    pts = sorted([(v["rtol"], v["max_drift"]) for k, v in tol.items() if v["method"] == method])
    axb.plot([p[0] for p in pts], [p[1] for p in pts], mk + "-", color=col, ms=3.2, lw=0.9, mfc=col, mec="white", mew=0.3, label=method.upper() if method == "bdf" else "Adams")
ctl = max(R["control_wrong_coeff_drift"])
axb.axhline(ctl, color=RED, lw=0.9, ls="--"); axb.text(0.88e-4, ctl * 0.45, "5 % wrong coefficient", color=RED, fontsize=6.8, ha="left", va="top")
axb.set_xscale("log"); axb.set_yscale("log"); axb.invert_xaxis()
axb.set_xlabel("CVODE rtol"); axb.set_ylabel("$\\max|H(l)-H(0)|$", fontsize=8.5)
log_ticks_plain(axb, "x", [1e-4, 1e-6, 1e-8, 1e-10])
axb.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: "$10^{%d}$" % round(math.log10(v))))
axb.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: "$10^{%d}$" % round(math.log10(v))))
axb.set_ylim(1e-12, 3e1)
axb.legend(loc="lower left", fontsize=6.8, handlelength=1.4, borderaxespad=0.2)
panel(axb, "b")

# ------------------------------------------------------------------ (c) escape times
axc = fig.add_subplot(gs[1, 4])
esc = R["escape"]
bnd = np.array([e["bound"] for e in esc]); cv = np.array([e["cvode"] for e in esc]); qd = np.array([e["quad"] for e in esc])
xx = np.array([3e-2, 5.0]); axc.plot(xx, xx, "--", color=RED, lw=0.9)
axc.plot(bnd, qd, "x", color="#111111", ms=4.5, mew=0.7, label="quadrature", zorder=3)
axc.plot(bnd, cv, "o", ms=3.4, mfc=BLUE, mec="white", mew=0.3, label="CVODE", zorder=4)
axc.set_xscale("log"); axc.set_yscale("log")
axc.set_xlabel("Lean bound $l_1$"); axc.set_ylabel("crossing time of $u=\\pi/2$", fontsize=8.5)
axc.legend(loc="upper left", fontsize=6.8, handlelength=1.0, borderaxespad=0.2)
log_ticks_plain(axc, "x", [0.03, 0.1, 0.3, 1, 3]); log_ticks_plain(axc, "y", [0.03, 0.1, 0.3, 1, 3])
panel(axc, "c")
save(fig, "ch06_portrait")
