"""Unregistered check (2026-10-12): C's 6/50 at a = 4, N = 120 is reproduced outcome-for-outcome by the first plain run of F1b,
yet restarts (5790 runs, 33%) and fresh seeds (12/40) succeed more often. Are C-formula seeds special? Plain L-BFGS (C settings,
F1 evaluator) from C's seed formula 1000*N + s + 100000*kernel_index for s = 50..149 (never used by C). Output: cseeds_plain_a4.log."""
import sys, numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, '../C')
import run_F1 as F, run_C as R
E6 = R.energy(R.cell600(), 'g', 4.0)
hits = 0
for s in range(50, 150):
    seed = 1000 * 120 + s + 100000 * list(R.KERNELS).index('gauss4')
    y0 = np.random.default_rng(seed).normal(size=(120, 4)).ravel()
    res = F.lbfgs(F.Counter(120, 4.0), y0); hits += abs(res.fun - E6) / E6 <= 1e-8
print('C-formula seeds s=50..149, plain a=4 hits', hits, '/ 100', flush=True)
