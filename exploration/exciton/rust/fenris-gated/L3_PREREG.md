# L3 pre-registration: wall-spacing scan with RSA starts, and engine-level sliding walls (2026-10-11)

Registered before any L3 relaxation was run. Scope: classical zero-temperature stationary node arrangements of stated pair
kernels with a wall of fixed (G1) or sliding (G2) point nodes. No claim about excitons is made under any outcome.
Task L3 of `docs/designs/PROJET_DIMENSION_ET_FRUSTRATION_2026-10.md`. It answers two reruns asked by the independent
verifier of L6 (`docs/designs/EXCITON_FLUID_VERIFIER_NOTES_verify2_fenris.md`, problems 1 and 2) and the open E2 question
of `exploration/exciton/dimlift/PREREG.md` at engine level.

## Engine and drivers

* Engine: a FRESH clone of rusty-Fenris-CMRR at 6d0df125 in `/mnt/data/xdev-cache/fenris-l3`, with the README steps
  (sed to `/home/xavkal/xdev/rusty-SUNDIALS-c3` at 5db8041, `engine_patch.diff`). The `fenris-gated` crate sources are copied
  unchanged to `/mnt/data/xdev-cache/fg-l3` with only the `cmrr` path in `Cargo.toml` pointing at the clone; build with
  `CARGO_TARGET_DIR=/mnt/data/xdev-cache/target_fenris_l3`. The clone is scratch: never pushed.
* Relaxation parameters: unchanged from production (A2 of `PREREG.md`): ftol 1e-9, CVODE rtol 1e-2, atol 1e-5, one RAYON
  thread; a state is *accepted* if inside the container, `max|F| <= 1e-6 |V'(ell)|` and the free-node Hessian is positive
  definite. Kernels (units: boundary spacing 1): `ungated:0.5` and `gated:0.5:1.5` (gated D/d = 3). Yukawa and D/d = 10 are
  not run (cost).
* Shapes (both gates): square, hexagon, disc, rect2, lshape, annulus (as in dimlift E2); containers, `N_free` rule
  (`round(A - B1/2)` with `B1` the node count of the spacing-1 wall, so `N_free` and the RSA starts are identical for all
  wall spacings), random-sequential-addition starts (mutual distance >= 0.6, wall distance >= 0.35) as in
  `python/geometry.py`/`study.py`. New code (the generalised wall spacing, sliding driver, analysis) is in `python/l3_*.py`.
* Defect count `n_non6` = number of free nodes whose Delaunay coordination is not 6; triangulation, `analyse_state`,
  Euler identity and conformity check are those of `study.py`, unchanged. Triangulation sites: for `w = 0.5` every second
  wall node (as registered in L6, so that coordination numbers stay comparable with the lattice); for every other `w`
  all wall nodes. This makes `n_non6` not strictly comparable between `w` (the wall density seen by the free nodes is
  `1/w` or `1`); G1 therefore compares wall-concentration ratios within each `w`, and reports raw counts across `w`
  only descriptively.

## G1: wall-spacing scan with RSA starts (L6 verifier problems 1, 2)

Wall node spacing `w in {0.5, 0.75, 1.0, 1.25}` times the mean node spacing (nodes per edge `max(1, round(length/w))`,
circles `round(2 pi R / w)`; corners are nodes), 6 shapes x 2 kernels x 24 RSA starts per case at `N_free ~ 100`
(48 cases, 1152 relaxations). Seeds `20261011 + 1000*(400 + 2*shape_index + kernel_index) + start` (same for every `w`,
so starts are paired across `w`).

Recorded per state: escaped (any free node outside), accepted, `n_non6`, `Q`, defect positions, wall-distance bands.

* **G1a (confinement).** Escape fraction `f_esc(w)` pooled over shapes, kernels, starts. The wall *confines at w* iff
  `f_esc(w) <= 5 %` and no (shape, kernel) cell exceeds 25 %. Reported for every `w`, in particular `w = 1.0` with RSA
  starts, to settle whether the L6 statement "a bare fixed-node wall at mean spacing does not confine" was a wall property
  or a start-distribution property (uniform starts at `w = 1`: 19-24 of 24 escaped). Outcome statements allowed:
  "confines at w" / "does not confine at w"; the largest `w` that confines is named.
