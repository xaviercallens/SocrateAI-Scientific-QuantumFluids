"""Chapter 4 -- every solver computation, with rusty-SUNDIALS CVODE (`rusty_sundials.CvodeSolver`, Adams-Moulton).

Run from book/figures with the module built from rusty-SUNDIALS commit 5db8041 (v11.6.0 line), NOT the one in the project's virtual
environment (built 2026-09-26, before the Adams fix of 2026-09-28, in which Method::Adams was implicit Euler):

    PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext  nice ../../.venv/bin/python ch04_cvode_compute.py

The script refuses to run otherwise (check_module).  The CVODE runs take seconds (the 30-digit mpmath and SciPy cross-checks are in ch04_crosschecks.py).  Writes ch04_cvode_raw.json (all numbers, with the module's path, commit and sha256) and ch04_cvode_results.npz.

(A) Bose integrals as initial-value problems.  y_m' = x^m / (m! (e^x - 1)), y_m(0) = 0, m in {3,5,6,7,8,9}; y_m(X) -> zeta(m+1),
    i.e. F_m = m! y_m -> the closed forms of Lean `PhononSpecificHeat.bose_integral_values`.
(B) The specific heat of the *model* dispersion eps = hbar c k (1 + a2 k^2 + a3 k^3 + a4 k^4) computed WITHOUT any series:
    C_V(T)/(A T^3) = 1 + y_T(KMAX),  y_T' = V k_B/(2 pi^2) k^2 [f(x_poly) - f(x_Debye)]/(A T^3),   f(x) = x^2 e^x/(e^x-1)^2,
    one ODE component per temperature.  The Debye part is removed analytically (Lean `debye_specific_heat`: its integral is
    exactly A T^3), so the solver only has to resolve the small difference.
(C) The specific heat from the measured dispersion table (cubic spline), total and phonon part (k < k_M), for the
    temperatures 0.05 ... 1.30 K, compared with the paper's table (Cv-and-Entropy.txt).
"""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import hashlib, json, math, sys, time
from pathlib import Path
import numpy as np
import mpmath as mp
import scipy
from scipy.integrate import quad
from scipy.interpolate import CubicSpline
import rusty_sundials as rs
import ch04_common as cc

OUT = Path(__file__).resolve().parent
QUICK = os.environ.get("CH04_QUICK") == "1"      # smoke-test mode: coarse grids, nothing is saved
mp.mp.dps = 30
CAP = 400_000            # hard cap on right-hand-side calls per solve (the Python binding keeps every call's arguments until `solve` returns)
METHOD = "adams"
GOOD_BUILD = Path("/mnt/data/xdev-cache/rs_py_5db8041")


class Cap(RuntimeError):
    pass


def check_module():
    """Refuse to run with a rusty_sundials whose Adams method is the pre-fix implicit Euler (the module in the project's venv, built
    2026-09-26).  Probe: Adams on y' = -y over [0, 10] at rtol 1e-8 needs a few hundred right-hand-side calls when fixed, ~2e5 when not."""
    f = Path(rs.__file__).resolve()
    n = [0]
    def rhs(t, y):
        n[0] += 1
        return [-y[0]]
    _, y = rs.CvodeSolver("adams", 1e-8, 1e-14, 5_000_000).solve(rhs, 0.0, [1.0], 10.0)
    if n[0] >= 5000:
        raise SystemExit(f"rusty_sundials at {f} has the pre-fix Adams method (probe used {n[0]} right-hand-side calls); "
                         f"put {GOOD_BUILD} first on PYTHONPATH")
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    exp = None
    if (GOOD_BUILD/"sha256.txt").exists():
        exp = (GOOD_BUILD/"sha256.txt").read_text().split()[0]
    if f.parent == GOOD_BUILD and exp is not None and sha != exp:
        raise SystemExit(f"sha256 of {f} is {sha}, expected {exp}")
    commit = (GOOD_BUILD/"commit.txt").read_text().strip() if (GOOD_BUILD/"commit.txt").exists() and f.parent == GOOD_BUILD else None
    return dict(module_file=str(f), sha256=sha, sha256_expected=exp, commit=commit, adams_probe_rhs_calls=n[0],
                adams_probe_relerr=abs(y[0] - math.exp(-10.0))/math.exp(-10.0), method=METHOD,
                python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__, mpmath=mp.__version__)


MODULE = check_module()
print("module:", MODULE["module_file"], "commit", MODULE["commit"], "probe calls", MODULE["adams_probe_rhs_calls"], flush=True)


