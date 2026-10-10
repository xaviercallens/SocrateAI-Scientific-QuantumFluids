"""Figure ch05_thresholds: where do the three-phonon decay channels of 4He close?  (HeliumKinematics, Godfrin et al. 2021.)
(a) the three different 'excess velocities' of the SVP series  eps = hbar c k (1 + a2 k^2 + a3 k^3 + a4 k^4):
        v_ph - c   = c k^2 (a2 + a3 k + a4 k^2)                    (HeliumKinematics.phase_velocity_excess)
        v_g  - c   = c k^2 (3 a2 + 4 a3 k + 5 a4 k^2)              (HeliumKinematics.group_velocity_excess)
        [eps(k) - 2 eps(k/2)]/(hbar k) = c k^2 (3/4 a2 + 7/8 a3 k + 15/16 a4 k^2)    (HeliumKinematics.symmetric_split_excess)
    with the same three quantities computed directly from the published table (dots).
(b) the energy balance g(k, q) = eps(k) - eps(q) - eps(k - q) of a collinear decay k -> q + (k - q), in micro-eV, versus q/k."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
plt.rcParams["axes.unicode_minus"] = False
import ch05_helium as H

k, e, de = H.load_table()
F = H.features()
c0 = H.C_SVP
A2, A3, A4 = H.A2, H.A3, H.A4
eps_s = lambda x: H.HBARC * H.series(np.asarray(x, dtype=float))          # meV

fig = plt.figure(figsize=(TEXTW, 2.95))
a = fig.add_axes([0.085, 0.16, 0.395, 0.78])
b = fig.add_axes([0.585, 0.16, 0.395, 0.78])

# ---------------- (a) three excess velocities ------------------------------------------------------------------
kk = np.linspace(0.0, 0.75, 400)
vp = c0 * kk ** 2 * (A2 + A3 * kk + A4 * kk ** 2)
vg = c0 * kk ** 2 * (3 * A2 + 4 * A3 * kk + 5 * A4 * kk ** 2)
vs = c0 * kk ** 2 * (0.75 * A2 + 7 / 8 * A3 * kk + 15 / 16 * A4 * kk ** 2)
for y, col, lab in ((vg, BLUE, r"$v_{\rm g}-c$"), (vs, ORANGE, r"$[\varepsilon(k)-2\varepsilon(k/2)]/\hbar k$"), (vp, TEAL, r"$v_{\rm ph}-c$")):
    a.plot(kk[kk <= 0.5], y[kk <= 0.5], color=col, lw=1.5)
    a.plot(kk[kk >= 0.5], y[kk >= 0.5], color=col, lw=1.0, ls=(0, (2, 2)))
# table-derived points
m = (k >= 0.15) & (k <= 0.75)
sel = m[::6]
kt, et = k[m][::6], e[m][::6]
a.plot(kt, (et / kt * H.MS_PER_MEVA) - c0, ".", ms=3.0, color=TEAL, alpha=0.9)
vgt = H.group_velocity(k, e, win=0.07)
mg = (k >= 0.15) & (k <= 0.7)
a.plot(k[mg][::10], vgt[mg][::10] - c0, ".", ms=3.0, color=BLUE, alpha=0.9)
ms_ = (k >= 0.30) & (k <= 0.75)
f = lambda x: np.interp(x, k, e)
a.plot(k[ms_][::6], ((f(k[ms_]) - 2 * f(k[ms_] / 2)) / k[ms_] * H.MS_PER_MEVA)[::6], ".", ms=3.0, color=ORANGE, alpha=0.9)
a.axhline(0, color=GREY, lw=0.8)
for key, col in (("k_group_series", BLUE), ("k_sym_series", ORANGE), ("k_phase_series", TEAL)):
    a.axvline(F[key], color=col, lw=0.7, ls=(0, (1, 2)))
a.text(F["k_group_series"] - 0.012, -33.5, "0.404", color=BLUE, fontsize=7.6, ha="right", va="bottom")
a.text(F["k_sym_series"] + 0.000, -33.5, "0.455", color=ORANGE, fontsize=7.6, ha="center", va="bottom")
a.text(F["k_phase_series"] + 0.012, -33.5, "0.566", color=TEAL, fontsize=7.6, ha="left", va="bottom")
a.text(0.04, 21.5, r"$v_{\rm g}-c$", color=BLUE, fontsize=8.2, ha="left", va="center")
a.text(0.40, 22.0, r"$v_{\rm ph}-c$", color=TEAL, fontsize=8.2, ha="left", va="center")
a.text(0.03, -13.0, r"$[\varepsilon(k)-2\varepsilon(k/2)]/\hbar k$", color=ORANGE, fontsize=8.2, ha="left", va="center")
a.set_xlim(0, 0.75); a.set_ylim(-34, 27)
a.set_xlabel(r"$k$ ($\mathrm{\AA}^{-1}$)"); a.set_ylabel("velocity excess (m/s)")
panel(a, "a")

# ---------------- (b) the energy balance of the decay k -> q + (k - q) --------------------------------------------
cols = [BLUE, TEAL, ORANGE, RED]
for kv, col in zip((0.30, 0.38, 0.43, 0.48), cols):
    q = np.linspace(0.0, kv / 2, 200)
    g = (eps_s(kv) - eps_s(q) - eps_s(kv - q)) * 1e3             # micro-eV
    b.plot(q / kv, g, color=col, lw=1.5)
    # the table where both q and k - q lie in the neutron / combined range (>= 0.15)
    qq = np.linspace(0.15, kv / 2, 60)
    qq = qq[(kv - qq) >= 0.15]
    if len(qq) > 3:
        gt = (f(kv) - f(qq) - f(kv - qq)) * 1e3
        b.plot(qq / kv, gt, ".", ms=2.4, color=col, alpha=0.8)
    b.text(0.508, g[-1], f"{kv:.2f}", color=col, fontsize=7.6, ha="left", va="center")
b.axhspan(0, 32, color=GOLD, alpha=0.07, lw=0); b.axhspan(-22, 0, color=RED, alpha=0.05, lw=0)
b.axhline(0, color=GREY, lw=0.8)
b.text(0.04, 21.3, "channel open: $g>0$", color=GREY, fontsize=7.8, ha="left", va="center")
b.text(0.04, -13.5, "closed", color=GREY, fontsize=7.8, ha="left", va="center")
b.text(0.455, 29.0, r"$k$ ($\mathrm{\AA}^{-1}$):", color=GREY, fontsize=7.6, ha="center", va="center")
b.set_xlim(0, 0.54); b.set_ylim(-22, 32)
b.set_xlabel(r"$q/k$"); b.set_ylabel(r"$g=\varepsilon(k)-\varepsilon(q)-\varepsilon(k-q)$ ($\mu$eV)")
panel(b, "b")
save(fig, "ch05_thresholds")
Path(__file__).with_name("ch05_thresholds_numbers.json").write_text(json.dumps({k_: F[k_] for k_ in (
    "k_group_series", "k_sym_series", "k_phase_series", "k_group_series_other_root", "k_sym_series_other_root", "k_phase_series_other_root",
    "k_sym_table_crossings", "sym_excess_max_ueV", "sym_excess_max_at_k", "series_minus_table_max_ueV_025_05", "series_minus_table_rms_ueV_025_05")}, indent=1))
