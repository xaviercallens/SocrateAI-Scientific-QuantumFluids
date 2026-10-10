"""Chapter 7: the registered estimators of the campaign, Python (exploration/pgpe/transport_estimators.py) against the Rust port
(qf_pgpe.analyse_tracks, crate qf-pgpe::transport), on the eight archived tracks of the T = 0.115 arm (prod_e0.60_d{8,12}_s{1,2,3} and the two
G2 runs, 2000 time units each).  Writes the relative differences of the six estimates and the two wall-clock times to ch07_numbers.json['estimator_crosscheck'].
The Python estimators take minutes (jackknife over 16 blocks), hence the run under the shared-machine lock.
    flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice env PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch07_xcheck.py"""
import sys, time, glob, os
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "exploration/pgpe"))
import qf_pgpe
from transport_estimators import analyse_tracks as py_an
from ch07_common import addnum
TR = ROOT / "data/generated/pgpe/transport"
fs = sorted(glob.glob(str(TR / "prod_e0.60_d*_s*.npz"))) + sorted(glob.glob(str(TR / "G2_e0.60_antiparallel_d10_s*.npz")))
tracks = []
for f in fs:
    z = np.load(f, allow_pickle=True); tracks.append((z["t"].astype(float), z["R"].astype(float), z["q"].astype(int)))
load0 = os.getloadavg()[0]
t0 = time.time(); r_py = py_an(tracks, 64.0); t1 = time.time()
r_rs = qf_pgpe.analyse_tracks([(t, R, q.astype(np.int64)) for t, R, q in tracks], 64.0); t2 = time.time()
keys = ("alpha_energy", "alpha_regression", "one_minus_alpha_prime", "eta", "msd_exponent", "msd_offset")
rel = {k: float(abs(r_py[k] - r_rs[k]) / abs(r_py[k])) for k in keys}
rel_se = {k + "_se": float(abs(r_py[k + "_se"] - r_rs[k + "_se"]) / abs(r_py[k + "_se"])) for k in keys}
addnum("estimator_crosscheck", dict(files=[Path(f).name for f in fs], python=dict(seconds=round(t1 - t0, 1), **{k: r_py[k] for k in keys}, **{k + "_se": r_py[k + "_se"] for k in keys}),
        rust=dict(seconds=round(t2 - t1, 2), **{k: r_rs[k] for k in keys}), rel_diff=rel, rel_diff_se=rel_se, max_rel_diff=float(max(list(rel.values()) + list(rel_se.values()))),
        load_average_start=round(load0, 1), n_tracks=len(tracks)))
print("python", round(t1 - t0, 1), "s; rust", round(t2 - t1, 2), "s; max rel diff", max(list(rel.values()) + list(rel_se.values())))
