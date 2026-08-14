"""Tier B harness for w4_shell_model.observable.

The point of this file is the SAMPLING-ADEQUACY negative controls. The
first-peak observable was adopted because it converges in the horizon where
sup_t Omega does not (O7), but it carries its own hazard: the detector is
sensitive to how finely the trajectory is sampled, and an undersampled
trace silently yields a DIFFERENT, later peak. Measured on the real model
at N=4, D=0.02, that error is +11%. A guard that has never been shown to
fire is not a guard.
"""

import numpy as np
import pytest

from quantumfluids.w4_shell_model.integrate import integrate
from quantumfluids.w4_shell_model.observable import (
    MIN_RISE,
    SAMPLING_TOL,
    check_sampling_adequacy,
    first_peak,
)


# =====================================================================
# Detection on synthetic traces where the answer is known exactly
# =====================================================================

def test_finds_the_first_peak_not_the_global_one():
    """Decisive: a later, HIGHER maximum must not be returned. This is
    exactly what an undersampled detector does wrong."""
    t = np.linspace(0, 10, 1001)
    y = np.exp(-((t - 2) ** 2)) + 3.0 * np.exp(-((t - 7) ** 2)) + 0.01
    res = first_peak(t, y)
    assert res.t_peak == pytest.approx(2.0, abs=0.05)
    assert res.value < 1.5, "returned the global maximum instead of the first peak"


def test_peak_value_and_time_are_consistent():
    t = np.linspace(0, 5, 501)
    y = np.sin(t) + 2.0
    res = first_peak(t, y)
    assert res.t_peak == pytest.approx(np.pi / 2, abs=0.05)
    assert res.value == pytest.approx(3.0, abs=0.01)
    assert y[res.index] == res.value


# =====================================================================
# NEGATIVE CONTROLS -- the guard must actually fire
# =====================================================================

def test_monotonic_trace_is_rejected_not_silently_endpointed():
    """A run whose horizon does not contain the peak must RAISE, not return
    Omega at the end of the run dressed up as a peak."""
    t = np.linspace(0, 5, 101)
    with pytest.raises(ValueError, match="no interior local maximum"):
        first_peak(t, np.exp(t))


def test_too_short_trace_rejected():
    with pytest.raises(ValueError, match="at least 3 trace samples"):
        first_peak(np.array([0.0, 1.0]), np.array([1.0, 2.0]))


def test_mismatched_shapes_rejected():
    with pytest.raises(ValueError, match="shape mismatch"):
        first_peak(np.zeros(5), np.zeros(6))


@pytest.mark.parametrize("spike_idx", [20, 21])
def test_sampling_guard_fires_on_a_trace_that_hides_its_first_peak(spike_idx):
    """NEGATIVE CONTROL: a trace whose first peak is a single narrow sample
    is not adequately resolved, and the guard must say so.

    Parametrised over an EVEN and an ODD spike index deliberately. An
    earlier version of the guard subsampled only as y[::2], which preserves
    even indices -- so it passed on the even case and had a parity blind
    spot. Both phases are now checked; this test would catch a regression
    to the one-phase version.
    """
    t = np.linspace(0, 10, 201)
    y = np.full_like(t, 1.0)
    y[spike_idx] = 5.0
    y[100:121] += 8.0 * np.exp(-((t[100:121] - 6.0) ** 2))  # broad later peak
    res = first_peak(t, y)
    assert res.value == pytest.approx(5.0)          # fine trace finds the spike
    assert not res.sampling_ok, (
        f"sampling guard did not fire for a single-sample first peak at index "
        f"{spike_idx} -- the guard has no detection power at this parity"
    )
    assert res.reason


def test_sampling_guard_passes_on_a_well_resolved_trace():
    t = np.linspace(0, 5, 2001)
    res = first_peak(t, np.sin(t) + 2.0)
    assert res.sampling_ok
    assert res.sampling_rel_change < SAMPLING_TOL


def test_check_sampling_adequacy_reports_when_subsample_has_no_peak():
    y = np.array([1.0, 5.0, 1.0, 1.0, 1.0])
    ok, rel, why = check_sampling_adequacy(y, 1)
    assert not ok
    assert "cannot be established" in why or "no detectable peak" in why


# =====================================================================
# On the real model -- the property that motivated the switch
# =====================================================================

