"""Figure ch03_phasefield: one wave function, three faces.  A vortex-antivortex pair of the projected Gross-Pitaevskii field (qf-pgpe, t = 20):
(a) phase (hue, with spokes) and density (brightness) with the streamlines of the Madelung velocity u = Im(conj(psi) grad psi)/|psi|^2,
(b) the density deficit 1 - n on a logarithmic scale, (c) the speed |u| (colour) against the periodic point-vortex field (dashed contours).
Data: /mnt/data/xdev-cache/ch03/pair_d12.npz written by ch03_run.py.
Run: OMP_NUM_THREADS=1 PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch03_phasefield.py"""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from ch03_analysis import madelung_fields, L, CACHE
import ch03_pv as PV

T_SNAP = 20
if os.environ.get("CH03_TEST"):          # development only: the early cached run (tilted pair), positions by detection
    import qf_pgpe
    c = np.load(f"{CACHE}/pair_snaps.npy")[T_SNAP]; pos, q = qf_pgpe.Pgpe(128, 64.0).detect(c); pos = np.asarray(pos)
else:
    z = np.load(f"{CACHE}/pair_d12.npz")
    c = z["snaps"][T_SNAP]; pos = z["pos"][T_SNAP]; q = z["q"]
F = madelung_fields(c, 4)
n, ux, uy, psi, dxf = F["n"], F["ux"], F["uy"], F["psi"], F["dx"]
# the uniform state rotates as exp(-i t): take the phase of the zero mode as the reference
phase = np.angle(psi * np.exp(-1j * np.angle(c[0, 0]))) % (2 * np.pi)

cx, cy = pos[:, 0].mean(), pos[:, 1].mean()
x0, x1, y0, y1 = cx - 15.0, cx + 15.0, cy - 8.0, cy + 8.0
i0, i1 = int(round(x0 / dxf)), int(round(x1 / dxf)); j0, j1 = int(round(y0 / dxf)), int(round(y1 / dxf))
sl = (slice(i0, i1), slice(j0, j1))
ext = [i0 * dxf, i1 * dxf, j0 * dxf, j1 * dxf]
xs = np.linspace(ext[0], ext[1], i1 - i0, endpoint=False) + 0.5 * dxf; ys = np.linspace(ext[2], ext[3], j1 - j0, endpoint=False) + 0.5 * dxf

# a saturated cyclic map built from the book's palette
cyc = LinearSegmentedColormap.from_list("qfwheel", [BLUE, TEAL, GOLD, ORANGE, RED, "#7A3B6E", BLUE], N=512)
rgb = cyc(phase[sl] / (2 * np.pi))[..., :3]
fr = 0.80 + 0.20 * np.cos(6 * phase[sl])                           # six spokes per turn: the pinwheel of a phase singularity
bright = np.clip(n[sl], 0, 1) ** 0.6 * fr
comp = np.clip(rgb * bright[..., None] + (1 - np.clip(n[sl], 0, 1) ** 0.6)[..., None] * np.array([0.03, 0.04, 0.07]), 0, 1)

fig = plt.figure(figsize=(TEXTW, 4.1))
gs = fig.add_gridspec(2, 2, height_ratios=[1.75, 1.0], hspace=0.20, wspace=0.30, left=0.075, right=0.985, top=0.985, bottom=0.085)
axa = fig.add_subplot(gs[0, :]); axb = fig.add_subplot(gs[1, 0]); axc = fig.add_subplot(gs[1, 1])

