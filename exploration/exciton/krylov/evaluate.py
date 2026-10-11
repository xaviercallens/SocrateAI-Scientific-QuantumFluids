#!/usr/bin/env python3
"""Gate evaluation for PREREG.md (K-a ... K-e). Reads results/*.jsonl, writes results/summary.json and prints a table."""
import json, os, math, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "results")
REC = os.path.join(HERE, "..", "results", "phase3")


def rows(name):
    p = os.path.join(R, name)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def by_tag(name):
    return {d["tag"]: d for d in rows(name)}


def jload(path):
    return json.load(open(path)) if os.path.exists(path) else None


out = {}

# ---- K-a1 ---------------------------------------------------------------------------------------------------------
ka1 = by_tag("ka1.jsonl")
rec4000 = [json.loads(l) for l in open(os.path.join(REC, "d_V0.5.jsonl"))][0]
rec16000 = [json.loads(l) for l in open(os.path.join(REC, "exploratory", "d_T16000.jsonl"))][0]


def compare(kr, rec, tol):
    res = {}
    ok = True
    for k, (kind, t) in tol.items():
        d = abs(kr[k] - rec[k])
        if kind == "rel":
            d /= abs(rec[k])
        res[k] = {"kr": kr[k], "rec": rec[k], "diff": d, "tol": t, "pass": d <= t}
        ok &= d <= t
    return ok, res


tol4000 = {"omega": ("abs", 1e-6), "n_center": ("abs", 1e-4), "n_corner": ("abs", 1e-4), "std_n": ("abs", 1e-5),
           "mean_n": ("rel", 1e-6), "mean_nr": ("rel", 1e-6)}
tol16000 = {"omega": ("abs", 1e-7), "n_center": ("abs", 1e-5), "n_corner": ("abs", 1e-5), "std_n": ("abs", 1e-5),
            "mean_n": ("rel", 1e-7), "mean_nr": ("rel", 1e-7)}
if "Ka1_t4000" in ka1:
    ok, res = compare(ka1["Ka1_t4000"], rec4000, tol4000)
    out["K-a1_t4000_vs_record"] = {"pass": ok, "detail": res, "resid_kr": ka1["Ka1_t4000"]["resid_rel"], "resid_rec": rec4000["resid_rel"],
                                   "cpu_s": ka1["Ka1_t4000"]["cpu_s"], "steps": ka1["Ka1_t4000"]["steps"]}
if "Ka1_cvode_t4000" in ka1:
    ok, res = compare(ka1["Ka1_cvode_t4000"], rec4000, tol4000)
    out["K-a1_cvode_rerun_vs_record"] = {"pass": ok, "detail": res}
c = jload(os.path.join(R, "ka1_t4000_cmp.json"))
if c:
    out["K-a1_fullstate_kr_vs_cvode"] = {"rel_l2_phase_aligned": c["rel_l2_phase_aligned"], "rel_l2": c["rel_l2"], "pass": c["rel_l2_phase_aligned"] <= 1e-5}
if "Ka1_t16000_rtol1e-4" in ka1:
    ok, res = compare(ka1["Ka1_t16000_rtol1e-4"], rec16000, tol16000)
    out["K-a1_t16000_vs_record"] = {"pass": ok, "detail": res, "resid_kr": ka1["Ka1_t16000_rtol1e-4"]["resid_rel"],
                                    "resid_rec": rec16000["resid_rel"], "cpu_s": ka1["Ka1_t16000_rtol1e-4"]["cpu_s"]}

# ---- K-a2 ---------------------------------------------------------------------------------------------------------
ka2 = by_tag("ka2.jsonl")
if "Ka2_cvode" in ka2:
    cv = ka2["Ka2_cvode"]
    res = {"cvode_cpu_s": cv["cpu_s"], "cvode_steps": cv.get("cvode_steps")}
    errs = []
    for rt in ["1e-6", "1e-7", "1e-8"]:
        t = "Ka2_kr_rtol" + rt
        if t in ka2:
            k = ka2[t]
            c = jload(os.path.join(R, f"ka2_cmp_{rt}.json"))
            res[rt] = {"rel_l2": c["rel_l2"], "d_omega": abs(k["omega"] - cv["omega"]), "d_n_center": abs(k["n_center"] - cv["n_center"]),
                       "cpu_s": k["cpu_s"], "steps": k["steps"]}
            errs.append(c["rel_l2"])
    g = res.get("1e-7")
    res["pass"] = bool(g and g["rel_l2"] <= 1e-4 and g["d_omega"] <= 1e-5 and g["d_n_center"] <= 1e-4)
    res["monotone"] = all(errs[i] > errs[i + 1] for i in range(len(errs) - 1)) if len(errs) == 3 else None
    out["K-a2"] = res

# ---- K-b ----------------------------------------------------------------------------------------------------------
hs = [0.2, 0.1, 0.05, 0.025, 0.0125]
e = []
for h in hs:
    c = jload(os.path.join(R, f"kb_cmp_h{h}.json"))
    e.append(c["rel_l2"] if c else None)
if all(x is not None for x in e):
    ratios = [e[i] / e[i + 1] for i in range(len(e) - 1)]
    out["K-b"] = {"h": hs, "rel_l2": e, "ratios": ratios, "pass": all(3 <= r <= 5 for r in ratios[-3:])}

