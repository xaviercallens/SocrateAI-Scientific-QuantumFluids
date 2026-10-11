"""Experiment A: Bravais lattices in 3D, 300 random starts per (kernel, parameter)."""
import json, sys, time, os
import numpy as np
from multiprocessing import Pool
from lattsum import Kernel, grid_kernels, reduce_cell
from structures import references
from opt import minimize_structure, energy

NSTART = 300
OUT = 'A_records.jsonl'


def random_cell(rng):
    while True:
        L = np.exp(0.25 * rng.normal(size=3))
        ang = np.deg2rad(rng.uniform(60, 120, size=3))
        G = np.diag(L * L)
        G[0, 1] = G[1, 0] = L[0] * L[1] * np.cos(ang[0])
        G[0, 2] = G[2, 0] = L[0] * L[2] * np.cos(ang[1])
        G[1, 2] = G[2, 1] = L[1] * L[2] * np.cos(ang[2])
        try:
            C = np.linalg.cholesky(G)
        except np.linalg.LinAlgError:
            continue
        A = C
        # random rotation (irrelevant to energy, avoids special alignment of the optimiser)
        Q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
        return A @ Q


def run_point(args):
    idx, name, par = args
    kern = Kernel(name, par)
    refs = references()
    EF = energy(kern, *refs['FCC'][:2])
    EB = energy(kern, *refs['BCC'][:2])
    rng = np.random.default_rng(1000 + idx)
    recs = []
    t0 = time.time()
    for s in range(NSTART):
        A0 = random_cell(rng)
        E, A, S, nfev = minimize_structure(kern, A0, np.zeros((1, 3)))
        recs.append(dict(exp='A', kernel=name, param=par, idx=idx, start=s, E=E, nfev=nfev,
                         A=np.round(A, 10).tolist()))
    return idx, name, par, EF, EB, recs, time.time() - t0


def main():
    kerns = grid_kernels()
    tasks = [(i, k.name, k.param if k.name != 'riesz' else k.param) for i, k in enumerate(kerns)]
    with Pool(2) as pool, open(OUT, 'w') as f:
        for idx, name, par, EF, EB, recs, dt in pool.imap_unordered(run_point, tasks):
            f.write(json.dumps(dict(exp='A', kind='ref', kernel=name, param=par, idx=idx,
                                    E_FCC=EF, E_BCC=EB, secs=dt)) + '\n')
            for r in recs:
                f.write(json.dumps(r) + '\n')
            f.flush()
            print(f'done {name} {par:.4g} FCC={EF:.12g} BCC={EB:.12g} min={min(r["E"] for r in recs):.12g} {dt:.0f}s', flush=True)


if __name__ == '__main__':
    main()
