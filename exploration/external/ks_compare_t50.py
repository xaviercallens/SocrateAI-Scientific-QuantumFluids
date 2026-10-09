#!/usr/bin/env python3
"""Compare a Kwon-Shin run to t = 50 (snapshots + force table written by the Rust example `kwon_shin --snap-dir`) with the reference:
force table (every 0.1 tau), wave function at t = 10, 20, ..., 50 (relative L2, and L2 of the density), and the vortex counts at t = 0, 5, ..., 50
counted with the reference's own rule (ks_vortex_count.py) on OUR snapshots and compared with the reference's vortex.txt.

    .venv/bin/python exploration/external/ks_compare_t50.py RUN_DIR      # RUN_DIR holds snap/psi_time_*.npy and kwon_shin_force.csv
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ks_vortex_count import count

REF = Path("/mnt/data/xdev-cache/qf-external/20068724/extracted")


def main():
    run = Path(sys.argv[1]); snap = run / "snap"
    rows = list(csv.DictReader(open(run / "kwon_shin_force.csv")))
    t = np.array([float(r["t"]) for r in rows]); f = np.array([float(r["force_x"]) for r in rows])
    ok = [r["force_ref"] != "" for r in rows]; fr = np.array([float(r["force_ref"]) if o else np.nan for r, o in zip(rows, ok)]); d = np.abs(f - fr)
    print(f"force: {np.isfinite(fr).sum()} reference points, t = {t[0]:.1f}..{t[-1]:.1f};  max|F_ref| = {np.nanmax(np.abs(fr)):.3f}")
    for a, b in ((0, 1), (1, 5), (5, 10), (10, 20), (20, 30), (30, 40), (40, 50.01)):
        m = (t >= a) & (t < b) & np.isfinite(d)
        if m.any():
            print(f"  t in [{a:4.0f},{b:4.0f}): max|dF| = {d[m].max():.3e}  rms|dF| = {np.sqrt(np.mean(d[m] ** 2)):.3e}  rms|F_ref| = {np.sqrt(np.mean(fr[m] ** 2)):.3f}")
    print("wave function against the reference snapshots (complex64 in the reference):")
    for tt in (10, 20, 30, 40, 50):
        fs = snap / f"psi_time_{tt:.1f}.npy"
        if fs.exists():
            a = np.load(fs).astype(complex); b = np.load(REF / f"psi_time_{tt:.1f}.npy").astype(complex)
            print(f"  t = {tt:2d}: relative L2 of psi = {np.linalg.norm(a - b) / np.linalg.norm(b):.3e}, of the density = "
                  f"{np.linalg.norm(abs(a) ** 2 - abs(b) ** 2) / np.linalg.norm(abs(b) ** 2):.3e}")
    ref = {round(r[0], 1): int(r[1]) for r in np.loadtxt(REF / "vortex.txt")}
    print("vortex counts (reference rule applied to our snapshots) | reference:")
    out = []
    for tt in range(5, 55, 5):
        fs = snap / f"psi_time_{tt:.1f}.npy"
        if fs.exists():
            v = count(np.load(fs)); out.append((tt, len(v), ref.get(float(tt))))
            print(f"  t = {tt:2d}: ours {len(v):2d} (+{sum(1 for x in v if x[2] > 0)}/-{sum(1 for x in v if x[2] < 0)})   reference {ref.get(float(tt))}", flush=True)
    print("counts ours :", [o[1] for o in out]); print("counts ref  :", [o[2] for o in out])


if __name__ == "__main__":
    main()
