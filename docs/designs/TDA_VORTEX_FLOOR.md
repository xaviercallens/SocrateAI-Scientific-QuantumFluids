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

---

## §9 Control baseline (run 2026-09-20, synthetic by construction — controls only, never a result)

`exploration/tda/controls_baseline.py` → `controls_baseline.json`. Configuration: triangular
(Abrikosov-like) lattice, the arrangement a rotating condensate actually forms.

| control | requirement | result |
|---|---|---|
| **C-POS** | recover planted vortices; `F` within 10 % | **PASS**: 36/36 recovered at every spacing; `F` = 3.816 / 5.831 / 7.846 for planted 4 / 6 / 8 (deficit 4.6 → 1.9 %, the half-cell quantisation of plaquette centres) |
| **C-RES** | `F` stable under a change of grid | **PASS, decisively**: `dx/ξ` = 0.5 → 0.125 (a 4× change) moves `F` from 5.831 to 5.938, **1.8 %**. A resolution artefact would have moved it 4×. |
| **C-NEG** | Poisson shows no floor | **PASS**: matched count `F` = 1.22 (p05 0.41, p95 2.39), `f_<` = 0.016; dense (n = 1600) `F` = 0.024, `f_<` = 0.48 |
| **C-PERM** | shuffled positions reproduce the null | **PASS**: `F` = 0.717, inside the C-NEG p05–p95 band |

**Discrimination, and an honest limit.** Lattice `F` = 6.00 against null p95 = 2.39 is only a
**2.5×** separation at 36 points: with few vortices the null is broad. Discrimination improves with
vortex count, so a real dataset needs **many** vortices for this test to bite. This is a
quantitative precondition on dataset selection, recorded before any dataset was chosen.

### Correction to prediction T4 (registered error)

T4 predicted "`L₁/F ≫ 1`, an estimate of `ℓ_v/ξ`". **The baseline shows this is wrong.** For an
ordered lattice `F`, mean-MST and `L₁` all coincide (e.g. 5.83 / 5.95 / 6.05 at spacing 6), so
`L₁/F` ≈ **1.03**, not ≫ 1. The error was conceptual: for a regular configuration the minimum, mean
and loop scales are the *same* length, so their ratios cannot carry `ℓ_v/ξ`.

Corrected, and this is the form that will be used:
- `ℓ_v/ξ` is estimated by **`mst_mean_over_xi`** (mean separation), not by any ratio;
- `F` is the **floor** (minimum separation) and equals `ℓ_v/ξ` only for an ordered configuration;
- **`L₁/F` measures disorder**: it is 1 for a lattice and grows as the configuration becomes irregular.

T4 is replaced by **T4′**: for a real (disordered) vortex configuration, `L₁/F > 1` measurably,
while `mst_mean_over_xi` estimates `ℓ_v/ξ`. As with the A1.2 dimension-count error in the
second-invariant memo, this is recorded rather than silently corrected.

### T5 made quantitative (2026-09-20) — the link to DS-QF′

T5 was registered as qualitative ("the separation of scales should degrade in ⁴He"). It can be made
a number, using `ξ` from this repo's own measurement (CLAIM-024) and the ratio that decides whether
a persistence floor is *resolvable at all*:

```
        ξ / d ,   d = n^(-1/3) = interparticle spacing          ξ/d = (8π (n a³)^{1/3})^{-1/2}
```

| system | `ξ/d` | is a TDA floor resolvable? |
|---|---|---|
| dilute BEC, `n a³ = 10⁻⁶` | 1.99 | yes — core is larger than the particle spacing |
| BEC, `n a³ = 10⁻⁴` | 0.93 | marginal |
| **superfluid ⁴He (measured `ξ` = 0.471 Å, `d` = 3.58 Å)** | **0.132** | **no** — the core is *smaller* than the interatomic spacing |

So in ⁴He the vortex core is not a resolvable continuum object at all: `ξ/d ≈ 0.13` puts it below the
granularity of the fluid. Inverting the dilute-gas formula on the measured `ξ/d` returns an implied
`n a³ ≈ 12`, i.e. wildly outside the dilute regime where that formula is even valid — which is the
correct conclusion stated in the formula's own terms.

**This is the same localisation as DS-QF′, reached through an unrelated quantity.** DS-QF′ found
⁴He 21–51× below the dual-scale floor in the *excitation spectrum*; T5 finds its healing length
0.13× the interatomic spacing in *real space*. Neither measurement feeds the other.

