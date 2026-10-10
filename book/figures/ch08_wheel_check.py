"""Chapter 8, solver note: what the Python module `rusty_sundials` does on the chapter's own problem.
Two modules are compared (run this script twice):
   (1)  the module installed in the shared virtual environment .venv (file date 2026-09-26, "stale": before the repository's
        CVODE tight-tolerance fix, merge #60 of 2026-09-27)
            .venv/bin/python figures/ch08_wheel_check.py
   (2)  the build of rusty-SUNDIALS commit 5db8041 made by the editor
            PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext .venv/bin/python figures/ch08_wheel_check.py
The chapter's own computations do NOT use either of them: they use the Rust crate `cvode` of the same commit 5db8041
directly (book/rust/ch08_kinetic).  This script exists so that the statements about the Python module are measurements.
Problem:  d nu_j/dt = -i c_j (nu_j + F <nu>),  c_j = cos((j + 1/2) pi / N),  uniform initial state, F = 0, finite-difference
Jacobian (the Python binding has no Jacobian argument);  exact answer  m(t) = <exp(-i c t)> = (1/N) sum_j cos(c_j t).
  test A:  N = 32, t_end = 0.5;      test B:  N = 4, t_end = 60 (one call), rtol = 1e-8, atol = 1e-10.
Writes figures/ch08_numbers.json["python_module_stale_venv"] or ["python_module_5db8041"], with rusty_sundials.__file__."""
import sys, json, os, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import rusty_sundials
from rusty_sundials import CvodeSolver

NUMS = Path(__file__).resolve().parent / "ch08_numbers.json"
modfile = rusty_sundials.__file__
sofile = next(Path(modfile).parent.glob("*.so")) if Path(modfile).name == "__init__.py" else Path(modfile)
key = "python_module_5db8041" if "rs_py_5db8041" in str(sofile) else "python_module_stale_venv"


def make_rhs(N, F):
    c = np.cos((np.arange(N) + 0.5) * np.pi / N)
    def rhs(t, y):
        y = np.asarray(y); nr, ni = y[:N], y[N:]
        mr, mi = nr.mean(), ni.mean()
        return np.concatenate([c * (ni + F * mi), -c * (nr + F * mr)]).tolist()
    return rhs, c


def attempt(N, F, tend, method, rtol, atol):
    rhs, c = make_rhs(N, F)
    y0 = np.concatenate([np.ones(N), np.zeros(N)]).tolist()
    sol = CvodeSolver(method=method, rtol=rtol, atol=atol, max_steps=500000)
    t0 = time.time()
    try:
        t, y = sol.solve(rhs, 0.0, y0, tend)
        exact = float(np.mean(np.cos(tend * c)))
        return dict(status="ok", abs_err_m=float(abs(np.mean(y[:N]) - exact)), wall_s=round(time.time() - t0, 3))
    except Exception as e:
        return dict(status="FAILED", message=str(e)[:160], wall_s=round(time.time() - t0, 3))


out = dict(rusty_sundials_file=str(sofile), module_file_date=time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(sofile))),
           test_A="N=32, F=0, t_end=0.5, finite-difference Jacobian", test_B="N=4, F=0, t_end=60, one call, rtol=1e-8, atol=1e-10", A={}, B={})
if (sofile.parent / "commit.txt").exists(): out["commit"] = (sofile.parent / "commit.txt").read_text().strip()
for method in ("bdf", "adams"):
    for rtol, atol in ((1e-6, 1e-8), (1e-8, 1e-10), (1e-10, 1e-12)):
        out["A"][f"{method}_rtol{rtol:g}"] = attempt(32, 0.0, 0.5, method, rtol, atol)
    out["B"][f"{method}_rtol1e-08"] = attempt(4, 0.0, 60.0, method, 1e-8, 1e-10)
allnums = json.loads(NUMS.read_text()) if NUMS.exists() else {}
allnums.pop("python_wheel", None)
allnums[key] = out
NUMS.write_text(json.dumps(allnums, indent=1))
print(key); print(json.dumps(out, indent=1))
