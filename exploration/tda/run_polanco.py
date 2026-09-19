"""Workstream T on real data: Zenodo 5510351 (Polanco/Muller/Krstulovic 256^3 generalised-GP snapshot).

Pre-registration: docs/designs/TDA_VORTEX_FLOOR.md (sections 1-6, incl. the two caveats in section 6).
Periodic box, xi = 1.5 dx (authors' convention). Writes results_polanco.json.
"""
import json, sys, time
import numpy as np
sys.path.insert(0, "src")
from quantumfluids.tda.vortex_persistence import (
    extract_vortex_points_3d, line_floor_stats, periodic_inter_line_distances,
    periodic_segment_lines, random_shift_null)

D = "data/external/polanco_2021_gp_turbulence/"
N, L = 256, 2 * np.pi
dx = L / N
XI = 1.5 * dx
print(f"grid {N}^3, L = {L:.4f}, dx = {dx:.6f}, xi = 1.5 dx = {XI:.6f}, box = {L/XI:.1f} xi")

t = time.time()
psi = (np.fromfile(D + "ReaPsi.001.dat", dtype="<f8").reshape(N, N, N, order="F")
       + 1j * np.fromfile(D + "ImaPsi.001.dat", dtype="<f8").reshape(N, N, N, order="F"))
pts = extract_vortex_points_3d(psi, dx)
print(f"vortex points: {len(pts)}  ({time.time()-t:.0f}s)")
del psi

res = {"grid": N, "L": L, "dx": dx, "xi": XI, "box_over_xi": L / XI, "n_vortex_points": len(pts)}

# raw point cloud -- reported ONLY to show it is the artefact the design predicted
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import cKDTree
tree = cKDTree(np.mod(pts, L), boxsize=L)
dnn, _ = tree.query(np.mod(pts, L), k=2)
res["raw_pointcloud_min_nn_over_xi"] = float(np.min(dnn[:, 1]) / XI)
res["raw_pointcloud_min_nn_over_dx"] = float(np.min(dnn[:, 1]) / dx)
print(f"RAW point cloud (artefact): min NN = {res['raw_pointcloud_min_nn_over_xi']:.3f} xi "
      f"= {res['raw_pointcloud_min_nn_over_dx']:.3f} dx  <- measures the grid, as designed-for")

for lr_cells in (1.5, 2.0, 3.0):
    labels = periodic_segment_lines(pts, link_radius=lr_cells * dx, L=L)
    n_lines = len(np.unique(labels))
    sizes = np.bincount(labels)
    rec = {"link_radius_cells": lr_cells, "n_lines": n_lines,
           "largest_component_frac": float(sizes.max() / len(pts)),
           "n_components_above_10_points": int((sizes > 10).sum())}
    print(f"link_radius {lr_cells} dx -> {n_lines} components, largest holds "
          f"{rec['largest_component_frac']*100:.1f}% of points, {rec['n_components_above_10_points']} with >10 points")
    res.setdefault("segmentation", []).append(rec)

LR = 2.0 * dx
labels = periodic_segment_lines(pts, link_radius=LR, L=L)
sizes = np.bincount(labels)
keep = np.isin(labels, np.flatnonzero(sizes > 10))          # drop specks below 10 points
pts_k, lab_k = pts[keep], labels[keep]
print(f"\nkeeping components with >10 points: {len(np.unique(lab_k))} lines, {len(pts_k)} points")
t = time.time()
Dm = periodic_inter_line_distances(pts_k, lab_k, L)
stats = line_floor_stats(Dm, XI)
print(f"LINE GRAPH ({time.time()-t:.0f}s): n_lines={stats['n_lines']}  F={stats['F']:.3f} xi  "
      f"f_<={stats['f_below']:.3f}  mean MST={stats['mst_mean_over_xi']:.2f} xi")
res["line_graph"] = {k: v for k, v in stats.items() if k != "mst_edges_over_xi"}
res["line_graph"]["mst_edges_over_xi_sorted"] = stats["mst_edges_over_xi"][:20]

rng = np.random.default_rng(20260920)
t = time.time()
null = random_shift_null(pts_k, lab_k, L, XI, reps=30, rng=rng)
print(f"RANDOM-SHIFT NULL ({time.time()-t:.0f}s): F mean {null['F']['mean']:.3f} "
      f"[p05 {null['F']['p05']:.3f}, p95 {null['F']['p95']:.3f}, min {null['F']['min']:.3f}]  "
      f"f_< mean {null['f_below']['mean']:.3f}  mean MST {null['mst_mean_over_xi']['mean']:.2f} xi")
res["random_shift_null"] = null
json.dump(res, open("exploration/tda/results_polanco.json", "w"), indent=1)
print("\nwritten: exploration/tda/results_polanco.json")
