#!/usr/bin/env python3
"""E1 (dimensional annealing) and E2 (flexible wall) of dimlift/PREREG.md.
Usage: dimlift.py <out.jsonl> <kernel dip|g3> <shape> [NS] [workers]
Containers/RSA starts/defect analysis are imported unchanged from exploration/exciton/rust/fenris-gated/python."""
import json, os, sys, time, zlib
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np
from scipy.optimize import minimize
from scipy.special import k0, k1
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
FGP = os.path.join(os.path.dirname(HERE), "rust", "fenris-gated", "python")
sys.path.insert(0, FGP)
import geometry as G
from study import analyse_state

D_OVER = 0.5   # electron-hole separation d
DGATE = 1.5    # gate separation D (D/d = 3)

# ---- kernels as functions of the (possibly lifted) distance r -------------------------------------------------------
def _dip(r):
    s = np.sqrt(r * r + D_OVER ** 2)
    return 2 / r - 2 / s, -2 / r ** 2 + 2 * r / s ** 3

_RG = np.concatenate([np.linspace(0.02, 1.0, 4000), np.linspace(1.0, 14.0, 6000)[1:]])
def _gated_exact(r):
    k = np.arange(1, 160)[:, None]
    a = 2 * np.pi * k / DGATE
    c = (1 - np.cos(2 * np.pi * k * D_OVER / DGATE))
    u = (8 / DGATE) * np.sum(c * k0(a * r[None, :]), axis=0)
    du = -(8 / DGATE) * np.sum(c * a * k1(a * r[None, :]), axis=0)
    return u, du
_UG, _DUG = _gated_exact(_RG)
def _gat(r):
    rr = np.clip(r, _RG[0], _RG[-1])
    return np.interp(rr, _RG, _UG), np.interp(rr, _RG, _DUG)

KERN = {"dip": _dip, "g3": _gat}

class Counter:
    n = 0

def energy_grad(X, W, g, lam=0.0):
    """E = sum_{i<j} g(|xi-xj|) + sum_{i,wall} g(|xi-w|) + lam*|extra|^2 ; X is n x D (D>=2); W is m x D fixed."""
    Counter.n += 1
    n = len(X)
    dXX = X[:, None, :] - X[None, :, :]
    r = np.sqrt((dXX ** 2).sum(-1)); np.fill_diagonal(r, 1.0)
    u, du = g(r)
    np.fill_diagonal(u, 0.0); np.fill_diagonal(du, 0.0)
    E = 0.5 * u.sum()
    F = (du / r)[:, :, None] * dXX
    gradX = F.sum(1)
    if len(W):
        dXW = X[:, None, :] - W[None, :, :]
        rw = np.sqrt((dXW ** 2).sum(-1))
        uw, duw = g(rw)
        E += uw.sum()
        gradX = gradX + ((duw / rw)[:, :, None] * dXW).sum(1)
    if X.shape[1] > 2 and lam > 0:
        E += lam * (X[:, 2:] ** 2).sum()
        gradX[:, 2:] += 2 * lam * X[:, 2:]
    return E, gradX


def _nearest_on_edges(Q, e0, e1):
    """Nearest point of the polygon edges (e0[k] -> e1[k]) to each row of Q, vectorised over edges."""
    v = e1 - e0                                   # (E,2)
    vv = np.maximum((v * v).sum(1), 1e-300)       # (E,)
    t = np.clip(((Q[:, None, :] - e0[None, :, :]) * v[None, :, :]).sum(-1) / vv[None, :], 0.0, 1.0)   # (m,E)
    pr = e0[None, :, :] + t[:, :, None] * v[None, :, :]                                           # (m,E,2)
    d = np.linalg.norm(Q[:, None, :] - pr, axis=-1)                                               # (m,E)
    k = np.argmin(d, axis=1)
    idx = np.arange(len(Q))
    return d[idx, k], pr[idx, k]


def make_container_penalty(shape, kappa=2000.0):
    """Quadratic penalty on the in-plane distance outside the container (first two coordinates only).
    The wall of the lifted problem is container x R^k: a point wall would leak into the extra dimensions."""
    e0 = shape._e0; e1 = shape._e1
    def pen(X):
        P = X[:, :2]
        out = ~shape.inside(P)
        E = 0.0; gr = np.zeros_like(X)
        if out.any():
            Q = P[out]
            best, proj = _nearest_on_edges(Q, e0, e1)
            diff = Q - proj
            E = kappa * (diff ** 2).sum()
            tmp = np.zeros((len(P), 2)); tmp[out] = 2 * kappa * diff
            gr[:, :2] = tmp
        return E, gr
    return pen


def project_inside(X, shape, margin=0.08):
    """Move in-plane points that left the container back to just inside (nearest boundary point + margin)."""
    X = X.copy(); P = X[:, :2]
    out = ~shape.inside(P)
    if out.any():
        Q = P[out]
        best, proj = _nearest_on_edges(Q, shape._e0, shape._e1)
        dirn = (proj - Q) / np.maximum(best, 1e-12)[:, None]
        newp = proj + margin * dirn
        Pn = P.copy(); Pn[out] = newp
        X[:, :2] = Pn
    return X


