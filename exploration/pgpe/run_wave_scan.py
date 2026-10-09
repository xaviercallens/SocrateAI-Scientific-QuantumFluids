"""Scan of PGPE_VORTEX_SCATTERING_PREREG.md: control + 13 wavenumbers x 2 directions (A_v = 0.04) + KA3 repeats (A_v = 0.08 at m = 8, 16).
    .venv/bin/python exploration/pgpe/run_wave_scan.py [--workers 4] [--dry]
Outputs data/generated/pgpe/wave_scattering/scan/WS_m{m:02d}_{p|m}_av{av}.npz (+ .log), control WS_control.npz; skips existing."""
import argparse, os, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / "data/generated/pgpe/wave_scattering/scan"
MS = [1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28]
def jobs():
    j = [("WS_control", ["--m", "4", "--eps", "0.0", "--dir", "1"])]
    for m in MS:
        for d, tag in ((1, "p"), (-1, "m")):
            j.append((f"WS_m{m:02d}_{tag}_av0.04", ["--m", str(m), "--av", "0.04", "--dir", str(d)]))
    for m in (8, 16):
        for d, tag in ((1, "p"), (-1, "m")):
            j.append((f"WS_m{m:02d}_{tag}_av0.08", ["--m", str(m), "--av", "0.08", "--dir", str(d)]))
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
