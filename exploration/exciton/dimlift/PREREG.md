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
