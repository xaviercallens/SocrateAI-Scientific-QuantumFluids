"""Observables of docs/designs/PGPE_BKT_PREREG.md §2 for a PGPE state c (projected Fourier amplitudes)."""
from __future__ import annotations
import numpy as np
from pgpe import PGPE


def thermometer(s: PGPE, occ: np.ndarray, lo: float, hi: float):
    """Classical equipartition fit 1/<n_k> = (eps_k + 2gn - mu)/T on k in [lo, hi]*k_cut. Returns (T, 2gn-mu)."""
    kk = np.sqrt(s.k2); eps = 0.5 * s.k2
    m = (kk >= lo * s.kcut) & (kk <= hi * s.kcut) & s.P & (occ > 0)
    x, y = eps[m], 1.0 / occ[m]
    A = np.vstack([x, np.ones_like(x)]).T
    slope, icpt = np.linalg.lstsq(A, y, rcond=None)[0]
    return float(1.0 / slope), float(icpt / slope)


def condensate_fraction(s: PGPE, c: np.ndarray) -> float:
    return float(np.abs(c[0, 0]) ** 2 * s.dx ** 2 / s.N ** 2 / s.norm(c))


def g1_radial(s: PGPE, c: np.ndarray, nbins: int | None = None):
    """First-order correlation g1(r) = <psi*(0) psi(r)> / n, azimuthally averaged (cyclic autocorrelation via FFT)."""
    corr = np.fft.ifft2(np.abs(c) ** 2).real          # sum_x psi*(x) psi(x+r)
    corr /= corr[0, 0]
    ix = np.fft.fftfreq(s.N, d=1.0 / s.N)              # lattice offsets -N/2..N/2-1
    RX, RY = np.meshgrid(ix, ix, indexing="ij")
    r = np.sqrt(RX ** 2 + RY ** 2) * s.dx
    nb = nbins or s.N // 2
    edges = np.linspace(0, s.L / 2, nb + 1)
    idx = np.digitize(r.ravel(), edges) - 1
    ok = (idx >= 0) & (idx < nb)
    num = np.bincount(idx[ok], weights=corr.ravel()[ok], minlength=nb)
    den = np.bincount(idx[ok], minlength=nb)
    rc = 0.5 * (edges[:-1] + edges[1:])
    good = den > 0
    return rc[good], num[good] / den[good]


def fit_g1(r: np.ndarray, g: np.ndarray, rmin: float, rmax: float):
    """Fit g1 on [rmin, rmax] as r^-eta (log-log) and as exp(-r/l) (log-lin); return both with residuals."""
    m = (r >= rmin) & (r <= rmax) & (g > 0)
    x, y = r[m], np.log(g[m])
    A1 = np.vstack([np.log(x), np.ones_like(x)]).T
    p1, res1 = np.linalg.lstsq(A1, y, rcond=None)[:2]
    A2 = np.vstack([x, np.ones_like(x)]).T
    p2, res2 = np.linalg.lstsq(A2, y, rcond=None)[:2]
    r1 = float(res1[0]) if len(res1) else float("nan"); r2 = float(res2[0]) if len(res2) else float("nan")
    return {"eta": float(-p1[0]), "res_alg": r1, "ell": float(-1.0 / p2[0]) if p2[0] < 0 else float("inf"),
            "res_exp": r2, "npts": int(m.sum())}


def vortices(s: PGPE, c: np.ndarray):
    """Vortex positions and charges by the phase-winding rule of lean_src/VortexWinding.lean: the sum of
    principal-value phase differences around each plaquette is an exact integer multiple of 2 pi."""
    th = np.angle(np.fft.ifft2(c))
    def pv(d):
        return (d + np.pi) % (2 * np.pi) - np.pi
    dx_ = pv(np.roll(th, -1, axis=0) - th)            # edge (i,j)->(i+1,j)
    dy_ = pv(np.roll(th, -1, axis=1) - th)            # edge (i,j)->(i,j+1)
    # plaquette (i,j): (i,j)->(i+1,j)->(i+1,j+1)->(i,j+1)->(i,j)
    w = dx_ + np.roll(dy_, -1, axis=0) - np.roll(dx_, -1, axis=1) - dy_
    q = np.rint(w / (2 * np.pi)).astype(int)
    ii, jj = np.nonzero(q)
    pos = np.column_stack([(ii + 0.5) * s.dx, (jj + 0.5) * s.dx])
    return pos, q[ii, jj]


