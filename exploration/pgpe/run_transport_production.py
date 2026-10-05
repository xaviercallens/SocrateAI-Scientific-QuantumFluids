#!/usr/bin/env python3
"""Production queue of the vortex-transport campaign (docs/designs/PGPE_TRANSPORT_GATES.md): 24 antiparallel runs
(4 bases x d0 in {8, 12} x 3 seeds, 2000 time units) and the two single-dipole runs of hypothesis W (W1).
Runs already finished (output file present) are skipped, so the script can be re-launched after an interruption.

    nohup .venv/bin/python exploration/pgpe/run_transport_production.py [workers=5] > .../production_runner.log 2>&1 &
"""
from __future__ import annotations
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]; T = ROOT / "data/generated/pgpe/transport"
BASES = {"e0.60": ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000_final.npy", "e0.70": T / "base_e0.70_final.npy",
         "e0.80": T / "base_e0.80_final.npy", "e0.90s12": ROOT / "data/generated/pgpe/sweep/e0.90_s12_t4000_final.npy"}
RERUN_WARM = True      # amendment A1.2 (2026-10-05): the T >= 0.22 runs are repeated as prodB_* with r_track = 3.0
jobs = []
for sd in (1, 2, 3):
    for d in (8, 12):
        for tag, base in BASES.items():
            jobs.append((f"prod_{tag}_d{d}_s{sd}", [str(base), "--geom", "antiparallel", "--d0", str(d), "--t-max", "2000", "--seed", str(100 * sd + d)]))
for sd in (1, 2):
    jobs.append((f"W1_e0.60_dipole_d12_s{sd}", [str(BASES["e0.60"]), "--geom", "dipole", "--d0", "12", "--t-max", "4000", "--seed", str(900 + sd)]))


def run(job):
    name, args = job; out = T / f"{name}.npz"
    if RERUN_WARM and not name.startswith(("prod_e0.60", "W1_")):
        name = name.replace("prod_", "prodB_"); out = T / f"{name}.npz"       # amendment A1.2: tracking radius 3.0
    if out.exists():
        return f"{name}: already done"
    cmd = [sys.executable, str(ROOT / "exploration/pgpe/vortex_transport.py"), args[0], str(out)] + args[1:] + ["--imprint", "v2"]
    with open(T / f"{name}.log", "w") as log:
        r = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, env={**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"})
    msg = f"{name}: exit {r.returncode}"; print(msg, flush=True); return msg


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    print(f"{len(jobs)} jobs, {workers} workers", flush=True)
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(run, jobs))
    (T / "production_done.flag").write_text("ALL_DONE\n"); print("ALL_DONE", flush=True)
