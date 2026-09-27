"""POST-HOC, after D1 FAILED (precision 0.87, recall 0.43).  For each true vortex: is there a density minimum
with birth < 0.1 n0 within 1 xi at all, and if so what is its depth (H0 persistence)?"""
import sys
import numpy as np
sys.path.insert(0, "src"); sys.path.insert(0, "exploration/tda")
from quantumfluids.gpe.solver2d import Grid2D, healing_length
from quantumfluids.tda.vortex_persistence import extract_vortices
from quantumfluids.tda.cubical import minima_with_depth
XI = healing_length(1.0); g = Grid2D(n=1024, dx=XI / 8)
psi = np.load("data/generated/kinetic_tda/psi_t10.npy"); rho = np.abs(psi) ** 2; rho /= rho.mean()
truth, _ = extract_vortices(psi, g.dx)
b, dep, ij = minima_with_depth(rho); pos = np.column_stack([ij[:, 1], ij[:, 0]]) * g.dx
d = np.abs(truth[:, None, :] - pos[None, :, :]); d = np.minimum(d, g.L - d); d = np.hypot(d[..., 0], d[..., 1]) / XI
low = b < 0.1
has_min = (d[:, low] <= 1.0).any(axis=1)
best_depth = np.array([dep[low][d[i, low] <= 1.0].max() if has_min[i] else np.nan for i in range(len(truth))])
print(f"t=10: {len(truth)} vortices; density field: std={rho.std():.3f}, fraction of area below 0.5 n0 = {(rho < 0.5).mean():.3f}")
print(f"  with a minimum (birth<0.1 n0) within 1 xi: {has_min.sum()} ({has_min.mean():.2f})")
for lo, hi in ((0, .1), (.1, .3), (.3, .5), (.5, 9)):
    m = (best_depth >= lo) & (best_depth < hi); print(f"     of those, best depth in [{lo},{hi}) n0: {m.sum()}")
print(f"  low-birth minima in the frame: {low.sum()};  of which within 1 xi of a vortex: {(d[:, low] <= 1.0).any(axis=0).sum()}")
