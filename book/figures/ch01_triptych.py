"""Chapter 1, triptych: ONE vortex-antivortex pair in a two-dimensional superfluid seen by the three instruments.
(a) the solver's field: density |psi|^2 (colour) and the superflow v = Im(conj(psi) grad psi)/|psi|^2 (streamlines);
(b) the phase arg(psi) with four closed lattice loops A-D;
(c-f) the proof: the running sum of principal phase differences (QuantumFluids.VortexWinding.pdiff) along each loop ends at 2 pi m, m integer.
Engine: qf_pgpe (Rust projected GPE of rusty-SUNDIALS), imprint_v2, evolution to t = 10, N = 128, L = 64, units hbar = m = g = n0 = 1.
Writes the section "triptych" of ch01_numbers.json, including the continuum circulation of the same field around the same loops
(Gauss-Legendre on the exact band-limited field), the conserved quantities, and the minimum density.
Run:  PYTHONPATH=/mnt/data/xdev-cache/qf_ext  flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice .venv/bin/python book/figures/ch01_triptych.py"""
import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
from ch01_common import *
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, Normalize

plt.rcParams["axes.unicode_minus"] = False
T_END = 10.0
t0 = time.time()
s = engine()
c0 = s.imprint_v2(s.uniform(), IMPRINT, CHARGE)
E0, N0, P0 = s.energy(c0), s.norm(c0), s.momentum(c0)
pos0, q0 = s.detect(c0)
c = s.run(c0, T_END)
seconds = time.time() - t0
E1, N1, P1 = s.energy(c), s.norm(c), s.momentum(c)
pos, q = s.detect(c)
psi, vx, vy = velocity_grid(c)
n = np.abs(psi) ** 2; th = np.angle(psi)
fd = fourier_data(c)

ip = lambda p: (int(round(p[0] / DX)), int(round(p[1] / DX)))
vp = [p for p, qq in zip(pos, q) if qq > 0][0]; vm = [p for p, qq in zip(pos, q) if qq < 0][0]
(ip_, jp_), (im_, jm_) = ip(vp), ip(vm)
h = 7
boxes = {                                  # lattice squares (i0, j0, i1, j1)
    "A": ("vortex", (ip_ - h, jp_ - h, ip_ + h, jp_ + h)),
    "B": ("antivortex", (im_ - h, jm_ - h, im_ + h, jm_ + h)),
    "C": ("both", (ip_ - h - 3, jp_ - h - 3, im_ + h + 3, jm_ + h + 3)),
    "D": ("empty fluid", (88, 80, 102, 94)),
}
loops = {k: (nm, square_loop(*b)) for k, (nm, b) in boxes.items()}
cols = {"A": "#111111", "B": "#111111", "C": ORANGE, "D": TEAL}
styles = {"A": "-", "B": (0, (4, 2)), "C": "-", "D": "-"}

fig = plt.figure(figsize=(TEXTW, 5.9))
outer = fig.add_gridspec(2, 1, height_ratios=[1.6, 1], hspace=0.42)
top = outer[0].subgridspec(1, 2, wspace=0.10)
gs = outer[1].subgridspec(1, 4, wspace=0.55)
ext = [0, L, 0, L]
axd = fig.add_subplot(top[0, 0]); axp = fig.add_subplot(top[0, 1])
# (a) density + streamlines
im = axd.imshow(n.T, origin="lower", extent=ext, cmap="Blues_r", vmin=0, vmax=1.1, interpolation="bilinear")
i0, i1 = 24, 104
xg = np.arange(i0, i1 + 1) * DX
U = vx[i0:i1 + 1, i0:i1 + 1].T; V = vy[i0:i1 + 1, i0:i1 + 1].T
speed = np.hypot(U, V)
spcm = LinearSegmentedColormap.from_list("sp", ["#EDC9A0", ORANGE, RED, "#4D140C"])
sl = axd.streamplot(xg, xg, U, V, color=np.log10(np.maximum(speed, 1e-3)), cmap=spcm, norm=Normalize(np.log10(0.035), np.log10(0.9)),
                    linewidth=0.85, density=1.25, arrowsize=0.75, arrowstyle="-|>", minlength=0.25, zorder=2)
cb = fig.colorbar(im, ax=axd, location="bottom", shrink=0.78, pad=0.20, aspect=28); cb.set_label(r"density $|\psi|^2$"); cb.outline.set_visible(False)
im2 = axp.imshow(th.T, origin="lower", extent=ext, cmap=vortex_cmap(), vmin=-np.pi, vmax=np.pi, interpolation="bilinear")
cb2 = fig.colorbar(im2, ax=axp, location="bottom", shrink=0.78, pad=0.20, aspect=28, ticks=[-np.pi, 0, np.pi]); cb2.ax.set_xticklabels([r"$-\pi$", "0", r"$\pi$"])
cb2.set_label(r"phase $\arg\psi$"); cb2.outline.set_visible(False)
for ax in (axd, axp):
    ax.set_xlabel(r"$x/\xi$"); ax.set_xlim(12, 52); ax.set_ylim(12, 52)
    for p, qq in zip(pos, q):
        ax.plot(*p, marker="o" if qq > 0 else "s", ms=5.5, mfc="none", mec="#111111" if ax is axp else RED, mew=1.3, zorder=6)
