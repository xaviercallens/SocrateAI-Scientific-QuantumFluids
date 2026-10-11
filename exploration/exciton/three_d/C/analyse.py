import json, numpy as np, collections
ref=json.load(open("reference.json")); R=ref["refs"]; geo=ref["geometry"]
recs=[json.loads(l) for l in open("records.jsonl")]
by=collections.defaultdict(list)
for r in recs: by[(r["N"],r["kernel"])].append(r)
K=list(R); TOL=1e-8
L=["# Experiment C results (S^3), run 2026-10-11","",
"Registered in `../PREREG.md`. Code: `run_C.py`, `analyse.py`. Records: `records.jsonl` (one L-BFGS start per line), `reference.json`.","",
"## Geometry checks","",
f"- 600-cell: {geo['n600']} vertices, unit norm to {geo['norm600']:.1e}, min chord {geo['min_chord_600']:.15f} (expected 2 sin(pi/10) = {geo['expected_min_chord_600']:.15f}).",
f"- 24-cell: {geo['n24']} vertices, min chord {geo['min_chord_24']:.15f} (expected 1).","",
"## Gate C1 (N = 120, 50 starts per kernel; reach 600-cell energy within 1e-8 relative)","",
"| kernel | E_600 | success | lowest found | max rel dev of lowest from E_600 |","|---|---|---|---|---|"]
ok=True
for k in K:
    rs=by[(120,k)]; E=np.array([r["E"] for r in rs]); e0=R[k]["E600"]
    rel=np.abs(E-e0)/abs(e0); s=int((rel<=TOL).sum()); ok&= s/len(rs)>=0.9
    L.append(f"| {k} | {e0:.10g} | {s}/{len(rs)} | {E.min():.10g} | {rel.min():.1e} |")
L+=["",f"**Gate C1: {'PASS' if ok else 'FAIL'}** (threshold >= 45/50 for every kernel).",""]
# lower than 600 cell?
low=[(k,r["E"]) for k in K for r in by[(120,k)] if r["E"]<R[k]["E600"]-TOL*abs(R[k]["E600"])]
L.append(f"Starts finding energy below the 600-cell by > 1e-8 relative: {len(low)}.")
gm=max(r["gmax"] for r in recs); L.append(f"Max |gradient| component over all {len(recs)} records: {gm:.1e}.")
L+=["","## N = 24 vs 24-cell (reported, not gated)","","| kernel | E_24cell | starts at 24-cell energy (1e-8) | lowest found | lowest below 24-cell? |","|---|---|---|---|---|"]
for k in K:
    E=np.array([r["E"] for r in by[(24,k)]]); e0=R[k]["E24"]
    s=int((np.abs(E-e0)/abs(e0)<=TOL).sum())
    L.append(f"| {k} | {e0:.10g} | {s}/50 | {E.min():.10g} | {'YES' if E.min()<e0-TOL*abs(e0) else 'no'} |")
L+=["","## Frustration scan, N = 12..48 even","",
"For each (N, kernel): number of distinct minima energies (clustered within 1e-8 relative) and the fraction of the 50 starts reaching the lowest. `unique` = one distinct minimum. Cells show `n_distinct / frac_lowest`.","",
"| N | "+" | ".join(K)+" |","|---|"+"---|"*len(K)]
nonunique=collections.defaultdict(list)
for N in range(12,50,2):
    row=[]
    for k in K:
        E=np.sort([r["E"] for r in by[(N,k)]]); e0=E[0]
        cl=[[E[0]]]
        for e in E[1:]:
            if abs(e-cl[-1][0])<=TOL*abs(cl[-1][0]): cl[-1].append(e)
            else: cl.append([e])
        n=len(cl); fr=len(cl[0])/len(E)
        if n>1: nonunique[k].append(N)
        row.append(f"{n} / {fr:.2f}")
    L.append(f"| {N} | "+" | ".join(row)+" |")
L+=["","Smallest N (in 12..48 even) with more than one distinct minimum found by 50 random starts:",""]
for k in K: L.append(f"- {k}: {nonunique[k][0] if nonunique[k] else 'none'} (all such N: {nonunique[k]})")
# distinct-minima energy lists for a few
open("RESULTS_body.md","w").write("\n".join(L)+"\n")
print("\n".join(L))
