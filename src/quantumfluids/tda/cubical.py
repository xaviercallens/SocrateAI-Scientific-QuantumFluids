"""Cubical sublevel persistence of periodic 2D fields (GUDHI), for KINETIC_TDA_PREREG.md D0, D1, D3.

Plain statement of what this computes, so nobody mistakes it for more: the H0 sublevel bar of a local
minimum is (value at the minimum, value at the saddle where its basin merges into a deeper one).  Its
length is the minimum's DEPTH -- topographic prominence, upside down.  Nothing here is new mathematics.

Two cubical constructions exist and they are NOT interchangeable (Bleile, Garin, Heiss, Maggs, Robins,
arXiv:2102.11397): pixels as top-dimensional cells (T; sublevel sets are 8-connected) or as vertices
(V; 4-connected).  With periodic identification V(I) and T(-I) are dual filtrations on the torus, so
    [b, d) in Dgm_k(T(I))   <->   [-d, -b) in Dgm_{1-k}(V(-I)).
`duality_defect` checks exactly that, and is the pipeline's known-answer control.
"""
from __future__ import annotations

import numpy as np
import gudhi


def _complex(field, construction: str, periodic):
    """`periodic`: bool for all axes, or one bool per axis (e.g. (True, False) for f(x, v))."""
    kw = {"top_dimensional_cells": field} if construction == "T" else {"vertices": field}
    per = [bool(periodic)] * field.ndim if isinstance(periodic, (bool, np.bool_)) else [bool(p) for p in periodic]
    if any(per):
        return gudhi.PeriodicCubicalComplex(periodic_dimensions=per, **kw)
    return gudhi.CubicalComplex(**kw)


def finite_pairs(field, dim: int, construction: str = "T", periodic=True) -> np.ndarray:
    cc = _complex(np.ascontiguousarray(field, dtype=float), construction, periodic)
    cc.compute_persistence(homology_coeff_field=2, min_persistence=0.0)
    iv = np.asarray(cc.persistence_intervals_in_dimension(dim)).reshape(-1, 2)
    iv = iv[np.isfinite(iv[:, 1])]
    return iv[iv[:, 1] > iv[:, 0]]


def _canon(p):
    return p[np.lexsort((p[:, 1], p[:, 0]))] if len(p) else p


def duality_defect(field, other: str = "V", periodic=True):
    """Compare H0 sublevel pairs of `field` (T) with the reflected H1 pairs of -field (construction
    `other`).  Returns (n_H0, n_H1, max |difference| after sorting, or inf if the counts differ)."""
    a = _canon(finite_pairs(field, 0, "T", periodic))
    h1 = finite_pairs(-np.asarray(field), 1, other, periodic)
    b = _canon(np.column_stack([-h1[:, 1], -h1[:, 0]])) if len(h1) else h1
    if len(a) != len(b):
        return len(a), len(b), float("inf")
    return len(a), len(b), float(np.max(np.abs(a - b))) if len(a) else 0.0


def minima_with_depth(field, periodic=True):
    """H0 sublevel classes of `field` (T-construction) as (birth value, depth, flat index of the birth pixel).
    The global minimum (the essential class) is included with depth = max(field) - min(field)."""
    field = np.ascontiguousarray(field, dtype=float)
    cc = _complex(field, "T", periodic)
    cc.compute_persistence(homology_coeff_field=2, min_persistence=0.0)
    regular, essential = cc.cofaces_of_persistence_pairs()
    flat = field.ravel(order="F")            # GUDHI indexes top cells in Fortran order
    out = []
    if len(regular) > 0:
        for b, d in regular[0]:
            out.append((flat[b], flat[d] - flat[b], int(b)))
    if len(essential) > 0 and len(essential[0]) > 0:
        b = int(essential[0][0]); out.append((flat[b], field.max() - flat[b], b))
    arr = np.array(out, dtype=float).reshape(-1, 3)
    idx = arr[:, 2].astype(int)
    ij = np.column_stack(np.unravel_index(idx, field.shape, order="F"))
    return arr[:, 0], arr[:, 1], ij
