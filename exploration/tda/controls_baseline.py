"""Workstream T control baseline (docs/designs/TDA_VORTEX_FLOOR.md section 4).

Records C-POS / C-RES / C-NEG / C-PERM and the meaning of the derived statistics, so that when a
real dataset arrives the comparison is against a documented, reproducible baseline rather than
numbers invented at that moment. SYNTHETIC BY CONSTRUCTION -- controls only, never a result (s.6).
"""
import json, sys
import numpy as np
sys.path.insert(0, "src")
from quantumfluids.tda.vortex_persistence import (
    extract_vortices, floor_stats, poisson_null, synthetic_vortex_field)

rng = np.random.default_rng(20260920)
XI = 1.0
out = {"xi": XI, "C_POS": [], "C_RES": [], "C_NEG": {}, "C_PERM": {}, "T4_loop_scale": []}

def triangular(spacing, nx=6, ny=6, origin=8.0):
    """Abrikosov-like triangular lattice -- the arrangement a rotating condensate actually forms."""
    c, q = [], []
    for i in range(nx):
        for j in range(ny):
            c.append((origin + spacing * (i + 0.5 * (j % 2)), origin + spacing * j * np.sqrt(3) / 2))
            q.append(1)
    return np.array(c), np.array(q)

print(f"{'test':<26} {'spacing/xi':>10} {'F':>8} {'f_<':>6} {'L1/xi':>8} {'L1/F':>8} {'n':>5}")
for spacing in (4.0, 6.0, 8.0):
    c, q = triangular(spacing)
    dx = 0.25
    box = spacing * 8 + 16
    shape = (int(box / dx), int(box / dx))
    psi = synthetic_vortex_field(c, q, shape, dx, XI)
    pts, _ = extract_vortices(psi, dx)
    s = floor_stats(pts, XI)
    rec = {"spacing_over_xi": spacing / XI, "recovered": len(pts), "planted": len(c), **s.as_dict()}
    rec["L1_over_F"] = s.L1_over_xi / s.F
    out["C_POS"].append(rec)
    out["T4_loop_scale"].append({"spacing_over_xi": spacing / XI, "L1_over_xi": s.L1_over_xi})
    print(f"{'C-POS triangular':<26} {spacing/XI:>10.1f} {s.F:>8.3f} {s.f_below:>6.2f} "
          f"{s.L1_over_xi:>8.3f} {rec['L1_over_F']:>8.3f} {len(pts):>5}")

c, q = triangular(6.0)
for dx in (0.5, 0.25, 0.125):
    box = 6.0 * 8 + 16
    shape = (int(box / dx), int(box / dx))
    psi = synthetic_vortex_field(c, q, shape, dx, XI)
    pts, _ = extract_vortices(psi, dx)
    s = floor_stats(pts, XI)
    out["C_RES"].append({"dx_over_xi": dx / XI, "F": s.F, "n": len(pts)})
    print(f"{'C-RES dx/xi=' + str(dx):<26} {6.0:>10.1f} {s.F:>8.3f} {s.f_below:>6.2f} "
          f"{s.L1_over_xi:>8.3f} {s.L1_over_xi/s.F:>8.3f} {len(pts):>5}")

n = len(c); box = 6.0 * 8 + 16
out["C_NEG"] = poisson_null(n=n, box=(box, box), xi=XI, reps=200, rng=rng)
out["C_NEG_dense"] = poisson_null(n=1600, box=(box, box), xi=XI, reps=20, rng=rng)
print(f"\nC-NEG  matched count n={n}, box {box:.0f}: F mean {out['C_NEG']['F']['mean']:.3f} "
      f"[p05 {out['C_NEG']['F']['p05']:.3f}, p95 {out['C_NEG']['F']['p95']:.3f}], "
      f"f_< mean {out['C_NEG']['f_below']['mean']:.3f}")
print(f"C-NEG  dense n=1600:            F mean {out['C_NEG_dense']['F']['mean']:.4f}, "
      f"f_< mean {out['C_NEG_dense']['f_below']['mean']:.3f}")

pts = np.stack([rng.uniform(0, box, n), rng.uniform(0, box, n)], axis=1)
s = floor_stats(pts, XI)
out["C_PERM"] = s.as_dict()
print(f"C-PERM shuffled positions:      F {s.F:.3f}  f_< {s.f_below:.3f}   "
      f"(inside C-NEG p05-p95: {out['C_NEG']['F']['p05'] <= s.F <= out['C_NEG']['F']['p95']})")

lat = floor_stats(triangular(6.0)[0], XI)
sep = lat.F / out["C_NEG"]["F"]["p95"]
out["discrimination_lattice_over_null_p95"] = sep
print(f"\nDiscrimination: lattice F = {lat.F:.2f} vs null p95 = {out['C_NEG']['F']['p95']:.2f}  "
      f"-> {sep:.1f}x")
json.dump(out, open("exploration/tda/controls_baseline.json", "w"), indent=1)
