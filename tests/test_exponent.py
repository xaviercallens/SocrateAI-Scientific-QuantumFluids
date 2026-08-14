"""Tier B harness for w4_shell_model.exponent.

The fitter is the instrument that produces the experiment's headline
number, so it is tested against KNOWN power laws where the right answer is
independently computable -- a fitter validated only on real data would be
unfalsifiable, since the real answer is what we are trying to measure.

Negative controls (LL-2) establish that the fitter and the inclusion
criterion both REJECT what they are supposed to reject.
"""

import numpy as np
import pytest

from quantumfluids.w4_shell_model.exponent import (
    DT_REFINEMENT_TOL,
    ExponentFit,
    SweepPoint,
    SweepResult,
    fit_loglog,
    refine_and_check,
    run_sweep,
)


# =====================================================================
# The fitter against known power laws
# =====================================================================

@pytest.mark.parametrize("true_beta", [-2.0 / 3.0, -1.0, 0.0, 0.5, 2.0])
def test_recovers_exact_power_law(true_beta):
    """Noiseless y = p^beta must be recovered to machine precision, with
    r^2 == 1. Includes -2/3, the value OP2_LITE pre-registers as its
    no-effect threshold."""
    p = np.array([1e-4, 1e-3, 1e-2, 1e-1, 1.0])
    y = p**true_beta
    fit = fit_loglog(p, y, "sum")
    assert fit.beta == pytest.approx(true_beta, abs=1e-12)
    assert fit.r_squared == pytest.approx(1.0, abs=1e-12)


def test_confidence_interval_brackets_the_truth_under_noise():
    """With multiplicative noise the 95% CI must still contain the true
    exponent, and must be non-degenerate."""
    rng = np.random.default_rng(20260814)
    p = np.geomspace(1e-4, 1.0, 12)
    true_beta = -2.0 / 3.0
    y = p**true_beta * np.exp(rng.normal(0, 0.02, len(p)))
    fit = fit_loglog(p, y, "sum")
    assert fit.ci95_low < true_beta < fit.ci95_high
    assert fit.ci95_high > fit.ci95_low


def test_noise_widens_the_interval():
    """A CI that ignored scatter would make two betas look distinguishable
    when they are not -- the failure mode that matters for this experiment."""
    rng = np.random.default_rng(1)
    p = np.geomspace(1e-4, 1.0, 12)
    quiet = fit_loglog(p, p**-0.5 * np.exp(rng.normal(0, 0.005, len(p))), "sum")
    noisy = fit_loglog(p, p**-0.5 * np.exp(rng.normal(0, 0.20, len(p))), "sum")
    assert (noisy.ci95_high - noisy.ci95_low) > (quiet.ci95_high - quiet.ci95_low)


def test_non_power_law_gives_poor_r_squared():
    """r^2 is the guard against reporting a slope for data that is not a
    power law at all."""
    p = np.geomspace(1e-3, 1.0, 10)
    y = np.sin(10 * p) + 2.0  # positive, but nothing like a power law
    assert fit_loglog(p, y, "sum").r_squared < 0.9


# =====================================================================
# NEGATIVE CONTROLS on the fitter
# =====================================================================

def test_rejects_fewer_than_three_points():
    """Two points give a zero-residual slope with no CI; a beta without an
    interval cannot be compared against another beta."""
    with pytest.raises(ValueError, match="at least 3 points"):
        fit_loglog(np.array([1.0, 2.0]), np.array([1.0, 4.0]), "sum")


def test_rejects_nonpositive_values():
    with pytest.raises(ValueError, match="strictly positive"):
        fit_loglog(np.array([1.0, 2.0, 3.0]), np.array([1.0, 0.0, 3.0]), "sum")


def test_rejects_nonpositive_params():
    with pytest.raises(ValueError, match="strictly positive"):
        fit_loglog(np.array([0.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]), "sum")


def test_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="shape mismatch"):
        fit_loglog(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0]), "sum")


def test_rejects_constant_parameter():
    """No slope is defined against a constant x."""
    with pytest.raises(ValueError, match="constant parameter"):
        fit_loglog(np.array([2.0, 2.0, 2.0]), np.array([1.0, 2.0, 3.0]), "sum")


