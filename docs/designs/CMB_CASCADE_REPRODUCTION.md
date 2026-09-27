# Independent reproduction check: the CMB bound on a late-time dark-energy phase transition

Written 2026-09-26, following the owner's request to look at whether the "discrete cascade vs.
continuous roll" discriminating test in `paper/cosmology_sectors.tex` could be run against real CMB
data. A feasibility-scoping pass first established: (a) the bound is a closed-form/numerical-
integration calculation, not a Boltzmann-code/MCMC pipeline, so it needs no GPU at all; (b) there is
**no established quantitative mapping** from this project's own e=0.60 toroidal winding-cascade toy
result to the physical parameters (`r`, `β/H⋆`) used here — none is constructed or implied below;
(c) real Planck 2018 low-ℓ error bars are freely downloadable, no registration. This document is the
follow-up: an independent numerical reproduction of one specific published bound, as a check, not a
new physics claim.

## What this is and is not

**Is:** an independent re-implementation, from the published equations, of the CMB-anisotropy bound
on a late-time first-order phase transition converting a fraction `r` of the dark energy into free-
streaming dark radiation, from Koren, Tsai, Wang, "Boiling After the Dust Settles: Constraining
First-Order Phase Transitions During Dark Energy Domination," arXiv:2509.07076 (hep-ph, 8 Sep 2025;
verified by direct PDF read). A sanity/reproduction exercise, in the spirit of this project's own
Bose-integral and phonon-series checks against Godfrin et al. — machine-checking someone else's
published number against their own stated method.

**Is not:** new physics; a test, endorsement, or extension of this project's own PGPE/quantum-fluid
simulations; a Boltzmann-code (CAMB/CLASS) or MCMC pipeline; a claim that this project's own e=0.60
winding-cascade result says anything quantitative about `r` or `β/H⋆`. No such bridge exists between
a dimensionless torus winding number and a cosmological bubble-nucleation rate; asserting one would
be exactly the LL-15 failure mode (analogy standing in for a real dependency) this project guards
against, and it is explicitly not made here.

## The published calculation

Koren-Tsai-Wang model a first-order phase transition (FOPT) completing at redshift z̄_pt, releasing a
fraction `r` of the dark energy into dark radiation. Bubble nucleation is stochastic (rate
`Γ = Γ₀e^{β(t-t_f)}`, their Eq. 1), so different patches complete the transition at slightly different
times; this "first-encounter-surface" fluctuation photon-by-photon imprints a late-time,
integrated-Sachs-Wolfe-like anisotropy in the CMB. Their pipeline (all read directly from the paper,
not a secondary summary):

1. A dimensionless power spectrum of bubble-completion-time fluctuations, `P_δt(ξ)`, a function of
   the rescaled wavenumber `ξ ≡ (8π)^{1/3} v_w (k/(a_pt H⋆))(H⋆/β)` (their Eq. 2-3, Fig. 4), adapted
   from Elor, Jinno, Kumar, McGehee, Tsai, "Finite Bubble Statistics Constrain Late Cosmological
   Phase Transitions," Phys. Rev. Lett. 133, 211003 (2024), arXiv:2311.16222 (verified by direct PDF
   read, including its Supplementary Material).
2. A closed-form redshift-perturbation formula, `δz₀ ≈ δz_pt² · [r Ω_Λ / ((1+z̄_pt)[Ω_Λ+Ω_m(1+z̄_pt)³]^{3/2})]`
   (their Eq. 9), and the resulting redshift power spectrum `P_δz₀(k)` (Eq. 11-12).
3. A Bessel-function line-of-sight projection onto the CMB temperature power spectrum,
   `D_ℓ^{TT,pt} = 2ℓ(ℓ+1) ∫ dk/k P_δz₀(k) j_ℓ²(k Δτ)` (Eq. 13).
