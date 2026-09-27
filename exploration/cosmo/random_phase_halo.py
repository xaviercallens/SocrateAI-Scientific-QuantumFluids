#!/usr/bin/env python3
"""Round 4 Part A (docs/designs/PGPE_R4_PREREG.md): Hui-Joyce-Landry-Li's random-phase model of a wave dark
matter halo in 2D, read with our instrument (plaquette windings; W(R) = net enclosed charge).
Known answer: <n_vortex> = pi / lambda_dB^2 (2004.01188 §4.2).  Output: data/generated/cosmo/random_phase_halo.json"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/generated/cosmo"
import os
L, N, LAM, NREAL = 64.0, 512, 4.0, int(os.environ.get("NREAL", "20"))
K0 = np.sqrt(2.0) * 2 * np.pi / LAM          # lambda_dB = sqrt(2) 2pi/k0 (mass-weighted 2D rms momentum k0/sqrt2)


def field(rng):
    dx = L / N
    k1 = 2 * np.pi * np.fft.fftfreq(N, d=dx); kx, ky = np.meshgrid(k1, k1, indexing="ij")
    amp = np.exp(-(kx ** 2 + ky ** 2) / K0 ** 2)
    return np.fft.ifft2(amp * np.exp(2j * np.pi * rng.random((N, N))))


def pv(d):
    return (d + np.pi) % (2 * np.pi) - np.pi


def plaquettes(psi):
    th = np.angle(psi)
    dx_ = pv(np.roll(th, -1, axis=0) - th); dy_ = pv(np.roll(th, -1, axis=1) - th)
    w = dx_ + np.roll(dy_, -1, axis=0) - np.roll(dx_, -1, axis=1) - dy_
    return np.rint(w / (2 * np.pi)).astype(int)


def row_winding(psi):
    """Loop sum along x for every row (an integer each); the median is the torus winding W_x."""
    th = np.angle(psi)
    return np.rint(pv(np.roll(th, -1, axis=0) - th).sum(axis=0) / (2 * np.pi)).astype(int)


def window_charges(q, R_cells, n_win, rng):
    """Net charge in n_win random square windows of side R_cells (periodic)."""
    cs = np.cumsum(np.cumsum(np.pad(q, ((1, 0), (1, 0))), axis=0), axis=1)
    out = []
    for _ in range(n_win):
        i0, j0 = rng.integers(0, N - R_cells, 2)
        i1, j1 = i0 + R_cells, j0 + R_cells
        out.append(cs[i1, j1] - cs[i0, j1] - cs[i1, j0] + cs[i0, j0])
    return np.array(out)


def main():
    rng = np.random.default_rng(2026)
    dx = L / N
    dens, hi, Ws, Wreal = [], [], {}, {}
    Rs = [2 * LAM, 3 * LAM, 4 * LAM, 6 * LAM, 8 * LAM, L / 2]
    for r in range(NREAL):
        psi = field(rng); q = plaquettes(psi)
        nv = int(np.abs(q).sum()); dens.append(nv / L ** 2); hi.append(int((np.abs(q) >= 2).sum()) / max(nv, 1))
        for R in Rs:
            wc = window_charges(q, int(round(R / dx)), 200, rng)
            Ws.setdefault(R, []).extend(wc.tolist()); Wreal.setdefault(R, []).append(float(wc.mean()))
    dens = np.array(dens); expected = np.pi / LAM ** 2
    a1 = dens.mean() / expected
    var = np.array([np.var(Ws[R]) for R in Rs]); mean = np.array([np.mean(Ws[R]) for R in Rs])
    sem = np.array([np.std(Ws[R]) / np.sqrt(len(Ws[R])) for R in Rs])
    alpha = np.polyfit(np.log(Rs), np.log(var), 1)[0]
    # amendment R4-A1: windows within one realisation overlap, so the pooled s.e.m. is too small; the independent
    # estimate uses the 20 per-realisation means
    sem_indep = np.array([np.std(Wreal[R], ddof=1) / np.sqrt(len(Wreal[R])) for R in Rs])
    # A4: imposed sector
    psi = field(np.random.default_rng(7)); q0 = plaquettes(psi); rho0 = np.abs(psi) ** 2
    x = (np.arange(N) * dx)[:, None]
    a4 = []
    for W0 in (1, 3, 6):
        psiW = psi * np.exp(2j * np.pi * W0 * x / L)
        a4.append({"W0": W0, "W_x_median": int(np.median(row_winding(psiW))), "W_x_rows_equal": float(np.mean(row_winding(psiW) == W0)),
                   "n_v_ratio": float(np.abs(plaquettes(psiW)).sum() / np.abs(q0).sum()), "max_density_change": float(np.abs(np.abs(psiW) ** 2 - rho0).max())})
    res = {"L": L, "N": N, "lambda_dB": LAM, "k0": K0, "n_real": NREAL, "expected_density": expected,
           "A1": {"ratio": float(a1), "density_mean": float(dens.mean()), "density_std": float(dens.std()), "pass": bool(0.85 <= a1 <= 1.15)},
           "A2": {"frac_high_winding": float(np.mean(hi)), "pass": bool(np.mean(hi) < 1e-3)},
           "A3": {"R": Rs, "var_W": var.tolist(), "mean_W": mean.tolist(), "sem_W": sem.tolist(), "alpha": float(alpha), "sem_W_indep": sem_indep.tolist(),
                  "mean_zero_as_written": bool(np.all(np.abs(mean) < 2 * sem)), "mean_zero_indep": bool(np.all(np.abs(mean) < 2 * sem_indep)),
                  "pass_as_written": bool(0.8 <= alpha <= 1.2 and np.all(np.abs(mean) < 2 * sem)),
                  "pass_R4A1": bool(0.8 <= alpha <= 1.2 and np.all(np.abs(mean) < 2 * sem_indep))},
           "A4": a4}
    OUT.mkdir(parents=True, exist_ok=True); (OUT / f"random_phase_halo{os.environ.get('TAG', '')}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k in ("A1", "A2", "A3", "A4")}, indent=1))


if __name__ == "__main__":
    main()
