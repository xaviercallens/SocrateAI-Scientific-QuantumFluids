#!/usr/bin/env python3
# TIER C - EXPLORATORY, NO CLAIMS
"""Which observable converges in the horizon T, for BOTH regulators?

OPEN ITEM O7 established that sup_t Omega does not converge in T for a
purely dispersive regulator (nu = 0), so the audited memo's exponent
protocol cannot be applied to it. Owner ruling 2026-08-14: change the
observable.

This script picks the replacement ON EVIDENCE rather than intuition --
the failure that produced O7 in the first place was assuming an
observable was well-behaved without checking. Each candidate is evaluated
at a doubling sequence of horizons and judged by whether its value stops
moving, SEPARATELY for the viscous and dispersive regulators. An
observable qualifies only if it converges for BOTH.

Candidates:
  sup       sup_t Omega                     -- the incumbent (expected to fail)
  first_pk  Omega at the first local maximum -- the initial cascade arrival
  fixed_T   Omega(T*) at a pre-registered T* -- trivially defined, arbitrary
  mean      time-averaged Omega             -- expected to decay for viscous
  max_rate  max_t dOmega/dt                 -- early-time cascade growth rate

Run:  PYTHONPATH=src python3 exploration/observable_convergence.py
"""

import sys

import numpy as np

from quantumfluids.w4_shell_model.integrate import integrate

N = 4
PROFILE = "P3"
COEFF = 0.02
HORIZONS = [2, 4, 8, 16, 32, 64]
FIXED_T = 1.0          # for the fixed_T candidate; pre-registered here
TRACE_EVERY = 5
CONVERGED_TOL = 0.02   # 2% between the last two horizons


def first_local_max(t, y):
    """Value at the first interior local maximum, or nan if none."""
    for i in range(1, len(y) - 1):
        if y[i] >= y[i - 1] and y[i] > y[i + 1]:
            return float(y[i])
    return float("nan")


def observables(run) -> dict:
    t, y = run.trace_t, run.trace_omega_sum
    at_fixed = float(np.interp(FIXED_T, t, y)) if t[-1] >= FIXED_T else float("nan")
    rate = np.gradient(y, t)
    return {
        "sup": float(np.max(y)),
        "first_pk": first_local_max(t, y),
        "fixed_T": at_fixed,
        "mean": float(np.trapezoid(y, t) / (t[-1] - t[0])),
        "max_rate": float(np.max(rate)),
    }


def main() -> int:
    names = ["sup", "first_pk", "fixed_T", "mean", "max_rate"]
    results = {}

    for label, nu, D in [("viscous  nu=0.02", COEFF, 0.0),
                         ("dispersive D=0.02", 0.0, COEFF)]:
        print(f"=== {label} (N={N}, profile={PROFILE}) ===")
        print(f"{'T':>5} " + " ".join(f"{n:>12}" for n in names))
        print("-" * (6 + 13 * len(names)))
        rows = {}
        for T in HORIZONS:
            r = integrate(N=N, nu=nu, D=D, profile=PROFILE,
                          t_horizon=float(T), trace_every=TRACE_EVERY)
            obs = observables(r)
            rows[T] = obs
            print(f"{T:>5} " + " ".join(f"{obs[n]:>12.5f}" for n in names))
        results[label] = rows
        print()

    print("=" * 72)
    print(f"CONVERGENCE VERDICT (relative change between T={HORIZONS[-2]} "
          f"and T={HORIZONS[-1]}, tol {CONVERGED_TOL:.0%})")
    print("=" * 72)
    print(f"{'observable':>12} {'viscous':>14} {'dispersive':>14}   verdict")
    print("-" * 62)
    for n in names:
        verdicts = []
        cells = []
        for label in results:
            a = results[label][HORIZONS[-2]][n]
            b = results[label][HORIZONS[-1]][n]
            if not (np.isfinite(a) and np.isfinite(b)) or a == 0:
                cells.append("   n/a")
                verdicts.append(False)
                continue
            rel = abs(b - a) / abs(a)
            cells.append(f"{rel:>13.2%}")
            verdicts.append(rel <= CONVERGED_TOL)
        ok = all(verdicts)
        print(f"{n:>12} {cells[0]} {cells[1]}   "
              f"{'CONVERGES for both' if ok else 'FAILS'}")

    print()
    print("An observable qualifies only if it converges for BOTH regulators.")
    print("Exploratory: one N, one profile, one coefficient value.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
