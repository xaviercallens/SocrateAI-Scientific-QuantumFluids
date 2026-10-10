#!/usr/bin/env python3
"""Independent reference numbers for the Phase 2 pre-registration (docs/designs/EXCITON_FLUID_PHASE2_PREREG.md)."""
import json, math
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parents[1] / "results" / "phase2"
OUT.mkdir(parents=True, exist_ok=True)
L, M, MU, D = 16.0, 16, 0.25, 1.0
k0 = 2 * math.pi * 3 / L

def U_B(k):
    k = np.asarray(k, dtype=float)
    out = np.empty_like(k)
    nz = k > 0
    out[nz] = 4 * math.pi * (1 - np.exp(-k[nz] * D)) / k[nz]
    out[~nz] = 4 * math.pi * D
    return out

def U_C(k):
    k = np.asarray(k, dtype=float)
    return U_B(k) - 28.0 * np.exp(-(k - k0) ** 2 / (2 * 0.2 ** 2))

ms = np.arange(M)
ms = np.where(ms > M // 2, ms - M, ms)            # wavenumber indices -8..7 (Nyquist at -8)
kx, ky = np.meshgrid(2 * math.pi * ms / L, 2 * math.pi * ms / L, indexing="ij")
kk = np.hypot(kx, ky)

ref = {"L": L, "M": M, "mu": MU, "d": D, "k0": k0}
for name, U in (("B", U_B), ("C", U_C)):
    U0 = float(U(np.array([0.0]))[0])
    n0 = MU / U0
    eps = 0.5 * kk ** 2
    om2 = eps * (eps + 2 * n0 * U(kk))
    ref[name] = {"U0": U0, "n0": n0, "omega0": -MU ** 2 / (2 * U0),
                 "omega2_min": float(om2[kk > 0].min()), "n_unstable": int((om2[kk > 0] < 0).sum()),
                 "unstable_k": sorted({round(float(k), 6) for k in kk[(om2 < 0) & (kk > 0)]}),
                 "omega2": {f"{int(i)},{int(j)}": float(om2[a, b]) for a, i in enumerate(ms) for b, j in enumerate(ms) if (i, j) != (0, 0)}}
(OUT / "reference.json").write_text(json.dumps(ref) + "\n")
print("B: U0=%.6f n0=%.6f omega0=%.6e min omega^2=%.3e unstable=%d" % (ref["B"]["U0"], ref["B"]["n0"], ref["B"]["omega0"], ref["B"]["omega2_min"], ref["B"]["n_unstable"]))
print("C: U0=%.6f n0=%.6f omega0=%.6e min omega^2=%.3e unstable=%d at k=%s" % (ref["C"]["U0"], ref["C"]["n0"], ref["C"]["omega0"], ref["C"]["omega2_min"], ref["C"]["n_unstable"], ref["C"]["unstable_k"]))