axd.set_ylabel(r"$y/\xi$"); axp.set_yticklabels([])
panel(axd, "a"); panel(axp, "b")
axd.set_title("superflow and density", fontsize=9.5)
axp.set_title(r"phase and four loops", fontsize=9.5)
halo = [pe.withStroke(linewidth=2.4, foreground="white")]
for key, (name, pts) in loops.items():
    xs = np.array([p[0] for p in pts]) * DX; ys = np.array([p[1] for p in pts]) * DX
    axp.plot(xs, ys, color="white", lw=3.0, zorder=3, solid_capstyle="butt")
    axp.plot(xs, ys, color=cols[key], lw=1.5, ls=styles[key], zorder=4)
    xm = (xs.min() + xs.max()) / 2
    if key == "C":
        axp.text(xm, ys.min() - 0.35, key, color=cols[key], fontsize=9.5, fontweight="bold", ha="center", va="top", path_effects=halo, zorder=7)
    else:
        axp.text(xm, ys.max() + 0.35, key, color=cols[key], fontsize=9.5, fontweight="bold", ha="center", va="bottom", path_effects=halo, zorder=7)
res = {}
for m, (key, (name, pts)) in enumerate(loops.items()):
    ax = fig.add_subplot(gs[0, m])
    ph = np.array([th[i, j] for i, j in pts]); steps = pdiff(ph[:-1], ph[1:])
    cum = np.concatenate([[0.0], np.cumsum(steps)]); w = cum[-1] / (2 * np.pi); wi = int(round(w))
    ax.plot(cum / (2 * np.pi), color=cols[key], lw=1.6, ls=styles[key] if key == "B" else "-")
    ax.axhline(0, color="#999999", lw=0.5)
    ax.set_ylim(-1.6, 1.6); ax.set_yticks([-1, 0, 1]); ax.set_xticks([0, len(steps)])
    ax.set_xticklabels(["0", r"$n$"]); ax.set_xlabel("steps along loop")
    if m == 0: ax.set_ylabel(r"$\sum\,\mathrm{pdiff}\,/\,2\pi$")
    ax.set_title(f"loop {key}: {name}", fontsize=8.0, color="#111111" if key in "AB" else cols[key], pad=5, loc="left")
    ytxt = -1.30 if wi > 0 else 1.30
    ax.text(0.5, 0.5 + ytxt / 3.2, "winding $=" + (f"{wi:+d}" if wi else "0") + "$", transform=ax.transAxes, ha="center", va="center", fontsize=9, fontweight="bold",
            color="#111111" if key in "AB" else cols[key])
    ax.set_xlim(0, len(steps))
    ax.text(-0.38, 1.20, "cdef"[m], transform=ax.transAxes, fontsize=11, fontweight="bold", color=BLUE)
    b = boxes[key][1]
    circ = polygon_circulation(fd, loop_corners(*b))
    trap = sum(0.5 * ((vx[a] + vx[bb]) * (bb[0] - a[0]) + (vy[a] + vy[bb]) * (bb[1] - a[1])) * DX for a, bb in zip(pts[:-1], pts[1:])) / (2 * np.pi)   # trapezoid rule on grid values
    res[key] = dict(name=name, box_grid=list(b), n_steps=len(steps), winding_raw=float(w), winding=wi, max_abs_step=float(np.abs(steps).max()),
                    circulation_over_kappa=float(circ), circulation_over_kappa_trapezoid_grid=float(trap))
save(fig, "ch01_triptych")
trap_h = {}                                  # trapezoid rule on the grid values, loops of half-side h around the vortex
for hh in (4, 5, 7, 9):
    pts_h = square_loop(ip_ - hh, jp_ - hh, ip_ + hh, jp_ + hh)
    trap_h[f"{hh * DX:g}"] = sum(0.5 * ((vx[a] + vx[bb]) * (bb[0] - a[0]) + (vy[a] + vy[bb]) * (bb[1] - a[1])) * DX for a, bb in zip(pts_h[:-1], pts_h[1:])) / (2 * np.pi)
out = dict(trapezoid_loop_A_by_half_side_xi=trap_h, N=N, L=L, t_end=T_END, imprint=[[26.0, 32.0, 1], [38.0, 32.0, -1]],
           detected_pos_t0=pos0.tolist(), detected_q_t0=[int(x) for x in q0], detected_pos=pos.tolist(), detected_q=[int(x) for x in q],
           separation_t0=float(abs(pos0[0][0] - pos0[1][0])), separation=float(abs(vm[0] - vp[0])), y_shift_of_pair=float(pos[0][1] - pos0[0][1]),
           energy_t0=E0, energy_t=E1, energy_rel_drift=float(abs(E1 - E0) / E0), norm_t0=N0, norm_t=N1, norm_rel_drift=float(abs(N1 - N0) / N0),
           momentum_t0=list(P0), momentum_t=list(P1), momentum_y_rel_drift=float(abs(P1[1] - P0[1]) / abs(P0[1])),
           min_density=float(n.min()), max_density=float(n.max()), loops=res, seconds=seconds, machine=machine_note(),
           max_abs_pdiff_step_over_pi=float(max(r["max_abs_step"] for r in res.values()) / np.pi))
update_numbers("triptych", out)
print(json.dumps(out, indent=1))
