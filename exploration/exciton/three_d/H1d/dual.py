"""H1d: rigorous UPPER bounds on the Cohn-Kumar two-point (LP) bound for Gaussian energy in R^d, by discrete reduction
(adapted from R. Li, arXiv:2206.09876, Cohn-Elkies case) -- development code.

Reduction (DESIGN.md): for any admissible h (continuous, integrable, h^ >= 0 integrable, h(x) <= g(x) = exp(-alpha|x|^2)
for x != 0, decay enough for Poisson summation) and any rational s > 1, integer m >= 2, define on Z_m^d
    G(x) = sum_{n = x mod m} h(n/s),   Gamma(x) = sum_{n = x mod m, n != 0} g(n/s).
Then G^ >= 0 (Poisson), h^(0) <= s^-d sum_x G(x), G(x) <= Gamma(x) (x != 0), -h(0) <= -G(0) + Gamma(0).  For any
lambda >= 0 on Z_m^d with sum lambda = 1 - s^-d and
    mu(x) = s^-d + sum_y lambda(y) cos(2 pi x.y / m) >= 0   (x != 0)
weak duality gives  h^(0) - h(0) <= UB := Gamma(0) + sum_{x != 0} mu(x) Gamma(x).

Symmetry: radial h makes G invariant under signed permutations; variables are orbit representatives b (sorted, entries in
0..M, M = m//2).  Folding signs: sum_{signs} cos(2 pi x.y/m) = prod_i c(x_i, b_i), c(a, b) = w_b cos(2 pi a b/m),
w_b = 1 if b in {0, m/2} else 2.

solve()   : float LP (HiGHS) for lambda with mu >= eps.
certify() : lambda -> exact rationals (clip at 0, exact renormalisation), mu and UB in arb (tensor contraction with an
            arb cosine matrix; theta sums with a rigorous tail bound).  Returns the lower and upper end of UB's ball;
            the certified statement uses the UPPER end.
"""
import itertools
import math
from fractions import Fraction

import numpy as np
from flint import arb, arb_mat, fmpq, ctx
from scipy.optimize import linprog
from scipy.sparse import csr_matrix


def orbits(d, m):
    M = m // 2
    reps = list(itertools.combinations_with_replacement(range(M + 1), d))
    def npts(b):
        w = 1
        for v in b:
            w *= 1 if (v == 0 or 2 * v == m) else 2
        perms = math.factorial(d)
        for v in set(b):
            perms //= math.factorial(b.count(v))
        return w * perms
    return reps, np.array([npts(b) for b in reps], dtype=float)


def kernel_float(reps, d, m):
    M = m // 2
    a = np.arange(M + 1)
    w = np.where((a == 0) | (2 * a == m), 1.0, 2.0)
    C = np.cos(2 * np.pi * np.outer(a, a) / m) * w[None, :]          # C[x_i, b_i]
    R = np.array(reps)
    K = np.zeros((len(reps), len(reps)))
    seen = {}
    for sig in itertools.permutations(range(d)):
        P = np.ones_like(K)
        for i in range(d):
            P *= C[R[:, i]][:, R[:, sig[i]]]
        K += P
    # each distinct ordering of Y counted (d! / #distinct) times
    nd = np.array([len(set(itertools.permutations(b))) for b in reps], dtype=float)
    K *= (nd / math.factorial(d))[None, :]
    return K


def theta_float(a, m, alpha_s2, J=60):
    j = np.arange(-J, J + 1)
    return float(np.exp(-alpha_s2 * (a + m * j) ** 2).sum())


