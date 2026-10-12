"""T1 polish: take the search records closest to self-duality (registered shell mismatch < THR, or the best few per N) and
minimise the registered shell-mismatch residuals directly (scipy least_squares, numerical Jacobian) with the cell free.
Writes T1_polish.json. Usage: python3 polishT1.py [records.jsonl] [THR]"""
import os, sys, json, math
os.environ.setdefault('OMP_NUM_THREADS', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'AB'))
import numpy as np
from scipy.optimize import least_squares
from selfdual import shell_lists, mismatch, is_lattice, energy_at_pi, normalise, K_SHELLS
from lattsum import reduce_cell

E_REF_SUM = 0.231536266184


def resid(x, N):
    A = x[:9].reshape(3, 3)
    S = x[9:].reshape(N, 3)
    if abs(np.linalg.det(A)) < 1e-3:
        return np.full(2 * K_SHELLS, 1e3)
    mu, nu = shell_lists(A, S)
    n = min(len(mu), len(nu), K_SHELLS)
    r = np.zeros(2 * K_SHELLS)
    for s in range(n):
        r[2 * s] = mu[s][0] - nu[s][0]
        r[2 * s + 1] = mu[s][1] - nu[s][1]
    return r


def polish(A, S):
    N = len(S)
    A, S = normalise(A, S)
    x0 = np.concatenate([A.ravel(), S.ravel()])
    res = least_squares(resid, x0, args=(N,), method='lm', diff_step=1e-7, xtol=1e-15, ftol=1e-15, gtol=1e-15,
                        max_nfev=4000)
    A1 = res.x[:9].reshape(3, 3)
    S1 = res.x[9:].reshape(N, 3)
    A1, S1 = normalise(A1, S1)
    A1, S1 = reduce_cell(A1, S1)
    S1 = S1 - np.floor(S1)
    return A1, S1, int(res.nfev)


def main(rfile, thr):
    recs = [json.loads(l) for l in open(rfile)]
    by_N = {}
    for r in recs:
        by_N.setdefault(r['N'], []).append(r)
    out = []
    for N, rs in sorted(by_N.items()):
        rs = sorted(rs, key=lambda r: r['shell_mismatch'])
        sel = [r for r in rs if r['shell_mismatch'] < thr] or rs[:3]
        sel = sel[:12]
        for r in sel:
            A, S = np.array(r['A']), np.array(r['S'])
            A1, S1, nfev = polish(A, S)
            mm, mu, nu = mismatch((A1, S1))
            E = energy_at_pi(A1, S1)
            row = dict(N=N, start=r['start'], mismatch_before=r['shell_mismatch'], mismatch_after=mm, nfev=nfev,
                       accepted=bool(mm < 1e-10), E_half=E, E_sum=2 * E, rel_vs_registered=(2 * E - E_REF_SUM) / E_REF_SUM,
                       is_lattice=is_lattice(A1, S1), shells_mu=mu[:6], shells_nu=nu[:6],
                       A=np.round(A1, 10).tolist(), S=np.round(S1, 9).tolist())
            out.append(row)
            print(json.dumps({k: v for k, v in row.items() if k not in ('A', 'S', 'shells_nu')}), flush=True)
    json.dump(out, open(os.path.join(HERE, 'T1_polish.json'), 'w'), indent=1)


if __name__ == '__main__':
    rfile = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'T1_records.jsonl')
    thr = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-2
    main(rfile, thr)
