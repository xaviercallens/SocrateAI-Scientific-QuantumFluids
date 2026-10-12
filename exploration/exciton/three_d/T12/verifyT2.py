"""Independent re-check of T2 (and T1) candidates: different cutoff (xcg = 70 instead of 45) and swapped real/reciprocal
splitting for each Gaussian component, brute-force direct sum, re-minimisation from perturbed coordinates with the
alternative engine, and a coexistence-approximant test (local Voronoi-volume bimodality; CKS 2009 report D3/D3*
coexistence at alpha = pi, communicated by the parent).  Usage: python3 verifyT2.py [candidates.json] [out.json]"""
import os, sys, json, math
os.environ.setdefault('OMP_NUM_THREADS', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'AB'))
import numpy as np
from scipy.spatial import Voronoi, ConvexHull
from lattsum import MixKernel, Kernel
from opt import minimize_structure, energy
from selfdual import normalise


def brute(kfun, A0, S, R=12.0):
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


def voronoi_volumes(A0, S):
    """Voronoi cell volumes of the N points in the periodic cell (3x3x3 images)."""
    A, S = normalise(A0, S)
    N = len(S)
    sh = np.array(np.meshgrid(*[np.arange(-1, 2)] * 3, indexing='ij')).reshape(3, -1).T
    pts = np.concatenate([(S + s) @ A for s in sh])          # central cell is the s = 0 block
    i0 = int(np.where((sh == 0).all(1))[0][0]) * N
    vor = Voronoi(pts)
    vols = []
    for i in range(i0, i0 + N):
        reg = vor.regions[vor.point_region[i]]
        if -1 in reg or len(reg) == 0:
            vols.append(float('nan'))
        else:
            vols.append(ConvexHull(vor.vertices[reg]).volume)
    return np.array(vols)


def coexistence_test(A0, S):
    v = voronoi_volumes(A0, S)
    v = v[np.isfinite(v)]
    if len(v) < 2:
        return dict(n=len(v), bimodal=False)
    vs = np.sort(v)
    gaps = np.diff(vs)
    k = int(np.argmax(gaps))
    lo, hi = vs[:k + 1], vs[k + 1:]
    spread = (hi.mean() - lo.mean()) / v.mean()
    within = max(lo.std(), hi.std()) / v.mean()
    return dict(n=len(v), vol_min=float(vs[0]), vol_max=float(vs[-1]), vol_mean=float(v.mean()),
                largest_gap_rel=float(gaps[k] / v.mean()), group_sizes=[len(lo), len(hi)],
                between_rel=float(spread), within_rel=float(within),
                bimodal=bool(spread > 5e-4 and spread > 5 * within and len(lo) >= 2 and len(hi) >= 2))


def main(cfile, ofile):
    cands = json.load(open(cfile))
    best = {}
    for c in cands:
        k = (c.get('idx', 'T1'), c['N'])
        if k not in best or c['E'] < best[k]['E']:
            best[k] = c
    rng = np.random.default_rng(5)
    out = []
    for k, c in sorted(best.items(), key=str):
        A = np.array(c['A']); S = np.array(c['S'])
        if 'a1' in c:
            k_alt = MixKernel(c['a1'], c['a2'], c['lam'], xcg=70.0, force=('real', 'recip' if c['N'] <= 4 else None))
            kf = lambda r2, c=c: np.exp(-c['a1'] * r2) + c['lam'] * np.exp(-c['a2'] * r2)
        else:
            k_alt = Kernel('gauss', math.pi, xcg=70.0)
            k_alt.use_real, k_alt.use_recip, k_alt.rc2, k_alt.gc2 = False, True, 1.0, 4.0 * math.pi * 70.0
            kf = lambda r2: np.exp(-math.pi * r2)
        E_alt = energy(k_alt, A, S)
        res = []
        for t in range(3):
            Sp = S + 1e-3 * rng.normal(size=S.shape)
            Ap = A * (1 + 1e-3 * rng.normal(size=(3, 3)))
            E, A2, S2, _ = minimize_structure(k_alt, Ap, Sp, gtol=1e-11)
            res.append(E)
        Eb = brute(kf, A, S)
        row = dict(key=str(k), N=c['N'], E_found=c['E'], E_alt_engine=E_alt, E_reminimised=res, E_brute=Eb,
                   rel_alt=abs(E_alt - c['E']) / abs(c['E']), rel_brute=abs(Eb - c['E']) / abs(c['E']),
                   rel_reminim_vs_found=[(e - c['E']) / abs(c['E']) for e in res],
                   rel_below_ref=c.get('rel_below'), best_ref=c.get('best_ref'),
                   still_below_after_reminimisation=bool(c.get('E_best_ref') is not None and
                                                         (min(res) - c['E_best_ref']) / abs(c['E_best_ref']) < -1e-8),
                   coexistence=coexistence_test(A, S))
        out.append(row)
        print(json.dumps(row), flush=True)
    json.dump(out, open(ofile, 'w'), indent=1)


if __name__ == '__main__':
    cfile = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'T2_candidates.json')
    ofile = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'T2_verification.json')
    main(cfile, ofile)
