"""Engine benchmark of the projected-GPE IF-RK4 step: the Rust engine (rusty-SUNDIALS `qf-pgpe`) against the Python engines on the SAME problem.

    .venv/bin/python exploration/pgpe/bench_engines.py single  --ns 64,128,256,512 --steps 100 --reps 3   -> bench/engines.json
    .venv/bin/python exploration/pgpe/bench_engines.py scaling --n 128 --steps 100 --procs 1,2,4,8          -> bench/scaling.json

Problem (identical in `crates/qf-pgpe/examples/bench_step.rs`): N x N grid, L = N/2 (dx = 0.5), g = 1, dt = 0.01, cutoff k_max/2, initial state c[0,0] = N^2,
c[0,1] = (0.3, 0.1) N, c[1,0] = (-0.2, 0.2) N projected by modes(psi(.)). Engines: numpy (pgpe.PGPE, pocketfft), scipy.fft (workers = 1, T), torch CPU (1, T threads)
and the Rust engine (single thread; `--rust-parallel` build with the rayon feature). The statistic is the best of `reps` repetitions (time per step); all engines'
final states are compared with the Rust checksum sum|Re c| + |Im c|. Run on a quiet machine (the scans of the programme were SIGSTOPped during the measurement).
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / "data/generated/pgpe/bench"; OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "exploration/pgpe"))
RUST = Path(os.environ.get("RUSTY_SUNDIALS", Path.home() / "xdev/rusty-SUNDIALS-c3"))
RUST_BIN = Path(os.environ.get("CARGO_TARGET_DIR", RUST / "target")) / "release/examples/bench_step"
RUST_PAR = Path("/mnt/data/xdev-cache/cargo-target-par/release/examples/bench_step")


def initial(N):
    c = np.zeros((N, N), complex); c[0, 0] = N * N; c[0, 1] = 0.3 * N + 0.1j * N; c[1, 0] = -0.2 * N + 0.2j * N
    return c


def checksum(c): return float(np.abs(c.real).sum() + np.abs(c.imag).sum())


class Eng:
    """IF-RK4 step with a pluggable FFT pair (f2, i2) on numpy arrays."""
    def __init__(self, N, f2, i2):
        from pgpe import PGPE
        s = PGPE(N=N, L=N / 2.0); self.s, self.f2, self.i2 = s, f2, i2; self.P = s.P; self.E1, self.E2 = s.E1, s.E2; self.dt = s.dt

    def nonlin(self, c):
        psi = self.i2(c); return -1j * self.s.g * self.P * self.f2(np.abs(psi) ** 2 * psi)

    def step(self, c):
        dt, E1, E2 = self.dt, self.E1, self.E2; a = self.nonlin(c); b = self.nonlin(E1 * (c + 0.5 * dt * a)); cc = self.nonlin(E1 * c + 0.5 * dt * b)
        d = self.nonlin(E2 * c + dt * E1 * cc); return E2 * c + (dt / 6.0) * (E2 * a + 2.0 * E1 * (b + cc) + d)

    def project(self, c): return self.f2(self.i2(c)) * self.P

    def run(self, c, n):
        for _ in range(n): c = self.step(c)
        return c


def make(engine, N):
    import scipy.fft as sf
    if engine == "numpy": return Eng(N, np.fft.fft2, np.fft.ifft2)
    if engine.startswith("scipy"):
        w = int(engine.split("-")[1]); return Eng(N, lambda x: sf.fft2(x, workers=w), lambda x: sf.ifft2(x, workers=w))
    if engine.startswith("torch"):
        import torch; th = int(engine.split("-")[1]); torch.set_num_threads(th)
        return Eng(N, lambda x: torch.fft.fft2(torch.from_numpy(x)).numpy(), lambda x: torch.fft.ifft2(torch.from_numpy(x)).numpy())
    raise ValueError(engine)


def time_python(engine, N, steps, reps):
    e = make(engine, N); c0 = e.project(initial(N)); e.run(c0, 2)
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter(); c = e.run(c0, steps); ts.append((time.perf_counter() - t0) / steps)
    ts.sort(); return dict(engine=engine, n=N, us_per_step_best=1e6 * ts[0], us_per_step_median=1e6 * ts[len(ts) // 2], checksum=checksum(c))


def time_rust(binpath, N, steps, reps, threads=1):
    env = dict(os.environ, RAYON_NUM_THREADS=str(threads), OMP_NUM_THREADS="1")
    out = subprocess.run([str(binpath), str(N), str(steps), str(reps)], capture_output=True, text=True, env=env, check=True).stdout.strip().splitlines()[-1]
    r = json.loads(out); r["engine"] = "rust" if binpath == RUST_BIN else f"rust-parallel-{threads}"; return r


def single(a):
    res = []
    for N in [int(x) for x in a.ns.split(",")]:
        steps = max(10, int(a.steps * (128 / N) ** 2)) if a.scale_steps else a.steps
        row = [time_rust(RUST_BIN, N, steps, a.reps)]
        for eng in a.engines.split(","): row.append(time_python(eng, N, steps, a.reps))
        if RUST_PAR.exists() and N >= 256:
            for th in (2, 4, 8): row.append(time_rust(RUST_PAR, N, steps, a.reps, th))
        ref = row[0]["checksum"]
        for r in row: r["checksum_rel_diff_vs_rust"] = abs(r["checksum"] - ref) / ref
        res += row
        print(f"N = {N} ({steps} steps):", {r["engine"]: round(r["us_per_step_best"]) for r in row}, "max checksum rel diff", f"{max(r['checksum_rel_diff_vs_rust'] for r in row):.1e}", flush=True)
    meta = dict(cpu=subprocess.run("lscpu | grep 'Model name'", shell=True, capture_output=True, text=True).stdout.strip(), steps=a.steps, reps=a.reps, date=time.strftime("%F %T"))
    (OUT / "engines.json").write_text(json.dumps(dict(meta=meta, results=res), indent=1))


def scaling(a):
    res = []
    for P in [int(x) for x in a.procs.split(",")]:
        for name, cmd in (("rust", [str(RUST_BIN), str(a.n), str(a.steps), "1"]),
                          ("numpy", [sys.executable, str(ROOT / "exploration/pgpe/bench_engines.py"), "one", "--n", str(a.n), "--steps", str(a.steps), "--engine", "numpy"])):
            env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", RAYON_NUM_THREADS="1")
            t0 = time.perf_counter(); ps = [subprocess.Popen(cmd, stdout=subprocess.DEVNULL, env=env) for _ in range(P)]
            [p.wait() for p in ps]; wall = time.perf_counter() - t0
            res.append(dict(engine=name, procs=P, n=a.n, steps=a.steps, wall_s=wall, steps_per_s=P * a.steps / wall))
            print(f"{name:6s} P = {P}: {P * a.steps / wall:8.1f} steps/s total ({wall:.1f} s)", flush=True)
    (OUT / "scaling.json").write_text(json.dumps(dict(date=time.strftime("%F %T"), results=res), indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["single", "scaling", "one"]); ap.add_argument("--ns", default="64,128,256,512"); ap.add_argument("--steps", type=int, default=100)
    ap.add_argument("--reps", type=int, default=3); ap.add_argument("--engines", default="numpy,scipy-1,scipy-4,torch-1,torch-4"); ap.add_argument("--scale-steps", action="store_true")
    ap.add_argument("--n", type=int, default=128); ap.add_argument("--procs", default="1,2,4,8"); ap.add_argument("--engine", default="numpy"); a = ap.parse_args()
    {"single": single, "scaling": scaling}.get(a.mode, lambda a: time_python(a.engine, a.n, a.steps, 1))(a)
