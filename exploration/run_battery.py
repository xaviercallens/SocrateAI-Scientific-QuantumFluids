#!/usr/bin/env python3
# TIER C - EXPLORATORY, NO CLAIMS
"""Apply the pre-registered validation battery to TIMESCALE observables.

docs/designs/M2_OBSERVABLE_VALIDATION_BATTERY.md (owner ruling 2026-08-14)
requires an observable to clear B1-B6 on BOTH regulators before any beta
comparison is run on it. Five AMPLITUDE observables -- all of the form "how
large does Omega become" -- have failed, every one of them on the dispersive
side, with a now-identified common cause: a purely dispersive regulator is
energy-neutral, so it has no attractor and Omega keeps exploring upward.

This script tests a class that structurally sidesteps that: TIMESCALES.
"When does something happen" is bounded for both regulators regardless of
whether the amplitude converges.

Candidates:
  t_peak       time of the first local maximum of Omega
  t_cross(th)  first time Omega(t) >= th * Omega(0)

t_cross is the more promising of the two a priori: unlike t_peak it does not
depend on the peak STRUCTURE at all, so the extra local maxima that appear as
D falls -- which is what broke first_peak's monotonicity -- cannot move it.
Its free parameter th is exactly what B3 exists to test.

Run:  PYTHONPATH=src python3 exploration/run_battery.py
"""

import sys

import numpy as np
from scipy import stats

from quantumfluids.w4_shell_model.integrate import integrate

PROFILE = "P3"
VALUES = [0.2, 0.15, 0.1, 0.07, 0.05, 0.035]
BASE_N = 5
BASE_T = 6.0

B1_TOL = 0.01     # horizon independence
B3_TOL = 0.05     # stability in the observable's own free parameter
B4_TOL = 0.01     # discretisation
B5_TOL = 0.01     # grid independence


# --------------------------------------------------------------------------
# Observables: (run, convention) -> float, or nan if undefined for this run
# --------------------------------------------------------------------------

def _trace(run, which):
    return run.trace_omega_sum if which == "sum" else run.trace_omega_max


def obs_t_peak(run, which="sum"):
    y, t = _trace(run, which), run.trace_t
    for i in range(1, len(y) - 1):
        if y[i] >= y[i - 1] and y[i] > y[i + 1]:
            return float(t[i])
    return float("nan")


def make_obs_t_cross(threshold):
    def obs(run, which="sum"):
        y, t = _trace(run, which), run.trace_t
        target = threshold * y[0]
        idx = np.flatnonzero(y >= target)
        return float(t[idx[0]]) if len(idx) else float("nan")
    obs.__name__ = f"t_cross({threshold})"
    return obs


# --------------------------------------------------------------------------

def sweep(obs, is_visc, N, T, which, dt=None, trace_every=1):
    out = []
    for v in VALUES:
        r = integrate(N=N, nu=v if is_visc else 0.0, D=0.0 if is_visc else v,
                      profile=PROFILE, t_horizon=T, dt=dt, trace_every=trace_every)
        out.append(obs(r, which))
    return np.array(out)


def beta_of(ys):
    if not np.all(np.isfinite(ys)) or np.any(ys <= 0):
        return float("nan"), float("nan")
    r = stats.linregress(np.log(VALUES), np.log(ys))
    return float(r.slope), float(r.rvalue ** 2)


def rel(a, b):
    if not (np.isfinite(a) and np.isfinite(b)) or a == 0:
        return float("nan")
    return abs(b - a) / abs(a)


