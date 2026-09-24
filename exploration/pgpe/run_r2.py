#!/usr/bin/env python3
"""Runs of docs/designs/PGPE_R2_PREREG.md: Part I (intervention), Part II (heating ladder), Part III (L = 32).
One JSON per run in data/generated/pgpe/r2/. Run: .venv/bin/python exploration/pgpe/run_r2.py [--parts I,II,III]"""
from __future__ import annotations
import argparse, json, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from round2 import quadrupole_config, imprint, heat, run_blocks

ROOT = Path(__file__).resolve().parents[2]; SW = ROOT / "data/generated/pgpe/sweep"; OUT = ROOT / "data/generated/pgpe/r2"
BASES_I = ["e0.90_s11_t4000", "e0.90_s12_t4000", "e0.60_s11_t4000"]
LADDER = [1.00, 1.05, 1.10, 1.15, 1.20]
FS_E = [0.90, 1.00, 1.10, 1.20, 1.40]


def job(spec):
    kind = spec["kind"]; t0 = time.time()
    if kind in ("I", "II"):
        s = PGPE(N=128, L=64.0)
        c0 = np.load(SW / f"{spec['base']}_final.npy")
    if kind == "I":
        pos, q = quadrupole_config(s.L)
        cV = imprint(s, c0, pos, q)
        c = {"V": cV, "P": heat(s, c0, s.energy(cV), np.random.default_rng(7)), "0": c0}[spec["arm"]]
        E0 = s.energy(c); c, blocks, whole = run_blocks(s, c, 1500.0, 0.0, seed=spec["idx"])
    elif kind == "II":
        c = heat(s, c0, spec["e"] * s.norm(c0), np.random.default_rng(100 + spec["idx"]))
        E0 = s.energy(c); c, blocks, whole = run_blocks(s, c, 1500.0, 500.0, seed=spec["idx"])
    else:
        s = PGPE(N=64, L=32.0)
        c = s.random_state(1.0, spec["e"], np.random.default_rng(spec["seed"]))
        E0 = s.energy(c); c, blocks, whole = run_blocks(s, c, 4000.0, 3000.0, seed=spec["seed"])
    res = {**spec, "E_per_particle": E0 / s.norm(c), "drift_E": abs(s.energy(c) - E0) / E0, "L": s.L,
           "blocks": blocks, "whole": whole, "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{spec['name']}.json").write_text(json.dumps(res, indent=1, default=float))
    np.save(OUT / f"{spec['name']}_final.npy", c)
    w = whole
    print(f"{spec['name']}: T={w['T']:.3f} cond={w['cond']:.3f} n_v={w['n_v']:.1f} Q={w['Q']:.2f} ns/n={w['ns_over_n']:.3f} "
          f"eta={w['eta']:.3f} ({w['law']}) R_L={w['R_L']:.2f} R_T={w['R_T']:.2f} dE={res['drift_E']:.1e} {res['seconds']}s", flush=True)


def specs(parts):
    out = []
    if "I" in parts:
        for i, b in enumerate(BASES_I):
            for arm in (["V", "P", "0"] if b.startswith("e0.90") else ["V", "P"]):
                out.append({"kind": "I", "base": b, "arm": arm, "idx": i, "name": f"I_{b}_{arm}"})
    if "II" in parts:
        for i, b in enumerate(BASES_I[:2]):
            for e in LADDER:
                out.append({"kind": "II", "base": b, "e": e, "idx": i, "name": f"II_{b}_e{e:.2f}"})
    if "III" in parts:
        for e in FS_E:
            for sd in (11, 12, 13):
                out.append({"kind": "III", "e": e, "seed": sd, "name": f"III_L32_e{e:.2f}_s{sd}"})
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--parts", default="I,II,III"); ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args()
    with Pool(a.procs) as pool:
        pool.map(job, specs(a.parts.split(",")), chunksize=1)
