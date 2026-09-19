"""Controls C-POS, C-NEG, C-RES, C-PERM of docs/designs/TDA_VORTEX_FLOOR.md."""
import numpy as np
import pytest

from quantumfluids.tda.vortex_persistence import (
    extract_vortices, floor_stats, h0_deaths, h0_deaths_gudhi, h1_births,
    phase_winding, poisson_null, synthetic_vortex_field)

XI, DX, SHAPE = 1.0, 0.25, (160, 160)


def _lattice(spacing, n=5, origin=6.0):
    c, q = [], []
    for i in range(n):
        for j in range(n):
            c.append((origin + i * spacing, origin + j * spacing))
            q.append(1 if (i + j) % 2 == 0 else -1)
    return np.array(c), np.array(q)


def test_h0_deaths_match_mst():
    """The bridge the whole workstream rests on: H0 deaths ARE the MST edge lengths."""
    rng = np.random.default_rng(0)
    pts = rng.uniform(0, 10, size=(40, 2))
    mine = h0_deaths(pts)
    theirs = h0_deaths_gudhi(pts, max_edge=50.0)
    assert len(mine) == len(theirs) == 39
    assert np.allclose(mine, theirs, atol=1e-9)


def test_winding_is_quantised_and_signed():
    c, q = _lattice(6.0, n=2)
    psi = synthetic_vortex_field(c, q, SHAPE, DX, XI)
    w = phase_winding(psi)
    assert set(np.unique(w)) <= {-1, 0, 1}
    assert w.sum() == q.sum()


def test_C_POS_recovers_planted_vortices():
    """C-POS: positions to within a grid cell, F within 10% of the planted value."""
    spacing = 6.0
    c, q = _lattice(spacing)
    psi = synthetic_vortex_field(c, q, SHAPE, DX, XI)
    pts, ch = extract_vortices(psi, DX)
    assert len(pts) == len(c)
    for cx, cy in c:
        assert np.min(np.hypot(pts[:, 0] - cx, pts[:, 1] - cy)) <= DX * np.sqrt(2)
    s = floor_stats(pts, XI)
    assert abs(s.F - spacing / XI) / (spacing / XI) < 0.10
    assert s.f_below == 0.0


@pytest.mark.parametrize("dx", [DX / 2, DX * 2])
def test_C_RES_floor_tracks_xi_not_grid(dx):
    """C-RES: if F followed the grid it would change by 4x across these two runs."""
    spacing = 6.0
    c, q = _lattice(spacing)
    shape = (int(SHAPE[0] * DX / dx), int(SHAPE[1] * DX / dx))
    psi = synthetic_vortex_field(c, q, shape, dx, XI)
    pts, _ = extract_vortices(psi, dx)
    s = floor_stats(pts, XI)
    assert abs(s.F - spacing / XI) / (spacing / XI) < 0.10


def test_C_NEG_poisson_has_no_floor():
    """C-NEG, as pre-registered: at DENSE sampling (mean spacing ~ xi) Poisson has F << 1.

    The memo's wording is "F << 1 for dense samples"; a sparse Poisson sample trivially has all
    separations above xi and would not test anything.
    """
    rng = np.random.default_rng(1)
    null = poisson_null(n=400, box=(40.0, 40.0), xi=XI, reps=20, rng=rng)
    assert null["F"]["mean"] < 0.5
    assert null["f_below"]["mean"] > 0.1


def test_C_NEG_discriminates_lattice_from_poisson_at_matched_count():
    """The comparison that carries the test: same count, same box, lattice vs uniform."""
    rng = np.random.default_rng(7)
    spacing, box = 6.0, 40.0
    c, q = _lattice(spacing)
    lat = floor_stats(c, XI)
    null = poisson_null(n=len(c), box=(box, box), xi=XI, reps=60, rng=rng)
    assert lat.F > null["F"]["p95"] * 1.5
    assert lat.f_below == 0.0


def test_C_PERM_shuffled_positions_reproduce_the_null():
    """C-PERM: same count, positions replaced by random grid sites -> null-like."""
    rng = np.random.default_rng(2)
    c, q = _lattice(6.0)
    box = 40.0
    pts = rng.uniform(0, box, size=(len(c), 2))
    s = floor_stats(pts, XI)
    null = poisson_null(n=len(c), box=(box, box), xi=XI, reps=40, rng=rng)
    assert null["F"]["p05"] <= s.F <= null["F"]["p95"] * 3


def test_h1_births_are_distances_not_radii_or_squares():
    """A square of side a: its loop must be born at a, in the same units as the H0 deaths.

    This pins the alpha->Rips convention. Squared radius gives 4, radius gives 2; only the
    distance convention gives 4 == the side, comparable with MST edge lengths.
    """
    a = 4.0
    pts = np.array([[0.0, 0.0], [a, 0.0], [a, a], [0.0, a]])
    b = h1_births(pts)
    assert len(b) == 1
    assert abs(b[0] - a) < 1e-6
    assert abs(b[0] - h0_deaths(pts)[0]) < 1e-6      # same scale as the H0 deaths