def solve_ode(rhs, y0, breaks, rtol, atol, label=""):
    """Integrate y' = rhs(x, y) through the consecutive breakpoints; return the final y and counters."""
    n = [0]
    def f(x, y):
        n[0] += 1
        if n[0] > CAP:
            raise Cap(label)
        return rhs(x, y)
    load0 = os.getloadavg()[0]
    t0 = time.perf_counter()
    y = list(y0)
    for a, b in zip(breaks[:-1], breaks[1:]):
        solver = rs.CvodeSolver(METHOD, rtol, atol, 200_000)
        _, y = solver.solve(f, a, y, b)
    return np.array(y), dict(rhs_calls=n[0], seconds=time.perf_counter() - t0, load_avg_start=load0, load_avg_end=os.getloadavg()[0])


# ============================================================================================ (A) Bose integrals
ms = [3, 5, 6, 7, 8, 9]
fact = {m: int(mp.factorial(m)) for m in ms}
lean_closed = {                      # the six values of Lean PhononSpecificHeat.bose_integral_values (as mpmath numbers)
    3: mp.pi**4/15, 5: 8*mp.pi**6/63, 6: 720*mp.zeta(7), 7: 8*mp.pi**8/15, 8: 40320*mp.zeta(9), 9: 128*mp.pi**10/33}
check_closed = {m: float(abs(lean_closed[m]/(mp.factorial(m)*mp.zeta(m+1)) - 1)) for m in ms}     # closed form vs m! zeta(m+1): ~1e-30
XEND = 80.0

def rhs_bose(x, y):
    if x <= 0.0:
        return [0.0]*len(ms)
    e = np.expm1(x)
    return [x**m/(fact[m]*e) for m in ms]

resA = []
for rtol in [1e-4, 1e-6, 1e-8, 1e-10, 1e-12]:
    y, info = solve_ode(rhs_bose, [0.0]*len(ms), [0.0, XEND], rtol, 1e-2*rtol, "bose")
    rel = {str(m): float(abs(mp.mpf(float(y[i]))*fact[m]/lean_closed[m] - 1)) for i, m in enumerate(ms)}
    resA.append(dict(rtol=rtol, rel_err_vs_lean_closed_form=rel, **info))
    print("A rtol", rtol, {m: f"{rel[str(m)]:.1e}" for m in ms}, info["rhs_calls"], f"{info['seconds']:.2f}s", flush=True)
quad_err = {}
for m in ms:
    v, e = quad(lambda x: x**m/np.expm1(x) if x > 0 else 0.0, 0, XEND, epsabs=0, epsrel=1e-13, limit=500)
    quad_err[str(m)] = float(abs(mp.mpf(v)/lean_closed[m] - 1))
print("A scipy.quad", {m: f"{quad_err[str(m)]:.1e}" for m in ms}, flush=True)
# cumulative curves F_m(x)/(m! zeta(m+1)) for the figure: one solve from 0 to each x
xs = np.linspace(0, 40, 161 if not QUICK else 9)
curves = np.zeros((len(xs), len(ms)))
for j in range(1, len(xs)):
    y, _ = solve_ode(rhs_bose, [0.0]*len(ms), [0.0, float(xs[j])], 1e-10, 1e-12, "bose-curve")
    curves[j] = y
print("A curves done", flush=True)

# ============================================================================================ (B) model dispersion
co = cc.coeffs_SI(); Aco = co["A"]
T_log = np.unique(np.concatenate([np.geomspace(0.005, 1.0, 41 if not QUICK else 7), [0.02]]))      # 41 geometric points + 0.02 K (a reference temperature)
T_lin = np.round(np.arange(1, 27)*0.05, 6)            # 0.05 ... 1.30 K, the grid used against the measured table
if QUICK: T_lin = T_lin[[1, 5, 9, 15, 25]]
T_all = np.concatenate([T_log, T_lin])
fT = lambda T: T**3*Aco

def rhs_model(k, y):
    if k <= 0.0:
        return [0.0]*len(T_all)
    xp = cc.THETA*cc.u_poly(k)/T_all
    xd = cc.THETA*k/T_all
    return (cc.PREF*k*k*(cc.bose_weight(xp) - cc.bose_weight(xd))/fT(T_all)).tolist()

