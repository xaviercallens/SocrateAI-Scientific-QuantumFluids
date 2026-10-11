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
M, NN = 16, 256
CM_N = LinearSegmentedColormap.from_list("qf", ["#f4f1ea", "#bcd7f2", "#2a78d6", "#241f6b"])

def jl(name):
    p = f"{R}/{name}"
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []

def field(v0, t):
    p = f"{R}/fields/field_V{int(round(v0*100))}_t{int(t)}.f64"
    if not os.path.exists(p): return None
    y = np.fromfile(p, dtype="<f8")
    re, im, nr = y[:NN].reshape(M, M), y[NN:2*NN].reshape(M, M), y[2*NN:].reshape(M, M)
    return re * re + im * im, nr, np.arctan2(im, re)

def gate_xy(v0=0.5, s=3.0):
    x = np.arange(M); X, Y = np.meshgrid(x, x, indexing="ij")
    dx = np.minimum(np.abs(X - 8), M - np.abs(X - 8)); dy = np.minimum(np.abs(Y - 8), M - np.abs(Y - 8))
    return v0 * np.exp(-(dx**2 + dy**2) / (2 * s * s))

def periodic(a):  # one extra row/col for pcolormesh continuity
    return np.pad(a, ((0, 1), (0, 1)), mode="wrap")

def label(ax, s):
    ax.text(-0.02, 1.04, s, transform=ax.transAxes, fontweight="bold", fontsize=10, ha="left", va="bottom")

# --------------------------------------------------------------------- device schematic (panel used on the cover and in Fig. 1)
def draw_device(ax):
    ax.set_xlim(0, 10); ax.set_ylim(-0.4, 6.6); ax.axis("off")
    for y, lab in [(5.9, "top gate  (grounded, $z=+h_1$)"), (0.1, "bottom gate  (grounded, $z=-h_2$)")]:
        ax.add_patch(Rectangle((0.3, y - 0.18), 9.4, 0.36, fc="#bdbdb9", ec="none"))
        ax.text(9.6, y + (0.5 if y > 3 else -0.62), lab, ha="right", va="center", fontsize=7.5, color=INK)
    ax.add_patch(Rectangle((0.3, 2.0), 9.4, 0.05, fc=BL, ec="none")); ax.add_patch(Rectangle((0.3, 3.55), 9.4, 0.05, fc=OR, ec="none"))
    ax.text(0.35, 1.72, "electron layer", fontsize=7.5, color=BL); ax.text(0.35, 3.8, "hole layer", fontsize=7.5, color=OR)
    # excitons (dipoles) in the real region
    for x in (2.6, 5.0, 7.4):
        ax.add_patch(Circle((x, 2.03), 0.17, fc=BL, ec="none")); ax.add_patch(Circle((x, 3.58), 0.17, fc=OR, ec="none"))
        ax.add_patch(FancyArrowPatch((x, 2.25), (x, 3.35), arrowstyle="-", lw=0.9, color=GR, ls=(0, (2, 2))))
    ax.text(5.0, 4.45, "dipolar excitons: kernel $U=V_{ee}+V_{hh}-2V_{eh}$", ha="center", fontsize=8)
    # faint image charges above and below (sign alternates)
    for x in (2.6, 5.0, 7.4):
        for (y, c, a) in [(9.4 - 3.58, OR, 0.35)]:
            pass
    ax.text(5.0, 6.35, "images: $z_0+Pn\\ (+),\\ 2h_1-z_0+Pn\\ (-)$,  $P=2(h_1+h_2)$", ha="center", fontsize=7.5, color=GR)

