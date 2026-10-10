"""Exact-rational series machinery for chapter 4 (independent of the Lean file, in Python):
reversion k(u), density of states g_n = coefficients of k^2 dk/du, and the T-series coefficients of C_V to high order.
Used (i) to cross-check the six closed forms A..L, (ii) to show that the series continues indefinitely and is asymptotic."""
from fractions import Fraction as Fr
import numpy as np
from mpmath import mp, mpf, zeta as mzeta, factorial as mfac, pi as mpi
import ch04_common as cc
mp.dps = 40

def revert(a, N):
    """k(u) up to u^N for u = k(1 + sum a[j] k^j), a = {2: a2, 3: a3, ...} (Fractions).  Fixed-point iteration, exact."""
    k = [Fr(0)]*(N+1); k[1] = Fr(1)
    def mul(p, q):
        r = [Fr(0)]*(N+1)
        for i, pi_ in enumerate(p):
            if pi_ == 0: continue
            for j, qj in enumerate(q):
                if i+j > N: break
                r[i+j] += pi_*qj
        return r
    for _ in range(N):
        pw = [None, k]
        for j in range(2, max(a)+1+1): pw.append(mul(pw[-1], k))
        new = [Fr(0)]*(N+1); new[1] = Fr(1)
        for j, aj in a.items():
            for i in range(N+1): new[i] -= aj*pw[j+1][i]
        if new == k: break
        k = new
    return k

def dos(a, N):
    k = revert(a, N)
    dk = [ (i+1)*k[i+1] for i in range(N)] + [Fr(0)]
    k2 = [Fr(0)]*(N+1)
    for i in range(N+1):
        for j in range(N+1-i): k2[i+j] += k[i]*k[j]
    g = [Fr(0)]*(N+1)
    for i in range(N+1):
        for j in range(N+1-i): g[i+j] += k2[i]*dk[j]
    return g[:N+1-0]

A_RAT = {2: Fr(31, 20), 3: Fr(-101, 25), 4: Fr(23, 10)}     # 1.55, -4.04, 2.30 exactly

def cv_coeffs(N=40, a=A_RAT):
    """Return {p: coefficient of T^p in J/(mol K^p)} for p = n+1, from g_n, n = 2..N (note: g_n exact up to order N of k(u))."""
    g = dos(a, N)
    out = {}
    pref = mpf(cc.Vm*1e30)*mpf(cc.kB)/(2*mpi**2)
    th = mpf(cc.THETA)
    for n in range(2, N+1):
        if g[n] == 0: continue
        gn = mpf(g[n].numerator)/mpf(g[n].denominator)
        out[n+1] = pref*gn*mfac(n+2)*mzeta(n+2)/th**(n+1)
    return out, g

if __name__ == "__main__":
    out, g = cv_coeffs(12)
    co = cc.coeffs_SI()
    for name, p in cc.POWERS.items():
        print(name, p, float(out[p]), co[name], float(out[p])/co[name]-1)
    print("g_n (exact):", [str(x) for x in g[:10]])
    print("T^4 term:", out.get(4, 0), " T^10:", float(out.get(10, 0)), " T^11", float(out.get(11,0)))
