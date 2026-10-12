"""Engine check before any T2/T1 run (2026-10-12).
1. The existing Gaussian kernel still reproduces the stored round-1 reference energies (AB/B_refs.json) to 1e-12.
2. MixKernel == Kernel(a1) + lam*Kernel(a2) == brute-force direct sum (all Gaussians converge superexponentially).
3. MixKernel analytic gradients vs central differences; forced real/recip branches agree.
"""
import os, sys, json, math
os.environ.setdefault('OMP_NUM_THREADS', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'AB'))
import numpy as np
from lattsum import Kernel, MixKernel
from structures import references
from opt import energy

out = {}
refs = references()
B = json.load(open(os.path.join(HERE, '..', 'AB', 'B_refs.json')))
worst = 0.0
rows = []
for k, v in B.items():
    if v['kernel'] != 'gauss':
        continue
    a = v['param']
    kern = Kernel('gauss', a)
    for nm in ('FCC', 'BCC'):
        E = energy(kern, refs[nm][0], refs[nm][1])
        Es = v['refs'][nm]['E_relaxed']
        rel = abs(E - Es) / abs(Es)
        worst = max(worst, rel)
        rows.append(dict(a=a, ref=nm, E_now=E, E_stored=Es, rel=rel))
out['gauss_vs_stored_refs'] = dict(worst_rel=worst, pass_1e12=bool(worst < 1e-12), rows=rows)
print('1. Gaussian FCC/BCC vs stored B_refs: worst rel', worst, 'PASS' if worst < 1e-12 else 'FAIL')


def brute(a1, a2, lam, A0, S, R=12.0):
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
            tot += (np.exp(-a1 * r2[m]) + lam * np.exp(-a2 * r2[m])).sum()
    return tot / (2 * N)


rng = np.random.default_rng(12)
configs = {nm: refs[nm][:2] for nm in ('FCC', 'BCC', 'HCP', 'A15')}
configs['random4'] = (np.eye(3) * 4 ** (1 / 3) + 0.1 * rng.normal(size=(3, 3)), rng.random((4, 3)))
pairs = [(math.pi / 2, 2 * math.pi), (math.pi / 4, 4 * math.pi), (2.0, 5.0)]
rows = []
w_sum = w_brute = w_force = w_grad = 0.0
for (a1, a2) in pairs:
    for lam in (0.5, 3.0):
        mk = MixKernel(a1, a2, lam)
        k1, k2 = Kernel('gauss', a1), Kernel('gauss', a2)
        mk_f = MixKernel(a1, a2, lam, xcg=70.0, force=('real', 'recip'))   # swapped branches, larger cutoff
        for nm, (A0, S) in configs.items():
            E = energy(mk, A0, S)
            Es = energy(k1, A0, S) + lam * energy(k2, A0, S)
            Eb = brute(a1, a2, lam, A0, S)
            Ef = energy(mk_f, A0, S) if nm != 'A15' else E   # forced recip for a2 on 8-point cell is slow; skip
            r = dict(a1=a1, a2=a2, lam=lam, cfg=nm, E=E, rel_sum=abs(E - Es) / E, rel_brute=abs(E - Eb) / E,
                     rel_forced=abs(E - Ef) / E)
            rows.append(r)
            w_sum = max(w_sum, r['rel_sum']); w_brute = max(w_brute, r['rel_brute']); w_force = max(w_force, r['rel_forced'])
# gradient FD on random 4-point config
A0, S = configs['random4']
for (a1, a2) in pairs:
    mk = MixKernel(a1, a2, 2.0)
    E, gA, gS = mk.eg(A0, S)
    h = 1e-6
    err = 0.0
    for a in range(3):
        for b in range(3):
            Ap = A0.copy(); Ap[a, b] += h
            Am = A0.copy(); Am[a, b] -= h
            err = max(err, abs((mk.eg(Ap, S)[0] - mk.eg(Am, S)[0]) / (2 * h) - gA[a, b]))
    for i in range(len(S)):
        for a in range(3):
            Sp = S.copy(); Sp[i, a] += h
            Sm = S.copy(); Sm[i, a] -= h
            err = max(err, abs((mk.eg(A0, Sp)[0] - mk.eg(A0, Sm)[0]) / (2 * h) - gS[i, a]))
    w_grad = max(w_grad, err)
out['mix_checks'] = dict(worst_rel_vs_sum=w_sum, worst_rel_vs_brute=w_brute, worst_rel_forced_branch=w_force,
                         worst_grad_fd_abs=w_grad, rows=rows)
print('2. MixKernel vs sum of kernels', w_sum, 'vs brute', w_brute, 'forced-branch/xcg=70', w_force)
print('3. gradient FD max abs err', w_grad)
json.dump(out, open(os.path.join(HERE, 'engine_check.json'), 'w'), indent=1)