def relax(X0, W, g, lam=0.0, maxiter=2000, gtol=1e-8, extra=None):
    shp = X0.shape
    def f(z):
        E, gr = energy_grad(z.reshape(shp), W, g, lam)
        if extra is not None:
            Ee, ge = extra(z.reshape(shp))
            E += Ee; gr = gr + ge
        return E, gr.ravel()
    res = minimize(f, X0.ravel(), jac=True, method="L-BFGS-B",
                   options=dict(maxiter=maxiter, gtol=gtol, ftol=1e-15, maxcor=20))
    return res.x.reshape(shp), res.fun


def lifted_run(P0, wall2, g, k, rng, shape, sched=(0.02, 0.1, 0.5, 2.5, 12.5, 62.5)):
    n = len(P0)
    X = np.hstack([P0, 0.1 * rng.standard_normal((n, k))])
    W = np.hstack([wall2, np.zeros((len(wall2), k))])
    pen = make_container_penalty(shape)
    for lam in sched:
        X, _ = relax(X, W, g, lam=lam, maxiter=150, extra=pen)
        X = project_inside(X, shape)
    X2 = project_inside(X, shape)[:, :2].copy()
    X2, E = relax(X2, wall2, g, maxiter=2000, extra=pen)
    X2 = project_inside(X2, shape, margin=0.02)
    X2, E = relax(X2, wall2, g, maxiter=2000)
    return X2, E


# ---- flexible wall (E2): wall nodes slide along their ring ------------------------------------------------------------
class SlidingWall:
    def __init__(self, shape):
        self.shape = shape
        pts = shape.boundary
        # per-ring closed polylines through the nodes in order; parameter = index position + fraction -> slide via arclength
        self.rings = []
        start = 0
        ring_ids = []
        for r in shape.rings:
            pass
        # reconstruct rings: boundary nodes are stored ring after ring (see geometry.Shape)
        sizes = []
        for r in shape.rings:
            if r["kind"] == "circle":
                sizes.append(max(3, int(round(2 * np.pi * r["R"]))) * int(round(1.0 / shape.w)))
            else:
                poly = r["pts"]; m = len(poly)
                sizes.append(sum(max(1, int(round(np.linalg.norm(poly[(i + 1) % m] - poly[i])))) * int(round(1.0 / shape.w))
                                 for i in range(m)))
        idx = 0
        self.poly, self.s0, self.slide, self.corner = [], [], [], []
        for r, sz in zip(shape.rings, sizes):
            nodes = pts[idx:idx + sz]; idx += sz
            if r["kind"] == "circle":
                poly = G._circle_poly(r["R"], 4000)
            else:
                poly = np.asarray(r["pts"])
            seg = np.linalg.norm(np.roll(poly, -1, axis=0) - poly, axis=1)
            cum = np.concatenate([[0], np.cumsum(seg)])
            # arclength of each node by projection onto the polyline
            s = np.empty(len(nodes))
            for j, p in enumerate(nodes):
                v = np.roll(poly, -1, axis=0) - poly
                t = np.clip(((p - poly) * v).sum(1) / (v * v).sum(1), 0, 1)
                proj = poly + t[:, None] * v
                d = np.linalg.norm(p - proj, axis=1)
                i = int(np.argmin(d)); s[j] = cum[i] + t[i] * seg[i]
            corner = np.zeros(len(nodes), bool)
            if r["kind"] != "circle":
                for q in poly:
                    corner[int(np.argmin(np.linalg.norm(nodes - q, axis=1)))] = True
            self.poly.append((poly, cum)); self.s0.append(s); self.corner.append(corner)
        self.sizes = sizes

    def positions(self, s_list):
        out = []
        for (poly, cum), s in zip(self.poly, s_list):
            L = cum[-1]; s = np.mod(s, L)
            i = np.clip(np.searchsorted(cum, s, side="right") - 1, 0, len(poly) - 1)
            seg = np.roll(poly, -1, axis=0) - poly
            ln = np.linalg.norm(seg, axis=1)
            t = (s - cum[i]) / ln[i]
            out.append(poly[i] + t[:, None] * seg[i])
        return np.vstack(out)

    def tangents(self, s_list):
        out = []
        for (poly, cum), s in zip(self.poly, s_list):
            L = cum[-1]; s = np.mod(s, L)
            i = np.clip(np.searchsorted(cum, s, side="right") - 1, 0, len(poly) - 1)
            seg = np.roll(poly, -1, axis=0) - poly
            ln = np.linalg.norm(seg, axis=1)
            out.append(seg[i] / ln[i][:, None])
        return np.vstack(out)


