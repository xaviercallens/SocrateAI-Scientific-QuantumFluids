#!/usr/bin/env python3
"""Solutions of the exercises of Chapter 6 (Appendix C): every number quoted by chapters/sol06.tex.

    PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext nice .venv/bin/python book/figures/sol06_kt.py

Exercise 1  sympy: d/dl [2u - pi ln u - (c/2) y^2] = 0 for u' = c y^2, y' = (2 - pi/u) y; Taylor expansion of f at pi/2; level sets
            x^2 - (pi c/4) y^2 = const and the separatrix slopes; CVODE check that the flows with c = 1 and c = 4 pi^3 are the same flow
            after the rescaling y -> y sqrt(c / 4 pi^3) (so the trapping statement changes only through H_c).
Exercise 2  sympy: the expansion x' = (4/pi) x^2 - (16/(3 pi^2)) x^3 + ..., 1/x' = pi/(4x^2) + 1/(3x) + O(1); the asymptotic series of
            l (n_s lambda^2 - 4) = 2 - (2/3) ln l / l + C1/l + (2/9) (ln l)^2 / l^2 + ...; the constant C1 of the chapter's critical
            trajectory (u0 = 0.6 on the separatrix) from the exact quadrature (mpmath, 40 digits); the quadrature values of
            l (n_s lambda^2 - 4) at l = 10 ... 10^5 against CVODE (Adams, rtol 1e-12, one call each, as in ch06_flow_compute.py) and
            against the asymptotic series with two, three and four terms.
Exercise 3  sympy: |e^{i phi} - 1| = 2 |sin(phi/2)|; tau = sin(k d/2)/(k d/2); k1 d = pi (d = L/2): tau = 2/pi, compared with the value of the
            gold curve stored by the chapter (ch06_cert_numbers.json, synthetic_dipoles_L64, d = 32); where tau = 0.9; two configurations with
            rho(k1) = 0 and large matching cost; a Monte Carlo gas of tight pairs (optimal matching by linear_sum_assignment, minimum image).
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
import numpy as np
import sympy as sp
import mpmath as mp
from scipy.optimize import linear_sum_assignment, brentq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sol_common import Numbers, cvode_env, fmt

N = Numbers("06", "sSix", "figures/sol06_kt.py")
env = cvode_env()
N.put("cvode_env", env)
from rusty_sundials import CvodeSolver

pi = math.pi
# ----------------------------------------------------------------------------------------------------- Exercise 1 (sympy)
l = sp.symbols("l", real=True)
c, X, Y = sp.symbols("c x y", positive=True)
u_ = sp.Function("u")(l); y_ = sp.Function("y")(l)
Hc = 2 * u_ - sp.pi * sp.log(u_) - c / 2 * y_ ** 2
dH = sp.diff(Hc, l).subs({sp.Derivative(u_, l): c * y_ ** 2, sp.Derivative(y_, l): (2 - sp.pi / u_) * y_})
assert sp.simplify(dH) == 0
uu, xx = sp.symbols("u x", real=True)
f_sym = 2 * uu - sp.pi * sp.log(uu)
f2 = sp.simplify(sp.diff(f_sym, uu, 2).subs(uu, sp.pi / 2))
f3 = sp.simplify(sp.diff(f_sym, uu, 3).subs(uu, sp.pi / 2))
assert sp.simplify(f2 - 4 / sp.pi) == 0 and sp.simplify(f3 + 16 / sp.pi ** 2) == 0
ser = sp.series(f_sym.subs(uu, sp.pi / 2 + xx) - f_sym.subs(uu, sp.pi / 2), xx, 0, 5).removeO()
assert sp.simplify(ser - (2 / sp.pi * xx ** 2 - sp.Rational(8, 3) / sp.pi ** 2 * xx ** 3 + 4 / sp.pi ** 3 * xx ** 4)) == 0
quad_form = sp.expand((2 / sp.pi * xx ** 2 - c / 2 * Y ** 2) * sp.pi / 2)          # level sets: x^2 - (pi c / 4) y^2 = const
assert sp.simplify(quad_form - (xx ** 2 - sp.pi * c / 4 * Y ** 2)) == 0
slope = sp.sqrt(4 / (sp.pi * c))                                                   # separatrix |y| = slope * |x|
assert sp.simplify(slope.subs(c, 4 * sp.pi ** 3) - 1 / sp.pi ** 2) == 0
N.put("ex1_sympy", dict(dH_dl="0 (simplified)", f2_at_pi_over_2="4/pi", f3_at_pi_over_2="-16/pi^2", series=str(ser),
                        level_sets="x^2 - (pi c/4) y^2 = const", separatrix_slope="2/sqrt(pi c), = 1/pi^2 at c = 4 pi^3"))

# CVODE: the flow with c = 1 from (u0, y0) and the flow with c = 4 pi^3 from (u0, y0 sqrt(1/(4 pi^3))) have the same u(l)
def rhs_c(cc):
    def r(t, s):
        return [cc * s[1] * s[1], (2 - pi / s[0]) * s[1]]
    return r
u0, y0 = 0.9, 0.5                     # c = 1: H_1 = f(0.9) - 0.125 = 2.0310 > f(pi/2) = 1.7229, trapped
f_ = lambda u: 2 * u - pi * math.log(u)
FC = f_(pi / 2)
H1 = f_(u0) - 0.5 * y0 ** 2
scale = math.sqrt(1.0 / (4 * pi ** 3))
grid = np.linspace(0, 30, 121)
sA = CvodeSolver("adams", 1e-11, 1e-14, 500000); sB = CvodeSolver("adams", 1e-11, 1e-14, 500000)
a = [u0, y0]; b = [u0, y0 * scale]; dmax = 0.0; hdrift = 0.0; umax = u0
for t0, t1 in zip(grid[:-1], grid[1:]):
    _, a = sA.solve(rhs_c(1.0), float(t0), a, float(t1))
    _, b = sB.solve(rhs_c(4 * pi ** 3), float(t0), b, float(t1))
    dmax = max(dmax, abs(a[0] - b[0])); umax = max(umax, a[0])
    hdrift = max(hdrift, abs(f_(a[0]) - 0.5 * a[1] ** 2 - H1))
ustar = brentq(lambda u: f_(u) - H1, 1e-6, pi / 2)
N.add("ResU", dmax, fmt(dmax, 2), "max |u_{c=1}(l) - u_{c=4pi^3}(l)| over 120 outputs, l <= 30, Adams rtol 1e-11 (chain)")
N.add("ResHone", hdrift, fmt(hdrift, 2), "max drift of H_1 = f(u) - y^2/2 along the c = 1 trajectory")
N.add("ResUmax", umax, f"{umax:.4f}", "largest u on the c = 1 trajectory (stays below pi/2)")
N.add("ResUstar", ustar, f"{ustar:.4f}", "root of f(u*) = H_1, the end point of the c = 1 trajectory")
N.add("ResUend", a[0], f"{a[0]:.4f}", "u(30) of the c = 1 trajectory")
N.add("ResHonezero", H1, f"{H1:.4f}", "H_1(0.9, 0.5)")
N.add("Fc", FC, f"{FC:.4f}", "f(pi/2) = pi - pi ln(pi/2)")
N.put("ex1_rescaling", dict(u0=u0, y0_c1=y0, y0_c4pi3=y0 * scale, l_max=30.0, n_outputs=120, max_abs_du=dmax, H1=H1, H1_drift=hdrift, u_end=a[0], u_star=ustar))

# ----------------------------------------------------------------------------------------------------- Exercise 2 (sympy + mpmath + CVODE)
g_sym = sp.series(2 * (f_sym.subs(uu, sp.pi / 2 + xx) - f_sym.subs(uu, sp.pi / 2)), xx, 0, 6).removeO()
assert sp.simplify(sp.expand(g_sym) - sp.expand(4 / sp.pi * xx ** 2 - sp.Rational(16, 3) / sp.pi ** 2 * xx ** 3 + 8 / sp.pi ** 3 * xx ** 4
                                               - sp.Rational(64, 5) / sp.pi ** 4 * xx ** 5)) == 0
inv = sp.series(1 / (2 * (f_sym.subs(uu, sp.pi / 2 + xx) - f_sym.subs(uu, sp.pi / 2))), xx, 0, 1).removeO()
assert sp.simplify(sp.expand(inv) - sp.expand(sp.pi / (4 * xx ** 2) + 1 / (3 * xx) - sp.Rational(1, 18) / sp.pi)) == 0, inv
N.put("ex2_sympy", dict(xprime_series=str(sp.expand(g_sym)), inverse_series=str(sp.expand(inv)),
                        note="1/x' = pi/(4x^2) + 1/(3x) - 1/(18 pi) + O(x): the logarithm comes from the 1/(3x) term"))
# asymptotic series of A(l) = l (n_s lambda^2 - 4) with w = 4X/pi, X = pi/2 - u > 0 :  1/w = l - (1/3) ln w - K' + O(w)
# check of the two-step inversion with sympy on the ansatz (eps = 1/l, Lg = ln l): done numerically below against the exact quadrature.

mp.mp.dps = 40
U0 = mp.mpf("0.6"); X0 = mp.pi / 2 - U0
def gneg(Xv):                      # x' at x = -X  (the separatrix, X = pi/2 - u > 0):  2 (f(pi/2 - X) - f(pi/2))
    return -4 * Xv - 2 * mp.pi * mp.log(1 - 2 * Xv / mp.pi)
Xs = sp.symbols("X", positive=True)
_rt_series = sp.series(1 / (-4 * Xs - 2 * sp.pi * sp.log(1 - 2 * Xs / sp.pi)) - sp.pi / (4 * Xs ** 2) + 1 / (3 * Xs), Xs, 0, 16).removeO()
_rt_coef = [sp.N(_rt_series.coeff(Xs, n), 50) for n in range(16)]
assert sp.simplify(_rt_series.coeff(Xs, 0) + sp.Rational(1, 18) / sp.pi) == 0
def Rt(Xv):                        # 1/g(-X) - pi/(4 X^2) + 1/(3 X): regular at X = 0 (Taylor series below X = 0.02: no cancellation)
    if Xv < mp.mpf("0.02"):
        return mp.fsum(mp.mpf(str(cf)) * Xv ** n for n, cf in enumerate(_rt_coef))
    return 1 / gneg(Xv) - mp.pi / (4 * Xv ** 2) + 1 / (3 * Xv)
IR = mp.quad(Rt, [0, mp.mpf("0.02"), mp.mpf("0.1"), X0])
K = -mp.pi / (4 * X0) - mp.log(X0) / 3 + IR
Kp = K + mp.log(mp.pi / 4) / 3
C1 = 2 * Kp + 1
def l_of_X(Xv):                    # exact RG 'time' at which the separatrix trajectory from u0 = 0.6 reaches u = pi/2 - X
    pts = [0, Xv] if Xv <= mp.mpf("0.02") else [0, mp.mpf("0.02"), Xv]
    return mp.pi / (4 * Xv) + mp.log(Xv) / 3 + K - mp.quad(Rt, pts)
def X_of_l(L):
    guess = mp.pi / (4 * (L - Kp + mp.log(L) / 3))
    return mp.findroot(lambda Xv: l_of_X(Xv) - L, guess)
# check of l_of_X against a direct quadrature at one point
Xt = mp.mpf("0.05")
direct = mp.quad(lambda s: 1 / gneg(s), [Xt, X0])
assert abs(direct - l_of_X(Xt)) < mp.mpf("1e-25")
N.add("Kconst", float(K), f"{float(K):.5f}", "K = lim [l(X) - pi/(4X) - (1/3) ln X], u0 = 0.6 on the separatrix, mpmath quadrature (40 digits)")
N.add("Kprime", float(Kp), f"{float(Kp):.5f}", "K' = K + (1/3) ln(pi/4)")
N.add("Cone", float(C1), f"{float(C1):.4f}", "C1 = 2K' + 1: coefficient of 1/l in l (n_s lambda^2 - 4) for this trajectory")
N.add("Xzero", float(X0), f"{float(X0):.4f}", "X0 = pi/2 - 0.6")

# CVODE re-run of the chapter's critical trajectory (same call as ch06_flow_compute.py: one Adams solve from 0 to l, rtol 1e-12, atol 1e-17)
def sep_y(u):
    return math.sqrt(max(f_(u) - FC, 0.0) / (2 * pi ** 3))
ys0 = sep_y(0.6)
rows = []
for L in (10, 30, 100, 300, 1000, 3000, 10000, 100000):
    Xl = X_of_l(mp.mpf(L)); A_ex = float(L * (4 / (1 - 2 * Xl / mp.pi) - 4))
    two = 2 - (2 / 3) * math.log(L) / L
    three = two + float(C1) / L
    four = three + (2 / 9) * math.log(L) ** 2 / L ** 2
    row = dict(l=L, A_exact=A_ex, two_term=two, three_term=three, four_term=four,
               dev_two=A_ex - two, dev_three=A_ex - three, dev_four=A_ex - four)
    if L <= 10000:
        n = [0]
        def rr(t, s):
            n[0] += 1
            return [4 * pi ** 3 * s[1] * s[1], (2 - pi / s[0]) * s[1]]
        _, s = CvodeSolver("adams", 1e-12, 1e-17, 5_000_000).solve(rr, 0.0, [0.6, ys0], float(L))
        A_cv = L * (2 * pi / s[0] - 4)
        row.update(A_cvode=A_cv, cvode_minus_exact=A_cv - A_ex, rhs_calls=n[0], H_drift=abs(f_(s[0]) - 2 * pi ** 3 * s[1] ** 2 - FC))
    rows.append(row)
    print(row, flush=True)
N.put("ex2_table", rows)
R = {r["l"]: r for r in rows}
N.add("AexTen", R[10]["A_exact"], f"{R[10]['A_exact']:.4f}", "exact (quadrature) l (n_s lambda^2 - 4) at l = 10")
N.add("AexHundred", R[100]["A_exact"], f"{R[100]['A_exact']:.5f}", "same at l = 100")
N.add("AexTenThousand", R[10000]["A_exact"], f"{R[10000]['A_exact']:.7f}", "same at l = 10^4")
N.add("AcvTen", R[10]["A_cvode"], f"{R[10]['A_cvode']:.4f}", "CVODE at l = 10")
N.add("AcvHundred", R[100]["A_cvode"], f"{R[100]['A_cvode']:.5f}", "CVODE at l = 100")
N.add("AcvTenThousand", R[10000]["A_cvode"], f"{R[10000]['A_cvode']:.7f}", "CVODE at l = 10^4")
cv_ex = max(abs(r["cvode_minus_exact"]) for r in rows if "A_cvode" in r)
N.add("CvEx", cv_ex, fmt(cv_ex, 2), "max |CVODE - quadrature| of l (n_s lambda^2 - 4), l = 10 ... 10^4")
N.add("DevTwoHundred", R[100]["dev_two"], fmt(R[100]["dev_two"], 2), "exact minus 2 - (2/3) ln l/l at l = 100")
N.add("DevTwoTenThousand", R[10000]["dev_two"], fmt(R[10000]["dev_two"], 2), "same at l = 10^4")
N.add("DevThreeHundred", R[100]["dev_three"], fmt(R[100]["dev_three"], 2), "exact minus (two terms + C1/l) at l = 100")
N.add("DevThreeTenThousand", R[10000]["dev_three"], fmt(R[10000]["dev_three"], 2), "same at l = 10^4")
N.add("DevFourHundred", R[100]["dev_four"], fmt(R[100]["dev_four"], 2), "exact minus (three terms + (2/9) ln^2 l / l^2) at l = 100")
N.add("DevFourTenThousand", R[10000]["dev_four"], fmt(R[10000]["dev_four"], 2), "same at l = 10^4")
N.add("DevFourHundredThousand", R[100000]["dev_four"], fmt(R[100000]["dev_four"], 2), "same at l = 10^5 (quadrature only)")
# independent checks of the exact value at l = 10^4: (i) direct quadrature of dl = dX/g(-X) (no regularisation, no K);
# (ii) scipy DOP853 on the scalar equation u' = 2 (f(u) - f(pi/2)) (rtol 1e-13)
from scipy.integrate import solve_ivp
def l_direct(Xv):
    pts = sorted(set([Xv] + [p for p in (mp.mpf("1e-4"), mp.mpf("1e-3"), mp.mpf("1e-2"), mp.mpf("0.1")) if p > Xv] + [X0]))
    return mp.quad(lambda s_: 1 / gneg(s_), pts)
gg = mp.pi / (4 * (10000 + 0.9 + mp.log(10000) / 3))
Xd = mp.findroot(lambda Xv: l_direct(Xv) - 10000, (gg * mp.mpf("0.9"), gg * mp.mpf("1.1")), solver="anderson")
A_direct = float(10000 * (4 / (1 - 2 * Xd / mp.pi) - 4))
sol = solve_ivp(lambda t, uv: [2 * (f_(uv[0]) - FC)], (0, 10000), [0.6], method="DOP853", rtol=1e-13, atol=1e-16)
A_dop = 10000 * (2 * pi / sol.y[0, -1] - 4)
N.put("ex2_independent_checks_l1e4", dict(direct_quadrature=A_direct, dop853=A_dop, dop853_nfev=int(sol.nfev), regularised=R[10000]["A_exact"]))
N.add("AdirTenThousand", A_direct, f"{A_direct:.7f}", "direct quadrature (no regularisation) at l = 10^4")
N.add("AdopTenThousand", A_dop, f"{A_dop:.7f}", "scipy DOP853 rtol 1e-13 on u' = 2(f(u) - f(pi/2)) at l = 10^4")
du_cv = abs((pi / 2) ** 2 / (2 * pi) * R[10000]["cvode_minus_exact"] / 10000)
N.add("DuCvode", du_cv, fmt(du_cv, 2), "|error of u| of CVODE at l = 10^4, from the error of l (n_s lambda^2 - 4): du = u^2 dn / (2 pi l)")
N.add("HdriftCvode", R[10000]["H_drift"], fmt(R[10000]["H_drift"], 2), "|H - f(pi/2)| of the CVODE state at l = 10^4")
N.add("CvTenThousandErr", R[10000]["cvode_minus_exact"], fmt(R[10000]["cvode_minus_exact"], 2), "CVODE minus exact, l (n_s lambda^2 - 4), l = 10^4")
N.add("CvHundredErr", R[100]["cvode_minus_exact"], fmt(R[100]["cvode_minus_exact"], 2), "CVODE minus exact, l = 100")
N.add("CvDevTenThousand", R[10000]["A_cvode"] - R[10000]["two_term"], fmt(R[10000]["A_cvode"] - R[10000]["two_term"], 2), "CVODE value minus 2 - (2/3) ln l/l at l = 10^4 (the chapter's 5e-5)")
# scaling of the remainder after four terms: l^2 * dev_four / ln l  (expected bounded: the next term is O(ln l / l^2))
N.put("ex2_remainder_scaling", {str(r["l"]): r["dev_four"] * r["l"] ** 2 / math.log(r["l"]) for r in rows})
# the chapter's printed values (ch06_numbers.json) against ours
ch = json.loads((HERE / "ch06_numbers.json").read_text())
crit = {int(r["l"]): r["excess_times_l"] for r in ch["key_results"]["flow"]["critical"]}
N.put("chapter_values", crit)
if crit:
    dch = max(abs(crit[L] - R[L]["A_cvode"]) for L in crit if L in R and "A_cvode" in R[L])
    N.add("ChapterVsOurs", dch, fmt(dch, 2), "max |chapter CVODE value - our CVODE value| of l (n_s lambda^2 - 4)")

# ----------------------------------------------------------------------------------------------------- Exercise 3
ph = sp.symbols("phi", real=True)
assert sp.simplify(sp.expand(sp.Abs(sp.exp(sp.I * ph) - 1) ** 2).rewrite(sp.cos) - 4 * sp.sin(ph / 2) ** 2) == 0 or \
    sp.simplify(sp.expand((sp.exp(sp.I * ph) - 1) * (sp.exp(-sp.I * ph) - 1)) - 4 * sp.sin(ph / 2) ** 2) == 0
Lb = 64.0; k1 = 2 * pi / Lb
tau = lambda kd: math.sin(kd / 2) / (kd / 2)
tau_half = tau(k1 * Lb / 2)
cert = json.loads((HERE / "ch06_cert_numbers.json").read_text())
gold = [r for r in cert["synthetic_dipoles_L64"] if r["d"] == 32][0]
N.add("TauHalf", tau_half, f"{tau_half:.4f}", "tau = sin(pi/2)/(pi/2) = 2/pi for d = L/2, k = k1")
N.add("RhoHalf", 2 * math.sin(pi / 2) / k1, f"{2 / k1:.2f}", "|rho(k1)|/k1 = 2 sin(k1 d/2)/k1 = L/pi for d = L/2 = 32, L = 64")
N.add("GoldRho", gold["bound_k1_max"], f"{gold['bound_k1_max']:.4f}", "ch06_cert_numbers.json synthetic_dipoles_L64 d=32: |rho(k1)|/k1")
N.add("GoldTau", gold["tau_k1"], f"{gold['tau_k1']:.5f}", "same: tau")
x9 = brentq(lambda z: math.sin(z) / z - 0.9, 0.1, 1.5)
N.add("KdNinety", 2 * x9, f"{2 * x9:.3f}", "k d at which tau = 0.9 (k parallel to d)")
N.add("TauQuarter", tau(k1 * Lb / 4), f"{tau(k1 * Lb / 4):.4f}", "tau for d = L/4: 2 sqrt 2 / pi")

def rho(k, P, M):
    return np.exp(1j * (P @ k)).sum() - np.exp(1j * (M @ k)).sum()
def mi(dv, L):
    return dv - L * np.round(dv / L)
def W_opt(P, M, L):
    D = np.sqrt(((mi(P[:, None, :] - M[None, :, :], L)) ** 2).sum(-1))
    r, cidx = linear_sum_assignment(D)
    return D[r, cidx].sum()
kvec = np.array([k1, 0.0])
# (a) one pair of size L/2 perpendicular to k1
P = np.array([[10.0, 5.0]]); M = np.array([[10.0, 5.0 + 32.0]])
ra = abs(rho(kvec, P, M)); Wa = W_opt(P, M, Lb)
# (b) two parallel pairs of size d = 8 along k1, half a box apart
P = np.array([[10.0, 5.0], [42.0, 20.0]]); M = P - np.array([8.0, 0.0])
rb = abs(rho(kvec, P, M)); Wb = W_opt(P, M, Lb)
N.add("RhoPerp", ra, fmt(ra, 1), "|rho(k1)| for a pair of size L/2 perpendicular to k1")
N.add("WPerp", Wa, f"{Wa:.0f}", "its matching cost")
N.add("RhoTwo", rb, fmt(rb, 1), "|rho(k1)| for two parallel pairs (d = 8) half a box apart")
N.add("WTwo", Wb, f"{Wb:.0f}", "their matching cost")
# (c) a gas of tight pairs: N pairs, size d, random centres and orientations, optimal matching
rng = np.random.default_rng(20261010)
mc = {}
for Np, d in ((25, 1.0), (100, 1.0), (100, 3.0)):
    taus = []
    for trial in range(200):
        Cc = rng.uniform(0, Lb, (Np, 2)); th = rng.uniform(0, 2 * pi, Np)
        Dv = d * np.column_stack([np.cos(th), np.sin(th)])
        P = np.mod(Cc + Dv / 2, Lb); M = np.mod(Cc - Dv / 2, Lb)
        taus.append(abs(rho(kvec, P, M)) / (k1 * W_opt(P, M, Lb)))
    taus = np.array(taus)
    mc[f"N{Np}_d{d:g}"] = dict(mean=float(taus.mean()), median=float(np.median(taus)), p95=float(np.percentile(taus, 95)),
                              mean_prediction=float(math.sqrt(math.pi / (8 * Np))))
    print("gas", Np, d, mc[f"N{Np}_d{d:g}"], flush=True)
N.put("ex3_gas", mc)
N.add("GasMeanA", mc["N25_d1"]["mean"], f"{mc['N25_d1']['mean']:.3f}", "mean tau, 25 random pairs of size 1 in L = 64 (200 draws)")
N.add("GasMeanB", mc["N100_d1"]["mean"], f"{mc['N100_d1']['mean']:.3f}", "mean tau, 100 random pairs of size 1")
N.add("GasMeanC", mc["N100_d3"]["mean"], f"{mc['N100_d3']['mean']:.3f}", "mean tau, 100 random pairs of size 3")
N.add("GasPredA", mc["N25_d1"]["mean_prediction"], f"{mc['N25_d1']['mean_prediction']:.3f}", "sqrt(pi/(8N)) (random phases, small k d), N = 25")
N.add("GasPredB", mc["N100_d1"]["mean_prediction"], f"{mc['N100_d1']['mean_prediction']:.3f}", "sqrt(pi/(8N)), N = 100")
N.write()
