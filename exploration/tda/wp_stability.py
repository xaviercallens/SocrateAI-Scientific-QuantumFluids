#!/usr/bin/env python3
"""Skraba-Turner cellular Wasserstein stability (arXiv:2006.16824 v7, Thm 4.6) on the closed-loop pairs.

Pre-registered in docs/designs/WASSERSTEIN_STABILITY_PREREG.md (read it first; the conventions below are
the theorem's own, not the l^inf ground cost of loop_certificate_*.py):

  * T-construction cell values: pixel = its value, every lower cell = min over the pixels containing it
    (`cell_values`), per-axis periodicity as GUDHI's PeriodicCubicalComplex.
  * ||f-g||_p^p = sum over ALL cells (part (i)); part (ii) k=0 = vertices and edges only.
  * W_p between diagrams with l_p ground metric, diagonal at perpendicular distance 2^{(1-p)/p}|b-a|,
    essential classes matched in sorted order at |a-b|, total over degrees as (sum_k W_p^(k)^p)^{1/p}.
  * every W_p^(k) is a primal assignment AND an LP dual certificate checked by an independent function.

Run:  .venv/bin/python exploration/tda/wp_stability.py            (controls, then the seven pairs)
      .venv/bin/python exploration/tda/wp_stability.py --controls-only
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.optimize import linear_sum_assignment, linprog

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
DATA = ROOT / "data" / "generated" / "kinetic_tda"
BIG = 1e9


# ----------------------------------------------------------------------------------------------------
# 1. The cell complex (T-construction) and its cell values
# ----------------------------------------------------------------------------------------------------
def _pad(field: np.ndarray, periodic) -> np.ndarray:
    """Pad so that Q[k] = pixel k-1 along each axis: wrap one pixel in front for a periodic axis,
    +inf on both sides for a non-periodic one (then boundary cells take the min over existing pixels)."""
    q = np.asarray(field, dtype=float)
    per = [bool(periodic)] * q.ndim if isinstance(periodic, (bool, np.bool_)) else [bool(p) for p in periodic]
    for ax, p in enumerate(per):
        if p:
            front = np.take(q, [-1], axis=ax)
            q = np.concatenate([front, q], axis=ax)
        else:
            shape = list(q.shape); shape[ax] = 1
            inf = np.full(shape, np.inf)
            q = np.concatenate([inf, q, inf], axis=ax)
    return q


def cell_values(field: np.ndarray, periodic) -> dict:
    """All cells of the T-construction cubical complex of a 1D or 2D array, with their filtration values.

    Returns {'pixels': top cells, 'vertices': V, 'edges0': E0, 'edges1': E1 (2D only)} where
    V[k,l] = min of the (up to) four pixels around vertex (k,l); E0[i,l] (parallel to axis 0) = min of
    the two pixels (i, l-1), (i, l); E1[k,j] (parallel to axis 1) = min of pixels (k-1, j), (k, j)."""
    f = np.asarray(field, dtype=float)
    q = _pad(f, periodic)
    if f.ndim == 1:
        v = np.minimum(q[:-1], q[1:])
        return {"pixels": f, "vertices": v}
    if f.ndim != 2:
        raise ValueError("1D or 2D only")
    v = np.minimum(np.minimum(q[:-1, :-1], q[1:, :-1]), np.minimum(q[:-1, 1:], q[1:, 1:]))
    per = [bool(periodic)] * 2 if isinstance(periodic, (bool, np.bool_)) else [bool(p) for p in periodic]
    r0 = slice(1, 1 + f.shape[0]) if not per[0] else slice(1, None)   # rows of q that are real pixels
    r1 = slice(1, 1 + f.shape[1]) if not per[1] else slice(1, None)
    e0 = np.minimum(q[r0, :-1], q[r0, 1:])            # shape (N, A1-1): pixel row i, vertex column l
    e1 = np.minimum(q[:-1, r1], q[1:, r1])            # shape (A0-1, M): vertex row k, pixel column j
    return {"pixels": f, "vertices": v, "edges0": e0, "edges1": e1}


def cell_norm(f: np.ndarray, g: np.ndarray, periodic, p: float, dims=("pixels", "vertices", "edges0", "edges1")):
    """||f-g||_p over the named cell families (all of them = part (i); vertices+edges = part (ii), k=0)."""
    cf, cg = cell_values(f, periodic), cell_values(g, periodic)
    tot = 0.0
    for d in dims:
        if d in cf:
            diff = np.abs(cf[d] - cg[d])
            diff = diff[np.isfinite(diff)]
            tot += float(np.sum(diff ** p))
    return tot ** (1.0 / p)


# ----------------------------------------------------------------------------------------------------
# 2. Independent H0 by union-find on the 1-skeleton (control C1) and GUDHI diagrams
# ----------------------------------------------------------------------------------------------------
def h0_unionfind(field: np.ndarray, periodic):
    """Finite H0 pairs (birth, death) and the essential birth, by the elder rule on the vertex/edge
    values of `cell_values`. Independent of GUDHI's persistence code (only the min-construction is
    shared, which is exactly what C1 tests)."""
    f = np.asarray(field, dtype=float)
    cells = cell_values(f, periodic)
    V = cells["vertices"]
    per = [bool(periodic)] * f.ndim if isinstance(periodic, (bool, np.bool_)) else [bool(p) for p in periodic]
    nv = V.size
    vidx = np.arange(nv).reshape(V.shape)
    edges = []      # (value, u, w)
    if f.ndim == 1:
        # pixel i connects vertices i and i+1 (mod N if periodic)
        N = f.shape[0]
        for i in range(N):
            a = i; b = (i + 1) % N if per[0] else i + 1
            edges.append((f[i], vidx[a], vidx[b]))
    else:
        E0, E1 = cells["edges0"], cells["edges1"]
        N, M = f.shape
        A0, A1 = V.shape
        for i in range(E0.shape[0]):           # E0[i,l]: vertices (i,l) -- (i+1,l)
            for l in range(E0.shape[1]):
                a = vidx[i, l]; b = vidx[(i + 1) % A0 if per[0] else i + 1, l]
                edges.append((E0[i, l], a, b))
        for k in range(E1.shape[0]):           # E1[k,j]: vertices (k,j) -- (k,j+1)
            for j in range(E1.shape[1]):
                a = vidx[k, j]; b = vidx[k, (j + 1) % A1 if per[1] else j + 1]
                edges.append((E1[k, j], a, b))
    evals = np.array([e[0] for e in edges])
    order = np.argsort(evals, kind="stable")
    vb = V.ravel()
    parent = np.arange(nv)
    birth = vb.copy()

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pairs = []
    for idx in order:
        val, u, w = edges[idx]
        if not np.isfinite(val):
            continue
        ru, rw = find(u), find(w)
        if ru == rw:
            continue
        # elder rule: the younger component (larger birth) dies
        if birth[ru] < birth[rw] or (birth[ru] == birth[rw] and ru < rw):
            old, young = ru, rw
        else:
            old, young = rw, ru
        parent[young] = old
        if val > birth[young]:
            pairs.append((birth[young], val))
    finite_v = vb[np.isfinite(vb)]
    return np.array(pairs, dtype=float).reshape(-1, 2), float(finite_v.min())


def gudhi_diagrams(field: np.ndarray, periodic):
    """{k: (finite pairs (n,2), sorted essential births)} for all degrees, GUDHI T-construction."""
    import gudhi
    f = np.ascontiguousarray(field, dtype=float)
    per = [bool(periodic)] * f.ndim if isinstance(periodic, (bool, np.bool_)) else [bool(p) for p in periodic]
    if any(per):
        cc = gudhi.PeriodicCubicalComplex(top_dimensional_cells=f, periodic_dimensions=per)
    else:
        cc = gudhi.CubicalComplex(top_dimensional_cells=f)
    cc.compute_persistence(homology_coeff_field=2, min_persistence=0.0)
    out = {}
    for k in range(f.ndim + 1):
        iv = np.asarray(cc.persistence_intervals_in_dimension(k)).reshape(-1, 2)
        ess = np.sort(iv[~np.isfinite(iv[:, 1]), 0])
        fin = iv[np.isfinite(iv[:, 1])]
        fin = fin[fin[:, 1] > fin[:, 0]]
        out[k] = (fin, ess)
    return out


def same_multiset(a: np.ndarray, b: np.ndarray, tol=0.0) -> bool:
    a = np.asarray(a, float).reshape(-1, 2); b = np.asarray(b, float).reshape(-1, 2)
    if len(a) != len(b):
        return False
    ka = a[np.lexsort((a[:, 1], a[:, 0]))]; kb = b[np.lexsort((b[:, 1], b[:, 0]))]
    return bool(np.all(np.abs(ka - kb) <= tol))


# ----------------------------------------------------------------------------------------------------
# 3. W_p between diagrams: primal assignment + LP dual certificate
# ----------------------------------------------------------------------------------------------------
def diag_cost(pts: np.ndarray, p: float, ground: str) -> np.ndarray:
    pers = pts[:, 1] - pts[:, 0]
    if ground == "linf":
        return pers / 2.0
    return 2.0 ** ((1.0 - p) / p) * pers          # perpendicular l_p distance to the diagonal


def point_cost(X: np.ndarray, Y: np.ndarray, p: float, ground: str) -> np.ndarray:
    db = np.abs(X[:, 0][:, None] - Y[:, 0][None, :]); dd = np.abs(X[:, 1][:, None] - Y[:, 1][None, :])
    if ground == "linf":
        return np.maximum(db, dd)
    return (db ** p + dd ** p) ** (1.0 / p)


def augmented_matrix(X: np.ndarray, Y: np.ndarray, p: float, ground: str):
    """(n+m) x (m+n) matrix of p-th powers of ground distances (Kerber-Morozov-Nigmetov augmentation):
    rows 0..n-1 = X, cols 0..m-1 = Y; row i's own diagonal slot is column m+i, column j's own diagonal
    slot is row n+j; cross-use costs BIG; dummy-dummy block costs 0."""
    n, m = len(X), len(Y)
    C = np.full((n + m, m + n), BIG)
    if n and m:
        C[:n, :m] = point_cost(X, Y, p, ground) ** p
    if n:
        C[np.arange(n), m + np.arange(n)] = diag_cost(X, p, ground) ** p
    if m:
        C[n + np.arange(m), np.arange(m)] = diag_cost(Y, p, ground) ** p
    C[n:, m:] = 0.0
    return C


def check_certificate(C: np.ndarray, rows, cols, u: np.ndarray, v: np.ndarray, tol=1e-9):
    """Independent check: potentials feasible everywhere, and the plan's cost equals sum u + sum v."""
    viol = float(np.max(u[:, None] + v[None, :] - C))
    primal = float(C[rows, cols].sum()); dual = float(u.sum() + v.sum())
    gap = abs(primal - dual) / max(1.0, abs(primal))
    return {"feasible": viol <= tol, "max_violation": viol, "primal": primal, "dual": dual,
            "rel_gap": gap, "tight": gap <= tol}


