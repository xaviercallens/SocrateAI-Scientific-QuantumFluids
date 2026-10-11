"""Kernels of the edge study (independent numpy/mpmath implementations).

All lengths in units of the electron-hole separation d = 1.  Pair energy U(r) = V_ee + V_hh - 2 V_eh (unordered-pair
energy; the factor 2 of the phase-1 'Bilayer' kernel).
 ungated:  U = 2/r - 2/sqrt(r^2+d^2)
 gated  :  symmetric grounded planes at z = +-D/2, layers at z = -+d/2.  Image series (docs/designs/EXCITON_FLUID_GATE_IMAGE_CM.md)
           and the equivalent Poisson/K0 series  U(r) = (8/D) sum_{k>=1} (1 - cos(2 pi k d/D)) K0(2 pi k r/D).
"""
import numpy as np
from scipy.special import k0, k1
import mpmath as mp


def U_ungated(r, d=1.0):
    r = np.asarray(r, float)
    return 2.0 / r - 2.0 / np.sqrt(r * r + d * d)


def dU_ungated(r, d=1.0):
    r = np.asarray(r, float)
    return -2.0 / r**2 + 2.0 * r / (r * r + d * d) ** 1.5


def _kgrid(r, D, tol=1e-18):
    # number of K0 terms: K0(x) ~ exp(-x): need 2 pi k r / D > 45
    kmax = int(np.ceil(45.0 * D / (2 * np.pi * max(float(np.min(r)), 1e-9)))) + 2
    return np.arange(1, kmax + 1, dtype=float)


def U_gated_K0(r, d, D):
    r = np.atleast_1d(np.asarray(r, float))
    out = np.empty_like(r)
    for i, ri in enumerate(r):
        k = _kgrid(ri, D)
        out[i] = (8.0 / D) * np.sum((1.0 - np.cos(2 * np.pi * k * d / D)) * k0(2 * np.pi * k * ri / D))
    return out


def dU_gated_K0(r, d, D):
    r = np.atleast_1d(np.asarray(r, float))
    out = np.empty_like(r)
    for i, ri in enumerate(r):
        k = _kgrid(ri, D)
        a = 2 * np.pi * k / D
        out[i] = -(8.0 / D) * np.sum((1.0 - np.cos(2 * np.pi * k * d / D)) * a * k1(a * ri))
    return out


def W_image_mp(r, d, D, dps=30):
    """Smooth part  W(r) = U(r) - 2/r + 2/sqrt(r^2+d^2)  from the image series (mpmath, Richardson over n)."""
    mp.mp.dps = dps
    r = mp.mpf(r); d = mp.mpf(d); D = mp.mpf(D)
    h = D / 2; P = 2 * D
    ze, zh = -d / 2, d / 2
    t = r * r
    def s(a):
        return 1 / mp.sqrt(t + a * a)
    # V(z,z0) = sum_n [ s(z - z0 - P n) - s(z - 2h + z0 - P n) ]
    def f(n):
        n = mp.mpf(n)
        ee = s(-P * n) - s(2 * ze - 2 * h - P * n)
        hh = s(-P * n) - s(2 * zh - 2 * h - P * n)
        eh = s(d - P * n) - s(ze + zh - 2 * h - P * n)
        return ee + hh - 2 * eh
    # n = 0 direct part removed: ee_direct + hh_direct - 2 eh_direct = 2/r - 2/sqrt(t+d^2)
    n0 = f(0) - (2 / r - 2 * s(d))
    tail = mp.nsum(lambda n: f(n) + f(-n), [1, mp.inf])
    return n0 + tail


def U_gated_image_mp(r, d, D, dps=30):
    r_ = mp.mpf(r)
    return W_image_mp(r, d, D, dps) + 2 / r_ - 2 / mp.sqrt(r_ * r_ + d * d)


if __name__ == "__main__":
    d = 1.0
    for D in (3.0, 10.0):
        for r in (0.3, 1.0, 2.5, 7.0):
            a = U_gated_K0(r, d, D)[0]
            b = float(U_gated_image_mp(r, d, D))
            print(D, r, a, b, abs(a - b) / abs(b))
