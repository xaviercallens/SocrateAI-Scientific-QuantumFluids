#!/usr/bin/env python3
"""The thermal sweep of docs/designs/PGPE_BKT_PREREG.md §2: 12 energies x 3 seeds, 128^2, L = 64, k_cut = k_max/2,
t in [0, 1500] at dt = 0.01, samples every 10 after t = 500. One JSON per trajectory in data/generated/pgpe/sweep/.

Run: .venv/bin/python exploration/pgpe/sweep.py [--procs 8] [--quick]   (--quick: 64^2, L=32, t=600, for a dry run)
"""
from __future__ import annotations
import argparse, json, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from observables import thermometer, condensate_fraction, g1_radial, fit_g1, vortices, pairing, current_correlators, dipole_matching

OUT = Path(__file__).resolve().parents[2] / "data" / "generated" / "pgpe" / "sweep"
ENERGIES = [0.6, 0.9, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.2]
SEEDS = [11, 12, 13]
RPAIR = 3.0          # pre-set: 3 xi_T with xi_T = 1/sqrt(g n) = 1


def trajectory(args):
    e, seed, quick, t_end_arg = args
    N, L, t_end, t_tr = (64, 32.0, 600.0, 200.0) if quick else (128, 64.0, 1500.0, 500.0)
    if t_end_arg:                      # amendment A3: extension runs, same seed, transient = t_end - 1000
        t_end, t_tr = t_end_arg, t_end_arg - 1000.0
    s = PGPE(N=N, L=L, g=1.0, dt=0.01)
    c = s.random_state(1.0, e, np.random.default_rng(seed))
    E0, N0 = s.energy(c), s.norm(c)
    t0 = time.time()
    c = s.run(c, t_tr)
    occ = np.zeros_like(s.k2); occ_h = [np.zeros_like(s.k2), np.zeros_like(s.k2)]; nh = [0, 0]
    smp = {"cond": [], "eta": [], "ell": [], "res_alg": [], "res_exp": [], "f_free": [], "n_v": [], "Q": [], "l_d": [], "l_null": [], "JL": {}, "JT": {}}
    g1_acc = None; n_s = 0
    mrng = np.random.default_rng(1000 + seed)
    every = int(round(10.0 / s.dt)); n_samples = int(round((t_end - t_tr) / 10.0))

    def cb(t, cc):
        nonlocal g1_acc, n_s
        w = np.abs(cc) ** 2 * s.dx ** 2 / s.N ** 2
        occ[...] += w
        half = 0 if t <= 0.5 * (t_end - t_tr) else 1      # t counts from the end of the transient (s.run restarts at 0)
        occ_h[half] += w; nh[half] += 1
        smp["cond"].append(condensate_fraction(s, cc))
        r, g = g1_radial(s, cc)
        g1_acc = g if g1_acc is None else g1_acc + g
        pos, q = vortices(s, cc)
        ff, nv = pairing(s, pos, q, RPAIR)
        smp["f_free"].append(ff); smp["n_v"].append(nv)
        ld, ln, Q = dipole_matching(s, pos, q, mrng)
        smp["l_d"].append(ld); smp["l_null"].append(ln); smp["Q"].append(Q)
        for sh, (jl, jt) in current_correlators(s, cc).items():
            smp["JL"].setdefault(str(sh), []).append(jl); smp["JT"].setdefault(str(sh), []).append(jt)
        n_s += 1
    c = s.run(c, t_end - t_tr, callback=cb, every=every)
    occ /= n_s
    T_hi, b_hi = thermometer(s, occ, 0.6, 1.0); T_lo, b_lo = thermometer(s, occ, 0.4, 0.6)
    T_h1 = thermometer(s, occ_h[0] / max(nh[0], 1), 0.6, 1.0)[0]; T_h2 = thermometer(s, occ_h[1] / max(nh[1], 1), 0.6, 1.0)[0]
    r, _ = g1_radial(s, c); g1m = g1_acc / n_s
    fit = fit_g1(r, g1m, 2.0, L / 4)
    JL = {k: float(np.mean(v)) for k, v in smp["JL"].items()}; JT = {k: float(np.mean(v)) for k, v in smp["JT"].items()}
    ratio = float(np.mean([JT[k] / JL[k] for k in JL]))
    res = {"e": e, "seed": seed, "N": N, "L": L, "n_modes": s.n_modes, "E_per_particle": E0 / N0,
           "drift_E": abs(s.energy(c) - E0) / abs(E0), "drift_N": abs(s.norm(c) - N0) / N0,
           "T": T_hi, "T_lowwindow": T_lo, "T_half1": T_h1, "T_half2": T_h2, "twogn_minus_mu": b_hi,
           "stationary_5pct": abs(T_h1 - T_h2) / T_hi <= 0.05, "thermometer_10pct": abs(T_hi - T_lo) / T_hi <= 0.10,
           "cond_frac": float(np.mean(smp["cond"])), "g1": {"r": r.tolist(), "g1": g1m.tolist(), **fit},
           "n_v": float(np.mean(smp["n_v"])), "f_free": float(np.nanmean(smp["f_free"])) if np.any(np.isfinite(smp["f_free"])) else float("nan"),
           "Q": float(np.nanmean(smp["Q"])) if np.any(np.isfinite(smp["Q"])) else float("nan"),
           "l_d": float(np.nanmean(smp["l_d"])) if np.any(np.isfinite(smp["l_d"])) else float("nan"),
           "Q_samples": smp["Q"], "nv_samples": smp["n_v"], "JL": JL, "JT": JT, "ns_over_n": 1.0 - ratio, "n_samples": n_s, "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    tag = ('_quick' if quick else '') + (f'_t{int(t_end)}' if t_end_arg else '')
    res["t_end"] = t_end
    np.save(OUT / f"e{e:.2f}_s{seed}{tag}_final.npy", c)
    (OUT / f"e{e:.2f}_s{seed}{tag}.json").write_text(json.dumps(res, indent=1, default=float))
    print(f"e={e:.2f} seed={seed} T={T_hi:.3f} (lo {T_lo:.3f}; halves {T_h1:.3f}/{T_h2:.3f}) cond={res['cond_frac']:.3f} "
          f"eta={fit['eta']:.3f} ell={fit['ell']:.1f} n_v={res['n_v']:.1f} f_free={res['f_free']:.2f} Q={res['Q']:.2f} ns/n={res['ns_over_n']:.3f} "
          f"dE={res['drift_E']:.1e} {res['seconds']}s", flush=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--procs", type=int, default=8); ap.add_argument("--quick", action="store_true")
    ap.add_argument("--energies", default=None); ap.add_argument("--t-end", type=float, default=0.0); ap.add_argument("--seeds", default=None)
    a = ap.parse_args()
    E = [float(x) for x in a.energies.split(",")] if a.energies else ENERGIES
    S = [int(x) for x in a.seeds.split(",")] if a.seeds else SEEDS
    jobs = [(e, sd, a.quick, a.t_end) for e in E for sd in S]
    with Pool(a.procs) as pool:
        pool.map(trajectory, jobs, chunksize=1)