def dual_potentials(C: np.ndarray, n: int | None = None, m: int | None = None, time_limit=1800.0):
    """Solve the dual LP  max sum u + sum v  s.t. u_i + v_j <= C_ij  (sparse, HiGHS).

    With the augmented structure (n, m) given, the LP is posed on a reduced constraint set: the n*m
    real block and the n + m diagonal slots as they are; the dummy-dummy block (cost 0, m*n
    constraints) replaced by two auxiliary variables a >= u_{n+j}, b >= v_{m+i} with a + b <= 0; the BIG
    cross-use constraints DROPPED. Dropping constraints relaxes the dual, so the returned potentials are
    not trusted here: `check_certificate` re-verifies feasibility against the FULL matrix afterwards,
    and a violated dropped constraint would fail that check. (The full LP needed > 8 GB on 1600x1600.)"""
    R, K = C.shape
    if n is None or m is None or n + m != R or m + n != K:
        ii, jj = np.meshgrid(np.arange(R), np.arange(K), indexing="ij")
        ii = ii.ravel(); jj = jj.ravel(); b = C.ravel()
        nvar = R + K; extra_rows = []
    else:
        ri, ci = np.meshgrid(np.arange(n), np.arange(m), indexing="ij")            # real block
        ii = [ri.ravel(), np.arange(n), n + np.arange(m)]
        jj = [ci.ravel(), m + np.arange(n), np.arange(m)]
        b = [C[:n, :m].ravel(), C[np.arange(n), m + np.arange(n)], C[n + np.arange(m), np.arange(m)]]
        ii = np.concatenate(ii); jj = np.concatenate(jj); b = np.concatenate(b)
        nvar = R + K + 2                                                            # + a, b
        extra_rows = True
    nz = len(ii)
    rows = np.repeat(np.arange(nz), 2); cols = np.column_stack([ii, R + jj]).ravel(); vals = np.ones(2 * nz)
    if extra_rows:
        # u_{n+j} - a <= 0 (m rows), v_{m+i} - b <= 0 (n rows), a + b <= 0 (1 row)
        r0 = nz
        ru = np.repeat(r0 + np.arange(m), 2); cu = np.column_stack([n + np.arange(m), np.full(m, R + K)]).ravel()
        vu = np.tile([1.0, -1.0], m)
        rv = np.repeat(r0 + m + np.arange(n), 2); cv = np.column_stack([R + m + np.arange(n), np.full(n, R + K + 1)]).ravel()
        vv = np.tile([1.0, -1.0], n)
        rab = np.array([r0 + m + n] * 2); cab = np.array([R + K, R + K + 1]); vab = np.array([1.0, 1.0])
        rows = np.concatenate([rows, ru, rv, rab]); cols = np.concatenate([cols, cu, cv, cab]); vals = np.concatenate([vals, vu, vv, vab])
        b = np.concatenate([b, np.zeros(m + n + 1)])
        nrows = nz + m + n + 1
    else:
        nrows = nz
    A = sp.csr_matrix((vals, (rows, cols)), shape=(nrows, nvar))
    c = -np.ones(nvar); c[R + K:] = 0.0
    # interior point + crossover: 4.5x faster than dual simplex on a 500x700 test, same exact vertex
    res = linprog(c=c, A_ub=A, b_ub=b, bounds=[(None, None)] * nvar, method="highs-ipm", options={"time_limit": time_limit})
    if res.status != 0:
        return None, res.message
    return res.x[:R], res.x[R:R + K]


