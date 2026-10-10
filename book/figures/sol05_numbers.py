"""Solutions to the exercises of Chapter 5 (Appendix C): every computed number of chapters/sol05.tex.
  .venv/bin/python book/figures/sol05_numbers.py        (seconds)
Writes figures/sol05_numbers.json.  The helium table is read with the chapter's own reader (ch05_helium.load_table).

Exercise 1  Landau's quadratic roton: sympy check of the minimisation, v_L with the exercise's inputs, with the table's own
            minimum, and the table's v_L (min of eps/hbar k).
Exercise 2  superadditivity of Bogoliubov's eps = k s(k) (numerical spot check), and, on the helium table and on the paper's
            quartic series, where the phase velocity s increases, and which collinear splits k -> q + (k - q) are open.
Exercise 3  omega^2 = eps_k (eps_k + 2 n V(k)), n V = 1 - 3 k^2 exp(-k^2): extrema, Landau velocity, stability, the low-k
            curvature, and for every property proved in Ch05_BogoliubovDispersion whether the analogue holds (with a witness).
"""
import json, math, sys
from pathlib import Path
import numpy as np
import sympy as sp
from scipy.optimize import brentq, minimize_scalar

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ch05_helium as H                                          # noqa: E402

R = {"script": "book/figures/sol05_numbers.py"}
feat = H.features()

# ------------------------------------------------------------------------------------------------ Exercise 1
k, kR, Dl, a = sp.symbols("k k_R Delta a", positive=True)
f = (Dl + a * (k - kR) ** 2) / k
num = sp.together(sp.diff(f, k)).as_numer_denom()[0]
assert sp.expand(num - (a * (k - kR) * (k + kR) - Dl)) == 0        # the hint's factorisation (numerator of f')
kL = sp.sqrt(kR ** 2 + Dl / a)
assert sp.simplify(f.subs(k, kL) - 2 * a * (kL - kR)) == 0         # value at the minimum
def landau(Delta, k_R, mu, h2m):
    aa = h2m / mu
    k_L = math.sqrt(k_R ** 2 + Delta / aa)
    hv = 2 * aa * (k_L - k_R)                                       # meV A
    return dict(Delta=Delta, k_R=k_R, mu=mu, hbar2_over_2m4=h2m, a_meV_A2=aa, Delta_over_a=Delta / aa, k_L=k_L,
                hbar_vL_meV_A=hv, v_L_ms=hv * H.MS_PER_MEVA)
ex1 = {"factorisation_checked": True,
       "exercise_inputs": landau(0.7418, 1.918, 0.141, 0.522),
       "exercise_inputs_unrounded_h2m4": landau(0.7418, 1.918, 0.141, H.HBAR2_2M4),
       "table_minimum_and_fitted_mass": landau(feat["roton_grid_e_meV"], feat["roton_grid_k"], feat["roton_mass_over_m4"], H.HBAR2_2M4),
       "table_landau": dict(v_L_ms=feat["landau_velocity_ms"], k=feat["landau_k_A_inv"], over_c=feat["landau_over_c"]),
       "hbar2_over_2m4_exact": H.HBAR2_2M4, "ms_per_meV_A": H.MS_PER_MEVA}
e = ex1["exercise_inputs"]
ex1["rel_diff_exercise_vs_table"] = e["v_L_ms"] / feat["landau_velocity_ms"] - 1
# sensitivity of v_L to Delta and k_R at fixed a:  hbar v_L = 2 a (k_L - k_R)
aa = e["a_meV_A2"]
dv_dD = (1 / e["k_L"]) * H.MS_PER_MEVA                             # d(2a(k_L - k_R))/dDelta = 2a * (1/(2 a k_L)) = 1/k_L
dv_dk = 2 * aa * (e["k_R"] / e["k_L"] - 1) * H.MS_PER_MEVA
ex1["sensitivity"] = dict(dvL_dDelta_ms_per_meV=dv_dD, dvL_dkR_ms_per_invA=dv_dk,
                          shift_from_Delta_0.7418_to_table=dv_dD * (feat["roton_grid_e_meV"] - 0.7418),
                          shift_from_kR_1.918_to_table=dv_dk * (feat["roton_grid_k"] - 1.918))
