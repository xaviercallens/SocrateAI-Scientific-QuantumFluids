# Results: vortex transport in a closed 2D Bose field — friction (A1), transverse coefficient (H03), Einstein relation (H02)

Pre-registrations: `PGPE_FRICTION_PREREG.md` (amendments A1, A1.1, A1.2), `PGPE_ALPHAPRIME_PREREG.md`,
`PGPE_EINSTEIN_PREREG.md`. Gates: `PGPE_TRANSPORT_GATES.md` (G0, G1, G2 all passed). Data
`data/generated/pgpe/transport/` (`prod_e0.60_*`, `G2_*`, `prodB_*`, `W1_*`; estimates in `production_estimates.json`).
Analysis 2026-10-06 06:45, after all 26 + 18 runs finished; decision rules applied as written.

## Data admitted

| base | T | T/T_BKT | `n_s/n` | `ρ_n/ρ` | runs (tracks) | track lengths (time units) | detections per sample |
|---|---|---|---|---|---|---|---|
| T = 0 control | 0 | 0 | 1 | 0 | 1 (2 pairs) | 400 | 4.00 |
| e = 0.60 | 0.115 | 0.14 | 0.973 | 0.027 | 8 (16 pairs; 6 production + 2 gate) | 1528–2000 | 4.00 |
| e = 0.70 | 0.220 | 0.27 | 0.947 | 0.053 | 6 (12 pairs) | 556–2000 (three ended by annihilation) | 4.09–4.13 |
| e = 0.80 | 0.353 | 0.43 | 0.906 | 0.094 | 6 (12 pairs) | 118–729 | 4.85–5.24 — **flagged** (thermal vortices in > 5 % of samples) |
| e = 0.90, s12 | 0.458 | 0.56 | 0.825 | 0.175 | 6 | 30–228 | 9.9–11.9 — report only, as registered |

The warm runs are the `prodB_*` repeats of amendment A1.2 (tracking radius 3.0); the first set lost its tracks
inside the settling window and produced no estimate. Settling time 100 excluded everywhere.

## Friction α(T) — amendment A1 criteria

| T | α, energy estimator | α, regression | `α(d₀=8)/α(d₀=12)` | regression/energy |
|---|---|---|---|---|
| 0 | 0.00041 (floor) | 0.00020 | — | — |
| 0.115 | **0.00617 ± 0.00041** | 0.00645 ± 0.00037 | 0.91 | 1.05 |
| 0.220 | **0.0138 ± 0.0023** | 0.0156 ± 0.0014 | 0.76 | 1.13 |
| 0.353 (flagged) | **0.021 ± 0.014** | 0.024 ± 0.007 | 1.04 | 1.18 |

- **F1′ (no intrinsic size dependence): PASS** — the `d₀ = 8 / 12` ratio lies in [0.7, 1.43] at all three
  temperatures (≥ 2 required). The size dependence of the withdrawn gate was an instrument artefact.
- **F2 (monotone in T): PASS** — 0.0062 < 0.0138 < 0.021 (the last with a large error).
- **F3 (two estimators agree within 25 %): PASS** at all three temperatures (5 %, 13 %, 18 %).
- Against the literature (report only): Shukla, Brachet & Pandit (2014) interpolated to `T/T̃_BKT = 0.14` give
  ≈ 0.013; we find 0.0062 — a factor 2 below, with their T̃_BKT itself uncertain. At `T/T_BKT = 0.27` and 0.43 no
  closed-field value existed; ours are 0.014 and 0.02, in the range of the atomic-gas measurements of Moon et al.
  (0.01–0.03) and above Kwon et al.'s unitary-gas 0.006. α/ρ_n is 0.23, 0.26, 0.22 at the three temperatures:
  **α is proportional to the normal fraction within errors**, `α ≈ 0.24 ρ_n/ρ` (not pre-registered).

## Hypothesis W (phonon wind of a closed box) — W1, W3 evaluated; W2 not run

Two single dipoles, `d₀ = 12`, T = 0.115, L = 64, 4000 time units each (`W1_*`). Neither annihilates.
- Run 1: separation 11.6 → 9.3 by t ≈ 1800, then 9.3–9.9 for the rest; `d²` slope over [2000, 4000] is +4 % of
  the early (shrinking) slope: **W1 satisfied**.
- Run 2: 11.2 → 10.2 by t ≈ 1600, then **re-expands** to 11.2–11.3; the late `d²` slope is positive, 57 % of the
  early magnitude. By the letter of W1 ("slope below 25 % of its early value") this run fails; in substance the
  pair stopped shrinking and moved back toward the predicted stall point (plane formula 10.2; torus-corrected ≈ 9).
- Zero-impulse pairs at the same temperature shrink steadily from 10 to 7–8 within 1500 time units — the contrast
  W predicts.
