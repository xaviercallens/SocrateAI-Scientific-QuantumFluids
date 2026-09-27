"""K2 of the pre-registration: Runs A, B, C.  Parameters are those written in the pre-registration."""
import numpy as np
from quantumfluids.kinetic import vlasov as V
from quantumfluids.kinetic.dispersion import landau_root

ROOT = {0.5: landau_root(0.5, 1.4156 - 0.1533j), 0.4: landau_root(0.4, 1.285 - 0.066j)}

def landau_run(k, nv, t_end=50.0, dt=0.1):
    g = V.Grid(L=2 * np.pi / k, nx=64, nv=nv, vmax=6.0)
    f = V.pulse(np.tile(V.maxwellian(g.v), (g.nx, 1)), g, 1, 0.01)
    m0, e0 = V.mass(f, g), V.energy(f, g)
    obs = lambda t, f: (t, abs(V.mode_amplitude(V.field_from(f, g), 1)))
    f, out = V.run(f, g, dt, t_end, obs)
    t, a = map(np.array, zip(*out))
    return g, t, a, abs(V.mass(f, g) / m0 - 1), abs(V.energy(f, g) / e0 - 1)

for name, k in (("A", 0.5), ("B", 0.4)):
    g, t, a, dm, de = landau_run(k, 256)
    rate, om, tp = V.peak_fit(t, a, 5, 25)
    r = ROOT[k]
    eg, eo = abs(rate - r.gamma) / abs(r.gamma), abs(om - r.omega_r) / r.omega_r
    print(f"Run {name} k={k}: gamma={rate:.5f} (K1 {r.gamma:.5f}, err {100*eg:.2f}%)  omega={om:.5f} (K1 {r.omega_r:.5f}, err {100*eo:.2f}%)"
          f"  peaks={len(tp)}  mass drift={dm:.1e}  energy drift={de:.1e}")
    print(f"      PASS gamma<=2%: {eg <= 0.02}   PASS omega<=1%: {eo <= 0.01}")
    if name == "B":
        o = ROOT[0.5]
        miss = abs(rate - o.gamma) / abs(o.gamma)
        print(f"      discrimination: misses the k=0.5 root by {100*miss:.0f}%  PASS(>20%): {miss > 0.20}")

g, t, a, dm, de = landau_run(0.5, 32)
TR = g.recurrence_time(1)
w = (t > 25) & (t < 45)
i = np.argmax(a[w]); tpk, apk = t[w][i], a[w][i]
print(f"Run C nv=32: T_R predicted={TR:.2f}  largest |E1| in (25,45) at t={tpk:.2f} (err {100*abs(tpk-TR)/TR:.1f}%), "
      f"height={apk/a[0]:.2f} x |E1(0)|   PASS: {abs(tpk-TR)/TR <= 0.05 and apk/a[0] > 0.10}")
