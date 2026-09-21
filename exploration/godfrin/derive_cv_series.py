"""Independent computer-algebra derivation of the phonon specific-heat series of
Godfrin et al., PRB 103, 104516 (2021), Eq. (22):  C_V = A T^3 + C T^5 + D T^6 + E T^7 + K T^8 + L T^9.

The paper prints closed forms for A..L and remarks that earlier published series (Phillips et al.,
Greywall) contain errors. An earlier check in this repo reproduced the NUMERICAL values from the
printed closed forms -- which tests arithmetic, not the formulas. This script derives the closed forms
from scratch and compares them symbolically with the printed ones.

Derivation:  eps = hbar c k (1 + a2 k^2 + ... + a6 k^6)      [paper Eq. (2), alpha_1 = 0]
  1. revert the series:  k(u), u = eps/(hbar c)               [Lagrange inversion]
  2. density of states:  d(k^3/3)/d eps
  3. E(T) = V/(2 pi^2) * sum_j c_j (kB T)^(j+2)/(hbar c)^... * Gamma(j+2) zeta(j+2)
     using  int_0^inf x^n/(e^x - 1) dx = n! zeta(n+1)         [Lean: BoseIntegral.bose_integral_nat]
  4. C_V = dE/dT.
"""
import sympy as sp

a1, a2, a3, a4, a5, a6 = sp.symbols("alpha1:7")
kB, hbar, c, V, T, u = sp.symbols("k_B hbar c V T u", positive=True)
ORDER = 8                                   # k(u) through u^7, as in the paper

# 1. series reversion of u(k) = k (1 + a2 k^2 + ... + a6 k^6)
k = sp.symbols("k")
uk = k * (1 + a1*k + a2*k**2 + a3*k**3 + a4*k**4 + a5*k**5 + a6*k**6)   # alpha_1 kept general here
coeffs = sp.symbols("b1:%d" % ORDER)
kser = sum(b * u**(i + 1) for i, b in enumerate(coeffs))
expr = sp.expand(uk.subs(k, kser))
sol = {}
for n in range(1, ORDER):
    eq = sp.expand(expr).coeff(u, n) - (1 if n == 1 else 0)
    eq = eq.subs(sol)
    b = coeffs[n - 1]
    sol[b] = sp.solve(eq, b)[0]
kser = sp.expand(kser.subs(sol))
# 1b. compare with the inverse series PRINTED in the paper (source lines 1359-1372), alpha_1 general
eta = (132*a1**6 - 330*a1**4*a2 + 120*a1**3*a3 + 180*a1**2*a2**2 - 36*a1**2*a4 - 72*a1*a2*a3
       + 8*a1*a5 - 12*a2**3 + 8*a2*a4 + 4*a3**2 - a6)
printed_inv = {1: 1, 2: -a1, 3: 2*a1**2 - a2, 4: -5*a1**3 + 5*a1*a2 - a3,
               5: 14*a1**4 - 21*a1**2*a2 + 6*a1*a3 + 3*a2**2 - a4,
               6: -42*a1**5 + 84*a1**3*a2 - 28*a1**2*a3 - 28*a1*a2**2 + 7*a1*a4 + 7*a2*a3 - a5, 7: eta}
inv_ok = True
for n, pr in printed_inv.items():
    d = sp.expand(kser.coeff(u, n) - pr)
    inv_ok &= (d == 0)
    print(f"inverse series, (omega/c)^{n}: {'matches' if d == 0 else 'DIFFERS by ' + str(d)}")
kser = sp.expand(kser.subs(a1, 0))          # the paper's C_V formulas are for alpha_1 = 0

# 2. d(k^3/3)/du, truncated consistently
g = sp.series(sp.diff(kser**3 / 3, u), u, 0, ORDER + 2).removeO()

# 3./4. energy and specific heat, term by term:  int u^n/(e^{hbar c u/kBT}-1) du = (kBT/hbar c)^(n+1) n! zeta(n+1)
CV = 0
for n in range(2, ORDER + 1):            # g_2..g_8 only: g_9 would need k(u) to u^8 and is not complete
    cn = sp.expand(g).coeff(u, n)
    if cn == 0: continue
    # E_n = V/(2 pi^2) * hbar c * cn * (kB T/(hbar c))^(n+2) * (n+1)! zeta(n+2)
    En = V / (2*sp.pi**2) * hbar*c * cn * (kB*T/(hbar*c))**(n + 2) * sp.factorial(n + 1) * sp.zeta(n + 2)
    CV += sp.diff(En, T)
CV = sp.expand(CV)

printed = {
 3: 2*sp.pi**2*kB**4*V/(15*c**3*hbar**3),
 5: -40*sp.pi**4*a2*kB**6*V/(21*c**5*hbar**5),
 6: -15120*a3*kB**7*V*sp.zeta(7)/(sp.pi**2*c**6*hbar**6),
 7: 224*sp.pi**6*kB**8*V*(4*a2**2 - a4)/(15*c**7*hbar**7),
 8: 1451520*kB**9*V*sp.zeta(9)*(9*a2*a3 - a5)/(sp.pi**2*c**8*hbar**8),
 9: -640*sp.pi**8*kB**10*V*(55*a2**3 - 30*a2*a4 - 15*a3**2 + 3*a6)/(11*c**9*hbar**9),
}
names = {3: "A", 5: "C", 6: "D", 7: "E", 8: "K", 9: "L"}
print()
allok = True
for p, name in names.items():
    derived = sp.simplify(CV.coeff(T, p))
    diff = sp.simplify(derived - printed[p])
    ok = diff == 0
    allok &= ok
    print(f"{name} (T^{p}): {'MATCHES the printed closed form' if ok else 'DIFFERS'}")
    if not ok:
        print("   derived:", sp.factor(derived)); print("   printed:", printed[p]); print("   ratio  :", sp.simplify(derived/printed[p]))
print("\nT^4 coefficient (paper: absent because alpha_1 = 0):", sp.simplify(CV.coeff(T, 4)))
print("INVERSE SERIES: all 7 printed coefficients match" if inv_ok else "INVERSE SERIES: DISCREPANCY")
print("C_V SERIES: ALL SIX MATCH" if allok else "C_V SERIES: DISCREPANCY FOUND")
