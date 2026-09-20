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

### 5b. Second direction carried out: the Debye coefficient `A` of Eq. (22), machine-checked end to end (2026-09-20)

`lean_src/BoseIntegral.lean`, 5 theorems, axioms `{propext, Classical.choice, Quot.sound}`; two
perturbed versions fail to compile.

Ranked first in §4 because the paper states earlier published series "contain errors". The chain for
the leading term is now verified:

| step | theorem |
|---|---|
| `1/(eᵗ−1) = Σₙ e^{−(n+1)t}` for `t > 0` | `hasSum_bose` |
| `∫₀^∞ t^{s−1}/(eᵗ−1) dt = Γ(s)·Σₙ (n+1)^{−s}`, `Re s > 1` | `hasSum_mellin_bose` |
| **`∫₀^∞ t³/(eᵗ−1) dt = π⁴/15`** (= `Γ(4)ζ(4)`) | `mellin_bose_four` |
| the Debye energy collapses to `π²V(k_BT)⁴/(30(ħc)³)` | `debyeEnergy_eq` |
| **`C_V = dE/dT = A T³` with `A = 2π²k_B⁴V/(15c³ħ³)`** | `debye_specific_heat` |

Numerically `A = 0.0831 J/(mol·K⁴)`, reproducing the value printed in Eq. (22) to the quoted four
digits. Mathlib supplied `ζ(4) = π⁴/90` and the Gamma integral but **not** the Bose integral; the
bridge is its Mellin–Dirichlet machinery, and `mellin_bose_four` is the reusable piece.

**Extended 2026-09-20: the Bose integral is now general, not just the `s = 4` case.**

- `bose_integral_nat`: `∫₀^∞ tⁿ/(eᵗ−1) dt = n! · ζ(n+1)` for every `n ≥ 1`. This is the single
  identity all six coefficients of Eq. (22) rest on, so `A, C, D, E, K, L` no longer need separate
  integral work.
- `bose_integral_even`: for even order the value is fully explicit, via Mathlib's Bernoulli formula
  for `ζ(2k)`.

**An honest structural remark on your Eq. (22).** `D` and `K` carry `ζ(7)` and `ζ(9)`. Those have no
known closed form — they are not missing from Mathlib, they are missing from mathematics. So `A, C,
E, L` can be given in closed form and `D, K` can only ever be *numerically* evaluated or left
symbolic. That is worth stating explicitly in any future comparison with Phillips et al. and
Greywall, because a disagreement in `D` or `K` cannot be settled by exact algebra alone.

**What remains for the full series:** the Lagrange inversion `k(ω)` to `ω⁷` and the density of
states. Those are combinatorial rather than analytic, and are the natural next increment.

### 5a. First direction carried out: where the three-phonon channel closes (2026-09-20)

`exploration/godfrin/three_phonon_threshold.py`; identities in `HeliumKinematics` (15 theorems now).

With the series of Eq. (2), each closing condition factors as `c·kⁿ` times a **quadratic** in `k`, so
the thresholds are explicit in the published coefficients — machine-checked:

| condition | identity (Lean) | SVP, from `α₂, α₃, α₄ = 1.55, −4.04, 2.30` |
|---|---|---|
| soft emission, `dε/dk = c` | `group_velocity_excess`: `c k²(3α₂ + 4α₃k + 5α₄k²)` | **0.404 Å⁻¹** |
| symmetric split, `ε(k) = 2ε(k/2)` | `symmetric_split_excess`: `c k³(¾α₂ + ⅞α₃k + (15/16)α₄k²)` | **0.455 Å⁻¹** |
| phase velocity, `ε/k = c` | `phase_velocity_excess`: `c k²(α₂ + α₃k + α₄k²)` | **0.566 Å⁻¹** |

Three remarks that may be useful to the experiment:

1. **They are three different numbers, and the symmetric split is the *last* two-phonon channel to
   close** (a scan over all splits confirms nothing is open beyond 0.455). A single quoted "`k_c`"
   hides which process is meant: a linewidth from *two*-phonon decay should vanish near 0.455, not 0.566.
2. **Independent agreement.** The measured SVP table, with no series at all, gives the symmetric-split
   crossing at **0.453 Å⁻¹** — within 0.002 of the value from the fitted coefficients. The maximum
   excess is only 14.5 µeV (at `k = 0.31`), which says how delicate the open window is.
3. **It does not depend on `Δ_R`.** The excess is homogeneous of degree one in the energy scale, so by
   `tofEnergy_rescale` a proportional recalibration cannot move `k_c`. It depends on the *shape* only.

**Honest limit under pressure.** The 7-pressure table starts at `k = 0.15`, so the symmetric split is
testable only for `k ≥ 0.30`, where the excess (≤ 12 µeV) is about 4× the propagated error (≈ 2.7 µeV).
The channel is open at ≤ 2 bar, consistent with zero at 5 bar (−2.4 ± 2.9 µeV), and clearly closed at
10 and 24 bar — but `k_c(P)` **cannot be localised** from this table. Two things would fix that:
published `α₂, α₃, α₄` at each pressure (the paper fits them; only the SVP set is printed in the text),
or table rows below 0.15 Å⁻¹. Note also that the P = 0 column of the 7-pressure table gives 0.414 where
the full-range SVP file gives 0.453: the former is raw neutron data, which the paper itself says runs
"slightly too high" below 0.2 Å⁻¹, while the latter merges in ultrasound — a visible consequence of
that known bias, at exactly the wave vectors `k/2` that the split probes.

**What we are *not* proposing**, having learned it the hard way (`RETRACTIONS.md`): any new bound or
"dual scale" on the dispersion. Our earlier attempt produced a quantity that was dimensionally forced
and a bound weaker than Onsager's. The value on offer here is verification of *his* derivations, not
new physics from us.
