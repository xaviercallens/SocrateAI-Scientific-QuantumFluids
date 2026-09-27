"""Projected Gross-Pitaevskii equation (classical field) on a 2D periodic box, hbar = m = 1.

    i d/dt psi = P[ -1/2 Lap psi + g |psi|^2 psi ],   P = sharp cutoff |k| <= k_cut in Fourier space.

Pre-registered in docs/designs/PGPE_BKT_PREREG.md. Integrator: integrating-factor RK4 in Fourier space
(linear part exact, nonlinear part RK4), the scheme of LeanFlow's `step_etd_rk4`, dealiased by the
projector: k_cut <= k_max/2 makes the CUBIC term alias-free (the 2/3 rule is for quadratic terms; the
pre-registration first said 2/3 and control K3 -- momentum drift of 1 % -- caught it; amendment A1). The state is the array of projected
Fourier amplitudes c_k (numpy fft convention, unnormalised: psi = ifft2(c)).

Nothing here is new numerics; the point of the file is that every invariant and known answer of
PGPE_BKT_PREREG.md §1 is computable from it, and that `rhs_real` exposes the same ODE to an external
integrator (rusty-SUNDIALS CVODE) for the K6 cross-check.
"""
from __future__ import annotations

import numpy as np

# Vortex detection is done in `observables.py` with the phase-winding rule proved in lean_src/VortexWinding.lean.


class PGPE:
    def __init__(self, N: int = 128, L: float = 64.0, g: float = 1.0, kcut_frac: float = 1 / 2, dt: float = 0.01):
        self.N, self.L, self.g, self.dt = N, L, g, dt
        self.dx = L / N
        k1 = 2 * np.pi * np.fft.fftfreq(N, d=self.dx)
        self.kx, self.ky = np.meshgrid(k1, k1, indexing="ij")
        self.k2 = self.kx ** 2 + self.ky ** 2
        self.kmax = np.pi / self.dx
        self.kcut = kcut_frac * self.kmax
        self.P = (np.sqrt(self.k2) <= self.kcut)          # projector mask
        self.n_modes = int(self.P.sum())
        self.lin = -0.5j * self.k2                          # linear operator in Fourier space
        self.E1 = np.exp(self.lin * dt / 2) * self.P
        self.E2 = np.exp(self.lin * dt) * self.P
        self.set_dt(dt)

    def set_dt(self, dt: float):
        self.dt = dt
        self.E1 = np.exp(self.lin * dt / 2) * self.P
        self.E2 = np.exp(self.lin * dt) * self.P

    # ---- field <-> modes -------------------------------------------------------------------------
    def psi(self, c: np.ndarray) -> np.ndarray:
        return np.fft.ifft2(c)

    def modes(self, psi: np.ndarray) -> np.ndarray:
        return np.fft.fft2(psi) * self.P

    # ---- right-hand side and one IF-RK4 step -------------------------------------------------------
    def nonlin(self, c: np.ndarray) -> np.ndarray:
        """N(c) = -i g P[ FFT( |psi|^2 psi ) ]."""
        psi = np.fft.ifft2(c)
        return -1j * self.g * self.P * np.fft.fft2(np.abs(psi) ** 2 * psi)

    def rhs(self, c: np.ndarray) -> np.ndarray:
        """Full right-hand side dc/dt = L c + N(c), for external integrators."""
        return self.lin * c * self.P + self.nonlin(c)

    def step(self, c: np.ndarray) -> np.ndarray:
        dt, E1, E2 = self.dt, self.E1, self.E2
        a = self.nonlin(c)
        b = self.nonlin(E1 * (c + 0.5 * dt * a))
        cc = self.nonlin(E1 * c + 0.5 * dt * b)
        d = self.nonlin(E2 * c + dt * E1 * cc)
        return E2 * c + (dt / 6.0) * (E2 * a + 2.0 * E1 * (b + cc) + d)

    def run(self, c: np.ndarray, t_end: float, callback=None, every: int = 0) -> np.ndarray:
        n = int(round(t_end / self.dt))
        for i in range(1, n + 1):
            c = self.step(c)
            if callback is not None and every and i % every == 0:
                callback(i * self.dt, c)
        return c

    # ---- invariants ---------------------------------------------------------------------------------
    def norm(self, c: np.ndarray) -> float:
        """N = integral |psi|^2 = (dx^2 / N^2) sum |c_k|^2  (Parseval, numpy convention)."""
        return float(np.sum(np.abs(c) ** 2)) * self.dx ** 2 / self.N ** 2

    def energy(self, c: np.ndarray) -> float:
        psi = np.fft.ifft2(c)
        kin = float(np.sum(0.5 * self.k2 * np.abs(c) ** 2)) * self.dx ** 2 / self.N ** 2
        pot = 0.5 * self.g * float(np.sum(np.abs(psi) ** 4)) * self.dx ** 2
        return kin + pot

    def momentum(self, c: np.ndarray) -> np.ndarray:
        w = np.abs(c) ** 2 * self.dx ** 2 / self.N ** 2
        return np.array([float(np.sum(self.kx * w)), float(np.sum(self.ky * w))])

    # ---- real-vector view for external integrators (rusty-SUNDIALS / scipy) --------------------------
    def pack(self, c: np.ndarray) -> np.ndarray:
        v = c[self.P]
        return np.concatenate([v.real, v.imag])

    def unpack(self, y: np.ndarray) -> np.ndarray:
        m = self.n_modes
        c = np.zeros((self.N, self.N), dtype=complex)
        c[self.P] = y[:m] + 1j * y[m:]
        return c

    def rhs_real(self, t: float, y) -> np.ndarray:
        return self.pack(self.rhs(self.unpack(np.asarray(y, dtype=float))))

    # ---- initial states -----------------------------------------------------------------------------
    def uniform(self, n0: float = 1.0) -> np.ndarray:
        return self.modes(np.full((self.N, self.N), np.sqrt(n0), dtype=complex))

    def random_state(self, n0: float, e_target: float, rng: np.random.Generator, iters: int = 60) -> np.ndarray:
        """Random projected field with norm n0*L^2 and energy per particle e_target, by rescaling a
        random-phase spectrum |c_k| ~ exp(-k^2/(2 s^2)) and bisecting on s (the classical-field
        'random high-energy initial state' of Simula-Blakie; the trajectory then thermalises)."""
        phase = np.exp(2j * np.pi * rng.random((self.N, self.N)))
        Ntot = n0 * self.L ** 2

        def make(s):
            amp = np.exp(-self.k2 / (2 * s ** 2)) * self.P
            c = amp * phase
            c *= np.sqrt(Ntot / self.norm(c))
            return c
        lo, hi = 0.02, self.kcut
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            e = self.energy(make(mid)) / Ntot
            if e < e_target:
                lo = mid
            else:
                hi = mid
        return make(0.5 * (lo + hi))
