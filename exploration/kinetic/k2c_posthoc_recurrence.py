"""POST-HOC diagnostic for the FAILED pre-registered Run C (written after seeing the failure; it does not
convert the failure into a pass).  Question: is T_R = 2 pi/(k dv) the recurrence time of the free-streaming
density, with the field's largest maximum merely lagging it?"""
import numpy as np
from quantumfluids.kinetic import vlasov as V
k = 0.5
g = V.Grid(L=2*np.pi/k, nx=64, nv=32, vmax=6.0)
f0 = V.pulse(np.tile(V.maxwellian(g.v), (g.nx, 1)), g, 1, 0.01)
for on in (False, True):
    obs = lambda t, f: (t, abs(V.mode_amplitude(V.density(f, g), 1)), abs(V.mode_amplitude(V.field_from(f, g), 1)))
    _, out = V.run(f0.copy(), g, 0.1, 50.0, obs, field_on=on)
    t, r, e = map(np.array, zip(*out)); w = (t > 25) & (t < 45)
    print(f"field_on={on}:  argmax |rho_1| in (25,45) = {t[w][np.argmax(r[w])]:.2f}   argmax |E_1| = {t[w][np.argmax(e[w])]:.2f}   (T_R = {g.recurrence_time():.2f})   rho_1(T_R)/rho_1(0) = {r[np.argmin(abs(t-g.recurrence_time()))]/r[0]:.3f}")
