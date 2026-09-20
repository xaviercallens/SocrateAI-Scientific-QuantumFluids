"""Split-step Fourier solver for the 2D Gross-Pitaevskii equation.

    i dpsi/dt = -1/2 Lap psi + g |psi|^2 psi - mu psi          (hbar = m = 1)

Written because the dataset survey (2026-09-20) established that NO public dilute-BEC dataset
resolves the healing length by 5 grid points or more -- the best available are 2.26 (2D) and 1.73
(3D), both within ~1.5x of the 1.5 that already made the TDA floor measurement inconclusive. The
measurement therefore needs a simulation of our own, at a resolution chosen so that the extraction
grid cannot be mistaken for the physics.

Units: g = 1, background density n0 = 1, so mu = 1, sound speed c = 1 and the healing length is
xi = 1/sqrt(2*mu). Set dx = xi/8.

The split-step scheme conserves the norm to machine precision by construction (both half-steps are
pointwise or Fourier-diagonal phase rotations), which makes norm drift a USELESS control -- it
cannot fail. Energy drift is the control that can, and the test suite uses it.

TIMESTEP. The Fourier half-step advances mode k by exp(-i dt k^2 / 2), so accuracy needs
`dt * k_max^2 / 2 << 1` with `k_max = pi/dx`. At dx = xi/8 that is dt << 0.0016, and a field with
white-noise phase (energy at the grid scale) really does need it: at dt = 0.005 the measured energy
drift was 33%. Use `max_dt`. A smooth field tolerates more, but the bound is what makes the
difference between a converged run and a plausible-looking wrong one.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Grid2D:
    n: int
    dx: float

    @property
    def L(self) -> float:
        return self.n * self.dx

    def coords(self) -> tuple[np.ndarray, np.ndarray]:
        x = np.arange(self.n) * self.dx
        return x[:, None], x[None, :]

    def k2(self) -> np.ndarray:
        k = 2 * np.pi * np.fft.fftfreq(self.n, d=self.dx)
        return k[:, None] ** 2 + k[None, :] ** 2


def healing_length(mu: float = 1.0) -> float:
    """xi = 1/sqrt(2 mu) in hbar = m = 1 units."""
    return 1.0 / np.sqrt(2.0 * mu)


def max_dt(grid: Grid2D, safety: float = 0.05) -> float:
    """Largest timestep for which the Fourier half-step stays accurate: `safety * 2/k_max^2`."""
    return float(safety * 2.0 / np.max(grid.k2()))


def smooth_phase_noise(grid: Grid2D, amp: float, k_cut_inv_xi: float,
                       rng: np.random.Generator, mu: float = 1.0) -> np.ndarray:
    """A random phase band-limited to `k < k_cut_inv_xi / xi` -- a physical initial condition, as
    opposed to white noise, which puts energy at the grid scale where no split-step is accurate."""
    xi = healing_length(mu)
    f = rng.normal(size=(grid.n, grid.n))
    kx = 2 * np.pi * np.fft.fftfreq(grid.n, d=grid.dx)
    k = np.sqrt(kx[:, None] ** 2 + kx[None, :] ** 2)
    fk = np.fft.fft2(f) * (k < k_cut_inv_xi / xi)
    ph = np.real(np.fft.ifft2(fk))
    ph *= amp / (np.std(ph) + 1e-30)
    return np.exp(1j * ph)


def step(psi: np.ndarray, grid: Grid2D, dt: complex, g: float = 1.0, mu: float = 1.0) -> np.ndarray:
    """One Strang split step. `dt` real = real time; `dt = -1j*tau` = imaginary time (relaxation)."""
    half = np.exp(-1j * dt * (g * np.abs(psi) ** 2 - mu) / 2)
    psi = half * psi
    psi = np.fft.ifft2(np.exp(-1j * dt * grid.k2() / 2) * np.fft.fft2(psi))
    return half * psi


def evolve(psi: np.ndarray, grid: Grid2D, dt: complex, n_steps: int, g: float = 1.0,
           mu: float = 1.0, renorm: bool = False) -> np.ndarray:
    for _ in range(n_steps):
        psi = step(psi, grid, dt, g, mu)
        if renorm:                       # imaginary time is not norm-preserving
            psi *= np.sqrt(grid.n ** 2 / np.sum(np.abs(psi) ** 2))
    return psi


def energy(psi: np.ndarray, grid: Grid2D, g: float = 1.0) -> float:
    """E = int [ |grad psi|^2 / 2 + g|psi|^4 / 2 ]. Kinetic part via Fourier (exact on the grid)."""
    psik = np.fft.fft2(psi)
    kin = 0.5 * np.sum(grid.k2() * np.abs(psik) ** 2) / psi.size
    inter = 0.5 * g * np.sum(np.abs(psi) ** 4)
    return float((kin + inter) * grid.dx ** 2)


def norm(psi: np.ndarray, grid: Grid2D) -> float:
    return float(np.sum(np.abs(psi) ** 2) * grid.dx ** 2)


def plant_vortices(grid: Grid2D, centres: np.ndarray, charges: np.ndarray,
                   n0: float = 1.0) -> np.ndarray:
    """Imprint a phase pattern with the given vortices; density is left flat.

    The cores are NOT put in by hand -- imaginary-time relaxation creates them, so the core profile
    is the solver's own solution rather than an ansatz. That is what makes the measured core size a
    result of the physics and not of the planting.

    Charges must sum to zero: a periodic box cannot carry net circulation.

    RELAX ONLY BRIEFLY. Imaginary time descends toward the LOWEST-energy state, which on a periodic
    box is the vortex-free uniform one, so it forms cores first and then destroys the vortices.
    Measured here for a +/- pair at dx = xi/8: the core is fully formed by tau ~ 2 (density at the
    core 7e-4), still fine at tau = 8, and by tau = 20 the vortices are GONE (core density back to
    0.97). Use tau ~ 2, then switch to real time, where vortices are dynamically stable.
    """
    if int(np.sum(charges)) != 0:
        raise ValueError(f"net charge {int(np.sum(charges))} != 0 is impossible on a periodic box")
    X, Y = grid.coords()
    phase = np.zeros((grid.n, grid.n))
    for (cx, cy), q in zip(centres, charges):
        dxp = (X - cx + grid.L / 2) % grid.L - grid.L / 2
        dyp = (Y - cy + grid.L / 2) % grid.L - grid.L / 2
        phase += q * np.arctan2(dyp, dxp)
    return np.sqrt(n0) * np.exp(1j * phase)


def radial_density_profile(psi: np.ndarray, grid: Grid2D, centre: tuple[float, float],
                           r_max: float, n_bins: int = 40) -> tuple[np.ndarray, np.ndarray]:
    """Azimuthally averaged |psi|^2 around a point -- used to measure a vortex core size."""
    X, Y = grid.coords()
    dxp = (X - centre[0] + grid.L / 2) % grid.L - grid.L / 2
    dyp = (Y - centre[1] + grid.L / 2) % grid.L - grid.L / 2
    r = np.hypot(dxp, dyp).ravel()
    rho = (np.abs(psi) ** 2).ravel()
    edges = np.linspace(0, r_max, n_bins + 1)
    idx = np.digitize(r, edges) - 1
    ok = (idx >= 0) & (idx < n_bins)
    prof = np.array([rho[ok][idx[ok] == b].mean() if np.any(idx[ok] == b) else np.nan
                     for b in range(n_bins)])
    return 0.5 * (edges[:-1] + edges[1:]), prof
