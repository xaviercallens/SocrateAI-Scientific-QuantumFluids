"""Queue for the friction-law base states (energy scan at two cutoffs), 2 workers, OMP 2 threads each.

    .venv/bin/python exploration/pgpe/run_friction_bases.py [--workers 2] [--dry]
N = 128, k_cut = 2pi/3: e in {0.54, 0.56, 0.58, 0.60}, 1500/1000;  N = 256, k_cut = 2pi: e in {0.90, 1.10, 1.30}, 2500/2000.
Targets: T ~ 0.11 and ~ 0.22 (the transport bases' temperatures); the two nearest admitted bases per cutoff are used.
"""
import argparse, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / "data/generated/pgpe/transport/fl"
# calibration (smoke runs of 100 t.u., 2026-10-08 01:50-02:10): k_cut = 2pi/3, e = 0.555 -> T = 0.104 (the projected e = 0.60 state
# has e = 0.545); k_cut = 2pi (N = 256), e = 1.00 -> T = 0.148, n_s/n = 0.924 (1052 s per 100 t.u. on a loaded machine).
# Long N = 256 jobs first; the start is an equilibrated condensate so 1000 t.u. of transient is used at both cutoffs.
JOBS = [(0.5, 256, e, 1500, 1000) for e in (0.80, 0.95, 1.10)] + [(1 / 3, 128, e, 1500, 1000) for e in (0.56, 0.60, 0.62, 0.66)]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=2); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True); todo = []
    for kf, N, e, te, tt in JOBS:
        import math
        kcut = kf * math.pi * N / 64.0; tag = f"base_k{kcut:.3f}_N{N}_e{e:.2f}"
        if (OUT / f"{tag}.json").exists():
            continue
        todo.append((tag, [sys.executable, str(ROOT / "exploration/pgpe/make_friction_bases.py"), "--kcut-frac", str(kf), "--N", str(N), "--e", str(e), "--t-end", str(te), "--t-tr", str(tt)]))
    for tag, cmd in todo: print(tag)
    if a.dry: return
    env = dict(os.environ, OMP_NUM_THREADS="2"); running = []; q = open(OUT / "queue.log", "a")
    while todo or running:
        while todo and len(running) < a.workers:
            tag, cmd = todo.pop(0); log = open(OUT / f"{tag}.log", "w")
            running.append((tag, subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=ROOT), time.time()))
            q.write(f"{time.strftime('%F %T')} start {tag}\n"); q.flush()
        time.sleep(30)
        for r in list(running):
            if r[1].poll() is not None:
                running.remove(r); q.write(f"{time.strftime('%F %T')} end   {r[0]} rc={r[1].returncode} {time.time() - r[2]:.0f}s\n"); q.flush()
    q.write(f"{time.strftime('%F %T')} queue done\n")


if __name__ == "__main__":
    main()
