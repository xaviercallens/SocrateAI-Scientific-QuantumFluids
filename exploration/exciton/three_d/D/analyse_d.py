#!/usr/bin/env python3
"""Gate D1 analysis. Usage: analyse_d.py  (reads records_p*.jsonl, writes summary_d.json, prints table)"""
import json, glob, os
import numpy as np
from math import comb
H = os.path.dirname(os.path.abspath(__file__))
by = {}
for p in sorted(glob.glob(f"{H}/records_p*.jsonl")):
    for l in open(p):
        r = json.loads(l); by.setdefault(r["seed"], {})[r["method"]] = r
arms = ["hybrid", "cm_only", "cvt20", "cvt40", "cvt80"]
seeds = sorted(s for s, d in by.items() if all(a in d for a in arms))
def col(a, k, ss=None): return np.array([by[s][a][k] for s in (ss or seeds)])
out = dict(n_seeds=len(seeds), arms={}, paired={})
L = [f"seeds complete: {len(seeds)}"]
for a in arms:
    out["arms"][a] = dict(rho_p5_median=float(np.median(col(a, "rho_p5"))), rho_p5_min=float(col(a, "rho_p5").min()),
        rho_min_worst=float(col(a, "rho_min").min()), dihed_p5_median=float(np.median(col(a, "dihed_p5_deg"))),
        dihed_min_worst=float(col(a, "dihed_min_deg").min()), frac_lt03_median=float(np.median(col(a, "frac_rho_lt_0p3"))),
        frac_lt03_worst=float(col(a, "frac_rho_lt_0p3").max()))
    L.append(a + " " + json.dumps({k: round(v, 4) for k, v in out["arms"][a].items()}))
def sign_p(w, n):  # one-sided exact binomial P(W >= w), p=.5
    return sum(comb(n, k) for k in range(w, n + 1)) / 2 ** n
for ref in ("cvt40", "cvt20", "cvt80", "cm_only"):
    for label, ss in (("all", seeds), ("excl_seed0", [s for s in seeds if s != 0])):
        d = col("hybrid", "rho_p5", ss) - col(ref, "rho_p5", ss)
        n = len(d); w = int((d > 0).sum())
        dd = col("hybrid", "dihed_p5_deg", ss) - col(ref, "dihed_p5_deg", ss)
        out["paired"][f"hybrid_vs_{ref}_{label}"] = dict(n=n, mean_diff=float(d.mean()), se=float(d.std(ddof=1) / np.sqrt(n)),
            median_diff=float(np.median(d)), wins=w, sign_p_one_sided=sign_p(w, n), min_diff=float(d.min()),
            dihed_p5_mean_diff=float(dd.mean()), dihed_p5_se=float(dd.std(ddof=1) / np.sqrt(n)),
            sliver_mean_diff=float((col("hybrid", "frac_rho_lt_0p3", ss) - col(ref, "frac_rho_lt_0p3", ss)).mean()))
        L.append(f"hybrid-{ref} [{label}] " + json.dumps({k: round(v, 5) if isinstance(v, float) else v for k, v in out["paired"][f'hybrid_vs_{ref}_{label}'].items()}))
if len(seeds) == 30:
    g = out["paired"]["hybrid_vs_cvt40_all"]
    out["gate_D1_primary_cvt40"] = bool(out["arms"]["hybrid"]["rho_p5_median"] >= out["arms"]["cvt40"]["rho_p5_median"] and g["wins"] >= 20)
    L.append(f"GATE D1 (primary, vs cvt40): {out['gate_D1_primary_cvt40']}")
    for ref in ("cvt20", "cvt80"):
        L.append(f"  gate vs {ref}: {out['arms']['hybrid']['rho_p5_median'] >= out['arms'][ref]['rho_p5_median'] and out['paired'][f'hybrid_vs_{ref}_all']['wins'] >= 20}")
json.dump(out, open(f"{H}/summary_d.json", "w"), indent=1)
print("\n".join(L))
