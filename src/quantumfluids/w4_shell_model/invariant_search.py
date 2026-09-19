"""Deterministic search for polynomial invariants of a truncated flow.

Implements docs/designs/DUAL_SCALE_SECOND_INVARIANT.md (audited 2026-09-19) and its addendum A1.
No trajectories are integrated anywhere: a functional F = sum_j c_j phi_j is conserved iff its Lie
derivative along the vector field vanishes at every state, i.e. iff c is a null vector of the matrix
M[s, j] = (L phi_j)(v_s) over sampled states v_s.

A monomial is a tuple of factors (index, is_conj). Real basis functionals are Re(m) and Im(m).
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np

Factor = tuple[int, bool]
Monomial = tuple[Factor, ...]


@dataclass(frozen=True)
class Functional:
    mono: Monomial
    part: str  # "re" or "im"
    label: str


def _eval_factor(V: np.ndarray, f: Factor) -> np.ndarray:
    col = V[:, f[0]]
    return np.conj(col) if f[1] else col


def lie_derivative(mono: Monomial, V: np.ndarray, dV: np.ndarray) -> np.ndarray:
    """(L m)(v) = sum over factor positions of (product of the others) * d(factor)/dt. Complex."""
    out = np.zeros(V.shape[0], dtype=complex)
    for j in range(len(mono)):
        term = _eval_factor(dV, mono[j])
        for i, f in enumerate(mono):
            if i != j:
                term = term * _eval_factor(V, f)
        out += term
    return out


def lie_matrix(basis: list[Functional], V: np.ndarray, dV: np.ndarray) -> np.ndarray:
    M = np.empty((V.shape[0], len(basis)))
    cache: dict[Monomial, np.ndarray] = {}
    for j, phi in enumerate(basis):
        if phi.mono not in cache:
            cache[phi.mono] = lie_derivative(phi.mono, V, dV)
        M[:, j] = cache[phi.mono].real if phi.part == "re" else cache[phi.mono].imag
    return M


def nullspace(M: np.ndarray, rel_tol: float = 1e-8) -> tuple[np.ndarray, np.ndarray]:
    """Columns of the returned matrix span the numerical nullspace; also returns singular values."""
    Mn = M / np.linalg.norm(M, axis=0, keepdims=True).clip(min=1e-300)  # column scaling
    _, s, Vt = np.linalg.svd(Mn, full_matrices=False)
    scale = np.linalg.norm(M, axis=0).clip(min=1e-300)
    null = Vt[s < rel_tol * s[0]].T / scale[:, None]
    return null, s


# ---------------------------------------------------------------- shell model

def shell_rhs(V: np.ndarray, k: np.ndarray, seam: str = "trunc", mu: float = 0.0, D: float = 0.0) -> np.ndarray:
    """dv_n/dt = k_{n-1} v_{n-1}^2 - k_n conj(v_n) v_{n+1} - i D k_n^2 v_n, rows of V are states.

    seam: 'trunc' v_{N+1} = 0 | 'gpe' v_{N+1} = i mu v_N^2 (conserving, CLAIM-016)
          | 'leak' v_{N+1} = v_{N-1} (neighbour-reading, leaks: negative control)
    """
    if seam == "trunc":
        top = np.zeros(V.shape[0], dtype=complex)
    elif seam == "gpe":
        top = 1j * mu * V[:, -1] ** 2
    elif seam == "leak":
        top = V[:, -2].copy()
    else:
        raise ValueError(f"unknown seam {seam!r}")
    Vext = np.concatenate([V, top[:, None]], axis=1)
    dV = -k[None, :] * np.conj(V) * Vext[:, 1:]
    dV[:, 1:] += k[None, :-1] * V[:, :-1] ** 2
    return dV - 1j * D * k[None, :] ** 2 * V


def quadratic_basis(n: int) -> list[Functional]:
    return [Functional(((i, True), (i, False)), "re", f"|v{i}|^2") for i in range(n)]


def quartic_basis(n: int) -> list[Functional]:
    """All real functionals Re/Im(conj(v_a)conj(v_b) v_c v_d), a<=b, c<=d, up to complex conjugation."""
    pairs = list(itertools.combinations_with_replacement(range(n), 2))
    out = []
    for ab, cd in itertools.combinations_with_replacement(pairs, 2):
        mono = ((ab[0], True), (ab[1], True), (cd[0], False), (cd[1], False))
        name = f"c{ab[0]}c{ab[1]}v{cd[0]}v{cd[1]}"
        out.append(Functional(mono, "re", "Re " + name))
        if ab != cd:
            out.append(Functional(mono, "im", "Im " + name))
    return out


def cubic_basis(n: int) -> list[Functional]:
    """Addendum A1 extension E1: Re/Im(conj(v_m)^2 v_{m+1}), the graded-phase-neutral cubics."""
    out = []
    for m in range(n - 1):
        mono = ((m, True), (m, True), (m + 1, False))
        out += [Functional(mono, "re", f"Re c{m}^2 v{m+1}"), Functional(mono, "im", f"Im c{m}^2 v{m+1}")]
    return out


def predicted_H(basis: list[Functional], k: np.ndarray, mu: float = 0.0, D: float = 0.0) -> np.ndarray:
    """Coefficient vector of H = sum 2^-n [D k_n^2 |v_n|^2 + k_n Im(conj(v_n)^2 v_{n+1})] + mu k_N 2^-N |v_N|^4 / 2."""
    N = len(k) - 1
    c = np.zeros(len(basis))
    for j, phi in enumerate(basis):
        for n in range(N + 1):
            if phi.label == f"|v{n}|^2":
                c[j] = D * k[n] ** 2 / 2.0 ** n
            if phi.label == f"Im c{n}^2 v{n+1}":
                c[j] = k[n] / 2.0 ** n
        if phi.label == f"Re c{N}c{N}v{N}v{N}":
            c[j] = 0.5 * mu * k[N] / 2.0 ** N
    return c


def sample_states(S: int, n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.normal(size=(S, n)) + 1j * rng.normal(size=(S, n))


def in_span(c: np.ndarray, null: np.ndarray) -> float:
    """Relative distance of c from span(null); 0 means c is in the nullspace."""
    if null.shape[1] == 0:
        return 1.0
    q, _ = np.linalg.qr(null)
    return float(np.linalg.norm(c - q @ (q.T @ c)) / np.linalg.norm(c))


# ---------------------------------------------------------------- GP positive control (1D lattice)

def gp_rhs(P: np.ndarray, modes: list[int], omega: np.ndarray, g: float) -> np.ndarray:
    """d psi_k/dt = -i (omega_k psi_k + g N_k), N as in lean_src/GPGalerkin.lean."""
    n = len(modes)
    Nl = np.zeros_like(P)
    for i1, i2, i3 in itertools.product(range(n), repeat=3):
        kk = modes[i1] + modes[i3] - modes[i2]
        if kk in modes:
            Nl[:, modes.index(kk)] += P[:, i1] * np.conj(P[:, i2]) * P[:, i3]
    return -1j * (omega[None, :] * P + g * Nl)


def gp_energy_coeffs(basis: list[Functional], modes: list[int], omega: np.ndarray, g: float) -> np.ndarray:
    """E = sum omega |psi|^2 + (g/2) sum_{k1+k3=k+k2} conj(psi_k) psi_k1 conj(psi_k2) psi_k3 in basis coordinates."""
    idx = {phi.label: j for j, phi in enumerate(basis)}
    c = np.zeros(len(basis))
    n = len(modes)
    for i in range(n):
        c[idx[f"|v{i}|^2"]] += omega[i]
    for a, b, p, q in itertools.product(range(n), repeat=4):  # conj a, conj b, p, q with a+b = p+q
        if modes[a] + modes[b] == modes[p] + modes[q]:
            ab, pq = tuple(sorted((a, b))), tuple(sorted((p, q)))
            sign_flip = ab > pq  # basis stores the monomial with ab <= pq; Re is symmetric
            key = (pq, ab) if sign_flip else (ab, pq)
            c[idx[f"Re c{key[0][0]}c{key[0][1]}v{key[1][0]}v{key[1][1]}"]] += g / 2
    return c
