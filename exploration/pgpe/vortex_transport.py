#!/usr/bin/env python3
"""Instrument v2 of PGPE_FRICTION_PREREG.md amendment A1: imprint a zero-net-impulse (or single-dipole) vortex
configuration into a thermal or T = 0 field, evolve the projected GPE, and save the sub-grid positions of the
imprinted vortices every time unit, with the field momentum.

    .venv/bin/python exploration/pgpe/vortex_transport.py BASE|T0 OUT.npz --geom antiparallel|dipole --d0 10 --t-max 400 [--seed 0] [--L 64 --N 128]

Detection: raw phase winding (lean_src/VortexWinding.lean), no coarse-graining. Refinement: zero of the
least-squares plane through psi at the four corners of the winding plaquette. Tracking: same sign, nearest
detection within r_track of the previous position; the run ends when a tracked vortex is lost or any tracked
vortex and antivortex come within d_stop."""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from round2 import imprint
from transport_estimators import antiparallel, min_opposite_distance


def detect(s: PGPE, c: np.ndarray):
    """Raw plaquette vortices with sub-grid refinement: (pos (n, 2), q (n,))."""
    psi = np.fft.ifft2(c); th = np.angle(psi)
    pv = lambda d: (d + np.pi) % (2 * np.pi) - np.pi
    dx_ = pv(np.roll(th, -1, axis=0) - th); dy_ = pv(np.roll(th, -1, axis=1) - th)
    w = dx_ + np.roll(dy_, -1, axis=0) - np.roll(dx_, -1, axis=1) - dy_
    qg = np.rint(w / (2 * np.pi)).astype(int); ii, jj = np.nonzero(qg)
    N = s.N; p00 = psi[ii, jj]; p10 = psi[(ii + 1) % N, jj]; p01 = psi[ii, (jj + 1) % N]; p11 = psi[(ii + 1) % N, (jj + 1) % N]
    b = 0.5 * ((p10 - p00) + (p11 - p01)); cc = 0.5 * ((p01 - p00) + (p11 - p10)); a = 0.25 * (p00 + p10 + p01 + p11) - 0.5 * (b + cc)
    det = b.real * cc.imag - b.imag * cc.real
    det = np.where(np.abs(det) < 1e-14, 1e-14, det)
    u = (-a.real * cc.imag + a.imag * cc.real) / det; v = (-b.real * a.imag + b.imag * a.real) / det
    u = np.clip(u, -0.5, 1.5); v = np.clip(v, -0.5, 1.5)
    return np.column_stack([(ii + u) * s.dx, (jj + v) * s.dx]) % s.L, qg[ii, jj]


