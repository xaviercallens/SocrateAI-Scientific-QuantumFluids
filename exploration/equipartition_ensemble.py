#!/usr/bin/env python3
# TIER C - EXPLORATORY, NO CLAIMS
"""Does time-averaging rescue CLAIM-012 from the single-trajectory problem?

CLAIM-014 established that INSTANTANEOUS trajectory-derived observables (tau)
carry 72-105% fixed-parameter scatter. CLAIM-012 used single trajectories too,
but its observable is a TIME AVERAGE of Omega over the second half of a long
run -- and time-averaging in a mixing system self-averages, so it may be far
more robust. That is a hypothesis, not a fact, and asserting the boundary of
the retraction without testing it would repeat the error being corrected.

Decision rule, fixed before looking: if the fixed-D ensemble CV of the
time-averaged Omega is small (<= ~10%) then CLAIM-012 stands as stated; if it
is comparable to tau's 23-49% then CLAIM-012 needs the same qualification as
CLAIM-013.
"""
import sys
import numpy as np
from quantumfluids.w4_shell_model.shell_dynamics import k_shells, rhs, enstrophy_sum, energy
from quantumfluids.w4_shell_model.integrate import make_profile

N, T, DT, NREAL = 4, 128.0, 6.25e-3, 4

def mean_omega_second_half(D, phases):
    k = k_shells(N)
    a = make_profile("P3", N).astype(complex) * np.exp(1j * phases)
    steps = int(T / DT); oms = []
    for s in range(steps):
        k1 = rhs(a, k, 0.0, D); k2 = rhs(a + 0.5*DT*k1, k, 0.0, D)
        k3 = rhs(a + 0.5*DT*k2, k, 0.0, D); k4 = rhs(a + DT*k3, k, 0.0, D)
        a = a + (DT/6.0)*(k1 + 2*k2 + 2*k3 + k4)
        if s % 40 == 0: oms.append(enstrophy_sum(a, k))
    oms = np.array(oms)
    return oms[len(oms)//2:].mean(), energy(a)

def main():
    E0 = 0.625
    pred = E0 * (4**(N+1) - 1) / (3*(N+1))
    print(f"Equipartition prediction <Omega_sum>_eq = {pred:.3f}  (N={N}, E={E0})")
    print(f"Time-averaged over the second half of T={T}, {NREAL} phase realisations\n")
    print(f"{'D':>7} {'n':>3} {'mean':>9} {'std':>8} {'CV':>7} {'% of pred':>10} {'range':>18}")
    print("-" * 66)
    rng = np.random.default_rng(23)
    for D in (0.0, 0.02):
        vals = []
        for i in range(NREAL):
            ph = 0.7*np.arange(N+1) if i == 0 else rng.uniform(0, 2*np.pi, N+1)
            m, _ = mean_omega_second_half(D, ph)
            vals.append(m)
            print(f"    [D={D} real {i+1}/{NREAL}: <Omega> = {m:.3f}]", flush=True)
        v = np.array(vals)
        print(f"{D:>7} {len(v):>3} {v.mean():>9.3f} {v.std():>8.3f} "
              f"{v.std()/v.mean():>6.1%} {100*v.mean()/pred:>9.1f}% "
              f"{f'{v.min():.1f}-{v.max():.1f}':>18}")
    print()
    print("Rule fixed before looking: CV <= ~10% -> CLAIM-012 stands as stated;")
    print("CV comparable to tau's 23-49% -> CLAIM-012 needs the same qualification.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
