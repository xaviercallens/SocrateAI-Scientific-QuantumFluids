"""Chapter 8, figure 1 (ch08_zerosound): the zero-sound root s(F), the weights of the pole and of the continuum in the
first moment, and the model structure factor S(s).

 - CVODE (crate `cvode` of rusty-SUNDIALS, driver book/rust/ch08_kinetic, subcommand `cont`) continues the root along
   ln F (Davidenko equation) in 2D and 3D; compared with the Lean closed form (2D) and a 40-digit mpmath root (3D).
 - Gauss-Legendre quadrature of the continuum in s = sin(phi) checks the f-sum rule  int s S ds = 1/4  and the closed
   forms  pole fraction = 1 - 1/(1+2F)^2  (Lean: pole_fraction).
Writes figures/ch08_zerosound.pdf and merges the numbers into figures/ch08_numbers.json["zerosound"]."""
import sys, json, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch08_style import *
import mpmath as mp
import ch08_theory as T

BIN = "/mnt/data/xdev-cache/cargo-target-book8/release/ch08_kinetic"
DATA = Path("/mnt/data/xdev-cache/book_ch08/kinetic"); DATA.mkdir(parents=True, exist_ok=True)
NUMS = FIG / "ch08_numbers.json"
F0, F1, NPTS, RTOL, ATOL = 0.05, 1000.0, 81, 1e-12, 1e-14


def continuation(dim):
    mp.mp.dps = 50
    w0 = float(mp.log(mp.mpf(T.s0(F0)) - 1)) if dim == 2 else float(mp.log(T.mp_s3(F0, 50) - 1))
    out = DATA / f"cont{dim}_{RTOL:g}.csv"
    r = subprocess.run([BIN, "cont", str(dim), repr(w0), str(F0), str(F1), str(NPTS), str(RTOL), str(ATOL), str(out)], capture_output=True, text=True, check=True)
    d = np.loadtxt(out, delimiter=",", skiprows=1)
    return d, r.stdout.strip()


