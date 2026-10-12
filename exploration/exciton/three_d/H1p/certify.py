"""H1' (PREREG.md + amendment A1): certified Cohn-Kumar two-point LP lower bounds for the Gaussian energy e^{-alpha|x|^2}
at unit density in R^d.

Variables.  Ansatz of ../H1/lp_bound.py: fhat(y) = sum_k c_k e^{-t/2} L_k^{(a)}(t), t = 2 pi |y|^2 / beta, and
f(x) = B sum_k (-1)^k c_k e^{-u/2} L_k^{(a)}(u), u = 2 pi beta |x|^2, with a = d/2 - 1 and B = beta^{d/2}.  Write
Q(t) = sum c_k L_k(t) and R(u) = sum (-1)^k c_k L_k(u): both are polynomials with coefficients rational in c.  With
beta = (alpha/pi) b, b rational, g(x) = e^{-alpha|x|^2} = e^{-u/(2b)} and
    f <= (1 + tau) g   <=>   B R(u) <= (1 + tau) e^{kappa u},   kappa = (1 - 1/b)/2 (rational),
    fhat >= 0          <=>   Q(t) >= 0 on [0, inf),
    bound              =     (Q(0) - B R(0)) / (1 + tau)            (Cohn-Kumar; 1603.09684 Prop. 2.2).
So the only irrational quantity is B (and pi inside it); everything else is exact.

Pipeline: double LP (../H1/lp_bound.py, unchanged)  ->  contact identification  ->  Remez exchange in mpmath  ->
exact lift of Q (sympy Sturm)  ->  interval verification of the f side (mpmath iv, adaptive bisection, second-order
centred form)  ->  certified bound (lower end of an interval).
"""
import math, sys, os, json, time
from fractions import Fraction
import numpy as np
import mpmath as mp
from mpmath import iv
import sympy as sp

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "H1"))
import lp_bound as LB

DPS = 80


# ---------------------------------------------------------------------------------------------------------------
# exact Laguerre coefficients
# ---------------------------------------------------------------------------------------------------------------
def laguerre_table(K, a):
    """Exact rational monomial coefficients: L_k^{(a)}(x) = sum_m T[k][m] x^m, a a Fraction."""
    T = []
    for k in range(K + 1):
        row = []
        for m in range(k + 1):
            # binom(k + a, k - m) = prod_{j=1}^{k-m} (m + a + j) / j
            b = Fraction(1)
            for j in range(1, k - m + 1):
                b *= (m + a + j) / Fraction(j)
            row.append((-1) ** m * b / math.factorial(m))
        T.append(row)
    return T


def poly_from_c(c, T, sign_alt):
    """Monomial coefficients (low -> high) of sum_k s_k c_k L_k, s_k = (-1)^k if sign_alt else 1.  c: list of
    Fractions or mpf; T: exact table."""
    K = len(c) - 1
    out = [0] * (K + 1)
    for k in range(K + 1):
        s = (-1) ** k if sign_alt else 1
        ck = c[k] * s
        for m in range(k + 1):
            out[m] = out[m] + ck * (T[k][m] if isinstance(ck, Fraction) else mp.mpf(T[k][m].numerator) / T[k][m].denominator)
    return out


def mp_polyval(coef, x):
    s = mp.mpf(0)
    for a_ in reversed(coef):
        s = s * x + a_
    return s


def mp_polyder(coef):
    return [coef[m] * m for m in range(1, len(coef))]