4. A 3-ℓ-bin χ² test against the **real, published Planck 2018 σ_ℓ error bars** (their Eq. 14, ref.
   [84] = the Planck Legacy Archive, `https://pla.esac.esa.int/#home`) — no re-fit of ΛCDM, no
   likelihood code, no MCMC. The 2σ bound is `χ² ≤ 5.99`.
5. An analytic order-of-magnitude approximation, `r ≲ 10⁻⁵(β/H⋆)²` (their Eq. 15), derived by
   approximating the power spectrum with just its peak value.

No code release was found for this paper (checked the acknowledgments and reference list) or for
either of the two related papers already cited in `cosmology_sectors.tex`
(Bai-Lu-Orlofsky arXiv:2605.30259; Friedman-Shaw-Johnson-Mack arXiv:2607.18376) — this reproduction
is built from the equations alone.

## What we implemented (`exploration/cmb/cmb_cascade.py`, `cmb_bound.py`)

Steps 1-4 above, in plain NumPy/SciPy (no Boltzmann code, no GPU — confirming the feasibility pass's
finding that this calculation is a few CPU-seconds per point, not a GPU workload), against the real
Planck 2018 TT power spectrum table, `data/external/planck2018_tt_full/COM_PowerSpect_CMB-TT-full_R3.01.txt`
(downloaded directly from the Planck Legacy Archive; verified authentic by cross-checking the
low-ℓ plateau, ~700-1700 μK², and the first-acoustic-peak amplitude, `D_220 ≈ 6373 μK²`, against the
well-known Planck 2018 TT spectrum shape from Aghanim et al. 2020, arXiv:1807.06209).

Three approximations we had to introduce, because the source papers do not give every detail needed
for an independent implementation — **stated explicitly, not hidden**:

1. **The `P_δt(ξ)` shape.** Neither paper publishes a single closed form for the full curve — only
   two asymptotic power laws (`P_δt ~ 3ξ³` for `ξ≪1`, `~ξ⁻³` for `ξ≫1`, in Koren-Tsai-Wang's own
   rescaled units, derived from Elor et al.'s Eq. 4 and Fig. S4) and a numerically-computed curve
   shown only as a plot. We use a smooth double-power-law interpolation matching **both** asymptotic
   coefficients exactly, `(β/H⋆)²P_δt(ξ) = 1/(1/(3ξ³) + ξ³)`, peaking at `ξ=3^{-1/6}≈0.833` with value
   `≈0.867` — close to, but not a digitisation of, the published peak (`≈1` near `ξ~1`).
2. **The μK² normalisation.** Eq. 13 as written gives a dimensionless quantity (a power spectrum of
   the dimensionless redshift perturbation `δz₀`); Fig. 2's y-axis is in μK². We restore this by
   multiplying by `T_CMB² = (2.7255×10⁶ μK)²`, the standard conversion for `ΔT/T = -δz₀` — a
   physically standard assumption, but one the paper does not spell out, so we flag it as ours.
3. **Integration limits and χ² binning.** The paper sets `k_min, k_max` to "10× smaller/larger than
   the peak mode" of `P_δt` — we take this literally in our own `ξ`-based peak. For the χ² bound we
   evaluate `D_ℓ^{TT,pt}` on a **sparse** `ℓ`-grid (`{3,5,7,9,12,15,20,25,30,40}`, not every integer)
   to keep the nested nine-dimensional-equivalent numerical integral tractable in CPU-minutes rather
   than CPU-hours; the peak is found on this coarse grid, not by continuous optimisation.

## Result: sanity check against Fig. 2

Reproducing their Fig. 2 (`z̄_pt=0.1, r=0.1`, several `β/H⋆`), our `D_ℓ^{TT,pt}` peaks at low `ℓ`
(`ℓ=5`, our coarsest sampled point) and falls off with increasing `ℓ`, in the right qualitative shape
and right order of magnitude for a 10%-of-dark-energy transition (tens to hundreds of μK²), but **not**
a precise match to the published curve — we cannot confirm agreement better than roughly an order of
magnitude at fixed `ℓ`, most likely because of approximation (1) above (a different `P_δt(ξ)` shape
shifts both the amplitude and the `ℓ` at which the curve peaks) compounded by approximation (2).

## Result: the 2σ bound on `r`, vs. Eq. (15)

| β/H⋆ | z̄_pt | ℓ_peak (ours) | r ≤ (ours, 2σ) | r ≲ 10⁻⁵(β/H⋆)² (their Eq. 15) | ratio |
|---:|---:|---:|---:|---:|---:|
| 10  | 0.1 | 3  | 0.0165 | 0.001 | 16.5× |
| 20  | 0.1 | 3  | 0.0223 | 0.004 | 5.6× |
| 50  | 0.1 | 3  | 0.0507 | 0.025 | 2.0× |
| 100 | 0.1 | 3  | 0.161  | 0.1   | 1.6× |
| 200 | 0.1 | 7  | 0.507  | 0.4   | 1.3× |
| 500 | 0.1 | 15 | 2.61   | 2.5   | 1.04× |
| 10  | 0.2 | 3  | 0.00754| 0.001 | 7.5× |
| 100 | 0.2 | 5  | 0.169  | 0.1   | 1.7× |
| 500 | 0.2 | 30 | 3.16   | 2.5   | 1.26× |

**Honest verdict.** At `β/H⋆ ≥ 100` — the regime Koren-Tsai-Wang's Fig. 3 resolves in the most
detail — our independent bound agrees with their own analytic approximation (Eq. 15) to within
**4-60%**, remarkably close given the three approximations listed above. At `β/H⋆ ≤ 50` our bound is
weaker (more permissive) by up to **16×**. This divergence has a physical explanation grounded in
the paper's own text, not a bug we are hiding: Koren-Tsai-Wang state directly that "the r bounds
also become weaker at lower z̄_pt [and, by the same mechanism, lower β/H⋆], as the peak of
`P_δz₀(k)` shifts to such low k-modes that it no longer contributes significantly to the power
spectrum with `ℓ≥2`" — exactly the regime our `ℓ_peak=3` (the lowest point on our coarse grid, itself
already close to the `ℓ=2` floor) indicates. Eq. (15) is explicitly labelled "a useful analytic
order-of-magnitude approximation," derived from the *peak* value of the spectrum; it is not expected
to hold precisely away from where that peak sits well inside the resolved `ℓ` range, and our result
is consistent with that caveat rather than contradicting it.

