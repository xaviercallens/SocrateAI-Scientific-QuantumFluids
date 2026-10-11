# Verification of package 'hf' (2026-10-11)
Verdict: accept_with_fixes. No blocking problem found; the negative verdict (gate FAILS for d and E_b) stands.

Checked and correct
- Re-downloaded colabfit/JARVIS_C2DB co_0.parquet and ds.parquet: sha256 identical to the recorded values (1.98 MB + 19 kB, CC-BY-4.0).
- Re-ran hf_extract.py on my copy: hf_gate_results.json and hf_gate_tables.md byte-identical.
- Independent scan (own code): 3520 entries, max 12 atoms; Mo/W-Se entries with metal-plane separation: max 3.7 A (Mo2Se6), none > 5 A (MXene-like / adsorbate structures, not vdW stacks). G3 FAIL confirmed.
- MoSe2 c2db_atoms_3150 a=3.3197, WSe2 c2db_atoms_3118 a=3.3190 confirmed, 2H geometry (chalcogens at same xy).
- Columns non-null: energy, atomic_forces, electronic_band_gap only; no optical/GW/BSE/dielectric/mass. G5 FAIL confirmed.
- Kormanyos 2015 (arXiv:1410.6666) Table 1 re-read: all MoSe2/WSe2 a0 values in LIT_A match (3.319/3.289/3.288/3.299/3.289/3.290; 3.316/3.291/3.286/3.282/3.282); dXX values match.
- Gillen-Maultzsch (PRB 97, 165306): 7.097/6.512/6.473 A in Fig. 1, text 'interlayer distances of 6.51 A (AA') and 6.47 A (AB)', PBE+D3, 0.48/0.46 eV quoted, 'order of 250 meV' all present.
- Torun (arXiv:1803.05483): Fig. 1b shows 3.12 A and 6.42 A for MoSe2/WSe2; 0.41 and 0.32 eV in text; LDA relaxation, bulk a 3.288. Stier (arXiv:1709.00123): 161 meV, kappa=4.5, mr=0.20+/-0.01 m0 present. Mak/Ugeda arXiv:1404.2331: 0.55+/-0.04 eV present.
- U(0)=235.67 eV A^2 recomputed; formula matches paper Eq. (U~(0)=4 pi d (1-d/D)).
- Pre-registration: PREREG.md committed 10:13:36, script/results mtime 10:17, results committed 10:18:31. Order is sound; the interactive look is disclosed.

Problems
1. (major, scope of claim) The headline 'No Hugging Face dataset or GNN supplies d' rests on one dataset opened plus substring name search. The worker did not list or open other colabfit 2D sources: JARVIS_DFT_2D_3_12_2021 (5 MB, licence 'unknown'), JARVIS_2DMatPedia (4 MB, CC-BY-4.0), JARVIS_EPC_2D, JARVIS_DFT_3D_12_12_2022 (54 MB, over the 50 MB cap; bulk 2H-MoSe2/WSe2 with optB88vdW c-axis would give a homo-stack interlayer distance). I scanned 2DMatPedia and JARVIS_DFT_2D: no pure MoSe2/WSe2 bilayer (only Mo3Se4/Se4W3 and 32-atom supercells), so the conclusion is probably right for heterobilayers, but it is not shown in the report. The claim should read 'not found in the datasets examined'.
2. (major, process) Deliverable paths differ from the assigned ones (docs/designs/EXCITON_FLUID_HF_GNN_GATE.md, python/hf_*.py, results/hf_gate/ do not exist); everything is in exploration/exciton/hf_gate/. Disclosed by the worker, but the orchestrator must pick up the right paths.
3. (minor) G5 is hard-coded pass=False in the script, not computed from the file (the null-column evidence is only in a reason string). G2 passes with 1 entry each; 3 further 3-atom MoSe2/WSe2 entries each exist (non-2H presumably) and are not discussed.
4. (minor) 'Metal-metal' reading of Torun's 6.42 A and Gillen's interlayer distance is an interpretation (disclosed). Gillen's 3.290 for d/a is approximate.
5. (minor) Licence for MACE/ALIGNN items not read from licence texts (disclosed); the 'ASL' reading is unverified. MACE/ALIGNN claims about what they predict were not re-verified by me.
6. (minor) The G4 pass compares a PBE value with experiment bulk values at up to 1.13%, so 'agrees within about 1.1%' is accurate but says nothing about the 2% threshold's meaning; threshold was pre-registered, fine.
