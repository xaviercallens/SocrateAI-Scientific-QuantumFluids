"""Chapter 5: the published 4He dispersion table (P = 0, T < 0.1 K) and every number the text quotes from it.

Source of the table: Godfrin et al., Phys. Rev. B 103, 104516 (2021), arXiv:2012.09067 -- the ancillary file
`DispersionP0allRange.txt` (the authors' own processed curve on a 0.002 A^-1 grid, NOT raw ILL counts), cached in
data/external/godfrin_2021_arxiv_ancillary/.  Per the caption of the paper's Table (arXiv version): below k = 0.15 A^-1 the
values are ultrasound data (Rugar & Foster), 0.15-0.3 combined ultrasound + neutron, above 0.3 neutron data.
Constants: sound speed c = 238.3 +- 0.1 m/s, atom mass 4.0026032 u, density 0.021836 A^-3 (all as quoted in that paper);
alpha_2, alpha_3, alpha_4 = 1.55, -4.04, 2.30 (A^2, A^3, A^4): the SVP series coefficients the paper uses for k < 0.5 A^-1.
"""
from pathlib import Path
import numpy as np
import scipy.constants as C

ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT / "data/external/godfrin_2021_arxiv_ancillary/DispersionP0allRange.txt"

HBAR, KB, EV, AMU = C.hbar, C.k, C.e, C.atomic_mass
MEV = 1e-3 * EV                                  # J
C_SVP = 238.3                                    # m/s (paper)
M4 = 4.0026032 * AMU                             # kg  (paper: 4.0026032 g/mol)
N_SVP = 0.021836                                 # A^-3 (paper, P = 0)
A2, A3, A4 = 1.55, -4.04, 2.30                   # A^2, A^3, A^4
HBARC = HBAR * C_SVP / MEV * 1e10                # meV A   (hbar c)
HBAR2_2M4 = HBAR ** 2 / (2 * M4) / MEV * 1e20    # meV A^2 (hbar^2 / 2 m4)
K_PER_MEV = MEV / KB                             # kelvin per meV
MS_PER_MEVA = MEV * 1e-10 / HBAR                 # (m/s) per (meV A):  hbar v = (meV A)  ->  v in m/s
KSTAR = 2 * M4 * C_SVP / HBAR * 1e-10            # A^-1: the one Bogoliubov wave number 2 m c / hbar for 4He parameters
A2_BOG = 1.0 / (2 * KSTAR ** 2)                  # A^2: Bogoliubov curvature coefficient hbar^2/(8 m^2 c^2) = 1/(2 k*^2)


def load_table(path=TABLE):
    """k [A^-1], e [meV], err [meV, NaN where the file has none].  ISO-8859-1, CRLF, tab-separated, two header lines,
    '--' = no value, one all-'--' separator row."""
    rows = []
    for ln in open(path, encoding="iso-8859-1", newline="").read().splitlines()[2:]:
        a = [x.strip() for x in ln.split("\t")]
        if len(a) < 3 or a[0] == "--":
            continue
        rows.append((float(a[0]), float(a[1]), np.nan if a[2] == "--" else float(a[2])))
    d = np.array(rows)
    return d[:, 0], d[:, 1], d[:, 2]


def series(k, a2=A2, a3=A3, a4=A4):
    """epsilon/(hbar c) = k (1 + a2 k^2 + a3 k^3 + a4 k^4) in A^-1 (HeliumKinematics.seriesDisp with c = 1)."""
    return k * (1 + a2 * k ** 2 + a3 * k ** 3 + a4 * k ** 4)


