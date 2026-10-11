# Experiments A and B: Bravais lattices and non-Bravais cells in 3D (2026-10-11)

Pre-registration: `../PREREG.md` (committed before any run, not edited). Code in this directory; raw records
`A_records.jsonl` (300 starts x 29 points), `B_records.jsonl` (see restart counts below), reference energies `B_refs.json`.
Nothing here claims a theorem. All energies are per particle at unit number density.

## Verdicts

| Gate | Verdict | Numbers |
|---|---|---|
| A1 (Bravais global minimiser = lower of FCC/BCC, >= 95 % of points) | **PASS** (5 of the 29 points, Gaussian a <= 0.46, are degenerate in double precision so passing there is vacuous; 24/29 non-degenerate, still >= 95 %) | 29/29 points; nothing lower than FCC/BCC found in 8700 starts |
| B1 (random restarts find best reference: >= 50 % for N <= 4; >= 10 % for N = 16) | **FAIL for N <= 4 under the strictest reading ("every gated cell must pass"; median hit fraction 0.76 for N=2, 0.66 for N=4 would pass a pooled reading)**, PASS for N = 16 (40 restarts per cell) | N<=4: 49/58 (point,N) cells pass, 9 fail with 39-49 % (all near-misses); N=16: 29/29 pass, min 25 % |
| B2 (non-reference structure below min(FCC,BCC,HCP,A15) by > 1e-8) | **no discovery** | 0 candidates in 9 860 restarts (145 cells) |

Two qualifications, stated plainly. (i) A1 is a statement at the 13-point-per-family registered grid and with a 1e-9
relative tolerance; for 5 Gaussian points (a <= 0.46) FCC and BCC are numerically degenerate (|dE|/E < 1e-9, below 1e-15 for
a <= 0.32), so "the lower of FCC and BCC" is decided there by exact duality, not by the double-precision numbers.
(ii) The B1 failure is a failure of the registered threshold, not evidence of a missed structure: at every failing cell the
best reference is FCC or BCC and the shortfall is caused by many distinct, nearly degenerate local minima (stacking variants,
HCP, FCC/BCC supercells) that the random search lands in with comparable probability.

## Engine verification (done before any run; `verify.py`, `verify.jsonl`, `tails_and_recheck.py`)

* Analytic gradients (cell + positions) vs central differences, all kernel kinds: max abs error 2e-9 (scale 0.03-4e4).
* Gaussian: FCC, BCC, SC energies vs closed-form theta-function expressions (independent code, 13 values of a):
  worst relative deviation 4.5e-12, located at a = 10 where E ~ 3e-5 and the theta formula itself suffers cancellation in
  0.5(theta^3-1); the engine agrees with the theta formula to <= 3e-13 elsewhere. Real-space vs reciprocal-space branch
  (forced) agree to 1e-14.
* Riesz (s = 4,6,12) and Yukawa (k = 0.1, 1, 10) on FCC/BCC/HCP/A15: independent of splitting parameter tau in {1.5,3,6}
  and cutoff x_c in {55,70} to <= 1e-13; vs brute-force direct sum (radius 30-45) plus continuum tail: agree to 1e-14 when the
  tail is negligible (Riesz s=12, Yukawa k >= 1), to 1e-8..1e-5 where the continuum tail itself is the limit (Riesz s=4,
  Yukawa k=0.1; the direct sum there converges only algebraically/slowly).
* Riesz s = 4, 6, 12 vs a separate scipy (gammaincc, recursion for negative order) Ewald implementation: 1e-15.
* Cutoffs (tau = 3, x_c = 55 for Yukawa/Riesz; Gaussian x_c = 45, purely reciprocal for a < 2.5 else purely real):
  tail bound beyond cutoff, computed by integration of the continuum density (`cutoff_tails.json`): real part
  <= 7.6e-16 |E|, reciprocal part <= 2.7e-19 |E| (target was 1e-12). r_cut = sqrt(x_c/tau) = 4.28; g_cut = sqrt(4 tau x_c) = 25.7
  (Yukawa/Riesz); per-kernel values in `cutoff_tails.json`.
* 300 random stored B records re-evaluated with tau = 1.7, x_c = 75: worst deviation 4e-12 (storage rounding of coordinates).
* Reference geometry: C15 (24-atom Fd-3m cell) shortest bond / a = 0.3536 = sqrt(2)/4 (Cu-Cu), Mg-Cu sqrt(11)/8; A15 0.559.

