#!/usr/bin/env python3
# TIER C - EXPLORATORY, NO CLAIMS
"""First beta_D vs beta_nu comparison -- the PRIMARY W4 experiment (memo O6).

THIS IS NOT THE W4 RESULT. It is an exploratory shakedown of the harness on
a small grid, to see whether the measurement is even well-posed before
spending compute on a real run. In particular it does NOT satisfy:

  - the grid-adequacy precondition (OP2_LITE section 3 requires it, and
    MechanicaFluidorum's D6 memo exists because a previous campaign's grid
    had ZERO detection power),
  - Positive Control #2 (a known-bounded regime must read as bounded),
  - any pre-registration of THIS grid.

What it CAN legitimately show: whether beta is measurable at all here,
whether the two enstrophy conventions (audit ruling O1) give different
answers, and whether nu and D are distinguishable at matched diffusivity.

Run:  PYTHONPATH=src python3 exploration/w4_first_comparison.py
"""

import sys

import numpy as np

from quantumfluids.w4_shell_model.exponent import run_sweep
from quantumfluids.w4_shell_model.integrate import integrate

N = 7
PROFILE = "P3"
T = 1.0
# Matched diffusivity values -- identical for both regulators, which is the
# whole point: nu and D share dimensions, so this comparison needs no
# conversion (memo O6).
VALUES = [0.05, 0.035, 0.025, 0.018, 0.012, 0.008]


def n_independence_check():
    """Is the measurement truncation-limited? If sup_Omega still moves with
    N, we are measuring the cutoff, not the regulator."""
    print("N-independence check (is the regulator biting inside the grid?)")
    print(f"{'N':>3} {'nu=0.02 supOm':>16} {'D=0.02 supOm':>16}")
    print("-" * 40)
    prev = None
    for n in [4, 5, 6, 7]:
        rv = integrate(N=n, nu=0.02, D=0.0, profile=PROFILE, t_horizon=T)
        rd = integrate(N=n, nu=0.0, D=0.02, profile=PROFILE, t_horizon=T)
        print(f"{n:>3} {rv.sup_enstrophy_sum:>16.6f} {rd.sup_enstrophy_sum:>16.6f}")
        prev = (rv.sup_enstrophy_sum, rd.sup_enstrophy_sum)
    print(f"\n(if the last rows agree, the grid resolves the regulator scale)\n")
    return prev


def main() -> int:
    n_independence_check()

    results = {}
    for reg in ("viscous", "dispersive"):
        print(f"=== sweep: {reg} (N={N}, profile={PROFILE}, T={T}) ===")
        res = run_sweep(reg, VALUES, N=N, profile=PROFILE, t_horizon=T)
        print(res.exclusion_report())
        print(f"{res.param_name:>8} {'supOm_sum':>14} {'supOm_max':>14} {'dt-refine sum':>14}")
        for p in res.points:
            mark = "" if p.included else "  <-- EXCLUDED"
            chg = p.rel_change_sum if np.isfinite(p.sup_sum_fine) else float("nan")
            print(f"{p.param:>8g} {p.sup_sum:>14.6f} {p.sup_max:>14.6f} {chg:>13.2%}{mark}")
        print()
        for f in (res.fit_sum, res.fit_max):
            print("   ", f if f else "(too few surviving points to fit)")
        print()
        results[reg] = res

    print("=" * 72)
    print("PRIMARY COMPARISON: beta_D vs beta_nu at matched diffusivity")
    print("=" * 72)
    for conv in ("sum", "max"):
        fv = getattr(results["viscous"], f"fit_{conv}")
        fd = getattr(results["dispersive"], f"fit_{conv}")
        if not (fv and fd):
            print(f"[{conv}] cannot compare -- a fit is missing")
            continue
        overlap = not (fv.ci95_high < fd.ci95_low or fd.ci95_high < fv.ci95_low)
        print(f"[{conv}] viscous    {fv}")
        print(f"[{conv}] dispersive {fd}")
        print(f"[{conv}] 95% CIs {'OVERLAP -> not distinguishable' if overlap else 'DISJOINT -> distinguishable'} "
              f"at this grid\n")

    print("Reminder: exploratory. Not a W4 result -- see this file's docstring")
    print("for the pre-registration and control requirements it does not meet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