def wasserstein_degree(X, Y, essX, essY, p: float, ground="lp", certify=True, cert_topk=None,
                       cert_full_max=1_000_000):
    """W_p^(k) between one degree's diagrams. Returns dict with the p-th power 'cost_p', the primal
    value, essential contribution, and the certificate: on the full diagram when n*m <= cert_full_max
    (the reduced dual LP has ~n*m constraints), otherwise on the cert_topk longest bars of each side --
    the scope is recorded in the certificate ('full' or 'top-k'); the primal is always on the full diagram."""
    X = np.asarray(X, float).reshape(-1, 2); Y = np.asarray(Y, float).reshape(-1, 2)
    essX = np.sort(np.asarray(essX, float)); essY = np.sort(np.asarray(essY, float))
    if len(essX) != len(essY):
        return {"cost_p": np.inf, "note": "different numbers of essential classes"}
    ess_p = float(np.sum(np.abs(essX - essY) ** p))
    out = {"n": int(len(X)), "m": int(len(Y)), "ess_cost_p": ess_p}
    if len(X) + len(Y) == 0:
        out.update(cost_p=ess_p, finite_cost_p=0.0, certificate=None)
        return out
    C = augmented_matrix(X, Y, p, ground)
    rows, cols = linear_sum_assignment(C)
    fin_p = float(C[rows, cols].sum())
    out.update(finite_cost_p=fin_p, cost_p=fin_p + ess_p)
    if certify:
        scope = "full"
        Cc, rc, cc = C, rows, cols
        nc, mc = len(X), len(Y)
        if cert_topk is not None and len(X) * len(Y) > cert_full_max and (len(X) > cert_topk or len(Y) > cert_topk):
            def topk(P):
                if len(P) <= cert_topk:
                    return P
                return P[np.argsort(-(P[:, 1] - P[:, 0]))[:cert_topk]]
            Xk, Yk = topk(X), topk(Y)
            Cc = augmented_matrix(Xk, Yk, p, ground); rc, cc = linear_sum_assignment(Cc)
            nc, mc = len(Xk), len(Yk)
            scope = f"top-{cert_topk}"
        t0 = time.time()
        u, v = dual_potentials(Cc, nc, mc)
        if u is None:
            out["certificate"] = {"status": f"LP failed: {v}", "scope": scope}
        else:
            cert = check_certificate(Cc, rc, cc, u, v)
            cert.update(scope=scope, lp_seconds=round(time.time() - t0, 1),
                        primal_topk=float(Cc[rc, cc].sum()))
            out["certificate"] = cert
    return out


