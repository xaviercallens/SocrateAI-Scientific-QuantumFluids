"""Chapter 8, figure (ch08_timedomain): the collisionless Landau kinetic equation of a 2D Fermi liquid, integrated in time
by CVODE (BDF; crate `cvode` of rusty-SUNDIALS, driver book/rust/ch08_kinetic), compared with the closed forms of ch08_theory.

 units a = q vF = 1;  nu(theta, t):  d nu/dt = -i cos(theta) [nu + F <nu>],   N = 64 half-circle nodes, rtol 1e-8, atol 1e-10.
 uniform initial condition nu = 1 (a released density wave):  m(t) = <nu>  vs  uniform_ref(t, F)
 kick initial condition nu = cos(theta):                       i m/2   vs  kick_ref(t, F)       (the sine transform of S)
Writes figures/ch08_timedomain.pdf and figures/ch08_numbers.json["timedomain"]."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch08_style import *
from scipy.optimize import least_squares
from scipy.special import j0, j1
import ch08_theory as T

DATA = Path("/mnt/data/xdev-cache/book_ch08/kinetic")
NUMS = FIG / "ch08_numbers.json"
STATS = json.loads((DATA / "stats.json").read_text())


def ftag(F): return ("m" if F < 0 else "p") + f"{abs(F):g}".replace(".", "_")
def ld(tag): return np.loadtxt(DATA / f"{tag}.csv", delimiter=",", skiprows=1)


def local_max(t, y):
    i = np.where((y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:]))[0] + 1
    return t[i], y[i]


def slope(tm, ym, t0, t1):
    m = (tm >= t0) & (tm <= t1)
    p = np.polyfit(np.log(tm[m]), np.log(ym[m]), 1)
    return float(p[0])


def main():
    nums = dict(machine_note="shared 8-core machine; uptime load averages read between 11.9 and 34.9 during the session; wall times are NOT benchmarks")
    # ------------------------------------------------------------------ uniform IC: accuracy, energy, steps
    uni = {}
    for F in (-0.5, 0.0, 0.5, 1.0, 4.0, 12.0):
        d = ld(f"uni_{ftag(F)}"); t, m = d[:, 0], d[:, 1]
        ref = T.uniform_ref(t, F); E = d[:, 3] + F * (d[:, 1] ** 2 + d[:, 2] ** 2)
        st = STATS[f"uni_{ftag(F)}"]
        uni[str(F)] = dict(max_abs_err=float(np.max(np.abs(m - ref))), max_abs_imag_m=float(np.max(np.abs(d[:, 2]))),
                           max_rel_energy_drift=float(np.max(np.abs(E / E[0] - 1))), steps=st["steps"], rhs_evals=st["rhs_evals"], wall_s=st["wall_s"])
    nums["uniform_IC"] = uni
    kick = {}
    for F in (-0.5, 0.5, 1.0, 4.0, 12.0):
        d = ld(f"kick_{ftag(F)}"); t = d[:, 0]
        k = -d[:, 2] / 2.0
        kick[str(F)] = dict(max_abs_err=float(np.max(np.abs(k - T.kick_ref(t, F)))), max_abs_re_m=float(np.max(np.abs(d[:, 1]))),
                            fsum_rule_slope_at_0=float((d[1, 2] - d[0, 2]) / (d[1, 0] - d[0, 0])), steps=STATS[f"kick_{ftag(F)}"]["steps"])
    nums["kick_IC"] = kick
    # ------------------------------------------------------------------ solver verification table (F = 0, exact answer J0)
    tab = {}
    for meth in ("bdf", "adams"):
        for rt in ("1e-06", "1e-08", "1e-10"):
            tag = f"tol_{meth}_{rt}"; d = ld(tag)
            tab[f"{meth}_{rt}"] = dict(max_abs_err_vs_J0=float(np.max(np.abs(d[:, 1] - j0(d[:, 0])))), steps=STATS[tag]["steps"], rhs_evals=STATS[tag]["rhs_evals"], wall_s=STATS[tag]["wall_s"])
    d4, dA, dN = ld("uni_p4"), ld("uni_p4_adams"), ld("uni_p4_N96")
    tab["F4_adams_rtol1e-8"] = dict(max_abs_err_vs_semianalytic=float(np.max(np.abs(dA[:, 1] - T.uniform_ref(dA[:, 0], 4.0)))), steps=STATS["uni_p4_adams"]["steps"])
    tab["F4_N96_vs_N64_max_abs_diff"] = float(np.max(np.abs(dN[:, 1] - d4[:, 1])))
    tab["F4_N96_max_abs_err_vs_semianalytic"] = float(np.max(np.abs(dN[:, 1] - T.uniform_ref(dN[:, 0], 4.0))))
    tab["F4_N96_wall_s"] = STATS["uni_p4_N96"]["wall_s"]; tab["F4_N64_wall_s"] = STATS["uni_p4"]["wall_s"]
    nums["solver_verification"] = tab
    # ------------------------------------------------------------------ fits of the late-time pole
    fits = {}
    for F in (0.5, 1.0, 4.0, 12.0):
        d = ld(f"uni_{ftag(F)}"); t = d[:, 0]
        r = d[:, 1] - T.uniform_cont(t, F)
        res = lambda p: p[0] * np.cos(p[1] * t + p[2]) - r
        sol = least_squares(res, [2 * T.R_pole(F), T.s0(F), 0.0], xtol=1e-14, ftol=1e-14, gtol=1e-14)
        fits[str(F)] = dict(omega_fit=float(sol.x[1]), s0=float(T.s0(F)), rel_dev_omega=float(abs(sol.x[1] / T.s0(F) - 1)),
                            amp_fit=float(sol.x[0]), amp_2R=float(2 * T.R_pole(F)), rel_dev_amp=float(abs(sol.x[0] / (2 * T.R_pole(F)) - 1)),
                            phase_fit=float(sol.x[2]), max_abs_resid=float(np.max(np.abs(res(sol.x)))))
    nums["pole_fits"] = fits
    # ------------------------------------------------------------------ algebraic decay of the continuum remnant
    env = {}
    series_env = {}
    for F in (-0.5, 0.0, 1.0, 4.0):
        d = ld(f"uni_{ftag(F)}"); t = d[:, 0]
        r = d[:, 1] - (2 * T.R_pole(F) * np.cos(T.s0(F) * t) if F > 0 else 0.0)
        tm, ym = local_max(t[t >= 2], np.abs(r[t >= 2]))
        series_env[F] = (tm, ym)
        env[str(F)] = dict(slope_t10_to_60=slope(tm, ym, 10, 60), n_maxima=int(len(tm)))
    nums["envelope_exponents"] = dict(per_F=env, expected={"F=0": -0.5, "F!=0": -1.5})
    # ------------------------------------------------------------------ below the Pomeranchuk bound F = -1: a growing mode
    d = ld("uni_m2"); t = d[:, 0]; mabs = np.sqrt(d[:, 1] ** 2 + d[:, 2] ** 2); Ecs = d[:, 3] + (-2.0) * mabs ** 2
    r_ = 1 - 1 / 2.0; y_pred = r_ / np.sqrt(1 - r_ ** 2)
    grow = {}
    for a_, b_ in ((6, 10), (8, 12), (10, 14)):
        sel = (t >= a_) & (t <= b_); grow[f"{a_}-{b_}"] = float(np.polyfit(t[sel], np.log(mabs[sel]), 1)[0])
    nums["unstable_F_minus2"] = dict(predicted_growth_rate=float(y_pred), fitted_growth_rates=grow, E0=float(Ecs[0]), max_rel_energy_dev=float(np.max(np.abs(Ecs / Ecs[0] - 1))),
                                     steps=STATS["uni_m2"]["steps"], formula="y = r/sqrt(1-r^2), r = 1 - 1/|F|")

    # ================================================================== FIGURE
    fig = plt.figure(figsize=(TEXTW, 5.5))
    outer = fig.add_gridspec(1, 2, width_ratios=[1.45, 1.0], wspace=0.36)
    left = outer[0].subgridspec(4, 1, hspace=0.16)
    right = outer[1].subgridspec(3, 1, hspace=0.62)
    rows = [(-0.5, GREY, r"$F=-\frac{1}{2}$: $m=2J_1(t)/t$", (-0.35, 1.2)), (0.0, BLUE, r"$F=0$: $m=J_0(t)$", (-0.55, 1.25)),
            (1.0, TEAL, r"$F=1$: pole $\frac{2}{3}\cos(s_0t)$", (-0.85, 1.6)), (4.0, ORANGE, r"$F=4$: pole $\frac{8}{9}\cos(\frac{5}{3}t)$", (-1.1, 1.7))]
    tf = np.linspace(0, 40, 1500)
    axs = []
    for i, (F, col, lab, ylim) in enumerate(rows):
        ax = fig.add_subplot(left[i, 0], sharex=axs[0] if axs else None); axs.append(ax)
        d = ld(f"uni_{ftag(F)}"); t, m = d[:, 0], d[:, 1]
        ax.plot(tf, T.uniform_ref(tf, F), color=col, lw=1.2, zorder=2)
        if F > 0: ax.plot(tf, 2 * T.R_pole(F) * np.cos(T.s0(F) * tf), color=col, lw=0.8, ls=(0, (3, 2)), alpha=0.9, zorder=1)
        sel = (t <= 40) & (np.arange(len(t)) % 5 == 0)
        ax.plot(t[sel], m[sel], "o", mfc="none", mec="black", ms=2.7, mew=0.5, zorder=3)
        ax.axhline(0, color=GREY, lw=0.4)
        ax.set_ylim(*ylim); ax.set_yticks([-1, -0.5, 0, 0.5, 1] if F == 4.0 else [-0.5, 0, 0.5, 1] if F != -0.5 else [0, 0.5, 1])
        ax.text(0.985, 0.90, lab, transform=ax.transAxes, ha="right", va="top", fontsize=7.4, color=col,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
        ax.set_ylabel(r"$m(t)$", fontsize=8.5)
        if i < 3: plt.setp(ax.get_xticklabels(), visible=False)
    axs[0].set_xlim(0, 40); axs[-1].set_xlabel(r"time $t$ (units $1/q v_F$)")
    panel(axs[0], "a")
    # ---- (b) envelope of the remnant
    b = fig.add_subplot(right[0, 0]); panel(b, "b")
    for F, col, lab in ((-0.5, GREY, r"$F=-\frac{1}{2}$"), (0.0, BLUE, r"$F=0$"), (1.0, TEAL, r"$F=1$"), (4.0, ORANGE, r"$F=4$")):
        tm, ym = series_env[F]
        b.plot(tm, ym, "o-", ms=2.2, lw=0.6, color=col, label=lab)
    tt = np.array([3.0, 60.0])
    b.plot(tt, 0.8 * tt ** -0.5, color="black", lw=0.7, ls=":"); b.text(3.2, 0.8 * 3.2 ** -0.5 * 1.25, r"$t^{-1/2}$", fontsize=7, va="bottom")
    b.plot(tt, 1.3 * tt ** -1.5, color="black", lw=0.7, ls=":"); b.text(22, 1.3 * 22 ** -1.5 * 1.45, r"$t^{-3/2}$", fontsize=7, va="bottom")
    b.set_xscale("log"); b.set_yscale("log"); b.set_xlim(2, 62); b.set_ylim(2e-4, 1.3)
    b.set_xticks([2, 5, 10, 20, 50]); b.set_xticklabels(["2", "5", "10", "20", "50"]); b.set_xticks([], minor=True)
    b.set_yticks([1e-3, 1e-2, 1e-1, 1]); b.set_yticklabels([r"$10^{-3}$", r"$10^{-2}$", r"$10^{-1}$", r"$1$"]); b.set_yticks([], minor=True)
    b.set_xlabel(r"$t$"); b.set_ylabel(r"peaks of $|m-m_{\rm pole}|$", fontsize=8.0)
    b.legend(fontsize=6.2, loc="lower left", ncol=2, handlelength=1.2, columnspacing=0.8, labelspacing=0.25, borderaxespad=0.2)
    # ---- (c) frequency and amplitude of the pole against the Lean root and the residue
    c = fig.add_subplot(right[1, 0]); panel(c, "c")
    Fq = np.array([0.5, 1.0, 4.0, 12.0])
    c.plot(Fq, [fits[str(F)]["rel_dev_omega"] for F in Fq], "s", color=BLUE, ms=4.2, label=r"$|\omega_{\rm fit}/s_0-1|$")
    c.plot(Fq, [fits[str(F)]["rel_dev_amp"] for F in Fq], "^", color=ORANGE, ms=4.2, label=r"$|A_{\rm fit}/\frac{2F}{1+2F}-1|$")
    c.axhline(1e-8, color=GREY, lw=0.7, ls="--"); c.text(0.52, 1.6e-8, "CVODE rtol", fontsize=6.5, color=GREY)
    c.set_xscale("log"); c.set_yscale("log"); c.set_ylim(1e-12, 1e-5); c.set_xlim(0.4, 16)
    c.set_xticks([0.5, 1, 4, 12]); c.set_xticklabels(["0.5", "1", "4", "12"]); c.set_xticks([], minor=True)
    c.set_yticks([1e-11, 1e-9, 1e-7, 1e-5]); c.set_yticklabels([r"$10^{-11}$", r"$10^{-9}$", r"$10^{-7}$", r"$10^{-5}$"]); c.set_yticks([], minor=True)
    c.set_xlabel("$F$"); c.set_ylabel("relative deviation", fontsize=8.0)
    c.tick_params(axis="y", labelsize=7.2)
    c.legend(fontsize=6.2, loc="upper left", handlelength=1.0, labelspacing=0.25, borderaxespad=0.2)
    # ---- (d) where the amplitude goes (F = 0): |m|^2 against the norm of the Fermi-surface distortion
    dd = fig.add_subplot(right[2, 0]); panel(dd, "d")
    d = ld("uni_p0"); t = d[:, 0]; m2 = d[:, 1] ** 2 + d[:, 2] ** 2; u = d[:, 3]
    dd.fill_between(t, m2, u, color=BLUE, alpha=0.16, lw=0)
    dd.plot(t, u, color=BLUE, lw=1.1, ls=(0, (4, 2)))
    dd.plot(t, m2, color=BLUE, lw=1.2)
    dd.text(34, 0.60, r"$\langle|\nu|^2\rangle=1$ stays:" "\n" "now in angular\nfine structure", fontsize=6.8, color=BLUE, ha="center", va="center")
    dd.text(34, 0.08, r"$|m|^2=J_0(t)^2$", fontsize=6.8, color=BLUE, ha="center", va="center")
    nums["norm_conservation_F0"] = dict(max_abs_norm2_minus_1=float(np.max(np.abs(u - 1))), norm2_at_t60=float(u[-1]), m2_at_t60=float(m2[-1]))
    dd.set_xlim(0, 60); dd.set_ylim(-0.03, 1.12)
    dd.set_xlabel(r"$t$ ($F=0$)"); dd.set_ylabel("squared amplitude", fontsize=8.0)
    save8(fig, "ch08_timedomain")

    allnums = json.loads(NUMS.read_text()) if NUMS.exists() else {}
    allnums["timedomain"] = nums
    NUMS.write_text(json.dumps(allnums, indent=1))
    print(json.dumps({k: nums[k] for k in ("pole_fits", "envelope_exponents")}, indent=1))
    print({F: v["max_abs_err"] for F, v in uni.items()})


main()
