#!/usr/bin/env python3
"""Evaluate the Phase 3 gates exactly as registered (docs/designs/EXCITON_FLUID_PHASE3_PREREG.md).
Usage: phase3_summarise.py <results_dir> <summary.json>"""
import json, sys, os
import numpy as np
R = sys.argv[1]; out = sys.argv[2]
ref = json.load(open(f"{R}/reference.json"))
import glob
def jl(name):
    """name like 'a.jsonl': reads a.jsonl and every a_*.jsonl (parallel shards)"""
    stem = name[:-6]
    out = []
    for p in sorted(glob.glob(f"{R}/{stem}.jsonl") + glob.glob(f"{R}/{stem}_*.jsonl")):
        out += [json.loads(l) for l in open(p) if l.strip()]
    return out
res = {}; N = 768
def rel(a, b): return abs(a - b) / abs(b)

# D-a
a = jl("a.jsonl"); ab = [r for r in a if r["case"] == "above"]; be = [r for r in a if r["case"] == "below"]
da_above = [dict(seed=r["seed"], n=rel(r["mean_n"], 10.0) <= 1e-6, nr=rel(r["mean_nr"], 0.1) <= 1e-6,
                 std=r["std_n"] <= 1e-6 * r["mean_n"], om=abs(r["omega"] - 0.5) <= 1e-6 * 0.5, err=r["error"]) for r in ab]
da_below = [dict(seed=r["seed"], psi=r["max_psi"] <= 1e-6, nr=rel(r["mean_nr"], 0.08) <= 1e-8, err=r["error"]) for r in be]
res["D-a"] = dict(above=da_above, below=da_below,
                  worst=dict(n=max((rel(r["mean_n"], 10.0) for r in ab), default=None), nr=max((rel(r["mean_nr"], 0.1) for r in ab), default=None),
                             om=max((abs(r["omega"] - 0.5) for r in ab), default=None), max_psi_below=max((r["max_psi"] for r in be), default=None),
                             nr_below=max((rel(r["mean_nr"], 0.08) for r in be), default=None)),
                  PASS=bool(ab) and bool(be) and all(all(v for k, v in d.items() if k not in ("seed", "err")) and d["err"] is None for d in da_above + da_below))
# D-b
jp = f"{R}/jac_uniform.f64"
if os.path.exists(jp):
    J = np.fromfile(jp, dtype="<f8").reshape(N, N).T  # file is column-major: column c written as rows r
    ev = np.linalg.eigvals(J)
    refev = [complex(z[0], z[1]) for s in ref["spectrum"] for z in s["ev"]]
    key = lambda z: (round(z.real, 6), round(z.imag, 6))
    # match by greedy nearest neighbour (sorting by rounded keys is fragile for degenerate pairs)
    ev_s = sorted(ev, key=lambda z: (z.real, z.imag)); rf = sorted(refev, key=lambda z: (z.real, z.imag))
    d_sorted = max(abs(x - y) for x, y in zip(ev_s, rf))
    # symmetric matching
    rem = list(ev); worst = 0.0
    for z in refev:
        j = int(np.argmin([abs(z - w) for w in rem])); worst = max(worst, abs(z - rem[j])); rem.pop(j)
    res["D-b"] = dict(n_eigs=len(ev), n_ref=len(refev), max_match_error=worst, max_sorted_error=d_sorted, max_re=float(max(e.real for e in ev)), PASS=bool(worst <= 1e-6 and len(ev) == len(refev)))
else:
    res["D-b"] = dict(PASS=False, note="no jacobian")
# D-c
c = json.load(open(f"{R}/c.json")) if os.path.exists(f"{R}/c.json") else None
res["D-c"] = dict(**(c or {}), PASS=bool(c and c["error"] is None and c["norm_rel"] < 1e-6 and c["energy_rel"] < 1e-6))
# D-d
d = jl("d.jsonl"); sweep = {}
for v0 in sorted({r["V0"] for r in d}):
    rs = [r for r in d if r["V0"] == v0]
    sweep[v0] = dict(n=len(rs), omega=[r["omega"] for r in rs], budget_max=max(r["budget_rel"] for r in rs), resid_max=max(r["resid_rel"] for r in rs),
                     n_center=[r["n_center"] for r in rs], n_corner=[r["n_corner"] for r in rs], max_j=[r["max_j"] for r in rs],
                     errors=[r["error"] for r in rs if r["error"]])
