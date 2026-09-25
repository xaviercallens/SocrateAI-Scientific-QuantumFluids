"""Torus point-vortex energy and a microcanonical vortex thermometer (Onsager), for the causal-topology stream.

Pair energy on the doubly periodic square, Weiss & McWilliams, Phys. Fluids A 3, 835 (1991), eq. (12), box side 2π:
    h(x, y) = Σ_m ln[(cosh(x − 2πm) − cos y) / cosh(2πm)] − x²/(2π),
    H = −Σ_{i<j} κ_i κ_j h(x_ij, y_ij),   κ_i = ±1,   with zero total circulation and zero vortex momentum P = Σ κ_i r_i.
Known answer (their Sec. III, N = 6, P = 0, 10 000 random configurations): mean energy −0.28, rms 2.90.
Thermometer: S(E) = ln ρ(E) from the density of states of random P = 0 configurations, 1/T = dS/dE
(Onsager 1949; Gauthier et al. Science 364, 1264 (2019); Groszek et al. PRL 120, 034504 (2018)).
Nothing here is new physics; the point is to have the instrument with its known answer.
"""
from __future__ import annotations
import numpy as np

TWO_PI = 2 * np.pi


def h_pair(x: np.ndarray, y: np.ndarray, M: int = 4) -> np.ndarray:
    """W&M eq. (12) on the 2π box; x, y reduced to (−π, π]."""
    x = (x + np.pi) % TWO_PI - np.pi
    y = (y + np.pi) % TWO_PI - np.pi
    s = np.zeros_like(x, dtype=float)
    for m in range(-M, M + 1):
        s += np.log((np.cosh(x - TWO_PI * m) - np.cos(y)) / np.cosh(TWO_PI * m))
    return s - x ** 2 / TWO_PI


def energy(pos: np.ndarray, q: np.ndarray, L: float) -> float:
    """H in W&M units (κ = 1, box rescaled to 2π); pos in a box of side L."""
    p = pos * (TWO_PI / L)
    n = len(q)
    E = 0.0
    for i in range(n):
        dx = p[i + 1:, 0] - p[i, 0]; dy = p[i + 1:, 1] - p[i, 1]
        E -= float(np.sum(q[i] * q[i + 1:] * h_pair(dx, dy)))
    return E


def random_neutral_p0(n_pairs: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Neutral configuration on the 2π box with vortex momentum Σ κ r = 0 (mod 2π): the last vortex is placed to cancel it."""
    n = 2 * n_pairs
    q = np.r_[np.ones(n_pairs, int), -np.ones(n_pairs, int)]
    pos = rng.random((n, 2)) * TWO_PI
    P = (q[:-1, None] * pos[:-1]).sum(0)
    pos[-1] = (-P / q[-1]) % TWO_PI
    return pos, q


def density_of_states(n_pairs: int, n_samples: int, rng: np.random.Generator, bins: int = 60):
    E = np.array([energy(*random_neutral_p0(n_pairs, rng), TWO_PI) for _ in range(n_samples)])
    hist, edges = np.histogram(E, bins=bins, density=True)
    centres = 0.5 * (edges[:-1] + edges[1:])
    return E, centres, hist


def temperature_from_dos(centres: np.ndarray, hist: np.ndarray, E: float, smooth: int = 5) -> float:
    """1/T = d ln ρ / dE at E, from a local linear fit of ln ρ over ±smooth bins (nan outside the sampled range)."""
    ok = hist > 0
    c, s = centres[ok], np.log(hist[ok])
    j = int(np.argmin(np.abs(c - E)))
    lo, hi = max(0, j - smooth), min(len(c), j + smooth + 1)
    if hi - lo < 3 or not (c[0] <= E <= c[-1]):
        return float("nan")
    slope = np.polyfit(c[lo:hi], s[lo:hi], 1)[0]
    return float(1.0 / slope) if slope != 0 else float("inf")


if __name__ == "__main__":
    rng = np.random.default_rng(1991)
    # Known answer 1: a single dipole of separation d << L has energy ≈ ln(d) + const (2D Coulomb); slope check.
    for d in (0.1, 0.2, 0.4):
        pos = np.array([[np.pi, np.pi], [np.pi + d, np.pi]]); q = np.array([1, -1])
        print(f"dipole d={d}: E={energy(pos, q, TWO_PI):.4f}")
    # Known answer 2: W&M N = 6, P = 0: mean −0.28, rms 2.90 over 10 000 random configurations.
    E, c, hist = density_of_states(3, 10_000, rng)
    print(f"W&M known answer N=6, P=0: mean {E.mean():.3f} (paper −0.28), rms {E.std():.3f} (paper 2.90)")
