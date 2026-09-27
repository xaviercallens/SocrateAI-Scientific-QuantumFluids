"""Where does the three-phonon decay channel close?  From Godfrin et al. PRB 103, 104516 (2021).

A phonon k can decay into q and k-q (collinear is the most favourable case) iff
    g(k, q) = eps(k) - eps(q) - eps(k - q) >= 0.
Two natural thresholds, which are DIFFERENT and are often conflated:
    symmetric split  q = k/2 :  eps(k) = 2 eps(k/2)
    soft emission    q -> 0  :  d eps/dk = c        (group velocity falls to the sound speed)
The channel is closed for ALL splits only beyond the larger of the two.

g is homogeneous of degree one in the energy scale, so k_c is INDEPENDENT of the proportional
energy calibration (HeliumKinematics.tofEnergy_rescale) -- it depends on Delta_R not at all.
"""
import json, sys
import numpy as np
from scipy.optimize import brentq
sys.path.insert(0, "src"); sys.path.insert(0, "exploration")
from quantumfluids.adapters.godfrin_ancillary import load_godfrin_p0_dispersion
from pressure_scaling import load

out = {}
# ---- (a) from the paper's SVP series, stated valid for k < 0.5 A^-1
a2, a3, a4 = 1.55, -4.04, 2.30
eps = lambda k: k * (1 + a2 * k**2 + a3 * k**3 + a4 * k**4)          # in units of hbar c
deps = lambda k: 1 + 3 * a2 * k**2 + 4 * a3 * k**3 + 5 * a4 * k**4
def roots(fn, lo=0.02, hi=1.5, n=3000):
    """All sign changes on a grid -- no assumption that a root exists (the series is a quartic
    whose positive alpha4 term takes over at large k, outside its stated validity)."""
    g = np.linspace(lo, hi, n); v = np.array([fn(x) for x in g]); r = []
    for i in np.where(np.diff(np.sign(v)) != 0)[0]:
        r.append(float(brentq(fn, g[i], g[i + 1])))
    return r
r_sym = roots(lambda k: eps(k) - 2 * eps(k / 2))
r_grp = roots(lambda k: deps(k) - 1)
r_ph = roots(lambda k: eps(k) / k - 1)
ks = r_sym[0] if r_sym else None; kg = r_grp[0] if r_grp else None; kp = r_ph[0] if r_ph else None
print("SERIES (alpha2, alpha3, alpha4 = 1.55, -4.04, 2.30; paper says valid for k < 0.5):")
print(f"  symmetric split  eps(k) = 2 eps(k/2)  roots: {np.round(r_sym, 3).tolist()}")
print(f"  soft emission    d eps/dk = c         roots: {np.round(r_grp, 3).tolist()}")
print(f"  phase velocity   eps/k = c            roots: {np.round(r_ph, 3).tolist()}")
kk = np.linspace(0.02, 1.0, 400)
gmax = [max(eps(k) - eps(q) - eps(k - q) for q in np.linspace(1e-3, k - 1e-3, 200)) for k in kk]
kall = kk[np.where(np.array(gmax) > 1e-9)[0][-1]]
print(f"  channel closed for EVERY split beyond           k = {kall:.3f} A^-1")
out["series"] = {"k_sym": ks, "k_group": kg, "k_phase": kp, "k_all_closed": float(kall),
                 "validity_note": "series stated valid only for k < 0.5; thresholds above that are extrapolation"}

# ---- (b) directly from the measured SVP table (no series)
d = load_godfrin_p0_dispersion("data/external/godfrin_2021_arxiv_ancillary/DispersionP0allRange.txt")
Q = np.asarray(d.Q).ravel(); E = np.asarray(d.omega).ravel()
f = lambda k: np.interp(k, Q, E)
gs = lambda k: f(k) - 2 * f(k / 2)
grid = np.linspace(0.1, 1.0, 901)
sign = np.sign(gs(grid)); cross = grid[1:][np.diff(sign) != 0]
print(f"\nMEASURED TABLE, SVP: symmetric-split excess changes sign at k = {np.round(cross, 3).tolist()} A^-1")
print(f"  max excess {gs(grid).max()*1e3:.2f} micro-eV at k = {grid[np.argmax(gs(grid))]:.3f}")
out["table_svp"] = {"sym_crossings": cross.tolist(), "max_excess_meV": float(gs(grid).max())}

# ---- (c) pressure dependence, symmetric split (needs k/2 >= 0.15, the table's lower edge)
P, Qp, Ep, dEp = load()
print("\nPRESSURE (symmetric split; table starts at k = 0.15 so only k >= 0.30 is testable):")
print(f"{'P(bar)':>7} {'k_c sym (A^-1)':>15} {'max excess (ueV)':>17} {'typ. err (ueV)':>15}")
rows = []
for j, p in enumerate(P):
    m = np.isfinite(Ep[:, j]); q, e, de = Qp[m], Ep[m, j], dEp[m, j]
    fj = lambda k: np.interp(k, q, e)
    g = np.linspace(0.30, 1.0, 701); val = fj(g) - 2 * fj(g / 2)
    cr = g[1:][np.diff(np.sign(val)) != 0]
    err = float(np.nanmedian(de[(q > 0.15) & (q < 0.6)])) * np.sqrt(1 + 4)      # eps(k) and 2*eps(k/2)
    kc = float(cr[0]) if len(cr) and val[0] > 0 else None
    rows.append({"P": float(p), "k_c_sym": kc, "max_excess_meV": float(val.max()), "err_meV": err,
                 "open_at_0.30": bool(val[0] > 0)})
    print(f"{p:>7} {(f'{kc:.3f}' if kc else 'closed at k>=0.30'):>15} {val.max()*1e3:>17.2f} {err*1e3:>15.2f}")
out["pressure"] = rows
json.dump(out, open("exploration/godfrin/three_phonon_threshold.json", "w"), indent=1)
