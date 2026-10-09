"""Reproduction of the reference numerics of Kwon & Shin, "Dynamic similarity of vortex shedding in a superfluid flowing past a penetrable obstacle"
(Phys. Rev. Research 2026; Zenodo 10.5281/zenodo.20068724, CC-BY-4.0) with an INDEPENDENT scheme: explicit RK4 on the full right-hand side with spectral
derivatives, started from the reference's own t = 0 wave function.

Model recovered from the reference code (src/gpe_dynamics/time_evolv_GPU.py, units hbar = m = 1, mu = 1, length xi, time tau = hbar/mu):
    d psi/dt = v(t) d_x psi - (i + Gamma(x,y)) [ -1/2 lap + |psi|^2 - 1 ] psi - i V(x,y) psi            (obstacle frame; V treated unitary as in the reference)
    V = V0 exp(-2 ((x - x_obs)^2 + y^2) / sigma^2),   Gamma = gamma0 * max( (2 + tanh((x-Wx1)/15) - tanh((x-Wx2)/15))/2, same in y ),
    v(t) = v_fin min(t / t_acc, 1)  (t_acc = 0.1 tau);  grid Nx x Ny = 1000 x 500, dx = 0.5, box 500 x 250 xi, periodic FFT.
Observable compared: force_x(t) = int dV/dx |psi|^2 over the interior |x| < 200, |y| < 85 (np.gradient, trapezoid), and psi(t) snapshots.
    .venv/bin/python exploration/external/kwon_shin_reproduction.py --t-end 2 [--dt 0.01]
"""
from __future__ import annotations
import argparse, io, json, time, zipfile
from pathlib import Path
import numpy as np

ZIP = Path("/mnt/data/xdev-cache/qf-external/20068724/Vortex-shedding-PRR-data-1.0.0.zip"); P = "Vortex-shedding-PRR-data-1.0.0/"
CASE = P + "outputs/Nx = 1000 Ny = 500 dt=0.010 obstacle=100/V0=0.9 sigma=20 v=0.550 dt = 0.0100 GPU/"
Nx, Ny, Rx, Ry = 1000, 500, 250.0, 125.0; dx = 2 * Rx / Nx; dy = 2 * Ry / Ny
V0, SIG, XOBS, VFIN, TACC, G0, WX, WY = 0.9, 20.0, 100.0, 0.55, 0.1, 0.1, 50.0, 40.0
x = np.arange(-Rx, Rx, dx); y = np.arange(-Ry, Ry, dy); xx, yy = np.meshgrid(x, y)
kx = 2 * np.pi * np.fft.fftfreq(Nx, dx); ky = 2 * np.pi * np.fft.fftfreq(Ny, dy); KX, KY = np.meshgrid(kx, ky); K2 = KX ** 2 + KY ** 2
V = V0 * np.exp(-2 * ((xx - XOBS) ** 2 + yy ** 2) / SIG ** 2)
Wx1, Wx2, Wy1, Wy2 = Rx - WX, -(Rx - WX), Ry - WY, -(Ry - WY)
gx = G0 * (2 + np.tanh((xx - Wx1) / 15) - np.tanh((xx - Wx2) / 15)) / 2; gy = G0 * (2 + np.tanh((yy - Wy1) / 15) - np.tanh((yy - Wy2) / 15)) / 2
GAM = np.where(gx > gy, gx, gy)
xmin, xmax = int(np.where(x == Wx2)[0][0]), int(np.where(x == Wx1)[0][0]); ymin, ymax = int(np.where(y == Wy2)[0][0]), int(np.where(y == Wy1)[0][0])
CROPV = V[ymin:ymax, xmin:xmax]; DVX = np.gradient(CROPV, dx, axis=1); XC = x[xmin:xmax]; YC = y[ymin:ymax]


def rhs(psi, v):
    ph = np.fft.fft2(psi)
    lap = np.fft.ifft2(-K2 * ph); dxpsi = np.fft.ifft2(1j * KX * ph)
    return v * dxpsi - (1j + GAM) * (-0.5 * lap + (np.abs(psi) ** 2 - 1.0) * psi) - 1j * V * psi


RAMP_RIGHT = False   # the reference evaluates v at the END of each step (time_evolv(tt), tt = i dt for the step ending at i dt) and holds it for the step


def vel(t): return min(VFIN * t / TACC, VFIN)


def force_x(psi): return float(np.trapezoid(np.trapezoid(DVX * np.abs(psi[ymin:ymax, xmin:xmax]) ** 2, XC, axis=1), YC))


def step(psi, t, dt):
    if RAMP_RIGHT:
        v = vel(t + dt); k1 = rhs(psi, v); k2 = rhs(psi + 0.5 * dt * k1, v); k3 = rhs(psi + 0.5 * dt * k2, v); k4 = rhs(psi + dt * k3, v)
        return psi + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    k1 = rhs(psi, vel(t)); k2 = rhs(psi + 0.5 * dt * k1, vel(t + 0.5 * dt)); k3 = rhs(psi + 0.5 * dt * k2, vel(t + 0.5 * dt)); k4 = rhs(psi + dt * k3, vel(t + dt))
    return psi + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--t-end", type=float, default=2.0); ap.add_argument("--dt", type=float, default=0.01); ap.add_argument("--out", default=None); ap.add_argument("--ramp-right", action="store_true"); a = ap.parse_args()
    global RAMP_RIGHT; RAMP_RIGHT = a.ramp_right
    z = zipfile.ZipFile(ZIP); psi = np.load(io.BytesIO(z.read(CASE + "Psi/psi_time_0.0.npy"))).astype(np.complex128)
    ref_force = np.loadtxt(io.StringIO(z.read(CASE + "Force/force_dt=0.02.txt").decode())); ref = {float(round(t, 3)): f for t, f, *_ in ref_force}
    snaps = {t: np.load(io.BytesIO(z.read(CASE + f"Psi/psi_time_{t:.1f}.npy"))).astype(np.complex128) for t in (10.0, 20.0, 30.0, 40.0, 50.0) if t <= a.t_end + 1e-9}
    n = int(round(a.t_end / a.dt)); t0 = time.time(); rows = []; psi_t = psi.copy()
    for i in range(n + 1):
        t = i * a.dt
        if i % int(round(0.1 / a.dt)) == 0:
            f = force_x(psi_t); fr = ref.get(round(t, 3)); rows.append((t, f, fr))
        if t in snaps or round(t, 1) in snaps and abs(round(t, 1) - t) < 1e-9:
            s = snaps[round(t, 1)]; print(f"t = {t:5.1f}: relative L2 difference of psi vs reference {np.linalg.norm(psi_t - s) / np.linalg.norm(s):.3e}  max |dpsi| {np.abs(psi_t - s).max():.3e}", flush=True)
        if i < n: psi_t = step(psi_t, t, a.dt)
        if i % 100 == 0: print(f"  step {i}/{n}  t={t:.2f}  {time.time() - t0:.0f}s", flush=True)
    d = np.array([[t, f, fr] for t, f, fr in rows if fr is not None])
    print("force_x(t): max |ours - reference| over t <= %.1f: %.3e (reference range %.3f .. %.3f); relative to max |F|: %.2e" % (a.t_end, np.abs(d[:, 1] - d[:, 2]).max(), d[:, 2].min(), d[:, 2].max(), np.abs(d[:, 1] - d[:, 2]).max() / np.abs(d[:, 2]).max()))
    if a.out: json.dump(dict(t_end=a.t_end, dt=a.dt, force=d.tolist()), open(a.out, "w"))


if __name__ == "__main__":
    main()