## Experiment A: Bravais lattices

300 random starts per (kernel, parameter), minimisation over unit-volume lattices (9-parameter basis, volume-normalised,
greedy Minkowski re-reduction every 60 L-BFGS iterations; the energy is lattice-invariant, so reduction is exact).

| kernel | param | E_FCC | E_BCC | lower | (E_F-E_B)/E | % starts at ref | pass |
|---|---|---|---|---|---|---|---|
| gauss | 0.1 | 87.54299614 | 87.54299614 | BCC (tie<1e-9) | 1.623e-16 | 100 | yes |
| gauss | 0.1468 | 49.01021513 | 49.01021513 | BCC (tie<1e-9) | 2.900e-16 | 100 | yes |
| gauss | 0.2154 | 27.34163998 | 27.34163998 | BCC (tie<1e-9) | 2.599e-16 | 100 | yes |
| gauss | 0.3162 | 15.15650472 | 15.15650472 | BCC (tie<1e-9) | 7.032e-16 | 100 | yes |
| gauss | 0.4642 | 8.304299615 | 8.304299615 | BCC (tie<1e-9) | 5.647e-11 | 100 | yes |
| gauss | 0.6813 | 4.451022796 | 4.451022216 | BCC | 1.304e-07 | 100 | yes |
| gauss | 1 | 2.284342296 | 2.284296878 | BCC | 1.988e-05 | 100 | yes |
| gauss | 1.468 | 1.070047152 | 1.069582889 | BCC | 4.341e-04 | 100 | yes |
| gauss | 2.154 | 0.4142453379 | 0.4133839616 | BCC | 2.084e-03 | 99 | yes |
| gauss | 3.162 | 0.1127583979 | 0.1127767508 | FCC | -1.628e-04 | 49 | yes |
| gauss | 4.642 | 0.01733864224 | 0.01782246467 | FCC | -2.790e-02 | 100 | yes |
| gauss | 6.813 | 0.00112284561 | 0.0012610198 | FCC | -1.231e-01 | 100 | yes |
| gauss | 10 | 2.024810514e-05 | 2.739536326e-05 | FCC | -3.530e-01 | 100 | yes |
| riesz | s=4 | 7.981065741 | 7.985940123 | FCC | -6.107e-04 | 79 | yes |
| riesz | s=6 | 3.613480261 | 3.630716405 | FCC | -4.770e-03 | 96 | yes |
| riesz | s=12 | 1.516485025 | 1.600295553 | FCC | -5.527e-02 | 100 | yes |
| yukawa | 0.1 | 626.9237458 | 626.9236565 | BCC | 1.424e-07 | 55 | yes |
| yukawa | 0.1468 | 290.2674896 | 290.2674008 | BCC | 3.061e-07 | 53 | yes |
| yukawa | 0.2154 | 134.0277175 | 134.0276296 | BCC | 6.557e-07 | 55 | yes |
| yukawa | 0.3162 | 61.53939433 | 61.53930853 | BCC | 1.394e-06 | 53 | yes |
| yukawa | 0.4642 | 27.93806309 | 27.9379817 | BCC | 2.913e-06 | 55 | yes |
| yukawa | 0.6813 | 12.40348875 | 12.40341656 | BCC | 5.820e-06 | 50 | yes |
| yukawa | 1 | 5.275382987 | 5.275329259 | BCC | 1.018e-05 | 48 | yes |
| yukawa | 1.468 | 2.070745351 | 2.070725743 | BCC | 9.469e-06 | 46 | yes |
| yukawa | 2.154 | 0.702630478 | 0.7026633053 | FCC | -4.672e-05 | 57 | yes |
| yukawa | 3.162 | 0.1844182267 | 0.1845023138 | FCC | -4.560e-04 | 66 | yes |
| yukawa | 4.642 | 0.03126655383 | 0.03135124509 | FCC | -2.709e-03 | 82 | yes |
| yukawa | 6.813 | 0.002601376341 | 0.002634554196 | FCC | -1.275e-02 | 98 | yes |
| yukawa | 10 | 7.158031668e-05 | 7.501326293e-05 | FCC | -4.796e-02 | 100 | yes |

A1: 29/29 = 100.0% -> PASS

Starts column: fraction of the 300 starts ending within 1e-9 of min(FCC,BCC).

### FCC <-> BCC crossover (continuous parameter, `A_crossovers.json`)

