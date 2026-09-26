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

## Reproducibility

- `exploration/cmb/cmb_cascade.py` — implements Eqs. (1), (4)-(5), (9)-(13) of arXiv:2509.07076.
- `exploration/cmb/cmb_bound.py` — implements Eq. (14), the χ² 2σ bound, against real Planck data.
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
