#!/usr/bin/env python3
"""Phase 1 summary and gate evaluation, computed from the run records only (pre-registration section 4).

    python3 exploration/exciton/python/phase1_summarise.py <runs_dir> <out_summary.json>
"""
import glob, json, math, os, sys

CM_EXACT = {"K1", "K2", "K3", "K4"}
CM_TRUNC = {"K5", "K6"}
CONTROL = {"N1"}

def load(runs_dir):
    cases = {}
    for f in sorted(glob.glob(os.path.join(runs_dir, "runs_*.jsonl"))):
        cid = os.path.basename(f)[5:-6]
        recs = [json.loads(l) for l in open(f) if l.strip()]
        meta_f = os.path.join(runs_dir, f"case_{cid}.json")
        meta = json.load(open(meta_f)) if os.path.exists(meta_f) else {}
        cases[cid] = (recs, meta)
    return cases

def summarise(cid, recs, meta, elat_factor=1.0):
    kernel, rho, torus = cid.split("_")
    ok = [r for r in recs if "e" in r]
    err = [r for r in recs if "error" in r]
    ratios = [r["e"] / (r["e_lat"] * elat_factor) for r in ok]
    rmin = min(ratios) if ratios else float("nan")
    imin = ratios.index(rmin) if ratios else -1
    comm = torus in ("T36c", "T64c")
    eps_viol = 1e-10 if kernel in CM_EXACT | CONTROL else 1e-6
    tol_att = 1e-6 if kernel in CM_TRUNC else 1e-9
    n_conv = sum(1 for r in ok if r["converged"])
    # fraction of runs within attain tolerance
    n_att = sum(1 for x in ratios if x - 1.0 <= tol_att)
    out = {
        "case": cid, "kernel": kernel, "rho": float(rho), "torus": torus, "n_runs": len(ok), "n_errors": len(err),
        "n_converged": n_conv, "n_start": sum(1 for r in ok if r["stage"] == "start"),
        "n_hop": sum(1 for r in ok if r["stage"] == "hop"),
        "min_ratio": rmin, "min_ratio_minus_1": rmin - 1.0, "argmin_stage": ok[imin]["stage"] if ok else None,
        "n_within_attain_tol": n_att, "l2_violations": sum(r.get("l2_viol", 0) for r in ok),
        "l2_max_rel_increase": max([r.get("l2_max_inc", 0.0) for r in ok] or [0.0]),
        "median_steps": sorted(r["steps"] for r in ok)[len(ok) // 2] if ok else None,
        "max_wall_s": max([r["wall_s"] for r in ok] or [0.0]),
        "selftest_rel": meta.get("selftest_rel"),
    }
    if kernel in CM_EXACT | CM_TRUNC:
        out["EX1a_pass"] = bool(rmin - 1.0 >= -eps_viol)
        if comm:
            out["EX1b_attained"] = bool(rmin - 1.0 <= tol_att)
        else:
            out["EX1c_frustration"] = rmin - 1.0
    if kernel in CONTROL:
        out["EX2_pass"] = bool(rmin <= 0.99)
    return out

def main():
    runs_dir, out_path = sys.argv[1], sys.argv[2]
    cases = load(runs_dir)
    rows = [summarise(cid, recs, meta) for cid, (recs, meta) in cases.items()]
    # planted-bug controls on K1_0.5_T36c
    neg = {}
    key = "K1_0.5_T36c"
    if key in cases:
        recs, meta = cases[key]
        dbl = summarise(key, recs, meta, elat_factor=2.0)     # ordered-pair convention
        half = summarise(key, recs, meta, elat_factor=0.5)
        neg = {"elat_doubled_EX1a_pass": dbl.get("EX1a_pass"), "elat_halved_EX1b_attained": half.get("EX1b_attained"),
               "expected": "both False (the gates must bite)",
               "bites": (dbl.get("EX1a_pass") is False) and (half.get("EX1b_attained") is False)}
    gates = {
        "EX1a_all_pass": all(r["EX1a_pass"] for r in rows if "EX1a_pass" in r),
        "EX1b_commensurate": {r["case"]: r["EX1b_attained"] for r in rows if "EX1b_attained" in r},
        "EX2": {r["case"]: (r["EX2_pass"], r["min_ratio"]) for r in rows if "EX2_pass" in r},
        "L2_total_violations": sum(r["l2_violations"] for r in rows),
        "n_cases": len(rows), "n_runs": sum(r["n_runs"] for r in rows),
        "n_not_converged": sum(r["n_runs"] - r["n_converged"] for r in rows),
        "n_errors": sum(r["n_errors"] for r in rows),
        "NEG": neg,
    }
    json.dump({"gates": gates, "cases": rows}, open(out_path, "w"), indent=1)
    print(f"{'case':16s} {'runs':>5s} {'conv':>5s} {'min E/e_lat - 1':>16s} {'#att':>5s} {'EX1a':>5s} {'EX1b':>5s} {'EX2':>5s} {'L2':>3s} {'med steps':>9s}")
    for r in rows:
        print(f"{r['case']:16s} {r['n_runs']:5d} {r['n_converged']:5d} {r['min_ratio_minus_1']:16.3e} {r['n_within_attain_tol']:5d} "
              f"{str(r.get('EX1a_pass','-')):>5s} {str(r.get('EX1b_attained', r.get('EX1c_frustration','-')))[:7]:>5s} "
              f"{str(r.get('EX2_pass','-')):>5s} {r['l2_violations']:3d} {r['median_steps']!s:>9s}")
    print(json.dumps(gates, indent=1)[:1500])

if __name__ == "__main__":
    main()
