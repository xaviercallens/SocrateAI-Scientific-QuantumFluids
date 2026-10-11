#!/usr/bin/env python3
"""Figures of the Phase 3 note (all generated from run records and reference files; nothing is typed in).
Usage: phase3_figures.py <results_dir> <out_dir>
Palette: blue #2a78d6, orange #eb6834, violet #6250d6 (validated, scripts/validate_palette.js, light mode), grey ink."""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle
from matplotlib.colors import LinearSegmentedColormap
sys.path.insert(0, os.path.dirname(__file__))
from gate_image_cm_sym import S as S_sym

R, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
BL, OR, VI, INK, GR, SURF = "#2a78d6", "#eb6834", "#6250d6", "#2b2b2b", "#9a9a98", "#fcfcfb"
plt.rcParams.update({"font.size": 8.5, "axes.edgecolor": GR, "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
                     "xtick.color": INK, "ytick.color": INK, "text.color": INK, "axes.labelcolor": INK, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "savefig.facecolor": SURF, "grid.color": "#e6e6e3", "grid.linewidth": 0.5,
                     "font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans"})
M = 8   # the gate sweep and field dumps are on the 8x8 grid (amendment A3)
NN = M * M
CM_N = LinearSegmentedColormap.from_list("qf", ["#f4f1ea", "#bcd7f2", "#2a78d6", "#241f6b"])

def jl(name):
    p = f"{R}/{name}"
    import glob
    stem = name[:-6]; out = []
    for q in sorted(glob.glob(f"{R}/{stem}.jsonl") + glob.glob(f"{R}/{stem}_*.jsonl")):
        out += [json.loads(l) for l in open(q) if l.strip()]
    return out

def field(v0, t):
    p = f"{R}/fields/field_V{int(round(v0*100))}_t{int(t)}.f64"
    if not os.path.exists(p): return None
    y = np.fromfile(p, dtype="<f8")
    re, im, nr = y[:NN].reshape(M, M), y[NN:2*NN].reshape(M, M), y[2*NN:].reshape(M, M)
    return re * re + im * im, nr, np.arctan2(im, re)

def gate_xy(v0=0.5, s=1.5):
    x = np.arange(M); X, Y = np.meshgrid(x, x, indexing="ij")
    dx = np.minimum(np.abs(X - M / 2), M - np.abs(X - M / 2)); dy = np.minimum(np.abs(Y - M / 2), M - np.abs(Y - M / 2))
    return v0 * np.exp(-(dx**2 + dy**2) / (2 * s * s))

def periodic(a):  # one extra row/col for pcolormesh continuity
    return np.pad(a, ((0, 1), (0, 1)), mode="wrap")

def label(ax, s):
    ax.text(-0.13, 1.10, s, transform=ax.transAxes, fontweight="bold", fontsize=10, ha="left", va="bottom")

# --------------------------------------------------------------------- device schematic (panel used on the cover and in Fig. 1)
def draw_device(ax):
    ax.set_xlim(0, 10); ax.set_ylim(-1.0, 8.0); ax.axis("off")
    for y, lab in [(7.2, "top gate  (grounded, $z=+h_1$)"), (0.0, "bottom gate  (grounded, $z=-h_2$)")]:
        ax.add_patch(Rectangle((0.3, y - 0.2), 9.4, 0.4, fc="#bdbdb9", ec="none"))
        ax.text(5.0, y + (0.65 if y > 3 else -0.75), lab, ha="center", va="center", fontsize=7.5, color=INK)
    ax.add_patch(Rectangle((0.3, 2.2), 9.4, 0.05, fc=BL, ec="none")); ax.add_patch(Rectangle((0.3, 4.6), 9.4, 0.05, fc=OR, ec="none"))
    ax.text(9.7, 1.75, "electron layer", fontsize=7.5, color=INK, ha="right"); ax.text(9.7, 5.0, "hole layer", fontsize=7.5, color=INK, ha="right")
    for x in (2.0, 4.6, 7.2):
        ax.add_patch(Circle((x, 2.22), 0.2, fc=BL, ec="none")); ax.add_patch(Circle((x, 4.62), 0.2, fc=OR, ec="none"))
        ax.add_patch(FancyArrowPatch((x, 2.5), (x, 4.34), arrowstyle="-", lw=0.9, color=GR, ls=(0, (2, 2))))
    # image charges: mirror of the excitons in the top gate (dim), alternating sign
    for x in (2.0, 4.6, 7.2):
        ax.add_patch(Circle((x, 7.2 + (7.2 - 4.62)), 0.2, fc="none", ec=OR, lw=0.8, ls=":")) if False else None
    ax.text(5.0, 3.4, "exciton: $d$", ha="center", va="center", fontsize=7.5, color=INK,
            bbox=dict(fc=SURF, ec="none", pad=1.5))
    ax.text(5.0, 6.25, "image charges, alternating sign,\nperiod $P=2(h_1+h_2)$", ha="center", va="center", fontsize=7.0, color=GR)

