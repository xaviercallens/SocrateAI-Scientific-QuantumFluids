"""Amendment A2 (exploratory): window edges of criterion B beyond the registered grid."""
import json, numpy as np, wigner_lib as w
from scipy.optimize import brentq
cal = json.load(open("calibration.json")); gB = cal["criterion_B"]["gamma_c"]
anch = cal["criterion_B"]["gamma_c_from_n"]     # [gamma(320), gamma(260)]
def G(nu, D):
    if D == "inf": return w.gamma_R(nu, "ungated", Nq=16)
    return w.gamma_R(nu, "gated", h=D/2.0, Nq=16)
res = []
for D in [2.0, 3.0, 5.0, 10.0, 20.0, "inf"]:
    # locate minimum on a coarse log grid first
    grid = np.logspace(-3, 3, 25)
    vals = np.array([G(x, D) for x in grid])
    i0 = int(np.argmin(vals)); numin = grid[i0]
    for Lam in [50.0, 100.0, 300.0, 1000.0]:
        row = dict(D_over_d=str(D), Lambda=Lam, nu_at_min_grid=float(numin))
        for lab, g in [("B", gB), ("B_anchor320", anch[0]), ("B_anchor260", anch[1])]:
            T = g*Lam**0.25
            f = lambda lx: np.log(G(np.exp(lx), D)) - np.log(T)
            # bracket: scan coarse grid values
            fv = np.log(vals) - np.log(T)
            lo = hi = None
            ins = fv < 0
            if ins.any():
                ii = np.where(ins)[0]
                a, b = ii[0], ii[-1]
                lo = None if a == 0 else float(np.exp(brentq(f, np.log(grid[a-1]), np.log(grid[a]), xtol=1e-4)))
                hi = None if b == len(grid)-1 else float(np.exp(brentq(f, np.log(grid[b]), np.log(grid[b+1]), xtol=1e-4)))
                row[lab] = dict(nu_lo=lo, nu_hi=hi, nr0_lo=None if lo is None else lo*Lam**2, nr0_hi=None if hi is None else hi*Lam**2)
            else:
                row[lab] = None
        res.append(row); print(row, flush=True)
json.dump(res, open("refine.json", "w"), indent=1)
print("DONE")
