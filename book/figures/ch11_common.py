"""Shared helpers of the chapter on Bose-Einstein condensation (file ch11).

Run every ch11 script from book/ with the repaired CVODE module of rusty-SUNDIALS (commit 5db8041), NOT the stale module of
the project's virtual environment:

    PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext ../.venv/bin/python figures/ch11_<name>.py

Contents
  update_numbers(section, values)   read-modify-write of figures/ch11_numbers.json (one section per script)
  cvode_info(), adams_probe()       module path, sha256 and commit of rusty_sundials; the Adams probe of the second edition
  bose_g(nu, z)                     Bose function g_nu(z) = sum_k z^k / k^nu (mpmath polylog)
  RadialGP                          the Gross-Pitaevskii energy of a spherically symmetric condensate in an isotropic harmonic
                                    trap, discretised on r_j = j h (u = sqrt(4 pi) r phi), with the normalized gradient flow
  tf_guess(r, Na)                   smoothed Thomas-Fermi start for the flow
  newton_ground_state(gp, u0)       the same discrete ground state by Newton's method (an independent reference, no CVODE)

Units of the trap: hbar = m = omega = 1, lengths in a_ho = sqrt(hbar/(m omega)), energies in hbar omega.  With the coupling
g = 4 pi hbar^2 a / m the only parameter of the ground state is N a / a_ho, written Na below.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
NUMBERS = HERE / "ch11_numbers.json"


# ----------------------------------------------------------------------------------------------------- bookkeeping
def update_numbers(section: str, values: dict) -> None:
    """Store `values` under `section` in figures/ch11_numbers.json (other sections are kept)."""
    data = json.loads(NUMBERS.read_text()) if NUMBERS.exists() else {}
    data[section] = values
    data.setdefault("_about", "Every number quoted in chapters/ch11.tex comes from this file; each section is written by the script named in it.")
    NUMBERS.write_text(json.dumps(data, indent=1, sort_keys=True, default=float) + "\n")


def cvode_info() -> dict:
    import rusty_sundials
    so = Path(rusty_sundials.__file__).resolve()
    commit_file = so.parent / "commit.txt"
    return dict(module=str(so), sha256=hashlib.sha256(so.read_bytes()).hexdigest(),
                commit=commit_file.read_text().strip() if commit_file.exists() else "unknown")


def adams_probe() -> dict:
    """y' = -y to t = 10 with Adams at rtol 1e-8: the repaired module needs fewer than 5000 right-hand-side calls."""
    from rusty_sundials import CvodeSolver
    n = {"calls": 0}

    def rhs(t, y):
        n["calls"] += 1
        return [-y[0]]

    _, y = CvodeSolver("adams", 1e-8, 1e-14, 5_000_000).solve(rhs, 0.0, [1.0], 10.0)
    out = dict(rhs_calls=n["calls"], rel_err=abs(y[0] - math.exp(-10.0)) / math.exp(-10.0))
    assert n["calls"] < 5000, f"stale CVODE module? Adams probe needed {n['calls']} calls"
    return out


# ------------------------------------------------------------------------------------------------- ideal Bose gas
def bose_g(nu: float, z: float) -> float:
    """g_nu(z) = sum_{k>=1} z^k / k^nu for 0 <= z <= 1 (g_nu(1) = zeta(nu) for nu > 1)."""
    import mpmath
    return float(mpmath.polylog(nu, z))


# ------------------------------------------------------------------------------------------ Gross-Pitaevskii, radial
class RadialGP:
    """phi(r) = u(r) / (sqrt(4 pi) r), so that int |phi|^2 d^3r = int_0^R u^2 dr = 1.  Grid r_j = j h, j = 1..M, u = 0 at
    r = 0 and r = rmax.  Discrete energy per particle (exactly the one whose gradient the flow follows):
        K = h/2 sum ((u_{j+1}-u_j)/h)^2,   V = h/2 sum r_j^2 u_j^2,   I = (Na/2) h sum u_j^4 / r_j^2,
    E = K + V + I, chemical potential mu = <u, H u>/<u, u> = K + V + 2 I at a stationary point, with
        (H u)_j = -(u_{j+1} - 2 u_j + u_{j-1}) / (2 h^2) + r_j^2 u_j / 2 + Na u_j^3 / r_j^2 ."""

    def __init__(self, Na: float, M: int, rmax: float):
        self.Na, self.M, self.rmax = float(Na), int(M), float(rmax)
        self.h = rmax / (M + 1)
        self.r = self.h * np.arange(1, M + 1)
        self.r2 = self.r ** 2
        self.inv_r2 = 1.0 / self.r2

    def H(self, u: np.ndarray) -> np.ndarray:
        lap = np.empty_like(u)
        lap[1:-1] = u[2:] - 2.0 * u[1:-1] + u[:-2]
        lap[0] = u[1] - 2.0 * u[0]
        lap[-1] = u[-2] - 2.0 * u[-1]
        return -0.5 * lap / self.h ** 2 + 0.5 * self.r2 * u + self.Na * u ** 3 * self.inv_r2

    def parts(self, u: np.ndarray) -> tuple[float, float, float]:
        du = np.diff(np.concatenate(([0.0], u, [0.0]))) / self.h
        K = 0.5 * self.h * float(np.sum(du ** 2))
        V = 0.5 * self.h * float(np.sum(self.r2 * u ** 2))
        I = 0.5 * self.Na * self.h * float(np.sum(u ** 4 * self.inv_r2))
        return K, V, I

    def mu(self, u: np.ndarray) -> float:
        return float(np.dot(u, self.H(u)) / np.dot(u, u))

    def flow(self, t: float, y) -> list:
        """Normalized gradient flow du/dtau = -H(u) u + mu(u) u: it keeps h sum u^2 and lowers E (Bao and Du 2004)."""
        u = np.asarray(y)
        Hu = self.H(u)
        mu = np.dot(u, Hu) / np.dot(u, u)
        return (-Hu + mu * u).tolist()

    def norm(self, u: np.ndarray) -> float:
        return self.h * float(np.sum(u ** 2))

    def residual(self, u: np.ndarray) -> float:
        Hu = self.H(u)
        return math.sqrt(self.h * float(np.sum((Hu - self.mu(u) * u) ** 2)))

    def rms_radius(self, u: np.ndarray) -> float:
        return math.sqrt(self.h * float(np.sum(self.r2 * u ** 2)) / self.norm(u))

    def density(self, u: np.ndarray) -> np.ndarray:
        """|phi|^2 = u^2 / (4 pi r^2): the density per atom (multiply by N for the number density)."""
        return u ** 2 / (4.0 * math.pi * self.r2)


