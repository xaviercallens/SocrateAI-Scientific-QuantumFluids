"""H1'': rigorous two-point (Cohn-Kumar) LP lower bounds for the Gaussian energy, with a high-precision LP.

Notation as rig.py:  t = 2 pi |y|^2 / beta,  u = 2 pi beta |x|^2 = 2 b alpha |x|^2,  b = pi beta / alpha,
    fhat = e^{-t/2} Q(t),  Q = sum c_k L_k^{(d/2-1)}(t);   f = beta^{d/2} e^{-u/2} R(u),  R = sum (-1)^k c_k L_k(u);
    f/g = beta^{d/2} e^{-kappa u} R(u),  kappa = (1 - 1/b)/2.
Bound (Cohn-Kumar; Cohn-de Courcy-Ireland 1603.09684 Prop. 2.2): f radial, continuous, integrable, fhat >= 0, f <= g off 0
=>  energy of any density-1 configuration >= fhat(0) - f(0) = Q(0) - beta^{d/2} R(0).

LP (solved by hp_lp.solve_ipm at ctx.prec bits, every row normalised to unit max-norm):
    f/g <= 1           on u in (0, u1],   u1 = 2 b log(1/gcut)  (g(x1) = gcut, default 1e-14)
    R(u) <= -margin    on u in [u1, u_far] (log grid): f < 0 <= g beyond x1
    Q(t) >= 0          on t in [0, T(y_max)] and a log grid beyond
    top coefficient:   c_K < 0, K odd (Q -> +oo, R -> -oo); for even K, c_K = 0 (effective degree K - 1).
Cutting planes: local maxima of f/g on a fine grid, rigorous real roots of R beyond u1 and of Q on [0, oo).
Certificate: rig.RigLP.certify-like, from the exact rational coefficients (arb midpoints are dyadic rationals).
"""
import math
from fractions import Fraction
import numpy as np
import flint
from flint import arb, fmpq, fmpq_poly, arb_poly
from rig import laguerre_exact, real_roots, lo_, hi_, fq
from hp_lp import solve_ipm

flint.ctx.prec = 256


def lag_arb(x, K, a):
    out = [arb(1)]
    if K >= 1:
        out.append(1 + a - x)
    for k in range(1, K):
        out.append(((2 * k + 1 + a - x) * out[k] - (k + a) * out[k - 1]) / (k + 1))
    return out


