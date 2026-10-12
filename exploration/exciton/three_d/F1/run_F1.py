"""F1 (PREREG_round2.md): alpha-homotopy on S^3 with the Gaussian chordal kernel e^{-a d^2}.

Method under test: L-BFGS to convergence at a0 = 0.25 from C's random start (same seed as C for the
target kernel), then follow the minimiser along the geometric ladder a_k = a0 * 2^{k/4} up to a_target,
re-converging (warm-started L-BFGS, C's optimiser settings) at every rung. a = 1, 2, 4 are rungs 8, 12, 16.
Gate F1b control: plain L-BFGS at a_target from the same start, hard-capped at the homotopy's total number
of gradient evaluations for that seed; on convergence before the cap, restart from a fresh random point
(continuing the same RNG stream); the best energy evaluated within the budget is reported.

Usage: python run_F1.py <out.jsonl> [--N 120] [--seeds 0:50] [--procs 2]
"""
import sys, os, json, argparse, time
import numpy as np
from scipy.optimize import minimize
from multiprocessing import Pool

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "C"))
import run_C as R  # energy_grad, cell600, cell24, KERNELS (seed formula)

A0 = 0.25
RATIO = 2 ** 0.25
TARGETS = {1.0: "gauss1", 2.0: "gauss2", 4.0: "gauss4"}
OPTS = dict(maxiter=8000, maxfun=16000, ftol=1e-17, gtol=1e-10, maxcor=30)  # identical to C


def energy_grad(y, N, a):
    """Same function as run_C.energy_grad(y, N, 'g', a) (same E, same gradient to ~1e-14 absolute), written
    with the Gram matrix instead of the N x N x 4 difference tensor: d^2_ij = 2 - 2 x_i.x_j on the unit sphere,
    sum_j df_ij 2 (x_i - x_j) = 2 (sum_j df_ij) x_i - 2 (df x)_i. About 5x faster at N = 120 (deviation 1)."""
    Y = y.reshape(N, 4); r = np.linalg.norm(Y, axis=1, keepdims=True); X = Y / r
    d2 = 2.0 - 2.0 * (X @ X.T); np.fill_diagonal(d2, 1.0)
    f = np.exp(-a * d2); np.fill_diagonal(f, 0.0); df = -a * f
    E = 0.5 * f.sum()
    gX = 2.0 * (df.sum(1, keepdims=True) * X - df @ X)
    gY = (gX - (gX * X).sum(1, keepdims=True) * X) / r
    return E, gY.ravel()


def check_evaluator(tol=1e-12):
    rng = np.random.default_rng(12345)
    for N in (24, 120):
        for a in (0.25, 1.0, 2.0, 4.0):
            y = rng.normal(size=(N, 4)).ravel()
            E1, g1 = R.energy_grad(y, N, "g", a); E2, g2 = energy_grad(y, N, a)
            assert abs(E1 - E2) <= tol * abs(E1) and np.abs(g1 - g2).max() <= tol, (N, a, E1 - E2)


def ladder(a_target):
    k_end = int(round(4 * np.log2(a_target / A0)))
    return [A0 * 2 ** (k / 4) for k in range(k_end + 1)]


class Counter:
    """Wraps energy_grad: counts gradient evaluations, tracks best point, enforces a hard budget."""
    def __init__(self, N, a, budget=None):
        self.N, self.a, self.budget = N, a, budget
        self.n = 0; self.bestE = np.inf; self.bestx = None
    def __call__(self, y):
        if self.budget is not None and self.n >= self.budget:
            raise BudgetExhausted()
        self.n += 1
        E, g = energy_grad(y, self.N, self.a)
        if E < self.bestE:
            self.bestE = E; self.bestx = y.copy()
        return E, g


class BudgetExhausted(Exception):
    pass


def normalise(y, N):
    X = y.reshape(N, 4); return X / np.linalg.norm(X, axis=1, keepdims=True)


def min_chord(X):
    D = np.linalg.norm(X[:, None] - X[None], axis=-1); np.fill_diagonal(D, 9); return float(D.min())


def lbfgs(fun, y0):
    return minimize(fun, y0, jac=True, method="L-BFGS-B", options=OPTS)


def homotopy(N, a_target, y0):
    rungs = []; y = y0; total = 0
    for a in ladder(a_target):
        c = Counter(N, a)
        res = lbfgs(c, y)
        y = res.x; total += c.n
        E, g = energy_grad(y, N, a)
        rungs.append(dict(a=a, E=float(E), gmax=float(np.abs(g).max()), nit=int(res.nit), nfev=int(c.n),
                          msg=str(res.message)))
    X = normalise(y, N)
    E, g = energy_grad(X.ravel(), N, a_target)
    return dict(E=float(E), gmax=float(np.abs(g).max()), min_chord=min_chord(X), nfev_total=int(total),
                rungs=rungs), X


def plain_equal_compute(N, a_target, y0, rng, budget):
    """Plain L-BFGS at a_target, restarts allowed, hard cap on gradient evaluations."""
    c = Counter(N, a_target, budget=budget)
    y = y0; restarts = 0; runs = []
    while c.n < budget:
        try:
            res = lbfgs(c, y)
            runs.append(dict(nit=int(res.nit), msg=str(res.message), E_end=float(res.fun)))
        except BudgetExhausted:
            runs.append(dict(nit=None, msg="budget exhausted", E_end=None)); break
        if c.n >= budget: break
        y = rng.normal(size=(N, 4)).ravel(); restarts += 1
    X = normalise(c.bestx, N)
    E, g = energy_grad(X.ravel(), N, a_target)
    return dict(E=float(E), gmax=float(np.abs(g).max()), min_chord=min_chord(X), nfev_used=int(c.n),
                budget=int(budget), restarts=restarts, runs=runs)


def job(args):
    N, a_target, s = args
    kernel = TARGETS[a_target]
    seed = 1000 * N + s + 100000 * list(R.KERNELS).index(kernel)  # C's seed formula
    rng = np.random.default_rng(seed)
    y0 = rng.normal(size=(N, 4)).ravel()  # identical to C's start for (N, kernel, s)
    t0 = time.time()
    hom, Xh = homotopy(N, a_target, y0)
    t1 = time.time()
    ctrl = plain_equal_compute(N, a_target, y0, rng, hom["nfev_total"])
    t2 = time.time()
    return dict(N=N, a_target=a_target, kernel=kernel, start=s, seed=int(seed), homotopy=hom,
                plain_equal_compute=ctrl, t_homotopy=t1 - t0, t_plain=t2 - t1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--N", type=int, default=120)
    ap.add_argument("--seeds", default="0:50"); ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--targets", default="1,2,4")
    A = ap.parse_args()
    check_evaluator()
    s0, s1 = map(int, A.seeds.split(":"))
    targets = [float(t) for t in A.targets.split(",")]
    jobs = [(A.N, a, s) for s in range(s0, s1) for a in targets]
    with Pool(A.procs) as pool, open(A.out, "a") as f:
        for r in pool.imap_unordered(job, jobs):
            f.write(json.dumps(r) + "\n"); f.flush()
            print(f"N={r['N']} a={r['a_target']} s={r['start']} E_hom={r['homotopy']['E']:.9f} "
                  f"chord={r['homotopy']['min_chord']:.6f} nfev={r['homotopy']['nfev_total']} "
                  f"E_plain={r['plain_equal_compute']['E']:.9f} t={r['t_homotopy']:.0f}+{r['t_plain']:.0f}s", flush=True)
    print("done")
