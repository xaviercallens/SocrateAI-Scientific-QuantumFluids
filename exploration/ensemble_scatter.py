#!/usr/bin/env python3
# TIER C - EXPLORATORY, NO CLAIMS
"""Is the round-4 'acceleration at small D' physics, or trajectory scatter?

The model is CHAOTIC and every tau measured so far came from a SINGLE
trajectory. Nearby parameter values give exponentially diverging orbits, so
tau(D) is not a smooth function of D for one trajectory -- it carries
intrinsic scatter that no amount of dt-refinement removes (dt-refinement
tests the integrator, not the ensemble).

This measures that scatter directly: fix D, vary only the initial PHASES
(identical |a_n|, identical energy, identical everything the physics cares
about), and see how much tau moves.

Decision rule, fixed before looking: if the fixed-D spread is comparable to
or larger than the round-4 |Delta-tau| signal (0.02-0.35, i.e. 2-20% of
tau_0), then that signal is noise and every single-trajectory exponent in
rounds 3-4 is noise-dominated.
"""
import sys
import numpy as np
from quantumfluids.w4_shell_model.integrate import integrate, make_profile
from quantumfluids.w4_shell_model.observable import crossing_time

N, F, T, NREAL = 4, 0.125, 24.0, 6

def tau_for(D, phases):
    a = make_profile("P3", N).astype(complex) * np.exp(1j * phases)
    r = integrate(N=N, nu=0.0, D=D, t_horizon=T, trace_every=1, a0=a)
    ceil = (2.0**N) ** 2 * r.energy_initial
    try:
        return crossing_time(r.trace_t, r.trace_omega_sum, F * ceil).time
    except ValueError:
        return float("nan")

def main():
    rng = np.random.default_rng(11)
    print(f"ENSEMBLE SCATTER of tau at FIXED D  (N={N}, f={F}, T={T}, "
          f"{NREAL} phase realisations, identical |a_n| and E)")
    print(f"{'D':>7} {'n':>3} {'mean':>8} {'std':>8} {'min':>8} {'max':>8} {'spread/mean':>12}")
    print("-" * 60)
    for D in (0.0, 0.018, 0.05, 0.1):
        ts = []
        for i in range(NREAL):
            ph = 0.7 * np.arange(N + 1) if i == 0 else rng.uniform(0, 2 * np.pi, N + 1)
            t = tau_for(D, ph)
            if np.isfinite(t):
                ts.append(t)
            print(f"    [D={D} real {i+1}/{NREAL}: tau={t:.4f}]", flush=True)
        ts = np.array(ts)
        if len(ts) >= 2:
            print(f"{D:>7} {len(ts):>3} {ts.mean():>8.3f} {ts.std():>8.3f} "
                  f"{ts.min():>8.3f} {ts.max():>8.3f} {(ts.max()-ts.min())/ts.mean():>11.1%}")
    print()
    print("Round-4 'acceleration' signal was |Delta-tau| ~ 0.02-0.35 (2-20% of tau_0).")
    print("If the spread above is comparable or larger, that signal is trajectory")
    print("noise -- and single-trajectory exponents in rounds 3-4 are noise-dominated.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
