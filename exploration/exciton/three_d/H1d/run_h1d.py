"""H1d driver (PREREG.md).  Usage: python run_h1d.py CASE S M
Writes records/CASE_s{S}_m{M}.json (float UB, exact rational lambda, certificate).  One record per (case, s, m), so a killed
launch resumes by skipping existing records (launch.sh).  Gates are evaluated by evaluate.py."""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from flint import arb  # noqa: E402
from fractions import Fraction  # noqa: E402
from dual import solve, certify  # noqa: E402

CASES = {  # d, alpha label
    "V1": (1, "pi"), "V2": (2, "pi"),
    "D3pi": (3, "pi"), "D3a2": (3, "2"), "D3a4": (3, "4"), "D3a8": (3, "8"),
    "DEV": (3, "1"),   # development only (non-gate); its records are moved to dev/
}
ALPHA_F = {"1": 1.0, "pi": math.pi, "2": 2.0, "4": 4.0, "8": 8.0}
ALPHA_A = {"1": lambda: arb(1), "pi": arb.pi, "2": lambda: arb(2), "4": lambda: arb(4), "8": lambda: arb(8)}


def main():
    case, s, m = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    os.makedirs(os.path.join(HERE, "records"), exist_ok=True)
    path = os.path.join(HERE, "records", f"{case}_s{s}_m{m}.json")
    if os.path.exists(path):
        print("record exists, skipping", path); return
    d, al = CASES[case]
    t0 = time.time()
    sol = solve(d, m, ALPHA_F[al], s)
    t1 = time.time()
    rec = {"case": case, "d": d, "alpha": al, "s": s, "m": m, "n_orbits": sol["n_orbits"], "UB_float": sol["UB_float"],
           "solve_s": t1 - t0}
    try:
        cert = certify(sol, ALPHA_A[al]())
        rec["certified"] = True
    except Exception as e:
        cert = {"error": repr(e)[:2000]}
        rec["certified"] = False
    rec["certificate"] = cert
    rec["certify_s"] = time.time() - t1
    # exact certified lambda (per point, by orbit representative) for independent re-verification
    lam = [Fraction(max(0.0, float(x))).limit_denominator(2 ** 64) for x in sol["lam"]]
    rec["reps"] = [list(b) for b in sol["reps"]]
    rec["orbit_sizes"] = [int(z) for z in sol["size"]]
    rec["lambda_float_rounded"] = [str(x) for x in lam]   # certify() renormalises these exactly to sum 1 - s^-d
    tmp = path + ".tmp"
    json.dump(rec, open(tmp, "w"))
    os.replace(tmp, path)
    print(f"[{case} s={s} m={m}] UB_float={sol['UB_float']!r} certified={rec['certified']} "
          f"{json.dumps(cert)[:300]} ({t1 - t0:.0f}+{rec['certify_s']:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
