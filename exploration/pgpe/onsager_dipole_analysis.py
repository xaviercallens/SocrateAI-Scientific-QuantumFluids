#!/usr/bin/env python3
"""Cosmology brief, Tier 1 item 2: Gauthier et al. 2019's Onsager-cluster dipole order parameter D
(observables.onsager_dipole), applied post hoc to the vortex-position data already on disk from rounds 3 and 4
-- no new runs. Cross-checked against each run's own sector/pair label (round 3 Part D's accidental torus
windings; round 4's imposed V3/P16/V3P16 arms) to see whether real-space clustering (D) and net winding (W)
agree, complicate, or are independent.
Run: .venv/bin/python exploration/pgpe/onsager_dipole_analysis.py -> data/generated/pgpe/onsager_dipole.json"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from observables import onsager_dipole

ROOT = Path(__file__).resolve().parents[2]
R3, R4 = ROOT / "data/generated/pgpe/r3", ROOT / "data/generated/pgpe/r4"


class _L:
    """Minimal stand-in for PGPE carrying only the box size onsager_dipole needs."""
    def __init__(self, L):
        self.L = L


def series_D(npz_path: Path, L: float, block=100.0):
    z = np.load(npz_path, allow_pickle=True)
    t, pos, q = z["t"], z["pos"], z["q"]
    s = _L(L)
    D = np.array([onsager_dipole(s, p, qq) for p, qq in zip(pos, q)])
    nb = int(round((t.max()) / block))
    block_D = []
    for i in range(nb):
        m = (t > i * block) & (t <= (i + 1) * block)
        vals = D[m]
        vals = vals[np.isfinite(vals)]
        block_D.append(float(np.mean(vals)) if len(vals) else float("nan"))
    return {"t": t.tolist(), "D": D.tolist(), "D_by_block": block_D}


def main():
    out = {}
    # Round 3 Part D: the accidental-sector runs (s12 persistent current W=-3; s11 coarsening W=0; e0.60 decaying W 2->0)
    for base in ("e0.60_s11_t4000", "e0.90_s11_t4000", "e0.90_s12_t4000"):
        p = R3 / f"D_{base}_16pairs_samples.npz"
        if p.exists():
            out[f"D3_{base}"] = series_D(p, 64.0)
    # Round 4 Part B: 0 / V3 (sector) / P16 (pairs) / V3P16 (both) x three bases
    for base in ("e0.60_s11_t4000", "e0.90_s11_t4000", "e0.90_s12_t4000"):
        for arm in ("0", "V3", "P16", "V3P16"):
            p = R4 / f"B_{base}_{arm}_samples.npz"
            if p.exists():
                out[f"B4_{base}_{arm}"] = series_D(p, 64.0)
    (ROOT / "data/generated/pgpe/onsager_dipole.json").write_text(json.dumps(out, indent=1, default=float))

    print("=== Round 3 Part D (accidental sectors) ===")
    for base, w_final, label in [("e0.60_s11_t4000", "0 (decayed from 2)", "decaying current"),
                                  ("e0.90_s11_t4000", "0 (clean coarsening)", "no sector"),
                                  ("e0.90_s12_t4000", "-3 (intact)", "persistent current")]:
        d = out[f"D3_{base}"]["D_by_block"]
        print(f"{base} [{label}, W_final={w_final}]: D(t)/block =", [round(x, 3) if np.isfinite(x) else None for x in d])

    print("\n=== Round 4 Part B (imposed sector vs pairs) ===")
    for base in ("e0.60_s11_t4000", "e0.90_s11_t4000", "e0.90_s12_t4000"):
        row = {}
        for arm in ("0", "V3", "P16", "V3P16"):
            d = out[f"B4_{base}_{arm}"]["D_by_block"]
            finite = [x for x in d if np.isfinite(x)]
            row[arm] = round(float(np.mean(finite)), 4) if finite else None
        print(base, row)


if __name__ == "__main__":
    main()
