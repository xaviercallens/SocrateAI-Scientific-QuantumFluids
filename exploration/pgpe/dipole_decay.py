#!/usr/bin/env python3
"""Single imprinted vortex dipole in a thermal PGPE state: track its separation d(t) until annihilation.
Dissipative point-vortex dynamics (mutual friction alpha, hbar = m = 1, Gamma = 2 pi): the dipole translates at 1/d
and its members approach at 2 alpha / d, so d^2 = d0^2 - 4 alpha t and the lifetime is d0^2 / (4 alpha).

    .venv/bin/python exploration/pgpe/dipole_decay.py BASE_FINAL.npy D0 T_MAX OUT.json [--seed S] [--dt-sample 0.5]

Tracking: the imprinted +1 and -1 are followed by nearest same-sign detection within r_track of their previous
positions; a step where either jumps by more than r_track is flagged (possible swap with a thermal vortex), and
the run ends when d < d_stop (cores merged) or a track is lost."""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from observables import vortices, thermometer
from round2 import imprint


def mindist(a, b, L):
    d = a - b; d -= L * np.round(d / L)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base"); ap.add_argument("d0", type=float); ap.add_argument("t_max", type=float); ap.add_argument("out")
    ap.add_argument("--N", type=int, default=128); ap.add_argument("--L", type=float, default=64.0)
    ap.add_argument("--dt-sample", type=float, default=0.5); ap.add_argument("--r-track", type=float, default=1.5)
    ap.add_argument("--d-stop", type=float, default=2.0); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smooth", type=float, default=0.0, help="Gaussian coarse-graining length applied before vortex detection")
    a = ap.parse_args()
    s = PGPE(N=a.N, L=a.L); c0 = np.load(a.base)
    rng = np.random.default_rng(a.seed)
    # dipole centre at a random point, axis along x (dipole then translates along y)
    x0, y0 = rng.uniform(0, a.L, 2)
    p_plus = np.array([(x0 + a.d0 / 2) % a.L, y0]); p_minus = np.array([(x0 - a.d0 / 2) % a.L, y0])
    E_base = s.energy(c0)
    c = imprint(s, c0, np.array([p_plus, p_minus]), np.array([1, -1]))
    T0 = float("nan")   # a single-snapshot thermometer reading is meaningless; T is the base run's block average
    E0 = s.energy(c)
    track = []; flags = 0; t = 0.0; t0 = time.time(); ended = "t_max"
    pp, pm = p_plus.copy(), p_minus.copy()
    while t <= a.t_max + 1e-9:
        pos, q = vortices(s, c * np.exp(-0.5 * s.k2 * a.smooth ** 2) if a.smooth > 0 else c)
        new = []
        for prev, sign in ((pp, 1), (pm, -1)):
            cand = pos[q == sign]
            if len(cand) == 0:
                new.append(None); continue
            dist = np.sqrt((mindist(cand, prev, a.L) ** 2).sum(1)); j = int(np.argmin(dist))
            new.append(cand[j] if dist[j] <= a.r_track else None)
        if new[0] is None or new[1] is None:
            ended = "track_lost"; break
        jump = max(np.sqrt((mindist(new[0], pp, a.L) ** 2).sum()), np.sqrt((mindist(new[1], pm, a.L) ** 2).sum()))
        pp, pm = new
        d = float(np.sqrt((mindist(pp, pm, a.L) ** 2).sum()))
        track.append({"t": t, "d": d, "n_v": int(len(q)), "jump": float(jump)})
        if d < a.d_stop:
            ended = "annihilated"; break
        c = s.run(c, a.dt_sample); t += a.dt_sample
    tt = np.array([r["t"] for r in track]); dd = np.array([r["d"] for r in track])
    m = dd > a.d_stop + 1.0
    fit = np.polyfit(tt[m], dd[m] ** 2, 1) if m.sum() >= 5 else [float("nan"), float("nan")]
    res = {"base": a.base, "d0": a.d0, "seed": a.seed, "T_after_imprint": T0, "E_base": E_base, "E_imprinted": E0,
           "drift_E": abs(s.energy(c) - E0) / E0, "ended": ended, "t_end": t, "slope_d2": float(fit[0]),
           "alpha_from_slope": float(-fit[0] / 4), "track": track, "seconds": round(time.time() - t0, 1)}
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(a.out, {k: res[k] for k in ("T_after_imprint", "ended", "t_end", "slope_d2", "alpha_from_slope", "drift_E", "seconds")})


if __name__ == "__main__":
    main()
