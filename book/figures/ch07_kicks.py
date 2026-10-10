"""Chapter 7, Figure 6: the random kicks of a vortex in the closed field.
 (a) the residual mean-square displacement <|e|^2>(tau) of a tracked vortex about the two-coefficient fit, against the lag tau, at the three temperatures
     of the campaign and at T = 0 (the diffusive-scaling check E2: slope 1 on this log-log plot is diffusion);
 (b) the Einstein statistic R_E = eta K / alpha at the same temperatures with the registered window [0.5, 2].
Data: archived campaign (data/generated/pgpe/transport/island_I1_I2.json, production_estimates.json; written by analyze_island.py and
analyze_transport.py).  K = 2 pi n_s / T from the base states; errors of R_E come from eta alone (alpha held fixed), as in the programme's results note."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
from ch07_common import addnum, logfmt
ROOT = Path(__file__).resolve().parents[2]; TR = ROOT / "data/generated/pgpe/transport"
isl = json.loads((TR / "island_I1_I2.json").read_text()); pe = json.loads((TR / "production_estimates.json").read_text())
lags = np.array([5, 10, 20, 40, 80, 120, 160, 240, 320, 400], float)          # the registered lags (pe[...]['lags_eta'] of analyse_tracks)
res = {}
fig = plt.figure(figsize=(TEXTW, 2.35)); gs = fig.add_gridspec(1, 2, wspace=0.34, left=0.085, right=0.99, top=0.95, bottom=0.17)
ax = fig.add_subplot(gs[0, 0])
for key, col, lab in (("0.115", BLUE, r"$0.14$"), ("0.220", TEAL, r"$0.27$"), ("0.353", ORANGE, r"$0.43$")):
    ms = np.array(isl["I1"][key]["msd"], float); ok = np.isfinite(ms); ax.loglog(lags[ok], ms[ok], "o-", color=col, ms=3.0, lw=1.0, label=lab)
    res[f"msd_{key}"] = dict(gamma_20_400=isl["I1"][key]["gamma_20_400"], gamma_se=isl["I1"][key]["gamma_se"], gamma_lags_ge_100=isl["I1"][key]["gamma_lags_ge_100"], eta_if_read=isl["I1"][key]["eta_if_read"],
                             msd_offset=isl["I1"][key]["msd_offset"], msd=[float(x) for x in ms])
ms0 = np.array(pe["T0"]["msd"], float); ok = np.isfinite(ms0); ax.loglog(lags[ok], ms0[ok], "o-", color=GREY, ms=2.6, lw=0.9, label=r"$T=0$")
ax.loglog([20, 400], [0.17, 3.4], "-", color="#BBBBBB", lw=0.7, zorder=0); ax.text(230, 0.55, "slope 1", fontsize=6.6, color=GREY, rotation=33)
ax.set_xlabel(r"lag $\tau$ (time units)"); ax.set_ylabel(r"$\langle|e|^2\rangle$, residual of the fit"); ax.set_ylim(2.5e-3, 6)
ax.yaxis.set_major_formatter(logfmt()); ax.xaxis.set_major_formatter(logfmt()); ax.legend(title=r"$T/T_{\rm BKT}$", title_fontsize=6.6, loc="lower right", bbox_to_anchor=(1.0, 0.16), fontsize=6.8, handlelength=1.4); panel(ax, "a")
ax = fig.add_subplot(gs[0, 1]); ax.axhspan(0.5, 2.0, color=TEAL, alpha=0.13, lw=0); ax.axhline(1.0, color=TEAL, lw=0.8)
RE = {}
for i, (key, quoted) in enumerate((("e0.60", False), ("e0.70", True), ("e0.80", False))):
    e = pe[key]; K = 2 * np.pi * e["ns"] / e["T"]; R = e["eta"] * K / e["alpha_energy"]; Rse = e["eta_se"] * K / e["alpha_energy"]
    RE[key] = dict(T=e["T"], ns=e["ns"], K=float(K), eta=e["eta"], eta_se=e["eta_se"], alpha_energy=e["alpha_energy"], alpha_energy_se=e["alpha_energy_se"], R_E=float(R), R_E_se_from_eta_only=float(Rse),
                   R_E_se_with_alpha_error=float(R * np.hypot(e["eta_se"] / e["eta"], e["alpha_energy_se"] / e["alpha_energy"])), gamma=e["msd_exponent"], quoted=quoted)
    ax.errorbar(i, R, Rse, fmt="o", color=BLUE if quoted else GREY, mfc=BLUE if quoted else "white", ms=5, capsize=2.5, lw=1.0)
    ax.text(i + 0.12, R, rf"${R:.1f}$", fontsize=7, color=BLUE if quoted else GREY, va="center")
    ax.text(i, 0.12, rf"$\gamma={e['msd_exponent']:.2f}$", ha="center", fontsize=7, color=BLUE if quoted else GREY)
ax.set_xticks([0, 1, 2]); ax.set_xticklabels([r"0.14", r"0.27", r"0.43"]); ax.set_xlabel(r"$T/T_{\rm BKT}$"); ax.set_ylabel(r"$R_E=\eta K/\alpha$"); ax.set_ylim(0.0, 4.2); ax.set_xlim(-0.5, 2.5)
ax.text(-0.45, 1.8, "registered window\n$[0.5,2]$", fontsize=6.5, color=TEAL, ha="left", va="top"); ax.text(-0.45, 1.0, "Einstein", fontsize=6.5, color=TEAL, ha="left", va="bottom"); panel(ax, "b")
res["einstein"] = RE
addnum("fig_kicks", res)
save(fig, "ch07_kicks")
