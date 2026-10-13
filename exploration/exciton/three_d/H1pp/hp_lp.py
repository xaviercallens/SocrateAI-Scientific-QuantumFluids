"""High-precision primal-dual interior-point LP (Mehrotra predictor-corrector), python-flint arb at ctx.prec bits.

    maximise obj . c   subject to   A c <= b      (c free; A m x n, m >> n)

Used by H1'' because the two-point LP needs ~25 significant digits where g = e^{-alpha r^2} is ~1e-14 (the terms of f are
O(1) and must cancel to below g there).  Radii are stripped after every operation (midpoint arithmetic): this is a solver,
not a certificate; the certificate is computed separately from the exact rational coefficients.
"""
import flint
from flint import arb, arb_mat


def _mid(x):
    return arb(x.mid())


def solve_ipm(A_rows, b, obj, c0=None, tol_feas=1e-45, tol_gap=1e-40, max_it=200, verbose=False, s_floor=None):
    """A_rows: list of m lists of n arb; b: list of m arb; obj: list of n arb.  Returns dict with c (list of arb)."""
    m, n = len(A_rows), len(obj)
    A = arb_mat(m, n, [x for row in A_rows for x in row])
    At = A.transpose()
    objm = arb_mat(n, 1, obj)
    bm = b
    c = arb_mat(n, 1, c0 if c0 is not None else [0] * n)
    Ac = A * c
    one = arb(1)
    if s_floor is None:
        s_floor = arb("1e-6")
    s = [max(bm[i] - Ac[i, 0], s_floor) if (bm[i] - Ac[i, 0]) > s_floor else s_floor for i in range(m)]
    mu0 = arb("1e-4")
    y = [mu0 / si for si in s]
    hist = []
    for it in range(max_it):
        Ac = A * c
        rp = [_mid(Ac[i, 0] + s[i] - bm[i]) for i in range(m)]
        ym = arb_mat(m, 1, y)
        Aty = At * ym
        rd = [_mid(Aty[j, 0] - objm[j, 0]) for j in range(n)]
        gap = sum((s[i] * y[i] for i in range(m)), arb(0))
        mu = gap / m
        pobj = sum((objm[j, 0] * c[j, 0] for j in range(n)), arb(0))
        nrp = max(abs(float(x.mid())) for x in rp)
        nrd = max(abs(float(x.mid())) for x in rd)
        hist.append((it, float(pobj.mid()), nrp, nrd, float(gap.mid())))
        if verbose and (it % 5 == 0):
            print(f"      ipm {it}: obj={float(pobj.mid()):.15f} |rp|={nrp:.1e} |rd|={nrd:.1e} gap={float(gap.mid()):.1e}",
                  flush=True)
        if nrp < tol_feas and nrd < tol_feas and float(gap.mid()) < tol_gap:
            break
        d = [y[i] / s[i] for i in range(m)]
        sq = [x.sqrt() for x in d]
        As = arb_mat(m, n, [x * sq[i] for i, row in enumerate(A_rows) for x in row])
        M = (As.transpose() * As).mid()

        def direction(rc):
            # M dc = -rd - A^T S^{-1}(rc + Y rp)
            v = arb_mat(m, 1, [_mid((rc[i] + y[i] * rp[i]) / s[i]) for i in range(m)])
            rhs = At * v
            rhs = arb_mat(n, 1, [_mid(-rd[j] - rhs[j, 0]) for j in range(n)])
            dc = M.solve(rhs).mid()
            Adc = A * dc
            ds = [_mid(-rp[i] - Adc[i, 0]) for i in range(m)]
            dy = [_mid((rc[i] - y[i] * ds[i]) / s[i]) for i in range(m)]
            return dc, ds, dy

        def steplen(v, dv):
            a = arb(1)
            for vi, dvi in zip(v, dv):
                if dvi < 0:
                    t = -vi / dvi
                    if t < a:
                        a = t
            return a

        # predictor
        rc = [-(s[i] * y[i]) for i in range(m)]
        dc, ds, dy = direction(rc)
        ap, ad = steplen(s, ds), steplen(y, dy)
        gap_aff = sum(((s[i] + ap * ds[i]) * (y[i] + ad * dy[i]) for i in range(m)), arb(0))
        sigma = (gap_aff / gap) ** 3
        if sigma > 1:
            sigma = arb(1)
        # corrector
        rc = [_mid(-(s[i] * y[i]) + sigma * mu - ds[i] * dy[i]) for i in range(m)]
        dc, ds, dy = direction(rc)
        eta = arb("0.995") if float(mu.mid()) > 1e-20 else arb("0.9999")
        ap, ad = steplen(s, ds), steplen(y, dy)
        ap = min(one, eta * ap) if ap * eta < one else one
        ad = min(one, eta * ad) if ad * eta < one else one
        c = arb_mat(n, 1, [_mid(c[j, 0] + ap * dc[j, 0]) for j in range(n)])
        s = [_mid(s[i] + ap * ds[i]) for i in range(m)]
        y = [_mid(y[i] + ad * dy[i]) for i in range(m)]
    pobj = sum((objm[j, 0] * c[j, 0] for j in range(n)), arb(0))
    return {"c": [c[j, 0] for j in range(n)], "obj": pobj, "iterations": it + 1, "history": hist, "y": y, "s": s}
