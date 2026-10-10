"""The code shown in boxes of Chapter 2, verbatim, with the output that the chapter prints.
Run:  PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext  .venv/bin/python book/figures/ch02_snippets.py
(the module of the programme's virtual environment predates the Adams fix: see ch02_compute.py)
The blocks between '# <<< name' and '# >>> name' are pasted into chapters/ch02.tex by the author's splice script."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# <<< snippet1  (CVODE through the Python module, harmonic oscillator, ten periods)
import math
from rusty_sundials import CvodeSolver

calls = 0
def rhs(t, y):
    # x'' = -x written as a first-order system (x, v)
    global calls
    calls += 1
    return [y[1], -y[0]]

T = 20 * math.pi        # ten periods; the exact solution is (cos T, -sin T)
for method in ("adams", "bdf"):
    calls = 0
    # arguments: method, rtol, atol, max_steps
    solver = CvodeSolver(method, 1e-8, 1e-10, 100000)
    t, y = solver.solve(rhs, 0.0, [1.0, 0.0], T)
    err = max(abs(y[0] - math.cos(T)), abs(y[1] + math.sin(T)))
    print(f"{method:5s} rhs calls {calls:6d}  error {err:.2e}")
# >>> snippet1

# <<< snippet2  (the Rust engine against the exact plane wave)
import numpy as np, qf_pgpe

N, L, g, m = 32, 16.0, 1.0, 3
engine = qf_pgpe.Pgpe(N, L, g, 0.01)       # grid, box, coupling, time step
x = np.arange(N) * L / N
X, Y = np.meshgrid(x, x, indexing="ij")
k = 2 * np.pi * m / L
psi0 = np.exp(1j * k * X)                  # one mode, density 1
c = engine.run(np.ascontiguousarray(engine.modes(psi0)), 10.0)
omega = 0.5 * k ** 2 + g                   # omega = k^2/2 + g |a0|^2
exact = psi0 * np.exp(-1j * omega * 10.0)
err = np.abs(engine.psi(c) - exact).max()
print(f"plane wave, t = 10: max |psi - exact| = {err:.2e}")
# >>> snippet2

# <<< snippet3  (the engine's cubic term against a literal transcription of GPGalerkin.nl)
from ch02_compute import bridge_case

cases = ((0.5, True), (0.5, False), (2 / 3, False))
for f, interior in cases:
    r = bridge_case(32, 16.0, 1.0, f, interior, seed=1)
    print(f"cutoff {f:.3f}  modes {r['n_modes']:3d}  "
          f"max|engine-nl|/max|nl| = {r['max_abs_diff_over_max_nl']:.2e}  "
          f"differing: {r['n_modes_differing_1e-12']}")
# >>> snippet3
