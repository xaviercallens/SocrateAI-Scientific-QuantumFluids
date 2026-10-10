"""Figure ch06_coulomb: the Coulomb gas inside the solver.
(a) phase (hue) of a vortex-antivortex pair imprinted with qf-pgpe in a uniform condensate (L = 64, d = 10), with the streamlines of the superfluid velocity;
(b) excess energy of the imprinted pair against separation, L = 64 and L = 128, against the torus point-vortex law pi*H_WM(d) + 2 pi^2 d^2/L^2 + C and the plane law 2 pi ln d;
(c) residuals of the torus law.
Data: figures/ch06_loglaw_numbers.json (made by ch06_loglaw.py).   Run: PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch06_coulomb.py"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
from ch06_common import *
import qf_pgpe
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "exploration" / "pgpe"))
from vortex_thermometer import h_pair

TWO_PI = 2 * np.pi
D = json.loads((Path(__file__).resolve().parent / "ch06_loglaw_numbers.json").read_text())


def model(d, L):
    d = np.asarray(d, float)
    return np.pi * h_pair(d * TWO_PI / L, np.zeros_like(d)) + 2 * np.pi ** 2 * d ** 2 / L ** 2


fig = plt.figure(figsize=(TEXTW, 2.45))
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.3, 0.95], wspace=0.5, left=0.07, right=0.995, top=0.93, bottom=0.17)

# ---------------- (a) the imprinted pair
axa = fig.add_subplot(gs[0])
N, L, d = 128, 64.0, 10.0
s = qf_pgpe.Pgpe(N, L); c0 = s.uniform()
x0 = L / 2 + 0.125
pos = np.array([[x0 + d / 2, x0], [x0 - d / 2, x0]]); q = np.array([1, -1])
c = s.imprint_v2(c0, pos, q)
psi = np.fft.ifft2(c); th = np.angle(psi); amp = np.abs(psi)
dx = L / N; x = np.arange(N) * dx
w = 15.0
i0, i1 = int((x0 - w) / dx), int((x0 + w) / dx)
sl = slice(i0, i1)
cm = vortex_cmap()
rgb = cm((th[sl, sl] + np.pi) / (2 * np.pi))[..., :3]
br = np.clip(amp[sl, sl] ** 1.5, 0, 1)[..., None]
img = rgb * (0.25 + 0.75 * br)
ext = [x[i0] - x0, x[i1 - 1] - x0, x[i0] - x0, x[i1 - 1] - x0]
axa.imshow(np.transpose(img, (1, 0, 2)), origin="lower", extent=ext, interpolation="bicubic")
kk = 2 * np.pi * np.fft.fftfreq(N, d=dx); KX, KY = np.meshgrid(kk, kk, indexing="ij")
gx = np.fft.ifft2(1j * KX * c); gy = np.fft.ifft2(1j * KY * c)
den = np.maximum(np.abs(psi) ** 2, 5e-2)
vx = (np.conj(psi) * gx).imag / den; vy = (np.conj(psi) * gy).imag / den
xs = x[i0:i1] - x0
axa.streamplot(xs, xs, vx[sl, sl].T, vy[sl, sl].T, color="#1b1b1b", linewidth=0.55, density=1.25, arrowsize=0.55, zorder=3)
axa.plot([d / 2], [0], "o", ms=6, mfc=RED, mec="white", mew=1.0, zorder=5); axa.plot([-d / 2], [0], "s", ms=6, mfc=BLUE, mec="white", mew=1.0, zorder=5)
import matplotlib.patheffects as pe
for xx, lab in ((d / 2, "+1"), (-d / 2, "-1")):
    axa.text(xx, 2.3, lab, color="#1b1b1b", fontsize=8, fontweight="bold", ha="center", va="bottom", zorder=6, path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
axa.set_xlabel("$x/\\xi$"); axa.set_ylabel("$y/\\xi$"); axa.set_xticks([-10, 0, 10]); axa.set_yticks([-10, 0, 10]); axa.set_xlim(ext[0], ext[1]); axa.set_ylim(ext[2], ext[3])
panel(axa, "a")
ins = axa.inset_axes([0.02, 0.02, 0.2, 0.2], projection="polar")
ang = np.linspace(0, 2 * np.pi, 200); rr = np.linspace(0.55, 1, 2)
A, R = np.meshgrid(ang, rr)
ins.pcolormesh(A, R, A, cmap=cm, vmin=0, vmax=2 * np.pi, shading="auto"); ins.set_axis_off()

# ---------------- (b) energy law
axb = fig.add_subplot(gs[1])
cols = {"L64": BLUE, "L128": ORANGE}
for key in ("L64", "L128"):
    r = D[key]; Lk = r["L"]
    dd = np.array([x_["d_detected"] for x_ in r["rows"]]); E = np.array([x_["dE"] for x_ in r["rows"]])
    C = r["fits"]["dmin8.0"]["C"]
    dg = np.geomspace(2.5, 0.47 * Lk, 200)
    axb.plot(dg, model(dg, Lk) + C, "-", color=cols[key], lw=1.1, zorder=2)
    axb.plot(dd, E, "o", ms=3.4, mfc=cols[key], mec="white", mew=0.4, zorder=3, label=f"$L={int(Lk)}\\,\\xi$")
d8 = np.geomspace(3, 40, 50)
C128 = D["L128"]["fits"]["dmin8.0"]["C"]
axb.plot(d8, TWO_PI * np.log(d8 / 8.0) + (model(8.0, 128.0) + C128), "--", color=GREY, lw=0.9, label="slope $2\\pi$")
axb.set_xscale("log"); axb.set_xlabel("pair separation $d/\\xi$"); axb.set_ylabel("$\\Delta E$  [$\\hbar^2 n/m$]")
log_ticks_plain(axb, "x", [2, 5, 10, 20, 50])
axb.legend(loc="lower right", fontsize=7.3, handlelength=1.4, borderaxespad=0.2)
panel(axb, "b")

# ---------------- (c) residuals
axc = fig.add_subplot(gs[2])
for key in ("L64", "L128"):
    r = D[key]; Lk = r["L"]; C = r["fits"]["dmin8.0"]["C"]
    dd = np.array([x_["d_detected"] for x_ in r["rows"]]); E = np.array([x_["dE"] for x_ in r["rows"]])
    res = E - model(dd, Lk) - C
    axc.plot(dd / Lk, res, "o-", ms=3.2, lw=0.7, color=cols[key], mfc=cols[key], mec="white", mew=0.4, label=f"$L={int(Lk)}$")
axc.axhline(0, color=GREY, lw=0.6); axc.axvspan(0, 8 / 64, color="#EEEEEE", zorder=0)
axc.set_xlabel("$d/L$"); axc.set_ylabel("$\\Delta E-$ torus law"); axc.set_xlim(0, 0.46); axc.set_ylim(-0.7, 0.25)
panel(axc, "c")
axc.text(0.065, -0.66, "cores,\nnot fitted", fontsize=7, color=GREY, ha="center", va="bottom")
save(fig, "ch06_coulomb")
