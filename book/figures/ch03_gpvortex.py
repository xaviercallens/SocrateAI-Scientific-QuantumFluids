"""Exact radial profile of the singly quantized GP vortex, psi = f(r) exp(i theta), units hbar = m = g = n0 = 1 (mu = 1):
    f'' + f'/r - f/r^2 + 2 f (1 - f^2) = 0 ,  f(0) = 0 , f(inf) = 1.   (from  mu f = -(1/2)(f'' + f'/r - f/r^2) + f^3)
solved with scipy solve_bvp on [r0, R] with the asymptotic boundary conditions f ~ c r at r0 and f' = 1/(r)(... ) at R."""
import numpy as np
from scipy.integrate import solve_bvp

def solve(R=30.0, r0=1e-3):
    def rhs(r, y):
        f, g = y
        return np.vstack([g, -g / r + f / r ** 2 - 2 * f * (1 - f ** 2)])
    def bc(ya, yb):
        # at r0: f = r0 f'(r0) (f ~ c r);  at R: f' = 1/R^2 * 1/... use the far-field f = 1 - 1/(4 r^2):  f' = 1/(2 R^3)... keep f = 1 - 1/(4R^2)
        return np.array([ya[0] - r0 * ya[1], yb[0] - (1 - 1 / (4 * R ** 2))])
    r = np.linspace(r0, R, 600)
    y0 = np.vstack([np.tanh(r), 1 / np.cosh(r) ** 2])
    sol = solve_bvp(rhs, bc, r, y0, tol=1e-10, max_nodes=200000)
    assert sol.success, sol.message
    return sol

if __name__ == "__main__":
    sol = solve(); c = sol.sol(1e-3)[1]
    print("slope at origin f ~ c r, c =", c, " f(5)=", sol.sol(5.0)[0])
