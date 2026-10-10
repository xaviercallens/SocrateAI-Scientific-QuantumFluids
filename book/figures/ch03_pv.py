"""Chapter 3: the periodic point-vortex model, the *reduced model* that the Gross-Pitaevskii runs are compared with.
Units hbar = m = 1, so every vortex has circulation kappa = 2 pi; the box has side L = 64 and periodic boundaries.

Three ingredients, each short enough to quote in the chapter:

  fourier_velocity : zero-mean-flow velocity of Gaussian-smoothed point vortices from the Fourier series
                         u(x) = sum_{k != 0}  i (k_y, -k_x) / |k|^2  rho_hat(k)  exp(i k.x),
                         rho_hat(k) = (kappa/L^2) sum_j q_j exp(-i k.x_j) exp(-sigma^2 k^2 / 2)
                     (the smoothing width sigma is far below every vortex-vortex distance, so it changes nothing measurable)
  wm_velocity      : the same field for exact point vortices in closed form (Weiss-McWilliams pair function, the
                     programme's `exploration/pgpe/transport_estimators.py`), at arbitrary points
  sector_flow      : the uniform flow that the winding integers of the torus force:
                         ubar = (kappa / L^2) ( sum_j q_j y_j , - sum_j q_j x_j )     (cycle windings 0, the minimal sector)

and `integrate_cvode`, which advances dz_a/dt = u_a(z) + ubar with rusty-SUNDIALS CVODE (`rusty_sundials.CvodeSolver`).
"""
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "exploration" / "pgpe"))
from transport_estimators import grad_h, pv_velocity          # noqa: E402  (programme code: Weiss-McWilliams pair function)

L = 64.0
KAPPA = 2 * np.pi


def sector_flow(pos, q, L=L):
    pos = np.atleast_2d(pos).astype(float); q = np.asarray(q, float)
    return (KAPPA / L ** 2) * np.array([np.sum(q * pos[:, 1]), -np.sum(q * pos[:, 0])])


def _kgrid(sigma, kfac=9.0, L=L):
    nmax = int(np.ceil(kfac / sigma / (2 * np.pi / L)))
    m = np.arange(-nmax, nmax + 1)
    kx, ky = np.meshgrid(2 * np.pi * m / L, 2 * np.pi * m / L, indexing="ij")
    k2 = kx ** 2 + ky ** 2
    mask = (k2 > 0) & (k2 <= (kfac / sigma) ** 2)
    return kx[mask], ky[mask], k2[mask]


def fourier_velocity(points, pos, q, sigma=0.7, L=L, chunk=48):
    kx, ky, k2 = _kgrid(sigma, L=L)
    points = np.atleast_2d(points).astype(float); pos = np.atleast_2d(pos).astype(float); q = np.asarray(q, float)
    rho = (KAPPA / L ** 2) * (q[:, None] * np.exp(-1j * (np.outer(pos[:, 0], kx) + np.outer(pos[:, 1], ky)))).sum(0)
    rho = rho * np.exp(-0.5 * sigma ** 2 * k2)
    out = np.empty((len(points), 2))
    for a in range(0, len(points), chunk):
        e = np.exp(1j * (np.outer(points[a:a + chunk, 0], kx) + np.outer(points[a:a + chunk, 1], ky))) * rho
        out[a:a + chunk, 0] = (e * (1j * ky / k2)).sum(1).real
        out[a:a + chunk, 1] = (e * (-1j * kx / k2)).sum(1).real
    return out


def wm_velocity(points, pos, q, L=L):
    """Zero-mean-flow velocity of exact point vortices at arbitrary points (not at a vortex)."""
    sc = 2 * np.pi / L
    points = np.atleast_2d(points).astype(float); pos = np.atleast_2d(pos).astype(float); q = np.asarray(q, float)
    dx = (points[:, None, 0] - pos[None, :, 0]) * sc
    dy = (points[:, None, 1] - pos[None, :, 1]) * sc
    hx, hy = grad_h(dx, dy)
    psix = -0.5 * sc * (hx * q[None, :]).sum(1)
    psiy = -0.5 * sc * (hy * q[None, :]).sum(1)
    return np.column_stack([psiy, -psix])


def vortex_velocity(pos, q, with_sector=True, L=L):
    """Velocity of every vortex: the field of the others (zero mean flow) plus, optionally, the sector flow."""
    pos = np.atleast_2d(pos).astype(float); q = np.asarray(q, float)
    v = pv_velocity(pos, q, L)
    if with_sector:
        v = v + sector_flow(pos, q, L)
    return v


def integrate_cvode(pos0, q, t_grid, rtol=1e-10, atol=1e-10, method="adams"):
    """Advance the model with CVODE, restarted at every output time; returns (positions, number of RHS calls)."""
    from rusty_sundials import CvodeSolver
    q = np.asarray(q, float); n = len(q)
    nfe = [0]

    def rhs(t, y):
        nfe[0] += 1
        return vortex_velocity(np.array(y).reshape(n, 2), q).ravel().tolist()

    solver = CvodeSolver(method, rtol, atol, 1_000_000)
    y = np.asarray(pos0, float).ravel().tolist()
    out = [np.array(y).reshape(n, 2)]
    for t0, t1 in zip(t_grid[:-1], t_grid[1:]):
        _, y = solver.solve(rhs, float(t0), y, float(t1))
        out.append(np.array(y).reshape(n, 2))
    return np.array(out), nfe[0]


def integrate_dop853(pos0, q, t_grid, rtol=1e-12, atol=1e-12):
    """Independent integrator for the same right-hand side (scipy DOP853), used only to check the CVODE trajectory."""
    from scipy.integrate import solve_ivp
    q = np.asarray(q, float); n = len(q)
    f = lambda t, y: vortex_velocity(y.reshape(n, 2), q).ravel()
    sol = solve_ivp(f, (t_grid[0], t_grid[-1]), np.asarray(pos0, float).ravel(), t_eval=t_grid, method="DOP853", rtol=rtol, atol=atol)
    return sol.y.T.reshape(len(t_grid), n, 2)


if __name__ == "__main__":
    pos = np.array([[26.30, 30.70], [38.10, 31.20]]); q = np.array([1, -1])
    a = vortex_velocity(pos, q, with_sector=False)
    b = fourier_velocity(pos, pos, q, sigma=0.7)
    print("Weiss-McWilliams :", a.round(7).tolist())
    print("Fourier (sigma .7):", b.round(7).tolist(), " max |diff| =", float(np.abs(a - b).max()))
    print("sector flow      :", sector_flow(pos, q).round(7).tolist())
    print("with sector flow :", vortex_velocity(pos, q).round(7).tolist())