class HPRig:
    def __init__(self, d, alpha, b, K, lam=2, gcut=1e-14, margin="1e-12"):
        """alpha: 'pi' or a rational (Fraction/str/int)."""
        self.d, self.K = d, K
        self.alpha_is_pi = (alpha == "pi")
        self.alpha_q = None if self.alpha_is_pi else Fraction(alpha)
        self.alpha = arb.pi() if self.alpha_is_pi else arb(fq(self.alpha_q))
        self.b = Fraction(b)
        self.bq = fq(self.b)
        self.beta = self.alpha * arb(self.bq) / arb.pi()
        self.bd = self.beta ** (arb(d) / 2)
        self.kappa_q = (1 - 1 / self.b) / 2
        self.kappa = arb(fq(self.kappa_q))
        self.a = arb(fq(Fraction(d, 2) - 1))
        self.lam = Fraction(lam)
        assert self.lam > 1 and self.lam >= 1 / self.b
        self.u1q = (2 * self.b * Fraction(math.log(1 / gcut))).limit_denominator(10 ** 6)
        self.u1 = float(self.u1q)
        self.margin = arb(margin)
        self.L = laguerre_exact(K, d)
        self.keff = K if K % 2 == 1 else K - 1     # c_K forced 0 for even K
        self.c = None

    # rows (lists of arb), over the free coefficients c_0..c_keff -----------------------------------------
    def _norm(self, row, rhs):
        nrm = max(abs(float(x.mid())) for x in row)
        nrm = arb(nrm) if nrm > 0 else arb(1)
        return [x / nrm for x in row], rhs / nrm

    def row_fg(self, u):
        u = arb(u)
        L = lag_arb(u, self.keff, self.a)
        pref = self.bd * (-(self.kappa * u)).exp()
        return self._norm([pref * (L[k] if k % 2 == 0 else -L[k]) for k in range(self.keff + 1)], arb(1))

    def row_tail(self, u):
        L = lag_arb(arb(u), self.keff, self.a)
        return self._norm([(L[k] if k % 2 == 0 else -L[k]) for k in range(self.keff + 1)], arb(0)) + (True,)

    def row_q(self, t):
        L = lag_arb(arb(t), self.keff, self.a)
        return self._norm([-x for x in L], arb(0))

    def objective(self):
        L = lag_arb(arb(0), self.keff, self.a)
        return [L[k] * (1 - (self.bd if k % 2 == 0 else -self.bd)) for k in range(self.keff + 1)]

    def exact_polys(self, c=None):
        c = self.c if c is None else c
        Q, R = fmpq_poly([0]), fmpq_poly([0])
        for k, ck in enumerate(c):
            q = ck if isinstance(ck, fmpq) else ck.mid().fmpq()
            Q += q * self.L[k]
            R += (q if k % 2 == 0 else -q) * self.L[k]
        return Q, R

    def F_arb(self, R):
        Ra = arb_poly([arb(x) for x in R.coeffs()])
        return lambda u: self.bd * (-(self.kappa * u)).exp() * Ra(u)

    # LP with cutting planes --------------------------------------------------------------------------------
    def solve(self, n_u=3000, n_tail_lin=1500, n_tail=300, u_far_factor=1e4, y_max=12.0, t_lin=200.0, n_t_lin=4000,
              n_t=1000, n_t_tail=150, rounds=10, n_fine=20000, verbose=False, prune=False, prune_tol=1e-2,
              certify_each=True, ckpt=None):
        import json, os
        assert not prune, 'checkpointing assumes prune=False'
        U = [self.u1 * (i / n_u) ** 2 for i in range(1, n_u + 1)]
        UT = ([self.u1 * (1 + 3 * i / n_tail_lin) for i in range(n_tail_lin)]
              + [4 * self.u1 * (u_far_factor / 4) ** (i / (n_tail - 1)) for i in range(n_tail)])
        Tmax = float((2 * arb.pi() * y_max ** 2 / self.beta).mid())
        tl = min(t_lin, Tmax)
        T = ([tl * i / n_t_lin for i in range(n_t_lin + 1)] + [tl + (Tmax - tl) * (i / n_t) ** 2 for i in range(1, n_t + 1)]
             + [Tmax * 1e4 ** (i / n_t_tail) for i in range(1, n_t_tail + 1)])
        P_fg, P_t, P_q = list(U), list(UT), list(T)       # row generators are deterministic in these points
        start, hist, best, c0, bound = 0, [], None, None, None
        if ckpt and os.path.exists(ckpt):
            st = json.load(open(ckpt))
            assert st['sig'] == [self.d, str(self.alpha_q), str(self.b), self.K, self.alpha_is_pi], 'checkpoint mismatch'
            P_fg, P_t, P_q = st['P_fg'], st['P_t'], st['P_q']
            start, hist, bound = st['next_round'], st['hist'], st['bound']
            c0 = [arb(fmpq(*map(int, x.split('/'))) if '/' in x else fmpq(int(x))) for x in st['c0']]
            if st['best'] is not None:
                bb = st['best']
                best = (bb[0], [arb(fmpq(*map(int, x.split('/'))) if '/' in x else fmpq(int(x))) for x in bb[1]], bb[2], bb[3])
            print(f'   RESUMED {ckpt} at round {start}', flush=True)
        rows_fg = [self.row_fg(u) for u in P_fg]
        rows_t = [self.row_tail(u)[:2] for u in P_t]
        rows_q = [self.row_q(t) for t in P_q]
        obj = self.objective()
        for it in range(start, rounds):
            top = [arb(0)] * self.keff + [arb(1)]
            A = [r for r, _ in rows_fg] + [r for r, _ in rows_t] + [r for r, _ in rows_q] + [top]
            bvec = ([h for _, h in rows_fg] + [h - self.margin for _, h in rows_t] + [h for _, h in rows_q]
                    + [-self.margin])
            res = solve_ipm(A, bvec, obj, c0=c0, verbose=verbose)
            self.c = res["c"]
            # active-set pruning: keep rows with small slack (normalised units) and every 8th row; dropped rows are
            # re-added by the exact cutting planes below if they become violated
            if prune and it < rounds - 1:
                sl = [float(x.mid()) for x in res["s"]]
                n1, n2 = len(rows_fg), len(rows_fg) + len(rows_t)
                keep = lambda i: sl[i] < prune_tol or i % 8 == 0
                rows_fg = [r for i, r in enumerate(rows_fg) if keep(i)]
                rows_t = [r for i, r in enumerate(rows_t) if keep(n1 + i)]
                rows_q = [r for i, r in enumerate(rows_q) if keep(n2 + i)]
            c0 = self.c
            bound = float(res["obj"].mid())
            Q, R = self.exact_polys()
            F = self.F_arb(R)
            # fine-grid maxima of f/g - 1
            uf = np.concatenate([self.u1 * (np.arange(1, n_fine + 1) / n_fine) ** 2])
            Fv = np.array([float(F(arb(float(u))).mid()) for u in uf]) - 1
            loc = np.nonzero((Fv[1:-1] >= Fv[:-2]) & (Fv[1:-1] >= Fv[2:]) & (Fv[1:-1] > -1e-12))[0] + 1
            add_u = []
            for i in loc:                       # refine each near-contact maximum (golden section, arb) and add a cluster
                lo_u, hi_u = float(uf[i - 1]), float(uf[i + 1])
                g1, g2 = 0.381966, 0.618034
                for _ in range(60):
                    x1, x2 = lo_u + g1 * (hi_u - lo_u), lo_u + g2 * (hi_u - lo_u)
                    if F(arb(x1)) > F(arb(x2)):
                        hi_u = x2
                    else:
                        lo_u = x1
                us = (lo_u + hi_u) / 2
                h = float(uf[i + 1] - uf[i - 1])
                add_u += [us + k * h / 8 for k in range(-6, 7) if 0 < us + k * h / 8 <= self.u1]
            rr_all = real_roots(R)
            rr = [z for z in rr_all if hi_(z) >= self.u1]
            qr = [z for z in real_roots(Q) if hi_(z) >= 0]
            # exact critical points of f/g: roots of R' - kappa R (rational); every local max of f/g is among them
            Ucheck = max(self.u1, max([hi_(z) for z in rr_all], default=0.0) * 1.0001 + 1.0)
            crit = [z for z in real_roots(R.derivative() - fq(self.kappa_q) * R) if 0 <= float(z.mid()) <= Ucheck]
            Fc = [(float(z.mid()), float(F(arb(z.mid())).mid())) for z in crit]
            Fcmax = max([v for _, v in Fc], default=-1.0) - 1
            for m, v in Fc:
                if v > 1 - 1e-9:
                    add_u += [m * (1 + k * 1e-7) for k in range(-3, 4)] + [m * (1 + k * 1e-4) for k in (-2, -1, 1, 2)]
            Fv = np.append(Fv, Fcmax)
            mf = float(Fv.max())
            # certify this round's coefficients (any certified coefficient vector gives a valid bound; the best
            # certified bound over rounds is kept)
            cert_r = None
            if certify_each:
                try:
                    cert_r = self.certify(self.c, max_boxes=200_000)
                    Bl = float(self.B.lower().mid())
                    if best is None or Bl > best[0]:
                        best = (Bl, [x for x in self.c], cert_r, it)
                except Exception as e:
                    cert_r = {"error": repr(e)[:300]}
            hist.append({"round": it, "certified_B_lower": (cert_r or {}).get("B_lower"),
                         "cert_tau": (cert_r or {}).get("tau_upper"), "cert_delta": (cert_r or {}).get("delta"),
                         "cert_error": (cert_r or {}).get("error"), "bound": bound, "max_fg_minus_1_crit": Fcmax, "ipm_iterations": res["iterations"], "max_fg_minus_1_fine": mf,
                         "n_fg_local_max_near_1": int(len(loc)), "R_roots_beyond_u1": len(rr), "Q_roots": len(qr),
                         "rows": len(A)})
            if verbose:
                print(f"   round {it}: certB={(cert_r or {}).get('B_lower', (cert_r or {}).get('error', ''))[:60]} "
                      f"tau={(cert_r or {}).get('tau_upper')} bound={bound:.15f} max f/g-1={mf:.2e} near-1 maxima={len(loc)} "
                      f"R roots>u1={len(rr)} Q roots={len(qr)} {[round(float(z.mid()), 4) for z in qr][:10]} "
                      f"rows={len(A)}", flush=True)
            if mf <= 1e-30 and it >= 2 and abs(hist[-1]["bound"] - hist[-2]["bound"]) < 1e-25:
                break
            new_fg = [u for u in add_u]
            # points across every interval where R > 0 beyond u1 / Q < 0 (between rigorously isolated roots)
            def spans(roots, P, sign, lo_lim):
                pts = []
                ms = [float(z.mid()) for z in roots]
                edges = sorted(set([lo_lim] + [m for m in ms if m >= lo_lim]))
                for a0, a1 in zip(edges[:-1], edges[1:]):
                    mid = (a0 + a1) / 2
                    if sign * P(fq(Fraction(mid))) > 0:
                        pts += [a0 + (a1 - a0) * j / 10 for j in range(11)]
                if ms and ms[-1] >= lo_lim and sign * P(fq(Fraction(ms[-1] * 1.0001 + 1e-9))) > 0:
                    pts += [ms[-1] * (1 + 0.01 * j) for j in range(11)]
                return pts
            for u in spans(rr, R, +1, self.u1):
                rows_t.append(self.row_tail(u)[:2]); P_t.append(u)
            for t in spans(qr, Q, -1, 0.0):
                rows_q.append(self.row_q(max(0.0, t))); P_q.append(max(0.0, t))
            for u in new_fg:
                rows_fg.append(self.row_fg(u)); P_fg.append(u)
            if ckpt:                                  # end-of-round state; written atomically
                st = {'sig': [self.d, str(self.alpha_q), str(self.b), self.K, self.alpha_is_pi], 'P_fg': P_fg, 'P_t': P_t, 'P_q': P_q,
                      'next_round': it + 1, 'hist': hist, 'bound': bound, 'c0': [str(x.mid().fmpq()) for x in c0],
                      'best': None if best is None else [best[0], [str(x.mid().fmpq()) for x in best[1]], best[2], best[3]]}
                json.dump(st, open(ckpt + '.tmp', 'w')); os.replace(ckpt + '.tmp', ckpt)
        out = {"bound_hp": bound, "history": hist, "coeffs": [x.mid().str(80) for x in self.c],
               "coeffs_exact": [str(x.mid().fmpq()) for x in self.c], "b": str(self.b), "u1": self.u1}
        if best is not None:
            out.update({"best_round": best[3], "best_B_lower": best[0], "best_certificate": best[2],
                        "best_coeffs_exact": [str(x.mid().fmpq()) for x in best[1]]})
            self.c = best[1]               # certify() after solve() re-certifies the best coefficients
        return out

    # rigorous certificate -------------------------------------------------------------------------------------
    def certify(self, c=None, tau_start=1e-35, max_boxes=5_000_000):
        Q, R = self.exact_polys(c)
        d, K = self.d, self.keff
        out = {"K_eff": K, "d": d, "b": str(self.b), "lam": str(self.lam), "u1": str(self.u1q)}
        lcR, lcQ = R.coeffs()[-1], Q.coeffs()[-1]
        assert lcR < 0 and lcQ > 0, "top-coefficient signs"
        # beyond the largest real root of R (and beyond u1) R < 0, so f < 0 <= g there; below it f/g is bounded by bisection
        rr = real_roots(R)
        U = max(self.u1, max([hi_(z) for z in rr], default=0.0) * 1.0001 + 1.0)
        assert all(hi_(z) < U for z in rr) and R(fq(Fraction(U))) < 0
        out["R_real_roots"] = [z.str(10) for z in rr]
        out["U_check"] = U
        # f/g <= 1 + tau0 on [0, U]
        Ra = arb_poly([arb(x) for x in R.coeffs()])
        dRa = Ra.derivative()
        bd, ka = self.bd, self.kappa
        F = lambda I: bd * (-(ka * I)).exp() * Ra(I)
        dF = lambda I: bd * (-(ka * I)).exp() * (dRa(I) - ka * Ra(I))
        # starting tau0 from the exact critical points of f/g (roots of R' - kappa R) and the end points
        crit = [z for z in real_roots(R.derivative() - fq(self.kappa_q) * R) if 0 <= float(z.mid()) <= U]
        fmax = max([float(F(arb(z.mid())).mid()) for z in crit] + [float(F(arb(0)).mid()), float(F(arb(U)).mid())])
        tau0 = max(fmax - 1, 0) * 2 + tau_start
        while True:
            try:
                nb = prove_upper_enc([make_encloser(Ra, bd, -ka)], arb(1) + arb(fq(Fraction(tau0))), 0.0, U,
                                     max_boxes=max_boxes)
                break
            except RuntimeError as e:
                out.setdefault("fg_retries", []).append(str(e)[:120])
                tau0 *= 16
                if tau0 > 1e-6:
                    raise
        tau0 = Fraction(tau0)
        out.update({"tau0": float(tau0), "fg_boxes": nb, "fg_max_sampled_minus_1": fmax - 1})
        # fhat >= 0 after the Gaussian lift: Q(t) + delta e^{s t} >= 0
        Qa = arb_poly([arb(x) for x in Q.coeffs()])
        dQa = Qa.derivative()
        lam = arb(fq(self.lam))
        s = (1 - 1 / lam) / 2
        qr = [z for z in real_roots(Q) if hi_(z) >= 0]
        for i in range(len(qr) - 1):
            assert hi_(qr[i]) < lo_(qr[i + 1]), "root balls overlap"
        edges = [(0.0, 0.0)] + [(lo_(z), hi_(z)) for z in qr]
        check = []
        for i in range(len(edges) - 1):
            lo, hi = edges[i][1], edges[i + 1][0]
            if hi > lo and Q(fq(Fraction((lo + hi) / 2))) < 0:
                check.append((max(0.0, edges[i][0]), edges[i + 1][1]))
        for z in qr:
            check.append((max(0.0, lo_(z) - float(z.rad())), hi_(z) + float(z.rad())))
        # lift width: lam from the ladder lam0 * 2^j (j = 0..6), lam0 = self.lam (>= 1/b, > 1); every lam is valid, the
        # one with the largest estimated bound is proved first (next ones on failure)
        samples = []
        for lo, hi in check:
            for x in np.linspace(lo, hi, 401):
                xa = arb(float(x))
                samples.append((xa, Qa(xa)))
        base = Qa(arb(0)) - bd * Ra(arb(0))
        cands = []
        for j in range(7):
            lamq = fq(self.lam) * (2 ** j)
            lam = arb(lamq)
            s_l = (1 - 1 / lam) / 2
            dmin = arb(0)
            for xa, qv in samples:
                v = qv * (-(s_l * xa)).exp()
                if v < dmin:
                    dmin = v
            delta = (-dmin.mid().fmpq()) * 4 + fmpq(1, 10 ** 60) if dmin < 0 else fmpq(0)
            de = arb(delta)
            lift = de * (lam * self.beta) ** (arb(d) / 2)
            Best = (base + de - lift) / (1 + arb(fq(tau0)) + lift)
            cands.append((float(Best.mid()), lamq, delta))
        cands.sort(key=lambda z: -z[0])
        proved = None
        for _, lamq, delta in cands:
            lam = arb(lamq)
            s_l = (1 - 1 / lam) / 2
            de = arb(delta)
            encQ = [make_encloser(arb_poly([-x for x in Qa.coeffs()]), arb(1), arb(0), nexp=0),
                    make_encloser(arb_poly([arb(1)]), -de, s_l)]
            try:
                nbq = sum(prove_upper_enc(encQ, arb(0), lo, hi, max_boxes=max_boxes) for lo, hi in check)
            except RuntimeError as e:
                out.setdefault("fhat_retries", []).append(f"lam={lamq}: {str(e)[:100]}")
                continue
            proved = (lam, lamq, delta, de, nbq)
            break
        if proved is None:
            raise RuntimeError("fhat check failed for every lam")
        lam, lamq, delta, de, nbq = proved
        lift = de * (lam * self.beta) ** (arb(d) / 2)
        tau = arb(fq(tau0)) + lift
        num = Qa(arb(0)) + de - bd * Ra(arb(0)) - lift
        B = num / (1 + tau)
        out["lam_used"] = str(lamq)
        out.update({"Q_real_roots_nonneg": len(qr), "Q_check_intervals": len(check), "delta": float(delta),
                    "fhat_boxes": nbq, "tau_upper": float(tau.upper().mid()), "B_ball": B.str(30, radius=True),
                    "B_lower": B.lower().str(30), "B_raw": float((Qa(arb(0)) - bd * Ra(arb(0))).mid())})
        self.B = B
        return out


