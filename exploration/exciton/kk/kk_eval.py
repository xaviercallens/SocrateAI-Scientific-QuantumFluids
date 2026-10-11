#!/usr/bin/env python3
"""L1 KK-tower evaluator for the gated kernel (see PREREG.md). Run: python3 kk_eval.py"""
import json, time, numpy as np
from scipy.special import k0e
import mpmath as mp

def modal(r, h1, h2, ze, zh, tol=1e-17, mmax=100000):
    """(4/l) sum (phi_m(ze)-phi_m(zh))^2 K0(m pi r / l); r array. Truncated where e^{-m pi r/l} < tol (in units of the sum)."""
    l = h1 + h2
    r = np.atleast_1d(np.asarray(r, float))
    M = int(min(mmax, np.ceil(l / (np.pi * r.min()) * (np.log(1/tol) + 5)) + 2))
    m = np.arange(1, M + 1)
    w = (np.sin(m*np.pi*(ze + h2)/l) - np.sin(m*np.pi*(zh + h2)/l))**2
    x = np.pi*np.outer(r, m)/l
    return (4/l)*(k0e(x)*np.exp(-x)*w).sum(1)

def _srcs(h1, h2, ze, zh):
    # (offset c, sign) for each of six pair terms: V_ee + V_hh - 2 V_eh ; image of z' reflected about plane z=h1
    out = []
    for (z, zp, wt) in ((ze, ze, 1.0), (zh, zh, 1.0), (ze, zh, -2.0)):
        out.append((z - zp, wt))
        out.append((z + zp - 2*h1, -wt))
    return out

def images(r, h1, h2, ze, zh, N=60, tail=True):
    """Image sum |n|<=N plus Euler-Maclaurin tail (through f''') for both ends. tail=False: plain truncation."""
    P = 2*(h1 + h2)
    r = np.atleast_1d(np.asarray(r, float))
    n = np.arange(-N, N + 1)
    tot = np.zeros_like(r)
    srcs = _srcs(h1, h2, ze, zh)
    for c, s in srcs:
        u = c - P*n
        tot += s*(1/np.sqrt(r[:, None]**2 + u[None, :]**2)).sum(1)
    if tail:
        for c, s in srcs:
            for sgn in (+1, -1):                       # n -> +inf and n -> -inf
                x = sgn*N
                u = c - P*x
                S = np.sqrt(r**2 + u**2)
                f = 1/S
                # integral from |x|=N to infinity of f (conditionally combined over sources, sum(s)=0)
                # d/dx f = -u * (-P)/S^3 ... use g(u): f(x)=g(u), du/dx=-P
                g1 = -u/S**3; g3 = u*(9*r**2 - 6*u**2)/S**7
                fp = -P*g1; fppp = -P**3*g3
                # sum_{n=N+1}^inf f(n) = int_N^inf f - f(N)/2 - f'(N)/12 + f'''(N)/720 ; for n->-inf mirror: f'->-f'
                em = -f/2 - sgn*fp/12 + sgn*fppp/720
                tot += s*em
        # integral parts: sum over sources of s*asinh-terms (the logs cancel since sum s = 0)
        for c, s in srcs:
            tot += s*(np.arcsinh((c - P*N)/r) + np.arcsinh((c + P*N)/r)*(-1))*(1/P)*(+1)
    return tot

def reference(r, h1, h2, ze, zh, dps=30):
    mp.mp.dps = dps
    l = mp.mpf(h1) + h2
    out = []
    for rr in r:
        rr = mp.mpf(rr); s = mp.mpf(0); m = 1
        while True:
            w = (mp.sin(m*mp.pi*(mp.mpf(ze)+h2)/l) - mp.sin(m*mp.pi*(mp.mpf(zh)+h2)/l))**2
            t = w*mp.besselk(0, m*mp.pi*rr/l)
            s += t
            if m*mp.pi*rr/l > 2.4*dps: break   # e^{-x} < 1e-(1.04 dps): bound on the tail; zero terms never stop the sum
            m += 1
            if m > 400000: break
        out.append(4/l*s)
    return out

if __name__ == "__main__":
    sets = [(1, 1.5, 0.3, -0.4), (0.5, 0.5, 0.1, -0.2), (1, 3, 0.9, -2.0), (2, 0.4, 1.5, -0.2)]
    res = []
    for (h1, h2, ze, zh) in sets:
        l = h1 + h2
        r = l*np.logspace(-2, np.log10(20), 40)
        ref = np.array([float(v) for v in reference(r, h1, h2, ze, zh)])
        mo = modal(r, h1, h2, ze, zh)
        im = images(r, h1, h2, ze, zh, N=60)
        e_mo = np.abs(mo/ref - 1); e_im = np.abs(im/ref - 1)
        res.append(dict(set=[h1, h2, ze, zh], r_over_l=(r/l).tolist(), relerr_modal=e_mo.tolist(), relerr_images_EM=e_im.tolist()))
        print((h1, h2, ze, zh), "modal max relerr %.2e  images+EM(N=60) max relerr %.2e" % (e_mo.max(), e_im.max()))
        # where does each fail 1e-12
        print("   modal ok r/l >=", (r/l)[e_mo <= 1e-12].min() if (e_mo <= 1e-12).any() else None,
              "| images ok for r/l <=", (r/l)[e_im <= 1e-12].max() if (e_im <= 1e-12).any() else None)
    json.dump(res, open("accuracy.json", "w"))
