#!/usr/bin/env python3
"""Vortex counter of the Kwon & Shin reference (Zenodo 10.5281/zenodo.20068724, src/gpe_dynamics/vortex_GPU.py::vortex_detect),
ported line by line (numpy/scipy instead of cupy) so that a snapshot of ANY solver is counted with the reference's own rule:
local minima of the density along axis 0 with n < 0.2, outside a disc of radius 5//dx grid units around the obstacle, merged when
closer than 3//dx grid units, kept when the phase circulation on a square loop of half-width 2//dx grid units exceeds 0.9 pi
(steps larger than 0.3 pi are dropped from the sum, as in the reference); vortices with X + 2//dx >= Nx - 2//dx or the same in Y are skipped.

    .venv/bin/python exploration/external/ks_vortex_count.py DIR [--times 10,20,30,40,50]      # counts of DIR/psi_time_<t>.npy
Validation on the reference's own snapshots: `--validate` (counts must be the vortex.txt entries at the same times).
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
from scipy import spatial
from scipy.signal import argrelmin

NX, NY, RX = 1000, 500, 250
DX = 2 * RX / NX            # = DY
OBST = 100                  # obstacle_position
SIGMA, V0 = 20, 0.9


def vortex_detect(density: np.ndarray, phase: np.ndarray):
    dx = DX
    r_th = 5 // dx + (SIGMA * np.sqrt(np.log(V0) / 2) if V0 > 1 else 0.0)
    ox = int(OBST * NX / 2 / RX + NX // 2); oy = NY // 2
    Y, X = argrelmin(density)                       # axis 0 only, as in the reference
    temp = [[y, x] for y, x in zip(Y, X) if density[y, x] < 0.2 and (x - ox) ** 2 + (y - oy) ** 2 > r_th ** 2]
    if not temp:
        return []
    temp = np.array(temp); count = 0
    while count < len(temp):
        dist, idx = spatial.KDTree(temp).query(temp[count], k=min(10, len(temp)))
        dist, idx = np.atleast_1d(dist)[1:], np.atleast_1d(idx)[1:]
        temp = np.delete(temp, idx[dist <= int(3 // dx)], axis=0); count += 1
    out = []; l = int(2 // dx)
    for Yc, Xc in temp:
        if Xc + l >= NX - l or Yc + l >= NY - l:
            continue
        xs = list(range(Xc - l, Xc + l + 1)) + [Xc + l] * (2 * l - 1) + list(range(Xc - l, Xc + l + 1))[::-1] + [Xc - l] * (2 * l - 1)
        ys = [Yc + l] * (2 * l + 1) + list(range(Yc - l + 1, Yc + l))[::-1] + [Yc - l] * (2 * l + 1) + list(range(Yc - l + 1, Yc + l))
        integral = 0.0
        for k in range(len(xs) - 1):
            d = np.angle(np.exp(1j * (phase[ys[k + 1], xs[k + 1]] - phase[ys[k], xs[k]])))
            if abs(d) < 0.3 * np.pi:
                integral += d
        integral += np.angle(np.exp(1j * (phase[ys[0], xs[0]] - phase[ys[-1], xs[-1]])))
        if integral > 0.9 * np.pi:
            out.append([Xc, Yc, 1])
        elif integral < -0.9 * np.pi:
            out.append([Xc, Yc, -1])
    return out


def count(psi: np.ndarray):
    return vortex_detect(np.abs(psi) ** 2, np.arctan2(psi.imag, psi.real))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--times", default="10,20,30,40,50"); ap.add_argument("--validate", action="store_true")
    a = ap.parse_args()
    ref = {}
    rf = Path("/mnt/data/xdev-cache/qf-external/20068724/extracted/vortex.txt")
    if rf.exists():
        for row in np.loadtxt(rf):
            ref[round(row[0], 1)] = int(row[1])
    for t in [float(x) for x in a.times.split(",")]:
        f = Path(a.dir) / f"psi_time_{t:.1f}.npy"
        if not f.exists():
            print(f"t={t:5.1f}: (no snapshot)"); continue
        v = count(np.load(f)); n = len(v)
        print(f"t={t:5.1f}: vortices {n:2d} (+{sum(1 for x in v if x[2] > 0)}/-{sum(1 for x in v if x[2] < 0)})   reference {ref.get(round(t, 1), '?')}", flush=True)


if __name__ == "__main__":
    main()
