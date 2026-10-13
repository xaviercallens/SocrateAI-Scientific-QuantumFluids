"""H1'' driver (PREREG.md).  Usage: python run_h1pp.py CASE K   (CASE in V1a V1b V2 V3 H2 H4 H8; K in 40 30)
Writes records/CASE_K{K}.json (LP history, exact coefficients, certificate).  Gates are evaluated by evaluate.py."""
import json
import math
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rig2 import HPRig  # noqa: E402

CASES = {  # d, alpha, b (H1' K = 40 best, snapped to denominator <= 100)
    "V1a": (1, "1", "106/79"), "V1b": (1, "pi", "23/21"), "V2": (2, "pi", "1"), "V3": (3, "pi", "17/20"),
    "H2": (3, "2", "106/79"), "H4": (3, "4", "7/10"), "H8": (3, "8", "29/99"),
}
GCUT = 1e-12
ROUNDS = 25


def lam_for(b):
    b = Fraction(b)
    return max(2, math.ceil(1 / b + 1)) if 1 / b + 1 > 2 else 2


def main():
    case, K = sys.argv[1], int(sys.argv[2])
    d, alpha, b = CASES[case]
    lam = lam_for(b)
    os.makedirs(os.path.join(HERE, "records"), exist_ok=True)
    t0 = time.time()
    lp = HPRig(d, alpha, b, K, lam=lam, gcut=GCUT)
    sol = lp.solve(rounds=ROUNDS, verbose=True)
    t1 = time.time()
    print(f"[{case} K={K}] hp LP bound {sol['bound_hp']!r} ({t1 - t0:.0f}s)", flush=True)
    rec = {"case": case, "d": d, "alpha": alpha, "b": b, "K": K, "lam": lam, "gcut": GCUT, "rounds_cap": ROUNDS,
           "solve": sol, "solve_s": t1 - t0}
    path = os.path.join(HERE, "records", f"{case}_K{K}.json")
    json.dump(rec, open(path, "w"), indent=1)
    try:
        cert = lp.certify()
        rec["certified"] = True
    except Exception as e:  # reported as "not certified" with the failing step
        cert = {"error": repr(e)[:2000]}
        rec["certified"] = False
    rec["certificate"] = cert
    rec["certify_s"] = time.time() - t1
    json.dump(rec, open(path, "w"), indent=1)
    print(f"[{case} K={K}] certified={rec['certified']} {json.dumps(cert)[:1500]}", flush=True)


if __name__ == "__main__":
    main()
