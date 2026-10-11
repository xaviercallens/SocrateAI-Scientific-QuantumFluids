"""Independent verification of the lattice-sum engine (run before trusting any result)."""
import json, sys, math, time
import numpy as np
from scipy import special
from lattsum import Kernel, grid_kernels, reduce_cell, energy_grad_norm
from structures import references
from opt import energy, minimize_structure

out = []
def rec(**kw):
    out.append(kw)
    print(json.dumps(kw), flush=True)

refs = references()
rng = np.random.default_rng(1)

# 1. gradient finite differences, all kernel kinds
for kern in (Kernel('gauss', 0.5), Kernel('gauss', 4.0), Kernel('yukawa', 1.3), Kernel('riesz', 3)):
    N = 5
    A0 = np.eye(3) * 1.7 + 0.2 * rng.normal(size=(3, 3))
    S = rng.random((N, 3))
    E, gA, gS = kern.eg(A0, S)
    num = np.zeros((3, 3))
    h = 1e-6
    for a in range(3):
        for b in range(3):
            Ap = A0.copy(); Ap[a, b] += h
            Am = A0.copy(); Am[a, b] -= h
            num[a, b] = (kern.eg(Ap, S)[0] - kern.eg(Am, S)[0]) / (2 * h)
    numS = np.zeros((N, 3))
    for i in range(N):
        for a in range(3):
            Sp = S.copy(); Sp[i, a] += h
            Sm = S.copy(); Sm[i, a] -= h
            numS[i, a] = (kern.eg(A0, Sp)[0] - kern.eg(A0, Sm)[0]) / (2 * h)
    rec(test='gradient_fd', kernel=kern.label(), E=E,
        maxerr_A=float(np.abs(num - gA).max()), maxerr_S=float(np.abs(numS - gS).max()),
        scale=float(max(np.abs(gA).max(), np.abs(gS).max())))

# 2. Gaussian: FCC/BCC/SC vs theta-function closed forms (independent of the engine)
def th(b, shift=0.0, sign=1, K=60):
    k = np.arange(-K, K + 1)
    n = k + shift
    sg = np.where(k % 2 == 0, 1.0, float(sign))
    return float(np.sum(sg * np.exp(-b * n * n)))
worst = 0
for a in np.logspace(-1, 1, 13):
    kern = Kernel('gauss', a)
    # SC unit density: r^2 = n^2
    E_sc = 0.5 * (th(a) ** 3 - 1)
    # FCC: D3 scaled c=2^{-1/3}: r^2 = 2^{-2/3} |n|^2, even-sum indicator
    b = a * 2 ** (-2 / 3)
    E_fcc = 0.5 * (0.5 * (th(b) ** 3 + th(b, sign=-1) ** 3) - 1)
    # BCC: Z^3 U (Z+1/2)^3 scaled r^2 = 2^{2/3}|n|^2
    b = a * 2 ** (2 / 3)
    E_bcc = 0.5 * (th(b) ** 3 + th(b, shift=0.5) ** 3 - 1)
    sc = (np.eye(3), np.zeros((1, 3)))
    for nm, E_an, st in (('SC', E_sc, sc), ('FCC', E_fcc, refs['FCC'][:2]), ('BCC', E_bcc, refs['BCC'][:2])):
        E_num = energy(kern, st[0], st[1])
        rel = abs(E_num - E_an) / abs(E_an)
        worst = max(worst, rel)
        rec(test='gauss_theta', lattice=nm, a=float(a), E_engine=E_num, E_theta=E_an, rel=rel,
            mode='recip' if kern.use_recip else 'real')
rec(test='gauss_theta_worst', rel=worst)

# 2b. force the other Gaussian branch (real vs recip) on a few a-values
for a in (1.0, 2.0, 3.0):
    k1 = Kernel('gauss', a)
    k2 = Kernel('gauss', a)
    # switch branch by hand
    if k1.use_recip:
        k2.use_real, k2.use_recip, k2.rc2, k2.gc2 = True, False, 45.0 / a, 1.0
    else:
        k2.use_real, k2.use_recip, k2.rc2, k2.gc2 = False, True, 1.0, 4 * a * 45.0
    for nm in ('FCC', 'A15'):
        e1 = energy(k1, *refs[nm][:2]); e2 = energy(k2, *refs[nm][:2])
        rec(test='gauss_branch', a=a, struct=nm, E1=e1, E2=e2, rel=abs(e1 - e2) / abs(e1))

# 3. tau / cutoff independence + brute force direct sums (Riesz, Yukawa)
def brute(kfun, A0, S, R):
    """direct (1/2N) sum over |r|<R, no tail. A0 normalised to det N."""
    N = len(S)
    A = A0 * (N / np.linalg.det(A0)) ** (1 / 3)
    nmax = [int(math.ceil(R * np.linalg.norm(np.linalg.inv(A)[:, k]) + 1)) for k in range(3)]
    rng_ = [np.arange(-n, n + 1) for n in nmax]
    n = np.array(np.meshgrid(*rng_, indexing='ij')).reshape(3, -1).T
    tot = 0.0
    for i in range(N):
        for j in range(N):
            d = (S[i] - S[j] + n) @ A
            r2 = (d * d).sum(1)
            m = (r2 < R * R) & (r2 > 1e-12)
            tot += kfun(r2[m]).sum()
    return tot / (2 * N)

