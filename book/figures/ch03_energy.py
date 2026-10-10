"""Figure ch03_energy: the kinetic energy of the field splits into a local quantum-pressure part and a long-range flow part
(the identity of `kinetic_density_split`, here on the solver field around the + vortex of the pair, t = 20).
(a-c) the three energy densities on a common logarithmic scale; (d) energy inside radius R about the + vortex: the flow part grows like
pi ln R, the quantum-pressure part saturates inside the core; (e) azimuthal mean of the density against the exact radial Gross-Pitaevskii vortex.
Data: ch03_derived.npz / ch03_numbers.json (ch03_compute.py) and the snapshot of ch03_run.py.
Run: OMP_NUM_THREADS=1 PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch03_energy.py"""
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from ch03_analysis import madelung_fields, L, CACHE
HERE = Path(__file__).resolve().parent
D = np.load(HERE / "ch03_derived.npz"); J = json.loads((HERE / "ch03_numbers.json").read_text())["pair"]
T_SNAP = J["snapshot_time"]
z = np.load(f"{CACHE}/pair_d12.npz"); c = z["snaps"][T_SNAP]; pos = z["pos"][T_SNAP]; q = z["q"]
ip = int(np.nonzero(q == 1)[0][0]); cen = pos[ip]
F = madelung_fields(c, 4); dxf = F["dx"]; nf = F["n"].shape[0]

fig = plt.figure(figsize=(TEXTW, 3.95))
gs = fig.add_gridspec(2, 6, height_ratios=[0.95, 1.15], hspace=0.50, wspace=1.2, left=0.085, right=0.985, top=0.965, bottom=0.095)
axm = [fig.add_subplot(gs[0, 0:2]), fig.add_subplot(gs[0, 2:4]), fig.add_subplot(gs[0, 4:6])]
axd = fig.add_subplot(gs[1, 0:3]); axe = fig.add_subplot(gs[1, 3:6])
# (a-c) maps
half = 5.5
i0, i1 = int(round((cen[0] - half) / dxf)), int(round((cen[0] + half) / dxf)); j0, j1 = int(round((cen[1] - half) / dxf)), int(round((cen[1] + half) / dxf))
sl = (slice(i0, i1), slice(j0, j1)); ext = [i0 * dxf - cen[0], i1 * dxf - cen[0], j0 * dxf - cen[1], j1 * dxf - cen[1]]
cm = LinearSegmentedColormap.from_list("qfe", ["#0B1B2B", BLUE, "#9EC1DD", PAPER, "#E8B07A", RED])
for ax, key, title, let in ((axm[0], "kin", r"$\frac{1}{2}|\nabla\psi|^2$", "a"), (axm[1], "q", r"$\frac{1}{2}|\nabla\sqrt{n}|^2$", "b"), (axm[2], "flow", r"$\frac{1}{2}\,n\,|\mathbf{u}|^2$", "c")):
    im = ax.imshow(np.transpose(F[key][sl]), origin="lower", extent=ext, cmap=cm, norm=LogNorm(1e-5, 0.4), interpolation="bilinear", aspect="equal")
    ax.set_title(title, fontsize=9, pad=3); ax.set_xticks([-4, 0, 4]); ax.set_yticks([-4, 0, 4]); ax.set_xlabel(r"$\Delta x/\xi$")
    for sp in ax.spines.values(): sp.set_visible(True)
    panel(ax, let)
axm[1].set_yticklabels([]); axm[2].set_yticklabels([]); axm[0].set_ylabel(r"$\Delta y/\xi$")
cb = fig.colorbar(im, ax=axm, fraction=0.025, pad=0.012); cb.ax.tick_params(labelsize=6.5)
cb.set_ticks([1e-5, 1e-4, 1e-3, 1e-2, 1e-1]); cb.set_ticklabels([r"$\mathrm{10^{-5}}$", r"$\mathrm{10^{-4}}$", r"$\mathrm{10^{-3}}$", r"$\mathrm{10^{-2}}$", r"$\mathrm{10^{-1}}$"]); cb.ax.minorticks_off()
# (d) cumulative energies
Rr = D["en_R"]; Ef = D["en_flow_plus"]; Eq = D["en_q_plus"]; Ek = D["en_kin_plus"]
axd.semilogx(Rr, Ek, "-", color=GREY, lw=1.0, label=r"kinetic $\frac{1}{2}|\nabla\psi|^2$")
axd.semilogx(Rr, Ef, "-", color=BLUE, lw=1.6, label=r"flow $\frac{1}{2} n|\mathbf{u}|^2$")
axd.semilogx(Rr, Eq, "-", color=ORANGE, lw=1.6, label=r"quantum pressure")
m = (Rr >= 2.5) & (Rr <= 5.0)
ref = np.pi * np.log(Rr)
off = np.mean(Ef[m] - ref[m])
axd.semilogx(Rr, ref + off, "--", color=RED, lw=1.0, label=r"$\pi\ln R$ + const.")
axd.axvspan(2.5, 5.0, color=GOLD, alpha=0.15, lw=0)
axd.set_xlabel(r"radius $R/\xi$ about the $+$ vortex"); axd.set_ylabel(r"energy inside $R$  $(\hbar^2 n_0/m)$")
axd.set_xlim(0.12, 9); axd.set_ylim(-0.3, 9.5)
axd.set_xticks([0.2, 0.5, 1, 2, 5]); axd.set_xticklabels(["0.2", "0.5", "1", "2", "5"]); axd.minorticks_off()
axd.legend(loc="upper left", fontsize=6.8, handlelength=1.3, borderaxespad=0.2)
panel(axd, "d")
# (e) density profile against the exact radial solution (arrays computed by ch03_compute.py)
rb = D["prof_r"]; nb = D["prof_n"]
rs = np.linspace(0.02, 8, 400)
from ch03_gpvortex import solve as solve_vortex
sol = solve_vortex(R=40.0); fs = sol.sol(rs)[0]
axe.plot(rs, fs ** 2, "-", color=ORANGE, lw=1.4, label=r"exact radial solution $f(r)^2$")
axe.plot(rb, nb, "o", ms=3.2, color=BLUE, label="solver, azimuthal mean about the core")
axe.plot(rs, 1 - 1 / (2 * rs ** 2), ":", color=GREY, lw=1.0, label=r"$1-1/(2r^2)$")
axe.set_xlim(0, 8); axe.set_ylim(-0.02, 1.05)
axe.set_xlabel(r"distance $r/\xi$ from the core"); axe.set_ylabel(r"density $n/n_0$")
axe.legend(loc="lower right", fontsize=6.8, handlelength=1.3, borderaxespad=0.2)
panel(axe, "e")
save(fig, "ch03_energy")