def features():
    """All table-derived numbers quoted in the chapter."""
    k, e, de = load_table()
    out = {"table_rows": int(len(k)), "k_min": float(k[0]), "k_max": float(k[-1]), "e_at_kmax_meV": float(e[-1]),
           "rows_with_error": int(np.isfinite(de).sum())}
    # constants
    out.update(c_ms=C_SVP, hbar_c_meV_A=float(HBARC), hbar2_over_2m4_meV_A2=float(HBAR2_2M4), K_per_meV=float(K_PER_MEV),
               kstar_A_inv=float(KSTAR), alpha2_bogoliubov_barem_A2=float(A2_BOG), alpha2_measured_A2=A2,
               alpha2_ratio=float(A2 / A2_BOG), density_A3=N_SVP)
    # maxon and roton: the paper's cubic / quartic polynomial fits around the extremum, applied to the table
    j = np.argmax(np.where((k > 0.8) & (k < 1.5), e, -1.0))
    sel = (k > k[j] - 0.1) & (k < k[j] + 0.1)
    p = np.polyfit(k[sel] - k[j], e[sel], 3)             # e = p0 x^3 + p1 x^2 + p2 x + p3
    xm = np.roots(np.polyder(p)); xm = xm[np.isreal(xm)].real; xm = xm[np.argmin(np.abs(xm))]
    kM, EM = k[j] + xm, np.polyval(p, xm)
    d2 = np.polyval(np.polyder(p, 2), xm)                # e'' at the maxon (< 0)
    out.update(maxon_grid_k=float(k[j]), maxon_grid_e_meV=float(e[j]), maxon_fit_k=float(kM), maxon_fit_e_meV=float(EM),
               maxon_mass_over_m4=float(HBAR2_2M4 / (d2 / 2)))
    j = np.argmin(np.where((k > 1.5) & (k < 2.5), e, 99.0))
    kR0 = k[j]
    sel = (k > kR0 - 0.2) & (k < kR0 + 0.3)              # the asymmetric range the paper uses for its quartic fit
    q = np.polyfit(k[sel] - kR0, e[sel], 4)
    xr = np.roots(np.polyder(q)); xr = xr[np.isreal(xr)].real; xr = xr[np.argmin(np.abs(xr))]
    kR, ER = kR0 + xr, np.polyval(q, xr)
    d2r = np.polyval(np.polyder(q, 2), xr)
    muR = HBAR2_2M4 / (d2r / 2)
    out.update(roton_grid_k=float(kR0), roton_grid_e_meV=float(e[j]), roton_fit_k=float(kR), roton_fit_e_meV=float(ER),
               roton_gap_K=float(ER * K_PER_MEV), roton_mass_over_m4=float(muR))
    # Landau velocity from the table: min over k of eps/(hbar k)
    ph = e[1:] / k[1:]
    sel = k[1:] > 1.0
    i = np.argmin(np.where(sel, ph, 1e9))
    out.update(landau_k_A_inv=float(k[1:][i]), landau_meV_A=float(ph[i]), landau_velocity_ms=float(ph[i] * MS_PER_MEVA),
               landau_over_c=float(ph[i] * MS_PER_MEVA / C_SVP))
    # Landau's quadratic roton form: closed-form critical velocity  hbar v_L = 2 a (k_L - k_R),  k_L = sqrt(k_R^2 + Delta/a)
    # (the table's own minimum, 0.7413 meV at 1.92 A^-1, and the roton mass of the quartic fit)
    a = HBAR2_2M4 / muR
    kR_g, ER_g = float(k[j]), float(e[j])
    kL = np.sqrt(kR_g ** 2 + ER_g / a)
    out.update(landau_quadratic_roton_k=float(kL), landau_quadratic_roton_ms=float(2 * a * (kL - kR_g) * MS_PER_MEVA),
               roton_grid_gap_K=float(ER_g * K_PER_MEV))
    j01 = int(np.argmin(np.abs(k - 0.01)))
    out.update(vph_at_k_0p01_ms=float(e[j01] / k[j01] * MS_PER_MEVA))
    # the paper's own roton parameters at P = 0, as printed (arXiv version, Table III): Delta_R = 0.7418(10) meV
    # (the energy-calibration input), k_R = 1.918(2) A^-1, mu_R = 0.141(2); maxon: 1.191(1) meV, 1.103(2) A^-1
    out.update(paper_roton=dict(gap_meV=0.7418, k=1.918, mu=0.141), paper_maxon=dict(e_meV=1.191, k=1.103, mu=-0.545))
    # phase velocity at a few points
    for kk in (0.3, 0.5, 1.0):
        jj = np.argmin(np.abs(k - kk))
        out[f"phase_velocity_over_c_at_{kk}"] = float(e[jj] / k[jj] / HBARC)
    # phonon window: maximum of the table's normalised phase velocity (k >= 0.15, the neutron / combined region)
    sel = (k >= 0.15) & (k <= 1.0)
    r = e[sel] / (HBARC * k[sel])
    out.update(phase_velocity_max_over_c=float(r.max()), phase_velocity_max_at_k=float(k[sel][np.argmax(r)]))
    # Debye wave number of the mode count (HeliumKinematics.debye_mode_count): k_D = (6 pi^2 n)^(1/3)
    out["debye_k_A_inv"] = float((6 * np.pi ** 2 * N_SVP) ** (1.0 / 3.0))
    # thresholds of the three-phonon channels from the series (HeliumKinematics: symmetric_split_excess,
    # group_velocity_excess, phase_velocity_excess): roots of the quadratics  Q(k) = 0
    def smallest_root(cq, cl, c0):                      # cq k^2 + cl k + c0 = 0
        r = np.roots([cq, cl, c0]); r = r[np.isreal(r)].real; r = r[r > 0]
        return float(np.sort(r)[0]), float(np.sort(r)[-1])
    out["k_group_series"], out["k_group_series_other_root"] = smallest_root(5 * A4, 4 * A3, 3 * A2)
    out["k_sym_series"], out["k_sym_series_other_root"] = smallest_root(15 / 16 * A4, 7 / 8 * A3, 3 / 4 * A2)
    out["k_phase_series"], out["k_phase_series_other_root"] = smallest_root(A4, A3, A2)
    # sensitivity of the two sound-line thresholds to a proportional recalibration of the energy scale by 1 +- 2.1e-3 (the relative
    # systematic uncertainty quoted by the paper); the symmetric split is exactly invariant (homogeneous of degree one in the energy)
    from scipy.optimize import brentq
    qg = lambda x: 3 * A2 * x ** 2 + 4 * A3 * x ** 3 + 5 * A4 * x ** 4
    qp = lambda x: A2 * x ** 2 + A3 * x ** 3 + A4 * x ** 4
    sg, sp_ = [], []
    for lam in (1 + 2.1e-3, 1 - 2.1e-3):
        sg.append(brentq(lambda x: lam * (1 + qg(x)) - 1, 0.3, 0.6) - out["k_group_series"])
        sp_.append(brentq(lambda x: lam * (1 + qp(x)) - 1, 0.4, 0.8) - out["k_phase_series"])
    out["k_group_shift_max"] = float(max(abs(x) for x in sg)); out["k_phase_shift_max"] = float(max(abs(x) for x in sp_))
    # symmetric-split excess from the table  eps(k) - 2 eps(k/2)  (needs k/2 >= 0.15)
    f = lambda kk: np.interp(kk, k, e)
    grid = np.linspace(0.30, 1.0, 1401)
    g = f(grid) - 2 * f(grid / 2)
    cross = grid[1:][np.diff(np.sign(g)) != 0]
    out.update(k_sym_table_crossings=[float(x) for x in cross], sym_excess_max_ueV=float(g.max() * 1e3),
               sym_excess_max_at_k=float(grid[np.argmax(g)]))
    # relative systematic energy uncertainty quoted by the paper (global, proportional): 2.1e-3
    out["paper_relative_energy_systematic"] = 2.1e-3
    # total the series reproduces the table to what level for 0.25 <= k <= 0.5
    sel = (k >= 0.25) & (k <= 0.5)
    dev = series(k[sel]) * HBARC - e[sel]
    out.update(series_minus_table_max_ueV_025_05=float(np.abs(dev).max() * 1e3), series_minus_table_rms_ueV_025_05=float(np.sqrt(np.mean(dev ** 2)) * 1e3))
    return out


