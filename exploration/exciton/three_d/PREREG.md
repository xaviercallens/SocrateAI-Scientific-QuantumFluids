# 3D programme, round 1 (pre-registration, 2026-10-11)

Framing (stated before any run): this round does **not** "solve 3D". No theorem is claimed. It measures, for completely
monotone (CM) radial kernels f(r²), where in 3D the structure problem is easy (Bravais lattices), where it is not (non-Bravais
cells), what the optimiser reliably finds, and whether a hybrid mesh generator improves on CVT. Known literature, to be checked
not assumed: no universally optimal configuration is expected in R³ (FCC and BCC trade places as the kernel parameter varies).

All energies per particle at unit number density, periodic; kernel list K = Gaussian e^{-a r²} (a ∈ logspace(−1,1,13)),
Yukawa e^{-k r}/r (k ∈ logspace(−1,1,13)), Riesz r^{-s} (s ∈ {4,6,12}); lattice sums to a cutoff giving tail < 1e-12·|E|
(report cutoff and tail bound).

## Experiment A — Bravais lattices in 3D
Minimise over unit-volume 3D lattices (Niggli-reduced parametrisation, 300 random starts per kernel/parameter).
Gate A1: for ≥ 95 % of (kernel, parameter) points the global Bravais minimiser equals the lower of FCC and BCC (energy
difference ≤ 1e-9 relative). Report: crossover parameters FCC↔BCC, and every point where something else wins.

## Experiment B — non-Bravais periodic cells
N ∈ {2, 4, 8, 12, 16} points per cell, free cell shape (unit volume per particle), 100 random restarts per
(kernel, parameter, N), L-BFGS on positions + cell. Reference set: FCC, BCC, HCP (N=2), A15 (N=8), diamond (N=2, expected
worse), C15 Laves (N=12... A+B sublattices equal weight, kernel is single-species).
Gate B1: random-restart search finds the best known reference (energy within 1e-8 relative) in ≥ 50 % of restarts for N ≤ 4,
and in ≥ 10 % for N=16 at the parameter points where FCC/BCC/HCP are best.
Gate B2 (discovery): any structure lower than min(FCC,BCC,HCP,A15) by > 1e-8 relative is reported with its coordinates and
the number of restarts reaching it; verified by independent re-minimisation before it is called a finding.

## Experiment C — curvature: S³
N = 120 on S³ (unit sphere) with chordal kernels in {Gaussian a ∈ {0.5,1,2,4}, Coulomb 1/chord, log-energy}; 50 random
starts, L-BFGS on the sphere. Known comparator: 600-cell is universally optimal for N=120 (Cohn–Kumar 2007, a proved result);
also N = 24 (24-cell, not proved universally optimal; report).
Gate C1: ≥ 90 % of starts reach the 600-cell energy within 1e-8 relative for every kernel.
Also report: smallest N ≤ 12 … 48 (even) for which random restarts fail to find a unique minimum (frustration count).

## Experiment D — hybrid 3D mesh (continuation of E3, paper IV)
Same protocol and seeds as E3 (`dimlift/mesh3d.py`, registered 30 test seeds disjoint from dev seeds): CM relaxation followed
by 20 CVT (Lloyd) iterations versus CVT alone with equal total iterations. Metric: 5th percentile of the radius ratio ρ.
Gate D1: hybrid ρ_p5 median ≥ CVT ρ_p5 median **and** wins ≥ 20 of 30 paired seeds. Report paired difference ± s.e.

Each experiment: code + raw records + RESULTS.md in `exploration/exciton/three_d/<A|B|C|D>/`, deviations disclosed in a dated
section, negative results kept. Independent review before any deposit. Nothing here uses the unrefereed planar theorem.
