#!/usr/bin/env python3
"""Estimators of vortex transport coefficients from tracked positions (PGPE_FRICTION_PREREG.md amendment A1,
PGPE_ALPHAPRIME_PREREG.md, PGPE_EINSTEIN_PREREG.md), and the synthetic generator of gate G0.

Model (hbar = m = 1, circulation 2 pi, normal fluid at rest), lean_src/DissipativeVortexDynamics.lean:
    dr_i/dt = (1 - alpha') v_s,i - alpha q_i z x v_s,i + sqrt(2 eta) xi_i,
v_s,i the torus point-vortex velocity induced by the other vortices (Weiss-McWilliams pair function h ~ 2 ln r).

    .venv/bin/python exploration/pgpe/transport_estimators.py G0      # synthetic known-answer gate
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

TWO_PI = 2 * np.pi


def grad_h(x, y, M: int = 4):
    """Gradient of the Weiss-McWilliams pair function on the 2 pi box (x, y reduced to (-pi, pi])."""
    x = (x + np.pi) % TWO_PI - np.pi; y = (y + np.pi) % TWO_PI - np.pi
    hx = -x / np.pi; hy = np.zeros_like(x)
    for m in range(-M, M + 1):
        den = np.cosh(x - TWO_PI * m) - np.cos(y)
        hx = hx + np.sinh(x - TWO_PI * m) / den; hy = hy + np.sin(y) / den
    return hx, hy


def h_pair(x, y, M: int = 4):
    x = (x + np.pi) % TWO_PI - np.pi; y = (y + np.pi) % TWO_PI - np.pi
    s = -x ** 2 / TWO_PI
    for m in range(-M, M + 1):
        s = s + np.log((np.cosh(x - TWO_PI * m) - np.cos(y)) / np.cosh(TWO_PI * m))
    return s


def pv_velocity(pos: np.ndarray, q: np.ndarray, L: float) -> np.ndarray:
    """v_s at every vortex: psi_i = -sum_j q_j h_ij/2, v = (d psi/dy, -d psi/dx)."""
    sc = TWO_PI / L; n = len(q)
    dx = (pos[:, None, 0] - pos[None, :, 0]) * sc; dy = (pos[:, None, 1] - pos[None, :, 1]) * sc
    off = ~np.eye(n, dtype=bool)
    hx = np.zeros((n, n)); hy = np.zeros((n, n))
    hx[off], hy[off] = grad_h(dx[off], dy[off])
    psix = -0.5 * sc * (hx * q[None, :]).sum(1); psiy = -0.5 * sc * (hy * q[None, :]).sum(1)
    return np.column_stack([psiy, -psix])


def pv_energy(pos: np.ndarray, q: np.ndarray, L: float) -> float:
    sc = TWO_PI / L; n = len(q); iu = np.triu_indices(n, 1)
    dx = (pos[iu[0], 0] - pos[iu[1], 0]) * sc; dy = (pos[iu[0], 1] - pos[iu[1], 1]) * sc
    return float(-np.sum(q[iu[0]] * q[iu[1]] * h_pair(dx, dy)))


def unwrap(R: np.ndarray, L: float) -> np.ndarray:
    """Positions (nt, n, 2) on the torus -> continuous trajectories."""
    d = np.diff(R, axis=0); d -= L * np.round(d / L)
    return np.concatenate([R[:1], R[:1] + np.cumsum(d, axis=0)], axis=0)


def predictors(t: np.ndarray, R: np.ndarray, q: np.ndarray, L: float):
    """Cumulative trapezoid integrals CA = int v_s dt and CB = int (-q z x v_s) dt, the point-vortex energy H(t)
    and S(t) = sum_i |v_s,i|^2, along a track."""
    nt = len(t); V = np.zeros_like(R); H = np.zeros(nt); S = np.zeros(nt)
    for k in range(nt):
        pk = np.mod(R[k], L); V[k] = pv_velocity(pk, q, L); H[k] = pv_energy(pk, q, L); S[k] = float((V[k] ** 2).sum())
    Bv = -q[None, :, None] * np.stack([-V[..., 1], V[..., 0]], axis=-1)            # -q z x v,  z x (a, b) = (-b, a)
    dt = np.diff(t)[:, None, None]
    CA = np.concatenate([np.zeros_like(V[:1]), np.cumsum(0.5 * (V[1:] + V[:-1]) * dt, axis=0)])
    CB = np.concatenate([np.zeros_like(V[:1]), np.cumsum(0.5 * (Bv[1:] + Bv[:-1]) * dt, axis=0)])
    return CA, CB, H, S


def analyse_tracks(tracks, L: float, lag: int = 10, t_settle: float = 100.0, d_valid: float = 4.0, lags_eta=(5, 10, 20, 40, 80, 120, 160, 240, 320, 400)):
    """tracks: list of (t, R (nt, n, 2), q). Returns the pre-registered estimators with block-jackknife errors
    (blocks = tracks x halves)."""
    blocks = []
    for (t, R, q) in tracks:
        # validity of the point-vortex description: keep the track up to the first sample where any vortex and
        # antivortex are closer than d_valid (below ~4 healing lengths a pair is a single solitary wave)
        close = np.array([min_opposite_distance(np.mod(R[k], L), q, L) < d_valid for k in range(len(t))])
        n_ok = int(np.argmax(close)) if close.any() else len(t)
        t, R = t[:n_ok], R[:n_ok]
        m = t >= t_settle
        if m.sum() < 3 * lag + 10:
            continue
        t, U = t[m], unwrap(R[m], L)
        CA, CB, H, S = predictors(t, U, q, L)
        half = len(t) // 2
        for sl in (slice(0, half), slice(half, len(t))):
            blocks.append({"t": t[sl], "U": U[sl], "CA": CA[sl], "CB": CB[sl], "H": H[sl], "S": S[sl]})
    if not blocks:
        return {"error": "no usable track"}

    def reg_sums(b, lg):
        D = b["U"][lg:] - b["U"][:-lg]; A = b["CA"][lg:] - b["CA"][:-lg]; B = b["CB"][lg:] - b["CB"][:-lg]
        return np.array([(A * A).sum(), (A * B).sum(), (B * B).sum(), (A * D).sum(), (B * D).sum(), (D * D).sum(), D.size])

    def solve(sm):
        M = np.array([[sm[0], sm[1]], [sm[1], sm[2]]]); c = np.linalg.solve(M, sm[3:5])
        return c                                                    # c[0] = 1 - alpha', c[1] = alpha

    def energy_sums(b):
        I = np.concatenate([[0.0], np.cumsum(0.5 * (b["S"][1:] + b["S"][:-1]) * np.diff(b["t"]))]) * 2.0   # int 2 S dt
        I0, H0 = I - I.mean(), b["H"] - b["H"].mean()
        return np.array([(I0 * H0).sum(), (I0 * I0).sum()])

    def eta_fit(bl, c):
        ms = []
        for lg in lags_eta:
            num = den = 0.0
            for b in bl:
                if len(b["t"]) <= lg + 2:
                    continue
                D = b["U"][lg:] - b["U"][:-lg]; A = b["CA"][lg:] - b["CA"][:-lg]; B = b["CB"][lg:] - b["CB"][:-lg]
                e = D - c[0] * A - c[1] * B; num += (e ** 2).sum(); den += e.shape[0] * e.shape[1]
            ms.append(num / den if den else np.nan)                 # mean |e|^2 per vortex (two components)
        lg = np.array(lags_eta, float); ms = np.array(ms); ok = np.isfinite(ms) & (lg >= 20)
        if ok.sum() < 4:
            return np.nan, np.nan, np.nan, ms
        dt = float(np.median(np.diff(bl[0]["t"])))
        p = np.polyfit(lg[ok] * dt, ms[ok], 1); eta = p[0] / 4.0; c0 = p[1]
        y = ms[ok] - c0; pos = y > 0
        gam = float(np.polyfit(np.log(lg[ok][pos]), np.log(y[pos]), 1)[0]) if pos.sum() >= 3 else np.nan
        return float(eta), float(c0), gam, ms

    def estimate(bl):
        c = solve(sum(reg_sums(b, lag) for b in bl))
        es = sum(energy_sums(b) for b in bl); a_en = -es[0] / es[1]
        eta, c0, gam, ms = eta_fit(bl, c)
        return np.array([c[0], c[1], a_en, eta, gam, c0]), ms

    full, ms = estimate(blocks); nb = len(blocks)
    jk = np.array([estimate(blocks[:i] + blocks[i + 1:])[0] for i in range(nb)]) if nb >= 3 else np.full((1, 6), np.nan)
    se = np.sqrt((nb - 1) / nb * np.nansum((jk - np.nanmean(jk, axis=0)) ** 2, axis=0)) if nb >= 3 else np.full(6, np.nan)
    names = ["one_minus_alpha_prime", "alpha_regression", "alpha_energy", "eta", "msd_exponent", "msd_offset"]
    out = {n: float(v) for n, v in zip(names, full)}; out.update({n + "_se": float(v) for n, v in zip(names, se)})
    out.update({"n_blocks": nb, "lag": lag, "lags_eta": list(lags_eta), "msd": [float(x) for x in ms]})
    return out


# ---- synthetic generator (gate G0) ------------------------------------------------------------------------------------
def antiparallel(L: float, d0: float, rng) -> tuple[np.ndarray, np.ndarray]:
    """Two antiparallel dipoles: zero net charge and zero net dipole moment (no net impulse)."""
    y0 = rng.uniform(0, L); ox, oy = rng.uniform(0, 0.5, 2)
    pos = np.array([[L / 4 + d0 / 2 + ox, y0 + oy], [L / 4 - d0 / 2 + ox, y0 + oy],
                    [3 * L / 4 - d0 / 2 + ox, y0 + oy], [3 * L / 4 + d0 / 2 + ox, y0 + oy]])
    return np.mod(pos, L), np.array([1, -1, 1, -1])


def min_opposite_distance(r, q, L):
    a, b = r[q > 0], r[q < 0]
    d = a[:, None, :] - b[None, :, :]; d -= L * np.round(d / L)
    return float(np.sqrt((d ** 2).sum(-1)).min())


def langevin(pos0, q, L, alpha, alphap, eta, t_end, rng, dt=0.05, dt_sample=1.0, d_stop=2.0):
    """Stops as soon as ANY vortex and antivortex come within d_stop (checked every substep): below that the
    point-vortex model is singular, and in the field the pair annihilates (first G0 attempt failed on exactly
    this: partner exchange between the two dipoles produced unphysical trajectories)."""
    r = pos0.astype(float).copy(); out_t, out_R = [0.0], [r.copy()]; nsub = int(round(dt_sample / dt)); t = 0.0
    while t < t_end - 1e-9:
        for _ in range(nsub):
            v = pv_velocity(np.mod(r, L), q, L)
            r = r + ((1 - alphap) * v - alpha * q[:, None] * np.column_stack([-v[:, 1], v[:, 0]])) * dt + np.sqrt(2 * eta * dt) * rng.standard_normal(r.shape)
            if min_opposite_distance(r, q, L) < d_stop:
                return np.array(out_t), np.array(out_R)
        t += dt_sample; out_t.append(t); out_R.append(r.copy())
    return np.array(out_t), np.array(out_R)


def gate_G0(out: Path):
    L, truth = 64.0, {"alpha": 0.02, "alphap": 0.10, "eta": 2e-3}; rng = np.random.default_rng(20261005); tracks = []
    for i in range(8):
        pos, q = antiparallel(L, 10.0, rng)
        t, R = langevin(pos, q, L, truth["alpha"], truth["alphap"], truth["eta"], 2000.0, rng)
        tracks.append((t, R + 0.2 * rng.standard_normal(R.shape), q))            # detection noise, 0.2 per coordinate
    r = analyse_tracks(tracks, L)
    chk = {"alpha_energy_within_15pct": abs(r["alpha_energy"] / truth["alpha"] - 1) <= 0.15,
           "one_minus_alphap_within_0.02": abs(r["one_minus_alpha_prime"] - (1 - truth["alphap"])) <= 0.02,
           "eta_within_25pct": abs(r["eta"] / truth["eta"] - 1) <= 0.25}
    res = {"truth": truth, "estimates": r, "checks": chk, "PASS": bool(all(chk.values())), "track_lengths": [float(t[-1]) for t, _, _ in tracks]}
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items() if k != "msd"}))
    print("track lengths", res["track_lengths"]); print("checks", chk, "-> G0", "PASS" if res["PASS"] else "FAIL")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "G0":
        ROOT = Path(__file__).resolve().parents[2]; (ROOT / "data/generated/pgpe/transport").mkdir(parents=True, exist_ok=True)
        gate_G0(ROOT / "data/generated/pgpe/transport/G0_synthetic.json")
