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
