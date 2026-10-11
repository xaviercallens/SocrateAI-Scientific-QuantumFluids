# Hugging Face data and GNNs as inputs to the gated exciton model: validity gate (2026-10-11)

**Verdict: the gate FAILS for the two quantities the model needs (electron-hole separation d of the heterobilayer, and an
exciton binding energy / dielectric environment).** One small permissive dataset passes the source and monolayer gates and
reproduces the in-plane lattice constant to 1.1 % of the published values; it contains no bilayer and nothing excitonic.
Pre-registration: `PREREG.md` (commit 9cf8995, before `hf_extract.py` was first run). Script and outputs: `hf_extract.py`,
`results/hf_gate_results.json`, `results/hf_gate_tables.md`. Hub search log: `results/hf_hub_search_log_2026-10-11.txt`.
Disclosure: the one candidate file was opened interactively before the pre-registration was written (stated in `PREREG.md`).
No GNN was run, nothing was uploaded, no token was used (anonymous read-only hub API and public file URLs).

## Step 1. What exists (all read on 2026-10-11)

Hub API (`https://huggingface.co/api/{models,datasets}?search=...`; log in `results/`). Name search is substring-only, so
absence of a hit means only "no repo with that string in its name".

| item | repo | licence (card) | content as read |
|---|---|---|---|
| (a) 2D structures, monolayers | `colabfit/JARVIS_C2DB` (1.98 MB co_0.parquet + 19 kB ds.parquet) | CC-BY-4.0 | 3520 single-layer entries, 17 990 atoms, 61 elements, GPAW PBE, properties: energy, electronic band gap; source C2DB, https://doi.org/10.1088/2053-1583/aacfc1; ColabFit DOI 10.60732/37c26dae |
| (a) bulk/3D crystals | `colabfit/Materials_Project` (1M-10M entries), `materials-toolkits/materials-project` (MIT), `atomind/alexandria` (CC-BY-4.0; has 1D/2D/3D folders, 375 files), `facebook/OMAT24` (CC-BY-4.0), `nimashoghi/matbench_jdft2d_fold0..4` (no licence field) | as listed | bulk PBE(+U) structures/energies, large; not opened (size) except by listing; Matbench jdft2d is exfoliation energy of 2D materials |
| (b) excitons / optical gaps | none found | | searches `exciton`, `MoSe2`, `WSe2`, `transition metal dichalcogenide` return no dataset/model with excitonic content (MoSe2: one unrelated model repo `jzone/mose22`, empty) |
| (c) MACE | `mace-foundations/mace-mp-0` (card header `license: mit`), `mace-mpa-0` (mit), `mace-mh-1` (`license: other`); mirrors `atomind/mace-mp-medium`, `cyrusyc/mace-mp*` | MIT / "ASL" per https://github.com/ACEsuit/mace-foundations | MP-0 trained on MPtrj (PBE+U); MPA-0 on MPtrj+sAlex; OMAT-0 / MH-1 on OMAT24 (PBE+U) (+OMOL, OC20, MatPES, SPICE heads for MH-1, per the HF card) |
| (c) ALIGNN | HF: user-contributed only (`crhysc/alignn-csp-angular-ablations`, MIT; `DreamLufei/invDesMobility-alignn-bandgap-nonmetal`, `license: other`; `shreyaspullehf/...tc-prediction`, MIT); official models are on Figshare per https://github.com/usnistgov/alignn | not shown on the page | JARVIS-DFT (about 75 000 materials); property models include formation energy, band gap (OptB88vdW, MBJ), exfoliation energy, DFPT dielectric constant; the page lists no exciton, optical-gap or interlayer-distance model |

What the force-field GNNs predict: total energy and forces (the MACE-MH-1 card lists phonon, bulk and shear modulus,
free-energy benchmarks). Not excitons. ALIGNN property models predict a (DFT) band gap; they are regressions on the
JARVIS-DFT labels, not many-body calculations. The ColabFit `JARVIS_C2DB` card lists the properties "energy, electronic band gap".