def gamma_float(reps, d, m, alpha, s):
    a2 = alpha / float(s) ** 2
    th = [theta_float(a, m, a2) for a in range(m // 2 + 1)]
    G = np.array([np.prod([th[v] for v in b]) for b in reps])
    G[0] -= 1.0                                               # n = 0 excluded from the class of x = 0
    return G


def solve(d, m, alpha, s, eps=1e-8):
    s = Fraction(s)
    reps, size = orbits(d, m)
    K = kernel_float(reps, d, m)
    Gam = gamma_float(reps, d, m, alpha, s)
    sd = float(s ** -d)
    # objective: Gamma(0) + sum_{X != 0} size_X Gamma_X (sd + K[X,:] lam)
    wX = size[1:] * Gam[1:]
    c = wX @ K[1:, :]
    const = Gam[0] + sd * wX.sum()
    A_ub = -K[1:, :]
    b_ub = sd - eps * np.ones(len(reps) - 1)                  # mu_X >= eps
    A_eq = size[None, :]
    b_eq = [1.0 - sd]
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs-ipm",
                  options={"primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10})
    if res.status != 0:
        raise RuntimeError(res.message)
    return {"d": d, "m": m, "alpha": alpha, "s": str(s), "n_orbits": len(reps), "UB_float": const + res.fun,
            "lam": res.x, "reps": reps, "size": size}


def _theta_arb(a, m, a2, J=40):
    # sum_{j in Z} exp(-a2 (a + m j)^2), |a| <= m/2; terms |j| > J bounded by a geometric tail
    tot = arb(0)
    for j in range(-J, J + 1):
        tot += (-(a2 * (a + m * j) ** 2)).exp()
    t0 = (-(a2 * (m * J - abs(a)) ** 2)).exp()          # >= every term with |j| > J; ratio <= exp(-a2 m^2 (2J-1))
    q = (-(a2 * m * m * (2 * J - 1))).exp()
    tail = 2 * t0 * q / (1 - q)
    return tot + arb(0, tail.upper())


def certify(sol, alpha_arb, den=2 ** 64):
    d, m = sol["d"], sol["m"]
    s = Fraction(sol["s"])
    reps, size = sol["reps"], sol["size"]
    M = m // 2
    # exact rational lambda >= 0, exact normalisation
    lam = [Fraction(max(0.0, float(x))).limit_denominator(den) for x in sol["lam"]]
    tot = sum(int(z) * l for z, l in zip(size, lam))
    target = 1 - s ** -d
    lam = [l * target / tot for l in lam]
    assert sum(int(z) * l for z, l in zip(size, lam)) == target and all(l >= 0 for l in lam)
    q = lambda f: fmpq(f.numerator, f.denominator)
    # tensor T[b] = lambda at folded coordinates b (ordered), as a (M+1)^(d-1) x (M+1) arb_mat
    idx = {b: i for i, b in enumerate(reps)}
    pi2m = 2 * arb.pi() / m
    C = arb_mat(M + 1, M + 1)
    for a in range(M + 1):
        for b in range(M + 1):
            w = 1 if (b == 0 or 2 * b == m) else 2
            C[a, b] = w * (pi2m * a * b).cos()
    # contraction mu(x) = sd + sum_b T[b] prod_i C[x_i, b_i]; done axis by axis
    n = M + 1
    T = {b: arb(q(lam[idx[tuple(sorted(b))]])) for b in itertools.product(range(n), repeat=d)}
    cur = T
    for axis in range(d):
        new = {}
        for key in itertools.product(range(n), repeat=d):
            # key: positions < axis are x-indices, >= axis are b-indices
            acc = arb(0)
            pre, post = key[:axis], key[axis + 1:]
            xa = key[axis]
            for b in range(n):
                acc += C[xa, b] * cur[pre + (b,) + post]
            new[key] = acc
        cur = new
    sd = arb(q(s ** -d))
    a2 = alpha_arb / arb(q(s * s))
    th = [_theta_arb(a, m, a2) for a in range(n)]
    UB = arb(0)
    min_mu = None
    for X, z in zip(reps, size):
        g = arb(1)
        for v in X:
            g *= th[v]
        if X == tuple([0] * d):
            UB += g - 1
            continue
        mu = sd + cur[X]
        if not (mu >= 0):
            raise RuntimeError(f"mu not provably >= 0 at {X}: {mu}")
        min_mu = mu if min_mu is None or mu.mid() < min_mu.mid() else min_mu
        UB += int(z) * mu * g
    return {"UB_ball": UB.str(25, radius=True), "UB_upper": UB.upper().str(25), "min_mu": min_mu.str(5, radius=True)}


def solve_cg(d, m, alpha, s, eps=1e-8, start=400, add=400, max_iter=60, verbose=False):
    """Same LP as solve(), by constraint generation on mu_X >= eps (the certificate re-checks every mu anyway)."""
    s = Fraction(s)
    reps, size = orbits(d, m)
    K = kernel_float(reps, d, m)
    Gam = gamma_float(reps, d, m, alpha, s)
    sd = float(s ** -d)
    wX = size[1:] * Gam[1:]
    c = wX @ K[1:, :]
    const = Gam[0] + sd * wX.sum()
    Kx = K[1:, :]
    n = Kx.shape[0]
    # start: the orbits with the largest Gamma weight (short vectors) plus an even spread
    order = np.argsort(-wX)
    act = set(order[:start // 2].tolist()) | set(np.linspace(0, n - 1, start // 2).astype(int).tolist())
    for it in range(max_iter):
        A = sorted(act)
        res = linprog(c, A_ub=-Kx[A, :], b_ub=sd - eps * np.ones(len(A)), A_eq=size[None, :], b_eq=[1.0 - sd],
                      bounds=(0, None), method="highs",
                      options={"primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10})
        if res.status != 0:
            raise RuntimeError(res.message)
        mu = sd + Kx @ res.x
        viol = np.where(mu < 0.5 * eps)[0]
        if verbose:
            print(f"   cg it {it}: active {len(A)} UB {const + res.fun:.12g} violated {len(viol)} min mu {mu.min():.3e}", flush=True)
        if len(viol) == 0:
            return {"d": d, "m": m, "alpha": alpha, "s": str(s), "n_orbits": len(reps), "UB_float": const + res.fun,
                    "lam": res.x, "reps": reps, "size": size, "cg_iters": it + 1, "active": len(A)}
        act |= set(viol[np.argsort(mu[viol])[:add]].tolist())
    raise RuntimeError("constraint generation did not converge")
