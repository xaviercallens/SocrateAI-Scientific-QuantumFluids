"""TDA floor test on our OWN well-resolved 2D GPE run (TDA_VORTEX_FLOOR.md, amendment A3).

Motivation: the dataset survey (2026-09-20) found NO public dilute-BEC data with xi/dx >= 5; the best
were 2.26 (2D) and 1.73 (3D), both within ~1.5x of the 1.5 that already made the measurement
inconclusive. So the resolution requirement is met by simulating instead.

Here xi/dx = 8, so the grid artefact scale (0.707 dx = 0.088 xi) sits a factor ~11 below xi. A floor
at ~xi is 8 cells wide and cannot be confused with the discretisation -- which is exactly what
failed before. Predictions and controls are the pre-registered ones (T1-T4', C-NEG, C-RES).

ERRATUM (found 2026-09-20 when the convergence run disagreed with this one): the stage loop below
advances FIVE time units per stage regardless of the label, so the rows printed as t = 5, 10, 20
are really t = 5, 10, 15. The archived results_own_gpe.json carries the wrong labels; the numbers
are right for t = 15. Fixed here so a re-run is labelled correctly.
"""
import json, sys, time
import numpy as np
sys.path.insert(0, "src")
from quantumfluids.gpe.solver2d import Grid2D, energy, evolve, healing_length, plant_vortices
from quantumfluids.tda.vortex_persistence import extract_vortices, floor_stats, poisson_null

XI = healing_length(1.0)
PER_XI = 8
N = 1024
g = Grid2D(n=N, dx=XI / PER_XI)
N_V = 200                      # 100 pairs -> mean spacing ~ L/sqrt(N_V) = 9 xi
rng = np.random.default_rng(20260920)
print(f"grid {N}^2, dx = xi/{PER_XI}, L = {g.L/XI:.1f} xi, planting {N_V} vortices")

c = rng.uniform(0, g.L, size=(N_V, 2))
q = np.array([1, -1] * (N_V // 2))
psi = plant_vortices(g, c, q)
psi = evolve(psi, g, dt=-0.02j, n_steps=100, renorm=True)      # tau = 2: form cores
e0 = energy(psi, g)

res = {"grid": N, "dx_over_xi": 1.0 / PER_XI, "xi_over_dx": PER_XI, "L_over_xi": g.L / XI,
       "n_planted": N_V, "stages": []}

DT = 0.01
t_now = 0
for t_target in (0, 5, 10, 20):
    if t_target > 0:
        steps = int(round((t_target - t_now) / DT))
        t_now = t_target
        t0 = time.time()
        psi = evolve(psi, g, dt=DT, n_steps=steps)
        el = time.time() - t0
    else:
        el = 0.0
    pts, ch = extract_vortices(psi, g.dx)
    s = floor_stats(pts, XI)
    drift = abs(energy(psi, g) - e0) / abs(e0)
    rec = {"t": t_target, "n_vortices": len(pts), "F": s.F, "f_below": s.f_below,
           "mst_mean_over_xi": s.mst_mean_over_xi, "L1_over_xi": s.L1_over_xi,
           "energy_drift": drift, "sec": round(el, 1)}
    res["stages"].append(rec)
    print(f"  t={t_target:>3}  n={len(pts):>4}  F={s.F:>6.3f} xi  f_<={s.f_below:>5.3f}  "
          f"meanMST={s.mst_mean_over_xi:>5.2f} xi  L1={s.L1_over_xi:>5.2f}  Edrift={drift:.2e}")

pts, _ = extract_vortices(psi, g.dx)
final = floor_stats(pts, XI)
res["final"] = final.as_dict()

# C-NEG: matched-count Poisson null, identical pipeline
null = poisson_null(n=len(pts), box=(g.L, g.L), xi=XI, reps=60, rng=rng)
res["poisson_null"] = null
print(f"\nC-NEG  n={len(pts)}: null F mean {null['F']['mean']:.3f} "
      f"[p05 {null['F']['p05']:.3f}, p95 {null['F']['p95']:.3f}]  f_< {null['f_below']['mean']:.3f}")
print(f"DATA:            F = {final.F:.3f} xi   f_< = {final.f_below:.3f}")
print(f"SEPARATION: F/null_p95 = {final.F/null['F']['p95']:.1f}x")

# C-RES: re-extract from a 2x coarsened field (xi/dx = 4). If F tracks the grid it must halve.
psi_c = psi[::2, ::2]
g_c = Grid2D(n=N // 2, dx=g.dx * 2)
pts_c, _ = extract_vortices(psi_c, g_c.dx)
s_c = floor_stats(pts_c, XI)
res["C_RES_coarse"] = {"xi_over_dx": PER_XI // 2, "n_vortices": len(pts_c), "F": s_c.F,
                       "f_below": s_c.f_below}
print(f"C-RES  xi/dx {PER_XI} -> {PER_XI//2}: n {len(pts)} -> {len(pts_c)}, "
      f"F {final.F:.3f} -> {s_c.F:.3f} xi  ({abs(s_c.F-final.F)/final.F*100:.1f}% change)")

json.dump(res, open("exploration/tda/results_own_gpe.json", "w"), indent=1)
print("\nwritten: exploration/tda/results_own_gpe.json")
