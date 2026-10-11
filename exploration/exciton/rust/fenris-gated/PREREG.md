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
(none yet)