def pairing(s: PGPE, pos: np.ndarray, q: np.ndarray, rpair: float):
    """Fraction of vortices that are NOT paired: paired = nearest opposite-sign neighbour closer than rpair
    and closer than the nearest same-sign neighbour (periodic distances)."""
    n = len(pos)
    if n == 0:
        return float("nan"), 0
    d = pos[:, None, :] - pos[None, :, :]
    d = d - s.L * np.round(d / s.L)
    dist = np.sqrt((d ** 2).sum(-1)); np.fill_diagonal(dist, np.inf)
    opp = q[:, None] != q[None, :]
    d_opp = np.where(opp, dist, np.inf).min(1)
    d_same = np.where(~opp, dist, np.inf).min(1)
    paired = (d_opp < rpair) & (d_opp < d_same)
    return float(1.0 - paired.mean()), int(n)


def current_correlators(s: PGPE, c: np.ndarray, shells=(1.0, np.sqrt(2.0), 2.0)):
    """<|J_L(k)|^2>, <|J_T(k)|^2> on the smallest |k| shells (units of 2 pi / L), J = Im(psi* grad psi)."""
    psi = np.fft.ifft2(c)
    gx = np.fft.ifft2(1j * s.kx * c); gy = np.fft.ifft2(1j * s.ky * c)
    Jx = (np.conj(psi) * gx).imag; Jy = (np.conj(psi) * gy).imag
    Jkx = np.fft.fft2(Jx) * s.dx ** 2; Jky = np.fft.fft2(Jy) * s.dx ** 2
    kk = np.sqrt(s.k2); dk = 2 * np.pi / s.L
    out = {}
    for sh in shells:
        m = np.abs(kk - sh * dk) < 1e-9
        kxh, kyh = s.kx[m] / kk[m], s.ky[m] / kk[m]
        JL = kxh * Jkx[m] + kyh * Jky[m]
        JT = kxh * Jky[m] - kyh * Jkx[m]
        out[round(float(sh), 4)] = (float(np.mean(np.abs(JL) ** 2)), float(np.mean(np.abs(JT) ** 2)))
    return out


def dipole_matching(s: PGPE, pos: np.ndarray, q: np.ndarray, rng: np.random.Generator, n_null: int = 4):
    """Amendment A2 (TDA instrument T1): the W1-optimal perfect matching of the +1 vortices to the -1 vortices
    (periodic distance), i.e. the 1-Wasserstein transport between the two signed point clouds. Returns
    (mean matched length l_d, same for charge-shuffled nulls l_null, ratio Q = l_d / l_null). Bound dipoles give
    Q << 1; an unbound plasma gives Q -> 1. No length scale is pre-set (unlike `pairing`'s 3 xi)."""
    from scipy.optimize import linear_sum_assignment
    if len(pos) < 4 or np.sum(q > 0) != np.sum(q < 0) or np.any(np.abs(q) != 1):
        return float("nan"), float("nan"), float("nan")

    def mean_len(qq):
        a, b = pos[qq > 0], pos[qq < 0]
        d = a[:, None, :] - b[None, :, :]
        d = d - s.L * np.round(d / s.L)
        D = np.sqrt((d ** 2).sum(-1))
        r, c = linear_sum_assignment(D)
        return float(D[r, c].mean())
    ld = mean_len(q)
    ln = float(np.mean([mean_len(rng.permutation(q)) for _ in range(n_null)]))
    return ld, ln, ld / ln


def onsager_dipole(s: PGPE, pos: np.ndarray, q: np.ndarray) -> float:
    """Periodic analogue of Gauthier et al. 2019's Onsager-cluster order parameter D = |mean_j sgn(Gamma_j) r_j|
    (Science 364, 1264, DOI 10.1126/science.aat5718): on their bounded trap D measures the vortex gas's offset
    from the trap centre. A periodic torus has no such centre, so the periodic-invariant analogue used here is
    the distance between the +1 and -1 sub-populations' own centroids (each a circular mean per axis, since a
    periodic domain has no absolute origin), normalised by L: D ~ 0 for a well-mixed (paired) gas; D grows as
    the two signs separate into distinct clusters. NOT claimed identical to Gauthier's D -- the geometry
    (bounded trap vs. periodic torus) differs; this is the natural adaptation, stated as such."""
    if len(pos) < 2 or np.sum(q > 0) == 0 or np.sum(q < 0) == 0:
        return float("nan")

    def centroid(p):
        ang = 2 * np.pi * p / s.L
        return (s.L / (2 * np.pi)) * np.angle(np.mean(np.exp(1j * ang), axis=0)) % s.L
    cp, cm = centroid(pos[q > 0]), centroid(pos[q < 0])
    d = cp - cm
    d = d - s.L * np.round(d / s.L)
    return float(np.sqrt((d ** 2).sum()) / s.L)
