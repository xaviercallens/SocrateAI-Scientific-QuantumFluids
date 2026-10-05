# Pre-registration: thermal mutual friction α(T) of a single vortex dipole in the microcanonical 2D PGPE

Filed 2026-10-05. The known-answer (KA) runs below were launched as pilots of the tracker a few hours before this
file. **Disclosure (corrected in the same day, before any further KA result):** one KA run had already ended when
this file was first committed (c9cc4c1) and its output was seen: `d₀ = 12`, placement 1, track lost at `t = 92`
(a thermal pair appeared and the 3-unit tracking radius dropped the track), fitted slope of the wrong sign
(α = −0.06, `d` drifting 10 → 12 under imprint sound). It is excluded from the gate as a tracking failure of the
first protocol, and rerun with tracking radius 8 (`_r8`), which counts. The other three KA runs had not finished.
Production runs do not exist yet.

## Why (literature gate, done first)

- Shukla, Brachet & Pandit, arXiv:1412.0706 (2014): α(T), α′(T) from a single dipole in the 2D Galerkin-truncated
  GPE — our model class (microcanonical, no phenomenological damping). They reached **T/T̃_BKT ≤ 0.18** with a
  rough T̃_BKT, one grid (128²), 10 realisations, no error bars on α′. Their dipole values:
  α = (1.6 ± 0.5)×10⁻³ at T/T̃_BKT = 0.032, (4 ± 1)×10⁻³ at 0.064, (1.2 ± 0.6)×10⁻² at 0.12.
- Experiments sit at 0.3–0.8 T_c: Moon et al. PRA 2015 (arXiv:1509.02236) α ≈ 0.01–0.03; Kwon et al. Nature 600,
  64 (2021) unitary α ≈ 0.006 at 0.3 T_c; Grani et al. Nat. Commun. 16, 10245 (2025) α = 0.018–0.082 at
  0.37–0.65 T_c (fermionic). Holography (Wittmer et al. PRL 2021): 0.03–0.1. Mehdi, Hope, Szigeti & Bradley,
  arXiv:2205.04065 (2022): SPGPE energy-damping theory, and an open call to measure vortex diffusion η and test
  η = α k_B T/(2πħρ₀).
- **The gap:** no first-principles microcanonical classical-field α(T) above 0.18 T_BKT, and no η test.
  Our assets: a calibrated temperature and `T_BKT(L = 64) = 0.821` (round 2), thermal bases spanning
  T = 0.115–0.97 at L = 64.

## Method (fixed)

`exploration/pgpe/dipole_decay.py`: imprint one dipole (separation `d₀`, axis along x, random centre) into a saved
thermal state; detect vortices on the field coarse-grained by a Gaussian of width `σ = 1.5` (removes core-scale
thermal defects; validated in pilots: 2–4 detections instead of 8–76); track by nearest same-sign detection;
`dt_sample = 2`; stop at `d < 2` (merger) or `t_max`. Point-vortex dissipative dynamics with `ħ = m = 1`,
`Γ = 2π`: `d² = d₀² − 4αt`, so **α = −(slope of d² vs t)/4**, fitted over samples with `d > 3`.
Temperature: the base run's block-averaged thermometer reading (the imprint adds energy `≲ 2π ln(d₀/ξ) ≈ 15`
against a bath of ≈ 10⁴ modes × T; its heating is reported, not corrected).

## Gate KA (known answer) — decides whether production runs happen

Base `sweep/e0.60_s11_t4000` (T = 0.115, `n_s/n = 0.97`, no thermal vortices ⇒ `T/T_BKT ≈ 0.14`), `d₀ ∈ {8, 12}`,
2 placements each (+ one rerun with a wider tracking radius after a pilot lost its track — all reported).
Interpolating Shukla et al. at 0.14 gives α ≈ 0.012–0.015; with their factor-2 error bars and the uncertainty of
mapping their T̃_BKT onto ours, **KA passes if the median α over the completed KA runs lies in [0.004, 0.045]**
(a factor 3 around 0.013). It **fails** if outside, or if fewer than 3 runs give a fit (`≥ 10` samples with
`d > 3`). If KA fails, the tracker/protocol is not a measurement of α and the production study is not run as
designed; the failure is reported.

## Production design (run only if KA passes)

- Temperatures: bases `e0.60` (0.115), `e0.90_s11/_s12` (≈ 0.40–0.44), ladder `II_*_e1.00/1.10/1.20` (0.57–0.78)
  → `T/T_BKT ≈ 0.14, 0.5, 0.7, 0.8, 0.95`. `d₀ ∈ {8, 12, 16}`; 4 placements per (T, d₀).
- **F1 (d² law):** at each T, the fitted lifetimes scale as `d₀²`: the log–log slope of mean lifetime vs `d₀`
  lies in [1.5, 2.5].