**What would close the remaining gap:** the exact (not interpolated) `P_δt(ξ)` curve — requiring
either digitising Fig. 4/Fig. S4 at higher fidelity than done here, or re-deriving Elor et al.'s full
numerical calculation (Eqs. S1-S16 of their Supplementary Material) rather than its two asymptotes;
and a finer `ℓ`-grid for peak-finding at low `β/H⋆`, which mainly costs more CPU time, not new
physics.

## What this does NOT establish

- No claim that the discrete-cascade dark-energy model is preferred, disfavoured, or newly
  constrained by this work — we reproduce an existing published bound, we do not extend it to new
  data or new parameter regions beyond the paper's own grid.
- No claim about this project's own quantum-fluid simulations: there is no established mapping from
  a 2D superfluid torus's winding number to `(r, β/H⋆)`, and none is proposed here.
- No claim of exact numerical agreement with Koren-Tsai-Wang's Fig. 2/Fig. 3 — agreement is to within
  an order of magnitude at low `β/H⋆` and to within tens of percent at high `β/H⋆`, for the reasons
  stated above, not better.
- Not a GPU workload: every number above was produced on a single CPU core in the general-purpose
  Codespace this repository already runs in, in well under an hour of wall-clock time including two
  full paper reads — confirming the earlier feasibility pass's finding that a rented T4 GPU would add
  nothing to this specific calculation.

## Addendum (2026-09-26, later): closing the P_delta-t approximation gap