def wasserstein_total(dgm_f: dict, dgm_g: dict, p: float, ground="lp", certify=True, cert_topk=None,
                      cert_full_max=1_000_000):
    per_deg = {}
    tot = 0.0
    for k in sorted(dgm_f):
        r = wasserstein_degree(dgm_f[k][0], dgm_g[k][0], dgm_f[k][1], dgm_g[k][1], p, ground, certify, cert_topk,
                               cert_full_max)
        r["W"] = r["cost_p"] ** (1.0 / p)
        per_deg[k] = r
        tot += r["cost_p"]
    return tot ** (1.0 / p), per_deg


def trivial_bound(dgm_f: dict, dgm_g: dict, p: float, ground="lp") -> float:
    """Z_p = W_p(Dgm f, empty) + W_p(Dgm g, empty), finite parts only (both share the essential classes)."""
    def to_empty(d):
        s = 0.0
        for k in d:
            pts = np.asarray(d[k][0], float).reshape(-1, 2)
            if len(pts):
                s += float(np.sum(diag_cost(pts, p, ground) ** p))
        return s ** (1.0 / p)
    return to_empty(dgm_f) + to_empty(dgm_g)


# ----------------------------------------------------------------------------------------------------
# 4. Controls
# ----------------------------------------------------------------------------------------------------
def control_C2():
    """Eight-point cycle, hand values: ||f-g||_1 = ||f-g||_2 = 5/2, W_1 = W_2 = 5/2 (l_p ground), and
    the previous round's l^inf-ground W_1 on the same example = 7/4."""
    f = np.array([1, 5, 2, 6, 3, 7, 4, 8], float)
    g = f.copy(); g[5] = 4.5
    df = gudhi_diagrams(f, True); dg = gudhi_diagrams(g, True)
    uf_f, ess_f = h0_unionfind(f, True); uf_g, ess_g = h0_unionfind(g, True)
    res = {"Dgm0_f": df[0][0].tolist(), "Dgm0_g": dg[0][0].tolist(),
           "ess_f": df[0][1].tolist(), "ess_g": dg[0][1].tolist(),
           "unionfind_matches_gudhi": same_multiset(uf_f, df[0][0]) and same_multiset(uf_g, dg[0][0])
                                       and ess_f == df[0][1][0] and ess_g == dg[0][1][0]}
    exp = {"Dgm0_f": [[2, 5], [3, 6], [4, 7]], "Dgm0_g": [[2, 5], [3, 6], [4, 4.5]]}
    res["diagrams_as_hand"] = same_multiset(df[0][0], exp["Dgm0_f"]) and same_multiset(dg[0][0], exp["Dgm0_g"])
    # Hand values (amendment A1 of the pre-registration): W_1 = 5/2 (match (4,7)<->(4,4.5)); for p = 2
    # the diagonal route is cheaper, (3/sqrt2)^2 + (1/(2 sqrt2))^2 = 37/8, so W_2 = sqrt(37/8), NOT 5/2.
    hand_W = {1: 2.5, 2: float(np.sqrt(37 / 8))}
    for p in (1, 2):
        B = cell_norm(f, g, True, p, dims=("pixels", "vertices"))
        W, per = wasserstein_total(df, dg, p, "lp", certify=True)
        res[f"p{p}"] = {"B": B, "W": W, "W0": per[0]["W"], "cert": per[0]["certificate"],
                        "hand_B": 2.5, "hand_W": hand_W[p], "B_ok": abs(B - 2.5) < 1e-12,
                        "W_ok": abs(W - hand_W[p]) < 1e-12, "bound_holds": W <= B + 1e-12}
    Winf, per = wasserstein_total(df, dg, 1, "linf", certify=True)
    res["linf_W1"] = {"W": Winf, "hand": 1.75, "ok": abs(Winf - 1.75) < 1e-12,
                      "cert": per[0]["certificate"]}
    res["PASS"] = bool(res["unionfind_matches_gudhi"] and res["diagrams_as_hand"]
                       and res["p1"]["B_ok"] and res["p1"]["W_ok"] and res["p2"]["B_ok"] and res["p2"]["W_ok"]
                       and res["linf_W1"]["ok"]
                       and all(res[f"p{p}"]["cert"]["tight"] and res[f"p{p}"]["cert"]["feasible"] for p in (1, 2)))
    return res


