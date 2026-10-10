"""Helpers shared by the chapter-7 figure scripts: numbers file."""
import json
from pathlib import Path
NUM = Path(__file__).resolve().parent / "ch07_numbers.json"

def addnum(key, d):
    """read-modify-write of ch07_numbers.json under an advisory file lock (several scripts may finish at the same time)"""
    import fcntl
    lock = Path("/mnt/data/xdev-cache/tmp/ch07_numbers.lock")
    with open(lock, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        cur = json.loads(NUM.read_text()) if NUM.exists() else {}
        cur[key] = d
        NUM.write_text(json.dumps(cur, indent=1, default=float))


def logfmt():
    """Tick labels 10^{k} for log axes written as plain mathtext (matplotlib's default uses \\mathdefault, whose minus sign is missing from EB Garamond)."""
    from matplotlib.ticker import FuncFormatter
    import numpy as np
    return FuncFormatter(lambda y, pos: (r"$10^{%d}$" % int(round(np.log10(y)))) if y > 0 else "")


def cvode_env(require_fixed=True):
    """Identify the rusty_sundials module in use and refuse the stale build of the shared .venv (built 2026-09-26, pre-fix Adams method).
    Probe (as in figures/ch02_compute.py): Adams on y' = -y, t in [0, 10], rtol 1e-8, atol 1e-14 must need < 5000 right-hand sides.
    Returns a dict that is stored in ch07_numbers.json['cvode_env']."""
    import hashlib, math, time
    import rusty_sundials
    from rusty_sundials import CvodeSolver
    n = [0]

    def f(t, y):
        n[0] += 1; return [-y[0]]
    s = CvodeSolver("adams", 1e-8, 1e-14, 5_000_000); _, y = s.solve(f, 0.0, [1.0], 10.0)
    err = abs(y[0] - math.exp(-10.0)) / math.exp(-10.0)
    path = Path(rusty_sundials.__file__).resolve()
    if require_fixed and (".venv" in str(path) or n[0] >= 5000):
        raise SystemExit(f"rusty_sundials at {path} is the stale build (Adams probe: {n[0]} right-hand sides); run with "
                         "PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext")
    commit_f = path.parent / "commit.txt"; sha = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return dict(module=str(path), module_sha256=sha, commit=commit_f.read_text().strip() if commit_f.exists() else None,
                adams_probe_rhs_calls=n[0], adams_probe_relerr=err, date=time.strftime("%Y-%m-%d %H:%M"))
