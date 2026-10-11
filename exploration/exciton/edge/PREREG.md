# Edge and frustration study of the exciton kernels: pre-registration

**Status: REGISTERED BEFORE ANY PRODUCTION RUN AND BEFORE ANY GATE RUN.** Date 2026-10-11. Follows
`paper/exciton_fluid_gated.tex` Sec. 5 ("Frustration and edges", announced as not started) and the style of
`docs/designs/EXCITON_FLUID_PHASE1_PREREG.md`. Gates are fixed here; a change is a dated amendment (section 9) written before
the run it affects; results are read as registered, failures included.

What this study is: the **classical** N-particle ground states of three repulsive, completely monotone pair kernels in
open geometries (no periodic images). What it is **not**: it makes no statement about exciton trapping, device performance,
quantum states, or the thermodynamic limit. Nothing here proves or disproves the upstream lattice theorem; open
geometries are outside its hypotheses (section 5).

## 0. Honest disclosure of what existed before this document

* The kernel table (`python/build_table.py`, `results/table_D*.txt`), the Rust crate `rust/qf-exciton-edge/`
  (`src/{kernel,geom,system,flow,linalg}.rs`, bins `edge`, `evalconf`, `bench`) and the python references
  (`python/edge_kernel.py`, `python/edge_ref.py`) were written first, and the following were run once as *development*
  checks, not as results: image series vs K0 series at 8 points (agreement 1e-16 relative); the first table (width 1, degree 24) vs
  the K0 series on 400 random points (max abs error of `U` 1.8e-15, of `U'` 3.9e-14); two timing runs of `g3`/disk/N=37
  (2 random + 2 patch starts, kappa 1e6, one of four runs not converged at tau 4000; and 2 random starts each at kappa 1e6, 1e4, 1e3), one `g3`/disk/N=91 timing run (2 + 2 starts, 94-146 s per run), and, with the new table and the screening of section 3, one `g3`/disk/N=61 run (4 random starts, 8-14 s each, three distinct minima at e = 0.20893, 0.21064, 0.21075 per particle: the landscape is multi-minimum, as expected), which showed the
  cost of the flow (6-10 s per N=37 run) and motivated the two-stage protocol and the faster table (width 0.5, degree 16)
  of section 3. No energy from those runs is used anywhere.
* No `E`, `E_edge`, defect count or aspect-ratio dependence of this study has been computed.

## 1. Quantities and units

Length unit `d` = electron-hole separation, so `d = 1`. Pair energy (unordered pairs, the registered convention of Phase 1;
the Phase-1 `Bilayer` kernel with `eps = 0`):

| id | `phi(r)` | what |
|---|---|---|
| `dip` | `2/r - 2/sqrt(r^2+1)` | ungated bilayer dipole, ~ `1/r^3` at large `r` |
| `g3` | `U(r)` of grounded gates at `+-D/2`, `D/d = 3`, layers at `-+d/2` | gated, completely monotone in `r^2` (`EXCITON_FLUID_GATE_IMAGE_CM.md`) |
| `g10` | same with `D/d = 10` | gated |
| `r3` | `1/r^3` | test kernel for the known answers only |

Gated kernel, defined by the image series `U = V_ee + V_hh - 2 V_eh` (period `P = 2D`, + charge at `z0 + Pn`, - charge at
`2h - z0 + Pn`, `h = D/2`), equivalently the Poisson series `U(r) = (8/D) sum_{k>=1} (1 - cos(2 pi k d/D)) K0(2 pi k r/D)`
(derived from the `S_m` of the design document: for symmetric gates only even `m` survive; verified against the image series
at 8 points to 1e-16 during development). `U` has the same `2/r` singularity at 0 as `dip`.

