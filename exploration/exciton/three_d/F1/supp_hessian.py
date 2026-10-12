"""Unregistered check (2026-10-12, after the F1 review): is the a0 = 0.25 state of the seed-0 ladder (a = 1 target, as in
supp_rung_chords.py) a local minimum? And the plain a = 4 endpoint from C's seed-0 start? Hessian of y -> E(y/|y|) restricted to
the tangent space (3 orthonormal tangent vectors per point, 360 directions), central differences of the gradient, h = 1e-4 and
1e-5. Also: does a fresh L-BFGS restart from the a0 state move it? Output: supp_hessian.log."""
import sys, numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, '../C')
import run_F1 as F, run_C as R
N = 120

def tangent_basis(X):
    B = []
    for i, x in enumerate(X):
        Q, _ = np.linalg.qr(np.column_stack([x, np.eye(4)]))
        for t in Q[:, 1:4].T:
            v = np.zeros((N, 4)); v[i] = t; B.append(v.ravel())
    return np.array(B)

def hess(y, a, h):
    X = y.reshape(N, 4) / np.linalg.norm(y.reshape(N, 4), axis=1, keepdims=True); y = X.ravel(); T = tangent_basis(X)
    H = np.array([T @ (F.energy_grad(y + h * t, N, a)[1] - F.energy_grad(y - h * t, N, a)[1]) / (2 * h) for t in T])
    return np.linalg.eigvalsh(0.5 * (H + H.T)), np.linalg.norm(T @ F.energy_grad(y, N, a)[1])

def report(name, y, a):
    for h in (1e-4, 1e-5):
        w, g = hess(y, a, h)
        print(f"{name} a={a:g} h={h:g}: |tangent grad|={g:.1e}; eigenvalues < -1e-8: {(w < -1e-8).sum()}, "
              f"|w| <= 1e-8: {(abs(w) <= 1e-8).sum()}, lowest {w[0]:.2e}, 7th {w[6]:.2e}", flush=True)

seed = 1000 * N + 0 + 100000 * list(R.KERNELS).index('gauss1')
y0 = np.random.default_rng(seed).normal(size=(N, 4)).ravel()
c = F.Counter(N, 0.25); r = F.lbfgs(c, y0)
print(f"a0 state seed 0: E={r.fun:.12f} nit={r.nit} msg={r.message}", flush=True)
report("a0 state", r.x, 0.25)
c2 = F.Counter(N, 0.25); r2 = F.lbfgs(c2, r.x)
print(f"restart from a0 state: nit={r2.nit} dE={r2.fun - r.fun:.2e} max|dy|={np.abs(r2.x - r.x).max():.1e} msg={r2.message}", flush=True)
seed4 = 1000 * N + 0 + 100000 * list(R.KERNELS).index('gauss4')
y4 = np.random.default_rng(seed4).normal(size=(N, 4)).ravel()
r4 = F.lbfgs(F.Counter(N, 4.0), y4); E6 = R.energy(R.cell600(), 'g', 4.0)
print(f"plain a=4 seed 0 endpoint: rel excess {(r4.fun - E6) / E6:.2e} nit={r4.nit}", flush=True)
report("plain a=4 endpoint", r4.x, 4.0)
