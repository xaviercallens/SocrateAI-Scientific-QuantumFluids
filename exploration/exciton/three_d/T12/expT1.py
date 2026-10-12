"""T1 (PREREG_round2.md, 51a85b1): search for formally self-dual periodic configurations at unit density.
Stage 'controls': detector values for diamond (D3+, positive control), FCC<->BCC (dual pair), HCP (negative), plus SC and
the isodual bct (c/a = 2^(1/4)) lattices, before any search result.
Stage 'search': N in {2,4,8}, random starts (expB.random_start), L-BFGS on the smooth Gaussian-family surrogate
(selfdual.SelfDualObjective) with the Experiment B minimiser; acceptance by the registered shell mismatch (< 1e-10 on the
first 40 shells); then Gaussian energy at alpha = pi, lattice test, and comparison with 0.231536266184.
"""
import os, sys, json, time, math
os.environ.setdefault('OMP_NUM_THREADS', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'AB'))
import numpy as np
from multiprocessing import Pool
from structures import references, FCC_A, BCC_A
from opt import minimize_structure
from expB import random_start
from selfdual import mismatch, SelfDualObjective, is_lattice, energy_at_pi, normalise

NSTART = {2: 100, 4: 100, 8: 60}          # run 1 (16 test functions)
if os.environ.get('T1_RUN2'):
    NSTART = {2: 60, 4: 60, 8: 40}        # run 2 (64 test functions, 4x cost per evaluation): reduced for time
OUT = os.path.join(HERE, os.environ.get('T1_OUT', 'T1_records.jsonl'))  # run 3: T1_run3_records.jsonl
E_REF_PI = 0.231536266184


def bct(t):
    a = (2 / t) ** (1 / 3)
    return np.array([[a, 0, 0], [0, a, 0], [a / 2, a / 2, t * a / 2]])   # c = t a; first controls run had t*a (typo)


def controls():
    refs = references()
    P = {nm: refs[nm][:2] for nm in ('FCC', 'BCC', 'HCP', 'diamond')}
    P['SC'] = (np.eye(3), np.zeros((1, 3)))
    P['bct_isodual'] = (bct(2 ** 0.25), np.zeros((1, 3)))
    obj = SelfDualObjective()
    out = []
    tests = [('diamond', 'diamond'), ('FCC', 'BCC'), ('BCC', 'FCC'), ('HCP', 'HCP'), ('FCC', 'FCC'), ('BCC', 'BCC'),
             ('SC', 'SC'), ('bct_isodual', 'bct_isodual')]
    for p, q in tests:
        mm, mu, nu = mismatch(P[p], P[q])
        row = dict(P=p, Q=q, shell_mismatch=mm, first_shells_mu=mu[:4], first_shells_nu=nu[:4])
        if p == q:
            row['surrogate_M'] = obj.eg(*P[p])[0]
            row['E_pi'] = energy_at_pi(*P[p])
            row['is_lattice'] = is_lattice(*P[p])
        out.append(row)
        print(json.dumps(row), flush=True)
    json.dump(out, open(os.path.join(HERE, 'T1_controls.json'), 'w'), indent=1)


CHUNK = 10


def task(args):
    N, chunk = args
    obj = SelfDualObjective()
    rng = np.random.default_rng(999 + 1000 * N + chunk)
    recs = []
    t0 = time.time()
    for s in range(chunk * CHUNK, min((chunk + 1) * CHUNK, NSTART[N])):
        A0, S0 = random_start(N, rng)
        M, A, S, nfev = minimize_structure(obj, A0, S0, gtol=1e-13)
        mm, mu, nu = mismatch((A, S))
        rec = dict(exp='T1', N=N, start=s, M=M, shell_mismatch=mm, nfev=nfev, accepted=bool(mm < 1e-10),
                   A=np.round(A, 10).tolist(), S=np.round(S, 9).tolist())
        if mm < 1e-6:
            rec['E_pi'] = energy_at_pi(A, S)
            rec['is_lattice'] = is_lattice(A, S)
            rec['rel_vs_ref'] = (rec['E_pi'] - E_REF_PI) / E_REF_PI
            rec['shells_mu'] = mu[:6]
            rec['shells_nu'] = nu[:6]
        recs.append(rec)
    return N, recs, time.time() - t0


def search(ns=(2, 4, 8)):
    tasks = [(N, c) for N in ns for c in range(math.ceil(NSTART[N] / CHUNK))]
    tasks.sort(key=lambda t: -t[0])
    with Pool(2) as pool, open(OUT, 'a') as f:
        for N, recs, dt in pool.imap_unordered(task, tasks):
            for r in recs:
                f.write(json.dumps(r) + '\n')
            f.flush()
            acc = [r for r in recs if r['accepted']]
            print(f'done N={N} chunk starts {recs[0]["start"]}-{recs[-1]["start"]} accepted={len(acc)} '
                  f'minM={min(r["M"] for r in recs):.3e} min_mismatch={min(r["shell_mismatch"] for r in recs):.3e} {dt:.0f}s',
                  flush=True)


if __name__ == '__main__':
    stage = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if stage in ('controls', 'all'):
        controls()
    if stage in ('search', 'all'):
        ns = tuple(int(x) for x in sys.argv[2].split(',')) if len(sys.argv) > 2 else (2, 4, 8)
        search(ns)
