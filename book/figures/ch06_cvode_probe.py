"""Chapter 6 -- how many right-hand-side evaluations does CVODE (Python module `rusty_sundials`) need?  Run with either module:

    .venv/bin/python figures/ch06_cvode_probe.py venv                                                               # the module in the project's virtual environment
    PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext .venv/bin/python figures/ch06_cvode_probe.py 5db8041

and writes figures/ch06_cvode_probe_<tag>.json.  Probes (Adams unless stated; counts of calls of the Python right-hand side are machine independent):
  P1  y' = -y on [0, 10], rtol 1e-8, atol 1e-14        (the probe of figures/ch02_compute.py: fixed module < 5000 calls, pre-fix about 2e5)
  P2  y' = -y on [0, 1],  rtol 1e-9, atol 1e-13, and the relative error
  P3  the Kosterlitz flow (u, y)' = (4 pi^3 y^2, (2 - pi/u) y), trapped start (u0, y0) = (1.2, 0.9 y_sep(1.2)), ONE solve from l = 0 to 0.25, rtol 1e-9, atol 1e-13
  P4  the same flow from l = 0 to 20 in one solve
  P5  P1 with BDF at rtol 1e-4 (the editor's check of the older BDF), y' = -y on [0, 10]"""
import json, math, sys, time, hashlib
from pathlib import Path
import rusty_sundials
from rusty_sundials import CvodeSolver

tag = sys.argv[1]
pi = math.pi
f = lambda u: 2 * u - pi * math.log(u)
FC = f(pi / 2)
ysep = lambda u: math.sqrt((f(u) - FC) / (2 * pi ** 3))


def run(label, method, rtol, atol, rhs, y0, t1, exact=None):
    n = {"c": 0}
    def wrapped(t, y):
        n["c"] += 1
        return rhs(t, y)
    t0 = time.process_time()
    try:
        _, y = CvodeSolver(method, rtol, atol, 5_000_000).solve(wrapped, 0.0, list(y0), t1); status = "ok"
    except RuntimeError as e:
        y, status = None, "RuntimeError: " + str(e)[:90]
    out = dict(label=label, method=method, rtol=rtol, atol=atol, t_end=t1, rhs_calls=n["c"], cpu_s=round(time.process_time() - t0, 3), status=status)
    if y is not None and exact is not None:
        out["relerr"] = abs(y[0] - exact) / abs(exact)
    if y is not None:
        out["y_end"] = y
    print(out, flush=True)
    return out


decay = lambda t, y: [-y[0]]
flow = lambda l, s: [4 * pi ** 3 * s[1] ** 2, (2 - pi / s[0]) * s[1]]
u0 = 1.2; y0 = 0.9 * ysep(u0)
mod = Path(rusty_sundials.__file__).resolve()
so = mod if mod.suffix == ".so" else next(mod.parent.glob("*.so"))      # the project's venv has a package directory around the extension module
res = dict(tag=tag, module=str(mod), extension_module=str(so), sha256=hashlib.sha256(so.read_bytes()).hexdigest(), probes=[])
res["probes"].append(run("P1 y'=-y [0,10] adams 1e-8", "adams", 1e-8, 1e-14, decay, [1.0], 10.0, math.exp(-10.0)))
res["probes"].append(run("P2 y'=-y [0,1] adams 1e-9", "adams", 1e-9, 1e-13, decay, [1.0], 1.0, math.exp(-1.0)))
res["probes"].append(run("P3 flow 0->0.25 adams 1e-9", "adams", 1e-9, 1e-13, flow, [u0, y0], 0.25))
res["probes"].append(run("P4 flow 0->20 adams 1e-9", "adams", 1e-9, 1e-13, flow, [u0, y0], 20.0))
res["probes"].append(run("P5 y'=-y [0,10] bdf 1e-4", "bdf", 1e-4, 1e-8, decay, [1.0], 10.0, math.exp(-10.0)))
json.dump(res, open(Path(__file__).resolve().parent / f"ch06_cvode_probe_{tag}.json", "w"), indent=1, default=float)
