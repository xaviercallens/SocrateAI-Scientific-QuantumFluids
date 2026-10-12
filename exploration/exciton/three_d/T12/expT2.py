"""T2 (PREREG_round2.md, 51a85b1): Gaussian mixtures f = e^{-a1 r^2} + lam e^{-a2 r^2} across the self-dual point.
Step 1: lam* with E_FCC = E_BCC by bisection to 1e-12 (and the closed-form check, since E is linear in lam).
Step 2: reference energies (FCC, BCC, HCP relaxed, plus diamond/A15 for information) at lam in lam*{0.9,0.97,1,1.03,1.1}.
Step 3: Experiment B search engine, N in {2,4,8,12,16}, restarts 100/100/60/40/40 (as round 1), seeds as expB.
Usage: python3 expT2.py [stage]  stage in {lam, refs, search, all}.
"""
import os, sys, json, time, math
os.environ.setdefault('OMP_NUM_THREADS', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'AB'))
import numpy as np
from multiprocessing import Pool
from lattsum import Kernel, MixKernel
from structures import references
from opt import minimize_structure, energy
from expB import random_start, NS, NREST

PAIRS = [(math.pi / 2, 2 * math.pi), (math.pi / 4, 4 * math.pi), (2.0, 5.0)]
FACS = (0.9, 0.97, 1.0, 1.03, 1.1)
LAMFILE = os.path.join(HERE, 'T2_lambda_star.json')
REFFILE = os.path.join(HERE, 'T2_refs.json')
OUT = os.path.join(HERE, 'T2_records.jsonl')


def ref_E(kern, nm):
    refs = references()
    A, S, _ = refs[nm]
    return energy(kern, A, S)


def lam_star(a1, a2):
    g = lambda lam: ref_E(MixKernel(a1, a2, lam), 'FCC') - ref_E(MixKernel(a1, a2, lam), 'BCC')
    lo, hi = 0.0, 1.0
    while g(lo) * g(hi) > 0:
        hi *= 2
        if hi > 1e6:
            raise RuntimeError('no bracket')
    glo = g(lo)
    it = 0
    while hi - lo > 1e-12:
        mid = 0.5 * (lo + hi)
        gm = g(mid)
        if gm == 0:
            lo = hi = mid
            break
        if gm * glo > 0:
            lo, glo = mid, gm
        else:
            hi = mid
        it += 1
    lam = 0.5 * (lo + hi)
    # closed form: E(lam) linear in lam
    d1 = ref_E(Kernel('gauss', a1), 'FCC') - ref_E(Kernel('gauss', a1), 'BCC')
    d2 = ref_E(Kernel('gauss', a2), 'FCC') - ref_E(Kernel('gauss', a2), 'BCC')
    return dict(a1=a1, a2=a2, lam_star=lam, bracket=[lo, hi], iters=it, residual=g(lam),
                lam_closed_form=-d1 / d2, dual_pair=bool(abs(a1 * a2 - math.pi ** 2) < 1e-12),
                lam_dual_prediction=(math.pi / a1) ** 1.5 if abs(a1 * a2 - math.pi ** 2) < 1e-12 else None)


def stage_lam():
    out = [lam_star(a1, a2) for a1, a2 in PAIRS]
    json.dump(out, open(LAMFILE, 'w'), indent=1)
    for o in out:
        print(json.dumps(o), flush=True)
    return out


def ref_task(args):
    idx, a1, a2, lam = args
    kern = MixKernel(a1, a2, lam)
    refs = references()
    out = {}
    for nm in ('FCC', 'BCC', 'HCP', 'diamond', 'A15'):
        A, S, n = refs[nm]
        E0 = energy(kern, A, S)
        E, A1, S1, _ = minimize_structure(kern, A, S)
        out[nm] = dict(E_ideal=E0, E_relaxed=min(E, E0))
    return idx, out


def points():
    lams = json.load(open(LAMFILE))
    pts = []
    for ip, o in enumerate(lams):
        for jf, f in enumerate(FACS):
            pts.append((ip * 10 + jf, o['a1'], o['a2'], f * o['lam_star'], f))
    return pts


def stage_refs(pool):
    pts = points()
    res = {}
    for idx, out in pool.imap_unordered(ref_task, [p[:4] for p in pts]):
        p = [q for q in pts if q[0] == idx][0]
        res[str(idx)] = dict(a1=p[1], a2=p[2], lam=p[3], fac=p[4], refs=out)
        print('ref', idx, {k: v['E_relaxed'] for k, v in out.items()}, flush=True)
    json.dump(res, open(REFFILE, 'w'), indent=1)


def point_task(args):
    idx, a1, a2, lam, fac, N, nrest = args
    kern = MixKernel(a1, a2, lam)
    rng = np.random.default_rng(777 + 1000 * idx + N)     # same seeding rule as expB.point_task
    recs = []
    t0 = time.time()
    for r in range(nrest):
        A0, S0 = random_start(N, rng)
        E, A, S, nfev = minimize_structure(kern, A0, S0)
        recs.append(dict(exp='T2', a1=a1, a2=a2, lam=lam, fac=fac, idx=idx, N=N, start=r, E=E, nfev=nfev,
                         A=np.round(A, 9).tolist(), S=np.round(S, 7).tolist()))
    return args, recs, time.time() - t0


def stage_search(pool, ns=NS):
    pts = points()
    tasks = [(i, a1, a2, lam, fac, N, NREST[N]) for (i, a1, a2, lam, fac) in pts for N in ns]
    tasks.sort(key=lambda t: -t[5])
    mode = 'a' if os.path.exists(OUT) else 'w'
    done = set()
    if mode == 'a':
        for line in open(OUT):
            r = json.loads(line)
            done.add((r['idx'], r['N']))
        tasks = [t for t in tasks if (t[0], t[5]) not in done]
    with open(OUT, mode) as f:
        for args, recs, dt in pool.imap_unordered(point_task, tasks):
            for r in recs:
                f.write(json.dumps(r) + '\n')
            f.flush()
            Es = np.array([r['E'] for r in recs])
            print(f'done idx={args[0]} a1={args[1]:.4g} a2={args[2]:.4g} lam={args[3]:.6g} (x{args[4]}) N={args[5]} '
                  f'Emin={Es.min():.12g} {dt:.0f}s', flush=True)


if __name__ == '__main__':
    stage = sys.argv[1] if len(sys.argv) > 1 else 'all'
    ns = tuple(int(x) for x in sys.argv[2].split(',')) if len(sys.argv) > 2 else NS
    if stage in ('lam', 'all'):
        stage_lam()
    with Pool(2) as pool:
        if stage in ('refs', 'all'):
            stage_refs(pool)
        if stage in ('search', 'all'):
            stage_search(pool, ns)