# ---------------------------------------------------------------------------------------------------- the pressure series
ALL_P = ROOT / "data/external/godfrin_2021_arxiv_ancillary/DispersionAllPressures.txt"
PRESSURES = [0.0, 0.51, 1.02, 2.01, 5.01, 10.01, 24.08]                  # bar (corrected pressures of the paper's Table I)
C_ULTRASOUND = [238.3, 242.6, 246.5, 253.9, 274.0, 302.3, 361.9]        # m/s, ultrasound column of the paper's sound-velocity table (arXiv v1)


def load_all_pressures(path=ALL_P):
    """k [A^-1] (from 0.150), E [meV] (n, 7) and err [meV] (n, 7) at the seven pressures.  UTF-16 LE, CRLF, tab-separated, 3 header lines."""
    txt = open(path, "rb").read().decode("utf-16-le", errors="replace").lstrip("\ufeff")
    rows = []
    for ln in txt.splitlines()[3:]:
        a = ln.split("\t")
        if len(a) < 16:
            continue
        rows.append([float(x) if x.strip() not in ("", "NAN", "NaN", "nan") else np.nan for x in a[1:16]])
    d = np.array(rows)
    return d[:, 0], d[:, 1::2][:, :7], d[:, 2::2][:, :7]


def landau_vs_pressure():
    """Roton minimum and Landau velocity min_k eps/(hbar k) (k >= 1 A^-1) of every pressure of the series, and v_L / c(P)."""
    k, E, dE = load_all_pressures()
    out = []
    for j, (P, c) in enumerate(zip(PRESSURES, C_ULTRASOUND)):
        e = E[:, j]; m = np.isfinite(e)
        kk, ee = k[m], e[m]
        iR = int(np.argmin(np.where(kk > 1.5, ee, 99.0)))
        sel = kk > 1.0
        ph = ee[sel] / kk[sel]
        i = int(np.argmin(ph))
        vL = ph[i] * MS_PER_MEVA
        out.append(dict(P_bar=P, c_ultrasound_ms=c, roton_k=float(kk[iR]), roton_E_meV=float(ee[iR]), landau_k=float(kk[sel][i]),
                        landau_ms=float(vL), landau_over_c=float(vL / c), k_range_max=float(kk.max())))
    return out


def group_velocity(k, e, win=0.06):
    """d eps/d(hbar k) in m/s from the table by a local linear (Savitzky-Golay-like) fit over +-win A^-1."""
    v = np.full_like(k, np.nan)
    for i, kk in enumerate(k):
        s = np.abs(k - kk) <= win
        if s.sum() >= 5:
            v[i] = np.polyfit(k[s], e[s], 1)[0] * MS_PER_MEVA
    return v


if __name__ == "__main__":
    import json
    print(json.dumps(features(), indent=1))
