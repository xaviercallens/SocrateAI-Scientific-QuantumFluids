"""Figure ch04_heatmap: which excitations carry the heat?  The distribution of the specific heat over the wavevector k of the
elementary excitation, w(k, T) = (V k_B / 2 pi^2) k^2 f(eps(k)/k_B T) / C_V(T), computed from the MEASURED dispersion table
(arXiv:2012.09067 ancillary file, CC BY 4.0), integration limit k_end = 3.6 / A as in the table.  Plotted per unit ln k so that
each column integrates to one.  Contours: wavevectors below which 10 / 50 / 90 % of the heat capacity sits.
Panel (b): the fraction of C_V that comes from k > 0.5 / A, the wavevector up to which the polynomial of Eq. (2) was fitted."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
from matplotlib.colors import LinearSegmentedColormap, PowerNorm
import ch04_common as cc
from scipy.interpolate import CubicSpline
from scipy.integrate import cumulative_trapezoid

kd, ed = cc.load_dispersion()
spl = CubicSpline(kd, ed*cc.MEV_K)                    # eps/k_B in kelvin
K0 = 0.002
ik = np.geomspace(K0, kd[-1], 2400)                   # log-spaced wavevector grid; the sliver 0 < k < K0 is added analytically (f = 1)
eps = spl(ik)
Ts = np.geomspace(0.05, 1.3, 220)
lnk = np.log(ik)
sliver = cc.PREF*K0**3/3
W = np.zeros((len(ik), len(Ts)))
cv = np.zeros(len(Ts))
cum = np.zeros((len(ik), len(Ts)))
for j, T in enumerate(Ts):
    wl = cc.PREF*ik**3*cc.bose_weight(eps/T)             # density per unit ln k
    tot = np.trapezoid(wl, lnk) + sliver
    cv[j] = tot
    W[:, j] = wl/tot
    cum[:, j] = (cumulative_trapezoid(wl, lnk, initial=0.0) + sliver)/tot
frac_above = 1.0 - np.array([np.interp(0.5, ik, cum[:, j]) for j in range(len(Ts))])
frac_above_0p25 = 1.0 - np.array([np.interp(0.25, ik, cum[:, j]) for j in range(len(Ts))])
q = {p: np.array([np.interp(p, cum[:, j], ik) for j in range(len(Ts))]) for p in (0.1, 0.5, 0.9)}

fig = plt.figure(figsize=(TEXTW, 3.25))
ax = fig.add_axes([0.075, 0.13, 0.50, 0.80]); bx = fig.add_axes([0.70, 0.13, 0.285, 0.80])
cmap = LinearSegmentedColormap.from_list("heat", ["#FFFFFF", "#F3E3C3", "#E8B07A", ORANGE, RED, "#4A1B14"], N=256)
im = ax.pcolormesh(Ts, ik, W, cmap=cmap, norm=PowerNorm(0.55, vmin=0, vmax=np.percentile(W, 99.8)), shading="auto", rasterized=True)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(Ts[0], Ts[-1]); ax.set_ylim(0.012, 3.6)
for p, ls, lab in ((0.9, (0, (5, 2)), "90 %"), (0.5, "-", "50 %"), (0.1, (0, (2, 2)), "10 %")):
    ax.plot(Ts, q[p], color=BLUE, lw=1.0 if p != 0.5 else 1.4, ls=ls, label=lab)
ax.legend(loc="lower right", fontsize=7.3, title="share of $C_V$ at wavevectors\nbelow the curve", title_fontsize=7.3, handlelength=2.2, labelspacing=0.25)
ax.axhline(0.5, color=GREY, lw=0.8, ls=(0, (6, 3))); ax.text(0.052, 0.54, r"end of the fit window  $k=0.5\ \mathrm{\AA}^{-1}$", fontsize=7.6, color=GREY, va="bottom")
ax.axhline(1.114, color=GREY, lw=0.5, ls=":"); ax.text(0.052, 1.19, "maxon", fontsize=7.6, color=GREY, va="bottom")
ax.axhline(1.92, color=GREY, lw=0.5, ls=":"); ax.text(0.052, 2.07, "roton minimum", fontsize=7.6, color=GREY, va="bottom")
ax.set_xlabel("temperature  $T$ (K)"); ax.set_ylabel(r"wavevector  $k\ (\mathrm{\AA}^{-1})$")
ax.set_xticks([0.05, 0.1, 0.2, 0.5, 1.0]); ax.set_xticklabels(["0.05", "0.1", "0.2", "0.5", "1"])
ax.set_yticks([0.02, 0.05, 0.1, 0.2, 0.5, 1, 2]); ax.set_yticklabels(["0.02", "0.05", "0.1", "0.2", "0.5", "1", "2"])
ax.minorticks_off()
ax.text(0.06, 0.035, "phonons", fontsize=8.5, color=RED, rotation=33, fontweight="bold")
ax.text(0.80, 2.75, "rotons", fontsize=8.5, color=RED, fontweight="bold")
panel(ax, "a")
cax = fig.add_axes([0.085, 0.935, 0.18, 0.016]); cb = fig.colorbar(im, cax=cax, orientation="horizontal"); cb.set_ticks([]); cax.set_title("weight per $\\ln k$", fontsize=7.5, pad=2)
# (b)
bx.plot(Ts, 100*frac_above_0p25, color=TEAL, lw=1.2, label=r"$k_0=0.25\ \mathrm{\AA}^{-1}$")
bx.plot(Ts, 100*frac_above, color=ORANGE, lw=1.6, label=r"$k_0=0.5\ \mathrm{\AA}^{-1}$")
bx.set_xscale("log"); bx.set_yscale("log"); bx.set_xlim(0.05, 1.3); bx.set_ylim(1e-6, 100)
bx.set_xlabel("temperature  $T$ (K)"); bx.set_ylabel(r"share of $C_V$ carried by modes with $k>k_0$ (%)")
bx.set_xticks([0.05, 0.1, 0.2, 0.5, 1.0]); bx.set_xticklabels(["0.05", "0.1", "0.2", "0.5", "1"]); bx.minorticks_off()
bx.set_yticks([1e-6, 1e-4, 1e-2, 1, 1e2]); bx.set_yticklabels([r"$10^{-6}$", r"$10^{-4}$", r"$10^{-2}$", r"$1$", r"$10^{2}$"])
bx.legend(loc="lower right", fontsize=7.6); bx.grid(True, which="major", axis="y"); panel(bx, "b")
save(fig, "ch04_heatmap")

def at(T, arr): return float(np.interp(np.log(T), np.log(Ts), arr))
d = dict(n_T=len(Ts), k_end=float(kd[-1]),
         share_above_0p5_percent={f"{T}": 100*at(T, frac_above) for T in (0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.3)},
         share_above_0p25_percent={f"{T}": 100*at(T, frac_above_0p25) for T in (0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.3)},
         median_k={f"{T}": at(T, q[0.5]) for T in (0.1, 0.3, 0.5, 1.0, 1.3)}, q90_k={f"{T}": at(T, q[0.9]) for T in (0.1, 0.3, 0.5, 1.0, 1.3)},
         cv_trapz_J_per_mol_K={f"{T}": at(T, cv) for T in (0.1, 0.5, 1.0, 1.3)})
Path(__file__).with_name("ch04_numbers_heatmap.json").write_text(json.dumps(d, indent=1)); print(json.dumps(d, indent=1))
