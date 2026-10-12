"""H1 driver (PREREG_round2.md, section H1).  Order: H0 (d = 1) first; stop if it fails.  Then d = 3, then d = 2 extra.
Usage: python run_h1.py [--stage h0|d3|d2|all]   (writes solutions/*.json, summary.json, run.log via stdout)."""
import argparse
import json
import math
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp_bound import GaussLP, theta_sum, lattice, E_Z_series  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SOL = os.path.join(HERE, "solutions")
os.makedirs(SOL, exist_ok=True)

COARSE = dict(n_y=4000, rounds=2, n_fine=100000, cut_per_round=200, tol_cut=1e-12)
FULL = dict(n_y=12000, rounds=8, n_fine=400000, cut_per_round=400, tol_cut=1e-12)
REL_BETAS = [0.5, 0.7, 0.85, 1.0, 1.2, 1.5, 2.0, 3.0]
K = 30


VIOL_COARSE = 1e-6     # coarse scan (2 cutting-plane rounds) only ranks betas; residual inter-grid dips ~1e-8 expected
VIOL_FULL = 5e-9       # full runs: residual violations must be below this (LP feasibility tolerance is 1e-10)


def admissible(res, viol_tol=VIOL_FULL):
    if res["bound"] is None:
        return False
    tc = res["tail_certificates"]
    return (tc["fhat_tail"]["ok"] and tc["f_tail"]["ok"]
            and max(res["final_max_f_minus_g"], res["final_max_neg_fhat"]) <= viol_tol)


