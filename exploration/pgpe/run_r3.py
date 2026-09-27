#!/usr/bin/env python3
"""Round 3 runs (docs/designs/PGPE_R3_PREREG.md). Parts A (V/P arms with positions), D (16-pair intervention), C (L=128).
Outputs data/generated/pgpe/r3/<name>.json (blocks) and <name>_samples.npz (positions per sample).
Run: .venv/bin/python exploration/pgpe/run_r3.py --parts A,D [--procs 8]"""
from __future__ import annotations
import argparse, json, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from round2 import quadrupole_config, imprint, heat, many_pair_config, run_blocks_positions
from observables import vortices

ROOT = Path(__file__).resolve().parents[2]; SW = ROOT / "data/generated/pgpe/sweep"; OUT = ROOT / "data/generated/pgpe/r3"
BASES = ["e0.60_s11_t4000", "e0.90_s11_t4000", "e0.90_s12_t4000"]


def job(spec):
    t0 = time.time(); kind = spec["kind"]
    if kind in ("A", "D"):
        s = PGPE(N=128, L=64.0); c0 = np.load(SW / f"{spec['base']}_final.npy")
        if kind == "A":
            pos, q = quadrupole_config(s.L); cV = imprint(s, c0, pos, q)
            c = cV if spec["arm"] == "V" else heat(s, c0, s.energy(cV), np.random.default_rng(7))
        else:
            pos, q = many_pair_config(s.L, 16, 8.0, np.random.default_rng(300 + spec["idx"]))
            c = imprint(s, c0, pos, q)
            det = vortices(s, c)[1]; spec["imprint_check"] = {"imprinted": 32, "detected": int(len(det)), "neutral": bool((det > 0).sum() == (det < 0).sum())}
        E0 = s.energy(c); c, blocks, samples = run_blocks_positions(s, c, 1500.0, 0.0, seed=spec["idx"])
    elif kind == "C":
        s = PGPE(N=256, L=128.0); c = s.random_state(1.0, spec["e"], np.random.default_rng(spec["seed"]))
        E0 = s.energy(c); c, blocks, samples = run_blocks_positions(s, c, 4000.0, 3000.0, seed=spec["seed"])
    else:  # C2: amendment R3-A2 -- t_tr doubled (3000 -> 6000) after Part C's admission failure at L = 128
        s = PGPE(N=256, L=128.0); c = s.random_state(1.0, spec["e"], np.random.default_rng(spec["seed"]))
        E0 = s.energy(c); c, blocks, samples = run_blocks_positions(s, c, 7000.0, 6000.0, seed=spec["seed"])
    res = {**spec, "E_per_particle": E0 / s.norm(c), "drift_E": abs(s.energy(c) - E0) / E0, "L": s.L, "blocks": blocks, "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{spec['name']}.json").write_text(json.dumps(res, indent=1, default=float))
    np.savez_compressed(OUT / f"{spec['name']}_samples.npz", t=np.array([x["t"] for x in samples]),
                        pos=np.array([np.array(x["pos"], dtype=float) for x in samples], dtype=object),
                        q=np.array([np.array(x["q"], dtype=int) for x in samples], dtype=object),
                        E_pv=np.array([x["E_pv"] for x in samples]), kin_bath=np.array([x["kin_bath"] for x in samples]),
                        E_inc=np.array([x["E_inc"] for x in samples]), E_comp=np.array([x["E_comp"] for x in samples]))
    np.save(OUT / f"{spec['name']}_final.npy", c)
    b1, bl = blocks[0], blocks[-1]
    print(f"{spec['name']}: T_b {b1['T']:.3f}->{bl['T']:.3f} cond {b1['cond']:.3f}->{bl['cond']:.3f} n_v {b1['n_v']:.1f}->{bl['n_v']:.1f} E_inc {b1['E_inc']:.1f}->{bl['E_inc']:.1f} dE={res['drift_E']:.1e} {res['seconds']}s", flush=True)


def specs(parts):
    out = []
    if "A" in parts:
        for i, b in enumerate(BASES):
            for arm in ("V", "P"):
                out.append({"kind": "A", "base": b, "arm": arm, "idx": i, "name": f"A_{b}_{arm}"})
    if "D" in parts:
        for i, b in enumerate(BASES):
            out.append({"kind": "D", "base": b, "idx": i, "name": f"D_{b}_16pairs"})
    if "C" in parts:
        for e in (1.00, 1.10, 1.20):
            for sd in (11, 12):
                out.append({"kind": "C", "e": e, "seed": sd, "name": f"C_L128_e{e:.2f}_s{sd}"})
    if "C2" in parts:
        for e in (1.00, 1.10, 1.20):
            for sd in (11, 12):
                out.append({"kind": "C2", "e": e, "seed": sd, "name": f"C2_L128_e{e:.2f}_s{sd}"})
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--parts", default="A,D"); ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args()
    with Pool(a.procs) as pool:
        pool.map(job, specs(a.parts.split(",")), chunksize=1)
