#!/usr/bin/env python3
"""Amendment E-A1 of PGPE_EINSTEIN_PREREG.md: I1 (residual MSD exponent gamma(T) on lags 20-400) and I2 (power
spectrum of the W1 single-pair separations on t in [2000, 4000]: island if the three largest lines carry > 50 % of
the variance). -> data/generated/pgpe/transport/island_I1_I2.json"""
from __future__ import annotations
import glob, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_transport import summarise, load, pair_separations

ROOT = Path(__file__).resolve().parents[2]; T = ROOT / "data/generated/pgpe/transport"
out = {"I1": {}, "I2": {}}
sets = {"0.115": sorted(glob.glob(str(T / "prod_e0.60_d*_s*.npz"))) + sorted(glob.glob(str(T / "G2_e0.60*.npz"))),
        "0.220": sorted(glob.glob(str(T / "prodB_e0.70_d*_s*.npz"))), "0.353": sorted(glob.glob(str(T / "prodB_e0.80_d*_s*.npz"))),
        "0.458_report_only": sorted(glob.glob(str(T / "prodB_e0.90s12_d*_s*.npz")))}
lags = [5, 10, 20, 40, 80, 120, 160, 240, 320, 400]
for Tlab, files in sets.items():
    r, info = summarise(files)
    ms = np.array(r["msd"]); lg = np.array(lags, float); ok = np.isfinite(ms) & (lg >= 20)
    y = ms[ok] - r["msd_offset"]; pos = y > 0
    gam_100 = float(np.polyfit(np.log(lg[ok][lg[ok] >= 100]), np.log(y[lg[ok] >= 100]), 1)[0]) if (lg[ok] >= 100).sum() >= 3 and np.all(y[lg[ok] >= 100] > 0) else float("nan")
    out["I1"][Tlab] = {"gamma_20_400": r["msd_exponent"], "gamma_se": r["msd_exponent_se"], "gamma_lags_ge_100": gam_100, "msd": [float(x) for x in ms],
                       "msd_offset": r["msd_offset"], "eta_if_read": r["eta"], "alpha_energy": r["alpha_energy"], "n_blocks": r["n_blocks"],
                       "tracks": [(i["file"], i["ended"], i["t_end"]) for i in info]}
    print(Tlab, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out["I1"][Tlab].items() if k not in ("msd", "tracks")}, flush=True)
for f in sorted(glob.glob(str(T / "W1_*.npz"))):
    t, R, q, z, meta = load(f); d = pair_separations(R, q, 64.0)[0]; m = (t >= 2000) & (t <= 4000); x = d[m] - d[m].mean()
    F = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2; F[0] = 0.0; tot = F.sum(); top = np.sort(F)[-3:].sum(); freqs = np.fft.rfftfreq(len(x), d=float(np.median(np.diff(t[m]))))
    peaks = [(float(freqs[i]), float(F[i] / tot)) for i in np.argsort(F)[-3:][::-1]]
    out["I2"][Path(f).stem] = {"var": float(x.var()), "top3_fraction": float(top / tot), "island": bool(top / tot > 0.5), "peaks_freq_frac": peaks, "d_mean": float(d[m].mean())}
    print(Path(f).stem, out["I2"][Path(f).stem], flush=True)
(T / "island_I1_I2.json").write_text(json.dumps(out, indent=1, default=float))
