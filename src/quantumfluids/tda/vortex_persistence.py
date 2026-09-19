"""Persistent homology of quantum-fluid vortex configurations (workstream T).

Implements docs/designs/TDA_VORTEX_FLOOR.md. GUDHI (INRIA) provides the filtrations.

The physical statement under test: quantized circulation with a finite core size `xi` implies a
minimum vortex separation, and a minimum separation is a floor in the persistence diagram. In a
Vietoris-Rips filtration the H0 deaths are exactly the Euclidean-MST edge lengths, so
"smallest H0 death" and "minimum separation" are the same number (asserted, not assumed: see
`h0_deaths_match_mst`).

Nothing here interprets anything. Statistics are returned next to a matched Poisson null, because a
floor can be manufactured by the extraction grid and only the comparison with the null distinguishes
the two (memo section 3).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

try:
    import gudhi
except ImportError as exc:                                    # pragma: no cover
    raise ImportError("workstream T needs gudhi (INRIA): uv add gudhi") from exc

from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial.distance import pdist, squareform


# ------------------------------------------------------------------ vortex extraction

def _principal(delta: np.ndarray) -> np.ndarray:
    """Wrap phase differences into (-pi, pi]."""
    return (delta + np.pi) % (2 * np.pi) - np.pi


def phase_winding(psi: np.ndarray) -> np.ndarray:
    """Topological charge of every plaquette of a 2D complex field.

    Sums principal-branch phase differences anticlockwise around each unit square. The result is an
    integer (the winding number); it is exact for a field resolved well enough that no true phase
    step exceeds pi between neighbouring grid points -- which is why `C-RES` in the memo exists.
    """
    if psi.ndim != 2:
        raise ValueError(f"phase_winding expects a 2D field, got shape {psi.shape}")
    th = np.angle(psi)
    w = (_principal(th[1:, :-1] - th[:-1, :-1])
         + _principal(th[1:, 1:] - th[1:, :-1])
         + _principal(th[:-1, 1:] - th[1:, 1:])
         + _principal(th[:-1, :-1] - th[:-1, 1:]))
    return np.rint(w / (2 * np.pi)).astype(int)


def extract_vortices(psi: np.ndarray, dx: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Vortex positions (plaquette centres, in physical units) and their charges."""
    charge = phase_winding(psi)
    iy, ix = np.nonzero(charge)
    pts = np.stack([(ix + 0.5) * dx, (iy + 0.5) * dx], axis=1)
    return pts, charge[iy, ix]


# ------------------------------------------------------------------ persistence

def h0_deaths(points: np.ndarray) -> np.ndarray:
    """H0 death times of the Rips filtration = Euclidean MST edge lengths, sorted."""
    if len(points) < 2:
        return np.empty(0)
    mst = minimum_spanning_tree(squareform(pdist(points)))
    return np.sort(mst.tocoo().data)


def h0_deaths_gudhi(points: np.ndarray, max_edge: float) -> np.ndarray:
    """The same quantity via GUDHI's Rips persistence, used to cross-check `h0_deaths`."""
    if len(points) < 2:
        return np.empty(0)
    st = gudhi.RipsComplex(points=points, max_edge_length=max_edge).create_simplex_tree(max_dimension=1)
    st.compute_persistence(persistence_dim_max=False)
    d = [p[1] for p in st.persistence_intervals_in_dimension(0) if np.isfinite(p[1])]
    return np.sort(np.asarray(d))


def h1_births(points: np.ndarray) -> np.ndarray:
    """Birth scales of H1 (loop) features of the alpha complex, as DISTANCES, sorted.

    GUDHI's alpha filtration values are SQUARED CIRCUMRADII. Two conversions are needed, and
    omitting either corrupts the comparison with `F`:
      * sqrt, to get a length rather than its square;
      * a factor 2, because an alpha radius `r` corresponds to a Rips distance `2r` -- H0 deaths
        (MST edge lengths) are point-to-point DISTANCES. Without it the loop scale would sit a
        factor 2 below the floor scale and `L1_over_xi / F` would be meaningless.
    Checked against a square of side `a`, whose loop is born at `a` (test suite).
    """
    if len(points) < 4:
        return np.empty(0)
    st = gudhi.AlphaComplex(points=points).create_simplex_tree()
    st.compute_persistence()
    b = [p[0] for p in st.persistence_intervals_in_dimension(1)]
    return 2.0 * np.sqrt(np.sort(np.asarray(b))) if len(b) else np.empty(0)


# ------------------------------------------------------------------ statistics

@dataclass
class FloorStats:
    n_points: int
    xi: float
    F: float               # min H0 death / xi -- the floor ratio
    f_below: float         # fraction of H0 deaths below xi
    mst_mean_over_xi: float
    L1_over_xi: float      # median H1 birth (as a distance) / xi -- the loop scale
    n_h1: int

    def as_dict(self) -> dict:
        return asdict(self)


