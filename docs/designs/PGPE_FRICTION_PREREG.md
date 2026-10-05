# Pre-registration: thermal mutual friction α(T) of a single vortex dipole in the microcanonical 2D PGPE

Filed 2026-10-05. The known-answer (KA) runs below were launched as pilots of the tracker a few hours before this
file; **none of them has finished and no KA number has been read** at the time of filing. Production runs do not
exist yet.

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
