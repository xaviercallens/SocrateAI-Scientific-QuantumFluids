# Pre-registration H07: the finite-wavevector dielectric relation of a compressible two-dimensional superfluid

Filed 2026-10-05. Selected by the triage of `AUTORESEARCH_SELECTION_2026-10.md` (hypothesis H07, rank 2).
Primary data: the L = 192 extension runs (`data/generated/pgpe/r3_C4/`, sampling window t ∈ [13 500, 14 500]),
**which do not exist yet** (first batch still integrating, no snapshot written at the time of filing).
Lean companion: `lean_src/PairPolarisation.lean` — `rho_polarisation`: for pairs with `|k·d_i| ≤ 1` the vortex
charge density is `i k·P(k)`, `P(k) = Σ d_i e^{ik·m_i}` the polarisation density, up to `Σ(k·d_i)² ≤ ‖k‖²Σ‖d_i‖²`;
`response_ceiling`: the point-vortex transverse response of bound pairs is at most `(2π)²(Σ‖d_i‖)²` at every `k`.

## The question

The superfluid stiffness is read from the transverse current response, `ρ_n(k) = ⟨|J_T(k)|²⟩/(T L²)`. In the
Coulomb-gas picture the vortices reduce it through their polarisation, `1/ε`; the dictionary is exact at `k = 0`
for lattice (Villain-type) models (Vallat & Beck 1994; Faulkner et al. 2017) and worked out at finite `k` for the
lattice Coulomb gas (Kim, Minnhagen & Olsson 1999). For a **compressible** Bose field there is no functional form:
classical-field papers extrapolate the current correlator to `k → 0` by fits of convenience (Foster, Blakie &
Davis 2010; Gawryluk & Brewczyk 2019), and the density–vorticity cross terms have not been measured.

**Hypothesis.** Mode by mode and snapshot by snapshot,
`J_T(k, t) = n_eff · 2πi ρ_q(k, t)/|k| + (phonon part uncorrelated with ρ_q)`, with a real, `k`-independent
`n_eff` equal to the **bare superfluid fraction** `1 − f`, where `f = ρ_n^{ph}/ρ` is the phonon normal fraction
(the vortex flow is carried by the fluid that the phonons have not already made normal). Then
`ρ_n(k)/ρ = f + (1 − f)² · (2π)²⟨|ρ_q(k)|²⟩/(k² T L²)` at every `k ≪ 1/ξ`: a measured `ε(k)`.

## What was seen before filing (disclosure)

CLAIM-069 (three lowest shells, run-averaged powers, post hoc): Pearson 0.996 over 18 runs, ratio 0.64 in the
depressed-stiffness runs. The five-minute probe on shells `|m|² = 5…16` of the **earlier** window
(t ∈ [6000, 7000], the C3 data): r = 0.987 over 36 (run, shell) points, slope 0.60, floor 0.13; within the healthy
runs r = 0.77. Both are correlations of time-averaged powers across runs, dominated by the contrast between runs
with and without a box-scale pair. No mode-by-mode amplitude regression has been computed on any data.

## Method

`exploration/pgpe/dielectric_modes.py`. For every snapshot and every wavevector `k = (2π/L)(m_x, m_y)` with
`|m|² ≤ 16`: `J_T(k)` from the field (`J = Im ψ*∇ψ`, transverse projection, as in `observables.current_correlators`)
and `ρ_q(k) = Σ_j q_j e^{−ik·r_j}` from the raw vortex positions of the same snapshot. Per run and per shell:
complex least squares of `J_T` on `X ≡ 2πi ρ_q/|k|` (with the sign convention fixed by gate D-G1) gives
`n_eff(k)`; the coherence `γ²(k) = |⟨J_T X*⟩|²/(⟨|J_T|²⟩⟨|X|²⟩)`; the residual power gives `f(k)`.
`n_eff(k)` is divided by the T = 0 core form factor measured in D-G1. Errors by jackknife over snapshots.

## Known answers (gates; run before the primary data are analysed)

- **D-G1 (T = 0).** Uniform condensate, L = 64, 12 random neutral pairs (pair size 4–10, positions known),
  field taken right after the imprint and after 20 time units: `n_eff = 1 ± 0.05` and `γ² ≥ 0.95` on the shells
  `|m|² ≤ 2`; the measured `n_eff(k)` for `|m|² ≤ 16` defines the core form factor. This also fixes the sign and
  normalisation conventions.
- **D-G2 (thermal, vortex-free + imprint).** The T = 0.115 state (`f = 0.027`, no thermal vortices) with the same
  12 pairs imprinted: `n_eff = (1 − f) ± 0.07` on `|m|² ≤ 2`, and the residual transverse power equals the
  state's own phonon normal fraction within 30 %.