def floor_stats(points: np.ndarray, xi: float) -> FloorStats:
    d0 = h0_deaths(points)
    b1 = h1_births(points)
    return FloorStats(
        n_points=len(points), xi=float(xi),
        F=float(d0[0] / xi) if len(d0) else float("nan"),
        f_below=float(np.mean(d0 < xi)) if len(d0) else float("nan"),
        mst_mean_over_xi=float(np.mean(d0) / xi) if len(d0) else float("nan"),
        L1_over_xi=float(np.median(b1) / xi) if len(b1) else float("nan"),
        n_h1=int(len(b1)))


def poisson_null(n: int, box: tuple[float, float], xi: float, reps: int,
                 rng: np.random.Generator) -> dict:
    """C-NEG: the identical pipeline on uniform points at the same count and in the same box."""
    F, fb, L1 = [], [], []
    for _ in range(reps):
        pts = np.stack([rng.uniform(0, box[0], n), rng.uniform(0, box[1], n)], axis=1)
        s = floor_stats(pts, xi)
        F.append(s.F); fb.append(s.f_below); L1.append(s.L1_over_xi)
    q = lambda a: {"mean": float(np.mean(a)), "p05": float(np.percentile(a, 5)),
                   "p95": float(np.percentile(a, 95))}
    return {"reps": reps, "n": n, "F": q(F), "f_below": q(fb), "L1_over_xi": q(L1)}


# ------------------------------------------------------------------ synthetic field (CONTROLS ONLY)

def synthetic_vortex_field(centres: np.ndarray, charges: np.ndarray, shape: tuple[int, int],
                           dx: float, xi: float) -> np.ndarray:
    """A complex field with vortices planted at `centres`, core size `xi`.

    `psi = prod_j tanh(|z - z_j|/xi) * exp(i q_j arg(z - z_j))` -- the standard core ansatz: correct
    winding, density vanishing linearly inside a core of size `xi`.

    FOR CONTROLS ONLY. Per memo section 6 a synthetic field is never reported as a result.
    """
    ny, nx = shape
    x = (np.arange(nx) + 0.5) * dx
    y = (np.arange(ny) + 0.5) * dx
    Z = x[None, :] + 1j * y[:, None]
    psi = np.ones_like(Z)
    for (cx, cy), q in zip(centres, charges):
        d = Z - (cx + 1j * cy)
        r = np.abs(d)
        psi = psi * np.tanh(r / xi) * np.exp(1j * q * np.angle(d))
    return psi


# ------------------------------------------------------------------ 3D: vortex LINES, not points

def phase_winding_3d(psi: np.ndarray) -> dict[str, np.ndarray]:
    """Topological charge on plaquettes normal to each axis of a 3D complex field `psi[z,y,x]`.

    A vortex line pierces a plaquette whose winding is nonzero, so the three arrays together trace
    the line set whatever its orientation.
    """
    if psi.ndim != 3:
        raise ValueError(f"phase_winding_3d expects a 3D field, got shape {psi.shape}")
    out = {}
    for axis, name in ((0, "z"), (1, "y"), (2, "x")):
        sl = np.moveaxis(psi, axis, 0)
        w = np.stack([phase_winding(sl[i]) for i in range(sl.shape[0])], axis=0)
        out[name] = w
    return out


def extract_vortex_points_3d(psi: np.ndarray, dx: float = 1.0) -> np.ndarray:
    """Points tracing the vortex lines: centres of pierced plaquettes, in physical units."""
    w = phase_winding_3d(psi)
    pts = []
    for name, arr in w.items():
        idx = np.argwhere(arr != 0).astype(float)          # (slice, row, col) in the moved frame
        if not len(idx):
            continue
        s, r, c = idx[:, 0], idx[:, 1] + 0.5, idx[:, 2] + 0.5
        if name == "z":      p = np.stack([c, r, s], axis=1)          # (x, y, z)
        elif name == "y":    p = np.stack([c, s, r], axis=1)
        else:                p = np.stack([s, c, r], axis=1)
        pts.append(p * dx)
    return np.concatenate(pts, axis=0) if pts else np.empty((0, 3))


def segment_lines(points: np.ndarray, link_radius: float) -> np.ndarray:
    """Label points by connected component under a `link_radius` proximity graph.

    WHY THIS EXISTS. In 3D the extractor returns points spaced by the GRID along each vortex line.
    Feeding them straight into `floor_stats` would report the grid spacing as the "floor" -- the
    resolution artefact C-RES exists to catch. The floor must be measured BETWEEN DISTINCT LINES, so
    points are first grouped into lines and the statistics are computed on the line-to-line
    distances (`inter_line_stats`).
    """
    from scipy.sparse.csgraph import connected_components
    from scipy.spatial import cKDTree
    if len(points) == 0:
        return np.empty(0, dtype=int)
    tree = cKDTree(points)
    adj = tree.sparse_distance_matrix(tree, link_radius, output_type="coo_matrix")
    _, labels = connected_components(adj, directed=False)
    return labels


