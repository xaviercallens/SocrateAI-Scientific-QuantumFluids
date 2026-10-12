"""Formal (self-)duality of periodic configurations at unit density -- AS IMPLEMENTED HERE (2026-10-12).

Convention.  P = Lambda + {x_1..x_N}, |Lambda| = N (unit density).  Fourier transform fhat(xi) = int f(x) e^{-2 pi i xi.x} dx,
dual lattice Lambda* = {w : w.v in Z}.  Average pair sum  Sigma_f(P) = (1/N) sum_{j,k} sum_{v in Lambda} f(x_j - x_k + v)
(the N diagonal terms f(0) included).  Poisson summation gives  Sigma_f(P) = (1/N^2) sum_{w in Lambda*} fhat(w) |S(w)|^2,
S(w) = sum_j e^{2 pi i w.x_j}.
Formal duality (Cohn-Kumar-Schuermann 2009, Sec. VI, communicated by the parent from the paper, not read here):
P of density delta and Q of density 1/delta are formal duals if Sigma_f(P) = delta * Sigma_{fhat}(Q) for every Schwartz f.
At delta = 1 and Q = P (formal SELF-duality) this reads Sigma_f(P) = Sigma_{fhat}(P), i.e. the two measures
    mu_P = (1/N) sum_{j,k,v} delta_{x_j - x_k + v}          (pair-difference measure, weights 1/N)
    nu_P = (1/N^2) sum_{w in Lambda*} |S(w)|^2 delta_w       (structure-factor measure)
must agree on every fhat, hence (radial test functions only, which is all an energy comparison uses) their radial
projections must agree shell by shell: same shell radii, same shell weights.  mu_P(0) = nu_P(0) = 1 always.
Detector used: the first K = 40 non-zero shells of each side; mismatch = sum_s [(r_s^mu - r_s^nu)^2 + (w_s^mu - w_s^nu)^2].
Formal duality of P with Q (same convention) uses mu_P against nu_Q at unit density.
Smooth surrogate for the search: the same identity tested on the Gaussian family f = e^{-alpha r^2}, fhat = (pi/alpha)^{3/2}
e^{-pi^2 r^2/alpha}:  Theta_P(alpha) = (pi/alpha)^{3/2} Theta_P(pi^2/alpha) with Theta = Sigma_f = 2 E + 1, E being the
engine's energy per particle (`AB/lattsum.py`); the Laplace-transform uniqueness theorem makes the two conditions equivalent
for polynomially bounded discrete measures, but the acceptance criterion is the registered shell mismatch, not the surrogate.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'AB'))
import numpy as np
from lattsum import Kernel, reduce_cell

K_SHELLS = 40


def normalise(A0, S):
    A0 = np.asarray(A0, float)
    S = np.asarray(S, float)
    N = len(S)
    d = np.linalg.det(A0)
    A = A0 * (N / abs(d)) ** (1 / 3)
    if d < 0:
        A = -A
    return A, S - np.floor(S)


def _lattice_points(B, R):
    """All integer combinations m.B with |m.B| <= R (B rows = basis)."""
    Bi = np.linalg.inv(B)
    nmax = [int(math.ceil(R * np.linalg.norm(Bi[:, k]) + 1)) for k in range(3)]
    m = np.array(np.meshgrid(*[np.arange(-n, n + 1) for n in nmax], indexing='ij')).reshape(3, -1).T
    v = m @ B
    r = np.linalg.norm(v, axis=1)
    keep = r <= R
    return m[keep], v[keep], r[keep]


def pair_measure(A0, S, R):
    """Radii and weights (1/N per ordered pair) of x_j - x_k + v, |.| <= R, zero vector excluded."""
    A, S = normalise(A0, S)
    N = len(S)
    m, v, _ = _lattice_points(A, R + 2 * np.linalg.norm(A, axis=1).sum())
    rs, ws = [], []
    for j in range(N):
        for k in range(N):
            d = (S[j] - S[k]) @ A + v
            r = np.linalg.norm(d, axis=1)
            keep = (r <= R) & (r > 1e-9)
            rs.append(r[keep])
            ws.append(np.full(keep.sum(), 1.0 / N))
    return np.concatenate(rs), np.concatenate(ws)


def sf_measure(A0, S, R):
    """Radii of w in Lambda*, |w| <= R, w != 0, with weights |S(w)|^2 / N^2."""
    A, S = normalise(A0, S)
    N = len(S)
    Bs = np.linalg.inv(A).T
    m, w, r = _lattice_points(Bs, R)
    keep = r > 1e-9
    m, r = m[keep], r[keep]
    ph = 2 * np.pi * (m @ S.T)                     # (M, N)
    S2 = np.cos(ph).sum(1) ** 2 + np.sin(ph).sum(1) ** 2
    return r, S2 / N ** 2


def shells(r, w, tol=1e-6, wmin=1e-8, K=K_SHELLS):
    o = np.argsort(r)
    r, w = r[o], w[o]
    out = []
    i = 0
    while i < len(r):
        j = i
        while j + 1 < len(r) and r[j + 1] - r[i] < tol:
            j += 1
        wt = w[i:j + 1].sum()
        if wt >= wmin:
            out.append((float(np.average(r[i:j + 1], weights=w[i:j + 1])) if wt > 0 else float(r[i]), float(wt)))
        i = j + 1
        if len(out) >= K:
            break
    return out


def shell_lists(A0, S, K=K_SHELLS, R0=None):
    """(mu shells, nu shells) each with >= K entries (R grown until both have K shells)."""
    N = len(S)
    R = R0 or 2.5 * N ** (1 / 3)
    for _ in range(12):
        mu = shells(*pair_measure(A0, S, R), K=K)
        nu = shells(*sf_measure(A0, S, R), K=K)
        if len(mu) >= K and len(nu) >= K:
            return mu[:K], nu[:K]
        R *= 1.4
    return mu[:K], nu[:K]


def mismatch(P, Q=None, K=K_SHELLS):
    """L2 shell mismatch between mu_P and nu_Q (Q = P: self-duality)."""
    A0, S = P
    if Q is None:
        Q = P
    N = len(S)
    R = 2.5 * max(N, len(Q[1])) ** (1 / 3)
    for _ in range(12):
        mu = shells(*pair_measure(A0, S, R), K=K)
        nu = shells(*sf_measure(Q[0], Q[1], R), K=K)
        if len(mu) >= K and len(nu) >= K:
            break
        R *= 1.4
    mu, nu = mu[:K], nu[:K]
    n = min(len(mu), len(nu))
    mm = sum((mu[s][0] - nu[s][0]) ** 2 + (mu[s][1] - nu[s][1]) ** 2 for s in range(n))
    return mm, mu, nu


class SelfDualObjective:
    """Smooth surrogate M(A0,S) = sum_m [Theta(alpha_m) - (pi/alpha_m)^{3/2} Theta(pi^2/alpha_m)]^2 with engine gradients.
    Same .eg interface as a Kernel so AB/opt.minimize_structure can be reused unchanged."""
    def __init__(self, scales=None, xcg=45.0, n_alpha=40, smin=0.3, smax=1.0, relative=True):
        # Run 2 final choice: alpha = pi s, s in [0.1, 1] (broad test Gaussians, exponents 0.31-3.14).  The identity at
        # alpha and at pi^2/alpha is the same equation, so (0, pi] covers everything; broad Gaussians see the far shells
        # with polynomial rather than exponential suppression (with alpha >= 3.2 a start stalled at M = 5e-9, shell
        # mismatch 1.2: far shells weighted e^{-alpha (r^2 - r_1^2)} ~ 1e-7 were invisible).
        # Run 1 (2026-10-12, T1_run1_16alpha_*): 16 scales in [1.15, 6], ABSOLUTE residuals.  Flaw: the residual scales
        # with the pair sum X(alpha) = 2E(alpha) ~ e^{-1.3 alpha}, so M ~ 1e-12 carries no information (FCC, far from
        # self-dual, gives M = 3.7e-6); shell mismatch stayed O(1-30).
        # Run 2: RELATIVE residuals r = 1 - X_nu/X_mu with X_mu = Theta(alpha) - 1 = sum' e^{-alpha r^2} dmu and
        # X_nu = (pi/alpha)^{3/2} Theta(pi^2/alpha) - 1 = sum'_{w} e^{-alpha |w|^2} |S(w)|^2/N^2 (Poisson), both O(1) relative.
        # X_nu is formed by cancellation (c Theta(small) - 1), absolute error ~1e-16, so alpha is kept <= 5.5 pi where
        # X >= ~1e-10; the equation at alpha simultaneously tests mu - nu with e^{-alpha r^2} and with e^{-(pi^2/alpha) r^2}.
        if scales is None:
            scales = np.geomspace(smin, smax, n_alpha)
        self.relative = relative
        self.alphas = [math.pi * s for s in scales]
        self.ks = [(Kernel('gauss', a, xcg=xcg), Kernel('gauss', math.pi ** 2 / a, xcg=xcg), (math.pi / a) ** 1.5)
                   for a in self.alphas]

    def residuals(self, A0, S):
        res, gA, gS = [], [], []
        for k1, k2, c in self.ks:
            E1, gA1, gS1 = k1.eg(A0, S)
            E2, gA2, gS2 = k2.eg(A0, S)
            Xm, dXm_A, dXm_S = 2 * E1, 2 * gA1, 2 * gS1
            Xn, dXn_A, dXn_S = c * (2 * E2 + 1) - 1, 2 * c * gA2, 2 * c * gS2
            if self.relative:
                if Xm <= 1e-300:
                    return np.array([1e4]), [np.zeros((3, 3))], [np.zeros(np.shape(S))]
                res.append(1.0 - Xn / Xm)
                gA.append(-(dXn_A * Xm - Xn * dXm_A) / Xm ** 2)
                gS.append(-(dXn_S * Xm - Xn * dXm_S) / Xm ** 2)
            else:
                res.append(Xm - Xn)
                gA.append(dXm_A - dXn_A)
                gS.append(dXm_S - dXn_S)
        return np.array(res), gA, gS

    def eg(self, A0, S):
        res, gA, gS = self.residuals(A0, S)
        M = float((res ** 2).sum())
        if not np.isfinite(M) or M > 1e12:
            return 1e8, np.zeros((3, 3)), np.zeros(np.shape(S))
        GA = sum(2 * r * g for r, g in zip(res, gA))
        GS = sum(2 * r * g for r, g in zip(res, gS))
        return M, GA, GS


def is_lattice(A0, S, tol=1e-5):
    """P is a Bravais lattice iff every translation x_j - x_1 maps the point set to itself mod Lambda."""
    A, S = normalise(A0, S)
    N = len(S)
    if N == 1:
        return True
    for j in range(1, N):
        t = S[j] - S[0]
        for k in range(N):
            d = S + 0 - (S[k] + t)
            d -= np.rint(d)
            if np.min(np.linalg.norm(d @ A, axis=1)) > tol:
                return False
    return True


def energy_at_pi(A0, S):
    return Kernel('gauss', math.pi).eg(np.asarray(A0, float), np.asarray(S, float))[0]
