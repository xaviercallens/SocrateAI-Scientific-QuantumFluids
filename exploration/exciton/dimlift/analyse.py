#!/usr/bin/env python3
"""Analysis of dimlift runs per PREREG.md (gates E1, E2, E3). Usage: analyse.py [results_dir]"""
import json, glob, os, sys
import numpy as np
R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
rng = np.random.default_rng(12345)
out = {"e1": {}, "e2": {}, "e3": {}}
lines = []

def load(p):
    return [json.loads(l) for l in open(p) if l.strip()]

for p in sorted(glob.glob(f"{R}/e12_*.jsonl")):
    recs = load(p)
    key = os.path.basename(p)[4:-6]
    by = {}
    for r in recs:
        by.setdefault(r["method"], {})[r["seed"]] = r
    valid = {m: {s: r for s, r in d.items() if r.get("escaped", 1) == 0 and "analysis_error" not in r} for m, d in by.items()}
    allE = [r["E"] for m in valid for r in valid[m].values()]
    if not allE: continue
    best = min(allE)
    row = {}
    for m, d in by.items():
        v = valid[m]
        E = np.array([r["E"] for r in v.values()])
        row[m] = dict(n=len(d), n_valid=len(v), fail=len(d) - len(v),
                      meanE=float(E.mean()) if len(E) else None,
                      seE=float(E.std(ddof=1) / np.sqrt(len(E))) if len(E) > 1 else None,
                      frac_best=float(np.mean(np.abs(E - best) <= 1e-6 * abs(best))) if len(E) else 0.0,
                      frac_best_of_all=float(np.sum(np.abs(E - best) <= 1e-6 * abs(best)) / max(1, len(d))),
                      non6=float(np.mean([r["n_non6"] for r in v.values()])) if v else None,
                      evals=float(np.mean([r["evals"] for r in d.values()])),
                      secs=float(np.mean([r["secs"] for r in d.values()])))
    # equal-compute control: direct best-of-m restarts, m = eval ratio
    if "direct" in valid and valid["direct"]:
        Ed = np.array([r["E"] for r in valid["direct"].values()])
        for m in ("lift1", "lift2"):
            if m in row:
                mm = max(1, int(round(row[m]["evals"] / row["direct"]["evals"])))
                boots = [rng.choice(Ed, size=mm, replace=True).min() for _ in range(4000)]
                row[m]["equal_compute_m"] = mm
                row[m]["direct_bestofm_mean"] = float(np.mean(boots))
                row[m]["direct_bestofm_hits_best"] = float(np.mean([abs(b - best) <= 1e-6 * abs(best) for b in boots]))
    # E1 gate pieces per lift variant
    g = {}
    for m in ("lift1", "lift2"):
        if m in row and row[m]["meanE"] is not None and row["direct"]["meanE"] is not None:
            diff = row["direct"]["meanE"] - row[m]["meanE"]
            se = np.hypot(row["direct"]["seE"] or 0, row[m]["seE"] or 0)
            g[m] = dict(better_by_2se=bool(diff > 2 * se), frac_not_lower=bool(row[m]["frac_best_of_all"] >= row["direct"]["frac_best_of_all"]),
                        survives_control=bool(row[m]["meanE"] < row[m]["direct_bestofm_mean"]), diff=float(diff), se=float(se))
    # E2
    e2 = None
    if "slide" in valid and "direct" in valid:
        common = sorted(set(valid["slide"]) & set(valid["direct"]))
        if common:
            dE = np.array([valid["slide"][s]["E"] - valid["direct"][s]["E"] for s in common])
            dn = np.array([valid["slide"][s]["n_non6"] - valid["direct"][s]["n_non6"] for s in common])
            dQ = np.array([valid["slide"][s]["Q"] - valid["direct"][s]["Q"] for s in common])
            e2 = dict(n=len(common), dE_mean=float(dE.mean()), dnon6_mean=float(dn.mean()),
                      dnon6_se=float(dn.std(ddof=1) / np.sqrt(len(dn))) if len(dn) > 1 else None,
                      frac_Q_unchanged=float(np.mean(dQ == 0)), gate_decrease_ge2=bool(dn.mean() <= -2))
    out["e1"][key] = dict(best=best, methods=row, gate=g)
    out["e2"][key] = e2
    lines.append(f"== {key}  best E={best:.6f}")
    for m, d in row.items():
        lines.append(f"  {m:6s} valid {d['n_valid']:2d}/{d['n']:2d} meanE {d['meanE'] if d['meanE'] is None else round(d['meanE'],4)} "
                     f"frac_best {d['frac_best_of_all']:.2f} non6 {d['non6'] if d['non6'] is None else round(d['non6'],1)} evals {d['evals']:.0f} secs {d['secs']:.1f}"
                     + (f" | control m={d.get('equal_compute_m')} direct best-of-m mean {d.get('direct_bestofm_mean'):.4f}" if 'equal_compute_m' in d else ""))
    lines.append(f"  E1 gate pieces: {json.dumps(g)}")
    lines.append(f"  E2: {json.dumps(e2)}")

p = f"{R}/e3_mesh3d.jsonl"
if os.path.exists(p):
    recs = load(p)
    by = {}
    for r in recs:
        by.setdefault(r["seed"], {})[r["method"]] = r
    seeds = [s for s, d in by.items() if len(d) == 3]
    wins = sum(by[s]["cm"]["rho_p5"] > by[s]["cvt"]["rho_p5"] for s in seeds)
    med = {m: float(np.median([by[s][m]["rho_p5"] for s in seeds])) for m in ("poisson", "cm", "cvt")}
    dih = {m: float(np.median([by[s][m]["dihed_p5_deg"] for s in seeds])) for m in ("poisson", "cm", "cvt")}
    slv = {m: float(np.median([by[s][m]["frac_rho_lt_0p3"] for s in seeds])) for m in ("poisson", "cm", "cvt")}
    out["e3"] = dict(n_seeds=len(seeds), cm_beats_cvt_p5=int(wins), median_rho_p5=med, median_dihed_p5=dih, median_frac_lt_0p3=slv,
                     gate_met=bool(len(seeds) >= 30 and wins >= 24))
    lines.append(f"== E3: {len(seeds)} seeds; CM beats CVT in rho_p5 in {wins}; median rho_p5 {med}; dihedral p5 {dih}; frac<0.3 {slv}")
json.dump(out, open(f"{R}/summary.json", "w"), indent=1)
print("\n".join(lines))
