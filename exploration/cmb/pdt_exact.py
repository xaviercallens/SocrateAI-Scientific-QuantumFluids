"""The EXACT bubble-completion-time power spectrum, from Elor, Jinno, Kumar, McGehee, Tsai
(arXiv:2311.16222), Supplementary Material Eqs. (S1)-(S16), read directly (2026-09-26).

`cmb_cascade.py`'s `P_interp_xi` approximates the full curve of their Fig. S4 with a two-asymptote
interpolation, because neither Elor et al. nor Koren-Tsai-Wang (arXiv:2509.07076) publish a single
closed form for it -- only the two power-law limits and a numerically-computed plot. Their
Supplementary Material DOES give the correlator itself in closed form (a finite sum of two
one-dimensional integrals, Eqs. S9-S16, "these are one-dimensional integrals and easy to evaluate"),
which we integrate here, then Fourier-transform (their Eq. S1-S2) to get the exact P_delta-t(k),
removing the interpolation approximation entirely.

Variable-name correspondence (checked against `cmb_cascade.py`'s existing `xi_of_hatk`): Elor's own
"k/beta" variable (beta=1, vw=1 units) is xi/(8pi)^(1/3), where `xi` is Koren-Tsai-Wang's own
rescaled wavenumber. We work in Elor's own "k/beta" variable throughout this module and expose
`P_exact_k_elor(k_elor)`; `cmb_cascade.py` converts `hat_k` to `k_elor` at the call site.

Sanity checks performed and passing before this module was relied on:
- correlator(r->0) = pi^2/6 = 1.6449... exactly, matching Fig. S3's single-bubble curve's r->0
  value (the double-bubble contribution vanishes at r=0, matching Fig. S3's red curve starting at 0).
- correlator(r) matches Fig. S3's shape and scale (single~1.64 falling to ~0 by r~15-20; double
  peaking ~0.4 near r~2; sum peaking at 1.64 at r->0) at several sampled r values.
- P_exact_k_elor(k) peaks at k=0.493 with value 1.077, matching Fig. S4's peak (~1, near k/beta~0.5)
  and its two labelled asymptotes (~70 k^3 for k<<1, ~0.7 k^-3 for k>>1) at the sampled endpoints.
"""
import numpy as np
from pathlib import Path
from scipy import integrate

_CACHE = Path(__file__).parent / "pdt_exact_table.npz"
_R_MAX = 45.0
_N_R = 250


def _I_func(t_xy, r):
    return 8 * np.pi * (
        np.exp(t_xy / 2) + np.exp(-t_xy / 2)
        + (t_xy ** 2 - (r ** 2 + 4 * r)) / (4 * r) * np.exp(-r / 2)
    )


def _single_integrand(t_xy, r):
    """Eq. (S11)'s integrand (single-bubble contribution to beta^2<delta_tc delta_tc>(r))."""
    Ival = _I_func(t_xy, r)
    term1 = 2 * np.pi * np.exp(-r / 2) / (r * Ival)
    term2 = r ** 2 / 4 + r + 2 - t_xy ** 2 / 4
    term3 = np.log(Ival / (8 * np.pi)) ** 2 - t_xy ** 2 / 4 + np.pi ** 2 / 6
    return term1 * term2 * term3


def _double_integrand(t_xy, r):
    """Eq. (S16)'s integrand (double-bubble contribution)."""
    Ival = _I_func(t_xy, r)
    termB = (np.exp(-t_xy / 2 - r / 2) / (2 * r)) * (r + t_xy + 4) * (r - t_xy)
    termC = (np.exp(t_xy / 2 - r / 2) / (2 * r)) * (r - t_xy + 4) * (r + t_xy)
    termD = (np.exp(-r) / (16 * r ** 2)) * ((r + 4) ** 2 - t_xy ** 2) * (r ** 2 - t_xy ** 2)
    bracket1 = 4 - termB - termC + termD
    bracket2 = (np.log(Ival / (8 * np.pi)) - 1) ** 2 - t_xy ** 2 / 4 + np.pi ** 2 / 6 - 1
    return (16 * np.pi ** 2 / Ival ** 2) * bracket1 * bracket2


def _correlator(r):
    """beta^2 <delta_tc(x) delta_tc(y)>(r), Eq. (S3) = Eq. (S11) + Eq. (S16)."""
    r = max(r, 1e-4)
    s, _ = integrate.quad(_single_integrand, -r, r, args=(r,), limit=200)
    d, _ = integrate.quad(_double_integrand, -r, r, args=(r,), limit=200)
    return s + d


def _build_table():
    r_grid = np.linspace(1e-4, _R_MAX, _N_R)
    corr_grid = np.array([_correlator(r) for r in r_grid])
    np.savez(_CACHE, r=r_grid, corr=corr_grid)
    return r_grid, corr_grid


def _load_table():
    if _CACHE.exists():
        d = np.load(_CACHE)
        return d["r"], d["corr"]
    return _build_table()


_R_GRID, _CORR_GRID = _load_table()


def P_beta_dtc_exact(k_elor):
    """Eq. (S2): the (non-dimensionless) Fourier transform of the correlator, via a Fourier
    sine transform over the precomputed correlator table (fast: no nested quadrature)."""
    k_elor = max(k_elor, 1e-8)
    kr = k_elor * _R_GRID
    sinc = np.where(kr < 1e-8, 1.0, np.sin(kr) / np.where(kr < 1e-8, 1.0, kr))
    integrand = 4 * np.pi * _R_GRID ** 2 * sinc * _CORR_GRID
    return np.trapezoid(integrand, _R_GRID)


def P_exact_k_elor(k_elor):
    """Eq. (S1): the dimensionless power spectrum P_delta-t, in Elor et al.'s own k/beta units
    (beta=1, vw=1 convention) -- the exact replacement for `cmb_cascade.P_interp_xi`.

    Known limitation, stated explicitly: for k_elor gtrsim 5-10 the fixed-grid Fourier sine
    transform below under-resolves the rapidly oscillating sin(kr) integrand (the correlator
    table has only `_N_R` points over `_R_MAX`), which can return small negative or noisy values
    where the true spectrum is a tiny positive number on its k^-3 tail. We clip to zero rather
    than report a negative "power". This region is never reached by the CMB bound calculation in
    `cmb_cascade.py` (whose scan stays within about a factor of 10 of the peak at k_elor~0.5, i.e.
    k_elor up to ~5), so it does not affect the reproduction reported in the design doc."""
    return max(0.0, (k_elor ** 3 / (2 * np.pi ** 2)) * P_beta_dtc_exact(k_elor))


if __name__ == "__main__":
    for k in [0.01, 0.03, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 2.0, 5.0, 10.0]:
        print(f"k/beta={k:6.3f}  P_dt_exact={P_exact_k_elor(k):12.6f}")
    kfine = np.geomspace(0.05, 3, 400)
    vfine = np.array([P_exact_k_elor(k) for k in kfine])
    imax = np.argmax(vfine)
    print("peak at k/beta =", kfine[imax], " value =", vfine[imax])