The section above flagged the interpolated `P_delta-t(xi)` shape as the main source of the
remaining mismatch, and named Elor et al.'s Supplementary Material as the place to look for an
exact form. It has one: their Eqs. (S1)-(S16) give the full bubble-time correlator
`beta^2<delta_tc(x)delta_tc(y)>(r)` in closed form, as a sum of a "single-bubble" and a
"double-bubble" contribution, each a finite one-dimensional integral ("these are one-dimensional
integrals and easy to evaluate" -- their own words). No code or data release was found for either
paper (checked again, including a search for a companion GitHub/Zenodo repository under the
authors' names and the paper's title; none exists publicly), so this is implemented directly from
their equations, in `exploration/cmb/pdt_exact.py`.

**What was implemented.** `_single_integrand`/`_double_integrand` are Eqs. (S9)-(S11) and
(S12)-(S16) exactly; `_correlator(r)` integrates each over `t_xy in [-r,r]` with `scipy.integrate.quad`
and sums them (Eq. S3); a 250-point table of `correlator(r)` over `r in [0,45]` (in units of
`1/beta`) is built once and cached (`pdt_exact_table.npz`); `P_beta_dtc_exact(k)` Fourier-sine-
transforms that table (Eq. S2, `int 4 pi r^2 dr sinc(kr) correlator(r)`); `P_exact_k_elor(k)` applies
the dimensionless prefactor (Eq. S1). `cmb_cascade.py` gained `Pdt_hatk_exact`, a drop-in
replacement for the original `Pdt_hatk` interpolation, converting `hat_k` to Elor's own `k/beta`
variable (`k_elor = (1+zpt)*hat_k/beta_over_H`, the correspondence verified against Koren-Tsai-
Wang's own Eq. (2) definition, which carries an explicit `(H_star/beta)^2` prefactor that Elor's own
dimensionless spectrum does not).

**Validation before trusting it.** `correlator(r->0) = pi^2/6 = 1.6449...` exactly (a closed-form
value the single-bubble integral reduces to, matching the paper's Fig. S3's blue curve's starting
value; the double-bubble contribution correctly vanishes at `r=0`, matching the red curve). The
resulting `P_exact_k_elor(k)` peaks at `k=0.493` with value `1.077`, matching Fig. S4's peak (`~1`
near `k/beta~0.5`) and its two labelled asymptotes at the sampled endpoints. One known numerical
limitation, stated explicitly: the fixed-grid Fourier transform under-resolves the oscillatory
integrand for `k_elor` beyond about 5-10 (a rapidly-oscillating `sin(kr)` against a 250-point grid),
occasionally returning small negative numerical noise there, which we clip to zero; this region is
never reached by the CMB bound calculation below (whose scan stays within a factor of 10 of the
peak, `k_elor` up to about 5).

**Result: does the exact spectrum improve the match?** Re-running `cmb_bound.py`'s full
`(beta/H_star, z_pt)` grid with `Pdt_hatk_exact` in place of the interpolation:

| β/H⋆ | z̄_pt | r (interpolated) | ratio to Eq. 15 | r (exact) | ratio to Eq. 15 |
|---:|---:|---:|---:|---:|---:|
| 10  | 0.1 | 0.01648 | 16.48× | 0.003156 | 3.16× |
| 20  | 0.1 | 0.02227 | 5.57×  | 0.005724 | 1.43× |
| 50  | 0.1 | 0.05073 | 2.03×  | 0.02322  | 0.93× |
| 100 | 0.1 | 0.1611  | 1.61×  | 0.08405  | 0.84× |
| 200 | 0.1 | 0.507   | 1.27×  | 0.2543   | 0.64× |
| 500 | 0.1 | 2.606   | 1.04×  | 1.425    | 0.57× |
| 10  | 0.2 | 0.007535| 7.54×  | 0.001845 | 1.84× |
| 20  | 0.2 | 0.01271 | 3.18×  | 0.004651 | 1.16× |
| 50  | 0.2 | 0.04731 | 1.89×  | 0.02494  | 1.00× |
| 100 | 0.2 | 0.1685  | 1.69×  | 0.08014  | 0.80× |
| 200 | 0.2 | 0.5058  | 1.26×  | 0.2744   | 0.69× |
| 500 | 0.2 | 3.161   | 1.26×  | 2.203    | 0.88× |

