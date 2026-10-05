#!/usr/bin/env python3
"""Gates and analyses of the vortex-transport campaign (PGPE_FRICTION_PREREG.md amendment A1).

    .venv/bin/python exploration/pgpe/analyze_transport.py G1                 # T = 0 control
    .venv/bin/python exploration/pgpe/analyze_transport.py G2                 # thermal known answer, T = 0.115
    .venv/bin/python exploration/pgpe/analyze_transport.py SET <glob> <out>   # any set of tracks -> estimators
"""
from __future__ import annotations
import glob, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from transport_estimators import analyse_tracks, min_opposite_distance

ROOT = Path(__file__).resolve().parents[2]; TR = ROOT / "data/generated/pgpe/transport"


def load(path):
    z = np.load(path, allow_pickle=True); meta = json.loads(str(z["meta"]))
    return z["t"], z["R"], z["q"], z, meta


def pair_separations(R, q, L):
    """Separation of each consecutive (+, -) pair of the imprint list."""
    out = []
    for i in range(0, len(q), 2):
        d = R[:, i] - R[:, i + 1]; d -= L * np.round(d / L); out.append(np.hypot(d[:, 0], d[:, 1]))
    return np.array(out)


def summarise(files, L=64.0, **kw):
    tracks, info = [], []
    for f in files:
        t, R, q, z, meta = load(f); tracks.append((t, R, q))
        d = pair_separations(R, q, L)
        info.append({"file": Path(f).name, "ended": meta["ended"], "t_end": meta["t_end"], "drift_E": meta["drift_E"], "n_raw_base": meta["n_raw_base"],
                     "n_det_mean": float(z["n_det"].mean()), "d_first": d[:, :20].mean(axis=1).round(3).tolist(), "d_last": d[:, -20:].mean(axis=1).round(3).tolist()})
    return analyse_tracks(tracks, L, **kw), info


def gate_G1():
    r, info = summarise([str(TR / "G1_T0_antiparallel_d10.npz")])
    t, R, q, z, meta = load(TR / "G1_T0_dipole_d10.npz"); d = pair_separations(R, q, 64.0)[0]; P = np.hypot(z["P"][:, 0], z["P"][:, 1])
    ratio = P / (2 * np.pi * d)
    chk = {"i_no_friction_|alpha|<=1e-3": abs(r["alpha_energy"]) <= 1e-3,
           "ii_point_vortex_translation_0.96-1.04": 0.96 <= r["one_minus_alpha_prime"] <= 1.04,
           "iii_no_diffusion_eta<=2e-5": r["eta"] <= 2e-5,
           "iv_momentum_2pi_n_d_within_5pct_and_constant": bool(np.all(np.abs(ratio - 1) <= 0.05) and np.ptp(P) / P.mean() <= 0.01)}
    res = {"estimates": r, "tracks": info, "dipole": {"d_first": float(d[:20].mean()), "d_last": float(d[-20:].mean()), "P_first": float(P[0]), "P_last": float(P[-1]),
           "P_over_2pi_n_d_min_max": [float(ratio.min()), float(ratio.max())], "P_ptp_rel": float(np.ptp(P) / P.mean())}, "checks": chk, "PASS": bool(all(chk.values()))}
    (TR / "G1_result.json").write_text(json.dumps(res, indent=1, default=float))
    print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items() if k != "msd"}); print("msd", [round(x, 5) for x in r["msd"]])
    print(info); print(res["dipole"]); print("checks", chk, "-> G1", "PASS" if res["PASS"] else "FAIL")


def gate_G2():
    files = sorted(glob.glob(str(TR / "G2_e0.60_antiparallel_d10_s*.npz")))
    r, info = summarise(files)
    chk = {"alpha_energy_in_[0.0028,0.0112]": 0.0028 <= r["alpha_energy"] <= 0.0112, "alpha_prime_in_[-0.02,0.06]": -0.02 <= 1 - r["one_minus_alpha_prime"] <= 0.06}
    res = {"estimates": r, "tracks": info, "checks": chk, "PASS": bool(all(chk.values()))}
    (TR / "G2_result.json").write_text(json.dumps(res, indent=1, default=float))
    print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items() if k != "msd"}); print("msd", [round(x, 5) for x in r["msd"]])
    print(info); print("checks", chk, "-> G2", "PASS" if res["PASS"] else "FAIL")


if __name__ == "__main__":
    if sys.argv[1] == "G1":
        gate_G1()
    elif sys.argv[1] == "G2":
        gate_G2()
    else:
        r, info = summarise(sorted(glob.glob(sys.argv[2])))
        Path(sys.argv[3]).write_text(json.dumps({"estimates": r, "tracks": info}, indent=1, default=float))
        print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items() if k != "msd"}); print(info)