Geometry: `N` points `x_i` in a container `Omega` with area `|Omega| = N/rho0`, `rho0 = 0.5 d^-2` (lattice spacing
`a0 = (2/(sqrt3 rho0))^(1/2) = 1.5197 d`). Hard-wall containers: disk, square, rectangles 3:2, 2:1, 3:1 (id `rect32`,
`rect21`, `rect31`), equilateral triangle (`tri`), regular hexagon (`hex`). Plus the isotropic harmonic trap `V = k r^2/2`
(`trap`) with `k = k(N)` fixed by the LDA condition of section 4 (centre density `rho0`). `N in {19, 37, 61, 91}` (centred
hexagonal numbers; "neighbours" of them, e.g. N = 18, 20, 36, 38, are **not** run, see section 8).

Energy: `E = sum_{i<j} phi(|x_i - x_j|)` (total) and `e = E/N`. Hard wall as a quadratic penalty
`(kappa/2) sum_i sum_{faces f} max(0, n_f . x_i - c_f)^2` (disk: `(kappa/2) max(0, |x_i| - R)^2`), **`kappa = 1e5`**
(registered; not the 1e6 of the development timing). The reported total `E_p = E + E_wall` at the minimum is a lower bound
of the true hard-wall minimum `E_c` and `E_c - E_p <= sum F_w^2/(2 kappa)`; the largest wall penetration and `E_wall` are recorded
for every run. Edge energies are computed from `E_p` (a deliberate choice: conservative, a lower bound).

Lattice reference `e_lat(rho) = (1/2) sum_{a in A_rho \ 0} phi(|a|)` (triangular lattice, unordered pairs, same convention as
Phase 1), numerically by summation to `R = 200` for `dip` (plus the continuum tail `2 pi rho (sqrt(R^2+1) - R)`) and to
`R = 36` for `g3`, `g10` (the gated kernel is below 1e-11 there). Edge excess for hard walls (`|Omega| = N/rho0`, so the
mean density is exactly `rho0`):

`E_edge(N) = E_p - N e_lat(rho0)`.

Boundary scaling: least-squares fit `E_edge = gamma sqrt(N) + c` over the four `N`, per kernel and shape; also `gamma_P =
gamma / (P/sqrt(N))` with `P/sqrt(N) = Pf / sqrt(rho0)` and shape factors `Pf` (perimeter over `sqrt(area)`): disk 3.545,
square 4, rect32 4.083, rect21 4.243, rect31 4.619, tri 4.559, hex 3.722.

## 2. Instruments

| item | value |
|---|---|
| solver | rusty-SUNDIALS tree `996aaf0706e1` = v11.6.0 = commit `5db8041` (`~/xdev/rusty-SUNDIALS-c3`, path dependencies as in `qf-exciton-p1`), crates `cvode`, `nvector`; `Method::Bdf`, analytic Jacobian = Hessian of `E + E_wall` |
| flow | `x' = -grad(E + E_wall)`, chunks of `dtau = 10` |
| generator | SplitMix64, run `s` of case index `c` seeds `1_000_003 c + s` (random starts) or `1_000_003 c + 500_000 + s` (patch starts) |
| build | `CARGO_TARGET_DIR=/mnt/data/xdev-cache/exciton_edge_target`, `cargo build --release -j2`, rustc 1.97.1; at most 2 threads |
| independent check | numpy/scipy/mpmath, `python/edge_kernel.py` (K0 series and image series), `python/edge_ref.py` |

Gated kernel in Rust: `phi = 2/r - 2/sqrt(r^2+d^2) + W(r)` with `W` piecewise Chebyshev (width 0.5, degree 16, 72 intervals
on `[0, 36]`, zero beyond 36) built from the **image series** by mpmath (30 digits, Richardson in `n`); force from the exact
derivative of the polynomial; Hessian from the second derivative. The independent numpy reference uses the **K0 series**
(different algorithm), so E-b tests the table.

## 3. Procedure

Per case (kernel, container, N):

