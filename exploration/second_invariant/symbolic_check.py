"""Exact check: dH/dt == 0 and d(mass)/dt == 0 as polynomial identities (generic real symbols x_n, y_n, k_n, D, mu)."""
import sympy as sp
def check(N, seam, general_k=True, perturb=False):
    x = sp.symbols(f"x0:{N+1}", real=True); y = sp.symbols(f"y0:{N+1}", real=True)
    k = sp.symbols(f"k0:{N+1}", real=True) if general_k else [sp.Integer(2) ** n for n in range(N + 1)]
    D, mu = sp.symbols("D mu", real=True)
    v = [x[n] + sp.I * y[n] for n in range(N + 1)]
    top = sp.I * mu * v[N] ** 2 if seam == "gpe" else 0
    ve = v + [top]
    dv = [(k[n-1] * v[n-1] ** 2 if n else 0) - k[n] * sp.conjugate(v[n]) * ve[n+1] - sp.I * D * k[n] ** 2 * v[n] for n in range(N + 1)]
    w = [sp.Rational(1, 2 ** n) for n in range(N + 1)]
    if perturb: w[2] = sp.Rational(1, 3)          # negative control: wrong weight on one shell
    H = sum(w[n] * (D * k[n] ** 2 * (x[n] ** 2 + y[n] ** 2)) for n in range(N + 1)) \
      + sum(w[n] * k[n] * sp.im(sp.expand(sp.conjugate(v[n]) ** 2 * v[n+1])) for n in range(N)) \
      + (sp.Rational(1, 2) * mu * k[N] * w[N] * (x[N] ** 2 + y[N] ** 2) ** 2 if seam == "gpe" else 0)
    mass = sum(x[n] ** 2 + y[n] ** 2 for n in range(N + 1))
    def rate(F):
        return sp.expand(sum(sp.diff(F, x[n]) * sp.re(sp.expand(dv[n])) + sp.diff(F, y[n]) * sp.im(sp.expand(dv[n])) for n in range(N + 1)))
    return rate(H) == 0, rate(mass) == 0
for N in (3, 5):
    for seam in ("trunc", "gpe"):
        print(f"N={N} seam={seam} general k: dH/dt==0: %s, dmass/dt==0: %s" % check(N, seam))
print("negative control (wrong weight 1/3 on shell 2): dH/dt==0: %s" % check(4, "trunc", perturb=True)[0])
