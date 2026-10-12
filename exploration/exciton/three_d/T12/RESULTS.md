# T2 and T1: Gaussian mixtures across the self-dual point; formal self-duality (2026-10-12)

Pre-registration: `../PREREG_round2.md` sections T2 and T1 (commit 51a85b1, not edited). Engine: `../AB/` (Ewald lattice
sums, L-BFGS minimiser, random starts, reference structures) reused unchanged except for one appended class
(`MixKernel` in `../AB/lattsum.py`, see Engine check). All energies per particle at unit number density. Nothing here is a
theorem; negative results are kept. No network access in this session: Cohn-Kumar-Schuermann (CKS) 2009 was NOT read here;
two facts from it were communicated by the parent session (marked as such below) and the formal-duality definition is used
"as implemented here" (`selfdual.py` docstring).

## Verdicts

| Gate | Verdict | Numbers |
|---|---|---|
| T2 (mixture kernel, any configuration below min(E_FCC, E_BCC, E_HCP) by > 1e-8 relative, re-verified) | **negative** (no candidate) | 3 pairs x 5 lambda x 5 N = 75 cells, 5 100 restarts; most negative (E_min - E_bestref)/E over all cells = -1.9e-15 (ties) |
| T1 (formally self-dual non-lattice configuration with 2E(pi) below 0.231536266184 by > 1e-8) | **no candidate, and uninformative**: the search never reaches the acceptance threshold, not even from 1e-3 perturbations of the diamond positive control | 160 random starts (N = 2, 4, 8): 0 accepted, min shell mismatch 19.8 / 7.7 / 1.26; 50 perturbed-control starts: 0 accepted (mismatch 28-73) |

## Engine check (`check_engine.py`, `engine_check.json`, run before any T2/T1 run)

* `MixKernel(a1, a2, lam)` = `Kernel('gauss', a1)` + lam `Kernel('gauss', a2)` as Python objects (energy and gradients are
  linear in the kernel); no existing kernel, numba function or default was modified -- the class was appended.
* Existing Gaussian kernel vs the stored round-1 reference energies (`../AB/B_refs.json`, FCC and BCC, 13 values of a):
  worst relative deviation 0.0 (bit-identical). Registered requirement 1e-12: met.
* MixKernel vs sum of two Kernel evaluations: 0.0; vs brute-force direct sum (radius 12, no tail needed for Gaussians) on
  FCC, BCC, HCP, A15 and a random 4-point cell, 3 pairs x 2 lambdas: worst 4.9e-15 relative; vs the same kernel with
  cutoff x_cg = 70 (instead of 45) and swapped real/reciprocal branches: worst 6.6e-15. Analytic gradients (cell +
  positions) vs central differences: max abs error 1.2e-9 (gradient scale ~ 1).

## T2: Gaussian mixtures f(r) = e^{-a1 r^2} + lambda e^{-a2 r^2}

### lambda* (E_FCC = E_BCC), bisection to 1e-12 (`expT2.py lam`, `T2_lambda_star.json`)

| (a1, a2) | lambda* (bisection) | closed form -dE(a1)/dE(a2) | exact prediction for a1 a2 = pi^2 | bisection iterations |
|---|---|---|---|---|
| (pi/2, 2pi) | 2.82842712475167 | 2.8284271247516 | (pi/a1)^{3/2} = 2 sqrt 2 = 2.828427124746 | 42 |
| (pi/4, 4pi) | 7.999999998137 | 7.999999998123 | (pi/a1)^{3/2} = 8 | 31 (g(mid) = 0 in double precision) |
| (2, 5) | 2.01658526276015 | 2.01658526276016 | n/a (a1 a2 != pi^2) | 42 |

