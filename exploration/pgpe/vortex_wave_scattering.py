#!/usr/bin/env python3
"""Force of a monochromatic Bogoliubov wave on a quantized vortex, read from the drift of a vortex pair (T = 0).

A vortex-antivortex pair a distance d0 apart along x, in a uniform condensate (psi = 1, n = 1, g = 1) with no thermal cloud, is
dressed with a travelling Bogoliubov wave of wavenumber k along +-y (perpendicular to the separation):
    psi = psi_pair * (1 + eps [u e^{i k y} - v e^{-i k y}]),   u, v = sqrt((e0 + 1)/(2 w) +- 1/2),  e0 = k^2/2, w = sqrt(e0 (e0 + 2)).
A wave of momentum flux j along y exerts on a vortex the force F = c sigma_par j yhat - q c sigma_perp zhat x j (Sonin 1997, Eq. 43); the
Magnus balance turns it into a drift  v_i = q_i zhat x F / (rho kappa): the two vortices of a pair drift in OPPOSITE x directions
(the longitudinal force changes the separation) and, from the transverse force, together along y. Observable: d_x(t) and the centroid
y_c(t) against the no-wave control. With j measured on the same wave without vortices,
    sigma_par = rho kappa |d d_x/dt| / (2 c j),    sigma_perp = rho kappa |d y_c/dt| / (c j)         (c = 1, kappa = 2 pi, rho = 1).

    .venv/bin/python exploration/pgpe/vortex_wave_scattering.py OUT.npz --m 4 --eps 0.05 --dir 1 --t-max 600 [--L 64 --N 128 --d0 32]
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from vortex_transport import detect, imprint_v2, momentum


def bogoliubov_uv(k: float):
    e0 = 0.5 * k * k; w = np.sqrt(e0 * (e0 + 2.0))
    return np.sqrt((e0 + 1.0) / (2 * w) + 0.5), np.sqrt(max((e0 + 1.0) / (2 * w) - 0.5, 0.0)), w


def dress(s: PGPE, c: np.ndarray, m: int, eps: float, direction: int):
    k = 2 * np.pi * m / s.L; u, v, w = bogoliubov_uv(k)
    y = np.arange(s.N) * s.dx; Y = np.tile(y, (s.N, 1)); ph = direction * k * Y      # psi indexed [i (x), j (y)]
    wave = 1.0 + eps * (u * np.exp(1j * ph) - v * np.exp(-1j * ph))
    c2 = s.modes(s.psi(c) * wave)
    return c2 * np.sqrt(s.norm(c) / s.norm(c2)), k, w


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--m", type=int, default=4); ap.add_argument("--eps", type=float, default=0.05); ap.add_argument("--av", type=float, default=0.0, help="if > 0: set eps so that the peak velocity amplitude k eps (u+v) = av")
    ap.add_argument("--dir", type=int, default=1, choices=[1, -1]); ap.add_argument("--t-max", type=float, default=600.0)
    ap.add_argument("--L", type=float, default=64.0); ap.add_argument("--N", type=int, default=128); ap.add_argument("--d0", type=float, default=32.0)
    ap.add_argument("--dt-sample", type=float, default=1.0); ap.add_argument("--r-track", type=float, default=3.0); ap.add_argument("--no-pair", action="store_true")
    a = ap.parse_args(); t0 = time.time(); s = PGPE(N=a.N, L=a.L)
    if a.av > 0:
        k_ = 2 * np.pi * a.m / a.L; u_, v_, _ = bogoliubov_uv(k_); a.eps = a.av / (k_ * (u_ + v_))
    c0 = np.zeros((a.N, a.N), complex); c0[0, 0] = a.N ** 2
    # wave momentum flux on the vortex-free field (same wave): j = P_y / L^2
    cw, k, w = dress(s, c0, a.m, a.eps, a.dir); Pw = momentum(s, cw); j = float(np.hypot(*Pw)) / a.L ** 2
    # energy/phonon content check: the wave is not a vortex-free eigenstate exactly, report the density amplitude
    dens = np.abs(s.psi(cw)) ** 2; amp_rho = float((dens.max() - dens.min()) / 2)
    if a.no_pair:
        pos = np.zeros((0, 2)); q = np.zeros(0, int); c = cw
    else:
        yc = a.L / 2
        x1 = a.L / 2 - a.d0 / 2; x2 = a.L / 2 + a.d0 / 2; pos = np.array([[x1, yc], [x2, yc]]) % a.L; q = np.array([1, -1])
        cp = imprint_v2(s, c0, pos, q); c, k, w = dress(s, cp, a.m, a.eps, a.dir)
    T, R, P, E = [], [], [], []; last = pos.copy(); t = 0.0; ended = "t_max"; E0 = s.energy(c)
    while True:
        if len(q):
            dp, dq = detect(s, c); cur = np.full_like(last, np.nan)
            for i in range(len(q)):
                cand = np.nonzero(dq == q[i])[0]
                if len(cand):
                    d = dp[cand] - last[i]; d -= a.L * np.round(d / a.L); r = np.hypot(d[:, 0], d[:, 1]); jj = int(np.argmin(r))
                    if r[jj] <= a.r_track:
                        cur[i] = dp[cand[jj]]
            if np.isnan(cur).any():
                ended = "track_lost"; break
            R.append(cur.copy()); last = cur
        T.append(t); P.append(momentum(s, c)); E.append(s.energy(c))
        if t >= a.t_max - 1e-9:
            break
        c = s.run(c, a.dt_sample); t += a.dt_sample
    meta = dict(m=a.m, k=float(k), omega=float(w), eps=a.eps, dir=a.dir, L=a.L, N=a.N, d0=a.d0, ended=ended, t_end=t, j=j, amp_rho=amp_rho,
                P_wave_only=Pw.tolist(), drift_E=abs(s.energy(c) - E0) / abs(E0), no_pair=a.no_pair, seconds=round(time.time() - t0, 1))
    np.savez(a.out, t=np.array(T), R=np.array(R), q=q, P=np.array(P), E=np.array(E), meta=json.dumps(meta))
    print(a.out, {kk: meta[kk] for kk in ("k", "eps", "dir", "j", "amp_rho", "ended", "t_end", "drift_E", "seconds")}, flush=True)


if __name__ == "__main__":
    main()
