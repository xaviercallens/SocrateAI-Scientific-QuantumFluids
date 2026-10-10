"""SUPERSEDED (not run, not used for any number or figure of chapter 5): an earlier single-mode version of the solver measurement,
kept only because it was inherited from an interrupted session; chapter 5 uses figures/ch05_dispersion_run.py (a broadband pulse that measures
all retained modes at once) and figures/ch05_common.py.

Chapter 5 solver measurement (earlier design): the dispersion relation of the projected GPE, measured with the Rust engine qf_pgpe.

Uniform condensate psi = 1 (g = n = m = hbar = 1, so c = 1), plus a weak plane-wave density perturbation
psi = 1 + eps cos(k.x); evolve; read the oscillation of the condensate-frame amplitude of mode k; fit a sinusoid for omega(k).
    PYTHONPATH=/mnt/data/xdev-cache/qf_ext  .venv/bin/python book/figures/ch05_measure.py
Writes book/figures/ch05_measure.json
"""
import json, sys, time
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit
import qf_pgpe

OUT = Path(__file__).resolve().parent / "ch05_measure.json"

def measure(N, L, dt, kcut_frac, mx, my, eps, T, every_steps):
    s = qf_pgpe.Pgpe(N, L, 1.0, dt, kcut_frac)
    x = np.arange(N) * (L / N)
    X, Y = np.meshgrid(x, x, indexing="ij")
    kx, ky = 2 * np.pi * mx / L, 2 * np.pi * my / L
    k = float(np.hypot(kx, ky))
    if k > s.kcut:
        return None
    psi0 = (1.0 + eps * np.cos(kx * X + ky * Y)).astype(complex)
    c = np.ascontiguousarray(s.modes(psi0))
    ts, amp = [], []
    nblocks = int(round(T / (every_steps * dt)))
    for b in range(nblocks):
        c = s.run(c, every_steps * dt)
        # condensate frame: divide out the global phase of c_00
        amp.append((c[mx % N, my % N] * np.conj(c[0, 0]) / abs(c[0, 0])).real)
        ts.append((b + 1) * every_steps * dt)
    ts, amp = np.array(ts), np.array(amp)
    a0 = amp - amp.mean()
    dtc = ts[1] - ts[0]
    sp = np.abs(np.fft.rfft(a0 * np.hanning(len(a0)))); f = np.fft.rfftfreq(len(a0), d=dtc)
    i = int(np.argmax(sp[1:])) + 1
    w0 = 2 * np.pi * f[i]
    model = lambda t, A, w, ph, B: A * np.cos(w * t + ph) + B
    best = None
    for ph0 in (0.0, np.pi / 2, np.pi, -np.pi / 2):
        try:
            p, cov = curve_fit(model, ts, amp, p0=[a0.max(), w0, ph0, amp.mean()], maxfev=20000)
            r = float(np.sqrt(np.mean((model(ts, *p) - amp) ** 2)))
            if best is None or r < best[0]:
                best = (r, p, cov)
        except Exception:
            pass
    r, p, cov = best
    return dict(k=k, mx=mx, my=my, omega=float(abs(p[1])), omega_err=float(np.sqrt(cov[1, 1])), resid=r, amp=float(abs(p[0])), kcut=float(s.kcut))

def bog(k, c=1.0, m=1.0):
    return np.sqrt(c ** 2 * k ** 2 + (k ** 2 / (2 * m)) ** 2)

if __name__ == "__main__":
    res = {"meta": {"units": "hbar=m=g=n=1, c=1", "engine": "qf_pgpe (Rust), IF-RK4"}}
    t0 = time.time()
    # (A) small amplitude, axis-aligned modes, N=128, L=64, kcut = pi (kcut_frac 1/2)
    N, L, dt = 128, 64.0, 0.005
    A = []
    for mx in list(range(1, 33)):
        r = measure(N, L, dt, 0.5, mx, 0, 2e-4, 300.0, 20)
        if r: A.append(r)
    res["A_axis"] = dict(N=N, L=L, dt=dt, eps=2e-4, T=300.0, sample_dt=20 * dt, points=A)
    print("A done", len(A), round(time.time() - t0, 1), "s", flush=True)
    # (B) diagonal modes (m,m): |k| = 2 pi sqrt2 m/L, to reach |k| up to kcut along the diagonal
    B = []
    for m in range(1, 23):
        r = measure(N, L, dt, 0.5, m, m, 2e-4, 300.0, 20)
        if r: B.append(r)
    res["B_diag"] = dict(points=B)
    print("B done", len(B), round(time.time() - t0, 1), "s", flush=True)
    # (C) finite amplitude eps = 0.1 and 0.3, axis modes
    for eps in (0.1, 0.3):
        C = []
        for mx in list(range(1, 33)):
            r = measure(N, L, dt, 0.5, mx, 0, eps, 300.0, 20)
            if r: C.append(r)
        res[f"C_eps{eps}"] = dict(eps=eps, points=C)
        print("C", eps, "done", round(time.time() - t0, 1), "s", flush=True)
    # (D) timestep check at three k (dt halved)
    D = []
    for mx in (4, 16, 30):
        r1 = measure(N, L, 0.0025, 0.5, mx, 0, 2e-4, 300.0, 40)
        D.append(r1)
    res["D_dt_half"] = dict(dt=0.0025, points=D)
    # (E) smaller cutoff: kcut_frac = 1/4 on the same grid (kcut = pi/2): modes above it cannot be excited at all
    E = []
    for mx in list(range(1, 33)):
        r = measure(N, L, dt, 0.25, mx, 0, 2e-4, 300.0, 20)
        E.append(r if r else {"mx": mx, "k": 2 * np.pi * mx / L, "excluded": True})
    res["E_kcut_quarter"] = dict(points=E)
    res["wall_seconds"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(res, indent=1))
    print("wrote", OUT, res["wall_seconds"], "s")
