"""Chapter 1, 'the bench': what a cold neutron can reach on the measured 4He dispersion curve.

Data: the author-processed dispersion curve omega(Q) at P = 0 (saturated vapour pressure) that Godfrin et al. (PRB 103, 104516)
distribute as the ancillary file DispersionP0allRange.txt of arXiv:2012.09067 (copy in data/external/godfrin_2021_arxiv_ancillary/).
It is NOT raw instrument data.  Everything else is kinematics (energy and momentum conservation for a neutron of wave number k_i):

    a neutron can create an excitation (Q, eps) only if  hbar^2 (2 k_i Q - Q^2) / 2m >= eps      (Lean: NeutronWindow.min_incident_wavevector)
    i.e. k_i >= Q/2 + m eps / (hbar^2 Q)   <=>   v_n >= hbar Q / 2m + eps / (hbar Q)   (recoil speed + phase velocity of the excitation).

No claim is made about the settings actually used in any experiment: this is the kinematic limit, not an instrument specification.
Run:  .venv/bin/python book/figures/ch01_bench.py          Writes ch01_bench.{pdf,png} and the section "bench" of ch01_numbers.json
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
from scipy import constants as C
from scipy.interpolate import CubicSpline
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize

plt.rcParams["axes.unicode_minus"] = False
TABLE = ROOT / "data/external/godfrin_2021_arxiv_ancillary/DispersionP0allRange.txt"

# ---------------------------------------------------------------- the table
rows = []; N_ERR = 0
for ln in TABLE.read_bytes().decode("iso-8859-1").replace("\r\n", "\n").split("\n")[2:]:
    f = ln.split("\t")
    try: k, e = float(f[0]), float(f[1])
    except (ValueError, IndexError): continue                       # header remnants and the all-"--" separator row
    rows.append((k, e))
    if len(f) > 2 and f[2].strip() not in ("--", ""): N_ERR += 1
Q, EPS = np.array(rows).T                                            # Q in 1/Angstrom, EPS in meV
MEV_K = C.e * 1e-3 / C.k                                             # 1 meV in kelvin
HB2_2M = C.hbar ** 2 / (2 * C.m_n) / C.e * 1e3 * 1e20               # hbar^2/2m_n in meV Angstrom^2
VLAM = C.h / C.m_n * 1e10                                            # v_n * lambda in m/s * Angstrom
v_ph = np.full_like(EPS, np.nan); v_ph[1:] = EPS[1:] * 1e-3 * C.e / C.hbar / (Q[1:] * 1e10)   # phase velocity eps/(hbar Q), m/s
REC = C.hbar / (2 * C.m_n) * 1e10                                    # hbar/2m_n in m/s per (1/Angstrom): recoil speed per unit Q
kmin = np.full_like(EPS, np.nan); kmin[1:] = Q[1:] / 2 + EPS[1:] / (2 * HB2_2M * Q[1:])      # minimum incident wave number, 1/Angstrom
lam_max = 2 * np.pi / kmin                                           # longest incident wavelength that can create (Q, eps), Angstrom
v_min = np.full_like(EPS, np.nan); v_min[1:] = REC * Q[1:] + v_ph[1:]                          # minimum neutron speed, m/s
assert np.allclose(VLAM / lam_max[1:], v_min[1:], rtol=1e-9)         # the two forms of the theorem agree

# ---------------------------------------------------------------- landmarks of the curve
i_L = int(np.nanargmin(v_ph[1:]) + 1)                                # Landau critical velocity: min of eps/(hbar Q)
sel = (Q > 1.5) & (Q < 2.4); i_R = int(np.where(sel)[0][np.argmin(EPS[sel])])
sel = (Q > 0.8) & (Q < 1.6); i_M = int(np.where(sel)[0][np.argmax(EPS[sel])])
i_V = int(np.nanargmax(v_ph))                                        # maximum of the phase velocity (anomalous dispersion)
sel = (Q > 0.005) & (Q <= 0.2)
pf = np.polyfit(Q[sel] ** 2, v_ph[sel], 1)                           # v_ph ~ c (1 + a Q^2) on 0 < Q <= 0.2 (a crude estimate of c, not of alpha_2)
c_fit = float(pf[1])
# symmetric split  eps(k) - 2 eps(k/2)  from a cubic spline of the table (searched for k >= 0.1: below that the table's own rounding,
# 5e-5 meV, is comparable to the excess)
spl = CubicSpline(Q, EPS)
kk = np.linspace(0.10, 1.6, 7501); exc = spl(kk) - 2 * spl(kk / 2)
neg = np.where(exc < 0)[0]; k_c = float(kk[neg[0]]); k_exc_max = float(kk[np.argmax(exc)]); exc_max = float(exc.max()); exc_at_0p1 = float(exc[0])
# where the phase velocity returns to its Q -> 0 value
kq = np.linspace(Q[i_V], 1.5, 6001); vq = spl(kq) * 1e-3 * C.e / C.hbar / (kq * 1e10); Q_back = float(kq[np.where(vq < c_fit)[0][0]])
# window of a neutron of wavelength lam_i: eps <= HB2_2M (2 k_i Q - Q^2);  first exit of the curve above Q = 0.5
def window(lam):
    ki = 2 * np.pi / lam
    return ki, HB2_2M * ki ** 2, HB2_2M * (2 * ki * Q - Q ** 2)
reach = {}
for lam in (6.0, 5.0, 4.0, 3.0):
    ki, Ei, bound = window(lam)
    bad = np.where((Q > 0.5) & (EPS > bound))[0]
    reach[f"{lam:g}"] = dict(k_i=ki, E_i_meV=Ei, v_n_ms=VLAM / lam, Q_first_exit=float(Q[bad[0]]) if len(bad) else None, elastic_limit_2ki=2 * ki)
lam_end = float(lam_max[-1])
HC_EVA = C.h * C.c / C.e * 1e10                                      # h c in eV Angstrom
photon_5A_keV = HC_EVA / 5.0 * 1e-3; photon_wavelength_mm = HC_EVA / (HB2_2M * (2 * np.pi / 5.0) ** 2 * 1e-3) * 1e-10 * 1e3; ratio_photon = photon_5A_keV * 1e6 / (HB2_2M * (2 * np.pi / 5.0) ** 2)
numbers = dict(
    table=dict(file="data/external/godfrin_2021_arxiv_ancillary/DispersionP0allRange.txt", n_rows=int(len(Q)), n_rows_with_uncertainty=N_ERR, Q_min=float(Q[0]), Q_max=float(Q[-1])),
    constants=dict(hbar2_over_2m_neutron_meV_A2=HB2_2M, neutron_v_times_lambda_ms_A=VLAM, recoil_speed_per_invA_ms=REC, meV_in_K=MEV_K,
                   E_over_lambda2_meV_A2=HB2_2M * (2 * np.pi) ** 2),
    sound=dict(c_fit_ms=c_fit, vph_at_Q0p01=float(v_ph[np.argmin(abs(Q - 0.01))]), vph_max_ms=float(v_ph[i_V]), vph_max_Q=float(Q[i_V]),
               rise_percent=float(100 * (v_ph[i_V] / c_fit - 1))),
    landau=dict(v_L_ms=float(v_ph[i_L]), Q_L=float(Q[i_L]), eps_at_Q_L_meV=float(EPS[i_L]), v_L_over_c=float(v_ph[i_L] / c_fit)),
    roton=dict(Q0=float(Q[i_R]), eps_meV=float(EPS[i_R]), eps_K=float(EPS[i_R] * MEV_K), lam_max_A=float(lam_max[i_R]), k_min_invA=float(kmin[i_R]),
               v_min_ms=float(v_min[i_R]), E_i_min_meV=float(HB2_2M * kmin[i_R] ** 2)),
    maxon=dict(Q=float(Q[i_M]), eps_meV=float(EPS[i_M]), eps_K=float(EPS[i_M] * MEV_K), lam_max_A=float(lam_max[i_M])),
    end_of_table=dict(Q=float(Q[-1]), eps_meV=float(EPS[-1]), lam_max_A=lam_end, v_min_ms=float(v_min[-1])),
    at_Q3=dict(eps_meV=float(spl(3.0)), lam_max_A=float(2 * np.pi / (1.5 + spl(3.0) / (2 * HB2_2M * 3.0)))),
    lam_max_at_Q_to_zero_A=float(VLAM / c_fit),
    photon_at_5A=dict(energy_keV=float(photon_5A_keV), ratio_to_neutron_energy=float(ratio_photon), neutron_energy_meV=float(HB2_2M * (2 * np.pi / 5.0) ** 2), neutron_speed_ms=float(VLAM / 5.0), wavelength_of_a_photon_with_the_neutron_energy_mm=float(photon_wavelength_mm)),
    symmetric_split=dict(first_negative_k=k_c, k_of_max_excess=k_exc_max, max_excess_meV=exc_max, excess_at_k0p1_meV=exc_at_0p1, table_rounding_meV=5e-5),
    vph_back_to_c_Q=Q_back, windows=reach)
print(json.dumps(numbers, indent=1))

# ---------------------------------------------------------------- figure
fig = plt.figure(figsize=(TEXTW, 5.3))
gs = fig.add_gridspec(2, 1, height_ratios=[1.5, 1.0], hspace=0.12)
ax = fig.add_subplot(gs[0]); bx = fig.add_subplot(gs[1], sharex=ax)
cmap = LinearSegmentedColormap.from_list("lam", [RED, ORANGE, GOLD, TEAL, BLUE])
norm = Normalize(vmin=3.0, vmax=9.0)
YTOP = 1.78
# kinematic limits (descending flank only) of neutrons of wavelength lambda_i; the point (Q, eps) must lie below the line to be reachable
xx = np.linspace(0, 4.3, 4000)
for lam in (6.0, 5.0, 4.0):
    ki = 2 * np.pi / lam
    right = xx >= ki
    yy = HB2_2M * (2 * ki * xx - xx ** 2)
    sel = right & (yy <= YTOP)
    ax.plot(xx[sel], yy[sel], color=GREY, lw=0.8, ls=(0, (4, 2)), zorder=1)
    ax.text(xx[sel][0] + 0.09, YTOP - 0.02, rf"$\lambda_i={lam:g}$ Å", fontsize=7.8, color=GREY, ha="left", va="top")
# the curve, coloured by the longest wavelength that reaches each point
pts = np.column_stack([Q, EPS]); seg = np.stack([pts[:-1], pts[1:]], axis=1)
lm = np.where(np.isnan(lam_max), 99.0, lam_max); lseg = 0.5 * (lm[:-1] + lm[1:])
lc = LineCollection(seg, array=lseg, cmap=cmap, norm=norm, linewidths=2.7, capstyle="round", zorder=3)
ax.add_collection(lc)
cb = fig.colorbar(lc, ax=ax, location="top", shrink=0.70, aspect=38, pad=0.035, extend="max", ticks=[3, 4, 5, 6, 7, 8, 9])
cb.set_label("longest incident wavelength that can create this excitation (Å)", fontsize=8.5, labelpad=3); cb.outline.set_visible(False)
cb.ax.tick_params(labelsize=7.5, length=2)
for j in (i_M, i_R):
    ax.plot(Q[j], EPS[j], "o", ms=5.2, mfc="white", mec="k", mew=1.0, zorder=5)
ax.annotate(rf"maxon: {EPS[i_M]:.2f} meV ({EPS[i_M]*MEV_K:.1f} K)" + "\n" + rf"at $Q={Q[i_M]:.2f}$ Å$^{{-1}}$; $\lambda_i\leq{lam_max[i_M]:.1f}$ Å",
            xy=(Q[i_M], EPS[i_M]), xytext=(Q[i_M] - 0.30, EPS[i_M] + 0.14), fontsize=8, ha="center", va="bottom", color="#222222", zorder=6)
ax.annotate(rf"roton: {EPS[i_R]:.3f} meV ({EPS[i_R]*MEV_K:.1f} K)" + "\n" + rf"at $Q={Q[i_R]:.2f}$ Å$^{{-1}}$; $\lambda_i\leq{lam_max[i_R]:.2f}$ Å",
            xy=(Q[i_R], EPS[i_R]), xytext=(1.30, 0.26), fontsize=8, ha="center", va="center", color="#222222", arrowprops=dict(arrowstyle="-", lw=0.6, color=GREY, shrinkA=2, shrinkB=3), zorder=6)
ax.annotate(rf"$Q={Q[-1]:.1f}$ Å$^{{-1}}$:" + "\n" + rf"$\lambda_i\leq{lam_end:.2f}$ Å", xy=(Q[-1], EPS[-1]), xytext=(3.58, 1.12), fontsize=8, ha="right", va="center", color="#222222",
            arrowprops=dict(arrowstyle="-", lw=0.6, color=GREY, shrinkA=2, shrinkB=3), zorder=6)
ax.set_xlim(0, 3.7); ax.set_ylim(0, YTOP)
ax.set_ylabel(r"excitation energy $\varepsilon(Q)$ (meV)")
panel(ax, "a")
sec = ax.secondary_yaxis("right", functions=(lambda y: y * MEV_K, lambda y: y / MEV_K)); sec.set_ylabel("K", fontsize=8.5); sec.tick_params(labelsize=7.5)
plt.setp(ax.get_xticklabels(), visible=False)

# bottom panel: phase velocity eps/(hbar Q)
bx.fill_between(Q[1:], c_fit, v_ph[1:], where=(v_ph[1:] > c_fit), color=ORANGE, alpha=0.35, lw=0)
bx.plot(Q[1:], v_ph[1:], color=BLUE, lw=1.7)
bx.axhline(c_fit, color=GREY, lw=0.8, ls=(0, (3, 2))); bx.axhline(v_ph[i_L], color=GREY, lw=0.8, ls=(0, (3, 2)))
bx.text(3.68, c_fit + 4, rf"$c\approx{c_fit:.0f}$ m/s (extrapolated from the table)", fontsize=7.8, color=GREY, ha="right", va="bottom")
bx.text(3.68, v_ph[i_L] - 4, rf"$v_L={v_ph[i_L]:.1f}$ m/s $={v_ph[i_L]/c_fit:.2f}\,c$", fontsize=7.8, color=GREY, ha="right", va="top")
bx.plot(Q[i_L], v_ph[i_L], "o", ms=5.0, mfc="white", mec=BLUE, mew=1.2, zorder=5)
bx.annotate(rf"minimum at $Q={Q[i_L]:.2f}$ Å$^{{-1}}$:" + "\n" + "the Landau critical velocity", xy=(Q[i_L], v_ph[i_L]), xytext=(2.85, 140), fontsize=7.8, color="#222222", ha="center", va="center",
            arrowprops=dict(arrowstyle="-", lw=0.6, color=GREY, shrinkA=2, shrinkB=3))
bx.annotate(rf"$\varepsilon/\hbar Q>c$ for $Q<{Q_back:.2f}$ Å$^{{-1}}$:" + "\n" + rf"anomalous dispersion, peak +{numbers['sound']['rise_percent']:.1f} %", xy=(Q[i_V], v_ph[i_V]), xytext=(1.05, 215),
            fontsize=7.8, color=ORANGE, ha="left", va="center", arrowprops=dict(arrowstyle="-", lw=0.6, color=ORANGE, shrinkA=2, shrinkB=2))
bx.plot([0.10, k_c], [33, 33], color=RED, lw=3.2, solid_capstyle="butt")
bx.text(k_c + 0.06, 33, rf"$\varepsilon(k)>2\,\varepsilon(k/2)$ for $0.10\leq k<{k_c:.2f}$ Å$^{{-1}}$", fontsize=7.6, color=RED, ha="left", va="center")
bx.set_ylim(22, 275); bx.set_yticks([50, 100, 150, 200, 250]); bx.set_xlim(0, 3.7)
bx.set_xlabel(r"wave number transfer $Q$ (Å$^{-1}$)"); bx.set_ylabel(r"$\varepsilon/\hbar Q$ (m/s)")
panel(bx, "b")

NJ = Path(__file__).with_name("ch01_numbers.json")
allj = json.loads(NJ.read_text()) if NJ.exists() else {}
allj["bench"] = numbers; NJ.write_text(json.dumps(allj, indent=1))
save(fig, "ch01_bench")