def test_first_peak_is_horizon_independent_for_the_dispersive_regulator():
    """The whole reason for this observable: unlike sup_t Omega (O7), it must
    not move when the horizon is extended."""
    vals = []
    for T in (4.0, 8.0, 16.0):
        r = integrate(N=4, nu=0.0, D=0.02, profile="P3", t_horizon=T, trace_every=1)
        vals.append(first_peak(r.trace_t, r.trace_omega_sum).value)
    assert max(vals) - min(vals) < 1e-9 * max(vals), (
        f"first-peak value moved with the horizon: {vals} -- it inherits the "
        f"O7 defect it was adopted to fix"
    )


def test_first_peak_is_horizon_independent_for_the_viscous_regulator():
    vals = []
    for T in (4.0, 8.0, 16.0):
        r = integrate(N=4, nu=0.02, D=0.0, profile="P3", t_horizon=T, trace_every=1)
        vals.append(first_peak(r.trace_t, r.trace_omega_sum).value)
    assert max(vals) - min(vals) < 1e-9 * max(vals)


def test_sup_omega_by_contrast_is_NOT_horizon_independent():
    """Pins the O7 finding itself, so a future change that accidentally
    'fixes' sup_t Omega would surface here rather than silently."""
    sups = []
    for T in (4.0, 16.0, 64.0):
        r = integrate(N=4, nu=0.0, D=0.02, profile="P3", t_horizon=T)
        sups.append(r.sup_enstrophy_sum)
    assert sups[-1] > sups[0] * 1.2, (
        "sup_t Omega no longer grows with the horizon for a dispersive "
        "regulator; O7 may need revisiting"
    )


def test_real_model_trace_passes_the_sampling_guard_at_trace_every_one():
    """Production setting must be adequate, or the guard is unusable."""
    r = integrate(N=4, nu=0.0, D=0.02, profile="P3", t_horizon=8.0, trace_every=1)
    assert first_peak(r.trace_t, r.trace_omega_sum).sampling_ok


# =====================================================================
# Minimum-rise criterion (MIN_RISE) -- the overdamped-degenerate guard
# =====================================================================

def test_rejects_a_peak_that_is_really_the_initial_condition():
    """NEGATIVE CONTROL for MIN_RISE. A trace that ticks up microscopically
    and then declines has a genuine local maximum, but its value IS Omega(0).
    Measured on the real model at N=4, nu=0.3: a rise of 0.0025%."""
    t = np.linspace(0, 5, 501)
    y = np.full_like(t, 1.0)
    y[:6] = [1.0, 1.000010, 1.000018, 1.000025, 1.000020, 1.000008]  # tick up, turn over
    y[6:] = 1.0 - 0.1 * t[6:]                                        # then decline
    res_rise = (y[3] - y[0]) / y[0]
    assert res_rise < 1e-4, "test fixture must have a microscopic rise"
    with pytest.raises(ValueError, match="rises only"):
        first_peak(t, y)


def test_accepts_a_peak_with_a_genuine_rise():
    t = np.linspace(0, 5, 501)
    y = 1.0 + 3.0 * np.exp(-((t - 1.0) ** 2))
    res = first_peak(t, y)
    assert res.rise > MIN_RISE
    assert res.value == pytest.approx(4.0, abs=0.01)


def test_min_rise_is_configurable_for_sensitivity_checks():
    """The threshold is pre-registered but its influence must be checkable."""
    t = np.linspace(0, 5, 501)
    # Narrow enough that y(0) is essentially 1.0, so the rise really is ~5%
    # (an earlier version used a wide Gaussian whose y(0) was already 1.018,
    # making the true rise 3.1% -- the fixture, not the code, was wrong).
    y = 1.0 + 0.05 * np.exp(-((t - 1.0) ** 2) / 0.01)
    assert y[0] == pytest.approx(1.0, abs=1e-6)
    with pytest.raises(ValueError, match="rises only"):
        first_peak(t, y)                            # default 10% -> rejected
    assert first_peak(t, y, min_rise=0.01).rise == pytest.approx(0.05, abs=1e-3)


def test_overdamped_real_run_is_rejected():
    """On the actual model, not a synthetic trace."""
    r = integrate(N=4, nu=0.3, D=0.0, profile="P3", t_horizon=4.0, trace_every=1)
    with pytest.raises(ValueError, match="rises only"):
        first_peak(r.trace_t, r.trace_omega_sum)


def test_pre_registered_min_rise_is_ten_percent():
    """Pinned so a later edit that loosens it is visible in a diff."""
    assert MIN_RISE == 0.10