* **G1b (concentration of defects at the wall).** Over accepted, non-escaped states at each `w` that confines:
  `R(w) = [defects with wall distance < 1.5 / all defects] / [free nodes with wall distance < 1.5 / all free nodes]`,
  pooled over states (ratio of sums), 95 % bootstrap CI over states (2000 resamples). *Concentration appears at w* iff
  `R(w) >= 1.5` and the lower CI bound `> 1`. Also reported: share of defects within 1.5 of the wall (L6 reported 30-88 %),
  per shape. If `w` does not confine, `R(w)` is reported with the survivor-bias warning and is not used for the gate.
* **G1c (w-dependence, descriptive, not a gate).** Mean `n_non6` per (shape, kernel) versus `w`; paired difference
  w = 1.0 minus w = 0.5 with s.e.

Not tested in G1: the static transverse-saddle mechanism at the wall midpoint (asserted in L6, A3; no direct test here);
wall spacing below 0.5; other kernels; other `N_free`.

## G2: engine-level sliding walls

Wall at `w = 0.5` (as L6 production). Same 6 shapes, kernels `ungated:0.5` and `gated:0.5:1.5`, `N_free ~ 60`
(as dimlift E2), 30 RSA starts per (shape, kernel) (360 runs), seeds
`20261011 + 1000*(500 + 2*shape_index + kernel_index) + start`.

Method (engine level): free nodes are relaxed by the Fenris engine; the wall nodes (all except polygon corners; circle
nodes all slide) are parametrised by arclength on their ring and the reduced energy
`f(s) = min_free E(free, wall(s))` (free-free + free-wall + wall-wall, shifted-force kernel) is minimised over `s`
by L-BFGS (scipy, `gtol 1e-6`, at most 40 iterations / 80 evaluations); each evaluation is a warm-started engine relaxation
and the gradient is the partial `dE/ds` at the relaxed free nodes (envelope theorem; free forces <= 1e-9 relative). The
start point is the fixed-wall minimum reached by the same start (iteration 0), so the *pair* for each start is:
fixed-wall minimum versus the sliding-wall state continued from it. Free-node basins can change during the continuation.

* **G2 (gate).** `Delta = n_non6(fixed) - n_non6(slid)`, paired over starts for which both ends are accepted;
  mean and standard error (`sd/sqrt(n)`) per (shape, kernel). A shape *passes* for a kernel iff mean `Delta >= 2`.
  The gate passes for a kernel iff at least 3 of the 6 shapes pass. The overall statement "sliding walls reduce the defect
  count" is made only if the gate passes for both kernels; one kernel only is reported as partial.
* Also reported (not gates): energy decrease, change of `Q = sum(6 - c)` (expected 0 where wall triangle counts are
  unchanged), Euler/conformity, fraction of runs whose L-BFGS did not reach `gtol` within the cap (these are kept in
  the primary analysis and the analysis is repeated without them), number of starts where `Delta != 0`, the fraction
  of defects at the wall before and after.
* Comparison with dimlift E2 (square -2.2 +- 1.5 i.e. defects *increased*; disc worse): E2 minimised free and wall nodes
  jointly from the RSA start with numpy L-BFGS; here the sliding continues from the engine's fixed-wall minimum, so the
  two are different protocols and are not expected to give identical numbers. The second-order condition in the wall
  coordinates is not checked (only the free-node Hessian of each relaxation).

## Reporting rules

Negative and partial results are deliverables. All deviations are dated amendments below; nothing below this line is
written before the first L3 relaxation except an engineering timing check on one case (not used in any result).

## Amendments
### A1 (2026-10-11, after all L3 runs, before the write-up; disclosure only, no gate changed)
1. A first engineering check (g2, square, two starts, seed index 999, outside the registered seeds) was run to time the
   driver; not used in any result.
2. G2 annulus (two cases) was run by a second worker process to use idle CPUs and then again, from the original pool's
   static case list, by the first process; the final files are those of the second run (same seeds and code; not
   compared with the first run).
3. In the G2 ungated square/rect2/L-shape and gated rect2/L-shape cases a large fraction of L-BFGS runs reached the
   40-iteration cap before gtol 1e-6 (counts in L3_RESULTS.md); they are kept in the primary analysis as registered.
4. The G1 triangulation-site rule (w = 0.5: every second node; other w: all nodes) makes raw n_non6 incomparable
   across w; as registered, only R(w) is gated.
