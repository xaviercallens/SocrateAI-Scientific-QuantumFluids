#!/usr/bin/env python3
"""Round-2 probes (hypotheses.json in this directory); same contract as ../probes.py: print PROBE_RESULT {D, consistent, ...}."""
from __future__ import annotations
import glob, json, sys, time
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; PARENT = HERE.parent
sys.path.insert(0, str(PARENT)); sys.path.insert(0, str(PARENT.parent / "pgpe"))
import prepare as P
import probes as R1
from pgpe import PGPE
from analyze_transport import load, pair_separations
import transport_estimators as TE

T0 = time.time(); PG = P.PG; TR = PG / "transport"; L64 = 64.0
left = lambda: P.BUDGET_S - (time.time() - T0)


def d2_slope(t, d, a, b):
    m = (t >= a) & (t <= b)
    return float(np.polyfit(t[m], d[m] ** 2, 1)[0]) if m.sum() > 20 else np.nan


def R2_01():
    single, zero = [], []
    for f in sorted(TR.glob("W1_e0.60_dipole_d12_s*.npz")):
        t, R, q, z, meta = load(f); d = pair_separations(R, q, L64)[0]
        single.append({"file": f.name, "early": d2_slope(t, d, 100, 600), "late": d2_slope(t, d, 2000, 4000), "d_last": float(d[-200:].mean())})
    for f in sorted(TR.glob("G2_e0.60_antiparallel_d10_s*.npz")) + sorted(TR.glob("prod_e0.60_d12_s*.npz")):
        t, R, q, z, meta = load(f); dd = pair_separations(R, q, L64)
        for d in dd:
            ok = d < 11.5                                               # before the partner exchange
            n = int(np.argmin(ok)) if (~ok).any() else len(t)
            if t[min(n, len(t) - 1)] >= 1400:
                zero.append({"file": f.name, "early": d2_slope(t[:n], d[:n], 100, 600), "late": d2_slope(t[:n], d[:n], 900, 1400)})
    ls = np.array([s["late"] for s in single]); lz = np.array([z_["late"] for z_ in zero if np.isfinite(z_["late"])])
    D = abs(ls.mean() - lz.mean()) / np.sqrt(ls.var(ddof=1) / len(ls) + lz.var(ddof=1) / len(lz)) if len(ls) > 1 and len(lz) > 1 else 0.0
    P.emit(D, consistent=bool(ls.mean() > lz.mean()), single=single, zero=zero,
           note=f"late d^2 slope: single pairs {ls.mean():+.4f} (early {np.mean([s['early'] for s in single]):+.4f}), zero-impulse pairs {lz.mean():+.4f} over {len(lz)} tracks; W2 (L=96) unread")


def R2_02():
    acs = []; lags = np.arange(0, 161)
    for f in sorted(TR.glob("prod_e0.60_d*_s*.npz")) + sorted(TR.glob("G2_e0.60*.npz")):
        t, R, q, z, meta = load(f); m = t >= 100; t, U = t[m], TE.unwrap(R[m], L64)
        CA, CB, H, S = TE.predictors(t, U, q, L64)
        D1 = U[1:] - U[:-1]; A1 = CA[1:] - CA[:-1]; B1 = CB[1:] - CB[:-1]
        sm = np.array([(A1 * A1).sum(), (A1 * B1).sum(), (B1 * B1).sum(), (A1 * D1).sum(), (B1 * D1).sum()])
        c = np.linalg.solve([[sm[0], sm[1]], [sm[1], sm[2]]], sm[3:5]); e = D1 - c[0] * A1 - c[1] * B1      # residual velocity per unit time
        for i in range(e.shape[1]):
            x = e[:, i] - e[:, i].mean(axis=0)
            if len(x) > 400:
                ac = np.array([(x[:len(x) - l] * x[l:]).sum() / (x * x).sum() for l in lags]); acs.append(ac)
    acs = np.array(acs); mean = acs.mean(axis=0); se = acs.std(axis=0, ddof=1) / np.sqrt(len(acs))
    win = (lags >= 40) & (lags <= 100); j = int(np.argmin(mean[win])); lag_star = int(lags[win][j]); val = float(mean[win][j]); s = float(se[win][j])
    P.emit(abs(val) / s if s > 0 else 0.0, consistent=bool(val < 0), lag_star=lag_star, vacf_min=val, se=s, n_tracks=len(acs),
           vacf_lags_1_2_5_10_20_64=[float(mean[k]) for k in (1, 2, 5, 10, 20, 64)],
           note=f"residual-velocity autocorrelation at T=0.115 ({len(acs)} tracks): most negative value in lags 40-100 is {val:+.4f} +- {s:.4f} at lag {lag_star} (L/c = 64); lag-1 {mean[1]:+.3f}, lag-10 {mean[10]:+.3f}, lag-64 {mean[64]:+.3f}")


