#!/usr/bin/env python3
"""Mode-by-mode test of the finite-k dielectric relation (docs/designs/PGPE_DIELECTRIC_PREREG.md):
    J_T(k) = n_eff X(k) + phonon part,      X(k) = -2 pi i rho_q(k)/|k|,   rho_q(k) = sum_j q_j exp(-i k.r_j)
(a point vortex of charge q has stream function -q ln r, so its Fourier velocity is 2 pi i q (k_y, -k_x)/k^2 and
its transverse component k_hat x v is -2 pi i q/|k|; lean_src/MatchingScreening.lean `pointVortex_norm_sq`).

    .venv/bin/python exploration/pgpe/dielectric_modes.py DG1      # T = 0 known-answer gate
    .venv/bin/python exploration/pgpe/dielectric_modes.py DG2      # thermal vortex-free state + imprint
    .venv/bin/python exploration/pgpe/dielectric_modes.py RUNS <dir> <tag>   # per-run analysis of saved snapshots
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from round2 import imprint
from vortex_transport import detect

ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / "data/generated/pgpe/dielectric"
SHELLS = {1: [(1, 0), (0, 1)], 2: [(1, 1), (1, -1)], 4: [(2, 0), (0, 2)], 5: [(1, 2), (2, 1), (1, -2), (2, -1)], 8: [(2, 2), (2, -2)],
          9: [(3, 0), (0, 3)], 10: [(1, 3), (3, 1), (1, -3), (3, -1)], 13: [(2, 3), (3, 2), (2, -3), (3, -2)], 16: [(4, 0), (0, 4)]}


def mode_amplitudes(s: PGPE, c: np.ndarray, pos: np.ndarray, q: np.ndarray):
    """{m2: (J_T array, X array)} over the vectors of each shell, for one field c (Fourier modes) and its vortices."""
    psi = np.fft.ifft2(c); gx = np.fft.ifft2(1j * s.kx * c); gy = np.fft.ifft2(1j * s.ky * c)
    Jx = np.fft.fft2((np.conj(psi) * gx).imag) * s.dx ** 2; Jy = np.fft.fft2((np.conj(psi) * gy).imag) * s.dx ** 2
    dk = 2 * np.pi / s.L; out = {}
    for m2, vecs in SHELLS.items():
        JT, X = [], []
        for (a, b) in vecs:
            kn = np.sqrt(m2); JT.append((a * Jy[a, b] - b * Jx[a, b]) / kn)
            rho = np.sum(q * np.exp(-1j * dk * (pos @ np.array([a, b], float)))) if len(q) else 0.0
            X.append(-2j * np.pi * rho / (kn * dk))
        out[m2] = (np.array(JT), np.array(X))
    return out


def fit(acc, norm):
    """acc: {m2: (JT (ns, nv), X (ns, nv))}. Per shell: n_eff (complex LS), coherence, residual and total power / norm."""
    res = {}
    for m2, (JT, X) in acc.items():
        JT, X = np.asarray(JT).ravel(), np.asarray(X).ravel()
        sxx = float((np.abs(X) ** 2).sum()); sjj = float((np.abs(JT) ** 2).sum()); sjx = complex((JT * np.conj(X)).sum())
        n_eff = sjx / sxx if sxx > 0 else complex("nan")
        res[m2] = {"n_eff_re": n_eff.real, "n_eff_im": n_eff.imag, "coherence": abs(sjx) ** 2 / (sjj * sxx) if sxx > 0 and sjj > 0 else float("nan"),
                   "R_T": sjj / len(JT) / norm, "R_Tv": sxx / len(X) / norm, "R_res": float((np.abs(JT - n_eff * X) ** 2).mean()) / norm, "n": int(len(JT))}
    return res


def neutral_pairs(L: float, n_half: int, rng, dmin=4.0, dmax=10.0):
    """2 n_half pairs with sum q r = 0 exactly (each random pair has a twin of opposite dipole moment elsewhere),
    so the theta-function phase is single-valued with zero winding."""
    pos, q = [], []
    for _ in range(n_half):
        d = rng.uniform(dmin, dmax); ang = rng.uniform(0, 2 * np.pi); dv = 0.5 * d * np.array([np.cos(ang), np.sin(ang)])
        for sgn in (1, -1):
            c0 = rng.uniform(0, L, 2); pos += [c0 + sgn * dv, c0 - sgn * dv]; q += [1, -1]
    return np.mod(np.array(pos), L), np.array(q)


def gate(kind: str):
    OUT.mkdir(parents=True, exist_ok=True); s = PGPE(N=128, L=64.0); rng = np.random.default_rng(20261005)
    if kind == "DG1":
        c0 = np.zeros((128, 128), complex); c0[0, 0] = 128 ** 2; T, f_known = 1.0, 0.0      # T only normalises powers here
    else:
        c0 = np.load(ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000_final.npy")
        b = json.loads((ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000.json").read_text()); T, f_known = b["T"], 1 - b["ns_over_n"]
    norm = T * s.L ** 2
    acc0 = {m2: ([], []) for m2 in SHELLS}; acc20 = {m2: ([], []) for m2 in SHELLS}; acc_det = {m2: ([], []) for m2 in SHELLS}; ndet = []
    for i in range(20):
        pos, q = neutral_pairs(s.L, 6, rng); c = imprint(s, c0, pos, q)
        for m2, (JT, X) in mode_amplitudes(s, c, pos, q).items():               # known positions
            acc0[m2][0].append(JT); acc0[m2][1].append(X)
        dp, dq = detect(s, c); ndet.append(len(dq))
        for m2, (JT, X) in mode_amplitudes(s, c, dp, dq).items():               # detected positions (the real pipeline)
            acc_det[m2][0].append(JT); acc_det[m2][1].append(X)
        if i < 3:
            c = s.run(c, 20.0); dp, dq = detect(s, c)
            for m2, (JT, X) in mode_amplitudes(s, c, dp, dq).items():
                acc20[m2][0].append(JT); acc20[m2][1].append(X)
    r0, rd, r20 = fit(acc0, norm), fit(acc_det, norm), fit(acc20, norm)
    low = [1, 2]
    ne = float(np.mean([rd[m]["n_eff_re"] for m in low])); co = float(np.min([rd[m]["coherence"] for m in low]))
    if kind == "DG1":
        chk = {"n_eff_1_pm_0.05": abs(ne - 1) <= 0.05, "coherence_ge_0.95": co >= 0.95}
    else:
        base = fit({m2: ([mode_amplitudes(s, c0, np.zeros((0, 2)), np.zeros(0))[m2][0]], [np.zeros(len(SHELLS[m2]))]) for m2 in SHELLS}, norm)
        fres = float(np.mean([rd[m]["R_res"] for m in low]))
        chk = {"n_eff_1_minus_f_pm_0.07": abs(ne - (1 - f_known)) <= 0.07, "residual_equals_phonon_fraction_30pct": abs(fres / f_known - 1) <= 0.30}
    res = {"kind": kind, "T": T, "f_known": f_known, "known_positions_t0": r0, "detected_positions_t0": rd, "detected_positions_t20": r20,
           "n_detected": ndet, "n_eff_low_shells": ne, "min_coherence_low_shells": co, "checks": chk, "PASS": bool(all(chk.values()))}
    if kind == "DG2":
        res["base_state_R_T"] = {m: base[m]["R_T"] for m in base}; res["residual_low_shells"] = fres
    (OUT / f"{kind}.json").write_text(json.dumps(res, indent=1, default=float))
    for lab, r in (("known pos, t=0", r0), ("detected, t=0", rd), ("detected, t=20", r20)):
        print(lab, {m: (round(r[m]["n_eff_re"], 3), round(r[m]["n_eff_im"], 3), round(r[m]["coherence"], 3), round(r[m]["R_res"], 4)) for m in r})
    print("detected vortices per configuration (24 imprinted):", ndet)
    print("checks", chk, "->", kind, "PASS" if res["PASS"] else "FAIL")


def gate_relaxed(kind: str, t_relax: float = 60.0, n_cfg: int = 6):
    """Amendment D-A1: the relation is tested on configurations evolved for t_relax after the imprint
    (new random configurations: a different seed stream from the first D-G1 run)."""
    OUT.mkdir(parents=True, exist_ok=True); s = PGPE(N=128, L=64.0); rng = np.random.default_rng(2026100560)
    if kind == "DG1p":
        c0 = np.zeros((128, 128), complex); c0[0, 0] = 128 ** 2; T, f_known = 1.0, 0.0
    else:
        c0 = np.load(ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000_final.npy")
        b = json.loads((ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000.json").read_text()); T, f_known = b["T"], 1 - b["ns_over_n"]
    norm = T * s.L ** 2; acc = {m2: ([], []) for m2 in SHELLS}; ndet = []
    for i in range(n_cfg):
        pos, q = neutral_pairs(s.L, 6, rng); c = s.run(imprint(s, c0, pos, q), t_relax); dp, dq = detect(s, c); ndet.append(len(dq))
        for m2, (JT, X) in mode_amplitudes(s, c, dp, dq).items():
            acc[m2][0].append(JT); acc[m2][1].append(X)
        print("configuration", i, "detected", len(dq), flush=True)
    r = fit(acc, norm); low = [1, 2]
    ne = float(np.mean([r[m]["n_eff_re"] for m in low])); co = float(np.min([r[m]["coherence"] for m in low])); fres = float(np.mean([r[m]["R_res"] for m in low]))
    if kind == "DG1p":
        chk = {"n_eff_1_pm_0.05": abs(ne - 1) <= 0.05, "coherence_ge_0.95": co >= 0.95}
    else:
        chk = {"n_eff_1_minus_f_pm_0.07": abs(ne - (1 - f_known)) <= 0.07, "residual_equals_phonon_fraction_30pct": abs(fres / f_known - 1) <= 0.30}
    res = {"kind": kind, "t_relax": t_relax, "T": T, "f_known": f_known, "shells": r, "n_detected": ndet, "n_eff_low_shells": ne,
           "min_coherence_low_shells": co, "residual_low_shells": fres, "checks": chk, "PASS": bool(all(chk.values()))}
    (OUT / f"{kind}.json").write_text(json.dumps(res, indent=1, default=float))
    print({m: (round(r[m]["n_eff_re"], 3), round(r[m]["n_eff_im"], 3), round(r[m]["coherence"], 3), round(r[m]["R_res"], 4)) for m in r})
    print("n_eff(low shells)", round(ne, 3), "coherence", round(co, 3), "residual", round(fres, 4), "f_known", round(f_known, 4))
    print("checks", chk, "->", kind, "PASS" if res["PASS"] else "FAIL")


# ---- amendment D-A2: Bernoulli form factor of a pair, matched pair sizes, gates D-G1'' and D-G2'' ----------------
MU_B_D = np.array([1.5, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 1e9])
MU_B = np.array([0.688, 0.737, 0.810, 0.858, 0.891, 0.913, 0.942, 0.958, 0.968, 0.980, 0.986, 1.0])
#   static calculation (single Bernoulli-imprinted pair at T = 0, field momentum / (2 pi n d)), reproduced by mu_B_table()


def mu_B(d):
    return np.interp(d, MU_B_D[:-1], MU_B[:-1], left=MU_B[0], right=MU_B[-2])


def mu_B_table():
    from vortex_transport import imprint_v2, momentum
    s = PGPE(N=128, L=64.0); c0 = np.zeros((128, 128), complex); c0[0, 0] = 128 ** 2; out = {}
    for d in MU_B_D[:-1]:
        pos = np.array([[30.13 + d / 2, 20.31], [30.13 - d / 2, 20.31]]); c = imprint_v2(s, c0, pos, np.array([1, -1]))
        out[float(d)] = float(np.hypot(*momentum(s, c)) / (2 * np.pi * d))
    return out


def matched_sizes(pos, q, L):
    """Pair sizes from the minimum-cost matching of + to - vortices (minimum-image distances)."""
    from scipy.optimize import linear_sum_assignment
    a, b = pos[q > 0], pos[q < 0]
    if len(a) == 0 or len(b) == 0:
        return np.zeros(0)
    d = a[:, None, :] - b[None, :, :]; d -= L * np.round(d / L); C = np.sqrt((d ** 2).sum(-1))
    ri, ci = linear_sum_assignment(C)
    return C[ri, ci]


def fixed_size_pairs(L, n_half, d, rng, min_sep=None):
    """2 n_half pairs of the same size d (twins of opposite moment), every vortex at least min_sep from every
    vortex of another pair."""
    min_sep = d if min_sep is None else min_sep
    for _ in range(10000):
        pos, q = [], []
        for _h in range(n_half):
            ang = rng.uniform(0, 2 * np.pi); dv = 0.5 * d * np.array([np.cos(ang), np.sin(ang)])
            for sgn in (1, -1):
                c0 = rng.uniform(0, L, 2); pos += [c0 + sgn * dv, c0 - sgn * dv]; q += [1, -1]
        pos = np.mod(np.array(pos), L); ok = True
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                if j == i + 1 and i % 2 == 0:
                    continue
                dd = pos[i] - pos[j]; dd -= L * np.round(dd / L)
                if np.hypot(*dd) < min_sep:
                    ok = False
        if ok:
            return pos, np.array(q)
    raise RuntimeError("could not place the pairs")


def gate_formfactor(kind: str, t_relax: float = 30.0, n_cfg: int = 4):
    from vortex_transport import imprint_v2
    OUT.mkdir(parents=True, exist_ok=True); s = PGPE(N=128, L=64.0); rng = np.random.default_rng(202610052)
    if kind == "DG1pp":
        c0 = np.zeros((128, 128), complex); c0[0, 0] = 128 ** 2; T, f_known, sizes, tol = 1.0, 0.0, (5.0, 8.0, 14.0), 0.03
    else:
        c0 = np.load(ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000_final.npy")
        b = json.loads((ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000.json").read_text()); T, f_known, sizes, tol = b["T"], 1 - b["ns_over_n"], (10.0,), 0.05
    norm = T * s.L ** 2; out = {}; ok_all = True
    base = fit({m2: ([mode_amplitudes(s, c0, np.zeros((0, 2)), np.zeros(0))[m2][0]], [np.zeros(len(SHELLS[m2]))]) for m2 in SHELLS}, norm)
    for d in sizes:
        acc = {m2: ([], []) for m2 in SHELLS}; num = den = 0.0; ndet = []
        for i in range(n_cfg):
            pos, q = fixed_size_pairs(s.L, 2, d, rng, min_sep=max(d, 8.0)); c = s.run(imprint_v2(s, c0, pos, q), t_relax)
            dp, dq = detect(s, c); ndet.append(len(dq)); ds = matched_sizes(dp, dq, s.L); num += float((mu_B(ds) * ds ** 2).sum()); den += float((ds ** 2).sum())
            for m2, (JT, X) in mode_amplitudes(s, c, dp, dq).items():
                acc[m2][0].append(JT); acc[m2][1].append(X)
        r = fit(acc, norm); low = [1, 2]
        ne = float(np.mean([r[m]["n_eff_re"] for m in low])); co = float(np.min([r[m]["coherence"] for m in low])); fres = float(np.mean([r[m]["R_res"] for m in low]))
        M = num / den; pred = (1 - f_known) * M; chk = {"n_eff_matches_prediction": abs(ne - pred) <= tol, "coherence_ge_0.95": co >= 0.95}
        if kind == "DG2pp":
            fb = float(np.mean([base[m]["R_T"] for m in low])); chk["residual_within_[0.7,2.0]_of_base"] = 0.7 <= fres / fb <= 2.0
            out[str(d)] = {"base_R_T_low": fb}
        out.setdefault(str(d), {}).update({"n_eff": ne, "M": M, "predicted": pred, "coherence": co, "residual": fres, "n_detected": ndet, "shells": r, "checks": chk})
        ok_all = ok_all and all(chk.values())
        print(f"d = {d}: n_eff = {ne:.3f}, predicted (1-f) M = {pred:.3f} (M = {M:.3f}), coherence {co:.3f}, residual {fres:.4f}, detected {ndet}, checks {chk}", flush=True)
    res = {"kind": kind, "T": T, "f_known": f_known, "sets": out, "PASS": bool(ok_all)}
    (OUT / f"{kind}.json").write_text(json.dumps(res, indent=1, default=float)); print("->", kind, "PASS" if ok_all else "FAIL")


def analyse_runs(rust_dir: Path, analysis_dir: Path, tag: str, N: int = 384, L: float = 192.0, every: int = 1):
    """Primary analysis of PGPE_DIELECTRIC_PREREG.md (D1, D2; D3 and D4 reported) on saved snapshots + vortex positions."""
    import re
    from analyze_r3 import whole_from_blocks
    s = PGPE(N=N, L=L); ff = json.loads((OUT / "DG1pp.json").read_text())["sets"]["8.0"]["shells"]
    form = {int(m): ff[m]["n_eff_re"] / ff["1"]["n_eff_re"] for m in ff}                   # T = 0 k-dependence, d = 8
    names = sorted(f.stem for f in analysis_dir.glob("C3_L192_e*_s??.json")); runs = {}
    for name in names:
        j = json.loads((analysis_dir / f"{name}.json").read_text()); w = whole_from_blocks(j); T = w["T"]; norm = T * L ** 2
        z = np.load(analysis_dir / f"{name}_samples.npz", allow_pickle=True); ts = z["t"]
        acc = {m2: ([], []) for m2 in SHELLS}; num = den = 0.0
        for i in range(0, len(ts), every):
            t = float(ts[i]); psi = np.fromfile(rust_dir / f"{name}_sample_t{t:07.1f}.raw", dtype=np.complex128).reshape(N, N)
            c = np.fft.fft2(psi) * s.P; pos = np.asarray(z["pos"][i], float); q = np.asarray(z["q"][i], int)
            for m2, (JT, X) in mode_amplitudes(s, c, pos, q).items():
                acc[m2][0].append(JT); acc[m2][1].append(X)
            ds = matched_sizes(pos, q, L); num += float((ds ** 2).sum()) / 2; den += 1
        r = fit(acc, norm)
        ne = np.array([r[m]["n_eff_re"] for m in SHELLS]); ni = np.array([r[m]["n_eff_im"] for m in SHELLS]); co = np.array([r[m]["coherence"] for m in SHELLS])
        nek = ne / np.array([form[m] for m in SHELLS])
        f_res = float(np.mean([r[m]["R_res"] for m in (1, 2)])); n_eff_mean = float(np.mean(nek))
        cands = {"1": 1.0, "1-f": 1 - f_res, "ns/n": w["ns_over_n"]}
        closest = min(cands, key=lambda k: abs(cands[k] - n_eff_mean))
        RTv1 = r[1]["R_Tv"]; plateau = float(np.mean([r[m]["R_Tv"] for m in (4, 5, 8, 9, 10, 13, 16)]))   # (2pi)^2 <|rho|^2>/(k^2 T L^2): the polarisability plateau of a bound-pair gas
        # (first version multiplied by k^2 by mistake and gave ratios ~0.01; corrected 2026-10-06 23:20, see PGPE_DIELECTRIC_RESULTS.md)
        pol_pred = (2 * np.pi) ** 2 * (num / den) / norm
        runs[name] = {"T": T, "ns_over_n": w["ns_over_n"], "K": 2 * np.pi * w["ns_over_n"] / T, "shells": r,
                      "D1_min_coherence": float(co.min()), "D1_pass": bool(co.min() >= 0.4),
                      "D2_im_ratio": float(np.max(np.abs(ni) / np.abs(ne))), "D2_k_ratio": float(nek.max() / nek.min()), "D2_pass": bool(np.max(np.abs(ni) / np.abs(ne)) <= 0.1 and nek.max() / nek.min() <= 1.25),
                      "n_eff_formfactor_corrected": n_eff_mean, "n_eff_raw_shells": ne.tolist(), "f_res_low": f_res, "D3_candidates": cands, "D3_closest": closest,
                      "R_Tv_k1": RTv1, "box_scale_pair": bool(RTv1 > 0.45), "D4_plateau_measured": plateau, "D4_pred_from_matching": pol_pred, "D4_ratio": plateau / pol_pred if pol_pred else float("nan")}
        print(f"{name}: T={T:.3f} K={runs[name]['K']:.2f} | D1 min coherence {co.min():.3f} | n_eff raw {ne.round(3).tolist()} | Im/Re max {runs[name]['D2_im_ratio']:.3f}, k-ratio {runs[name]['D2_k_ratio']:.3f} | n_eff(ff-corr) {n_eff_mean:.3f} f_res {f_res:.3f} ns/n {w['ns_over_n']:.3f} -> closest {closest} | R_Tv(k1) {RTv1:.2f} D4 ratio {runs[name]['D4_ratio']:.2f}", flush=True)
    d1 = sum(v["D1_pass"] for v in runs.values()); d2 = sum(v["D2_pass"] for v in runs.values())
    d3 = {k: sum(v["D3_closest"] == k for v in runs.values()) for k in ("1", "1-f", "ns/n")}
    d4 = [v["D4_ratio"] for v in runs.values() if not v["box_scale_pair"]]
    verdict = {"D1_pass_runs": d1, "D1": d1 >= 5, "D2_pass_runs": d2, "D2": d2 >= 5, "D3_closest_counts": d3, "D4_ratios_no_box_pair": d4,
               "D4": bool(d4) and all(0.7 <= x <= 1.3 for x in d4)}
    (OUT / f"primary_{tag}.json").write_text(json.dumps({"runs": runs, "verdict": verdict}, indent=1, default=float))
    print("VERDICT", json.dumps(verdict, default=float))


if __name__ == "__main__":
    if sys.argv[1] == "RUNS":
        analyse_runs(ROOT / "data/generated/pgpe" / sys.argv[2], ROOT / "data/generated/pgpe" / sys.argv[3], sys.argv[4]); sys.exit(0)
    if sys.argv[1] in ("DG1pp", "DG2pp"):
        gate_formfactor(sys.argv[1]); sys.exit(0)
    if sys.argv[1] == "MU_B":
        print(mu_B_table()); sys.exit(0)
    if sys.argv[1] in ("DG1", "DG2"):
        gate(sys.argv[1])
    elif sys.argv[1] in ("DG1p", "DG2p"):
        gate_relaxed(sys.argv[1])
