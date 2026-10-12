"""Periodic lattice sums (Ewald-type split of completely monotone kernels) with analytic gradients.

Kernel f(r^2) = int w(t) exp(-t r^2) dt.  Split at t=tau: real part (t>tau) summed in direct space,
long part (t<tau) summed in reciprocal space.  Energy per particle at unit number density:
    E = 1/(2N) sum_{i,j} sum_R' f(|x_i-x_j+R|^2),  cell volume V = N.
Kernels: GAUSS e^{-a r^2}; YUK e^{-k r}/r; RIESZ r^{-2m} (m integer).
"""
import math
import numpy as np
from numba import njit

GAUSS, YUK, RIESZ = 0, 1, 2
SQRTPI = math.sqrt(math.pi)
GAUSS_RECIP_MAX = 2.5     # Gaussians with a < this are summed purely in reciprocal space


@njit(cache=True)
def _Q(m, x):
    s = 1.0
    t = 1.0
    for k in range(1, m):
        t *= x / k
        s += t
    return math.exp(-x) * s


@njit(cache=True)
def _gam_half(j, x):
    """Upper incomplete gamma Gamma(1/2 - j, x)."""
    g = SQRTPI * math.erfc(math.sqrt(x))
    a = 0.5
    for k in range(j):
        g = (g - x ** (a - 1.0) * math.exp(-x)) / (a - 1.0)
        a -= 1.0
    return g


@njit(cache=True)
def _fact(n):
    r = 1.0
    for k in range(2, n + 1):
        r *= k
    return r


@njit(cache=True)
def real_kernel(kind, p, tau, r2):
    """(phi, dphi/dr2) of the short-range part."""
    if kind == 0:
        v = math.exp(-p * r2)
        return v, -p * v
    elif kind == 1:
        r = math.sqrt(r2)
        st = math.sqrt(tau)
        a = st * r + p / (2.0 * st)
        b = st * r - p / (2.0 * st)
        ea = math.exp(p * r) * math.erfc(a)
        eb = math.exp(-p * r) * math.erfc(b)
        F = 0.5 * (ea + eb)
        gau = math.exp(-tau * r2 - p * p / (4.0 * tau))
        Fp = 0.5 * p * (ea - eb) - (2.0 / SQRTPI) * st * gau
        phi = F / r
        dphidr = Fp / r - F / r2
        return phi, dphidr / (2.0 * r)
    else:
        m = int(p)
        x = tau * r2
        rs = r2 ** (-m)
        return rs * _Q(m, x), -m * rs / r2 * _Q(m + 1, x)


@njit(cache=True)
def recip_kernel(kind, p, tau, g2):
    """(hhat, dhhat/dg2) of the long-range part (3D Fourier transform)."""
    if kind == 0:
        h = (math.pi / p) ** 1.5 * math.exp(-g2 / (4.0 * p))
        return h, -h / (4.0 * p)
    elif kind == 1:
        c = p * p + g2
        h = 4.0 * math.pi * math.exp(-c / (4.0 * tau)) / c
        return h, -h * (1.0 / c + 1.0 / (4.0 * tau))
    else:
        m = int(p)
        u0 = g2 / (4.0 * tau)
        gm = _fact(m - 1)
        pre = math.pi ** 1.5
        h = pre * (g2 / 4.0) ** (m - 1.5) * _gam_half(m - 1, u0) / gm
        dh = -0.25 * pre * (g2 / 4.0) ** (m - 2.5) * _gam_half(m - 2, u0) / gm
        return h, dh


@njit(cache=True)
def zero_terms(kind, p, tau):
    """(hhat(0), long-part value at r=0)."""
    if kind == 0:
        return (math.pi / p) ** 1.5, 1.0
    elif kind == 1:
        e = math.exp(-p * p / (4.0 * tau))
        return (4.0 * math.pi * e / (p * p),
                2.0 * math.sqrt(tau / math.pi) * e - p * math.erfc(p / (2.0 * math.sqrt(tau))))
    else:
        m = int(p)
        gm = _fact(m - 1)
        return (math.pi ** 1.5 * tau ** (m - 1.5) / ((m - 1.5) * gm), tau ** m / (m * gm))


@njit(cache=True)
def _inv3(A):
    a, b, c = A[0, 0], A[0, 1], A[0, 2]
    d, e, f = A[1, 0], A[1, 1], A[1, 2]
    g, h, i = A[2, 0], A[2, 1], A[2, 2]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    B = np.empty((3, 3))
    B[0, 0] = (e * i - f * h) / det
    B[0, 1] = (c * h - b * i) / det
    B[0, 2] = (b * f - c * e) / det
    B[1, 0] = (f * g - d * i) / det
    B[1, 1] = (a * i - c * g) / det
    B[1, 2] = (c * d - a * f) / det
    B[2, 0] = (d * h - e * g) / det
    B[2, 1] = (b * g - a * h) / det
    B[2, 2] = (a * e - b * d) / det
    return B, det


