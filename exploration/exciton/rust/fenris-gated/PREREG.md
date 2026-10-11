# L6 design target: boundary-shaped node arrangements of the gated dipole kernel (pre-registration)

Date 2026-10-11 (registered before any relaxation or gate was run). Package L6 of `paper/exciton_fluid_gated.tex`
("Edge/frustration: boundary-shaped trap arrays; no numerical prediction yet").

## What this is, and what it is not

Output: the classical stationary node arrangements of a *stated pair kernel* with *fixed boundary nodes*, found by the
rusty-Fenris-CMRR relaxation engine (author's own repository, MIT, v0.1, commit 6d0df125) with the pair kernel replaced.
It is a design target for L6 (what boundary shapes to put in a trap array, how many 5/7 defects and which local order to
expect, in a purely classical, zero-temperature, repulsive-point model). It is **not** a prediction about excitons: no
quantum fluctuations, no temperature, no driven-dissipative physics, no trap potential (the wall is made of repelling
point nodes at fixed positions), no claim that the boundary nodes represent anything physical. Gradient flows find local
minima, not global ones; the fraction of starts reaching the best energy is reported. The Cohn-Kumar universal-optimality
statement is about infinite configurations and says nothing about these finite clusters.

## Kernels (units: boundary node spacing = 1)

All normalised so that the ungated bilayer is the dipole `U(r) = 1/r - 1/sqrt(r^2+d^2)` (the note's exciton-exciton
kernel `V_ee+V_hh-2V_eh` divided by 2; a global factor does not change stationary points).

* `ungated:d`  `1/r - 1/sqrt(r^2+d^2)`, closed form, no cutoff (rc = 1e4, shifted-force, negligible).
* `gated:d:D`  symmetric grounded gates at `z=+-D/2`, layers at `z=-+d/2`; Laplace/image representation
  `U(r) = (4/D) sum_{k>=1} (1 - cos(2 pi k d/D)) K0(2 pi k r/D)` (mode sum of the Laplace measure, note
  `docs/designs/EXCITON_FLUID_GATE_IMAGE_CM.md`; `D -> inf` gives the ungated kernel; `U~(0) = 2 pi d (1-d/D)` in this
  normalisation). `U'(r) = -(4/D) sum (1-cos) q K1(qr)`, `U''(r) = (4/D) sum (1-cos) q^2 [K0(qr) + K1(qr)/(qr)]`,
  `q = 2 pi k/D`. Evaluation: quintic Hermite table of `R = U - 1/r` built from the series (spacing 0.01, `r in [0.02, 3D]`),
  series elsewhere. Cutoff `rc = 6D` (`exp(-37)`), shifted-force.
* `yukawa:kappa`  `exp(-kappa r)/r`, `rc = 20/kappa`, shifted-force (the CMRR control).

Primary parameters: `d = 0.5` spacing (`n d^2 = 0.25`, inside the density range of the note's L1 table), `D/d = 3` (`D = 1.5`)
and `D/d = 10` (`D = 5`), `kappa = 1.5` (CMRR's example value). Sensitivity: `d = 1.0` (`D = 3`, `D = 10`), `kappa = 3`.

## Engine

`fenris-cmrr` v0.1 with `Cargo.toml` pointed at the pinned rusty-SUNDIALS-c3 (v11.6.0, 5db8041) and the kernel
generalisation `engine_patch.diff` (a `Pair` trait; `optimize` is unchanged and bit-identical for Yukawa). Defaults of the
engine are used unchanged: RK23 un-clumping, CVODE BDF, max order 2, rtol 1e-6, atol 1e-9, `max|F| <= 1e-9 |V'(ell)|`.
Dense LU (<= 1500 free nodes), O(N^2) forces. The engine has **no domain constraint**: a free node can leave through a gap
between boundary nodes. States with any free node outside the container are *escaped*, are excluded from the statistics
and are counted and reported per case. Rule: if more than 25 % of the starts of a case escape, the case is reported with
that fraction and survivor-bias warning; a dated amendment may then add a denser wall (spacing 0.5).

## Geometries (`python/geometry.py`)

Boundary nodes every ~1 along the container (edges divided into round(length) segments, corners are nodes, circles carry
round(2 pi R) nodes). `N_free = round(A - B/2)` (each boundary node half-shared with the exterior; mean node spacing 1).
Primary size: scale chosen so `N_free` is closest to 200. Shapes: square; rectangles of aspect 1.25, 1.5, 2; regular
hexagon; equilateral triangle; disc; annulus (inner radius = half the outer); L-shape (three unit squares); "kagome cut"
= regular hexagon with each corner cut at one third of the side (a 12-gon; **this is the stated reading of "Kagome trap";
it is not a kagome lattice and no claim is made about kagome physics**); maze = one serpentine corridor of width 3 with four
runs (wall thickness 3, single simply-connected region). Size series (square, hexagon, disc): `N_free` near 100, 400, 600,
primary kernels. Starts: uniform random in the domain, `numpy.random.default_rng(seed)` with
`seed = 20261011 + 1000*case_index + start_index`, 24 starts per case (60 for gate L-c); seeds are written to the results.

## Observables (final stationary state of each start; all from converged, non-escaped states)

1. Energy per node: `E_tot/N_tot` with `E_tot = E_ff + E_fb + E_bb`, `N_tot = N_free + B`; the free-node energy
   `E_ff + E_fb` (what the engine minimises); excess `Delta E = E_tot - N_tot e_bulk` and `Delta E / perimeter`, where
   `e_bulk` is the energy per node `1/2 sum_j U(|R_j|)` of the periodic triangular lattice at density
   `n = (N_free + B/2)/A` (same shifted-force kernel; ungated tail `n pi d^2/(2R)` added beyond the lattice-sum radius).
2. Delaunay triangulation (`scipy.spatial.Delaunay`) of all nodes (free + boundary); triangles with centroid outside the
   domain are removed. Coordination `c_i` = number of Delaunay neighbours of free node `i`. Histogram over free nodes;
   5-fold and 7-fold counts (and other) in three wall-distance bands: `< 1.5`, `1.5-3`, `>= 3` (distance to nearest
   boundary edge); positions saved.
3. Local `psi6_i = (1/c_i) sum_j exp(6 i theta_ij)`; `<|psi6|>` of free nodes; global `|<psi6>|`; `<|psi6|>` in wall-distance
   bins of width 0.5 up to 8. Reference for the periodic lattice: `c = 6`, `|psi6| = 1`.
4. Heat-maps (best-energy start): coordination and local energy `e_i = 1/2 sum_{j != i} U(r_ij)` (all nodes), PNG plus CSV;
   defect-probability map over all starts (2D histogram of non-6 nodes, normalised per start), PNG plus CSV.
5. Energy spread: sorted energies, fraction of starts within `1e-6`, `1e-4`, `1e-3` relative of the best, number of
   distinct minima at `1e-7` relative.

## Euler-characteristic bookkeeping (gate L-e), derived

Retained complex `T` (triangles of the Delaunay triangulation whose centroid lies in the domain). If `T` triangulates the
domain with boundary equal to the boundary-node cycles, then `V - E + F = chi` (1 for simply connected, 0 for the
annulus), `3F = 2E - B`, so `E = 3V - B - 3 chi` and `sum_v (6 - deg v) = 2B + 6 chi`. A boundary vertex lies in `k_b`
triangles and has degree `k_b + 1`; an interior vertex has degree `c_i`. Hence

    Q := sum_{free i} (6 - c_i) = 6 chi + sum_b (k_b - 3) = sum_b (k_b - theta_b/(pi/3)),

with `theta_b` the interior angle at `b` (`sum_b theta_b = pi (B - 2 chi)`). This is the "boundary-dependent constant":
the net 5-fold-minus-7-fold charge of the interior is fixed by the number of triangles at each boundary node. It is
not a function of the boundary geometry alone, so the test is of the integer identity per state, plus a conformity
check. Gate: for every converged, non-escaped state the identity `Q = 6 chi + sum_b (k_b - 3)` holds exactly and the
retained complex is conforming (boundary edges of `T` = consecutive boundary node pairs, `V-E+F = chi`); non-conforming
states are counted and reported, not hidden. Also reported: distribution of Q across starts per case.

## Gates (all before the production run; thresholds fixed here)

* **L-a** (a1) per kernel, `U'` vs central difference of `U` and `U''` vs central difference of `U'` at
  `r in {0.03,0.1,0.3,1,2,5}` (h = 1e-5 r): relative error `<= 1e-6`; (a2) full Model: force vs central FD of the energy
  (h = 1e-6) `|fd-an| <= 1e-6 (1+|an|)`, Hessian vs FD of the force `<= 1e-5 (1+|an|)`, 8 free + 6 fixed nodes, all four
  kernels; (a3) table vs series: `|dU| <= 1e-10(1+|U|)`, `|dU'| <= 1e-8(1+|U'|)`, `|dU''| <= 1e-6(1+|U''|)` on 2000
  random `r in [0.02, 3D]`; (a4) independent kernel check: series vs a direct real-space image sum (numpy, `|n| <= 2e5`,
  four-image `V_ee + V_hh - 2V_eh` of two grounded planes) relative `<= 1e-8` at `r in {0.05,0.2,0.5,1,2,4}`,
  and `int U d^2r = 2 pi d (1 - d/D)` (numerical quadrature of the series, relative `<= 1e-6`); (a5) K0, K1 vs
  `scipy.special.k0/k1`, relative `<= 1e-13` on `x in [1e-4, 40]`.
* **L-b** (b1) the patched engine on the original 12x12 square patch (121 free nodes, kappa 1.5, jitter 0.35, seed 42,
  CMRR `examples/square_patch.rs`) reproduces the unpatched engine's final coordinates to `1e-9`, with `max|F| <=
  1e-9 |V'(ell)|` (the README's 1.7e-11 is reported, not gated); (b2) 1D chain closed form: for Yukawa, `E(N+1) - E(N)`
  of N free nodes at unit spacing on a line with kappa = 1.5 tends to `-ln(1 - e^{-kappa})` (relative `<= 1e-7` at N=60);
  (b3) the full CMRR cargo test-suite of the unmodified engine on the pinned rusty-SUNDIALS is run and reported
  (the order-1-fallback test is expected to behave differently on v11.6.0; that is a finding, not hidden).
* **L-c** square container side 5 (20 boundary nodes), `N_free = 3` and `7`, four kernels (ungated d=0.5, gated D=1.5,
  gated D=5, yukawa 1.5): the engine's inside-domain stationary energies (60 starts) against an independent numpy/scipy
  search (400 random-start L-BFGS-B-free local minimisations with `scipy.special.k0/k1` kernels, `gtol 1e-12`, plus
  basin-hopping 200 steps). Pass: best inside energy equal to `1e-7` relative and every engine distinct minimum matches
  a numpy minimum to `1e-7` relative.
* **L-d** planted bugs, each in a separate build (cargo features): `bug1` flips the `K1/(qr)` term of `U''`;
  `bug2` replaces `1 - cos` by `1 + cos` in the mode weights; `bug3` halves `U'`. Each must fail at least one of
  L-a (a1, a2, a4). `bug2` is expected to pass the FD checks and be caught only by the independent check.
* **L-e** as above, on every converged non-escaped state of the production runs.

## Reporting rules

Negative and partial results are deliverables. Claims about excitons are not made. If the sibling edge study has produced
`exploration/exciton/results/edge/` before this finishes, the overlap (square, N near 37 and 61) is compared and reported,
without waiting. Deviations after seeing results are dated amendments appended below.

## Amendments
### A1 (2026-10-11, after the first run of gate L-a4/a5, before any production run)
First run of a4: harness faults, no kernel fault. (i) the quadrature for `int U d^2r` started at r = 1e-6 and omitted the
piece `2 pi * 1e-6` (relative error 3.0e-6 = exactly that piece); the piece is now added analytically. (ii) the direct
image sum has an absolute rounding/truncation floor of about 5e-13, which made the pure relative criterion fail at
`U ~ 6e-8` (relative 7.2e-6, absolute 4.6e-13). The a4 criterion is now `|U_series - U_image| <= 1e-8 (|U_image| + 1e-3)`
i.e. a 1e-8 relative criterion with a 1e-11 absolute floor. Bessel gate a5 passed unchanged (max relative 1.5e-14).
The kernel agrees with the image sum to 1e-13 absolute in all 24 test points.

### A2 (2026-10-11, after engineering smoke runs, before any production run or L-c/L-d/L-e result)
Smoke runs (one container, 3 starts, N_free 30-100; no observable was inspected for tuning) showed that the engine
defaults (CVODE rtol 1e-6, atol 1e-9) need 4000-6000 BDF steps per relaxation (several seconds at N = 30, estimated hours
per case at N = 200 on the shared machine) because the trajectory is integrated to 1e-6 although only the end state
matters. Changes, all in the driver/parameters, none in the physics:
1. CVODE tolerances rtol 1e-2, atol 1e-5 (engine `Params` fields, no code change). New gate **L-f**: final energies for 4
   starts x 4 kernels at N_free ~ 30 agree between (1e-6, 1e-9) and (1e-2, 1e-5) to relative 1e-6.
2. Primary size N_free ~ 100 (the lower end of the requested 100-600) instead of 200: cost. Size series at N_free ~ 200 and
   ~ 400 for square/hexagon/disc, 20 starts, as far as the time budget allows; whatever is not run is listed as not run.
   Sensitivity group also at N_free ~ 100.
3. Convergence classes: strict `max|F| <= 1e-9 |V'(ell)|` (engine criterion); a state is *accepted* if
   `max|F| <= 1e-6 |V'(ell)|` **and** the free-node Hessian is positive definite (Cholesky succeeds, i.e. a strict local
   minimum rather than a saddle). Both counts, and the count of accepted-but-not-strict states, are reported.
4. Kernel evaluation: the Hermite table now covers `[0.02, rc]` (rc = 6D) instead of `[0.02, 3D]`, and `val/d1/d2` are
   evaluated separately (engine patch regenerated: `Pair::val`, `Pair::d1`). Gate a3 range extended to `[0.02, 6D]`
   (max relative errors unchanged: U 9e-14, U' 7e-12, U'' 8e-10).
5. Gate a1 criterion gets an absolute floor: `|fd - an| <= 1e-6 |an| + 1e-10`. At r = 5 and D = 1.5 the kernel is
   ~1e-9 and the central difference of the table has noise ~2e-12 (the table stores `U - 1/r`); the relative-only criterion
   failed there at the first run after change 4. Not a kernel fault: a3 compares the same points with the series directly.
6. Observed at the first L-b3 run: the original CMRR suite on the pinned rusty-SUNDIALS passes 5 of 6; the 6th
   (`order1_restart_rescues_tight_high_order_bdf`) fails because the order-1 fallback is no longer needed on v11.6.0
   (the solve converges at max order 5 with 1e-10/1e-12, 641 steps, force 7e-12). This is the benign direction.

### A3 (2026-10-11, after 12 of the 44 primary cases; the primary run was then stopped)
Result of the primary (wall spacing 1) cases square, rect1.25, rect1.5 x 4 kernels (24 starts each): between 0 and 5
of 24 starts per case stayed inside the container (23/24 escaped for the ungated kernel in the square). The bare
fixed-node wall at the mean spacing does **not** confine the free nodes: at the midpoint between two wall nodes the
transverse potential is a saddle, and the interior pressure pushes a node through; there is no confining potential in this
model. The pre-registered contingency applies (> 25 % escape). The primary run was stopped after 12 cases (the remaining
32 would have been ~45 more minutes of the 2-thread budget for the same conclusion); the 12 cases are kept as data
(`case_primary_*.json`, with the survivor-bias warning: statistics of the 0-5 survivors are not representative).
New group **wallhalf**: identical shapes, `N_free`, seeds and kernels, with the fixed wall at spacing 0.5
(`w = 0.5`: every edge divided into 2 round(length) segments). Bookkeeping: `N_free = round(A - B/2)` with `B` the node
count of the spacing-1 wall (so `N_free` is the same as in the primary group); the Delaunay triangulation, coordination,
defect counts and the Euler identity use the spacing-1 subset of the wall nodes ("sites", the corners and every second
node) so that coordination numbers remain comparable with the lattice; the energy, force and Hessian use all wall nodes.
Energy bookkeeping for this group (and recorded for all): `E_ff` and `E_fb` separately and
`dE' = E_ff + E_fb/2 - N_free e_bulk` (a pair with a fixed node is shared half-and-half), per perimeter.
Whether the denser wall confines the short-range gated kernel (D = 1.5, screening length ~0.24) is not known in advance.

### A4 (2026-10-11, after 2 uniform-start wallhalf cases and 4 square cases with the new start)
With the spacing-0.5 wall and uniform random starts, 10 to 11 of 24 starts still escaped (square: ungated 11/24, gated
D=1.5 10/24; 13 and 14 survivors). The escape happens in the first, violent part of the flow (uniform random starts contain
pairs at tiny separations, whose force throws a node through the wall); inside-the-container minima exist (the survivors
converge into them). Design change: **random-sequential-addition starts**: uniform in the domain, mutual distance >= 0.6,
distance to the wall >= 0.35 (`Shape.sample_rsa`), seeds as before. Group **wallhalfrsa** (w = 0.5, RSA starts, all 44
cases, N_free ~ 100, 24 starts) is the production group; the uniform-start groups `primary` (12 of 44 cases, w = 1) and
`wallhalf` (2 cases) are kept as data and as the evidence for the leakage statement. Not a physics change: the start
distribution only selects among basins; it is recorded in each case file. The first four wallhalfrsa cases (square, all
four kernels) were run as a test of this change: 0 of 96 starts escaped, 95 of 96 reached 1e-6 (one ungated start did not),
all 96 Hessians positive definite.

### A5 (2026-10-11, during the wallhalfrsa analysis; no new relaxation involved)
1. The first-pass analysis flagged every state of the "kagome cut" container as non-conforming and its Euler identity as
   failed (n = 23-24 of 24 in each of the four cases). Cause (reproduced on a synthetic filled lattice): three exactly
   collinear wall nodes give a zero-area Delaunay triangle whose centroid lies on the wall and is classed "outside", so two
   wall edges are lost and the identity is applied to a complex that is not a triangulation of the domain. Not a
   property of the states. Fix in `study.triangulate`: zero-area triangles are removed and the triangle across the
   resulting bridging wall edge is split along the intermediate wall nodes; the conformity check (boundary edges of the
   complex = consecutive wall sites, V - E + F = chi, every free node used) is unchanged. All states are re-analysed from the
   stored relaxation output (`REANALYSE=1`); the numbers of the first pass are superseded.
2. The first production code did not record `E_ff`, `E_fb`, `dE'` (added during the run); the 44 wallhalfrsa cases are
   re-analysed with it from the same relaxations.
3. Size series: only N_free ~ 200 (square, hexagon, disc; 4 kernels; 20 starts; w = 0.5; RSA starts) is run; N_free ~ 400
   is not run (cost: an N = 200 relaxation is ~ 25 s per start at the shared load, N = 400 would be several minutes).
   N_free ~ 600 is not run. The sensitivity group (d = 1, kappa = 3) is run at w = 0.5 with RSA starts.
4. Overlap with the sibling edge study (square, N = 37, 61, d = 1/sqrt(2) spacing so that their rho0 = 0.5 d^-2 holds):
   six cases `edgecmp_*` are run. The sibling's interior-defect definition (non-hull vertices of the Delaunay
   triangulation of the particles alone) is not meaningful for these states (the free nodes sit in rows inside a wall of
   nodes and are not on the convex hull), see `edge_overlap.json`; no agreement claim is made.
