"""Unregistered check (2026-10-12): per-start success of plain L-BFGS (C settings, F1 evaluator) at a = 4, N = 120 on 40 fresh
seeds (rng 777001), to compare with C's 6/50. Output: fresh_plain_a4.log."""
import sys, os, json, numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, '../C')
import run_F1 as F, run_C as R
E6 = R.energy(R.cell600(), 'g', 4.0)
C = [json.loads(l) for l in open('../C/records.jsonl')]
c4 = [c for c in C if c['N'] == 120 and c['kernel'] == 'gauss4']
print('C gauss4 hits', sum(abs(c['E'] - E6) / E6 <= 1e-8 for c in c4), '/', len(c4), 'keys', list(c4[0].keys())[:12])
hits = 0; n = 0
rng = np.random.default_rng(777001)
for k in range(40):
    y0 = rng.normal(size=(120, 4)).ravel(); c = F.Counter(120, 4.0); res = F.lbfgs(c, y0)
    n += 1; hits += abs(res.fun - E6) / E6 <= 1e-8
print('fresh plain a=4 hits', hits, '/', n, flush=True)