def imprint_v2(s: PGPE, c: np.ndarray, pos: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Imprint with (a) a periodic phase for ANY dipole moment and (b) the quasi-static (Bernoulli) density.

    (a) The theta-function product of round2.imprint is periodic only when sum q r lies in L Z^2; otherwise it
        jumps by a constant across a box boundary (2 pi D_x / L across Y for tau = i). The jump across each
        boundary is measured on the phase factor itself and removed by a uniform phase gradient (the uniform
        counterflow of the torus), minimal sector.
    (b) Amplitude sqrt(1/(1 + |v|^2/2)) with v the velocity of the imprinted phase: zero at the cores, and
        1 - v^2/2 (Bernoulli, c = 1) far from them, so that a neutral configuration removes little density
        (round2.imprint's per-vortex factor r^2/(r^2+2) has a 1/r^2 tail: 21 % of the box for 24 vortices)."""
    from round2 import theta1
    x = np.arange(s.N) * s.dx; X, Y = np.meshgrid(x, x, indexing="ij")

    def factor(Zs):
        ph = np.ones(Zs.shape, complex)
        for (xj, yj), qj in zip(pos, q):
            t = theta1(np.pi * (Zs - (xj + 1j * yj)) / s.L); u = t / (np.abs(t) + 1e-300); ph = ph * (u if qj > 0 else np.conj(u))
        return ph
    Z = X + 1j * Y; ph = factor(Z)
    jx = np.angle(np.mean(factor(Z + s.L) * np.conj(ph))); jy = np.angle(np.mean(factor(Z + 1j * s.L) * np.conj(ph)))
    ph = ph * np.exp(-1j * (jx * X + jy * Y) / s.L)
    vx = np.angle(np.roll(ph, -1, 0) * np.conj(np.roll(ph, 1, 0))) / (2 * s.dx); vy = np.angle(np.roll(ph, -1, 1) * np.conj(np.roll(ph, 1, 1))) / (2 * s.dx)
    amp = np.sqrt(1.0 / (1.0 + 0.5 * (vx ** 2 + vy ** 2)))
    c2 = s.modes(s.psi(c) * ph * amp)
    return c2 * np.sqrt(s.norm(c) / s.norm(c2))


def momentum(s: PGPE, c: np.ndarray, kmin: float = 0.0) -> np.ndarray:
    w = np.abs(c) ** 2 * s.dx ** 2 / s.N ** 2
    if kmin > 0:
        w = w * (np.sqrt(s.k2) > kmin)
    return np.array([float((s.kx * w).sum()), float((s.ky * w).sum())])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base"); ap.add_argument("out")
    ap.add_argument("--geom", default="antiparallel", choices=["antiparallel", "dipole"])
    ap.add_argument("--d0", type=float, default=10.0); ap.add_argument("--t-max", type=float, default=400.0)
    ap.add_argument("--N", type=int, default=128); ap.add_argument("--L", type=float, default=64.0)
    ap.add_argument("--dt-sample", type=float, default=1.0); ap.add_argument("--r-track", type=float, default=3.0)   # 1.5 until amendment A1.2
    ap.add_argument("--d-stop", type=float, default=1.5); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--imprint", default="v2", choices=["v1", "v2"], help="v1 = round2.imprint (first G1 run); v2 = periodic phase + Bernoulli density")
    ap.add_argument("--kcut-frac", type=float, default=0.5, help="projector cutoff as a fraction of the grid wavenumber (friction-law campaign: 1/3, 1/2)")
    ap.add_argument("--nk-every", type=float, default=0.0, help="save the occupation spectrum |c_k|^2 every this many time units (0 = never; counterflow C3)")
    a = ap.parse_args(); t0 = time.time()
    s = PGPE(N=a.N, L=a.L, kcut_frac=a.kcut_frac); rng = np.random.default_rng(a.seed)
    if a.base == "T0":
        c0 = np.zeros((a.N, a.N), complex); c0[0, 0] = a.N ** 2                 # psi = 1: uniform condensate, n = 1
    else:
        c0 = np.load(a.base)
    n_raw_base = int(len(detect(s, c0)[1]))
    if a.geom == "antiparallel":
        pos, q = antiparallel(a.L, a.d0, rng)
    else:
        x0, y0 = rng.uniform(0, a.L, 2)
        pos = np.mod(np.array([[x0 + a.d0 / 2, y0], [x0 - a.d0 / 2, y0]]), a.L); q = np.array([1, -1])
    P_base = momentum(s, c0); c = (imprint if a.imprint == 'v1' else imprint_v2)(s, c0, pos, q); E0 = s.energy(c)
    T, R, ND, P, PH = [], [], [], [], []; last = pos.copy(); t = 0.0; ended = "t_max"
    NKT, NK = [], []                                                       # occupation spectra (times, |c_k|^2 as float32)
    while True:
        if a.nk_every > 0 and (len(NKT) == 0 or t >= NKT[-1] + a.nk_every - 1e-9):
            NKT.append(t); NK.append((np.abs(c) ** 2 / s.N ** 4).astype(np.float32))   # |psi_k|^2 per mode, sum = mean density
        dp, dq = detect(s, c); cur = np.full_like(last, np.nan)
        for i in range(len(q)):
            cand = np.nonzero(dq == q[i])[0]
            if len(cand):
                d = dp[cand] - last[i]; d -= a.L * np.round(d / a.L); r = np.hypot(d[:, 0], d[:, 1]); j = int(np.argmin(r))
                if r[j] <= a.r_track or (t == 0.0 and r[j] <= 3.0):
                    cur[i] = dp[cand[j]]
        if np.isnan(cur).any():
            ended = "track_lost"; break
        T.append(t); R.append(cur.copy()); ND.append(len(dq)); P.append(momentum(s, c)); PH.append(momentum(s, c, 1.0)); last = cur
        if min_opposite_distance(cur, q, a.L) < a.d_stop:
            ended = "annihilated"; break
        if t >= a.t_max - 1e-9:
            break
        c = s.run(c, a.dt_sample); t += a.dt_sample
    meta = {"base": a.base, "geom": a.geom, "d0": a.d0, "seed": a.seed, "L": a.L, "N": a.N, "ended": ended, "t_end": t,
            "n_raw_base": n_raw_base, "P_base": P_base.tolist(), "E_imprinted": E0, "drift_E": abs(s.energy(c) - E0) / abs(E0),
            "pos0": pos.tolist(), "q": q.tolist(), "imprint": a.imprint, "r_track": a.r_track, "kcut_frac": a.kcut_frac,
            "kcut": float(s.kcut), "seconds": round(time.time() - t0, 1)}
    extra = {"nk_t": np.array(NKT), "nk": np.array(NK)} if NK else {}
    np.savez(a.out, t=np.array(T), R=np.array(R), q=q, n_det=np.array(ND), P=np.array(P), P_hi=np.array(PH), meta=json.dumps(meta), **extra)
    print(a.out, {k: meta[k] for k in ("ended", "t_end", "n_raw_base", "drift_E", "seconds")}, flush=True)


if __name__ == "__main__":
    main()
