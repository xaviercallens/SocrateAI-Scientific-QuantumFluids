# Workstream T — persistent homology of quantum-fluid vortex configurations

**Date:** 2026-09-20. **Status:** PRE-REGISTRATION (§1–§5 written before any code runs and before the dataset
is chosen). **Audit:** required before §6 is filled (E-1). **Tool:** GUDHI 3.13.0 (INRIA).
**Runs in parallel with** the dual-scale line; it is an *independent* observable for the same question.

---

## 1. Why TDA, and why it is not decorative

`docs/DUAL_SCALE_PROPOSAL.md` established DS-QF′: the dual-scale structure is a property of the **weakly
interacting** regime, and `ℓ(k)/(√2 ξ)` is a dimensionless number measuring how far a real superfluid departs from it.
That number comes from the **excitation spectrum**. It would be worth much more if a *second, structurally unrelated*
observable measured the same departure. Persistent homology of the **vortex configuration** is such an observable:
it uses positions in real space, not energies in Fourier space, and it shares no data, no instrument, and no fitted
parameter with the dispersion measurement.

The physical bridge is sharp and is the whole reason this is worth doing:

> In a quantum fluid, circulation is quantized and vortex cores have size `ξ`. Two vortex lines therefore cannot sit
> arbitrarily close — below `~ξ` they reconnect instead. **A minimum separation is a floor in a persistence diagram.**

In the Vietoris–Rips filtration of a point set the `H₀` deaths are exactly the edge lengths of the Euclidean minimum
spanning tree, so "minimum vortex separation" is literally "smallest `H₀` death". The dual-scale claim "no scale below
`ξ`" thus becomes a statement about a persistence diagram, measurable on real data.

A vortex tangle also carries a *second* scale: the mean inter-vortex distance `ℓ_v ≈ n_v^{-1/2}` (2D) or `n_v^{-1/2}`
per unit area of line density (3D). `H₁` features (loops) live at that scale. **One persistence diagram therefore
returns both scales of the dual-scale picture**, and their ratio `ℓ_v/ξ` is the standard quantum-turbulence parameter.

## 2. Definitions (fixed now)

Given extracted vortex positions `X = {x_i} ⊂ ℝᵈ` and the healing length `ξ` of the same configuration:

- `MST(X)` = Euclidean minimum spanning tree; its edge lengths are the `H₀` deaths of the Rips filtration.
- **Floor ratio** `F := min_{i≠j} |x_i − x_j| / ξ` (smallest `H₀` death, in units of `ξ`).
- **Sub-healing fraction** `f_< := #{MST edges shorter than ξ} / #{MST edges}`.
- **Loop scale** `L₁ := median birth of `H₁` features of the alpha complex, in units of `ξ`.
- `ℓ_v` := mean MST edge length (a density-free estimate of inter-vortex spacing).

## 3. Hypothesis TDA-DS, and what refutes it

> **TDA-DS.** For a quantum fluid in the weakly interacting regime, the vortex configuration has a persistence floor at
> the healing length: `F = O(1)` and `f_<` is small, **and both differ from a matched Poisson null model**.

Refuted if `f_<` is statistically indistinguishable from the Poisson null at the same point density, or if `F ≪ 1`
systematically (which would mean vortices routinely sit far inside each other's cores).

**The null model is the load-bearing part.** A floor can be manufactured by the extraction algorithm (grid resolution
sets a minimum separation), so the test is never "is there a floor" but "is the floor different from a random
configuration at the same density, analysed by the identical pipeline". Every number is reported alongside its Poisson
counterpart.

## 4. Controls (a run that fails any of these is void)

| control | construction | requirement |
|---|---|---|
| **C-POS** synthetic GP field | analytic `ψ` with vortices at **known** positions and **known** `ξ` on a grid | the extractor must recover the planted positions to within one grid cell, and `F` must match the planted minimum separation / `ξ` to within 10 % |
| **C-NEG** Poisson null | uniform random points at the same density, same pipeline | must show **no** floor: `f_<` at the analytic Poisson level, `F ≪ 1` for dense samples |
| **C-RES** resolution | rerun C-POS at half and double grid spacing | `F` must be stable; if `F` tracks the grid spacing rather than `ξ`, the pipeline is measuring its own resolution and the run is void |
| **C-PERM** label shuffle | same number of points, positions replaced by a random subset of the grid | must reproduce C-NEG |

`C-RES` is included because the most likely way this whole workstream produces a false positive is by measuring its own
discretisation. It is the control this design most expects to have to answer to.

## 5. Pre-registered predictions

- **T1.** C-POS recovers planted vortices; `F` within 10 % of planted.
- **T2.** For a genuine quantum-fluid configuration, `f_< < 0.1` while the matched Poisson null gives `f_<` several times larger.
- **T3.** `F` is stable under a 2× change of grid resolution (C-RES).
- **T4.** `L₁/F` (loop scale over floor) is `≫ 1` and is an estimate of `ℓ_v/ξ`, the quantum-turbulence parameter.
- **T5 (the DS-QF′ link, honest status: weakest).** The floor is well separated from the microscopic scale only when
  `ξ` ≫ interparticle distance, i.e. in the weakly interacting regime. In ⁴He, `ξ ≈ 0.5 Å` is *comparable* to the
  interatomic spacing (≈ 3.6 Å⁻¹ in `k`), so the separation of scales that makes TDA-DS meaningful **should itself
  degrade** — the same localisation DS-QF′ states, seen in an unrelated observable. This is a qualitative expectation,
  not a fitted prediction, and will be reported as such.

## 6. Data

Real data only; synthetic fields are used **exclusively** for controls and are never reported as a result.
Dataset selection is deferred to a search and recorded here with licence, URL and size before use. If no suitable
public dataset with a recoverable healing length exists, that is itself the reported outcome and the workstream stops at
the controls — it does **not** silently fall back to reporting synthetic data as findings.

## 7. Formalization target (scoped small on purpose)

Not persistence theory — that is a large project and is not attempted. The one elementary bridge lemma is:

> For a finite point set, the smallest positive `H₀` death of the Rips filtration equals the minimum pairwise distance;
> hence a proven minimum separation `d` implies no `H₀` death below `d`.

This is the step that licenses reading "persistence floor" as "minimum separation", and it is small enough to be
Lean-checked honestly. Anything beyond it is out of scope for this memo.

## 8. Out of scope

Dynamics and reconnection events (snapshots only); any claim about ⁴He from BEC data or vice versa (LL-15 — the
property that must transfer is *quantized circulation with a resolvable core*, and it must be checked per dataset);
any novelty claim (TDA on vortex tangles has a literature, which must be checked before any external communication).