Consequence for this workstream, fixed now: **⁴He is not a valid target for TDA-DS** — not because
the test fails there but because the scale it would test does not exist as a resolvable length.
Dataset selection must therefore prefer **dilute-BEC** configurations (`ξ/d ≳ 1`), and any ⁴He
vortex-tangle data would be analysed for `ℓ_v` only, never for a floor at `ξ`.

*Caveat:* the He-II density 145.1 kg/m³ is a standard literature value **not verified in this
repository**; a 2× density error moves `ξ/d` by only 1.26×, so the conclusion is insensitive to it.

---

## §6 DATA — selection recorded 2026-09-20, before any measurement

A search over HuggingFace, Zenodo, NIST and lab portals returned **one** dataset meeting the
critical criterion (a real quantum-fluid field with a recoverable healing length, downloadable
without authentication, within the disk budget). Negative results are recorded because they bound
what this workstream can ever claim:

- **HuggingFace has nothing.** Direct API queries for `superfluid`, `gross-pitaevskii`,
  `bose einstein`, `quantum turbulence`, `cold atom`, `helium neutron` return zero relevant datasets;
  the full 21-dataset `polymathic-ai`/"The Well" collection contains no GPE/BEC entry.
- **No public superfluid ⁴He `S(Q,ω)` or `S(Q)` dataset was found.** ILL raw data are credentialled;
  the classic static `S(Q)` tables are print-only behind a paywall. **This blocks the structure-factor
  test** `S(k) ≤ √(k/2k*)` proposed in `DUAL_SCALE_PROPOSAL.md` §4 — recorded as a data gap, not a result.
- **No public vortex-filament / Biot–Savart tangle coordinates** from the usual groups. A genuine gap.

### Selected: Zenodo 5510351 — Polanco, Müller & Krstulovic

`data/external/polanco_2021_gp_turbulence/` (see `README.meta`). CC-BY-4.0, 268 MB, 256³ complex
wavefunction, `L = 2π`, `c = 1`, **`ξ = 1.5 Δx`** taken from the authors' own analysis code.

**Two caveats fixed before measuring, both of which constrain what may be concluded:**

1. **`ξ` is only 1.5 grid cells.** A floor *at* `ξ` is therefore barely above the discretisation, and a
   raw point-cloud floor would measure the grid (demonstrated in `tests/test_vortex_3d.py`). The
   measurement is therefore made on the **line graph** — distinct vortex lines, whose separation the
   paper puts at `ℓ_v ≈ 28 ξ ≈ 42 cells` and which is well resolved. The raw-point-cloud number will
   be reported *alongside*, explicitly labelled as the artefact it is.