R["exercise1"] = ex1

# ------------------------------------------------------------------------------------------------ Exercise 2
def bog(kk, c=1.0, m=1.0):
    return math.sqrt(c * c * kk * kk + (kk * kk / (2 * m)) ** 2)
rng = np.random.default_rng(5)
pairs = rng.uniform(1e-3, 10, size=(200000, 2))
exc = np.array([bog(x + y) - bog(x) - bog(y) for x, y in pairs])
ex2 = {"bogoliubov_spot_check": dict(n_pairs=len(pairs), min_excess=float(exc.min()), all_positive=bool((exc > 0).all()))}
kt, et, _ = H.load_table()
def eps_table(q):
    return np.interp(q, kt, et)
sel = (kt >= 0.15) & (kt <= 1.0)
s_tab = et[sel] / (H.HBARC * kt[sel])                               # phase velocity / c (c = 238.3 m/s)
kmax_s = float(kt[sel][np.argmax(s_tab)])
ex2["table_phase_velocity_max_k"] = kmax_s
ex2["table_phase_velocity_max_over_c"] = float(s_tab.max())
# phase velocity increasing on [0.15, kmax_s]?  fraction of increasing steps (the table is rounded to 1e-4 meV)
ss = s_tab[kt[sel] <= kmax_s]
ex2["table_s_increasing_fraction_0.15_to_max"] = float(np.mean(np.diff(ss) >= 0))
def series_eps(q):                                                  # meV, the paper's quartic series (valid k < 0.5)
    return H.HBARC * H.series(q)
def open_splits(kk, eps, qmin=0.0):
    """fraction of x = q/k in (0, 1/2] (the split is symmetric in x <-> 1 - x) for which eps(k) - eps(q) - eps(k - q) > 0,
    and the smallest open x; q and k - q both >= qmin."""
    xs = np.linspace(1e-4, 0.5, 5000)
    q = xs * kk
    ok = (q >= qmin) & (kk - q >= qmin)
    gexc = eps(kk) - eps(q) - eps(kk - q)
    op = (gexc > 0) & ok
    return dict(k=kk, open_fraction=float(op[ok].mean()) if ok.any() else None,
                smallest_open_x=float(xs[op].min()) if op.any() else None, symmetric_excess_ueV=float((eps(kk) - 2 * eps(kk / 2)) * 1e3))
ex2["splits_series"] = [open_splits(kk, series_eps) for kk in (0.30, 0.35, 0.38, 0.40, 0.42, 0.43, 0.45, 0.46, 0.50)]
ex2["splits_table_q_ge_0.15"] = [open_splits(kk, eps_table, 0.15) for kk in (0.32, 0.35, 0.38, 0.40, 0.42, 0.43, 0.45, 0.46, 0.50)]
ex2["thresholds_series"] = dict(k_group=feat["k_group_series"], k_sym=feat["k_sym_series"], k_phase=feat["k_phase_series"])
ex2["k_sym_table"] = feat["k_sym_table_crossings"]
# series: maximum of the phase velocity s(k)/c = 1 + a2 k^2 + a3 k^3 + a4 k^4  (d/dk: 2 a2 + 3 a3 k + 4 a4 k^2 = 0)
r = np.roots([4 * H.A4, 3 * H.A3, 2 * H.A2]); r = r[np.isreal(r)].real; r = r[r > 0]
ex2["series_phase_velocity_max_k"] = float(r.min())
R["exercise2"] = ex2

