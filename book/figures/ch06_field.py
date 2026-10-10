"""Figure ch06_field: the simulated classical Bose field near the Kosterlitz-Thouless transition.
Top row (a-c): final states of the L = 64 heating ladder (data/generated/pgpe/r2/II_e0.90_s11_t4000_e{1.00,1.25,1.40}), vortices by the plaquette winding rule
(+1 red, -1 blue), optimal +/- matching (minimum image) as black bonds, coarse-grained phase as background hue.
(d) n_s lambda_T^2 against T for L = 64 and L = 32 (single runs open, seed means filled), the Nelson-Kosterlitz level 4, interpolated crossings;
(e) measured eta against 1/(n_s lambda^2) for n_s lambda^2 > 4 (spin-wave relation eta n_s lambda^2 = 1).
Data: ch06_pgpe_numbers.json (ch06_pgpe_data.py).  Writes ch06_field_info.json (vortex numbers and mean matched separations of the three maps)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
from ch06_common import *
from scipy.optimize import linear_sum_assignment
from scipy.ndimage import gaussian_filter
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "exploration" / "pgpe"))
from pgpe import PGPE
from observables import vortices

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
R2 = ROOT / "data/generated/pgpe/r2"
pg = json.loads((HERE / "ch06_pgpe_numbers.json").read_text())
TBKT = pg["L64"]["crossing"]["T_BKT"]
pi = np.pi

fig = plt.figure(figsize=(TEXTW, 3.45))
gs = fig.add_gridspec(2, 6, height_ratios=[1.0, 0.86], hspace=0.42, wspace=1.0, left=0.075, right=0.995, top=0.945, bottom=0.11)

# ------------------------------------------------------------------ (a-c) vortex maps
L = 64.0; s = PGPE(N=128, L=L)
cm = vortex_cmap()
info = {}
for k, (e, letter) in enumerate((("1.00", "a"), ("1.25", "b"), ("1.40", "c"))):
    ax = fig.add_subplot(gs[0, 2 * k:2 * k + 2])
    c = np.load(R2 / f"II_e0.90_s11_t4000_e{e}_final.npy"); meta = json.loads((R2 / f"II_e0.90_s11_t4000_e{e}.json").read_text())
    psi = np.fft.ifft2(c); amp = np.abs(psi)
    pos, q = vortices(s, c)
    ps = gaussian_filter(psi.real, 3, mode="wrap") + 1j * gaussian_filter(psi.imag, 3, mode="wrap")
    rgb = cm((np.angle(ps) + np.pi) / (2 * np.pi))[..., :3]
    dens = gaussian_filter(amp ** 2, 1.0, mode="wrap")
    br = np.clip(0.55 + 0.45 * (dens - dens.min()) / (dens.max() - dens.min()), 0, 1)
    img = 0.33 * rgb + 0.67 * br[..., None]
    ax.imshow(np.transpose(img, (1, 0, 2)), origin="lower", extent=[0, L, 0, L], interpolation="bilinear")
    a, b = pos[q > 0], pos[q < 0]
    dmean = np.nan
    if len(a) == len(b) and len(a) > 0:
        d = a[:, None, :] - b[None, :, :]; d -= L * np.round(d / L)
        Dm = np.hypot(d[..., 0], d[..., 1]); r, cidx = linear_sum_assignment(Dm)
        dmean = float(Dm[r, cidx].mean())
        for i, j in zip(r, cidx):
            dv = b[j] - a[i]; dv -= L * np.round(dv / L)
            for sx in (-L, 0, L):
                for sy in (-L, 0, L):
                    ax.plot([a[i, 0] + sx, a[i, 0] + sx + dv[0]], [a[i, 1] + sy, a[i, 1] + sy + dv[1]], "-", color="#222222", lw=0.55, zorder=2)
    ax.plot(a[:, 0], a[:, 1], "o", ms=2.7, mfc=RED, mec="white", mew=0.35, zorder=3)
    ax.plot(b[:, 0], b[:, 1], "o", ms=2.7, mfc=BLUE, mec="white", mew=0.35, zorder=3)
    ax.set_xlim(0, L); ax.set_ylim(0, L); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(True); sp.set_color(GREY); sp.set_linewidth(0.6)
    T = meta["whole"]["T"]
    ax.set_title(f"$T={T:.2f}$ ($T/T_{{\\rm BKT}}={T / TBKT:.2f}$)", fontsize=8, pad=3)
    import matplotlib.patheffects as pe
    for yy, line in ((0.085, f"{len(q)} vortices"), (0.025, f"mean pair {dmean:.1f}")):    # one Text per line: multi-line Text ignores the lining-figure feature
        ax.text(0.04, yy, line, transform=ax.transAxes, fontsize=7.2, ha="left", va="bottom", color="#111111",
                path_effects=[pe.withStroke(linewidth=2.4, foreground="white", alpha=0.85)])
    panel(ax, letter)
    info[e] = dict(T=T, T_over_TBKT=T / TBKT, n_v=int(len(q)), mean_pair=dmean, n_plus=int(len(a)), n_minus=int(len(b)))

# ------------------------------------------------------------------ (d) n_s lambda^2 vs T
axd = fig.add_subplot(gs[1, 0:3])
for tag, col, mk, lab in (("L64", BLUE, "o", "$L=64\\,\\xi$"), ("L32", TEAL, "s", "$L=32\\,\\xi$")):
    runs = [r for r in pg[tag]["per_run"] if r["admitted"]]
    axd.plot([r["T"] for r in runs], [r["K"] for r in runs], mk, ms=2.6, mfc="none", mec=col, mew=0.6, alpha=0.8, zorder=2)
    rows = pg[tag]["rows"]
    axd.plot([r["T"] for r in rows], [r["K"] for r in rows], mk + "-", color=col, ms=4.2, lw=1.0, mfc=col, mec="white", mew=0.4, label=lab, zorder=3)
    cr = pg[tag]["crossing"]
    axd.plot([cr["T_BKT"]], [4], "|", color=col, ms=12, mew=1.6, zorder=4)
axd.axhline(4, color=RED, lw=0.8, ls="--"); axd.text(1.01, 4.3, "$n_s\\lambda_T^2=4$", color=RED, fontsize=7.3, ha="right", va="bottom")
Tg = np.linspace(0.42, 1.03, 50); axd.plot(Tg, 2 * pi / Tg, ":", color=GREY, lw=0.8, zorder=1); axd.text(0.46, 2 * pi / 0.46 + 0.2, "$2\\pi/T$ (all of the fluid)", color=GREY, fontsize=6.8, ha="left", va="bottom")
axd.set_xlim(0.42, 1.03); axd.set_ylim(0, 14)
axd.set_xlabel("temperature $T$ [$\\hbar^2/(m\\xi^2)$, $k_B=1$]", fontsize=8.5); axd.set_ylabel("$n_s\\lambda_T^2$")
axd.legend(loc="upper right", fontsize=7, handlelength=1.2, borderaxespad=0.2, bbox_to_anchor=(1.0, 0.92))
panel(axd, "d")

# ------------------------------------------------------------------ (e) eta vs 1/(n_s lambda^2)
axe = fig.add_subplot(gs[1, 3:6])
for tag, col, mk, lab in (("L64", BLUE, "o", "$L=64$"), ("L32", TEAL, "s", "$L=32$")):
    rows = [r for r in pg[tag]["rows"] if r["K"] > 4]
    axe.plot([1 / r["K"] for r in rows], [r["eta"] for r in rows], mk, ms=4.2, mfc=col, mec="white", mew=0.4, label=lab, zorder=3)
xx = np.array([0.05, 0.26]); axe.plot(xx, xx, "-", color=GREY, lw=0.9); axe.text(0.255, 0.236, "$\\eta\\,n_s\\lambda_T^2=1$", color=GREY, fontsize=7.2, ha="right", va="top")
axe.plot(xx, 1.27 * xx, ":", color=GREY, lw=0.7); axe.plot(xx, 1.12 * xx, ":", color=GREY, lw=0.7)
axe.set_xlim(0.05, 0.27); axe.set_ylim(0.05, 0.34)
axe.set_xlabel("$1/(n_s\\lambda_T^2)$"); axe.set_ylabel("measured $\\eta$ of $g_1(r)\\sim r^{-\\eta}$", fontsize=8.5)
axe.legend(loc="upper left", fontsize=7, handlelength=1.0, borderaxespad=0.2)
panel(axe, "e")
save(fig, "ch06_field")
json.dump(info, open(HERE / "ch06_field_info.json", "w"), indent=1)
