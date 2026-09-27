#!/usr/bin/env python3
"""Verdicts of docs/designs/PGPE_R3_PREREG.md from data/generated/pgpe/r3/*.json and *_samples.npz.
Vortex temperature per block: torus point-vortex energy of each neutral sample, inverted through the canonical
calibration at the sample's N (nearest calibrated size if N is odd-sized/uncalibrated -> that sample skipped),
validity beta_WM >= 0.3 ('hot, unreadable' below; 'cold, unreadable' if E below the coldest calibrated point).
Run: .venv/bin/python exploration/pgpe/analyze_r3.py -> data/generated/pgpe/r3_verdicts.json"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vortex_thermometer_canonical import read_beta

ROOT = Path(__file__).resolve().parents[2]; R3 = ROOT / "data/generated/pgpe/r3"
CAL = json.loads((ROOT / "data/generated/pgpe/vortex_thermometer_cal.json").read_text())
_large = ROOT / "data/generated/pgpe/vortex_thermometer_cal_large.json"
if _large.exists():
    CAL.update(json.loads(_large.read_text()))          # N = 26..40 (2000 sweeps), same closure criterion
BASES = ["e0.60_s11_t4000", "e0.90_s11_t4000", "e0.90_s12_t4000"]
BETA_MIN = 0.3


def tv_per_block(name, t_tr=0.0, block=100.0):
    """Per block: T_v (phys) from readable samples, or a status string."""
    z = np.load(R3 / f"{name}_samples.npz", allow_pickle=True)
    t, q, E = z["t"], z["q"], z["E_pv"]
    nb = int(round((t.max() - t_tr) / block)); out = []
    for i in range(nb):
        m = (t > t_tr + i * block) & (t <= t_tr + (i + 1) * block)      # blocks (i*100, (i+1)*100], as in the runner
        betas, status = [], {"hot": 0, "cold": 0, "uncal": 0, "ok": 0}
        for qq, e in zip(q[m], E[m]):
            n = len(qq)
            if not np.isfinite(e) or str(n) not in CAL or not CAL[str(n)]["closure_PASS"]:
                status["uncal"] += 1; continue
            b = read_beta(CAL[str(n)]["cal"], float(e))
            if not np.isfinite(b):
                cal_e = [c["E_mean"] for c in CAL[str(n)]["cal"]]
                status["cold" if e < min(cal_e) else "hot"] += 1; continue
            if b < BETA_MIN:
                status["hot"] += 1; continue
            betas.append(b); status["ok"] += 1
        Tv = float(np.pi / np.mean(betas)) if betas else float("nan")
        out.append({"block": i, "T_v": Tv, "n_readable": len(betas), **status})
    return out


def part_A():
    out = {}
    for base in BASES:
        V = json.loads((R3 / f"A_{base}_V.json").read_text()); P = json.loads((R3 / f"A_{base}_P.json").read_text())
        tv = tv_per_block(f"A_{base}_V")
        Tb = [b["T"] for b in V["blocks"]]
        # P1
        b1 = tv[0]; readable1 = np.isfinite(b1["T_v"])
        p1 = ("hot_unreadable" if (not readable1 and b1["hot"] > b1["cold"] + b1["uncal"]) else
              ("PASS" if readable1 and b1["T_v"] > 1.5 * Tb[0] else ("FAIL" if readable1 else "not evaluable")))
        # P2
        diffs = [(i, abs(x["T_v"] - Tb[i])) for i, x in enumerate(tv) if np.isfinite(x["T_v"])]
        rho = float(spearmanr([d[0] for d in diffs], [d[1] for d in diffs])[0]) if len(diffs) >= 8 else float("nan")
        # P3 over t in [0,300): blocks 0-2, relative to P
        dEb = np.mean([V["blocks"][i]["kin_bath"] - P["blocks"][i]["kin_bath"] for i in range(3)])
        dEf = np.mean([V["blocks"][i]["E_inc"] - P["blocks"][i]["E_inc"] for i in range(3)])
        p3 = bool(abs(dEb + dEf) <= 0.3 * abs(dEf))
        # P4
        Einc_P = [b["E_inc"] for b in P["blocks"]]; p4 = bool(all(abs(x - Einc_P[0]) <= 0.15 * abs(Einc_P[0]) for x in Einc_P))
        out[base] = {"P1": p1, "T_v_block1": b1["T_v"], "T_b_block1": Tb[0], "block1_status": {k: b1[k] for k in ("ok", "hot", "cold", "uncal")},
                     "P2_spearman": rho, "P2": bool(np.isfinite(rho) and rho < -0.7) if len(diffs) >= 8 else "not evaluable", "n_readable_blocks": len(diffs),
                     "P3_dE_bath": dEb, "P3_dE_flow": dEf, "P3": p3, "P4": p4, "T_v_blocks": tv, "T_b_blocks": Tb, "n_v_blocks": [b["n_v"] for b in V["blocks"]]}
    out["P1_all"] = all(out[b]["P1"] in ("PASS", "hot_unreadable") for b in BASES)
    out["P2_two_of_three"] = sum(out[b]["P2"] is True for b in BASES) >= 2
    out["P3_all"] = all(out[b]["P3"] for b in BASES); out["P4_all"] = all(out[b]["P4"] for b in BASES)
    return out


def part_D():
    out = {}
    for base in BASES:
        D = json.loads((R3 / f"D_{base}_16pairs.json").read_text()); z = np.load(R3 / f"D_{base}_16pairs_samples.npz", allow_pickle=True)
        t = z["t"]; nv = np.array([len(qq) for qq in z["q"]], dtype=float)
        base_nv = json.loads((ROOT / f"data/generated/pgpe/sweep/{base}.json").read_text())["n_v"]
        nfree = nv - base_nv
        # power-law window search: largest window [t1, t2] with t2/t1 >= 10 where log-log fit has R^2 >= 0.95
        best = None
        ok = (nfree > 0) & (t > 0)
        tt, nn = np.log(t[ok]), np.log(nfree[ok])
        for i in range(len(tt)):
            for j in range(i + 6, len(tt)):
                if tt[j] - tt[i] < np.log(10):
                    continue
                p = np.polyfit(tt[i:j + 1], nn[i:j + 1], 1); pred = np.polyval(p, tt[i:j + 1])
                r2 = 1 - np.sum((nn[i:j + 1] - pred) ** 2) / max(np.sum((nn[i:j + 1] - nn[i:j + 1].mean()) ** 2), 1e-12)
                if r2 >= 0.95 and (best is None or (tt[j] - tt[i]) > best["span"]):
                    best = {"t1": float(np.exp(tt[i])), "t2": float(np.exp(tt[j])), "slope": float(p[0]), "z": float(-2 / p[0]) if p[0] < 0 else float("inf"), "r2": float(r2), "span": float(tt[j] - tt[i])}
        d1 = bool(best is not None and 1.5 <= best["z"] <= 2.0)
        Tb = [b["T"] for b in D["blocks"]]; Tbase = json.loads((ROOT / f"data/generated/pgpe/sweep/{base}.json").read_text())["T"]
        d2 = bool(Tb[0] < Tbase and Tb[-1] > Tb[0])
        out[base] = {"imprint_check": D.get("imprint_check"), "N_thermal": base_nv, "fit": best, "D1": d1, "D2": d2, "T_b_blocks": Tb, "T_base": Tbase,
                     "T_v_blocks": tv_per_block(f"D_{base}_16pairs"), "nv_t": [(float(a), float(b)) for a, b in zip(t, nv)]}
    out["D1_two_of_three"] = sum(out[b]["D1"] for b in BASES) >= 2; out["D2_all"] = all(out[b]["D2"] for b in BASES)
    return out


# ---- Part C: L = 128 ladder (blocks over t in [3000, 4000]; admission A4 as in analyze_sweep/analyze_r2) ----------
L64_OFFSETS = {1.00: 0.12, 1.10: 0.12, 1.20: 0.20}       # eta*K - 1 at L = 64, round-2 ladder (prereg C1)
T_BKT_64 = 0.821


def whole_from_blocks(d):
    """The round-2 'whole' record rebuilt from the per-block means (T from the block mean, not the pooled occupation)."""
    B = d["blocks"]; T = float(np.mean([b["T"] for b in B])); JL = float(np.mean([b["JL"] for b in B])); JT = float(np.mean([b["JT"] for b in B]))
    et = [b["eta"] for b in B if np.isfinite(b["eta"])]
    return {"T": T, "JL": JL, "JT": JT, "ns_over_n": 1 - JT / JL, "R_L": JL / (T * d["L"] ** 2), "R_T": JT / (T * d["L"] ** 2),
            "eta": float(np.mean(et)) if et else float("nan"), "Q": float(np.nanmean([b["Q"] for b in B])), "cond": float(np.mean([b["cond"] for b in B])),
            "n_v": float(np.mean([b["n_v"] for b in B])), "laws": [b["law"] for b in B], "drift_E": d["drift_E"]}


def ladder_rows_C(runs):
    from collections import defaultdict
    by = defaultdict(list); excluded = []
    for d in runs:
        w = whole_from_blocks(d)
        if d["drift_E"] > 1e-5:
            excluded.append({"name": d["name"], "why": "drift", "drift_E": d["drift_E"]}); continue
        if not (w["R_L"] <= 1.25 and w["R_T"] <= 1.1 * w["R_L"]):
            excluded.append({"name": d["name"], "why": "A4", "R_L": w["R_L"], "R_T": w["R_T"]}); continue
        by[round(d["e"], 3)].append(w)
    rows = []
    for e in sorted(by):
        ws = by[e]; T = float(np.mean([w["T"] for w in ws])); ns = float(np.mean([w["ns_over_n"] for w in ws]))
        et = [w["eta"] for w in ws if np.isfinite(w["eta"])]; eta = float(np.mean(et)) if et else float("nan")
        rows.append({"e": e, "n": len(ws), "T": T, "ns_over_n": ns, "K": ns * 2 * np.pi / T, "eta": eta, "eta_K_minus_1": eta * ns * 2 * np.pi / T - 1,
                     "Q": float(np.mean([w["Q"] for w in ws])), "cond": float(np.mean([w["cond"] for w in ws])), "n_v": float(np.mean([w["n_v"] for w in ws]))})
    return rows, excluded


def crossing_C(rows):
    for a, b in zip(rows, rows[1:]):
        if a["K"] >= 4 > b["K"]:
            t = (a["K"] - 4) / (a["K"] - b["K"])
            return {"between": (a["e"], b["e"]), "T_BKT": a["T"] + t * (b["T"] - a["T"]),
                    "eta": a["eta"] + t * (b["eta"] - a["eta"]) if np.isfinite(a["eta"]) and np.isfinite(b["eta"]) else float("nan")}
    return None


def part_C(runs=None):
    runs = runs if runs is not None else [json.loads(f.read_text()) for f in sorted(R3.glob("C_L128_*.json"))]
    rows, excluded = ladder_rows_C(runs); cr = crossing_C(rows)
    off128 = [(r["e"], r["eta_K_minus_1"]) for r in rows if r["K"] > 4 and np.isfinite(r["eta"]) and r["e"] in L64_OFFSETS]
    off64 = [(e, L64_OFFSETS[e]) for e, _ in off128]
    ratio = float(np.mean([o for _, o in off128]) / np.mean([o for _, o in off64])) if off128 else float("nan")
    c1 = bool(off128) and 0.6 <= ratio <= 1.0
    c2 = ("not bracketed" if cr is None else bool(cr["T_BKT"] <= T_BKT_64))
    return {"rows": rows, "excluded": excluded, "n_runs": len(runs), "crossing_L128": cr, "T_BKT_64": T_BKT_64,
            "C1_offsets_L128": off128, "C1_offsets_L64": off64, "C1_ratio": ratio, "C1": c1, "C2": c2,
            "note": "T per run is the mean of the block thermometer readings (round 2 used the pooled occupation); offsets use K > 4 rows only, as in round 2 L3"}


if __name__ == "__main__":
    v = {}
    if (R3 / "A_e0.60_s11_t4000_V.json").exists(): v["A"] = part_A()
    if (R3 / "D_e0.60_s11_t4000_16pairs.json").exists(): v["D"] = part_D()
    if list(R3.glob("C_L128_*.json")): v["C"] = part_C()
    (ROOT / "data/generated/pgpe/r3_verdicts.json").write_text(json.dumps(v, indent=1, default=float))
    if "C" in v:
        print("C", json.dumps({k: x for k, x in v["C"].items() if k != "rows"}, default=float)); [print("C row", r) for r in v["C"]["rows"]]
    for part in [p for p in v if p != "C"]:
        for base in BASES:
            r = v[part][base]; print(part, base, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in r.items() if k not in ("T_v_blocks", "T_b_blocks", "n_v_blocks", "nv_t", "fit")}, r.get("fit"))
        print(part, {k: x for k, x in v[part].items() if k not in BASES})
