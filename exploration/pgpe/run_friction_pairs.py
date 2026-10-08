"""Pair runs of the friction-law campaign (PGPE_FRICTION_LAW_PREREG.md) at one cutoff.

    .venv/bin/python exploration/pgpe/run_friction_pairs.py --cutoff third  [--workers 2] [--dry]
    .venv/bin/python exploration/pgpe/run_friction_pairs.py --cutoff fine   [--workers 2] [--dry]

Per cutoff: the T = 0 control of A1 (uniform condensate, antiparallel d0 = 10, 400 time units) and, for each of the two
admitted bases nearest T = 0.11 and 0.22, antiparallel pairs d0 in {8, 12} x seeds {1, 2, 3}, 2000 time units, imprint v2,
the same geometry and flags as the production runs (run_transport_production.py) plus --kcut-frac / --N.
Outputs data/generated/pgpe/transport/fl/FL_<cutoff>_<base>_antiparallel_d<d0>_s<seed>.npz; skips existing.
"""
import argparse, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]; FL = ROOT / "data/generated/pgpe/transport/fl"
CUT = {"third": dict(kcut_frac="0.3333333333", N=128, bases=["base_k2.094_N128_e0.55", "base_k2.094_N128_e0.60"]),   # T = 0.100, 0.216
       "fine": dict(kcut_frac="0.5", N=256, bases=[])}                                                              # filled when the scan lands


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cutoff", required=True, choices=list(CUT)); ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--bases", default="", help="override: comma-separated base tags"); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
    c = CUT[a.cutoff]; bases = [b for b in a.bases.split(",") if b] or c["bases"]
    if not bases:
        sys.exit("no bases selected for this cutoff")
    common = ["--imprint", "v2", "--L", "64", "--N", str(c["N"]), "--kcut-frac", c["kcut_frac"]]
    jobs = [(f"FL_{a.cutoff}_T0_antiparallel_d10", ["T0", "--geom", "antiparallel", "--d0", "10", "--t-max", "400", "--seed", "0"])]
    for b in bases:
        if not (FL / f"{b}_final.npy").exists():
            sys.exit(f"missing base {b}")
        for d in (8, 12):
            for sd in (1, 2, 3):
                jobs.append((f"FL_{a.cutoff}_{b}_antiparallel_d{d}_s{sd}", [str(FL / f"{b}_final.npy"), "--geom", "antiparallel", "--d0", str(d), "--t-max", "2000", "--seed", str(100 * sd + d)]))
    todo = [(n, [sys.executable, str(ROOT / "exploration/pgpe/vortex_transport.py"), args[0], str(FL / f"{n}.npz")] + args[1:] + common)
            for n, args in jobs if not (FL / f"{n}.npz").exists()]
    for n, _ in todo: print(n)
    if a.dry: return
    env = dict(os.environ, OMP_NUM_THREADS="2"); running = []; q = open(FL / f"pairs_{a.cutoff}_queue.log", "a")
    while todo or running:
        while todo and len(running) < a.workers:
            n, cmd = todo.pop(0); log = open(FL / f"{n}.log", "w")
            running.append((n, subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=ROOT), time.time()))
            q.write(f"{time.strftime('%F %T')} start {n}\n"); q.flush()
        time.sleep(30)
        for r in list(running):
            if r[1].poll() is not None:
                running.remove(r); q.write(f"{time.strftime('%F %T')} end   {r[0]} rc={r[1].returncode} {time.time() - r[2]:.0f}s\n"); q.flush()
    q.write(f"{time.strftime('%F %T')} queue done\n")


if __name__ == "__main__":
    main()
