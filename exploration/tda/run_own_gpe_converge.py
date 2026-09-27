"""Timestep-convergence control for run_own_gpe.py.

The production run used dt = 0.01, which is ~125x `max_dt` and drifted 2.9% in energy by t = 20 --
it FAILS the solver's own energy control. Before any conclusion is drawn, the quantity of interest
(the floor F, and the vortex count) must be shown independent of dt. Same seed, same everything,
half the timestep.
"""
import json, sys
import numpy as np
sys.path.insert(0, "src")
from quantumfluids.gpe.solver2d import Grid2D, energy, evolve, healing_length, plant_vortices
from quantumfluids.tda.vortex_persistence import extract_vortices, floor_stats

XI = healing_length(1.0); PER_XI = 8; N = 1024; N_V = 200
g = Grid2D(n=N, dx=XI / PER_XI)
out = {"dt_runs": []}
for DT in (0.01, 0.005):
    rng = np.random.default_rng(20260920)
    c = rng.uniform(0, g.L, size=(N_V, 2))
    q = np.array([1, -1] * (N_V // 2))
    psi = plant_vortices(g, c, q)
    psi = evolve(psi, g, dt=-0.02j, n_steps=100, renorm=True)
    e0 = energy(psi, g)
    psi = evolve(psi, g, dt=DT, n_steps=int(20 / DT))
    pts, _ = extract_vortices(psi, g.dx)
    s = floor_stats(pts, XI)
    drift = abs(energy(psi, g) - e0) / abs(e0)
    rec = {"dt": DT, "n": len(pts), "F": s.F, "f_below": s.f_below,
           "mst_mean_over_xi": s.mst_mean_over_xi, "energy_drift": drift}
    out["dt_runs"].append(rec)
    print(f"dt={DT:<7} n={len(pts):>4}  F={s.F:>6.3f} xi  f_<={s.f_below:>5.3f}  "
          f"meanMST={s.mst_mean_over_xi:>5.2f} xi  Edrift={drift:.2e}", flush=True)
a, b = out["dt_runs"]
print(f"\nCONVERGENCE: F {a['F']:.3f} -> {b['F']:.3f} ({abs(b['F']-a['F'])/a['F']*100:.0f}% change), "
      f"n {a['n']} -> {b['n']} ({abs(b['n']-a['n'])/a['n']*100:.0f}%), "
      f"meanMST {a['mst_mean_over_xi']:.2f} -> {b['mst_mean_over_xi']:.2f} "
      f"({abs(b['mst_mean_over_xi']-a['mst_mean_over_xi'])/a['mst_mean_over_xi']*100:.0f}%)")
json.dump(out, open("exploration/tda/results_converge.json", "w"), indent=1)
