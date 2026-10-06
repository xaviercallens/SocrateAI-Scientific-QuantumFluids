#!/usr/bin/env python3
"""Josephson relation eta*K = 1 on the equilibrated L = 192 snapshots (r3_C4, window t in [13500, 14500]).

eta from ln g1(r) = c - eta * G_T(r) with G_T the torus Green function (2 pi [A(0) - A(r)], A = FFT^-1 of 1/k^2 on the
projector), fitted on 8 <= r <= r_max for r_max in {16, 32, 48}; also the naive window fit (round2.fit_g1_window).
K = 2 pi n_s / T from the run's block-averaged current correlators (analysis JSON). Exploratory (H05 was discarded
at triage); no decision rule. -> data/generated/pgpe/r3_C4/analysis/josephson_l192.json
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from observables import g1_radial
from round2 import fit_g1_window
from analyze_r3 import whole_from_blocks

ROOT = Path(__file__).resolve().parents[2]; C4 = ROOT / "data/generated/pgpe/r3_C4"; A = C4 / "analysis"
s = PGPE(N=384, L=192.0)
Ghat = np.where(s.P & (s.k2 > 0), 1.0 / np.where(s.k2 > 0, s.k2, 1.0), 0.0)
Acorr = np.fft.ifft2(Ghat).real * s.N ** 2 / s.L ** 2; GT = 2 * np.pi * (Acorr[0, 0] - Acorr)
ix = np.fft.fftfreq(s.N, d=1.0 / s.N) * s.dx; RX, RY = np.meshgrid(ix, ix, indexing="ij"); R = np.hypot(RX, RY)
out = {}
for j in sorted(A.glob("C3_L192_*.json")):
    name = j.stem; d = json.loads(j.read_text()); w = whole_from_blocks(d); K = 2 * np.pi * w["ns_over_n"] / w["T"]
    snaps = sorted(C4.glob(f"{name}_sample_t*.raw"))
    g = np.zeros((s.N, s.N)); gr = None
    for f in snaps:
        psi = np.fromfile(f, dtype=np.complex128).reshape(s.N, s.N); c = np.fft.fft2(psi) * s.P
        corr = np.fft.ifft2(np.abs(c) ** 2).real; g += corr / corr[0, 0]
        rr, gg = g1_radial(s, c); gr = gg if gr is None else gr + gg
    g /= len(snaps); gr /= len(snaps)
    rec = {"K": K, "T": w["T"], "ns_over_n": w["ns_over_n"], "eta_blocks": w["eta"], "x_blocks": w["eta"] * K - 1, "n_snapshots": len(snaps)}
    for rmax in (16, 32, 48):
        m = (R >= 8) & (R <= rmax) & (g > 0)
        p, cov = np.polyfit(GT[m], np.log(g[m]), 1, cov=True); eta = float(-p[0])
        rec[f"eta_torus_8_{rmax}"] = eta; rec[f"x_torus_8_{rmax}"] = eta * K - 1
    fit = fit_g1_window(rr, gr, s.L); rec["eta_naive"] = fit["eta"]; rec["x_naive"] = fit["eta"] * K - 1; rec["naive_rmax"] = fit["r_max"]
    out[name] = rec
    print(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in rec.items()}, flush=True)
xs = {k: [r[f"x_torus_8_{k}"] for r in out.values()] for k in (16, 32, 48)}
summary = {k: {"mean": float(np.mean(v)), "se": float(np.std(v, ddof=1) / np.sqrt(len(v))) if len(v) > 1 else None} for k, v in xs.items()}
A.mkdir(exist_ok=True); (A / "josephson_l192.json").write_text(json.dumps({"runs": out, "x_summary": summary}, indent=1, default=float))
print("eta*K - 1 (torus Green function):", summary)
