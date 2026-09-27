"""DS-QF amendment A2: P4 only (roton-region ratio vs pressure). M2/M3 are impossible on this table
(k* = 3.1-4.4 A^-1 lies outside its range [0.15, 2.21]); that is why the original M4 control failed.
Amended control C2: the Bogoliubov reference must satisfy l_B(k)/(sqrt2 xi) >= 1 at EVERY k, including the roton.
"""
import json, sys
import numpy as np
from scipy.optimize import curve_fit
sys.path.insert(0, "exploration"); sys.path.insert(0, "exploration/dual_scale")
from pressure_scaling import load
from dual_length import hbar_c, k_star, dual_length, HBAR_MEVS, M_HE4, J_PER_MEV

P, Q, E, dE = load()
C_BIAS = 238.8 / 249.6     # measured at P=0: fine-grid (k<=0.05) vs this table's window (k<=0.3)
rows, ctrl_ok = [], True
for j, p in enumerate(P):
    m = np.isfinite(E[:, j]) & (Q > 0); q, e = Q[m], E[m, j]
    w = q <= 0.3
    c_raw = curve_fit(lambda x, s: s * x, q[w], e[w], p0=[1.5])[0][0] / (HBAR_MEVS * 1e10)
    for tag, c in (("raw", c_raw), ("bias_corrected", c_raw * C_BIAS)):
        ks = k_star(c); xi2 = HBAR_MEVS * J_PER_MEV / (M_HE4 * c) * 1e10   # sqrt2 * xi = hbar/(mc)
        L = dual_length(q, e, c)
        LB = 1.0 / q + q / ks ** 2
        if (LB / xi2).min() < 1 - 1e-9:                                    # control C2
            ctrl_ok = False
        rm = (q > 1.6) & (q < 2.3); ir = int(np.argmin(e[rm]))
        rows.append({"P_bar": float(p), "c_variant": tag, "c_ms": float(c), "k_star": float(ks),
                     "sqrt2_xi_A": float(xi2), "roton_k": float(q[rm][ir]), "roton_eps": float(e[rm][ir]),
                     "ratio": float(L[rm][ir] / xi2), "bogoliubov_ratio_at_roton": float(np.interp(q[rm][ir], q, LB) / xi2)})
print("Control C2 (Bogoliubov ratio >= 1 at every k, all pressures):", "PASS" if ctrl_ok else "FAIL")
print(f"\n{'P(bar)':>7} {'c(m/s)':>8} {'k*':>6} {'s2.xi(A)':>9} {'roton k':>8} {'eps(meV)':>9} {'l/s2xi':>8} {'Bog l/s2xi':>11} {'shortfall':>10}")
for r in rows:
    if r["c_variant"] != "bias_corrected": continue
    print(f"{r['P_bar']:>7} {r['c_ms']:>8.1f} {r['k_star']:>6.3f} {r['sqrt2_xi_A']:>9.3f} {r['roton_k']:>8.3f} "
          f"{r['roton_eps']:>9.4f} {r['ratio']:>8.4f} {r['bogoliubov_ratio_at_roton']:>11.3f} {1/r['ratio']:>9.1f}x")
b = [r for r in rows if r["c_variant"] == "bias_corrected"]
print("\nratio(24.08 bar)/ratio(0 bar) = %.3f  (P4 predicted < 1: the violation deepens with pressure)"
      % (b[-1]["ratio"] / b[0]["ratio"]))
raw = [r for r in rows if r["c_variant"] == "raw"]
print("same with uncorrected c: %.3f  (trend is insensitive to the common c bias)" % (raw[-1]["ratio"] / raw[0]["ratio"]))
json.dump({"control_C2_pass": ctrl_ok, "c_bias_factor": C_BIAS, "rows": rows},
          open("exploration/dual_scale/results_pressure.json", "w"), indent=1)