1. **Screening stage.** `n_rand` random starts (uniform in `Omega`, hard-core rejection at `0.3 a0`, up to 1e4 tries) and
   `n_patch` lattice-patch starts (triangular lattice of spacing `a0`, random rotation and offset, the `N` points of largest
   depth in `Omega`). Flow with `rtol = 1e-8`, `atol = 1e-10`, stop when `max|F| < 1e-4` and `|dE| <= 1e-9 |E|` over a chunk, or
   `tau = 2000`. Non-converged runs count with their final energy. (Screening energies are accurate to about 1e-6 relative;
   they are used to rank basins, not as results.)
2. **Polish stage.** The best 3 distinct (`|dE| > 1e-5 |E|`) screened configurations are re-relaxed with `rtol = 1e-10`,
   `atol = 1e-12`, `max|F| < 1e-9`, `|dE| <= 1e-14 |E|`, `tau_max = 4000`. The best polished configuration is the registered
   ground-state candidate; its smallest Hessian eigenvalue `lambda_min` (Jacobi) is recorded.
3. Numbers of starts (the budget rule, section 8), `(random + patch)`: `N = 19`: 60 + 20; `N = 37`: 40 + 12; `N = 61`: 16 + 6;
   `N = 91`: 8 + 4. **This is below the requested >= 60 starts for every `N` except 19 (80 starts there)** and is a registered
   reduction caused by the 90-minute budget on a loaded machine (development timing: 8-14 s per N = 61 run, 100-150 s
   per N = 91 run with the first kernel table). The success rate (fraction of screened starts whose energy is within `1e-5`
   relative of the best polished energy) is reported so that the reader can judge the search; with so few starts the
   energies of the larger `N` are **upper bounds on the ground-state energy of the kernel, not certified ground states**.
4. Cases and order. Kernel/shape grid: `dip` x {disk, hex, square, rect21, tri, trap, rect32, rect31}; `g3` x the same;
   `g10` x {disk, rect21, trap} (the gate separation `D = 10 d` exceeds the lattice spacing 6.6-fold, the kernel is close to `dip`).
   19 (kernel, shape) pairs x 4 values of `N` = 76 cases. **Order: `N` ascending over the whole grid** (so that every
   shape gets small `N` first), inside one `N` kernels `dip, g3, g10`, inside a kernel the shapes in the order above. A
   case is never started after the budget (about 5400 s of production wall time) is spent; unrun cases are listed as NOT RUN
   and no number is extrapolated for them.

Defect analysis (python, `scipy.spatial.Delaunay` of the best polished configuration): neighbours are Delaunay edges of
length `<= 1.4 x` the median Delaunay edge length of the configuration; `z_i` the number of neighbours; a vertex is
**interior** if it is farther than `0.25 x` the median nearest-neighbour distance from the boundary of the convex hull of
the point set (amendment A1: the first formulation, "not a hull vertex", is wrong for straight walls because Qhull drops
collinear points; found on the first analysis of the N = 19 results, before any defect count was read); reported per case: counts of interior `z = 5`, `z = 7`,
other `z != 6`, and the total interior topological charge `sum (6 - z)`. Known limitation, stated now: near-square
arrangements have four co-circular points and the Delaunay triangulation is degenerate there, so `z = 5, 7` counts in
square-like regions are not reliable; they are flagged when more than 30 % of interior vertices have a Delaunay-edge
length ratio (longest/shortest edge of the vertex star) above 1.35.

## 4. The harmonic trap and its reference

The trap has no fixed area. The reference is the local-density approximation (LDA):
`f(rho) = rho e_lat(rho)`, chemical potential `mu = f'(rho_c)` with centre density `rho_c = rho0`, `V = k r^2/2`; the
change of variables `r^2 = 2(mu - f'(rho))/k` gives `N = (2 pi/k)(rho_c f' - f)(rho_c)` and
`E_LDA = (2 pi/k) int_0^{rho_c} f''(rho) [f + (mu - f') rho] d rho` (`python/edge_ref.py`). Hence `k(N)` is computed from `N`
and `rho_c`, and `E_edge^trap = (E + E_trap) - E_LDA` (beyond-LDA excess). The LDA is a **reference, not a bound**; it
neglects gradients and the discrete lattice, and `E_edge^trap` is defined only against it.

