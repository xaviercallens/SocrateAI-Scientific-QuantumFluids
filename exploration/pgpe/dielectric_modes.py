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


if __name__ == "__main__":
    if sys.argv[1] in ("DG1", "DG2"):
        gate(sys.argv[1])
    elif sys.argv[1] in ("DG1p", "DG2p"):
        gate_relaxed(sys.argv[1])
