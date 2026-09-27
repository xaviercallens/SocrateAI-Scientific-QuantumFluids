#!/usr/bin/env python3
"""Round 4 Part B (docs/designs/PGPE_R4_PREREG.md): arms 0 / V3 / P16 / V3P16 on the three bases, saving the
density band spectrum, the torus winding and the momentum fraction at every sample.
Run: .venv/bin/python exploration/pgpe/run_r4.py [--procs 6]"""
from __future__ import annotations
import argparse, json, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from round2 import imprint, heat, run_blocks_positions
from observables import vortices

ROOT = Path(__file__).resolve().parents[2]; SW = ROOT / "data/generated/pgpe/sweep"; OUT = ROOT / "data/generated/pgpe/r4"
BASES = ["e0.60_s11_t4000", "e0.90_s11_t4000", "e0.90_s12_t4000"]
W0, BAND = 3, (0.3, 1.2)


def many_pair_config_exact(L, n_pairs=16, d=8.0, rng=None):
    """Round-3 generator with the R3-A1 fix: positions are NOT wrapped modulo L, so that sum q r = 0 exactly
    (the theta-function phase is then single-valued with no accidental torus winding)."""
    rng = rng or np.random.default_rng(0); pos, q = [], []
    for _ in range(n_pairs // 2):
        phi = rng.random() * 2 * np.pi
        for sgn in (1, -1):
            cx, cy = rng.random(2) * L; ux, uy = sgn * np.cos(phi), sgn * np.sin(phi)
            pos += [(cx - d / 2 * ux, cy - d / 2 * uy), (cx + d / 2 * ux, cy + d / 2 * uy)]; q += [1, -1]
    return np.array(pos), np.array(q)


def pv(d):
    return (d + np.pi) % (2 * np.pi) - np.pi


def torus_winding(s, c):
    th = np.angle(s.psi(c))
    wx = np.rint(pv(np.roll(th, -1, axis=0) - th).sum(axis=0) / (2 * np.pi)); wy = np.rint(pv(np.roll(th, -1, axis=1) - th).sum(axis=1) / (2 * np.pi))
    return int(np.median(wx)), int(np.median(wy))


def boost(s, c, w0):
    x = (np.arange(s.N) * s.dx)[:, None]
    c2 = s.modes(s.psi(c) * np.exp(2j * np.pi * w0 * x / s.L))
    return c2 * np.sqrt(s.norm(c) / s.norm(c2))


def density_band(s, c):
    rho = np.abs(s.psi(c)) ** 2; rk = np.fft.fft2(rho - rho.mean()); kk = np.sqrt(s.k2)
    m = (kk >= BAND[0]) & (kk <= BAND[1])
    return float(np.sum(np.abs(rk[m]) ** 2) / s.N ** 4)


def job(spec):
    t0 = time.time(); s = PGPE(N=128, L=64.0); c = np.load(SW / f"{spec['base']}_final.npy"); arm = spec["arm"]
    if "P16" in arm:
        pos, q = many_pair_config_exact(s.L, 16, 8.0, np.random.default_rng(400 + spec["idx"])); c = imprint(s, c, pos, q)
        det = vortices(s, c)[1]; spec["imprint_check"] = {"imprinted": 32, "detected": int(len(det)), "neutral": bool((det > 0).sum() == (det < 0).sum()), "W_after_pairs": torus_winding(s, c)}
    if "V3" in arm:
        # the boost shifts the spectrum by K and the projector clips the far edge of the bath (84-153 of the 177.8
        # superflow energy survive at t = 0, base-dependent); the bath is restored by `heat` so that the arm is
        # exactly "the same energy content + the superflow energy" (prereg, arm definition)
        E_before = s.energy(c); c = boost(s, c, W0); E_boost = s.energy(c)
        E_target = E_before + 0.5 * s.norm(c) * (2 * np.pi * W0 / s.L) ** 2
        c = heat(s, c, E_target, np.random.default_rng(500 + spec["idx"]))
        spec["boost_check"] = {"E_before": E_before, "E_after_boost": E_boost, "E_target": E_target, "E_after_heat": s.energy(c), "W_after_boost": torus_winding(s, c)}
    spec["W_initial"] = torus_winding(s, c); E0 = s.energy(c)
    iK = int(round(W0)); extra = []
    def cb(t, cc):
        extra.append({"t": t, "S_band": density_band(s, cc), "W": torus_winding(s, cc), "f_K": float(np.abs(cc[iK, 0]) ** 2 / np.sum(np.abs(cc) ** 2))})
    # one evolution: hook our per-sample observables onto the sampling of round_blocks_positions (same samples, same times)
    rbp = run_blocks_positions
    orig_run = s.run
    def run_with_extra(cc, t_end, callback=None, every=0):
        def both(t, x):
            callback(t, x); cb(t, x)
        return orig_run(cc, t_end, callback=both, every=every)
    s.run = run_with_extra
    c, blocks, samples = rbp(s, c, 1500.0, 0.0, seed=spec["idx"])
    s.run = orig_run
    res = {**spec, "E_per_particle": E0 / s.norm(c), "drift_E": abs(s.energy(c) - E0) / E0, "L": s.L, "blocks": blocks, "extra": extra, "W_final": torus_winding(s, c), "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True); (OUT / f"{spec['name']}.json").write_text(json.dumps(res, indent=1, default=float))
    np.savez_compressed(OUT / f"{spec['name']}_samples.npz", t=np.array([x["t"] for x in samples]),
                        pos=np.array([np.array(x["pos"], dtype=float) for x in samples], dtype=object),
                        q=np.array([np.array(x["q"], dtype=int) for x in samples], dtype=object),
                        E_inc=np.array([x["E_inc"] for x in samples]), kin_bath=np.array([x["kin_bath"] for x in samples]))
    np.save(OUT / f"{spec['name']}_final.npy", c)
    b1, bl = blocks[0], blocks[-1]
    print(f"{spec['name']}: W {spec['W_initial']}->{res['W_final']} T_b {b1['T']:.3f}->{bl['T']:.3f} n_v {b1['n_v']:.1f}->{bl['n_v']:.1f} S_band {extra[0]['S_band']:.3e}->{extra[-1]['S_band']:.3e} f_K {extra[-1]['f_K']:.3f} dE={res['drift_E']:.1e} {res['seconds']}s", flush=True)


def specs():
    return [{"kind": "B", "base": b, "arm": arm, "idx": i, "name": f"B_{b}_{arm}"} for i, b in enumerate(BASES) for arm in ("0", "V3", "P16", "V3P16")]


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--procs", type=int, default=6); a = ap.parse_args()
    with Pool(a.procs) as pool:
        pool.map(job, specs(), chunksize=1)
