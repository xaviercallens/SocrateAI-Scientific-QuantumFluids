# hf_extract.py output (auto-generated)

## Gates

- G1_source: PASS
- G2_content: PASS
- G3_stack: FAIL
- G4_lattice_constant: PASS
- G5_excitonic_content: FAIL

## Monolayers read from the dataset (G2, G4)

| material | entry | a (A) | d_XX (A) | PBE gap (eV) | max abs dev from 5-6 lit. a (%) | spread all values (A) |
|---|---|---|---|---|---|---|
| MoSe2 | c2db_atoms_3150 | 3.3197 | 3.338 | 1.321 | 0.97 | 0.0317 |
| WSe2 | c2db_atoms_3118 | 3.3190 | 3.359 | 1.238 | 1.13 | 0.0370 |

## Interlayer distance d of MoSe2/WSe2 (LITERATURE, not HF)

| source | d (A, metal-metal) | a (A) | d/a | method | where |
|---|---|---|---|---|---|
| Gillen-Maultzsch AA' | 6.512 | 3.290 | 1.979 | PBE+D3 relaxed (theory) | 10.1103/PhysRevB.97.165306, Fig. 1 |
| Gillen-Maultzsch AB | 6.473 | 3.290 | 1.967 | PBE+D3 relaxed (theory) | 10.1103/PhysRevB.97.165306, Fig. 1 |
| Gillen-Maultzsch AA | 7.097 | 3.290 | 2.157 | PBE+D3 relaxed (theory) | 10.1103/PhysRevB.97.165306, Fig. 1 |
| Torun et al. A-A' | 6.420 | 3.288 | 1.953 | LDA relaxed at experimental a (theory) | 10.1103/PhysRevB.97.245427, Fig. 1b |

range all: 6.420-7.097 A; commensurate stackings: 6.42-6.51 A (1.42 % of mean)

## Conversion example

d = 6.512 A (d/a = 1.979), D/d = 10 -> D = 65.12 A, epsilon = 4.5:
U(0) = 4 pi d (1-d/D) e^2/eps = 235.67 eV A^2 (= 73.649 x e^2/eps in A)
