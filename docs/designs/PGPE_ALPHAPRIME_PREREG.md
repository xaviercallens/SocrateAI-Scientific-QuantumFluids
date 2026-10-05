# Pre-registration H03: the transverse friction coefficient α′ of a vortex in a closed classical Bose field

Filed 2026-10-05, before any run of the campaign defined in `PGPE_FRICTION_PREREG.md`, amendment A1 (instrument v2,
gates G0–G2, bases, geometry). Selected by the triage of `AUTORESEARCH_SELECTION_2026-10.md` (hypothesis H03).
Lean companion: `lean_src/DissipativeVortexDynamics.lean` — `centre_velocity_identity` (a pair's centre moves at
`(1 − α′)/|d|` perpendicular to its axis, whatever α) and `energy_dissipation` (the energy decay carries no
information on α′): the two coefficients are measured by orthogonal observables.

## The question

With the normal fluid at rest a vortex moves at `v = (1 − α′) v_s − α q ẑ×v_s`. For α → 0 the two sides of a
thirty-year controversy predict different α′:
- **no transverse force from the normal fluid** (Thouless, Ao & Niu 1996): the vortex moves with the superfluid,
  `1 − α′ = 1`;
- **Iordanskii force** (Iordanskii 1964; Sonin 1997; Stone 2000): the vortex moves with the mass current,
  `1 − α′ = ρ_s/ρ`, i.e. `α′ = ρ_n/ρ`.
For a bosonic classical field the only published values (Shukla, Brachet & Pandit 2014) have no error bars and
change sign; in 3D truncated-GPE Kelvin-wave fits α′ "deviates" from expectation (Krstulovic & Brachet 2023);
experiments exist only for a Fermi superfluid (Grani et al. 2025, α′ = 0.10–0.22).

## What was seen before filing (disclosure)

The five-minute probe (round-3 Part A arms, positions every 10 time units, raw detection): regression slope of
measured on point-vortex-predicted displacement **0.997 ± 0.009 at T = 0.115**, and 0.717 ± 0.045, 0.833 ± 0.046
at T ≈ 0.45 where `ρ_s/ρ` is 0.59 and 0.82 by a stiffness estimate now known to be unreliable for the first.
Named confound: at T ≈ 0.45 thermal pairs enter the predictor, and noise in a predictor biases a slope downward.

## Design

The campaign of amendment A1 (antiparallel dipoles, `d₀ ∈ {8, 12}`, raw detection with sub-grid refinement,
`dt_sample = 1`). Predictor `v_s,i` computed **from the tracked imprinted vortices only**; temperatures restricted
to bases whose mean raw vortex count is below 0.5, so that the predictor has no thermal-pair noise.
Estimator: the two-coefficient regression of A1 at lag 10; standard error by block jackknife over runs and time
blocks; the reverse regression (predicted on measured) is reported as the errors-in-variables bound.
`ρ_n/ρ` of each base: `1 − n_s/n` from the base's own current correlators (vortex-free states, where that
estimator is clean), with its block error.

## Known answers (gates of A1)

- G1(ii): at T = 0, `1 − α̂′ ∈ [0.96, 1.04]`.
- G2 extended: at T = 0.115 (`ρ_n/ρ = 0.027`), `α̂′ ∈ [−0.02, 0.06]` — both theories agree there within errors.

## Predictions and decision rule (frozen)

Let `b` be the slope and `a` the intercept of the weighted regression of `α̂′(T)` on `ρ_n/ρ(T)` over the admitted
temperatures (T = 0 included as the point (0, α̂′(0))).
- **Iordanskii-like:** `b ∈ [0.6, 1.4]` and `|a| ≤ 0.03`.
- **No transverse force:** the 2σ upper bound on `b` is below 0.3.
- **Otherwise:** reported as measured ("intermediate"), with no label.
- **T3 (geometry independence).** The round-3 Part A arm at T = 0.115 re-analysed with the v2 estimators agrees
  with the antiparallel result within 2σ.
- **Not evaluable** if fewer than three admitted temperatures (including T = 0) have `σ(α̂′) ≤ 0.03`.

The prediction registered here is the first outcome (Iordanskii-like): the probe's two warm points sit near
`ρ_s/ρ`, and phonons scattering off a vortex in a classical wave field carry the Aharonov–Bohm asymmetry on which
the Iordanskii force rests. It is the outcome most exposed to the named confound, which this design removes.

Report only: α̂′ at the T = 0.458 base (thermal pairs present); dependence on `d₀`; the regression at lags 5 and 20.

## Limits

Classical field, one cutoff, two dimensions, `mg = 1`; `ρ_n` is the classical-field normal density, which depends
on the cutoff; the comparison between theories is made at the same `ρ_n/ρ`, not at the same `T/T_c` as an
experiment. Nothing is claimed about helium or Fermi superfluids.
