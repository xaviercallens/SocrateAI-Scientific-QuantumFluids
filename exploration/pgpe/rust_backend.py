"""Run the PGPE vortex-transport instrument on the pure-Rust engine (rusty-SUNDIALS `qf-pgpe`) and read the result back in the
layout of the Python instrument (npz with t, R, q, n_det, P, P_hi, meta), so that `analyze_transport.summarise`,
`transport_estimators.analyse_tracks` and every other analysis script run unchanged on Rust output.

    from rust_backend import run_vortex_transport, to_raw
    to_raw("base.npy", "base.raw")                                     # numpy complex128 modes -> raw little-endian
    run_vortex_transport("T0", "out.npz", geom="dipole", d0=10, t_max=100, n=128, l=64, seed=1)

The Rust binaries are built from the `rusty-SUNDIALS` workspace (`cargo build --release -p qf-pgpe --examples`); the location is taken from
$RUSTY_SUNDIALS (default ~/xdev/rusty-SUNDIALS-c3, a worktree of rusty-SUNDIALS; the crate is on main since PR #69, commit 72cad84) and its `target/release/examples`.
Rust placements use a small LCG, not numpy's generator: single trajectories differ from the Python ones for the same seed; the
campaign's claims are ensemble statements. Measurements on a GIVEN field are identical (see crates/qf-pgpe/*CROSSCHECK.md).
"""
from __future__ import annotations
import json, os, subprocess
from pathlib import Path
import numpy as np

ROOT = Path(os.environ.get("RUSTY_SUNDIALS", Path.home() / "xdev/rusty-SUNDIALS-c3"))


def example(name: str) -> Path:
    for tgt in (os.environ.get("CARGO_TARGET_DIR"), str(ROOT / "target")):
        if tgt and (Path(tgt) / "release/examples" / name).exists():
            return Path(tgt) / "release/examples" / name
    raise FileNotFoundError(f"build it: cd {ROOT} && cargo build --release -p qf-pgpe --examples ({name})")


def to_raw(npy: str | Path, raw: str | Path) -> None:
    np.load(npy).astype("<c16").tofile(raw)


def read_csv_track(csv: str | Path, n_v: int):
    d = np.loadtxt(csv, delimiter=",", skiprows=1, ndmin=2)
    t = d[:, 0]; R = d[:, 1:1 + 2 * n_v].reshape(len(t), n_v, 2)
    n_det, P, P_hi = d[:, 1 + 2 * n_v], d[:, 2 + 2 * n_v:4 + 2 * n_v], d[:, 4 + 2 * n_v:6 + 2 * n_v]
    return t, R, n_det, P, P_hi


def run_vortex_transport(base: str, out_npz: str | Path, geom: str = "antiparallel", d0: float = 10.0, t_max: float = 400.0, n: int = 128, l: float = 64.0,
                         seed: int = 1, r_track: float = 3.0, d_stop: float = 1.5) -> dict:
    """base = 'T0' or a raw complex128 field. Returns the metadata dict; writes `out_npz`."""
    out_npz = Path(out_npz); csv = out_npz.with_suffix(".csv")
    cmd = [str(example("vortex_transport")), base, str(csv), "--geom", geom, "--d0", str(d0), "--t-max", str(t_max), "--n", str(n), "--l", str(l),
           "--seed", str(seed), "--r-track", str(r_track), "--d-stop", str(d_stop)]
    msg = subprocess.run(cmd, check=True, capture_output=True, text=True, env=dict(os.environ, RAYON_NUM_THREADS="1")).stdout.strip()
    q = np.array([1, -1, 1, -1] if geom == "antiparallel" else [1, -1])
    t, R, n_det, P, P_hi = read_csv_track(csv, len(q))
    ended = msg.split(":")[-1].split()[0]
    meta = dict(base=base, geom=geom, d0=d0, seed=seed, L=l, N=n, ended=ended, t_end=float(t[-1]), imprint="v2", r_track=r_track, backend="rusty-sundials qf-pgpe")
    np.savez(out_npz, t=t, R=R, q=q, n_det=n_det, P=P, P_hi=P_hi, meta=json.dumps(meta))
    return meta
