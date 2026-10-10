"""The code shown in the rusty-SUNDIALS box of Chapter 1, and nothing else: a vortex pair, ten time units, the conserved quantities,
and the winding of the phase around a loop computed exactly as `QuantumFluids.VortexWinding.pdiff` prescribes.
Run:  PYTHONPATH=/mnt/data/xdev-cache/qf_ext  nice .venv/bin/python book/figures/ch01_snippet.py"""
import numpy as np, qf_pgpe

s = qf_pgpe.Pgpe(128, 64.0)     # 128^2 points, box 64 xi; g = 1
pos0 = np.array([[26., 32.], [38., 32.]])   # vortex, antivortex
c0 = s.imprint_v2(s.uniform(), pos0, np.array([1, -1]))
c = s.run(c0, 10.0)             # 1000 RK4 steps in one call
for name, f in (("energy", s.energy), ("norm", s.norm)):
    print(f"{name:6s} t=0 {f(c0):.9f}  t=10 {f(c):.9f}  "
          f"relative drift {abs(f(c) - f(c0)) / f(c0):.1e}")
pos, q = s.detect(c)
print("vortices at t=10:", pos.round(3).tolist(), q.tolist())

def winding(psi, loop):         # loop: grid points, first = last
    th = np.angle([psi[i, j] for i, j in loop])
    d = np.diff(th)
    d -= 2 * np.pi * np.ceil((d - np.pi) / (2 * np.pi))   # pdiff
    return d.sum() / (2 * np.pi), np.abs(d).max()

def ring(i0, j0, h):             # ccw square, half-side h
    up = [(i0 + h, j0 + t) for t in range(-h, h)]
    left = [(i0 + h - t, j0 + h) for t in range(2 * h)]
    down = [(i0 - h, j0 + h - t) for t in range(2 * h)]
    right = [(i0 - h + t, j0 - h) for t in range(2 * h)]
    return up + left + down + right + [(i0 + h, j0 - h)]

psi = np.asarray(s.psi(c))
cases = {"around the vortex": pos[0],
         "around the antivortex": pos[1],
         "empty fluid": (47., 40.)}
for name, centre in cases.items():
    i0, j0 = (int(round(x / 0.5)) for x in centre)
    w, step = winding(psi, ring(i0, j0, 7))
    print(f"{name:22s} winding {w:+.15f}  max step {step:.3f}")
