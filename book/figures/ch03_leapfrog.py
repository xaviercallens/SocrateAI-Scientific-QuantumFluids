"""Figure ch03_leapfrog: two vortex pairs of the same sense leapfrog (qf-pgpe, 120 time units) against the periodic point-vortex model
integrated with rusty-SUNDIALS CVODE.  (a-f) the wave function at six times, phase as hue and density as brightness, the view re-centred on the
centroid of the four vortices; (g) the tracked vortices (solid) and the CVODE trajectories (dashed); (h) the largest position error.
Data: /mnt/data/xdev-cache/ch03/quad.npz (ch03_run.py) and figures/ch03_derived.npz, ch03_numbers.json (ch03_compute.py, part `quad`).
Run: OMP_NUM_THREADS=1 PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch03_leapfrog.py"""
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
from matplotlib.colors import LinearSegmentedColormap
from ch03_analysis import refine, L, CACHE
HERE = Path(__file__).resolve().parent
D = np.load(HERE / "ch03_derived.npz"); J = json.loads((HERE / "ch03_numbers.json").read_text())["quad"]
z = np.load(f"{CACHE}/quad.npz"); snaps = z["snaps"]; snap_t = z["snap_t"]; q = z["q"]
t = D["quad_t"]; P_gp = D["quad_pos_gp"]; P_ode = D["quad_pos_ode"]; err = D["quad_err"]
TS = [float(x) for x in os.environ.get("CH03_TS", "0,30,60,80,100,120").split(",")]
cyc = LinearSegmentedColormap.from_list("qfwheel", [BLUE, TEAL, GOLD, ORANGE, RED, "#7A3B6E", BLUE], N=512)
HALF = 20.0

def composite(c, centre):
    psi, C, k1, dxf = refine(c, 3)
    n = np.abs(psi) ** 2
    phase = np.angle(psi * np.exp(-1j * np.angle(c[0, 0]))) % (2 * np.pi)
    nf = n.shape[0]
    sx = nf // 2 - int(round(centre[0] / dxf)); sy = nf // 2 - int(round(centre[1] / dxf))
    n = np.roll(n, (sx, sy), axis=(0, 1)); phase = np.roll(phase, (sx, sy), axis=(0, 1))
    h = int(round(HALF / dxf)); sl = slice(nf // 2 - h, nf // 2 + h)
    n = n[sl, sl]; phase = phase[sl, sl]
    rgb = cyc(phase / (2 * np.pi))[..., :3]
    bright = np.clip(n, 0, 1) ** 0.6 * (0.80 + 0.20 * np.cos(6 * phase))
    return np.clip(rgb * bright[..., None] + (1 - np.clip(n, 0, 1) ** 0.6)[..., None] * np.array([0.03, 0.04, 0.07]), 0, 1)

fig = plt.figure(figsize=(TEXTW, 5.15))
gs = fig.add_gridspec(2, 6, hspace=0.40, wspace=0.55, left=0.075, right=0.985, top=0.975, bottom=0.458)    # six snapshots
gb = fig.add_gridspec(1, 6, wspace=0.55, left=0.075, right=0.985, top=0.312, bottom=0.07)                  # (g, h); the gap above holds the x labels and the legend of (g)
axs = [fig.add_subplot(gs[i // 3, 2 * (i % 3): 2 * (i % 3) + 2]) for i in range(6)]
for i, (ax, tt) in enumerate(zip(axs, TS)):
    k = int(np.argmin(np.abs(snap_t - tt))); tk = snap_t[k]
    pos = P_gp[int(tk)]
    # centre on the centroid of the four vortices (periodic mean around the first vortex)
    ref = pos[0]; rel = (pos - ref + L / 2) % L - L / 2
    centre = ref + rel.mean(0)
    img = composite(snaps[k], centre)
    ax.imshow(np.transpose(img, (1, 0, 2)), origin="lower", extent=[-HALF, HALF, -HALF, HALF], interpolation="bilinear", aspect="equal")
    relp = (pos - centre + L / 2) % L - L / 2
    for (px, py), qq in zip(relp, q):
        ax.plot(px, py, marker="o", ms=7.5, mfc="none", mec="white", mew=0.8)
        ax.text(px, py, "+" if qq > 0 else "\u2212", color="white", ha="center", va="center", fontsize=6.5)
    ax.set_xticks([-15, 0, 15]); ax.set_yticks([-15, 0, 15]); ax.tick_params(labelsize=7)
    ax.text(0.03, 0.95, r"$t=%d$" % tk, transform=ax.transAxes, color="white", fontsize=8.5, va="top")
    panel(ax, "abcdef"[i])
    for sp in ax.spines.values(): sp.set_visible(True)
    if i % 3: ax.set_yticklabels([])
    if i < 3: ax.set_xticklabels([])
axs[0].set_ylabel(r"$\Delta y/\xi$"); axs[3].set_ylabel(r"$\Delta y/\xi$")
for a in axs[3:]: a.set_xlabel(r"$\Delta x/\xi$")
# (g) trajectories
axg = fig.add_subplot(gb[0, 0:3]); axh = fig.add_subplot(gb[0, 3:6])
cols = [BLUE, ORANGE, TEAL, RED]
names = [r"rear $+$", r"rear $-$", r"front $+$", r"front $-$"]
for a in range(4):
    axg.plot(P_gp[:, a, 0], P_gp[:, a, 1], "-", color=cols[a], lw=1.5, label=names[a])
    axg.plot(P_ode[:, a, 0], P_ode[:, a, 1], "--", color="#222222", lw=0.8)
    axg.plot(P_gp[0, a, 0], P_gp[0, a, 1], "o", ms=3.5, color=cols[a])
axg.plot([], [], "--", color="#222222", lw=0.8, label="CVODE")
axg.set_xlabel(r"$x/\xi$"); axg.set_ylabel(r"$y/\xi$")
axg.set_xlim(22.5, 41.5); axg.set_ylim(25, 63)
axg.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=6.4, handlelength=1.3, borderaxespad=0.1, ncol=3, labelspacing=0.25, columnspacing=0.9)
panel(axg, "g")
axh.semilogy(t[1:], np.maximum(err[1:], 1e-4), "-", color=BLUE, lw=1.4)
for tp in J["pass_times"]["gp"]:
    axh.axvline(tp, color=GREY, lw=0.8, ls=":")
axh.set_xlabel("time  $t\\,c/\\xi$"); axh.set_ylabel(r"max position error $/\xi$")
axh.set_xlim(0, t[-1]); axh.set_ylim(1e-2, 20)
axh.set_yticks([1e-2, 1e-1, 1, 10]); axh.set_yticklabels(["0.01", "0.1", "1", "10"]); axh.minorticks_off()
panel(axh, "h")
save(fig, "ch03_leapfrog")