# ---- K-d ----------------------------------------------------------------------------------------------------------
kd = by_tag("kd.jsonl")
if "Kd_block" in kd:
    d = {}
    for tag in ["Kd_block", "Kd_badsign", "Kd_precnone", "Kd_prekin", "Kd_bugrhs", "Kd_bugjac", "Kd_fd"]:
        if tag not in kd:
            continue
        k = kd[tag]
        cc = jload(os.path.join(R, f"{tag}_cmp_cvode.json"))
        cb = jload(os.path.join(R, f"{tag}_cmp_block.json"))
        d[tag] = {"gmres": k.get("gmres"), "newton": k.get("newton"), "steps": k.get("steps"), "cpu_s": k["cpu_s"],
                  "rel_l2_vs_cvode": cc["rel_l2"] if cc else None, "rel_l2_vs_block": cb["rel_l2"] if cb else None, "error": k["error"]}
    gb = d["Kd_block"]["gmres"]
    if "Kd_badsign" in d:
        b = d["Kd_badsign"]
        d["K-d1_pass"] = bool(b["error"] is None and b["rel_l2_vs_block"] <= 1e-6 and b["gmres"] >= 1.5 * gb)
    if "Kd_bugrhs" in d:
        b = d["Kd_bugrhs"]
        d["K-d2_pass"] = bool(b["rel_l2_vs_cvode"] is not None and b["rel_l2_vs_cvode"] > 1e-2)
    if "Kd_bugjac" in d:
        b = d["Kd_bugjac"]
        d["K-d3_pass"] = bool(b["error"] is not None or (b["rel_l2_vs_block"] is not None and b["rel_l2_vs_block"] <= 1e-6))
    if "Kd_fd" in d:
        b = d["Kd_fd"]
        d["K-d4_pass"] = bool(b["error"] is None and b["rel_l2_vs_block"] <= 1e-6)
    out["K-d"] = d

# ---- K-e ----------------------------------------------------------------------------------------------------------
ke = by_tag("ke.jsonl")
rev16 = {0.25: (0.046, 5.84), 0.5: (0.077, 2.38), 1.0: (0.107, 0.10)}
rev8 = {0.25: (0.04878, 7.068), 0.5: (0.08761, 4.581), 1.0: (0.14212, 1.493)}
table = []
for tag, d in ke.items():
    table.append({"tag": tag, "M": d["M"], "L": d["L"], "sigma": d["sigma"], "V0": d["V0"], "seed": d["seed"], "rtol": d["rtol"],
                  "shift": d["shift"], "n_center": d["n_center"], "n_corner": d["n_corner"], "mean_n": d["mean_n"], "std_n": d["std_n"],
                  "resid": d["resid_rel"], "t_reached": d["t_reached"], "steps": d["steps"], "cpu_s": d["cpu_s"], "error": d["error"],
                  "box_avg": d["V0"] * 2 * math.pi * d["sigma"] ** 2 / d["L"] ** 2})
out["K-e_table"] = table
k3 = {}
for v in (0.25, 0.5, 1.0):
    t = f"Ke_G16_V{v}_s1"
    if t in ke:
        s, nc = rev16[v]
        tolnc = 0.005 if v == 1.0 else 0.01
        k3[f"G16_V{v}"] = {"shift": ke[t]["shift"], "ref_shift": s, "d_shift": abs(ke[t]["shift"] - s), "n_center": ke[t]["n_center"], "ref_nc": nc,
                           "d_nc": abs(ke[t]["n_center"] - nc), "pass": abs(ke[t]["shift"] - s) <= 6e-4 and abs(ke[t]["n_center"] - nc) <= tolnc}
    t = f"Ke_G8_V{v}_s1"
    if t in ke:
        s, nc = rev8[v]
        k3[f"G8_V{v}"] = {"shift": ke[t]["shift"], "ref_shift": s, "d_shift": abs(ke[t]["shift"] - s), "n_center": ke[t]["n_center"], "ref_nc": nc,
                          "d_nc": abs(ke[t]["n_center"] - nc), "pass": abs(ke[t]["shift"] - s) <= 2e-4 and abs(ke[t]["n_center"] - nc) <= 5e-3}
out["K-a3"] = k3
a, b = ke.get("Ke_G16_V0.5_s1"), ke.get("Ke0_G16_V0.5_s1_rtol1e-6")
if a and b:
    out["K-e0"] = {"d_shift": abs(a["shift"] - b["shift"]), "d_nc": abs(a["n_center"] - b["n_center"]),
                   "pass": abs(a["shift"] - b["shift"]) <= 1e-7 and abs(a["n_center"] - b["n_center"]) <= 1e-6,
                   "cpu_rtol1e-4": a["cpu_s"], "cpu_rtol1e-6": b["cpu_s"]}
s = [ke[t]["shift"] for t in ("Ke_G16_V0.5_s1", "Ke_G16_V0.5_s2", "Ke_G16_V0.5_s3") if t in ke]
if len(s) == 3:
    out["K-e1_seed_independence"] = {"shifts": s, "spread": max(s) - min(s), "pass": max(s) - min(s) <= 1e-6}
out["K-e1_resid_gate"] = {t: d["resid_rel"] < 1e-7 for t, d in ke.items()}

json.dump(out, open(os.path.join(R, "summary.json"), "w"), indent=1)
print(json.dumps(out, indent=1)[:20000])