cases = [('riesz', 2, lambda r2: r2 ** -2.0, 'tail'), ('riesz', 3, lambda r2: r2 ** -3.0, 'tail'),
         ('riesz', 6, lambda r2: r2 ** -6.0, 'tail'),
         ('yukawa', 0.1, lambda r2: np.exp(-0.1 * np.sqrt(r2)) / np.sqrt(r2), 'tail'),
         ('yukawa', 1.0, lambda r2: np.exp(-np.sqrt(r2)) / np.sqrt(r2), 'tail'),
         ('yukawa', 10.0, lambda r2: np.exp(-10 * np.sqrt(r2)) / np.sqrt(r2), 'tail')]
for name, par, kf, _ in cases:
    for st in ('FCC', 'BCC', 'HCP', 'A15'):
        A0, S = refs[st][:2]
        Es = []
        for tau, xc in ((3.0, 55.0), (1.5, 55.0), (6.0, 70.0)):
            Es.append(energy(Kernel(name, par, tau=tau, xc=xc), A0, S))
        sp = (max(Es) - min(Es)) / abs(Es[0])
        R = 45.0 if name == 'yukawa' and par < 0.5 else 30.0
        B = brute(kf, A0, S, R)
        # continuum tail of the direct sum beyond R (per particle, density 1): (1/2) int_R^inf 4 pi r^2 f(r) dr
        if name == 'riesz':
            s = 2 * par
            tail = 0.5 * 4 * math.pi * R ** (3 - s) / (s - 3)
        else:
            from scipy.integrate import quad
            tail = 0.5 * 4 * math.pi * quad(lambda r: r * r * math.exp(-par * r) / r, R, np.inf)[0]
        rec(test='tau_and_bruteforce', kernel=f"{name}_{par}", struct=st, E=Es[0], spread_tau_xc=sp,
            E_brute=B + tail, rel_brute=abs(B + tail - Es[0]) / abs(Es[0]), tail_rel=tail / Es[0])

# 4. general-s Epstein/Ewald in numpy+scipy (negative-order incomplete gamma by recursion) vs engine, m=2,3,6
def gammainc_upper(a, x):
    """Gamma(a,x), any real a (recursion down from a>0)."""
    if a > 0:
        return special.gamma(a) * special.gammaincc(a, x)
    return (gammainc_upper(a + 1, x) - x ** a * np.exp(-x)) / a

def epstein_general(s, A0, S, tau=3.0):
    N = len(S); A = A0 * (N / np.linalg.det(A0)) ** (1 / 3)
    m = s / 2
    V = N
    nr = 8
    nn = np.array(np.meshgrid(*[np.arange(-nr, nr + 1)] * 3, indexing='ij')).reshape(3, -1).T
    Er = 0.0
    for i in range(N):
        for j in range(N):
            d = (S[i] - S[j] + nn) @ A
            r2 = (d * d).sum(1); msk = r2 > 1e-12
            Er += (special.gammaincc(m, tau * r2[msk]) / r2[msk] ** m).sum()
    Binv = np.linalg.inv(A)
    mm = np.array(np.meshgrid(*[np.arange(-nr, nr + 1)] * 3, indexing='ij')).reshape(3, -1).T
    G = 2 * np.pi * mm @ Binv.T
    g2 = (G * G).sum(1)
    nz = g2 > 1e-12
    ph = 2 * np.pi * mm @ S.T
    Sf = np.exp(1j * ph).sum(1)
    h = np.pi ** 1.5 * (g2[nz] / 4) ** (m - 1.5) * np.array([gammainc_upper(1.5 - m, g / (4 * tau)) for g in g2[nz]]) / special.gamma(m)
    Erec = (h * np.abs(Sf[nz]) ** 2).sum() / V
    h0 = np.pi ** 1.5 * tau ** (m - 1.5) / ((m - 1.5) * special.gamma(m))
    self0 = tau ** m / (m * special.gamma(m))
    return (Er + Erec + N * h0 / V * N - N * self0) / (2 * N)

for mval in (2, 3, 6):
    for st in ('FCC', 'BCC', 'HCP'):
        A0, S = refs[st][:2]
        e1 = energy(Kernel('riesz', mval), A0, S)
        e2 = epstein_general(2 * mval, A0, S)
        rec(test='epstein_scipy', s=2 * mval, struct=st, E_engine=e1, E_scipy=e2, rel=abs(e1 - e2) / abs(e1))

# 5. reference geometry sanity: nearest-neighbour distances of C15 / A15 (unit density)
for nm in ('C15', 'A15'):
    A0, S = refs[nm][:2]
    N = len(S); A = A0 * (N / np.linalg.det(A0)) ** (1 / 3)
    nn = np.array(np.meshgrid(*[np.arange(-2, 3)] * 3, indexing='ij')).reshape(3, -1).T
    dm = []
    for j in range(1, N):
        d = np.linalg.norm((S[0] - S[j] + nn) @ A, axis=1); dm.append(d.min())
    a = np.linalg.det(A) ** (1 / 3)
    rec(test='geometry', struct=nm, natoms=N, a_cubic=float(a), nn_over_a=float(min(dm) / a))

json.dump(out, open('verify_records.json', 'w'), indent=1)
