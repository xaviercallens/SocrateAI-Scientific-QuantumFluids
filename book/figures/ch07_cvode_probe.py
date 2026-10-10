"""Chapter 7: record the Adams probe (y' = -y, t in [0, 10], rtol 1e-8, atol 1e-14) for the module of the shared .venv (stale, pre-fix Adams) -- run WITHOUT the
fixed build on PYTHONPATH:   env -u PYTHONPATH .venv/bin/python book/figures/ch07_cvode_probe.py
The fixed build (commit 5db8041, /mnt/data/xdev-cache/rs_py_5db8041) is probed at the start of ch07_dipole.py and ch07_failures.py (key cvode_env)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch07_common import addnum, cvode_env
e = cvode_env(require_fixed=False); print(e); addnum("cvode_stale_probe", e)
