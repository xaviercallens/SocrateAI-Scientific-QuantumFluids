"""Pins for src/quantumfluids/kinetic (pre-registration docs/designs/KINETIC_TDA_PREREG.md).

Each test is either a known answer or a failure mode the project actually hit."""
import numpy as np
import pytest

from quantumfluids.kinetic import vlasov as V
from quantumfluids.kinetic.dispersion import certify, landau_root


def test_landau_root_is_certified_and_matches_canosa():
    r = landau_root(0.5, 1.4156 - 0.1533j)
    assert r.certified
    assert abs(r.omega_r - 1.415661888604536) < 1e-14
    assert abs(r.gamma - (-0.153359466909605)) < 1e-14      # Canosa (1973): -0.15336


def test_certification_rejects_a_wrong_root():
    """A checker that has never been seen to reject is not yet a checker."""
    assert not certify(1.4156 - 0.1433j, 1e-3, 0.5).certified
    assert certify(1.415661888604536 - 0.153359466909605j, 1e-3, 0.5).certified


def test_two_stream_root_is_purely_growing():
    r = landau_root(0.2, 0.2j, beams=((0.5, 2.4), (0.5, -2.4)))
    assert r.certified and abs(r.omega_r) < 1e-30 and r.gamma > 0


def _landau(nv, t_end, field_on=True, k=0.5):
    g = V.Grid(L=2 * np.pi / k, nx=32, nv=nv, vmax=6.0)
    f = V.pulse(np.tile(V.maxwellian(g.v), (g.nx, 1)), g, 1, 0.01)
    obs = lambda t, f: (t, abs(V.mode_amplitude(V.density(f, g), 1)), abs(V.mode_amplitude(V.field_from(f, g), 1)))
    f, out = V.run(f, g, 0.1, t_end, obs, field_on=field_on)
    return (g,) + tuple(map(np.array, zip(*out)))


def test_landau_damping_rate_matches_certified_root():
    g, t, rho, E = _landau(128, 25.0)
    rate, omega, _ = V.peak_fit(t, E, 5, 25)
    r = landau_root(0.5, 1.4156 - 0.1533j)
    assert abs(rate - r.gamma) / abs(r.gamma) < 0.02
    assert abs(omega - r.omega_r) / r.omega_r < 0.01


def test_recurrence_free_streaming_is_exact_and_field_shifts_it():
    """Pre-registered Run C FAILED: T_R = 2 pi/(k dv) is the recurrence time of FREE STREAMING (exact, amplitude
    ratio 1); with the self-consistent field the largest maximum lags it.  Both facts pinned."""
    g, t, rho, E = _landau(32, 45.0, field_on=False)
    TR = g.recurrence_time(1)
    w = (t > 25) & (t < 45)
    assert abs(t[w][np.argmax(rho[w])] - TR) <= 0.1
    assert rho[np.argmin(abs(t - TR))] / rho[0] == pytest.approx(1.0, abs=2e-3)
    g, t, rho, E = _landau(32, 45.0, field_on=True)
    assert t[w][np.argmax(E[w])] > TR + 1.0


def test_ballistic_echo_matches_closed_form():
    """rho_{k2-k1}(t) = (a1 a2/2) exp(-[(k2-k1) t - k2 tau]^2 / 2); Lean: PhaseMixing.maxwellian_mode."""
    k0, tau, a = 0.5, 10.0, 0.01
    g = V.Grid(L=2 * np.pi / k0, nx=32, nv=512, vmax=6.0)
    f = V.pulse(np.tile(V.maxwellian(g.v), (g.nx, 1)), g, 1, a)
    obs = lambda t, f: (t, 2 * V.mode_amplitude(V.density(f, g), 2).real)
    _, out = V.run(f, g, 0.1, 20.0, obs, field_on=False, events=((tau, lambda f: V.pulse(f, g, 3, a)),))
    t, c = map(np.array, zip(*out))
    s = 2 * k0 * t - 3 * k0 * tau
    formula = np.where(t >= tau, 0.5 * a * a * np.exp(-0.5 * s ** 2), 0.0)
    assert np.max(np.abs(c - formula)) < 1e-6 * formula.max()
    assert t[np.argmax(c)] == pytest.approx(15.0, abs=0.05)
