"""POST-HOC (after the pre-registered D3 growth-rate criterion FAILED: measured 0.18656 vs certified 0.22584).
Which number is wrong?  (1) Independent evaluation of D(i gamma) by direct quadrature -- legitimate without
analytic continuation because Im(omega) > 0.  (2) The measured local growth rate as a function of time."""
import numpy as np
from scipy.integrate import quad
from quantumfluids.kinetic import vlasov as V

U, k = 2.4, 0.2
f0p = lambda v: 0.5 * (-(v - U) * V.maxwellian(v, U) - (v + U) * V.maxwellian(v, -U))
def D(gamma):
    w = 1j * gamma / k
    re = quad(lambda v: (f0p(v) / (v - w)).real, -12, 12, limit=400)[0]
    im = quad(lambda v: (f0p(v) / (v - w)).imag, -12, 12, limit=400)[0]
    return 1 - (re + 1j * im) / k ** 2
for g_ in (0.18656, 0.22584425503471):
    print(f"quadrature D(i*{g_}) = {D(g_):.3e}")

g = V.Grid(L=2 * np.pi / k, nx=128, nv=512, vmax=8.0)
f = V.pulse(np.tile(0.5 * (V.maxwellian(g.v, U) + V.maxwellian(g.v, -U)), (g.nx, 1)), g, 1, 1e-3)
_, out = V.run(f, g, 0.1, 40.0, lambda t, f: (t, abs(V.mode_amplitude(V.field_from(f, g), 1))))
t, a = map(np.array, zip(*out))
print("local growth rate d ln|E1|/dt, 5-unit windows:")
for t0 in range(0, 40, 5):
    w = (t >= t0) & (t < t0 + 5)
    print(f"   t in [{t0:>2},{t0+5:>2}): {np.polyfit(t[w], np.log(a[w]), 1)[0]:+.4f}    |E1| = {a[w][0]:.2e} .. {a[w][-1]:.2e}")
isat = np.argmax(a); print(f"saturation |E1|={a[isat]:.3e} at t={t[isat]:.1f};  1%..10% window = [{t[np.argmax(a>0.01*a[isat])]:.1f}, {t[np.argmax(a>0.10*a[isat])]:.1f}]")

print("\nPOST-HOC rerun with seed 1e-8 (six more decades of linear growth):")
f = V.pulse(np.tile(0.5 * (V.maxwellian(g.v, U) + V.maxwellian(g.v, -U)), (g.nx, 1)), g, 1, 1e-8)
_, out = V.run(f, g, 0.1, 90.0, lambda t, f: (t, abs(V.mode_amplitude(V.field_from(f, g), 1))))
t, a = map(np.array, zip(*out))
for t0 in range(10, 90, 10):
    w = (t >= t0) & (t < t0 + 10)
    print(f"   t in [{t0:>2},{t0+10:>2}): {np.polyfit(t[w], np.log(a[w]), 1)[0]:+.5f}   |E1| up to {a[w][-1]:.2e}")
w = (t >= 30) & (t <= 60); r = np.polyfit(t[w], np.log(a[w]), 1)[0]
print(f"   fit over [30,60]: {r:.5f} vs certified 0.22584  (err {100*abs(r-0.22584425)/0.22584425:.2f}%)")
