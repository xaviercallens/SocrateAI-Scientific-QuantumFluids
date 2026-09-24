#!/usr/bin/env python3
"""Verdicts of docs/designs/PGPE_R2_PREREG.md (with amendments R2-A1, R2-A2) from data/generated/pgpe/r2/*.json,
plus the Part IV post-hoc re-analysis of round 1's g1 with the noise-aware window.
Run: .venv/bin/python exploration/pgpe/analyze_r2.py  -> data/generated/pgpe/r2_verdicts.json"""
from __future__ import annotations
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from round2 import fit_g1_window

ROOT = Path(__file__).resolve().parents[2]; R2 = ROOT / "data/generated/pgpe/r2"; SW = ROOT / "data/generated/pgpe/sweep"


def load(prefix):
    return {f.stem: json.loads(f.read_text()) for f in sorted(R2.glob(f"{prefix}*.json"))}


def early(d):
    """R2-A2: blocks with t0 in {100, 200}."""
    bl = [b for b in d["blocks"] if b["t0"] in (100.0, 200.0)]
    eta = [b["eta"] for b in bl]
    return {"cond": float(np.mean([b["cond"] for b in bl])), "T": float(np.mean([b["T"] for b in bl])),
            "Q": float(np.mean([b["Q"] for b in bl])), "n_v": float(np.mean([b["n_v"] for b in bl])),
            "eta": float(np.mean(eta)) if all(np.isfinite(eta)) else float("nan")}


def part_I():
    D = load("I_"); out = {}
    for base in sorted({d["base"] for d in D.values()}):
        arm = {d["arm"]: d for d in D.values() if d["base"] == base}
        if not {"V", "P"} <= set(arm):
            continue
        V, P = early(arm["V"]), early(arm["P"])
        late = lambda d: float(np.mean([b["cond"] for b in d["blocks"] if b["t0"] >= 1000]))
        track = [(b["t0"], bv["cond"] - bp["cond"], bv["n_v"] - bp["n_v"]) for b, bv, bp in
                 zip(arm["V"]["blocks"], arm["V"]["blocks"], arm["P"]["blocks"])]
        r = {"V": V, "P": P,
             "I1_cond_gap": P["cond"] - V["cond"], "I1": bool(V["cond"] < P["cond"] - 0.15),
             "I2_relT": abs(V["T"] - P["T"]) / P["T"], "I2": bool(abs(V["T"] - P["T"]) / P["T"] <= 0.05),
             "I3_Q_gap": V["Q"] - P["Q"], "I3": bool(V["Q"] >= P["Q"] + 0.2),
             "I4_eta_ratio": V["eta"] / P["eta"] if np.isfinite(V["eta"]) and np.isfinite(P["eta"]) else float("nan"),
             "I5_late_cond_V": late(arm["V"]), "I5_late_cond_P": late(arm["P"]),
             "I5_relaxed": bool(abs(late(arm["V"]) - late(arm["P"])) <= 0.05),
             "I5_corr_dcond_dnv": float(np.corrcoef([x[1] for x in track], [x[2] for x in track])[0, 1]),
             "track": track}
        r["I4"] = bool(np.isfinite(r["I4_eta_ratio"]) and r["I4_eta_ratio"] >= 1.5) if np.isfinite(r["I4_eta_ratio"]) else "not evaluable"
        if "0" in arm:
            b0 = arm["0"]["blocks"]; r["C4_cond_first_last"] = (b0[0]["cond"], b0[-1]["cond"])
            r["C4"] = bool(abs(b0[0]["cond"] - b0[-1]["cond"]) <= 0.05)
        out[base] = r
    out["causal_claim"] = bool(out) and all(r["I1"] and r["I2"] and r["I4"] is True for r in out.values() if isinstance(r, dict))
    return out


def ladder_rows(prefix):
    D = load(prefix); by = defaultdict(list)
    for d in D.values():
        w = d["whole"]
        if not (w["R_L"] <= 1.25 and w["R_T"] <= 1.1 * w["R_L"]):       # A4 admission
            continue
        by[round(d["e"], 3)].append(w)
    rows = []
    for e in sorted(by):
        ws = by[e]; T = float(np.mean([w["T"] for w in ws])); ns = float(np.mean([w["ns_over_n"] for w in ws]))
        et = [w["eta"] for w in ws if np.isfinite(w["eta"])]
        rows.append({"e": e, "n": len(ws), "T": T, "ns_over_n": ns, "K": ns * 2 * np.pi / T,
                     "eta": float(np.mean(et)) if et else float("nan"), "Q": float(np.mean([w["Q"] for w in ws])),
                     "cond": float(np.mean([w["cond"] for w in ws])), "laws": [w["law"] for w in ws]})
    n_all = len(D); n_adm = sum(len(v) for v in by.values())
    return rows, n_all, n_adm