## 5. What is a valid lower bound (E-c)

The imported upstream statement (conditional, unrefereed in this repository: "for a completely monotone kernel the triangular
lattice minimises the periodic energy per particle among `N`-point configurations on any torus of the same density", the
`TorusBound` hypothesis; the Cohn-Kumar universal-optimality theorem is **not** proved in 2D) concerns translation-invariant
periodic systems. It does **not** apply as written to a hard-wall container (the energy of a patch is *below* `N e_lat`
because it misses neighbours: negative `E_edge` is expected) and does not apply at all to a non-translation-invariant trap.
The statement that **can** be made, conditionally on that theorem and for hard walls, is:

Let `B` be the bounding rectangle of `Omega` with sides `b_x, b_y`; take the torus of sides `L_x = b_x + w`, `L_y = b_y + w`,
`w > 0`. The periodic energy of the tiled configuration equals the open pair energy plus image terms,
`N e_per = E + (1/2) sum_{i,j} sum_{m != 0} phi(|x_i - x_j + L m|) >= N e_lat(N/(L_x L_y))`
(theorem), and every image term is `<= phi(delta_m)` with `delta_m` the distance between `B` and `B + L m` (`phi` is
decreasing). Hence, for every `w > 0`,

`E/N >= e_lat(N/(L_x L_y)) - (N/2) sum_{m != 0} phi(delta_m)  =: LB(w)`,  `LB = max_w LB(w)`.

This is **weak** (the factor `N/2` from bounding every image pair by its minimum distance) and may be negative or below the
unconstrained `E/N >= 0` (every kernel here is positive). The gate E-c uses `max(LB, 0)`. Its purpose is that a violation
would be an unmistakable instrument error, not that it is tight. For the trap no bound is claimed; the gate there is
`E_int >= 0`. The sum over `m` is truncated at `|m| <= 300` with the integral remainder added (`python/edge_ref.py`).

## 6. Gates (all fixed here)

**E-a (known answers).** Instrument `edge` on kernel `r3`, container `trap` with `k = 1`, `rho = 0.5`
(sampling disk of area `N/rho`), 60 random starts, no patch starts, `N = 1, 2, 3, 7`, `E` the total energy (interaction +
trap), `C = 1`:

* `N = 1`: `E = 0`.
* `N = 2`: `E = C/(2x)^3 + k x^2`, `x^5 = 3C/(16 k)`.
* `N = 3` (equilateral, side `s`): `E = 3C/s^3 + k s^2/2`, `s^5 = 9C/k`.
* `N = 7`, hexagonal (1,6): `E = S C/R^3 + 3 k R^2`, `S = 12 + 2/sqrt3 + 3/8`, `R^5 = S C/(2k)`.

Pass: relative difference `<= 1e-9` (absolute `<= 1e-9` for `N = 1`) between the best Rust energy and the closed form; for
`N = 7` additionally an independent global optimiser (scipy `basinhopping` + L-BFGS, 14 variables, 200 starts, seeded) gives
the same minimum within `1e-9`, and the best Rust energy `<=` the optimiser's `+ 1e-9`. Also **E-a2**: `N = 2` for
`dip`, `g3`, `g10` in the same trap: the Rust minimum equals the 1-D root of `d/dx[phi(2x) + k x^2] = 0` found by `brentq`
on the K0-series kernel to `1e-9` relative.

