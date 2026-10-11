#!/usr/bin/env python3
"""hf_extract.py -- validity gate for Hugging Face data as input to the gated exciton model.

Pre-registered in PREREG.md (committed before the first run of this script).
Reads ONE small file set (colabfit/JARVIS_C2DB, CC-BY-4.0, ~2 MB) and evaluates gates G1..G5.
Run:  python3 -I hf_extract.py --data-dir <dir with co_0.parquet and ds.parquet> --out results/
      (--fetch downloads the two files read-only from the public Hugging Face URL, hard cap 50 MB, no token.)
Needs pyarrow and numpy.  Nothing is uploaded anywhere.

The literature table below is HAND-ENTERED from papers read in the session (arXiv PDFs, extracted text), with the
location of each number. It is labelled LITERATURE, never HF output.
"""
import argparse, hashlib, json, os, re, sys, urllib.request
import numpy as np
import pyarrow.parquet as pq

REPO = "https://huggingface.co/datasets/colabfit/JARVIS_C2DB/resolve/main/"
FILES = {"co/co_0.parquet": "co_0.parquet", "ds.parquet": "ds.parquet"}
SHA256 = {  # recorded 2026-10-11 at first download
    "co_0.parquet": "b3daf88861342e3132661d25a73e396fe379314236e752c472be7f285dce04f3",
    "ds.parquet": "8cd046837601470b034dd65bb5e13fd8e8629c2c415deb3fbec0f691468c5a01",
}
E2_EV_A = 14.399645  # e^2/(4 pi eps0) in eV*Angstrom (CODATA)
MAXBYTES = 50 * 1024 * 1024