* **Gaussian e^(-a r^2)**: single crossover at a* = 3.1415926535899 = pi (to 3e-14). This is exact: Poisson summation maps
  Theta_FCC(a) to (pi/a)^(3/2) Theta_BCC(pi^2/a) because FCC* = BCC at unit covolume, so FCC and BCC coincide at the
  self-dual point a = pi. BCC lower for a < pi, FCC lower for a > pi.
* **Yukawa e^(-k r)/r**: single crossover at k* = 1.71792 (relative to unit density): BCC lower for k < k*, FCC lower for
  k > k*. The gap is small: |E_FCC-E_BCC|/E ~ 1e-7 (k=0.1) to 1e-5 (k~1).
* **Riesz r^(-s)**: FCC is lower on the whole scanned range s in [3.05, 30] (scipy-based Epstein-zeta evaluator, no sign
  change); registered grid points s = 4, 6, 12 all FCC. No crossover for s > 3 in the scanned range.
* Non-lattice winners (Bravais): none. The minimiser over all 8700 starts is always FCC or BCC (or equal energy within 1e-9).
  Other local minima of the lattice energy, where present, are higher (`n_distinct_minima` in `A_summary.json`).

### Exploratory (not registered) `hcp_scan.py`
HCP and DHCP (relaxed c/a) vs min(FCC,BCC) on a 61-point grid per family: never below by more than 1e-9; the smallest
(HCP - ref)/|E| is 3.6e-16 (Gaussian, degenerate regime) and 1.9e-7 (Yukawa k = 0.1, DHCP).

## Experiment B: non-Bravais periodic cells

Restarts per (kernel, parameter, N): **N = 2, 4: 100; N = 8: 60; N = 12, 16: 40** (reduced from the registered 100 for time,
see Deviations). 29 parameter points x 5 values of N = 145 cells, 9 860 restarts in total.
Starts: random cell (near cubic, volume N) and random-sequential-addition positions with minimum separation 0.55
(to avoid r^-12 overflow); L-BFGS-B on cell + fractional positions with periodic cell re-reduction.
References (each relaxed with the same minimiser from the ideal geometry, so HCP c/a is optimised): FCC, BCC, HCP (N=2),
diamond (N=2), A15 (N=8), C15 Laves (24-atom conventional cell = 4 primitive cells of 6 atoms; counted as representable
for N a multiple of 6, i.e. N = 12 only). A reference is "best known" at N if it is the lowest among references that fit in
an N-point cell (primitive atom count divides N).

Best reference at every one of the 29 parameter points is FCC, BCC or HCP (exactly the Experiment A winner; HCP is listed
when it is below FCC/BCC by < 1e-15 in the degenerate Gaussian regime). A15, C15 and diamond are never below
min(FCC,BCC); A15 comes within 1e-8 of FCC/BCC only for Gaussian a <= 0.46, C15 only for a <= 0.22, diamond for a <= 0.32 (the degenerate regime).

B1 (N<=4, >=50%): 49/58 gated points pass -> FAIL
   fail: gauss 3.1622776601683795 N 2 best FCC frac 0.42
   fail: gauss 3.1622776601683795 N 4 best FCC frac 0.39
   fail: yukawa 0.31622776601683794 N 4 best BCC frac 0.47
   fail: yukawa 0.6812920690579611 N 2 best BCC frac 0.49
   fail: yukawa 0.6812920690579611 N 4 best BCC frac 0.46
   fail: yukawa 1.0 N 4 best BCC frac 0.47
   fail: yukawa 1.467799267622069 N 4 best BCC frac 0.4
   fail: yukawa 2.1544346900318834 N 2 best FCC frac 0.43
   fail: yukawa 2.1544346900318834 N 4 best FCC frac 0.42
B1 (N=16, >=10%): 29/29 gated points pass -> PASS
N=2: points=29, best ref counts: {'BCC': 14, 'HCP': 3, 'FCC': 12} median frac_hit=0.76, min=0.42
N=4: points=29, best ref counts: {'BCC': 14, 'HCP': 3, 'FCC': 12} median frac_hit=0.66, min=0.39
N=8: points=29, best ref counts: {'BCC': 14, 'HCP': 3, 'FCC': 12} median frac_hit=0.60, min=0.32
N=12: points=29, best ref counts: {'BCC': 14, 'HCP': 3, 'FCC': 12} median frac_hit=0.53, min=0.35
N=16: points=29, best ref counts: {'BCC': 14, 'HCP': 3, 'FCC': 12} median frac_hit=0.55, min=0.25

