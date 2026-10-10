"""Chapter 6 -- the flow run BACKWARDS in l.  The library statements of KTFlow assume the flow equations for every real l; on the superfluid side (u < pi/2) with y != 0
the backward flow leaves u > 0 at a finite negative l (Lean: Ch06_KTForward.kt_eternal_trivial).  Here the time is computed two ways:
  * exact quadrature of the scalar reduction u' = 2 (f(u) - H0):   l_minus = - int_0^{u0} du / (2 (f(u) - H0))   (finite because f ~ -pi ln u is integrable against 1/f near 0);
  * CVODE (Adams, rtol 1e-11) on the time-reversed system (u~(s), y~(s)) = (u(-s), y(-s)), du~/ds = -4 pi^3 y~^2, dy~/ds = -(2 - pi/u~) y~ (the Python
    module's solve() with t_out < t0 did not terminate in a test, so backward integration is done by reversing the equations), to s = -l_minus - 0.02: the solution has
    collapsed (u small, y large) there.  Closer to the singular point the nonlinear solver of CVODE gives up.
Also the disordered side (u0 > pi/2): the backward flow of (1.8, 0.004) exists for all l (integrated to l = -50), so the library's hypotheses are not empty there.
Run: PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext .venv/bin/python ch06_backward.py     -> ch06_backward.json"""
import json, math
from pathlib import Path
from scipy.integrate import quad
from rusty_sundials import CvodeSolver
import rusty_sundials

pi = math.pi
OUT = Path(__file__).resolve().parent
f = lambda u: 2 * u - pi * math.log(u)
FC = f(pi / 2)
ysep = lambda u: math.sqrt((f(u) - FC) / (2 * pi ** 3))
rhs = lambda l, s: [4 * pi ** 3 * s[1] ** 2, (2 - pi / s[0]) * s[1]]
rhs_rev = lambda t, s: [-4 * pi ** 3 * s[1] ** 2, -(2 - pi / s[0]) * s[1]]
res = dict(module=str(Path(rusty_sundials.__file__).resolve()), cases=[])
for lab, u0, frac in (("trapped", 0.9, 0.5), ("below separatrix", 0.9, 1.5)):
    y0 = frac * ysep(u0); H0 = f(u0) - 2 * pi ** 3 * y0 ** 2
    lm = -quad(lambda u: 1.0 / (2.0 * (f(u) - H0)), 0.0, u0, epsabs=1e-13, epsrel=1e-13, limit=400)[0]
    _, s = CvodeSolver("adams", 1e-11, 1e-14, 5_000_000).solve(rhs_rev, 0.0, [u0, y0], -lm - 0.02)
    res["cases"].append(dict(label=lab, u0=u0, y0=y0, H0=H0, H0_minus_fc=H0 - FC, l_minus_quadrature=lm, cvode_at_lm_plus_002=dict(l=lm + 0.02, u=s[0], y=s[1])))
    print(res["cases"][-1])
_, s = CvodeSolver("adams", 1e-11, 1e-14, 5_000_000).solve(rhs_rev, 0.0, [1.8, 0.004], 50.0)
res["disordered_side_backward_to_-50"] = dict(u0=1.8, y0=0.004, u_end=s[0], y_end=s[1])
print(res["disordered_side_backward_to_-50"])
json.dump(res, open(OUT / "ch06_backward.json", "w"), indent=1, default=float)
