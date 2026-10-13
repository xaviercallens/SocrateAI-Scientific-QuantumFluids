"""H1'': rigorous two-point (Cohn-Kumar) LP lower bounds for the Gaussian energy e^{-alpha r^2} at unit density in R^d.

Same ansatz as ../H1/lp_bound.py (fhat(y) = sum_k c_k phi_k(y/sqrt(beta)), phi_k = e^{-pi|y|^2} L_k^{(d/2-1)}(2 pi |y|^2)),
written in the variables t = 2 pi |y|^2 / beta and u = 2 pi beta |x|^2:
    fhat = e^{-t/2} Q(t),  Q = sum_k c_k L_k(t);      f = beta^{d/2} e^{-u/2} R(u),  R = sum_k (-1)^k c_k L_k(u).
With b = pi beta / alpha and kappa = (1 - 1/b)/2:  f/g = beta^{d/2} e^{-kappa u} R(u)  (g = e^{-alpha |x|^2}).

Why H1/H1' could not be certified (../H1p/PREREG.md amendment A1): the LP enforced f <= g and fhat >= 0 with an absolute
tolerance, so where g or e^{-t/2} underflow the relative violations are enormous.  Here:
  * f <= g is split at u1 = 2 pi beta r1^2 (r1: g(r1) = 1e-14, beyond which a contact contributes < 1e-14):
      on (0, r1]  the LP rows are f/g <= 1 (row-normalised: relative tolerance);
      on [u1, oo) the LP rows are R(u) <= -m (row-normalised, margin m), i.e. f < 0 <= g there;
  * fhat >= 0: rows Q(t) >= 0, row-normalised;
  * top coefficients: Q -> +oo and R -> -oo at infinity (odd effective degree, as H1);
  * cutting planes: fine-grid maxima of f/g - 1 and -Q/norm, and the exact real roots of R beyond u1 and of Q
    (flint, rigorous) are appended and the LP re-solved.
Certificate (exact rationals + arb interval arithmetic, flint):
  (a) c rationalised exactly (the doubles are rationals); Q, R exact rational polynomials.
  (b) R < 0 on [u1, oo): all real roots of R (rigorous arb enclosures) lie below u1, R(u1) < 0 exactly.
  (c) f/g <= 1 + tau0 on [0, u1]: bisection with a centred-form enclosure (value at midpoint + derivative enclosure
      on the box x half-width); tau0 starts at 2 x the sampled excess (+1e-15) and is multiplied by 4 on failure.
  (d) fhat >= 0 after a Gaussian lift: fhat + delta e^{-pi |y|^2/(lam beta)} >= 0  <=>  Q(t) + delta e^{s t} >= 0,
      s = (1 - 1/lam)/2.  Q > 0 off the intervals where Q < 0 (signs from exact rational evaluation between the
      rigorously isolated real roots; the root balls are always checked); on those intervals the inequality is proved
      by bisection.  The lift adds delta (lam beta)^{d/2} e^{-lam u/2} to f, i.e. delta (lam beta)^{d/2} e^{-(lam - 1/b) u/2}
      to f/g, at most delta (lam beta)^{d/2} when lam >= 1/b; beyond u1 it may make f positive, so (b) is applied to
      f_total: on [u1, oo) f_total <= g is proved from R(u) <= R_max < 0 ... we instead require
      delta (lam beta)^{d/2} e^{-lam u/2} <= g e^{0} on [u1, oo), i.e. delta (lam beta)^{d/2} <= e^{(lam - 1/b) u1/2}
      (checked; since f = (R part) + (lift part) with R part < 0, f_total <= lift part <= g).
  tau = tau0 + delta (lam beta)^{d/2};  certified bound
      B = [Q(0) + delta - beta^{d/2} R(0) - delta (lam beta)^{d/2}] / (1 + tau),   lower end of the arb ball.
"""
import math
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog
import flint
from flint import arb, fmpq, fmpq_poly, arb_poly

flint.ctx.prec = 320


def fq(x):
    x = Fraction(x)
    return fmpq(x.numerator, x.denominator)


def laguerre_exact(K, d):
    """[L_0..L_K]^{(a)}, a = d/2 - 1, as fmpq_poly (exact)."""
    a = Fraction(d, 2) - 1
    out = [fmpq_poly([1])]
    if K >= 1:
        out.append(fmpq_poly([fq(1 + a), -1]))
    x = fmpq_poly([0, 1])
    for k in range(1, K):
        out.append(((fmpq_poly([fq(2 * k + 1 + a)]) - x) * out[k] - fq(k + a) * out[k - 1]) * fmpq(1, k + 1))
    return out


