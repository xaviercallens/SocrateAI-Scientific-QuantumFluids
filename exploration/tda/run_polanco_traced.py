"""Workstream T, second attempt: threshold-free topological line tracing (memo section 10.4, fix 2).

The first run was confounded because proximity segmentation imposed the floor it measured.
Here line identity comes from cube adjacency, so there is NO parameter for the floor to track.
"""
import json, sys, time
import numpy as np
sys.path.insert(0, "src")
from quantumfluids.tda.vortex_persistence import (
    line_floor_stats, periodic_inter_line_distances, random_shift_null, trace_lines)

D = "data/external/polanco_2021_gp_turbulence/"
N, L = 256, 2 * np.pi
dx = L / N; XI = 1.5 * dx
psi = (np.fromfile(D + "ReaPsi.001.dat", dtype="<f8").reshape(N, N, N, order="F")
       + 1j * np.fromfile(D + "ImaPsi.001.dat", dtype="<f8").reshape(N, N, N, order="F"))
t = time.time()
pts, labels, diag = trace_lines(psi, dx); del psi
print(f"traced in {time.time()-t:.0f}s: {diag}")

sizes = np.bincount(labels)
keep = np.isin(labels, np.flatnonzero(sizes > 10))
pts_k, lab_k = pts[keep], labels[keep]
n_lines = len(np.unique(lab_k))
print(f"components: {len(sizes)} total, {n_lines} with >10 faces "
      f"(largest {sizes.max()/len(labels)*100:.1f}% of faces)")

res = {"xi": XI, "dx": dx, "diagnostics": diag, "n_components_total": int(len(sizes)),
       "n_lines_kept": int(n_lines), "largest_frac": float(sizes.max() / len(labels))}
if n_lines >= 2:
    t = time.time()
    Dm = periodic_inter_line_distances(pts_k, lab_k, L)
    s = line_floor_stats(Dm, XI)
    print(f"LINE GRAPH ({time.time()-t:.0f}s): n_lines={s['n_lines']} F={s['F']:.3f} xi "
          f"f_<={s['f_below']:.3f} meanMST={s['mst_mean_over_xi']:.2f} xi")
    res["line_graph"] = {k: v for k, v in s.items() if k != "mst_edges_over_xi"}
    res["line_graph"]["first_10_mst_over_xi"] = s["mst_edges_over_xi"][:10]
    rng = np.random.default_rng(20260920)
    null = random_shift_null(pts_k, lab_k, L, XI, reps=20, rng=rng)
    print(f"RANDOM-SHIFT NULL: F {null['F']['mean']:.3f} [p05 {null['F']['p05']:.3f}, "
          f"p95 {null['F']['p95']:.3f}]  f_< {null['f_below']['mean']:.3f}")
    res["random_shift_null"] = null
    print(f"\nSEPARATION FROM NULL: data F = {s['F']:.3f} vs null p95 = {null['F']['p95']:.3f} "
          f"-> {s['F']/null['F']['p95']:.1f}x")
else:
    print("FEWER THAN 2 LINES -- the tangle is one percolating component; floor undefined.")
json.dump(res, open("exploration/tda/results_polanco_traced.json", "w"), indent=1)