- **W3 (the wind seen directly): PASS** — the momentum of the modes with `|k| > 1`, projected on the initial
  impulse direction, follows the impulse lost by the pair with slopes 0.68 and 0.52 (window [0.5, 1.2]); in run 1
  it rises from 3.0 to 17.9 while the pair sheds 14; in run 2 it falls back as the pair re-expands.
- **W2 (no stall at L = 96) was not run** (no L = 96 base state exists). Verdict: **unresolved, with first
  support** — W1 one of two by the letter, both in substance; W3 both.

## Transverse coefficient α′ — `PGPE_ALPHAPRIME_PREREG.md`

| `ρ_n/ρ` | T | `1 − α̂′` | `α̂′` | σ |
|---|---|---|---|---|
| 0 | 0 | 0.9986 | +0.0014 | (0.0015 assumed, the T = 0.115 scale) |
| 0.027 | 0.115 | 1.0100 | **−0.0100** | 0.0015 |
| 0.053 | 0.220 | 1.0154 | **−0.0154** | 0.0029 |
| 0.094 | 0.353 | 1.0093 | −0.0093 | 0.0106 |

Weighted regression of `α̂′` on `ρ_n/ρ`: slope **b = −0.31 ± 0.05**, intercept 0.0002 ± 0.0014; 2σ upper bound
on `b` = −0.21.
- **Registered rule: "no transverse force"** (2σ upper bound on `b` below 0.3; the Iordanskii-like window
  `b ∈ [0.6, 1.4]` is excluded by 18σ). **The registered prediction (Iordanskii-like) is refuted.**
- **But α′ is not zero**: it is *negative*, 7σ at T = 0.115 and 5σ at 0.220 — the vortices move 1–1.5 % *faster*
  than the point-vortex velocity induced by the other vortices, while at T = 0 they move 0.14 % slower. Neither
  theory has a sign for this. Candidate systematics, to be tested before any physical reading (none is excluded
  here): a thermal change of the pair's own translation speed (the Jones–Roberts compressibility correction, which
  at T = 0 and `d = 10` is −0.14 %, could change with the thermal depletion of the core); a local normal-fluid
  drift set up by each pair's own drag (the wind of W, which would act with the sign observed if α′ > 0); a bias of
  the sub-grid detector in a thermal field. The size dependence at T = 0.115 (−0.0135 ± 0.0018 at `d₀ = 8`,
  −0.0038 ± 0.0016 at 12) points to the first.
- T3 (geometry independence against the round-3 arm) not evaluated here.

## Einstein relation — `PGPE_EINSTEIN_PREREG.md`

| T | K = 2πn_s/T | η measured | scaling exponent (E2, [0.8, 1.2]) | quoted? | `R_E = ηK/α` |
|---|---|---|---|---|---|
| 0 | — | ≈ 0 (bounded residual 0.005) | — | floor | — |
| 0.115 | 53.2 | (3.7 ± 0.7)×10⁻⁴ | 0.71 | **no** | (3.2 ± 0.6) |
| 0.220 | 27.1 | (1.08 ± 0.35)×10⁻³ | 0.82 | **yes** | **2.1 ± 0.7** |
| 0.353 | 16.1 | (1.8 ± 0.4)×10⁻³ | 1.28 | **no** | (1.4 ± 0.3) |

- **Verdict by the registered rule: inconclusive** — one admitted temperature (two required). At that
  temperature `R_E = 2.1 ± 0.7` sits on the edge of the Einstein window [0.5, 2]; the two unquoted temperatures
  would give 3.2 and 1.4. Taken together (and against the rule, which is why it is not a verdict), the vortex
  diffuses at **1.4–3 times the Einstein value**, decreasing with temperature — not the 100× of Neely et al. 2024,
  and not clearly 1.
- The scaling exponents are the reason for caution: at T = 0.115 the residual mean square grows sub-linearly
  (0.71 — bounded oscillation plus diffusion), at 0.353 super-linearly (1.28 — drift from thermal vortices,
  whose presence flagged that base). The T = 0.115 excess is the result the five-minute probe hinted at, now with
  a clean instrument, but it does not pass the diffusive-scaling check and is not quoted.

## What is established, what is not

Established (pre-registered criteria passed): the longitudinal friction of a vortex pair in the closed classical
field, `α(T) = 0.0062, 0.014, 0.02` at `T/T_BKT = 0.14, 0.27, 0.43`, size-independent and estimator-independent;
α′ is not Iordanskii-like. Observed and not pre-registered: `α ≈ 0.24 ρ_n/ρ`; `α′` slightly negative; vortex
diffusion 1.4–3× the Einstein value; one single pair stalls while zero-impulse pairs shrink, with the phonon band
taking the momentum. Not established: the Einstein relation either way (inconclusive by rule); hypothesis W
(W2 missing); the origin of the negative α′.

Next (not started): the T = 0 pair-speed sweep in `d` (systematic for α′); an L = 96 base state (W2); longer tracks
at T = 0.220 and a cleaner T ≈ 0.3 base (the Einstein rule needs a second admitted temperature); the round-3 arm
re-analysed with the v2 estimators (T3).