# ---- LITERATURE (read in session; see report for the exact quotes) ----
LIT_A = {  # in-plane lattice constant a (Angstrom)
    "MoSe2": [
        ("Kormanyos 2015 Table 1, FLEUR PBE (theory)", 3.319, "10.1088/2053-1583/2/2/022001 (arXiv:1410.6666)"),
        ("Kormanyos 2015 Table 1, VASP HSE06 (theory)", 3.289, "10.1088/2053-1583/2/2/022001"),
        ("Kormanyos 2015 Table 1, bulk experiment (ref a)", 3.288, "10.1088/2053-1583/2/2/022001"),
        ("Kormanyos 2015 Table 1, bulk experiment (ref c)", 3.299, "10.1088/2053-1583/2/2/022001"),
        ("Kormanyos 2015 Table 1, bulk experiment (ref e)", 3.289, "10.1088/2053-1583/2/2/022001"),
        ("Kormanyos 2015 Table 1, bulk experiment (ref g)", 3.290, "10.1088/2053-1583/2/2/022001"),
    ],
    "WSe2": [
        ("Kormanyos 2015 Table 1, FLEUR PBE (theory)", 3.316, "10.1088/2053-1583/2/2/022001"),
        ("Kormanyos 2015 Table 1, VASP HSE06 (theory)", 3.291, "10.1088/2053-1583/2/2/022001"),
        ("Kormanyos 2015 Table 1, bulk experiment (ref a)", 3.286, "10.1088/2053-1583/2/2/022001"),
        ("Kormanyos 2015 Table 1, bulk experiment (ref c)", 3.282, "10.1088/2053-1583/2/2/022001"),
        ("Kormanyos 2015 Table 1, bulk experiment (ref d)", 3.282, "10.1088/2053-1583/2/2/022001"),
    ],
}
LIT_DXX = {  # chalcogen-chalcogen distance within one layer (Angstrom)
    "MoSe2": [("Kormanyos 2015 HSE06", 3.307), ("Kormanyos 2015 PBE (FLEUR)", 3.4371), ("Kormanyos 2015 Exp (ref e)", 3.335)],
    "WSe2": [("Kormanyos 2015 HSE06", 3.327), ("Kormanyos 2015 PBE (FLEUR)", 3.471), ("Kormanyos 2015 Exp (ref d)", 3.34)],
}
# Gillen-Maultzsch state a = 3.290-3.293 A for the three stackings; 3.290 is used for d/a (0.1 % effect).
# interlayer distance of the MoSe2/WSe2 heterobilayer. 'metal-metal' = vertical distance between the Mo plane
# and the W plane, which is the electron-hole separation d of the interlayer exciton to a first approximation.
LIT_D = [
    # label, d_metal_metal (A), a used (A), method, source
    ("Gillen-Maultzsch AA'", 6.512, 3.290, "PBE+D3 relaxed (theory)", "10.1103/PhysRevB.97.165306, Fig. 1"),
    ("Gillen-Maultzsch AB", 6.473, 3.290, "PBE+D3 relaxed (theory)", "10.1103/PhysRevB.97.165306, Fig. 1"),
    ("Gillen-Maultzsch AA", 7.097, 3.290, "PBE+D3 relaxed (theory)", "10.1103/PhysRevB.97.165306, Fig. 1"),
    ("Torun et al. A-A'", 6.42, 3.288, "LDA relaxed at experimental a (theory)", "10.1103/PhysRevB.97.245427, Fig. 1b"),
]
LIT_EB = [  # exciton binding energies (eV) with the environment: they differ by a factor ~3.5
    ("MoSe2 monolayer, on bilayer graphene, STS + PL (experiment)", 0.55, "arXiv:1404.2331 / 10.1038/nmat4061"),
    ("MoSe2 monolayer, isolated, as quoted by Gillen-Maultzsch (theory)", 0.48, "10.1103/PhysRevB.97.165306"),
    ("WSe2 monolayer, isolated, as quoted by Gillen-Maultzsch (theory)", 0.46, "10.1103/PhysRevB.97.165306"),
    ("MoSe2/WSe2 intralayer exciton, vacuum, GW-BSE (theory)", 0.41, "10.1103/PhysRevB.97.245427"),
    ("MoSe2/WSe2 interlayer exciton, vacuum, GW-BSE (theory)", 0.32, "10.1103/PhysRevB.97.245427"),
    ("MoSe2/WSe2 interlayer exciton X0/Y0, vacuum, GW-BSE (theory)", 0.25, "10.1103/PhysRevB.97.165306 (order of 250 meV)"),
    ("WSe2 1s exciton, hBN-encapsulated, Keldysh fit kappa=4.5 (model calc. vs. magneto-optics)", 0.161, "arXiv:1709.00123 / 10.1103/PhysRevLett.120.057405"),
]
LIT_MR = ("WSe2 reduced mass m_r (magneto-optics, hBN-encapsulated)", 0.20, 0.01, "arXiv:1709.00123 / 10.1103/PhysRevLett.120.057405")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def fetch(dest):
    os.makedirs(dest, exist_ok=True)
    for rel, name in FILES.items():
        out = os.path.join(dest, name)
        if os.path.exists(out):
            continue
        with urllib.request.urlopen(urllib.request.Request(REPO + rel, headers={"User-Agent": "hf_extract/1"}), timeout=60) as r:
            n = int(r.headers.get("Content-Length", "0"))
            if n > MAXBYTES:
                sys.exit("refusing: %s is %d bytes (> 50 MB cap)" % (rel, n))
            data = r.read(MAXBYTES + 1)
            if len(data) > MAXBYTES:
                sys.exit("refusing: download exceeded 50 MB cap")
        with open(out, "wb") as f:
            f.write(data)


def classify_monolayer(r):
    """Return dict for a 3-atom MX2 entry: a, angle, dXX, phase ('2H' if both X at same in-plane position)."""
    c = np.array(r["cell"]); p = np.array(r["positions"]); z = np.array(r["atomic_numbers"])
    if len(z) != 3:
        return None
    se = p[z == 34]
    if len(se) != 2:
        return None
    a1, a2 = c[0], c[1]
    ang = float(np.degrees(np.arccos(a1 @ a2 / np.linalg.norm(a1) / np.linalg.norm(a2))))
    inv = np.linalg.inv(c[:2, :2])
    dxy = (se[0, :2] - se[1, :2]) @ inv
    dxy = dxy - np.round(dxy)
    same = bool(np.allclose(dxy, 0, atol=1e-3))
    return {"a": float(np.linalg.norm(a1)), "angle": ang, "dXX": float(abs(se[0, 2] - se[1, 2])),
            "phase": "2H" if (same and abs(ang - 120) < 0.5) else "other", "Lz": float(c[2, 2])}


