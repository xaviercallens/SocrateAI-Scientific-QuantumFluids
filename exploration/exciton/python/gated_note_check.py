#!/usr/bin/env python3
"""Numerical check of Theorem 1 of paper/gated_kernel_note.tex: image series U(r) against int exp(-r^2 s) mu(s) ds, mu from Eq. (mu)."""
import numpy as np
from scipy import integrate
h1, h2, ze, zh = 1.0, 1.5, 0.3, -0.4
l = h1 + h2; P = 2 * l
def K(r, z, zp, N=200000):
    n = np.arange(-N, N + 1)
    return np.sum(1/np.sqrt(r*r + (z - zp - P*n)**2) - 1/np.sqrt(r*r + (z + zp - 2*h1 - P*n)**2))
def U(r): return K(r, ze, ze) + K(r, zh, zh) - 2*K(r, ze, zh)
def mu(s):
    m = np.arange(1, 4000)
    phi = lambda z: np.sin(m*np.pi*(z + h2)/l)
    lam = (m*np.pi/l)**2
    return 4/(P*s)*np.sum(np.exp(-lam/(4*s))*(phi(ze) - phi(zh))**2)
for r in [0.3, 1.0, 2.5]:
    v, _ = integrate.quad(lambda s: np.exp(-r*r*s)*mu(s), 0, np.inf, limit=400)
    print(f"r={r}: image series {U(r):.12f}  Laplace integral {v:.12f}")