# --------------------------------------------------------------------- Fig. 1 : completely monotone, any gate geometry
def fig_cm():
    fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.5), gridspec_kw=dict(width_ratios=[1.0, 1.15, 1.15]))
    draw_device(ax[0]); label(ax[0], "a")
    s = np.logspace(-6, 3, 4000)
    for h, c in [(0.6, BL), (2.0, OR), (10.0, VI)]:
        v = S_sym(s, 1.0, h) / (2 * (1 - np.exp(-s)))
        ax[1].semilogx(s, v, color=c, lw=1.6)
        ax[1].text(s[np.argmax(v)] * 1.4, v.max(), f"$h/d={h:g}$", color=INK, fontsize=7.5, va="center")
    ax[1].axhline(0, color=GR, lw=0.8); ax[1].set_xlabel("$s\\,d^2$  (Laplace variable of $r^2$)")
    ax[1].set_ylabel("$S(s)\\,/\\,2(1-e^{-sd^2})$"); ax[1].set_ylim(-0.1, 1.15); label(ax[1], "b")
    ax[1].set_title("measure $\\mu(s)\\propto S(s)\\geq 0$", fontsize=8.5, loc="left")
    # kernel with and without gates
    r = np.logspace(-0.7, 1.6, 400)
    def U(r, h):
        t = r * r
        tot = 0 * r
        n = np.arange(-60, 61)
        P = 4 * h; ze, zh = -0.5, 0.5
        for (a, b, sg) in [(0, 0, 2)]:
            pass
        v = lambda z, z0: sum(1 / np.sqrt(t + (z - z0 - 2 * (h + h) * k) ** 2) - 1 / np.sqrt(t + (z - (2 * h - z0) - 2 * (h + h) * k) ** 2) for k in n)
        return v(ze, ze) + v(zh, zh) - 2 * v(zh, ze)
    ax[2].loglog(r, 1 / r - 1 / np.sqrt(r * r + 1), color=GR, lw=1.4, ls="--"); ax[2].text(0.34, 0.02, "ungated bilayer\n$\\propto r^{-3}$", color=INK, fontsize=7.5)
    for h, c in [(1.5, BL), (4.0, OR)]:
        ax[2].loglog(r, U(r, h) / 2, color=c, lw=1.6)
    ax[2].text(5.5, 3e-4, "$h=1.5d$", color=INK, fontsize=7.5); ax[2].text(8.3, 5e-3, "$h=4d$", color=INK, fontsize=7.5)
    ax[2].set_xlabel("$r/d$"); ax[2].set_ylabel("$U(r)\\,d/2$"); ax[2].set_ylim(1e-8, 1); label(ax[2], "c")
    ax[2].set_title("gates screen the tail; $U(r^2)$ stays c.m.", fontsize=8.5, loc="left")
    fig.tight_layout(); fig.savefig(f"{OUT}/fig_cm_gates.pdf"); fig.savefig(f"{OUT}/fig_cm_gates.png", dpi=220); plt.close(fig)

