"""Physics controls for the 2D GPE solver. Norm conservation is deliberately NOT the main control:
split-step conserves it by construction, so it cannot fail. Energy drift and the vortex core
profile can."""
import numpy as np
import pytest

from quantumfluids.gpe.solver2d import (
    Grid2D, energy, evolve, healing_length, max_dt, norm, plant_vortices, radial_density_profile,
    smooth_phase_noise, step)

XI = healing_length(1.0)


def _grid(n=128, per_xi=8):
    return Grid2D(n=n, dx=XI / per_xi)


def test_norm_is_conserved_by_construction():
    g = _grid()
    rng = np.random.default_rng(0)
    psi = smooth_phase_noise(g, amp=0.3, k_cut_inv_xi=2.0, rng=rng)
    n0 = norm(psi, g)
    psi = evolve(psi, g, dt=max_dt(g), n_steps=50)
    assert abs(norm(psi, g) - n0) / n0 < 1e-12


def test_energy_is_conserved_at_the_prescribed_timestep():
    """The control that can actually fail: energy drift on a physical (band-limited) field at
    dt = max_dt. A white-noise phase at dt = 0.005 drifts 33%, which is why max_dt exists."""
    g = _grid()
    psi = smooth_phase_noise(g, amp=0.3, k_cut_inv_xi=2.0, rng=np.random.default_rng(1))
    e0 = energy(psi, g)
    psi = evolve(psi, g, dt=max_dt(g), n_steps=400)
    assert abs(energy(psi, g) - e0) / abs(e0) < 1e-4


def test_oversized_timestep_is_detectably_wrong():
    """The bound is not decorative: 50x max_dt must visibly break energy conservation."""
    g = _grid()
    psi = smooth_phase_noise(g, amp=0.3, k_cut_inv_xi=2.0, rng=np.random.default_rng(1))
    e0 = energy(psi, g)
    bad = evolve(psi.copy(), g, dt=50 * max_dt(g), n_steps=400)
    assert abs(energy(bad, g) - e0) / abs(e0) > 1e-3


def test_energy_drift_shrinks_with_timestep():
    """O(dt^2): halving dt over the same physical time must reduce the drift."""
    g = _grid()
    psi0 = smooth_phase_noise(g, amp=0.3, k_cut_inv_xi=2.0, rng=np.random.default_rng(2))
    e0 = energy(psi0, g)
    drifts = []
    for mult, steps in ((4, 100), (2, 200)):
        psi = evolve(psi0.copy(), g, dt=mult * max_dt(g), n_steps=steps)
        drifts.append(abs(energy(psi, g) - e0))
    assert drifts[1] < drifts[0]


def test_relaxation_builds_a_core_of_size_xi():
    """Plant only a PHASE; the core must be created by the solver, and come out of size ~xi."""
    g = _grid(n=256)
    c = np.array([[g.L * 0.35, g.L / 2], [g.L * 0.65, g.L / 2]])
    psi = plant_vortices(g, c, np.array([1, -1]))
    psi = evolve(psi, g, dt=-0.02j, n_steps=100, renorm=True)     # tau = 2, see solver docstring
    r, prof = radial_density_profile(psi, g, tuple(c[0]), r_max=6 * XI)
    ok = ~np.isnan(prof)
    assert prof[0] < 0.2, f"core not formed: {prof[0]:.3f}"
    assert prof[-1] > 0.8, f"density does not recover: {prof[-1]:.3f}"
    half = np.interp(0.5, prof[ok], r[ok])
    assert 0.5 * XI < half < 3.0 * XI, f"core half-density radius {half/XI:.2f} xi"


def test_over_relaxation_destroys_the_vortices():
    """The failure mode above, pinned as a test so the solver's docstring cannot silently rot."""
    g = _grid(n=256)
    c = np.array([[g.L * 0.35, g.L / 2], [g.L * 0.65, g.L / 2]])
    psi = plant_vortices(g, c, np.array([1, -1]))
    long = evolve(psi.copy(), g, dt=-0.02j, n_steps=1000, renorm=True)   # tau = 20
    r, prof = radial_density_profile(long, g, tuple(c[0]), r_max=6 * XI)
    assert prof[0] > 0.9, "expected the pair to have annihilated by tau = 20"


def test_net_charge_must_vanish_on_a_periodic_box():
    g = _grid(n=64)
    with pytest.raises(ValueError, match="net charge"):
        plant_vortices(g, np.array([[1.0, 1.0]]), np.array([1]))


def test_opposite_pair_annihilates_but_same_sign_pair_does_not():
    """Physics control: a close +/- dipole annihilates under real-time evolution; ++ does not."""
    from quantumfluids.tda.vortex_persistence import extract_vortices
    g = _grid(n=256)
    sep = 4 * XI
    mid = g.L / 2
    out = {}
    for label, q in (("dipole", np.array([1, -1])), ("same", np.array([1, 1]))):
        if label == "same":
            c = np.array([[mid - sep / 2, mid], [mid + sep / 2, mid],
                          [mid, mid - g.L / 4], [mid, mid + g.L / 4]])
            qq = np.array([1, 1, -1, -1])
        else:
            c = np.array([[mid - sep / 2, mid], [mid + sep / 2, mid]])
            qq = q
        psi = plant_vortices(g, c, qq)
        psi = evolve(psi, g, dt=-0.02j, n_steps=100, renorm=True)
        psi = evolve(psi, g, dt=0.01, n_steps=1500)
        pts, _ = extract_vortices(psi, g.dx)
        near = [p for p in pts if abs(p[1] - mid) < g.L / 8]
        out[label] = len(near)
    assert out["dipole"] < out["same"], out
