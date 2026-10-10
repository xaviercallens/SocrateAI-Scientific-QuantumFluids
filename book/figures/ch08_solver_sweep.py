"""Chapter 8, solver note: the Adams and BDF options of the Rust crate `cvode` (rusty-SUNDIALS commit 5db8041) on the
undamped linear system of the chapter, N = 4 angular nodes, F = 0, uniform initial state, rtol = 1e-8, atol = 1e-10, t = 0..60,
as a function of the spacing at which the solution is requested (each request is one call of `Cvode::solve(tout, Normal)`
on the same integrator).  Exact answer: m(t) = (1/N) sum_j cos(c_j t), c_j = cos((j + 1/2) pi / N).
Runs the driver `ch08_kinetic kin` (analytic Jacobian, and with CH08_NOJAC=1 CVODE's own differencing).
Writes figures/ch08_numbers.json["cvode_output_spacing_sweep"]."""
import sys, json, subprocess, os, re
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
NUMS = HERE / "ch08_numbers.json"
BIN = "/mnt/data/xdev-cache/cargo-target-book8/release/ch08_kinetic"
TMP = Path("/mnt/data/xdev-cache/book_ch08/kinetic/sweep"); TMP.mkdir(parents=True, exist_ok=True)
N = 4
c = np.cos((np.arange(N) + 0.5) * np.pi / N)

res = {}
for jac in ("analytic_jacobian", "differenced_jacobian"):
    for method in ("bdf", "adams"):
        row = {}
        for dt in (0.01, 0.1, 1.0, 5.0, 10.0, 20.0, 60.0):
            out = TMP / f"{jac}_{method}_{dt:g}.csv"
            env = dict(os.environ); env.pop("CH08_NOJAC", None)
            if jac == "differenced_jacobian": env["CH08_NOJAC"] = "1"
            r = subprocess.run(["nice", BIN, "kin", "0", "uniform", str(N), method, "1e-8", "1e-10", "60", str(dt), str(out)], capture_output=True, text=True, env=env)
            d = np.loadtxt(out, delimiter=",", skiprows=1)
            t = d[:, 0]; ex = np.mean(np.cos(np.outer(t, c)), axis=1)
            m = re.search(r"steps=(\d+) rhs_evals=(\d+)", r.stdout)
            row[f"{dt:g}"] = dict(n_outputs=len(t) - 1, max_abs_err=float(np.max(np.abs(d[:, 1] - ex))), steps=int(m.group(1)), rhs_evals=int(m.group(2)))
        res[f"{jac}_{method}"] = row
allnums = json.loads(NUMS.read_text()) if NUMS.exists() else {}
allnums["cvode_output_spacing_sweep"] = dict(
    problem="N=4 nodes, F=0, uniform IC, t in [0,60], rtol=1e-8, atol=1e-10; one Cvode::solve(tout) call per output; exact answer mean(cos(c t))",
    crate="cvode 6.4.0 of rusty-SUNDIALS commit 5db8041fd2e3840defcff2b4a8c26c1cbb2467fd", results=res)
NUMS.write_text(json.dumps(allnums, indent=1))
for k, row in res.items():
    print(k, {dt: f"{v['max_abs_err']:.1e}" for dt, v in row.items()})