def sliding_run(P0, sw, g):
    """Relax free nodes and sliding wall nodes together (corners fixed)."""
    n = len(P0)
    s0 = np.concatenate(sw.s0); free_mask = ~np.concatenate(sw.corner)
    nw = len(s0)
    def unpack(z):
        X = z[:2 * n].reshape(n, 2)
        s = s0.copy(); s[free_mask] = z[2 * n:]
        return X, s
    def f(z):
        X, s = unpack(z)
        splits = np.cumsum(sw.sizes)[:-1]
        sl = np.split(s, splits)
        Wp = sw.positions(sl); T = sw.tangents(sl)
        Counter.n += 1
        # free-free and free-wall
        dXX = X[:, None, :] - X[None, :, :]
        r = np.sqrt((dXX ** 2).sum(-1)); np.fill_diagonal(r, 1.0)
        u, du = g(r); np.fill_diagonal(u, 0); np.fill_diagonal(du, 0)
        E = 0.5 * u.sum(); gX = ((du / r)[:, :, None] * dXX).sum(1)
        dXW = X[:, None, :] - Wp[None, :, :]
        rw = np.sqrt((dXW ** 2).sum(-1)); uw, duw = g(rw)
        E += uw.sum()
        Fw = (duw / rw)[:, :, None] * dXW            # dE/dx_i from each wall node
        gX += Fw.sum(1)
        # wall nodes: dE/dWp = -Fw summed over free nodes ; plus wall-wall energy
        gW = -Fw.sum(0)
        dWW = Wp[:, None, :] - Wp[None, :, :]
        rww = np.sqrt((dWW ** 2).sum(-1)); np.fill_diagonal(rww, 1.0)
        uww, duww = g(rww); np.fill_diagonal(uww, 0); np.fill_diagonal(duww, 0)
        E += 0.5 * uww.sum()
        gW += ((duww / rww)[:, :, None] * dWW).sum(1)
        gs = (gW * T).sum(1)
        return E, np.concatenate([gX.ravel(), gs[free_mask]])
    z0 = np.concatenate([P0.ravel(), s0[free_mask]])
    res = minimize(f, z0, jac=True, method="L-BFGS-B", options=dict(maxiter=3000, gtol=1e-8, ftol=1e-15, maxcor=20))
    X, s = unpack(res.x)
    Wp = sw.positions(np.split(s, np.cumsum(sw.sizes)[:-1]))
    return X, Wp, res.fun


def distinct(Es, tol=1e-6):
    Es = np.sort(np.asarray(Es)); out = []
    for e in Es:
        if not out or abs(e - out[-1]) > tol * abs(out[-1]):
            out.append(e)
    return len(out)


def one(args):
    kern, shape_name, seed, method = args
    g = KERN[kern]
    nf = 60
    shape = G.fit_shape(shape_name, nf, w=0.5)
    rng = np.random.default_rng(zlib.crc32(shape_name.encode()) % (2 ** 31) + 7919 * seed)
    P0 = shape.sample_rsa(shape.n_free, rng)
    wall2 = shape.boundary
    Counter.n = 0
    t0 = time.time()
    rec = dict(kern=kern, shape=shape_name, seed=seed, method=method, n=shape.n_free)
    dww = np.sqrt(((wall2[:, None, :] - wall2[None, :, :]) ** 2).sum(-1)); np.fill_diagonal(dww, 1.0)
    uww = g(dww)[0]; np.fill_diagonal(uww, 0.0)
    rec["Eww0"] = float(0.5 * uww.sum())
    site_idx = np.array([int(np.argmin(np.linalg.norm(wall2 - p, axis=1))) for p in shape.sites])
    if method == "direct":
        X, E = relax(P0, wall2, g, maxiter=2000)
        Wp = wall2
    elif method.startswith("lift"):
        k = int(method[4:])
        X, E = lifted_run(P0, wall2, g, k, rng, shape)
        Wp = wall2
    elif method == "slide":
        sw = SlidingWall(shape)
        X, Wp, E = sliding_run(P0, sw, g)
    else:
        raise ValueError(method)
    rec["E"] = float(E) + (0.0 if method == "slide" else rec["Eww0"]); rec["evals"] = Counter.n; rec["secs"] = time.time() - t0
    inside = shape.inside(X)
    rec["escaped"] = int((~inside).sum())
    try:
        # triangulation uses the w=1 'sites' as fixed nodes (positions of slid sites are not tracked: use nearest nodes)
        fixed = Wp[site_idx]
        a = analyse_state(shape, fixed, X)
        c = a["c"]
        rec["n_non6"] = int((c != 6).sum()); rec["Q"] = int(a["Q"]); rec["euler_ok"] = bool(a["euler_ok"])
        rec["conforming"] = bool(a["conforming"])
    except Exception as ex:
        rec["analysis_error"] = str(ex)[:80]
    return rec


if __name__ == "__main__":
    out, kern, shape_name = sys.argv[1], sys.argv[2], sys.argv[3]
    NS = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    W = int(sys.argv[5]) if len(sys.argv) > 5 else 2
    methods = sys.argv[6].split(",") if len(sys.argv) > 6 else ["direct", "lift1", "lift2", "slide"]
    jobs = [(kern, shape_name, s, m) for s in range(NS) for m in methods]
    with Pool(W) as p, open(out, "a") as fo:
        for rec in p.imap_unordered(one, jobs):
            fo.write(json.dumps(rec) + "\n"); fo.flush()
