"""Tier B harness for w4_shell_model.integrate.

Small N and short horizons throughout, so the suite stays fast; the
full-scale comparison against MechanicaFluidorum is Positive Control #1 and
lives in exploration/ (it takes minutes, not milliseconds).

The load-bearing test here is
test_pure_dispersion_conserves_energy_under_integration: the energy-neutrality
of -i D k^2 a is an algebraic property of a single RHS evaluation, but what
the experiment actually depends on is that it survives INTEGRATION. A
dispersive regulator that quietly leaked energy over 10^4 RK4 steps would
produce a beta difference caused by leakage rather than by dispersion --
the exact confound OP2_LITE flags for its Candidate A.
"""

import numpy as np
import pytest

from quantumfluids.w4_shell_model.integrate import (
    PROFILES,
    integrate,
    make_profile,
    step_size,
)


# =====================================================================
# Step size -- must reduce exactly to MechanicaFluidorum's rule at D=0
# =====================================================================

@pytest.mark.parametrize("N,nu", [(8, 0.1), (8, 0.01), (12, 0.001), (4, 1.0)])
def test_step_size_matches_mechanicafluidorum_rule_at_D_zero(N, nu):
    """dt = 0.1 / (nu*k_N^2 + k_N). Required for Positive Control #1 to be
    a like-for-like comparison."""
    k_N = 2.0**N
    assert step_size(N, nu, D=0.0) == pytest.approx(0.1 / (nu * k_N * k_N + k_N), rel=1e-15)


def test_step_size_shrinks_when_D_added():
    """The dispersive term contributes stiffness of the same order, so it
    must tighten dt, not be ignored."""
    assert step_size(8, 0.01, D=0.1) < step_size(8, 0.01, D=0.0)


# =====================================================================
# Profiles
# =====================================================================

@pytest.mark.parametrize("name", PROFILES)
def test_profiles_are_real_and_right_length(name):
    a = make_profile(name, 6)
    assert a.shape == (7,)
    assert not np.iscomplexobj(a), "profiles must start real -- that is what exercises the invariant subspace"


def test_profile_P2_is_geometric():
    assert make_profile("P2", 4) == pytest.approx(np.array([1.0, 0.5, 0.25, 0.125, 0.0625]))


def test_unknown_profile_rejected():
    with pytest.raises(ValueError, match="unknown profile"):
        make_profile("P9", 4)


# =====================================================================
# Energy behaviour under integration
# =====================================================================

def test_viscosity_dissipates_energy_under_integration():
    run = integrate(N=5, nu=0.5, D=0.0, profile="P2", t_horizon=0.5)
    assert run.status == "OK"
    assert run.energy_final < run.energy_initial


def test_pure_dispersion_conserves_energy_under_integration():
    """THE key test: -i D k^2 a must be energy-neutral over many steps, not
    just per-RHS-evaluation. Residual drift here is RK4 truncation error,
    which shrinks with dt (see the companion test below), NOT leakage."""
    run = integrate(N=5, nu=0.0, D=0.2, profile="P2", t_horizon=0.5)
    assert run.status == "OK"
    rel_drift = abs(run.energy_final - run.energy_initial) / run.energy_initial
    assert rel_drift < 1e-6, f"pure dispersion leaked energy: relative drift {rel_drift:.3e}"


def test_dispersive_energy_drift_shrinks_with_timestep():
    """Confirms the residual drift above is integrator truncation error and
    not a genuine leak in the model: halving dt must reduce it."""
    kw = dict(N=5, nu=0.0, D=0.2, profile="P2", t_horizon=0.2)
    coarse = integrate(**kw, dt=1e-4)
    fine = integrate(**kw, dt=5e-5)
    d_coarse = abs(coarse.energy_final - coarse.energy_initial)
    d_fine = abs(fine.energy_final - fine.energy_initial)
    assert d_fine < d_coarse, (
        f"energy drift did not shrink with dt ({d_coarse:.3e} -> {d_fine:.3e}); "
        f"this indicates a real leak rather than truncation error"
    )


def test_inviscid_undispersed_conserves_energy_over_short_horizon():
    """nu = D = 0: the nonlinearity alone conserves energy. Short horizon
    only -- this is the regime where Katz-Pavlovic proves blow-up."""
    run = integrate(N=5, nu=0.0, D=0.0, profile="P2", t_horizon=0.2)
    rel = abs(run.energy_final - run.energy_initial) / run.energy_initial
    assert rel < 1e-8, f"conservative model drifted by {rel:.3e}"


# =====================================================================
# The invariant subspace, integrated (memo §2c(i), §6)
# =====================================================================

