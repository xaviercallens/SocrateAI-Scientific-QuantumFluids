"""H1' driver, amendment A2 (PREREG.md): numerical (non-rigorous) LP values with the H1 code, K = 30 and K = 40.
Usage: python run_h1p.py <case> <K>   with case in V1a (d1, alpha 1), V1b (d1, pi), V2 (d2, pi), V3 (d3, pi),
H2 (d3, 2), H4 (d3, 4), H8 (d3, 8).  Writes records/<case>_K<K>.json; prints to stdout (collected in run.log)."""
import json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "H1"))
import lp_bound as LB
import run_h1 as RH

CASES = {"V1a": (1, 1.0), "V1b": (1, math.pi), "V2": (2, math.pi), "V3": (3, math.pi),
         "H2": (3, 2.0), "H4": (3, 4.0), "H8": (3, 8.0)}
VIOL_NUM = 1e-7


def main():
    case, K = sys.argv[1], int(sys.argv[2])
    d, alpha = CASES[case]
    RH.K = K
    RH.VIOL_FULL = VIOL_NUM
    RH.SOL = os.path.join(HERE, "records", "solutions")
    os.makedirs(RH.SOL, exist_ok=True)
    t0 = time.time()
    out = RH.scan(d, alpha, f"{case}_K{K}")
    refs = {}
    if d == 1:
        refs["E_Z"] = LB.E_Z_series(alpha)
    elif d == 2:
        refs["E_A2"] = LB.theta_sum(LB.lattice("A2"), alpha)[0]
    else:
        refs["E_FCC"] = LB.theta_sum(LB.lattice("FCC"), alpha)[0]
        refs["E_BCC"] = LB.theta_sum(LB.lattice("BCC"), alpha)[0]
    rec = {"case": case, "d": d, "alpha": alpha, "K": K, "accepted_numerical": out is not None,
           "B": out["bound"] if out else None, "beta": out["beta_best"] if out else None,
           "max_f_minus_g": out["final_max_f_minus_g"] if out else None,
           "max_neg_fhat": out["final_max_neg_fhat"] if out else None,
           "verification_random": out["verification_random"] if out else None, "refs": refs,
           "seconds": time.time() - t0}
    os.makedirs(os.path.join(HERE, "records"), exist_ok=True)
    with open(os.path.join(HERE, "records", f"{case}_K{K}.json"), "w") as fh:
        json.dump(rec, fh, indent=1)
    print(f"RESULT {case} K={K}: B={rec['B']} refs={refs} ({rec['seconds']:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
