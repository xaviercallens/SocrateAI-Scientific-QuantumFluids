"""Hull-based interior defect counts of the sibling edge study's definition (non-hull vertices of the Delaunay
triangulation of the free particles only), applied to the edgecmp cases, and comparison with the sibling's summary.json
(read-only). Usage: python3 post_analysis.py"""
import glob, json, os, sys
import numpy as np
from scipy.spatial import Delaunay
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geometry as G
from gates import SCR
from study import parse_out, RES

SIB = "/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/exploration/exciton/edge/results/analysis/summary.json"


def hull_counts(P):
    tri = Delaunay(P)
    deg = np.zeros(len(P), int)
    edges = set()
    for t in tri.simplices:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            edges.add((min(a, b), max(a, b)))
    for a, b in edges:
        deg[a] += 1; deg[b] += 1
    hull = set(tri.convex_hull.ravel().tolist())
    inner = np.array([i not in hull for i in range(len(P))])
    c = deg[inner]
    return dict(n_interior=int(inner.sum()), n5=int((c == 5).sum()), n7=int((c == 7).sum()), other=int(((c != 5) & (c != 6) & (c != 7)).sum()),
                charge=int((6 - c).sum()))


out = {}
sib = {}
if os.path.exists(SIB):
    for c in json.load(open(SIB))["cases"]:
        sib[c["case"]] = c
names = {"ungated": "dip", "3.0": "g3", "10.0": "g10"}
for f in sorted(glob.glob(RES + "/case_edgecmp_*.json")):
    d = json.load(open(f)); s = d["summary"]
    shape = G.fit_shape(s["shape"], s["N_free"], w=s["w"])
    nf = s["N_free"]
    runs = parse_out(f"{SCR}/prod/{s['case']}/out.txt", nf)
    recs = []
    for st, r in zip(d["starts"], runs):
        if "E_tot" not in st:
            continue
        h = hull_counts(r["P"]); h["E_tot"] = st["E_tot"]; recs.append(h)
    if not recs:
        continue
    best = min(recs, key=lambda x: x["E_tot"])
    spec = s["spec"].split(":")
    ratio = "ungated" if spec[0] == "ungated" else f"{float(spec[2]) / float(spec[1]):.1f}"
    kk = names.get(ratio, ratio)
    key = f"{kk}_square_N{nf}"
    entry = dict(case=s["case"], N_free=nf, n_good=len(recs), best=best,
                 n5_range=[min(r["n5"] for r in recs), max(r["n5"] for r in recs)],
                 n7_range=[min(r["n7"] for r in recs), max(r["n7"] for r in recs)],
                 charge_range=[min(r["charge"] for r in recs), max(r["charge"] for r in recs)])
    if key in sib:
        entry["sibling_best"] = sib[key]["defects"]
        entry["sibling_E_edge_over_sqrtN"] = sib[key].get("E_edge_over_sqrtN")
    out[key] = entry
json.dump(out, open(RES + "/edge_overlap.json", "w"), indent=1)
print(json.dumps(out, indent=1))