def gaussian_start(r: np.ndarray) -> np.ndarray:
    """Ground state of the trap without interactions: phi = pi^(-3/4) exp(-r^2/2), i.e. u = 2 pi^(-1/4) r exp(-r^2/2)."""
    return 2.0 * math.pi ** -0.25 * r * np.exp(-0.5 * r ** 2)


def tf_guess(r: np.ndarray, Na: float, s: float = 1.0) -> np.ndarray:
    """Thomas-Fermi profile mu_TF - r^2/2 smoothed at the edge by a softplus of width s (energy units), as a start."""
    mu_tf = 0.5 * (15.0 * Na) ** 0.4
    phi2 = s * np.logaddexp(0.0, (mu_tf - 0.5 * r ** 2) / s)
    return r * np.sqrt(phi2)


def tf_numbers(Na: float) -> dict:
    """Thomas-Fermi limit in trap units: R^5 = 15 Na, mu = R^2/2, E/N = 5 mu/7, <r^2> = 3 R^2/7."""
    R = (15.0 * Na) ** 0.2
    mu = 0.5 * R ** 2
    return dict(R=R, mu=mu, E=5.0 * mu / 7.0, rms=math.sqrt(3.0 / 7.0) * R)


def run_flow(gp: RadialGP, u0: np.ndarray, taus, rtol: float = 1e-10, atol: float = 1e-12, method: str = "bdf"):
    """Integrate the normalized gradient flow with CVODE from tau = 0 through the output times `taus` (one solver object,
    restarted at each output time because the binding returns the end state only).  Returns the final u and a history."""
    from rusty_sundials import CvodeSolver
    calls = {"n": 0}

    def rhs(t, y):
        calls["n"] += 1
        return gp.flow(t, y)

    u = u0 / math.sqrt(gp.norm(u0))
    hist = []
    K, V, I = gp.parts(u)
    hist.append(dict(tau=0.0, mu=gp.mu(u), E=K + V + I, K=K, V=V, I=I, norm=gp.norm(u), resid=gp.residual(u), calls=0, wall=0.0))
    solver = CvodeSolver(method, rtol, atol, 5_000_000)
    y, t, t0 = u.tolist(), 0.0, time.time()
    for tau in taus:
        _, y = solver.solve(rhs, t, y, float(tau))
        t = float(tau)
        u = np.asarray(y)
        K, V, I = gp.parts(u)
        hist.append(dict(tau=t, mu=gp.mu(u), E=K + V + I, K=K, V=V, I=I, norm=gp.norm(u), resid=gp.residual(u),
                         calls=calls["n"], wall=time.time() - t0))
    return u, hist


def newton_ground_state(gp: RadialGP, u0: np.ndarray, tol: float = 1e-13, maxit: int = 50):
    """Solve H(u) u = mu u, h sum u^2 = 1 by Newton's method on (u, mu) (bordered tridiagonal system, scipy banded solver).
    Independent of CVODE: same discretisation, different algorithm.  Returns (u, mu, iterations, final residual)."""
    from scipy.linalg import solve_banded
    h, M = gp.h, gp.M
    u = u0 / math.sqrt(gp.norm(u0))
    mu = gp.mu(u)
    for it in range(1, maxit + 1):
        F = gp.H(u) - mu * u
        G = gp.norm(u) - 1.0
        # Jacobian: A = d(H(u)u)/du - mu I  (tridiagonal), bordered by -u (column) and 2 h u^T (row)
        diag = 1.0 / h ** 2 + 0.5 * gp.r2 + 3.0 * gp.Na * u ** 2 * gp.inv_r2 - mu
        off = -0.5 / h ** 2 * np.ones(M - 1)
        ab = np.zeros((3, M))
        ab[0, 1:] = off
        ab[1, :] = diag
        ab[2, :-1] = off
        x1 = solve_banded((1, 1), ab, -F)          # A dx1 = -F
        x2 = solve_banded((1, 1), ab, u)           # A dx2 = u   (so that dx = x1 + dmu * x2 solves A dx - dmu u = -F)
        dmu = (-G - 2.0 * h * np.dot(u, x1)) / (2.0 * h * np.dot(u, x2))
        du = x1 + dmu * x2
        u, mu = u + du, mu + dmu
        if max(np.max(np.abs(du)), abs(dmu)) < tol:
            break
    return u, mu, it, gp.residual(u)
