"""Frames for D0/D1 of KINETIC_TDA_PREREG.md: the run_own_gpe.py configuration (same seed, grid, dt),
saving psi at t = 5, 10, 20, plus a vortex-free control frame."""
import sys
import numpy as np
sys.path.insert(0, "src")
from quantumfluids.gpe.solver2d import Grid2D, evolve, healing_length, plant_vortices, smooth_phase_noise
from quantumfluids.tda.vortex_persistence import extract_vortices

OUT = "data/generated/kinetic_tda"
XI = healing_length(1.0); N = 1024
g = Grid2D(n=N, dx=XI / 8)
rng = np.random.default_rng(20260920)
c = rng.uniform(0, g.L, size=(200, 2)); q = np.array([1, -1] * 100)
psi = evolve(plant_vortices(g, c, q), g, dt=-0.02j, n_steps=100, renorm=True)
t_now = 0
for t in (5, 10, 20):
    psi = evolve(psi, g, dt=0.01, n_steps=int(round((t - t_now) / 0.01))); t_now = t
    np.save(f"{OUT}/psi_t{t}.npy", psi.astype(np.complex128))
    print("saved t =", t, "vortices:", len(extract_vortices(psi, g.dx)[0]), flush=True)

# vortex-free control: sound only.  Smooth phase noise, evolved so phase gradients become density waves.
rng = np.random.default_rng(7)
psi = smooth_phase_noise(g, amp=0.3, k_cut_inv_xi=1.0, rng=rng)
psi = evolve(psi, g, dt=0.01, n_steps=500)
np.save(f"{OUT}/psi_sound_only.npy", psi)
rho = np.abs(psi) ** 2
print("control: vortices by winding =", len(extract_vortices(psi, g.dx)[0]), " density range", rho.min(), rho.max(), flush=True)