def metal_planes(r):
    p = np.array(r["positions"]); z = np.array(r["atomic_numbers"])
    zs = np.sort(p[np.isin(z, [42, 74]), 2])
    if len(zs) == 0:
        return 0, 0.0
    planes = [zs[0]]
    for v in zs[1:]:
        if v - planes[-1] > 0.5:
            planes.append(v)
    return len(planes), float(planes[-1] - planes[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--D-over-d", type=float, default=10.0)
    ap.add_argument("--epsilon", type=float, default=4.5)
    ap.add_argument("--spacer", type=float, default=0.0, help="extra e-h separation from an hBN spacer, Angstrom (user-chosen)")
    a = ap.parse_args()
    if a.fetch:
        fetch(a.data_dir)
    os.makedirs(a.out, exist_ok=True)
    res = {"gates": {}}

    # G1 source
    g1 = {"license": None, "files": {}}
    ds = pq.read_table(os.path.join(a.data_dir, "ds.parquet")).to_pylist()[0]
    g1["license"] = ds["license"]; g1["doi"] = ds["doi"]; g1["source_publication"] = ds["links"]
    tot = 0
    for name, ref in SHA256.items():
        pth = os.path.join(a.data_dir, name); s = os.path.getsize(pth); tot += s
        g1["files"][name] = {"bytes": s, "sha256": sha256(pth), "sha256_matches_first_download": sha256(pth) == ref}
    g1["total_bytes"] = tot
    g1["pass"] = bool(tot < MAXBYTES and ds["license"] in ("CC-BY-4.0", "CC0-1.0", "MIT") and all(v["sha256_matches_first_download"] for v in g1["files"].values()))
    res["gates"]["G1_source"] = g1

    cols = ["names", "chemical_formula_hill", "nsites", "cell", "positions", "atomic_numbers", "electronic_band_gap",
            "energy", "software", "method", "nperiodic_dimensions", "pbc"]
    rows = pq.read_table(os.path.join(a.data_dir, "co_0.parquet"), columns=cols).to_pylist()
    res["n_entries"] = len(rows)
    res["nsites_max"] = max(r["nsites"] for r in rows)
    res["software_methods"] = sorted({(r["software"], r["method"]) for r in rows})

    # G2 content
    mono = {}
    for r in rows:
        f = r["chemical_formula_hill"]
        if r["nsites"] == 3 and f in ("MoSe2", "Se2W"):
            k = classify_monolayer(r)
            if k and k["phase"] == "2H":
                mono.setdefault("MoSe2" if f == "MoSe2" else "WSe2", []).append(
                    dict(k, name=r["names"][0], gap_PBE=r["electronic_band_gap"]))
    res["monolayers_2H"] = mono
    res["gates"]["G2_content"] = {"pass": all(len(mono.get(m, [])) >= 1 for m in ("MoSe2", "WSe2")),
                                  "n_2H": {m: len(v) for m, v in mono.items()}}

    # G3 stack: any entry with Se and Mo/W having >= 2 metal planes separated by > 5 A
    stacks = []
    for r in rows:
        z = set(r["atomic_numbers"])
        if 34 in z and (42 in z or 74 in z):
            n, span = metal_planes(r)
            if n >= 2 and span > 5.0:
                stacks.append({"name": r["names"][0], "formula": r["chemical_formula_hill"], "n_planes": n, "span": span})
    se_entries = sum(1 for r in rows if 34 in set(r["atomic_numbers"]) and (42 in set(r["atomic_numbers"]) or 74 in set(r["atomic_numbers"])))
    res["gates"]["G3_stack"] = {"pass": len(stacks) > 0, "n_Mo/W-Se_entries_scanned": se_entries,
                                "n_multi_metal_plane_entries": len(stacks), "examples": stacks[:5]}

    # G4 lattice constant
    g4 = {"pass": True, "per_material": {}}
    for m in ("MoSe2", "WSe2"):
        hf = [e["a"] for e in mono.get(m, [])]
        if not hf:
            g4["pass"] = False; continue
        aHF = hf[0]
        lit = LIT_A[m]
        dev = [(lab, v, 100 * (aHF - v) / v) for lab, v, _ in lit]
        allv = [aHF] + [v for _, v, _ in lit]
        g4["per_material"][m] = {"a_HF": aHF, "deviations_percent": [(l, v, round(d, 2)) for l, v, d in dev],
                                 "max_abs_dev_percent": round(max(abs(d) for _, _, d in dev), 2),
                                 "spread_A_all_values": round(max(allv) - min(allv), 4),
                                 "spread_A_experiment_only": round(max(v for l, v, _ in lit if "experiment" in l) - min(v for l, v, _ in lit if "experiment" in l), 4),
                                 "dXX_HF": mono[m][0]["dXX"], "dXX_literature": LIT_DXX[m]}
        if max(abs(d) for _, _, d in dev) > 2.0:
            g4["pass"] = False
    res["gates"]["G4_lattice_constant"] = g4

    # G5 excitonic content
    res["gates"]["G5_excitonic_content"] = {
        "pass": False,
        "reason": "columns present and non-empty: energy, electronic_band_gap (GPAW PBE, type 'unknown'); no GW, no BSE, "
                  "no optical gap, no dielectric tensor, no effective mass in this dataset",
        "software_methods": res["software_methods"]}

    # literature d table and conversion (labelled LITERATURE)
    dvals = np.array([x[1] for x in LIT_D])
    tab = [{"label": l, "d_A": d, "a_A": aa, "d_over_a": round(d / aa, 3), "method": m, "source": s} for l, d, aa, m, s in LIT_D]
    sub = dvals[:3]  # same code and functional: Gillen-Maultzsch three stackings
    d_ex = LIT_D[0][1] + a.spacer       # example: AA' stacking, + optional spacer
    D = a.D_over_d * d_ex
    fac = 1.0 - d_ex / D
    U0 = 4 * np.pi * d_ex * fac * E2_EV_A / a.epsilon
    res["literature_d_table"] = {
        "NOTE": "LITERATURE values, hand-entered from papers read in session; NOT output of the HF dataset (G3 fails)",
        "rows": tab,
        "d_range_A_all": [float(dvals.min()), float(dvals.max())],
        "d_range_A_commensurate_stackings_AA'_AB_Torun": [float(min(6.512, 6.473, 6.42)), float(max(6.512, 6.473, 6.42))],
        "relative_spread_commensurate_percent": round(100 * (max(6.512, 6.473, 6.42) - min(6.512, 6.473, 6.42)) / np.mean([6.512, 6.473, 6.42]), 2),
    }
    res["conversion_example"] = {
        "inputs": {"d_A (Gillen AA' metal-metal + spacer)": d_ex, "spacer_A": a.spacer, "a_A (Gillen AA')": 3.290,
                   "d_over_a": round(d_ex / 3.290, 3), "D_over_d": a.D_over_d, "D_A": D, "epsilon (uniform; kappa_hBN of Stier 2018)": a.epsilon,
                   "e2_eV_A": E2_EV_A},
        "U0_eV_A2": float(U0),
        "U0_in_units_of_e2_over_eps_A": float(4 * np.pi * d_ex * fac),
        "caveats": ["uniform-epsilon formula; for hBN/TMD stacks the factor is 1-(d/eps_m)/sum(t_i/eps_i) (paper Sec. cm, review M2)",
                    "d is the metal-plane separation of a relaxed heterobilayer in vacuum from DFT-D3/LDA, not a measured quantity",
                    "epsilon=4.5 is the in-plane-averaged IR value Stier et al. use for hBN in a Keldysh model; it is not the epsilon of the "
                    "stack, and the exciton itself screens (Keldysh r0 not included in the gated kernel)"],
    }
    res["exciton_binding_energy_literature"] = {
        "NOTE": "LITERATURE; spread is environment/method, not noise",
        "rows": [{"label": l, "Eb_eV": v, "source": s} for l, v, s in LIT_EB],
        "min_eV": min(v for _, v, _ in LIT_EB), "max_eV": max(v for _, v, _ in LIT_EB),
        "ratio_max_over_min": round(max(v for _, v, _ in LIT_EB) / min(v for _, v, _ in LIT_EB), 2),
        "reduced_mass": {"label": LIT_MR[0], "m_r_over_m0": LIT_MR[1], "err": LIT_MR[2], "source": LIT_MR[3]},
    }
    ok = {k: v["pass"] for k, v in res["gates"].items()}
    res["summary"] = {"gates": ok,
                      "supplies_d_from_HF": bool(ok["G3_stack"]),
                      "supplies_Eb_from_HF": bool(ok["G5_excitonic_content"]),
                      "verdict": "FAIL" if not (ok["G3_stack"] and ok["G5_excitonic_content"]) else "PASS"}
    with open(os.path.join(a.out, "hf_gate_results.json"), "w") as f:
        json.dump(res, f, indent=1, default=str)

    # markdown table
    L = ["# hf_extract.py output (auto-generated)", "", "## Gates", ""]
    for k, v in res["gates"].items():
        L.append("- %s: %s" % (k, "PASS" if v["pass"] else "FAIL"))
    L += ["", "## Monolayers read from the dataset (G2, G4)", "", "| material | entry | a (A) | d_XX (A) | PBE gap (eV) | max abs dev from 5-6 lit. a (%) | spread all values (A) |", "|---|---|---|---|---|---|---|"]
    for m, v in g4["per_material"].items():
        e = mono[m][0]
        L.append("| %s | %s | %.4f | %.3f | %.3f | %.2f | %.4f |" % (m, e["name"], v["a_HF"], e["dXX"], e["gap_PBE"], v["max_abs_dev_percent"], v["spread_A_all_values"]))
    L += ["", "## Interlayer distance d of MoSe2/WSe2 (LITERATURE, not HF)", "", "| source | d (A, metal-metal) | a (A) | d/a | method | where |", "|---|---|---|---|---|---|"]
    for t in tab:
        L.append("| %s | %.3f | %.3f | %.3f | %s | %s |" % (t["label"], t["d_A"], t["a_A"], t["d_over_a"], t["method"], t["source"]))
    c = res["literature_d_table"]
    L += ["", "range all: %.3f-%.3f A; commensurate stackings: %.2f-%.2f A (%.2f %% of mean)" % (c["d_range_A_all"][0], c["d_range_A_all"][1], c["d_range_A_commensurate_stackings_AA'_AB_Torun"][0], c["d_range_A_commensurate_stackings_AA'_AB_Torun"][1], c["relative_spread_commensurate_percent"])]
    ce = res["conversion_example"]
    L += ["", "## Conversion example", "", "d = %.3f A (d/a = %.3f), D/d = %g -> D = %.2f A, epsilon = %g:" % (ce["inputs"]["d_A (Gillen AA' metal-metal + spacer)"], ce["inputs"]["d_over_a"], a.D_over_d, D, a.epsilon),
          "U(0) = 4 pi d (1-d/D) e^2/eps = %.2f eV A^2 (= %.3f x e^2/eps in A)" % (ce["U0_eV_A2"], ce["U0_in_units_of_e2_over_eps_A"] ), ""]
    with open(os.path.join(a.out, "hf_gate_tables.md"), "w") as f:
        f.write("\n".join(L))
    print("\n".join(L))
    print("\nVERDICT:", res["summary"])


if __name__ == "__main__":
    main()
