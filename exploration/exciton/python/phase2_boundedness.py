#!/usr/bin/env python3
"""Boundedness of the grand-canonical functional of the Phase 2 control kernel (amendment A3 of the Phase 2 pre-registration).

For a stripe with Gaussian profile c_m = nbar * exp(-m^2 k0^2 w^2 / 2) the interaction energy density is (1/2) nbar^2 F(w) with
    F(w) = U(0) + 2 * sum_{m >= 1} U(m k0) exp(-m^2 k0^2 w^2).
If min_w F < 0 the functional  Omega[psi] = int (1/2)|grad psi|^2 + (1/2) n (U * n) - mu n  has no minimum at fixed mu
(Omega -> -infinity as nbar grows).  Kernel B: U_B(k) = 4 pi (1 - exp(-k d)) / k, d = 1; kernel C: U_B - depth * exp(-(k-k0)^2/(2*0.2^2)),
k0 = 2 pi 3 / L, L = 16.  `grid` keeps the harmonics representable on the 16x16 grid (m <= 2), `continuum` m <= 8.

    python3 exploration/exciton/python/phase2_boundedness.py
"""
import math
import numpy as np

L = 16.0
k0 = 2 * math.pi * 3 / L

def UB(k):
    return 4 * math.pi * (1 - np.exp(-k)) / k

print(f"U_B(0) = {4 * math.pi:.4f}, U_B(k0) = {UB(k0):.4f}")
print("depth   min_w F (grid, m<=2)   min_w F (continuum, m<=8)   linearly unstable? (U_C(k0) < -eps_k0/(2 n0))")
n0 = 0.25 / (4 * math.pi)
for depth in (28, 24.8, 20, 18, 16, 12):
    UC = lambda k: UB(k) - depth * np.exp(-(k - k0) ** 2 / (2 * 0.2 ** 2))
    res = []
    for mmax in (2, 8):
        res.append(min(4 * math.pi + 2 * sum(UC(m * k0) * math.exp(-(m * k0 * w) ** 2) for m in range(1, mmax + 1))
                       for w in np.linspace(0.05, 3, 400)))
    unstable = UC(k0) < -(0.5 * k0 ** 2) / (2 * n0)
    print(f"{depth:5.1f}   {res[0]:10.3f}             {res[1]:10.3f}                  {unstable}")