def kernel_laplace(r, h, d=1.0):
    """U(r) from its exact Laplace representation with the Poisson-resummed S(s) (no image truncation)."""
    ls = np.linspace(-14, 8, 6000); s = np.exp(ls)
    S = S_sym(s, d, h)
    w = S / np.sqrt(np.pi * s) * s   # ds = s dlog s
    return np.array([np.trapz(w * np.exp(-s * rr * rr), ls) for rr in r])

# --------------------------------------------------------------------- Fig. 1 : completely monotone, any gate geometry
def fig_cm():
    fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.7), gridspec_kw=dict(width_ratios=[1.0, 1.1, 1.1]))
    draw_device(ax[0]); label(ax[0], "a")
    s = np.logspace(-6, 3, 4000)
    for h, c, xt in [(10.0, VI, 1e-4), (2.0, OR, 3e-2), (0.6, BL, 1e1)]:
        v = S_sym(s, 1.0, h) / (2 * (1 - np.exp(-s)))
        ax[1].semilogx(s, v, color=c, lw=1.6)
        ax[1].text(xt, 1.07, f"$h/d={h:g}$", color=INK, fontsize=7, va="center", ha="center")
    ax[1].axhline(0, color=GR, lw=0.8); ax[1].set_xlabel("$s\\,d^2$  (Laplace variable of $r^2$)")
    ax[1].set_ylabel("$S(s)\\,/\\,2(1-e^{-sd^2})$"); ax[1].set_ylim(-0.1, 1.2); label(ax[1], "b")
    ax[1].set_title("$S(s)\\geq0$: Laplace measure of $U(r^2)$", fontsize=8.5, loc="left")
    r = np.logspace(-0.7, 1.45, 120)
    ax[2].loglog(r, 1 / r - 1 / np.sqrt(r * r + 1), color=GR, lw=1.4, ls="--")
    ax[2].text(0.22, 1e-8 * 3, "dashed: ungated, $\\propto r^{-3}$", color=INK, fontsize=7.5)
    for h, c, tx, ty in [(1.5, BL, 1.1, 1e-6), (4.0, OR, 6.0, 1e-7)]:
        u = kernel_laplace(r, h) / 2
        ax[2].loglog(r, np.clip(u, 1e-12, None), color=c, lw=1.6); ax[2].text(tx, ty, f"$h={h:g}d$", color=INK, fontsize=7.5)
    ax[2].set_xlabel("$r/d$"); ax[2].set_ylabel("$U(r)\\,d/2$ (units $e^2/\\varepsilon$)"); ax[2].set_ylim(1e-9, 1); label(ax[2], "c")
    ax[2].set_title("tail screened", fontsize=8.5, loc="left")
    fig.tight_layout(); fig.savefig(f"{OUT}/fig_cm_gates.pdf"); fig.savefig(f"{OUT}/fig_cm_gates.png", dpi=220); plt.close(fig)

