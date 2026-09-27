#!/usr/bin/env python3
"""Verdicts of docs/designs/PGPE_R4_PREREG.md Part B from data/generated/pgpe/r4/*.json.
Run: .venv/bin/python exploration/pgpe/analyze_r4.py -> data/generated/pgpe/r4_verdicts.json"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]; R4 = ROOT / "data/generated/pgpe/r4"
BASES = ["e0.60_s11_t4000", "e0.90_s11_t4000", "e0.90_s12_t4000"]
ARMS = ["0", "V3", "P16", "V3P16"]


def load(base, arm):
    return json.loads((R4 / f"B_{base}_{arm}.json").read_text())


def window_mean(d, key, t_lo, t_hi):
    xs = [e[key] for e in d["extra"] if t_lo <= e["t"] <= t_hi]
    return float(np.mean(xs)) if xs else float("nan")


def window_series(d, key, t_lo, t_hi):
    return [(e["t"], e[key]) for e in d["extra"] if t_lo <= e["t"] <= t_hi]


def frac_Wx_equals(d, w0, t_lo, t_hi):
    xs = [e["W"][0] for e in d["extra"] if t_lo <= e["t"] <= t_hi]
    return float(np.mean([1.0 if x == w0 else 0.0 for x in xs])) if xs else float("nan")


def part_B():
    out = {}
    S0, SV3, SP16, SV3P16 = {}, {}, {}, {}
    for base in BASES:
        d = {arm: load(base, arm) for arm in ARMS}
        s0 = window_mean(d["0"], "S_band", 500, 1500)
        sV3 = window_mean(d["V3"], "S_band", 500, 1500)
        s0_early = window_mean(d["0"], "S_band", 0, 300)
        sP16_early = window_mean(d["P16"], "S_band", 0, 300)
        sP16_e = sP16_early
        sV3P16_early = window_mean(d["V3P16"], "S_band", 0, 300)
        b1_ratio = sV3 / s0 - 1
        b2_ratio = sP16_e / s0_early - 1
        b4_ratio = sV3P16_early / sP16_e - 1
        b1 = bool(abs(b1_ratio) <= 0.15)
        b2 = bool(b2_ratio >= 0.30)
        b4 = bool(abs(b4_ratio) <= 0.15)
        # B3
        fWx_V3 = frac_Wx_equals(d["V3"], 3, 500, 1500)
        fWx_V3P16 = frac_Wx_equals(d["V3P16"], 3, 500, 1500)
        fWx_0 = frac_Wx_equals(d["0"], 0, 500, 1500)
        fWx_P16 = frac_Wx_equals(d["P16"], 0, 500, 1500)
        fK_V3 = window_mean(d["V3"], "f_K", 500, 1500)
        e090 = "e0.90" in base
        b3 = None
        if e090:
            b3 = bool(fWx_V3 >= 0.95 and fWx_V3P16 >= 0.95 and fWx_0 >= 0.95 and fWx_P16 >= 0.95 and fK_V3 >= 0.15)
        out[base] = {
            "S_band_0_late": s0, "S_band_V3_late": sV3, "B1_ratio": b1_ratio, "B1": b1,
            "S_band_0_early": s0_early, "S_band_P16_early": sP16_early, "B2_ratio": b2_ratio, "B2": b2,
            "S_band_V3P16_early": sV3P16_early, "B4_ratio": b4_ratio, "B4": b4,
            "W_x_frac_V3": fWx_V3, "W_x_frac_V3P16": fWx_V3P16, "W_x_frac_0": fWx_0, "W_x_frac_P16": fWx_P16,
            "f_K_V3": fK_V3, "B3": b3,
            "N_v_P16": [(e["t"], None) for e in []],  # filled below from blocks
        }
        # B5 reported series
        nv_P16 = [(b["t0"], b["n_v"]) for b in d["P16"]["blocks"]]
        nv_V3P16 = [(b["t0"], b["n_v"]) for b in d["V3P16"]["blocks"]]
        Wx_V3P16_series = window_series(d["V3P16"], "W", 0, 1500)
        Tb_series = {arm: [(b["t0"], b["T"]) for b in d[arm]["blocks"]] for arm in ARMS}
        out[base]["B5"] = {"N_v_P16": nv_P16, "N_v_V3P16": nv_V3P16,
                            "Wx_V3P16_first_last": (Wx_V3P16_series[0], Wx_V3P16_series[-1]) if Wx_V3P16_series else None,
                            "T_b_series": Tb_series, "drift_E": {arm: d[arm]["drift_E"] for arm in ARMS}}
    out["B1_all"] = all(out[b]["B1"] for b in BASES)
    out["B2_all"] = all(out[b]["B2"] for b in BASES)
    out["B4_all"] = all(out[b]["B4"] for b in BASES)
    e090_bases = [b for b in BASES if "e0.90" in b]
    out["B3_all_e090"] = all(out[b]["B3"] for b in e090_bases)
    return out


if __name__ == "__main__":
    v = part_B()
    (ROOT / "data/generated/pgpe/r4_verdicts.json").write_text(json.dumps(v, indent=1, default=float))
    for base in BASES:
        r = v[base]
        print(base, {k: (round(x, 4) if isinstance(x, float) else x) for k, x in r.items() if k != "B5"})
    print("SUMMARY", {k: v[k] for k in ("B1_all", "B2_all", "B4_all", "B3_all_e090")})
