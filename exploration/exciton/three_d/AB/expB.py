"""Experiment B: non-Bravais periodic cells, N points per cell, random restarts + L-BFGS on positions + cell."""
import json, sys, time, os
import numpy as np
from multiprocessing import Pool
from lattsum import Kernel, grid_kernels
from structures import references, representable
from opt import minimize_structure, energy

NS = (2, 4, 8, 12, 16)
NREST = {2: 100, 4: 100, 8: 60, 12: 40, 16: 40}   # reduced for N>=8 for time (disclosed in RESULTS.md)
OUT = os.environ.get('BOUT', 'B_records.jsonl')
REFOUT = 'B_refs.json'
DMIN = 0.55


def random_start(N, rng):
    # near-cubic random cell of volume N; random-sequential-addition positions with min physical distance DMIN
    while True:
        M = np.eye(3) + 0.2 * rng.normal(size=(3, 3))
        if np.linalg.det(M) > 0.3:
            break
    A = M * (N / np.linalg.det(M)) ** (1 / 3)
    nn = np.array(np.meshgrid(*[np.arange(-1, 2)] * 3, indexing='ij')).reshape(3, -1).T
    dmin = DMIN
    S = []
    tries = 0
    while len(S) < N:
        s = rng.random(3)
        ok = True
        for t in S:
            d = (s - t + nn) @ A
            if ((d * d).sum(1)).min() < dmin * dmin:
                ok = False
                break
        if ok:
            S.append(s)
        tries += 1
        if tries > 2000:
            dmin *= 0.9
            tries = 0
    return A, np.array(S)


def ref_task(args):
    idx, name, par = args
    kern = Kernel(name, par)
    refs = references()
    out = {}
    for nm, (A, S, n) in refs.items():
        E0 = energy(kern, A, S)
        E, A1, S1, _ = minimize_structure(kern, A, S)
        out[nm] = dict(E_ideal=E0, E_relaxed=min(E, E0))
    return idx, name, par, out


def point_task(args):
    idx, name, par, N, nrest = args
    kern = Kernel(name, par)
    rng = np.random.default_rng(777 + 1000 * idx + N)
    recs = []
    t0 = time.time()
    for r in range(nrest):
        A0, S0 = random_start(N, rng)
        E, A, S, nfev = minimize_structure(kern, A0, S0)
        recs.append(dict(exp='B', kernel=name, param=par, idx=idx, N=N, start=r, E=E, nfev=nfev,
                         A=np.round(A, 9).tolist(), S=np.round(S, 7).tolist()))
    return args, recs, time.time() - t0


def main():
    kerns = grid_kernels()
    pts = [(i, k.name, k.param) for i, k in enumerate(kerns)]
    with Pool(2) as pool:
        if not os.path.exists(REFOUT):
            res = {}
            for idx, name, par, out in pool.imap_unordered(ref_task, pts):
                res[str(idx)] = dict(kernel=name, param=par, refs=out)
                print('ref', name, par, {k: v['E_relaxed'] for k, v in out.items()}, flush=True)
            json.dump(res, open(REFOUT, 'w'), indent=1)
        tasks = [(i, n, p, N, NREST[N]) for (i, n, p) in pts for N in NS]
        # longest first
        tasks.sort(key=lambda t: -t[3])
        with open(OUT, 'w') as f:
            for args, recs, dt in pool.imap_unordered(point_task, tasks):
                for r in recs:
                    f.write(json.dumps(r) + '\n')
                f.flush()
                Es = np.array([r['E'] for r in recs])
                print(f'done {args[1]} {args[2]:.4g} N={args[3]} Emin={Es.min():.12g} {dt:.0f}s', flush=True)


if __name__ == '__main__':
    main()
