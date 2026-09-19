"""CONFOUND CHECK, not in the original design: does the measured floor F merely track the
segmentation threshold?

Distinct components are by construction separated by more than `link_radius`, so segmentation
imposes F > link_radius automatically. The first run used link_radius = 2 dx = 1.333 xi and
measured F = 1.491 xi -- only 12% above its own threshold. That is not yet evidence of physics.

Signature of an artefact: F tracks link_radius.   Signature of physics: F saturates.
"""
import json, sys
import numpy as np
sys.path.insert(0, "src")
from quantumfluids.tda.vortex_persistence import (
    extract_vortex_points_3d, line_floor_stats, periodic_inter_line_distances,
    periodic_segment_lines)

D = "data/external/polanco_2021_gp_turbulence/"
N, L = 256, 2 * np.pi
dx = L / N; XI = 1.5 * dx
psi = (np.fromfile(D + "ReaPsi.001.dat", dtype="<f8").reshape(N, N, N, order="F")
       + 1j * np.fromfile(D + "ImaPsi.001.dat", dtype="<f8").reshape(N, N, N, order="F"))
pts = extract_vortex_points_3d(psi, dx); del psi

print(f"{'lr/dx':>6} {'lr/xi':>7} {'n_lines':>8} {'F/xi':>7} {'F/lr':>7} {'margin':>8} {'meanMST/xi':>11}")
rows = []
for lr_cells in (1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0, 4.0):
    lr = lr_cells * dx
    lab = periodic_segment_lines(pts, link_radius=lr, L=L)
    sizes = np.bincount(lab)
    keep = np.isin(lab, np.flatnonzero(sizes > 10))
    if len(np.unique(lab[keep])) < 2:
        continue
    s = line_floor_stats(periodic_inter_line_distances(pts[keep], lab[keep], L), XI)
    F = s["F"]; margin = F / (lr / XI)
    rows.append({"lr_over_dx": lr_cells, "lr_over_xi": lr / XI, "n_lines": s["n_lines"],
                 "F_over_xi": F, "F_over_lr": margin, "mean_mst_over_xi": s["mst_mean_over_xi"]})
    print(f"{lr_cells:>6.1f} {lr/XI:>7.3f} {s['n_lines']:>8} {F:>7.3f} {margin:>7.2f} "
          f"{F - lr/XI:>8.3f} {s['mst_mean_over_xi']:>11.2f}")
json.dump(rows, open("exploration/tda/linkradius_check.json", "w"), indent=1)
F = np.array([r["F_over_xi"] for r in rows]); lr = np.array([r["lr_over_xi"] for r in rows])
print(f"\nF range over a {lr.max()/lr.min():.1f}x change in link_radius: "
      f"{F.min():.3f} .. {F.max():.3f} xi  ({(F.max()-F.min())/F.mean()*100:.0f}% spread)")
print("VERDICT:", "F tracks the threshold -> ARTEFACT" if np.corrcoef(lr, F)[0, 1] > 0.9
      and (F - lr).std() < 0.1 * F.mean() else "F does not simply track the threshold")
