"""Analysis of PGPE_VORTEX_SCATTERING_PREREG.md: sigma_par(k), sigma_perp(k), gates KA1-KA4, predictions P1, P2, P4, P5.
    .venv/bin/python exploration/pgpe/analyze_wave_scan.py   -> data/generated/pgpe/wave_scattering/scan/wave_scan_results.json"""
import glob, json, re, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / "data/generated/pgpe/wave_scattering/scan"; L = 64.0; KAPPA = 2 * np.pi
sys.path.insert(0, str(ROOT / "exploration/pgpe"))
from predict_friction_from_sigma import integral
uw = lambda a: np.unwrap(a * 2 * np.pi / L) * L / (2 * np.pi)


def slopes(f, t0=50.0):
    z = np.load(f); m = json.loads(str(z["meta"])); t = z["t"]; R = z["R"]
    if m["ended"] != "t_max" or len(R) < 100:
        return None
    x0, x1, y0, y1 = uw(R[:, 0, 0]), uw(R[:, 1, 0]), uw(R[:, 0, 1]), uw(R[:, 1, 1]); dx = x0 - x1; yc = 0.5 * (y0 + y1); msk = t >= t0
    f_ = lambda v: float(np.polyfit(t[msk], v[msk], 1)[0])
    return dict(sdx=f_(dx), syc=f_(yc), j=m["j"], k=m["k"], eps=m["eps"], dir=m["dir"], d_change=float(dx[-1] - dx[0]), meta=m)


def main():
    c = slopes(OUT / "WS_control.npz")
    if c is None:
        sys.exit("control missing")
    res = dict(control=dict(sdx=c["sdx"], syc=c["syc"], d_change=c["d_change"]), KA1=bool(abs(c["sdx"]) <= 3e-5 and abs(c["d_change"]) <= 0.02), points=[], KA3={})
    by = {}
    for f in sorted(glob.glob(str(OUT / "WS_m*_av*.npz"))):
        mm = re.match(r".*WS_m(\d+)_([pm])_av([\d.]+)\.npz", f); m, d, av = int(mm.group(1)), mm.group(2), float(mm.group(3))
        s = slopes(f)
        if s is None:
            print("dropped (vortex lost or short):", Path(f).name); continue
        s["dsdx"] = s["sdx"] - c["sdx"]; s["dsyc"] = s["syc"] - c["syc"]; by.setdefault((m, av), {})[d] = s
    for (m, av), dd in sorted(by.items()):
        if "p" not in dd or "m" not in dd:
            continue
        p, q = dd["p"], dd["m"]; k = p["k"]; j = 0.5 * (p["j"] + q["j"])
        sp, sm = abs(p["dsdx"]) * KAPPA / (2 * p["j"]), abs(q["dsdx"]) * KAPPA / (2 * q["j"])
        tp, tm = abs(p["dsyc"]) * KAPPA / p["j"], abs(q["dsyc"]) * KAPPA / q["j"]
        odd = bool(np.sign(p["dsdx"]) == -np.sign(q["dsdx"]) and abs(sp - sm) / max(sp, sm) <= 0.25)
        sig = 0.5 * (sp + sm); err = max(0.5 * abs(sp - sm), 0.05 * sig)
        pt = dict(m=m, av=av, k=k, j=j, sigma_par=sig, sigma_par_err=err, sp=sp, sm=sm, sigma_perp=0.5 * (tp + tm), sigma_perp_p=tp, sigma_perp_m=tm, odd=odd, born=KAPPA ** 2 * k / 8,
                  ratio_born=sig / (KAPPA ** 2 * k / 8), d_dx_p=p["dsdx"], d_dx_m=q["dsdx"])
        res["points"].append(pt)
    pts = [p for p in res["points"] if p["av"] == 0.04]
    for m in (8, 16):
        a4 = next((p for p in pts if p["m"] == m), None); a8 = next((p for p in res["points"] if p["m"] == m and p["av"] == 0.08), None)
        if a4 and a8:
            r = abs(0.5 * (a8["d_dx_p"] - a8["d_dx_m"])) / abs(0.5 * (a4["d_dx_p"] - a4["d_dx_m"])); res["KA3"][str(m)] = dict(ratio=float(r), ok=bool(3.0 <= r <= 5.0))
    res["KA2"] = bool(pts and all(p["odd"] for p in pts))
    ka4 = [p for p in pts if p["m"] in (1, 2, 3)]; res["KA4"] = dict(ratios=[p["ratio_born"] for p in ka4], ok=bool(len(ka4) == 3 and all(abs(p["ratio_born"] - 1) <= 0.30 for p in ka4)))
    res["gates_pass"] = bool(res["KA1"] and res["KA2"] and res["KA3"] and all(v["ok"] for v in res["KA3"].values()) and res["KA4"]["ok"])
    # P1
    ks = np.array([p["k"] for p in pts]); sg = np.array([p["sigma_par"] for p in pts]); sk = sg / ks
    hi = [i for i in range(len(ks)) if ks[i] >= 1.0]
    mono = bool(all(sk[hi[i + 1]] <= sk[hi[i]] * 1.05 for i in range(len(hi) - 1))) if len(hi) > 1 else None
    i049 = int(np.argmin(abs(ks - 0.49))); iend = int(np.argmax(ks))
    res["P1"] = dict(monotone_decreasing=mono, ratio_end_to_049=float(sk[iend] / sk[i049]), PASS=bool(mono and sk[iend] / sk[i049] <= 0.6))
    res["P2"] = dict(max_sigma_perp_k_ge_02=float(max(p["sigma_perp"] for p in pts if p["k"] >= 0.2)), PASS=bool(all(p["sigma_perp"] < np.pi for p in pts if p["k"] >= 0.2)))
    # P4
    kk, ss = ks[np.argsort(ks)], sg[np.argsort(ks)]
    def sig(x, tail=True):
        out = np.interp(x, kk, ss)
        return np.where(x > kk.max(), (ss[-1] * kk.max() / x) if tail else 0.0, out)
    pred = {f"{kc:.3f}": dict(one_over_k_tail=integral(sig, kc), zero_tail=integral(lambda x: sig(x, False), kc)) for kc in (2.0944, np.pi, 2 * np.pi)}
    a_meas, a_se = 0.0540, 0.0026; p2 = pred["2.094"]["one_over_k_tail"]; r = p2 / a_meas
    res["P4"] = dict(pred=pred, measured=a_meas, ratio_at_2p09=float(r), verdict="WITHIN 30 %" if abs(r - 1) <= 0.30 else ("PARTIAL (30-60 %)" if abs(r - 1) <= 0.60 else "REFUTED (> 60 %)"))
    json.dump(res, open(OUT / "wave_scan_results.json", "w"), indent=1, default=float)
    print(f"control: slope dx {c['sdx']:+.1e}, d change {c['d_change']:+.3f} -> KA1 {res['KA1']}")
    for p in pts: print(f"m={p['m']:2d} k={p['k']:.3f} sigma_par {p['sigma_par']:.3f}+-{p['sigma_par_err']:.3f} (Born {p['born']:.3f}, ratio {p['ratio_born']:.2f}) sigma_perp {p['sigma_perp']:.2f} odd {p['odd']}")
    print("KA2", res["KA2"], "KA3", res["KA3"], "KA4", res["KA4"]); print("P1", res["P1"]); print("P2", res["P2"]); print("P4", json.dumps(res["P4"], indent=0)); print("gates pass:", res["gates_pass"])


if __name__ == "__main__":
    main()
