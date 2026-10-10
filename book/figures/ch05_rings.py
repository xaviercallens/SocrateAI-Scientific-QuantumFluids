"""Chapter 5: a localised density pulse in the projected GPE spreads as a *dispersive* ring wave, and the group velocity of
the Bogoliubov spectrum (not the sound speed) sets where each wavelength is found.

Computation (Rust engine qf_pgpe, hbar = m = g = n0 = 1, c = 1; N = 128, L = 64, dt = 0.02, 450 steps to t = 9):
    psi(x, 0) = sqrt(1 + A exp(-|x - x_c|^2 / (2 sigma^2))),  A = 0.02, sigma = 0.6      (a density bump, no velocity)
Stationary phase for a linear dispersive wave:  delta rho(r, t) ~ Re int dk a(k) J_0(k r) cos(omega(k) t); a ripple of
wave number k sits at the radius r = v_g(k) t, so the *local* wave number of the radial profile at r is the solution k_s of
        v_g(k_s) = r / t ,     v_g = d omega / d k = (k + k^3/2)/omega  (m = c = 1).
The script measures the local wave number of the azimuthally averaged profile (phase of the analytic signal), compares it
with k_s(r/t) and draws the density map, the comparison, and the group velocity of 4He (from the published table) next to
the Bogoliubov one in the universal variable x = k/(2 m c / hbar).
    cd book && PYTHONPATH=/mnt/data/xdev-cache/qf_ext ../.venv/bin/python figures/ch05_rings.py
"""
import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from scipy.optimize import brentq
from scipy.signal import hilbert
from scipy.ndimage import gaussian_filter1d
import qf_pgpe
from figstyle import *
plt.rcParams["axes.unicode_minus"] = False
import ch05_helium as H
from ch05_common import bog

HERE = Path(__file__).resolve().parent
N, L, g, dt, T_END, A, SIG = 128, 64.0, 1.0, 0.02, 9.0, 0.02, 0.6
DATA = HERE / "ch05_rings_data.npz"

def vg_bog(k):
    return (k + k ** 3 / 2.0) / bog(k)

if not DATA.exists():
    t0 = time.time()
    eng = qf_pgpe.Pgpe(N, L, g, dt, 0.5)
    x = np.arange(N) * (L / N)
    X, Y = np.meshgrid(x, x, indexing="ij")
    r2 = (X - L / 2) ** 2 + (Y - L / 2) ** 2
    psi0 = np.sqrt(1.0 + A * np.exp(-r2 / (2 * SIG ** 2))).astype(complex)
    c = np.ascontiguousarray(eng.modes(psi0))
    snaps = {}
    t = 0.0
    for tt in (3.0, 6.0, T_END):
        c = eng.run(c, tt - t); t = tt
        rho = np.abs(np.asarray(eng.psi(c))) ** 2
        snaps[f"rho_t{tt:g}"] = rho
    np.savez_compressed(DATA, **snaps, N=N, L=L, g=g, dt=dt, A=A, sigma=SIG, t_end=T_END, seconds=time.time() - t0)
    print("ran in", round(time.time() - t0, 1), "s")
D = np.load(DATA)
rho = D["rho_t9"]; dx = L / N