# ---------------------------------------------------------------------------------------------------------------
# problem
# ---------------------------------------------------------------------------------------------------------------
class Problem:
    def __init__(self, d, alpha, b, K):
        """alpha: 'pi' or a Fraction/int; b: Fraction (beta = (alpha/pi) b)."""
        self.d, self.K = d, K
        self.alpha_sym = alpha
        self.b = Fraction(b)
        self.a = Fraction(d, 2) - 1
        self.kappa = (1 - 1 / self.b) / 2
        self.T = laguerre_table(K, self.a)
        mp.mp.dps = DPS
        self.alpha_mp = mp.pi if alpha == "pi" else mp.mpf(Fraction(alpha).numerator) / Fraction(alpha).denominator
        self.beta_mp = self.alpha_mp / mp.pi * mp.mpf(self.b.numerator) / self.b.denominator
        self.B_mp = self.beta_mp ** (mp.mpf(d) / 2)
        self.kappa_mp = mp.mpf(self.kappa.numerator) / self.kappa.denominator

    @property
    def beta_float(self):
        return float(self.beta_mp)

    def alpha_float(self):
        return float(self.alpha_mp)

    # mp versions of the objective and constraint functions
    def mp_polys(self, c):
        Q = poly_from_c(c, self.T, False)
        R = poly_from_c(c, self.T, True)
        return Q, R

    def objective(self, c):
        Q, R = self.mp_polys(c)
        return Q[0] - self.B_mp * R[0]

    def phi(self, R, u):
        """relative f-side violation: B R(u) e^{-kappa u} - 1 (<= 0 required)."""
        return self.B_mp * mp_polyval(R, u) * mp.exp(-self.kappa_mp * u) - 1

    def Lvec(self, x):
        """[L_0(x), ..., L_K(x)] in mp via the three-term recurrence."""
        a = mp.mpf(self.a.numerator) / self.a.denominator
        L = [mp.mpf(1)]
        if self.K >= 1:
            L.append(1 + a - x)
        for k in range(1, self.K):
            L.append(((2 * k + 1 + a - x) * L[k] - (k + a) * L[k - 1]) / (k + 1))
        return L


# ---------------------------------------------------------------------------------------------------------------
# contacts and Remez exchange
# ---------------------------------------------------------------------------------------------------------------
def local_max_indices(v):
    idx = []
    n = len(v)
    for i in range(n):
        left = v[i - 1] if i > 0 else -mp.inf
        right = v[i + 1] if i < n - 1 else -mp.inf
        if v[i] >= left and v[i] >= right:
            idx.append(i)
    return idx


def find_contacts(P, c, u_max, t_max, n=6000):
    """Local maxima of phi(u) on [0, u_max] and of -Q(t)/N(t) on [0, t_max] (N = sum |c_k L_k(t)|).
    Returns list of (value, side, location, is_endpoint), sorted by value descending."""
    Q, R = P.mp_polys(c)
    us = [mp.mpf(u_max) * (mp.mpf(i) / n) ** 2 for i in range(n + 1)]      # denser near 0
    ts = [mp.mpf(t_max) * (mp.mpf(i) / n) ** 2 for i in range(n + 1)]
    vf = [P.phi(R, u) for u in us]
    vh = []
    for t in ts:
        L = P.Lvec(t)
        N = sum(abs(ck * Lk) for ck, Lk in zip(c, L))
        vh.append(-mp_polyval(Q, t) / N if N > 0 else mp.mpf(0))
    out = []
    for i in local_max_indices(vf):
        out.append((vf[i], "f", us[i], i == 0))
    for i in local_max_indices(vh):
        out.append((vh[i], "h", ts[i], i == 0))
    out.sort(key=lambda z: -z[0])
    return out


def newton_root(fun, dfun, x0, lo, hi, steps=200, tol=None):
    x = mp.mpf(x0)
    tol = tol or mp.mpf(10) ** (-(DPS - 15))
    for _ in range(steps):
        fx, dx = fun(x), dfun(x)
        if dx == 0:
            break
        x1 = x - fx / dx
        if x1 < lo or x1 > hi:
            x1 = (x + (lo if x1 < lo else hi)) / 2
        if abs(x1 - x) < tol * (1 + abs(x)):
            return x1
        x = x1
    return x


