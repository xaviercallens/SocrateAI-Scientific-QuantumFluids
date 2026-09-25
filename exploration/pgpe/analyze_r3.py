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
BASES = ["e0.60_s11_t4000", "e0.90_s11_t4000", "e0.90_s12_t4000"]
BETA_MIN = 0.3


def tv_per_block(name, t_tr=0.0, block=100.0):
    """Per block: T_v (phys) from readable samples, or a status string."""
    z = np.load(R3 / f"{name}_samples.npz", allow_pickle=True)
    t, q, E = z["t"], z["q"], z["E_pv"]
    nb = int(np.ceil((t.max() - t_tr + 1e-9) / block)); out = []
    for i in range(nb):
        m = (t >= t_tr + i * block) & (t < t_tr + (i + 1) * block)
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


if __name__ == "__main__":
    v = {}
    if (R3 / "A_e0.60_s11_t4000_V.json").exists(): v["A"] = part_A()
    if (R3 / "D_e0.60_s11_t4000_16pairs.json").exists(): v["D"] = part_D()
    (ROOT / "data/generated/pgpe/r3_verdicts.json").write_text(json.dumps(v, indent=1, default=float))
    for part in v:
        for base in BASES:
            r = v[part][base]; print(part, base, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in r.items() if k not in ("T_v_blocks", "T_b_blocks", "n_v_blocks", "nv_t", "fit")}, r.get("fit"))
        print(part, {k: x for k, x in v[part].items() if k not in BASES})