2. **This is a roton-bearing generalised GP, not a weakly interacting BEC** (LL-15: the property that
   must transfer is *quantized circulation with a resolvable core*; it has that, but it does **not**
   have Bogoliubov's dispersion). It therefore sits **between** the two ends of DS-QF′ by construction,
   and must not be reported as a test of the weakly interacting regime.

---

## §10 REAL-DATA RUN (2026-09-20) — **INCONCLUSIVE; the floor statistic is confounded**

Dataset: Zenodo 5510351 as recorded in §6. `exploration/tda/run_polanco.py`, `linkradius_check.py`.

### 10.1 What was extracted (this part is sound)

46 581 vortex points from the 256³ field. The **raw point-cloud floor is 0.707 Δx = 0.471 ξ** — i.e. it
measures the grid, exactly the artefact §6 predicted and `tests/test_vortex_3d.py` demonstrates. So the
raw statistic is correctly identified as meaningless, as designed.

### 10.2 The line-graph result, and why it does not stand

Segmenting at `link_radius = 2 Δx` gave 67 lines with `F = 1.491 ξ`, `f_< = 0.000`, against a
random-shift null of `F = 0.101 ξ` (p95 `0.150`), `f_< = 0.594`. Taken at face value that is a strong
confirmation of TDA-DS.

**It is not taken at face value.** Segmentation by proximity *guarantees* that distinct components are
separated by more than `link_radius`, so the statistic has a floor built into it. At
`link_radius = 2 Δx = 1.333 ξ` the measured `F = 1.491 ξ` sits only **12 % above its own threshold**.
A sweep settles it:

| `link_radius/Δx` | 1.0 | 1.2 | 1.5 | 1.8 | 2.0 | 2.5 | 3.0 | 4.0 |
|---|---|---|---|---|---|---|---|---|
| lines | 1030 | 175 | 105 | 67 | 67 | 31 | 30 | 20 |
| `F/ξ` | 0.667 | 0.943 | 1.155 | 1.491 | 1.491 | 2.000 | 2.108 | 2.749 |
| **`F`/threshold** | **1.00** | **1.18** | **1.15** | **1.24** | **1.12** | **1.20** | **1.05** | **1.03** |

`F` ranges over 132 % as the threshold changes 4×, and never rises more than 24 % above it.
**`F` tracks the segmentation threshold: it is an artefact, not a measured floor.** The mean-MST
estimate is threshold-dependent for the same reason (1.75 → 5.37 ξ) and is likewise not reportable.

The null comparison is *also* invalid, and would have been even had `F` been stable: the data's `F` is
bounded below by segmentation while the shifted null's is not, because the null was not re-segmented.
The two sides were not the same pipeline. Recorded as a design defect.

### 10.3 Why this was foreseeable, and what it costs

§6 recorded before the run that `ξ = 1.5 Δx` leaves the healing length barely above the discretisation.
That caveat is what came true: any proximity-based line segmentation needs a threshold of order one to
two cells, which on this dataset is *the same size as ξ*, so threshold and signal cannot be separated.
**The dataset is too coarse in `ξ/Δx` for this test**, whatever the pipeline.

**TDA-DS is neither confirmed nor refuted.** Nothing from §10.2 may be cited.

### 10.4 Requirements for a valid future run (fixed now)

1. **Either** a dataset with `ξ/Δx ≳ 5`, so a segmentation threshold of 1–2 cells sits far below `ξ`;
2. **or** topological line tracing — walking each vortex line through the grid via its pierced faces —
   which assigns line identity **without any proximity threshold** and removes the confound at its root.
   This is the principled fix and is the recommended next step.
3. Either way the null must be re-segmented by the identical pipeline before comparison.

---

## §11 SECOND REAL-DATA RUN — threshold-free tracing. **Split verdict.**

`exploration/tda/run_polanco_traced.py`, implementing §10.4 fix 2. Line identity now comes from
**cube adjacency**: a vortex line enters a grid cube through one face and leaves by another, so
connectivity is combinatorial and there is **no parameter for the floor to track**.

### 11.1 Validation of the tracing

**`multi_face_cubes = 0`** out of 46 762 pierced cubes: every pierced cube has exactly two faces, so
line identity is unambiguous everywhere in this snapshot — no reconnection-site or crossing ambiguity
to hide. 181 components, 175 with more than 10 faces (largest holds 3.4 % of faces). The earlier
proximity method reported only 67 lines at `link_radius = 2 Δx`: **it was merging distinct lines**.

### 11.2 Result

| statistic | data | random-shift null | verdict |
|---|---|---|---|
| floor `F` | **0.943 ξ** | 0.105 (p95 **0.156**) | **6.1× above the null's p95** |
| `f_<` (fraction of MST edges below ξ) | **0.402** | **0.381** | **indistinguishable** |
| mean MST | 1.75 ξ | 1.78 ξ | indistinguishable |

### 11.3 Verdict against the pre-registration — it splits, and both halves are reported

§3 fixed two refutation conditions. They disagree:

- **The floor statistic supports TDA-DS.** `F = 0.943 ξ` — the minimum separation between distinct
  vortex lines sits essentially *at* the healing length — and is 6.1× the null's 95th percentile. With
  no threshold in the method, this cannot be the parameter artefact of §10.
- **`f_<` refutes it as written.** §3: *"Refuted if `f_<` is statistically indistinguishable from the
  null."* It is: 0.402 against 0.381. **Prediction T2 (`f_< < 0.1`) is wrong**, and by a wide margin.

The two are consistent once looked at: both distributions put ~40 % of edges below `ξ`, but the data's
edges *stop* at 0.943 ξ while the null's continue down to 0.105 ξ. `f_<` at a single threshold is
simply a poor discriminator here; the minimum is the informative statistic. That is a lesson about the
statistic, not a rescue of the prediction — **T2 stands as refuted.**

### 11.4 The limit that remains, unchanged

`ξ = 1.5 Δx`, so `F = 0.943 ξ = 1.41 Δx`. The geometry of face centres permits distinct traced lines to
approach ≈ 0.707 Δx = 0.47 ξ, so the measured floor sits a factor **2** above what discretisation alone
allows. Real, and above both the null and the geometric minimum — but a factor 2 is not a wide margin.

**Net status: TDA-DS is partially supported and not established.** The floor result is reportable with
its caveat; the hypothesis as pre-registered is not confirmed, because one of its own refutation
criteria fired. A dataset with `ξ/Δx ≳ 5` remains required for a strong claim.
