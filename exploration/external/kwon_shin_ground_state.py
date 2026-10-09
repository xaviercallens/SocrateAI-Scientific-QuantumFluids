#!/usr/bin/env python3
"""Ground-state preparation of the Kwon & Shin reference (Zenodo 10.5281/zenodo.20068724), re-implemented from the description of the
algorithm in src/gpe_dynamics/imag_time_evolv.py and scripts/run_shedding.py (v_init = 0, init = "imaginary"):

  start from the Thomas-Fermi field sqrt(-V') (V' = V - 1), then repeat
      psi <- IFFT[ exp(-k^2 dtau / 2) FFT[psi] ]                                   (kinetic half: heat kernel, v_init = 0)
      psi <- psi exp(-V' dtau) / sqrt(1 + |psi|^2 (1 - exp(-2 V' dtau)) / V')      (exact solution of d psi/d tau = -(V' + |psi|^2) psi)
  until  gamma = int |psi_new - psi_old|^2 dx dy  (trapezoid rule) < eps dtau,  eps = Nx Ny 1e-9,  dtau = 0.04,  at most 25000 steps;
  then add the reference's seeded noise 1e-4 (integers in [-5, 5), real and imaginary parts, default_rng(2026)).

Compares the result with the reference's own psi_time_0.0.npy. The point of the comparison is what it says about the PREPARATION, which the
real-time comparison (kwon_shin_reproduction.py) skips by starting from the reference's field.

    .venv/bin/python exploration/external/kwon_shin_ground_state.py [--save OUT.npy]
"""
from __future__ import annotations
import argparse, time
import numpy as np

NX, NY, RX, RY = 1000, 500, 250, 125
DX, DY = 2 * RX / NX, 2 * RY / NY
OBST, SIGMA, V0 = 100, 20, 0.9
DTAU, EPS, NTAU = 0.04, NX * NY * 10e-10, 25000
REF = "/mnt/data/xdev-cache/qf-external/20068724/extracted/psi_time_0.0.npy"


def compare(psi):
    rng = np.random.default_rng(seed=2026)
    noise = 1e-4 * (rng.integers(-5, 5, size=(NY, NX)) + 1j * rng.integers(-5, 5, size=(NY, NX)))
    ref = np.load(REF).astype(complex)
    for lab, p in (("without noise", psi), ("with the reference's seeded noise", psi + noise)):
        d = p - ref
        print(f"{lab:36s}: relative L2 distance to psi_time_0.0 = {np.linalg.norm(d) / np.linalg.norm(ref):.3e}, max |d psi| = {np.abs(d).max():.3e}, "
              f"max | |psi|^2 difference | = {np.abs(np.abs(p) ** 2 - np.abs(ref) ** 2).max():.3e}")
    print("reference noise level 1e-4 * (up to 5 + 5i): rms of the noise =", f"{np.sqrt(np.mean(np.abs(noise) ** 2)):.3e}")
    return noise


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--save", default=None); ap.add_argument("--rust", default=None, help="noise-free field written by the Rust example kwon_shin_ground: compare it instead of preparing one"); a = ap.parse_args()
    x = np.arange(-RX, RX, DX); y = np.arange(-RY, RY, DY); xx, yy = np.meshgrid(x, y)
    vp = V0 * np.exp(-2 * ((xx - OBST) ** 2 + yy ** 2) / SIGMA ** 2) - 1.0
    kx = np.fft.fftfreq(NX, DX) * 2 * np.pi; ky = np.fft.fftfreq(NY, DY) * 2 * np.pi; KX, KY = np.meshgrid(kx, ky)
    heat = np.exp(-(KX ** 2 + KY ** 2) / 2 * DTAU)
    temp = (1 - np.exp(-2 * vp * DTAU)) / vp; damp = np.exp(-vp * DTAU)
    psi = np.zeros((NY, NX), complex); m = vp < 0; psi[m] = np.sqrt(-vp[m])
    if a.rust:
        return compare(np.load(a.rust).astype(complex))
    t0 = time.time(); g0 = 1e10; steps = 0; why = "exhausted"
    for i in range(NTAU):
        old = psi
        p1 = np.fft.ifft2(heat * np.fft.fft2(psi))
        psi = np.nan_to_num(p1 * damp / np.sqrt(1 + np.abs(p1) ** 2 * temp)); steps = i + 1
        gamma = float(np.trapezoid(np.trapezoid(np.abs(psi - old) ** 2, x), y))
        if gamma > g0:
            why = "gamma increased"; break
        if gamma < EPS * DTAU:
            why = "converged"; break
        g0 = gamma
        if i % 500 == 0:
            print(f"tau={i * DTAU:7.2f} gamma={gamma:.3e} ({time.time() - t0:.0f} s)", flush=True)
    print(f"{why} after {steps} steps (tau = {steps * DTAU:.2f}), gamma = {gamma:.3e}, threshold {EPS * DTAU:.3e}, {time.time() - t0:.0f} s")
    noise = compare(psi)
    if a.save:
        np.save(a.save, psi + noise)


if __name__ == "__main__":
    main()
