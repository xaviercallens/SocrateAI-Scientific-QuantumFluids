# M1 Interim Report: Dispersion-Relation Reproduction (Tier C pass)

**Status:** Partial — roton branch validated, phonon branch not yet reproduced  
**Data source:** Digitized Fig. 5 (Godfrin & Krotscheck 2022, [LIT-001]) — Tier C, fallback pathway  
**Date:** 2026-08-14

---

## Summary

While M1-DATA-001 (raw ILL data access) is pending author response
(see M1_DATA_ACCESS_STRATEGY.md), this report runs the full M1 pipeline
against a Tier-C fallback: points visually traced from Fig. 5 of the
Godfrin & Krotscheck (2022) review, which the figure caption identifies
as representing the Godfrin et al. (2021) high-precision dataset ([LIT-002]).

**Result: partial success, cleanly separated by branch.**

| Parameter | Fitted | Literature (Godfrin 2021) | % diff | Tolerance | Pass? |
|---|---|---|---|---|---|
| Δ (roton gap) | 0.7306 ± 0.0040 meV | 0.7445 meV | 1.9% | ±10% | ✅ PASS |
| Q_m (roton momentum) | 1.9192 ± 0.0044 Å⁻¹ | 1.925 Å⁻¹ | 0.3% | (informal) | ✅ PASS |
| c (sound velocity) | 1.15 meV·Å | 1.568 meV·Å | 26.7% | ±5% | ❌ FAIL |

μ/m(⁴He) (roton effective mass) = 0.400, in the physically reasonable range.

## Figure

![Dispersion fit](data/derived/fig5_digitized_fit.png)

*Top: digitized points (blue), phonon linear fit (orange, Q < 0.3 Å⁻¹), roton
parabolic fit (green, |Q − 1.9| < 0.5 Å⁻¹). Bottom: residuals.*

Full numeric results: `data/derived/godfrin_2021_fit_results.json`

---

## Why the roton fit succeeds and the phonon fit does not

The roton-branch fit is well-constrained: it uses 10 points spanning a
visible, unambiguous minimum, and small vertical reading errors barely
shift the fitted minimum location or depth. Both Δ and Q_m land within
2% of the literature values Godfrin et al. themselves report — a solid
validation of both the fitting code (`landau_model.fit_roton_branch`)
and the digitization approach for well-defined curve features.

The phonon-branch fit is not: the sound velocity c is the *asymptotic
tangent slope as Q → 0*, and at the scale of the printed figure the
curve's height at Q < 0.3 Å⁻¹ is a small fraction of the plot's total
vertical range (comparable to my own reading uncertainty). A visual
trace of "looks like a straight line to the origin" systematically
underestimates the true tangent slope whenever the actual curve already
has non-negligible upward curvature by the smallest Q I could read
confidently (here, ≈0.1 Å⁻¹) — which physically it does, since the curve
must bend continuously toward the maxon peak at Q ≈ 1.1 Å⁻¹.

This was checked, not assumed: scanning `phonon_q_max` from 0.2 to 0.6 Å⁻¹
gives c between 1.10 and 1.15 meV·Å throughout — a stable but *wrong*
plateau, not a region-selection artifact that would resolve with a
narrower window. See `M1_CHECKLIST.md` Phase 1.3 / `M1_DATA_ACCESS_STRATEGY.md`
for the fallback-data caveats this was expected to surface.

**No compensating adjustment was made to the digitized points or the fit
region to force agreement.** The point of this pass was to test the
pipeline honestly against real published data at real precision limits,
and the phonon-branch result is filed as a genuine negative finding, not
smoothed over.

---

## Filed claims

Per LEDGER.md governance (Tier C claims are narrative-adjacent, not
peer-review-grade, but the underlying fit code is the same Tier-B-eligible
machinery that will run against Tier-B data once M1-DATA-001 resolves):

- **[CLAIM-001]** [TIER-C] — "The roton-branch fit recovers Δ and Q_m
  from a hand-digitized version of Godfrin et al. 2021's own published
  curve within 2%." — Source: this report, `data/derived/godfrin_2021_fit_results.json`
- **[CLAIM-002]** [TIER-C] — "The phonon-branch fit does NOT recover c
  from this same digitization; the gap (~27%) is stable against region
  width and attributable to near-origin visual reading precision, not
  a code defect." — Source: this report

See LEDGER.md for the full entries.

---

## Bugs found and fixed during this pass

Running the pipeline against real (well, real-figure-derived) data caught
three defects that synthetic round-trip tests alone did not surface,
because the synthetic tests generated data using the same (buggy)
constants they were checked against:

1. **`REFERENCE_VALUES` unit error** (`fit_dispersion.py`): roton-gap
   literature values were entered in Kelvin (8.65, 8.63, 8.64) but
   labeled and used as `delta_meV` directly — overstating Δ by the
   factor k_B ≈ 11.6×. Fixed: values now stored as `delta_K` and
   explicitly converted (`_K_B_MEV_PER_K = 0.08617333262`).
2. **Roton effective-mass constant off by 2×** (`landau_model.py`):
   `HBAR2_OVER_2M_HE4` was 1.0454 meV·Å²; the correct value (verified
   against the standard neutron-mass reference constant, scaled by the
   He-4/neutron mass ratio) is 0.52218 meV·Å².
3. **Plotting size-mismatch on non-default region widths**
   (`plotting.py`): `plot_dispersion_fit` recomputed the phonon/roton
   Q-masks using hardcoded thresholds (0.4, 0.5) instead of the
   `phonon_q_max` / `roton_q_center` / `roton_half_width` actually used
   for the fit, so any non-default call crashed with a scatter()
   size mismatch. Fixed by threading the region parameters through;
   regression test added (`tests/test_plotting.py`).

All three are now covered by tests using physically realistic values
(`tests/test_dispersion_fit.py` TRUE_C/TRUE_DELTA), not just
internally-self-consistent ones — see LL.md for the lesson recorded from
this.

---

## Next steps

1. **Does not block M1-DATA-001 outreach** (in progress — see
   M1_DATA_ACCESS_STRATEGY.md). Once raw or pre-reduced instrument data
   is available, rerun `run_dispersion_fit` against it — the phonon-branch
   limitation identified here is specific to hand-digitized figure data,
   not the fitting code itself (which the roton-branch result validates).
2. If a second attempt at the digitized fallback is wanted before then:
   read the low-Q phonon region at finer Q spacing (e.g. every 0.02 Å⁻¹
   instead of 0.1) directly from a zoomed crop of Fig. 5, since the
   current limitation is reading resolution, not methodology.
3. Phase 4 (full literature comparison table incl. Cowley–Woods 1971,
   Glyde 1998) deferred until c is recoverable from *some* dataset within
   tolerance.
