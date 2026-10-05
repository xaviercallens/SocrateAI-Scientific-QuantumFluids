#!/usr/bin/env python3
"""autoresearch / probes.py -- the MUTABLE file (Karpathy's train.py): one <= 5-minute probe per hypothesis of
hypotheses.json. Each prints one line `PROBE_RESULT {...}` with
    D           discriminating power in standard errors (see prepare.py)
    consistent  False if the probe's outcome contradicts the hypothesis' own sharp prediction by > 3 sigma, or its
                built-in known-answer check fails (then the engine scores it 0)
and whatever detail explains the number. Existing data only, except H08, which is a 5-minute simulation.

    .venv/bin/python exploration/autoresearch/probes.py H04
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "pgpe"))
import prepare as P
from pgpe import PGPE

T0 = time.time()
PG = P.PG


def left() -> float:
    return P.BUDGET_S - (time.time() - T0)


def mindist(d, L):
    return d - L * np.round(d / L)


# ---- H01 / H02: single-dipole tracks already on disk (tracker pilots and known-answer runs) -----------------------
def dipole_tracks():
    """(label, T_bath, t, d) for every finished dipole track with coarse-grained detection (sigma = 1.5)."""
    out = []
    Tb = {"e0.90_s11_t4000": json.loads((PG / "sweep/e0.90_s11_t4000.json").read_text())["T"],
          "e0.60_s11": json.loads((PG / "sweep/e0.60_s11_t4000.json").read_text())["T"],
          "II_e0.90_s11_t4000_e1.10": json.loads((PG / "r2/II_e0.90_s11_t4000_e1.10.json").read_text())["whole"]["T"]}
    files = sorted((PG / "dipole_pilot2").glob("*_sm1.5.json")) + sorted(f for f in (PG / "dipole_ka").glob("*.json") if "seed1.json" not in f.name)
    for f in files:
        d = json.loads(f.read_text()); tr = d["track"]
        base = next((k for k in Tb if f.name.startswith(k)), None)
        if base is None or len(tr) < 30:
            continue
        out.append((f.stem, Tb[base], np.array([r["t"] for r in tr]), np.array([r["d"] for r in tr])))
    return out


def d2_slope(t, d, nblock=5):
    """Slope of d^2 vs t over d > 3, with a block-jackknife standard error."""
    m = d > 3.0; t, y = t[m], d[m] ** 2
    if len(t) < 20:
        return np.nan, np.nan
    full = np.polyfit(t, y, 1)[0]
    idx = np.array_split(np.arange(len(t)), nblock)
    jk = np.array([np.polyfit(np.delete(t, i), np.delete(y, i), 1)[0] for i in idx])
    se = np.sqrt((nblock - 1) / nblock * np.sum((jk - jk.mean()) ** 2))
    return full, se


def H01():
    rows = []
    for lab, T, t, d in dipole_tracks():
        s, se = d2_slope(t, d)
        if np.isfinite(s):
            rows.append({"track": lab, "T": T, "alpha": -s / 4, "se": se / 4, "z": (-s / se) if se > 0 else 0.0})
    if not rows:
        return P.emit(float("nan"), note="no usable track")
    D = float(np.median([max(r["z"], 0.0) for r in rows]))
    P.emit(D, consistent=True, rows=rows, note=f"median slope significance over {len(rows)} tracks; alpha = " + ", ".join(f"{r['alpha']:.3f}@T={r['T']:.2f}" for r in rows))


def H02():
    ratios, rows = [], []
    for lab, T, t, d in dipole_tracks():
        s, _ = d2_slope(t, d)
        if not np.isfinite(s) or s >= 0:
            continue
        alpha = -s / 4; eta_pred = alpha * T / (2 * np.pi)          # Mehdi et al.: eta = alpha k_B T / (2 pi hbar rho_0), rho_0 = 1
        m = d > 3.0; tt, dd = t[m], d[m]; dt = float(np.median(np.diff(tt)))
        p = np.polyfit(tt, dd ** 2, 1); res = dd - np.sqrt(np.clip(np.polyval(p, tt), 1e-6, None))
        for blk in np.array_split(np.arange(len(res)), 3):
            r = res[blk]
            if len(r) < 20:
                continue
            lags = np.arange(1, 9); S = np.array([np.mean((r[l:] - r[:-l]) ** 2) for l in lags])
            b = np.polyfit(lags * dt, S, 1)[0]                        # S = a (detection noise) + 4 eta tau
            ratios.append((b / 4) / eta_pred)
        rows.append({"track": lab, "T": T, "alpha": alpha, "eta_pred": eta_pred})
    pos = np.array([r for r in ratios if r > 0])
    if len(pos) < max(3, len(ratios) // 2 + 1):
        return P.emit(0.0, consistent=True, note=f"diffusion slope not positive in {len(ratios) - len(pos)}/{len(ratios)} blocks: eta not resolved", rows=rows)
    x = np.log10(pos); med = float(np.median(x)); sig = float(1.4826 * np.median(np.abs(x - med)) / np.sqrt(len(x))) or 1e-9
    P.emit(2.0 / sig, consistent=True, log10_ratio=med, sigma=sig, n_blocks=len(x), rows=rows,
           note=f"log10(eta_meas/eta_Einstein) = {med:.2f} +- {sig:.2f} ({len(x)} blocks); Einstein = 0, Neely-like excess = 2")


# ---- H03: do vortices move at the point-vortex velocity? (alpha' from the round-3 V arms) ---------------------------
def pv_velocity(pos, q, L):
    """Velocity of every vortex induced by all others on the torus (hbar = m = 1, Gamma = 2 pi), from the
    Weiss-McWilliams pair function h (h ~ 2 ln r): psi_ij = -kappa_j h/2, u = d psi/dy, v = -d psi/dx."""
    from vortex_thermometer import h_pair
    sc = 2 * np.pi / L; eps = 1e-4; n = len(q); v = np.zeros((n, 2))
    for i in range(n):
        dxy = (pos[i] - np.delete(pos, i, axis=0)) * sc; kj = np.delete(q, i)
        hx = (h_pair(dxy[:, 0] + eps, dxy[:, 1]) - h_pair(dxy[:, 0] - eps, dxy[:, 1])) / (2 * eps)
        hy = (h_pair(dxy[:, 0], dxy[:, 1] + eps) - h_pair(dxy[:, 0], dxy[:, 1] - eps)) / (2 * eps)
        v[i, 0] = np.sum(-kj * 0.5 * hy) * sc; v[i, 1] = np.sum(kj * 0.5 * hx) * sc
    return v


def slope_arm(name, L=64.0, t_max=600.0):
    from scipy.optimize import linear_sum_assignment
    z = np.load(P.R3 / f"{name}_samples.npz", allow_pickle=True); t, POS, Q = z["t"], z["pos"], z["q"]
    meas, pred, blk = [], [], []
    for i in range(len(t) - 1):
        if t[i + 1] > t_max:
            break
        p0, q0, p1, q1 = np.asarray(POS[i], float), np.asarray(Q[i], int), np.asarray(POS[i + 1], float), np.asarray(Q[i + 1], int)   # npz object arrays
        if len(q0) < 2 or len(q1) < 2:
            continue
        v0, v1 = pv_velocity(p0, q0, L), pv_velocity(p1, q1, L)
        for sgn in (1, -1):
            a, b = np.nonzero(q0 == sgn)[0], np.nonzero(q1 == sgn)[0]
            if len(a) == 0 or len(b) == 0:
                continue
            C = np.sqrt((mindist(p0[a][:, None, :] - p1[b][None, :, :], L) ** 2).sum(-1))
            ri, ci = linear_sum_assignment(C)
            for r_, c_ in zip(ri, ci):
                ia, ib = a[r_], b[c_]
                if C[r_, c_] > 2.5 or np.hypot(*v0[ia]) > 0.2 or np.hypot(*v1[ib]) > 0.2:
                    continue                                          # lost track, or a tight (fast) thermal pair
                meas.append(mindist(p1[ib] - p0[ia], L)); pred.append(0.5 * (v0[ia] + v1[ib]) * (t[i + 1] - t[i])); blk.append(i)
    meas, pred, blk = np.array(meas), np.array(pred), np.array(blk)
    if len(meas) < 40:
        return np.nan, np.nan, len(meas)
    s = float(np.sum(meas * pred) / np.sum(pred * pred))
    groups = np.array_split(np.unique(blk), 6)
    jk = []
    for g in groups:
        keep = ~np.isin(blk, g); jk.append(np.sum(meas[keep] * pred[keep]) / np.sum(pred[keep] * pred[keep]))
    jk = np.array(jk); se = float(np.sqrt(5 / 6 * np.sum((jk - jk.mean()) ** 2)))
    return s, se, len(meas)


def H03():
    res = {}
    for base in ("e0.60_s11_t4000", "e0.90_s11_t4000", "e0.90_s12_t4000"):
        s, se, n = slope_arm(f"A_{base}_V")
        rho_n = 1 - json.loads((PG / f"sweep/{base}.json").read_text())["ns_over_n"]
        res[base] = {"slope": s, "se": se, "n": n, "rho_n_over_rho": rho_n}
    ka = res["e0.60_s11_t4000"]                                       # known answer: at T = 0.115 both theories give slope ~ 1
    ok = bool(np.isfinite(ka["slope"]) and abs(ka["slope"] - 1) <= max(0.15, 3 * ka["se"]))
    hot = [res[b] for b in ("e0.90_s11_t4000", "e0.90_s12_t4000") if np.isfinite(res[b]["slope"]) and res[b]["se"] > 0]
    D = min((r["rho_n_over_rho"] / r["se"] for r in hot), default=0.0)
    P.emit(D if ok else 0.0, consistent=ok, arms=res,
           note=("known-answer slope at T=0.115: %.3f +- %.3f; " % (ka["slope"], ka["se"])) + "; ".join(f"1-alpha' = {r['slope']:.3f} +- {r['se']:.3f} (rho_n/rho = {r['rho_n_over_rho']:.2f})" for r in hot))


# ---- H04: pair-size law -------------------------------------------------------------------------------------------
def pair_exponent(name, L, rlo=1.4, rhi=6.0):
    t, POS, Q = P.positions(name); dist = []
    for pos, q in zip(POS, Q):
        a, b = pos[q > 0], pos[q < 0]
        if len(a) == 0 or len(b) == 0:
            continue
        dist.append(np.sqrt((mindist(a[:, None, :] - b[None, :, :], L) ** 2).sum(-1)).min(axis=1))
    dist = np.concatenate(dist)
    edges = rlo * 1.2 ** np.arange(0, int(np.log(rhi / rlo) / np.log(1.2)) + 2)
    cnt, _ = np.histogram(dist, edges); ctr = np.sqrt(edges[:-1] * edges[1:]); ok = cnt >= 5
    if ok.sum() < 4:
        return np.nan, np.nan, len(dist)
    y = np.log(cnt[ok] / np.diff(edges)[ok]); x = np.log(ctr[ok]); w = np.sqrt(cnt[ok])
    cf, cov = np.polyfit(x, y, 1, w=w, cov=True)
    return float(-cf[0]), float(np.sqrt(cov[0, 0])), len(dist)


def H04():
    rows = []
    for part in ("C", "C2", "C3"):
        for name in P.run_names(part):
            r = P.record(name)
            if r["class"] != "N":
                continue
            a, se, n = pair_exponent(name, r["L"])
            if np.isfinite(a):
                rows.append({"name": name, "K": r["K"], "a": a, "se": se, "n_pairs": n})
    K = np.array([r["K"] for r in rows]); a = np.array([r["a"] for r in rows])
    cf, cov = np.polyfit(K, a, 1, cov=True); b, sb = float(cf[0]), float(np.sqrt(cov[0, 0]))
    P.emit(abs(b) / sb, consistent=bool(b > 0), slope=b, slope_se=sb, intercept=float(cf[1]), rows=rows,
           note=f"P(r) ~ r^-a on r in [1.4, 6]: a vs K over {len(rows)} runs, slope {b:.2f} +- {sb:.2f} (law: a = K - 1 at the local K; rival: 0), a range {a.min():.1f}-{a.max():.1f}")


# ---- H05: Josephson relation with the torus geometry factor ---------------------------------------------------------
def H05():
    from observables import g1_radial
    from round2 import fit_g1_window
    s = PGPE(N=256, L=128.0)
    Ghat = np.where(s.P & (s.k2 > 0), 1.0 / np.where(s.k2 > 0, s.k2, 1.0), 0.0)
    A = np.fft.ifft2(Ghat).real * s.N ** 2 / s.L ** 2; GT = 2 * np.pi * (A[0, 0] - A)       # ~ ln r + const at small r
    ix = np.fft.fftfreq(s.N, d=1.0 / s.N) * s.dx; RX, RY = np.meshgrid(ix, ix, indexing="ij"); R = np.hypot(RX, RY)
    win = (R >= 8) & (R <= 32)
    rows = []
    for name in P.run_names("C2"):
        r = P.record(name)
        if r["class"] != "N" or not (r["R_L"] <= 1.25 and r["R_T"] <= 1.1 * r["R_L"]):
            continue
        c = np.load(P.R3 / f"{name}_final.npy")
        g = np.fft.ifft2(np.abs(c) ** 2).real; g /= g[0, 0]
        m = win & (g > 0)
        eta_t = float(-np.polyfit(GT[m], np.log(g[m]), 1)[0])
        rr, gg = g1_radial(s, c); eta_n = fit_g1_window(rr, gg, s.L)["eta"]
        rows.append({"name": name, "K": r["K"], "eta_torus_8_32": eta_t, "eta_naive_final": float(eta_n), "eta_blocks": r["eta"],
                     "x_torus": eta_t * r["K"] - 1, "x_naive": float(eta_n) * r["K"] - 1, "x_blocks": r["eta"] * r["K"] - 1})
    xt = np.array([r["x_torus"] for r in rows]); xn = np.array([r["x_blocks"] for r in rows])
    sig = float(xt.std(ddof=1) / np.sqrt(len(xt)))
    P.emit(0.2 / sig, consistent=bool(abs(xt.mean()) <= 3 * sig), x_torus_mean=float(xt.mean()), x_sigma=sig, x_blocks_mean=float(xn.mean()), rows=rows,
           note=f"eta*K - 1 with the torus Green function on r in [8, 32]: {xt.mean():+.3f} +- {sig:.3f} over {len(rows)} admitted L=128 runs (standard window, block mean: {xn.mean():+.3f}); H: 0, rival: +0.2")


# ---- H06: is the box-scale vortex charge one pair, whatever the vortex number? --------------------------------------
def box_charge(name, L):
    t, POS, Q = P.positions(name); k = 2 * np.pi / L
    return float(np.mean([0.5 * sum(abs(np.sum(q * np.exp(1j * k * pos[:, a]))) ** 2 for a in (0, 1)) for pos, q in zip(POS, Q) if len(q)]))


def H06():
    rows = []
    for part in ("C", "C2", "C3"):
        for name in P.run_names(part):
            r = P.record(name)
            rows.append({"name": name, "class": r["class"], "L": r["L"], "n_v": r["n_v"], "Q1": box_charge(name, r["L"]), "ns_over_n": r["ns_over_n"]})
    A = [r for r in rows if r["class"] == "A"]; N = [r for r in rows if r["class"] == "N"]
    x = np.log([r["n_v"] for r in A]); y = np.log([r["Q1"] for r in A])
    cf, cov = np.polyfit(x, y, 1, cov=True); b, sb = float(cf[0]), float(np.sqrt(cov[0, 0]))
    P.emit(1.0 / sb, consistent=bool(abs(b) <= 3 * sb), slope=b, slope_se=sb, Q1_A=[r["Q1"] for r in A], Q1_N=[r["Q1"] for r in N], rows=rows,
           note=f"ln Q1 vs ln N_v over {len(A)} depressed-stiffness runs (N_v {min(r['n_v'] for r in A):.0f}-{max(r['n_v'] for r in A):.0f}): slope {b:+.2f} +- {sb:.2f} (one pair: 0; extensive: 1); Q1 median A {np.median([r['Q1'] for r in A]):.2f} vs N {np.median([r['Q1'] for r in N]):.2f}")


# ---- H07: finite-k dielectric relation beyond the three lowest shells -----------------------------------------------
SHELLS = {5: [(1, 2), (2, 1), (1, -2), (2, -1)], 8: [(2, 2), (2, -2)], 9: [(3, 0), (0, 3)], 10: [(1, 3), (3, 1), (1, -3), (3, -1)],
          13: [(2, 3), (3, 2), (2, -3), (3, -2)], 16: [(4, 0), (0, 4)]}


def H07():
    s = PGPE(N=384, L=192.0); dk = 2 * np.pi / s.L; pts = []
    for name in P.run_names("C3"):
        if left() < 40:
            break
        r = P.record(name); t, POS, Q = P.positions(name)
        acc = {m2: [[], [], []] for m2 in SHELLS}
        for i in range(0, len(t), 2):
            psi = P.snapshot(name, float(t[i])); c = np.fft.fft2(psi) * s.P
            gx = np.fft.ifft2(1j * s.kx * c); gy = np.fft.ifft2(1j * s.ky * c)
            Jx = np.fft.fft2((np.conj(psi) * gx).imag) * s.dx ** 2; Jy = np.fft.fft2((np.conj(psi) * gy).imag) * s.dx ** 2
            pos, q = POS[i], Q[i]
            for m2, vecs in SHELLS.items():
                jl = jt = jv = 0.0
                for (a, b) in vecs:
                    kh = np.array([a, b]) / np.sqrt(m2); JL = kh[0] * Jx[a, b] + kh[1] * Jy[a, b]; JT = kh[0] * Jy[a, b] - kh[1] * Jx[a, b]
                    rho = np.sum(q * np.exp(-1j * dk * (pos @ np.array([a, b], float))))
                    jl += abs(JL) ** 2; jt += abs(JT) ** 2; jv += (2 * np.pi) ** 2 * abs(rho) ** 2 / (m2 * dk ** 2)
                for lst, val in zip(acc[m2], (jl, jt, jv)):
                    lst.append(val / len(vecs))
        for m2 in SHELLS:
            nrm = r["T"] * s.L ** 2
            pts.append({"name": name, "class": r["class"], "m2": m2, "R_L": float(np.mean(acc[m2][0]) / nrm), "R_T": float(np.mean(acc[m2][1]) / nrm), "R_Tv": float(np.mean(acc[m2][2]) / nrm)})
    x = np.array([p["R_Tv"] for p in pts]); y = np.array([p["R_T"] for p in pts]); n = len(pts)
    rr = float(np.corrcoef(x, y)[0, 1]); cf = np.polyfit(x, y, 1)
    P.emit(float(np.arctanh(min(rr, 0.999999)) * np.sqrt(max(n - 3, 1))) if rr > 0 else 0.0, consistent=bool(rr > 0), pearson=rr, n=n, slope=float(cf[0]), floor=float(cf[1]), pts=pts,
           note=f"shells |m|^2 = 5..16 only (none used before): R_T vs vortex-only R_T over {n} (run, shell) points, r = {rr:.3f}, slope {cf[0]:.2f}, floor {cf[1]:.2f}")


# ---- H08: 5-minute simulation -- winding slips of an imposed supercurrent at L = 32 ---------------------------------
def H08():
    from run_r4 import boost, torus_winding
    s = PGPE(N=64, L=32.0); c0 = np.load(PG / "r2/III_L32_e1.20_s11_final.npy")
    t1 = time.time(); s.run(c0.copy(), 1.0); per = time.time() - t1
    t_arm = max(10.0, min(120.0, (left() - 30) / 3 / per)); res = {}
    for w0 in (1, 2, 3):
        c = boost(s, c0, w0); W = [torus_winding(s, c)[0]]; tt = 0.0
        while tt < t_arm and left() > 15:
            c = s.run(c, 1.0); tt += 1.0; W.append(torus_winding(s, c)[0])
        W = np.array(W); res[w0] = {"t": tt, "slips": int(np.sum(np.abs(np.diff(W)))), "W_first": int(W[0]), "W_last": int(W[-1]), "v": 2 * np.pi * w0 / s.L}
    n1, n3 = res[1]["slips"] / max(res[1]["t"], 1), res[3]["slips"] / max(res[3]["t"], 1)
    D = (res[3]["slips"] - res[1]["slips"] * res[3]["t"] / max(res[1]["t"], 1)) / np.sqrt(res[3]["slips"] + res[1]["slips"] + 1)
    P.emit(max(float(D), 0.0), consistent=True, arms=res, sec_per_unit=per,
           note=f"L=32, T~0.79 (K~5.4): slips at windings 1/2/3 = {res[1]['slips']}/{res[2]['slips']}/{res[3]['slips']} in {res[1]['t']:.0f}/{res[2]['t']:.0f}/{res[3]['t']:.0f} time units (final W {res[1]['W_last']}/{res[2]['W_last']}/{res[3]['W_last']})")


# ---- H09: cutoff law of the classical-field BKT point (retrodiction; inputs known before registration) --------------
def H09():
    v = json.loads((PG / "r2_verdicts.json").read_text())
    T64 = v["II"]["crossing"]["T_BKT"]; T32 = v["III"]["crossing_L32"]["T_BKT"]
    kcut = 0.5 * np.pi / 0.5; Ec = kcut ** 2 / 2; lo, hi = 0.3, 2.0
    for _ in range(80):                                                # solve 2 pi / T = ln(380/g) + ln(E_cut/T), g = 1
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if 2 * np.pi / mid > np.log(380.0) + np.log(Ec / mid) else (lo, mid)
    TH = 0.5 * (lo + hi); xH = 2 * np.pi / TH; x = 2 * np.pi / T64; xr = np.log(380.0)

    def tpred(kc):
        a, b = 0.3, 2.0
        for _ in range(80):
            m_ = 0.5 * (a + b)
            a, b = (m_, b) if 2 * np.pi / m_ > np.log(380.0) + np.log(kc ** 2 / 2 / m_) else (a, m_)
        return 0.5 * (a + b)
    sig = x * abs(T32 - T64) / T64                                     # finite-size systematic taken as the full L = 32 -> 64 shift
    P.emit(abs(xH - xr) / sig, consistent=bool(abs(x - xH) <= 3 * sig), T_pred=TH, T64=T64, T32=T32, x_pred=xH, x_meas=x, x_rival=xr, sigma=sig,
           predictions={"kcut=2pi/3": tpred(2 * np.pi / 3), "kcut=2pi": tpred(2 * np.pi)},
           note=f"n lambda^2 at BKT: predicted {xH:.2f} (T = {TH:.3f}), measured {x:.2f} (L=64; L=32 gives {2 * np.pi / T32:.2f}), no-UV-log rival {xr:.2f}; sigma = L=32->64 shift = {sig:.2f}. RETRODICTION: inputs were known before registration")


# ---- H10: two sound branches in the density dynamic structure factor at L = 192 -------------------------------------
def H10():
    N, L = 384, 192.0; dk = 2 * np.pi / L
    vecs = [(2, 0), (0, 2), (2, 2), (2, -2), (3, 0), (0, 3), (4, 0), (0, 4)]
    cgrid = np.linspace(0.05, 2.0, 196); out = []
    for name in P.run_names("C3"):
        if left() < 40:
            break
        r = P.record(name); ts = P.snapshot_times(name); dt = ts[1] - ts[0]
        series = np.zeros((len(ts), len(vecs)), complex)
        for i, t in enumerate(ts):
            rk = np.fft.fft2(np.abs(P.snapshot(name, t)) ** 2)
            series[i] = [rk[a, b] for a, b in vecs]
        series -= series.mean(axis=0); w = np.hanning(len(ts))[:, None]
        F = np.abs(np.fft.fft(series * w, axis=0)) ** 2; om = 2 * np.pi * np.fft.fftfreq(len(ts), d=dt)
        S = np.zeros_like(cgrid)
        for j, (a, b) in enumerate(vecs):
            k = dk * np.hypot(a, b); pos = om > 0
            spec = F[pos, j] + F[(-om[pos] / (om[1] - om[0])).round().astype(int) % len(ts), j]      # fold +-omega
            S += np.interp(cgrid, om[pos] / k, spec / spec.sum(), left=0.0, right=0.0)
        i1 = int(np.argmax(S)); c1 = float(cgrid[i1])
        lowband = (cgrid >= 0.15) & (cgrid <= 0.7 * c1)
        if lowband.sum() < 8:
            out.append({"name": name, "class": r["class"], "c1": c1, "z2": 0.0}); continue
        seg = S[lowband]; i2 = int(np.argmax(seg)); bg = float(np.median(seg)); mad = float(1.4826 * np.median(np.abs(seg - bg))) or 1e-12
        out.append({"name": name, "class": r["class"], "T": r["T"], "ns_over_n": r["ns_over_n"], "c1": c1, "c2": float(cgrid[lowband][i2]), "z2": float((seg[i2] - bg) / mad)})
    z = np.array([o["z2"] for o in out])
    P.emit(float(np.median(z)), consistent=True, runs=out,
           note="upper branch c1 = " + ", ".join(f"{o['c1']:.2f}" for o in out) + "; candidate lower branch c2 = " + ", ".join(f"{o.get('c2', float('nan')):.2f}(z={o['z2']:.1f})" for o in out))


if __name__ == "__main__":
    {"H01": H01, "H02": H02, "H03": H03, "H04": H04, "H05": H05, "H06": H06, "H07": H07, "H08": H08, "H09": H09, "H10": H10}[sys.argv[1]]()
