#!/usr/bin/env python3
"""Thermal base states for the vortex-transport campaign (PGPE_FRICTION_PREREG.md amendment A1): the vortex-free
e = 0.60 state heated to a target energy per particle by the phonon construction of round 2 (round2.heat), then
1000 time units of equilibration and 500 of measurement (five blocks: T, n_s/n, raw vortex count).

    .venv/bin/python exploration/pgpe/make_transport_bases.py 0.70      -> data/generated/pgpe/transport/base_e0.70.{json,npy}
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from round2 import heat, run_blocks

ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / "data/generated/pgpe/transport"
e = float(sys.argv[1]); t0 = time.time(); s = PGPE(N=128, L=64.0)
c0 = np.load(ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000_final.npy")
c = heat(s, c0, e * s.norm(c0), np.random.default_rng(int(round(1000 * e))))
E0 = s.energy(c); c, blocks, whole = run_blocks(s, c, 1500.0, 1000.0, seed=int(round(100 * e)))
res = {"e": e, "E_per_particle": E0 / s.norm(c), "drift_E": abs(s.energy(c) - E0) / E0, "L": s.L, "blocks": blocks, "whole": whole,
       "T": whole["T"], "ns_over_n": whole["ns_over_n"], "n_v": whole["n_v"], "seconds": round(time.time() - t0, 1)}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / f"base_e{e:.2f}.json").write_text(json.dumps(res, indent=1, default=float)); np.save(OUT / f"base_e{e:.2f}_final.npy", c)
print(f"base e={e:.2f}: T = {whole['T']:.4f}, n_s/n = {whole['ns_over_n']:.4f}, raw n_v = {whole['n_v']:.2f}, drift {res['drift_E']:.1e}, {res['seconds']} s")
