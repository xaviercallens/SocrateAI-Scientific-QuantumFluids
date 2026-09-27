"""DS-QF, amended scope (A2): full-range P=0 file, which alone covers the self-dual point k*."""
import json, sys
import numpy as np
from scipy.optimize import curve_fit
sys.path.insert(0, "src")
from quantumfluids.adapters.godfrin_ancillary import load_godfrin_p0_dispersion
sys.path.insert(0, "exploration/dual_scale")
from dual_length import hbar_c, k_star, dual_length, analyse, HBAR_MEVS

PATH = "data/external/godfrin_2021_arxiv_ancillary/DispersionP0allRange.txt"

def fit_c(Q, E, kmax):
    m = (Q <= kmax) & (Q > 0)
    f = lambda q, s: s * q
    popt, pcov = curve_fit(f, Q[m], E[m], p0=[1.5])
    return popt[0] / (HBAR_MEVS * 1e10), int(m.sum()), float(np.max(np.abs(E[m] - f(Q[m], *popt))))

d = load_godfrin_p0_dispersion(PATH)
Q = np.asarray(d.Q).ravel(); E = np.asarray(d.omega).ravel()
m = Q > 0; Q, E = Q[m], E[m]
res = {"file": PATH, "k_range": [float(Q.min()), float(Q.max())], "n": int(len(Q)), "c_fits": {}}
print("k range %.3f .. %.3f A^-1, %d points" % (Q.min(), Q.max(), len(Q)))
for kmax in (0.05, 0.1, 0.2, 0.3):
    c, n, r = fit_c(Q, E, kmax)
    res["c_fits"][str(kmax)] = {"c_ms": float(c), "n": n, "max_resid_meV": r}
    print("  c fit k<=%.2f : c = %.1f m/s (n=%d, max resid %.4f meV)" % (kmax, c, n, r))
C_LIT = 238.3
for label, c in (("fitted_k<=0.1", res["c_fits"]["0.1"]["c_ms"]), ("literature_238.3", C_LIT)):
    ks = k_star(c); L = dual_length(Q, E, c)
    a = analyse(Q, L, ks, c)
    LB = 1.0 / Q + Q / ks ** 2
    ctrl = analyse(Q, LB, ks, c)
    rm = (Q > 1.6) & (Q < 2.3); ir = int(np.argmin(E[rm]))
    a["roton"] = {"k": float(Q[rm][ir]), "eps_meV": float(E[rm][ir]),
                  "l_over_sqrt2xi": float(L[rm][ir] / a["sqrt2_xi_A"])}
    res[label] = {"c_ms": float(c), "data": a, "M4_control": ctrl}
    print("\n=== c = %.1f m/s (%s):  k* = %.3f A^-1, sqrt2.xi = %.3f A" % (c, label, ks, a["sqrt2_xi_A"]))
    print("  M4 CONTROL (Bogoliubov): interior=%s k_min/k*=%.4f l_min/(s2xi)=%.4f duality_err=%s"
          % (ctrl["interior"], ctrl["k_min_over_kstar"], ctrl["l_min_over_sqrt2xi"],
             ctrl["duality"].get("max_rel_err")))
    print("  DATA (He-II):            interior=%s k_min=%.3f (k_min/k*=%.3f) l_min/(s2xi)=%.4f duality_err=%s"
          % (a["interior"], a["k_min"], a["k_min_over_kstar"], a["l_min_over_sqrt2xi"],
             a["duality"].get("max_rel_err")))
    print("  roton k=%.3f eps=%.4f meV : l/(sqrt2 xi) = %.4f" % (a["roton"]["k"], a["roton"]["eps_meV"], a["roton"]["l_over_sqrt2xi"]))
    print("  duality window:", a["duality"].get("k_window"), "n_pairs", a["duality"].get("n_pairs"))
json.dump(res, open("exploration/dual_scale/results_p0.json", "w"), indent=1)
