#!/usr/bin/env python3
"""Chapter 9: continue OUR t = 20 snapshot (complex128, from the Rust t = 50 run) to t = 25 with the numpy RK4 scheme of
exploration/external/kwon_shin_reproduction.py (same model, same dt = 0.01, v = 0.55 constant) and store the sub-box
x in [60,120), y in [-25,25) every 0.1 tau, to watch the birth of the first vortex pair at the level of single edge steps.
Output: /mnt/data/xdev-cache/qf-external/ch09/birth_t20_25.npz   (about 15 min on a loaded machine)
    nice .venv/bin/python book/figures/ch09_birth_run.py
"""
import sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "exploration" / "external"))
import kwon_shin_reproduction as K
OUT = Path("/mnt/data/xdev-cache/qf-external/ch09"); OUT.mkdir(parents=True, exist_ok=True)
psi = np.load("/mnt/data/xdev-cache/qf-external/ks_rust_t50/snap/psi_time_20.0.npy").astype(np.complex128)
K.RAMP_RIGHT = False
dt = 0.01
x0, x1 = int((60 + 250) / 0.5), int((120 + 250) / 0.5); y0, y1 = int((-25 + 125) / 0.5), int((25 + 125) / 0.5)
times, boxes = [], []
t0 = time.time()
for i in range(501):
    t = 20.0 + i * dt
    if i % 10 == 0:
        times.append(t); boxes.append(psi[y0:y1, x0:x1].copy())
        print(f"t = {t:.2f}  ({time.time()-t0:.0f} s)", flush=True)
    if i < 500:
        psi = K.step(psi, t, dt)
np.savez(OUT / "birth_t20_25.npz", t=np.array(times), box=np.array(boxes), x0=x0, y0=y0, final=psi)
ref = np.load("/mnt/data/xdev-cache/qf-external/ks_rust_t50/snap/psi_time_25.0.npy")
print("relative L2 of the numpy continuation against the Rust t = 25 snapshot:", np.linalg.norm(psi - ref) / np.linalg.norm(ref))