def remez(P, contacts, iters=200, verbose=False):
    """contacts: list of (side, location, endpoint).  Solves f-contacts B R(u_i) = e^{kappa u_i} and h-contacts
    Q(t_j) = 0 for c, then moves interior contacts to the stationary points of R e^{-kappa u} resp. Q.  Returns c, contacts,
    history."""
    K = P.K
    assert len(contacts) == K + 1, (len(contacts), K + 1)
    cs = [list(z) for z in contacts]
    hist = []
    c = None
    for it in range(iters):
        M = mp.matrix(K + 1, K + 1)
        rhs = mp.matrix(K + 1, 1)
        for i, (side, x, ep) in enumerate(cs):
            L = P.Lvec(x)
            if side == "f":
                for k in range(K + 1):
                    M[i, k] = P.B_mp * (-1) ** k * L[k]
                rhs[i] = mp.exp(P.kappa_mp * x)
            else:
                for k in range(K + 1):
                    M[i, k] = L[k]
                rhs[i] = 0
        try:
            sol = mp.lu_solve(M, rhs)
        except ZeroDivisionError:
            return None, cs, hist + [{"it": it, "error": "singular"}]
        c = [sol[k] for k in range(K + 1)]
        Q, R = P.mp_polys(c)
        dQ, dR = mp_polyder(Q), mp_polyder(R)
        ddQ, ddR = mp_polyder(dQ), mp_polyder(dR)
        kap = P.kappa_mp
        moved = mp.mpf(0)
        locs = sorted(z[1] for z in cs)
        for z in cs:
            side, x, ep = z
            if ep:
                continue
            # neighbouring contacts bound the search interval
            lo = max([y for y in locs if y < x] + [mp.mpf(0)])
            hi = min([y for y in locs if y > x] + [x * 2 + 10])
            if side == "f":
                fun = lambda u: mp_polyval(dR, u) - kap * mp_polyval(R, u)
                dfun = lambda u: mp_polyval(ddR, u) - kap * mp_polyval(dR, u)
            else:
                fun = lambda t: mp_polyval(dQ, t)
                dfun = lambda t: mp_polyval(ddQ, t)
            xn = newton_root(fun, dfun, x, lo, hi)
            moved = max(moved, abs(xn - x))
            z[1] = xn
        obj = P.objective(c)
        hist.append({"it": it, "objective": mp.nstr(obj, 30), "max_move": mp.nstr(moved, 5)})
        if verbose:
            print(f"   remez it {it}: obj {mp.nstr(obj, 25)} move {mp.nstr(moved, 3)}", flush=True)
        if moved < mp.mpf(10) ** -40:
            break
    return c, cs, hist


# ---------------------------------------------------------------------------------------------------------------
# exact positivity of Q (with lift)
# ---------------------------------------------------------------------------------------------------------------
def mp_to_fraction(x):
    m, e = mp.mpf(x).man_exp
    return Fraction(int(m)) * (Fraction(2) ** int(e))


def lift_Q(P, cF):
    """cF: exact Fractions.  Returns (delta, Qpoly_sympy_after_lift, info).  delta >= 0 is added to c_0."""
    tsym = sp.Symbol("t")
    Qc = poly_from_c(cF, P.T, False)
    Qs = sp.Poly(list(reversed([sp.Rational(q.numerator, q.denominator) for q in Qc])), tsym, domain="QQ")
    # numerical minimum of Q on [0, inf): real roots of Q' and t = 0
    dQ = Qs.diff(tsym)
    cand = [sp.Rational(0)]
    if dQ.degree() >= 1:
        for (lo, hi), mult in dQ.intervals(eps=sp.Rational(1, 10 ** 40)):
            if hi >= 0:
                cand.append(max(sp.Rational(lo), sp.Rational(0)))
                cand.append(max(sp.Rational(hi), sp.Rational(0)))
    vals = [Qs.eval(x) for x in cand]
    qmin = min(vals)
    lead = Qs.LC()
    delta = Fraction(0)
    if qmin <= 0:
        dq = -qmin
        delta = Fraction(int(dq.p), int(dq.q)) * 2 + Fraction(1, 10 ** 50)
    Ql = Qs + sp.Rational(delta.numerator, delta.denominator)
    nroots = Ql.count_roots(0, None) if hasattr(Ql, "count_roots") else None
    # count_roots(0, None) counts roots in [0, oo)
    ok = (nroots == 0) and (Ql.eval(0) > 0) and (lead > 0)
    return delta, Ql, {"qmin_sampled": float(qmin), "delta": float(delta), "n_roots_nonneg_after_lift": int(nroots),
                       "leading_coeff_positive": bool(lead > 0), "ok": bool(ok)}


# ---------------------------------------------------------------------------------------------------------------
# interval verification of the f side
# ---------------------------------------------------------------------------------------------------------------
def iv_poly(coefF, x):
    """Horner in interval arithmetic with exact rational coefficients."""
    s = iv.mpf(0)
    for q in reversed(coefF):
        s = s * x + iv.mpf(q.numerator) / q.denominator
    return s


