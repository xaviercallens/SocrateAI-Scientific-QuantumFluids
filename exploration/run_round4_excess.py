#!/usr/bin/env python3
# TIER C - EXPLORATORY, NO CLAIMS
"""Round 4: excess delay Delta-tau = tau(D) - tau_0.

Specified in docs/designs/M2_OBSERVABLE_VALIDATION_BATTERY.md "Round 4",
WITH an explicit honesty label: post-hoc MOTIVATED (written knowing round 3's
outcome) but pre-run SPECIFIED, with inherited criteria and a fixed kill rule.

Reads round3_tau.csv -- no re-integration, so no configuration can be
re-tuned between the rounds.

Run:  PYTHONPATH=src python3 exploration/run_round4_excess.py
"""
import csv, os, sys
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
B3_ABS_FLOOR = 0.05

def load():
    rows = []
    with open(os.path.join(HERE, "round3_tau.csv")) as fh:
        for r in csv.DictReader(fh):
            rows.append((int(r["N"]), r["convention"], float(r["f"]),
                         float(r["D"]), float(r["tau"]), int(r["attained"])))
    return rows

def fit(xs, ys):
    r = stats.linregress(np.log(xs), np.log(ys))
    return float(r.slope), float(r.rvalue**2)

def main():
    rows = load()
    if not rows:
        print("no data"); return 2
    Ns = sorted({r[0] for r in rows}); convs = ["sum", "max"]
    fs = sorted({r[2] for r in rows})
    print("ROUND 4: excess delay Delta-tau = tau(D) - tau_0")
    print("  (post-hoc motivated, pre-run specified -- see the battery doc's honesty label)\n")
    alphas = {}
    for N in Ns:
        for which in convs:
            for f in fs:
                sub = [r for r in rows if r[0]==N and r[1]==which and r[2]==f]
                base = [r for r in sub if r[3]==0.0 and r[5]==1]
                if not base:
                    print(f"  N={N} [{which}] f={f}: no baseline -- skipped"); continue
                tau0 = base[0][4]
                xs, ys, excl = [], [], []
                for _,_,_,D,tau,att in sorted(sub, key=lambda r:-r[3]):
                    if D == 0.0: continue
                    if not att:
                        excl.append((D, "censored (never attained)")); continue
                    d = tau - tau0
                    if d <= 0:
                        excl.append((D, f"Delta-tau = {d:+.4f} <= 0 (dispersion ACCELERATES here)"))
                        continue
                    xs.append(D); ys.append(d)
                if len(xs) < 3:
                    print(f"  N={N} [{which}] f={f}: only {len(xs)} usable points -- no fit")
                    for D,w in excl: print(f"       excl D={D}: {w}")
                    continue
                a, r2 = fit(xs, ys)
                h = len(xs)//2
                a_hi,_ = fit(xs[:h+1], ys[:h+1]); a_lo,_ = fit(xs[h:], ys[h:])
                mono = all(ys[i] >= ys[i+1] for i in range(len(ys)-1))
                alphas[(N,which,f)] = a
                print(f"  N={N} [{which}] f={f}: n={len(xs)} alpha={a:+.4f} r2={r2:.4f} "
                      f"windows[{a_hi:+.3f},{a_lo:+.3f}] B2={'ok' if mono else 'FAIL'} "
                      f"tau_0={tau0:.4f}")
                for D,w in excl: print(f"       excl D={D}: {w}")
    print("\n" + "="*70)
    print("KILL CRITERION (fixed in advance): alpha must be stable across BOTH f")
    print("AND both conventions, |d-alpha| <= 0.05 (absolute floor).")
    print("="*70)
    vals = list(alphas.values())
    if len(vals) < 2:
        print("  insufficient fits to evaluate -- treated as FAIL")
        verdict = False
    else:
        spread = max(vals) - min(vals)
        for k,v in sorted(alphas.items()): print(f"    N={k[0]} [{k[1]}] f={k[2]}: alpha={v:+.4f}")
        print(f"\n  spread = {spread:.4f}  ->  {'PASS' if spread <= B3_ABS_FLOOR else 'FAIL'}")
        verdict = spread <= B3_ABS_FLOOR
    print()
    if verdict:
        print("  => alpha is stable. The delay HAS an exponent in this model; report it")
        print("     as a LOWER BOUND (censoring removes the most-delayed configurations).")
    else:
        print("  => PER THE KILL CRITERION: the delay has NO exponent in this model.")
        print("     M3 closes on CLAIM-013's ordinal finding plus Option C's")
        print("     triangulation. No fifth observable is attempted.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
