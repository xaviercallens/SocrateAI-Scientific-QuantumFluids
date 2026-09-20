# What formal verification could do for the ⁴He dispersion programme

**Addressed to:** H. Godfrin and co-authors, as a possible basis for correspondence (PLAN M4).
**Based on:** the two publications in the 2021–2026 window, both read in full from their arXiv
sources — Phys. Rev. B **103**, 104516 (2021) [arXiv:2012.09067, with Supplemental and ancillary
tables] and Godfrin & Krotscheck, *The Dynamics of Quantum Fluids* [arXiv:2206.06039]. A survey of
arXiv, HAL, Crossref, OpenAlex and Semantic Scholar found **no other** H. Godfrin publication in that
window (the other "Godfrin" entries are different people). Manifest: `data/external/godfrin_papers/`.

**Status of this note:** every number below was recomputed here from the published ancillary tables;
nothing is taken on trust from a summary. It is a draft for the owner to review — **it has not been
sent to anyone.**

---

## 1. Two misprints in arXiv v1, with a numerical demonstration

We could not access the PRB version of record, so these may already be corrected there.

**Eq. (25), normal-fluid density.** As printed the Bose factor is `e^x/(e^x − 1)`; the Landau formula
needs `(e^x − 1)²`. This is not a matter of convention — it is checkable against the paper's own table:

| T (K) | standard formula, from `DispersionP0allRange.txt` | paper's table | formula *as printed* |
|---|---|---|---|
| 0.5 | 1.2305×10⁻⁶ g/cm³ | 1.230×10⁻⁶ | **329 g/cm³** |
| 1.0 | 1.0019×10⁻³ g/cm³ | 1.002×10⁻³ | **165 g/cm³** |

The tabulated values are right; the printed equation is not (the total density of the liquid is
0.145 g/cm³). **Eq. (20)** carries a spurious `k_B` prefactor (dimensionally inconsistent); the same
slip is in the Supplemental.

## 2. An observation on the Pitaevskii plateau — offered carefully

