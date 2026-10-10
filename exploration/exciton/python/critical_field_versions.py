#!/usr/bin/env python3
"""Closed-form critical field of the four-flavour model (T5) for the two parameter sets of Qi et al.

arXiv v1: g_X = 1, Delta = 1 ueV.  Nature version (Extended Data Fig. 8, quoted there as "the parameters used in the main text"):
g_X = 1.5, Delta = 0.3 ueV, n_x = 0.4e12 cm^-2, energy crossing at ~30 mT.  Units: Rydberg and Bohr radius; g_H = 8 pi d / a_B.
Two sets of unit constants are shown: those of the repository's reference (a_B = 1.5 nm, Ry = 67 meV) and those of the paper's
Methods (a_B = 1.543 nm, Ry = 66.64 meV).  Run: python3 exploration/exciton/python/critical_field_versions.py
"""
import json, math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "results" / "critical_field_versions.json"
muB = 57.88  # ueV/T
gc, gv, d_nm = 3.0, 6.0, 2.0
rows = []
for units, (aB, Ry) in {"repo reference (aB=1.5 nm, Ry=67 meV)": (1.5, 67e3),
                        "paper Methods (aB=1.543 nm, Ry=66.64 meV)": (1.543, 66.64e3)}.items():
    for label, gX, Dl in (("arXiv v1", 1.0, 1.0), ("Nature (ED Fig. 8)", 1.5, 0.3)):
        for nx12 in (0.4, 0.5):
            gH = 8 * math.pi * d_nm / aB
            Delta = Dl / Ry
            nx = nx12 * 1e12 * 1e-14 * aB ** 2          # n_x in units of a_B^-2 (aB in nm: 1 nm^2 = 1e-14 cm^2)
            mu = nx * (2 * gH + gX) / 2
            bc2 = gX * Delta * (2 * mu + Delta) / (4 * gc * gv * (2 * gH + gX))
            Bc_mT = math.sqrt(bc2) * Ry / muB * 1e3
            rows.append({"units": units, "version": label, "g_X": gX, "Delta_ueV": Dl, "n_x_1e12_cm2": nx12, "B_c_mT": round(Bc_mT, 1)})
OUT.write_text(json.dumps(rows, indent=1) + "\n")
for r in rows:
    print(f'{r["units"]:46s} {r["version"]:20s} g_X={r["g_X"]:<4} Delta={r["Delta_ueV"]:<4} n_x={r["n_x_1e12_cm2"]}e12  B_c = {r["B_c_mT"]} mT')