# --------------------------------------------------------------------- Fig. 2 : solver tests
def fig_solver():
    fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.6))
    ref = json.load(open(f"{R}/reference.json"))
    P = np.linspace(0, 30, 400); Pth = 20.0
    n = np.where(P > Pth, P / 0.1 - 200.0, 0.0)
    ax[0].plot(P, n, color=BL, lw=1.8)
    a = jl("a.jsonl")
    ab = [r for r in a if r["case"] == "above"]; be = [r for r in a if r["case"] == "below"]
    if ab: ax[0].plot([21] * len(ab), [r["mean_n"] for r in ab], "o", mfc=OR, mec=SURF, ms=6, label="CVODE (10 seeds)")
    if be: ax[0].plot([16] * len(be), [r["mean_n"] for r in be], "o", mfc=OR, mec=SURF, ms=6)
    ax[0].axvline(Pth, color=GR, lw=0.8, ls=":"); ax[0].text(Pth - 0.4, 62, "$P_{th}$", fontsize=8, ha="right")
    ax[0].set_xlabel("pump $P$"); ax[0].set_ylabel("condensate density $|\\psi|^2$"); label(ax[0], "a")
    ax[0].set_title("reservoir clamp", fontsize=8.5, loc="left")
    ax[0].text(25, 30, "$n=P/\\gamma-\\gamma_R/R$", fontsize=7.5, color=INK)
    ax[0].legend(frameon=False, fontsize=7.5, loc="upper left")
    jp = f"{R}/jac_uniform.f64"
    if os.path.exists(jp):
        J = np.fromfile(jp, dtype="<f8").reshape(768, 768).T
        ev = np.linalg.eigvals(J)
        rf = np.array([complex(z[0], z[1]) for s in ref["spectrum"] for z in s["ev"]])
        sel = np.abs(rf.real) < 1.0
        ax[1].plot(rf[sel].imag, rf[sel].real, "+", color=INK, ms=7, mew=1.0, label="reference ($3\\times3$ per $k$)")
        sv = np.abs(ev.real) < 1.0
        ax[1].plot(ev[sv].imag, ev[sv].real, "o", mfc="none", mec=BL, ms=5, mew=0.9, label="finite-diff. Jacobian ($768^2$)")
        ax[1].axhline(0, color=GR, lw=0.8); ax[1].set_xlabel("Im $\\lambda$"); ax[1].set_ylabel("Re $\\lambda$")
        ax[1].legend(frameon=False, fontsize=7.0, loc="lower center", bbox_to_anchor=(0.5, 0.22))
    ax[1].set_title("linearisation: no unstable mode", fontsize=8.5, loc="left"); label(ax[1], "b")
    e = jl("e.jsonl")
    h = np.linspace(0.002, 0.06, 200); q = h * 200.0 * (1 - 1 / np.sqrt(2))
    ax[2].plot(h, q, color=VI, lw=1.6)
    ax[2].axhline(1.0, color=GR, lw=0.8, ls=":")
    for r in [r for r in e if r["kind"] == "one_step"]:
        ok = r["status"] == "ok"
        ax[2].plot(r["h"], r["h"] * 200 * (1 - 1 / np.sqrt(2)), "o" if ok else "X", ms=7, mfc=BL if ok else OR, mec=SURF)
    ax[2].text(0.035, 0.25, "ok", fontsize=7.5, color=INK); ax[2].text(0.0225, 2.1, "error", fontsize=7.5, color=INK)
    ax[2].set_xlabel("step $h$"); ax[2].set_ylabel("$q=h\\gamma_R a_{ii}$")
    ax[2].set_title("IMEX: error for $q>1$ (5 steps tried)", fontsize=8.5, loc="left"); label(ax[2], "c")
    fig.tight_layout(); fig.savefig(f"{OUT}/fig_solver.pdf"); fig.savefig(f"{OUT}/fig_solver.png", dpi=220); plt.close(fig)