## Predictions on the primary data and decision rule (frozen)

Six runs, 100 snapshots each, shells `|m|² ∈ {1, 2, 4, 5, 8, 9, 10, 13, 16}`.
- **D1 (the relation exists mode by mode).** `γ²(k) ≥ 0.4` on every shell in at least 5 of 6 runs.
  Rival (cross terms dominate): `γ² < 0.1`.
- **D2 (one real coefficient).** `|Im n_eff| ≤ 0.1 |n_eff|` and `max_k n_eff / min_k n_eff ≤ 1.25` over the shells,
  in at least 5 of 6 runs.
- **D3 (two-fluid closure).** Of the three candidates — total density (`n_eff = 1`), bare superfluid fraction
  (`n_eff = 1 − f`, with `f` the run's own residual power), renormalised superfluid fraction (`n_eff = n_s/n`) —
  the closest to the measured shell-averaged `n_eff` is **`1 − f`** in at least 5 of 6 runs, and
  `|n_eff − (1 − f)| ≤ 0.1` in those.
- **D4 (polarisability from pair statistics).** In the runs without a box-scale pair
  (`(2π)²⟨|ρ_q(k₁)|²⟩/(k₁² T L²) ≤ 0.45`), the plateau of `⟨|ρ_q(k)|²⟩/k²` over the shells `|m|² ∈ [4, 16]`
  equals `Σ_pairs d²/2` computed from the minimum-cost matching of `+` to `−` vortices (averaged over snapshots)
  within 30 %. A ratio outside [0.7, 1.3] is reported as the screening of dipoles by dipoles.
- **Verdict.** D1 ∧ D2 ∧ D3 → *the finite-k dielectric relation holds with the bare superfluid density*.
  D1 ∧ D2 with another closure in D3 → the relation holds with the closure found. D1 failing → no mode-by-mode
  relation; CLAIM-069's correlation is then a statement about run-averaged powers only.

Secondary (already partly seen, labelled as such): the same analysis on the t ∈ [6000, 7000] window.
Report only: `f(T)` against the Landau phonon formula evaluated with the measured occupations; `ε(k)` curves;
the stiffness reconstructed from vortex positions alone, `K_v = 2π[(1−f) − (1−f)²R_T^v]/T`, against the
current-correlator `K`.

## Limits

`k ξ ≤ 0.13` at L = 192 for the shells used; classical field, one cutoff, `mg = 1`; the L = 192 states may still
not be fully equilibrated (that is the question of `PGPE_ONSAGER_RESULTS.md`'s registered prediction, evaluated
on the same runs) — the relation tested here is kinematic and should hold in or out of equilibrium, which is
itself part of the claim.


## Gate D-G1, first run: FAIL as written — and amendment D-A1 (2026-10-05, before the primary data exist)

Result (`data/generated/pgpe/dielectric/DG1.json`, 20 configurations of 12 pairs at T = 0, L = 64):

| | shells `|m|² ≤ 2`: `n_eff` | coherence γ² | `Im n_eff` |
|---|---|---|---|
| right after the imprint (20 configurations) | **0.90–0.91** | 0.98–0.99 | ≤ 0.011 |
| after 20 time units (3 configurations) | 0.96 | 0.996–0.999 | ≤ 0.04 |

The coherence criterion passes at both times and on every shell up to `|m|² = 16` (γ² ≥ 0.977): at T = 0 the
transverse current **is** the point-vortex term, mode by mode, with the sign convention of the method section.
The amplitude criterion (`n_eff = 1 ± 0.05`) **fails right after the imprint** and holds after 20 time units.
The gate as written required both. It is recorded as failed.

Cause, checked on the imprint itself: `round2.imprint` multiplies the field by `[r²/(r² + 2)]^{1/2}` per vortex.
That factor has a `1/r²` tail, so 24 vortices remove ≈ 23 % of the density of a 64² box before the uniform
renormalisation restores the norm: the field right after the imprint is a large correlated density disturbance,
not a point-vortex state. It relaxes by radiating sound; the amplitude relation is restored as it does.

**Amendment D-A1.** The "right after the imprint" clause is dropped — it tested the imprint, not the relation.
Replacement gate **D-G1′**, on new configurations not yet generated: six configurations of 12 pairs at T = 0
evolved for 60 time units; pass if `n_eff = 1 ± 0.05` and `γ² ≥ 0.95` on the shells `|m|² ≤ 2`. The values already
seen at 20 time units (0.96) make a pass likely; that is stated. D-G2 is changed in the same way (pairs imprinted
into the T = 0.115 state, evolved 60 time units, six configurations), with the same thresholds as before.
The core form factor used for the primary analysis is the D-G1′ `n_eff(k)`.
Nothing else in the pre-registration changes; the primary snapshots still do not exist.
