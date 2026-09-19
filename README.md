# SocrateAI-Scientific-QuantumFluids

**A dual-scale proposal for quantum fluids — stated as a measurable quantity, proved where it is provable, and refuted where it is false**

[![Tests](https://img.shields.io/badge/tests-163%20passing-brightgreen)]() [![Lean](https://img.shields.io/badge/Lean-4.34.0--rc2-blue)]() [![Theorems](https://img.shields.io/badge/theorems-57%20kernel--checked-blue)]() [![Comparator](https://img.shields.io/badge/Comparator-55%20re--verified-success)]() [![Release](https://img.shields.io/badge/release-v1.0.0-orange)](https://github.com/xaviercallens/SocrateAI-Scientific-QuantumFluids/releases)

---

## The result in one paragraph

For a quantum fluid with excitation dispersion `ε(k)`, sound speed `c` and mass `m`, define the
**dual length**

```
    ℓ(k) := ε(k)² / (ħ²c²k³)          k* := 2mc/ħ          √2 ξ = ħ/(mc)
```

Its phonon limit is `1/k` and its free-particle limit is `k/k*²`. Because the Bogoliubov dispersion is
Pythagorean in those two branches, `ℓ_B(k) = 1/k + k/k*²` **exactly** — the `R + α′/R` shape as an
identity rather than an analogy, invariant under `k ↦ k*²/k` and bounded below by `√2 ξ`. All of that is
Lean-checked. **Superfluid ⁴He violates the bound by a factor 21 at saturated vapour pressure, rising
to 51 at 24 bar.** So the dual-scale idea is not dead; it is *localised* to the weakly interacting
regime, and `ℓ/(√2ξ)` is a single dimensionless number measuring how far a real superfluid sits from it.

Full statement: **[docs/DUAL_SCALE_PROPOSAL.md](docs/DUAL_SCALE_PROPOSAL.md)**.

## What is proved, measured, refuted, and open

| | status | where |
|---|---|---|
| `ℓ`, its two limits, duality invariance, the `√2 ξ` floor, the `k^{3/2}` envelope, the structure-factor form `S(k) ≤ √(k/2k*)`, and two falsification lemmas | **proved** (12 theorems) | `lean_src/DualLength.lean` |
| DS-QF for ⁴He | **refuted**, 7 pressures, controls passing | CLAIM-024 |
| DS-QF′ — the structure belongs to the weakly interacting regime | **proposed, untested** | needs cold-atom or `S(k)` data |
| Second invariant of the complexified shell model; Hamiltonian SHG structure; the σ-rule | **proved** (7 theorems) + exact symbolic + search | CLAIM-023 |
| Truncated Gross–Pitaevskii: `Q = Σ_q|A_q|² ≥ 0` for every truncation | **proved** (7 theorems) | `lean_src/GPGalerkin.lean` |
| TDA floor in a real vortex tangle (workstream T) | **inconclusive** — the statistic was confounded by its own threshold | CLAIM-T1 |
| Novelty of any of the physics | **not claimed**; literature check pending | blocks external claims |

## Negative results are first-class here

Several of the most useful outcomes in this repository are failures, and they are kept at the same
level of detail as the successes:

- **A pre-registered positive control voided an entire run** by revealing that `k*` lay outside the
  7-pressure table's range — a data-scope error, not a code error.
- **The TDA floor measurement did not survive its own check.** A line-graph floor of `F = 1.491 ξ`
  against a null of `0.101` looked like a clean confirmation; a threshold sweep showed `F` tracks the
  segmentation threshold (ratio 1.00–1.24 across a 4× change). The floor was the parameter, not the
  physics. Nothing from that run is citable.
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
# 163 tests
uv run pytest tests/ -q

# Lean (4.34.0-rc2, Mathlib v4.34.0-rc2); 57 theorems across 7 libraries
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
| `lean_src/` | 7 Lean libraries, 57 theorems, axiom footprint `{propext, Classical.choice, Quot.sound}` |
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

## Licence and status

Research code. Nothing here is a claim of priority: the physics of the ⁴He roton is textbook, and the
contribution is the dimensionless packaging plus the Lean-checked bound. A literature check is pending
and blocks any external novelty claim.