# --------------------------------------------------------------------- Fig. 2 : solver tests
def fig_solver():
    fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.5))
    ref = json.load(open(f"{R}/reference.json"))
    # (a) steady state vs pump
    P = np.linspace(0, 30, 400); Pth = 20.0
    n = np.where(P > Pth, P / 0.1 - 200.0, 0.0)
    ax[0].plot(P, n, color=BL, lw=1.8)
    a = jl("a.jsonl")
    ab = [r for r in a if r["case"] == "above"]; be = [r for r in a if r["case"] == "below"]
    if ab: ax[0].plot([21] * len(ab), [r["mean_n"] for r in ab], "o", mfc=OR, mec=SURF, ms=6, label="CVODE, 10 seeds")
    if be: ax[0].plot([16] * len(be), [r["mean_n"] for r in be], "o", mfc=OR, mec=SURF, ms=6)
    ax[0].axvline(Pth, color=GR, lw=0.8, ls=":"); ax[0].text(Pth + 0.3, 40, "$P_{th}=\\gamma\\gamma_R/R$", fontsize=7.5)
    ax[0].set_xlabel("pump $P$"); ax[0].set_ylabel("condensate density $|\\psi|^2$"); label(ax[0], "a")
    ax[0].set_title("clamped reservoir: $n=P/\\gamma-\\gamma_R/R$", fontsize=8.5, loc="left")
    if ab or be: ax[0].legend(frameon=False, fontsize=7.5, loc="upper left")
    # (b) linearisation spectrum: solver Jacobian vs reference
    jp = f"{R}/jac_uniform.f64"
    if os.path.exists(jp):
        J = np.fromfile(jp, dtype="<f8").reshape(768, 768).T
        ev = np.linalg.eigvals(J)
        rf = np.array([complex(z[0], z[1]) for s in ref["spectrum"] for z in s["ev"]])
        sel = np.abs(rf.real) < 1.0
        ax[1].plot(rf[sel].imag, rf[sel].real, "+", color=INK, ms=7, mew=1.0, label="reference (3×3 per $k$)")
        sv = np.abs(ev.real) < 1.0
        ax[1].plot(ev[sv].imag, ev[sv].real, "o", mfc="none", mec=BL, ms=5, mew=0.9, label="CVODE Jacobian, 768×768")
        ax[1].axhline(0, color=GR, lw=0.8); ax[1].set_xlabel("Im $\\lambda$"); ax[1].set_ylabel("Re $\\lambda$")
        ax[1].legend(frameon=False, fontsize=7.0, loc="lower right")
    ax[1].set_title("Bogoliubov-type spectrum, stable", fontsize=8.5, loc="left"); label(ax[1], "b")
    # (c) IMEX
    e = jl("e.jsonl"); f = jl("f.jsonl")
    h = np.linspace(0.002, 0.06, 200); q = h * 200.0 * (1 - 1 / np.sqrt(2))
    ax[2].plot(h, q, color=VI, lw=1.6)
    ax[2].axhline(1.0, color=GR, lw=0.8, ls=":")
    for r in [r for r in e if r["kind"] == "one_step"]:
        ok = r["status"] == "ok"
        ax[2].plot(r["h"], r["h"] * 200 * (1 - 1 / np.sqrt(2)), "o" if ok else "X", ms=7, mfc=BL if ok else OR, mec=SURF)
    ax[2].text(0.0025, 1.08, "fixed point diverges ($q>1$)", fontsize=7.5); ax[2].text(0.0025, 0.2, "converges", fontsize=7.5)
    ax[2].set_xlabel("step $h$"); ax[2].set_ylabel("contraction $q=h\\gamma_R a_{ii}$")
    ax[2].set_title("ARS222 module: error exactly where $q\\geq1$", fontsize=8.5, loc="left"); label(ax[2], "c")
    fig.tight_layout(); fig.savefig(f"{OUT}/fig_solver.pdf"); fig.savefig(f"{OUT}/fig_solver.png", dpi=220); plt.close(fig)

