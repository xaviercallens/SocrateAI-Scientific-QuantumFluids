"""Independent numpy implementation of the edge-study energies/forces, the lattice reference and the LDA reference."""
import numpy as np
from scipy.optimize import brentq
from scipy.interpolate import CubicSpline
from scipy.integrate import quad
from edge_kernel import U_ungated, dU_ungated, U_gated_K0, dU_gated_K0

D_OF = {"g3": 3.0, "g10": 10.0}


def pair(kid):
    """(phi, dphi) callables on arrays of r."""
    if kid == "dip":
        return (lambda r: U_ungated(r, 1.0)), (lambda r: dU_ungated(r, 1.0))
    if kid == "r3":
        return (lambda r: 1.0 / r**3), (lambda r: -3.0 / r**4)
    D = D_OF[kid]
    def f(r):
        r = np.asarray(r, float)
        out = U_gated_K0(r.ravel(), 1.0, D).reshape(r.shape)
        return np.where(r >= 36.0, 0.0, out)
    def g(r):
        r = np.asarray(r, float)
        out = dU_gated_K0(r.ravel(), 1.0, D).reshape(r.shape)
        return np.where(r >= 36.0, 0.0, out)
    return f, g


def polygon(cid, area):
    def rect(p, q):
        w = np.sqrt(area * p / q); h = area / w
        return np.array([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]])
    if cid == "square": return rect(1, 1)
    if cid == "rect32": return rect(3, 2)
    if cid == "rect21": return rect(2, 1)
    if cid == "rect31": return rect(3, 1)
    if cid == "tri":
        s = np.sqrt(4 * area / np.sqrt(3)); rc = s / np.sqrt(3)
        a = np.pi / 2 + np.arange(3) * 2 * np.pi / 3
        return rc * np.c_[np.cos(a), np.sin(a)]
    if cid == "hex":
        s = np.sqrt(2 * area / (3 * np.sqrt(3)))
        a = np.arange(6) * np.pi / 3
        return s * np.c_[np.cos(a), np.sin(a)]
    raise ValueError(cid)


def energy_force(kid, cid, area, kappa, ktrap, x):
    """returns (e_int, e_wall, f) with f = -grad(e_int + e_wall); x shape (N,2)."""
    phi, dphi = pair(kid)
    n = len(x)
    iu = np.triu_indices(n, 1)
    d = x[iu[0]] - x[iu[1]]
    r = np.hypot(d[:, 0], d[:, 1])
    e_int = float(np.sum(phi(r)))
    c = -dphi(r) / r
    f = np.zeros_like(x)
    np.add.at(f, iu[0], c[:, None] * d)
    np.add.at(f, iu[1], -c[:, None] * d)
    e_w = 0.0
    if cid == "trap":
        e_w = 0.5 * ktrap * float(np.sum(x * x)); f -= ktrap * x
    elif cid == "disk":
        R = np.sqrt(area / np.pi); rr = np.hypot(x[:, 0], x[:, 1]); s = np.maximum(rr - R, 0.0)
        e_w = 0.5 * kappa * float(np.sum(s * s)); f -= kappa * (s / np.where(rr > 0, rr, 1.0))[:, None] * x
    else:
        V = polygon(cid, area)
        for i in range(len(V)):
            a, b = V[i], V[(i + 1) % len(V)]
            t = b - a; nrm = np.array([t[1], -t[0]]) / np.hypot(*t)
            s = np.maximum(x @ nrm - nrm @ a, 0.0)
            e_w += 0.5 * kappa * float(np.sum(s * s)); f -= kappa * s[:, None] * nrm[None, :]
    return e_int, e_w, f


def spacing(rho):
    return np.sqrt(2.0 / (np.sqrt(3.0) * rho))


def e_lat(kid, rho, R=None):
    """energy per particle (unordered pairs) of the triangular lattice of density rho, plus the continuum tail for 'dip'."""
    a = spacing(rho)
    if R is None:
        R = 200.0 if kid == "dip" else 36.0
    m = int(R / (a * np.sqrt(3) / 2)) + 3
    i, j = np.meshgrid(np.arange(-m - int(R / a), m + int(R / a) + 1), np.arange(-m, m + 1))
    x = a * (i + 0.5 * j); y = a * (np.sqrt(3) / 2) * j
    r = np.hypot(x, y); r = r[(r > 1e-9) & (r <= R)]
    phi, _ = pair(kid)
    s = 0.5 * float(np.sum(phi(r)))
    if kid == "dip":
        s += 2 * np.pi * rho * (np.sqrt(R * R + 1.0) - R)
    return s


class LDA:
    """Local-density reference for the harmonic trap V = k r^2/2:  f(rho) = rho e_lat(rho);
    mu = f'(rho_c) fixes the centre density rho_c; N = (2 pi / k)(rho_c f' - f)(rho_c); E = (2 pi / k) int_0^rho_c f''(f + (mu - f') rho) d rho.
    (r^2 = 2 (mu - f'(rho)) / k is a monotone change of variables.)  The LDA is a reference, not a bound."""
    def __init__(self, kid):
        self.rlo = 1e-5 if kid in ('dip', 'r3') else 0.02   # gated kernels vanish beyond 36 d: below this density e_lat underflows
        rhos = np.geomspace(self.rlo, 0.8, 120)
        e = np.array([e_lat(kid, r) for r in rhos])
        self.spl = CubicSpline(np.log(rhos), np.log(rhos * e))
        self.kid = kid
    def _d(self, rho):
        l = np.log(rho)
        s = float(self.spl(l)); s1 = float(self.spl(l, 1)); s2 = float(self.spl(l, 2))
        f = np.exp(s)
        return f, f * s1 / rho, f * (s1 * s1 + s2 - s1) / rho**2
    def solve(self, N, rho_c):
        f, fp, _ = self._d(rho_c)
        mu = fp
        k = 2 * np.pi * (rho_c * fp - f) / N
        def integrand(rho):
            ff, f1, f2 = self._d(rho)
            return f2 * (ff + (mu - f1) * rho)
        E = 2 * np.pi / k * quad(integrand, self.rlo, rho_c, epsabs=1e-12, epsrel=1e-10, limit=200)[0]
        rmax = np.sqrt(2 * (mu - 0.0) / k)
        return k, E, rmax