B2 candidates (below min(FCC,BCC,HCP,A15) by >1e-8): 0


Full per-cell table (kernel, parameter, N, best reference, hit fractions at 1e-8 and 1e-6, number of distinct final energies):
`B_analysis.txt`. Per-restart records including final cell and coordinates: `B_records.jsonl`.

### B1 failures (N <= 4) in detail
Gaussian a = 3.16 (the FCC=BCC self-dual point, N = 2: 42 %, N = 4: 39 %), Yukawa k = 0.32 (N=4: 47 %), 0.68 (N=2: 49 %,
N=4: 46 %), 1.0 (N=4: 47 %), 1.47 (N=4: 40 %), 2.15 (N=2: 43 %, N=4: 42 %). All are at parameters where FCC, BCC and HCP/DHCP
are within 1e-5 of each other, so the shortfall is plausibly due to the search splitting between near-degenerate basins (not diagnosed structure by structure; the 1e-6 hit fractions in B_analysis.txt show the near-degenerate remainder). The registered threshold is
not met; I do not reinterpret it.

### B2
No restart in any cell reached a structure below min(FCC,BCC,HCP,A15) by more than 1e-8 relative. `B2_candidates.json` is
empty, so no independent re-minimisation was needed (`verifyB2.py` written but not exercised on data). Nothing
non-lattice wins anywhere, including near the FCC/BCC crossovers (the natural place for an intermediate structure to appear).
Caveat: coverage at N=16 is 40 restarts per cell, and only N <= 16 cells were searched; absence of a candidate is not a proof.

## Deviations and incidents (dated 2026-10-11)

1. **Engine bug (first A run, invalid)**: the line search can cross det A0 = 0, giving NaN cells whose "energy" was read as 0.
   Fix: inversion symmetry for det < 0 and a guard returning 1e8 for degenerate cells. Original records kept in
   `run0_buggy/` (`A_records.jsonl`, copy taken mid-run, and the code before the fix).
2. **Overlapping A runs**: the buggy run was still alive when the fixed run started; both wrote `A_records.jsonl`. I killed
   both by PID; the corrupted file is kept as `run0_buggy/A_records_second_run_corrupted_by_overlap.jsonl`.
3. **Hung A run**: with the fix a third run hung on two points (Yukawa k=6.8, Riesz s=12) in extremely skewed cells reached by
   a line search (cost of the lattice enumeration grows without bound). Added a cost guard (> 6e4 lattice vectors -> energy 1e8,
   no gradient). Files kept: `run0_buggy/A_records_third_run_hung_idx24_28.jsonl`. The reported A results are the fourth run,
   with the final code. The guard only fires in cells that are never near a minimum.
4. **Restart reduction in B**: a first B run with 100 restarts for all N was aborted after 4 cells (N=16 Gaussians took up to
   324 s per cell, projected > 80 min) and kept as `run0_buggy/B_records_aborted_nrest100_first4_N16.jsonl`. Final: N=8: 60,
   N=12: 40, N=16: 40 restarts. The N <= 4 cells have the full 100.
5. **Parametrisation**: "Niggli-reduced parametrisation" implemented as a free 9-parameter basis with exact greedy Minkowski
   re-reduction every 60 iterations (energy invariant); starts sample the reduced Gram region (lengths log-normal, angles 60-120).
6. **Riesz**: the numba engine supports integer s/2 only (s = 4, 6, 12 as registered); the continuum-s crossover scan
   used a separate scipy implementation, verified against the engine at s = 4, 6, 12 to 1e-15.
7. **Random start positions** use a minimum-separation 0.55 rejection (not plain uniform) so that r^-12 stays finite.
8. **B1 interpretation**: evaluated per (parameter, N) cell, "gate passes iff every gated cell passes"; gated cells =
   cells whose best reference is FCC/BCC/HCP (all of them). Per-cell numbers are in the table so other readings can be applied.
   N = 8, 12 are not gated by the registration (reported only).
9. **Lattice-sum tolerance** at the registered 1e-12|E| was met with large margin (above). Gaussian a <= 0.46 energies of
   FCC, BCC, HCP, A15, C15, diamond coincide to 1e-9 and below: the Gaussian-regime "winner" there is not resolvable in double
   precision, so no structural claim is made for a <= 0.46.
