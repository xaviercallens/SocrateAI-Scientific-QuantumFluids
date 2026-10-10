"""Chapter 8, figure (ch08_window): the (q, omega) plane of a Fermi liquid, in the units of the free gas
(x = q/kF, y = omega/EF with EF = kF^2/2m, so that vF q = 2 x EF and q^2/2m = x^2 EF).

  * grey: the free-fermion particle-hole band  [ lower(x), upper(x) ] with  upper = 2x + x^2,
    lower = 0 for x <= 2 and x^2 - 2x for x > 2  (Lean: ph_energy_window, ph_gap, ph_edge_attained);
  * lines (panel a): the Landau zero-sound branch  y = 2 s0 x,  s0 = (1+F)/sqrt(1+2F)  (Lean: zero_sound_2d_iff), solid
    where it lies ABOVE the band edge (undamped), dashed once it has entered the band; entry point x_c = 2 (s0 - 1).
    The branch is derived for q << kF and is drawn only up to x = 1.5 for orientation;
  * gold (panel b): the momentum transfers q > 2 kF at which Godfrin et al. (Nature 483, 576, 2012) report the roton-like
    mode.  NO curve is drawn there: the film's F, m* and kF are not known to this book.
Numbers go to figures/ch08_numbers.json["window"]."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch08_style import *
from matplotlib.patches import Rectangle
import ch08_theory as T

NUMS = FIG / "ch08_numbers.json"


def upper(x): return 2 * x + x ** 2
def lower(x): return np.where(x > 2, x ** 2 - 2 * x, 0.0)


def main():
    Fs = (0.5, 1.0, 4.0)
    cols = {0.5: TEAL, 1.0: BLUE, 4.0: ORANGE}
    fig, (a, b) = plt.subplots(1, 2, figsize=(TEXTW, 2.95), gridspec_kw=dict(width_ratios=[1.0, 1.28], wspace=0.40))
    panel(a, "a"); panel(b, "b")
    nums = {}
    # ---------------------------------------------------------------- (a) the Landau regime
    XA, YA = 1.5, 5.4
    x = np.linspace(0, XA, 400)
    a.fill_between(x, 0, upper(x), color="#D9D5C8", lw=0, zorder=1)
    a.plot(x, upper(x), color=GREY, lw=0.9, zorder=2)
    a.text(1.12, 0.55, "free particle–\nhole band", fontsize=7.0, color=GREY, ha="center", va="center")
    for F in Fs:
        s0 = float(T.s0(F)); xc = 2 * (s0 - 1)
        xx = np.linspace(0, XA, 200); und = xx <= xc
        a.plot(xx[und], 2 * s0 * xx[und], color=cols[F], lw=1.7, zorder=4)
        a.plot(xx[~und], 2 * s0 * xx[~und], color=cols[F], lw=1.3, ls=(0, (3, 2)), zorder=4)
        a.plot([xc], [2 * s0 * xc], "o", color=cols[F], ms=3.8, zorder=5)
        nums[str(F)] = dict(s0=s0, x_c=xc, omega_c_over_EF=float(2 * s0 * xc), enters_band_before_2kF=bool(xc < 2.0))
    a.text(0.50, 2.55, r"$F=4$", color=ORANGE, fontsize=7.4, ha="right", va="center")
    a.text(1.24, 3.42, r"$F=1$", color=BLUE, fontsize=7.4, ha="center", va="center")
    a.text(1.36, 2.30, r"$F=\frac{1}{2}$", color=TEAL, fontsize=7.4, ha="center", va="center")
    a.text(0.03, 5.0, r"solid: undamped, $\omega>$ band edge" "\n" r"dashed: inside the band" "\n" r"dot: entry $q_c=2k_F(s_0-1)$", fontsize=6.6, color=GREY, va="top")
    a.set_xlim(0, XA); a.set_ylim(0, YA)
    a.set_xlabel(r"$q/k_F$"); a.set_ylabel(r"$\omega/E_F$")
    # ---------------------------------------------------------------- (b) the whole plane up to 3.3 kF
    x = np.linspace(0, 3.3, 800)
    b.axvspan(2.0, 3.3, color=GOLD, alpha=0.13, lw=0)
    b.fill_between(x, lower(x), upper(x), color="#D9D5C8", lw=0, zorder=1)
    b.plot(x, upper(x), color=GREY, lw=0.9, zorder=2); b.plot(x, lower(x), color=GREY, lw=0.9, zorder=2)
    b.fill_between(x[x >= 2], 0, lower(x[x >= 2]), facecolor="none", hatch="////", edgecolor=GOLD, lw=0, zorder=1)
    b.axvline(2.0, color=GOLD, lw=1.0, ls="--", zorder=2)
    b.text(2.03, 11.7, r"$q=2k_F$", color="#8A6B1E", fontsize=7.6, ha="left", va="top")
    b.text(0.95, 8.6, "free band, $q\\leq 2k_F$:\n" r"$0\leq\omega\leq v_Fq+q^2/2m$", fontsize=7.2, color=GREY, ha="center", va="center")
    b.text(2.66, 1.05, "gap of the free band\n" r"$\omega\geq q(q-2k_F)/2m$", fontsize=6.9, color="#6F5415", ha="center", va="center",
           bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9))
    b.text(2.66, 6.4, "$q>2k_F$: collective mode\nreported by Godfrin\net al. ($2012$)\n(no curve drawn)", fontsize=7.0, color="#6F5415", ha="center", va="center",
           bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
    b.add_patch(Rectangle((0, 0), XA, YA, fill=False, ec=BLUE, lw=0.8, ls=":", zorder=3)); b.text(0.78, 0.75 + YA, "(a)", color=BLUE, fontsize=7.6, ha="center", va="bottom")
    b.set_xlim(0, 3.3); b.set_ylim(0, 12)
    b.set_xlabel(r"$q/k_F$"); b.set_ylabel(r"$\omega/E_F$")
    save8(fig, "ch08_window")
    # numbers: F at which the Landau line stays above the band edge up to q = 2 kF  (s0 = 2):  F^2 - 6F - 3 = 0
    Fstar = 3 + np.sqrt(12)
    nums["F_star_s0_equals_2"] = dict(F=float(Fstar), s0=float(T.s0(Fstar)), closed_form="3+2*sqrt(3)")
    nums["edges"] = dict(upper="2x+x^2", lower_x_le_2="0", lower_x_gt_2="x^2-2x")
    allnums = json.loads(NUMS.read_text()) if NUMS.exists() else {}
    allnums["window"] = nums
    NUMS.write_text(json.dumps(allnums, indent=1))
    print(json.dumps(nums, indent=1))


main()
