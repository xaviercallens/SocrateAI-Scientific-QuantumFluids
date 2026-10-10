"""Figure ch06_jump: the universal jump of the stiffness and the essential singularity, in the RG flow integrated with CVODE.
(a) renormalised n_s lambda^2 = 2 pi K_R against the bare u0 = 1/K0 at fixed y0 = 0.03: exact (root of f(u*) = H0, Lean invariant) and CVODE chain to l = 80; the jump 4 -> 0
    sits at u0c;  (b) the same flow stopped at l = ln(L/a): the jump is rounded and its crossing of 4 moves to larger u0 (higher temperature) in a small box;
(c) the essential singularity: RG time l* to leave the critical region against 1/a, a^2 = (pi/2)(f(pi/2) - H0): CVODE and the exact quadrature against pi^2/(4a).
Data: ch06_flow_numbers.json (ch06_flow_compute.py)."""
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
from ch06_common import *

HERE = Path(__file__).resolve().parent
R = json.loads((HERE / "ch06_flow_numbers.json").read_text())
pi = math.pi

fig = plt.figure(figsize=(TEXTW, 2.15))
gs = fig.add_gridspec(1, 3, wspace=0.55, left=0.075, right=0.995, top=0.93, bottom=0.2)

# ---------------------------------------------------------------- (a) jump
axa = fig.add_subplot(gs[0, 0])
J = R["jump"]; K0 = np.array(J["K0"]); KR = np.array(J["KR_inv"]); u0 = 1 / K0
order = np.argsort(u0)
axa.plot(u0[order], (2 * pi * K0)[order], ":", color=GREY, lw=0.9, label="bare $2\\pi K_0$", zorder=1)
axa.plot(u0[order], (2 * pi * KR)[order], "-", color=BLUE, lw=1.3, label="exact", zorder=2)
Kc = np.array(J["K0_cv"]); KRc = np.array(J["KR_cv"])
axa.plot(1 / Kc, 2 * pi * KRc, "o", ms=3.0, mfc=ORANGE, mec="white", mew=0.3, label="CVODE", zorder=3)
axa.axhline(4, color=RED, lw=0.7, ls="--")
axa.axvline(J["u0c"], color=GREY, lw=0.5, ls=":")
axa.text(2.38, 4.2, "4", color=RED, fontsize=7.5, ha="right", va="bottom")
axa.set_xlim(0.9, 2.4); axa.set_ylim(0, 8.5)
axa.set_xlabel("bare $u_0=1/K_0\\ (\\propto T)$"); axa.set_ylabel("$n_s\\lambda_T^2$ after the flow", fontsize=8.5)
axa.legend(loc="upper right", fontsize=6.6, handlelength=1.3, borderaxespad=0.15, labelspacing=0.25)
panel(axa, "a")

# ---------------------------------------------------------------- (b) finite box
axb = fig.add_subplot(gs[0, 1])
FB = R["finite_box"]; K0e = np.array(FB["K0"]); cols = {"16": TEAL, "64": GOLD, "256": ORANGE, "4096": RED}
for key in ("16", "64", "256", "4096"):
    v = np.array(FB["runs"][key]["nslam2"])
    axb.plot((1 / K0e), v, "-", color=cols[key], lw=1.0, label=f"$L/a={key}$")
axb.plot(u0[order], (2 * pi * KR)[order], "-", color="#111111", lw=1.0, label="$\\infty$")
axb.axhline(4, color=RED, lw=0.6, ls="--")
axb.set_xlim(1.0, 1.5); axb.set_ylim(0, 8.5)
axb.set_xlabel("bare $u_0$"); axb.set_ylabel("$n_s\\lambda_T^2$ at $l=\\ln(L/a)$", fontsize=8.5)
axb.legend(loc="upper right", fontsize=6.2, handlelength=1.1, borderaxespad=0.1, labelspacing=0.2, ncol=1)
panel(axb, "b")

# ---------------------------------------------------------------- (c) essential singularity
axc = fig.add_subplot(gs[0, 2])
E = R["essential"]["rows"]
a = np.array([e["a"] for e in E]); lq = np.array([e["l_quad"] for e in E]); lc = np.array([e["l_cvode"] for e in E])
xx = np.geomspace(a.min() * 0.7, a.max() * 1.4, 50)
axc.plot(1 / xx, math.pi ** 2 / (4 * xx), "-", color=GREY, lw=1.0, label="$\\pi^2/(4a)$")
axc.plot(1 / a, lq, "x", color="#111111", ms=4.5, mew=0.8, label="quadrature", zorder=3)
axc.plot(1 / a, lc, "o", ms=3.2, mfc=BLUE, mec="white", mew=0.3, label="CVODE", zorder=4)
axc.set_xscale("log"); axc.set_yscale("log")
axc.set_xlabel("$1/a\\ (a\\propto\\sqrt{T-T_c})$"); axc.set_ylabel("RG time $l^*$ to leave", fontsize=8.5)
axc.legend(loc="upper left", fontsize=6.6, handlelength=1.2, borderaxespad=0.15, labelspacing=0.25)
log_ticks_plain(axc, "x", [1, 10, 100, 1000]); log_ticks_plain(axc, "y", [3, 10, 100, 1000])
panel(axc, "c")
save(fig, "ch06_jump")
