#!/usr/bin/env python3
# TIER C - EXPLORATORY, NO CLAIMS
"""Option C cross-check: sweep D at a small viscous floor (pre-registered in
docs/designs/C_NU_FLOOR_CROSSCHECK.md). Run: PYTHONPATH=src python3 exploration/run_nu_floor.py
"""
import sys
import numpy as np
from scipy import stats
from quantumfluids.w4_shell_model.integrate import integrate, make_profile, step_size

D_VALUES = [0.2, 0.15, 0.1, 0.07, 0.05, 0.035, 0.025, 0.018]
FLOORS = [0.01, 0.02]
N = 5
T = 8.0

def a0():
    a = make_profile("P3", N).astype(complex)
    return a * np.exp(1j * 0.7 * np.arange(N + 1))

def sup(nu, D, dt=None, T_=T):
    r = integrate(N=N, nu=nu, D=D, t_horizon=T_, dt=dt, a0=a0())
    return r.sup_enstrophy_sum, r.sup_enstrophy_max

def fit(xs, ys):
    r = stats.linregress(np.log(xs), np.log(ys))
    return float(r.slope), float(r.rvalue**2)

def main():
    print(f"OPTION C: sup_t Omega with a viscous floor (N={N}, T={T}, common complex data)")
    betas = {}
    for nu in FLOORS:
        print(f"\n--- floor nu={nu} ---")
        # B1 spot-checks at 2T
        for D in (D_VALUES[0], D_VALUES[-1]):
            s1, _ = sup(nu, D); s2, _ = sup(nu, D, T_=2*T)
            rel = abs(s2-s1)/s1
            print(f"  B1 D={D}: sup changes {rel:.3%} at 2T -> {'ok' if rel < 0.01 else 'FAIL'}")
        for which, idx in (("sum", 0), ("max", 1)):
            xs, ys = [], []
            for D in D_VALUES:
                coarse = sup(nu, D)[idx]
                fine = sup(nu, D, dt=step_size(N, nu, D)/2.0)[idx]
                if abs(fine-coarse)/coarse > 0.01:
                    print(f"  [{which}] D={D} excluded: dt-refine {abs(fine-coarse)/coarse:.2%}")
                    continue
                xs.append(D); ys.append(coarse)
            b, r2 = fit(xs, ys)
            betas[(nu, which)] = b
            h = len(xs)//2
            b_hi, _ = fit(xs[:h+1], ys[:h+1]); b_lo, _ = fit(xs[h:], ys[h:])
            print(f"  [{which}] n={len(xs)} beta_D={b:+.4f} r2={r2:.4f} windows[{b_hi:+.3f},{b_lo:+.3f}]")
    print("\nFloor stability (B3' absolute):")
    for which in ("sum", "max"):
        d = abs(betas[(FLOORS[0], which)] - betas[(FLOORS[1], which)])
        print(f"  [{which}] |beta({FLOORS[0]}) - beta({FLOORS[1]})| = {d:.4f} -> "
              f"{'PASS' if d <= 0.05 else 'FAIL (floor-dependence is the result)'}")
    print("\n--- pure viscous comparator (D=0), same values as nu ---")
    for which, idx in (("sum", 0), ("max", 1)):
        xs, ys = [], []
        for nu in D_VALUES:
            xs.append(nu); ys.append(sup(nu, 0.0)[idx])
        b, r2 = fit(xs, ys)
        print(f"  [{which}] beta_nu={b:+.4f} r2={r2:.4f}")
    print("\nExploratory cross-check; interpretation pre-registered in C_NU_FLOOR_CROSSCHECK.md.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