## Step 2. Validity

Inputs the gated kernel needs: (i) d, in Angstrom and d/a; (ii) dielectric environment (hBN spacer, gate distance D,
epsilon of the layers); (iii) exciton mass and binding energy.

| gate | result | evidence |
|---|---|---|
| G1 source (read-only, < 50 MB, permissive, hashed) | PASS | CC-BY-4.0, 1.99 MB, sha256 in `hf_gate_results.json` |
| G2 2H MoSe2 and WSe2 monolayers present | PASS | entries `c2db_atoms_3150` (MoSe2) and `c2db_atoms_3118` (WSe2), identified by geometry (hexagonal cell, chalcogens vertically aligned) |
| G3 any MoSe2/WSe2 bilayer or heterobilayer, so d can be read | **FAIL** | 0 of the Mo/W-Se entries has two metal planes more than 5 A apart; maximum 12 atoms per entry; the database is C2DB single layers |
| G4 lattice constant within 2 % of >= 2 independent published values | PASS | MoSe2 3.3197 A, WSe2 3.3190 A; largest deviation from five or six published values 0.97 % and 1.13 %; equals the PBE value of Kormanyos et al. (3.319, 3.316), is 0.9-1.0 % above bulk experiment (3.282-3.299) |
| G5 any excitonic/optical quantity | **FAIL** | only PBE energy and PBE band gap; no GW, BSE, optical gap, dielectric tensor, mass |

### Why a ground-state model cannot give E_b, and what a predicted d is worth
* A DFT/GNN ground-state model yields E_total(R), forces, a Kohn-Sham gap. The exciton binding energy is the difference
  between the quasi-particle gap and the optical transition: it requires GW (quasi-particle gap) and BSE (electron-hole),
  or experiment, and it depends on the environment: the values read span a factor 3.4 (table below).
* Interlayer distance **is** a ground-state quantity, so a MACE/ALIGNN relaxation could in principle supply it. But
  (i) the training sets read (MPtrj, OMAT24, JARVIS-DFT) are bulk crystals with PBE(+U) energies; PBE has no dispersion
  and the MACE card does not say whether D3 is included, so the vdW gap of a heterobilayer is exactly what the training
  labels describe poorly; (ii) the published first-principles values already available differ by 1.4 % between commensurate
  stackings and by 9 % for the AA stacking (table below), so a GNN value is only useful if its error is shown to be below
  that, which needs a held-out check against those references that has not been made; (iii) d enters U(0) linearly, so a
  few-per-cent error in d is a few-per-cent error in the amplitude, much smaller than the factor 3.4 from epsilon and E_b.
  Conclusion: d is the one input a ground-state model might supply, and it is also the one the literature already supplies
  to about 1.5 %; the inputs that carry the uncertainty (epsilon, E_b, reduced mass) are not ground-state quantities.

## Step 3. Table and conversion (literature, not HF output; G3 failed)

Numbers hand-entered from the PDFs read (arXiv extracts, figure checked by rendering the Torun et al. Fig. 1).

| source | d metal-metal (A) | d/a | method |
|---|---|---|---|
| Gillen & Maultzsch AA' (https://doi.org/10.1103/PhysRevB.97.165306, Fig. 1 and text) | 6.512 | 1.979 | PBE+D3 |
| same, AB | 6.473 | 1.968 | PBE+D3 |
| same, AA | 7.097 | 2.157 | PBE+D3 |
| Torun et al. A-A' (https://doi.org/10.1103/PhysRevB.97.245427, Fig. 1b; chalcogen-chalcogen gap 3.12 A) | 6.42 | 1.953 | LDA at experimental a = 3.288 A |

