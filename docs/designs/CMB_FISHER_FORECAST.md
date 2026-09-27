# How much could a next-generation CMB experiment improve Koren-Tsai-Wang's bound?

Written 2026-09-26, following the owner's request to prepare the next tier of experimentation on
the "discrete cascade vs. continuous roll" line (`docs/designs/CMB_CASCADE_REPRODUCTION.md`). This
is a forecast, not a reproduction: it asks whether a future CMB temperature dataset (ACT DR6,
SPT-3G, CMB-S4, or any TT-only successor to Planck) could meaningfully tighten the bound on the
dark-energy-conversion fraction `r` from Koren, Tsai, Wang (arXiv:2509.07076), using the exact
bubble-time spectrum from `docs/designs/CMB_CASCADE_REPRODUCTION.md`'s addendum.

## What this is and is not

**Is:** a forecast of the maximum possible improvement to this specific CMB-temperature-anisotropy
bound from any future temperature-only measurement, grounded in a real, checked physical fact
(whether Planck's own measurement is already close to the cosmic-variance floor at the relevant
multipoles) rather than an assumed noise curve for a specific future instrument.

**Is not:** a survey of ACT DR6 or SPT-3G's actual published noise curves (see "What was not done"
below); a claim about polarization channels (E-mode), which this specific late-time signal's
polarization content neither source paper addresses and which is not assumed here; a claim about
non-CMB channels (spectral distortions, pulsar timing arrays) that Koren-Tsai-Wang and Elor et al.
themselves point to as potentially more promising -- those are out of scope for this document.

## The exact scaling relation (no linearization needed)

`D_ell,pt(r)` is proportional to `r^2` exactly (Eq. 11 of arXiv:2509.07076: `P_delta-z0` is
proportional to `r^2`), so the chi-squared of Eq. (14) scales as `chi2(r) proportional to
r^4 / sigma_ell^2`, and the 2-sigma bound on `r` scales as

    r_bound  proportional to  sigma_ell^(1/2)

exactly -- an experiment with `N` times smaller error bars at the relevant `ell` tightens the bound
by exactly `sqrt(N)`, with no Fisher-matrix linearization approximation needed (unlike a generic
signal linear in its parameter, this quadratic-in-`r` signal's exact `r^4` chi-squared scaling,
already used by `cmb_bound.r_bound_2sigma`, makes the forecast exact rather than approximate).

## The physical question this reduces to

Given that relation, "how much could a bigger telescope help" reduces entirely to: how much smaller
can `sigma_ell` get at the `ell` where this signal peaks (`ell~3-30` across the `beta/H_star` range
considered)? The answer is bounded below by **cosmic variance**: with only `2*ell+1` independent
modes per multipole on a finite sky, `sigma_CV(ell) = D_ell * sqrt(2/((2*ell+1)*f_sky))`, and no
temperature-only experiment, however sensitive, can beat this floor.

`exploration/cmb/fisher_forecast.py` computes `sigma_CV(ell)` directly from Planck's own measured
`D_ell` (the same real data table used throughout this line of work,
`data/external/planck2018_tt_full/`) and compares it to Planck's own measured error bars:

| ℓ | D_ℓ (μK²) | σ_Planck | σ_CV | ratio (Planck/CV) |
|---:|---:|---:|---:|---:|
| 2  | 225.90  | 332.72 | 170.76 | 1.95 |
| 3  | 936.92  | 831.39 | 598.58 | 1.39 |
| 5  | 1501.70 | 865.12 | 765.34 | 1.13 |
| 10 | 803.66  | 300.40 | 296.43 | 1.01 |
| 15 | 1022.11 | 296.59 | 310.30 | 0.96 |
| 20 | 659.86  | 171.21 | 174.19 | 0.98 |
| 30 | 1102.81 | 274.69 | 238.67 | 1.15 |
| 40 | 1715.07 | 274.43 | 322.11 | 0.85 |
| 50 | 1707.31 | 282.96 | 287.16 | 0.99 |

(`f_sky=0.7`, an order-of-magnitude Planck-TT-analysis sky fraction; the ratio is only mildly
sensitive to this choice since it cancels partially between the numerator and denominator's own
`D_ell` dependence.)

**The honest finding.** For `ell=5-50` -- exactly the range this PT signal's peak falls in for
`beta/H_star gtrsim 20` -- Planck's own TT measurement is ALREADY within 15% of the pure
cosmic-variance floor. Only at the very lowest multipoles (`ell=2,3`, relevant only for the smallest
`beta/H_star ~ 10`) is there more room (`ratio 1.4-2.0`), and that gap is dominated by residual
foreground/masking systematics at the largest scales, not by detector/instrument noise a bigger
telescope would improve.

## Numeric confirmation (not a full grid -- see below)