def control_C1_random(seed=0, trials=6):
    """Union-find H0 == GUDHI H0 on random small arrays with every periodicity pattern (unit test)."""
    rng = np.random.default_rng(seed)
    ok = True; cases = []
    for t in range(trials):
        shape = (int(rng.integers(3, 9)), int(rng.integers(3, 9)))
        f = rng.integers(0, 6, size=shape).astype(float) + rng.random(shape) * (t % 2)   # ties on even t
        for per in [(True, True), (True, False), (False, True), (False, False)]:
            d = gudhi_diagrams(f, per); uf, ess = h0_unionfind(f, per)
            good = same_multiset(uf, d[0][0]) and abs(ess - d[0][1][0]) == 0 and len(d[0][1]) == 1
            ok &= bool(good); cases.append((shape, per, bool(good), int(len(uf))))
    return ok, cases


def control_C3(rho: np.ndarray, periodic):
    """Exact known answer on real data: raise the birth pixel of the deepest finite H0 bar by delta."""
    from quantumfluids.tda.cubical import minima_with_depth
    births, depths, ij = minima_with_depth(rho, periodic)
    d0 = gudhi_diagrams(rho, periodic)
    fin = d0[0][0]
    order = np.argsort(-depths)
    N, M = rho.shape
    chosen = None
    for idx in order:
        i, j = int(ij[idx][0]), int(ij[idx][1])
        if births[idx] == rho.min():
            continue                                   # the essential class: skip
        nb = [rho[(i + di) % N, (j + dj) % M] for di in (-1, 0, 1) for dj in (-1, 0, 1) if (di, dj) != (0, 0)]
        if all(rho[i, j] < x for x in nb):            # strict local minimum in 8-connectivity
            chosen = (i, j, float(births[idx]), float(depths[idx]), float(min(nb) - rho[i, j]))
            break
    if chosen is None:
        return {"PASS": False, "note": "no strict-minimum birth pixel found"}
    i, j, b, dep, gap = chosen
    delta = 0.01 * dep
    note = ""
    if delta >= gap:
        delta = 0.5 * gap; note = f"delta reduced to half the gap to the nearest neighbour ({gap:.3e})"
    g = rho.copy(); g[i, j] += delta
    dg = gudhi_diagrams(g, periodic)
    res = {"pixel": [i, j], "birth": b, "depth": dep, "delta": delta, "note": note}
    for p in (1, 2):
        B_all = cell_norm(rho, g, periodic, p)
        B_k0 = cell_norm(rho, g, periodic, p, dims=("vertices", "edges0", "edges1"))
        W, per = wasserstein_total(d0, dg, p, "lp", certify=False)
        exp_all = 9 ** (1 / p) * delta; exp_k0 = 8 ** (1 / p) * delta
        res[f"p{p}"] = {"B_all": B_all, "B_all_expected": exp_all, "B_k0": B_k0, "B_k0_expected": exp_k0,
                        "W": W, "W0": per[0]["W"], "W_expected": delta,
                        "ok": abs(B_all - exp_all) <= 1e-12 * exp_all and abs(B_k0 - exp_k0) <= 1e-12 * exp_k0
                              and abs(W - delta) <= 1e-9 * delta,
                        "slack": B_all / W if W > 0 else np.inf}
    res["PASS"] = bool(res["p1"]["ok"] and res["p2"]["ok"])
    return res