Remarks. (i) E(lambda) is linear in lambda, so the bisection is only a check of the closed form; they agree to 1e-12 (pair 1,
3) and to 2e-12 (pair 2). (ii) For a1 a2 = pi^2 the 3D Fourier transform of e^{-a1 r^2} is (pi/a1)^{3/2} e^{-a2 r^2}, so at
lambda = (pi/a1)^{3/2} the mixture kernel is exactly self-dual (f-hat = f) and E_FCC = E_BCC follows from FCC* = BCC; the
numbers reproduce this. Pair 2's lambda* deviates from 8 by 2.3e-10 relative. *Corrected after review:* the cause is
double-precision cancellation -- the FCC-BCC difference of the a2 = 4pi term is only 4.8e-7 (E_FCC(4pi) = 8.0e-7,
E_BCC(4pi) = 1.28e-6, reviewer's independent sum) against total energies of order 3.5 -- not a 1e-9 size of that term as an
earlier draft said; it is a numerical artefact, not a physical deviation. Pair 1's bisection agrees with 2 sqrt 2 to 1.9e-12. (iii) Consequence for pair 2: the FCC/BCC splitting at lambda*(1 +/- 0.03) is only
~1e-7 relative (`T2_refs.json`), so pair 2 is a weak discriminator between structures (every structure within 1e-6 of the
best reference; the 1e-8 gate is still well resolved, at 1e-15).

### Search (`expT2.py search`, `T2_records.jsonl`, `T2_summary.json`, `T2_analysis.txt`)

Restarts per cell exactly as round 1: N = 2, 4: 100; N = 8: 60; N = 12, 16: 40 (`expB.NREST`); seeds `777 + 1000 idx + N`
with idx = 10 x pair + lambda-index (same rule as `expB.point_task`). Random starts, minimiser, cell reduction and
cutoffs identical to Experiment B (`expB.random_start`, `opt.minimize_structure`, x_cg = 45, tails < 1e-15).
References at each lambda (`T2_refs.json`): FCC, BCC, HCP (c/a relaxed), plus diamond and A15 for information.

Per-cell table in `T2_analysis.txt` (75 rows). Summary:

| pair | lambda/lambda* | best reference | hit fraction at 1e-8 (N = 2 / 4 / 8 / 12 / 16) | min over N of (E_min - E_ref)/E |
|---|---|---|---|---|
| (pi/2, 2pi) | 0.9, 0.97 | BCC | 0.59/0.46/0.53/0.55/0.50 ; 0.52/0.50/0.40/0.53/0.45 | -7e-16 |
| (pi/2, 2pi) | 1 | FCC = BCC (tie to 1e-16) | 0.94/0.88/0.93/0.75/0.88 | -1e-15 |
| (pi/2, 2pi) | 1.03, 1.1 | FCC | 0.33/0.46/0.40/0.35/0.38 ; 0.45/0.45/0.48/0.33/0.42 | -1e-15 |
| (pi/4, 4pi) | 0.9, 0.97 | BCC | 0.60/0.55/0.63/0.72/0.42 ; 0.61/0.57/0.55/0.53/0.45 (1.00/.../0.85 at 1e-6) | -9e-16 |
| (pi/4, 4pi) | 1 | FCC = BCC | 1.00/1.00/0.93/0.95/0.82 | -9e-16 |
| (pi/4, 4pi) | 1.03, 1.1 | FCC | 0.55/0.48/0.55/0.38/0.42 ; 0.58/0.53/0.67/0.50/0.47 | -8e-16 |
| (2, 5) | 0.9, 0.97, 1 | BCC | 0.58/0.44/0.52/0.47/0.45 ; 0.59/0.47/0.38/0.57/0.50 ; 0.90/0.92/0.80/0.80/0.85 | -1.9e-15 |
| (2, 5) | 1.03, 1.1 | FCC | 0.41/0.47/0.50/0.33/0.33 ; 0.55/0.36/0.37/0.45/0.33 | -1.9e-15 |

* **T2 candidates (below min(FCC, BCC, HCP) by > 1e-8 relative): 0** (`T2_candidates.json` empty). Independent
  re-minimisation (`verifyT2.py`: x_cg = 70, swapped real/reciprocal splitting, brute-force sum, perturbed restart,
  Voronoi-volume coexistence test) was therefore not exercised on data.
* Nothing in any cell is below the best reference lattice (most negative relative difference -1.9e-15, ties); in 14 cells
  (pair (pi/4, 4pi), N >= 8) the lowest energy found is above it by up to 3.7e-13 relative (corrected after review; an earlier
  draft said "<= 2e-15 in every cell"). So the FCC/BCC crossover of the
  mixture kernel is crossed without any intermediate non-lattice structure for N <= 16, including at the exactly
  self-dual kernels (pairs 1, 2 at lambda*).
* Hit fractions at the degenerate point lambda* are high (0.75-1.00) because FCC and BCC are then one target; away from it
  they drop to 0.33-0.72 as in round 1 (near-degenerate stacking variants/HCP absorb the rest; `n_distinct` column).
* For pair 3 at lambda* x 1.1 HCP (0.53336458) is below BCC (0.53336865) but above FCC (0.53328095).
* **Coexistence remark (communicated by the parent from CKS 2009)**: at the single-Gaussian self-dual point alpha = pi the
  3D Gaussian-core ground state at rho = 1 is reported to be a Maxwell coexistence of D3 and D3* over
  0.99899854 <= rho <= 1.00100312, with per-particle energy 0.11576766 (half-sum convention), about 4e-6 relative below
  pure FCC/BCC. Our engine's half-sum E_FCC(pi) = E_BCC(pi) = 0.115768133092; (0.115768133 - 0.11576766)/0.115768133 =
  +4.1e-6, consistent with that statement. A fixed-density periodic cell with N <= 16 points cannot represent a
  two-density coexistence (the density contrast is 1e-3 and the interfacial cost is paid per cell), so **no coexistence
  approximant appeared in T2, and none is expected to** (an argument, bulk gain 4e-6 against interface cost, not a demonstration); nothing in T2 bears on the CKS coexistence claim. The analogous
  question for the exactly self-dual mixture kernels (pairs 1, 2 at lambda*) is open and not addressed by this search.

## T1: formally self-dual periodic configurations at alpha = pi

### Definition as implemented (`selfdual.py`)

CKS 2009 Sec. VI (communicated by the parent, not read here): P of density delta and Q of density 1/delta are formal duals
if for every Schwartz f the average pair sum of f over P equals delta times the average pair sum of f-hat over Q; the
radial version depends only on the pair correlations. Implemented at delta = 1, Q = P: Sigma_f(P) = (1/N) sum_{j,k,v}
f(x_j - x_k + v) (diagonal f(0) terms included) must equal Sigma_{f-hat}(P). By Poisson summation this is the identity of
two radial measures: the pair-difference measure mu_P (weights 1/N) and the structure-factor measure nu_P on Lambda*
(weights |S(w)|^2/N^2). Detector (registered functional): the first 40 non-zero shells of each side, mismatch =
sum_s [(r_s^mu - r_s^nu)^2 + (w_s^mu - w_s^nu)^2]; accept if < 1e-10. Note: the prereg text writes |S|^2/N for the
structure-factor weight; the Poisson-consistent weight is |S|^2/N^2 (both give 1 at w = 0 only for N = 1); the N^2 version
is what the controls below confirm.

### Controls (`expT1.py controls`, `T1_controls.json`), reported before any search result

| P | Q | shell mismatch (40 shells) | surrogate M | comment |
|---|---|---|---|---|
| diamond (D3+, unit density) | diamond | 1.1e-26 | 2.6e-29 | **positive control passes** (CKS Prop. 1: D_n^+ formally self-dual for n odd; D3+ = diamond, communicated by the parent); first shells (0.866, 4), (1.414, 12), (1.658, 12), (2, 6) on both sides |
| FCC | BCC | 0.0 | - | FCC and BCC are formal duals of each other (expected: FCC* = BCC at unit covolume) |
| BCC | FCC | 0.0 | - | idem |
| HCP | HCP | 3.2e3 | 8.1e-5 | negative control fails as required |
| FCC | FCC | 3.5e4 | 7.1e-5 | not self-dual (first shell 1.1225 x12 vs 1.0911 x8) |
| SC (Z^3) | SC | 0.0 | 3.5e-29 | self-dual lattice (sanity) |
| bct c/a = 2^{1/4} | itself | 8.8e-30 | 1.4e-29 | isodual fixed point of the Bain path (`../AB/bain_selfdual.py`); 2E(pi) = 0.231925337063, the Bain-path maximum |

Energies at alpha = pi (half-sum convention of the engine): FCC = BCC = 0.115768133092, diamond = 0.201839614314,
SC = 0.141181557930, HCP = 0.115775868722.

**Normalisation of the registered threshold.** The registered E_FCC(pi) = E_BCC(pi) = 0.231536266184 is in the
sum_{v != 0} e^{-pi |v|^2} convention of `../AB/bain_selfdual.py` (theta without the 1/2), i.e. exactly 2 x the engine's
half-sum energy (2 x 0.115768133092 = 0.231536266184). All T1 comparisons below use 2E. (CKS's 0.11576766 is in the
half-sum convention.)

### Search (`expT1.py search`, `selfdual.SelfDualObjective`, `T1_records.jsonl`, `T1_analysis.txt`, `polishT1.py`)

Run 2 (the run used for the verdict) minimises `SelfDualObjective()` with its defaults in `selfdual.py`: 40 relative residuals
1 - X_nu(alpha)/X_mu(alpha) at alpha = pi s, s log-spaced in [0.3, 1] (so each residual tests e^{-alpha r^2} and, through
Poisson, e^{-(pi^2/alpha) r^2}: exponents 0.94-10.5). Starts: 60 (N = 2), 60 (N = 4), 40 (N = 8), `expB.random_start`, seeds
`999 + 1000 N + chunk`, Experiment B minimiser with gtol 1e-13. Acceptance: registered 40-shell mismatch < 1e-10.

| N | starts | accepted | registered mismatch < 1e-6 | min shell mismatch | min surrogate M |
|---|---|---|---|---|---|
| 2 | 60 | 0 | 0 | 19.8 | 3.8e-15 |
| 4 | 60 | 0 | 0 | 7.69 | 6.4e-15 |
| 8 | 40 | 0 | 0 | 1.26 | 7.4e-13 |

The polish stage (`polishT1.py`, least-squares on the shell residuals directly, 8 records) lowered no mismatch below 0.30
(`T1_polish.log`). **Gate T1: 0 candidates.**

**Why this negative carries no information (diagnostics, unregistered, 2026-10-12).**

1. *Surrogate and detector disagree.* The best N = 2 record has M = 3.8e-15 but its first shells are (0.737, 1), (0.906, 1),
   (0.961, 1) on the pair side against (0.737, 0.89), (0.742, 0.12), (0.920, 1.56) on the structure-factor side: the two
   measures are genuinely different. A continuous measure of the difference, the L1 distance between the two cumulative
   distributions on [0, 2.2] (`diagW1T1.py`), is 1.39 (N = 2), 2.40 (N = 4), 0.70 (N = 8) for the best records and 0 for exact
   diamond. So the Gaussian-family identity on this range of exponents is satisfied to 1e-15 by configurations that are not
   formally self-dual: the surrogate does not identify the property (the restricted Laplace transform is ill-conditioned).
2. *The surrogate cannot resolve the known solution's neighbourhood* (`basinT1.py`, `T1_basin.jsonl`). From diamond and from the simple cubic
   lattice written as a 2-point cell, perturbed by eps in {1e-3, 1e-2, 5e-2, 1e-1, 2e-1} (5 draws each), the same minimiser
   ends at M <= 9e-11 in all 50 cases and is accepted in **0/50** (shell mismatch 28-73). *Qualified after review:* at
   eps = 1e-3 the unminimised perturbed start already has M = 3.6e-11 (shell mismatch 30.5), so M <= 1e-10 is not an
   achievement of the minimiser; the surrogate simply cannot resolve a 1e-3 displacement from diamond. Example (eps = 1e-3):
   the CDF distance goes from 0.027 at the start to 0.0088 at the end; the end state is genuinely not self-dual (relative
   residual 1.5e-5 at alpha = 30, reviewer's check). Its shell mismatch is 30 because diamond's systematically absent
   reflections reappear in nu with weights < 5e-5 (above the weight floor 1e-8), have no counterpart in mu, and shift every
   later nu index by 3 (reviewer's diagnosis; splitting of degenerate shells alone does not misalign, since both measures split).
3. *The registered detector is correct but discontinuous.* It returns 1e-26 on the exact controls and O(10) once
   extinct reflections or split shells appear on one side only; the grouping tolerance (1e-6) and weight floor (1e-8) are
   implementation choices, not registered; acceptance at 1e-10 therefore requires an exact
   formally self-dual configuration, which a smooth minimiser of a non-identifying surrogate does not deliver.

Also stale: the comment at `selfdual.py:135-138` ("s in [0.1, 1]"); the defaults actually used are smin = 0.3, smax = 1
(run 3 reproduction). Code left as run.

Reading: T1 is a method failure, not an absence of formally self-dual configurations below FCC/BCC. It is reported as "no
counterexample found with a search shown unable to find the known example". A usable T1 needs either an identifying
objective (e.g. the CDF distance above, or the exact shell equations solved with the shell multiplicities imposed) or an
algebraic enumeration of the CKS constructions; not attempted here.

## Deviations, clarifications and incidents (dated 2026-10-12)

1. **Mixture kernel**: added as an appended class `MixKernel` in `../AB/lattsum.py` composed of two existing Gaussian
   kernels; nothing existing changed (bit-identical reproduction of stored references, above).
2. **lambda* bisection**: performed as registered, although E is linear in lambda; closed-form value recorded alongside.
   Pair 2's bisection terminates on an exact zero of the double-precision residual (bracket collapses) at 7.999999998,
   2.3e-10 below the exact 8 (see T2 remarks).
3. **T2 references**: FCC, BCC, HCP as registered; diamond and A15 added for information only (not in the gate).
4. **T1 definition**: CKS 2009 not read here (no network); the definition is used as implemented (`selfdual.py`) with the
   delta-factor form and the D3+ positive control communicated by the parent. The prereg's "|S|^2/N" was implemented as
   |S|^2/N^2 (Poisson-consistent; the controls confirm it). Only radial test functions are used, which is all an energy
   comparison needs; non-radial formal duality is stronger and was not tested.
5. **T1 optimisation device**: L-BFGS needs a smooth objective, so the search minimises a surrogate -- the self-duality
   identity tested on the Gaussian family (Theta(alpha) = (pi/alpha)^{3/2} Theta(pi^2/alpha), engine energies and
   gradients) -- and acceptance uses the registered 40-shell mismatch. **Run 1 used 16 test functions (scales 1.15-6),
   absolute residuals (which scale like the pair sum, ~e^{-1.3 alpha}, so M ~ 1e-12 carries no information), and was also
   underdetermined for N = 4, 8 (21 and 33 free parameters): the surrogate reached 1e-12
   while the shell mismatch stayed O(1-10).** Its records are kept (`T1_run1_16alpha_records.jsonl`,
   `T1_run1_16alpha_run.log`) and not used for the verdict. Run 2 uses 40 relative residuals at alpha = pi s, s in
   [0.3, 1] (the defaults of `SelfDualObjective` in `selfdual.py`), and a polish stage that minimises the registered shell
   residuals directly (`polishT1.py`). *Correction (2026-10-12, after the session that ran it was compacted): an earlier
   draft of this item said "64 test functions (scales 1.02-40)"; that was a description of an intermediate version. Run 3
   (`T1_run3_records.jsonl`, `T1_run3.log`), run with the file as committed, reproduces 20 run-2 records bit for bit, which
   fixes the configuration actually used.* The comment "64 test functions, 4x cost" next to NSTART in `expT1.py` is stale
   in the same way. Start counts were not registered; run 2 used 60 (N = 2), 60 (N = 4), 40 (N = 8), reduced from run 1's
   100/100/60 for time.
6. **Control typo**: the first controls run built the bct lattice with third row (a/2, a/2, t a) instead of
   (a/2, a/2, t a/2) (wrong lattice; reported mismatch 1993 there). Fixed and rerun; the other seven controls are
   unaffected. The first controls output is preserved at the top of `T1_run1_16alpha_run.log`.
7. **Normalisation of the T1 threshold**: see above (registered 0.231536266184 = 2 x half-sum energy). The `rel_vs_ref`
   field written into T1 records during the runs compared E (half-sum) with the sum-convention threshold and is off by
   a factor 2; `analyzeT1.py` and this file use the corrected comparison.
8. **Coexistence check** (requested by the parent after CKS 2009): `verifyT2.py` includes a Voronoi-volume bimodality
   test for any candidate; no candidate arose, and N <= 16 cells cannot form the D3/D3* coexistence (see T2 remarks).
9. Runtime: T2 25 min (2 processes); T1 run 1 ~8 min; T1 run 2 about 9 min (2 processes); run 3 (reproduction of run 2 with the final code, 20 records, bit-identical M and mismatch, then stopped to free the machine) and the basin diagnostic about 10 min. N = 16 was kept (no budget cut needed).
10. **Diagnostics added after the run** (unregistered): `basinT1.py` (perturbed positive controls) and `diagW1T1.py` (CDF
   distance), see the T1 section; they change no gate, they qualify the T1 negative as uninformative.
11. **F1 stop rule.** F1a failed at every a (see `../F1/RESULTS.md`); by the registered rule T1/T2 are reported as "no
   counterexample found with an unreliable search". For T2 this adds to, and does not replace, the T2 hit fractions above.
