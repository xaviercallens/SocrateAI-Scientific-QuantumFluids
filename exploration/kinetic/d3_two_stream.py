"""D3 of KINETIC_TDA_PREREG.md (with amendment A3): two-stream growth rate against a certified root, and
phase-space hole counting by H0 sublevel persistence.  Saves f snapshots for the record."""
import sys, json
import numpy as np
sys.path.insert(0, "src")
from quantumfluids.kinetic import vlasov as V
from quantumfluids.kinetic.dispersion import landau_root
from quantumfluids.tda.cubical import minima_with_depth

BEAMS = ((0.5, 2.4), (0.5, -2.4)); U = 2.4
root = landau_root(0.2, 0.0 + 0.2j, beams=BEAMS)
print(f"certified two-stream root k=0.2: certified={root.certified} omega_r={root.omega_r:.3e} gamma={root.omega.imag.str(20)}")

def holes(f, g, thresh=0.1):
    b, dep, ij = minima_with_depth(f, periodic=(True, False))
    keep = (np.abs(g.v[ij[:, 1]]) < U) & (dep > thresh * f.max())
    return int(keep.sum()), sorted((dep[keep] / f.max()).round(3).tolist(), reverse=True)

def two_stream(L, mode, label, t_end=80.0, dt=0.1, nv=512):
    g = V.Grid(L=L, nx=128, nv=nv, vmax=8.0)
    f0 = 0.5 * (V.maxwellian(g.v, U) + V.maxwellian(g.v, -U))
    f = V.pulse(np.tile(f0, (g.nx, 1)), g, mode, 1e-3)
    snaps = {}
    def obs(t, f):
        if abs(t - round(t)) < 1e-9 and int(round(t)) % 2 == 0:
            snaps[int(round(t))] = holes(f, g)
        return t, abs(V.mode_amplitude(V.field_from(f, g), mode))
    f, out = V.run(f, g, dt, t_end, obs)
    t, a = map(np.array, zip(*out))
    isat = next(i for i in range(1, len(a) - 1) if a[i] > a[i - 1] and a[i] >= a[i + 1] and a[i] > 50 * a[0])
    w = (a > 0.01 * a[isat]) & (a < 0.10 * a[isat]) & (t < t[isat])
    rate = np.polyfit(t[w], np.log(a[w]), 1)[0]
    err = abs(rate - root.gamma) / root.gamma
    print(f"{label}: saturation at t={t[isat]:.1f}; growth rate={rate:.5f} vs certified {root.gamma:.5f} (err {100*err:.2f}%)  PASS(<=5%): {err <= 0.05}")
    ts = min(snaps, key=lambda s: abs(s - t[isat]))
    print(f"   holes at first saturation peak (t={ts}): {snaps[ts]}   at t=60: {snaps[60]}   at t=80: {snaps[80]}")
    print("   hole count vs t:", {k: v[0] for k, v in snaps.items() if k % 10 == 0})
    np.save(f"data/generated/kinetic_tda/f_{label}_t80.npy", f)
    return snaps, float(t[isat]), float(rate)

s1 = two_stream(2 * np.pi / 0.2, 1, "S1")
print("   PREDICTION S1 exactly 1 hole at t=60:", s1[0][60][0] == 1)
s2 = two_stream(2 * np.pi / 0.1, 2, "S2")
ts = min(s2[0], key=lambda s: abs(s - s2[1]))
print("   PREDICTION S2 exactly 2 holes at first saturation peak:", s2[0][ts][0] == 2)
# negative control: stable Maxwellian, Run A of K2, t = 50
g = V.Grid(L=4 * np.pi, nx=64, nv=256, vmax=6.0)
f = V.pulse(np.tile(V.maxwellian(g.v), (g.nx, 1)), g, 1, 0.01)
f, _ = V.run(f, g, 0.1, 50.0, lambda t, f: 0)
print("negative control (Maxwellian, t=50): holes =", holes(f, g), "  PASS(==0):", holes(f, g)[0] == 0)
json.dump({"S1": {str(k): v for k, v in s1[0].items()}, "S2": {str(k): v for k, v in s2[0].items()}},
          open("exploration/kinetic/results_d3.json", "w"))