# ----------------------------------------------------------------------------------------------------
# 5. The seven pairs
# ----------------------------------------------------------------------------------------------------
def rho_of(path: Path, restrict: bool = False) -> np.ndarray:
    psi = np.load(path)
    if restrict:
        psi = psi[::2, ::2]
    dens = np.abs(psi) ** 2
    return dens / dens.mean()


def load_pairs():
    P = DATA
    pairs = {
        "R1": (rho_of(P / "psi_t5.npy", True), rho_of(P / "psi_n512_t5.npy"), (True, True)),
        "R2": (rho_of(P / "psi_t10.npy", True), rho_of(P / "psi_n512_t10.npy"), (True, True)),
        "R3": (rho_of(P / "psi_t20.npy", True), rho_of(P / "psi_n512_t20.npy"), (True, True)),
        "T1": (rho_of(P / "psi_t5.npy"), rho_of(P / "psi_t10.npy"), (True, True)),
        "T2": (rho_of(P / "psi_t10.npy"), rho_of(P / "psi_t20.npy"), (True, True)),
        "S1": (rho_of(P / "psi_sound_only.npy"), rho_of(P / "psi_t5.npy"), (True, True)),
    }
    f1, f2 = np.load(P / "f_S1_t80.npy"), np.load(P / "f_S2_t80.npy")
    pairs["P1"] = (f1 / f1.mean(), f2 / f2.mean(), (True, False))
    return pairs


