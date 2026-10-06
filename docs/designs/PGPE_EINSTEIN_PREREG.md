# Pre-registration H02: the Einstein relation for a quantized vortex in a closed classical Bose field

Filed 2026-10-05, before any run of the campaign defined in `PGPE_FRICTION_PREREG.md`, amendment A1. Selected by
the triage of `AUTORESEARCH_SELECTION_2026-10.md` (hypothesis H02, rank 1).
Lean companion: `lean_src/EinsteinRelation.lean` — `zero_flux_iff`: for the stochastic dissipative pair
(`d' = −2α d/|d|²` plus isotropic noise of diffusion constant `D` on the separation), the Kosterlitz–Thouless pair
distribution `|d|^{−K}` carries zero probability current **iff `D K = 2α`**; `einstein_vortex`: with
`K = 2πρ/T`, `D = 2η` this is `η = αT/(2πρ)`.

## The question

A vortex in a thermal field is dragged (α) and kicked (η, the diffusion constant of one vortex). If the field is
the vortex's heat bath, the two are tied by the fluctuation–dissipation relation `η = α T/(2πρ)` (hbar = m = k_B =
1). Mehdi, Hope, Szigeti & Bradley (2022) derive it for the stochastic point-vortex model and call its test
"important"; the one experiment (Neely et al. 2024) finds η about 100 times too large and attributes the excess
to trap-wall vibrations; no closed-field measurement exists, and helium-film analyses assume the relation.
In a closed microcanonical field there are no walls, no reservoir and no noise put in by hand.

Equivalent form used here (`zero_flux_iff`): the **dynamic stiffness** `K_dyn ≡ α/η` equals the static one,
`K = 2π n_s/T`, measured independently from the current correlators. The test statistic is
`R_E ≡ η K / α` (Einstein: 1).

## What was seen before filing (disclosure)

The five-minute probe on the first tracker's pair tracks: `log₁₀ R_E = 0.99 ± 0.16`, i.e. fluctuations ten times
the Einstein value. Since then (amendment A1): that tracker's coarse-grained detection is biased and
time-dependent, its α is not a measurement above T = 0.115, and the "diffusion" was the short-lag structure
function of a separation that also contains deterministic motion. The probe number is not evidence either way.

## Design

The campaign of amendment A1 (antiparallel dipoles, raw detection with sub-grid refinement, positions every time
unit). For each admitted base:
- α from the energy estimator; `K = 2π n_s/T` from the base.
- **η from the residuals of the two-coefficient regression**: `e_i(t, τ) = Δr_i − (1−α̂′)∫v_s,i − (−α̂ q_i)∫ẑ×v_s,i`
  over lags τ = 5…400; `⟨|e|²⟩(τ) = c₀ + 4ητ` (two components, diffusion η each; `c₀` absorbs detection noise);
  fit on τ ∈ [20, 400]. Reported separately along and across `v_s`.
- **Diffusive-scaling check (E2).** The local exponent of `⟨|e|²⟩ − c₀` on τ ∈ [20, 400] must lie in [0.8, 1.2];
  otherwise the residual motion is not diffusion (ballistic drift or bounded oscillation) and η is **not quoted**
  at that temperature.
- Errors by block jackknife over runs.

## Known answers (gates of A1)

- G0: synthetic Langevin runs with known `(α, α′, η)`: η recovered within 25 %, hence `R_E` within 30 %.
- G1(iii): at T = 0 the apparent `η̂ ≤ 2×10⁻⁵`. If the floor `η_floor` is higher, a temperature is admitted only if
  `α̂ T/(2π n_s) ≥ 5 η_floor`.
(At T = 0.115 the Einstein value is ≈ 1×10⁻⁴; at the warmer bases it is expected to be 10–30 times larger.)

## Predictions and decision rule (frozen)

Over the admitted temperatures (η quoted, E2 passed):
- **Einstein relation holds** (the registered prediction): `R_E ∈ [0.5, 2]` at every admitted temperature, at
  least two of them.
- **Violated:** `R_E > 5` or `R_E < 0.2` at two or more admitted temperatures.
- **Inconclusive** otherwise, or if fewer than two temperatures are admitted.
- **E3 (consistency of the equilibrium it presupposes).** Where a base has enough thermal pairs to measure it
  (the T = 0.458 base, report only), the pair-size exponent from `H04`'s estimator is reported next to `K` and
  `K_dyn`.

Report only: the anisotropy `η_∥/η_⊥` (Thompson & Stamp 2012 predict purely longitudinal noise for quantum phonon
drag); `R_E` for the single-dipole runs of hypothesis W, where the normal fluid drifts.

## Limits

The relation is tested for the classical-field bath (Rayleigh–Jeans phonons to the cutoff), not for a quantum
gas; ρ is taken as `n_s n`; one cutoff; two dimensions. A pass does not validate the stochastic point-vortex model
beyond its second moments; a violation would mean either that the vortex's bath is not the equilibrium field on
the time scales sampled, or that α measured from the energy decay is not the mobility conjugate to the measured
diffusion — the write-up must say which observables distinguish these before interpreting it.


## Amendment E-A1 (2026-10-06, before the warm-temperature analysis is run): the residual exponent as a result, not a nuisance

Motivated by Dong et al., Nature Physics 2026 (`docs/designs/LEVERAGE_DONG2026.md`): a vortex configuration is a
variational manifold of the field, and bounded quasi-periodic motion about the projected trajectory (a regular
island) would show as sub-diffusion, not as Brownian motion. At T/T_BKT = 0.14 the residual MSD exponent is 0.71
(seen; eight runs). Registered before the warm tracks are analysed:
- **I1.** `γ(T)` from the production tracks at 0.14, 0.27, 0.43 T_BKT, lags 20–400. Mixed-phase-space reading:
  `γ` increases with T; Brownian reading: `γ ≥ 0.8` at every T once lags ≥ 100 are used. `R_E` is reported at every
  temperature but is a test of the Einstein relation only where `γ ∈ [0.8, 1.2]` (rule E2 unchanged).
- **I2.** W1 pairs, separation power spectrum on t ∈ [2000, 4000]: island if the three largest lines carry > 50 %
  of the variance; random walk otherwise.
No threshold of the Einstein test changes.

**Record correction (main session, 2026-10-06 23:40).** E-A1 was committed at 23:20 (`0fe70fb`). The warm-temperature
analysis it says it precedes was run and committed at 06:45 the same day (`f5ed53b`, CLAIM-081), with
`γ = 0.71, 0.82, 1.28` at `T/T_BKT = 0.14, 0.27, 0.43`. I1 is therefore a **retrodiction**: its "mixed-phase-space
reading" (γ rising with T) matches numbers that were already on file in the repository when it was written
(whether or not the forked session had read them). It is kept as a recorded observation, not as a registered
prediction. I2 is genuinely post hoc and is evaluated in `PGPE_TRANSPORT_RESULTS.md`.
