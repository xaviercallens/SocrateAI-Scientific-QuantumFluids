# Pre-registration: the friction law α ∝ ρ_n/ρ against cutoff and temperature (direction R2-04 / D7)

Filed 2026-10-07 09:00, before any run. Runs if the counterflow control (W2) refutes W; otherwise it is the second
campaign. Builds on `PGPE_TRANSPORT_RESULTS.md`: `α = (0.232 ± 0.014) ρ_n/ρ` at `T/T_BKT = 0.14, 0.27, 0.43`, one
cutoff (`k_cut = π`, i.e. half the grid wavenumber at `dx = ξ/2`), `mg = 1`.

## Question

Is the coefficient 0.23 a property of the vortex–phonon interaction in the classical field, or of the cutoff that
defines its phonon bath? Both α (momentum transfer from phonons scattering off the vortex) and ρ_n (phonon momentum
susceptibility) are sums over the thermal modes up to the cutoff; their ratio may or may not be.

## Design

Two further cutoffs at the same temperatures: `k_cut = 2π/3` (same grid, projector at a third of the grid
wavenumber) and `k_cut = 2π` (`dx = ξ/4`, `N = 256` at L = 64, projector at half). Base states at
`T/T_BKT ≈ 0.14` and `0.27` for each cutoff (heated from vortex-free states, 1000 time units of equilibration;
T, `n_s/n` and raw vortex count measured; a base is admitted only if its vortex count is below 0.5). Antiparallel
pairs, `d₀ ∈ {8, 12}`, three seeds, 2000 time units; energy and regression estimators as registered in A1.
Known answer per cutoff: the T = 0 control of A1 repeated (no shrink, no diffusion, point-vortex speed within 4 %).
Estimated 30 CPU-hours plus 10 for the `dx = ξ/4` bases.

## Predictions (frozen)

- **FL1 (proportionality at each cutoff).** At each cutoff, α at the two temperatures is proportional to `ρ_n/ρ`
  (free intercept consistent with zero at 2σ).
- **FL2 (the registered prediction: near-universality).** The coefficient `c = α/(ρ_n/ρ)` differs between the three
  cutoffs by less than 20 % (spread of the three values over their mean). Rival: a shift larger than 40 % with the
  logarithm of the cutoff energy, as a bath-dominated momentum transfer would give.
- **FL3 (kinetic reading, computed before the runs — `FRICTION_LAW_THEORY_NOTE.md`).** `α/(ρ_n/ρ) = (ρ/ρ_s)⟨c_g σ_tr⟩/κ`,
  the disk-averaged transport cross-section of the vortex; the measured 0.232 means `⟨σ_tr⟩ = 1.4 ξ` (geometric
  core size). Sonin's Born transport cross-section `σ_∥ = κ²k/(8c²)` (valid for `2πkξ ≪ 1`, i.e. < 3 % of our modes),
  extrapolated over the disk, gives 10 ξ: seven times the measurement. Expectation recorded: `c` nearly constant
  across cutoffs (spread 10–30 %, weak ordering `c(2π/3) ≤ c(π) ≤ c(2π)`); the rival is the Born scaling
  `c ∝ k_c`, i.e. `0.67 : 1 : 2`.
- **Report:** `α′` at each cutoff (with the T = 0 baseline of each); the residual exponents.

Verdict: FL1 ∧ FL2 → the friction law is a property of the model's vortex–phonon interaction, usable at any cutoff
within 20 %. FL1 ∧ ¬FL2 → the coefficient is a bath property; the cutoff dependence is reported as the result.

## Amendment FL-A1 (2026-10-08 21:45) — filed after the coarse arm and the fine T = 0.127 arm were read, BEFORE the fine T = 0.173 arm (started 21:31) is read

**What was read.** Coarse arm (k_cut = 2π/3, T = 0.100 and 0.216, 6 runs each) and fine arm (k_cut = 2π, T = 0.127,
6 runs). The fine T ≈ 0.22 base (e = 1.25: T = 0.217, 1.32 thermal vortices) failed admission (n_v < 0.5); the
second fine temperature is the admitted e = 1.10 base (T = 0.173, n_v = 0.08), not the registered 0.22 — a deviation, reported.

**Registered predictions, as read** (details in `PGPE_FRICTION_LAW_RESULTS.md`): c = α_E/(ρ_n/ρ) = 0.32 ± 0.05
(2π/3, T = 0.100), 0.31 ± 0.04 (2π/3, T = 0.216), 0.232 ± 0.014 (π, reference), 0.096 ± 0.013 (2π, T = 0.127).
**FL2 (spread < 20 %) FAILS** (factor 3.3 between the extremes); **the Born rival (c ∝ k_c) FAILS** (c falls with
the cutoff, it does not rise); **FL3's expectation (spread 10–30 %) FAILS.** FL1 holds at 2π/3 (two temperatures,
c = 0.32, 0.31) and at π (published); it cannot be tested at 2π until the second temperature is read.

**Post hoc observation (not registered; labelled as such).** α is nearly independent of the cutoff at fixed T while ρ_n
is not: α_E/T = 0.049 ± 0.008 (2π/3, 0.100), 0.056 ± 0.008 (2π/3, 0.216), 0.054 ± 0.004 and 0.063 ± 0.011 (π, 0.115 and
0.220), 0.053 ± 0.007 (2π, 0.127). The earlier "α ∝ ρ_n" was a degeneracy: at fixed cutoff ρ_n ∝ T.

**New hypothesis H-T: α = a·T with a = 0.054 ± 0.004, independent of the cutoff for k_cξ ≥ 2.** (The coarse cutoff,
k_cξ = 2.1, already has the full friction: the modes that drag the vortex have kξ ≲ 2.)

**Prediction for the unread fine arm, fixed now:** at T = 0.1734 (e = 1.10, ρ_n/ρ = 0.0802, k_cut = 2π),
**H-T predicts α_E = 0.0094 ± 0.0010** (a·T with its error); the proportionality to ρ_n at the 2π coefficient
(c = 0.096) predicts 0.0077. **Decision:** α_E ∈ [0.0084, 0.0104] supports H-T; α_E ∈ [0.0067, 0.0087] supports
"∝ ρ_n at the cutoff-specific coefficient"; the two windows overlap in [0.0084, 0.0087] and a value there is
**inconclusive**. The comparison across cutoffs (the 2π point against the others) does not depend on this arm.

**Instrument caveat to carry.** At k_cut = 2π/3, α′ = −0.017 ± 0.001 (T = 0.100) and −0.031 ± 0.003 (T = 0.216),
and the d₀ = 12 pairs show 35 % larger α than d₀ = 8 at k_cut = 2π/3 and 2π; at k_cut = π neither appeared. These are
reported, not explained: the pair-size dependence is a possible bias of the energy estimator at the coarse cutoff or a
physical finite-pair effect.
