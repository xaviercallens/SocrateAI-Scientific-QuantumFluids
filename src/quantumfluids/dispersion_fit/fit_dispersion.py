"""End-to-end dispersion-fit workflow: load data -> select regions -> fit -> compare.

Ties together adapters.load_ascii_sqw / load_digitized_csv (or nexus_reader)
with landau_model.fit_phonon_branch / fit_roton_branch, and reports results
against the literature comparison table (LITERATURE_LEDGER.md).
"""

from dataclasses import dataclass

import numpy as np

from quantumfluids.adapters.ascii_sqw import SQwData
from quantumfluids.dispersion_fit.landau_model import (
    PhononFitResult,
    RotonFitResult,
    fit_phonon_branch,
    fit_roton_branch,
)

# Literature reference values (meV, Angstrom^-1) — see LITERATURE_LEDGER.md
# and M1_CHECKLIST.md Phase 4.1. c is quoted in m/s in the literature;
# converted here to meV*Angstrom (E = c*Q convention) via
# c[meV*Angstrom] = c[m/s] * hbar[meV*s] * 1e10[Angstrom/m], hbar = 6.582e-13 meV*s
_HBAR_MEV_S = 6.582119569e-13


def c_ms_to_meV_angstrom(c_ms: float) -> float:
    return c_ms * _HBAR_MEV_S * 1e10


# NOTE: the roton gap is conventionally quoted in the literature in Kelvin
# (Delta/k_B); values below are converted to meV via k_B = 0.08617333 meV/K.
# An earlier version of this table entered the Kelvin figures directly as
# "delta_meV", overstating Delta by a factor of ~11.6 -- caught before any
# fit was run against it (see M1_CHECKLIST.md).
_K_B_MEV_PER_K = 0.08617333262

REFERENCE_VALUES = {
    "cowley_woods_1971": {"c_ms": 238.0, "delta_K": 8.65, "q_m_angstrom": 1.92},
    "glyde_1998": {"c_ms": 239.0, "delta_K": 8.63, "q_m_angstrom": 1.91},
    "godfrin_2021": {"c_ms": 238.2, "delta_K": 8.64, "q_m_angstrom": 1.925},
}


@dataclass
class DispersionFitReport:
    phonon: PhononFitResult
    roton: RotonFitResult
    source: str
    tier: str


def select_phonon_region(data: SQwData, q_max: float = 0.4) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """Select the low-Q phonon-linear region (Q < q_max, default 0.4 Angstrom^-1).

    Caller is expected to pass omega already in energy units (meV) if S(Q,w)
    was recorded in frequency; this module treats `data.omega` as energy E.
    """
    mask = data.Q < q_max
    if not np.any(mask):
        raise ValueError(f"No points with Q < {q_max} found in {data.source}")
    return data.Q[mask], data.omega[mask], _sanitize_sigma(data.dS, mask)


def select_roton_region(
    data: SQwData, q_center: float = 1.9, half_width: float = 0.5
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """Select the region around the roton minimum (default 1.4-2.4 Angstrom^-1)."""
    mask = np.abs(data.Q - q_center) < half_width
    if not np.any(mask):
        raise ValueError(
            f"No points within {half_width} of Q={q_center} found in {data.source}"
        )
    return data.Q[mask], data.omega[mask], _sanitize_sigma(data.dS, mask)


def _sanitize_sigma(dS: np.ndarray | None, mask: np.ndarray) -> np.ndarray | None:
    """Return dS[mask], or None if that would contain any NaN.

    scipy.optimize.curve_fit's sigma parameter cannot handle partial NaNs
    (it does not error cleanly -- it silently returns garbage covariances).
    Some sources (e.g. adapters.godfrin_ancillary) report per-point
    uncertainty for only a sparse subset of rows, using NaN elsewhere as a
    documented "no estimate available" sentinel, not a corruption signal.
    Falling back to unweighted (sigma=None) fitting is the correct response
    to that sparsity, not an error.
    """
    if dS is None:
        return None
    sub = dS[mask]
    if np.any(np.isnan(sub)):
        return None
    return sub


def run_dispersion_fit(
    data: SQwData,
    phonon_q_max: float = 0.4,
    roton_q_center: float = 1.9,
    roton_half_width: float = 0.5,
) -> DispersionFitReport:
    """Full M1 workflow: select regions, fit both branches, return report."""
    Qp, Ep, dEp = select_phonon_region(data, q_max=phonon_q_max)
    phonon = fit_phonon_branch(Qp, Ep, dEp)

    Qr, Er, dEr = select_roton_region(data, q_center=roton_q_center, half_width=roton_half_width)
    roton = fit_roton_branch(Qr, Er, dEr)

    return DispersionFitReport(phonon=phonon, roton=roton, source=data.source, tier=data.tier)


def compare_to_literature(report: DispersionFitReport, reference: str = "godfrin_2021") -> dict:
    """Compute percent agreement between fitted (c, delta) and a literature entry.

    Returns dict with keys: c_lit_meV_angstrom, c_fit, c_pct_diff,
    delta_lit, delta_fit, delta_pct_diff, within_tolerance (bool, using
    PLAN.md M1 metrics: c within +/-5%, delta within +/-10%).
    """
    ref = REFERENCE_VALUES[reference]
    c_lit = c_ms_to_meV_angstrom(ref["c_ms"])
    delta_lit = ref["delta_K"] * _K_B_MEV_PER_K

    c_pct = 100.0 * abs(report.phonon.c - c_lit) / c_lit
    delta_pct = 100.0 * abs(report.roton.delta - delta_lit) / delta_lit

    return {
        "reference": reference,
        "c_lit_meV_angstrom": c_lit,
        "c_fit": report.phonon.c,
        "c_pct_diff": c_pct,
        "delta_lit": delta_lit,
        "delta_fit": report.roton.delta,
        "delta_pct_diff": delta_pct,
        # bool(...) avoids returning numpy.bool_, which json.dump() rejects
        # (report.phonon.c / report.roton.delta are numpy float64 from
        # curve_fit, so the comparisons above are numpy bool_ too).
        "within_tolerance": bool(c_pct <= 5.0 and delta_pct <= 10.0),
    }