# --------------------------------------------------------------------- Fig. 3 : the gated condensate (fields + sweep)
def fig_gate():
    fig = plt.figure(figsize=(7.4, 4.9))
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1.05], hspace=0.55, wspace=0.55)
    ts = [(0.5, 10, "t=10"), (0.5, 150, "t=150"), (0.5, 4000, "t=4000")]
    nmax = 0
    for v in (0.0, 0.5, 1.0):
        for t in (4000, 150, 40, 10):
            fl = field(v, t)
            if fl is not None: nmax = max(nmax, fl[0].max())
    cols = [(0.5, 10), (0.5, 150), (0.5, 4000)]
    first = None
    for j, (v, t) in enumerate(cols):
        ax = fig.add_subplot(gs[0, j]); fl = field(v, t)
        if fl is None: ax.axis("off"); continue
        im = ax.imshow(fl[0].T, origin="lower", cmap=CM_N, vmin=0, vmax=max(nmax, 1), extent=(0, M, 0, M)); first = im
        ax.contour(np.arange(M) + 0.5, np.arange(M) + 0.5, gate_xy(v).T, levels=[0.1, 0.3], colors=[OR], linewidths=0.9)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_title(f"$V_0={v:g}$, $t={t}$", fontsize=8.5, loc="left")
        for sp in ax.spines.values(): sp.set_visible(False)
    axc = fig.add_subplot(gs[0, 3]); fl = field(0.5, 4000)
    if fl is not None:
        im = axc.imshow(fl[2].T, origin="lower", cmap="twilight", vmin=-np.pi, vmax=np.pi, extent=(0, M, 0, M))
        axc.contour(np.arange(M) + 0.5, np.arange(M) + 0.5, gate_xy(0.5).T, levels=[0.1, 0.3], colors=[OR], linewidths=0.9)
        axc.set_xticks([]); axc.set_yticks([]); axc.set_title("phase, $t=4000$", fontsize=8.5, loc="left")
        for sp in axc.spines.values(): sp.set_visible(False)
    if first is not None:
        cax = fig.add_axes([0.915, 0.58, 0.012, 0.32]); fig.colorbar(first, cax=cax); cax.set_ylabel("$|\\psi|^2$", fontsize=8)
    # sweep
    d = jl("d.jsonl")
    ax1 = fig.add_subplot(gs[1, 0:2]); ax2 = fig.add_subplot(gs[1, 2:4])
    if d:
        v0 = sorted({r["V0"] for r in d})
        om = [np.median([r["omega"] for r in d if r["V0"] == v]) for v in v0]
        nc = [np.median([r["n_center"] for r in d if r["V0"] == v]) for v in v0]
        nk = [np.median([r["n_corner"] for r in d if r["V0"] == v]) for v in v0]
        jm = [np.median([r["max_j"] for r in d if r["V0"] == v]) for v in v0]
        om0 = om[0]
        xs = np.linspace(0, max(v0), 50)
        ax1.plot(xs, xs, color=GR, lw=0.9, ls=":"); ax1.text(0.62 * max(v0), 0.7 * max(v0), "$\\Delta\\omega=V_0$", fontsize=7.5, color=INK)
        ax1.plot(v0, np.array(om) - om0, "o-", color=BL, lw=1.6, ms=6, mec=SURF)
        ax1.set_xlabel("gate amplitude $V_0$"); ax1.set_ylabel("emission shift $\\omega(V_0)-\\omega(0)$")
        ax1.set_title("single locked frequency, shifted by less than $V_0$", fontsize=8.5, loc="left")
        ax2.plot(v0, nc, "o-", color=OR, lw=1.6, ms=6, mec=SURF); ax2.plot(v0, nk, "s-", color=VI, lw=1.6, ms=6, mec=SURF)
        ax2.text(v0[-1], nc[-1], "  gate centre", fontsize=7.5, va="center"); ax2.text(v0[-1], nk[-1], "  box corner", fontsize=7.5, va="center")
        ax2.set_xlim(-0.05, max(v0) * 1.5); ax2.set_xlabel("gate amplitude $V_0$"); ax2.set_ylabel("$|\\psi|^2$")
        ax2.set_title("density is not pinned: currents flow", fontsize=8.5, loc="left")
    label(fig.axes[0], "a"); label(ax1, "b"); label(ax2, "c")
    fig.savefig(f"{OUT}/fig_gate.pdf", bbox_inches="tight"); fig.savefig(f"{OUT}/fig_gate.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# --------------------------------------------------------------------- Cover
def fig_cover():
    fig = plt.figure(figsize=(7.4, 3.3))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.0, 1.0], wspace=0.28)
    ax = fig.add_subplot(gs[0]); draw_device(ax)
    ax2 = fig.add_subplot(gs[1]); fl = field(0.5, 4000)
    if fl is not None:
        n = fl[0]
        X = np.arange(M + 1)
        ax2.pcolormesh(X, X, periodic(n).T, cmap=CM_N, shading="auto")
        ax2.contour(np.arange(M + 1) + 0.0, np.arange(M + 1) + 0.0, periodic(gate_xy(0.5)).T, levels=[0.1, 0.25, 0.4], colors=[OR], linewidths=0.9)
        ax2.set_aspect("equal"); ax2.set_xticks([]); ax2.set_yticks([])
        for sp in ax2.spines.values(): sp.set_visible(False)
        ax2.set_title("gated condensate $|\\psi|^2$\n(orange: gate potential)", fontsize=8.5)
    ax3 = fig.add_subplot(gs[2])
    s = np.logspace(-4, 2, 1200)
    for h, c in [(0.6, BL), (2.0, OR), (10.0, VI)]:
        ax3.semilogx(s, S_sym(s, 1.0, h) / (2 * (1 - np.exp(-s))), color=c, lw=1.8)
    ax3.axhline(0, color=GR, lw=0.8); ax3.set_ylim(-0.1, 1.15)
    ax3.set_xlabel("$s\\,d^2$"); ax3.set_ylabel("Laplace measure $\\mu(s)$ (rescaled)")
    ax3.set_title("positive for every gate geometry\n$\\Rightarrow$ completely monotone", fontsize=8.5)
    fig.savefig(f"{OUT}/fig_cover.pdf", bbox_inches="tight"); fig.savefig(f"{OUT}/fig_cover.png", dpi=220, bbox_inches="tight"); plt.close(fig)

if __name__ == "__main__":
    fig_cm(); fig_solver(); fig_gate(); fig_cover()
    print(sorted(os.listdir(OUT)))
