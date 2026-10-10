"""Chapter 4 -- independent cross-checks of the CVODE results (no solver involved): 30-digit mpmath quadrature of the Debye-subtracted
thermal integral of the model dispersion at seven temperatures, and SciPy adaptive quadrature of the thermal integral of the measured
dispersion table (phonon part and total).  Reads ch04_cvode_results.npz (written by ch04_cvode_compute.py), writes ch04_crosschecks.json.
About a minute of single-core CPU:   nice ../../.venv/bin/python ch04_crosschecks.py"""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import json
from pathlib import Path
import numpy as np
import mpmath as mp
from scipy.integrate import quad
from scipy.interpolate import CubicSpline
import ch04_common as cc

OUT = Path(__file__).resolve().parent
mp.mp.dps = 30
R = np.load(OUT/"ch04_cvode_results.npz")
T_all = R["T_all"]; co = cc.coeffs_SI(); Aco = co["A"]

def mp_ref(T):
    T = mp.mpf(T); th = mp.mpf(cc.THETA)
    a2, a3, a4 = [mp.mpf(s) for s in ("1.55", "-4.04", "2.30")]
    def f(x):
        return x*x*mp.e**(-x)/(1 - mp.e**(-x))**2 if x > 0 else mp.mpf(1)
    def g(k):
        up = k*(1 + a2*k**2 + a3*k**3 + a4*k**4)
        return k*k*(f(th*up/T) - f(th*k/T))
    kT = T/th                                                  # thermal wavevector: break points at multiples of it
    pts = [mp.mpf(0)] + [kT*s for s in (0.5, 1, 2, 4, 8, 16, 32, 64) if kT*s < 2.5] + [mp.mpf(cc.KMAX_MODEL)]
    v = mp.quad(g, pts)
    return float(mp.mpf(cc.PREF)*v/(mp.mpf(Aco)*T**3))

ref_T = [0.005, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
ref_val = {}
for T in ref_T:
    ref_val[str(T)] = mp_ref(T)
    print("mp ref T =", T, ref_val[str(T)], flush=True)
iT = {T: int(np.argmin(abs(T_all - T))) for T in ref_T}
assert all(abs(T_all[iT[T]] - T) < 1e-12 for T in ref_T), "reference temperatures must be on the solver grid"
err = {}
for tag, key in (("1e-08", "yB_1e8"), ("1e-10", "yB_1e10"), ("1e-12", "yB")):
    y = R[key]; err[tag] = {str(T): float(abs(y[iT[T]] - ref_val[str(T)])) for T in ref_T}
    print("abs err vs mp, rtol", tag, {k: f"{v:.1e}" for k, v in err[tag].items()}, flush=True)
y_raw = R["y_raw"]
raw_err = {str(T): float(abs((y_raw[iT[T]] - 1.0) - ref_val[str(T)])) for T in ref_T}
print("un-subtracted (rtol 1e-12) abs err vs mp", {k: f"{v:.1e}" for k, v in raw_err.items()}, flush=True)
raw_err8 = {str(T): float(abs((R["y_raw_1e8"][iT[T]] - 1.0) - ref_val[str(T)])) for T in ref_T}
print("un-subtracted (rtol 1e-8) abs err vs mp", {k: f"{v:.1e}" for k, v in raw_err8.items()}, flush=True)

# the measured table: SciPy adaptive quadrature of the same integrand
kd, ed = cc.load_dispersion()
spl = CubicSpline(kd, ed*cc.MEV_K)
kM = float(R["kM"]); KEND = float(R["KEND"]); Tc = R["T_lin"]
def quad_cv(T, k0, k1):
    f = lambda kk: kk*kk*float(cc.bose_weight(float(spl(kk))/T))
    pts = [p for p in (0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0) if k0 < p < k1]
    v, e = quad(f, k0, k1, points=pts, epsabs=0, epsrel=1e-11, limit=4000)
    return cc.PREF*v
quad_ph = [quad_cv(T, 0.0, kM) for T in Tc]; quad_tot = [quad_cv(T, 0.0, KEND) for T in Tc]
print("quad of the measured table done", flush=True)
json.dump(dict(B=dict(ref_T=ref_T, mp_ref=ref_val, abs_err_vs_mp=err, abs_err_unsubtracted_vs_mp=raw_err, abs_err_unsubtracted_1e8_vs_mp=raw_err8),
               C=dict(quad_ph=quad_ph, quad_tot=quad_tot)), open(OUT/"ch04_crosschecks.json", "w"), indent=1)
print("saved")
