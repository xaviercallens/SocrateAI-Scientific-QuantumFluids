"""Solutions to the exercises of Chapter 4 (Appendix C): every computed number of chapters/sol04.tex.
  .venv/bin/python book/figures/sol04_numbers.py        (about a minute: sympy series, exact-rational coefficients to T^61)
Writes figures/sol04_numbers.json.

Exercise 1  alpha_1 only: exact inverse, density of states to u^11 by sympy, the closed form (-1)^n C(2n-2, n-2) alpha_1^(n-2),
            the T^4 coefficient B by sympy from (ch04:eq-series), its ratio to A, and a numerical-quadrature check of B for a test
            value of alpha_1 (a check of sign and size, not a statement about helium).
Exercise 2  alpha_2 only: g_{2n+2} = (-1)^n C(3n+2, n) alpha_2^n checked by sympy reversion (n <= 7) and by the chapter's
            exact-rational reversion (ch04_series_ext.dos, alpha_2 = 31/20, n <= 12).
Exercise 3  coefficients c_p of T^p for the paper's coefficient set (ch04_series_ext.cv_coeffs, exact rationals x mpmath zeta),
            p = 3..61; root test; the order of the smallest term at several T against Theta/T; its size against exp(-Theta/T).
"""
import json, math, sys
from fractions import Fraction as Fr
from pathlib import Path
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ch04_common as cc                                         # noqa: E402
import ch04_series_ext as se                                     # noqa: E402

R = {"script": "book/figures/sol04_numbers.py", "sympy": sp.__version__}
u, a1, a2, T, V, kB, hb, c = sp.symbols("u alpha_1 alpha_2 T V k_B hbar c", positive=True)

# ------------------------------------------------------------------------------------------------ Exercise 1
k1 = (-1 + sp.sqrt(1 + 4 * a1 * u)) / (2 * a1)
assert sp.simplify(k1 * (1 + a1 * k1) - u) == 0
assert sp.limit(k1, a1, 0) == u                                   # the root with k -> u as alpha_1 -> 0 (k(0) = 0)
g1 = sp.diff(k1 ** 3 / 3, u)
NS = 12
ser = sp.series(g1, u, 0, NS).removeO()
coef1 = {n: sp.factor(sp.simplify(ser.coeff(u, n))) for n in range(0, NS)}
closed1 = {n: (-1) ** n * sp.binomial(2 * n - 2, n - 2) * a1 ** (n - 2) for n in range(2, NS)}
assert all(sp.simplify(coef1[n] - closed1[n]) == 0 for n in range(2, NS)) and coef1[0] == 0 and coef1[1] == 0
# the T^4 term: (ch04:eq-series) with n = 3 and g_3 = -4 alpha_1
n = 3
Cterm = V * kB ** (n + 2) / (2 * sp.pi ** 2 * (hb * c) ** (n + 1)) * coef1[3] * sp.factorial(n + 2) * sp.zeta(n + 2)
B_claim = -240 * sp.zeta(5) * a1 * V * kB ** 5 / (sp.pi ** 2 * hb ** 4 * c ** 4)
assert sp.simplify(Cterm - B_claim) == 0
# the same from the energy (ch04:eq-series-E), differentiated
Eterm = V / (2 * sp.pi ** 2) * coef1[3] * sp.factorial(n + 1) * sp.zeta(n + 2) * (kB * T) ** (n + 2) / (hb * c) ** (n + 1)
assert sp.simplify(sp.diff(Eterm, T) - B_claim * T ** 4) == 0
A_expr = 2 * sp.pi ** 2 * kB ** 4 * V / (15 * hb ** 3 * c ** 3)
ratio_BA = sp.simplify(B_claim / A_expr)                          # = -(1800 zeta(5)/pi^4) alpha_1 k_B/(hbar c)
ratio_num = float(sp.N(-1800 * sp.zeta(5) / sp.pi ** 4))
assert sp.simplify(ratio_BA - sp.Rational(-1800) * sp.zeta(5) / sp.pi ** 4 * a1 * kB / (hb * c)) == 0
# numerical check by quadrature for a TEST value alpha_1 = 0.01 A (dimensionless units: k in 1/A, temperature as theta*k_T)
from scipy.integrate import quad
THETA = cc.THETA                                                  # hbar c / k_B in K A
def cv_reduced(tau, alpha):
    """C_V / (V k_B /(2 pi^2)) in A^-3 for eps = hbar c k (1 + alpha k), k_B T = hbar c tau (tau in 1/A)."""
    f = lambda k: (lambda x: x * x * math.exp(-x) / (1 - math.exp(-x)) ** 2 if x < 700 else 0.0)(k * (1 + alpha * k) / tau) * k * k
    return quad(f, 0, 60 * tau, epsabs=0, epsrel=1e-13, limit=400)[0]
