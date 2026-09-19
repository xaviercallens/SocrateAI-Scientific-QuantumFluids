"""3D controls: the floor must be the LINE separation, never the grid spacing along a line."""
import numpy as np

from quantumfluids.tda.vortex_persistence import (
    extract_vortex_points_3d, floor_stats, inter_line_stats, segment_lines,
    synthetic_line_field_3d)

XI = 1.0


def _two_lines(sep, dx, nz=12):
    c = np.array([[8.0, 8.0], [8.0 + sep, 8.0]])
    q = np.array([1, 1])
    box = 16.0 + sep
    shape = (nz, int(box / dx), int(box / dx))
    psi = synthetic_line_field_3d(c, q, shape, dx, XI)
    pts = extract_vortex_points_3d(psi, dx)
    return pts, c


def test_naive_point_cloud_would_report_the_grid_spacing():
    """The artefact this design guards against, demonstrated rather than asserted."""
    dx, sep = 0.5, 6.0
    pts, _ = _two_lines(sep, dx)
    naive = floor_stats(pts, XI)
    assert naive.F < sep / 2          # the naive floor is NOT the line separation ...
    assert naive.F <= dx / XI + 1e-9  # ... it is the grid spacing along the lines


def test_line_segmentation_recovers_the_separation():
    dx, sep = 0.5, 6.0
    pts, c = _two_lines(sep, dx)
    labels = segment_lines(pts, link_radius=2.0 * dx)
    assert len(np.unique(labels)) == 2
    s = inter_line_stats(pts, labels, XI)
    assert abs(s.F - sep / XI) / (sep / XI) < 0.10


def test_C_RES_3d_floor_tracks_separation_not_grid():
    """A 2x grid change must not move the line-based floor."""
    sep = 6.0
    vals = []
    for dx in (0.5, 0.25):
        pts, _ = _two_lines(sep, dx)
        labels = segment_lines(pts, link_radius=2.0 * dx)
        vals.append(inter_line_stats(pts, labels, XI).F)
    assert abs(vals[0] - vals[1]) / vals[0] < 0.05
    assert all(abs(v - sep / XI) / (sep / XI) < 0.10 for v in vals)
