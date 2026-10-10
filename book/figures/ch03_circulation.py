"""Figure ch03_circulation: counting quanta on the solver field (pair d = 12, t = 20, loops centred on the + vortex).
(a) circulation Gamma/kappa of the Madelung velocity along circles of radius R (line integral) and the winding found by the Lean-verified
principal-difference detector; (b) distance of Gamma/kappa from the nearest integer; (c) how many samples the detector needs (the n_0 of
`detector_correct`); (d) the velocity along the line through both cores against the periodic point-vortex field.
Data: figures/ch03_derived.npz and ch03_numbers.json written by ch03_compute.py."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
HERE = Path(__file__).resolve().parent
D = np.load(HERE / "ch03_derived.npz"); J = json.loads((HERE / "ch03_numbers.json").read_text())["pair"]
d = J["separation_d"]
R = D["circ_R"]; gam = D["circ_gamma"]; win = D["circ_winding"]
order = np.argsort(R); R, gam, win = R[order], gam[order], win[order]

fig, axs = plt.subplots(2, 2, figsize=(TEXTW, 3.95), gridspec_kw=dict(hspace=0.42, wspace=0.34, left=0.095, right=0.985, top=0.965, bottom=0.095))
axa, axb, axc, axd = axs.ravel()
# (a)
axa.axvline(d, color=GREY, lw=0.8, ls=":")
axa.axhline(1, color="#BBBBBB", lw=0.6); axa.axhline(0, color="#BBBBBB", lw=0.6)
axa.plot(R, gam, "-", color=BLUE, lw=1.3, label=r"$\Gamma/\kappa=\oint\mathbf{u}\cdot d\mathbf{l}\,/\,\kappa$")
axa.plot(R, win, "o", ms=3.0, mfc="none", mec=ORANGE, mew=0.8, label="winding, principal differences")
axa.set_xscale("log"); axa.set_xlim(0.12, 40); axa.set_ylim(-0.25, 1.45)
axa.set_xticks([0.2, 1, 5, 20]); axa.set_xticklabels(["0.2", "1", "5", "20"]); axa.minorticks_off()
axa.set_xlabel(r"loop radius $R/\xi$"); axa.set_ylabel(r"circulation $\Gamma/\kappa$")
axa.text(0.35, 1.12, r"$+1$", color=BLUE, fontsize=9); axa.text(18, 0.10, r"$0$", color=BLUE, fontsize=9)
axa.text(d * 1.06, 1.18, r"$R=d$", color=GREY, fontsize=8)
axa.legend(loc="lower left", bbox_to_anchor=(0.0, 0.30), fontsize=7.2, handlelength=1.4, borderaxespad=0.2)
panel(axa, "a")
# (b)
err = np.abs(gam - np.rint(gam))
axb.semilogy(R, np.maximum(err, 1e-17), "o", ms=2.8, color=BLUE)
axb.axvline(d, color=GREY, lw=0.8, ls=":")
axb.set_xscale("log"); axb.set_xlim(0.12, 40); axb.set_ylim(1e-17, 1e-1)
axb.set_xticks([0.2, 1, 5, 20]); axb.set_xticklabels(["0.2", "1", "5", "20"])
axb.set_yticks([1e-16, 1e-12, 1e-8, 1e-4]); axb.set_yticklabels([r"$\mathrm{10^{-16}}$", r"$\mathrm{10^{-12}}$", r"$\mathrm{10^{-8}}$", r"$\mathrm{10^{-4}}$"]); axb.minorticks_off()
axb.set_xlabel(r"loop radius $R/\xi$"); axb.set_ylabel(r"$|\Gamma/\kappa-\mathrm{round}|$")
axb.text(0.16, 3e-13, "quadrature\nround-off", fontsize=7.5, color=GREY)
axb.text(d * 1.1, 3e-4, "loop touches\nthe other core", fontsize=7.5, color=GREY)
panel(axb, "b")
# (c) n0: smallest sampling from which the detector is right, other core outside / inside the loop
n0 = J["n0_scan"]["rows"]
out_ = [r for r in n0 if r["side"] == "zero_outside"]; in_ = [r for r in n0 if r["side"] == "zero_inside"]
dd = np.geomspace(0.04, 10, 80)
axc.loglog(dd, np.maximum(3, np.pi * np.sqrt(np.maximum(d - dd, 1e-9) / dd)), "-", color=GREY, lw=0.9, label=r"$\pi\sqrt{R/\delta}$")
axc.loglog([r["delta"] for r in out_], [r["M0_worst"] for r in out_], "o", ms=4.2, color=BLUE, label="other core outside the loop")
axc.loglog([r["delta"] for r in in_], [r["M0_worst"] for r in in_], "s", ms=4.2, color=ORANGE, mfc="none", label="other core inside the loop")
axc.axhline(3, color="#BBBBBB", lw=0.7, ls="--")
axc.set_xlabel(r"distance $\delta$ of the loop to the other core $(\xi)$"); axc.set_ylabel(r"samples $M_0$ needed")
axc.set_xlim(0.035, 12); axc.set_ylim(2.2, 90)
axc.set_xticks([0.05, 0.2, 1, 5]); axc.set_xticklabels(["0.05", "0.2", "1", "5"]); axc.set_yticks([3, 10, 30]); axc.set_yticklabels(["3", "10", "30"]); axc.minorticks_off()
axc.legend(loc="upper right", fontsize=6.6, handlelength=1.2, borderaxespad=0.2)
panel(axc, "c")
# (d) speed against distance from the + core, along the line through both cores, on the side away from the partner
x = D["cut_x"]; ugp = D["cut_uy_gp"]; upv = D["cut_uy_pv"]; ycut = float(D["cut_y"])
xp, yp = J["vortex_plus"]
sel = (x < xp - 0.1) & (x > xp - 13.0)
rr = np.hypot(xp - x[sel], ycut - yp)
axd.loglog(rr, 1 / rr, ":", color=GREY, lw=1.0, label=r"$\kappa/2\pi r$")
axd.loglog(rr, np.abs(upv[sel]), "--", color=ORANGE, lw=1.4, label="point vortices + torus mean flow")
axd.loglog(rr, np.abs(ugp[sel]), "-", color=BLUE, lw=1.1, label="solver")
axd.set_xlabel(r"distance $r/\xi$ from the $+$ core (away from the partner)"); axd.set_ylabel(r"speed $|u|\;(\hbar/m\xi)$")
axd.set_yticks([0.1, 1, 5]); axd.set_yticklabels(["0.1", "1", "5"]); axd.minorticks_off()
axd.legend(loc="upper right", fontsize=6.6, handlelength=1.4, borderaxespad=0.2)
ax2 = axd.twinx(); ax2.spines["right"].set_visible(True)
rel = np.abs(ugp[sel] - upv[sel]) / np.abs(upv[sel])
ax2.loglog(rr, np.maximum(rel, 1e-5), "-", color=GOLD, lw=0.9)
ax2.set_ylim(1e-4, 3.0); ax2.set_ylabel("relative difference", color=GOLD, fontsize=8); ax2.tick_params(axis="y", colors=GOLD, labelsize=7)
ax2.set_yticks([1e-3, 1e-2, 1e-1, 1]); ax2.set_yticklabels(["0.001", "0.01", "0.1", "1"]); ax2.minorticks_off()
axd.set_xlim(0.12, 14)
axd.set_xticks([0.2, 1, 5, 10]); axd.set_xticklabels(["0.2", "1", "5", "10"]); axd.minorticks_off()    # after the twin axis: ax2.loglog resets the shared x ticker
panel(axd, "d")
save(fig, "ch03_circulation")
