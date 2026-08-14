#!/usr/bin/env python3
# TIER C - EXPLORATORY, NO CLAIMS
"""Is windowed-sup a better observable than first-peak?

first_peak was adopted to resolve O7 (sup_t Omega diverges in the horizon
for a purely dispersive regulator). It fixes that, but a follow-up sweep
showed it has a DIFFERENT defect: it is discontinuous in the swept
parameter. As D decreases the trace develops additional local maxima
(1, 2, 2, 3 before t=2 at D = 0.05, 0.035, 0.025, 0.018), so "the first
peak" is not the same physical feature at every D -- at D=0.025 the
detector catches a new earlier, smaller peak (t=1.20, 48.2) than at
D=0.035 (t=1.52, 55.0), breaking monotonicity in the sweep.

CANDIDATE: sup over a PRE-REGISTERED FINITE WINDOW, max_{t <= T*} Omega(t).

  - horizon-independent by construction, for any run with T >= T*
    (so it does not inherit O7), and
  - continuous in the swept parameter, since the max of a continuously
    varying family over a fixed compact set is continuous (so it does not
    inherit first_peak's discontinuity).

Its cost is that T* is arbitrary. That is testable rather than fatal: if
beta is stable across a range of T*, the arbitrariness does not affect the
conclusion. This script measures exactly that, plus monotonicity.

Run:  PYTHONPATH=src python3 exploration/windowed_sup_check.py
"""

import sys

import numpy as np
from scipy import stats

from quantumfluids.w4_shell_model.integrate import integrate

N = 5
PROFILE = "P3"
T_RUN = 6.0
VALUES = [0.2, 0.15, 0.1, 0.07, 0.05, 0.035, 0.025, 0.018]
T_STARS = [1.5, 2.0, 3.0, 4.0]


def windowed_sup(run, t_star, which="sum"):
    y = run.trace_omega_sum if which == "sum" else run.trace_omega_max
    return float(np.max(y[run.trace_t <= t_star]))


def main() -> int:
    for label, is_visc in (("viscous", True), ("dispersive", False)):
        runs = {
            v: integrate(N=N, nu=v if is_visc else 0.0, D=0.0 if is_visc else v,
                         profile=PROFILE, t_horizon=T_RUN, trace_every=1)
            for v in VALUES
        }
        print(f"--- {label} (N={N}, T_run={T_RUN}) ---")
        print(f"  {'T*':>5} {'beta[sum]':>11} {'r^2':>8} {'mono':>6}   "
              f"{'beta[max]':>11} {'r^2':>8} {'mono':>6}")
        for ts in T_STARS:
            cells = []
            for which in ("sum", "max"):
                ys = [windowed_sup(runs[v], ts, which) for v in VALUES]
                mono = all(ys[i] <= ys[i + 1] for i in range(len(ys) - 1))
                r = stats.linregress(np.log(VALUES), np.log(ys))
                cells.append((r.slope, r.rvalue ** 2, mono))
            print(f"  {ts:>5} {cells[0][0]:>+11.4f} {cells[0][1]:>8.4f} "
                  f"{str(cells[0][2]):>6}   {cells[1][0]:>+11.4f} "
                  f"{cells[1][1]:>8.4f} {str(cells[1][2]):>6}")
        print()

    print("An observable qualifies only if beta is STABLE across T* and the")
    print("response is MONOTONIC in the swept parameter. Exploratory: one N,")
    print("one profile.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
