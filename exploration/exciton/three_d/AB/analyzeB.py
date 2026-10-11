"""Analyse Experiment B records: gates B1, B2."""
import json, sys
import numpy as np
from structures import representable

fn = sys.argv[1] if len(sys.argv) > 1 else 'B_records.jsonl'
refs = json.load(open('B_refs.json'))
data = {}
for l in open(fn):
    d = json.loads(l)
    data.setdefault((d['idx'], d['N']), []).append(d)

BASE = ('FCC', 'BCC', 'HCP', 'A15')
rows = []
cands = []
for (idx, N), recs in sorted(data.items()):
    rk = refs[str(idx)]
    R = {k: v['E_relaxed'] for k, v in rk['refs'].items()}
    repr_names = [k for k in R if representable(k, N)]
    best_name = min(repr_names, key=lambda k: R[k])
    Eref = R[best_name]
    E = np.array([r['E'] for r in recs])
    E = np.where(np.isfinite(E), E, np.inf)
    hit = np.abs(E - Eref) <= 1e-8 * abs(Eref)
    hit6 = np.abs(E - Eref) <= 1e-6 * abs(Eref)
    Eglob = min(R[k] for k in BASE)
    below = (Eglob - E.min()) / abs(Eglob)
    # degenerate (within 1e-8) best set among references
    tie = [k for k in repr_names if abs(R[k] - Eref) <= 1e-8 * abs(Eref)]
    row = dict(kernel=rk['kernel'], param=rk['param'], idx=idx, N=N, nrest=len(recs),
               best_ref=best_name, ties=tie, E_ref=Eref, E_min=float(E.min()),
               frac_hit=float(hit.mean()), frac_hit_1em6=float(hit6.mean()),
               rel_below_FCCBCCHCPA15=float(below),
               n_distinct=len(set(np.round(E / abs(Eref) - 1, 8))))
    rows.append(row)
    if below > 1e-8:
        i = int(np.argmin(E))
        Ec = E[i]
        n_reach = int((np.abs(E - Ec) <= 1e-8 * abs(Ec)).sum())
        cands.append(dict(kernel=rk['kernel'], param=rk['param'], idx=idx, N=N, E=float(Ec),
                          rel_below=float(below), n_restarts_reaching=n_reach, nrest=len(recs),
                          A=recs[i]['A'], S=recs[i]['S'], refs=R))

json.dump(dict(rows=rows), open('B_summary.json', 'w'), indent=1)
json.dump(cands, open('B2_candidates.json', 'w'), indent=1)

def gated(r):
    return set(r['ties']) & {'FCC', 'BCC', 'HCP'} and r['best_ref'] in ('FCC', 'BCC', 'HCP') or r['best_ref'] in ('FCC', 'BCC', 'HCP')

print('| kernel | param | N | best ref | ref E | % hit(1e-8) | % hit(1e-6) | distinct E | below base |')
print('|---|---|---|---|---|---|---|---|---|')
for r in rows:
    p = f"s={int(2*r['param'])}" if r['kernel'] == 'riesz' else f"{r['param']:.4g}"
    print(f"| {r['kernel']} | {p} | {r['N']} | {r['best_ref']} | {r['E_ref']:.10g} | {100*r['frac_hit']:.0f} | {100*r['frac_hit_1em6']:.0f} | {r['n_distinct']} | {r['rel_below_FCCBCCHCPA15']:.1e} |")

print()
for lab, Ns, thr in (('B1 (N<=4, >=50%)', (2, 4), 0.5), ('B1 (N=16, >=10%)', (16,), 0.10)):
    sel = [r for r in rows if r['N'] in Ns and r['best_ref'] in ('FCC', 'BCC', 'HCP')]
    ok = [r for r in sel if r['frac_hit'] >= thr]
    print(f"{lab}: {len(ok)}/{len(sel)} gated points pass -> {'PASS' if len(ok)==len(sel) else 'FAIL'}")
    for r in sel:
        if r['frac_hit'] < thr:
            print('   fail:', r['kernel'], r['param'], 'N', r['N'], 'best', r['best_ref'], 'frac', r['frac_hit'])
for N in (2, 4, 8, 12, 16):
    sel = [r for r in rows if r['N'] == N]
    print(f"N={N}: points={len(sel)}, best ref counts:",
          {k: sum(r['best_ref'] == k for r in sel) for k in set(r['best_ref'] for r in sel)},
          f"median frac_hit={np.median([r['frac_hit'] for r in sel]):.2f}, min={min(r['frac_hit'] for r in sel):.2f}")
print('\nB2 candidates (below min(FCC,BCC,HCP,A15) by >1e-8):', len(cands))
for c in cands:
    print(' ', c['kernel'], c['param'], 'N', c['N'], 'rel_below %.3e' % c['rel_below'], 'reach', c['n_restarts_reaching'], '/', c['nrest'])
