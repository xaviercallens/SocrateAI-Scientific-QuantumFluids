"""Figures ch05_solver and ch05_universal from the broadband runs of ch05_dispersion_run.py (results in ch05_results.npz).

ch05_solver:   (a) all 3208 frequencies of the N = 128 projected GPE against the Bogoliubov curve (hbar = m = n0 = g = 1);
               (b) relative deviation of every mode, for g = 1 and g = 2;
               (c) the Lean error band: (omega - c k (1 + a2 k^2)) / (c a2^2 k^5 / 2) must lie in [-1, 0] (a2 = 1/(8 m^2 c^2));
               (d) the time-step ladder: |omega(dt) - omega(0.005)| / omega, fourth order.
ch05_universal: (a) spectral-intensity map of the pulse record in the (k, omega) plane; (b) omega/(c k) against k/(2 m c): the g = 1 and
               g = 2 runs collapse on sqrt(1 + x^2), and the helium table does not.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
plt.rcParams["axes.unicode_minus"] = False
from matplotlib.colors import LinearSegmentedColormap, LogNorm
import ch05_helium as H
from ch05_common import bog

HERE = Path(__file__).resolve().parent
from matplotlib.ticker import FuncFormatter, NullFormatter
_SUP = {"-": "\u207b", "0": "\u2070", "1": "\u00b9", "2": "\u00b2", "3": "\u00b3", "4": "\u2074", "5": "\u2075", "6": "\u2076", "7": "\u2077", "8": "\u2078", "9": "\u2079"}
def pow10(e):
    return "10" + "".join(_SUP[ch] for ch in str(e))
def set_log_ticks(ax, axis, values, labels=None):
    """fixed tick positions on a log axis with plain-text labels (matplotlib's mathtext minus is missing from the house font)"""
    labels = labels or [f"{v:g}" for v in values]
    if axis == "x":
        ax.set_xticks(values); ax.set_xticklabels(labels); ax.xaxis.set_minor_formatter(NullFormatter())
    else:
        ax.set_yticks(values); ax.set_yticklabels(labels); ax.yaxis.set_minor_formatter(NullFormatter())
D = np.load(HERE / "ch05_results.npz")
LOG = json.load(open(HERE / "ch05_run_log.json"))
k1, w1 = D["R1_k"], D["R1_omega"]
k2, w2 = D["R2_k"], D["R2_omega"]
dev1 = w1 / bog(k1, 1.0) - 1
dev2 = w2 / bog(k2, 2.0) - 1
out = {}

# ============================================================== figure ch05_solver
fig = plt.figure(figsize=(TEXTW, 4.95))
a = fig.add_axes([0.085, 0.575, 0.40, 0.385]); b = fig.add_axes([0.585, 0.575, 0.395, 0.385])
c = fig.add_axes([0.085, 0.085, 0.40, 0.385]); d = fig.add_axes([0.585, 0.085, 0.395, 0.385])

# (a) the dispersion relation, log-log
kk = np.logspace(np.log10(0.08), np.log10(3.4), 300)
a.plot(kk, kk, color=GREY, lw=0.9, ls=(0, (1, 2)))
a.plot(kk, kk ** 2 / 2, color=GREY, lw=0.9, ls=(0, (1, 2)))
a.plot(k1, w1, ".", ms=1.6, color=ORANGE, alpha=0.55, rasterized=True, zorder=3)
a.plot(kk, bog(kk, 1.0), color="#222222", lw=0.9, zorder=4)
a.axvline(2.0, color=GOLD, lw=0.8, ls=(0, (4, 2)))
a.text(1.93, 0.115, r"$k_\ast=2mc/\hbar$", color="#7a5a10", fontsize=7.6, ha="right", va="bottom")
a.text(0.095, 0.145, r"$ck$", color=GREY, fontsize=8.2, ha="left", va="bottom", rotation=29)
a.text(1.0, 0.35, r"$k^2/2m$", color=GREY, fontsize=8.2, ha="left", va="center", rotation=44)
a.text(0.10, 3.4, r"%d modes," "\n" r"$N=128,\ L=64$" % len(k1), color=ORANGE, fontsize=7.8, ha="left", va="center")
a.set_xscale("log"); a.set_yscale("log"); a.set_xlim(0.08, 3.5); a.set_ylim(0.08, 8.0)
set_log_ticks(a, "x", [0.1, 0.3, 1, 3]); set_log_ticks(a, "y", [0.1, 0.3, 1, 3])
a.set_xlabel(r"$k$ (units of $1/\xi$, $\xi=\hbar/mc$)"); a.set_ylabel(r"$\omega(k)$ ($c/\xi$)")
panel(a, "a")

# (b) deviation of every mode from the Bogoliubov frequency, in parts per million
b.axhline(0, color=GREY, lw=0.7)
b.plot(k1, 1e6 * dev1, ".", ms=1.8, color=ORANGE, alpha=0.55, rasterized=True)
b.plot(k2 / np.sqrt(2.0) * 1.0, 1e6 * dev2, ".", ms=1.8, color=RED, alpha=0.55, rasterized=True)   # same plot axis: k in units of 1/xi with xi = hbar/(m c), c = sqrt 2
b.set_xscale("log"); b.set_xlim(0.08, 3.5); set_log_ticks(b, "x", [0.1, 0.3, 1, 3])
b.set_yscale("symlog", linthresh=1.0, linscale=0.6); b.set_ylim(-60, 60)
b.set_yticks([-10, -1, 0, 1, 10]); b.set_yticklabels(["-10", "-1", "0", "1", "10"])
b.text(0.095, 20, r"$g=1$", color=ORANGE, fontsize=8, ha="left", va="center")
b.text(0.095, 8.5, r"$g=2$", color=RED, fontsize=8, ha="left", va="center")
med1 = float(np.median(np.abs(dev1))); med2 = float(np.median(np.abs(dev2)))
b.text(3.4, -22, f"median $|\\delta|$ = {1e6 * med1:.2f} ppm", color=ORANGE, fontsize=7.6, ha="right", va="center")
b.text(3.4, -7.5, f"median $|\\delta|$ = {1e6 * med2:.2f} ppm", color=RED, fontsize=7.6, ha="right", va="center")
b.set_xlabel(r"$k$ (units of $1/\xi$)"); b.set_ylabel(r"$(\omega_{\rm meas}/\omega_{\rm Bog}-1)\times10^{6}$")
panel(b, "b")

# (c) the proved band
a2 = 1 / 8.0
half = 0.5 * a2 ** 2 * k1 ** 5
z = (w1 - k1 * (1 + a2 * k1 ** 2)) / half
s = k1 >= 0.3
t = a2 * kk ** 2
zex = (np.sqrt(1 + 2 * t) - 1 - t) / (t ** 2 / 2)
c.axhspan(-1, 0, color=GOLD, alpha=0.14, lw=0)
c.axhline(-1, color="#7a5a10", lw=0.9); c.axhline(0, color="#7a5a10", lw=0.9)
c.plot(k1[s], z[s], ".", ms=1.8, color=ORANGE, alpha=0.6, rasterized=True)
c.plot(kk[kk >= 0.3], zex[kk >= 0.3], color="#222222", lw=1.0)
c.text(3.4, -0.045, "upper bound", fontsize=7.4, color="#7a5a10", ha="right", va="top")
c.text(3.4, -1.045, "lower bound", fontsize=7.4, color="#7a5a10", ha="right", va="top")
c.text(1.0, -0.62, "exact Bogoliubov", fontsize=7.6, color="#222222", ha="left", va="center")
c.set_xscale("log"); c.set_xlim(0.3, 3.5); c.set_ylim(-1.45, 0.25); set_log_ticks(c, "x", [0.3, 0.5, 1, 2, 3])
c.set_xlabel(r"$k$ (units of $1/\xi$)"); c.set_ylabel(r"$(\omega-ck(1+\alpha_2k^2))\,/\,(c\alpha_2^2k^5/2)$")
panel(c, "c")
sb = k1 >= 0.5
out["band"] = dict(n_k_ge_0p5=int(sb.sum()), fraction_inside_k_ge_0p5=float(np.mean((z[sb] >= -1) & (z[sb] <= 0))),
                   z_min_k_ge_0p5=float(z[sb].min()), z_max_k_ge_0p5=float(z[sb].max()),
                   max_abs_z_minus_exact_k_ge_0p5=float(np.abs(z[sb] - ((np.sqrt(1 + 2 * a2 * k1[sb] ** 2) - 1 - a2 * k1[sb] ** 2) / ((a2 * k1[sb] ** 2) ** 2 / 2))).max()),
                   n_k_ge_0p3=int(s.sum()), fraction_inside_k_ge_0p3=float(np.mean((z[s] >= -1) & (z[s] <= 0))),
                   z_min_k_ge_0p3=float(z[s].min()))

# (d) time-step ladder: differences to the finest run, same initial pulse
ref = D["R3_dt0.005_omega"]; kr = D["R3_dt0.005_k"]; wbr = bog(kr, 1.0)
dts = [0.04, 0.02, 0.01]
med = []; mx = []
for dt in dts:
    dd = np.abs(D[f"R3_dt{dt}_omega"] - ref) / wbr
    med.append(float(np.median(dd))); mx.append(float(dd.max()))
d.loglog(dts, mx, "s-", color=ORANGE, ms=4.2, lw=1.2, label="max over modes")
d.loglog(dts, med, "o-", color=BLUE, ms=4.2, lw=1.2, label="median")
g4 = np.array([0.01, 0.04])
d.loglog(g4, med[-1] * (g4 / dts[-1]) ** 4 * 0.45, color=GREY, lw=0.9, ls=(0, (4, 2)))
d.text(0.0165, 1.15e-8, r"$\propto \Delta t^{4}$", color=GREY, fontsize=8.2, ha="left", va="center", rotation=36)
d.axhline(med1, color=ORANGE, lw=0.8, ls=(0, (1, 2)))
d.text(0.0102, med1 * 1.35, "median deviation from Bogoliubov (b)", color=ORANGE, fontsize=7.2, ha="left", va="bottom")
d.set_xlim(0.0085, 0.05); d.set_ylim(5e-10, 4e-6)
set_log_ticks(d, "x", [0.01, 0.02, 0.04]); set_log_ticks(d, "y", [1e-9, 1e-8, 1e-7, 1e-6], ["1e-9", "1e-8", "1e-7", "1e-6"])
d.set_xlabel(r"time step $\Delta t$"); d.set_ylabel(r"$|\omega(\Delta t)-\omega(0.005)|/\omega$")
d.legend(loc="lower right", fontsize=7.4, handlelength=1.4, bbox_to_anchor=(1.0, 0.0))
panel(d, "d")
ratio1 = med[0] / med[1]; ratio2 = med[1] / med[2]
out["dt_ladder"] = dict(dts=dts, median=med, max=mx, ratio_004_over_002=ratio1, ratio_002_over_001=ratio2, reference_dt=0.005)
out["R1"] = dict(median_abs_dev=med1, p99=float(np.quantile(np.abs(dev1), 0.99)), max=float(np.abs(dev1).max()), n=int(len(k1)),
                 median_abs_dev_k_ge_2p5=float(np.median(np.abs(dev1[k1 >= 2.5]))), median_abs_dev_k_lt_0p4=float(np.median(np.abs(dev1[k1 < 0.4]))),
                 median_signed=float(np.median(dev1)))
out["R2"] = dict(median_abs_dev=med2, max=float(np.abs(dev2).max()), n=int(len(k2)))
save(fig, "ch05_solver")

# ============================================================== figure ch05_universal
fig = plt.figure(figsize=(TEXTW, 3.05))
a = fig.add_axes([0.075, 0.15, 0.50, 0.79]); b = fig.add_axes([0.69, 0.15, 0.295, 0.79])
MAPFILE = HERE / "ch05_map.npz"
SERIES = Path("/mnt/data/xdev-cache/book_ch05/series_R1.npz")
if SERIES.exists():                                              # (re)build the smoothed map from the per-mode records of run R1
    ser = np.load(SERIES)
    S = ser["S"].astype(np.complex128); ks = ser["k"]
    nfft = 4 * S.shape[0]
    F = np.fft.fft(S * np.hanning(S.shape[0])[:, None], n=nfft, axis=0)
    P = np.abs(F) ** 2
    fr = 2 * np.pi * np.fft.fftfreq(nfft, d=0.4)
    ipos = np.nonzero((fr > 0) & (fr < 6.3))[0]
    Pf = P[ipos] + P[(-ipos) % nfft]                             # +w and -w folded together
    wf = fr[ipos]
    kgrid = np.linspace(0.0, np.pi, 420)
    SIGK = 0.03                                                  # Gaussian resolution in k (display only)
    W = np.exp(-0.5 * ((kgrid[:, None] - ks[None, :]) / SIGK) ** 2)
    Mapw = W @ Pf.T                                              # (nk, nw)
    Mapw /= np.maximum(Mapw.max(axis=1, keepdims=True), 1e-300)
    np.savez_compressed(MAPFILE, kgrid=kgrid, wf=wf, Mapw=Mapw.astype(np.float32), sigk=SIGK)
mp = np.load(MAPFILE)
kgrid, wf, Mapw = mp["kgrid"], mp["wf"], mp["Mapw"].astype(float)
Z = np.clip(Mapw, 1e-3, None)
cm = LinearSegmentedColormap.from_list("qfseq", ["#0c1d33", BLUE, TEAL, GOLD, "#FFF6DC"], N=256)
im = a.pcolormesh(kgrid, wf, Z.T, cmap=cm, norm=LogNorm(vmin=1e-3, vmax=1.0), shading="auto", rasterized=True)
kc = np.linspace(0.02, np.pi, 300)
a.plot(kc, bog(kc, 1.0), color="white", lw=1.0, ls=(0, (5, 3)), alpha=0.9)
a.plot(kc, kc, color="white", lw=0.8, ls=(0, (1, 2.5)), alpha=0.9)
a.plot(kc, kc ** 2 / 2, color="white", lw=0.8, ls=(0, (1, 2.5)), alpha=0.9)
a.text(0.12, 0.55, r"$ck$", color="white", fontsize=8, ha="left", va="bottom", rotation=29)
a.text(2.15, 1.55, r"$k^2/2m$", color="white", fontsize=8, ha="left", va="top", rotation=52)
a.text(1.05, 3.7, "Bogoliubov", color="white", fontsize=8.2, ha="center", va="center", rotation=47)
a.set_xlim(0, np.pi); a.set_ylim(0, 6.2)
a.set_xlabel(r"$k$ ($1/\xi$)"); a.set_ylabel(r"$\omega$ ($c/\xi$)")
a.text(0.04, 5.95, r"spectral intensity of a weak random pulse ($N=128$)", color="white", fontsize=7.8, ha="left", va="top")
cax = a.inset_axes([0.05, 0.775, 0.30, 0.028])
cb = fig.colorbar(im, cax=cax, orientation="horizontal"); cb.set_ticks([1e-3, 1e-2, 1e-1, 1]); cb.set_ticklabels(["1e-3", "1e-2", "0.1", "1"])
cb.ax.tick_params(labelsize=6.5, length=2, colors="white", pad=1); cb.outline.set_edgecolor("white")
a.text(0.20, 0.84, "normalised at each $k$", transform=a.transAxes, color="white", fontsize=6.6, ha="center", va="bottom")
panel(a, "a")

# (b) universal coordinates  x = k/k*,  y = omega/(c k)
xs = np.linspace(0, 1.65, 300)
b.plot(xs, np.sqrt(1 + xs ** 2), color=TEAL, lw=1.3, ls=(0, (5, 2)), zorder=5)
kt, et, _ = H.load_table()
m = kt >= 0.15
b.plot(kt[m] / H.KSTAR, et[m] / (H.HBARC * kt[m]), color=BLUE, lw=1.4, zorder=4)
x1 = k1 / 2.0; y1 = w1 / k1
x2 = k2 / (2 * np.sqrt(2.0)); y2 = w2 / (np.sqrt(2.0) * k2)
b.plot(x1, y1, ".", ms=1.4, color=ORANGE, alpha=0.5, rasterized=True, zorder=3)
b.plot(x2, y2, ".", ms=1.6, color=RED, alpha=0.6, rasterized=True, zorder=3)
b.axhline(1.0, color=GREY, lw=0.7, ls=(0, (4, 2)))
b.text(0.04, 1.90, r"Bogoliubov: $\sqrt{1+x^2}$", color=TEAL, fontsize=8.0, ha="left", va="center")
b.text(1.56, 1.53, r"$g=1$", color=ORANGE, fontsize=7.6, ha="right", va="top")
b.text(1.06, 1.20, r"$g=2$", color=RED, fontsize=7.6, ha="right", va="top")
b.text(1.18, 0.38, r"$^4$He" "\n" "table", color=BLUE, fontsize=8, ha="right", va="top")
b.set_xlim(0, 1.65); b.set_ylim(0, 2.0)
b.set_xlabel(r"$x=k/k_\ast$"); b.set_ylabel(r"$\omega/(ck)$ or $\varepsilon/(\hbar ck)$")
panel(b, "b")
save(fig, "ch05_universal")
out["collapse"] = dict(max_abs_y_over_universal_minus_1_g1=float(np.abs(y1 / np.sqrt(1 + x1 ** 2) - 1).max()),
                       max_abs_y_over_universal_minus_1_g2=float(np.abs(y2 / np.sqrt(1 + x2 ** 2) - 1).max()),
                       x_max_g1=float(x1.max()), x_max_g2=float(x2.max()),
                       helium_x_max=float(kt[-1] / H.KSTAR))
(HERE / "ch05_solver_numbers.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
