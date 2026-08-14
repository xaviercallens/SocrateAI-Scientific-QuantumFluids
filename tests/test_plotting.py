"""Tests for dispersion_fit.plotting.

Primarily a regression test: plot_dispersion_fit() used to recompute the
phonon/roton Q-masks with hardcoded thresholds (0.4, 0.5) instead of the
ones actually passed to run_dispersion_fit(), causing a scatter() size
mismatch whenever a caller used non-default region widths (found while
running the M1 digitized-Fig.5 pipeline with phonon_q_max=0.3).
"""

import numpy as np

from quantumfluids.adapters.ascii_sqw import SQwData
from quantumfluids.dispersion_fit.fit_dispersion import run_dispersion_fit
from quantumfluids.dispersion_fit.landau_model import phonon_branch, roton_branch
from quantumfluids.dispersion_fit.plotting import plot_dispersion_fit


def _synth_data(rng, c=1.5665, delta=0.7454, q_m=1.92, inv_two_mu=3.3):
    Qp = np.linspace(0.02, 0.4, 15)
    Ep = phonon_branch(Qp, c) + rng.normal(0, 0.01, 15)
    Qr = np.linspace(q_m - 0.4, q_m + 0.4, 15)
    Er = roton_branch(Qr, delta, q_m, inv_two_mu) + rng.normal(0, 0.02, 15)
    Q = np.concatenate([Qp, Qr])
    E = np.concatenate([Ep, Er])
    order = np.argsort(Q)
    return SQwData(Q=Q[order], omega=E[order], S=np.full(len(Q), np.nan),
                    dS=None, source="synthetic_plot_test", tier="C", meta={})


def test_plot_with_default_regions_does_not_raise(tmp_path):
    rng = np.random.default_rng(11)
    data = _synth_data(rng)
    report = run_dispersion_fit(data)
    out = str(tmp_path / "fit.png")
    plot_dispersion_fit(data, report, out)
    assert (tmp_path / "fit.png").exists()


def test_plot_with_nondefault_phonon_q_max_does_not_raise(tmp_path):
    """Regression test for the hardcoded-threshold size-mismatch bug."""
    rng = np.random.default_rng(11)
    data = _synth_data(rng)
    report = run_dispersion_fit(data, phonon_q_max=0.3, roton_half_width=0.35)
    out = str(tmp_path / "fit_narrow.png")
    plot_dispersion_fit(data, report, out, phonon_q_max=0.3, roton_half_width=0.35)
    assert (tmp_path / "fit_narrow.png").exists()
