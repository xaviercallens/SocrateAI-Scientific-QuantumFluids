"""Chapter 6 -- re-derive, from the raw per-run JSON files of the programme's PGPE runs, the numbers the chapter quotes about
the classical-field (projected Gross-Pitaevskii) fluid near the Kosterlitz-Thouless transition:

  * the heating ladder (L = 64, round 2 part II, files data/generated/pgpe/r2/II_*.json) and the finite-size series (L = 32, part III, III_*.json):
    seed means of T, n_s/n, n_s lambda_T^2 (lambda_T^2 = 2 pi / T in units hbar = m = k_B = 1, mean density n = 1), eta, eta * n_s lambda^2,
    Q (dipole-matching ratio), condensate fraction, vortex number;
  * the interpolated crossing n_s lambda^2 = 4 (the Nelson-Kosterlitz level) and eta there, its slope.
The definitions are those of exploration/pgpe/analyze_r2.py (admission rule of amendment A4: R_L <= 1.25 and R_T <= 1.1 R_L); this script
re-implements them independently and cross-checks the result against data/generated/pgpe/r2_verdicts.json written by that analysis.
Writes figures/ch06_pgpe_numbers.json.  These runs were made with the numpy PGPE engine of the programme (exploration/pgpe/pgpe.py), not re-run here."""
import json
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
R2 = ROOT / "data/generated/pgpe/r2"
OUT = Path(__file__).resolve().parent
TWO_PI = 2 * np.pi


def load(prefix):
    return [json.loads(f.read_text()) for f in sorted(R2.glob(f"{prefix}*.json"))]


def rows_for(prefix):
    runs = load(prefix); by = defaultdict(list); n_all = len(runs); per_run = []
    for d in runs:
        w = d["whole"]
        adm = bool(w["R_L"] <= 1.25 and w["R_T"] <= 1.1 * w["R_L"])
        per_run.append(dict(name=d["name"], e=round(d["e"], 3), T=w["T"], ns_over_n=w["ns_over_n"], K=w["ns_over_n"] * TWO_PI / w["T"], eta=w["eta"], n_v=w["n_v"], Q=w["Q"], cond=w["cond"], admitted=adm,
                            drift_E=d["drift_E"], seconds=d["seconds"]))
        if adm:
            by[round(d["e"], 3)].append(w)
    rows = []
    for e in sorted(by):
        ws = by[e]; T = float(np.mean([w["T"] for w in ws])); ns = float(np.mean([w["ns_over_n"] for w in ws]))
        et = [w["eta"] for w in ws if np.isfinite(w["eta"])]
        eta = float(np.mean(et)) if et else float("nan")
        rows.append(dict(e=e, n=len(ws), T=T, ns_over_n=ns, K=ns * TWO_PI / T, eta=eta, eta_K=eta * ns * TWO_PI / T, Q=float(np.mean([w["Q"] for w in ws])),
                         cond=float(np.mean([w["cond"] for w in ws])), n_v=float(np.mean([w["n_v"] for w in ws]))))
    return rows, n_all, sum(len(v) for v in by.values()), per_run


def crossing(rows):
    for a, b in zip(rows, rows[1:]):
        if a["K"] >= 4 > b["K"]:
            t = (a["K"] - 4) / (a["K"] - b["K"])
            return dict(between=(a["e"], b["e"]), T_BKT=a["T"] + t * (b["T"] - a["T"]), eta=a["eta"] + t * (b["eta"] - a["eta"]), slope=abs((b["K"] - a["K"]) / (b["T"] - a["T"])))
    return None


res = {}
for tag, prefix, L in (("L64", "II_", 64), ("L32", "III_", 32)):
    rows, n_all, n_adm, per_run = rows_for(prefix)
    res[tag] = dict(L=L, rows=rows, admitted=f"{n_adm}/{n_all}", crossing=crossing(rows), per_run=per_run)

# per-seed crossings (each seed's own ladder, interpolated like the seed mean) -- the spread is the honest error bar of T_BKT(L)
def per_seed_crossings(tag):
    runs = res[tag]["per_run"]; seeds = sorted({r["name"].split("_s")[-1].split("_")[0] for r in runs}); out = {}
    for sd in seeds:
        rr = sorted([r for r in runs if r["name"].count("_s%s" % sd) and r["admitted"]], key=lambda r: r["e"])
        for a, b in zip(rr, rr[1:]):
            if a["K"] >= 4 > b["K"]:
                t = (a["K"] - 4) / (a["K"] - b["K"])
                out[sd] = dict(between=(a["e"], b["e"]), T_BKT=a["T"] + t * (b["T"] - a["T"]), eta=a["eta"] + t * (b["eta"] - a["eta"])); break
    return out
for tag in ("L64", "L32"):
    res[tag]["per_seed_crossings"] = per_seed_crossings(tag)
    ts = [v["T_BKT"] for v in res[tag]["per_seed_crossings"].values()]
    res[tag]["per_seed_T_BKT_range"] = (min(ts), max(ts)) if ts else None

# cross-check against the programme's own analysis output
v = json.loads((ROOT / "data/generated/pgpe/r2_verdicts.json").read_text())
chk = []
for tag, key in (("L64", "II"), ("L32", "III")):
    ref = v[key]["rows"]; mine = res[tag]["rows"]
    assert len(ref) == len(mine)
    chk.append(max(max(abs(a["T"] - b["T"]), abs(a["K"] - b["K"]), abs(a["eta"] - b["eta"])) for a, b in zip(ref, mine)))
res["crosscheck_max_abs_diff_vs_r2_verdicts"] = float(max(chk))
res["crosscheck_crossings"] = dict(L64_ref=v["II"]["crossing"], L32_ref=v["III"]["crossing_L32"])
res["constants"] = dict(units="hbar = m = k_B = 1, mean density n = 1, g n = 1, healing length xi = 1", lambda_T_squared="2 pi / T", L64_N=128, L32_N="64 (as stored)")
json.dump(res, open(OUT / "ch06_pgpe_numbers.json", "w"), indent=1, default=float)
for tag in ("L64", "L32"):
    print(tag, res[tag]["admitted"], "crossing", res[tag]["crossing"])
    for r in res[tag]["rows"]:
        print("  e=%.2f T=%.3f ns/n=%.3f K=%.2f eta=%.3f eta*K=%.2f Q=%.2f cond=%.3f nv=%.1f" % (r["e"], r["T"], r["ns_over_n"], r["K"], r["eta"], r["eta_K"], r["Q"], r["cond"], r["n_v"]))
print("crosscheck", res["crosscheck_max_abs_diff_vs_r2_verdicts"])
for tag in ("L64", "L32"): print(tag, "per-seed crossings", res[tag]["per_seed_crossings"], "range", res[tag]["per_seed_T_BKT_range"])
