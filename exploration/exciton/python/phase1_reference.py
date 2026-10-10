#!/usr/bin/env python3
"""Independent reference numbers for the Phase 1 pre-registration (docs/designs/EXCITON_FLUID_PHASE1_PREREG.md).

Written and run BEFORE the Rust experiments.  numpy float64 for lattice sums (converged cutoffs, checked against a
shorter cutoff), mpmath (30 digits) for closed forms.  Output: exploration/exciton/results/phase1/reference.json.

    python3 exploration/exciton/python/phase1_reference.py
"""
import json, math
from pathlib import Path
import numpy as np
import mpmath as mp

OUT = Path(__file__).resolve().parents[1] / "results" / "phase1" / "reference.json"
mp.mp.dps = 30

# ---- kernels g(t), t = r^2 (registered in the pre-registration, section 2)
def K1(t): return np.exp(-t)
def K2(t): r = np.sqrt(t); return np.exp(-r) / r
def K3(t): return t ** -1.5 * np.exp(-0.02 * t)
def _b(t):
    A = np.sqrt(t + 1.0); B = np.sqrt(t); return 2.0 / (B * A * (A + B))      # 2[t^-1/2 - (t+1)^-1/2], stable
def K4(t): return _b(t) * np.exp(-0.02 * t)
def K5(t): return t ** -1.5
def K6(t): return _b(t)
def N1(t): return np.exp(-t * t)

def lat_r(a, R):
    # k (the second index) must reach R / (a sqrt(3)/2); m must reach R/a + |k|/2.  (Amendment A1: the first version
    # used n = R/a + 3 for both and missed the caps |y| > (sqrt(3)/2) R; caught by the closed-form KA-1a.)
    kmax = int(R / (a * math.sqrt(3) / 2)) + 3
    mmax = int(R / a + kmax / 2) + 3
    m = np.arange(-mmax, mmax + 1)
    k = np.arange(-kmax, kmax + 1)
    M, N = np.meshgrid(m, k)
    X = a * (M + 0.5 * N); Y = a * (math.sqrt(3) / 2 * N)
    r = np.hypot(X, Y)
    return r[(r > 1e-12) & (r <= R)]

def a_of_rho(rho): return (2.0 / (math.sqrt(3) * rho)) ** 0.5

def e_lat(g, rho, R):
    return 0.5 * float(np.sum(g(lat_r(a_of_rho(rho), R) ** 2)))

ref = {"tolerance_note": "e_lat per particle (unordered pairs); exactly summable kernels converged to double precision",
       "KA1_constant": str(6 * mp.zeta(1.5) * mp.dirichlet(1.5, [0, 1, -1])),
       "KA1_constant_float": float(6 * mp.zeta(1.5) * mp.dirichlet(1.5, [0, 1, -1])),
       "e_lat": {}}
cases = {"K1": (K1, [0.5, 1.5], 40.0), "K2": (K2, [0.5, 1.5], 60.0), "K3": (K3, [0.1, 0.5], 90.0),
         "K4": (K4, [0.1, 0.5], 90.0), "N1": (N1, [1.0, 4.0], 10.0)}
for name, (g, rhos, R) in cases.items():
    for rho in rhos:
        v, v2 = e_lat(g, rho, R), e_lat(g, rho, R / 1.5)
        assert abs(v - v2) <= 1e-13 * abs(v), (name, rho, v, v2)
        ref["e_lat"][f"{name}@{rho}"] = v

# Gaussian closed form with Jacobi thetas: sum_{m,n} q^{m^2+mn+n^2} = th3(q) th3(q^3) + th2(q) th2(q^3)
def tri_gauss_closed(rho):
    a2 = 2 / (mp.sqrt(3) * rho)
    q = mp.e ** (-a2)
    S = mp.jtheta(3, 0, q) * mp.jtheta(3, 0, q ** 3) + mp.jtheta(2, 0, q) * mp.jtheta(2, 0, q ** 3)
    return (S - 1) / 2
ref["K1_theta_closed_form"] = {f"{rho}": str(tri_gauss_closed(rho)) for rho in (0.5, 1.5)}
for rho in (0.5, 1.5):
    assert abs(float(tri_gauss_closed(rho)) - ref["e_lat"][f"K1@{rho}"]) < 1e-14

