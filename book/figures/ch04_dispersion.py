"""Figure ch04_dispersion: the measured phonon branch of superfluid 4He (P = 0, T < 0.1 K) and the polynomial of Eq. (2) of
Godfrin et al., PRB 103, 104516, with the coefficient set quoted in the arXiv source (c = 238.3 m/s, a2, a3, a4).
Data: ancillary file DispersionP0allRange.txt of arXiv:2012.09067 (CC BY 4.0), through ch04_common.load_dispersion()."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
import ch04_common as cc

k, e = cc.load_dispersion()                              # 1/A, meV
import scipy.constants as _C
HBARC_exact = cc.hbar*cc.c*1e10/(1e-3*_C.e)             # hbar c in meV*A from the SI constants
HBARC = HBARC_exact
HBARC_paper = 0.0065821*cc.c                            # the constant printed in the paper's eps(k) formula (meV, k in 1/A)
a2, a3, a4 = 1.55, -4.04, 2.30
kk = np.linspace(0, 1.6, 600)
poly = lambda x, *a: HBARC*x*(1 + sum(ai*x**(i+2) for i, ai in enumerate(a)))

fig = plt.figure(figsize=(TEXTW, 2.75))
ax = fig.add_axes([0.07, 0.15, 0.40, 0.78]); bx = fig.add_axes([0.58, 0.15, 0.40, 0.78])
# (a) full range
ax.axvspan(0, 0.5, color=GOLD, alpha=0.13, lw=0)
ax.plot(k, e, color=BLUE, lw=1.3, label="measured")
ax.plot(kk, HBARC*kk, color=GREY, lw=1.0, ls=(0, (4, 2)), label=r"Debye $\hbar ck$")
ax.plot(kk, poly(kk, a2, a3, a4), color=ORANGE, lw=1.3, label="polynomial, Eq. (2)")
ax.set_xlim(0, 3.0); ax.set_ylim(0, 1.75)
ax.set_xlabel(r"$k\ (\mathrm{\AA}^{-1})$"); ax.set_ylabel(r"$\varepsilon\ (\mathrm{meV})$")
ax.text(0.25, 1.12, "Eq. $(2)$ quoted valid for $k<0.5$", rotation=90, va="center", ha="center", fontsize=7.4, color="#7a5a10")
ax.annotate("roton\nminimum", xy=(1.92, 0.743), xytext=(1.05, 0.30), fontsize=8.2, color=GREY, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6))
ax.annotate("maxon", xy=(1.114, 1.19), xytext=(1.30, 1.47), fontsize=8.2, color=GREY, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6))
ax.legend(loc="lower right", fontsize=7.2, bbox_to_anchor=(1.01, 0.0)); panel(ax, "a")
# (b) the correction, divided by k^2:  (eps/(hbar c k) - 1)/k^2  = a2 + a3 k + a4 k^2 + ...
m = (k >= 0.06) & (k <= 0.7)
y = (e[m]/(HBARC*k[m]) - 1)/k[m]**2
bx.axvspan(0.15, 0.5, color=GOLD, alpha=0.13, lw=0)
bx.plot(k[m], y, ".", ms=2.2, color=BLUE, label="measured")
ks = np.linspace(0.0, 0.7, 300)
bx.plot(ks, a2 + 0*ks, color=GREY, lw=1.1, ls=(0, (4, 2)), label=r"$\alpha_2$ only")
bx.plot(ks, a2 + a3*ks, color=TEAL, lw=1.3, label=r"$+\alpha_3k$")
bx.plot(ks, a2 + a3*ks + a4*ks**2, color=ORANGE, lw=1.5, label=r"$+\alpha_4k^2$")
bx.set_xlim(0, 0.7); bx.set_ylim(-1.0, 2.4)
bx.set_xlabel(r"$k\ (\mathrm{\AA}^{-1})$"); bx.set_ylabel(r"$(\varepsilon/\hbar ck-1)/k^2\ (\mathrm{\AA}^{2})$")
bx.legend(loc="lower left", fontsize=7.6); panel(bx, "b")
m2_ = (k >= 0.15) & (k <= 0.5); res_ = e[m2_] - poly(k[m2_], a2, a3, a4)
bx.text(0.325, 2.17, "rms deviation of the polynomial\nfrom the data: $%.2f\\,\\mu$eV" % (1e3*np.sqrt(np.mean(res_**2))), fontsize=7.4, color="#7a5a10", va="center", ha="center")
bx.text(0.012, 1.68, r"$\alpha_2=1.55$", fontsize=7.6, color=GREY)
save(fig, "ch04_dispersion")
# numbers
m2 = (k >= 0.15) & (k <= 0.5)
res = (e[m2] - poly(k[m2], a2, a3, a4))
d = dict(hbarc_meV_A_paper_constant=HBARC_paper, hbarc_meV_A_from_SI=HBARC_exact, theta_K_A=cc.THETA, n_points_total=int(len(k)), n_points_window=int(m2.sum()),
         k_window=[0.15, 0.5],
         rms_residual_window_meV=float(np.sqrt(np.mean(res**2))), max_abs_residual_window_meV=float(np.max(np.abs(res))),
         eps_at_0p5_meV=float(e[np.argmin(abs(k-0.5))]), poly_at_0p5_meV=float(poly(0.5, a2, a3, a4)),
         rel_dev_poly_at_1p0=float(poly(1.0, a2, a3, a4)/e[np.argmin(abs(k-1.0))]-1),
         min_du_dk_on_0_3=float(cc.du_dk(np.linspace(0, 3, 30001)).min()),
         maxon_k=float(k[(k > 0.5) & (k < 1.6)][np.argmax(e[(k > 0.5) & (k < 1.6)])]), maxon_meV=float(e[(k > 0.5) & (k < 1.6)].max()),
         roton_k=float(k[(k > 1.5) & (k < 2.4)][np.argmin(e[(k > 1.5) & (k < 2.4)])]), roton_meV=float(e[(k > 1.5) & (k < 2.4)].min()))
d["roton_K"] = d["roton_meV"]*cc.MEV_K; d["maxon_K"] = d["maxon_meV"]*cc.MEV_K
_k, _e, _er = cc.load_dispersion(return_err=True)
d["n_rows_with_uncertainty"] = int(np.sum(~np.isnan(_er))); d["k_first_row_with_uncertainty"] = float(_k[~np.isnan(_er)][0])
_dk = np.round(np.diff(_k), 4); d["n_grid_steps_not_0p002"] = int(np.sum(_dk != 0.002)); d["grid_steps_not_0p002"] = sorted(set(_dk[_dk != 0.002].tolist()))
_bad = np.where(np.abs(np.diff(_k) - 0.002) > 1e-6)[0]; d["grid_uniform_until_k"] = float(_k[_bad[0]]); d["coarse_step"] = float(np.max(_dk))
Path(__file__).with_name("ch04_numbers_dispersion.json").write_text(json.dumps(d, indent=1)); print(d)