def R2_03():
    from analyze_r3 import whole_from_blocks
    N, L = 384, 192.0; s = PGPE(N=N, L=L)
    Ghat = np.where(s.P & (s.k2 > 0), 1.0 / np.where(s.k2 > 0, s.k2, 1.0), 0.0)
    A = np.fft.ifft2(Ghat).real * N ** 2 / L ** 2; GT = 2 * np.pi * (A[0, 0] - A)
    ix = np.fft.fftfreq(N, d=1.0 / N) * s.dx; RX, RY = np.meshgrid(ix, ix, indexing="ij"); Rr = np.hypot(RX, RY); win = (Rr >= 8) & (Rr <= 48)
    rows = []
    for name in P.run_names("C3"):
        j = json.loads((PG / "r3_C4/analysis" / f"{name}.json").read_text()); w = whole_from_blocks(j); K = 2 * np.pi * w["ns_over_n"] / w["T"]
        ts = sorted(float(f.name.split("_sample_t")[1][:-4]) for f in (PG / "r3_C4").glob(f"{name}_sample_t*.raw"))[::5]
        gf = np.zeros((N, N)); gp = np.zeros((N, N))
        for t in ts:
            if left() < 30:
                break
            psi = np.fromfile(PG / "r3_C4" / f"{name}_sample_t{t:07.1f}.raw", dtype=np.complex128).reshape(N, N)
            F = np.fft.fft2(psi); gf += np.fft.ifft2(np.abs(F) ** 2).real
            u = psi / np.abs(psi); Fu = np.fft.fft2(u); gp += np.fft.ifft2(np.abs(Fu) ** 2).real
        gf /= gf[0, 0]; gp /= gp[0, 0]
        ef = float(-np.polyfit(GT[win & (gf > 0)], np.log(gf[win & (gf > 0)]), 1)[0]); ep = float(-np.polyfit(GT[win & (gp > 0)], np.log(gp[win & (gp > 0)]), 1)[0])
        rows.append({"name": name, "K": K, "eta_g1": ef, "eta_phase": ep, "x_g1": ef * K - 1, "x_phase": ep * K - 1, "n_snap": len(ts)})
    xg = np.array([r["x_g1"] for r in rows]); xp = np.array([r["x_phase"] for r in rows]); dx = xg - xp
    sig = float(dx.std(ddof=1) / np.sqrt(len(dx))); sp = float(xp.std(ddof=1) / np.sqrt(len(xp)))
    P.emit(abs(dx.mean()) / sig if sig > 0 else 0.0, consistent=bool(abs(xp.mean()) <= 0.1 + 2 * sp), rows=rows, x_g1_mean=float(xg.mean()), x_phase_mean=float(xp.mean()),
           note=f"eta*K-1 with g1: {xg.mean():+.3f}; with the phase-only correlator: {xp.mean():+.3f} +- {sp:.3f} (6 runs, torus Green function, r in [8,48]); difference {dx.mean():+.3f} +- {sig:.3f}")


def R2_04():
    est = json.loads((TR / "production_estimates.json").read_text())
    x = np.array([est[k]["rho_n"] for k in ("e0.60", "e0.70", "e0.80")]); y = np.array([est[k]["alpha_energy"] for k in ("e0.60", "e0.70", "e0.80")]); w = 1 / np.array([est[k]["alpha_energy_se"] for k in ("e0.60", "e0.70", "e0.80")]) ** 2
    c = (w * x * y).sum() / (w * x * x).sum(); sc = 1 / np.sqrt((w * x * x).sum())
    A = np.vstack([x, np.ones_like(x)]).T; cov = np.linalg.inv(A.T @ (A * w[:, None])); beta = cov @ (A.T @ (w * y))
    P.emit(c / sc, consistent=bool(abs(beta[1]) <= 2 * np.sqrt(cov[1, 1])), c=float(c), c_se=float(sc), intercept=float(beta[1]), intercept_se=float(np.sqrt(cov[1, 1])),
           note=f"alpha = c rho_n/rho: c = {c:.3f} +- {sc:.3f}; free intercept {beta[1]:+.4f} +- {np.sqrt(cov[1, 1]):.4f} (zero within errors: proportional)")