def scan(d, alpha, tag):
    t0 = time.time()
    unit = alpha / math.pi
    rel = list(REL_BETAS)
    coarse = {}
    tried = set()
    for _ in range(4):                      # extend the grid if the best is at an edge
        for rb in rel:
            if rb in tried:
                continue
            tried.add(rb)
            beta = unit * rb
            lp = GaussLP(d, alpha, beta, K)
            res = lp.solve(**COARSE)
            ok = admissible(res, VIOL_COARSE)
            coarse[rb] = (res["bound"] if res["bound"] is not None else None, ok, res.get("message", ""))
            print(f"[{tag}] coarse beta={beta:.5f} (x{rb}) bound={coarse[rb][0]} admissible={ok} "
                  f"viol={res.get('final_max_f_minus_g')}/{res.get('final_max_neg_fhat')} "
                  f"cert={res.get('tail_certificates')}", flush=True)
        oks = [(b, rb) for rb, (b, ok, _) in coarse.items() if ok and b is not None]
        if not oks:
            print(f"[{tag}] no admissible LP solution in the coarse scan", flush=True)
            return None
        best_rb = max(oks)[1]
        srel = sorted(tried)
        if best_rb == srel[0]:
            rel = [srel[0] * 0.7]
        elif best_rb == srel[-1]:
            rel = [srel[-1] * 1.5]
        else:
            break
    # refine at full settings: the best coarse beta and the geometric means with its two neighbours
    srel = sorted(tried)
    i = srel.index(best_rb)
    cands = {srel[i]}
    if i > 0:
        cands.add(math.sqrt(srel[i - 1] * srel[i]))
    if i < len(srel) - 1:
        cands.add(math.sqrt(srel[i + 1] * srel[i]))
    best = None
    fine = {}
    for rb in sorted(cands):
        beta = unit * rb
        lp = GaussLP(d, alpha, beta, K)
        res = lp.solve(**FULL)
        ok = admissible(res)
        fine[rb] = (res["bound"], ok)
        print(f"[{tag}] full beta={beta:.5f} (x{rb:.4f}) bound={res['bound']} admissible={ok} "
              f"viol={res.get('final_max_f_minus_g')}/{res.get('final_max_neg_fhat')} rounds={len(res.get('history', []))}",
              flush=True)
        if ok and (best is None or res["bound"] > best[0]["bound"]):
            best = (res, lp, beta)
    if best is None:
        print(f"[{tag}] no admissible full solution", flush=True)
        return None
    res, lp, beta = best
    ver = lp.verify_random(n=100000, r_max=24.0)
    out = dict(res)
    out.update({"tag": tag, "beta_best": beta, "coarse_scan": {str(k): v for k, v in coarse.items()},
                "full_scan": {str(k): v for k, v in fine.items()}, "verification_random": ver,
                "elapsed_s": time.time() - t0, "coarse_settings": COARSE, "full_settings": FULL,
                "grid_registered": "r in (0,6], 2000 points; tail grid (6,24], 600 points; y in [0,12]"})
    with open(os.path.join(SOL, f"{tag}.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"[{tag}] BEST beta={beta:.6f} bound={res['bound']:.13f} verify={ver} ({time.time() - t0:.0f}s)", flush=True)
    return out


def stage_h0(summary):
    summary["H0"] = {}
    passed = True
    for alpha in (1.0, math.pi):
        EZ = E_Z_series(alpha)
        EZ_direct, tail = theta_sum(lattice("Z"), alpha)
        tag = f"d1_alpha{alpha:.6g}"
        out = scan(1, alpha, tag)
        bound = out["bound"] if out else None
        diff = (bound - EZ) if bound is not None else None
        ok = diff is not None and abs(diff) <= 1e-8
        passed &= ok
        summary["H0"][tag] = {"alpha": alpha, "E_Z": EZ, "E_Z_direct": EZ_direct, "tail_est": tail, "LP_bound": bound,
                              "bound_minus_EZ": diff, "pass_1e-8": ok,
                              "beta_best": out["beta_best"] if out else None,
                              "verification_random": out["verification_random"] if out else None}
        print(f"H0 alpha={alpha}: E_Z={EZ:.13f} LP={bound} diff={diff} pass={ok}", flush=True)
    summary["H0"]["pass"] = passed
    return passed


def stage_d3(summary):
    summary["d3"] = {}
    for alpha in (2.0, math.pi, 4.0, 8.0):
        E_fcc, t_f = theta_sum(lattice("FCC"), alpha)
        E_bcc, t_b = theta_sum(lattice("BCC"), alpha)
        Emin = min(E_fcc, E_bcc)
        tag = f"d3_alpha{alpha:.6g}"
        out = scan(3, alpha, tag)
        bound = out["bound"] if out else None
        gap = (Emin - bound) / Emin if bound is not None else None
        summary["d3"][tag] = {"alpha": alpha, "E_FCC": E_fcc, "E_BCC": E_bcc, "tail_est": max(t_f, t_b),
                              "min_E": Emin, "which_min": "FCC" if E_fcc <= E_bcc else "BCC", "LP_bound": bound,
                              "relative_gap": gap, "beta_best": out["beta_best"] if out else None,
                              "verification_random": out["verification_random"] if out else None,
                              "tail_certificates": out["tail_certificates"] if out else None}
        print(f"d3 alpha={alpha}: E_FCC={E_fcc:.12f} E_BCC={E_bcc:.12f} LP={bound} gap={gap}", flush=True)


def stage_d2(summary):
    alpha = math.pi
    E_a2, t = theta_sum(lattice("A2"), alpha)
    out = scan(2, alpha, "d2_alphapi")
    bound = out["bound"] if out else None
    summary["d2"] = {"alpha": alpha, "E_A2": E_a2, "tail_est": t, "LP_bound": bound,
                     "relative_gap": (E_a2 - bound) / E_a2 if bound is not None else None,
                     "beta_best": out["beta_best"] if out else None,
                     "verification_random": out["verification_random"] if out else None}
    print(f"d2 alpha=pi: E_A2={E_a2:.12f} LP={bound} gap={summary['d2']['relative_gap']}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all")
    args = ap.parse_args()
    spath = os.path.join(HERE, "summary.json")
    summary = json.load(open(spath)) if os.path.exists(spath) else {}
    summary["date"] = time.strftime("%Y-%m-%d %H:%M")
    summary["K"] = K
    summary["solver"] = "scipy.optimize.linprog method=highs (cvxpy not installed)"
    try:
        import scipy
        summary["scipy_version"] = scipy.__version__
    except Exception:
        pass
    if args.stage in ("h0", "all"):
        ok = stage_h0(summary)
        json.dump(summary, open(spath, "w"), indent=1)
        if not ok:
            print("H0 FAILED: stopping as registered.", flush=True)
            return
    if args.stage in ("d3", "all"):
        stage_d3(summary)
        json.dump(summary, open(spath, "w"), indent=1)
    if args.stage in ("d2", "all"):
        stage_d2(summary)
        json.dump(summary, open(spath, "w"), indent=1)
    print("done", flush=True)


if __name__ == "__main__":
    main()
