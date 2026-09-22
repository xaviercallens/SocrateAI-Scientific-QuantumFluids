#!/usr/bin/env python3
"""Turn wp_stability_results.json into the paper's tables (paper/wp_tables.tex) and a verdict summary.

Reads only the JSON written by wp_stability.py; computes nothing new except the PASS/FAIL verdicts of
docs/designs/WASSERSTEIN_STABILITY_PREREG.md §3, which are re-derived here from the stored numbers so
that the paper's verdict column is not copied by hand.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
J = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "data/generated/kinetic_tda/wp_stability_results.json").read_text())
pairs = J["pairs"]; order = [p for p in ["R1", "R2", "R3", "T1", "T2", "S1", "P1"] if p in pairs]


def g(x, d=4):
    return f"{x:.{d}g}"


rows = []
for n in order:
    r = pairs[n]
    for p in (1, 2):
        q = r[f"p{p}"]
        rows.append((n, p, q["B_all"], q["B_k0"], q["W_total"], q["W0"], q["Z_trivial"], q["slack_S"], q["vacuity_V"],
                     q["P1_i"] and q["P1_ii_k0"]))

tex = ["\\begin{tabular}{llrrrrrrrc}", "\\toprule",
       "pair & $p$ & $\\|f-g\\|_p$ & $B_p^{(ii,0)}$ & $W_p$ & $W_p^{(0)}$ & $Z_p$ & $S_p$ & $V_p$ & bound \\\\", "\\midrule"]
for n, p, B, Bk, W, W0, Z, S, V, ok in rows:
    tex.append(f"{n} & {p} & {g(B)} & {g(Bk)} & {g(W)} & {g(W0)} & {g(Z)} & {g(S,3)} & {g(V,3)} & {'holds' if ok else 'VIOLATED'} \\\\")
tex += ["\\bottomrule", "\\end{tabular}"]

# certificates table (degree 0, p = 1 and 2)
ctex = ["\\begin{tabular}{llrrlr}", "\\toprule", "pair & $p$ & rel.\\ gap & max viol. & scope & LP s \\\\", "\\midrule"]
for n in order:
    for p in (1, 2):
        c = pairs[n][f"p{p}"]["certificates"].get("0") or pairs[n][f"p{p}"]["certificates"].get(0)
        if c and "rel_gap" in c:
            ctex.append(f"{n} & {p} & {c['rel_gap']:.1e} & {c['max_violation']:.1e} & {c['scope']} & {c['lp_seconds']} \\\\")
        else:
            ctex.append(f"{n} & {p} & \\multicolumn{{4}}{{l}}{{{(c or {}).get('status','none')}}} \\\\")
ctex += ["\\bottomrule", "\\end{tabular}"]

# verdicts
V1R = [pairs[n]["p1"]["vacuity_V"] for n in ("R1", "R2", "R3") if n in pairs]
V2R = [pairs[n]["p2"]["vacuity_V"] for n in ("R1", "R2", "R3") if n in pairs]
verd = {
    "P1": all(r[-1] for r in rows),
    "P2": all(v >= 1 for v in V1R) if V1R else None,
    "P3": all(v >= 1 for v in V2R) if V2R else None,
    "P4": pairs["P1"]["p1"]["vacuity_V"] < 1 if "P1" in pairs else None,
    "P6": all(pairs[n]["p1"]["slack_S"] >= 10 for n in order if n != "P1"),
    "P7": all(pairs[n]["P7"] for n in order),
    "C1_all_fields": all(pairs[n]["C1_unionfind_ok"] for n in order),
}
Path(ROOT / "paper" / "wp_tables.tex").write_text("\n".join(tex) + "\n")
Path(ROOT / "paper" / "wp_certificates.tex").write_text("\n".join(ctex) + "\n")
print(json.dumps(verd, indent=1))
print("controls:", {k: v.get("PASS") for k, v in J["controls"].items()})
for n in order:
    r = pairs[n]
    print(n, r["shape"], "eps", g(r["eps_sup"]), "H0 bars", r["bars"]["0"] if "0" in r["bars"] else r["bars"][0],
          "linf top30 W1", g(r["linf_top30_W1"]), "| p1: S", g(r["p1"]["slack_S"], 3), "V", g(r["p1"]["vacuity_V"], 3),
          "| p2: S", g(r["p2"]["slack_S"], 3), "V", g(r["p2"]["vacuity_V"], 3))
