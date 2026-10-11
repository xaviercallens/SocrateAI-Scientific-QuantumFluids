#!/usr/bin/env python3
"""Generate paper/exciton3_numbers.tex from results/phase3/summary.json (every number of the Phase 3 text).
Usage: phase3_paper_numbers.py <summary.json> <out.tex>"""
import json, sys
s = json.load(open(sys.argv[1])); out = sys.argv[2]
def sci(x, d=1):
    m, e = f"{x:.{d}e}".split("e"); return f"${m}\\times10^{{{int(e)}}}$"
L = []
def mac(name, val): L.append(f"\\newcommand{{\\{name}}}{{{val}}}")
w = s["D-a"]["worst"]
mac("DaWorstN", sci(w["n"])); mac("DaWorstNR", sci(w["nr"])); mac("DaWorstOm", sci(w["om"])); mac("DaBelowPsi", sci(w["max_psi_below"]))
mac("DbMatch", sci(s["D-b"]["max_match_error"])); mac("DbMaxRe", sci(s["D-b"]["max_re"]))
mac("DcNorm", sci(s["D-c"]["norm_rel"])); mac("DcEnergy", sci(s["D-c"]["energy_rel"])); mac("DcSteps", str(s["D-c"]["steps"]))
d = s["D-d"]; sw = d["sweep"]
mac("DdBudgetMax", sci(max(x["budget_max"] for x in sw.values()))); mac("DdResidMax", sci(max(x["resid_max"] for x in sw.values())))
mac("DdResidZero", sci(sw["0"]["resid_max"])); mac("DdBudgetZero", sci(sw["0"]["budget_max"]))
om0 = d["omega_median"]["0"]
for k, nm in [("0.25", "A"), ("0.5", "B"), ("1", "C")]:
    mac(f"DdShift{nm}", f"{d['omega_median'][k]-om0:.4f}")
    mac(f"DdCentre{nm}", f"{sw[k]['n_center'][0]:.2f}"); mac(f"DdCorner{nm}", f"{sw[k]['n_corner'][0]:.2f}")
    mac(f"DdJ{nm}", sci(sw[k]['max_j'][0], 1))
mac("DdOmegaZero", f"{om0:.6f}")
mac("DdMaxReLambda", sci(max(abs(v) for v in d["max_re_lambda"].values())))
ex = {e["file"]: e for e in s["exploratory"]}
e16 = ex["d_T16000.jsonl"]
mac("ExplResid", sci(e16["resid_rel"])); mac("ExplBudget", sci(e16["budget_rel"])); mac("ExplOmega", f"{e16['omega']:.6f}")
def f_(k): return ex.get(k)
rows = []
for v, fn in [("0", "d_T16000_V0.jsonl"), ("0.25", "d_T16000_V0.25.jsonl"), ("1", "d_T16000_V1.0.jsonl")]:
    e_ = f_(fn)
    if e_: rows.append((v, e_["resid_rel"], e_["budget_rel"]))
txt = "; ".join(f"$V_0={v}$: residual {sci(r)}, budget {sci(b)}" for v, r, b in rows)
allpass = all(r <= 1e-7 and b <= 1e-8 for _, r, b in rows) and e16["resid_rel"] <= 1e-7
mac("ExplOtherSentence", "the other amplitudes give " + txt + (" (all within the registered thresholds)." if allpass else " (not all within the registered thresholds)."))
mac("ExplRtolResid", sci(ex["d_rtol1e-12.jsonl"]["resid_rel"]))
de = s["D-e"]; mac("DeTraj", sci(de["trajectory"]["diff_rel"]))
r = s["D-f"]["ratios"]; mac("DfRatioA", f"{r[0]:.2f}"); mac("DfRatioB", f"{r[1]:.2f}")
g = s["D-g"]; mac("DgN", f"{g['runs'][0]['n']:.1f}"); mac("DgBudget", f"{min(x['budget'] for x in g['runs']):.2f}"); mac("DgSeeds", str(g["n_seeds"]))
sh = max(d['omega_median'][k] - om0 for k in ("0.25", "0.5", "1"))
mac("NPARTABSTRACTTHREE",
    "the steady states, the $768\\times768$ linearisation (matched to " + sci(s["D-b"]["max_match_error"]) + "), the conservative limit and the IMEX threshold and "
    "order passed as registered; the stationarity and pump-budget gates of the gate sweep \\emph{failed} as registered at $t=4000$ "
    "(residual up to " + sci(max(x["resid_max"] for x in sw.values())) + "; the horizon was too short for the slow relaxation) and pass in an exploratory continuation to $t=16000$, one seed per amplitude; the "
    "expected shift of the locked emission frequency lay between $0$ and $V_0$, which in this small periodic box is only the area average of the gate.")
open(out, "w").write("\n".join(L) + "\n")
print(len(L), "macros")
