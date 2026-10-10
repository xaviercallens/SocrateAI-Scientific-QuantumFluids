# Study-only: is the exciton-exciton direct kernel of a DUAL-GATED bilayer completely monotone in t = r^2?
# Geometry (nm): interlayer distance d, gates at +-h from the bilayer mid-plane (grounded planes, same dielectric).
# Units: q^2/(4 pi eps0 eps) = 1.  V_xx = G_ee + G_hh - 2 G_eh with the grounded-plane Green function.
import mpmath as mp
mp.mp.dps = 40
def make(h, d, nmax=400):
    L = 2*h; ze = h - d/2; zh = h + d/2
    def G(t, z, zp):
        s = mp.mpf(0)
        for n in range(-nmax, nmax+1):
            s += 1/mp.sqrt(t + (z - zp + 2*n*L)**2) - 1/mp.sqrt(t + (z + zp + 2*n*L)**2)
        return s
    def Vxx(t):
        return G(t, ze, ze) + G(t, zh, zh) - 2*G(t, ze, zh)
    def Gee(t):
        return G(t, ze, ze)
    return Vxx, Gee
def ungated(d):
    return lambda t: 2/mp.sqrt(t) - 2/mp.sqrt(t + d*d)
def test(f, name, ts, kmax=6):
    bad = []
    for t0 in ts:
        for k in range(0, kmax+1):
            val = (-1)**k * mp.diff(f, t0, k)
            if val < 0: bad.append((float(t0), k, float(val)))
    print(f"{name}: {'CM at all tested (t,k)' if not bad else 'VIOLATIONS: ' + str(bad[:6])}")
ts = [mp.mpf(x) for x in (0.5, 2, 8, 30, 100, 400, 1500)]
d = 2.0
test(ungated(d), "ungated bilayer dipole kernel (control)", ts)
for h in (5.0, 7.5, 10.0):
    Vxx, Gee = make(h, d, nmax=150)
    test(Gee, f"gated single-layer Coulomb G_ee, h={h} nm", ts, kmax=5)
    test(Vxx, f"gated exciton-exciton kernel V_xx, h={h} nm, d={d} nm", ts, kmax=5)