def test_flat_response_gives_beta_zero_not_nan():
    """beta = 0 is the memo's pre-registered 'cutoff mechanism is irrelevant'
    outcome -- explicitly a useful negative result, not a failure. scipy's
    rvalue is 0/0 = nan for an exactly constant response, so returning nan
    for the single most consequential possible result would be a defect.
    """
    fit = fit_loglog(np.geomspace(1e-3, 1.0, 5), np.full(5, 7.25), "sum")
    assert fit.beta == 0.0
    assert not np.isnan(fit.r_squared)
    assert fit.r_squared == 1.0
    assert fit.ci95_low == 0.0 and fit.ci95_high == 0.0


# =====================================================================
# The dt-refinement inclusion criterion
# =====================================================================

def test_refinement_accepts_a_converged_configuration():
    """A well-resolved run must survive halving dt."""
    *_, ok, why = refine_and_check(N=4, nu=0.1, D=0.0, profile="P3", t_horizon=0.5)
    assert ok, f"a converged configuration was excluded: {why}"


def test_refinement_reports_both_conventions():
    cs, cm, fs, fm, ok, _ = refine_and_check(N=4, nu=0.1, D=0.0, profile="P3", t_horizon=0.5)
    for v in (cs, cm, fs, fm):
        assert np.isfinite(v) and v > 0


def test_refinement_excludes_a_diverged_configuration():
    """NEGATIVE CONTROL: a run that fails must be excluded WITH a reason,
    never silently admitted to the fit."""
    *_, ok, why = refine_and_check(N=4, nu=0.0, D=0.0, profile="P1",
                                   t_horizon=1.0, max_steps=5)
    assert not ok
    assert why, "an excluded configuration must carry a stated reason"


# =====================================================================
# Sweep bookkeeping
# =====================================================================

def test_sweep_fits_both_conventions():
    res = run_sweep("viscous", [0.4, 0.3, 0.2, 0.15], N=4, profile="P3", t_horizon=0.5)
    assert res.fit_sum is not None and res.fit_max is not None
    assert res.fit_sum.convention == "sum"
    assert res.fit_max.convention == "max"


def test_sweep_reports_exclusions_with_a_count():
    """Memo §6: exclusions are reported with their count, never dropped."""
    res = run_sweep("viscous", [0.4, 0.3, 0.2], N=4, profile="P3", t_horizon=0.5)
    report = res.exclusion_report()
    assert str(len(res.points)) in report
    assert res.n_excluded == sum(1 for p in res.points if not p.included)


def test_sweep_leaves_fits_none_when_too_few_points_survive():
    """Rather than fitting a slope through 2 points and reporting it."""
    res = run_sweep("viscous", [0.4, 0.3], N=4, profile="P3", t_horizon=0.5)
    assert res.fit_sum is None and res.fit_max is None


def test_truncation_sweep_records_exact_alpha_prime():
    """alpha' = 4^-N is exact for truncation and is the ONLY regulator for
    which the memo's alpha' axis is unambiguous (see O6)."""
    res = run_sweep("truncation", [3, 4], N=0, profile="P3", t_horizon=0.2)
    for p in res.points:
        assert p.alpha_prime == pytest.approx(4.0 ** (-int(p.param)))


def test_diffusivity_sweeps_record_no_alpha_prime():
    """Honesty guard for O6: nu and D sweeps must NOT silently invent an
    alpha' value, since the diffusivity->length^2 conversion is unresolved."""
    res = run_sweep("dispersive", [0.3, 0.2], N=4, profile="P3", t_horizon=0.3)
    assert all(p.alpha_prime is None for p in res.points)


def test_rejects_unknown_regulator():
    with pytest.raises(ValueError, match="unknown regulator"):
        run_sweep("bounce", [0.1, 0.2, 0.3], N=4)


def test_pre_registered_tolerance_is_one_percent():
    """Pinned so a later edit that loosens it is visible in a diff."""
    assert DT_REFINEMENT_TOL == 0.01
