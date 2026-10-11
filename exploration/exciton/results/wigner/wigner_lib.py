"""Harmonic-phonon (Lindemann) estimate for the triangular lattice of the gated exciton kernel.
Units hbar = M = 1, lengths in d. phi(x) = Lambda * u(x).  See docs/designs/EXCITON_FLUID_WIGNER_PREREG.md."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "python"))
from gate_image_cm_sym import S as S_gate   # S(s, d, h), d = 1 here

SQ3 = np.sqrt(3.0)

# ---------------- kernel u(x), u'(x), u''(x) ----------------
def kernel(x, kind, h=None, npts=3000):
    """kind: 'dip' (x^-3), 'ungated' (2(1/x - 1/sqrt(x^2+1))), 'gated' (Laplace integral, gates at +-h, layers +-1/2)."""
    x = np.asarray(x, float)
    if kind == "dip":
        return x**-3, -3*x**-4, 12*x**-5
    if kind == "ungated":
        q = x*x + 1.0
        u = 2*(1/x - q**-0.5)
        u1 = 2*(-1/x**2 + x*q**-1.5)
        u2 = 2*(2/x**3 + q**-1.5 - 3*x*x*q**-2.5)
        return u, u1, u2
    if kind == "gated":
        P = 4.0*h
        smin = 0.02/(P*P)
        smax = 70.0/(x.min()**2)
        t = np.linspace(np.log(smin), np.log(smax), npts)
        s = np.exp(t)
        mu = S_gate(s, 1.0, h)/np.sqrt(np.pi*s)
        dt = t[1]-t[0]
        w = np.full(npts, dt); w[0] = w[-1] = dt/2
        base = (w*s*mu)                      # ds = s dt
        u = np.empty_like(x); u1 = np.empty_like(x); u2 = np.empty_like(x)
        xf = x.ravel()
        out = np.empty((3, xf.size))
        for i0 in range(0, xf.size, 400):
            xx = xf[i0:i0+400, None]
            E = np.exp(-s[None, :]*xx*xx)
            I0 = (E*base).sum(1)
            I1 = (E*base*s).sum(1)
            I2 = (E*base*s*s).sum(1)
            out[0, i0:i0+400] = I0
            out[1, i0:i0+400] = -2*xf[i0:i0+400]*I1
            out[2, i0:i0+400] = -2*I1 + 4*xf[i0:i0+400]**2*I2
        return out[0].reshape(x.shape), out[1].reshape(x.shape), out[2].reshape(x.shape)
    raise ValueError(kind)

def image_series_u(r, h, nmax=400000):
    """Independent real-space image series: U = V_ee + V_hh - 2 V_eh, layers z=-1/2,+1/2, grounded gates z=+-h.
    V(za,zb;r) = sum_n [1/sqrt(r^2+(za-zb-4hn)^2) - 1/sqrt(r^2+(za+zb-2h-4hn)^2)]  (images of zb: zb+4hn (+), 2h-zb+4hn (-))."""
    n = np.arange(-nmax, nmax+1, dtype=float)
    def V(za, zb):
        return (1/np.sqrt(r*r + (za-zb-4*h*n)**2) - 1/np.sqrt(r*r + (za+zb-2*h-4*h*n)**2)).sum()
    ze, zh = -0.5, 0.5
    return V(ze, ze) + V(zh, zh) - 2*V(ze, zh)

# ---------------- triangular lattice ----------------
def lattice_points(Rc_over_a):
    """unit-spacing triangular lattice vectors with 0 < |R| <= Rc."""
    m = int(Rc_over_a/ (SQ3/2)) + 2
    i, j = np.meshgrid(np.arange(-m, m+1), np.arange(-m, m+1), indexing="ij")
    X = i + 0.5*j; Y = (SQ3/2)*j
    R = np.hypot(X, Y)
    k = (R > 1e-9) & (R <= Rc_over_a)
    return X[k], Y[k], R[k]

def gamma_harmonic(nu, kind, h=None, Lam=1.0, Nq=64, Rc_over_a=60.0, return_all=False):
    """Harmonic Lindemann ratio gamma_h = sqrt(<u^2>)/a, nu = n d^2, potential Lam*u(x)."""
    a = np.sqrt(2.0/(SQ3*nu))
    X, Y, Ru = lattice_points(Rc_over_a)
    Rm = np.round(Ru, 9)
    uniq, inv = np.unique(Rm, return_inverse=True)
    u0, u1, u2 = kernel(uniq*a, kind, h)
    phi1 = Lam*u1[inv]; phi2 = Lam*u2[inv]; phi0 = Lam*u0[inv]
    R = Ru*a                                  # physical distance (units of d)
    # note derivatives are w.r.t. x = R (physical), Rhat unchanged
    cx = X/Ru; cy = Y/Ru
    L = phi2; T = phi1/R
    wxx = L*cx*cx + T*(1-cx*cx)
    wxy = (L-T)*cx*cy
    wyy = L*cy*cy + T*(1-cy*cy)
    Xp = X*a; Yp = Y*a
    # tail: -pi n Rc phi'(Rc) * identity (trace-averaged continuum)
    Rc = Rc_over_a*a
    uc = kernel(np.array([Rc]), kind, h)
    n_den = nu
    tail = -np.pi*n_den*Rc*Lam*uc[1][0]
    # BZ grid in reciprocal coordinates, shifted
    # lattice vectors a1=(a,0), a2=(a/2, a*sqrt3/2); reciprocal b1,b2 with a_i.b_j = 2 pi delta
    a1 = np.array([a, 0.0]); a2 = np.array([0.5*a, SQ3/2*a])
    A = np.array([a1, a2])
    B = 2*np.pi*np.linalg.inv(A).T
    f = (np.arange(Nq)+0.5)/Nq
    F1, F2 = np.meshgrid(f, f, indexing="ij")
    Qx = (F1*B[0, 0] + F2*B[1, 0]).ravel(); Qy = (F1*B[0, 1] + F2*B[1, 1]).ravel()
    sxx, sxy, syy = wxx.sum(), wxy.sum(), wyy.sum()
    Dxx = np.empty(Qx.size); Dxy = np.empty(Qx.size); Dyy = np.empty(Qx.size)
    for i0 in range(0, Qx.size, 512):
        C = np.cos(np.outer(Qx[i0:i0+512], Xp) + np.outer(Qy[i0:i0+512], Yp))
        Dxx[i0:i0+512] = sxx - C@wxx
        Dxy[i0:i0+512] = sxy - C@wxy
        Dyy[i0:i0+512] = syy - C@wyy
    # tail contribution: (1-cos) averaged -> add tail*identity (only where q.Rc >> 1; error is O(1/(q Rc))^k small)
    Dxx += tail; Dyy += tail
    tr = Dxx + Dyy; det = Dxx*Dyy - Dxy**2
    disc = np.sqrt(np.maximum(tr*tr/4 - det, 0.0))
    e1 = tr/2 - disc; e2 = tr/2 + disc
    ok = (e1 > 1e-14*np.abs(e2).max())
    # exclude the q=0-adjacent noise? grid is shifted so q != 0
    if not ok.all():
        # unstable lattice (negative eigenvalues)
        if (e1 < -1e-12*np.abs(e2).max()).any():
            return (np.inf, dict(unstable=True)) if return_all else np.inf
    u2m = 0.5*np.mean(1/np.sqrt(np.maximum(e1, 1e-300)) + 1/np.sqrt(e2))
    g = np.sqrt(u2m)/a
    if return_all:
        # classical energy per particle: 1/2 sum phi(R) + continuum tail  (-pi n int_{Rc}^inf phi R dR is skipped for non-dip)
        return g, dict(a=a, nR=int(R.size), tail=float(tail), eminmax=(float(e1.min()), float(e2.max())), Epot_sum=float(0.5*phi0.sum()))
    return g

def lattice_sum_dipole(Rc_over_a=200.0):
    X, Y, R = lattice_points(Rc_over_a)
    s = (R**-3).sum()
    # continuum tail: n_unit * 2 pi int_{Rc}^inf R^-3 R dR, n_unit = 2/sqrt3 per unit-spacing area
    tail = (2/SQ3)*2*np.pi/Rc_over_a
    return s + tail

def gamma_R(nu, kind, h=None, Lam=1.0, Nq=32, Rc_over_a=40.0):
    """Richardson-extrapolated harmonic Lindemann ratio (registered numerical method, amendment A1)."""
    g1 = gamma_harmonic(nu, kind, h, Lam, Nq, Rc_over_a)
    g2 = gamma_harmonic(nu, kind, h, Lam, 2*Nq, Rc_over_a)
    if not (np.isfinite(g1) and np.isfinite(g2)):
        return np.inf
    return 2*g2 - g1
