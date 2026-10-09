"""Follow-up scan WS-A1 (PGPE_VORTEX_SCATTERING_PREREG.md): d0 in {20, 24, 28} x m in {4, 8, 10, 12, 14, 16, 20} x 2 directions + a control per d0.
    .venv/bin/python exploration/pgpe/run_wave_scan_d0.py [--workers 4] [--dry]   -> data/generated/pgpe/wave_scattering/scan_d0/"""
import argparse, os, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / "data/generated/pgpe/wave_scattering/scan_d0"; MS = [4, 8, 10, 12, 14, 16, 20]; D0S = [20, 24, 28]
def jobs():
    j = []
    for d0 in D0S:
        j.append((f"WS_d{d0}_control", ["--m", "4", "--eps", "0.0", "--dir", "1", "--d0", str(d0)]))
        for m in MS:
            for d, tag in ((1, "p"), (-1, "m")):
                j.append((f"WS_d{d0}_m{m:02d}_{tag}_av0.04", ["--m", str(m), "--av", "0.04", "--dir", str(d), "--d0", str(d0)]))
    return j
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=4); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True); todo = [(n, args) for n, args in jobs() if not (OUT / f"{n}.npz").exists()]
    for n, _ in todo: print(n)
    if a.dry: return
    env = dict(os.environ, OMP_NUM_THREADS="2"); running = []; q = open(OUT / "queue.log", "a")
    while todo or running:
        while todo and len(running) < a.workers:
            n, args = todo.pop(0); log = open(OUT / f"{n}.log", "w")
            cmd = [sys.executable, str(ROOT / "exploration/pgpe/vortex_wave_scattering.py"), str(OUT / f"{n}.npz"), "--t-max", "400"] + args
            running.append((n, subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=ROOT), time.time())); q.write(f"{time.strftime('%F %T')} start {n}\n"); q.flush()
        time.sleep(20)
        for r in list(running):
            if r[1].poll() is not None:
                running.remove(r); q.write(f"{time.strftime('%F %T')} end   {r[0]} rc={r[1].returncode} {time.time() - r[2]:.0f}s\n"); q.flush()
    q.write(f"{time.strftime('%F %T')} queue done\n")
if __name__ == "__main__":
    main()
