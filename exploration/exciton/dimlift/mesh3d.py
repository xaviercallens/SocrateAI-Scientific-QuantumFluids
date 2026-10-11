#!/usr/bin/env python3
"""E3 of dimlift/PREREG.md: periodic 3D point sets, CM-relaxed vs Lloyd/CVT vs Poisson, Delaunay tetra quality.
Usage: mesh3d.py <out.jsonl> [NS] [N]"""
import json, os, sys, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import Delaunay, cKDTree

KL = 6.0   # screening parameter times box length (box = 1)


def cm_energy(z, n, k=KL):
    X = z.reshape(n, 3)
    d = X[:, None, :] - X[None, :, :]
    d -= np.round(d)                       # minimum image
    r = np.sqrt((d ** 2).sum(-1)); np.fill_diagonal(r, 1.0)
    u = np.exp(-k * r) / r
    du = -np.exp(-k * r) * (k * r + 1) / r ** 2
    # cutoff at r = 0.5 (minimum image): shifted so the energy is continuous
    u0 = np.exp(-k * 0.5) / 0.5
    mask = (r < 0.5)
    np.fill_diagonal(mask, False)
    E = 0.5 * np.sum(np.where(mask, u - u0, 0.0))
    g = np.where(mask, du / r, 0.0)[:, :, None] * d
    return E, g.sum(1).ravel()


def relax_cm(X0):
    n = len(X0)
    res = minimize(cm_energy, X0.ravel(), args=(n,), jac=True, method="L-BFGS-B",
                   options=dict(maxiter=3000, gtol=1e-9, ftol=1e-14))
    return np.mod(res.x.reshape(n, 3), 1.0), res.fun


def lloyd(X0, rng, iters=40, ns=150000):
    X = X0.copy()
    for _ in range(iters):
        S = rng.random((ns, 3))
        tree = cKDTree(np.mod(X, 1.0), boxsize=1.0)
        _, idx = tree.query(S)
        # periodic centroid: unwrap each sample relative to its generator
        dlt = S - X[idx]; dlt -= np.round(dlt)
        sums = np.zeros_like(X); cnt = np.zeros(len(X))
        np.add.at(sums, idx, dlt); np.add.at(cnt, idx, 1)
        X = np.mod(X + sums / np.maximum(cnt, 1)[:, None], 1.0)
    return X


def tet_quality(X):
    n = len(X)
    shifts = np.array([[i, j, k] for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1)])
    P = np.vstack([X + s for s in shifts])
    tri = Delaunay(P)
    S = tri.simplices
    c = P[S].mean(1)
    keep = np.all((c >= 0) & (c < 1), axis=1)
    T = P[S[keep]]                                     # (m,4,3)
    a, b, c_, d = T[:, 0], T[:, 1], T[:, 2], T[:, 3]
    V = np.abs(np.einsum("ij,ij->i", b - a, np.cross(c_ - a, d - a))) / 6.0
    def area(p, q, r): return 0.5 * np.linalg.norm(np.cross(q - p, r - p), axis=1)
    A = area(a, b, c_) + area(a, b, d) + area(a, c_, d) + area(b, c_, d)
    rin = 3 * V / A
    # circumradius
    A_ = b - a; B_ = c_ - a; C_ = d - a
    num = (np.sum(A_ ** 2, 1)[:, None] * np.cross(B_, C_) + np.sum(B_ ** 2, 1)[:, None] * np.cross(C_, A_) +
           np.sum(C_ ** 2, 1)[:, None] * np.cross(A_, B_))
    den = 2 * np.einsum("ij,ij->i", A_, np.cross(B_, C_))
    R = np.linalg.norm(num, axis=1) / np.abs(den)
    rho = 3 * rin / R
    # min dihedral angle
    idx = [(0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2), (1, 2, 0, 3), (1, 3, 0, 2), (2, 3, 0, 1)]
    mind = np.full(len(T), np.pi)
    for i, j, k, l in idx:
        e = T[:, j] - T[:, i]
        e /= np.linalg.norm(e, axis=1)[:, None]
        u = T[:, k] - T[:, i]; v = T[:, l] - T[:, i]
        u = u - np.einsum("ij,ij->i", u, e)[:, None] * e; v = v - np.einsum("ij,ij->i", v, e)[:, None] * e
        cs = np.einsum("ij,ij->i", u, v) / (np.linalg.norm(u, axis=1) * np.linalg.norm(v, axis=1))
        mind = np.minimum(mind, np.arccos(np.clip(cs, -1, 1)))
    return dict(m=int(len(T)), rho_med=float(np.median(rho)), rho_p5=float(np.percentile(rho, 5)),
                rho_min=float(rho.min()), frac_rho_lt_0p3=float((rho < 0.3).mean()),
                dihed_min_deg=float(np.degrees(mind.min())), dihed_p5_deg=float(np.degrees(np.percentile(mind, 5))))


if __name__ == "__main__":
    out = sys.argv[1]; NS = int(sys.argv[2]) if len(sys.argv) > 2 else 30; N = int(sys.argv[3]) if len(sys.argv) > 3 else 432
    with open(out, "a") as fo:
        for s in range(NS):
            rng = np.random.default_rng(31337 + s)
            X0 = rng.random((N, 3))
            t0 = time.time()
            Xc, E = relax_cm(X0)
            Xl = lloyd(X0, rng)
            for name, X in (("poisson", X0), ("cm", Xc), ("cvt", Xl)):
                rec = dict(seed=s, N=N, method=name, **tet_quality(X))
                if name == "cm": rec["E"] = float(E)
                fo.write(json.dumps(rec) + "\n"); fo.flush()
            print(s, round(time.time() - t0, 1), flush=True)