- **F2 (monotone α(T)):** α increases with T across the five temperatures (Spearman ρ ≥ 0.9).
- **F3 (continuity with Shukla et al.):** the lowest-T point equals the KA value (same runs).
- **Report only (no prediction):** α at `T/T_BKT ≈ 0.5–0.8` against Moon 2015 / Kwon 2021 / holography;
  centre-of-mass mean-square displacement of the dipole and the ratio `η/(αT/2πρ₀)` (Mehdi et al.'s test);
  vortex count of thermal pairs near the dipole.
- **Stated limits:** classical-field α depends on the cutoff through the thermal-mode population (one cutoff
  here, `k_cut = k_max/2`); 2D only; imprint transients (sound) are part of the measured dynamics; above
  ≈ 0.8 T_BKT, thermal pairs can swap with the tracked vortices (jumps > 3 are counted and reported).


## Amendment A1 (2026-10-05, after the KA gate — `PGPE_FRICTION_RESULTS.md`, CLAIM-075 — and the literature review; before any production run)

This amendment replaces the "Method" and "Production design" sections above. It also defines the shared
simulation campaign used by `PGPE_ALPHAPRIME_PREREG.md` (H03) and `PGPE_EINSTEIN_PREREG.md` (H02).
Lean companion: `lean_src/DissipativeVortexDynamics.lean` (kernel-checked, standard axioms).

### What was looked at before writing this (disclosure)

1. **Detection bias of the first tracker.** A 40-time-unit control at T = 0 (uniform condensate, one dipole,
   `d₀ = 8, 12`), run to choose the detector: with raw phase-winding detection the separation stays constant
   (7.5 and 11.5 on the half-integer grid) — no shrinking at T = 0, as Lucas & Surówka (2014) predict; with the
   Gaussian coarse-graining used for the KA gate (σ = 1.5) the detected separation is **biased low by ≈ 1 and the
   bias changes in time** (σ = 3: by 4, with a spurious shrink 10.5 → 7.5 in 40 units). The KA numbers of
   CLAIM-075 therefore carry a detector bias (they underestimate α by roughly the ratio `d_true/d_meas ≈ 1.2`;
   the gate verdict is not affected in direction), and the pilot value α ≈ 0.3–0.4 at T ≈ 0.45 (σ = 1.5 and 3) is
   not a measurement.
2. **An independent α already on disk.** The round-3 Part A vortex arm at T = 0.115 (eight imprinted vortices,
   zero net dipole moment, raw detection, 150 samples over 1500 time units): the torus point-vortex energy falls
   linearly, and the energy estimator below gives **α = 0.0056**.
3. **A stall.** One KA run (`d₀ = 12`, placement 2) shrinks from 10.1 to ≈ 7 (detected) in 2000 time units and
   then stays at 6.7–7.4 for the next 2000. The `d₀ = 8` runs do not stall.

### Hypothesis W (phonon wind of a closed box) — the proposed reading of (3) and of the size dependence

A pair of separation `d` carries the impulse `2πρ_s d`. In a closed periodic box that momentum has nowhere to go
but the phonons: as the pair shrinks from `d₀` to `d`, the normal component acquires the drift
`u = 2πρ_s (d₀ − d)/(ρ_n L²)` along the pair's motion, and the friction, which acts on the *relative* velocity,
drives the separation as `d' = −2α(1/d − u)`. When `π ρ_s d₀² > 2 ρ_n L²` the right-hand side vanishes at
`b = [d₀ + (d₀² − 2ρ_nL²/(πρ_s))^{1/2}]/2` and the pair stalls there for ever (`wind_stall`, machine-checked).
At T = 0.115, L = 64 (`ρ_n/ρ = 0.027`): `ρ_nL²/(2πρ_s) = 18.1`, so `d₀ = 12` stalls (`d₀²/4 = 36`) and
`d₀ = 8` does not (16) — as observed. Quantitatively the observed plateau (≈ 8–8.5 after bias correction) is below
the predicted 10.2: the model is not confirmed at that level, and W is registered as a hypothesis, not a result.
If W holds, every closed-box friction measurement on a single pair at low temperature is contaminated unless
`ρ_n L² ≫ π ρ_s d₀²/2` — including, possibly, part of the literature's.

### Instrument (v2)

`exploration/pgpe/vortex_transport.py`: **raw** phase-winding detection (no coarse-graining) with **sub-grid
refinement** (zero of the least-squares plane through the four corner values of ψ on the winding plaquette);
tracking of the imprinted vortices by continuity (same sign, displacement ≤ 1.5 per sample, `dt_sample = 1`);
all tracked positions saved, with the number of detected vortices, the total field momentum and the momentum in
the band `|k| > 1`. Detector bias is measured, not assumed: gate G1.

Estimators (`exploration/pgpe/transport_estimators.py`), all from the saved positions `r_i(t)`, charges `q_i` and
the torus point-vortex velocities `v_s,i` (Weiss–McWilliams Green function, hbar = m = 1, circulation 2π):
- **two-coefficient regression** (primary for α′, secondary for α): displacements over a lag regressed on the two
  orthogonal predictors, `Δr_i = (1 − α′) ∫v_s,i dt − α q_i ∫ẑ×v_s,i dt + noise`;
- **energy estimator** (primary for α): `α = −ΔH / (2 ∫Σ_i |v_s,i|² dt)`, `H` the torus point-vortex energy of
  the tracked vortices — valid for any configuration and independent of α′ (`energy_dissipation`);
- **diffusion**: mean-square of the regression residuals against lag (see the Einstein pre-registration).
A settling time of 100 time units after the imprint is excluded from every fit (imprint radiation: Rorai,
Sreenivasan & Fisher 2013).

### Geometry

**Zero net impulse** is the default: two antiparallel dipoles (`+−` at `x = L/4`, `−+` at `x = 3L/4`, same `d₀`),
so that the momenta they shed cancel and no wind builds up. Single-dipole runs are kept only to test W.

### Gates (run in this order; production runs do not start until all three pass)

- **G0, synthetic.** Langevin integration of the dissipative point-vortex model on the L = 64 torus, antiparallel
  geometry `d₀ = 10`, with known `(α, α′, η) = (0.02, 0.10, 2×10⁻³)`, detection noise 0.2 per coordinate, 8 runs
  of 2000 time units. Pass: α recovered within 15 %, `1 − α′` within 0.02, η within 25 %.
- **G1, T = 0 control** (uniform condensate, antiparallel `d₀ = 10`, 400 time units, fit on 100–400), known
  answers: (i) no friction, `|α̂| ≤ 10⁻³`; (ii) point-vortex translation, `1 − α̂′ ∈ [0.96, 1.04]`; (iii) no
  diffusion, apparent `η̂ ≤ 2×10⁻⁵`; (iv) momentum bookkeeping on a single dipole: field momentum equal to
  `2π n d` within 5 % and constant. If only (iii) fails, the campaign proceeds with the measured floor `η_floor`
  and the Einstein test is restricted to temperatures where the Einstein value exceeds `5 η_floor`.
- **G2, thermal known answer** (T = 0.115, antiparallel `d₀ = 10`, 2 runs × 2000 time units): `α̂` (energy
  estimator) within a factor 2 of the independent value 0.0056 of disclosure (2), i.e. in **[0.0028, 0.0112]**,
  which lies inside the Shukla–Brachet–Pandit window of the original gate.

### Bases and production

Temperatures: `e = 0.60` (T = 0.115, on disk), `e = 0.70` and `0.80` (made from the `e = 0.60` state by the
phonon-heating construction of round 2 and 1000 time units of equilibration; their T, `n_s/n` and raw vortex count
are measured before use), and `e = 0.90, s12` (T = 0.458) as a **report-only** point because thermal pairs are
present. A base enters the pre-registered tests only if its mean raw vortex count is below 0.5.
Per temperature: antiparallel geometry, `d₀ ∈ {8, 12}`, 3 runs each of 2000 time units (two pairs per run).

Criteria (replace F1–F3):
- **F1′ (no intrinsic size dependence).** In the zero-impulse geometry the energy-estimator α at `d₀ = 8` and
  `d₀ = 12` agree within 30 % at each temperature (≥ 2 of the 3 tested). A ratio outside [0.7, 1.43] at ≥ 2
  temperatures is recorded as a real size dependence of the friction.
- **F2 (monotone).** α increases with T over the tested bases.
- **F3 (cross-estimator).** Energy and regression estimates of α agree within 25 % at each temperature.
- **W1 (stall).** Single dipole, `d₀ = 12`, T = 0.115, L = 64, 4000 time units, 2 runs: the slope of `d²` over
  `t ∈ [2000, 4000]` is below 25 % of its value over `t ∈ [100, 600]` in both.
- **W2 (no stall in the larger box).** Same pair at L = 96 (`ρ_nL²/(2πρ_s) = 40.7 > d₀²/4`): no stall — the late
  slope is at least 50 % of the early one, or the pair annihilates.
- **W3 (the wind seen directly).** In the W1 runs the momentum of the modes with `|k| > 1`, projected on the
  initial impulse direction, grows with the impulse lost by the pair, with regression slope in [0.5, 1.2].
- W is **refuted** if W1 holds and W2 fails (a stall that does not depend on the box), or if W3's slope is
  below 0.2; it is **supported** if W1, W2 and W3 hold. Anything else is reported as unresolved.

Report only: α(T) against Shukla et al. (2014), Moon et al. (2015) and Kwon et al. (2021); the L = 96 value of α.
Stated limits as before (one cutoff, two dimensions, classical field); in addition, the torus motion law is used
throughout (Zhu 2023), and the plane `d²` law only in the Lean companion and as the small-`d/L` limit.
