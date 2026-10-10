"""Chapter 10 / appendix B: which rusty_sundials build is on the path?  The probe is y' = -y on [0, 10], atol 1e-14, relative error of y(10), counted right-hand-side
calls; the Adams method of the build before the fix of 2026-09-28 is implicit Euler (docs/CVODE_ADAMS_FIX.md of rusty-SUNDIALS), the fixed one needs a few hundred.
Run twice and compare:
    .venv/bin/python book/figures/ch10_cvode_probe.py stale                       # the module installed in the project's virtual environment
    PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext .venv/bin/python book/figures/ch10_cvode_probe.py fixed
Writes figures/ch10_raw/cvode_probe_<tag>.json."""
import hashlib, json, math, os, sys, time
from pathlib import Path
import rusty_sundials
from rusty_sundials import CvodeSolver
tag = sys.argv[1] if len(sys.argv) > 1 else "run"
so = Path(rusty_sundials.__file__)
sofile = so if so.suffix == ".so" else next(so.parent.glob("*.so"))
rows = []
for method in ("adams", "bdf"):
    for rtol in (1e-4, 1e-6, 1e-8, 1e-10):
        n = [0]
        def f(t, y, n=n): n[0] += 1; return [-y[0]]
        t0 = time.perf_counter()
        try:
            _, y = CvodeSolver(method, rtol, 1e-14, 5_000_000).solve(f, 0.0, [1.0], 10.0); err = abs(y[0] - math.exp(-10.0)) / math.exp(-10.0); status = "ok"
        except Exception as e:                                           # a step limit counts as a result
            err, status = None, str(e)[:60]
        rows.append(dict(method=method, rtol=rtol, nfe=n[0], relerr=err, status=status, wall_s=round(time.perf_counter() - t0, 2)))
        print(f"{tag:6s} {method:5s} rtol {rtol:.0e}  rhs calls {n[0]:>9d}  rel. error {err if err is None else format(err, '.2e')}  ({status})", flush=True)
out = dict(tag=tag, module=str(so), shared_object=str(sofile), sha256=hashlib.sha256(sofile.read_bytes()).hexdigest(),
           built=time.strftime("%Y-%m-%d %H:%M", time.localtime(sofile.stat().st_mtime)), rows=rows)
(Path(__file__).with_name("ch10_raw") / f"cvode_probe_{tag}.json").write_text(json.dumps(out, indent=1))
print(out["module"], out["sha256"][:16], out["built"])
