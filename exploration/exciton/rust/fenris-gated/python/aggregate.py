"""Collect case_*.json into CSV tables and two summary figures."""
import csv, glob, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
rows = []
for f in sorted(glob.glob(RES + "/case_*.json")):
    d = json.load(open(f)); s = d["summary"]
    st = d["starts"]
    keys = ["case", "group", "shape", "spec", "N_free", "B", "area", "perimeter", "nstart", "n_converged", "n_loose", "n_pd", "n_escaped",
            "n_good", "e_bulk", "E_per_node_best", "dE_best", "dE_per_perimeter_best", "E_mean", "E_std", "n_distinct_1e7",
            "n5_best", "n7_best", "n5_mean", "n5_std", "n7_mean", "n7_std", "n_other_mean", "n_defect_wall_mean", "n_defect_near_mean",
            "n_defect_deep_mean", "n_deep_mean", "psi6_abs_mean_mean", "psi6_global_mean", "Q_mean", "Q_std", "euler_all_ok",
            "n_nonconforming", "n_euler_fail", "secs_total"]
    r = {k: s.get(k) for k in keys}
    for t, v in (s.get("frac_best") or {}).items():
        r["frac_best_" + t] = v
    r["n_not_strict_but_accepted"] = sum(1 for p in st if "E_tot" in p and p.get("converged") == 0)
    rows.append(r)
if rows:
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with open(RES + "/table_all.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(len(rows), "cases ->", RES + "/table_all.csv")
    prim = [r for r in rows if r["group"] == "primary" and r["n_good"]]
    shapes = list(dict.fromkeys(r["shape"] for r in prim)); specs = list(dict.fromkeys(r["spec"] for r in prim))
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
    x = np.arange(len(shapes)); wd = 0.8 / max(1, len(specs))
    for k, sp in enumerate(specs):
        y1 = [next((r["n_defect_wall_mean"] + r["n_defect_near_mean"] + r["n_defect_deep_mean"] for r in prim if r["shape"] == s and r["spec"] == sp), np.nan) / 1 for s in shapes]
        y2 = [next((r["dE_per_perimeter_best"] for r in prim if r["shape"] == s and r["spec"] == sp), np.nan) for s in shapes]
        ax[0].bar(x + k * wd, y1, wd, label=sp); ax[1].bar(x + k * wd, y2, wd, label=sp)
    for a, t in zip(ax, ["non-6 free nodes (mean over accepted starts)", "excess energy per perimeter (best state)"]):
        a.set_xticks(x + 0.4); a.set_xticklabels(shapes, rotation=45, ha="right", fontsize=8); a.set_title(t, fontsize=9)
    ax[0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(RES + "/png/summary_primary.png", dpi=110)