**E-b (instrument equality).** `evalconf` vs the numpy implementation (`python/edge_ref.py`, K0 series for the gated
kernels, independent polygon/penalty code) on **random configurations**: kernels `dip, g3, g10, r3` x containers `disk,
square, tri, hex, trap` x `N in {7, 19}` x 5 configurations each, points uniform in a disk of 1.15 times the circumradius
(so that some violate the wall), `kappa = 1e5`, `k = 0.3`, area `N/rho0`. Pass: relative difference of `E_int` and of `E_wall`
`<= 1e-12`; forces: `max|F_rust - F_numpy| <= 1e-12 max|F_numpy|`; and the analytic Hessian equals the central finite
difference of the Rust force (step `1e-5`) to `1e-6` of its max-norm on 5 configurations of `N = 7` per kernel
(`dip, g3, g10`, container `disk` and `hex`). If the table fails the 1e-12 energy test, that is reported as a FAIL with the
measured error and the table is not "re-tuned" silently; any rebuild is an amendment.

**E-c (no violation of the stated bound).** Every polished and screened energy of a hard-wall case satisfies
`E/N >= max(LB, 0) - 1e-10`; trap cases satisfy `E_int >= 0`. Also reported (not gated): `E_edge` against the cut-lattice
patch, i.e. the best patch start's *screened* energy vs the best energy of the case (a case where the best random start is
worse than the best patch start by more than 1e-6 relative flags an under-searched `N`).

**E-d (planted-bug controls; the gates must bite).** With the instrument run under the planted bugs `1` ordered pairs
(energy and force x2), `2` sign of the `y` force flipped, `3` force x1.01, `4` the `D = 10` table loaded for `g3`
(`QF_PLANT_TABLE_SWAP`), the E-b gate must FAIL for each bug (kernel `g3` for bug 4, all kernels for 1-3). Also on the
recorded production energies: with `E` doubled (bug 1) or halved the E-c gate is evaluated; **it is expected to FAIL only
for energies that fall below `LB`; whether E-c can detect a halved energy is reported as measured** (the bound is weak, so a
negative answer is a finding about E-c, not a failure of the study).

**E-e (stationarity; informational but counted).** Best polished configurations: `max|F| < 1e-9`, `lambda_min >= -1e-6`
(rotation zero modes of the disk and the trap give `|lambda| ~ 0`). Failures are listed as "flat/saddle: not certified".

**L2 (energy monitor).** Along every flow the energy at chunk ends never increases by more than `1e-9` relative; the
number of violations is reported.

## 7. Outputs fixed in advance (no further gate)

1. Table of `e = E_p/N`, `E_edge`, `E_edge/sqrt(N)`, `lambda_min`, success rate, number of distinct polished minima within
   `1e-5` of the best, per case.
2. `gamma`, `c`, `gamma_P` per kernel and shape; whether `gamma_P` is constant across the hard-wall shapes (spread, as
   max/min and as standard deviation), reported as measured: **no prediction of constancy is made.**
3. Aspect ratio: `E_edge(N)` and `E_edge/P` for square, rect32, rect21, rect31 at each `N`; report whether `E_edge/P` and
   `E_edge` are monotone in the aspect ratio at each `N` and each kernel; a non-monotone result is reported as such.
4. Defects: counts of interior `z = 5, 7`, topological charge, per case and for the best configuration, with the hexagon /
   triangle commensurate-patch expectations (a perfect triangular patch has none) stated as a *comparison*, not a gate.
5. Trap: `E_edge^trap(N)` and its `sqrt(N)` fit; the count of interior defects.
6. Everything labelled exploratory if run beyond this document.

## 8. Budget and what is reduced

Machine: 8 cores shared with other workers (load 10-13 during development); this study uses at most 2 threads; target
total compute `<~` 90 minutes. Reductions registered here: starts and the case grid as in section 3; the neighbours of the
centred hexagonal numbers are **not run**; only one density `rho0 = 0.5`; one value of `kappa`; `g10` on three shapes
only. The missing cases are listed in the report; **no number is extrapolated for them.**

## 9. Amendments

**A1 (2026-10-11, analysis only, before any defect count was interpreted).** The definition of "interior" in section 3 is
replaced by the 0.25 x nearest-neighbour distance from the convex-hull boundary (see there). No run, gate or energy is
affected.

