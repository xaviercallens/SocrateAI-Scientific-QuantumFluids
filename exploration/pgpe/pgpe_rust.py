"""Drop-in replacement of `pgpe.PGPE` whose time stepping runs in the Rust engine of rusty-SUNDIALS (`qf_pgpe` Python extension).

    from pgpe_rust import PGPERust as PGPE          # every script that does `from pgpe import PGPE` now steps in Rust
    s = PGPE(N=128, L=64.0); c = s.run(c, 100.0)    # same arrays, same conventions (numpy fft2, projected amplitudes)

Everything except `run` (and the invariants `norm`, `energy`, `momentum`, which are delegated too) is inherited from the Python class, so the
measurement code (observables.py, round2.py, ...) is unchanged. `run(c, t_end, callback, every)` keeps the contract of PGPE.run: with a
callback, the evolution is chunked in blocks of `every` steps and `callback(t, c)` is called after each block.
The extension is built from `rusty-SUNDIALS/crates/qf-pgpe-py` (`cargo build --release -p qf-pgpe-py`, then copy `libqf_pgpe.so` to `qf_pgpe.so` on PYTHONPATH,
or $QF_PGPE_EXT). Results agree with the numpy engine to ~1e-10 after 20 time units (tests in crates/qf-pgpe-py).
"""
from __future__ import annotations
import os, sys
import numpy as np

ext = os.environ.get("QF_PGPE_EXT")
if ext and ext not in sys.path:
    sys.path.insert(0, ext)
import qf_pgpe
from pgpe import PGPE


class PGPERust(PGPE):
    def __init__(self, N: int = 128, L: float = 64.0, g: float = 1.0, kcut_frac: float = 1 / 2, dt: float = 0.01):
        super().__init__(N=N, L=L, g=g, kcut_frac=kcut_frac, dt=dt)
        self._rust = qf_pgpe.Pgpe(N, L, g, dt, kcut_frac)

    def run(self, c, t_end, callback=None, every: int = 0):
        n = int(round(t_end / self.dt))
        c = np.ascontiguousarray(c, dtype=np.complex128)
        if callback is None or not every:
            return self._rust.run(c, n * self.dt)
        i = 0
        while i < n:
            m = min(every, n - i)
            c = self._rust.run(c, m * self.dt); i += m
            if i % every == 0:
                callback(i * self.dt, c)
        return c

    def norm(self, c): return self._rust.norm(np.ascontiguousarray(c, dtype=np.complex128))
    def energy(self, c): return self._rust.energy(np.ascontiguousarray(c, dtype=np.complex128))
    def momentum(self, c): return np.array(self._rust.momentum(np.ascontiguousarray(c, dtype=np.complex128)))