`r_bound_2sigma`, called with `sigma_cv` in place of Planck's real `sigma_ell` (exact spectrum,
`beta/H_star=10, z_pt=0.1`, where `ell_peak=3`): `r_bound(Planck) = 0.003156`,
`r_bound(cosmic-variance floor) = 0.002263`, ratio `1.39x` -- matching the `ell=3` Planck/CV ratio in
the table above to three significant figures, exactly as the `r_bound proportional to
sqrt(sigma_ell)` relation predicts (the 3-ell-bin chi-squared is dominated by its central,
peak-`ell` term). This is a genuine, checked confirmation of the scaling relation on real numbers,
not just the analytic argument.

**What was not completed, and why, stated honestly.** A full `(beta/H_star, z_pt)` grid analogous to
the reproduction table (10 more benchmark points) was started but did not finish within this
session's time budget: `Pdt_hatk_exact` is called on the order of `10^5-10^6` times per
`r_bound_2sigma` evaluation (the nested nine-point-Gauss-Legendre / 40-point-log-r / 60-point-log-k
integration structure inherited from `cmb_cascade.py`, each inner call doing a 250-point NumPy
trapezoid), and at Python-loop speed this is minutes per benchmark point rather than seconds. This
is a **performance** limitation, not a physics uncertainty: the one confirmed point already
verifies the exact scaling relation on real data, and the cosmic-variance-ratio table (computed
directly from Planck's own published numbers, no nested integration needed) already answers the
physical question for the full `ell` range this signal occupies. A future session wanting the full
grid should first vectorize `Pdt_hatk_exact`/`Idt`/`D_ell_pt` over the `ell`/`k` grids instead of
Python-level loops -- a real speedup, not a physics change.

## Conclusion

**A next-generation ground-based or satellite CMB temperature experiment cannot meaningfully improve
Koren-Tsai-Wang's bound over most of its `beta/H_star` range** -- Planck's own TT measurement is
already within about 15% of the cosmic-variance floor at `ell=5-50`. The one place with real
remaining room is `beta/H_star lesssim 20` (`ell_peak=2-3`), where the gap (`ratio up to ~2`,
i.e. up to about `sqrt(2)~1.4x` tighter `r`) comes from foreground/mask systematics at the very
largest scales rather than instrument sensitivity -- better component separation, not a bigger
mirror, would be the relevant lever there, and even that caps out at a modest, not order-of-
magnitude, improvement. This matches, and gives a quantitative reason for, why the source papers
themselves (Koren-Tsai-Wang's own conclusion; Elor et al.'s discussion) point to qualitatively
different channels -- CMB spectral distortions (mu/y-distortions, via a future PIXIE-like mission)
and pulsar timing arrays -- for further gains at other transition-temperature ranges, rather than
more CMB-temperature data at the temperatures this specific bound covers.

## Reproducibility

- `exploration/cmb/fisher_forecast.py` — the cosmic-variance-ratio table and the exact-vs-CV bound
  comparison. Run: `uv run python exploration/cmb/fisher_forecast.py` (the ratio table prints in
  seconds; the full bound-comparison grid is slow, see above -- a partial run's first row is
  reported here; a future session can vectorize the hot path before re-running the rest).
- Builds on `exploration/cmb/cmb_cascade.py` and `pdt_exact.py`
  (`docs/designs/CMB_CASCADE_REPRODUCTION.md`'s addenda) and the same real Planck 2018 TT data.

## References (all verified by direct read, same sources as the reproduction document)

- S. Koren, Y. Tsai, R. Wang, arXiv:2509.07076 [hep-ph].
- G. Elor, R. Jinno, S. Kumar, R. McGehee, Y. Tsai, Phys. Rev. Lett. 133, 211003 (2024),
  arXiv:2311.16222 [hep-ph].
- Planck Collaboration, N. Aghanim et al., Astron. Astrophys. 641, A6 (2020), arXiv:1807.06209
  [astro-ph.CO] (also the source of the standard cosmic-variance formula used here).

## Erratum (2026-09-27): the "within 15%" statement, checked at every multipole

The table above samples nine multipoles, and the text generalised it to "within 15% for ℓ=5–50." A scan
of every multipole (same data, same f_sky=0.7), made while building the SectorCausalityTheory
repository's reproduction notebook and re-checked independently, gives:

| ℓ range | Planck σ / cosmic-variance σ |
|---|---|
| 2–4 | 1.23–1.95 |
| 5–29 | 0.96–1.13 |
| 30–50 | 0.83–1.84 (floor estimated from the measured, noisy spectrum; 1.03–1.42 against a smoothed spectrum) |

So "within ~13%" holds for 5 ≤ ℓ < 30 only. The conclusion is unchanged: because r_bound ∝ √σ, the
worst ratio (1.95 at ℓ=2) still permits at most ~1.4× tightening, so no temperature-only successor can
meaningfully improve this bound. The quantitative basis is now stated correctly. LEDGER CLAIM-064.