def main():
    nums = {}
    # ---------------------------------------------------------------- CVODE continuation vs exact roots
    mp.mp.dps = 50
    cont = {}
    for dim in (2, 3):
        d, stats = continuation(dim)
        F, w, s = d[:, 0], d[:, 1], d[:, 2]
        err_rel, resid = [], []
        for Fi, wi, si in zip(F, w, s):
            sx = (1 + mp.mpf(Fi)) / mp.sqrt(1 + 2 * mp.mpf(Fi)) if dim == 2 else T.mp_s3(Fi, 40)
            err_rel.append(float(abs(mp.mpf(si) - sx) / sx))
            sc = 1 + mp.e ** mp.mpf(wi)
            resid.append(float(abs(1 + mp.mpf(Fi) * (1 - sc / mp.sqrt(sc ** 2 - 1)))) if dim == 2 else float(abs(mp.mpf(Fi) * T.mp_g3(sc) - 1)))
        cont[dim] = dict(F=F, s=s, err=np.array(err_rel))
        nums[f"cvode_continuation_{dim}d"] = dict(F_min=F0, F_max=F1, n_points=NPTS, rtol=RTOL, atol=ATOL, driver_stats=stats,
                                                  max_rel_err_s=max(err_rel), max_residual_original_equation=max(resid))
    # ---------------------------------------------------------------- closed forms in the text
    nums["roots_2d"] = {str(F): dict(s0=float(T.s0(F)), s0_sq_minus_1=float(T.s0(F) ** 2 - 1), F2_over_1p2F=float(F ** 2 / (1 + 2 * F)),
                                     first_sound=float(T.s1_first_sound(F)), pole_weight_W=float(T.W_pole(F)),
                                     pole_fraction=float(T.pole_fraction(F)), uniform_IC_pole_amplitude_2R=float(2 * T.R_pole(F)),
                                     uniform_IC_continuum_weight=float(1 / (1 + 2 * F)), q_c_over_kF=float(2 * (T.s0(F) - 1)))
                        for F in (0.1, 0.5, 1.0, 4.0, 12.0, 40.0)}
    nums["roots_3d"] = {str(F): float(T.mp_s3(F, 40)) for F in (0.5, 1.0, 4.0, 12.0)}
    nums["asymptotics"] = dict(
        F_large=[1e3, 1e4, 1e6],
        s0_over_sqrtFover2=[float(T.s0(F) / np.sqrt(F / 2)) for F in (1e3, 1e4, 1e6)],
        s3_over_sqrtFover3=[float(T.mp_s3(F, 40) / mp.sqrt(F / 3)) for F in (1e3, 1e4, 1e6)],
        F_small=[1e-2, 1e-3, 1e-4],
        s0_minus1_over_Fsq_over_2=[float((T.s0(F) - 1) / (F ** 2 / 2)) for F in (1e-2, 1e-3, 1e-4)],
        s3_minus1_over_2exp_m2_m2overF=[float((T.mp_s3(F, 60) - 1) / (2 * mp.e ** (-2 - 2 / mp.mpf(F)))) for F in (0.05, 0.1, 0.2)],
        s0_sq_partial_fractions_max_abs_err=float(max(abs(T.s0(F) ** 2 - (F / 2 + 0.75 + 0.25 / (1 + 2 * F))) for F in np.logspace(-3, 3, 50))))
    # ---------------------------------------------------------------- sum rule
    rows = []
    for F in (-0.9, -0.5, -0.25, 0.1, 0.5, 1.0, 4.0, 15.0):
        c = T.first_moment_cont(F); p = float(T.s0(F) * T.W_pole(F)) if F > 0 else 0.0
        rows.append(dict(F=F, continuum=c, pole=p, total=c + p, deviation_from_quarter=c + p - 0.25,
                         continuum_expected=(0.25 / (1 + 2 * F) ** 2 if F > 0 else 0.25), pole_fraction=4 * p,
                         pole_fraction_closed=(float(T.pole_fraction(F)) if F > 0 else 0.0)))
    nums["sum_rule_2d"] = dict(expected=0.25, rows=rows, max_abs_deviation=max(abs(r["deviation_from_quarter"]) for r in rows),
                               max_abs_cont_vs_closed=max(abs(r["continuum"] - r["continuum_expected"]) for r in rows),
                               S_cont_closed_form_vs_definition_max_rel=float(max(
                                   np.max(np.abs(T.S_cont(np.linspace(0.01, 0.99, 99), F) - T.S_cont_from_Omega(np.linspace(0.01, 0.99, 99), F)) / T.S_cont(np.linspace(0.01, 0.99, 99), F))
                                   for F in (-0.9, -0.5, 0.3, 1.0, 4.0, 15.0))))

    # ================================================================ FIGURE
    fig = plt.figure(figsize=(TEXTW, 4.95))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.95], hspace=0.50, wspace=0.34)
    # ---- (a) the root
    a = fig.add_subplot(gs[0, 0]); panel(a, "a")
    Ff = np.logspace(np.log10(F0), 3, 300)
    a.axhspan(0.55, 1.0, color="#EEE9DD", zorder=0)
    a.text(0.065, 0.72, r"particle–hole continuum, $s<1$", fontsize=7, color=GREY, va="center")
    a.plot(Ff, T.s0(Ff), color=BLUE, lw=1.6, label=r"$\mathrm{2D}$: $(1+F)/\sqrt{1+2F}$ (Lean)", zorder=3)
    F3 = Ff[::6]; s3 = np.array([float(T.mp_s3(F, 30)) for F in F3])
    a.plot(F3, s3, color=ORANGE, lw=1.6, label=r"$\mathrm{3D}$: root of $g_3(s)=1/F$", zorder=3)
    for dim, col in ((2, BLUE), (3, ORANGE)):
        a.plot(cont[dim]["F"][::3], cont[dim]["s"][::3], "o", mfc="none", mec=col, ms=4.2, mew=0.9, zorder=4, label="CVODE continuation" if dim == 2 else None)
    Fl = Ff[Ff > 30]
    a.plot(Fl, np.sqrt(Fl / 2), ":", color=BLUE, lw=1.0, label=r"asymptotes $\sqrt{F/2}$, $\sqrt{F/3}$")
    a.plot(Fl, np.sqrt(Fl / 3), ":", color=ORANGE, lw=1.0)
    a.axhline(1, color=GREY, lw=0.8)
    a.set_xscale("log"); a.set_yscale("log"); a.set_xlim(0.05, 1000); a.set_ylim(0.55, 60)
    a.set_yticks([1, 2, 5, 10, 20]); a.set_yticklabels(["1", "2", "5", "10", "20"]); a.set_yticks([], minor=True)
    a.set_xticks([0.1, 1, 10, 100, 1000]); a.set_xticklabels([r"$10^{-1}$", r"$10^{0}$", r"$10^{1}$", r"$10^{2}$", r"$10^{3}$"]); a.set_xticks([], minor=True)
    a.set_xlabel("Landau parameter $F$"); a.set_ylabel(r"$s=\omega/(v_Fq)$")
    a.legend(loc="upper left", fontsize=6.4, handlelength=1.6, borderaxespad=0.2, labelspacing=0.3)
    # ---- (b) shares of the first moment
    b = fig.add_subplot(gs[0, 1]); panel(b, "b")
    Fp = np.linspace(1e-4, 4.0, 400)
    b.plot(Fp, T.pole_fraction(Fp), color=BLUE, lw=1.6, label=r"pole: $1-(1+2F)^{-2}$")
    b.plot(Fp, (1 + 2 * Fp) ** -2.0, color=ORANGE, lw=1.6, label=r"continuum: $(1+2F)^{-2}$")
    Fn = np.linspace(-0.95, 0.0, 50)
    b.plot(Fn, np.ones_like(Fn), color=ORANGE, lw=1.6); b.plot(Fn, np.zeros_like(Fn), color=BLUE, lw=1.6)
    Fm = np.array([-0.9, -0.5, -0.25, 0.1, 0.5, 1.0, 2.0, 4.0])
    b.plot(Fm, [4 * T.first_moment_cont(F) for F in Fm], "o", mfc="none", mec=ORANGE, ms=4.5, mew=0.9, zorder=4, label="quadrature")
    b.plot(Fm[Fm > 0], [4 * T.s0(F) * T.W_pole(F) for F in Fm[Fm > 0]], "o", mfc="none", mec=BLUE, ms=4.5, mew=0.9, zorder=4)
    b.axvline(0, color=GREY, lw=0.6, ls="--")
    b.set_xlim(-1, 4); b.set_ylim(-0.04, 1.08)
    b.set_xlabel("$F$"); b.set_ylabel(r"share of the $f$-sum rule")
    b.legend(loc="center right", fontsize=6.6, handlelength=1.6, bbox_to_anchor=(1.03, 0.52))
    b.text(-0.93, 0.5, "no undamped\nroot", fontsize=7, color=GREY, va="center")
    # ---- (c) structure factor with stems
    c = fig.add_subplot(gs[1, :]); panel(c, "c")
    c.axvspan(0, 1, color="#EEE9DD", zorder=0)
    sv = np.linspace(1e-4, 1 - 1e-7, 3000)
    cols = {-0.5: GREY, 0.3: TEAL, 1.0: BLUE, 4.0: ORANGE, 15.0: RED}
    for F, col in cols.items():
        c.plot(sv, T.S_cont(sv, F), color=col, lw=1.3, label=f"$F={F:g}$")
        if F > 0:
            s0, W = float(T.s0(F)), float(T.W_pole(F))
            c.vlines(s0, 0, W, color=col, lw=1.3); c.plot([s0], [W], "o", color=col, ms=3.6)
    c.set_xlim(0, 3.6); c.set_ylim(0, 0.8)
    c.set_xlabel(r"$s=\omega/(v_Fq)$"); c.set_ylabel(r"$S(s)$ (continuum), weight $W$ (stem)")
    c.legend(fontsize=7, ncol=5, loc="upper right", bbox_to_anchor=(1.0, 1.02), handlelength=1.3, columnspacing=1.2)
    c.text(0.5, 0.735, "particle–hole continuum\n(Landau damping)", ha="center", va="center", fontsize=7.5, color=GREY)
    c.text(2.2, 0.40, "stems: undamped zero sound at\n" r"$s_0=(1+F)/\sqrt{1+2F}>1$," "\n" r"height $W=F/(1+2F)^{3/2}$", fontsize=7.5, color=GREY)
    save8(fig, "ch08_zerosound")

    allnums = json.loads(NUMS.read_text()) if NUMS.exists() else {}
    allnums["zerosound"] = nums
    NUMS.write_text(json.dumps(allnums, indent=1))
    print(json.dumps({k: nums[k] for k in ("cvode_continuation_2d", "cvode_continuation_3d")}, indent=1))
    print("sum rule max dev", nums["sum_rule_2d"]["max_abs_deviation"], nums["sum_rule_2d"]["max_abs_cont_vs_closed"])


main()