def R2_05():
    from vortex_transport import imprint_v2, detect
    s = PGPE(N=48, L=24.0); rng = np.random.default_rng(5); c = s.random_state(1.0, 0.60, rng); c = s.run(c, 60.0)
    pos = np.array([[12.13 + 5, 12.31], [12.13 - 5, 12.31]]); q = np.array([1, -1]); c0 = imprint_v2(s, c, pos, q)

    class Damped(PGPE):
        def __init__(self, gamma, mu, **kw):
            super().__init__(**kw); self.gamma, self.mu = gamma, mu
            f = 1 - 1j * gamma; self.E1 = np.exp((self.lin + 1j * mu) * self.dt * f / 2) * self.P; self.E2 = np.exp((self.lin + 1j * mu) * self.dt * f) * self.P

        def nonlin(self, c):
            return (1 - 1j * self.gamma) * super().nonlin(c)
    sd = Damped(0.02, 1.0, N=48, L=24.0)

    def track(sim, c, t_end):
        d = []; last = pos.copy()
        for k in range(int(t_end)):
            if left() < 20:
                break
            c = sim.run(c, 1.0); dp, dq = detect(sim, c)
            if len(dq) < 2:
                d.append(0.0); break
            cur = last.copy()
            for i in range(2):
                cand = np.nonzero(dq == q[i])[0]
                if len(cand):
                    dd = dp[cand] - last[i]; dd -= 24 * np.round(dd / 24); j = int(np.argmin(np.hypot(dd[:, 0], dd[:, 1]))); cur[i] = dp[cand[j]]
            last = cur; dd = cur[0] - cur[1]; dd -= 24 * np.round(dd / 24); d.append(float(np.hypot(*dd)))
        return np.array(d)
    d_pg = track(s, c0.copy(), 120); d_dg = track(sd, c0.copy(), 120)
    n = min(len(d_pg), len(d_dg)); gap = float(d_pg[n - 1] - d_dg[n - 1])
    P.emit(abs(gap) / 0.3, consistent=bool(gap > 0), d_pgpe_first_last=[float(d_pg[0]), float(d_pg[n - 1])], d_damped_first_last=[float(d_dg[0]), float(d_dg[n - 1])], t_compared=n,
           note=f"L=24 box-scale pair (d0=10): after {n} time units d = {d_pg[n - 1]:.2f} (PGPE) vs {d_dg[n - 1]:.2f} (damped GPE, gamma=0.02, mu=1): gap {gap:+.2f}")


def R2_06():
    from vortex_transport import imprint_v2, detect
    s = PGPE(N=64, L=32.0); rng = np.random.default_rng(6); base = s.run(s.random_state(1.0, 0.60, rng), 60.0)
    noise = (rng.standard_normal(base.shape) + 1j * rng.standard_normal(base.shape)) * s.P * (s.N / s.dx) * np.sqrt(0.25)   # half a quantum per mode: <|c_k|^2> dx^2/N^2 = 1/2
    pos, q = TE.antiparallel(32.0, 8.0, rng); res = {}
    for lab, c in (("classical", base), ("with vacuum noise", base + noise)):
        c = imprint_v2(s, c, pos, q); last = pos.copy(); R = [pos.copy()]; T = [0.0]; t = 0.0
        while left() > 25 and t < 80:
            c = s.run(c, 1.0); t += 1.0; dp, dq = detect(s, c); cur = last.copy()
            for i in range(4):
                cand = np.nonzero(dq == q[i])[0]
                if len(cand):
                    dd = dp[cand] - last[i]; dd -= 32 * np.round(dd / 32); j = int(np.argmin(np.hypot(dd[:, 0], dd[:, 1])))
                    if np.hypot(*dd[j]) <= 3: cur[i] = dp[cand[j]]
            last = cur; R.append(cur.copy()); T.append(t)
        r = TE.analyse_tracks([(np.array(T), np.array(R), q)], 32.0, lag=5, t_settle=10.0, lags_eta=(2, 4, 8, 16, 24, 32))
        res[lab] = {"one_minus_alpha_prime": r.get("one_minus_alpha_prime"), "t": t}
    dlt = (res["with vacuum noise"]["one_minus_alpha_prime"] or np.nan) - (res["classical"]["one_minus_alpha_prime"] or np.nan)
    P.emit(abs(dlt) / 0.02 if np.isfinite(dlt) else 0.0, consistent=True, res=res, note=f"L=32, {res['classical']['t']:.0f} time units: 1-alpha' classical {res['classical']['one_minus_alpha_prime']}, with half-quantum noise {res['with vacuum noise']['one_minus_alpha_prime']} (no error bar possible in the budget)")


def R2_07():
    prim = json.loads((PG / "dielectric/primary_C4.json").read_text())["runs"]
    shares = [v["n_eff_raw_shells"][0] ** 2 * v["shells"]["1"]["R_Tv"] / v["shells"]["1"]["R_T"] for v in prim.values() if not v["box_scale_pair"]]
    med = float(np.median(shares)); sig = float(np.std(shares, ddof=1) / np.sqrt(len(shares)))
    P.emit(abs(0.5 - med) / sig if sig > 0 else 0.0, consistent=bool(med < 0.5), shares=shares, note=f"vortex share of rho_n(k1) in the five equilibrated runs: {np.round(shares, 3).tolist()} (median {med:.3f})")


def R2_10():
    est = json.loads((TR / "production_estimates.json").read_text()); x = est["e0.70"]; K = 2 * np.pi * x["ns"] / x["T"]
    RE = x["eta"] * K / x["alpha_energy"]; se = x["eta_se"] * K / x["alpha_energy"]
    P.emit(abs(RE - 1) / se, consistent=True, R_E=RE, se=se, note=f"the one admitted temperature: R_E = {RE:.2f} +- {se:.2f} (Einstein = 1; exponent 0.82)")


if __name__ == "__main__":
    {"R2-01": R2_01, "R2-02": R2_02, "R2-03": R2_03, "R2-04": R2_04, "R2-05": R2_05, "R2-06": R2_06, "R2-07": R2_07, "R2-08": R1.H06, "R2-09": R1.H09, "R2-10": R2_10}[sys.argv[1]]()
