#!/usr/bin/env python3
"""Canonical (Metropolis) calibration of the torus vortex thermometer, after Groszek et al. PRL 120, 034504 (2018),
with the Weiss-McWilliams torus Hamiltonian. Moves displace a same-sign pair oppositely, so the vortex momentum
P = Σ κ r is conserved exactly. Two internal known answers, run before any reading:
  (i) fluctuation identity  d<E>/dβ = −Var(E)  (canonical ensemble, exact);
  (ii) closure: an ensemble generated at β0 must read back β0 within 10 % from <E>.
Units: E_WM (κ = 1, box 2π). Physical: E_phys = π E_WM, β_phys = β_WM / π  (ρ = 1, κ = 2π, k_B = 1).
Run: .venv/bin/python exploration/pgpe/vortex_thermometer_canonical.py  -> data/generated/pgpe/vortex_thermometer_cal.json
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vortex_thermometer import h_pair, energy, random_neutral_p0, TWO_PI

ROOT = Path(__file__).resolve().parents[2]
CORE = 0.02 * TWO_PI          # hard core (in 2π-box units) ≈ 1.3 ξ at L = 64: prevents the ln divergence


def pair_energies(pos, q, i):
    """Interaction energy of vortex i with all others."""
    dx = pos[:, 0] - pos[i, 0]; dy = pos[:, 1] - pos[i, 1]
    h = h_pair(dx, dy); h[i] = 0.0
    return -float(np.sum(q[i] * q * h))


def too_close(pos, i):
    d = pos - pos[i]; d = (d + np.pi) % TWO_PI - np.pi
    r = np.hypot(d[:, 0], d[:, 1]); r[i] = np.inf
    return bool(np.any(r < CORE))


def metropolis(n_pairs, beta, rng, sweeps=4000, burn=1000, step=0.6):
    pos, q = random_neutral_p0(n_pairs, rng)
    n = len(q); E = energy(pos, q, TWO_PI)
    samples = []
    plus = np.nonzero(q > 0)[0]; minus = np.nonzero(q < 0)[0]
    for s in range(sweeps):
        for _ in range(n):
            grp = plus if rng.random() < 0.5 else minus
            i, j = rng.choice(grp, 2, replace=False)
            d = rng.normal(0, step, 2)
            old_i, old_j = pos[i].copy(), pos[j].copy()
            e_old = pair_energies(pos, q, i) + pair_energies(pos, q, j) + q[i] * q[j] * h_pair(np.array([pos[j, 0] - pos[i, 0]]), np.array([pos[j, 1] - pos[i, 1]]))[0]
            pos[i] = (pos[i] + d) % TWO_PI; pos[j] = (pos[j] - d) % TWO_PI
            if too_close(pos, i) or too_close(pos, j):
                pos[i], pos[j] = old_i, old_j; continue
            e_new = pair_energies(pos, q, i) + pair_energies(pos, q, j) + q[i] * q[j] * h_pair(np.array([pos[j, 0] - pos[i, 0]]), np.array([pos[j, 1] - pos[i, 1]]))[0]
            dE = e_new - e_old
            if dE <= 0 or rng.random() < np.exp(-beta * dE):
                E += dE
            else:
                pos[i], pos[j] = old_i, old_j
        if s >= burn and s % 5 == 0:
            samples.append(E)
    return np.array(samples)


def calibrate(n_pairs, betas, rng, **kw):
    cal = []
    for b in betas:
        t0 = time.time(); Es = metropolis(n_pairs, b, rng, **kw)
        cal.append({"beta": b, "E_mean": float(Es.mean()), "E_var": float(Es.var()), "n": len(Es), "sec": round(time.time() - t0, 1)})
        print(f"  beta={b:+.3f}  <E>={Es.mean():8.3f}  Var={Es.var():7.3f}  ({cal[-1]['sec']}s)", flush=True)
    return cal


def read_beta(cal, E):
    """Invert the monotone <E>(β) by linear interpolation; nan outside the calibrated range."""
    b = np.array([c["beta"] for c in cal]); e = np.array([c["E_mean"] for c in cal])
    o = np.argsort(e); b, e = b[o], e[o]
    if not (e[0] <= E <= e[-1]):
        return float("nan")
    return float(np.interp(E, e, b))


if __name__ == "__main__":
    rng = np.random.default_rng(2018)
    out = {}
    for n_pairs in (2, 3, 4, 5, 6, 8):
        print(f"N = {2*n_pairs} vortices")
        betas = [-0.6, -0.3, 0.0, 0.3, 0.6, 1.0, 1.5, 2.0, 3.0]
        cal = calibrate(n_pairs, betas, rng)
        # (i) fluctuation identity: finite-difference d<E>/dβ vs −Var(E) at interior points
        b = np.array([c["beta"] for c in cal]); e = np.array([c["E_mean"] for c in cal]); v = np.array([c["E_var"] for c in cal])
        dEdb = np.gradient(e, b); fd = [(float(bb), float(x), float(-y)) for bb, x, y in zip(b[1:-1], dEdb[1:-1], v[1:-1])]
        # (ii) closure at β0 = 1.2 (not in the grid)
        Es = metropolis(n_pairs, 1.2, rng, sweeps=3000, burn=800)
        b_read = read_beta(cal, float(Es.mean()))
        out[str(2 * n_pairs)] = {"cal": cal, "fluct_identity_(beta,dE/dbeta,-Var)": fd, "closure_beta0": 1.2, "closure_read": b_read,
                                 "closure_PASS": bool(np.isfinite(b_read) and abs(b_read - 1.2) / 1.2 <= 0.10)}
        print(f"  closure: set 1.2 read {b_read:.3f}  -> {'PASS' if out[str(2*n_pairs)]['closure_PASS'] else 'FAIL'}")
    (ROOT / "data/generated/pgpe/vortex_thermometer_cal.json").write_text(json.dumps(out, indent=1))