def verify_f_side(P, RF, tau, U, n0=2000, wmin=1e-14, max_boxes=2_000_000):
    """Prove h(u) = (1+tau) e^{kappa u} - B R(u) >= 0 on [0, U] (RF exact Fractions, low -> high).
    Second-order centred form on each box.  Returns (ok, n_boxes, worst)."""
    iv.dps = 60
    if P.alpha_sym == "pi":
        Bi = iv.mpf(P.b.numerator) / P.b.denominator
    else:
        al = Fraction(P.alpha_sym)
        Bi = iv.mpf(al.numerator) / al.denominator / iv.pi * iv.mpf(P.b.numerator) / P.b.denominator
    Bi = Bi ** (iv.mpf(P.d) / 2)
    kap = iv.mpf(P.kappa.numerator) / P.kappa.denominator
    one_tau = 1 + iv.mpf(tau)
    dR = [RF[m] * m for m in range(1, len(RF))]
    ddR = [dR[m] * m for m in range(1, len(dR))]

    def h(x):
        return one_tau * iv.exp(kap * x) - Bi * iv_poly(RF, x)

    def dh(x):
        return one_tau * kap * iv.exp(kap * x) - Bi * iv_poly(dR, x)

    def ddh(x):
        return one_tau * kap * kap * iv.exp(kap * x) - Bi * iv_poly(ddR, x)

    U = Fraction(U)
    stack = [(U * i / n0, U * (i + 1) / n0) for i in range(n0)]
    nbox = 0
    worst = None
    while stack:
        lo, hi = stack.pop()
        nbox += 1
        if nbox > max_boxes:
            return False, nbox, "box budget exhausted"
        m = (lo + hi) / 2
        w = hi - lo
        mi = iv.mpf(m.numerator) / m.denominator
        I = iv.mpf([iv.mpf(lo.numerator) / lo.denominator, iv.mpf(hi.numerator) / hi.denominator])
        hw = iv.mpf(w.numerator) / w.denominator / 2
        hm, dhm, ddhI = h(mi), dh(mi), ddh(I)
        neg = ddhI.a if ddhI.a < 0 else iv.mpf(0)
        lower_iv = hm - abs(dhm) * hw + neg * hw * hw / 2
        if lower_iv.a > 0:
            continue
        if hm.b < 0:
            return False, nbox, f"h < 0 at u = {float(m):.17g}: h(m) <= {mp.nstr(hm.b, 5)}"
        if float(w) < wmin:
            return False, nbox, f"box narrower than {wmin} not proved at u = {float(m):.17g}"
        stack.append((lo, m))
        stack.append((m, hi))
    return True, nbox, None


def tail_U(P, RF):
    """Choose U and prove the tail u >= U.  kappa > 0: envelope B sum |r_m| u^m e^{-kappa u} <= 1 at U, U >= deg/kappa.
    kappa <= 0: R < 0 on [U, inf) by exact Sturm count.  Returns (U Fraction, info)."""
    usym = sp.Symbol("u")
    deg = max(m for m in range(len(RF)) if RF[m] != 0)
    if P.kappa > 0:
        U = Fraction(max(deg, 1)) / P.kappa
        iv.dps = 60
        B = mp.mpf(P.B_mp)
        while True:
            Uf = mp.mpf(U.numerator) / U.denominator
            env = B * sum(abs(mp.mpf(r.numerator) / r.denominator) * Uf ** m for m, r in enumerate(RF)) * mp.exp(-P.kappa_mp * Uf)
            if env <= mp.mpf("0.5"):          # margin; envelope is decreasing beyond deg/kappa
                return U, {"mode": "kappa>0 envelope", "U": float(U), "envelope_at_U": float(env)}
            U *= 2
            if U > 10 ** 7:
                return None, {"mode": "kappa>0 envelope", "error": "U too large"}
    Rs = sp.Poly(list(reversed([sp.Rational(r.numerator, r.denominator) for r in RF])), usym, domain="QQ")
    if Rs.LC() >= 0:
        return None, {"mode": "kappa<=0", "error": "leading coefficient of R not negative"}
    roots = [float(r) for r in sp.Poly(Rs).nroots(n=30, maxsteps=200) if abs(sp.im(r)) < 1e-20]
    U = Fraction(int(max(roots + [0.0])) + 2)
    n_after = Rs.count_roots(sp.Rational(U.numerator, U.denominator), None)
    val = Rs.eval(sp.Rational(U.numerator, U.denominator))
    ok = (n_after == 0) and (val < 0)
    return (U if ok else None), {"mode": "kappa<=0 sign", "U": float(U), "roots_beyond_U": int(n_after), "R(U)<0": bool(val < 0)}


