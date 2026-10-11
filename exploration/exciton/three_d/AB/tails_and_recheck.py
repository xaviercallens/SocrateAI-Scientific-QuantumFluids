import json, math, numpy as np
from scipy.integrate import quad
from lattsum import Kernel, grid_kernels, real_kernel, recip_kernel
from structures import references
from opt import energy
R = references()
rows = []
for k in grid_kernels():
    E = energy(k, *R['FCC'][:2])
    tr = tg = 0.0
    if k.use_real:
        tr = 0.5 * 4 * math.pi * quad(lambda r: real_kernel(k.kind, k.param, k.tau, r * r)[0] * r * r, math.sqrt(k.rc2), math.sqrt(k.rc2) + 40, limit=200)[0]
    if k.use_recip:
        tg = 0.5 * 4 * math.pi / (2 * math.pi) ** 3 * quad(lambda g: recip_kernel(k.kind, k.param, k.tau, g * g)[0] * g * g, math.sqrt(k.gc2), math.sqrt(k.gc2) + 200, limit=200)[0]
    rows.append(dict(kernel=k.label(), mode=('real' if k.use_real else '')+('+recip' if k.use_recip else ''), tau=k.tau,
                     r_cut=math.sqrt(k.rc2), g_cut=math.sqrt(k.gc2), E_FCC=E, tail_real_rel=tr / abs(E), tail_recip_rel=tg / abs(E)))
print('max tail_real_rel', max(r['tail_real_rel'] for r in rows), 'max tail_recip_rel', max(r['tail_recip_rel'] for r in rows))
json.dump(rows, open('cutoff_tails.json', 'w'), indent=1)
# recheck 300 stored restart energies with different tau/cutoffs
rng = np.random.default_rng(3)
recs = [json.loads(l) for l in open('B_records.jsonl')]
sel = rng.choice(len(recs), 300, replace=False)
worst = 0
for i in sel:
    r = recs[i]
    k = Kernel(r['kernel'], r['param'], tau=1.7, xc=75.0, xcg=60.0)
    e = energy(k, np.array(r['A']), np.array(r['S']))
    worst = max(worst, abs(e - r['E']) / abs(r['E']))
print('recheck 300 stored B records with tau=1.7, xc=75: worst rel dev', worst)
