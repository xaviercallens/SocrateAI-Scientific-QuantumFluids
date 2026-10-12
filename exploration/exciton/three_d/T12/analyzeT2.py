"""T2 analysis: per (pair, lambda, N) cell -- best reference, hit fractions, candidates below min(FCC,BCC,HCP) by > 1e-8."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np

refs = json.load(open(os.path.join(HERE, 'T2_refs.json')))
recs = [json.loads(l) for l in open(os.path.join(HERE, 'T2_records.jsonl'))]
cells = {}
for r in recs:
    cells.setdefault((r['idx'], r['N']), []).append(r)
rows, cands = [], []
for (idx, N), rs in sorted(cells.items()):
    R = refs[str(idx)]
    Eref = {k: v['E_relaxed'] for k, v in R['refs'].items() if k in ('FCC', 'BCC', 'HCP')}
    gated = {k: v for k, v in Eref.items() if N % (2 if k == 'HCP' else 1) == 0}
    best = min(gated, key=gated.get)
    Eb = gated[best]
    Es = np.array([r['E'] for r in rs])
    hit8 = float(np.mean(np.abs(Es - Eb) <= 1e-8 * abs(Eb)))
    hit6 = float(np.mean(np.abs(Es - Eb) <= 1e-6 * abs(Eb)))
    ndist = len(np.unique(np.round(Es / abs(Eb), 8)))
    rel_min = float((Es.min() - Eb) / abs(Eb))
    rows.append(dict(idx=idx, a1=R['a1'], a2=R['a2'], lam=R['lam'], fac=R['fac'], N=N, nrest=len(rs), best_ref=best,
                     E_best_ref=Eb, E_min=float(Es.min()), rel_min_vs_ref=rel_min, hit_1e8=hit8, hit_1e6=hit6,
                     n_distinct=ndist, E_FCC=Eref['FCC'], E_BCC=Eref['BCC'], E_HCP=Eref['HCP']))
    for r in rs:
        if (r['E'] - Eb) / abs(Eb) < -1e-8:
            c = dict(r)
            c['rel_below'] = (r['E'] - Eb) / abs(Eb)
            c['best_ref'] = best
            c['E_best_ref'] = Eb
            c['n_restarts_reaching'] = int(np.sum(np.abs(Es - r['E']) <= 1e-8 * abs(Eb)))
            c['nrest'] = len(rs)
            cands.append(c)
json.dump(rows, open(os.path.join(HERE, 'T2_summary.json'), 'w'), indent=1)
json.dump(cands, open(os.path.join(HERE, 'T2_candidates.json'), 'w'), indent=1)
with open(os.path.join(HERE, 'T2_analysis.txt'), 'w') as f:
    f.write('idx a1 a2 lam fac N nrest best_ref E_best_ref E_min rel_min hit1e-8 hit1e-6 n_distinct\n')
    for r in rows:
        f.write(f"{r['idx']} {r['a1']:.6g} {r['a2']:.6g} {r['lam']:.9g} {r['fac']} {r['N']} {r['nrest']} {r['best_ref']} "
                f"{r['E_best_ref']:.12g} {r['E_min']:.12g} {r['rel_min_vs_ref']:+.3e} {r['hit_1e8']:.2f} {r['hit_1e6']:.2f} "
                f"{r['n_distinct']}\n")
    f.write(f'\ncells={len(rows)} restarts={len(recs)} candidates(below min(FCC,BCC,HCP) by >1e-8)={len(cands)}\n')
    f.write(f'most negative rel_min over all cells: {min(r["rel_min_vs_ref"] for r in rows):+.3e}\n')
print(open(os.path.join(HERE, 'T2_analysis.txt')).read())
