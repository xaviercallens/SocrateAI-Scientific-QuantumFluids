"""Independent re-minimisation of every B2 candidate (different tau/cutoffs, perturbed coordinates, tighter gtol)
plus a brute-force direct-sum energy check."""
import json, math, sys
import numpy as np
from scipy.integrate import quad
from lattsum import Kernel
from opt import minimize_structure, energy

cands = json.load(open('B2_candidates.json'))
out = []
# keep lowest candidate per (kernel, param)
best = {}
for c in cands:
    k = (c['kernel'], c['param'])
    if k not in best or c['E'] < best[k]['E']:
        best[k] = c

def brute(kfun, A0, S, R):
    N = len(S)
    A = A0 * (N / np.linalg.det(A0)) ** (1 / 3)
    Ai = np.linalg.inv(A)
    nmax = [int(math.ceil(R * np.linalg.norm(Ai[:, k]) + 1)) for k in range(3)]
    n = np.array(np.meshgrid(*[np.arange(-m, m + 1) for m in nmax], indexing='ij')).reshape(3, -1).T
    tot = 0.0
    for i in range(N):
        for j in range(N):
            d = (S[i] - S[j] + n) @ A
            r2 = (d * d).sum(1)
            m = (r2 < R * R) & (r2 > 1e-12)
            tot += kfun(r2[m]).sum()
    return tot / (2 * N)

rng = np.random.default_rng(5)
for (name, par), c in sorted(best.items()):
    A = np.array(c['A']); S = np.array(c['S'])
    k2 = Kernel(name, par, tau=1.7, xc=75.0, xcg=60.0)
    E_alt = energy(k2, A, S)
    # re-minimise from perturbed start with different engine settings
    res = []
    for t in range(3):
        Sp = S + 1e-3 * rng.normal(size=S.shape)
        Ap = A * (1 + 1e-3 * rng.normal(size=(3, 3)))
        E, A2, S2, _ = minimize_structure(k2, Ap, Sp, gtol=1e-11)
        res.append(E)
    # brute force
    if name == 'riesz':
        s = 2 * par
        kf = lambda r2: r2 ** (-s / 2); R = 30.0
        tail = 0.5 * 4 * math.pi * R ** (3 - s) / (s - 3)
    elif name == 'yukawa':
        kf = lambda r2: np.exp(-par * np.sqrt(r2)) / np.sqrt(r2); R = 40.0 if par < 0.5 else 25.0
        tail = 0.5 * 4 * math.pi * quad(lambda r: r * math.exp(-par * r), R, np.inf)[0]
    else:
        kf = lambda r2: np.exp(-par * r2); R = 12.0 if par > 0.3 else 40.0; tail = 0.0
    Eb = brute(kf, A, S, R) + tail
    row = dict(kernel=name, param=par, N=c['N'], E_found=c['E'], E_alt_engine=E_alt,
               E_reminimised=res, E_brute=Eb,
               rel_alt=abs(E_alt - c['E']) / abs(c['E']), rel_brute=abs(Eb - c['E']) / abs(c['E']),
               rel_reminim=[abs(e - c['E']) / abs(c['E']) for e in res],
               rel_below_base=c['rel_below'], reach=c['n_restarts_reaching'], nrest=c['nrest'])
    out.append(row)
    print(json.dumps(row), flush=True)
json.dump(out, open('B2_verification.json', 'w'), indent=1)
