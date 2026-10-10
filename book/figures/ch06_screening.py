"""Figure ch06_screening: the two Lean statements about vortex positions, tested on vortex configurations of the solver.
(a) MatchingScreening.norm_rho_le_matching_torus:  |rho_q(k_1)| / |k_1|  <=  W (optimal matching cost), on 33 PGPE configurations (final fields of the L = 64 and L = 32
    series), on the six L = 192 runs (100 snapshots each), and on one isolated pair;
(b) the polarisability plateau <|rho_q(k)|^2>/k^2 (shells m^2 = 4,...,16) against <sum_i d_i^2>/2 from the optimal matching, six L = 192 runs
    (independent recomputation of the D4 statistic of PGPE_DIELECTRIC_RESULTS.md).
Data: figures/ch06_cert_numbers.json (ch06_certificates.py)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
from ch06_common import *

HERE = Path(__file__).resolve().parent
cert = json.loads((HERE / "ch06_cert_numbers.json").read_text())

fig = plt.figure(figsize=(TEXTW, 2.55))
gs = fig.add_gridspec(1, 2, wspace=0.42, left=0.085, right=0.995, top=0.94, bottom=0.2)

# ------------------------------------------------------------------ (a) matching certificate
axd = fig.add_subplot(gs[0, 0])
fields = cert["fields"]
for Lval, col, mk, lab in ((64.0, BLUE, "o", "PGPE $L=64$"), (32.0, TEAL, "s", "PGPE $L=32$")):
    pts = [(r["W"], r["bound_k1"]) for r in fields if r["L"] == Lval]
    axd.plot([p[0] for p in pts], [p[1] for p in pts], mk, ms=3.3, mfc=col, mec="white", mew=0.3, label=lab, zorder=3)
runs = cert["L192"]
axd.errorbar([r["W_mean"] for r in runs.values()], [r["bound_k1_mean"] for r in runs.values()],
             xerr=[r["W_std"] for r in runs.values()], yerr=[r["bound_k1_std"] for r in runs.values()], fmt="D", ms=3.6, mfc=ORANGE, mec="white", mew=0.3, ecolor=ORANGE, elinewidth=0.6,
             label="PGPE $L=192$", zorder=3)
dd = np.geomspace(0.7, 40, 100); kk1 = 2 * np.pi / 64.0
axd.plot(dd, 2 * np.sin(kk1 * dd / 2) / kk1, "-", color=GOLD, lw=1.0, label="one pair", zorder=2)
xx = np.array([0.5, 3000]); axd.plot(xx, xx, "--", color=RED, lw=0.9, zorder=1)
axd.fill_between(xx, xx, [3000, 3000], color=RED, alpha=0.06, zorder=0)
axd.text(0.85, 120, "forbidden:", color=RED, fontsize=7, ha="left", va="center")
axd.text(0.85, 55, "$|\\rho_q|/|k|>W$", color=RED, fontsize=7, ha="left", va="center")
axd.set_xscale("log"); axd.set_yscale("log"); axd.set_xlim(0.7, 2000); axd.set_ylim(0.5, 800)
axd.set_xlabel("optimal matching cost $W$  [$\\xi$]"); axd.set_ylabel("$|\\rho_q(k_1)|\\,/\\,|k_1|$  [$\\xi$]")
log_ticks_plain(axd, "x", [1, 10, 100, 1000]); log_ticks_plain(axd, "y", [1, 10, 100])
axd.legend(loc="lower right", fontsize=6.8, handlelength=1.2, borderaxespad=0.2, labelspacing=0.25, ncol=1)
panel(axd, "a")

# ------------------------------------------------------------------ (b) D4 polarisability
axe = fig.add_subplot(gs[0, 1])
names = list(runs.keys()); ecol = {"1.00": BLUE, "1.10": TEAL, "1.20": ORANGE}
for n in names:
    r = runs[n]; e = n.split("_e")[1].split("_")[0]
    axe.plot(r["pred"], r["plateau"], "o", ms=4.2, mfc=ecol[e], mec="white", mew=0.4, zorder=3)
xx = np.array([20, 600]); axe.plot(xx, xx, "-", color=GREY, lw=0.8, zorder=1)
axe.plot(xx, 0.79 * xx, ":", color=GREY, lw=0.8, zorder=1); axe.plot(xx, 0.95 * xx, ":", color=GREY, lw=0.8, zorder=1)
for e, col in ecol.items():
    axe.plot([], [], "o", ms=4.2, mfc=col, mec="white", mew=0.4, label=f"$e={e}$")
axe.set_xscale("log"); axe.set_yscale("log"); axe.set_xlim(25, 600); axe.set_ylim(25, 600)
axe.set_xlabel("$\\langle\\sum_i d_i^2\\rangle/2$ from the matching  [$\\xi^2$]"); axe.set_ylabel("$\\langle|\\rho_q(k)|^2\\rangle/k^2$  [$\\xi^2$]")
log_ticks_plain(axe, "x", [30, 100, 300]); log_ticks_plain(axe, "y", [30, 100, 300])
axe.legend(loc="upper left", fontsize=7, handlelength=1.0, borderaxespad=0.2, labelspacing=0.3)
axe.text(0.97, 0.05, "ratio 0.79 to 0.95", transform=axe.transAxes, fontsize=7, ha="right", va="bottom")
panel(axe, "b")
save(fig, "ch06_screening")