def prove_upper(F, dF, cap, lo, hi, max_boxes=3_000_000):
    """Prove F < cap on [lo, hi] by bisection: F(mid) + F'(box) [-w, w] < cap."""
    stack = [(lo, hi)]
    n = 0
    while stack:
        a0, a1 = stack.pop()
        mid = (a0 + a1) / 2
        w = (a1 - a0) / 2
        rad = arb(0, w * (1 + 1e-9) + 1e-300)
        enc = F(arb(mid)) + dF(arb(mid) + rad) * rad
        n += 1
        if enc < cap:
            continue
        if w < 1e-60 * max(1.0, abs(a1)) or w == 0 or mid in (a0, a1):
            raise RuntimeError(f"check failed near {mid!r}: enclosure {enc.str(8, radius=True)}")
        if n > max_boxes:
            raise RuntimeError("too many boxes")
        stack += [(a0, mid), (mid, a1)]
    return n


# ------------------------------------------------------------------------------------------------------------
# Tight box enclosures by Taylor shift (replaces the plain centred form, which overestimates enormously for
# high-degree polynomials with large alternating coefficients).
# ------------------------------------------------------------------------------------------------------------
def make_encloser(Pa, A, c, nexp=60):
    """Return enc(m, w) -> arb enclosing { A e^{c u} P(u) : |u - m| <= w } (P: arb_poly with exact coefficients,
    A: arb, c: arb).  P(m + h) by composition (Taylor shift at the point m), e^{c h} by its Taylor polynomial of
    degree nexp plus a rigorous remainder (|c| w)^{n+1}/(n+1)! e^{|c| w} times a bound on |P(m + h)|."""
    E = [arb(1)]
    for n in range(1, nexp + 1):
        E.append(E[-1] * c / n)
    Ea = arb_poly(E)
    ca = abs(c)

    def enc(m, w):
        ma = arb(m)
        S = Pa(arb_poly([ma, 1]))
        h = arb(0, w)
        Sabs = sum((abs(x) * arb(w) ** j for j, x in enumerate(S.coeffs())), arb(0))
        rem = (ca * w) ** (nexp + 1) / arb(nexp + 1).gamma() * (ca * w).exp() * Sabs if nexp is not None else arb(0)
        core = (S * Ea)(h)
        return A * (c * ma).exp() * (core + arb(0, 1) * rem)
    return enc


def prove_upper_enc(encs, cap, lo, hi, max_boxes=5_000_000):
    """Prove sum_i enc_i(box) < cap on [lo, hi] by bisection; encs: list of enclosers. Returns box count."""
    stack = [(lo, hi)]
    n = 0
    while stack:
        a0, a1 = stack.pop()
        m = (a0 + a1) / 2
        w = (a1 - a0) / 2 * (1 + 1e-12) + 1e-300
        v = sum((e(m, w) for e in encs), arb(0))
        n += 1
        if v < cap:
            continue
        if (a1 - a0) / 2 < 1e-60 * max(1.0, abs(a1)) or m in (a0, a1):
            raise RuntimeError(f"check failed near {m!r}: enclosure {v.str(8, radius=True)}")
        if n > max_boxes:
            raise RuntimeError("too many boxes")
        stack += [(a0, m), (m, a1)]
    return n
