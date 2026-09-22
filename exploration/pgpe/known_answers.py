#!/usr/bin/env python3
"""K1-K7 of docs/designs/PGPE_BKT_PREREG.md. Run: .venv/bin/python exploration/pgpe/known_answers.py"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE

OUT = Path(__file__).resolve().parents[2] / "data" / "generated" / "pgpe"
OUT.mkdir(parents=True, exist_ok=True)
res = {}


def drift_run(dt, N=64, L=32.0, t_end=20.0, seed=1):
    s = PGPE(N=N, L=L, g=1.0, dt=dt)
    c0 = s.random_state(1.0, 3.0, np.random.default_rng(seed))
    n0, e0, p0 = s.norm(c0), s.energy(c0), s.momentum(c0)
    c = s.run(c0, t_end)
    return abs(s.norm(c) - n0) / n0, abs(s.energy(c) - e0) / abs(e0), float(np.max(np.abs(s.momentum(c) - p0)))


# K1-K3 at dt = 0.005 and dt = 0.01 (scaling)
t0 = time.time()
dn1, de1, dp1 = drift_run(0.005)
dn2, de2, dp2 = drift_run(0.01)
_, de3, _ = drift_run(0.02); _, de4, _ = drift_run(0.04)      # A1: scaling measured where drift >> roundoff
res["K1_norm"] = {"drift_dt0.005": dn1, "drift_dt0.01": dn2, "PASS": dn1 <= 1e-8}
res["K2_energy"] = {"drift_dt0.005": de1, "drift_dt0.01": de2, "drift_dt0.02": de3, "drift_dt0.04": de4,
                    "ratio_dt0.01_over_dt0.005": de2 / de1 if de1 > 0 else None,
                    "ratio_dt0.04_over_dt0.02": de4 / de3 if de3 > 0 else None,
                    "PASS": de1 <= 1e-6 and (de3 > 0 and 13 <= de4 / de3 <= 19)}
res["K3_momentum"] = {"drift_dt0.005": dp1, "drift_dt0.01": dp2, "PASS": dp1 <= 1e-10}
print("K1-K3", {k: res[k]["PASS"] for k in ("K1_norm", "K2_energy", "K3_momentum")},
      f"dN={dn1:.2e} dE={de1:.2e} ratio(0.01/0.005)={de2/de1:.1f} ratio(0.04/0.02)={de4/de3:.1f} dP={dp1:.2e}  ({time.time()-t0:.0f}s)")

# K4: plane wave psi = sqrt(n0) e^{i(k.x - w t)}, w = k^2/2 + g n0
s = PGPE(N=64, L=32.0, g=1.0, dt=0.005)
x = np.arange(64) * s.dx
X, Y = np.meshgrid(x, x, indexing="ij")
kx = 2 * np.pi * 3 / s.L
psi0 = np.sqrt(1.0) * np.exp(1j * kx * X)
c = s.run(s.modes(psi0), 10.0)
w = 0.5 * kx ** 2 + 1.0
psi_exact = psi0 * np.exp(-1j * w * 10.0)
err = float(np.max(np.abs(s.psi(c) - psi_exact)))
res["K4_plane_wave"] = {"max_abs_error": err, "PASS": err <= 1e-9}
print("K4", res["K4_plane_wave"])

# K5: Bogoliubov dispersion, three k values, amplitude 1e-3
k5 = {}
s = PGPE(N=64, L=32.0, g=1.0, dt=0.005)
for m in (1, 2, 4):
    kk = 2 * np.pi * m / s.L
    psi0 = 1.0 + 1e-3 * np.cos(kk * X)
    c = s.modes(psi0.astype(complex))
    T_end, every = 60.0, 4
    amps, ts = [], []

    def cb(t, cc, m=m):
        # A1: measure in the condensate frame (divide out the global phase e^{-i mu t} of c_0)
        ts.append(t); amps.append(cc[m, 0] * np.conj(cc[0, 0]) / abs(cc[0, 0]))
    s.run(c, T_end, callback=cb, every=every)
    a = np.array(amps); a = a - a.mean()
    # density perturbation ~ Re part oscillates at the Bogoliubov frequency; use |FFT| peak with parabolic refinement
    dtc = every * s.dt
    sp = np.abs(np.fft.rfft(a.real * np.hanning(len(a))))
    f = np.fft.rfftfreq(len(a), d=dtc)
    i = int(np.argmax(sp[1:])) + 1
    # parabolic interpolation of the peak
    y0, y1, y2 = np.log(sp[i - 1]), np.log(sp[i]), np.log(sp[i + 1])
    delta = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    w_meas = 2 * np.pi * (f[i] + delta * (f[1] - f[0]))
    w_bog = np.sqrt(0.5 * kk ** 2 * (0.5 * kk ** 2 + 2.0))
    k5[f"k={kk:.4f}"] = {"w_bogoliubov": w_bog, "w_measured": w_meas, "rel_err": abs(w_meas - w_bog) / w_bog}
res["K5_bogoliubov"] = {"modes": k5, "PASS": all(v["rel_err"] <= 5e-3 for v in k5.values())}
print("K5", {k: round(v["rel_err"], 5) for k, v in k5.items()}, res["K5_bogoliubov"]["PASS"])

# K6: cross-check against rusty-SUNDIALS (Adams) on a 16x16 grid to t = 5; fallback DOP853 as pre-registered
s = PGPE(N=16, L=8.0, g=1.0, dt=0.002)
c0 = s.random_state(1.0, 2.0, np.random.default_rng(7))
c_rk4 = s.run(c0, 5.0)
y0 = s.pack(c0)
scale = float(np.linalg.norm(y0))
k6 = {"n_unknowns": int(2 * s.n_modes)}
try:
    import rusty_sundials
    def rhs_list(t, y):
        return s.rhs_real(t, y).tolist()
    t1 = time.time()
    _, y_a = rusty_sundials.CvodeSolver("adams", 1e-8, 1e-10, 2_000_000).solve(rhs_list, 0.0, y0.tolist(), 5.0)
    k6["integrator"] = "rusty-SUNDIALS CVODE Adams (rtol 1e-8, atol 1e-10)"; k6["seconds"] = round(time.time() - t1, 1)
    _, y_bad = rusty_sundials.CvodeSolver("adams", 1e-3, 1e-5, 2_000_000).solve(rhs_list, 0.0, y0.tolist(), 5.0)
    y_a, y_bad = np.array(y_a), np.array(y_bad)
except Exception as e:  # pre-registered fallback
    from scipy.integrate import solve_ivp
    k6["integrator"] = f"scipy DOP853 fallback (rusty_sundials unavailable: {type(e).__name__}: {str(e)[:80]})"
    y_a = solve_ivp(s.rhs_real, (0, 5.0), y0, method="DOP853", rtol=1e-8, atol=1e-10).y[:, -1]
    y_bad = solve_ivp(s.rhs_real, (0, 5.0), y0, method="DOP853", rtol=1e-3, atol=1e-5).y[:, -1]
diff = float(np.max(np.abs(s.pack(c_rk4) - y_a)))
diff_bad = float(np.max(np.abs(s.pack(c_rk4) - y_bad)))
tol = 10 * 1e-8 * scale
k6.update(max_diff=diff, tolerance=tol, max_diff_loose=diff_bad, PASS=(diff <= tol) and (diff_bad > tol))
res["K6_crosscheck"] = k6
print("K6", k6)

# K7: thermometer on two k-windows after thermalisation (small box so it is fast here; the sweep uses 128^2)
s = PGPE(N=64, L=32.0, g=1.0, dt=0.01)
c = s.random_state(1.0, 2.5, np.random.default_rng(3))
c = s.run(c, 400.0)                      # transient
acc = np.zeros_like(s.k2); nsmp = 0

def cb(t, cc):
    global acc, nsmp
    acc += np.abs(cc) ** 2; nsmp += 1
s.run(c, 400.0, callback=cb, every=200)
occ = acc / nsmp * s.dx ** 2 / s.N ** 2          # <|c_k|^2> normalised so that sum = N (particles)
eps = 0.5 * s.k2
kk = np.sqrt(s.k2)

def fit_T(lo, hi):
    m = (kk >= lo * s.kcut) & (kk <= hi * s.kcut) & s.P
    x, y = eps[m], 1.0 / occ[m]                  # 1/<n_k> = (eps_k + 2gn - mu)/T  => slope 1/T
    A = np.vstack([x, np.ones_like(x)]).T
    slope, icpt = np.linalg.lstsq(A, y, rcond=None)[0]
    return 1.0 / slope, icpt / slope             # T, (2gn - mu)
T_hi, b_hi = fit_T(0.6, 1.0); T_lo, b_lo = fit_T(0.4, 0.6)
res["K7_thermometer"] = {"T_window_0.6-1.0": T_hi, "T_window_0.4-0.6": T_lo, "rel_diff": abs(T_hi - T_lo) / T_hi,
                         "2gn_minus_mu_hi": b_hi, "2gn_minus_mu_lo": b_lo, "PASS": abs(T_hi - T_lo) / T_hi <= 0.10}
print("K7", res["K7_thermometer"])

res["ALL_PASS"] = all(res[k]["PASS"] for k in res if k != "ALL_PASS")
(OUT / "known_answers.json").write_text(json.dumps(res, indent=1, default=float))
print("ALL_PASS:", res["ALL_PASS"], "->", OUT / "known_answers.json")
