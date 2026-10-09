"""WS-A1: L1 (is the sigma_par ripple the lattice?) and P4' (friction from the d0-averaged sigma_par). Uses analyze_wave_scan.slopes.
    .venv/bin/python exploration/pgpe/analyze_wave_scan_d0.py -> scan_d0/wave_scan_d0_results.json"""
import glob, json, re, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "exploration/pgpe"))
from analyze_wave_scan import slopes, KAPPA, OUT as OUT1
from predict_friction_from_sigma import integral
OUT = ROOT / "data/generated/pgpe/wave_scattering/scan_d0"


def sigma_set(dirpath, control, pattern, d0):
    c = slopes(control)
    if c is None:
        return None, None
    by = {}
    for f in sorted(glob.glob(str(dirpath / pattern))):
        mm = re.match(r".*_m(\d+)_([pm])_av0\.04\.npz", f); m, d = int(mm.group(1)), mm.group(2); s = slopes(f)
        if s is None:
            continue
        s["dsdx"] = s["sdx"] - c["sdx"]; s["dsyc"] = s["syc"] - c["syc"]; by.setdefault(m, {})[d] = s
    out = {}
    for m, dd in by.items():
        if "p" in dd and "m" in dd:
            p, q = dd["p"], dd["m"]; sp, sm = abs(p["dsdx"]) * KAPPA / (2 * p["j"]), abs(q["dsdx"]) * KAPPA / (2 * q["j"])
            tp, tm = abs(p["dsyc"]) * KAPPA / p["j"], abs(q["dsyc"]) * KAPPA / q["j"]
            out[m] = dict(k=p["k"], sigma_par=0.5 * (sp + sm), sp=sp, sm=sm, sigma_perp=0.5 * (tp + tm), odd=bool(np.sign(p["dsdx"]) == -np.sign(q["dsdx"])))
    return c, out


def main():
    data = {32: sigma_set(OUT1, OUT1 / "WS_control.npz", "WS_m*_av0.04.npz", 32)[1]}
    ctrl = {32: dict(sdx=slopes(OUT1 / "WS_control.npz")["sdx"])}
    for d0 in (20, 24, 28):
        c, o = sigma_set(OUT, OUT / f"WS_d{d0}_control.npz", f"WS_d{d0}_m*_av0.04.npz", d0)
        if o is not None:
            data[d0] = o; ctrl[d0] = dict(sdx=c["sdx"], syc=c["syc"])
    ms = [4, 8, 10, 12, 14, 16, 20]; res = dict(controls=ctrl, table={}, L1={})
    for m in ms:
        row = {d0: data[d0][m]["sigma_par"] for d0 in data if m in data[d0]}
        if len(row) >= 3:
            v = np.array(list(row.values())); res["table"][m] = dict(k=2 * np.pi * m / 64, by_d0=row, mean=float(v.mean()), spread=float(v.max() / v.min() - 1), std=float(v.std(ddof=1)))
    mid = [m for m in (10, 12, 14, 16) if m in res["table"]]
    res["L1"] = dict(spread_mid=[res["table"][m]["spread"] for m in mid], spread_hi=[res["table"][m]["spread"] for m in (20,) if m in res["table"]],
                     PASS=bool(mid and all(res["table"][m]["spread"] > 0.30 for m in mid) and all(res["table"][m]["spread"] < 0.30 for m in (20,) if m in res["table"])))
    # P4': d0-averaged sigma at the scan points; low-k and high-k filled from the d0 = 32 first scan (m = 1, 2, 3, 6, 24, 28 not repeated)
    k_all, s_all = [], []
    first = {p["m"]: p["sigma_par"] for p in json.load(open(OUT1 / "wave_scan_results.json"))["points"] if p["av"] == 0.04}
    for m, v in sorted(first.items()):
        k_all.append(2 * np.pi * m / 64); s_all.append(res["table"][m]["mean"] if m in res["table"] else v)
    k_all, s_all = np.array(k_all), np.array(s_all)
    def sig(x, tail=True):
        out = np.interp(x, k_all, s_all); return np.where(x > k_all.max(), (s_all[-1] * k_all.max() / x) if tail else 0.0, out)
    pred = {f"{kc:.3f}": integral(sig, kc) for kc in (2.0944, np.pi, 2 * np.pi)}; r = pred["2.094"] / 0.0540
    res["P4prime"] = dict(pred=pred, measured=0.0540, ratio_at_2p09=float(r), verdict="WITHIN 30 %" if abs(r - 1) <= 0.30 else ("PARTIAL (30-60 %)" if abs(r - 1) <= 0.60 else "REFUTED (> 60 %)"), sigma_used=dict(zip(k_all.round(3).tolist(), s_all.round(3).tolist())))
    json.dump(res, open(OUT / "wave_scan_d0_results.json", "w"), indent=1, default=float)
    print("controls (d_x slope):", {k: f"{v['sdx']:+.1e}" for k, v in ctrl.items()})
    print("sigma_par by d0:"); [print(f"  m={m:2d} k={t['k']:.3f} " + " ".join(f"d0={d}:{s:.2f}" for d, s in sorted(t['by_d0'].items())) + f" | mean {t['mean']:.2f} spread {t['spread']*100:.0f}%") for m, t in sorted(res["table"].items())]
    print("L1:", res["L1"]); print("P4':", json.dumps(res["P4prime"]["pred"]), "ratio", round(res["P4prime"]["ratio_at_2p09"], 3), res["P4prime"]["verdict"])


if __name__ == "__main__":
    main()
