#!/usr/bin/env python3
"""Amendment R3-A3, part C3-b (docs/designs/PGPE_R3_PREREG.md): refit eta on one fixed physical window r in [2, 16]
at every box size and compare with the L/4-scaled window (round2.fit_g1_window) used so far.

Like for like at every size: g1 of the saved FINAL field of each run (L = 64: round-2 ladder II_*, L = 128: C2_*,
L = 192: C3_* snapshot at t_end), both windows fitted to the same g1. K = n_s/n * 2pi/T comes from each run's own
block-averaged record (whole_from_blocks / the round-2 'whole'), admission A4 as in the ladders. A single field is
noisier than the 100-sample block average the ladders use, so absolute offsets here differ from the ladder ones;
the pre-registered question is only whether the *trend with L* survives the change of window.
Run: .venv/bin/python exploration/pgpe/analyze_r3_c3b.py -> data/generated/pgpe/r3_c3b.json"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from observables import g1_radial
from round2 import fit_g1_window
from analyze_r3 import whole_from_blocks

ROOT = Path(__file__).resolve().parents[2]; PG = ROOT / "data/generated/pgpe"
ENERGIES = (1.00, 1.10, 1.20); FIXED = (2.0, 16.0)


def fit_fixed(r, g, rmin=FIXED[0], rmax=FIXED[1]):
    m = (r >= rmin) & (r < rmax) & (g > 0)                 # same half-open convention as fit_g1_window
    p = np.polyfit(np.log(r[m]), np.log(g[m]), 1)
    return float(-p[0]), int(m.sum())


def runs():
    """(L, e, seed, c_final, whole) for every run of the three sizes."""
    for f in sorted((PG / "r2").glob("II_e0.90_s1*_t4000_e1.[012]0.json")):
        d = json.loads(f.read_text()); e = round(d["e"], 2)
        if e in ENERGIES:
            yield 64.0, e, d["base"], np.load(f.with_name(f.stem + "_final.npy")), d["whole"]
    for f in sorted((PG / "r3").glob("C2_L128_e*_s*.json")):
        d = json.loads(f.read_text())
        yield 128.0, round(d["e"], 2), d["seed"], np.load(f.with_name(f.stem + "_final.npy")), whole_from_blocks(d)
    for f in sorted((PG / "r3").glob("C3_L192_e*_s??.json")):
        d = json.loads(f.read_text()); s = PGPE(N=384, L=192.0)
        psi = np.fromfile(PG / "r3" / f"{d['name']}_sample_t07000.0.raw", dtype=np.complex128).reshape(384, 384)
        yield 192.0, round(d["e"], 2), d["seed"], s.modes(psi), whole_from_blocks(d)


def main():
    rows = []
    for L, e, seed, c, w in runs():
        s = PGPE(N=int(2 * L), L=L)
        r, g = g1_radial(s, c)
        sc = fit_g1_window(r, g, L); eta_fx, n_fx = fit_fixed(r, g)
        K = w["ns_over_n"] * 2 * np.pi / w["T"]
        adm = bool(w["R_L"] <= 1.25 and w["R_T"] <= 1.1 * w["R_L"])
        rows.append({"L": L, "e": e, "seed": seed, "admitted": adm, "K": K, "T": w["T"],
                     "eta_scaled": sc["eta"], "r_max_scaled": sc["r_max"], "eta_fixed": eta_fx, "npts_fixed": n_fx,
                     "off_scaled": sc["eta"] * K - 1, "off_fixed": eta_fx * K - 1})
    table = {}
    for e in ENERGIES:
        table[e] = {}
        for L in (64.0, 128.0, 192.0):
            a = [x for x in rows if x["L"] == L and x["e"] == e and x["admitted"]]
            table[e][L] = {"n": len(a), "off_scaled": float(np.mean([x["off_scaled"] for x in a])) if a else float("nan"),
                           "off_fixed": float(np.mean([x["off_fixed"] for x in a])) if a else float("nan")}
    inc = lambda key: {e: bool(table[e][64.0][key] < table[e][128.0][key] < table[e][192.0][key]) for e in ENERGIES}
    out = {"rows": rows, "table": {str(e): {str(int(L)): v for L, v in t.items()} for e, t in table.items()},
           "increasing_scaled": inc("off_scaled"), "increasing_fixed": inc("off_fixed")}
    (PG / "r3_c3b.json").write_text(json.dumps(out, indent=1, default=float))
    for x in rows:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in x.items()})
    for e in ENERGIES:
        print(e, {int(L): (v["n"], round(v["off_scaled"], 3), round(v["off_fixed"], 3)) for L, v in table[e].items()})
    print("strictly increasing (scaled window):", out["increasing_scaled"]); print("strictly increasing (fixed window):", out["increasing_fixed"])


if __name__ == "__main__":
    main()
