#!/usr/bin/env python3
# TIER C - EXPLORATORY, NO CLAIMS
"""Battery round 3: thermalization time tau_f, all-conservative family.

Pre-registered in docs/designs/M2_OBSERVABLE_VALIDATION_BATTERY.md ("Round 3
pre-registration"). Observable: tau_f = crossing time of Omega to f*k_N^2*E.
Arms: pure truncation baseline (D=0) and dispersive sweep, nu=0 throughout,
COMMON complexified initial data. Fits: windowed-slope stability, no t-CIs.

Run:  PYTHONPATH=src python3 exploration/run_battery_round3.py
"""
import sys
import numpy as np
from scipy import stats
from quantumfluids.w4_shell_model.integrate import integrate, make_profile, step_size
from quantumfluids.w4_shell_model.observable import crossing_time

D_VALUES = [0.2, 0.15, 0.1, 0.07, 0.05, 0.035, 0.025, 0.018]
FRACTIONS = [0.125, 0.25, 0.5]
T_MAX = 64.0

def a0_for(N):
    a = make_profile("P3", N).astype(complex)
    return a * np.exp(1j * 0.7 * np.arange(N + 1))

_RUN_CACHE = {}

def get_run(N, D, fine=False, T=T_MAX):
    """ONE integration per (N, D, dt-level); every f and convention reads the
    same trace. (v1 re-integrated per (f, which) -- a 12x waste that timed the
    whole job out.)"""
    key = (N, D, fine, T)
    if key not in _RUN_CACHE:
        dt = step_size(N, 0.0, D) / (2.0 if fine else 1.0)
        _RUN_CACHE[key] = integrate(N=N, nu=0.0, D=D, t_horizon=T, dt=dt,
                                    trace_every=1, a0=a0_for(N))
        print(f"    [integrated N={N} D={D} fine={fine}: {_RUN_CACHE[key].steps} steps]",
              flush=True)
    return _RUN_CACHE[key]

def tau_from(r, f, which="sum"):
    ceiling = (2.0**r.N) ** 2 * r.energy_initial
    y = r.trace_omega_sum if which == "sum" else r.trace_omega_max
    return crossing_time(r.trace_t, y, f * ceiling)

def slope(xs, ys):
    r = stats.linregress(np.log(xs), np.log(ys))
    return float(r.slope), float(r.rvalue**2)

def windowed(xs, ys):
    n = len(xs); h = n // 2
    b_full, r2 = slope(xs, ys)
    b_lo, _ = slope(xs[h-0:], ys[h-0:]) if n - h >= 3 else (float("nan"), 0)
    b_hi, _ = slope(xs[:h+1], ys[:h+1]) if h + 1 >= 3 else (float("nan"), 0)
    return b_full, r2, b_hi, b_lo   # hi = large-D half (list is descending)

def main():
    print("ROUND 3: tau_f (thermalization time), all-conservative, common complex data")
    results = {}
    for N in (4, 5):
        print(f"\n=== N={N}  (ceiling = {(2.0**N)**2*0.625:.1f}) ===")
        base = {}
        rb = get_run(N, 0.0)
        for f in FRACTIONS:
            try:
                base[f] = tau_from(rb, f).time
            except ValueError as e:
                base[f] = None
                print(f"  baseline f={f}: EXCLUDED  {str(e)[:70]}")
        print("  baseline tau_f (truncation, D=0): " +
              "  ".join(f"f={f}:{(base[f] if base[f] is None else round(base[f],4))}" for f in FRACTIONS))
        for which in ("sum", "max"):
            for f in FRACTIONS:
                xs, ys, excl = [], [], []
                for D in D_VALUES:
                    try:
                        res = tau_from(get_run(N, D), f, which)
                        if not res.sampling_ok:
                            excl.append((D, f"sampling: {res.reason[:50]}")); continue
                        # B4: dt refinement (same fine trace reused across f, which)
                        fine = tau_from(get_run(N, D, fine=True), f, which)
                        rel = abs(fine.time - res.time)/res.time
                        if rel > 0.01:
                            excl.append((D, f"dt-refine {rel:.2%}")); continue
                        xs.append(D); ys.append(res.time)
                    except ValueError as e:
                        excl.append((D, str(e)[:55]))
                mono_inc = all(ys[i] >= ys[i+1] for i in range(len(ys)-1))
                mono_dec = all(ys[i] <= ys[i+1] for i in range(len(ys)-1))
                tag = f"[{which}] f={f}"
                if len(xs) >= 3:
                    b, r2, b_hi, b_lo = windowed(xs, ys)
                    results[(N, which, f)] = (b, xs, ys, base[f])
                    print(f"  {tag}: n={len(xs)} excl={len(excl)} beta={b:+.4f} r2={r2:.4f} "
                          f"windows[{b_hi:+.3f},{b_lo:+.3f}] B2={'ok' if (mono_inc or mono_dec) else 'FAIL'}")
                else:
                    print(f"  {tag}: only {len(xs)} points survive -- no fit")
                for D, why in excl:
                    print(f"      excluded D={D}: {why}")
    # B3': stability across f (absolute floor)
    print("\nB3' across f (per N, [sum]):")
    for N in (4, 5):
        bs = [results.get((N, "sum", f), (None,))[0] for f in FRACTIONS]
        bs = [b for b in bs if b is not None]
        if len(bs) >= 2:
            d = max(bs) - min(bs)
            crit = 0.05 if min(abs(b) for b in bs) < 0.1 else 0.05*abs(np.mean(bs))
            print(f"  N={N}: betas {['%+.4f'%b for b in bs]}  max|dbeta|={d:.4f} -> "
                  f"{'PASS' if d <= max(0.05, 0.05*abs(np.mean(bs))) else 'FAIL'}")
    # B5': delay-ratio stability across N
    print("\nB5' delay ratio tau(D)/tau(0) beta across N (f=0.25, [sum]):")
    for N in (4, 5):
        if (N, "sum", 0.25) in results and results[(N,"sum",0.25)][3]:
            b, xs, ys, b0 = results[(N, "sum", 0.25)]
            ratios = [y/b0 for y in ys]
            br, r2 = slope(xs, ratios)
            print(f"  N={N}: beta_ratio={br:+.4f} (r2={r2:.4f})")
    print("\nExploratory. A PASS licenses the comparison; nothing here is a claim.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
