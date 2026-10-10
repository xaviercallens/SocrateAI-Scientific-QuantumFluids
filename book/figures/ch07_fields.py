"""Chapter 7, Figure 4 (the striking one): two antiparallel vortex pairs imprinted in a thermal projected-GP field and followed by the Rust engine.
Input: the run written by ch07_pairrun.py (default tag e060_d10_s7: base e0.60, T = 0.115, T/T_BKT = 0.14, L = 64, N = 128, k_c = pi, d_0 = 10).
(a) phase of psi right after the imprint, (b) phase at the end of the run with the tracks of the four vortices (colour = time, drawn on the periodic box),
(c) density |psi|^2 - 1 right after the imprint, (d) the separations of the two pairs against time (25-unit running mean) with the straight lines of the d^2 law."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
ROOT_ = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT_ / 'exploration/pgpe'))
from transport_estimators import pv_velocity
from ch07_common import addnum
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
tag = sys.argv[1] if len(sys.argv) > 1 else "e060_d10_s7"
z = np.load(f"/mnt/data/xdev-cache/book_ch07/ch07_pairrun_{tag}.npz", allow_pickle=True); meta = json.loads(str(z["meta"]))
t, R, q, ST, SN = z["t"], z["R"], z["q"], z["snap_t"], z["snaps"]; L = meta["L"]; N = meta["N"]
res = dict(tag=tag, ended=meta["ended"], t_end=meta["t_end"], n_samples=int(len(t)), drift_E=meta.get("drift_E"), seconds=meta.get("seconds"), chunks=meta.get("chunks"),
           base=meta["base"], d0=meta["d0"], seed=meta["seed"], pos0=meta["pos0"], mean_n_det=float(z["n_det"].mean()))
psi = lambda c: np.fft.ifft2(c)
cmap_ph = vortex_cmap()
blues = LinearSegmentedColormap.from_list("qfb", ["#C9DCEC", BLUE]); oranges = LinearSegmentedColormap.from_list("qfo", ["#F3D9B8", ORANGE])


def wrapped_segments(x, y, L):
    """polyline pieces of a track on the periodic box, broken where a coordinate jumps by more than L/2"""
    pts = np.column_stack([np.mod(x, L), np.mod(y, L)]); segs, idx = [], []
    for k in range(len(pts) - 1):
        if np.abs(pts[k + 1] - pts[k]).max() < L / 2:
            segs.append([pts[k], pts[k + 1]]); idx.append(k)
    return segs, np.array(idx)


def pair_sep(R, i, j):
    d = R[:, i] - R[:, j]; d -= L * np.round(d / L); return np.hypot(d[:, 0], d[:, 1])


from scipy.ndimage import gaussian_filter
SIGMA = 3.0                                                       # coarse-graining length of the flow portrait, in healing lengths


def flow(c):
    """coarse-grained superfluid velocity v = Im(psi* grad psi)/|psi|^2, current and density smoothed by a Gaussian of width SIGMA (periodic)"""
    dx = L / N; k1 = 2 * np.pi * np.fft.fftfreq(N, d=dx); kx, ky = np.meshgrid(k1, k1, indexing="ij"); ps = psi(c)
    jx = np.imag(np.conj(ps) * np.fft.ifft2(1j * kx * c)); jy = np.imag(np.conj(ps) * np.fft.ifft2(1j * ky * c)); n = np.abs(ps) ** 2; s_ = SIGMA / dx
    Jx = gaussian_filter(jx, s_, mode="wrap"); Jy = gaussian_filter(jy, s_, mode="wrap"); Nn = gaussian_filter(n, s_, mode="wrap")
    return Jx / Nn, Jy / Nn


fig = plt.figure(figsize=(TEXTW, 3.9)); gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.62], wspace=0.10, hspace=0.38, left=0.075, right=0.99, top=0.945, bottom=0.085)
t_last = ST[-1]; c0 = SN[0]; c1 = SN[-1]; x1d = np.arange(N) * (L / N)
mark = lambda ax, P: [ax.plot(p[0], p[1], "o", ms=4.0, mfc="white" if qq > 0 else "#1a1a1a", mec="#1a1a1a", mew=0.7, zorder=5) for p, qq in zip(P, q)]
seq = LinearSegmentedColormap.from_list("qfseq", ["#B9CFE2", "#5E93BF", TEAL, "#12365A"])
# (a) phase just after the imprint
ax = fig.add_subplot(gs[0, 0]); ax.imshow(np.angle(psi(c0)).T, origin="lower", extent=[0, L, 0, L], cmap=cmap_ph, vmin=-np.pi, vmax=np.pi, interpolation="bilinear"); mark(ax, R[0])
ax.set_title(r"phase, $t=0$", fontsize=8.5, pad=3); ax.set_xticks([0, 32, 64]); ax.set_yticks([0, 32, 64]); ax.tick_params(length=2); ax.set_xlabel(r"$x/\xi$", labelpad=1); ax.set_ylabel(r"$y/\xi$", labelpad=1); panel(ax, "a")
# (b) the flow portrait: coarse-grained superfluid velocity, streamlines coloured by speed
ax = fig.add_subplot(gs[0, 1]); vx, vy = flow(c0); sp = np.hypot(vx, vy)
ax.imshow(sp.T, origin="lower", extent=[0, L, 0, L], cmap=LinearSegmentedColormap.from_list("qfw", [PAPER, "#DCE7F0"]), vmax=0.5, interpolation="bilinear")
ax.streamplot(x1d, x1d, vx.T, vy.T, color=sp.T, cmap=seq, norm=plt.Normalize(0, 0.22), density=2.1, linewidth=0.9, arrowsize=0.6); mark(ax, R[0])
ax.set_xlim(0, L); ax.set_ylim(0, L); ax.set_title(r"superfluid velocity, $t=0$", fontsize=8.5, pad=3); ax.set_xticks([0, 32, 64]); ax.set_yticks([0, 32, 64]); ax.set_yticklabels([]); ax.tick_params(length=2)
ax.set_xlabel(r"$x/\xi$", labelpad=1); panel(ax, "b")
res["flow_portrait"] = dict(sigma_xi=SIGMA, max_speed_smoothed=float(sp.max()), mean_speed_smoothed=float(sp.mean()))
# (c) phase at the end of the run with the four tracks
ax = fig.add_subplot(gs[0, 2]); ax.imshow(np.angle(psi(c1)).T, origin="lower", extent=[0, L, 0, L], cmap=cmap_ph, vmin=-np.pi, vmax=np.pi, interpolation="bilinear")
for i in range(4):
    segs, idx = wrapped_segments(R[:, i, 0], R[:, i, 1], L)
    if len(segs):
        lc = LineCollection(segs, cmap=blues if q[i] > 0 else oranges, linewidths=1.0, alpha=0.95); lc.set_array(t[idx]); lc.set_clim(0, t[-1]); ax.add_collection(lc)
mark(ax, R[-1]); ax.set_xlim(0, L); ax.set_ylim(0, L); ax.set_title(rf"phase, $t={t_last:.0f}$, and tracks", fontsize=8.5, pad=3)
ax.set_xticks([0, 32, 64]); ax.set_yticks([0, 32, 64]); ax.set_yticklabels([]); ax.tick_params(length=2); ax.set_xlabel(r"$x/\xi$", labelpad=1); panel(ax, "c")
# (d) separations
ax = fig.add_subplot(gs[1, :]); n = min(25, max(1, len(t) // 3)); k = np.ones(n) / n
for (i, j), col in (((0, 1), BLUE), ((2, 3), ORANGE)):
    d = pair_sep(R, i, j); y = np.convolve(d, k, mode="valid"); tt = t[n // 2:n // 2 + len(y)]
    ax.plot(t, d, "-", color=col, lw=0.35, alpha=0.35); ax.plot(tt, y, "-", color=col, lw=1.3)
    A = np.vstack([t, np.ones_like(t)]).T; sl, ic = np.linalg.lstsq(A, d ** 2, rcond=None)[0]
    trend = np.polyval(np.polyfit(tt, y, 1), tt)
    res[f"pair{i // 2 + 1}"] = dict(d_first20=float(d[:20].mean()), d_last20=float(d[-20:].mean()), d2_slope=float(sl), alpha_from_d2_slope=float(-sl / 4), d_min=float(d.min()), d_max=float(d.max()), d_sd_about_trend_25unit_means=float(np.std(y - trend)), d25_min=float(y.min()), d25_max=float(y.max()))
    ax.plot(t, np.sqrt(np.maximum(ic + sl * t, 0)), "--", color="#333333", lw=0.7)
    dd = R[:, j] - R[:, i]; dd -= L * np.round(dd / L); cen = R[:, i] + dd / 2                      # centre from the minimum-image separation (the tracks are wrapped into [0, L))
    dc = np.diff(cen, axis=0); dc -= L * np.round(dc / L); net = dc.sum(axis=0)                  # steps are small: unwrap them, then add up the NET displacement
    v = float(np.hypot(*net) / (t[-1] - t[0]))
    Vm = np.array([pv_velocity(np.mod(R[k], L), q.astype(float), L) for k in range(len(t))]); vmod = float(np.mean(np.hypot(*((Vm[:, i] + Vm[:, j]) / 2).T)))   # the torus point-vortex speed of the pair centre at the tracked positions
    res[f"laps_pair{i // 2 + 1}"] = float(np.hypot(*net) / L); res[f"pair{i // 2 + 1}"].update(centre_speed=v, model_speed_torus=vmod, speed_over_model=float(v / vmod), planar_speed_1_over_meand=float(1 / d.mean()), centre_speed_times_mean_d=float(v * d.mean()), centre_direction=[float(net[0] / np.hypot(*net)), float(net[1] / np.hypot(*net))])
ax.set_ylim(6.2, 12.6); ax.set_xlabel(r"time $t$"); ax.set_ylabel(r"pair separation $d$"); panel(ax, "d")
ax.plot([], [], "-", color=BLUE, lw=1.3, label="pair at $x\\approx L/4$"); ax.plot([], [], "-", color=ORANGE, lw=1.3, label="pair at $x\\approx 3L/4$"); ax.plot([], [], "--", color="#333333", lw=0.7, label="$|d|^2$ linear in $t$ (least squares)")
ax.legend(loc="lower left", fontsize=6.8, handlelength=1.6, ncol=1)
addnum("fig_fields", res)
save(fig, "ch07_fields")