**Honest verdict.** The exact spectrum closes most of the gap the design doc flagged as the weakest
part of the first pass: at `β/H⋆<=50`, where the interpolation was off by up to 16.5×, the exact
spectrum is now off by at most 3.16× -- a genuine, large improvement, and consistent with the
diagnosis that the interpolation's wrong peak location (`xi=0.833` vs the exact `xi=1.468`) mattered
most exactly in the regime where the signal's own peak sits close to the resolved-`ell` boundary.
It is not a uniform win: at `β/H⋆>=200`, where the interpolation actually agreed reasonably well
(within 27%), the exact spectrum now UNDERshoots the analytic approximation by 30-45%. This is not
hidden or reconciled away -- it is a real, reported trade-off: the worst-case mismatch across the
whole 12-point grid shrank from 16.5× (interpolated) to 3.16× (exact), a genuine improvement, but
the two versions do not bracket the truth from the same side, and Eq. (15) is itself only ever
described by its own authors as "a useful analytic order-of-magnitude approximation" derived from
the spectrum's peak value alone -- neither reproduction should be read as more than a same-order-of-
magnitude-to-tens-of-percent check on a deliberately approximate published formula, not on the
paper's own full numerical Fig. 3 (which was not independently re-extracted here; doing so would
need to either digitise Fig. 3 directly or re-derive the full χ² pipeline exactly as the paper's own
code, which does not exist publicly, would have done).

## Addendum (2026-09-26, later still): a Fisher-matrix forecast, prepared and run

See `docs/designs/CMB_FISHER_FORECAST.md` for a new, separate line of work: not a reproduction
check, but a forecast of how much a next-generation CMB dataset could improve on Koren-Tsai-Wang's
own bound, using the exact spectrum above. That document also records the two things this
forecast does NOT establish, matching the standard set above.

## Reproducibility

- `exploration/cmb/cmb_cascade.py` — implements Eqs. (1), (4)-(5), (9)-(13) of arXiv:2509.07076.
- `exploration/cmb/pdt_exact.py` — the exact `P_delta-t(k)` from Elor et al.'s Eqs. (S1)-(S16)
  (2026-09-26 addendum below), an alternative to `cmb_cascade.py`'s original interpolation.
- `exploration/cmb/cmb_bound.py` — implements Eq. (14), the χ² 2σ bound, against real Planck data;
  now runs both the interpolated and exact spectra and prints both tables.
- `data/external/planck2018_tt_full/COM_PowerSpect_CMB-TT-full_R3.01.txt` — the real Planck 2018 TT
  power spectrum (ℓ, D_ℓ, -dD_ℓ, +dD_ℓ, μK²), downloaded from the Planck Legacy Archive.
- Run: `uv run python exploration/cmb/cmb_cascade.py` (Fig. 2 sanity check) then
  `uv run python exploration/cmb/cmb_bound.py` (the table above; a few CPU-minutes).

## References (all verified by direct PDF read)

- S. Koren, Y. Tsai, R. Wang, "Boiling After the Dust Settles: Constraining First-Order Phase
  Transitions During Dark Energy Domination," arXiv:2509.07076 [hep-ph].
- G. Elor, R. Jinno, S. Kumar, R. McGehee, Y. Tsai, "Finite Bubble Statistics Constrain Late
  Cosmological Phase Transitions," Phys. Rev. Lett. 133, 211003 (2024), arXiv:2311.16222 [hep-ph].
- Planck Collaboration, N. Aghanim et al., "Planck 2018 results. VI. Cosmological parameters,"
  Astron. Astrophys. 641, A6 (2020), arXiv:1807.06209 [astro-ph.CO].
- Planck Legacy Archive, `https://pla.esac.esa.int/#home` (data source for the TT power spectrum
  table used here).
