"""Chapter 4: a probe of the rusty_sundials module that is on the path -- run once with each of the two builds that matter:

  (1) the module in the project's virtual environment (built 2026-09-26, before the Adams fix of 2026-09-28):
        flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice ../../.venv/bin/python ch04_solver_probe.py
  (2) the build of rusty-SUNDIALS commit 5db8041 used for every number of the chapter:
        PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext nice ../../.venv/bin/python ch04_solver_probe.py

Both Adams and BDF are tried on three pure problems with known answers
   y' = -y on [0, 10]                              (exp(-10))
   y' = cos(t) on [0, 70]                          (no dependence on y)
   y' = x^3/(e^x - 1) on [0, 70], y(0) = 0         (the Debye integral, exact value pi^4/15)
with a hard cap on right-hand-side calls (the Python binding keeps every call's arguments alive until `solve` returns), and then
the six Bose integrals of the chapter are integrated from 0 to each of 160 end points to count the solves that give up.
Writes ch04_solver_probe_venv.json or ch04_solver_probe_fixed.json according to the module found."""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import hashlib, json, math, time
from pathlib import Path
import numpy as np
import rusty_sundials as rs

HERE = Path(__file__).resolve().parent
MODFILE = Path(rs.__file__).resolve()
_ext = getattr(getattr(rs, "rusty_sundials", None), "__file__", None)          # the venv module is a package around the extension; the fixed build is the extension itself
EXTFILE = Path(_ext).resolve() if _ext else MODFILE
TAG = "fixed" if "rs_py_5db8041" in str(MODFILE) else "venv"
CAP = 60_000

class Cap(Exception): pass

def run(rhs, y0, t1, rtol, atol, method, ref=None):
    n = [0]; last_t = [0.0]
    def f(t, y):
        n[0] += 1; last_t[0] = t
        if n[0] > CAP: raise Cap()
        return rhs(t, y)
    s = rs.CvodeSolver(method, rtol, atol, 100_000)
    t0 = time.perf_counter()
    try:
        _, y = s.solve(f, 0.0, y0, t1)
        err = abs(y[0] - ref)/abs(ref) if ref else None
        return dict(method=method, rtol=rtol, atol=atol, status="ok", rhs_calls=n[0], rel_err=err, seconds=time.perf_counter() - t0)
    except Exception as ex:
        return dict(method=method, rtol=rtol, atol=atol, status="stopped at the cap of %d calls" % CAP if n[0] > CAP else "error: " + str(ex)[:60],
                    rhs_calls=n[0], last_t=last_t[0], rel_err=None, seconds=time.perf_counter() - t0)

out = dict(tag=TAG, module_file=str(MODFILE), extension_file=str(EXTFILE), sha256=hashlib.sha256(EXTFILE.read_bytes()).hexdigest(), cap_calls=CAP, loadavg_start=os.getloadavg()[0], runs=[])
for method in ("adams", "bdf"):
    out["runs"].append(dict(problem="decay", **run(lambda t, y: [-y[0]], [1.0], 10.0, 1e-8, 1e-14, method, math.exp(-10.0))))
    out["runs"].append(dict(problem="cos", **run(lambda t, y: [math.cos(t)], [0.0], 70.0, 1e-6, 1e-9, method)))
    out["runs"].append(dict(problem="bose3", **run(lambda x, y: [x**3/math.expm1(x) if x > 0 else 0.0], [0.0], 70.0, 1e-6, 1e-8, method, math.pi**4/15)))
    out["runs"].append(dict(problem="bose3", **run(lambda x, y: [x**3/math.expm1(x) if x > 0 else 0.0], [0.0], 70.0, 1e-9, 1e-11, method, math.pi**4/15)))
    print(method, "probes done", flush=True)

# solves that give up when asked to land on an end point (a solver error), and solves that need more than LCAP calls
ms = [3, 5, 6, 7, 8, 9]
fact = {m: math.factorial(m) for m in ms}
LCAP = 5_000
def bose_rhs(x, y):
    if x <= 0.0: return [0.0]*len(ms)
    e = math.expm1(x)
    return [x**m/(fact[m]*e) for m in ms]
xs = np.linspace(0, 40, 161)[1:]
out["landing"] = {}
for method in ("adams", "bdf"):
    errors = 0; capped = 0; calls = 0
    for x in xs:
        n = [0]
        def f(t, y):
            n[0] += 1
            if n[0] > LCAP: raise Cap()
            return bose_rhs(t, y)
        try:
            rs.CvodeSolver(method, 1e-9, 1e-11, 100_000).solve(f, 0.0, [0.0]*len(ms), float(x))
        except Cap:
            capped += 1
        except Exception:
            errors += 1
        calls += n[0]
    out["landing"][method] = dict(problem="y_m' = x^m/(m!(e^x-1)), m = 3,5,6,7,8,9, y(0) = 0, integrated from 0 to each end point", rtol=1e-9, atol=1e-11,
                                  call_cap=LCAP, n_endpoints=len(xs), n_solver_errors=errors, n_over_cap=capped, total_rhs_calls=calls)
    print(method, "landing: solver errors", errors, "over the cap", capped, "of", len(xs), flush=True)
out["loadavg_end"] = os.getloadavg()[0]
(HERE/f"ch04_solver_probe_{TAG}.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))