def lag_rows(t, K, a, pref):
    t = np.asarray(t, float)
    out = np.empty((t.size, K + 1))
    out[:, 0] = pref
    if K >= 1:
        out[:, 1] = (1 + a - t) * pref
    for k in range(1, K):
        out[:, k + 1] = ((2 * k + 1 + a - t) * out[:, k] - (k + a) * out[:, k - 1]) / (k + 1)
    return out


def real_roots(P):
    """Rigorous enclosures (arb) of the real roots of an exact rational polynomial, sorted."""
    # flint (arb_fmpz_poly_complex_roots) returns certified real roots with an exactly zero imaginary part
    out = []
    for r, m in P.complex_roots():
        if isinstance(r, arb):
            out.append(r)
        elif r.imag.is_zero():
            out.append(r.real)
    return sorted(out, key=lambda z: float(z.mid()))


def lo_(z):
    return float(z.mid()) - float(z.rad())


def hi_(z):
    return float(z.mid()) + float(z.rad())


class RigLP:
    def __init__(self, d, alpha, b, K, lam=2, margin=1e-9, alpha_is_pi=False):
        self.d, self.alpha, self.K = d, float(alpha), K
        self.alpha_is_pi = alpha_is_pi or abs(float(alpha) - math.pi) < 1e-15
        self.b = Fraction(b).limit_denominator(1000)
        self.beta = self.alpha * float(self.b) / math.pi
        self.kappa = (1 - 1 / float(self.b)) / 2
        self.a = d / 2 - 1
        self.lam = Fraction(lam)
        assert self.lam >= 1 / self.b and self.lam > 1
        self.margin = margin
        self.r1 = math.sqrt(math.log(1e14) / self.alpha)
        self.u1 = 2 * math.pi * self.beta * self.r1 ** 2
        self.c = None
        self.L = laguerre_exact(K, d)
        if K % 2 == 0:
            self.bounds = [(None, None)] * K + [(0.0, 0.0)]
            self.bounds[K - 1] = (None, -1e-14)
            self.keff = K - 1
        else:
            self.bounds = [(None, None)] * K + [(None, -1e-14)]
            self.keff = K

    def fg_rows(self, r):
        u = 2 * math.pi * self.beta * np.asarray(r, float) ** 2
        return lag_rows(u, self.K, self.a, np.exp(-self.kappa * u)) * ((-1.0) ** np.arange(self.K + 1)) * self.beta ** (self.d / 2)

    def R_rows(self, u):
        return lag_rows(np.asarray(u, float), self.K, self.a, np.ones(np.size(u))) * ((-1.0) ** np.arange(self.K + 1))

    def q_rows(self, t):
        return lag_rows(np.asarray(t, float), self.K, self.a, np.ones(np.size(t)))

    def obj(self):
        L0 = lag_rows(np.array([0.0]), self.K, self.a, np.ones(1))[0]
        return L0 * (1 - self.beta ** (self.d / 2) * (-1.0) ** np.arange(self.K + 1))

    def exact_polys(self, c):
        Q, R = fmpq_poly([0]), fmpq_poly([0])
        for k in range(self.K + 1):
            ck = fq(float(c[k]))
            if ck == 0:
                continue
            Q += ck * self.L[k]
            R += (ck if k % 2 == 0 else -ck) * self.L[k]
        return Q, R

    def solve(self, n_r=3000, n_tail=1500, u_far=1e5, y_max=12.0, n_y=6000, rounds=12, n_fine=200000, tol_lp=1e-11,
              verbose=False):
        K = self.K
        r1 = self.r1
        Rg = r1 * np.arange(1, n_r + 1) / n_r
        Ut = self.u1 * (u_far / self.u1) ** (np.arange(0, n_tail) / (n_tail - 1))
        Tq = 2 * math.pi * (y_max * np.arange(0, n_y + 1) / n_y) ** 2 / self.beta
        Tq = np.concatenate([Tq, Tq[-1] * (1e5) ** (np.arange(1, 400) / 399)])     # Q rows far out (log grid)
        obj = self.obj()
        rng = np.random.default_rng(7)
        hist = []
        for it in range(rounds):
            Af = self.fg_rows(Rg)
            nf = np.abs(Af).max(1)
            At = self.R_rows(Ut)
            nt = np.abs(At).max(1)
            Aq = -self.q_rows(Tq)
            nq = np.abs(Aq).max(1)
            A = np.vstack([Af / nf[:, None], At / nt[:, None], Aq / nq[:, None]])
            bb = np.concatenate([1 / nf, -self.margin * np.ones(Ut.size), np.zeros(Tq.size)])
            res = None
            for meth in ("highs-ds", "highs-ipm", "highs"):
                res = linprog(-obj, A_ub=A, b_ub=bb, bounds=self.bounds, method=meth,
                              options={"primal_feasibility_tolerance": tol_lp, "dual_feasibility_tolerance": tol_lp})
                if res.status == 0:
                    break
            if res.status != 0:
                return {"status": res.status, "message": res.message}
            self.c = res.x
            bound = float(obj @ self.c)
            rf = np.sort(np.concatenate([r1 * np.arange(1, n_fine + 1) / n_fine, rng.uniform(1e-6, r1, n_fine // 4)]))
            vf = self.fg_rows(rf) @ self.c - 1
            tf = np.sort(np.concatenate([Tq[:n_y + 1].max() * (np.arange(n_fine + 1) / n_fine) ** 2,
                                         rng.uniform(0, Tq[:n_y + 1].max(), n_fine // 4)]))
            Qr = self.q_rows(tf)
            vq = -(Qr @ self.c) / np.abs(Qr).max(1)
            Q, R = self.exact_polys(self.c)
            rr = [z for z in real_roots(R) if hi_(z) >= self.u1]
            qr = [z for z in real_roots(Q) if hi_(z) >= 0]
            mf, mq = float(vf.max()), float(vq.max())
            hist.append({"round": it, "bound": bound, "max_fg_minus_1": mf, "max_negQ_rel": mq,
                         "R_roots_beyond_u1": len(rr), "Q_roots": len(qr), "rows": int(A.shape[0])})
            if verbose:
                print(f"   round {it}: bound={bound:.12f} f/g-1={mf:.2e} -Q/n={mq:.2e} R roots>u1={len(rr)} "
                      f"Q roots={len(qr)} {[round(float(z.mid()), 3) for z in qr][:12]} rows={A.shape[0]}", flush=True)
            add_r = rf[np.nonzero((vf[1:-1] >= vf[:-2]) & (vf[1:-1] >= vf[2:]) & (vf[1:-1] > -1e-7))[0] + 1]
            add_t = tf[np.nonzero((vq[1:-1] >= vq[:-2]) & (vq[1:-1] >= vq[2:]) & (vq[1:-1] > -1e-7))[0] + 1]
            add_u = np.array([float(z.mid()) for z in rr] + [float(z.mid()) * f for z in rr for f in (0.999, 1.001)])
            add_tq = np.array([float(z.mid()) for z in qr if float(z.mid()) > Tq[n_y]])
            if mf <= 1e-12 and mq <= 1e-12 and not rr and it > 0:
                break
            Rg = np.concatenate([Rg, add_r])
            Ut = np.concatenate([Ut, add_u[add_u >= self.u1]]) if add_u.size else Ut
            Tq = np.concatenate([Tq, add_t, add_tq])
        return {"status": 0, "bound_double": bound, "history": hist, "coeffs": [float(x) for x in self.c],
                "b": str(self.b), "beta": self.beta, "r1": r1, "u1": self.u1}

    # ---------------------------------------------------------------------------------------------- certificate
    def certify(self, coeffs=None):
        K, d = self.K, self.d
        Q, R = self.exact_polys(self.c if coeffs is None else coeffs)
        pi = arb.pi()
        b = arb(fq(self.b))
        alpha = pi if self.alpha_is_pi else arb(fq(self.alpha))
        beta = alpha * b / pi
        bd = beta ** (arb(d) / 2)
        kap = arb(fq((1 - 1 / self.b) / 2))
        lam = arb(fq(self.lam))
        u1 = arb(fq(Fraction(self.u1).limit_denominator(10 ** 12)))
        u1f = float(u1.mid())
        out = {"K": K, "d": d, "b": str(self.b), "lam": str(self.lam), "u1": u1f, "r1": self.r1}
        # (b) R < 0 on [u1, oo)
        lcR, lcQ = R.coeffs()[-1], Q.coeffs()[-1]
        assert lcR < 0 and lcQ > 0, "top-coefficient signs"
        rr = real_roots(R)
        assert all(hi_(z) < u1f for z in rr), "R has a root beyond u1"
        assert R(fq(Fraction(u1f))) < 0
        out["R_largest_root"] = max([hi_(z) for z in rr], default=None)
        # (c) f/g <= 1 + tau0 on [0, u1]
        Ra = arb_poly([arb(x) for x in R.coeffs()])
        dRa = Ra.derivative()
        F = lambda I: bd * (-(kap * I)).exp() * Ra(I)
        dF = lambda I: bd * (-(kap * I)).exp() * (dRa(I) - kap * Ra(I))
        uu = np.linspace(0, u1f, 200001)
        Fd = np.array([float(F(arb(x)).mid()) for x in uu])
        fmax = float(Fd.max())
        tau0 = max(fmax - 1, 0) * 2 + 1e-15
        while True:
            try:
                nb = prove_upper(F, dF, 1 + tau0, 0.0, u1f)
                break
            except RuntimeError:
                tau0 *= 4
                if tau0 > 1e-4:
                    raise
        out.update({"tau0": tau0, "fg_boxes": nb, "fg_max_sampled": fmax})
        # (d) Q + delta e^{s t} >= 0
        Qa = arb_poly([arb(x) for x in Q.coeffs()])
        dQa = Qa.derivative()
        s = (1 - 1 / lam) / 2
        qr = [z for z in real_roots(Q) if hi_(z) >= 0]
        edges = [(0.0, 0.0)] + [(lo_(z), hi_(z)) for z in qr]
        for i in range(len(qr) - 1):
            assert hi_(qr[i]) < lo_(qr[i + 1]), "root balls overlap"
        check = []
        for i in range(len(edges) - 1):
            lo, hi = edges[i][1], edges[i + 1][0]
            if hi > lo:
                mid = Fraction((lo + hi) / 2)
                if Q(fq(mid)) < 0:
                    check.append((max(0.0, edges[i][0]), edges[i + 1][1]))
        for z in qr:
            check.append((max(0.0, lo_(z) - float(z.rad())), hi_(z) + float(z.rad())))
        dmin = 0.0
        for lo, hi in check:
            for x in np.linspace(lo, hi, 2001):
                v = float((Qa(arb(x)) * (-(s * arb(x))).exp()).mid())
                dmin = min(dmin, v)
        delta = Fraction(-dmin * 2) + Fraction(1, 10 ** 40) if dmin < 0 else Fraction(0)
        de = arb(fq(delta))
        H = lambda I: -(Qa(I) + de * (s * I).exp())
        dH = lambda I: -(dQa(I) + de * s * (s * I).exp())
        nbq = 0
        for lo, hi in check:
            nbq += prove_upper(H, dH, 0, lo, hi, strict=True)
        lift = de * (lam * beta) ** (arb(d) / 2)
        # lift beyond u1 must stay below g: delta (lam beta)^{d/2} <= exp((lam - 1/b) u1 / 2)
        assert lift < ((lam - 1 / b) * u1 / 2).exp(), "lift exceeds g beyond u1"
        tau = arb(fq(Fraction(tau0))) + lift
        num = Qa(arb(0)) + de - bd * Ra(arb(0)) - lift
        B = num / (1 + tau)
        out.update({"Q_roots": len(qr), "Q_check_intervals": len(check), "delta": float(delta), "fhat_boxes": nbq,
                    "tau": float(tau.mid()) + float(tau.rad()), "B_ball": B.str(25, radius=True),
                    "B_lower": float(B.mid()) - float(B.rad()) * 2,     # double conversion: widen by one radius
                    "B_raw": float((Qa(arb(0)) - bd * Ra(arb(0))).mid())})
        return out


def prove_upper(F, dF, cap, lo, hi, strict=False):
    """Prove F(u) < cap (or <= for strict=False, same test) on [lo, hi] by bisection with a centred form."""
    stack = [(lo, hi)]
    n = 0
    while stack:
        a0, a1 = stack.pop()
        mid = (a0 + a1) / 2
        w = (a1 - a0) / 2
        enc = F(arb(mid)) + dF(arb(mid, w * (1 + 1e-12) + 1e-300)) * arb(0, w * (1 + 1e-12) + 1e-300)
        n += 1
        if enc < cap:
            continue
        if w < 1e-14 * max(1.0, abs(a1)):
            raise RuntimeError(f"check failed near {mid}: enclosure {enc.str(5, radius=True)}")
        if n > 2_000_000:
            raise RuntimeError("too many boxes")
        stack += [(a0, mid), (mid, a1)]
    return n