def evaluate(obs, label, free_param_variants=None):
    print(f"\n{'=' * 74}\nCANDIDATE: {label}\n{'=' * 74}")
    verdicts = {}

    for reg_label, is_visc in (("viscous", True), ("dispersive", False)):
        print(f"\n  --- {reg_label} ---")
        for which in ("sum", "max"):
            base = sweep(obs, is_visc, BASE_N, BASE_T, which)
            b0, r2 = beta_of(base)
            if not np.isfinite(b0):
                print(f"    [{which}] UNDEFINED for some parameter values -> DISQUALIFIED")
                verdicts[(reg_label, which)] = False
                continue

            # B1 horizon: 4x range
            long_ = sweep(obs, is_visc, BASE_N, BASE_T * 4, which)
            b1 = max(rel(a, b) for a, b in zip(base, long_))

            # B2 monotonic (timescales should DEcrease as the regulator weakens,
            # or increase -- either is fine, but it must not turn around)
            inc = all(base[i] <= base[i + 1] for i in range(len(base) - 1))
            dec = all(base[i] >= base[i + 1] for i in range(len(base) - 1))
            b2 = inc or dec

            # B4 discretisation: dt/2, and 2x-coarser sampling
            fine_dt = sweep(obs, is_visc, BASE_N, BASE_T, which,
                            dt=integrate(N=BASE_N, nu=0.1 if is_visc else 0.0,
                                         D=0.0 if is_visc else 0.1,
                                         profile=PROFILE, t_horizon=0.01).dt / 2)
            b4a = max(rel(a, b) for a, b in zip(base, fine_dt))
            coarse = sweep(obs, is_visc, BASE_N, BASE_T, which, trace_every=2)
            b4b = max(rel(a, b) for a, b in zip(base, coarse))

            # B5 grid: N and N+1
            bigN = sweep(obs, is_visc, BASE_N + 1, BASE_T, which)
            b5 = max(rel(a, b) for a, b in zip(base, bigN))

            # B6 non-degeneracy: response must actually vary
            b6 = (np.max(base) - np.min(base)) / np.min(base) > 0.05

            ok = (b1 <= B1_TOL and b2 and b4a <= B4_TOL and b4b <= B4_TOL
                  and b5 <= B5_TOL and b6)
            verdicts[(reg_label, which)] = ok
            print(f"    [{which}] beta={b0:+.4f} r2={r2:.4f} | "
                  f"B1={b1:.2%} B2={'ok' if b2 else 'FAIL'} "
                  f"B4dt={b4a:.2%} B4samp={b4b:.2%} B5={b5:.2%} "
                  f"B6={'ok' if b6 else 'FAIL'} -> {'PASS' if ok else 'FAIL'}")

    # B3: stability in the observable's own free parameter
    if free_param_variants:
        print(f"\n  --- B3 (own free parameter) ---")
        for reg_label, is_visc in (("viscous", True), ("dispersive", False)):
            betas = []
            for vlabel, vobs in free_param_variants:
                b, _ = beta_of(sweep(vobs, is_visc, BASE_N, BASE_T, "sum"))
                betas.append((vlabel, b))
            finite = [b for _, b in betas if np.isfinite(b)]
            drift = (max(finite) - min(finite)) / abs(np.mean(finite)) if len(finite) > 1 else float("nan")
            detail = "  ".join(f"{l}:{b:+.4f}" for l, b in betas)
            ok3 = np.isfinite(drift) and drift <= B3_TOL
            print(f"    {reg_label:>10}  {detail}   drift={drift:.2%} -> "
                  f"{'PASS' if ok3 else 'FAIL'}")
            verdicts[(reg_label, "B3")] = ok3

    overall = all(verdicts.values())
    print(f"\n  OVERALL: {'PASSES THE BATTERY' if overall else 'FAILS'}")
    return overall


def main() -> int:
    evaluate(obs_t_peak, "t_peak  (time of first local maximum)")

    variants = [(f"th={t}", make_obs_t_cross(t)) for t in (2.0, 4.0, 8.0)]
    evaluate(make_obs_t_cross(4.0), "t_cross(4)  (first time Omega >= 4*Omega(0))",
             free_param_variants=variants)

    print("\nExploratory: one profile, N=5/6, limited sweep. A PASS here licenses"
          "\nrunning the comparison, not filing a claim.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
