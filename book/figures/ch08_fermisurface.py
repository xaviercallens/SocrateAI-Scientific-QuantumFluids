"""Chapter 8, figure (ch08_fermisurface): the Fermi circle as the dynamical variable, F = 0 against F = 4.

nu(theta, t) is the displacement of the Fermi circle in direction theta, at the position where the density wave has its
maximum (e^{iqx} = 1).  The CVODE run (book/rust/ch08_kinetic) integrates N = 64 nodes; the profile on a fine angular grid is
reconstructed from the SAME solution through the exact Duhamel formula
        nu(theta, t) = e^{-i c t} [ nu(theta, 0) - i F c  int_0^t e^{i c t'} m(t') dt' ],   c = cos(theta),  m = <nu>,
with m(t') the CVODE output (Simpson).  The reconstruction is checked against the CVODE nodal values.
Top: heat maps of Re nu(theta, t).  Below: the circle r = 1 + eps Re nu(theta, t) at t = 0, 6, 12, 24 (deformation magnified
by 1/eps; red = bulge outwards, blue = inwards).  Numbers -> figures/ch08_numbers.json["fermisurface"]."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch08_style import *
from matplotlib.colors import LinearSegmentedColormap
from scipy.integrate import cumulative_simpson
import ch08_theory as T

DATA = Path("/mnt/data/xdev-cache/book_ch08/kinetic")
NUMS = FIG / "ch08_numbers.json"
EPS = 0.10
TIMES = (0, 6, 12, 24)


def ld(tag): return np.loadtxt(DATA / f"{tag}.csv", delimiter=",", skiprows=1)


def reconstruct(tag, F, theta, tmax=24.0):
    d = ld(tag); sel = d[:, 0] <= tmax + 1e-9
    t, m = d[sel, 0], d[sel, 1] + 1j * d[sel, 2]
    c = np.cos(theta)
    integrand = np.exp(1j * c[:, None] * t[None, :]) * m[None, :]
    I = cumulative_simpson(integrand, x=t, axis=1, initial=0.0)
    return t, np.exp(-1j * c[:, None] * t[None, :]) * (1.0 - 1j * F * c[:, None] * I)


def main():
    nums = {}
    div = LinearSegmentedColormap.from_list("qfdiv", [BLUE, "#9EC1DD", PAPER, "#E8B07A", RED], N=256)
    th = np.linspace(0, np.pi, 481)
    cases = ((0.0, "uni_p0", BLUE), (4.0, "uni_p4", ORANGE))
    rec = {}
    for F, tag, col in cases:
        t, nu = reconstruct(tag, F, th); rec[F] = (t, nu)
        # check against the CVODE nodal values at the snapshot times
        snap = np.loadtxt(DATA / f"{tag}_snap.csv", delimiter=",", skiprows=1)
        worst = 0.0
        for Ts in sorted(set(snap[:, 0])):
            sub = snap[np.isclose(snap[:, 0], Ts)]
            _, nu_nodes = reconstruct(tag, F, sub[:, 2])
            j = int(round(Ts / 0.1))
            worst = max(worst, float(np.max(np.abs(nu_nodes[:, j] - (sub[:, 3] + 1j * sub[:, 4])))))
        nums[f"reconstruction_vs_nodes_F{F:g}"] = dict(max_abs_diff=worst, N_nodes=64, times=sorted(set(map(float, snap[:, 0]))))
        nums[f"max_abs_nu_F{F:g}"] = {str(Ts): float(np.max(np.abs(nu[:, int(round(Ts / 0.1))]))) for Ts in TIMES}
        nums[f"min_abs_nu_F{F:g}"] = {str(Ts): float(np.min(np.abs(nu[:, int(round(Ts / 0.1))]))) for Ts in TIMES}

    fig = plt.figure(figsize=(TEXTW, 4.95))
    gs = fig.add_gridspec(4, 4, height_ratios=[0.95, 0.24, 1.0, 1.0], hspace=0.06, wspace=0.22)
    for k, (F, tag, col) in enumerate(cases):
        ax = fig.add_subplot(gs[0, 2 * k:2 * k + 2]); panel(ax, "ab"[k])
        t, nu = rec[F]
        im = ax.imshow(nu.real, origin="lower", extent=[0, t[-1], 0, 1], aspect="auto", cmap=div, vmin=-1.6, vmax=1.6, interpolation="bilinear")
        for Ts in TIMES[1:]: ax.axvline(Ts, color="black", lw=0.5, ls=":")
        ax.set_yticks([0, 0.5, 1]); ax.set_yticklabels(["0", r"$\frac{1}{2}$", "1"]); ax.set_xticks([0, 6, 12, 18, 24])
        ax.set_xlabel(r"time $t$");
        if k == 0: ax.set_ylabel(r"angle $\theta/\pi$")
        else: ax.set_yticklabels([])
        ax.text(0.015, 0.93, r"$F=0$: free streaming" if F == 0 else r"$F=4$: zero sound + filaments", transform=ax.transAxes, fontsize=7.4, va="top",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))
    cax = fig.add_axes([0.915, 0.735, 0.012, 0.19]); cb = fig.colorbar(im, cax=cax); cb.set_ticks([-1.5, 0, 1.5]); cb.ax.tick_params(labelsize=6.5)
    cb.set_label(r"Re $\nu$", fontsize=7.5, labelpad=1)
    thf = np.linspace(0, 2 * np.pi, 961)
    for r, (F, tag, col) in enumerate(cases):
        t, nu = rec[F]
        for c_, Ts in enumerate(TIMES):
            ax = fig.add_subplot(gs[2 + r, c_], projection="polar")
            j = int(round(Ts / 0.1))
            nuf = np.interp(np.abs(((thf + np.pi) % (2 * np.pi)) - np.pi), th, nu[:, j].real)       # nu depends on |theta| only
            rad = 1 + EPS * nuf
            ax.plot(thf, np.ones_like(thf), color=GREY, lw=0.5)
            ax.fill_between(thf, 1, rad, where=rad >= 1, color=RED, alpha=0.75, lw=0)
            ax.fill_between(thf, 1, rad, where=rad < 1, color=BLUE, alpha=0.75, lw=0)
            ax.plot(thf, rad, color="black", lw=0.5)
            ax.set_ylim(0, 1.0 + EPS * 3.6); ax.set_yticks([]); ax.set_xticks([]); ax.spines["polar"].set_visible(False)
            ax.set_title(rf"$t={Ts}$", fontsize=7.6, pad=-1)
            if c_ == 0:
                ax.text(-0.02, 0.5, rf"$F={F:g}$", transform=ax.transAxes, rotation=90, ha="right", va="center", fontsize=8.2, color=col)
    save8(fig, "ch08_fermisurface")
    nums["epsilon"] = EPS
    allnums = json.loads(NUMS.read_text()) if NUMS.exists() else {}
    allnums["fermisurface"] = nums
    NUMS.write_text(json.dumps(allnums, indent=1))
    print(json.dumps(nums, indent=1))


main()