Spread: 6.42-6.51 A for the commensurate stackings (1.4 % of the mean), 6.42-7.10 A including AA. "Metal-metal" is my
reading of the figures (the 6.4-6.5 A values equal bulk c/2 scale and Torun's Fig. 1 shows the dashed lines at the metal
planes); with a hBN spacer of thickness t the model's d is d_MM + t (t left as a free parameter, no hBN number was read).
The paper's d is "electron-hole layer separation"; taking the metal-plane distance ignores the finite thickness of the
wavefunctions (a model choice, not a measurement).

Conversion of one example (script default): d = 6.512 A, D/d = 10, D = 65.12 A, uniform epsilon = 4.5
(the kappa_hBN used by Stier et al., https://doi.org/10.1103/PhysRevLett.120.057405, arXiv:1709.00123):
U(0) = 4 pi d (1 - d/D) e^2/epsilon = 73.65 x e^2/epsilon [A] = **235.7 eV A^2** (e^2 = 14.3996 eV A). Caveats: uniform-epsilon
formula (review M2: for hBN stacks use the piecewise factor); epsilon = 4.5 is a Keldysh-model input of a different
experiment, not the dielectric constant of a device; the d value is a vacuum DFT-D3 result.

### Binding energies and mass: the spread an input would have to resolve

| quantity | value | environment, method | source |
|---|---|---|---|
| E_b MoSe2 | 0.55 +/- 0.04 eV | on bilayer graphene, STS + PL | arXiv:1404.2331 (https://doi.org/10.1038/nmat4061) |
| E_b MoSe2, WSe2 | 0.48, 0.46 eV | isolated monolayer, as quoted | Gillen & Maultzsch |
| E_b MoSe2/WSe2 intralayer, interlayer | 0.41, 0.32 eV | vacuum, GW-BSE | Torun et al. |
| E_b interlayer X0/Y0 | about 0.25 eV | vacuum, GW-BSE | Gillen & Maultzsch |
| E_b WSe2 1s | 0.161 eV | hBN/hBN, Keldysh model with kappa = 4.5, m_r = 0.20 m0 | Stier et al. |
| m_r WSe2 | 0.20 +/- 0.01 m0 | magneto-optics, hBN-encapsulated | Stier et al. |

Ratio max/min of E_b: 3.4. This is the environment and method dependence, the same factor that the model's epsilon and D carry.

## What a valid pipeline would need
1. A heterobilayer structure source: either a database with relaxed MoSe2/WSe2 stackings (C2DB's bilayer sets, Alexandria 2D
   subsets, JARVIS-DFT 2D) read for d(stacking, twist), with the functional and dispersion correction recorded; or a
   relaxation with a force field that has been validated on vdW gaps of TMD bilayers against the DFT-D3/experimental values
   above (a held-out test with a stated tolerance, e.g. 0.1 A, chosen before the run).
2. Dielectric environment from a layered-dielectric model fed with measured hBN permittivities (in-plane and out-of-plane
   separately) and layer thicknesses, using the piecewise-epsilon factor, not a single epsilon.
3. E_b and m_r from GW-BSE of the specific stack (including the substrate/encapsulation) or from experiment on the stack
   (Rydberg series, magneto-optics), never from a ground-state GNN; report them with the environment attached.
4. A decision rule: the model's amplitude U(0) depends linearly on d and on 1/epsilon; propagate the table spread
   (d: 1.4-9 %, epsilon/E_b: factor 3.4) before claiming any quantitative comparison.
5. Do not label any model output as a measurement; keep literature and HF-derived tables in separate files (as here).

## Limits of this check
Only `colabfit/JARVIS_C2DB` was opened and analysed. The Alexandria 2D and Materials Project mirrors were listed, not
downloaded (size); they may contain MoSe2/WSe2 bilayers, which this gate does not exclude. No MACE or ALIGNN inference was
run, so the 'would a GNN d be good enough' question is argued, not tested. Licences were read from card headers or the one
GitHub page, not from the licence texts (ASL not expanded). Literature numbers come from the arXiv versions of the papers.