The text invokes the bound that a sharp excitation cannot lie above `2Δ_R` ("they cannot remain sharp
above the plateau"). In the published table `ε(k)` crosses `2Δ_R = 1.4836 meV` at `k = 3.01 Å⁻¹`.

| k (Å⁻¹) | ε (meV) | ε/Δ_R | excess over 2 |
|---|---|---|---|
| 3.0 | 1.4784 | 1.9930 | −0.0070 |
| 3.2 | 1.4805 | 1.9958 | −0.0042 |
| 3.4 | 1.4940 | 2.0140 | +0.0140 |
| 3.6 | 1.5538 | 2.0946 | **+0.0946** |

**What this does and does not show.** Up to `k ≈ 3.4 Å⁻¹` the excess (≤ 0.010 meV) is *below* the
quoted 0.013 meV uncertainty — not significant. It is significant (≈ 5σ) only at the last point,
`3.6 Å⁻¹`, which is exactly where the paper says the single- and multi-excitation contributions
"cannot be disentangled unambiguously". So this is **not** a claim that the bound is violated; the
natural reading is that the fitted peak there is no longer the single-excitation branch. Only 5 of the
227 tabulated points with `k ≥ 3.0` carry an error bar, which limits what can be said.

**The part that is solid, and machine-checked.** The paper notes that if `Δ_R` is revised, all
energies rescale proportionally (Eq. 13). Since `Δ_R` is itself one of those energies, **the ratio
`ε(k)/Δ_R` is invariant under any such recalibration** — `HeliumKinematics.
plateau_excess_calibration_invariant`. Whatever the last point means physically, it cannot be moved
relative to `2Δ_R` by improving the energy calibration. That seems worth knowing before anyone
re-measures `Δ_R`.

A related kinematic remark: the review states the plateau "ends at `2k_Δ`" = 3.84 Å⁻¹ at SVP, while
the measured termination is ≈ 3.6–3.7 Å⁻¹. `two_roton_momentum_le` makes the first an *upper
kinematic limit* (triangle inequality), not a prediction of where intensity vanishes — the two
statements are compatible, and the 0.15–0.2 Å⁻¹ gap is then a statement about matrix elements.

## 3. What is now machine-checked (`lean_src/HeliumKinematics.lean`, 12 theorems)

Axiom footprint `{propext, Classical.choice, Quot.sound}`; perturbed versions fail to compile.

| paper statement | theorem |
|---|---|
| 3-phonon damping "is then allowed up to a critical wave-vector" when dispersion is anomalous | `three_phonon_excess`: excess energy of `k₁+k₂ → k₁,k₂` is exactly `3c·a·k₁k₂(k₁+k₂)`; `three_phonon_open_iff`: open **iff** `a ≥ 0` (γ ≤ 0) |
| "the plateau ends at a wave number of `2k_Δ`… can in principle extend to zero wave number" | `two_roton_momentum_le`, `two_roton_parallel`, `two_roton_antiparallel` |
| "energies should be corrected proportionally, as indicated by Eq. 13" | `tofEnergy_rescale`, `plateau_excess_calibration_invariant` |
| Eqs. (12) and (13); "only two independent instrumental parameters" | `tof_eq12_eq_eq13` |
| "in a Bose gas, where the dispersion relation is parabolic, the critical velocity is zero" | `landau_velocity_parabolic_zero`, `landau_velocity_ge_of_above_sound_line` |
| Eq. (7) from Eq. (6) (Abraham) | `abraham_sound_speed_sq`: Eq. (7) **is** `dP/dρ` of Eq. (6) |
| `k_D = (6π²n)^{1/3}` ≈ `k_M` | `debye_mode_count`; numerically `k_D = 1.0895 Å⁻¹` vs `k_M = 1.103` |

## 4. Where formalization would genuinely help this programme — ranked by value to the experiment

1. **The specific-heat series, coefficients A…L of Eq. (22).** The paper states that Phillips et al.'s
   published series "contain errors" and Greywall's "misprints", and that the coefficients do not map
   one-to-one onto dispersion coefficients. That is precisely the situation in which a machine-checked
   derivation earns its keep: a symbolic chain — series inversion `k(ω)` to `ω⁷` (Lagrange inversion),
   density of states, then Bose integrals `∫xⁿ/(eˣ−1) = Γ(n+1)ζ(n+1)` — where one slip propagates
   silently. All six printed values were reproduced numerically here to 3 s.f.; a Lean proof of the
   closed forms would settle the literature disagreement permanently. *Most valuable, and the largest.*
2. **The new roton correction, Eq. (24)**, including the Supplemental's claim that the linear cross
   term "vanishes by symmetry". A new formula with a symmetry argument in prose is a natural target.
3. **Thermodynamic consistency of the tabulated series**: `F = E − TS`, `S = ∫C_V/T dT` applied to the
   printed `E^Ph`, `S^Ph`, `F^Ph` — cheap, and would have caught Eq. (20).
4. **Dimensional checking as a routine.** Both misprints in §1 are dimensional or convergence errors
   of the kind a units-aware formal statement rejects on sight.

## 5. Research directions that follow from the experiment, not from our earlier programme

Stated as questions, because the data are his and the physics is his.

- **The anomalous-to-normal transition near 20 bar.** With `three_phonon_open_iff`, the sign change of
  `γ(ρ)` at `P ≈ 20.4 bar` is *exactly* the closing of the three-phonon channel. The paper measures
  `γ(ρ)`, `α₃ < 0` at all densities, and `α₄ > 0`. With higher-order terms the open/closed boundary is
  no longer `γ = 0` but a curve `k_c(ρ)`; the exact excess for `ε = ck(1+α₂k²+α₃k³+α₄k⁴)` is a
  polynomial identity we can derive and check, giving `k_c(P)` from the *published* coefficients with
  propagated uncertainties. That is a prediction his phonon linewidth data could confront.
- **Maxon damping at `Δ_M ≈ 2Δ_R`** (`n_c = 0.0255 Å⁻³`, 21.5 ± 1.6 bar). The same two-roton
  kinematics as the plateau, applied at `k_M`: the decay needs `|k_M| ≤ 2k_R`, which holds with wide
  margin, so the threshold is purely energetic. Tables III and V let the crossing pressure be
  recomputed with uncertainties and compared with the quoted 21.5 bar.
- **The three-and-a-half coincidences.** `k_D ≈ k_M` (1.0895 vs 1.103), roton at `≈ 2k_D`, plateau end
  near `2k_R`. Are these one statement or three? Mode counting fixes `k_D` from density alone; tracking
  all three against the seven pressures in `DispersionAllPressures.txt` would show whether they move
  together.

**What we are *not* proposing**, having learned it the hard way (`RETRACTIONS.md`): any new bound or
"dual scale" on the dispersion. Our earlier attempt produced a quantity that was dimensionally forced
and a bound weaker than Onsager's. The value on offer here is verification of *his* derivations, not
new physics from us.
