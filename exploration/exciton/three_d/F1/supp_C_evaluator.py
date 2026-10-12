"""Unregistered check (2026-10-12, after the F1 review): the F1b first runs differ from C's records at seeds 11 and 44 (a = 4)
and by 5.5e-12 at seed 16. Re-run C's own minimise() (C's evaluator) at those seeds and compare with C's records.
Output: supp_C_evaluator.log."""
import sys, json
sys.path.insert(0, '../C')
import run_C as R
C = {c['start']: c for c in map(json.loads, open('../C/records.jsonl')) if c['N'] == 120 and c['kernel'] == 'gauss4'}
for s in (11, 44, 16):
    seed = 1000 * 120 + s + 100000 * list(R.KERNELS).index('gauss4')
    out = R.minimise(120, 'gauss4', seed)
    E = out['E'] if isinstance(out, dict) else out[0]
    print(f"seed {s}: C evaluator re-run E={E:.12f}, C record E={C[s]['E']:.12f}, diff={E - C[s]['E']:.1e}", flush=True)
