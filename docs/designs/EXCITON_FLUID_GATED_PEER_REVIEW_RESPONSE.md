# Response to the external review of "Gated exciton fluids" (Zenodo 10.5281/zenodo.23294615)

Date 2026-10-11. The review text was supplied by the owner (source not stated; treated as an external referee report). This is a
point-by-point response with what was checked, what is accepted, what is corrected, and what is planned. Nothing here changes
the deposited record; changes will go into a new version after the running work packages are verified.

## 1. Corrections to the review's reading of the paper

| Review statement | Check | Response |
|---|---|---|
| "the author brilliantly proves that the sum of alternating image charges resolves into a manifestly non-negative structure" | Theorem 1 and the independent review of the paper both confirm the algebra `S_m = 2(1-cos(b-a))(1+cos(a+b)) = 2(sin a - sin b)^2` | Accepted. It is paper-and-pencil, not Lean (see 2.1). |
| "Real-world gating does not break the universal optimality theorem" | The paper says: *within the ideal-metal model* and *conditionally on an unrefereed lattice theorem*. Layered dielectrics keep complete monotonicity (reviewer's Sturm-Liouville argument); finite gate screening and lateral inhomogeneity are not covered. | The review's sentence is stronger than the paper's. Not accepted as written. |
| "If exotic non-triangular phases are observed, they must be due to quantum fluctuations or disorder, not the macroscopic electrostatics of the gates" | The paper lists lateral inhomogeneity and finite gate screening as further possible causes, and the whole statement is conditional on the lattice theorem. | Not accepted as written; hedge restored. |
| "experimentalists now have a concrete blueprint to detect the universally optimal state in the lab" via L1 | L1 tests the *dependence of the interaction strength on gate separation*, which is what depends on the new mathematics' geometry. The paper states (Sec. 6, "What can fail") that L3 (lattice symmetry) cannot discriminate the theorem from other repulsive monotone interactions: a triangular lattice is the ground state of almost every such interaction. | Not accepted: no item of the protocol detects "the universally optimal state" as such. |
| "forced the author to reduce the grid to a practically useless 8x8 resolution, making the gate-sweep frequency shifts a mere box-size artifact" | Correct in effect, but the cause of the artefact is the *box size* (shift scales as L^-2, independent reviewer's solver), not the solver: a dense solver on 32x32 would show the same area-average. The cost explains why 16x16/sigma=3 could not be run to stationarity in the registered budget. | Accepted with the distinction: the Krylov package addresses the cost; the box-size dependence needs L-scans, not only speed. |
| "ARKode-style IMEX failed because the reservoir dynamics were wildly faster ... broke the contraction mapping" | Correct: the module's implicit stage is a fixed point and converges iff h*gamma_R*a_ii < 1. D-e *passed*: that is exactly the predicted behaviour. | Accepted; "failure" is the predicted outcome of a unit test. |

## 2. The four proposed improvements

### 2.1 Formalise Theorem 1 in Lean (restore Tier A)

*Agreed.* One factual correction: the review says Mathlib lacks "robust formalisations of Poisson summation applied to Jacobi
theta functions". The Mathlib pinned in this repository (v4.34.1) contains `Mathlib/Analysis/Fourier/PoissonSummation.lean` and
`Mathlib/Analysis/SpecialFunctions/Gaussian/PoissonSummation.lean` (found by listing the pinned package directories on 2026-10-11),
so the Gaussian lattice-sum identity needed in the proof is available. *Status:* work package `lean` of workflow
`gated-exciton-completion` (target tiers: the trigonometric core T1, the Laplace-measure positivity T2, the library's
CompletelyMonotone class T3), each tier labelled by what is proved versus assumed. Result pending.

### 2.2 Matrix-free Krylov (JFNK) solver

*Agreed on the diagnosis, with one technical amendment to the proposal.* The review proposes a *finite-difference Laplacian* as the
Krylov preconditioner "because the spectral Laplacian makes the Jacobian dense". For the periodic pseudo-spectral discretisation
used here a better preconditioner exists: the linear part is *diagonal in Fourier space* (kinetic term) and *diagonal in real space*
(reservoir equation), so a block-diagonal preconditioner built from (I - gamma_step*(-i k^2/2)) in Fourier and
(I - gamma_step*(-gamma_R - R|psi|^2)) pointwise is exact for the linear part and costs two FFTs per application. A
finite-difference preconditioner would be the right choice for a finite-difference or finite-element discretisation (and for the open
boundaries of L6). *Status:* work package `krylov` of workflow `gated-exciton-completion` (BDF2/SDIRK-type implicit scheme, GMRES from the
pinned `sundials-core`, block preconditioner; gates against the CVODE records; scaling M = 8..64). Result pending. The note
about SPGMR: the pinned tree provides a GMRES module in `sundials-core` but CVODE in that tree has only a dense linear solver;
the Krylov work therefore lives outside CVODE (a new implicit stepper), not as a CVODE option.

### 2.3 Exponential integrators (ETDRK4)

*Agreed as a worthwhile comparison; one caveat.* The linear parts (kinetic -i k^2/2 and reservoir decay -gamma_R) are diagonal in the
chosen bases, which is what ETD needs. The nonlinear rate term R|psi|^2 n_R is not in the linear part, so ETD is not unconditionally
better than a Newton-based implicit stage when the gate drives R|psi|^2 close to gamma_R; this is part of the gate set of the work
package (T-c, T-e, "what ETD cannot do"). *Status:* work package `etd` of workflow `gated-exciton-peer-review-followup`. Result pending.

### 2.4 L6 with the Fenris-CMRR architecture

*Agreed; and the repository is a good fit.* `xaviercallens/rusty-Fenris-CMRR` (v0.1, MIT, public, 924 lines) relaxes free nodes that
repel each other and fixed boundary nodes with a Yukawa potential on rusty-SUNDIALS CVODE with an analytic Hessian and a C API. Its
own README states the limits that matter: <= 1500 free nodes (dense LU), no triangulation or defect counting, no wall potential, and
that its Yukawa kernel is *motivated by* but *not certified by* the universal-optimality theory (no Lean proof that Yukawa is
admissible; the shifted-force cutoff breaks exact complete monotonicity by about exp(-kappa r_c)). *Plan:* a crate that reuses the
engine with (i) the ungated bilayer dipole kernel, (ii) the gated kernels of Theorem 1 (analytic force and Hessian from the Laplace
representation), (iii) fixed boundary nodes in the shapes of L6 (square, rectangles of several aspect ratios, hexagon with corner
cuts, triangle, disc, annulus, L-shape, a corridor "maze"), with Delaunay defect counting and heat-maps. Two cautions that the
review does not make but that the repository's own README does: the universal-optimality statements concern infinite
configurations at fixed density and *say nothing* about a bounded domain with pinned boundary nodes, and gradient flows find local
minima. The L6 output is therefore a *classical node-arrangement design target*, not a prediction about excitons, and the paper
will say so. *Status:* work package `fenris` of workflow `gated-exciton-peer-review-followup`; a cross-check against the independent
open-boundary study (`edge` package) is part of its gates. Result pending.

## 3. Items of the review not taken up, and why

* "Simulate ... a Kagome trap or a nanofabricated maze ... predict exactly where the triangular lattice will break": the work
  package reads "Kagome trap" as a hexagon-with-corner-cuts container and includes a corridor geometry; "exactly where" is not
  promised: the deliverable is defect statistics over multi-start relaxations with the fraction of starts reaching the best energy.
* Anything about the solver "effortlessly" scaling to 128x128 or 256x256: not promised; the Krylov package measures the scaling
  exponent up to 64x64 and reports it.

## 4. What stays open whatever the packages return

The lattice theorem remains unrefereed and AI-generated; the model parameters remain dimensionless and chosen for stiffness; no
experimental data are used; the Wigner-crystallisation point needs quantum Monte Carlo (package `wigner` produces a literature gate
and a calibrated harmonic estimate, not a critical density); a validity gate stands before any Hugging Face / GNN input (package `hf`).
