"""Development only (amendment A1): LP bound vs b at non-gate parameters, d=1 alpha=2 and d=2 alpha=2."""
import sys, math
sys.path.insert(0, '../H1'); import lp_bound as LB
d, alpha = int(sys.argv[1]), float(sys.argv[2])
for b in [0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.3]:
    beta = alpha / math.pi * b
    r = LB.GaussLP(d, alpha, beta, 30).solve(rounds=4, n_fine=50000)
    print(f"d={d} alpha={alpha} b={b} beta={beta:.4f} bound={r['bound']}", flush=True)
