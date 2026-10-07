#!/usr/bin/env python3
"""L = 128 base state at e = 0.60 for hypothesis W's box-size control (W2 of PGPE_FRICTION_PREREG.md amendment A1):
the round-1 recipe (random high-energy state at the target energy, relaxed to t = 4000), then 500 time units of
measurement (T, n_s/n, raw vortex count). -> data/generated/pgpe/transport/base_L128_e0.60.{json,npy}"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from round2 import run_blocks

ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / "data/generated/pgpe/transport"
t0 = time.time(); s = PGPE(N=256, L=128.0); c = s.random_state(1.0, 0.60, np.random.default_rng(12811))
E0 = s.energy(c); c, blocks, whole = run_blocks(s, c, 4500.0, 4000.0, seed=128)
res = {"e": 0.60, "L": 96.0, "N": 192, "E_per_particle": E0 / s.norm(c), "drift_E": abs(s.energy(c) - E0) / E0, "blocks": blocks, "whole": whole,
       "T": whole["T"], "ns_over_n": whole["ns_over_n"], "n_v": whole["n_v"], "seconds": round(time.time() - t0, 1)}
(OUT / "base_L128_e0.60.json").write_text(json.dumps(res, indent=1, default=float)); np.save(OUT / "base_L128_e0.60_final.npy", c)
print(f"base L=128 e=0.60: T = {whole['T']:.4f}, n_s/n = {whole['ns_over_n']:.4f}, raw n_v = {whole['n_v']:.2f}, {res['seconds']} s")
