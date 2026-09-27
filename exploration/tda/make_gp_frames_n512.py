"""N=512 (xi/dx=4) counterpart of make_gp_frames.py, same physical domain L=128*xi, same seed, so
the N=512 grid is the literal coarse-grid restriction (every other point) of the N=1024 run's grid."""
import sys
import time
import numpy as np
sys.path.insert(0, "src")
from quantumfluids.gpe.solver2d import Grid2D, evolve, healing_length, plant_vortices
from quantumfluids.tda.vortex_persistence import extract_vortices

OUT = "data/generated/kinetic_tda"
XI = healing_length(1.0); N = 512
g = Grid2D(n=N, dx=XI / 4)
rng = np.random.default_rng(20260920)
c = rng.uniform(0, g.L, size=(200, 2)); q = np.array([1, -1] * 100)

t0 = time.time()
psi = evolve(plant_vortices(g, c, q), g, dt=-0.02j, n_steps=100, renorm=True)
print("relaxation done, elapsed:", time.time() - t0, flush=True)

t_now = 0
for t in (5, 10, 20):
    ts = time.time()
    psi = evolve(psi, g, dt=0.01, n_steps=int(round((t - t_now) / 0.01))); t_now = t
    np.save(f"{OUT}/psi_n512_t{t}.npy", psi.astype(np.complex128))
    print("saved t =", t, "vortices:", len(extract_vortices(psi, g.dx)[0]),
          "elapsed:", time.time() - ts, flush=True)

print("total elapsed:", time.time() - t0, flush=True)
