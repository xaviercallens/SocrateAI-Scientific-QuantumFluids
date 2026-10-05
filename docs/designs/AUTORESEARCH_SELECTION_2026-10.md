# Ten hypotheses, ten five-minute probes, three selected (autoresearch triage, 2026-10-05)

Protocol `exploration/autoresearch/program.md` (Karpathy's `autoresearch` loop adapted to hypothesis selection).
Hypotheses, rivals, probes and the three judgement terms (novelty, reach, cost) were committed in `5ecad2c`
**before any probe ran**; the literature behind them is `LITERATURE_REVIEW_2026-10.md` (773 entries, vector
database on the large disk). Log: `exploration/autoresearch/results.tsv`; probe outputs: `logs/H*.log`.

`score = min(D,5)/5 · novelty · reach/3 · 1/(1 + cost_days/5)`; `D` is the only term computed from data.

## Results

| rank | id | hypothesis | D | novelty · reach · cost | score | probe outcome (five minutes, existing data unless stated) |
|---|---|---|---|---|---|---|
| 1 | **H02** | Einstein relation for a vortex in a closed field, `η = αT/(2πρ₀)` | 12.8 | 1.0 · 3 · 5 d | **0.500** | `log₁₀(η/η_Einstein) = 0.99 ± 0.16` on 15 blocks of 5 dipole tracks: diffusion ≈ 10× the Einstein value — neither the theory (0) nor the 100× of Neely et al. (2) |
| 2 | **H07** | Finite-k dielectric relation: transverse response = vortex polarisation + phonon floor at every k | 14.4 | 0.6 · 2 · 2 d | **0.286** | on six shells never used before (`|m|² = 5…16`, L = 192): r = 0.987 over 36 (run, shell) points, slope 0.60, floor 0.13; within the healthy runs alone r = 0.77 |
| 3 | **H03** | Transverse friction α′: do vortices move at the point-vortex velocity? | 3.8 | 0.6 · 3 · 4 d | **0.255** | known answer at T = 0.115: slope **0.997 ± 0.009**; at T ≈ 0.45: `1 − α′ = 0.717 ± 0.045` and `0.833 ± 0.046` (ρ_n/ρ = 0.41, 0.18) |
| 4 | H06 | Last-pair equilibration; time-resolved box-scale charge gives z | 1.8 | 1.0 · 3 · 4 d | 0.205 | `ln Q₁` vs `ln N_v` slope +0.25 ± 0.54 over 7 runs (one pair: 0; extensive: 1): consistent, weak; Q₁ median 1.24 (depressed) vs 0.27 (healthy) |
| 5 | H09 | Cutoff law of the classical-field BKT point | 2.7 | 0.6 · 3 · 3 d | 0.201 | retrodiction: predicted `nλ² = 7.75` (T = 0.811), measured 7.65; rival 5.94; σ = full L = 32→64 shift |
| 6 | H04 | Pair-size law `P(r) ~ r^{1−K}` | 3.5 | 0.6 · 2 · 2 d | 0.198 | exponent rises with K, slope 0.25 ± 0.07 (law at the local K: 1; rival 0); a = 4.7–6.7 for K = 4.3–10.3 |
| 7 | H01 | Friction α(T), α(d), 0.14–0.95 T_BKT | 1.5 | 0.6 · 3 · 4 d | 0.098 | per-track slope significance low; α = 0.002–0.006 (T = 0.11), 0.13 (T = 0.66), 0.39 (T = 0.44) |
| 8 | H05 | Josephson relation with the torus geometry factor | 0.9 | 0.6 · 2 · 2 d | 0.050 | `ηK − 1 = +0.29 ± 0.23` (five final fields): cannot separate 0 from +0.2 |
| 9 | H10 | Two-fluid sound in S(k, ω) | 1.8 | 0.3 · 2 · 4 d | 0.040 | upper branch c₁ = 0.52–0.77; candidate lower branch at z = 1.4–4.8, not robust |
| 10 | H08 | Supercurrent decay law (AHNS vs MWJO exponent) | 0.0 | 0.6 · 3 · 6 d | 0.000 | 5-minute simulation, L = 32, T ≈ 0.79: no slip at windings 1, 2, 3 in 120 time units each |

**Selected: H02, H07, H03.**

## What drove the selection (sensitivity)

- By `D` alone: H07, H02, H03, H04, H09, H06, H10, H01, H05, H08.
- By the prior terms alone (before any probe): H06, H02, H09, H01 = H03, H04 = H05 = H07, H08, H10.
- H02 is in the top two either way. H07 is selected by its probe, H03 by both. **H06 was first on priors and
  fell to fourth on a seven-point probe**; H09 is fifth by 0.004 on a retrodiction with a deliberately generous σ.
  The margin between ranks 3, 4, 5 and 6 (0.255, 0.205, 0.201, 0.198) is smaller than the arbitrariness of the
  cost scale: the selection of H02 is robust, the choice of H03 over H06/H09/H04 is not, and is recorded as such.

## Process record

- H03's first run crashed (object-dtype positions from the `npz`); fixed in `probes.py` and re-run, both rows kept
  (rule 3). No estimator was changed after a valid result.
- H01's probe unintentionally excluded one finished known-answer track (a filename filter matched `d8_seed1`
  as well as the excluded `d12_seed1`). Not corrected after the fact; it would not change the rank materially.
