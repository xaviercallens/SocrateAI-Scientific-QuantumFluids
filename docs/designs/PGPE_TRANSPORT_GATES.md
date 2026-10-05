# Vortex-transport campaign: gate record (G0, G1, G2) and admitted bases

Pre-registration: `PGPE_FRICTION_PREREG.md` amendments A1 and A1.1; shared by `PGPE_ALPHAPRIME_PREREG.md` (H03) and
`PGPE_EINSTEIN_PREREG.md` (H02). Data `data/generated/pgpe/transport/`. Date 2026-10-05.
All three gates have passed; production runs were launched only after this file was committed.

## G0 — synthetic recovery (Langevin point-vortex model, known α = 0.02, α′ = 0.10, η = 2×10⁻³)

| attempt | `1 − α′` | α (energy) | η | verdict |
|---|---|---|---|---|
| 1 | 0.22 | 7×10⁻⁵ | 0.99 | **FAIL** — generator defect: the two dipoles exchanged partners and one track became unphysical |
| 2 (generator stops on any opposite-sign approach < 2; analysis keeps a track while all such distances ≥ 4) | 0.9006 ± 0.0021 | 0.0187 ± 0.0024 | (1.53 ± 0.13)×10⁻³ | **PASS** |

Side checks on synthetic data: η is recovered without bias in three further parameter sets; the energy estimator of
α becomes noisy when diffusion is strong compared with friction (α/η ≲ 3), which its jackknife error reflects.

## G1 — T = 0 control (uniform condensate, 400 time units, fit on 100–400)

| clause | run 1 (`round2.imprint`) | run 2 (`imprint_v2`, amendment A1.1) |
|---|---|---|
| (i) `|α̂| ≤ 10⁻³` | 1.02×10⁻³ — **fail** | **4.1×10⁻⁴ — pass** |
| (ii) `1 − α̂′ ∈ [0.96, 1.04]` | 1.0021 — pass | **0.9986 — pass** |
| (iii) `η̂ ≤ 2×10⁻⁵` | pass (bounded residual ≈ 0.1) | **pass (−1×10⁻⁶; bounded residual ≈ 0.005)** |
| (iv) single dipole: momentum `2πnd` within 5 %, constant | 0.71–0.91, separation shrinks 9.57 → 8.74 — **fail** | **0.96–0.99, constant to 3×10⁻¹⁰; separation 9.815 → 9.821 — pass** |

At T = 0, with a correct imprint, a vortex pair in the projected GPE neither shrinks nor diffuses over 400 time
units and its members move at the torus point-vortex velocity to 0.14 %. Floors of the instrument:
`|α| ≈ 4×10⁻⁴`, residual mean-square displacement 0.005.

## G2 — thermal known answer (T = 0.115, antiparallel `d₀ = 10`, 2 runs × 2000 time units, `imprint_v2`)

| quantity | value | window | verdict |
|---|---|---|---|
| α, energy estimator | **0.00705 ± 0.00012** | [0.0028, 0.0112] | **PASS** |
| α, regression | 0.00755 ± 0.00036 | — | agrees with the energy estimator within 7 % |
| `α′ = 1 − (1 − α̂′)` | **−0.0080 ± 0.0007** | [−0.02, 0.06] | **PASS** |

Energy drift 9×10⁻⁸; four tracked vortices detected in 99.9 % of samples; no thermal vortex in the base.
The point-vortex energy falls monotonically (−1.1 → −2.9 and −3.2). The two dipoles shrink from 10 to 7–8, drift
toward each other and, after t ≈ 1500, collide and exchange partners (new pairs of size 6–8); the estimators do not
use the pairing, and every opposite-sign distance stays above the validity limit of 4.

Observed, not part of the gate:
- α(T = 0.115) = 0.0070 is 17 times the T = 0 floor, within a factor 2 of the round-3 arm's 0.0056 and of
  Shukla–Brachet–Pandit's interpolated 0.013.
- `α′` is **negative** and eleven standard errors from zero: the vortices move 0.8 % *faster* than the point-vortex
  velocity (at T = 0: 0.14 % slower). The Iordanskii-limit value at this temperature would be +0.027.
  One temperature decides nothing; the registered regression needs the warmer bases.
- Residual mean-square displacement: 0.21 at lag 5 rising to 0.82 at lag 400; fitted η = (3.6 ± 1.0)×10⁻⁴ with a
  scaling exponent of 0.71, **outside the registered [0.8, 1.2]**: by rule E2, η is not quoted at this temperature
  from these two runs. (The Einstein value would be 1.3×10⁻⁴.)

## Bases

| base | T | T/T_BKT(64) | `n_s/n` | raw vortex count | status |
|---|---|---|---|---|---|
| `sweep/e0.60_s11_t4000` | 0.115 | 0.14 | 0.973 | 0.00 | admitted |
| `transport/base_e0.70` (heated, 1000 + 500 time units) | 0.220 | 0.27 | 0.947 | 0.00 | admitted |
| `transport/base_e0.80` (same) | 0.353 | 0.43 | 0.906 | 0.36 | admitted (below the 0.5 limit) |
| `sweep/e0.90_s12_t4000` | 0.458 | 0.56 | 0.825 | 5.8 | report only |

## Production (launched after this commit)

Per base: antiparallel geometry, `d₀ ∈ {8, 12}`, seeds 1–3, 2000 time units, `imprint_v2` — 24 runs
(`prod_e*_d*_s*.npz`). Hypothesis W: two single-dipole runs, `d₀ = 12`, T = 0.115, L = 64, 4000 time units
(`W1_*.npz`). W2 (L = 96) needs a base state that does not exist yet and is not launched here.
