"""Chapter 8, figure (ch08_vlasov): the plasma cousin of zero sound, solved by the crate qf-vlasov1d (rusty-SUNDIALS repository).

 Vlasov-Poisson, 1D1V, electrons on a neutralising background (units: plasma frequency 1):
        df/dt + v df/dx - E df/dv = 0,   dE/dx = 1 - rho.
 Two backgrounds f0(v) with the same density: a Maxwellian (unbounded support) and a degenerate Fermi-Dirac profile
        f0 ~ 1/(1 + exp((|v| - v0)/w)),   v0 = 1, w = 0.1     (bounded support: two smeared edges = the 1D Fermi surface).
 Linear theory:  eps(k, omega) = 1 - (1/k^2) int f0'(v)/(v - omega/k) dv = 0  (Landau contour), root omega = omega_r + i gamma.
 The driver book/rust/ch08_vlasov writes the series; here: nonlinear least-squares fits  A e^{gamma t} cos(omega t + phi)  of the
 signed density mode, linear-theory roots (mpmath for the Maxwellian, quadrature + analytic continuation for Fermi-Dirac),
 the free-streaming control against the closed form exp(-k^2 t^2/2) (Lean: PhaseMixing.maxwellian_mode), and the figure.
Numbers -> figures/ch08_numbers.json["vlasov"]."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch08_style import *
import mpmath as mp
from scipy.integrate import quad
from scipy.optimize import least_squares, fsolve
from matplotlib.colors import LinearSegmentedColormap

DATA = Path("/mnt/data/xdev-cache/book_ch08/vlasov")
NUMS = FIG / "ch08_numbers.json"
NX, NV, VMAX, KSNAP = 32, 512, 6.0, 0.5
V0, W = 1.0, 0.1


# ----------------------------------------------------------------------------------------------- linear theory
def root_maxwell(k, guess):
    mp.mp.dps = 30
    def f(w):
        xi = w / (mp.sqrt(2) * k)
        Z = 1j * mp.sqrt(mp.pi) * mp.exp(-xi ** 2) * mp.erfc(-1j * xi)          # plasma dispersion function
        return 1 + (1 + xi * Z) / k ** 2
    return complex(mp.findroot(f, mp.mpc(guess), tol=1e-25))


_Z0 = quad(lambda v: 1 / (1 + np.exp((abs(v) - V0) / W)), -8, 8, points=[-1, 0, 1], limit=400)[0]
_A = 1 / _Z0


def _f0p(v):                                   # d f0/dv for v > 0, analytic in v
    e = np.exp((v - V0) / W)
    return -_A / W * e / (1 + e) ** 2


def _f0p_full(v): return _f0p(abs(v)) * np.sign(v)


def _I(u):
    def re(v): return (_f0p_full(v) / (v - u)).real
    def im(v): return (_f0p_full(v) / (v - u)).imag
    pts = sorted(set(p for p in [-8, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, u.real - 0.2, u.real, u.real + 0.2, 8] if -8 <= p <= 8))
    R = sum(quad(re, a, b, limit=400, epsabs=1e-14, epsrel=1e-12)[0] for a, b in zip(pts[:-1], pts[1:]))
    J = sum(quad(im, a, b, limit=400, epsabs=1e-14, epsrel=1e-12)[0] for a, b in zip(pts[:-1], pts[1:]))
    val = R + 1j * J
    if u.imag < 0: val += 2j * np.pi * _f0p(u)             # analytic continuation to Im u < 0 (Landau contour)
    return val


def root_fermi(k, guess):
    def F(x):
        e = 1 - _I(complex(x[0], x[1]) / k) / k ** 2
        return [e.real, e.imag]
    sol = fsolve(F, [guess.real, guess.imag], xtol=1e-13)
    return complex(sol[0], sol[1])


def _eps_real(omega, k):
    """Real part of eps(k, omega) for real omega (principal-value integral)."""
    u = omega / k
    pv = quad(_f0p_full, -8, 8, weight="cauchy", wvar=u, limit=400, epsabs=1e-14, epsrel=1e-12)[0]
    return 1 - pv / k ** 2


def gamma_weak_fermi(k, omega_guess):
    """Weak-damping rate gamma = -Im eps / (d Re eps / d omega) at the real root, Im eps = -(pi/k^2) f0'(u).
    Valid while |gamma| << omega (checked against the exact continued root at k = 0.3, 0.5, 0.8)."""
    from scipy.optimize import brentq
    w = brentq(lambda x: _eps_real(x, k), omega_guess - 0.01, omega_guess + 0.20, xtol=1e-14)
    h = 1e-4
    dre = (_eps_real(w + h, k) - _eps_real(w - h, k)) / (2 * h)
    return w, float((np.pi / k ** 2) * _f0p(w / k) / dre)


# ----------------------------------------------------------------------------------------------- fits
def fit(bg, k, nv, ta=5.0, tb=40.0):
    d = np.loadtxt(DATA / f"scan_{bg}_k{k}_nv{nv}.csv", delimiter=",", skiprows=1)
    t, y = d[:, 0], d[:, 5]
    if bg == "maxwell":
        tb = min(tb, float(t[np.abs(y) > 3e-5 * np.abs(y).max()].max()))
    m = (t >= ta) & (t <= tb); tt, yy = t[m], y[m]
    best = None
    for w0 in np.linspace(0.8, 2.2, 15):
        for g0 in (-0.3, -0.01):
            res = lambda p: p[0] * np.exp(p[1] * (tt - ta)) * np.cos(p[2] * tt + p[3]) - yy
            try: sol = least_squares(res, [np.abs(yy).max(), g0, w0, 0.0], xtol=1e-14, ftol=1e-14, gtol=1e-14, max_nfev=2000)
            except Exception: continue
            if best is None or sol.cost < best.cost: best = sol
    r = best.fun
    return dict(gamma=float(best.x[1]), omega=float(best.x[2]), window=[ta, float(tb)], rms_over_max=float(np.sqrt(np.mean(r ** 2)) / np.abs(yy).max()))


def main():
    nums = dict(grid=dict(nx=NX, nv=NV, vmax=VMAX, dt=0.1, a_scan=0.01, a_snapshots=0.05, t_end=40.0, k_snapshots=KSNAP),
                background=dict(fermi_v0=V0, fermi_w=W, normalisation_A=float(_A)))
    # ------------------------------------------------------------ roots and fits, Maxwellian
    ks_m = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    th_m, fit_m, conv = {}, {}, {}
    for k in ks_m:
        r = root_maxwell(k, np.sqrt(1 + 3 * k * k) - 0.05j * (k / 0.3))
        th_m[k] = r
        fit_m[k] = {nv: fit("maxwell", k, nv) for nv in (128, 256, 512)}
        conv[k] = float(max(abs(fit_m[k][nv]["gamma"] - fit_m[k][512]["gamma"]) for nv in (128, 256)))
    nums["maxwell"] = {str(k): dict(theory_omega=th_m[k].real, theory_gamma=th_m[k].imag, fit_nv512=fit_m[k][512],
                                    rel_diff_gamma=float(abs(fit_m[k][512]["gamma"] / th_m[k].imag - 1)), rel_diff_omega=float(abs(fit_m[k][512]["omega"] / th_m[k].real - 1)),
                                    max_abs_gamma_change_nv128_256_vs_512=conv[k]) for k in ks_m}
    nums["maxwell_certified_root_k0.5"] = dict(programme_value=[1.415661888604536, -0.153359466909605], this_calculation=[th_m[0.5].real, th_m[0.5].imag])
    # ------------------------------------------------------------ roots and fits, Fermi-Dirac
    ks_f = [0.3, 0.5, 0.8]
    th_f, fit_f = {}, {}
    for k in ks_f:
        th_f[k] = root_fermi(k, np.sqrt(1 + (k * V0) ** 2) - 1e-4j)
        fit_f[k] = {nv: fit("fermi", k, nv) for nv in (512, 1024)}
    nums["fermi_weak_damping_formula_check"] = {str(k): dict(weak=gamma_weak_fermi(k, np.sqrt(1 + (k * V0) ** 2))[1], exact_continued_root=th_f[k].imag) for k in ks_f}
    nums["fermi"] = {str(k): dict(theory_omega=th_f[k].real, theory_gamma=th_f[k].imag, waterbag_omega=float(np.sqrt(1 + (k * V0) ** 2)),
                                  fit_nv512=fit_f[k][512], fit_nv1024=fit_f[k][1024], rel_diff_omega=float(abs(fit_f[k][512]["omega"] / th_f[k].real - 1)))
                     for k in ks_f}
    # theory curves
    kk = np.linspace(0.25, 0.85, 31)
    gm, gf = [], []
    guess = np.sqrt(1 + 3 * 0.25 ** 2) - 0.02j
    for k in kk:
        r = root_maxwell(k, guess); guess = r; gm.append(r.imag)
    wprev = np.sqrt(1 + 0.25 ** 2)
    for k in kk:
        w, g = gamma_weak_fermi(k, wprev); wprev = w; gf.append(g)
    gm, gf = np.array(gm), np.array(gf)
    # ------------------------------------------------------------ free streaming (Lean: maxwellian_mode)
    fs = np.loadtxt(DATA / "series_free_k0.5_nv512.csv", delimiter=",", skiprows=1)
    tfs, rfs = fs[:, 0], fs[:, 1] / fs[0, 1]
    ref = np.exp(-(KSNAP * tfs) ** 2 / 2)
    nums["free_streaming"] = dict(k=KSNAP, nv=NV, vmax=VMAX, max_abs_dev=float(np.max(np.abs(rfs - ref))),
                                  dev_at_t={str(tt): float(abs(rfs[int(round(tt / 0.1))] - ref[int(round(tt / 0.1))])) for tt in (2, 4, 6, 8, 10)},
                                  floor_at_t40=float(rfs[-1]), recurrence_time=2 * np.pi / (KSNAP * (2 * VMAX / NV)))
    # ------------------------------------------------------------ conservation
    cons = {}
    for bg in ("maxwell", "fermi"):
        s = np.loadtxt(DATA / f"series_{bg}_k0.5_nv512.csv", delimiter=",", skiprows=1)
        cons[bg] = dict(mass_rel_drift_at_t40=float(s[-1, 4] / s[0, 4] - 1), energy_max_rel_dev=float(np.max(np.abs(s[:, 3] / s[0, 3] - 1))))
    nums["conservation_k0.5_nv512"] = cons
    # rust-side peak-fit table, for the record
    nums["rust_peak_fit_tables"] = dict(maxwell=(DATA / "rates_maxwell.csv").read_text(), fermi=(DATA / "rates_fermi.csv").read_text())

    # ================================================================ FIGURE
    div = LinearSegmentedColormap.from_list("qfdiv", [BLUE, "#9EC1DD", PAPER, "#E8B07A", RED], N=256)
    x = np.arange(NX) * (2 * np.pi / KSNAP / NX); v = -VMAX + (np.arange(NV) + 0.5) * (2 * VMAX / NV)
    def load(bg, t): return np.fromfile(DATA / f"snap_{bg}_k0.5_nv512_t{int(t)}.f64").reshape(NX, NV)
    fig = plt.figure(figsize=(TEXTW, 5.35))
    gs = fig.add_gridspec(5, 4, height_ratios=[0.9, 0.9, 1.15, 0.30, 1.35], hspace=0.55, wspace=0.34)
    gsb = fig.add_gridspec(5, 2, height_ratios=[0.9, 0.9, 1.15, 0.30, 1.35], hspace=0.55, wspace=0.50)
    snapT = (5, 10, 20, 30)
    for r, (bg, lab, col) in enumerate((("maxwell", "Maxwellian", BLUE), ("fermi", "degenerate", ORANGE))):
        f0 = load(bg, 0).mean(axis=0)
        dfs = [load(bg, t) - f0[None, :] for t in snapT]
        mx = max(np.abs(d).max() for d in dfs)
        for c, (t, df) in enumerate(zip(snapT, dfs)):
            ax = fig.add_subplot(gs[r, c])
            ax.imshow(df.T, origin="lower", extent=[0, x[-1] + x[1], -VMAX, VMAX], aspect="auto", cmap=div, vmin=-mx, vmax=mx, interpolation="nearest")
            ax.set_ylim(-3.2, 3.2); ax.set_xticks([0, 6.28, 12.57]); ax.set_xticklabels(["0", r"$\pi/k$", r"$2\pi/k$"], fontsize=6.5)
            ax.set_yticks([-2, 0, 2]); ax.tick_params(axis="y", labelsize=6.5)
            if c > 0: ax.set_yticklabels([])
            else: ax.set_ylabel(r"$v$", fontsize=8)
            if r == 0: ax.set_title(rf"$t={t}$", fontsize=7.6, pad=2)
            if c == 0:
                ax.text(0.03, 0.94, lab, transform=ax.transAxes, fontsize=7.2, color=col, va="top", fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8))
            if r == 0 and c == 0: panel(ax, "a")
    # ---- (b) time series
    b = fig.add_subplot(gs[2, :]); panel(b, "b")
    sm = np.loadtxt(DATA / "series_maxwell_k0.5_nv512.csv", delimiter=",", skiprows=1); sf = np.loadtxt(DATA / "series_fermi_k0.5_nv512.csv", delimiter=",", skiprows=1)
    b.plot(sm[:, 0], sm[:, 5] / sm[0, 5], color=BLUE, lw=1.2, label=r"Maxwellian: solver")
    b.plot(sf[:, 0], sf[:, 5] / sf[0, 5], color=ORANGE, lw=1.2, label=r"degenerate: solver")
    tt = np.linspace(0, 40, 400); g5 = th_m[0.5].imag
    b.plot(tt, np.exp(g5 * tt), color=BLUE, lw=0.8, ls="--"); b.plot(tt, -np.exp(g5 * tt), color=BLUE, lw=0.8, ls="--")
    b.text(0.8, 1.34, r"dashed: $\pm e^{\gamma t}$, $\gamma=-0.1534$ (Landau root)", fontsize=6.9, color=BLUE, va="center")
    b.set_xlim(0, 40); b.set_ylim(-1.15, 1.55); b.set_xlabel(r"time $t$"); b.set_ylabel(r"$\rho_1(t)/\rho_1(0)$, $k=\frac{1}{2}$", fontsize=8)
    b.legend(fontsize=6.8, ncol=2, loc="upper right", handlelength=1.4, borderaxespad=0.2)
    # ---- (c) rates
    c = fig.add_subplot(gsb[4, 0]); panel(c, "c")
    c.plot(kk, -gm, color=BLUE, lw=1.4, label="Maxwellian"); c.plot(kk, -gf, color=ORANGE, lw=1.4, label="degenerate")
    c.plot(ks_m, [-fit_m[k][512]["gamma"] for k in ks_m], "o", mfc="none", mec=BLUE, ms=4.5, mew=0.9, label="solver (fit)")
    c.plot(ks_f, [abs(fit_f[k][512]["gamma"]) for k in ks_f], "s", mfc="none", mec=ORANGE, ms=4.5, mew=0.9)
    c.axhline(1e-4, color=GREY, lw=0.7, ls=":"); c.text(0.255, 1.4e-4, "fit resolution", fontsize=6.3, color=GREY)
    c.set_yscale("log"); c.set_xlim(0.25, 0.85); c.set_ylim(1e-9, 1.2)
    c.set_yticks([1e-8, 1e-6, 1e-4, 1e-2, 1]); c.set_yticklabels([r"$10^{-8}$", r"$10^{-6}$", r"$10^{-4}$", r"$10^{-2}$", r"$1$"]); c.set_yticks([], minor=True)
    c.set_xlabel(r"wave number $k$"); c.set_ylabel(r"damping rate $|\gamma|$", fontsize=8)
    c.legend(fontsize=6.2, loc="lower right", handlelength=1.4, labelspacing=0.22, borderaxespad=0.2)
    # ---- (d) free streaming
    d = fig.add_subplot(gsb[4, 1]); panel(d, "d")
    sel = np.arange(len(tfs)) % 4 == 0
    d.plot(tfs, np.exp(-(KSNAP * tfs) ** 2 / 2), color=TEAL, lw=1.3, label=r"$e^{-k^2t^2/2}$ (Lean)")
    d.plot(tfs[sel], rfs[sel], "o", mfc="none", mec="black", ms=2.8, mew=0.5, label="solver, field off")
    d.plot(tfs, np.abs(rfs - np.exp(-(KSNAP * tfs) ** 2 / 2)) + 1e-14, color=GREY, lw=0.8, ls=":", label="difference")
    d.set_yscale("log"); d.set_xlim(0, 20); d.set_ylim(1e-11, 2)
    d.set_yticks([1e-9, 1e-6, 1e-3, 1]); d.set_yticklabels([r"$10^{-9}$", r"$10^{-6}$", r"$10^{-3}$", r"$1$"]); d.set_yticks([], minor=True)
    d.set_xlabel(r"time $t$"); d.text(0.03, 0.33, r"$\rho_1(t)/\rho_1(0)$, field off", transform=d.transAxes, fontsize=6.8, color=GREY)
    d.legend(fontsize=6.4, loc="upper right", handlelength=1.5, labelspacing=0.25, borderaxespad=0.2)
    save8(fig, "ch08_vlasov")

    allnums = json.loads(NUMS.read_text()) if NUMS.exists() else {}
    allnums["vlasov"] = nums
    NUMS.write_text(json.dumps(allnums, indent=1))
    print(json.dumps({k: nums[k] for k in ("maxwell", "fermi", "free_streaming", "conservation_k0.5_nv512")}, indent=1)[:6000])
    print("Fermi theory gamma curve (k, gamma):", list(zip(np.round(kk[::5], 3), gf[::5])))


main()
