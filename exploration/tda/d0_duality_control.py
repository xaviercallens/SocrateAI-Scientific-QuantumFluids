"""D0 of KINETIC_TDA_PREREG.md: the duality control.  P-D0a: T(rho) vs V(-rho) agree exactly.
P-D0b: T(rho) vs T(-rho) do NOT.  Plus a non-tautological check of GUDHI's pixel indexing."""
import sys, os
import numpy as np
sys.path.insert(0, "src")
from quantumfluids.tda.cubical import duality_defect, minima_with_depth

def smooth_random(n, seed, kc=12):
    rng = np.random.default_rng(seed)
    k = np.fft.fftfreq(n, 1 / n); K = np.hypot(k[:, None], k[None, :])
    return np.real(np.fft.ifft2(np.fft.fft2(rng.normal(size=(n, n))) * (K < kc)))

fields = {"smooth random 128^2 (seed 1)": smooth_random(128, 1)}
p = "data/generated/kinetic_tda/psi_t10.npy"
if os.path.exists(p):
    fields["GP |psi|^2, t=10, 1024^2"] = np.abs(np.load(p)) ** 2
else:
    print("(GP frame not generated yet; run make_gp_frames.py)")

for name, f in fields.items():
    # indexing check: every reported birth pixel must be a local minimum under 8-connectivity
    b, dep, ij = minima_with_depth(f)
    nb = np.stack([np.roll(np.roll(f, di, 0), dj, 1) for di in (-1, 0, 1) for dj in (-1, 0, 1) if (di, dj) != (0, 0)])
    is_min = (f <= nb.min(axis=0))[ij[:, 0], ij[:, 1]]
    n0, n1, dV = duality_defect(f, "V")
    m0, m1, dT = duality_defect(f, "T")
    print(f"{name}\n   indexing: {is_min.sum()}/{len(ij)} reported birth pixels are local minima"
          f"\n   P-D0a  T(rho) vs V(-rho): |H0|={n0} |H1|={n1} max diff={dV:.2e}   PASS(<1e-12): {dV < 1e-12}"
          f"\n   P-D0b  T(rho) vs T(-rho): |H0|={m0} |H1|={m1} max diff={dT:.2e}   PASS(differs): {not dT < 1e-12}")
