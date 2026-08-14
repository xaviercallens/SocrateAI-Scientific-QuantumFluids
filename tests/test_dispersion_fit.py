"""Tests for dispersion_fit — synthetic-data recovery + integration with adapters.

Strategy: generate synthetic S(Q,omega) with KNOWN Landau parameters
(c, Delta, Q_m), add small Gaussian noise, fit, and assert the fit recovers
the known parameters within a tight tolerance. This validates the fitting
math independent of the M1-DATA-001 access-pathway question (works with
Tier B or Tier C data equally, per M1_CHECKLIST.md Phase 3).
"""

import numpy as np
import pytest

from quantumfluids.adapters.ascii_sqw import AsciiFormatError, load_ascii_sqw, SQwData
from quantumfluids.dispersion_fit.fit_dispersion import (
    compare_to_literature,
    run_dispersion_fit,
    select_phonon_region,
    select_roton_region,
)
from quantumfluids.dispersion_fit.landau_model import (
    fit_phonon_branch,
    fit_roton_branch,
    phonon_branch,
    roton_branch,
)

# Known "true" parameters, literature-typical (LITERATURE_LEDGER.md).
TRUE_C = 0.16  # meV*Angstrom (~ 240 m/s converted)
TRUE_DELTA = 8.65
TRUE_QM = 1.92
TRUE_INV_TWO_MU = 5.0


def synth_phonon(rng, n=20, q_max=0.4, noise=0.001):
    Q = np.linspace(0.02, q_max, n)
    E = phonon_branch(Q, TRUE_C) + rng.normal(0, noise, n)
    return Q, E


def synth_roton(rng, n=20, half_width=0.4, noise=0.02):
    Q = np.linspace(TRUE_QM - half_width, TRUE_QM + half_width, n)
    E = roton_branch(Q, TRUE_DELTA, TRUE_QM, TRUE_INV_TWO_MU) + rng.normal(0, noise, n)
    return Q, E


# --- Landau model fit recovery (happy path) ------------------------------

def test_phonon_fit_recovers_known_c():
    rng = np.random.default_rng(42)
    Q, E = synth_phonon(rng)
    result = fit_phonon_branch(Q, E)
    assert abs(result.c - TRUE_C) / TRUE_C < 0.05  # within 5%, M1 metric


def test_roton_fit_recovers_known_delta_and_qm():
    rng = np.random.default_rng(42)
    Q, E = synth_roton(rng)
    result = fit_roton_branch(Q, E)
    assert abs(result.delta - TRUE_DELTA) / TRUE_DELTA < 0.10  # within 10%, M1 metric
    assert abs(result.q_m - TRUE_QM) / TRUE_QM < 0.05


def test_roton_fit_effective_mass_positive():
    rng = np.random.default_rng(1)
    Q, E = synth_roton(rng)
    result = fit_roton_branch(Q, E)
    assert result.effective_mass_amu() > 0


# --- Negative controls (LL-2) --------------------------------------------

def test_phonon_fit_rejects_too_few_points():
    with pytest.raises(ValueError, match="at least 2"):
        fit_phonon_branch(np.array([0.1]), np.array([0.02]))


def test_roton_fit_rejects_too_few_points():
    with pytest.raises(ValueError, match="at least 4"):
        fit_roton_branch(np.array([1.8, 1.9, 2.0]), np.array([8.6, 8.5, 8.7]))


# --- End-to-end via SQwData / adapters ------------------------------------

def _synth_sqw_data(rng, source="synthetic_test") -> SQwData:
    Qp, Ep = synth_phonon(rng, n=15)
    Qr, Er = synth_roton(rng, n=15)
    Q = np.concatenate([Qp, Qr])
    E = np.concatenate([Ep, Er])
    order = np.argsort(Q)
    return SQwData(Q=Q[order], omega=E[order], S=np.full(len(Q), np.nan),
                    dS=None, source=source, tier="C", meta={})


def test_run_dispersion_fit_end_to_end():
    rng = np.random.default_rng(7)
    data = _synth_sqw_data(rng)
    report = run_dispersion_fit(data)
    assert abs(report.phonon.c - TRUE_C) / TRUE_C < 0.05
    assert abs(report.roton.delta - TRUE_DELTA) / TRUE_DELTA < 0.10


def test_select_phonon_region_rejects_empty_selection():
    rng = np.random.default_rng(7)
    data = _synth_sqw_data(rng)
    with pytest.raises(ValueError, match="No points"):
        select_phonon_region(data, q_max=-1.0)  # impossible mask


def test_select_roton_region_rejects_empty_selection():
    rng = np.random.default_rng(7)
    data = _synth_sqw_data(rng)
    with pytest.raises(ValueError, match="No points"):
        select_roton_region(data, q_center=99.0, half_width=0.01)


def test_compare_to_literature_flags_tolerance():
    rng = np.random.default_rng(7)
    data = _synth_sqw_data(rng)
    report = run_dispersion_fit(data)
    comparison = compare_to_literature(report, reference="godfrin_2021")
    assert "within_tolerance" in comparison
    assert comparison["c_pct_diff"] >= 0
    assert comparison["delta_pct_diff"] >= 0


# --- Full pipeline through the ASCII adapter (adapter -> fit integration) -

def test_pipeline_from_ascii_file(tmp_path):
    rng = np.random.default_rng(3)
    Qp, Ep = synth_phonon(rng, n=15)
    Qr, Er = synth_roton(rng, n=15)
    Q = np.concatenate([Qp, Qr])
    E = np.concatenate([Ep, Er])
    order = np.argsort(Q)
    Q, E = Q[order], E[order]

    lines = "\n".join(f"{q:.6f} {e:.6f}" for q, e in zip(Q, E))
    path = tmp_path / "synthetic_sqw.txt"
    path.write_text(lines + "\n")

    data = load_ascii_sqw(str(path))
    report = run_dispersion_fit(data)
    assert abs(report.phonon.c - TRUE_C) / TRUE_C < 0.05
    assert abs(report.roton.delta - TRUE_DELTA) / TRUE_DELTA < 0.10
