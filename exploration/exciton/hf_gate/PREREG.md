# Hugging Face / GNN validity gate for the exciton model: pre-registration (2026-10-11)

Written and committed BEFORE hf_extract.py is first run. Status disclosure: while doing Step 1 (inventory) the author already
opened the one candidate file (colabfit/JARVIS_C2DB, co_0.parquet, 1.98 MB, CC-BY-4.0) interactively and saw that it holds
single-layer entries (3-12 atoms, no vdW stacks) and 3-atom 2H MoSe2 / WSe2 entries with a = 3.32 A. The gates below are
therefore pre-registered for the SCRIPT and for the decision, not blind to the file's existence; the interactive look is
declared here.

## Model inputs needed (gated kernel, paper/exciton_fluid_gated.tex)
(i) electron-hole layer separation d in Angstrom (and d/a); (ii) in-plane/out-of-plane dielectric environment (epsilon, hBN
spacer, gate distance D); (iii) exciton mass and binding energy. U(0) = 4 pi d (1 - d/D) e^2/epsilon (uniform-epsilon form).

## Gates (all evaluated by hf_extract.py unless stated)
- G1 source: read-only, < 50 MB, permissive licence, provenance DOI/URL recorded, sha256 recorded.
- G2 content: the file contains a 2H monolayer MoSe2 and a 2H monolayer WSe2 (identified by geometry: hexagonal cell,
  both chalcogens at the same in-plane position). PASS if both found.
- G3 stack: the file contains at least one entry of MoSe2/WSe2 with two layers (interlayer d is then readable from it).
  PASS only if found. Prediction: FAIL (monolayer-only database).
- G4 lattice constant: HF value of a for each monolayer agrees within 2 % with each of >= 2 independent published values
  that the author actually read (DOIs in the report). Spread = max-min over all sources. PASS if all within 2 %.
- G5 excitonic content: the file carries a quantity from which an exciton binding energy or optical gap can be read.
  Properties listed are energy and (PBE) electronic band gap; PASS only if an optical/GW-BSE field exists. Prediction: FAIL.
- Overall: d and E_b are "supplied by HF/GNN" only if G3 and G5 pass. Otherwise the deliverable is the gate document and the
  list of what a valid pipeline needs. Literature d values (not HF) may be tabulated, labelled as literature, never as HF output.

## Not done / out of scope
No GNN is run (no MACE/ALIGNN inference): a force-field relaxation of a bilayer would be a model output, not data; whether it
is worth doing is argued in the report, not tested here. Nothing is uploaded to Hugging Face.
