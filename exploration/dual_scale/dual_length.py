"""DS-QF measurement (docs/designs/DUAL_SCALE_QUANTUM_FLUID.md M1-M5). Deterministic; writes results.json."""
import json, sys
import numpy as np
from scipy.optimize import curve_fit
sys.path.insert(0, "exploration")
from pressure_scaling import load

HBAR_MEVS = 6.582119569e-13          # meV s
M_HE4 = 6.6464731e-27                # kg
J_PER_MEV = 1.602176634e-22

def hbar_c(c_ms):                     # meV A
    return HBAR_MEVS * c_ms * 1e10

def k_star(c_ms):                     # A^-1 ; k* = 2 m c / hbar
    return 2 * M_HE4 * c_ms / (HBAR_MEVS * J_PER_MEV) * 1e-10

def fit_c(Q, E, dE, kmax=0.3):
    """M1: phonon slope E = hbar c k on k <= kmax, through the origin."""
    m = (Q <= kmax) & (Q > 0) & np.isfinite(E)
    w = np.where(np.isfinite(dE[m]) & (dE[m] > 0), dE[m], np.nanmedian(dE[np.isfinite(dE)]))
    f = lambda q, s: s * q
    popt, pcov = curve_fit(f, Q[m], E[m], p0=[1.5], sigma=w, absolute_sigma=True)
    resid = float(np.max(np.abs(E[m] - f(Q[m], *popt))))
    return popt[0] / (HBAR_MEVS * 1e10), float(np.sqrt(pcov[0, 0])) / (HBAR_MEVS * 1e10), int(m.sum()), resid

def dual_length(Q, E, c_ms):
    return E ** 2 / (hbar_c(c_ms) ** 2 * Q ** 3)

def analyse(Q, L, ks, c_ms):
    """M2 + M3. Returns interior-minimum verdict and duality error."""
    i = int(np.argmin(L))
    interior = 0 < i < len(L) - 1
    xi = HBAR_MEVS * J_PER_MEV / (np.sqrt(2) * M_HE4 * c_ms) * 1e10   # A
    out = {"k_min": float(Q[i]), "l_min": float(L[i]), "interior": bool(interior),
           "k_min_over_kstar": float(Q[i] / ks), "l_min_over_sqrt2xi": float(L[i] / (np.sqrt(2) * xi)),
           "xi_A": float(xi), "sqrt2_xi_A": float(np.sqrt(2) * xi), "k_star": float(ks)}
    dual = ks ** 2 / Q
    ok = (dual >= Q.min()) & (dual <= Q.max())
    if ok.sum() >= 2:
        Ld = np.interp(dual[ok], Q, L)
        err = np.abs(Ld / L[ok] - 1)
        out["duality"] = {"n_pairs": int(ok.sum()), "k_window": [float(Q[ok].min()), float(Q[ok].max())],
                          "max_rel_err": float(err.max()), "median_rel_err": float(np.median(err))}
    else:
        out["duality"] = {"n_pairs": int(ok.sum()), "note": "window too small"}
    return out

def main():
    P, Q, E, dE = load()
    res = {"pressures": P.tolist(), "per_pressure": [], "controls": {}}
    for j, p in enumerate(P):
        m = np.isfinite(E[:, j]) & (Q > 0)
        q, e, d = Q[m], E[m, j], dE[m, j]
        c, cerr, n, resid = fit_c(q, e, d)
        ks = k_star(c)
        L = dual_length(q, e, c)
        row = {"P_bar": float(p), "c_ms": float(c), "c_err": float(cerr), "n_phonon": n,
               "max_phonon_resid_meV": resid, "k_range": [float(q.min()), float(q.max())]}
        row.update(analyse(q, L, ks, c))
        # P3: l at the roton (minimum of E over 1.6..2.3)
        rm = (q > 1.6) & (q < 2.3)
        ir = int(np.argmin(e[rm]))
        row["roton"] = {"k": float(q[rm][ir]), "eps_meV": float(e[rm][ir]),
                        "l_over_sqrt2xi": float(L[rm][ir] / row["sqrt2_xi_A"])}
        # M4 positive control: Bogoliubov with the same c on the same grid
        LB = 1.0 / q + q / ks ** 2
        row["M4_bogoliubov_control"] = analyse(q, LB, ks, c)
        res["per_pressure"].append(row)
    # M5 negative control: pure phonon, must be an endpoint minimum
    q = np.linspace(0.15, 3.6, 400)
    c = 238.3
    Lp = dual_length(q, hbar_c(c) * q, c)
    res["controls"]["M5_pure_phonon"] = analyse(q, Lp, k_star(c), c)
    json.dump(res, open("exploration/dual_scale/results.json", "w"), indent=1)
    # report
    print(f"{'P':>6} {'c(m/s)':>9} {'k*':>6} {'sqrt2.xi':>8} {'k_min':>7} {'interior':>9} {'l_min/s2xi':>11} {'roton l/s2xi':>13} {'dual err':>9}")
    for r in res["per_pressure"]:
        du = r["duality"].get("max_rel_err")
        print(f"{r['P_bar']:>6} {r['c_ms']:>9.1f} {r['k_star']:>6.3f} {r['sqrt2_xi_A']:>8.3f} {r['k_min']:>7.3f} "
              f"{str(r['interior']):>9} {r['l_min_over_sqrt2xi']:>11.3f} {r['roton']['l_over_sqrt2xi']:>13.3f} "
              f"{(f'{du:.3f}' if du is not None else 'n/a'):>9}")
    c0 = res["per_pressure"][0]["M4_bogoliubov_control"]
    print("\nM4 positive control (Bogoliubov, P=0): k_min/k* = %.4f, l_min/(sqrt2 xi) = %.4f, duality err = %s"
          % (c0["k_min_over_kstar"], c0["l_min_over_sqrt2xi"], c0["duality"].get("max_rel_err")))
    print("M5 negative control (pure phonon): interior minimum =", res["controls"]["M5_pure_phonon"]["interior"])

main()
