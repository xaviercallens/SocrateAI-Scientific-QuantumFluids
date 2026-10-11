# Dimensional lifting, flexible walls and a 3D mesh baseline: pre-registration (2026-10-11)

Status: REGISTERED BEFORE ANY RUN of `dimlift.py`. These are exploratory classical tests of three ideas from the 2026-10-11
brainstorm (higher-dimensional lift as an optimisation aid, boundary degrees of freedom, CM-relaxed 3D point sets as meshes).
They test numerical heuristics; they say nothing about string theory, excitons, or the universal-optimality theorem.

Engine: own numpy/scipy L-BFGS-B (not the Fenris CVODE engine); containers, wall nodes (spacing 0.5), RSA starts and defect
analysis are those of `exploration/exciton/rust/fenris-gated/python/{geometry,study}.py` (imported unchanged).
Kernels: `dip` = `2/r - 2/sqrt(r^2+d^2)`, d = 0.5; `g3` = gated, D/d = 3 (Poisson series in K0, tabulated).
Shapes: square, hexagon, disc, rect2, lshape, annulus; N_free target 60 (fit_shape, w = 0.5).

## E1. Dimensional annealing
Same RSA 2D starts (NS = 30 per shape and kernel) are relaxed (i) directly in 2D, (ii) lifted to 2+k dimensions, k = 1, 2, with initial
extra coordinates N(0, 0.3^2), pair energy g(sqrt(|dx|^2 + |dw|^2)), wall nodes at w = 0, quadratic confinement
lambda |w|^2 stepped through (0.02, 0.1, 0.5, 2.5, 12.5, 62.5) with 150 L-BFGS iterations per stage, then a 2D polish
(w = 0, up to 2000 iterations). Recorded: final 2D energy, number of distinct minima (1e-6 relative), fraction of starts reaching
the best energy found for that (shape, kernel) over all methods, non-6 free-node count, and function-evaluation counts.
Equal-compute control: `direct` best-of-m restarts with m = eval ratio.
**Gate E1 (lifting helps):** for k = 1 or k = 2, on at least 4 of 6 shapes (dip kernel) the mean final energy is lower than direct by
more than two standard errors, AND the fraction reaching the best energy is not lower; AND this survives the equal-compute control
(best-of-m of direct has a mean not better than lifted). Otherwise: "no demonstrated benefit". No other outcome is pre-judged.

## E2. Flexible wall
Wall nodes (not corners) slide along their ring (arclength parameter), with the wall-wall repulsion included; same starts and
kernels; compare against the fixed-wall direct 2D run. Recorded: energy difference, non-6 count, net charge Q = sum(6 - c).
Expectation (not a gate): sliding lowers the energy by construction (a superset of degrees of freedom is minimised); the
informative outcome is the change in defect count. **Gate E2:** the mean non-6 count decreases by at least 2 on at least 3 of 6
shapes. Q is expected unchanged on shapes where the wall coordination is unchanged (Gauss-Bonnet identity of the Fenris study).

## E3. Periodic 3D mesh baseline
N = 432 points in the unit periodic cube (30 random starts). Relax (a) a CM repulsive kernel `exp(-k r)/r` with k L = 6 (minimum
image), (b) Lloyd/CVT with 40 iterations of 200k Monte-Carlo samples. Delaunay of the 3x3x3 tiling restricted to the central cell.
Metrics: tetra radius ratio `3 r_in / R` and minimum dihedral angle: median, 5th percentile, fraction with radius ratio < 0.3.
**Gate E3:** CM-relaxed 5th-percentile radius ratio exceeds CVT's in at least 24 of 30 paired starts. Otherwise: no advantage.
Not claimed under any outcome: anything about conforming meshes of CAD domains, size grading, or boundary recovery.

## Reporting
All three outcomes are reported whatever they are, with raw jsonl in `results/`. Deviations are dated amendments below.

## Amendment A1 (2026-10-11, after three small development runs of `dimlift.py` on the square, before any registered run)
Development runs (square, dip, seeds 0-5, not used in any result) showed that a point wall leaks in the lifted problem
(15 of 60 nodes ended outside the container), so the lifted runs additionally use (i) a quadratic container penalty
(kappa = 2000) on the in-plane coordinates during every lifted stage and in the first 2D polish, (ii) a projection of
escaped in-plane points to just inside the boundary after every stage, (iii) initial extra coordinates N(0, 0.1^2) (was
0.3^2), and a final unpenalised 2D polish. `direct` and `slide` are unchanged. Energies are reported as total energy including
the constant wall-wall term of the fixed wall (sliding includes its own). **A run with any free node outside the container
after the final polish is a failed run: counted as a failure, its energy excluded from means and from "best energy".** Eval
counts are function+gradient evaluations. Seeds 0..NS-1 are shared across methods. The registered gates are unchanged.

## Amendment A2 (2026-10-11, after one development run of `mesh3d.py` on seed 0 with N = 216, before the registered E3 runs)
E3 uses N = 216 (not 432) because one seed took 95 s on a machine shared with an unrelated build; the 30 starts, the CM kernel,
the CVT iterations and the gate are unchanged. The development seed 0 (N = 216) showed radius-ratio 5th percentiles 0.61 (CM) and
0.64 (CVT); it is part of the registered 30 (seeds 0..29), i.e. it was seen before registration of this amendment.

## Amendment A3 (2026-10-11, during E1/E2; speed only)
On the disc the nearest-edge search of the container penalty looped over the 2000 polygon edges in Python (about 330 s per lifted
run). It was vectorised over edges (`_nearest_on_edges`); the results are the same function (a two-seed check on the disc
reproduced the same energies as before to the printed digits). The partial disc records produced with the slow code (76 runs,
kept in `results/partial_disc_slow_harness.jsonl`) are not used; the disc is rerun from scratch with the vectorised code. Square
and hexagon records (produced before the change) are kept: the change does not alter any value the algorithm computes.