@njit(cache=True)
def energy_grad(kind, p, tau, rc2, gc2, use_real, use_recip, A, S):
    """Energy per particle and gradients wrt A (3x3 rows=lattice vectors, volume free) and S (N x 3 fractional)."""
    N = S.shape[0]
    Ainv, V = _inv3(A)
    gA = np.zeros((3, 3))
    gS = np.zeros((N, 3))
    E = 0.0
    h0, self0 = zero_terms(kind, p, tau)
    rc = math.sqrt(rc2)
    if use_real:
        nmax = np.empty(3, dtype=np.int64)
        for k in range(3):
            nrm = math.sqrt(Ainv[0, k] ** 2 + Ainv[1, k] ** 2 + Ainv[2, k] ** 2)
            nmax[k] = int(math.ceil(rc * nrm + 0.5))
        invN = 1.0 / N
        # self images (each i identical): (1/N)*N*(1/2) sum_{n!=0}
        for n0 in range(-nmax[0], nmax[0] + 1):
            for n1 in range(-nmax[1], nmax[1] + 1):
                for n2 in range(-nmax[2], nmax[2] + 1):
                    if n0 == 0 and n1 == 0 and n2 == 0:
                        continue
                    d0 = n0 * A[0, 0] + n1 * A[1, 0] + n2 * A[2, 0]
                    d1 = n0 * A[0, 1] + n1 * A[1, 1] + n2 * A[2, 1]
                    d2 = n0 * A[0, 2] + n1 * A[1, 2] + n2 * A[2, 2]
                    r2 = d0 * d0 + d1 * d1 + d2 * d2
                    if r2 < rc2:
                        ph, dph = real_kernel(kind, p, tau, r2)
                        E += 0.5 * ph
                        un = (n0, n1, n2)
                        dd = (d0, d1, d2)
                        for a in range(3):
                            for b in range(3):
                                gA[a, b] += dph * un[a] * dd[b]
        for i in range(N):
            for j in range(i + 1, N):
                D0 = S[i, 0] - S[j, 0]
                D1 = S[i, 1] - S[j, 1]
                D2 = S[i, 2] - S[j, 2]
                D0 -= np.rint(D0)
                D1 -= np.rint(D1)
                D2 -= np.rint(D2)
                for n0 in range(-nmax[0], nmax[0] + 1):
                    u0 = D0 + n0
                    for n1 in range(-nmax[1], nmax[1] + 1):
                        u1 = D1 + n1
                        for n2 in range(-nmax[2], nmax[2] + 1):
                            u2 = D2 + n2
                            d0 = u0 * A[0, 0] + u1 * A[1, 0] + u2 * A[2, 0]
                            d1 = u0 * A[0, 1] + u1 * A[1, 1] + u2 * A[2, 1]
                            d2 = u0 * A[0, 2] + u1 * A[1, 2] + u2 * A[2, 2]
                            r2 = d0 * d0 + d1 * d1 + d2 * d2
                            if r2 < rc2:
                                if r2 < 1e-12:
                                    r2 = 1e-12
                                ph, dph = real_kernel(kind, p, tau, r2)
                                E += invN * ph
                                c2 = 2.0 * dph * invN
                                uu = (u0, u1, u2)
                                dd = (d0, d1, d2)
                                for a in range(3):
                                    for b in range(3):
                                        gA[a, b] += c2 * uu[a] * dd[b]
                                    gi = c2 * (A[a, 0] * d0 + A[a, 1] * d1 + A[a, 2] * d2)
                                    gS[i, a] += gi
                                    gS[j, a] -= gi
        # self-image gradient already includes factor: dph*n*d (=(1/N)*N*(1/2)*2*dph)
    if use_recip:
        gc = math.sqrt(gc2)
        nm = np.empty(3, dtype=np.int64)
        for k in range(3):
            nrm = math.sqrt(A[k, 0] ** 2 + A[k, 1] ** 2 + A[k, 2] ** 2)
            nm[k] = int(gc * nrm / (2.0 * math.pi))
        # G = 0
        E += 0.5 * N * h0 / V
        for a in range(3):
            for b in range(3):
                gA[a, b] -= 0.5 * N * h0 / V * Ainv[b, a]
        E -= 0.5 * self0
        cs = np.empty(N)
        sn = np.empty(N)
        for m0 in range(0, nm[0] + 1):
            for m1 in range(-nm[1], nm[1] + 1):
                for m2 in range(-nm[2], nm[2] + 1):
                    if m0 == 0 and (m1 < 0 or (m1 == 0 and m2 <= 0)):
                        continue
                    # G_a = 2pi sum_b Ainv[a,b] m_b
                    G0 = 2.0 * math.pi * (Ainv[0, 0] * m0 + Ainv[0, 1] * m1 + Ainv[0, 2] * m2)
                    G1 = 2.0 * math.pi * (Ainv[1, 0] * m0 + Ainv[1, 1] * m1 + Ainv[1, 2] * m2)
                    G2 = 2.0 * math.pi * (Ainv[2, 0] * m0 + Ainv[2, 1] * m1 + Ainv[2, 2] * m2)
                    g2 = G0 * G0 + G1 * G1 + G2 * G2
                    if g2 >= gc2:
                        continue
                    h, dh = recip_kernel(kind, p, tau, g2)
                    Sr = 0.0
                    Si = 0.0
                    for i in range(N):
                        th = 2.0 * math.pi * (m0 * S[i, 0] + m1 * S[i, 1] + m2 * S[i, 2])
                        cs[i] = math.cos(th)
                        sn[i] = math.sin(th)
                        Sr += cs[i]
                        Si += sn[i]
                    S2 = Sr * Sr + Si * Si
                    k = 2.0 / (2.0 * N * V)
                    E += k * h * S2
                    # dA
                    w0 = G0 * Ainv[0, 0] + G1 * Ainv[1, 0] + G2 * Ainv[2, 0]
                    w1 = G0 * Ainv[0, 1] + G1 * Ainv[1, 1] + G2 * Ainv[2, 1]
                    w2 = G0 * Ainv[0, 2] + G1 * Ainv[1, 2] + G2 * Ainv[2, 2]
                    ww = (w0, w1, w2)
                    GG = (G0, G1, G2)
                    cf = k * S2
                    for a in range(3):
                        for b in range(3):
                            gA[a, b] += cf * (dh * (-2.0 * ww[a] * GG[b]) - h * Ainv[b, a])
                    # dS
                    mm = (m0, m1, m2)
                    for i in range(N):
                        dS2 = 2.0 * (Si * cs[i] - Sr * sn[i])
                        for a in range(3):
                            gS[i, a] += k * h * 2.0 * math.pi * mm[a] * dS2
    return E, gA, gS


