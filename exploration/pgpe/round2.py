"""Round 2 of the PGPE programme (docs/designs/PGPE_R2_PREREG.md): vortex imprinting on the torus, energy-matched
heating, and a block-averaged trajectory with the noise-aware g1 window (Part IV)."""
from __future__ import annotations
import numpy as np
from pgpe import PGPE
from observables import thermometer, condensate_fraction, g1_radial, vortices, dipole_matching, current_correlators

Q_NOME = np.exp(-np.pi)          # nome of the square torus, tau = i


def theta1(u: np.ndarray, nterms: int = 10) -> np.ndarray:
    """Jacobi theta_1(u | tau = i) = 2 sum_{n>=0} (-1)^n q^{(n+1/2)^2} sin((2n+1)u), q = e^{-pi}."""
    out = np.zeros_like(u, dtype=complex)
    for n in range(nterms):
        out += (-1) ** n * Q_NOME ** ((n + 0.5) ** 2) * np.sin((2 * n + 1) * u)
    return 2 * out


def quadrupole_config(L: float, d: float = 16.0, off: float = 0.25):
    """4 vortex-antivortex pairs of separation d on a 2x2 arrangement with alternating dipole orientation, so that
    sum q = 0 and sum q r = 0 (the conditions for the theta-function phase to be single-valued; prereg Part I)."""
    pos, q = [], []
    for (cx, cy, sgn) in [(L / 4, L / 4, 1), (3 * L / 4, L / 4, -1), (L / 4, 3 * L / 4, -1), (3 * L / 4, 3 * L / 4, 1)]:
        pos += [(cx - d / 2 + off, cy + off), (cx + d / 2 + off, cy + off)]
        q += [sgn, -sgn]
    return np.array(pos), np.array(q)


def imprint(s: PGPE, c: np.ndarray, pos: np.ndarray, q: np.ndarray, core2: float = 2.0) -> np.ndarray:
    """Multiply psi by prod_j (theta1_j/|theta1_j|)^{q_j} * rho_j/sqrt(rho_j^2 + core2), project, restore the norm."""
    x = np.arange(s.N) * s.dx
    X, Y = np.meshgrid(x, x, indexing="ij")
    Z = X + 1j * Y
    phase = np.ones_like(Z); amp = np.ones(Z.shape)
    for (xj, yj), qj in zip(pos, q):
        t = theta1(np.pi * (Z - (xj + 1j * yj)) / s.L)
        u = t / np.abs(t)
        phase *= u if qj > 0 else np.conj(u)
        dxp = X - xj; dxp -= s.L * np.round(dxp / s.L)
        dyp = Y - yj; dyp -= s.L * np.round(dyp / s.L)
        r2 = dxp ** 2 + dyp ** 2
        amp *= np.sqrt(r2 / (r2 + core2))
    psi = s.psi(c) * phase * amp
    c2 = s.modes(psi)
    return c2 * np.sqrt(s.norm(c) / s.norm(c2))


def heat(s: PGPE, c: np.ndarray, E_target: float, rng: np.random.Generator, band=(0.2, 1.0), iters: int = 80) -> np.ndarray:
    """Add eps * P[eta], eta random complex on |k| in band*k_cut, restore the norm, bisect eps so that E = E_target."""
    kk = np.sqrt(s.k2)
    mask = (kk >= band[0] * s.kcut) & (kk <= band[1] * s.kcut) & s.P
    eta = (rng.standard_normal(c.shape) + 1j * rng.standard_normal(c.shape)) * mask
    eta *= np.sqrt(s.norm(c) / s.norm(eta))
    N0 = s.norm(c)

    def make(eps):
        c2 = c + eps * eta
        return c2 * np.sqrt(N0 / s.norm(c2))
    if s.energy(make(0.0)) > E_target:
        raise ValueError("target energy below the base energy")
    lo, hi = 0.0, 0.05
    while s.energy(make(hi)) < E_target:
        hi *= 2
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if s.energy(make(mid)) < E_target:
            lo = mid
        else:
            hi = mid
    return make(0.5 * (lo + hi))


def fit_g1_window(r, g, L, rmin=2.0, floor=0.05, minpts=6):
    """Part IV: fit on [rmin, r_max], r_max = min(L/4, first r >= rmin with g < floor); < minpts points -> no law."""
    rmax = L / 4
    below = np.nonzero((r >= rmin) & (g < floor))[0]
    if len(below):
        rmax = min(rmax, r[below[0]])
    m = (r >= rmin) & (r < rmax) & (g > 0)
    out = {"r_max": float(rmax), "npts": int(m.sum())}
    if m.sum() < minpts:
        return {**out, "eta": float("nan"), "ell": float("nan"), "law": "none"}
    x, y = r[m], np.log(g[m])
    p1, res1 = np.linalg.lstsq(np.vstack([np.log(x), np.ones_like(x)]).T, y, rcond=None)[:2]
    p2, res2 = np.linalg.lstsq(np.vstack([x, np.ones_like(x)]).T, y, rcond=None)[:2]
    r1 = float(res1[0]) if len(res1) else 0.0; r2 = float(res2[0]) if len(res2) else 0.0
    return {**out, "eta": float(-p1[0]), "ell": float(-1 / p2[0]) if p2[0] < 0 else float("inf"),
            "law": "algebraic" if r1 < r2 else "exponential"}


