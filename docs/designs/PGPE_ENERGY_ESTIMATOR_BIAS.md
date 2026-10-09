# The energy estimator of α is biased low by diffusion (found by the Rust port of the estimators, 2026-10-09)

Source: the port of `transport_estimators.py` to rusty-SUNDIALS (`qf-pgpe::transport`, bit-identical to Python on four real tracks, max relative difference 2×10⁻¹⁴)
and its `g0_scan` example, which runs the registered synthetic gate G0 (known α = 0.02, α′ = 0.10, η = 2×10⁻³; 8 tracks of 2000 t.u.; detection noise 0.2) over many seeds.

## What the registered gate G0 did not show

G0 passed once (`PGPE_TRANSPORT_GATES.md`: α_energy 0.0187 against the 15 % criterion) on one numpy seed. Over seeds the energy estimator is **biased low**:

| synthetic truth α = 0.02 | α_energy (mean ± sd over 8–10 seeds) | α_regression | 1 − α′ (truth 0.90) |
|---|---|---|---|
| η = 0 (noise-free) | 0.0200 ± 0 (exact) | 0.0200 | 0.9000 |
| η = 5×10⁻⁴ | 0.0183 ± 0.0017 (−8 %) | 0.0198 | 0.9000 |
| η = 10⁻³ | 0.0163 ± 0.0012 (−18 %) | 0.0194 | 0.9000 |
| η = 2×10⁻³, detection noise 0 | 0.0156 ± 0.0032 (−22 %) | 0.0194 ± 0.0024 | 0.8994 |
| η = 2×10⁻³, detection noise 0.05 / 0.1 / 0.2 | 0.0151 / 0.0149 / 0.0145 | 0.0193 / 0.0193 / 0.0189 | 0.8992 |

The criterion α_energy within 15 % passes on 2 of 12 seeds. **The bias comes from the diffusion, not from the detection noise** (it is already −22 % with zero noise and barely moves when the noise grows 0 → 0.2);
the regression estimator is unbiased (within 3 %). (Cause, not proven: the stochastic part of H(t) is correlated with the cumulative regressor ∫2S dt, which depends on the same noisy path.)

## Consequence for the measured values

η/α in the real arms: 0.07 (k_c = 2π/3, T = 0.100), 0.27 (T = 0.216), 0.08 (2π, 0.127), 0.19 (2π, 0.173) — the synthetic range 0.025–0.1 and beyond. The real energy and regression estimators differ by 5–21 % in exactly this direction
(regression/energy = 1.18, 1.06, 1.21, 1.14, 1.05, 1.13). **The published α values (energy estimator, the registered primary) are low by roughly 5–20 %; the regression estimator is the unbiased one.**

Robustness of the friction-law conclusions (`analyze_friction_law.py` numbers, regression estimator in place of the energy estimator):
- α/T = **0.0598 ± 0.0023**, χ² = 5.15 for 5 degrees of freedom (energy estimator: 0.0540 ± 0.0026, χ² 1.28): the temperature law holds with either estimator, with a 11 % higher coefficient;
- the coefficient c = α_reg/(ρ_n/ρ) is 0.355 ± 0.035, 0.250 ± 0.012, 0.124 ± 0.011 at k_c = 2.1, 3.1, 6.3: a factor 2.9 (energy: 3.1);
- the registered verdicts FL2, Born rival, one-common-c are unchanged.

## What this does and does not change

It does not change any registered verdict (they are comparisons across cutoffs with the same estimator). It changes the absolute values of α quoted in the vortex-transport paper (α = 0.0062, 0.014, 0.02 → 0.0065, 0.016, 0.024 with the regression estimator),
the reading of the G0 gate (the energy-estimator criterion is not a reliable known answer; the regression criterion is), and the T-law coefficient (0.054 → 0.060). Both papers state this (limits sections).