def crossing(rows):
    for a, b in zip(rows, rows[1:]):
        if a["K"] >= 4 > b["K"]:
            t = (a["K"] - 4) / (a["K"] - b["K"])
            return {"between": (a["e"], b["e"]), "T_BKT": a["T"] + t * (b["T"] - a["T"]),
                    "eta": a["eta"] + t * (b["eta"] - a["eta"]) if np.isfinite(a["eta"]) and np.isfinite(b["eta"]) else float("nan"),
                    "slope": abs((b["K"] - a["K"]) / (b["T"] - a["T"]))}
    return None


def part_II():
    rows, n_all, n_adm = ladder_rows("II_")
    cr = crossing(rows)
    r1 = {"K": 3.04, "eta": 0.349}                        # round 1, e = 1.20 (PGPE_BKT_RESULTS.md)
    e12 = next((r for r in rows if abs(r["e"] - 1.2) < 1e-9), None)
    out = {"rows": rows, "admitted": f"{n_adm}/{n_all}", "crossing": cr}
    if e12:
        out["C5"] = {"K": e12["K"], "eta": e12["eta"], "PASS": bool(abs(e12["K"] - r1["K"]) / r1["K"] <= 0.25 and abs(e12["eta"] - r1["eta"]) / r1["eta"] <= 0.20)}
    out["L1"] = bool(cr is not None)
    out["L2"] = bool(cr is not None and np.isfinite(cr["eta"]) and abs(cr["eta"] - 0.25) <= 0.08)
    d = [(r["e"], r["eta"] * r["K"]) for r in rows if r["K"] > 4 and np.isfinite(r["eta"])]
    out["L3_products"] = d; out["L3"] = bool(d) and all(0.75 <= p <= 1.33 for _, p in d)
    return out


def part_III(cr64):
    rows, n_all, n_adm = ladder_rows("III_")
    cr = crossing(rows)
    out = {"rows": rows, "admitted": f"{n_adm}/{n_all}", "crossing_L32": cr, "crossing_L64": cr64}
    out["F1"] = bool(cr and cr64 and cr["T_BKT"] >= cr64["T_BKT"])
    out["F2"] = bool(cr and cr64 and cr64["slope"] > cr["slope"])
    return out


def part_IV():
    """POST-HOC re-analysis of round 1 with the noise-aware g1 window (original verdicts stay on record)."""
    by = defaultdict(list)
    best = {}
    for f in sorted(SW.glob("e*_s*.json")):
        if "quick" in f.name:
            continue
        d = json.loads(f.read_text()); d.setdefault("t_end", 1500.0); k = (d["e"], d["seed"])
        if k not in best or d["t_end"] > best[k]["t_end"]:
            best[k] = d
    for (e, sd), d in sorted(best.items()):
        fit = fit_g1_window(np.array(d["g1"]["r"]), np.array(d["g1"]["g1"]), d["L"])
        by[e].append(fit)
    rows = [{"e": e, "laws": [f["law"] for f in fs], "eta": [round(f["eta"], 3) for f in fs], "r_max": [f["r_max"] for f in fs]} for e, fs in sorted(by.items())]
    alg = [sum(l == "algebraic" for l in r["laws"]) * 2 > len(r["laws"]) for r in rows]
    last_alg = max((i for i, a in enumerate(alg) if a), default=None)
    eta_last = float(np.mean([x for x in rows[last_alg]["eta"] if np.isfinite(x)])) if last_alg is not None else float("nan")
    return {"rows": rows, "last_algebraic_e": rows[last_alg]["e"] if last_alg is not None else None,
            "D3_reanalysed": bool(last_alg is not None and eta_last < 0.5), "eta_last_alg": eta_last,
            "B1_reanalysed_high_T_not_algebraic": not alg[-1]}


if __name__ == "__main__":
    v = {"I": part_I(), "II": part_II()}
    v["III"] = part_III(v["II"].get("crossing"))
    v["IV_posthoc_round1"] = part_IV()
    (ROOT / "data/generated/pgpe/r2_verdicts.json").write_text(json.dumps(v, indent=1, default=float))
    print(json.dumps(v, indent=1, default=float))