@njit(cache=True)
def energy_grad_norm(kind, p, tau, rc2, gc2, use_real, use_recip, A0, S):
    """Same with A = s*A0 enforcing det A = N; gradient wrt A0."""
    N = S.shape[0]
    _, det0 = _inv3(A0)
    sgn = 1.0
    if det0 < 0:
        sgn = -1.0          # inversion x -> -x leaves the energy unchanged
        A0 = -A0
        det0 = -det0
    s = (N / det0) ** (1.0 / 3.0)
    A = s * A0
    E, gA, gS = energy_grad(kind, p, tau, rc2, gc2, use_real, use_recip, A, S)
    A0inv, _ = _inv3(A0)
    dot = 0.0
    for a in range(3):
        for b in range(3):
            dot += gA[a, b] * A0[a, b]
    gA0 = np.empty((3, 3))
    for a in range(3):
        for b in range(3):
            gA0[a, b] = sgn * (s * gA[a, b] - s * dot / 3.0 * A0inv[b, a])
    return E, gA0, gS


class Kernel:
    """Kernel + summation settings."""
    def __init__(self, name, param, tau=3.0, xc=55.0, xcg=45.0):
        self.name, self.param = name, float(param)
        self.kind = {'gauss': GAUSS, 'yukawa': YUK, 'riesz': RIESZ}[name]
        if self.kind == RIESZ:
            assert abs(param - round(param)) < 1e-12 and round(param) >= 2   # param = m = s/2
        self.tau = tau
        if self.kind == GAUSS:
            if param < GAUSS_RECIP_MAX:
                self.use_real, self.use_recip = False, True
                self.rc2, self.gc2 = 1.0, 4.0 * param * xcg
                self.tau = param
            else:
                self.use_real, self.use_recip = True, False
                self.rc2, self.gc2 = xcg / param, 1.0
                self.tau = param
        else:
            self.use_real = self.use_recip = True
            self.rc2 = xc / tau
            self.gc2 = 4.0 * tau * xc

    def eg(self, A0, S):
        A0 = np.asarray(A0, float)
        d = abs(np.linalg.det(A0))
        if not np.isfinite(d) or d < 1e-4 * np.prod(np.linalg.norm(A0, axis=1)):
            # numerically degenerate cell (line-search excursion): huge energy, no gradient
            return 1e8, np.zeros((3, 3)), np.zeros(np.shape(S))
        N = np.shape(S)[0]
        As = A0 * (N / d) ** (1 / 3) if np.linalg.det(A0) > 0 else -A0 * (N / d) ** (1 / 3)
        Ai = np.linalg.inv(As)
        nreal = np.prod(2 * (math.sqrt(self.rc2) * np.linalg.norm(Ai, axis=0) + 1) + 1)
        nrec = np.prod(2 * (math.sqrt(self.gc2) * np.linalg.norm(As, axis=1) / (2 * math.pi)) + 1)
        if (self.use_real and nreal > 60000) or (self.use_recip and nrec > 60000):
            # extremely skewed cell reached in a line search: treat as prohibitively expensive/high energy
            return 1e8, np.zeros((3, 3)), np.zeros(np.shape(S))
        return energy_grad_norm(self.kind, self.param, self.tau, self.rc2, self.gc2,
                                self.use_real, self.use_recip, A0, S)

    def label(self):
        if self.kind == RIESZ:
            return f"riesz_s{int(2*self.param)}"
        return f"{self.name}_{self.param:.6g}"


