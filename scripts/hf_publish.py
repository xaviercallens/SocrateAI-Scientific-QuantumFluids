#!/usr/bin/env python3
"""Publish the causal-topology stream to a Hugging Face dataset repo (owner-authorised 2026-09-25).

    python3 scripts/hf_publish.py --tag v1.12.0 --doi 10.5281/zenodo.XXXXXXX [--repo callensxavier/socrateai-quantumfluids-causal-topology]

Uploads: the three papers of the stream (PDF), the Lean sources of the four causal modules + QHFricke, the design
documents, the verdict JSONs of rounds 1-3, the round-3 vortex-position samples, the external-data source notes,
and a dataset card. Token from ~/.cache/huggingface/token (never printed). Nothing is deleted on the remote.
"""
import argparse, json, subprocess, tempfile, shutil
from pathlib import Path
from huggingface_hub import HfApi, create_repo

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ["causal_topology.pdf", "astro_topological_measurement.pdf", "sector_temperature.pdf", "duality_sector.pdf", "cosmology_sectors.pdf"]
LEAN = ["ChargeLattice.lean", "CompactBoson.lean", "TopologicalProtection.lean", "ScaleResolvedWinding.lean", "ContinuumWinding.lean", "SectorTemperature.lean", "QHFricke.lean", "VortexWinding.lean", "QuantizedCirculation.lean"]
DOCS = ["CAUSAL_TOPOLOGY.md", "CAUSAL_TOPOLOGY_DEEP_NOTES.md", "PGPE_BKT_PREREG.md", "PGPE_BKT_RESULTS.md", "PGPE_R2_PREREG.md", "PGPE_R2_RESULTS.md", "PGPE_R3_PREREG.md", "PGPE_R3_RESULTS.md"]
GEN = ["pgpe/r2_verdicts.json", "pgpe/r3_verdicts.json", "pgpe/r2_energy_budget.json", "pgpe/vortex_thermometer_cal.json", "pgpe/vortex_thermometer_cal_large.json",
       "pgpe/r2_vortex_temperature_posthoc.json", "external_gauthier2019_lifetime.json", "external_christodoulou2021_overlay.json", "pgpe/sweep_verdicts_A4.json"]


def card(tag, doi):
    return f"""---
license: cc-by-4.0
tags: [physics, quantum-fluids, superfluid, BKT, topology, lean4, formal-verification, pre-registration]
pretty_name: "SocrateAI QuantumFluids — causal topology stream ({tag})"
---

# Does topology causally influence physics? — data, papers and machine-checked theorems

Companion dataset of the SocrateAI-Scientific-QuantumFluids repository, release **{tag}**,
archived on Zenodo: **https://doi.org/{doi}** (concept DOI 10.5281/zenodo.22855581).
Code: https://github.com/xaviercallens/SocrateAI-Scientific-QuantumFluids

## Contents
- `papers/` — *Does topology causally influence physics?* (winding numbers as difference-makers in a 2D Bose gas);
  *Topological charge as a measurement principle for astrophysical U(1) phase fields* (methods; no astrophysical number
  claimed); *Topological sectors carry their own temperature* (proposal, with rounds 2–3 verdicts).
- `lean/` — Lean 4 sources (Mathlib pinned): `TopologicalProtection` (winding conserved without phase slips, XY-ring
  barrier), `ScaleResolvedWinding` (discrete Stokes: W(R) = net charge inside R), `ContinuumWinding` (the sampled
  loop sum equals the topological degree), `SectorTemperature` (mediant inequality), `QHFricke`, and their
  prerequisites. All accepted by the Lean kernel and by nanoda via Comparator; standard axioms.
- `docs/` — pre-registrations and results of the three PGPE rounds, with every amendment dated.
- `data/` — verdict JSONs, calibration of the torus vortex thermometer, energy budgets, and the round-3 vortex
  position samples (`r3_samples/`, npz).
- `external/` — source notes for the public datasets used (Gauthier et al. 2019, Zenodo 2548958; Christodoulou et al.
  2021, Apollo 10.17863/CAM.66056; Sunami et al. 2023, Zenodo 8385524), all CC BY 4.0; the data themselves are at
  their original DOIs.

## What is claimed, and what is not
No physics is claimed as new (Anderson 1966; Kosterlitz–Thouless 1973; Nelson–Kosterlitz 1977; Onsager 1949;
Gauthier/Johnstone 2019; Groszek 2018). What is new is the machine-checked chain and the pre-registered,
energy-matched intervention, with failed criteria reported as failed. See the LEDGER in the repository.

Licence: code MIT OR Apache-2.0; papers, documents and data CC BY 4.0. Author: Xavier Callens.
"""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True); ap.add_argument("--doi", required=True)
    ap.add_argument("--repo", default="callensxavier/socrateai-quantumfluids-causal-topology"); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(); api = HfApi()
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "README.md").write_text(card(a.tag, a.doi))
        for sub, items, src in (("papers", PAPERS, ROOT / "paper"), ("lean", LEAN, ROOT / "lean_src"), ("docs", DOCS, ROOT / "docs/designs")):
            (d / sub).mkdir()
            for f in items:
                if (src / f).exists(): shutil.copy(src / f, d / sub / f)
        (d / "data").mkdir()
        for f in GEN:
            p = ROOT / "data/generated" / f
            if p.exists(): shutil.copy(p, d / "data" / p.name)
        (d / "data/r3_samples").mkdir()
        for p in (ROOT / "data/generated/pgpe/r3").glob("*_samples.npz"): shutil.copy(p, d / "data/r3_samples" / p.name)
        (d / "external").mkdir()
        for p in (ROOT / "data/external").glob("*/SOURCE.meta"): shutil.copy(p, d / "external" / f"{p.parent.name}.SOURCE.meta")
        (d / "LEDGER.md").write_text((ROOT / "LEDGER.md").read_text()); (d / "CITATION.cff").write_text((ROOT / "CITATION.cff").read_text())
        files = sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()); total = sum(p.stat().st_size for p in d.rglob("*") if p.is_file())
        print(f"{len(files)} files, {total/1e6:.1f} MB ->", a.repo)
        if a.dry:
            print("\n".join(files)); return
        create_repo(a.repo, repo_type="dataset", exist_ok=True)
        api.upload_folder(folder_path=str(d), repo_id=a.repo, repo_type="dataset", commit_message=f"{a.tag}: causal-topology stream, Zenodo {a.doi}")
        print("published: https://huggingface.co/datasets/" + a.repo)


if __name__ == "__main__":
    main()
