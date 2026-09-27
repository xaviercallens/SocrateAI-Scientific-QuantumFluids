"""1D1V Vlasov-Poisson, electrons on a neutralising background (pre-registration K2, K3).

    df/dt + v df/dx - E df/dv = 0,     dE/dx = 1 - rho,     rho = int f dv.

Strang splitting.  The x-advection f(x - v dt, v) is an exact Fourier shift.  The v-advection
f(x, v + E dt) is a cubic-spline semi-Lagrangian interpolation, zero outside [-vmax, vmax].

Two failure modes of this scheme are pinned by tests rather than hidden:
  * RECURRENCE.  The velocity quadrature rho = sum f dv aliases the free-streaming phase exp(-i k v t)
    at T_R = 2 pi / (k dv): the initial perturbation reappears.  It is not physical and no resolution
    removes it, only postpones it.
  * FILAMENTATION.  f develops v-structure of wavelength 2 pi/(k t); once that reaches a few dv the
    spline smooths it away.  The echo (K3) exists to test exactly this.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.interpolate import CubicSpline


def maxwellian(v, u=0.0):
    return np.exp(-0.5 * (v - u) ** 2) / np.sqrt(2 * np.pi)


@dataclass
class Grid:
    L: float
    nx: int
    nv: int
    vmax: float
    x: np.ndarray = field(init=False)
    v: np.ndarray = field(init=False)
    kx: np.ndarray = field(init=False)

    def __post_init__(self):
        self.x = np.arange(self.nx) * (self.L / self.nx)
        self.dv = 2 * self.vmax / self.nv
        self.v = -self.vmax + (np.arange(self.nv) + 0.5) * self.dv   # cell centres, symmetric about 0
        self.kx = 2 * np.pi * np.fft.fftfreq(self.nx, d=self.L / self.nx)

    def recurrence_time(self, mode: int = 1) -> float:
        return 2 * np.pi / (mode * 2 * np.pi / self.L * self.dv)


def density(f, g: Grid):
    return f.sum(axis=1) * g.dv


def field_from(f, g: Grid):
    rho_k = np.fft.fft(density(f, g))
    E_k = np.zeros_like(rho_k)
    nz = g.kx != 0
    E_k[nz] = 1j * rho_k[nz] / g.kx[nz]        # i k E_k = -rho_k  (the background cancels the k=0 part)
    return np.fft.ifft(E_k).real


def advect_x(f, g: Grid, dt):
    fk = np.fft.fft(f, axis=0)
    fk *= np.exp(-1j * g.kx[:, None] * g.v[None, :] * dt)
    return np.fft.ifft(fk, axis=0).real


def advect_v(f, g: Grid, E, dt):
    out = np.empty_like(f)
    for i in range(g.nx):
        s = CubicSpline(g.v, f[i], extrapolate=False)
        r = s(g.v + E[i] * dt)
        out[i] = np.where(np.isnan(r), 0.0, r)
    return out


def step(f, g: Grid, dt, field_on: bool = True):
    f = advect_x(f, g, 0.5 * dt)
    if field_on:
        f = advect_v(f, g, field_from(f, g), dt)
    return advect_x(f, g, 0.5 * dt)


def mode_amplitude(a, mode: int):
    """Complex Fourier amplitude c_m with a(x) = sum_m c_m exp(i m k0 x); cosine amplitude is 2 Re c_m."""
    return np.fft.fft(a)[mode] / a.size


def pulse(f, g: Grid, mode: int, amp: float):
    return f * (1 + amp * np.cos(mode * 2 * np.pi / g.L * g.x))[:, None]


def energy(f, g: Grid):
    dx = g.L / g.nx
    kin = 0.5 * (f * g.v[None, :] ** 2).sum() * g.dv * dx
    return kin + 0.5 * (field_from(f, g) ** 2).sum() * dx


def mass(f, g: Grid):
    return f.sum() * g.dv * g.L / g.nx


def run(f, g: Grid, dt, t_end, observe, field_on=True, events=()):
    """Evolve; `observe(t, f)` is called every step; `events` = ((time, fn), ...) applied when reached."""
    n = int(round(t_end / dt))
    pending = sorted(events, key=lambda e: e[0])
    out = [observe(0.0, f)]
    for j in range(1, n + 1):
        f = step(f, g, dt, field_on)
        t = j * dt
        while pending and t >= pending[0][0] - 1e-12:
            f = pending.pop(0)[1](f)
        out.append(observe(t, f))
    return f, out


def peak_fit(t, a, t0, t1):
    """Damping rate and frequency from the local maxima of |a(t)| in [t0, t1]:
    rate = slope of ln|a| at the maxima; omega = pi / mean spacing of maxima."""
    t, a = np.asarray(t), np.abs(np.asarray(a))
    idx = [i for i in range(1, len(a) - 1) if a[i] > a[i - 1] and a[i] >= a[i + 1] and t0 <= t[i] <= t1]
    # parabolic refinement of each maximum
    tp, ap = [], []
    for i in idx:
        y0, y1, y2 = np.log(a[i - 1]), np.log(a[i]), np.log(a[i + 1])
        d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
        tp.append(t[i] + d * (t[1] - t[0])); ap.append(y1 - 0.25 * (y0 - y2) * d)
    tp, ap = np.array(tp), np.array(ap)
    rate = np.polyfit(tp, ap, 1)[0]
    omega = np.pi / np.mean(np.diff(tp))
    return rate, omega, tp
