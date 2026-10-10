"""Figure ch05_curve: the dispersion relation of superfluid 4He at saturated vapour pressure, the Landau line, the phase
velocity, and the phonon window -- against the Bogoliubov curve one would get from the bare atomic mass and the measured
sound speed.  Data: Godfrin et al. (2021), arXiv:2012.09067, ancillary file DispersionP0allRange.txt (authors' processed
curve, 0.002 A^-1 grid; the printed uncertainties are the 34 rows that carry one)."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
plt.rcParams["axes.unicode_minus"] = False
import ch05_helium as H

k, e, de = H.load_table()
F = H.features()
HBARC, KSTAR = H.HBARC, H.KSTAR
kp = k[1:]; vph = e[1:] / kp * H.MS_PER_MEVA                      # phase velocity in m/s

fig = plt.figure(figsize=(TEXTW, 5.35))
a = fig.add_axes([0.085, 0.585, 0.815, 0.385])
b = fig.add_axes([0.085, 0.075, 0.385, 0.385])
c = fig.add_axes([0.595, 0.075, 0.385, 0.385])

# ---------------- (a) the curve ------------------------------------------------------------------------------
a.axvspan(0, 0.15, color=GOLD, alpha=0.30, lw=0)                    # ultrasound-based
a.axvspan(0.15, 0.5, color=GOLD, alpha=0.11, lw=0)                  # the window magnified in (c)
kk = np.linspace(0, 1.05, 100)
a.plot(kk, HBARC * kk, color=GREY, lw=1.0, ls=(0, (4, 2)))
a.text(0.84, 1.60, r"sound line $\hbar c k$", color=GREY, fontsize=8, ha="right", va="center")
kl = np.linspace(0, 2.75, 50)
a.plot(kl, F["landau_meV_A"] * kl, color=RED, lw=1.3)
a.plot([F["landau_k_A_inv"]], [F["landau_meV_A"] * F["landau_k_A_inv"]], "o", color=RED, ms=4.5, zorder=5)
a.text(2.52, 0.50, "Landau line\n" + r"slope $\hbar v_{\rm L}$", color=RED, fontsize=8, ha="left", va="center")
a.plot(k, e, color=BLUE, lw=1.9, zorder=4)
a.plot([F["maxon_grid_k"]], [F["maxon_grid_e_meV"]], "o", color=BLUE, ms=4.5, zorder=6, mfc="white", mew=1.3)
a.plot([F["roton_grid_k"]], [F["roton_grid_e_meV"]], "o", color=BLUE, ms=4.5, zorder=6, mfc="white", mew=1.3)
a.annotate(r"maxon" "\n" + f"$\\Delta_{{\\rm M}}={F['maxon_grid_e_meV']:.2f}$ meV, $k_{{\\rm M}}={F['maxon_grid_k']:.2f}\\ \\mathrm{{\\AA}}^{{-1}}$", xy=(F["maxon_grid_k"], F["maxon_grid_e_meV"]),
           xytext=(1.80, 1.66), fontsize=8, color=BLUE, ha="center", va="bottom", arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
a.annotate(r"roton" "\n" + f"$\\Delta_{{\\rm R}}={F['roton_grid_e_meV']:.3f}$ meV $\\approx {F['roton_grid_gap_K']:.2f}$ K, $k_{{\\rm R}}={F['roton_grid_k']:.2f}\\ \\mathrm{{\\AA}}^{{-1}}$", xy=(F["roton_grid_k"], F["roton_grid_e_meV"]),
           xytext=(1.85, 0.20), fontsize=8, color=BLUE, ha="center", va="center", arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
a.text(0.075, 0.60, "ultrasound", rotation=90, fontsize=7, color="#7a5a10", ha="center", va="bottom")
a.text(0.33, 1.78, "phonon\nwindow", fontsize=7.5, color="#7a5a10", ha="center", va="bottom")
a.text(3.18, 1.70, "plateau\nregion", fontsize=8, color=GREY, ha="center", va="bottom")
a.set_xlim(0, 3.6); a.set_ylim(0, 1.95)
a.set_xlabel(r"wave number $k$ ($\mathrm{\AA}^{-1}$)"); a.set_ylabel(r"excitation energy $\varepsilon(k)$ (meV)")
sec = a.secondary_yaxis("right", functions=(lambda x: x * H.K_PER_MEV, lambda x: x / H.K_PER_MEV))
sec.set_ylabel(r"$\varepsilon/k_{\rm B}$ (K)", color=GREY); sec.tick_params(colors=GREY)
sec.spines["right"].set_visible(True); sec.spines["right"].set_color(GREY); sec.spines["right"].set_linewidth(0.7)
panel(a, "a")

# ---------------- (b) the phase velocity: Landau's critical velocity is its minimum --------------------------------
m = kp >= 0.15
b.axhline(H.C_SVP, color=GREY, lw=0.9, ls=(0, (4, 2)))
b.text(3.58, H.C_SVP + 6, r"$c=238.3$ m/s", color=GREY, fontsize=8, ha="right", va="bottom")
kb = np.linspace(0.0, 3.6, 300)
b.plot(kb, H.C_SVP * np.sqrt(1 + (kb / KSTAR) ** 2), color=TEAL, lw=1.3, ls=(0, (5, 2)))
b.text(0.55, 335, "Bogoliubov, bare mass", color=TEAL, fontsize=7.8, ha="left", va="center")
b.plot(kp[m], vph[m], color=BLUE, lw=1.7)
b.plot(kp[~m], vph[~m], color=BLUE, lw=1.0, alpha=0.45)
b.plot([F["landau_k_A_inv"]], [F["landau_velocity_ms"]], "o", color=RED, ms=5, zorder=5)
b.annotate("Landau velocity\n" f"$v_{{\\rm L}}={F['landau_velocity_ms']:.1f}$ m/s", xy=(F["landau_k_A_inv"], F["landau_velocity_ms"]),
           xytext=(2.30, 150), color=RED, fontsize=8, ha="left", va="center", arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
b.set_xlim(0, 3.6); b.set_ylim(0, 400)
b.set_xlabel(r"$k$ ($\mathrm{\AA}^{-1}$)"); b.set_ylabel(r"phase velocity $\varepsilon/\hbar k$ (m/s)")
panel(b, "b")

# ---------------- (c) the phonon window: epsilon/(hbar c k) - 1 -------------------------------------------------------
w = (k >= 0.15) & (k <= 0.85)
y = 100 * (e[w] / (HBARC * k[w]) - 1)
c.axhline(0, color=GREY, lw=0.9, ls=(0, (4, 2)))
kk = np.linspace(0.0, 0.85, 300)
ser = 100 * (H.A2 * kk ** 2 + H.A3 * kk ** 3 + H.A4 * kk ** 4)
c.plot(kk[kk <= 0.5], ser[kk <= 0.5], color=ORANGE, lw=1.4)
c.plot(kk[kk >= 0.5], ser[kk >= 0.5], color=ORANGE, lw=1.0, ls=(0, (2, 2)))
c.plot(kk, 100 * (np.sqrt(1 + (kk / KSTAR) ** 2) - 1), color=TEAL, lw=1.3, ls=(0, (5, 2)))
c.plot(k[w], y, color=BLUE, lw=1.2, alpha=0.9)
me = w & np.isfinite(de)
c.errorbar(k[me], 100 * (e[me] / (HBARC * k[me]) - 1), yerr=100 * de[me] / (HBARC * k[me]), fmt="o", ms=2.8, color=BLUE, elinewidth=0.8, capsize=1.5, zorder=5)
c.text(0.03, 5.75, r"table and series" "\n" r"$\alpha_2=1.55\ \mathrm{\AA}^2$", fontsize=8, color=ORANGE, ha="left", va="center")
c.annotate(r"Bogoliubov, bare mass" "\n" r"$\alpha_2=0.055\ \mathrm{\AA}^2$", xy=(0.80, 100 * (np.sqrt(1 + (0.80 / KSTAR) ** 2) - 1)),
           xytext=(0.84, 5.9), fontsize=7.8, color=TEAL, ha="right", va="center", arrowprops=dict(arrowstyle="-", color=TEAL, lw=0.7))
c.text(0.84, -0.35, r"$v_{\rm ph}=c$", fontsize=7.8, color=GREY, ha="right", va="top")
c.set_xlim(0, 0.85); c.set_ylim(-3.0, 7.2)
c.set_xlabel(r"$k$ ($\mathrm{\AA}^{-1}$)"); c.set_ylabel(r"$100\,[\varepsilon/(\hbar c k)-1]$ (%)")
panel(c, "c")
save(fig, "ch05_curve")

out = {kk_: F[kk_] for kk_ in ("maxon_grid_k", "maxon_grid_e_meV", "roton_grid_k", "roton_grid_e_meV", "maxon_fit_k", "maxon_fit_e_meV", "roton_fit_k", "roton_fit_e_meV", "landau_velocity_ms", "landau_k_A_inv",
                              "phase_velocity_max_over_c", "phase_velocity_max_at_k")}
Path(__file__).with_name("ch05_curve_numbers.json").write_text(json.dumps(out, indent=1))