alpha_test = 0.01
rows = []
for TK in (0.02, 0.05, 0.1):
    tau = TK / THETA
    ex = cv_reduced(tau, alpha_test)
    a_term = (4 * math.pi ** 4 / 15) * tau ** 3                    # Debye: int k^2 f(k/tau) dk = tau^3 int x^4 e^x/(e^x-1)^2 = tau^3 4 pi^4/15
    b_term = -4 * alpha_test * 120 * float(sp.zeta(5)) * tau ** 4  # g_3 * 5! zeta(5) tau^4
    rows.append(dict(T_K=TK, exact_over_A=ex / a_term, series_A_plus_B_over_A=1 + b_term / a_term,
                     B_T_over_A_predicted=b_term / a_term, B_T_over_A_measured=ex / a_term - 1,
                     ratio_measured_to_predicted=(ex / a_term - 1) / (b_term / a_term)))
R["exercise1"] = {"g_n_alpha1": {n_: str(coef1[n_]) for n_ in range(2, NS)},
                  "closed_form_checked_through_n": NS - 1,
                  "binomials_2n-2_n-2": [int(sp.binomial(2 * m - 2, m - 2)) for m in range(2, NS)],
                  "B": str(B_claim), "B_over_A_times_T": str(ratio_BA * T), "B_over_A_numeric_factor": ratio_num,
                  "theta_K_A": THETA, "k_T_per_K": 1 / THETA,
                  "B_T_over_A_per_alpha1_per_K_in_1_over_A": ratio_num / THETA,
                  "quadrature_check_alpha1_0.01A": rows}

# ------------------------------------------------------------------------------------------------ Exercise 2
k = sp.symbols("k")
NMAX = 7
order = 2 * NMAX + 4
# series reversion of u = k (1 + a2 k^2) by iteration k <- u - a2 k^3 (exact in sympy, truncated at u^order)
kk = u
for _ in range(order):
    kk = sp.expand(u - a2 * sp.series(kk ** 3, u, 0, order).removeO())
    kk = sum(kk.coeff(u, j) * u ** j for j in range(order))
g2 = sp.expand(sp.series(kk ** 2 * sp.diff(kk, u), u, 0, order - 1).removeO())
check2 = []
for nn in range(0, NMAX + 1):
    got = sp.simplify(g2.coeff(u, 2 * nn + 2))
    want = (-1) ** nn * sp.binomial(3 * nn + 2, nn) * a2 ** nn
    odd = sp.simplify(g2.coeff(u, 2 * nn + 3)) if 2 * nn + 3 < order - 1 else 0
    check2.append(dict(n=nn, power=2 * nn + 2, g=str(got), closed=str(want), equal=bool(sp.simplify(got - want) == 0), next_odd_coeff=str(odd)))
assert all(r["equal"] for r in check2)
# the binomial step of the Lagrange inversion: [k^{2n}] (1 + a2 k^2)^{-(2n+3)} = C(-(2n+3), n) a2^n = (-1)^n C(3n+2, n) a2^n
lag = [dict(n=nn, value=str(sp.expand(sp.series((1 + a2 * k ** 2) ** (-(2 * nn + 3)), k, 0, 2 * nn + 1).removeO().coeff(k, 2 * nn))),
            closed=str((-1) ** nn * sp.binomial(3 * nn + 2, nn) * a2 ** nn)) for nn in range(0, NMAX + 1)]
# independent: the chapter's exact-rational reversion with alpha_2 = 31/20 only
A2 = Fr(31, 20)
gr = se.dos({2: A2}, 2 * 12 + 2)
rat = [dict(n=nn, g=str(gr[2 * nn + 2]), closed=str((-1) ** nn * math.comb(3 * nn + 2, nn) * A2 ** nn),
            equal=gr[2 * nn + 2] == (-1) ** nn * math.comb(3 * nn + 2, nn) * A2 ** nn, odd_zero=gr[2 * nn + 1] == 0) for nn in range(0, 13)]
