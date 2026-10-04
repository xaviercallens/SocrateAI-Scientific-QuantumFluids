#!/usr/bin/env python3
"""Criteria of docs/designs/PGPE_ONSAGER_PREREG.md: are the negative-stiffness runs of round 3 (Parts C, C2, C3)
Onsager-clustered vortex states? Analysis of the saved vortex positions only; no new simulation.
Run: .venv/bin/python exploration/pgpe/analyze_onsager.py -> data/generated/pgpe/onsager_clusters.json"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_r3 import whole_from_blocks
from observables import onsager_dipole
from vortex_thermometer import energy as pv_energy
from pgpe import PGPE
from run_r4 import torus_winding

ROOT = Path(__file__).resolve().parents[2]; R3 = ROOT / "data/generated/pgpe/r3"
TAGS = {"C": ("C_L128", 128.0), "C2": ("C2_L128", 128.0), "C3": ("C3_L192", 192.0)}


class _L:
    def __init__(self, L):
        self.L = L


def s_q_k1(pos, q, L):
    """|sum_j q_j exp(i k.r_j)|^2 / N_v averaged over the first shell k = (+-2pi/L, 0), (0, +-2pi/L)."""
    k = 2 * np.pi / L
    vals = [abs(np.sum(q * np.exp(1j * k * pos[:, a]))) ** 2 for a in (0, 1)]   # +k and -k give the same modulus
    return float(np.mean(vals) / len(q))


def f_same_sign(pos, q, L):
    d = pos[:, None, :] - pos[None, :, :]
    d -= L * np.round(d / L)
    r2 = (d ** 2).sum(-1); np.fill_diagonal(r2, np.inf)
    nn = np.argmin(r2, axis=1)
    return float(np.mean(q[nn] == q))


def z_energy(pos, q, L, E, rng, n_rand=8):
    Er = [pv_energy(rng.uniform(0, L, size=pos.shape), q, L) for _ in range(n_rand)]
    return float((E - np.mean(Er)) / np.std(Er)), float(np.mean(Er)), float(np.std(Er))


def analyse(part, tag, L, rng):
    out = []
    for f in sorted(R3.glob(f"{tag}_e*_s??.json")):
        d = json.loads(f.read_text()); w = whole_from_blocks(d)
        z = np.load(R3 / f"{d['name']}_samples.npz", allow_pickle=True)
        t, P, Q, E = z["t"], z["pos"], z["q"], z["E_pv"]
        sq = np.array([s_q_k1(p, qq, L) for p, qq in zip(P, Q)])
        fss = np.array([f_same_sign(p, qq, L) for p, qq in zip(P, Q)])
        D = np.array([onsager_dipole(_L(L), p, qq) for p, qq in zip(P, Q)])
        zs = [z_energy(P[i], Q[i], L, float(E[i]), rng) for i in range(0, len(t), 10) if np.isfinite(E[i])]
        rec = {"part": part, "name": d["name"], "L": L, "e": round(float(d["e"]), 2), "seed": d["seed"],
               "class": "A" if w["ns_over_n"] < 0 else "N", "ns_over_n": w["ns_over_n"], "R_L": w["R_L"], "R_T": w["R_T"],
               "n_v": float(np.mean([len(qq) for qq in Q])), "cond": w["cond"],
               "S_q_k1": float(sq.mean()), "S_q_k1_first_last_tenth": (float(sq[:10].mean()), float(sq[-10:].mean())),
               "f_ss": float(fss.mean()), "D": float(np.nanmean(D)),
               "z_E": float(np.mean([x[0] for x in zs])) if zs else float("nan"), "z_E_n": len(zs),
               "E_pv": float(np.nanmean(E)), "E_rand": float(np.mean([x[1] for x in zs])) if zs else float("nan")}
        if part == "C3":
            psi = np.fromfile(R3 / f"{d['name']}_sample_t07000.0.raw", dtype=np.complex128).reshape(384, 384)
            s = PGPE(N=384, L=192.0); rec["W_final"] = torus_winding(s, s.modes(psi))
        out.append(rec); print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in rec.items()}, flush=True)
    return out


def auc(a, n):
    return float(np.mean([(x > y) + 0.5 * (x == y) for x in a for y in n])) if a and n else float("nan")


def main():
    rng = np.random.default_rng(20261004)
    runs = [r for part, (tag, L) in TAGS.items() for r in analyse(part, tag, L, rng)]
    A = [r for r in runs if r["class"] == "A"]; N = [r for r in runs if r["class"] == "N"]
    by_L = lambda cls, L, key: [r[key] for r in cls if r["L"] == L]
    aucs = {key: {int(L): auc(by_L(A, L, key), by_L(N, L, key)) for L in (128.0, 192.0)} for key in ("S_q_k1", "f_ss", "D", "z_E")}
    P1 = all(aucs["S_q_k1"][L] >= 0.9 for L in (128, 192)) and sum(r["S_q_k1"] > 1 for r in A) >= 6
    P2 = all(aucs["f_ss"][L] >= 0.9 for L in (128, 192))
    P3 = sum(r["z_E"] > 0 for r in A) >= 6 and sum(r["z_E"] < 0 for r in N) >= 10
    get = lambda part, name: next(r for r in runs if r["part"] == part and r["name"].endswith(name))
    cured = ["e1.00_s12", "e1.10_s11", "e1.20_s11"]
    p4a = {c: (get("C", c)["S_q_k1"], get("C2", c)["S_q_k1"]) for c in cured}
    c2 = [r for r in runs if r["part"] == "C2"]
    P4 = all(b < a for a, b in p4a.values()) and max(c2, key=lambda r: r["S_q_k1"])["name"].endswith("e1.00_s11")
    C0 = all(r["W_final"] == (0, 0) for r in runs if r["part"] == "C3")
    kill = any(aucs["S_q_k1"][L] < 0.7 and aucs["f_ss"][L] < 0.7 for L in (128, 192))
    v = {"runs": runs, "AUC": aucs, "P1": P1, "P2": P2, "P3": P3, "P4": P4, "P4_detail": p4a, "C0": C0, "kill": kill,
         "nA": len(A), "nN": len(N)}
    (ROOT / "data/generated/pgpe/onsager_clusters.json").write_text(json.dumps(v, indent=1, default=float))
    print(json.dumps({k: x for k, x in v.items() if k != "runs"}, default=float, indent=1))


if __name__ == "__main__":
    main()
