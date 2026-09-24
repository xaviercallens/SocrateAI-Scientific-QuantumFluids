#!/usr/bin/env python3
"""Apply the pre-registered criteria of PGPE_BKT_PREREG.md (B1-B5, amendment A2: D1-D3, T1) to the sweep JSONs.
Seed-means per energy; no criterion is tuned here. Writes data/generated/pgpe/sweep_verdicts.json.

Run: .venv/bin/python exploration/pgpe/analyze_sweep.py
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SW = ROOT / "data" / "generated" / "pgpe" / "sweep"
LN380 = float(np.log(380.0))


def sum_rules(d):
    """Amendment A3: R_L = <|J_L|^2>/(nTA) and R_T = <|J_T|^2>/(nTA) over the three smallest shells (n = 1)."""
    nTA = d["T"] * d["L"] ** 2
    return float(np.mean(list(d["JL"].values())) / nTA), float(np.mean(list(d["JT"].values())) / nTA)


def admitted(d):
    RL, RT = sum_rules(d)
    return 0.8 <= RL <= 1.25 and RT <= 1.1


def load():
    """One record per (e, seed): the longest run available (A3 extensions supersede the t=1500 run)."""
    best = {}
    for f in sorted(SW.glob("e*_s*.json")):
        if "quick" in f.name:
            continue
        d = json.loads(f.read_text()); d.setdefault("t_end", 1500.0)
        d["R_L"], d["R_T"] = sum_rules(d); d["admitted"] = admitted(d); d["file"] = f.name
        k = (d["e"], d["seed"])
        if k not in best or d["t_end"] > best[k]["t_end"]:
            best[k] = d
    by_e, excluded = defaultdict(list), []
    for (e, sd), d in sorted(best.items()):
        (by_e[e] if d["admitted"] else excluded).append(d if d["admitted"] else
                                                        {"e": e, "seed": sd, "t_end": d["t_end"], "R_L": d["R_L"], "R_T": d["R_T"]})
    return dict(sorted(by_e.items())), excluded


def row(runs):
    m = lambda k: float(np.nanmean([r[k] for r in runs]))
    T = m("T"); ns = m("ns_over_n")
    return {"e": runs[0]["e"], "n_seeds": len(runs), "T": T, "T_sd": float(np.std([r["T"] for r in runs])),
            "ns_over_n": ns, "ns_lam2": ns * 2 * np.pi / T, "n_lam2": 2 * np.pi / T,
            "eta": float(np.mean([r["g1"]["eta"] for r in runs])), "ell": float(np.mean([r["g1"]["ell"] for r in runs])),
            "alg_wins": int(sum(r["g1"]["res_alg"] < r["g1"]["res_exp"] for r in runs)),
            "f_free": m("f_free"), "Q": m("Q"), "n_v": m("n_v"), "cond": m("cond_frac"),
            "stationary": all(r["stationary_5pct"] for r in runs), "thermo10": all(r["thermometer_10pct"] for r in runs),
            "L": runs[0]["L"]}


def crossing(x, y, level):
    """First index i with y[i] >= level > y[i+1]; returns (i, interpolated x) or (None, nan)."""
    for i in range(len(y) - 1):
        if y[i] >= level > y[i + 1]:
            t = (y[i] - level) / (y[i] - y[i + 1])
            return i, float(x[i] + t * (x[i + 1] - x[i]))
    return None, float("nan")


def main():
    by_e, excluded = load()
    R = [row(v) for v in by_e.values()]
    E = [r["e"] for r in R]; T = np.array([r["T"] for r in R]); K = np.array([r["ns_lam2"] for r in R])
    eta = np.array([r["eta"] for r in R]); alg = [2 * r["alg_wins"] > r["n_seeds"] for r in R]
    out = {"rows": R, "excluded_by_A3": excluded, "verdicts": {}}
    v = out["verdicts"]
    # K7 health over the sweep
    v["thermometer_stationary_all"] = all(r["stationary"] for r in R)
    v["thermometer_10pct_all"] = all(r["thermo10"] for r in R)
    # B1: both regimes, crossover index
    ix_x = next((i for i, a in enumerate(alg) if not a), None)
    v["B1"] = {"low_T_algebraic_eta_lt_quarter": bool(alg[0] and eta[0] < 0.25),
               "high_T_exponential_ell_lt_L4": bool((not alg[-1]) and R[-1]["ell"] < R[-1]["L"] / 4),
               "T_cross_index": ix_x, "T_cross": float(T[ix_x]) if ix_x is not None else float("nan")}
    v["B1"]["both_regimes"] = v["B1"]["low_T_algebraic_eta_lt_quarter"] and v["B1"]["high_T_exponential_ell_lt_L4"]
    # B2
    ff = [r["f_free"] for r in R]
    i_ff = next((i for i, f in enumerate(ff) if f > 0.5), None)
    v["B2"] = {"f_free_low": ff[0], "first_index_gt_half": i_ff,
               "PASS": bool(ff[0] < 0.1 and i_ff is not None and ix_x is not None and abs(i_ff - ix_x) <= 1)}
    # B3: n_s lambda^2 = 4 crossing (interpolated in T)
    i_c, T_bkt = crossing(T, K, 4.0)
    v["B3"] = {"crossing_between_indices": i_c, "T_BKT": T_bkt,
               "PASS": bool(i_c is not None and ix_x is not None and min(abs(i_c - ix_x), abs(i_c + 1 - ix_x)) <= 1)}
    # B4: n lambda^2 at T_BKT vs ln 380
    nl2 = 2 * np.pi / T_bkt if np.isfinite(T_bkt) else float("nan")
    v["B4"] = {"n_lam2_at_T_BKT": nl2, "ln380": LN380, "rel_dev": abs(nl2 - LN380) / LN380 if np.isfinite(nl2) else float("nan"),
               "PASS": bool(np.isfinite(nl2) and abs(nl2 - LN380) / LN380 <= 0.20)}
    # D1: eta * n_s lambda^2 = 1 in the algebraic regime with n_s lambda^2 > 4
    d1 = [(E[i], float(eta[i] * K[i])) for i in range(len(R)) if alg[i] and K[i] > 4]
    v["D1"] = {"products": d1, "PASS": bool(d1) and all(0.75 <= p <= 1.33 for _, p in d1)}
    # D2: eta interpolated at the crossing
    if i_c is not None:
        t = (K[i_c] - 4.0) / (K[i_c] - K[i_c + 1]); eta_c = float(eta[i_c] + t * (eta[i_c + 1] - eta[i_c]))
    else:
        eta_c = float("nan")
    v["D2"] = {"eta_at_T_BKT": eta_c, "PASS": bool(np.isfinite(eta_c) and abs(eta_c - 0.25) <= 0.08)}
    # D3: last algebraic energy has eta < 0.5
    last_alg = max((i for i, a in enumerate(alg) if a), default=None)
    v["D3"] = {"last_alg_index": last_alg, "eta_there": float(eta[last_alg]) if last_alg is not None else float("nan"),
               "PASS": bool(last_alg is not None and eta[last_alg] < 0.5)}
    # T1: dipole matching ratio
    Q = np.array([r["Q"] for r in R]); nv = np.array([r["n_v"] for r in R])
    i_lo = next((i for i in range(len(R)) if nv[i] >= 4 and np.isfinite(Q[i])), None)
    dQ = np.diff(Q); j = int(np.nanargmax(dQ)) if np.any(np.isfinite(dQ)) else None
    v["T1"] = {"Q_low": float(Q[i_lo]) if i_lo is not None else float("nan"), "Q_high": float(Q[-1]), "max_rise_step": j,
               "part1_Qlow_le_0.5": bool(i_lo is not None and Q[i_lo] <= 0.5),
               "part2_Qhigh_ge_0.8": bool(Q[-1] >= 0.8),
               "part3_rise_at_T_BKT": bool(j is not None and i_c is not None and abs(j - i_c) <= 1)}
    (ROOT / "data" / "generated" / "pgpe" / "sweep_verdicts.json").write_text(json.dumps(out, indent=1, default=float))
    print(f"{'e':>5} {'T':>6} {'ns/n':>6} {'nsl2':>6} {'eta':>6} {'alg':>3} {'ell':>6} {'f_free':>6} {'Q':>5} {'n_v':>7} {'cond':>6} st th")
    for r in R:
        print(f"{r['e']:5.2f} {r['T']:6.3f} {r['ns_over_n']:6.3f} {r['ns_lam2']:6.2f} {r['eta']:6.3f} {r['alg_wins']:3d} {r['ell']:6.1f} "
              f"{r['f_free']:6.2f} {r['Q']:5.2f} {r['n_v']:7.1f} {r['cond']:6.3f} {int(r['stationary'])}  {int(r['thermo10'])}")
    print("excluded by A3 (not equilibrated):", json.dumps(excluded, default=float))
    print(json.dumps(v, indent=1, default=float))


if __name__ == "__main__":
    main()
