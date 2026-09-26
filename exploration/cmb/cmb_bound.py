"""Independent 2-sigma bound on the dark-energy-conversion fraction r, following Koren, Tsai,
Wang, "Boiling After the Dust Settles" (arXiv:2509.07076), Sec. III, Eq. (14), against the real
Planck 2018 TT power spectrum. See docs/designs/CMB_CASCADE_REPRODUCTION.md for the full writeup,
the equations implemented, and an honest account of what does and does not match the published
Fig. 3 / Eq. (15).

    uv run python exploration/cmb/cmb_bound.py
"""
import os

import numpy as np

from cmb_cascade import D_ell_pt

_HERE = os.path.dirname(os.path.abspath(__file__))
_PLANCK_TT = os.path.join(_HERE, "..", "..", "data", "external", "planck2018_tt_full",
                           "COM_PowerSpect_CMB-TT-full_R3.01.txt")

# Real Planck 2018 TT power spectrum (ell, Dl, -dDl, +dDl), muK^2, from the Planck Legacy Archive
# (COM_PowerSpect_CMB-TT-full_R3.01.txt), cross-checked against Aghanim et al. 2020 (arXiv:1807.06209):
# the low-l plateau (~700-1700 muK^2 for l<50) and first-peak amplitude (D_220 ~ 6373 muK^2) match
# the published Planck 2018 TT spectrum.
_ELL_P, _DL_P, _DM_P, _DP_P = np.loadtxt(_PLANCK_TT, unpack=True)
_SIGMA_P = 0.5 * (_DM_P + _DP_P)  # symmetrized 1-sigma error bar, muK^2 (Planck's own bars are
                                   # mildly asymmetric at very low ell; we average them)


def sigma_ell(ell):
    idx = int(np.argmin(np.abs(_ELL_P - ell)))
    return _SIGMA_P[idx]


def peak_ell(zpt, beta_over_H, r_pt=0.1, ell_grid=(3, 5, 7, 9, 12, 15, 20, 25, 30, 40)):
    """Coarse peak-finder for D_ell,pt -- the paper's own l_p, found on a sparse grid (not every
    integer ell) to keep the nested-integral cost tractable; see the design doc for the cost/
    accuracy tradeoff this implies."""
    vals = [D_ell_pt(l, zpt, r_pt, beta_over_H) for l in ell_grid]
    return ell_grid[int(np.argmax(vals))]


def chi2_for_r(r_pt, zpt, beta_over_H, ell_peak):
    """Eq. (14), three l-bins centered on ell_peak."""
    ells = [l for l in (ell_peak - 1, ell_peak, ell_peak + 1) if l >= 2]
    chi2 = 0.0
    for l in ells:
        Dl = D_ell_pt(l, zpt, r_pt, beta_over_H)
        chi2 += (Dl / sigma_ell(l)) ** 2
    return chi2


def r_bound_2sigma(zpt, beta_over_H, chi2_target=5.99, r_probe=0.1):
    """D_ell,pt(r) = r^2 * D_ell,pt(1) exactly (Eq. 11: Pdz0 is proportional to r^2), so
    chi2(r) = (r/r_probe)^4 * chi2(r_probe): solve directly, no root-finder needed."""
    ell_p = peak_ell(zpt, beta_over_H)
    chi2_probe = chi2_for_r(r_probe, zpt, beta_over_H, ell_p)
    if chi2_probe <= 0:
        return np.nan, ell_p
    return r_probe * (chi2_target / chi2_probe) ** 0.25, ell_p


if __name__ == "__main__":
    print(f"{'beta/H*':>8} {'zpt':>5} {'ell_peak':>9} {'r_2sigma (ours)':>16} {'r<=1e-5*(beta/H)^2':>20}")
    for zpt in (0.1, 0.2):
        for beta_h in (10, 20, 50, 100, 200, 500):
            r_b, ell_p = r_bound_2sigma(zpt, beta_h)
            analytic = 1e-5 * beta_h ** 2
            print(f"{beta_h:8d} {zpt:5.2f} {ell_p:9d} {r_b:16.4g} {analytic:20.4g}")