# sandwich table for the undamped bilayer kernel K6 (d = 1): e_H = 2 pi rho, e_lat with exact tail pi rho 2 (sqrt(R^2+1)-R)
def e_lat_K6(rho, R=400.0):
    tail = 2 * math.pi * rho * (math.sqrt(R * R + 1.0) - R)
    return e_lat(K6, rho, R) + tail
tab = {}
for rd2 in (1e-3, 1e-2, 0.1, 0.3, 1.0, 3.0):
    tab[str(rd2)] = 2 * math.pi * rd2 / e_lat_K6(rd2)
ref["sandwich_K6_eH_over_elat"] = tab
tab2 = {}
for n12 in (0.1, 0.3, 0.5, 0.75):                      # 1e12 cm^-2 ; d = 2 nm ; 1e12 cm^-2 = 0.01 nm^-2
    rd2 = n12 * 0.01 * 4.0
    tab2[str(n12)] = {"rho_d2": rd2, "ratio": 2 * math.pi * rd2 / e_lat_K6(rd2)}
ref["sandwich_K6_d2nm"] = tab2

# GEM-4 cluster crystals on triangular site lattices (an upper bound for the true minimum)
def e_cluster(g, rho, nc, R=12.0):
    a = a_of_rho(rho / nc)
    return 0.5 * ((nc - 1) * float(g(np.array(0.0))) + nc * float(np.sum(g(lat_r(a, R) ** 2))))
ref["N1_cluster"] = {}
for rho in (1.0, 4.0):
    e1 = e_cluster(N1, rho, 1)
    best = min((e_cluster(N1, rho, nc), nc) for nc in range(2, 13))
    ref["N1_cluster"][str(rho)] = {"e_single": e1, "e_cluster_best": best[0], "nc": best[1], "ratio": best[0] / e1}

# four-flavour model (Qi et al. Eq. 2-3), units Ry, a_B; parameters as quoted in the arXiv v1
Ry, muB_ueV_per_T, aB, d_nm = 67e3, 57.88, 1.5, 2.0
gH = 8 * math.pi * d_nm / aB; gX = 1.0; Delta = 1.0 / Ry; gc, gv = 3.0, 6.0
nx = 0.5e12 * 1e-14 * aB ** 2
mu = nx * (2 * gH + gX) / 2
def phase(B_T):
    b = muB_ueV_per_T * B_T / Ry
    NA = 2 * (mu + Delta) / (2 * gH + gX); NB = 2 * mu / (2 * gH + gX)
    DA = 2 * (gv - gc) * b / gX; DB = 2 * (gc + gv) * b / gX                 # n1-n0 (IIA), n2-n3 (IIB)
    OmA = -(mu + Delta) ** 2 / (2 * gH + gX) - ((gv - gc) * b) ** 2 / gX
    OmB = -mu ** 2 / (2 * gH + gX) - ((gc + gv) * b) ** 2 / gX
    return {"b_Ry": b, "N_A": NA, "N_B": NB, "n1_minus_n0_IIA": DA, "n2_minus_n3_IIB": DB, "Omega_A": OmA, "Omega_B": OmB}
bc2 = gX * Delta * (2 * mu + Delta) / (4 * gc * gv * (2 * gH + gX))
b_c = math.sqrt(bc2)
ref["four_flavour"] = {"params": {"gH": gH, "gX": gX, "Delta": Delta, "gc": gc, "gv": gv, "mu": mu, "n_x": nx,
                                  "Ry_ueV": Ry, "muB_ueV_per_T": muB_ueV_per_T},
                       "b_c_Ry": b_c, "B_c_T": b_c * Ry / muB_ueV_per_T,
                       "spinodal_IIA_b_Ry": (gX * mu + 2 * (gH + gX) * Delta) / ((gc + gv) * (2 * gH + gX)),
                       "grid_B_T": {str(B): phase(B) for B in (0.01, 0.04, 0.2)}}
OUT.write_text(json.dumps(ref, indent=1) + "\n")
print(json.dumps({k: ref[k] for k in ("KA1_constant_float", "sandwich_K6_eH_over_elat", "N1_cluster")}, indent=1))
print("B_c [mT] =", ref["four_flavour"]["B_c_T"] * 1e3, " spinodal IIA [T] =",
      ref["four_flavour"]["spinodal_IIA_b_Ry"] * Ry / muB_ueV_per_T)