# ---------------------------------------------------------------------------------------------------------------
# driver for one (d, alpha, b, K)
# ---------------------------------------------------------------------------------------------------------------
def certify_one(d, alpha, b, K, verbose=True, lp_kw=None, tau0=1e-12, tau_max=1e-6):
    t0 = time.time()
    P = Problem(d, alpha, b, K)
    out = {"d": d, "alpha": str(alpha), "b": f"{P.b.numerator}/{P.b.denominator}", "K": K,
           "beta": float(P.beta_mp), "kappa": f"{P.kappa}"}
    lp = LB.GaussLP(d, float(P.alpha_mp), float(P.beta_mp), K)
    res = lp.solve(**(lp_kw or {}))
    if res["bound"] is None:
        out["status"] = "LP failed"
        return out
    out["lp_bound_double"] = res["bound"]
    c0 = [mp.mpf(x) for x in res["coeffs"]]
    # contacts (ranges: x <= 24, |y| <= 12 as in the LP)
    u_max = 2 * mp.pi * P.beta_mp * 24 ** 2
    t_max = 2 * mp.pi * 12 ** 2 / P.beta_mp
    cont = find_contacts(P, c0, min(u_max, mp.mpf(4000)), min(t_max, mp.mpf(4000)))
    sel = cont[:K + 1]
    out["contacts_initial"] = [(z[1], float(z[2]), float(z[0]), bool(z[3])) for z in sel]
    out["contact_value_gap"] = float(cont[K][0] - cont[K + 1][0]) if len(cont) > K + 1 else None
    if verbose:
        print(f" d={d} alpha={alpha} b={P.b} K={K}: LP {res['bound']:.15f}; contacts kept {len(sel)}, "
              f"value of K+1-th {float(cont[K][0]):.2e}, next {float(cont[K+1][0]) if len(cont) > K+1 else None}", flush=True)
    c, cs, hist = remez(P, [(z[1], z[2], z[3]) for z in sel], verbose=False)
    out["remez_iterations"] = len(hist)
    use_remez = c is not None and hist and "error" not in hist[-1] and mp.mpf(hist[-1]["max_move"]) < mp.mpf(10) ** -40
    if use_remez:
        obj_r = P.objective(c)
        if obj_r < mp.mpf(res["bound"]) * (1 - mp.mpf("1e-6")):
            use_remez = False
    out["remez_converged"] = bool(use_remez)
    if not use_remez:
        c = c0
    out["objective_polished"] = mp.nstr(P.objective(c), 25)
    cF = [mp_to_fraction(x) for x in c]
    delta, Ql, qinfo = lift_Q(P, cF)
    out["fhat_certificate"] = qinfo
    if not qinfo["ok"]:
        out["status"] = "fhat positivity not certified"
        return out
    cF[0] += delta
    RF = poly_from_c(cF, P.T, True)
    QF = poly_from_c(cF, P.T, False)
    U, tinfo = tail_U(P, RF)
    out["tail"] = tinfo
    if U is None:
        out["status"] = "tail not certified"
        return out
    tau = tau0
    while tau <= tau_max:
        ok, nbox, why = verify_f_side(P, RF, tau, U)
        if verbose:
            print(f"   f-side tau={tau:.0e}: ok={ok} boxes={nbox} {why or ''}", flush=True)
        if ok:
            break
        tau *= 2 if why and "narrower" in why else 10
    out["f_certificate"] = {"tau": tau, "ok": bool(ok), "boxes": nbox, "why": why, "U": float(U)}
    if not ok:
        out["status"] = "f side not certified"
        return out
    # certified bound: (Q(0) - B R(0)) / (1 + tau), interval lower end
    iv.dps = 60
    if P.alpha_sym == "pi":
        Bi = (iv.mpf(P.b.numerator) / P.b.denominator) ** (iv.mpf(d) / 2)
    else:
        al = Fraction(P.alpha_sym)
        Bi = (iv.mpf(al.numerator) / al.denominator / iv.pi * iv.mpf(P.b.numerator) / P.b.denominator) ** (iv.mpf(d) / 2)
    Bd = (iv.mpf(QF[0].numerator) / QF[0].denominator - Bi * iv.mpf(RF[0].numerator) / RF[0].denominator) / (1 + iv.mpf(tau))
    out["certified_bound_interval"] = [mp.nstr(mp.mpf(Bd.a), 20), mp.nstr(mp.mpf(Bd.b), 20)]
    out["certified_bound"] = mp.nstr(mp.mpf(Bd.a), 20)
    out["status"] = "certified"
    out["coeffs_exact"] = [f"{q.numerator}/{q.denominator}" for q in cF]
    out["seconds"] = time.time() - t0
    return out
