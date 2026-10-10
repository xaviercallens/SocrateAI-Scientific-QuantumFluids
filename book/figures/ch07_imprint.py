"""Chapter 7, Figure 3: the defective imprint of the first instrument, and the T = 0 control that caught it (CLAIM-078, CLAIM-079).
A single vortex pair of separation 10 is written into a UNIFORM condensate (T = 0, L = 64, N = 128, k_c = pi) with
  (old)  round2.imprint:  theta-function phase (periodic only if sum q r is in L Z^2) x per-vortex amplitude r^2/(r^2+2)
  (new)  qf_pgpe.Pgpe.imprint_v2:  phase made periodic by a uniform gradient x Bernoulli amplitude [1 + |v|^2/2]^(-1/2),
and evolved by the Rust engine for 20 time units (maps).  The separation-versus-time curves over 400 time units are the ARCHIVED tracks of the
two gate runs of the campaign (data/generated/pgpe/transport/G1attempt1_T0_dipole_d10_imprint_v1.npz = first attempt, FAILED, and
G1_T0_dipole_d10.npz = second attempt with the corrected imprint, PASSED); the apparent friction is read from the slope of |d|^2 by least squares.
    PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch07_imprint.py"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
from ch07_common import addnum
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "exploration/pgpe"))
import qf_pgpe
from pgpe import PGPE
from round2 import imprint as imprint_old
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

L, N, d0 = 64.0, 128, 10.0; TR = ROOT / "data/generated/pgpe/transport"
res = {}
zv1 = np.load(TR / "G1attempt1_T0_dipole_d10_imprint_v1.npz", allow_pickle=True); zv2 = np.load(TR / "G1_T0_dipole_d10.npz", allow_pickle=True)
pos0 = np.array(json.loads(str(zv2["meta"]))["pos0"]); q = np.array([1, -1])
res["pos0"] = pos0.tolist()

CACHE = Path("/mnt/data/xdev-cache/book_ch07/imprint_maps.npz")
if CACHE.exists():                                                                   # the 20-time-unit runs are cached; delete the file to recompute
    zc = np.load(CACHE, allow_pickle=True); maps = {"old": zc["old"], "new": zc["new"]}; res.update(json.loads(str(zc["res"])))
else:
    s_np = PGPE(N=N, L=L); s_rs = qf_pgpe.Pgpe(N, L)
    c0 = np.zeros((N, N), complex); c0[0, 0] = N ** 2                                    # psi = 1, n = 1
    c_old = np.ascontiguousarray(imprint_old(s_np, c0, pos0, q)); c_new = np.ascontiguousarray(s_rs.imprint_v2(np.ascontiguousarray(c0), pos0, q))
    maps = {}; r2 = {}
    for name, c in (("old", c_old), ("new", c_new)):
        r2[f"{name}_peak_density_t0"] = float((np.abs(np.fft.ifft2(c)) ** 2).max())
        cc = np.ascontiguousarray(s_rs.run(c, 20.0)); rho = np.abs(np.fft.ifft2(cc)) ** 2
        maps[name] = rho - 1.0; r2[f"{name}_rho_minus_1_t20_40th_largest_abs"] = float(np.sort(np.abs(rho - 1.0).ravel())[-40])
        r2[f"{name}_momentum_t20"] = [float(x) for x in s_rs.momentum(cc)]
        r2[f"{name}_energy_t20"] = float(s_rs.energy(cc))
        pos_t, q_t = s_rs.detect(cc); r2[f"{name}_n_vortices_t20"] = int(len(q_t))
    r2["two_pi_n_d"] = float(2 * np.pi * d0)
    np.savez(CACHE, old=maps["old"], new=maps["new"], res=json.dumps(r2)); res.update(r2)


def sep(z):
    R = z["R"]; d = R[:, 0] - R[:, 1]; d -= L * np.round(d / L); return z["t"], np.hypot(d[:, 0], d[:, 1])


fig = plt.figure(figsize=(TEXTW, 2.5))
gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1.15], height_ratios=[1, 0.07], wspace=0.30, hspace=0.62, left=0.04, right=0.995, top=0.92, bottom=0.13)
div = LinearSegmentedColormap.from_list("qfdiv", [BLUE, "#9EC1DD", PAPER, "#E8B07A", RED]); vmax = 0.10
for k, (name, title, letter) in enumerate((("old", "first instrument", "a"), ("new", "corrected imprint", "b"))):
    ax = fig.add_subplot(gs[0, k]); im = ax.imshow(maps[name].T, origin="lower", extent=[0, L, 0, L], cmap=div, norm=TwoSlopeNorm(0, -vmax, vmax), interpolation="bilinear")
    for p, qq in zip(pos0, q):
        ax.plot(p[0], p[1], "o", ms=3.2, mfc="white" if qq > 0 else "#222222", mec="#222222", mew=0.6)
    ax.set_xticks([0, 32, 64]); ax.set_yticks([0, 32, 64]); ax.set_xlabel(r"$x/\xi$", labelpad=1); ax.tick_params(length=2)
    if k == 0:
        ax.set_ylabel(r"$y/\xi$", labelpad=1)
    ax.set_title(title, fontsize=8.5, pad=3); panel(ax, letter); ax.spines["top"].set_visible(True); ax.spines["right"].set_visible(True)
cax = fig.add_subplot(gs[1, 0:2]); cb = fig.colorbar(im, cax=cax, orientation="horizontal"); cb.set_label(r"$|\psi|^2-1$ at $t=20$ (saturated beyond $\pm0.1$)", fontsize=7.2, labelpad=1); cb.ax.tick_params(labelsize=7, length=2)
ax = fig.add_subplot(gs[0:2, 2])
for z, col, lab in ((zv1, RED, "first instrument"), (zv2, BLUE, "corrected imprint")):
    t, d = sep(z); ax.plot(t, d, "-", color=col, lw=1.0, label=lab)
    A = np.vstack([t, np.ones_like(t)]).T; slope, icpt = np.linalg.lstsq(A, d ** 2, rcond=None)[0]
    tag = "old" if col == RED else "new"
    res[f"{tag}_track_d_first"] = float(d[0]); res[f"{tag}_track_d_last"] = float(d[-1]); res[f"{tag}_track_d_min"] = float(d.min()); res[f"{tag}_track_d_max"] = float(d.max())
    res[f"{tag}_d2_slope_per_time"] = float(slope); res[f"{tag}_alpha_apparent"] = float(-slope / 4); res[f"{tag}_t_end"] = float(t[-1])
    ax.plot(t, np.sqrt(np.maximum(icpt + slope * t, 0)), "--", color=col, lw=0.7)
ax.set_xlabel(r"time $t$"); ax.set_ylabel(r"separation $d$"); ax.set_ylim(8.0, 10.7); ax.legend(loc="lower left", handlelength=1.2, fontsize=7.2); panel(ax, "c")
ax.text(0.97, 0.95, "$T=0$: there is no bath\nto rub against", transform=ax.transAxes, ha="right", va="top", fontsize=7, color="#333333")
addnum("fig_imprint", res)
save(fig, "ch07_imprint")