- H06 and H09 used inputs partly known before registration (flagged in `hypotheses.json`).
- Stated bias of the procedure (program.md rule 5): hypotheses that need days of new simulation for a first signal
  (H08, H09's cutoff scan, H06's seed ensembles) cannot score on `D`.

## What the three selected probes do and do not show

These are triage numbers, not results. Each has a named confound that the full test must remove.

- **H03 (α′).** The estimator is validated where the answer is known: at T = 0.115, eight imprinted vortices
  move at the torus point-vortex velocity to 0.3 ± 0.9 %. At T ≈ 0.45 they move 17–28 % slower.
  Confound: at that temperature thermal pairs are present, and noise in the *predicted* velocity (pairs appearing
  between samples) biases a regression slope downward (errors in variables). The full test must predict from the
  imprinted vortices only, bound the bias by the reverse regression, and sample faster than 10 time units.
  If it survives, `α′ ≈ 0.17–0.28` against `ρ_n/ρ = 0.18–0.41` would be the first error-barred transverse
  coefficient for a bosonic classical field (Shukla et al. 2014 could not give one), bearing on the
  Iordanskii-force controversy.
- **H02 (Einstein relation).** The separation of a tracked pair fluctuates about its friction law ten times more
  than the Einstein relation allows. Confounds: deterministic motion (imprint sound, the fields of thermal pairs,
  torus image forces) is counted as diffusion; α itself is poorly determined on these tracks. The full test needs
  the geometry Mehdi et al. proposed (centre-of-mass drift of a same-sign pair, where the deterministic part is a
  rotation), positions saved, many realisations, and the torus motion law.
- **H07 (finite-k dielectric relation).** The vortex-only transverse response tracks the measured one on shells
  out to `|k| = 4·2π/L` with one slope (0.60, i.e. the `n_eff² ≈ 0.64` of CLAIM-069) and a floor of 0.13. Within
  the healthy runs alone the correlation is 0.77: most of the signal is still the box-scale-charge contrast. The
  full test needs equilibrated states (the L = 192 extension, due ≈ 2026-10-07), the bound-pair polarisability
  plateau, and the density–vorticity cross terms measured directly.

**The pivot these three define:** *vortex transport and screening in a closed two-dimensional Bose field* — the
three coefficients of single-vortex motion (α, α′, η) measured with no reservoir and no fit parameter, and the
static screening ε(k) measured from vortex positions. H02 and H03 share one simulation campaign with the already
registered friction study (H01), whose known-answer gate has now passed (`PGPE_FRICTION_RESULTS.md`).

## Next

Full pre-registrations for H02, H03 and H07 (each with a known-answer gate and its Lean companion statement from
`hypotheses.json`), written before any production run; the friction pre-registration amended for the torus motion
law, imprint radiation and size-dependent mobility. H06 and H09 are kept as the reserve pair: H06's data arrive for
free with any seed ensemble, and H09 needs only one cheap ladder at a second cutoff.