okI = all(s["budget_max"] <= 1e-8 for s in sweep.values()) if sweep else False
okII = all(s["resid_max"] <= 1e-7 for s in sweep.values()) if sweep else False
om = {v: np.median(s["omega"]) for v, s in sweep.items()}
hyp = bool(sweep) and all(0 < om[v] - om[0.0] < v for v in om if v > 0) and all(om[a_] < om[b_] for a_, b_ in zip(sorted(om), sorted(om)[1:]))
# max real part of the rotating frame linearisation about the numerical steady states
lam = {}
for v0 in sweep:
    p = f"{R}/jac_V{int(round(v0*100))}.f64"
    if os.path.exists(p):
        raw = np.fromfile(p, dtype="<f8"); Nv = int(round(np.sqrt(raw.size)))
        Jv = raw.reshape(Nv, Nv).T
        e = np.linalg.eigvals(Jv); lam[v0] = float(max(x.real for x in e if abs(x) > 1e-9 or True))
res["D-d"] = dict(sweep={str(k): v for k, v in sweep.items()}, budget_ok=okI, stationary_ok=okII, omega_median={str(k): float(v) for k, v in om.items()},
                  hypothesis_iii=hyp, max_re_lambda=lam, PASS_i_ii=bool(okI and okII and all(not s["errors"] for s in sweep.values())), PASS_iii=hyp)
# D-e
e = jl("e.jsonl"); one = {r["h"]: r for r in e if r["kind"] == "one_step"}
traj = next((r for r in e if r["kind"] == "trajectory"), None)
okh = lambda h: h in one and one[h]["status"] == "ok" and one[h]["finite"]
badh = lambda h: h in one and (one[h]["status"] == "error")
silent = [h for h in one if one[h]["status"] == "ok" and not one[h]["finite"]]
res["D-e"] = dict(one_step={str(h): (r["status"], r["finite"]) for h, r in one.items()}, silent_nonfinite_at=silent, trajectory=traj,
                  PASS_threshold=bool(all(okh(h) for h in (0.005, 0.01, 0.0125)) and all(badh(h) for h in (0.02, 0.05))),
                  PASS_trajectory=bool(traj and traj.get("diff_rel", 1) <= 1e-3 and traj.get("finite", False)))
# D-f
f = jl("f.jsonl"); er = [r.get("err") for r in f]
ratios = [er[i] / er[i + 1] for i in range(len(er) - 1)] if len(er) == 3 and None not in er else None
res["D-f"] = dict(errors=er, ratios=ratios, PASS=bool(ratios and all(3 <= r_ <= 5 for r_ in ratios)))
# D-g (amendment A4: per-seed log lines of the first three seeds)
import re
gl = []
lp = f"{R}/run_log_g.txt"
if os.path.exists(lp):
    for l in open(lp):
        m = re.match(r"above seed (\d+): n=([0-9.eE+-]+) nR=([0-9.eE+-]+) omega=([0-9.eE+-]+) budget=([0-9.eE+-]+)", l)
        if m: gl.append(dict(seed=int(m[1]), n=float(m[2]), nr=float(m[3]), omega=float(m[4]), budget=float(m[5])))
res["D-g"] = dict(n_seeds=len(gl), runs=gl, violates_D_a=bool(gl) and all(rel(r["n"], 10.0) > 1e-6 for r in gl),
                  violates_budget=bool(gl) and all(r["budget"] > 1e-8 for r in gl))
res["D-g"]["PASS"] = bool(res["D-g"]["violates_D_a"] and res["D-g"]["violates_budget"])
# exploratory (not gates): continuation and tolerance variants of D-d, seed 1, V0 = 0.5
ex = []
for p_ in sorted(glob.glob(f"{R}/exploratory/d_*.jsonl")):
    for l in open(p_):
        r = json.loads(l); ex.append(dict(file=os.path.basename(p_), omega=r["omega"], resid_rel=r["resid_rel"], budget_rel=r["budget_rel"], n_center=r["n_center"], steps=r["steps"]))
res["exploratory"] = ex
json.dump(res, open(out, "w"), indent=1, default=float)
for k, v in res.items():
    if isinstance(v, dict): print(k, {kk: vv for kk, vv in v.items() if kk.startswith("PASS")})