def test_reality_preserved_through_integration_at_D_zero():
    """Must hold to the last bit: it is what makes the D=0 run identical to
    MechanicaFluidorum's real-valued one, and keeps the O5 trap alive."""
    run = integrate(N=5, nu=0.01, D=0.0, profile="P3", t_horizon=0.3)
    assert run.max_abs_imag == 0.0


def test_dispersion_takes_the_state_out_of_the_reals():
    run = integrate(N=5, nu=0.0, D=0.2, profile="P3", t_horizon=0.3)
    assert run.max_abs_imag > 0.0


# =====================================================================
# Both enstrophy conventions (audit ruling O1)
# =====================================================================

def test_both_enstrophy_conventions_recorded_and_ordered():
    run = integrate(N=6, nu=0.05, D=0.0, profile="P2", t_horizon=0.3)
    assert run.sup_enstrophy_sum >= run.sup_enstrophy_max
    row = run.as_row()
    assert "sup_Omega_sum" in row and "sup_Omega_max" in row


def test_the_two_conventions_genuinely_differ():
    """If they ever coincided, O1's 'record both' would be vacuous."""
    run = integrate(N=6, nu=0.05, D=0.0, profile="P2", t_horizon=0.3)
    assert run.sup_enstrophy_sum > run.sup_enstrophy_max * 1.01


# =====================================================================
# Guards -- refuse rather than silently mislead
# =====================================================================

def test_max_steps_raises_rather_than_truncating():
    """A sup_Omega measured over a sliver of the horizon is worse than no
    number; the runner must refuse, not quietly return one."""
    with pytest.raises(ValueError, match="Refusing to run"):
        integrate(N=16, nu=0.1, D=0.0, profile="P1", max_steps=1000)


# =====================================================================
# Boundedness of the TRUNCATED inviscid model -- design memo ERRATUM E1
#
# These replace an earlier test that asserted the truncated inviscid model
# "must blow up", accepting either outcome and therefore asserting nothing.
# It cannot blow up: energy conservation bounds every amplitude by sqrt(2E),
# hence Omega by k_N^2 * E. Katz-Pavlovic blow-up is a statement about the
# INFINITE system. Getting this wrong would have made the memo's O5
# falsification trap unfireable.
# =====================================================================

def test_truncated_inviscid_model_stays_bounded():
    """No finite-time blow-up with finitely many shells, however long we run."""
    run = integrate(N=6, nu=0.0, D=0.0, profile="P3", t_horizon=40.0, dt=1e-3)
    assert run.status == "OK", "truncated inviscid model diverged -- it cannot"
    assert run.t_stop == pytest.approx(40.0)


def test_amplitudes_respect_the_sqrt_2E_bound():
    """|a_n| <= sqrt(2E) for all n,t -- the bound that forbids blow-up."""
    run = integrate(N=6, nu=0.0, D=0.0, profile="P3", t_horizon=40.0, dt=1e-3)
    bound = np.sqrt(2.0 * run.energy_initial)
    assert run.sup_abs_amplitude <= bound * (1 + 1e-6), (
        f"sup|a| = {run.sup_abs_amplitude:.6f} exceeded sqrt(2E) = {bound:.6f}"
    )


def test_enstrophy_respects_the_kN_squared_energy_bound():
    """Omega <= k_N^2 * E, the consequence of the amplitude bound."""
    run = integrate(N=6, nu=0.0, D=0.0, profile="P3", t_horizon=40.0, dt=1e-3)
    bound = (2.0**6) ** 2 * run.energy_initial
    assert run.sup_enstrophy_sum <= bound * (1 + 1e-6)


def test_the_bound_also_holds_under_pure_dispersion():
    """Dispersion is energy-neutral, so the same bound applies at nu=0, D>0.
    If it did not, the dispersive term would be secretly injecting energy."""
    run = integrate(N=6, nu=0.0, D=0.1, profile="P3", t_horizon=5.0, dt=1e-4)
    bound = np.sqrt(2.0 * run.energy_initial)
    assert run.sup_abs_amplitude <= bound * (1 + 1e-6)


def test_divergence_guard_trips_on_numerical_instability():
    """The guard's real job: catching an RK4 instability from too large a dt,
    which IS reachable (unlike blow-up). Uses a deliberately reckless step."""
    run = integrate(N=8, nu=0.0, D=0.0, profile="P1", t_horizon=50.0, dt=0.5)
    assert run.status == "DIVERGED", (
        "an absurdly large dt did not trip the divergence guard; the guard "
        "cannot be relied on to catch integrator instability"
    )
    assert run.t_stop < 50.0
