"""T1 analysis.  Energies: the engine gives E = (1/2N) sum' f (half-sum convention, CKS 2009 normalisation); the registered
reference 0.231536266184 is in the sum_{v != 0} e^{-pi r^2} convention of AB/bain_selfdual.py, i.e. 2E.  Comparison uses 2E.
(The 'rel_vs_ref' field written into T1_records.jsonl during the run compared E with 2E_ref and is off by a factor 2; ignore it.)"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'AB'))
import numpy as np
from selfdual import mismatch, is_lattice, energy_at_pi, shell_lists
from structures import references

E_REF_SUM = 0.231536266184          # registered (sum' convention) = 2 * E_engine(FCC, pi)
E_COEX_HALF = 0.11576766            # CKS 2009 D3/D3* coexistence, half-sum convention (communicated by the parent)
recs = [json.loads(l) for l in open(os.path.join(HERE, 'T1_records.jsonl'))]
refs = references()
known = {'diamond': refs['diamond'][:2], 'SC': (np.eye(3), np.zeros((1, 3)))}
t = 2 ** 0.25; a = (2 / t) ** (1 / 3)
known['bct_isodual'] = (np.array([[a, 0, 0], [0, a, 0], [a / 2, a / 2, t * a / 2]]), np.zeros((1, 3)))
known_sh = {k: shell_lists(*v, K=12) for k, v in known.items()}


def identify(A, S):
    mu, nu = shell_lists(A, S, K=12)
    for k, (kmu, _) in known_sh.items():
        n = min(len(mu), len(kmu))
        if n and max(abs(mu[i][0] - kmu[i][0]) + abs(mu[i][1] - kmu[i][1]) for i in range(n)) < 1e-6:
            return k
    return 'unidentified'


rows = []
by_N = {}
for r in recs:
    by_N.setdefault(r['N'], []).append(r)
out = dict(per_N={}, accepted=[], gate_T1_candidates=[])
for N, rs in sorted(by_N.items()):
    acc = [r for r in rs if r['shell_mismatch'] < 1e-10]
    out['per_N'][N] = dict(starts=len(rs), accepted=len(acc), min_mismatch=min(r['shell_mismatch'] for r in rs),
                           min_surrogate=min(r['M'] for r in rs),
                           n_below_1e6=sum(r['shell_mismatch'] < 1e-6 for r in rs))
    groups = {}
    for r in acc:
        A, S = np.array(r['A']), np.array(r['S'])
        E = energy_at_pi(A, S)
        key = round(2 * E, 9)
        g = groups.setdefault(key, dict(N=N, E_half=E, E_sum=2 * E, rel_vs_registered=(2 * E - E_REF_SUM) / E_REF_SUM,
                                        rel_vs_coexistence_half=(E - E_COEX_HALF) / E_COEX_HALF,
                                        is_lattice=is_lattice(A, S), identity=identify(A, S), count=0,
                                        example_start=r['start'], A=r['A'], S=r['S'],
                                        shells_mu=shell_lists(A, S, K=6)[0], mismatch=r['shell_mismatch']))
        g['count'] += 1
        if (2 * E - E_REF_SUM) / E_REF_SUM < -1e-8 and not g['is_lattice']:
            out['gate_T1_candidates'].append(dict(N=N, start=r['start'], E=E, A=r['A'], S=r['S'],
                                                  rel_below=(2 * E - E_REF_SUM) / E_REF_SUM))
    out['accepted'].extend(groups.values())
json.dump(out, open(os.path.join(HERE, 'T1_summary.json'), 'w'), indent=1, default=float)
with open(os.path.join(HERE, 'T1_analysis.txt'), 'w') as f:
    for N, d in out['per_N'].items():
        f.write(f"N={N}: starts={d['starts']} accepted(mismatch<1e-10)={d['accepted']} below1e-6={d['n_below_1e6']} "
                f"min_mismatch={d['min_mismatch']:.3e} min_surrogate={d['min_surrogate']:.3e}\n")
    f.write('\nDistinct accepted structures (grouped by 2E(pi) to 1e-9):\n')
    f.write('N count identity lattice 2E(pi) rel_vs_0.231536266184 E_half rel_vs_CKS_coex first_shells(r,w)\n')
    for g in sorted(out['accepted'], key=lambda g: (g['N'], g['E_sum'])):
        f.write(f"{g['N']} {g['count']} {g['identity']} {g['is_lattice']} {g['E_sum']:.12f} {g['rel_vs_registered']:+.3e} "
                f"{g['E_half']:.10f} {g['rel_vs_coexistence_half']:+.3e} "
                f"{[(round(r, 5), round(w, 5)) for r, w in g['shells_mu'][:4]]}\n")
    f.write(f"\nGate T1 candidates (non-lattice, 2E(pi) below registered by >1e-8): {len(out['gate_T1_candidates'])}\n")
print(open(os.path.join(HERE, 'T1_analysis.txt')).read())
