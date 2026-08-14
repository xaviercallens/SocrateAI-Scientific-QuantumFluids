#!/usr/bin/env python3
# TIER C - EXPLORATORY, NO CLAIMS
"""Verification for the M2/W4 design memo -- NOT a repository test.

Reproduces the numbers quoted in docs/designs/M2_W4_DISPERSIVE_SHELL.md
sections 2a, 2b and 3, so that the audit of that memo can check its
mathematics rather than take it on trust.

STATUS: this is a Tier C scratch check, not a Tier B harness. It has no
negative controls and asserts nothing. Per the memo's section 8, promoting
it to a proper Tier B test (with negative controls, per LL-2) is the FIRST
implementation step after the memo is audited -- not a retrofit afterwards.

Run:  python3 exploration/verify_complexification.py

Checks the memo's load-bearing mathematical claims BEFORE they are written
down as fact (LL-7: do not trust internally-consistent-but-unchecked math).

Claims under test:
  C1. The real dyadic nonlinearity B_n = k_{n-1}a_{n-1}^2 - k_n a_n a_{n+1}
      conserves E = 1/2 sum a_n^2.  (baseline, known)
  C2. The NAIVE complexification (same formula, complex a) does NOT conserve
      E = 1/2 sum |a_n|^2.  (i.e. the problem is real)
  C3. The CONJUGATED complexification
        B_n = k_{n-1} a_{n-1}^2 - k_n conj(a_n) a_{n+1}
      DOES conserve E = 1/2 sum |a_n|^2.
  C4. C3 reduces exactly to the real model on real data (reals are an
      invariant subspace).
  C5. The viscous term -nu k^2 a dissipates; the quantum-pressure term
      -i D k^2 a is exactly energy-neutral.
"""

import numpy as np

rng = np.random.default_rng(20260814)


def k_arr(N):
    return 2.0 ** np.arange(N + 1)


def B_real(a, k):
    """Real dyadic nonlinearity, a_{-1}=a_{N+1}=0."""
    N = len(a) - 1
    out = np.zeros_like(a)
    for n in range(N + 1):
        a_nm1 = a[n - 1] if n - 1 >= 0 else 0.0
        k_nm1 = k[n - 1] if n - 1 >= 0 else 0.0
        a_np1 = a[n + 1] if n + 1 <= N else 0.0
        out[n] = k_nm1 * a_nm1 * a_nm1 - k[n] * a[n] * a_np1
    return out


def B_naive(a, k):
    """Naive complexification: identical formula, complex a."""
    N = len(a) - 1
    out = np.zeros_like(a, dtype=complex)
    for n in range(N + 1):
        a_nm1 = a[n - 1] if n - 1 >= 0 else 0.0
        k_nm1 = k[n - 1] if n - 1 >= 0 else 0.0
        a_np1 = a[n + 1] if n + 1 <= N else 0.0
        out[n] = k_nm1 * a_nm1 * a_nm1 - k[n] * a[n] * a_np1
    return out


def B_conj(a, k):
    """Conjugated complexification: B_n = k_{n-1}a_{n-1}^2 - k_n conj(a_n) a_{n+1}."""
    N = len(a) - 1
    out = np.zeros_like(a, dtype=complex)
    for n in range(N + 1):
        a_nm1 = a[n - 1] if n - 1 >= 0 else 0.0
        k_nm1 = k[n - 1] if n - 1 >= 0 else 0.0
        a_np1 = a[n + 1] if n + 1 <= N else 0.0
        out[n] = k_nm1 * a_nm1 * a_nm1 - k[n] * np.conj(a[n]) * a_np1
    return out


def dE_dt(a, B):
    """d/dt (1/2 sum |a_n|^2) = sum Re(conj(a_n) * B_n)."""
    return float(np.sum(np.real(np.conj(a) * B)))


N = 10
k = k_arr(N)
print("=" * 68)
print(f"Shell model verification, N={N}, k_n = 2^n")
print("=" * 68)

# --- C1: real model conserves energy -------------------------------------
worst = 0.0
for _ in range(200):
    a = rng.normal(size=N + 1)
    worst = max(worst, abs(dE_dt(a, B_real(a, k))))
print(f"C1  real dyadic      max |dE/dt| over 200 random states: {worst:.3e}")

# --- C2: naive complexification does NOT conserve ------------------------
vals = []
for _ in range(200):
    a = rng.normal(size=N + 1) + 1j * rng.normal(size=N + 1)
    vals.append(abs(dE_dt(a, B_naive(a, k))))
print(f"C2  naive complex    max |dE/dt|: {max(vals):.3e}   "
      f"median: {np.median(vals):.3e}   <-- expect LARGE (claim: fails)")

# --- C3: conjugated complexification conserves ---------------------------
worst = 0.0
for _ in range(200):
    a = rng.normal(size=N + 1) + 1j * rng.normal(size=N + 1)
    worst = max(worst, abs(dE_dt(a, B_conj(a, k))))
print(f"C3  conj. complex    max |dE/dt|: {worst:.3e}   <-- expect ~round-off")

# --- C4: reduction to the real model on real data ------------------------
worst = 0.0
for _ in range(200):
    a = rng.normal(size=N + 1)
    diff = B_conj(a.astype(complex), k) - B_real(a, k).astype(complex)
    worst = max(worst, float(np.max(np.abs(diff))))
print(f"C4  conj == real on real data, max abs diff: {worst:.3e}")

# imaginary part stays exactly zero => reals are an invariant subspace
a = rng.normal(size=N + 1).astype(complex)
print(f"C4b Im(B_conj) on real data, max |Im|: "
      f"{float(np.max(np.abs(np.imag(B_conj(a, k))))):.3e}")

# --- C5: linear regulator terms ------------------------------------------
nu, D = 0.03, 0.03
worst_visc, worst_qp = 0.0, 0.0
for _ in range(200):
    a = rng.normal(size=N + 1) + 1j * rng.normal(size=N + 1)
    visc = -nu * k**2 * a
    qp = -1j * D * k**2 * a
    worst_visc = min(worst_visc, dE_dt(a, visc))   # want strictly negative
    worst_qp = max(worst_qp, abs(dE_dt(a, qp)))    # want ~0
print(f"C5  viscous  -nu k^2 a : most-negative dE/dt = {worst_visc:.3e}  "
      f"<-- expect NEGATIVE (dissipates)")
print(f"C5  quantum  -i D k^2 a: max |dE/dt|         = {worst_qp:.3e}  "
      f"<-- expect ~0 (energy-neutral)")
print("=" * 68)
