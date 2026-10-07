"""Queue runner for the counterflow campaign (docs/designs/PGPE_COUNTERFLOW_PREREG.md, cells 1-11, two seeds each).

Runs only if the W2 tie-break supports W (or leaves it graded as the wind equation predicts); do not start before
that verdict is recorded. Usage:
    .venv/bin/python exploration/pgpe/run_counterflow.py [--workers 3] [--only CELL,CELL] [--dry]
Each run: vortex_transport.py <base> <out> --geom dipole --d0 D --t-max 4000 --seed S --imprint v2 --L L --N N --nk-every 100
Skips runs whose .npz exists. Logs to data/generated/pgpe/transport/counterflow/<name>.log; progress in queue.log.
"""
import argparse, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]; TR = ROOT / "data/generated/pgpe/transport"; OUT = TR / "counterflow"
BASES = {(64, 0.60): (ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000_final.npy", 128),   # the W1 / production base
         (96, 0.60): (TR / "base_L96_e0.60_final.npy", 192),
         (128, 0.60): (TR / "base_L128_e0.60_final.npy", 256), (64, 0.70): (TR / "base_e0.70_final.npy", 128)}
# cell -> (L, e, d0)
CELLS = {1: (64, 0.60, 8), 2: (64, 0.60, 10), 3: (64, 0.60, 12), 4: (64, 0.60, 14),
         5: (96, 0.60, 12), 6: (96, 0.60, 14), 7: (96, 0.60, 16),
         8: (128, 0.60, 16), 9: (128, 0.60, 20),
         10: (64, 0.70, 10), 11: (64, 0.70, 14)}


def jobs(only):
    out = []
    for cell, (L, e, d0) in CELLS.items():
        if only and cell not in only:
            continue
        base, N = BASES[(L, e)]
        for seed in (1, 2):
            name = f"CF_c{cell:02d}_L{L}_e{e:.2f}_d{d0}_s{seed}"
            out.append((cell, name, [sys.executable, str(ROOT / "exploration/pgpe/vortex_transport.py"), str(base), str(OUT / f"{name}.npz"),
                                     "--geom", "dipole", "--d0", str(d0), "--t-max", "4000", "--seed", str(1000 * cell + seed),
                                     "--imprint", "v2", "--L", str(L), "--N", str(N), "--nk-every", "100"]))
    # bigger boxes first so the long runs do not end up alone at the tail of the queue
    return sorted(out, key=lambda j: -CELLS[j[0]][0])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--only", default=""); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
    only = {int(x) for x in a.only.split(",") if x}; OUT.mkdir(exist_ok=True)
    todo = [j for j in jobs(only) if not (OUT / f"{j[1]}.npz").exists()]
    missing = {str(BASES[(CELLS[c][0], CELLS[c][1])][0]) for c, _, _ in todo if not BASES[(CELLS[c][0], CELLS[c][1])][0].exists()}
    if a.dry or missing:
        for c, n, cmd in todo: print(c, n)
        if missing: print("MISSING BASES:", *sorted(missing)); sys.exit(1)
        return
    env = dict(os.environ, OMP_NUM_THREADS="2"); running = []; qlog = open(OUT / "queue.log", "a")
    while todo or running:
        while todo and len(running) < a.workers:
            c, n, cmd = todo.pop(0); log = open(OUT / f"{n}.log", "w")
            running.append((n, subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=ROOT), time.time()))
            qlog.write(f"{time.strftime('%F %T')} start {n}\n"); qlog.flush()
        time.sleep(30)
        for r in list(running):
            if r[1].poll() is not None:
                running.remove(r); qlog.write(f"{time.strftime('%F %T')} end   {r[0]} rc={r[1].returncode} {time.time() - r[2]:.0f}s\n"); qlog.flush()
    qlog.write(f"{time.strftime('%F %T')} queue done\n")


if __name__ == "__main__":
    main()