def inter_line_distances(points: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Minimum distance between every pair of distinct lines (the condensed inter-line metric)."""
    uniq = np.unique(labels)
    n = len(uniq)
    D = np.zeros((n, n))
    for a in range(n):
        Pa = points[labels == uniq[a]]
        for b in range(a + 1, n):
            Pb = points[labels == uniq[b]]
            d = np.min(np.linalg.norm(Pa[:, None, :] - Pb[None, :, :], axis=2))
            D[a, b] = D[b, a] = d
    return D


def inter_line_stats(points: np.ndarray, labels: np.ndarray, xi: float) -> FloorStats:
    """Floor statistics on the LINE graph: H0 deaths are MST edges of the inter-line metric."""
    D = inter_line_distances(points, labels)
    if D.shape[0] < 2:
        return FloorStats(n_points=D.shape[0], xi=float(xi), F=float("nan"), f_below=float("nan"),
                          mst_mean_over_xi=float("nan"), L1_over_xi=float("nan"), n_h1=0)
    d0 = np.sort(minimum_spanning_tree(D).tocoo().data)
    return FloorStats(n_points=D.shape[0], xi=float(xi),
                      F=float(d0[0] / xi), f_below=float(np.mean(d0 < xi)),
                      mst_mean_over_xi=float(np.mean(d0) / xi),
                      L1_over_xi=float("nan"), n_h1=0)


def synthetic_line_field_3d(xy_centres: np.ndarray, charges: np.ndarray,
                            shape: tuple[int, int, int], dx: float, xi: float) -> np.ndarray:
    """3D field with straight vortex lines along z at the given (x, y). CONTROLS ONLY."""
    nz, ny, nx = shape
    psi2 = synthetic_vortex_field(xy_centres, charges, (ny, nx), dx, xi)
    return np.repeat(psi2[None, :, :], nz, axis=0)


# ------------------------------------------------------------------ periodic box support

def periodic_inter_line_distances(points: np.ndarray, labels: np.ndarray, L: float) -> np.ndarray:
    """Minimum-image minimum distance between every pair of distinct lines in a periodic box.

    Periodicity is not optional here: ignoring it drops pairs that are close across a face and so
    INFLATES the measured floor, which is the direction that would manufacture a false positive.
    """
    from scipy.spatial import cKDTree
    uniq = np.unique(labels)
    trees = {u: cKDTree(np.mod(points[labels == u], L), boxsize=L) for u in uniq}
    n = len(uniq)
    D = np.zeros((n, n))
    for a in range(n):
        Pa = np.mod(points[labels == uniq[a]], L)
        for b in range(a + 1, n):
            d, _ = trees[uniq[b]].query(Pa, k=1)
            D[a, b] = D[b, a] = float(np.min(d))
    return D


def periodic_segment_lines(points: np.ndarray, link_radius: float, L: float) -> np.ndarray:
    """Connected components under a periodic proximity graph."""
    from scipy.sparse.csgraph import connected_components
    from scipy.spatial import cKDTree
    if len(points) == 0:
        return np.empty(0, dtype=int)
    P = np.mod(points, L)
    tree = cKDTree(P, boxsize=L)
    adj = tree.sparse_distance_matrix(tree, link_radius, output_type="coo_matrix")
    _, labels = connected_components(adj, directed=False)
    return labels


def line_floor_stats(D: np.ndarray, xi: float) -> dict:
    """Floor statistics from an inter-line distance matrix (H0 deaths = MST edges of that metric)."""
    if D.shape[0] < 2:
        return {"n_lines": int(D.shape[0]), "F": float("nan"), "f_below": float("nan"),
                "mst_mean_over_xi": float("nan")}
    d0 = np.sort(minimum_spanning_tree(D).tocoo().data)
    return {"n_lines": int(D.shape[0]), "F": float(d0[0] / xi),
            "f_below": float(np.mean(d0 < xi)),
            "mst_mean_over_xi": float(np.mean(d0) / xi),
            "mst_edges_over_xi": (d0 / xi).tolist()}


def random_shift_null(points: np.ndarray, labels: np.ndarray, L: float, xi: float,
                      reps: int, rng: np.random.Generator) -> dict:
    """Null model: keep every line's SHAPE, give each an independent random periodic translation.

    This is the right null for extended objects. A Poisson point null would destroy the fact that a
    vortex line is a connected curve and would therefore compare against the wrong thing; here only
    the inter-line arrangement is randomised, so the test isolates exactly the correlation of interest.
    """
    F, fb, mm = [], [], []
    uniq = np.unique(labels)
    for _ in range(reps):
        P = points.copy()
        for u in uniq:
            P[labels == u] = np.mod(P[labels == u] + rng.uniform(0, L, 3), L)
        s = line_floor_stats(periodic_inter_line_distances(P, labels, L), xi)
        F.append(s["F"]); fb.append(s["f_below"]); mm.append(s["mst_mean_over_xi"])
    q = lambda a: {"mean": float(np.mean(a)), "p05": float(np.percentile(a, 5)),
                   "p95": float(np.percentile(a, 95)), "min": float(np.min(a))}
    return {"reps": reps, "F": q(F), "f_below": q(fb), "mst_mean_over_xi": q(mm)}