**A2 (2026-10-11, driver only).** The production driver crashed once at `g3`/trap/N = 19 (the LDA spline of a gated kernel
took the log of an underflowed `e_lat` at `rho = 1e-5`); the lower density limit of the LDA grid for gated kernels was set to
0.02 (`python/edge_ref.py`) and the driver restarted; finished cases (`dip` x 8 shapes, `g3` x 5 shapes at N = 19)
were not re-run. The restart gives the driver a fresh 5400 s budget; total production wall time is reported.

**A3 (2026-10-11, a statement of fact).** Gate E-b is evaluated on 200 configurations (the grid of section 6 has 4 kernels x 5
containers x 2 sizes x 5 configurations = 200), E-a2 on three kernels; both as registered.

**A4 (2026-10-11 10:48, order of work only; no result of N >= 61 had been produced).** Development timing of the production
runs showed that `N = 37` costs 12-31 s per case for `dip` and 60 s for `g3`, i.e. `N = 61` cases would cost about 3 and 6 minutes, so
the registered order ("`N` ascending over the whole grid") would exhaust the budget inside `N = 61` and never reach `N = 91`.
The order from `N = 37` (g3, g10 remaining) on is replaced by an explicit plan (`python/run_study.py`, `PLAN`):
`dip` N = 61 (8 shapes); `dip` N = 91 (disk, hex, square, rect21, tri, trap); `g3` N = 61 (disk, hex, square, rect21, tri, trap);
`g10` N = 61 (disk, rect21, trap); `dip` N = 91 (rect32, rect31); `g3` N = 61 (rect32, rect31). The numbers of starts of
section 3 are unchanged. The driver budget of this phase is 4300 s (total production wall time about 90 minutes from 10:34).
Cases the plan does not reach are NOT RUN. The first `N = 37` cases of `g3` finished before the change.

**A5 (2026-10-11 10:54, an addition of starts; written after the `N = 19, 37` main-stage energies of `dip` had been looked at
for success rates, before any aligned start was run).** The registered patch starts use a *random* lattice orientation,
so the perfect, symmetry-aligned patch (e.g. the 37-point centred-hexagonal patch in the hexagon container) is essentially
never generated, and the success rates at `N = 37` are 0.02-0.15 (the best is found once or twice in 52 starts).
An *aligned* stage is added: starts with orientation 0 or 30 degrees, lattice offset at one of the six high-symmetry
points (site, the two triangle centres, the three bond midpoints), spacing `x 1.0` or `x 0.94`: 24 starts for `N <= 37`, 12
for `N >= 61` (`edge ... n_aligned`, `python/run_aligned.py`), no random starts, screened and polished exactly as in section
3. The best polished configuration of a case is then the best over the main and the aligned stage; **both are reported**,
so that the reader sees how much the aligned stage changed. This does not make the search exhaustive: the registered
language "upper bound on the ground-state energy" stands. Done after the main plan for `N <= 37` first (in the pause of the
main driver), then for `N = 61, 91` as the budget allows (budget of this stage 1500 s).

**A6 (2026-10-11 11:05, an addition of starts; after the registered `N = 61` `dip` cases had finished and been timed, before any
extra start was run).** The production cost is far below the development estimate of section 3 (`dip`: N = 61 about 40 s per
case for 22 starts, N = 91 about 77 s per case for 12 starts; `g3` about twice that), so the registered 16 + 6 and 8 + 4 starts leave
the larger `N` badly under-searched (success rates of a few per cent at N = 37 already). After the main plan has finished
and the aligned stage (A5) for `N = 61, 91`, an **extra random stage** is run for `dip` only: 44 further random starts at
`N = 61` (60 random + 6 patch in total) and 32 at `N = 91` (40 random + 4 patch), new seeds (index offset = the registered
count), separate files (`results/runs_extra/`), screened and polished as in section 3, best-of-all reported with the stage
contributions shown. Budget 1500 s. `g3`, `g10` are not extended. The total production wall time will therefore exceed the
nominal 90 minutes by about the duration of the A5 + A6 stages; it is reported.