# --------------------------------------------------------------------- Fig. 3 : the gated condensate (fields + sweep)
def fig_gate():
    fig = plt.figure(figsize=(7.4, 4.7))
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1.0], hspace=0.62, wspace=0.55)
    nmax = 0
    for v in (0.0, 0.5, 1.0):
        for t in (4000, 150, 10):
            fl = field(v, t)
            if fl is not None: nmax = max(nmax, fl[0].max())
    first = None
    for j, (v, t) in enumerate([(0.5, 10), (0.5, 150), (0.5, 4000)]):
        ax = fig.add_subplot(gs[0, j]); fl = field(v, t)
        if fl is None: ax.axis("off"); continue
        im = ax.imshow(fl[0].T, origin="lower", cmap=CM_N, vmin=0, vmax=max(nmax, 1), extent=(0, M, 0, M), interpolation="bicubic"); first = im
        ax.contour(np.arange(M) + 0.5, np.arange(M) + 0.5, gate_xy(v).T, levels=[0.1, 0.3], colors=[OR], linewidths=0.9)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_title(f"$V_0={v:g}$, $t={t}$", fontsize=8.5, loc="left")
        for sp in ax.spines.values(): sp.set_visible(False)
        if j == 0: label(ax, "a")
    if first is not None:
        cax = fig.add_axes([0.13, 0.545, 0.5, 0.014]); fig.colorbar(first, cax=cax, orientation="horizontal"); cax.set_xlabel("$|\\psi|^2$", fontsize=8)
    axc = fig.add_subplot(gs[0, 3])
    for v, c in [(0.0, GR), (0.5, BL), (1.0, OR)]:
        fl = field(v, 4000)
        if fl is None: continue
        cut = fl[0][:, M // 2]
        axc.plot(np.arange(M) + 0.5, cut, "-o", color=c, lw=1.5, ms=3.5, mec=SURF, label=f"$V_0={v:g}$")
    axc.legend(frameon=False, fontsize=7, loc="center left", bbox_to_anchor=(0.9, 0.55))
    axc.set_xlim(0, M); axc.set_xlabel("$x$ (cut through the gate)"); axc.set_ylabel("$|\\psi|^2$"); axc.set_title("line cut, $t=4000$", fontsize=8.5, loc="left")
    d = jl("d.jsonl")
    ax1 = fig.add_subplot(gs[1, 0:2]); ax2 = fig.add_subplot(gs[1, 2:4])
    if d:
        v0 = sorted({r["V0"] for r in d})
        om = [np.median([r["omega"] for r in d if r["V0"] == v]) for v in v0]
        nc = [np.median([r["n_center"] for r in d if r["V0"] == v]) for v in v0]
        nk = [np.median([r["n_corner"] for r in d if r["V0"] == v]) for v in v0]
        om0 = om[0]
        xs = np.linspace(0, max(v0), 50)
        ax1.plot(xs, xs, color=GR, lw=0.9, ls=":"); ax1.text(0.55 * max(v0), 0.66 * max(v0), "$\\Delta\\omega=V_0$", fontsize=7.5, color=INK)
        ax1.plot(v0, np.array(om) - om0, "o-", color=BL, lw=1.6, ms=6, mec=SURF)
        ax1.set_xlabel("gate amplitude $V_0$"); ax1.set_ylabel("$\\omega(V_0)-\\omega(0)$")
        ax1.set_title("locked frequency shift (box-area average)", fontsize=8.5, loc="left"); label(ax1, "b")
        ax2.plot(v0, nc, "o-", color=OR, lw=1.6, ms=6, mec=SURF); ax2.plot(v0, nk, "s-", color=VI, lw=1.6, ms=6, mec=SURF)
        ax2.text(v0[-1] + 0.04, nc[-1], "gate centre", fontsize=7.5, va="center"); ax2.text(v0[-1] + 0.04, nk[-1], "box corner", fontsize=7.5, va="center")
        ax2.set_xlim(-0.05, max(v0) * 1.6); ax2.set_xlabel("gate amplitude $V_0$"); ax2.set_ylabel("$|\\psi|^2$")
        ax2.set_title("density not pinned: currents flow", fontsize=8.5, loc="left"); label(ax2, "c")
    fig.savefig(f"{OUT}/fig_gate.pdf", bbox_inches="tight"); fig.savefig(f"{OUT}/fig_gate.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# --------------------------------------------------------------------- Cover
def fig_cover():
    fig = plt.figure(figsize=(7.4, 3.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.0, 1.0], wspace=0.30)
    ax = fig.add_subplot(gs[0]); draw_device(ax)
    ax2 = fig.add_subplot(gs[1]); fl = field(0.5, 4000)
    if fl is not None:
        ax2.imshow(fl[0].T, origin="lower", cmap=CM_N, extent=(0, M, 0, M), interpolation="bicubic")
        ax2.contour(np.arange(M) + 0.5, np.arange(M) + 0.5, gate_xy(0.5).T, levels=[0.1, 0.25, 0.4], colors=[OR], linewidths=0.9)
        ax2.set_aspect("equal"); ax2.set_xticks([]); ax2.set_yticks([])
        for sp in ax2.spines.values(): sp.set_visible(False)
        ax2.set_title("gated condensate $|\\psi|^2$\n(orange: gate potential)", fontsize=8.5)
    ax3 = fig.add_subplot(gs[2])
    s = np.logspace(-4, 2, 1200)
    for h, c, xt in [(10.0, VI, 3e-4), (2.0, OR, 2e-2), (0.6, BL, 3e1)]:
        ax3.semilogx(s, S_sym(s, 1.0, h) / (2 * (1 - np.exp(-s))), color=c, lw=1.8)
        ax3.text(xt, 1.07, f"$h/d={h:g}$", fontsize=7, ha="center", va="center")
    ax3.axhline(0, color=GR, lw=0.8); ax3.set_ylim(-0.1, 1.2)
    ax3.set_xlabel("$s\\,d^2$"); ax3.set_ylabel("Laplace measure (rescaled)")
    ax3.set_title("non-negative for every gate geometry\n$\\Rightarrow$ completely monotone", fontsize=8.5)
    fig.savefig(f"{OUT}/fig_cover.pdf", bbox_inches="tight"); fig.savefig(f"{OUT}/fig_cover.png", dpi=220, bbox_inches="tight"); plt.close(fig)

if __name__ == "__main__":
    fig_cm(); fig_solver(); fig_gate(); fig_cover()
    print(sorted(os.listdir(OUT)))