assert all(r["equal"] and r["odd_zero"] for r in rat)
R["exercise2"] = {"sympy_reversion": check2, "lagrange_binomial_step": lag, "exact_rational_alpha2_31_20": rat,
                  "C(3n+2,n)_n0..8": [math.comb(3 * nn + 2, nn) for nn in range(0, 9)],
                  "chapter_brackets_alpha3..6=0": {"g4": "-5 a2", "g6": "7*4 a2^2 = 28 a2^2", "g8": "-3*55 a2^3 = -165 a2^3"}}

# ------------------------------------------------------------------------------------------------ Exercise 3
co, g = se.cv_coeffs(61)                                         # {p: c_p (mpmath)} for p = n + 1, n = 2..61
ps = sorted(co)
cp = {p: float(co[p]) for p in ps}
A = cp[3]
# critical points of u(k) = k (1 + a2 k^2 + a3 k^3 + a4 k^4): du/dk = 1 + 3 a2 k^2 + 4 a3 k^3 + 5 a4 k^4 = 0
al = cc.ALPHA
roots = np.roots([5 * al["a4"], 4 * al["a3"], 3 * al["a2"], 0.0, 1.0])
uc = [r * (1 + al["a2"] * r ** 2 + al["a3"] * r ** 3 + al["a4"] * r ** 4) for r in roots]
j = int(np.argmin(np.abs(uc)))
Theta = float(cc.THETA * abs(uc[j]))
root_test = {p: float((abs(co[p]) / math.factorial(p)) ** (1.0 / p)) for p in (20, 30, 40, 50, 60) if p in co}


def terms(TK):
    """|c_p| T^p / (A T^3) for p = 3..61 (0 where c_p = 0, i.e. p = 4)."""
    return {p: abs(cp[p]) * TK ** p / (A * TK ** 3) for p in ps}


def pstar(TK):
    t = terms(TK)
    env = {p: max(t.get(p - 1, 0), t[p], t.get(p + 1, 0)) for p in ps if p >= 5 and p + 1 in t}
    p0 = min(env, key=env.get)
    pmin = min((p for p in ps if p >= 5), key=lambda p: t[p])
    return p0, env[p0], pmin, t[pmin]


opt = []
for TK in (0.1, 0.15, 0.2, 0.3, 0.4, 0.5):
    p0, e0, pmin, tmin = pstar(TK)
    opt.append(dict(T=TK, pstar_envelope=p0, envelope_value=e0, pstar_plain=pmin, smallest_term=tmin,
                    Theta_over_T=Theta / TK, exp_minus_Theta_over_T=math.exp(-Theta / TK), ratio_term_to_exp=e0 / math.exp(-Theta / TK)))
# fit ln(envelope minimum) = ln a + s ln T - b/T over 0.08..0.6 K
Ts = np.linspace(0.08, 0.6, 27)
ys = np.array([math.log(pstar(t)[1]) for t in Ts])
M = np.column_stack([np.ones_like(Ts), np.log(Ts), -1.0 / Ts])
(lna, s_fit, b_fit), *_ = np.linalg.lstsq(M, ys, rcond=None)
# Stirling: ln(p! x^p) ~ p ln(p x / e); minimum at p = 1/x, value -1/x
x = 0.2 / Theta
stir = [dict(p=p, lnfac_plus_p_lnx=math.lgamma(p + 1) + p * math.log(x), stirling=p * math.log(p * x / math.e)) for p in (15, 20, 22, 23, 25, 30)]
R["exercise3"] = {"Theta_c_K": Theta, "u_c_per_A": [float(uc[j].real), float(uc[j].imag)], "abs_u_c": float(abs(uc[j])),
                  "one_over_Theta": 1 / Theta, "root_test": root_test, "optimal_truncation": opt,
                  "envelope_fit_0.08_0.6K": dict(a=math.exp(lna), s=float(s_fit), b_K=float(b_fit)),
                  "stirling_check_T0.2": stir, "c_p_over_A_p5_to_14": {p: cp[p] / A for p in ps if 5 <= p <= 14}}
(HERE / "sol04_numbers.json").write_text(json.dumps(R, indent=1, default=str))
print(json.dumps(R, indent=1, default=str)[:9000])