# (a) phase + density + streamlines
axa.imshow(np.transpose(comp, (1, 0, 2)), origin="lower", extent=ext, interpolation="bilinear", aspect="equal")
axa.streamplot(xs, ys, np.transpose(ux[sl]), np.transpose(uy[sl]), density=0.85, color=(1, 1, 1, 0.6), linewidth=0.55, arrowsize=0.55, minlength=0.5, broken_streamlines=False)
# (b) density deficit, logarithmic
deficit = np.clip(1.0 - n[sl], 1e-4, 1.0)
cmb = LinearSegmentedColormap.from_list("qfdef", [PAPER, "#9EC1DD", BLUE, "#0B1B2B"])
imb = axb.imshow(np.transpose(deficit), origin="lower", extent=ext, cmap=cmb, norm=LogNorm(1e-4, 1.0), interpolation="bilinear", aspect="equal")
# (c) speed, GP against point vortices (+ the uniform flow of the torus)
speed = np.hypot(ux, uy)[sl]
cms = LinearSegmentedColormap.from_list("qfspd", [PAPER, "#E8B07A", RED, "#4A1510"])
imc = axc.imshow(np.transpose(np.clip(speed, 0, 0.6)), origin="lower", extent=ext, cmap=cms, vmin=0, vmax=0.6, interpolation="bilinear", aspect="equal")
XX, YY = np.meshgrid(xs[::2], ys[::2], indexing="ij")
v = PV.wm_velocity(np.column_stack([XX.ravel(), YY.ravel()]), pos, q) + PV.sector_flow(pos, q)
spv = np.hypot(v[:, 0], v[:, 1]).reshape(XX.shape)
axc.contour(XX, YY, spv, levels=[0.04, 0.08, 0.16, 0.32], colors=[BLUE], linewidths=0.9, linestyles="--")
for ax in (axa, axb, axc):
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    for (px, py), qq in zip(pos, q):
        ax.plot(px, py, marker="o", ms=10, mfc="none", mec="white" if ax is axa else "#222222", mew=0.9, zorder=5)
        ax.text(px, py, "+" if qq > 0 else "\u2212", color="white" if ax is axa else "#222222", ha="center", va="center", fontsize=8, zorder=6)
    for sp in ax.spines.values(): sp.set_visible(True)
axa.set_ylabel(r"$y\,/\,\xi$"); axb.set_xlabel(r"$x\,/\,\xi$"); axc.set_xlabel(r"$x\,/\,\xi$"); axb.set_ylabel(r"$y\,/\,\xi$")
axa.set_xticklabels([]); axc.set_yticklabels([])
lab = dict(fontsize=8.2, va="top", ha="left", bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.82))
axa.text(0.012, 0.975, r"phase $S$ (hue), density $n$ (brightness), streamlines of $\mathbf{u}$", transform=axa.transAxes, **lab)
axb.text(0.015, 0.97, r"$1-n$ (log scale)", transform=axb.transAxes, **lab)
axc.text(0.015, 0.97, r"$|\mathbf{u}|$: solver (colour), point vortices (dashed)", transform=axc.transAxes, **lab)
panel(axa, "a"); panel(axb, "b"); panel(axc, "c")
# phase wheel
axw = axa.inset_axes([0.858, 0.08, 0.105, 0.30], projection="polar")      # left of the edge: the white label "0" must stay inside the panel
th = np.linspace(0, 2 * np.pi, 361); rr = np.linspace(0.5, 1.0, 8)
TH, RR = np.meshgrid(th, rr)
axw.pcolormesh(TH, RR, TH, cmap=cyc, vmin=0, vmax=2 * np.pi, shading="auto")
axw.set_ylim(0, 1.0); axw.set_yticks([]); axw.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2]); axw.set_xticklabels([r"$0$", r"$\pi/2$", r"$\pi$", r"$3\pi/2$"], fontsize=5.8, color="white")
axw.tick_params(pad=-3); axw.spines["polar"].set_visible(False); axw.set_facecolor("none")
cbb = fig.colorbar(imb, ax=axb, fraction=0.04, pad=0.02); cbb.ax.tick_params(labelsize=6.5)
cbb.set_ticks([1e-4, 1e-3, 1e-2, 1e-1, 1.0]); cbb.set_ticklabels([r'$\mathrm{10^{-4}}$', r'$\mathrm{10^{-3}}$', r'$\mathrm{10^{-2}}$', r'$\mathrm{10^{-1}}$', r'$\mathrm{1}$']); cbb.ax.minorticks_off()
cbc = fig.colorbar(imc, ax=axc, fraction=0.04, pad=0.02); cbc.set_label(r"$|\mathbf{u}|\;(\hbar/m\xi)$", fontsize=7.5); cbc.ax.tick_params(labelsize=6.5)
save(fig, "ch03_phasefield")
