"""POST-HOC: is the field-on echo time 16.4 (pre-registered prediction 15.0, FAILED) converged in resolution?"""
import numpy as np
from quantumfluids.kinetic import vlasov as V
k0, tau = 0.5, 10.0
for nv, dt in ((512, 0.05), (1024, 0.025)):
    g = V.Grid(L=2*np.pi/k0, nx=64, nv=nv, vmax=6.0)
    f0 = V.pulse(np.tile(V.maxwellian(g.v), (g.nx, 1)), g, 1, 0.01)
    obs = lambda t, f: (t, 2*abs(V.mode_amplitude(V.density(f, g), 2)))
    _, out = V.run(f0, g, dt, 25.0, obs, events=((tau, lambda f: V.pulse(f, g, 3, 0.01)),))
    t, m = map(np.array, zip(*out)); w = (t > 10) & (t < 25)
    print(f"nv={nv} dt={dt}: echo peak t={t[w][np.argmax(m[w])]:.3f} amplitude={m[w].max():.4e}", flush=True)