def run_pair(name, f, g, periodic, cert_topk=None, verbose=True, cert_full_max=1_000_000):
    t0 = time.time()
    df, dg = gudhi_diagrams(f, periodic), gudhi_diagrams(g, periodic)
    uf_f, ess_f = h0_unionfind(f, periodic); uf_g, ess_g = h0_unionfind(g, periodic)
    c1 = same_multiset(uf_f, df[0][0]) and same_multiset(uf_g, dg[0][0]) and ess_f == df[0][1][0] and ess_g == dg[0][1][0]
    eps = float(np.max(np.abs(f - g)))
    out = {"pair": name, "shape": list(f.shape), "periodic": list(periodic), "eps_sup": eps, "C1_unionfind_ok": bool(c1),
           "bars": {k: [int(len(df[k][0])), int(len(dg[k][0])), int(len(df[k][1]))] for k in df}}
    for p in (1, 2):
        B_all = cell_norm(f, g, periodic, p)
        B_k0 = cell_norm(f, g, periodic, p, dims=("vertices", "edges0", "edges1"))
        W, per = wasserstein_total(df, dg, p, "lp", certify=True, cert_topk=cert_topk, cert_full_max=cert_full_max)
        Z = trivial_bound(df, dg, p, "lp")
        out[f"p{p}"] = {"B_all": B_all, "B_k0": B_k0, "W_total": W, "W0": per[0]["W"],
                        "W_by_degree": {k: per[k]["W"] for k in per},
                        "certificates": {k: per[k]["certificate"] for k in per},
                        "Z_trivial": Z, "slack_S": B_all / W if W > 0 else np.inf, "vacuity_V": B_all / Z,
                        "P1_i": bool(W <= B_all * (1 + 1e-12)), "P1_ii_k0": bool(per[0]["W"] <= B_k0 * (1 + 1e-12))}
    # cross-check with the previous round's convention: l^inf ground, top-30 finite H0 bars, no essential
    def top30(P):
        return P if len(P) <= 30 else P[np.argsort(-(P[:, 1] - P[:, 0]))[:30]]
    r = wasserstein_degree(top30(df[0][0]), top30(dg[0][0]), [], [], 1, "linf", certify=False)
    out["linf_top30_W1"] = r["cost_p"]
    out["P7"] = bool(r["cost_p"] <= out["p1"]["W0"] * (1 + 1e-12))
    out["seconds"] = round(time.time() - t0, 1)
    if verbose:
        print(f"[{name}] {f.shape} eps={eps:.4f} bars H0 {out['bars'][0]} | "
              + " | ".join(f"p={p}: B={out[f'p{p}']['B_all']:.4g} W={out[f'p{p}']['W_total']:.4g} Z={out[f'p{p}']['Z_trivial']:.4g} "
                           f"S={out[f'p{p}']['slack_S']:.3g} V={out[f'p{p}']['vacuity_V']:.3g}" for p in (1, 2))
              + f" | {out['seconds']}s", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--controls-only", action="store_true")
    ap.add_argument("--cert-topk", type=int, default=None,
                    help="when n*m exceeds --cert-full-max, certify on the k longest bars only (scope recorded)")
    ap.add_argument("--cert-full-max", type=int, default=1_000_000)
    ap.add_argument("--pairs", default="R1,R2,R3,T1,T2,S1,P1")
    ap.add_argument("--out", default=str(DATA / "wp_stability_results.json"))
    a = ap.parse_args()
    results = {"controls": {}}
    ok, cases = control_C1_random()
    results["controls"]["C1_random"] = {"PASS": ok, "cases": cases}
    print("C1 (union-find == GUDHI on random arrays, all periodicities):", "PASS" if ok else "FAIL")
    c2 = control_C2(); results["controls"]["C2"] = c2
    print("C2 (eight-point cycle, hand values):", "PASS" if c2["PASS"] else "FAIL",
          {k: (c2[k]["B"], c2[k]["W"]) for k in ("p1", "p2")}, "linf W1 =", c2["linf_W1"]["W"])
    if not (ok and c2["PASS"]):
        sys.exit("controls failed; stop")
    pairs = load_pairs()
    c3 = control_C3(pairs["T1"][0], pairs["T1"][2]); results["controls"]["C3"] = c3
    print("C3 (exact known answer on T1's first field):", "PASS" if c3["PASS"] else "FAIL",
          {k: (c3[k]["B_all"], c3[k]["W"], c3[k]["slack"]) for k in ("p1", "p2")}, c3.get("note", ""))
    if not c3["PASS"]:
        sys.exit("C3 failed; stop")
    if a.controls_only:
        Path(a.out).write_text(json.dumps(results, indent=1, default=float)); return
    results["pairs"] = {}
    for name in a.pairs.split(","):
        f, g, per = pairs[name]
        results["pairs"][name] = run_pair(name, f, g, per, cert_topk=a.cert_topk, cert_full_max=a.cert_full_max)
        Path(a.out).write_text(json.dumps(results, indent=1, default=float))
    # C4 (negative): T1's plan with T2's potentials must be rejected
    if {"T1", "T2"} <= set(results["pairs"]):
        f1, g1, per = pairs["T1"]; f2, g2, _ = pairs["T2"]
        d1f, d1g = gudhi_diagrams(f1, per), gudhi_diagrams(g1, per); d2f, d2g = gudhi_diagrams(f2, per), gudhi_diagrams(g2, per)
        k = a.cert_topk or 100
        def topk(P):
            return P if len(P) <= k else P[np.argsort(-(P[:, 1] - P[:, 0]))[:k]]
        C1m = augmented_matrix(topk(d1f[0][0]), topk(d1g[0][0]), 1, "lp"); r1, c1 = linear_sum_assignment(C1m)
        X2, Y2 = topk(d2f[0][0]), topk(d2g[0][0])
        C2m = augmented_matrix(X2, Y2, 1, "lp")
        u2, v2 = dual_potentials(C2m, len(X2), len(Y2))
        if C1m.shape == C2m.shape and u2 is not None:
            chk = check_certificate(C1m, r1, c1, u2, v2)
            results["controls"]["C4"] = {"PASS": not (chk["feasible"] and chk["tight"]), **chk}
        else:
            results["controls"]["C4"] = {"PASS": None, "note": f"shapes {C1m.shape} vs {C2m.shape}: potentials not transferable; "
                                                                "treated as a rejection by construction, recorded as not run"}
        print("C4 (negative, T1 plan with T2 potentials):", results["controls"]["C4"])
    Path(a.out).write_text(json.dumps(results, indent=1, default=float))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
