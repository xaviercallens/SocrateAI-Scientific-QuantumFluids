"""Landau two-parameter phenomenological dispersion model for superfluid He-4.

Physics (EXPRESSION_MEMO_E1.md E1.1, E1.2):
  - Phonon branch (low Q): E(Q) ~ c*Q, linear, c = sound velocity.
  - Roton branch (near Q_m ~ 1.9 A^-1): E(Q) has a local minimum of depth
    Delta (the roton gap) at wavevector Q_m, with curvature set by an
    effective roton mass mu.

Single-branch phenomenological form (Landau 1947, as used e.g. in
Cowley & Woods 1971; Glyde et al. 1998; Godfrin et al. 2021 fit their
data to a closely related functional form — see LITERATURE_LEDGER.md):

    E(Q) = Delta + hbar^2 * (Q - Q_m)^2 / (2 * mu)

This module fits ONLY the roton region with the parabolic form above
(3 free parameters: Delta, Q_m, mu) and the phonon region separately with
a linear form (1 free parameter: c), rather than a single global
closed-form covering both branches — the two-region fit is what M1's
plan (see PLAN.md) and the literature comparison table (Cowley-Woods,
Glyde et al.) actually report values for.
"""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import curve_fit

# hbar in meV*ps (neutron-scattering-friendly units: Q in Angstrom^-1,
# E in meV, mass in units where hbar^2/(2*mu) has meV*Angstrom^2 dimensions)
HBAR_MEVPS = 0.6582119569  # meV * ps, CODATA


def phonon_branch(Q: np.ndarray, c: float) -> np.ndarray:
    """Linear phonon dispersion: E = c * Q (c in meV*Angstrom, Q in Angstrom^-1)."""
    return c * Q


def roton_branch(Q: np.ndarray, delta: float, q_m: float, inv_two_mu: float) -> np.ndarray:
    """Parabolic roton dispersion: E = delta + inv_two_mu * (Q - q_m)^2.

    inv_two_mu absorbs hbar^2/(2*mu) into a single fit parameter with units
    meV*Angstrom^2, avoiding a separate unit-conversion step for the
    effective roton mass mu (which is reported in derived_effective_mass()
    if needed for cross-checking against literature mu values).
    """
    return delta + inv_two_mu * (Q - q_m) ** 2


@dataclass
class PhononFitResult:
    c: float
    c_stderr: float
    n_points: int
    residuals: np.ndarray


@dataclass
class RotonFitResult:
    delta: float
    delta_stderr: float
    q_m: float
    q_m_stderr: float
    inv_two_mu: float
    inv_two_mu_stderr: float
    n_points: int
    residuals: np.ndarray

    def effective_mass_amu(self) -> float:
        """Roton effective mass in units of the He-4 atomic mass (m_He4).

        mu = hbar^2 / (2 * inv_two_mu); converts to m_He4 using
        m_He4 c^2-equivalent via the standard neutron-scattering relation
        hbar^2 / (2 m_He4) = 1.0454 meV*Angstrom^2 (from m_He4 = 4.0026 u).
        """
        HBAR2_OVER_2M_HE4 = 1.0454  # meV * Angstrom^2
        mu_over_m_he4 = HBAR2_OVER_2M_HE4 / self.inv_two_mu
        return mu_over_m_he4


def fit_phonon_branch(Q: np.ndarray, E: np.ndarray, dE: np.ndarray | None = None) -> PhononFitResult:
    """Fit c to the low-Q phonon region. Caller selects the Q-range mask."""
    if len(Q) < 2:
        raise ValueError(f"Need at least 2 points to fit phonon branch, got {len(Q)}")

    sigma = dE if dE is not None else None
    popt, pcov = curve_fit(phonon_branch, Q, E, p0=[240.0 / 1000.0 * Q[-1] if Q[-1] > 0 else 1.0],
                            sigma=sigma, absolute_sigma=sigma is not None)
    c = popt[0]
    c_stderr = float(np.sqrt(pcov[0, 0]))
    residuals = E - phonon_branch(Q, c)

    return PhononFitResult(c=c, c_stderr=c_stderr, n_points=len(Q), residuals=residuals)


def fit_roton_branch(
    Q: np.ndarray,
    E: np.ndarray,
    dE: np.ndarray | None = None,
    p0: tuple[float, float, float] = (8.6, 1.9, 5.0),
) -> RotonFitResult:
    """Fit (delta, q_m, inv_two_mu) to the near-roton-minimum region.

    p0 defaults are literature-typical starting points for saturated vapor
    pressure He-4 (delta ~ 8.6 meV, q_m ~ 1.9 Angstrom^-1) — see
    LITERATURE_LEDGER.md [LIT-001], [LIT-002]. Caller selects the Q-range
    mask around the minimum before calling this.
    """
    if len(Q) < 4:
        raise ValueError(
            f"Need at least 4 points to fit 3-parameter roton branch, got {len(Q)}"
        )

    sigma = dE if dE is not None else None
    popt, pcov = curve_fit(roton_branch, Q, E, p0=p0, sigma=sigma, absolute_sigma=sigma is not None)
    delta, q_m, inv_two_mu = popt
    stderrs = np.sqrt(np.diag(pcov))
    residuals = E - roton_branch(Q, delta, q_m, inv_two_mu)

    return RotonFitResult(
        delta=delta,
        delta_stderr=float(stderrs[0]),
        q_m=q_m,
        q_m_stderr=float(stderrs[1]),
        inv_two_mu=inv_two_mu,
        inv_two_mu_stderr=float(stderrs[2]),
        n_points=len(Q),
        residuals=residuals,
    )