resB = []
for rtol in [1e-8, 1e-10, 1e-12]:
    y, info = solve_ode(rhs_model, [0.0]*len(T_all), [0.0, cc.KMAX_MODEL], rtol, 1e-14, "model")
    resB.append(dict(rtol=rtol, y=y.tolist(), **info))
    print("B rtol", rtol, info["rhs_calls"], f"{info['seconds']:.2f}s", flush=True)
# un-subtracted version at the tightest tolerance (to show what the analytic Debye subtraction buys)
def rhs_model_raw(k, y):
    if k <= 0.0:
        return [0.0]*len(T_all)
    xp = cc.THETA*cc.u_poly(k)/T_all
    return (cc.PREF*k*k*cc.bose_weight(xp)/fT(T_all)).tolist()
y_raw, info_raw = solve_ode(rhs_model_raw, [0.0]*len(T_all), [0.0, cc.KMAX_MODEL], 1e-12, 1e-14, "model-raw")
print("B raw (no subtraction) rtol 1e-12", info_raw["rhs_calls"], f"{info_raw['seconds']:.2f}s", flush=True)
y_raw8, info_raw8 = solve_ode(rhs_model_raw, [0.0]*len(T_all), [0.0, cc.KMAX_MODEL], 1e-8, 1e-14, "model-raw8")
print("B raw (no subtraction) rtol 1e-8", info_raw8["rhs_calls"], f"{info_raw8['seconds']:.2f}s", flush=True)

# ============================================================================================ (C) measured dispersion
kd, ed = cc.load_dispersion()
spl = CubicSpline(kd, ed*cc.MEV_K)                 # eps in kelvin
kM = float(kd[(kd > 0.5) & (kd < 1.6)][np.argmax(ed[(kd > 0.5) & (kd < 1.6)])])
KEND = float(kd[-1])
Tc = T_lin
def rhs_data(k, y):
    if k <= 0.0:
        return [0.0]*len(Tc)
    x = float(spl(k))/Tc
    return (cc.PREF*k*k*cc.bose_weight(x)/fT(Tc)).tolist()
resC = {}
for rtol in [1e-6, 1e-8]:
    y_ph, i1 = solve_ode(rhs_data, [0.0]*len(Tc), [0.0, kM], rtol, 1e-11, "data-ph")
    y_tot, i2 = solve_ode(rhs_data, [0.0]*len(Tc), [0.0, KEND], rtol, 1e-11, "data-tot")
    resC[str(rtol)] = dict(ph=(y_ph*fT(Tc)).tolist(), tot=(y_tot*fT(Tc)).tolist(), info_ph=i1, info_tot=i2)
    print("C rtol", rtol, i1["rhs_calls"] + i2["rhs_calls"], f"{i1['seconds'] + i2['seconds']:.2f}s", flush=True)
# ============================================================================================ save
if QUICK:
    print('quick mode: not saving'); raise SystemExit
np.savez(OUT/"ch04_cvode_results.npz", ms=np.array(ms), xs=xs, curves=curves, T_all=T_all, T_log=T_log, T_lin=T_lin,
         yB=np.array(resB[-1]["y"]), yB_1e8=np.array(resB[0]["y"]), yB_1e10=np.array(resB[1]["y"]), y_raw=y_raw, y_raw_1e8=y_raw8, kM=kM, KEND=KEND,
         C_ph=np.array(resC["1e-08"]["ph"]), C_tot=np.array(resC["1e-08"]["tot"]), C_ph_1e6=np.array(resC["1e-06"]["ph"]),
         C_tot_1e6=np.array(resC["1e-06"]["tot"]))
json.dump(dict(
    method=METHOD, module=MODULE, rusty_sundials=f"rusty-sundials-py, commit {MODULE['commit']}, {MODULE['module_file']}",
    A=dict(ms=ms, closed_form_vs_factorial_zeta=check_closed, XEND=XEND, runs=resA, scipy_quad_rel_err=quad_err),
    B=dict(T_log=T_log.tolist(), T_lin=T_lin.tolist(), KMAX=cc.KMAX_MODEL, runs=[{k: v for k, v in r.items() if k != "y"} for r in resB],
           raw_unsubtracted_1e12=dict(rhs_calls=info_raw["rhs_calls"], seconds=info_raw["seconds"]),
           raw_unsubtracted_1e8=dict(rhs_calls=info_raw8["rhs_calls"], seconds=info_raw8["seconds"])),
    C=dict(kM=kM, KEND=KEND, runs=resC),
), open(OUT/"ch04_cvode_raw.json", "w"), indent=1)
print("saved")
