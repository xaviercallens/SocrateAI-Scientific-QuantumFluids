"""Chapter 10, cross-implementation check: the SAME synthetic tracks of the registered gate G0 (8 antiparallel dipole pairs, 2000 time
units, known alpha = 0.02, alpha' = 0.10, eta = 2e-3, detection noise 0.2, numpy seed 20261005 as in
exploration/pgpe/transport_estimators.py) analysed by (i) the numpy estimators and (ii) the Rust estimators of rusty-SUNDIALS
(`qf_pgpe.analyse_tracks`).  Prints and saves the six estimates of each and their relative differences.
Run (heavy: ~2 min CPU, goes through the shared lock):
    PYTHONPATH=/mnt/data/xdev-cache/qf_ext .venv/bin/python book/figures/ch10_cross_impl.py"""
import json, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "exploration/pgpe")); sys.path.insert(0, "/mnt/data/xdev-cache/qf_ext")
import numpy as np
import transport_estimators as te
import qf_pgpe

L, truth = 64.0, dict(alpha=0.02, alphap=0.10, eta=2e-3)
rng = np.random.default_rng(20261005)
tracks = []
t0 = time.time()
for i in range(8):
    pos, q = te.antiparallel(L, 10.0, rng)
    t, R = te.langevin(pos, q, L, truth["alpha"], truth["alphap"], truth["eta"], 2000.0, rng)
    tracks.append((t, R + 0.2 * rng.standard_normal(R.shape), q))
print("tracks generated in %.1f s; lengths (time units):" % (time.time() - t0), [float(t[-1]) for t, _, _ in tracks], flush=True)
t0 = time.time(); py = te.analyse_tracks(tracks, L); t_py = time.time() - t0
t0 = time.time()
rs = qf_pgpe.analyse_tracks([(np.ascontiguousarray(t, dtype=np.float64), np.ascontiguousarray(R, dtype=np.float64), np.asarray(q, dtype=np.int64)) for t, R, q in tracks], L)
t_rs = time.time() - t0
names = ["one_minus_alpha_prime", "alpha_regression", "alpha_energy", "eta", "msd_exponent", "msd_offset"]
rows = []
for n in names + [n + "_se" for n in names]:
    a, b = float(py[n]), float(rs[n])
    rel = abs(a - b) / max(abs(a), 1e-300)
    rows.append(dict(name=n, numpy=a, rust=b, rel_diff=rel))
    print(f"{n:28s} numpy {a:.12g}  rust {b:.12g}  rel.diff {rel:.2e}")
out = dict(truth=truth, seed=20261005, n_tracks=len(tracks), track_lengths=[float(t[-1]) for t, _, _ in tracks], numpy_s=round(t_py, 2), rust_s=round(t_rs, 3),
           max_rel_diff_estimates=max(r["rel_diff"] for r in rows[:6]), max_rel_diff_errors=max(r["rel_diff"] for r in rows[6:]), rows=rows,
           n_blocks=[py["n_blocks"], rs["n_blocks"]])
Path(__file__).with_name("ch10_raw").mkdir(exist_ok=True)
(Path(__file__).with_name("ch10_raw") / "cross_impl.json").write_text(json.dumps(out, indent=1))
print("max relative difference of the six estimates: %.2e ; of the six errors: %.2e ; numpy %.1f s, Rust %.3f s" % (out["max_rel_diff_estimates"], out["max_rel_diff_errors"], t_py, t_rs))
