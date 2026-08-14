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


_K_B_MEV_PER_K = 0.08617333262  # retained: some literature quotes Delta in Kelvin

# ---------------------------------------------------------------------------
# CORRECTED 2026-08-14 -- see LL-10. The previous version of this table was a
# DEFECT: it carried values recalled from memory and attributed them to
# "cowley_woods_1971" and "glyde_1998", neither of which reports the Landau
# triple at all:
#
#   Cowley & Woods, Can. J. Phys. 49, 177 (1971) -- verified to exist
#     (DOI 10.1139/p71-021) but is a broad inelastic-scattering study;
#     Godfrin et al. (2021) explicitly EXCLUDE it from their Table IV of
#     zero-pressure roton parameters. The values previously attributed to it
#     appear to belong to Henshaw & Woods (1961) instead.
#   Glyde et al., EPL 43, 422 (1998) -- verified to exist
#     (DOI 10.1209/epl/i1998-00375-2) but measures 2.0 <= Q <= 4.0 A^-1,
#     entirely BEYOND the roton with no phonon region, so it cannot report a
#     sound velocity and reports no numerical Delta or Q_m.
#
# Both are removed as sources of Landau parameters. The entries below are
# taken from Table IV of Godfrin et al. (2021) [LIT-002], which compiles
# independent P=0 determinations, and are quoted natively in meV (no Kelvin
# conversion, removing a whole class of unit error).
#
# Cross-checked first-hand and independently: the roton minimum of that
# paper's own published dispersion table (the ancillary file this repo caches
# under data/external/godfrin_2021_arxiv_ancillary/) sits at E = 0.7413 meV,
# Q = 1.9200 A^-1, consistent with the tabulated Delta_R / k_R below to within
# their stated uncertainties.
# ---------------------------------------------------------------------------

# Sound velocity at SVP. NOTE this is not a neutron-scattering result: it is
# an ultrasonic measurement (Abraham et al.), quoted by Godfrin et al. Only
# one value is listed because the Table IV compilation is of ROTON parameters;
# the papers there do not each redetermine c.
C_SVP_MS = 238.3          # +/- 0.1 m/s
C_SVP_MS_ERR = 0.1

# Independent P = 0 roton-parameter determinations, Godfrin et al. (2021)
# Table IV. delta_meV = roton gap Delta_R; q_m = roton wavevector k_R.
REFERENCE_VALUES = {
    "godfrin_2021": {
        "c_ms": C_SVP_MS, "delta_meV": 0.7418, "delta_err": 0.0010,
        "q_m_angstrom": 1.918, "q_m_err": 0.002,
        "note": "Table III/IV, P=0. CAVEAT: their Delta_R at P=0 is itself "
                "taken from Stirling as an energy-calibration input, so it is "
                "NOT an independent determination -- see CLAIM-003's caveat.",
    },
    "woods_1977": {
        "c_ms": C_SVP_MS, "delta_meV": 0.7426, "delta_err": 0.0010,
        "q_m_angstrom": 1.926, "q_m_err": 0.005,
        "note": "Godfrin et al. 2021 Table IV compilation entry.",
    },
    "stirling": {
        "c_ms": C_SVP_MS, "delta_meV": 0.7418, "delta_err": 0.0010,
        "q_m_angstrom": 1.920, "q_m_err": 0.002,
        "note": "Godfrin et al. 2021 Table IV compilation entry.",
    },
    "andersen": {
        "c_ms": C_SVP_MS, "delta_meV": 0.743, "delta_err": 0.001,
        "q_m_angstrom": 1.931, "q_m_err": 0.003,
        "note": "Godfrin et al. 2021 Table IV compilation entry.",
    },
    "gibbs_1999": {
        "c_ms": C_SVP_MS, "delta_meV": 0.7426, "delta_err": 0.0021,
        "q_m_angstrom": 1.929, "q_m_err": 0.002,
        "note": "Godfrin et al. 2021 Table IV compilation entry.",
    },
    "pearce_2001": {
        "c_ms": C_SVP_MS, "delta_meV": 0.7440, "delta_err": 0.0020,
        "q_m_angstrom": 1.926, "q_m_err": None,
        "note": "Godfrin et al. 2021 Table IV compilation entry.",
    },
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
    delta_lit = ref["delta_meV"]

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