def run_blocks(s: PGPE, c: np.ndarray, t_end: float, t_tr: float = 0.0, block: float = 100.0, every_t: float = 10.0, seed: int = 0):
    """Evolve; after t_tr sample every every_t; aggregate per block of `block` time units and over the whole window."""
    c = s.run(c, t_tr) if t_tr > 0 else c
    rng = np.random.default_rng(10_000 + seed)
    nb = int(round((t_end - t_tr) / block)); per = int(round(block / every_t)); every = int(round(every_t / s.dt))
    blocks = [dict(occ=np.zeros_like(s.k2), g1=None, cond=[], nv=[], Q=[], JL=[], JT=[]) for _ in range(nb)]
    k = {"i": 0}

    def cb(t, cc):
        b = blocks[min(k["i"] // per, nb - 1)]; k["i"] += 1
        b["occ"] += np.abs(cc) ** 2 * s.dx ** 2 / s.N ** 2
        r, g = g1_radial(s, cc); b["g1"] = g if b["g1"] is None else b["g1"] + g; b["r"] = r
        b["cond"].append(condensate_fraction(s, cc))
        pos, q = vortices(s, cc); b["nv"].append(len(q)); b["Q"].append(dipole_matching(s, pos, q, rng)[2])
        cr = current_correlators(s, cc)
        b["JL"].append(np.mean([v[0] for v in cr.values()])); b["JT"].append(np.mean([v[1] for v in cr.values()]))
    c = s.run(c, t_end - t_tr, callback=cb, every=every)
    out = []
    for i, b in enumerate(blocks):
        n = len(b["cond"]); occ = b["occ"] / n; g = b["g1"] / n
        T = thermometer(s, occ, 0.6, 1.0)[0]; JL, JT = float(np.mean(b["JL"])), float(np.mean(b["JT"]))
        fit = fit_g1_window(b["r"], g, s.L)
        out.append({"t0": t_tr + i * block, "T": T, "cond": float(np.mean(b["cond"])), "n_v": float(np.mean(b["nv"])),
                    "Q": float(np.nanmean(b["Q"])) if np.any(np.isfinite(b["Q"])) else float("nan"),
                    "JL": JL, "JT": JT, "ns_over_n": 1 - JT / JL, "eta": fit["eta"], "law": fit["law"], "g1_npts": fit["npts"]})
    # whole window
    occ = sum(b["occ"] for b in blocks) / sum(len(b["cond"]) for b in blocks)
    g = sum(b["g1"] for b in blocks) / sum(len(b["cond"]) for b in blocks)
    T = thermometer(s, occ, 0.6, 1.0)[0]; T_lo = thermometer(s, occ, 0.4, 0.6)[0]
    JL = float(np.mean([x for b in blocks for x in b["JL"]])); JT = float(np.mean([x for b in blocks for x in b["JT"]]))
    fit = fit_g1_window(blocks[0]["r"], g, s.L)
    whole = {"T": T, "T_lowwindow": T_lo, "cond": float(np.mean([x for b in blocks for x in b["cond"]])),
             "n_v": float(np.mean([x for b in blocks for x in b["nv"]])),
             "Q": float(np.nanmean([x for b in blocks for x in b["Q"]])) if any(np.isfinite(x) for b in blocks for x in b["Q"]) else float("nan"),
             "JL": JL, "JT": JT, "ns_over_n": 1 - JT / JL, "R_L": JL / (T * s.L ** 2), "R_T": JT / (T * s.L ** 2),
             "eta": fit["eta"], "ell": fit["ell"], "law": fit["law"], "g1_npts": fit["npts"], "g1_rmax": fit["r_max"]}
    return c, out, whole


def many_pair_config(L: float, n_pairs: int = 16, d: float = 8.0, rng=None):
    """Round 3 Part D: n_pairs dipoles of separation d at random centres, dipole vectors in cancelling groups of two
    (orientation phi and phi + pi), so that sum q = 0 and sum q r = 0 exactly (single-valued theta-function phase)."""
    rng = rng or np.random.default_rng(0)
    assert n_pairs % 2 == 0
    pos, q = [], []
    for k in range(n_pairs // 2):
        phi = rng.random() * 2 * np.pi
        for sgn in (1, -1):
            cx, cy = rng.random(2) * L
            ux, uy = sgn * np.cos(phi), sgn * np.sin(phi)
            pos += [((cx - d / 2 * ux) % L, (cy - d / 2 * uy) % L), ((cx + d / 2 * ux) % L, (cy + d / 2 * uy) % L)]
            q += [1, -1]
    return np.array(pos), np.array(q)


def run_blocks_positions(s: PGPE, c: np.ndarray, t_end: float, t_tr: float = 0.0, block: float = 100.0, every_t: float = 10.0, seed: int = 0):
    """As run_blocks, but also returns the vortex positions/charges and the energy budget at every sample."""
    from vortex_thermometer import energy as pv_energy
    c = s.run(c, t_tr) if t_tr > 0 else c
    rng = np.random.default_rng(10_000 + seed)
    nb = int(round((t_end - t_tr) / block)); per = int(round(block / every_t)); every = int(round(every_t / s.dt))
    blocks = [dict(occ=np.zeros_like(s.k2), g1=None, cond=[], nv=[], Q=[], JL=[], JT=[], E_pv=[], budget=[]) for _ in range(nb)]
    samples = []; k = {"i": 0}
    kk = np.sqrt(s.k2); w = s.dx ** 2 / s.N ** 2

    def budget(cc):
        psi = s.psi(cc); rho = np.abs(psi) ** 2; kin_k = 0.5 * s.k2 * np.abs(cc) ** 2 * w
        gx = np.fft.ifft2(1j * s.kx * cc); gy = np.fft.ifft2(1j * s.ky * cc); jx = (np.conj(psi) * gx).imag; jy = (np.conj(psi) * gy).imag
        sr = np.sqrt(rho + 1e-30); Ux, Uy = np.fft.fft2(jx / sr), np.fft.fft2(jy / sr); k2 = np.where(s.k2 == 0, 1, s.k2)
        div = (s.kx * Ux + s.ky * Uy) / k2; Ic = 0.5 * np.sum(np.abs(s.kx * div) ** 2 + np.abs(s.ky * div) ** 2) * w
        It = 0.5 * np.sum(np.abs(Ux) ** 2 + np.abs(Uy) ** 2) * w
        return {"kin_bath": float(kin_k[(kk >= 0.4 * s.kcut) & s.P].sum()), "kin_lowk": float(kin_k[(kk < 0.4 * s.kcut)].sum()),
                "E_inc": float(It - Ic), "E_comp": float(Ic), "interaction": float(0.5 * s.g * np.sum(rho ** 2) * s.dx ** 2)}

    def cb(t, cc):
        b = blocks[min(k["i"] // per, nb - 1)]; k["i"] += 1
        b["occ"] += np.abs(cc) ** 2 * w
        r, g = g1_radial(s, cc); b["g1"] = g if b["g1"] is None else b["g1"] + g; b["r"] = r
        b["cond"].append(condensate_fraction(s, cc))
        pos, q = vortices(s, cc); b["nv"].append(len(q)); b["Q"].append(dipole_matching(s, pos, q, rng)[2])
        neutral = len(q) >= 4 and (q > 0).sum() == (q < 0).sum()
        b["E_pv"].append(pv_energy(pos, q, s.L) if neutral else float("nan"))
        cr = current_correlators(s, cc); b["JL"].append(np.mean([v[0] for v in cr.values()])); b["JT"].append(np.mean([v[1] for v in cr.values()]))
        bud = budget(cc); b["budget"].append(bud)
        samples.append({"t": t_tr + t, "pos": pos.tolist(), "q": q.tolist(), "E_pv": b["E_pv"][-1], **bud})
    c = s.run(c, t_end - t_tr, callback=cb, every=every)
    out = []
    for i, b in enumerate(blocks):
        n = len(b["cond"]); occ = b["occ"] / n; g = b["g1"] / n
        T = thermometer(s, occ, 0.6, 1.0)[0]; fit = fit_g1_window(b["r"], g, s.L)
        Epv = np.array(b["E_pv"]); nv = np.array(b["nv"])
        keys = b["budget"][0].keys()
        out.append({"t0": t_tr + i * block, "T": T, "cond": float(np.mean(b["cond"])), "n_v": float(nv.mean()),
                    "Q": float(np.nanmean(b["Q"])) if np.any(np.isfinite(b["Q"])) else float("nan"),
                    "JL": float(np.mean(b["JL"])), "JT": float(np.mean(b["JT"])), "eta": fit["eta"], "law": fit["law"],
                    "E_pv_mean": float(np.nanmean(Epv)) if np.any(np.isfinite(Epv)) else float("nan"),
                    "N_mode": int(np.round(np.median(nv[np.isfinite(Epv)]))) if np.any(np.isfinite(Epv)) else 0,
                    **{k2: float(np.mean([bb[k2] for bb in b["budget"]])) for k2 in keys}})
    return c, out, samples