# ---- radial profile and its local wave number ---------------------------------------------------------------------------
# the centre is the grid point x = L/2, i.e. index N/2; coordinates relative to it:
ix = (np.arange(N) - N // 2) * dx
Xc, Yc = np.meshgrid(ix, ix, indexing="ij")
R = np.sqrt(Xc ** 2 + Yc ** 2)
drho = rho - rho.mean()
# rho is stored with the grid origin at x = 0; the pulse is centred at x = L/2 -> pixel (N/2, N/2): so index shift is already right
dr = 0.2
edges = np.arange(4.0, 31.0, dr)
rc = 0.5 * (edges[1:] + edges[:-1])
prof = np.array([drho[(R >= a_) & (R < b_)].mean() for a_, b_ in zip(edges[:-1], edges[1:])])
# remove the analytic 1/sqrt(r) decay by multiplying with sqrt(r); analytic signal; phase derivative
w = np.sqrt(rc) * prof
ana = hilbert(w)
sel = (rc > 11.0) & (rc < 28.0)
phase = np.unwrap(np.angle(ana))
kloc = np.gradient(phase, rc)
kloc_s = gaussian_filter1d(kloc, 2.0)
ampl = np.abs(ana)
# theory k_s(r/t)
def ks_of(v):
    f = lambda k: vg_bog(k) - v
    if f(1e-6) > 0 or f(np.pi) < 0:
        return np.nan
    return brentq(f, 1e-6, np.pi)
kth = np.array([ks_of(r / T_END) for r in rc])
ok = sel & np.isfinite(kth) & (ampl > 1e-3 * ampl[sel].max())
dev = (kloc_s[ok] - kth[ok]) / kth[ok]
print("local wavenumber vs stationary phase: n points", int(ok.sum()), "median |rel dev|", float(np.median(np.abs(dev))), "max", float(np.abs(dev).max()),
      "r range", rc[ok].min(), rc[ok].max(), "k range", kth[ok].min(), kth[ok].max())
# the group velocity of the highest retained mode
vmax = vg_bog(np.pi)
res = dict(N=N, L=L, dt=dt, t_end=T_END, A=A, sigma=SIG, n_points=int(ok.sum()), median_abs_rel_dev=float(np.median(np.abs(dev))),
           max_abs_rel_dev=float(np.abs(dev).max()), r_min=float(rc[ok].min()), r_max=float(rc[ok].max()),
           k_min=float(kth[ok].min()), k_max=float(kth[ok].max()), vg_at_kcut=float(vmax), r_reached_by_kcut=float(vmax * T_END),
           half_box=L / 2, seconds_run=float(D["seconds"]) if "seconds" in D.files else None)
(HERE / "ch05_rings_numbers.json").write_text(json.dumps(res, indent=1))

# ---- figure -----------------------------------------------------------------------------------------------------
from matplotlib.colors import LinearSegmentedColormap, SymLogNorm
cm = LinearSegmentedColormap.from_list("qfdiv", [BLUE, "#9EC1DD", PAPER, "#E8B07A", RED], N=256)
fig = plt.figure(figsize=(TEXTW, 3.15))
a = fig.add_axes([0.005, 0.07, 0.40, 0.84])
b = fig.add_axes([0.505, 0.15, 0.215, 0.76])
c = fig.add_axes([0.805, 0.15, 0.185, 0.76])
a.imshow(drho.T, origin="lower", extent=[-L / 2 - dx / 2, L / 2 - dx / 2, -L / 2 - dx / 2, L / 2 - dx / 2], cmap=cm,
         norm=SymLogNorm(linthresh=3e-5, linscale=0.6, vmin=-2e-2, vmax=2e-2), interpolation="bicubic")
th = np.linspace(0, 2 * np.pi, 400)
for kv, lab in ((1.0, ""), (2.0, ""), (3.0, "")):
    rr = vg_bog(kv) * T_END
    a.plot(rr * np.cos(th), rr * np.sin(th), color="k", lw=0.6, ls=(0, (2, 3)), alpha=0.7)
rr = 1.0 * T_END
a.plot(rr * np.cos(th), rr * np.sin(th), color=GREY, lw=0.6, ls=(0, (4, 3)))
a.text(0.0, T_END + 1.0, r"$ct$", fontsize=7.5, color=GREY, ha="center", va="bottom")
for kv, ang in ((1.0, 0.9), (2.0, 0.9), (3.0, 0.9)):
    rr = vg_bog(kv) * T_END
    a.text(rr * np.cos(ang) + 0.4, rr * np.sin(ang) + 0.4, f"$k={kv:g}$", fontsize=7.2, color="k", ha="left", va="bottom")
a.set_xlim(-31, 31); a.set_ylim(-31, 31); a.set_aspect("equal"); a.axis("off")
a.text(-30.5, 29.5, r"$\delta\rho(x,y)$ at $t=9$", fontsize=8.5, color="#222222", ha="left", va="top")
a.text(-30.5, -29.5, "dotted rings: $r=v_{\\rm g}(k)\\,t$", fontsize=7.5, color="#222222", ha="left", va="bottom")
a.text(-0.02, 1.01, "a", transform=a.transAxes, fontsize=11, fontweight="bold", color=BLUE)

b.plot(rc[sel], kth[sel], color=GREY, lw=2.6, alpha=0.55, label="stationary phase")
b.plot(rc[ok], kloc_s[ok], color=BLUE, lw=1.2, label="measured")
b.set_xlim(11, 29); b.set_ylim(0, 3.4)
b.set_xlabel(r"radius $r$"); b.set_ylabel(r"local wave number $k$")
b.legend(loc="upper left", fontsize=7.2, handlelength=1.3)
panel(b, "b")

# group velocity of 4He (table) vs Bogoliubov, universal variable x = k/k*
k, e, de = H.load_table()
vg_t = H.group_velocity(k, e, win=0.06)
m = (k >= 0.1) & (k <= 3.5)
xx = np.linspace(0.0, 1.2, 300)
c.axhline(1.0, color=GREY, lw=0.8, ls=(0, (4, 2)))
c.axhline(0.0, color=GREY, lw=0.6)
c.plot(xx, (1 + 2 * xx ** 2) / np.sqrt(1 + xx ** 2), color=TEAL, lw=1.4, ls=(0, (5, 2)))
c.plot(k[m] / H.KSTAR, vg_t[m] / H.C_SVP, color=BLUE, lw=1.4)
c.set_xlim(0, 1.2); c.set_ylim(-0.6, 3.3)
c.set_xlabel(r"$x=k/k_\ast$"); c.set_ylabel(r"group velocity $v_{\rm g}/c$")
c.text(1.18, 2.75, "Bogoliubov", color=TEAL, fontsize=7.4, ha="right", va="top")
c.text(1.18, 0.30, r"$^4$He" "\n" "(table)", color=BLUE, fontsize=7.4, ha="right", va="bottom")
panel(c, "c")
save(fig, "ch05_rings")
