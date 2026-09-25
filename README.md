# SocrateAI-Scientific-QuantumFluids

**A machine-checked Lean 4 library of quantum-fluid structure — with a record of what formalization caught, and what it could not**

[![Tests](https://img.shields.io/badge/tests-183%20passing-brightgreen)]() [![Lean](https://img.shields.io/badge/Lean-4.34.0--rc2-blue)]() [![Theorems](https://img.shields.io/badge/theorems-215%20kernel--checked-blue)]() [![Comparator](https://img.shields.io/badge/Comparator-two%20kernels-success)]() [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22904619.svg)](https://doi.org/10.5281/zenodo.22904619) [![Release](https://img.shields.io/badge/release-v1.10.0-orange)](https://github.com/xaviercallens/SocrateAI-Scientific-QuantumFluids/releases)

---

## What this is

A **Lean 4 / Mathlib library of 181 machine-checked theorems on the structure of quantum fluids**, with
the verification tooling around it and an unusually complete record of what went wrong on the way.

```lean
import QuantumFluids   -- Lean 4.34.0-rc2, Mathlib tag v4.34.0-rc2
```

| module | what it gives you |
|---|---|
| **`VortexWinding`** | correctness of phase-winding vortex detection — the loop sum is *exactly* an integer multiple of 2π — and its **exact failure case**: edge cancellation breaks at a phase step of exactly π, so bare antisymmetry of the principal phase difference, which codes routinely assume, is **false**. Also the discrete `∇·ω = 0`: **vortex lines do not end**, which line tracers presuppose. |
| **`QuantizedCirculation`** | `Γ = q·κ`, `κ = h/m`; no fraction of a quantum; and the quantum is *attained* by an explicit loop, so the bound is sharp. |
| **`HeliumKinematics`**, **`BoseIntegral`** | the identities a neutron-scattering analysis of superfluid ⁴He rests on — three-phonon decay open **iff** the dispersion is anomalous, two-roton momentum range, calibration-invariance of any comparison with 2Δ_R — and `∫₀^∞ t³/(eᵗ−1) = π⁴/15` with the Debye `T³` coefficient. Addressed to published work: see [`docs/FOR_GODFRIN.md`](docs/FOR_GODFRIN.md). |
| **`GPGalerkin`** | truncated Gross–Pitaevskii on **any** finite mode set: `Q = Σ_q|A_q|² ≥ 0`, mass and energy algebra, the Hamiltonian gradient identity. |
| `MadelungSplit`, `MadelungNSE` | the Madelung decomposition, and the same objects inside the vocabulary of OpenAI's Navier–Stokes formalization, **imported as a real dependency**. |
| `DualLength`, `QuantumFluidsShell`, `ShellHamiltonian`, `SigmaRule`, `Duality`, `RipsFloor` | correct but withdrawn-as-contributions or auxiliary — see below. |
| `PhononSeries`, `PhononSpecificHeat` | the phonon specific-heat series of Godfrin et al., PRB 103, 104516, Eq. (22) — **confirmed**, all six coefficients and the printed inverse series, from a computer-algebra-generated `linear_combination` certificate the kernel checks. |
| `ZeroSound`, `PhaseMixing` | undamped zero sound in a Fermi liquid iff `F₀ˢ > 0` (2D and 3D); free transport's solution and mode decay — the known answer the kinetic solver below is validated against. |
| **`Villani`** | a foundation for formalizing Cédric Villani's work, offered as a tribute: Ollivier–Villani (arXiv:1011.4779) Theorem 1 at `K = 0` — `#A·#B ≤ (#M)²` for the midpoint set of nonempty `A, B` in the Hamming cube — **fully proved**, by the crossover-coding injection the paper describes; plus a 3-line corollary of Mathlib's own Markov-kernel Data Processing Inequality (a discrete H-theorem). |
| `Fricke` | the group-theoretic core of the Fricke/K3 gate of `paper/wasserstein_slack.pdf` §6.3, as group theory only: the integer Fricke matrix `W = (0,-1; n,0)` squares to `-n·1`, **normalizes Mathlib's `Gamma0 n`** (explicit conjugate, itself an involution), acts on the imaginary axis by `y ↦ 1/(n y)`, which for `n = 1/ks²` is exactly `DualLength`'s `k ↦ ks²/k`, leaves `ell ks` invariant and fixes `1/√n`. Nothing about K3 surfaces, mirror symmetry or helium is claimed: the paper's verdict is "the same involution without the group". |
| `WassersteinCertificate` | finite LP weak duality for an assignment problem: a feasible, tight dual potential certifies a matching optimal without searching the others — general over any cost matrix, any finite index types. Instantiated on a hand-verified toy persistence-diagram pair (`docs/designs/CLOSED_LOOP_PREREG.md`): the found matching is optimal at cost exactly `7/4`; the broken negative-control potential is shown infeasible. |

The first three depend only on Mathlib and are meant to be reused.

## This is not a physics-discovery repository — and that is the interesting part

It started as one. **Two results we had regarded as findings were withdrawn after a literature check**
([RETRACTIONS.md](RETRACTIONS.md)):

- a cubic invariant of a complexified dyadic shell model is a degenerate case of published Hamiltonian
  structure — Vladimirova–Shavit–Falkovich (PRX 2021), L'vov–Podivilov–Procaccia (EPL 1999),
  Ditlevsen (PRE 2000) — and the dyadic case has *less* structure than theirs, not more;
- a "dual length" bound on the Bogoliubov dispersion is **dimensionally forced** and weaker than
  Onsager's inequality wherever it is not vacuous. Measuring that ⁴He violates it by 21–51× confirms
  that ⁴He has a roton.

What that leaves is a sharp answer to a question worth asking — **what does formal verification
actually buy in physics?**

| it caught | it could not catch |
|---|---|
| a **false lemma** before it was used (antisymmetry of the phase difference) | that a correct theorem was **already known** |
| an inequality our **prose had turned into an equality** (Bijl–Feynman) — the Lean was right, the memo was wrong | that a result was **dimensionally forced** |
| a **`1/D` constant** that made a bound useless in the limit that mattered | that a hypothesis was **physically naive** |

The kernel is for truth. Novelty needs a library, measurement needs controls, and the build needs a
second person. Paper: [`paper/quantumfluids_lean4.pdf`](paper/quantumfluids_lean4.pdf).

## Negative results are first-class here

Several of the most useful outcomes in this repository are failures, and they are kept at the same
level of detail as the successes:

- **A pre-registered kinetic and TDA programme scored 14 of 25** (`docs/designs/KINETIC_TDA_RESULTS.md`).
  What held: a computer-assisted *certified* Landau damping root (`1.41566188860… − 0.15335946691… i` at
  `k = 0.5`), a Vlasov–Poisson solver matching it to 0.14 %, a ballistic plasma echo matching its closed form
  to 2×10⁻⁹, and an exact persistent-homology duality control on Gross–Pitaevskii data. What did not: two
  topological instruments — density-only vortex detection (precision 0.87, recall 0.43) and phase-space hole
  counting — both refuted for one reason (persistence is depth to the *connecting saddle*, and the features
  share a valley); two free-streaming formulas misapplied to the interacting plasma (both off by ≈ 9 %); and
  three criteria that failed through my own design. A 17 % growth-rate discrepancy was resolved in minutes
  because one side of it was certified. Draft paper: `paper/kinetic_known_answers.pdf`.
- **A pre-registered positive control voided an entire run** by revealing that `k*` lay outside the
  7-pressure table's range — a data-scope error, not a code error.
- **A TDA measurement did not survive its own check.** A line-graph floor of `F = 1.491 ξ` against a
  null of `0.101` looked like a clean confirmation; a threshold sweep showed `F` tracks the
  segmentation threshold (ratio 1.00–1.24 across a 4× change). The floor was the parameter, not the
  physics. Rebuilt with threshold-free topological line tracing, the floor survives (`F = 0.943 ξ`,
  6.1× the null) — but the pre-registered `f_<` criterion then **refutes the hypothesis as written**
  (0.402 vs 0.381 in the null). The split verdict is reported as a split verdict.
- **Registered predictions that were wrong** are recorded as wrong: a nullspace dimension (the trivial
  invariant `mass²` was forgotten) and prediction T4 (for an ordered lattice the floor, mean and loop
  scales coincide, so their ratio is 1, not ≫ 1).
- **A search killed by its own timeout** is recorded as a bookkeeping stop, never as a finding.
- **M3 closed with no quantitative result** after four measurement rounds; the diagnosis — single
  trajectories of a chaotic system, 72–105 % scatter — is the transferable output. **CLAIM-017 was
  retracted** after being tested in a neighbouring stream's own code.

## Verification

Every theorem is re-checked by **[Comparator](https://github.com/leanprover/comparator)**: statement
equivalence against a generated challenge, an axiom whitelist, and acceptance by *two independent
kernels* (Lean's own and `nanoda`). A pass means the proof is sound and uses only
`propext`, `Classical.choice`, `Quot.sound` — it does **not** mean the statement is the right physics,
which remains a human audit.

```bash
# 174 tests
uv run pytest tests/ -q

# Lean (4.34.0-rc2, Mathlib v4.34.0-rc2); 181 theorems across 21 libraries
cd lean_src && lake build

# Comparator (needs landrun, lean4export, nanoda_bin on PATH — see docs/COMPARATOR_SETUP.md)
python3 scripts/make_comparator_challenges.py
cd lean_src && lake env comparator ComparatorChallenges/DualLength.json
```

## Reproducing the headline measurement

```bash
# DS-QF: dual length vs the Bogoliubov floor, on Godfrin et al. (2021) published data
uv run python exploration/dual_scale/dual_length_p0.py      # P = 0, full range, with controls
uv run python exploration/dual_scale/pressure_trend.py      # 7 pressures

# The second invariant, and the nullspace search that bounds it
uv run python exploration/second_invariant/symbolic_check.py
uv run python exploration/second_invariant/run_search.py
```

## Layout

| path | contents |
|---|---|
| `lean_src/` | 21 Lean libraries, 181 theorems, axiom footprint `{propext, Classical.choice, Quot.sound}` |
| `lean_src/ComparatorChallenges/` | generated challenge statements + configs (contain `sorry` **by design**) |
| `src/quantumfluids/` | adapters, dispersion fit, shell model, invariant search, TDA (GUDHI) |
| `docs/DUAL_SCALE_PROPOSAL.md` | the consolidated proposal |
| `docs/GEDANKEN_DUAL_SCALE.md` | thought experiments, including the ones that failed |
| `docs/designs/` | pre-registrations — written *before* the runs, with results appended |
| `LEDGER.md` | every claim with its tier, status and, where applicable, its retraction |
| `LL.md` | lessons learned |
| `paper/` | LaTeX source and PDF |

## Method

Pre-registration before measurement (E-1); a claim exists only in `LEDGER.md`; every measurement
carries a control whose expected answer is known independently, and a run that fails its control is
**void** rather than reinterpreted; findings transfer between models only after checking the *property*
they depend on, never by analogy (LL-15).

## Related streams

`SocrateAI-Scientific-MechanicaFluidorum` (Hypothesis U; the O5 uniformity obstruction),
`SocrateAI-Mathesis` (Stream 0), and the OpenAI Navier–Stokes/Euler audit work. The Lean toolchain is
aligned at 4.34.0-rc2 across streams for cross-integration.

## Citing

Archived on Zenodo: **[10.5281/zenodo.22904619](https://doi.org/10.5281/zenodo.22904619)** (`v1.9.0`).
Cite the concept DOI **10.5281/zenodo.22855581** for all versions. See `CITATION.cff`.

*Note on the record history.* `v1.2.0` (10.5281/zenodo.22853896) was deposited as its own Zenodo
record rather than as an earlier version of the same one, so the two carry different concept DOIs.
They are joined by `isNewVersionOf` / `isPreviousVersionOf` relations, and `scripts/zenodo_deposit.py`
now takes `--new-version-of` so later releases stay on one record.

## Licence and status

Code: **MIT OR Apache-2.0**, at your option (`LICENSE`). Paper and documentation: **CC BY 4.0** (`NOTICE`). Nothing here is a
claim of priority; the literature check has been run and its outcome is in `RETRACTIONS.md`.
