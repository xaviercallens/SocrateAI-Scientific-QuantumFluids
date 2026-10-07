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
  core size). Expectation recorded: `c(2π/3) < c(π) ≤ c(2π)` with a spread of 10–30 %; a spread above 40 % linear
  in `k_c` would mean the long-wavelength `σ_tr ∝ k` law holds to the cutoff.
- **Report:** `α′` at each cutoff (with the T = 0 baseline of each); the residual exponents.

Verdict: FL1 ∧ FL2 → the friction law is a property of the model's vortex–phonon interaction, usable at any cutoff
within 20 %. FL1 ∧ ¬FL2 → the coefficient is a bath property; the cutoff dependence is reported as the result.
