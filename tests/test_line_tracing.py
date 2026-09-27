"""Threshold-free line tracing: connectivity comes from the grid, never from a distance."""
import numpy as np

from quantumfluids.tda.vortex_persistence import (
    inter_line_stats, synthetic_line_field_3d, trace_lines)

XI = 1.0


def _field(centres, dx, nz=10, box=24.0):
    n = int(box / dx)
    return synthetic_line_field_3d(np.array(centres), np.ones(len(centres)), (nz, n, n), dx, XI)


def test_single_line_is_one_component():
    psi = _field([(12.0, 12.0)], dx=0.5)
    pts, labels, diag = trace_lines(psi, 0.5)
    assert len(pts) > 0
    assert len(np.unique(labels)) == 1, diag


def test_two_lines_are_two_components_with_no_threshold():
    sep = 6.0
    psi = _field([(9.0, 12.0), (9.0 + sep, 12.0)], dx=0.5)
    pts, labels, diag = trace_lines(psi, 0.5)
    assert len(np.unique(labels)) == 2, diag
    s = inter_line_stats(pts, labels, XI)
    assert abs(s.F - sep / XI) / (sep / XI) < 0.15


def test_floor_is_independent_of_resolution():
    """The decisive property the proximity method lacked: no parameter for the floor to track."""
    sep = 6.0
    out = []
    for dx in (0.5, 0.25):
        psi = _field([(9.0, 12.0), (9.0 + sep, 12.0)], dx=dx)
        pts, labels, _ = trace_lines(psi, dx)
        assert len(np.unique(labels)) == 2
        out.append(inter_line_stats(pts, labels, XI).F)
    assert abs(out[0] - out[1]) / out[0] < 0.10
    assert all(abs(v - sep / XI) / (sep / XI) < 0.15 for v in out)