# ------------------------------------------------------------------------------------------------ Exercise 3
K = sp.symbols("k", positive=True)
nV = sp.Function("nV")
om2 = (K ** 2 / 2) * (K ** 2 / 2 + 2 * nV(K))
assert sp.simplify(sp.sqrt(om2) / K - sp.sqrt(K ** 2 / 4 + nV(K))) == 0
nVex = 1 - 3 * K ** 2 * sp.exp(-K ** 2)
y = sp.sqrt(K ** 2 / 4 + nVex)                                      # omega / k
low = sp.series(y, K, 0, 6).removeO()
alpha2_eff = sp.nsimplify(low.coeff(K, 2))
def nv(q): return 1 - 3 * q * q * math.exp(-q * q)
def om(q): return q * math.sqrt(q * q / 4 + nv(q))
def ph(q): return math.sqrt(q * q / 4 + nv(q))
mx = minimize_scalar(lambda q: -om(q), bounds=(0.3, 0.7), method="bounded", options=dict(xatol=1e-10))
mn = minimize_scalar(om, bounds=(0.7, 1.2), method="bounded", options=dict(xatol=1e-10))
lv = minimize_scalar(ph, bounds=(0.3, 1.5), method="bounded", options=dict(xatol=1e-10))
k_cross = math.sqrt(math.log(12.0))                                 # omega/k = 1  <=>  exp(-k^2) = 1/12
grid = np.linspace(1e-4, 4, 40001)
stab = min(q * q / 4 + nv(q) for q in grid)
# witnesses for the failing analogues
w = {}
w["strict_monotonicity"] = dict(k1=0.6, k2=0.8, omega1=om(0.6), omega2=om(0.8), fails=om(0.8) < om(0.6))
w["superadditivity_small_k"] = dict(k1=0.1, k2=0.1, excess=om(0.2) - 2 * om(0.1), fails=om(0.2) - 2 * om(0.1) < 0)
w["superadditivity_roton"] = dict(k1=mn.x / 2, k2=mn.x / 2, excess=om(mn.x) - 2 * om(mn.x / 2), fails=om(mn.x) - 2 * om(mn.x / 2) < 0)
w["sound_line_le"] = dict(k=0.5, omega=om(0.5), ck=0.5, fails=om(0.5) < 0.5)
w["sub_sound_strictMono"] = dict(a=0.1, b=0.2, val_a=om(0.1) - 0.1, val_b=om(0.2) - 0.2, fails=(om(0.2) - 0.2) < (om(0.1) - 0.1))
w["sound_lt_phase_velocity"] = dict(range=[0.0, k_cross], at_k=0.9, phase_velocity=ph(0.9), fails=ph(0.9) < 1)
w["landau_velocity_eq_c"] = dict(v_L=lv.fun, at_k=lv.x, fails=lv.fun < 1)
w["alpha2_value"] = dict(alpha2_bogoliubov=0.125, alpha2_here=str(alpha2_eff), fails=True)
w["band_with_alpha2_1_8"] = dict(k=0.5, lhs=abs(om(0.5) - 0.5 * (1 + 0.125 * 0.25)), bound=1 * 0.125 ** 2 * 0.5 ** 5 / 2,
                                 fails=abs(om(0.5) - 0.5 * (1 + 0.125 * 0.25)) > 0.125 ** 2 * 0.5 ** 5 / 2)
w["universal_form"] = dict(k=0.5, ratio=om(0.5) / 0.5, sqrt_1_plus_k2_4=math.sqrt(1 + 0.25 / 4), fails=abs(om(0.5) / 0.5 - math.sqrt(1 + 0.25 / 4)) > 1e-6)
holds = {"bogEps_zero": om(0.0) == 0.0, "bogEps_nonneg_and_pos(stability)": stab > 0, "bogEps_neg (even)": True,
         "sound_speed_limit (omega/k -> c)": abs(ph(1e-6) - 1) < 1e-9}
ex3 = dict(phase_velocity=str(y), low_k_series=str(low), alpha2_eff=str(alpha2_eff),
           maxon=dict(k=mx.x, omega=om(mx.x)), roton=dict(k=mn.x, omega=om(mn.x)), landau=dict(k=lv.x, v_L=lv.fun),
           min_k2_4_plus_nV=stab, k_where_omega_over_k_returns_to_c=k_cross, witnesses_fail=w, analogues_that_hold=holds)
R["exercise3"] = ex3
(HERE / "sol05_numbers.json").write_text(json.dumps(R, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
print(json.dumps(R, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))[:10000])