class MixKernel:
    """Gaussian mixture f(r) = e^{-a1 r^2} + lam e^{-a2 r^2} (round 2, T2; added 2026-10-12).

    Implemented as the sum of two independent Gaussian `Kernel` objects (energy and gradients are linear in
    the kernel), so nothing in the existing kernels or the numba engine is changed.  `force` = (f1, f2) with
    fi in {None, 'real', 'recip'} overrides the real/reciprocal branch of each component (verification only);
    `xcg` is the dimensionless Gaussian cutoff (default 45 as in round 1)."""
    def __init__(self, a1, a2, lam, xcg=45.0, force=(None, None)):
        self.name = 'mix'
        self.a1, self.a2, self.lam = float(a1), float(a2), float(lam)
        self.param = (self.a1, self.a2, self.lam)
        self.k1 = Kernel('gauss', a1, xcg=xcg)
        self.k2 = Kernel('gauss', a2, xcg=xcg)
        for k, f in ((self.k1, force[0]), (self.k2, force[1])):
            if f == 'real':
                k.use_real, k.use_recip, k.rc2, k.gc2 = True, False, xcg / k.param, 1.0
            elif f == 'recip':
                k.use_real, k.use_recip, k.rc2, k.gc2 = False, True, 1.0, 4.0 * k.param * xcg

    def eg(self, A0, S):
        E1, gA1, gS1 = self.k1.eg(A0, S)
        E2, gA2, gS2 = self.k2.eg(A0, S)
        return E1 + self.lam * E2, gA1 + self.lam * gA2, gS1 + self.lam * gS2

    def label(self):
        return f"mix_{self.a1:.6g}_{self.a2:.6g}_{self.lam:.9g}"


def grid_kernels(**kw):
    out = []
    for a in np.logspace(-1, 1, 13):
        out.append(Kernel('gauss', a, **kw))
    for k in np.logspace(-1, 1, 13):
        out.append(Kernel('yukawa', k, **kw))
    for s in (4, 6, 12):
        out.append(Kernel('riesz', s // 2, **kw))
    return out


# ---------------- cell reduction ----------------
def reduce_cell(A, S):
    """Greedy Minkowski-type reduction. Returns A', S' (same crystal), det>0."""
    A = np.array(A, float)
    T = np.eye(3)
    for _ in range(200):
        changed = False
        for i in range(3):
            for j in range(3):
                if i == j:
                    continue
                mu = np.rint(A[i] @ A[j] / (A[j] @ A[j]))
                if mu != 0:
                    A[i] -= mu * A[j]
                    T[i] -= mu * T[j]
                    changed = True
        for i in range(3):
            j, k = [x for x in range(3) if x != i]
            best = A[i] @ A[i]
            for e1 in (-1, 0, 1):
                for e2 in (-1, 0, 1):
                    if e1 == 0 and e2 == 0:
                        continue
                    v = A[i] + e1 * A[j] + e2 * A[k]
                    if v @ v < best - 1e-12:
                        best = v @ v
                        bv = (e1, e2)
            if best < A[i] @ A[i] - 1e-12:
                A[i] = A[i] + bv[0] * A[j] + bv[1] * A[k]
                T[i] = T[i] + bv[0] * T[j] + bv[1] * T[k]
                changed = True
        if not changed:
            break
    order = np.argsort((A * A).sum(1), kind='stable')
    A, T = A[order], T[order]
    if np.linalg.det(A) < 0:
        A[2] = -A[2]
        T[2] = -T[2]
    S2 = S @ np.linalg.inv(T)
    return A, S2
