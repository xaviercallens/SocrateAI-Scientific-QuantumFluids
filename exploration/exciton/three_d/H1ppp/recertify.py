"""H1''' post-hoc re-check (review docs/designs/EXCITON_FLUID_VERIFIER_NOTES_H1ppp.md, item B1). Usage: python recertify.py records/*.json ../H1pp/records/*.json
Independent re-certification (read-only use of rig3.py helpers):
 - bisection boxes cover exactly (radius >= exact distance from float midpoint to both ends);
 - root enclosures converted to floats with outward rounding; overlapping padded balls merged into clusters;
 - Q + delta e^{s t} >= 0 proved on every cluster and every inter-cluster gap where Q(mid) < 0 (exact sign).
Uses the record's lam_used and float(delta) (taken as exact rational) and recomputes B."""
import sys, json, math, time
from fractions import Fraction
import os
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import rig3
from rig3 import real_roots, make_encloser, fq
from flint import arb, fmpq, arb_poly

def prove(encs, cap, lo, hi, max_boxes=20_000_000):
    stack = [(lo, hi)]; n = 0
    while stack:
        a0, a1 = stack.pop()
        m = (a0 + a1) / 2
        we = max(Fraction(a1) - Fraction(m), Fraction(m) - Fraction(a0))
        w = math.nextafter(float(we), math.inf) * (1 + 1e-12) + 1e-300
        assert Fraction(w) >= we
        v = sum((e(m, w) for e in encs), arb(0)); n += 1
        if v < cap: continue
        if m in (a0, a1): raise RuntimeError(f"check failed near {m!r}: {v.str(8, radius=True)}")
        if n > max_boxes: raise RuntimeError("too many boxes")
        stack += [(a0, m), (m, a1)]
    return n

def flo(z):   # float <= every point of ball z
    x = z.lower().mid().fmpq(); f = float(Fraction(int(x.p), int(x.q)))
    return f if Fraction(f) <= Fraction(int(x.p), int(x.q)) else math.nextafter(f, -math.inf)
def fhi(z):
    x = z.upper().mid().fmpq(); f = float(Fraction(int(x.p), int(x.q)))
    return f if Fraction(f) >= Fraction(int(x.p), int(x.q)) else math.nextafter(f, math.inf)

def parse(x): return fmpq(*map(int, x.split('/'))) if '/' in x else fmpq(int(x))

for path in sys.argv[1:]:
    rec = json.load(open(path)); t0 = time.time()
    lp = rig3.HPRig(rec['d'], rec['alpha'], rec['b'], rec['K'], lam=rec['lam'], gcut=rec['gcut'])
    Q, R = lp.exact_polys([parse(x) for x in rec['solve']['best_coeffs_exact']])
    d = lp.d
    assert R.coeffs()[-1] < 0 and Q.coeffs()[-1] > 0
    rr = real_roots(R)
    U = max(lp.u1, max([fhi(z) for z in rr], default=0.0) * 1.0001 + 1.0)
    assert all(fhi(z) < U for z in rr) and R(fq(Fraction(U))) < 0
    Ra = arb_poly([arb(x) for x in R.coeffs()])
    tau0 = Fraction(rec['certificate']['tau0'])
    nb = prove([make_encloser(Ra, lp.bd, -lp.kappa)], arb(1) + arb(fq(tau0)), 0.0, U)
    # fhat part
    Qa = arb_poly([arb(x) for x in Q.coeffs()])
    lamq = Fraction(rec['certificate']['lam_used']); lam = arb(fq(lamq))
    assert lamq >= 1 / lp.b
    delta = Fraction(rec['certificate']['delta']); de = arb(fq(delta))
    s_l = (1 - 1 / lam) / 2
    balls = sorted([(flo(z), fhi(z)) for z in real_roots(Q) if fhi(z) >= 0])
    cl = []
    for a, b in balls:
        a = max(a, 0.0)
        if cl and a <= cl[-1][1]: cl[-1][1] = max(cl[-1][1], b)
        else: cl.append([a, b])
    check = [tuple(c) for c in cl]
    edges = [0.0] + [x for c in cl for x in c]
    gaps = [(edges[0], cl[0][0])] if cl else []
    gaps += [(cl[i][1], cl[i + 1][0]) for i in range(len(cl) - 1)]
    for a, b in gaps:
        if b > a and Q(fq((Fraction(a) + Fraction(b)) / 2)) < 0: check.append((a, b))
    if cl: assert Q(fq(Fraction(cl[-1][1]) + 1)) > 0
    encQ = [make_encloser(arb_poly([-x for x in Qa.coeffs()]), arb(1), arb(0), nexp=0), make_encloser(arb_poly([arb(1)]), -de, s_l)]
    try:
        nq = sum(prove(encQ, arb(0), a, b) for a, b in check); status = 'record delta OK'
    except RuntimeError as e:
        status = f'RECORD DELTA FAILS ({str(e)[:70]})'
        for ex in range(36, 15, -1):
            delta = Fraction(1, 10**ex); de = arb(fq(delta))
            encQ = [make_encloser(arb_poly([-x for x in Qa.coeffs()]), arb(1), arb(0), nexp=0), make_encloser(arb_poly([arb(1)]), -de, s_l)]
            try:
                nq = sum(prove(encQ, arb(0), a, b) for a, b in check); status += f'; delta=1e-{ex} proves'; break
            except RuntimeError:
                continue
        else:
            status += '; NO delta <= 1e-16 proves'
    lift = de * (lam * lp.beta) ** (arb(d) / 2)
    tau = arb(fq(tau0)) + lift
    B = (Qa(arb(0)) + de - lp.bd * Ra(arb(0)) - lift) / (1 + tau)
    print(path.split('/')[-2] + '/' + path.split('/')[-1], 'recert B_lower', B.lower().str(20), '| record', rec['certificate']['B_lower'][:24],
          '|', status, '| clusters', len(cl), 'checks', len(check), 'boxes', nb, nq, f'{time.time()-t0:.1f}s', flush=True)
