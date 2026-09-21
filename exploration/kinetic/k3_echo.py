"""K3 of the pre-registration: plasma echo.  k0=0.5, modes 1 and 3, echo in mode 2, tau=10 -> t_echo = 15."""
import numpy as np
from quantumfluids.kinetic import vlasov as V
k0, tau, a1, a2 = 0.5, 10.0, 0.01, 0.01
g = V.Grid(L=2*np.pi/k0, nx=64, nv=512, vmax=6.0)
f0 = V.pulse(np.tile(V.maxwellian(g.v), (g.nx, 1)), g, 1, a1)
obs = lambda t, f: (t, 2*V.mode_amplitude(V.density(f, g), 2).real, 2*abs(V.mode_amplitude(V.density(f, g), 2)))
second = ((tau, lambda f: V.pulse(f, g, 3, a2)),)

def go(field_on, events):
    _, out = V.run(f0.copy(), g, 0.05, 25.0, obs, field_on=field_on, events=events)
    return map(np.array, zip(*out))

t, c, m = go(False, second)
s = (3*k0 - k0)*t - 3*k0*tau
formula = np.where(t >= tau, 0.5*a1*a2*np.exp(-0.5*s**2), 0.0)
w = (t >= 10) & (t <= 20); peak = formula.max()
err = np.max(np.abs(c[w] - formula[w])) / peak
print(f"K3a field off: peak formula={peak:.3e} measured={c[w].max():.3e} at t={t[w][np.argmax(c[w])]:.2f};  max|meas-formula|/peak={err:.2e}   PASS(<=1e-3): {err <= 1e-3}")
t, c, m = go(True, second)
w = (t > 10) & (t < 25); tp = t[w][np.argmax(m[w])]
print(f"K3b field on : max |rho_2| at t={tp:.2f} (predicted 15.00, err {100*abs(tp-15)/15:.1f}%)  amplitude={m[w].max():.3e} (= {m[w].max()/peak:.2f} x ballistic)   PASS(<=5%): {abs(tp-15)/15 <= 0.05}")
for on in (False, True):
    t, c, m = go(on, ())
    w = (t >= 12) & (t <= 18)
    print(f"negative control (no second pulse), field_on={on}: max|rho_2| in [12,18] = {m[w].max():.2e} = {m[w].max()/peak:.1e} x peak   PASS(<1%): {m[w].max()/peak < 0.01}")
