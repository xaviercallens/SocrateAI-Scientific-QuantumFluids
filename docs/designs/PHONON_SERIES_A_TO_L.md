# The phonon specific-heat series, coefficients A to L — derivation and completion record

**Subject.** Godfrin, Beauvois, Sultan, Krotscheck, Dawidowski, Fåk, Ollivier, Sokol,
PRB 103, 104516 (2021), arXiv:2012.09067, Eq. (22):
`C_V = A T³ + C T⁵ + D T⁶ + E T⁷ + K T⁸ + L T⁹` for `ε = ck(1 + α₂k² + … + α₆k⁶)`, `α₁ = 0`.
The paper remarks that earlier published versions of this series contain errors; that remark is why the
series is worth checking rather than trusting.

**Status: COMPLETE. All six printed closed forms, and the printed inverse series including η, are
confirmed. No discrepancy was found.** (2026-09-21)

## 1. What had been checked before, and why it was not enough

An earlier pass reproduced the six printed *numbers* (A = 0.0831 … L = 0.141) from the six printed
*closed forms*. That tests the paper's arithmetic. It says nothing about whether the closed forms are
right — which is the only place the claimed errors in earlier literature could live. LL-15 again: the
check has to touch the property the claim depends on.

## 2. What was and was not decided in advance

**This check was not pre-registered, and E-1 was therefore not followed.** The derivation script was
written and run first; the list below was written afterwards. What can honestly be said:

- The script's docstring, written before the first run, states the purpose — derive the closed forms
  from scratch and compare symbolically with the printed ones — and the comparison is a symbolic
  `simplify(derived − printed) == 0`, which leaves no analyst freedom in how a match is scored.
- No prior about which coefficients might fail was recorded, so none is claimed.
- The checks: (P1) each of A, C, D, E, K, L as a symbolic identity; (P2) the printed inverse series,
  α₁ general, through (ω/c)⁷ with η; (P3) the T⁴ coefficient vanishes when α₁ = 0.
- **Outcome rule** (written after, but it binds what follows): a mismatch would be a candidate misprint
  *in the preprint*, subject to the version-of-record gate in `docs/FOR_GODFRIN.md`; a full match is a
  confirmation and is **not** to be dressed up as a finding.
- **Negative controls (must fail)**, chosen after the proofs compiled and run once each, all reported:
  η's `−12α₂³ → −11α₂³`, D's `15120 → 15121`, K's `9α₂α₃ → 8α₂α₃`, L's `55 → 54`.

## 3. The derivation

With `u = ε/ħc`:

1. **Reversion.** Solve `u = k(1 + α₁k + … + α₆k⁶)` for `k(u)` through `u⁷`.
2. **Density of states.** `k² dk/du = Σ gₙ uⁿ`. For α₁ = 0:
   `g₂ = 1, g₃ = 0, g₄ = −5α₂, g₅ = −6α₃, g₆ = 7(4α₂² − α₄), g₇ = 8(9α₂α₃ − α₅),
   g₈ = −3(55α₂³ − 30α₂α₄ − 15α₃² + 3α₆)`.
   The brackets of the printed C, D, E, K, L are already visible here; `g₃ = 0` is the absent `B T⁴`.
3. **Thermal integral.** `∫₀^∞ uⁿ/(e^{βu} − 1) du = β^{−(n+1)} n! ζ(n+1)`.
4. **Assemble and differentiate.**
   `E(T) = V/(2π²) Σ gₙ · (n+1)! ζ(n+2) · k_B^{n+2} T^{n+2} / (ħc)^{n+1}`, `C_V = dE/dT`.

Even `n` gives `ζ(4), ζ(6), ζ(8), ζ(10)` — rational multiples of powers of π, hence the π⁴…π⁸ in
A, C, E, L. Odd `n = 5, 7` gives `ζ(7), ζ(9)`, which have no known closed form, hence the explicit ζ in
D and K. That asymmetry is structural, not a presentational choice.

## 4. Results

| Check | Tool | Outcome |
|---|---|---|
| P2: 7 inverse-series coefficients, α₁ general | sympy, `exploration/godfrin/derive_cv_series.py` | **all match** |
| P1: A, C, D, E, K, L symbolic | same | **all six match** |
| P3: T⁴ coefficient | same | **0** |
| P2 in Lean | `PhononSeries.dispersion_kInv` | proved |
| DOS in Lean | `PhononSeries.density_of_states` | proved |
| `B₆ = 1/42, B₈ = −1/30, B₁₀ = 5/66` | `PhononSpecificHeat.bernoulli'_six` … | proved (Mathlib's table stops at `B₄`) |
| `ζ(6) = π⁶/945, ζ(8) = π⁸/9450, ζ(10) = π¹⁰/93555` | `riemannZeta_six/eight/ten` | proved |
| thermal integral, every order | `thermal_bose_integral` | proved |
| the six integrals `π⁴/15, 8π⁶/63, 720ζ(7), 8π⁸/15, 40320ζ(9), 128π¹⁰/33` | `bose_integral_values` | proved |
| **P1 in Lean: all six coefficients** | **`phonon_specific_heat`** | **proved** |
| negative controls (4) | scratch copies | **all four rejected** |

P1, P2, P3 all hold: the paper is right. Because a symbolic match admits no tuning, the missing
pre-registration does not weaken this particular result — but it is recorded as a process lapse.

## 5. How it is stated in Lean, and why that way

**Truncation without analysis.** "Equal up to O(u⁸)" is stated as an identity in an arbitrary
commutative ring `R` with an element `e` such that `e ^ 8 = 0`. Taking `R = A[[u]]/(u⁸)` recovers the
power-series statement; nothing about convergence is needed, and the theorem is pure ring theory.

**Certificates, not trust.** The direct identity has a 4,918-term remainder — not something to hand to
`ring`. Instead the powers `k², …, k⁷` are truncated one at a time; each step is
`linear_combination (r) * h` with `h : e ^ 8 = 0` and a remainder `r` of 40–202 terms computed by sympy.
The generator is *untrusted*: if it produced a wrong certificate the kernel would reject it. This is the
first generated proof file in the tree (`exploration/godfrin/gen_phonon_series_lean.py`).

**ζ(7), ζ(9) as parameters.** `phonon_specific_heat` takes real `z7 z9`; `bose_integral_values` is
where they are tied to `riemannZeta 7`, `riemannZeta 9`. This keeps the capstone in ℝ and makes the
"no closed form" point visible in the type.

## 6. What is NOT proved — do not overstate

1. **The link between `density_of_states` and `phonon_specific_heat` is by inspection.** The `g`
   arguments passed to `energyTerm` are the DOS brackets retyped; no theorem says "these are the
   coefficients of that polynomial". Closing this needs the statement in `Polynomial` or `PowerSeries`
   with a `coeff` extraction. Small, and should be done before anyone calls the chain end-to-end.
2. **Term-by-term integration is assumed legitimate.** Each term's integral is proved; that the sum of
   integrals equals the integral of the (truncated) sum is linearity plus integrability and is not
   stated as one theorem.
3. **Asymptotic validity** — that this series approximates `C_V` for the *measured* dispersion, with the
   upper limit sent to infinity and the roton branch dropped — is a statement about a measured function.
   Not provable; roadmap T6 covers the mathematical half only.
4. **Units.** The paper's source prints `α₂ = 1.55 Å⁻²` in §VI but `Å²` in §II. Dimensional analysis
   (`α₂k²` dimensionless) requires `Å²`. Lean is unit-blind here. Minor; third item for the misprint
   list, same version-of-record gate.

## 7. Consequence for the note to Godfrin

The note's strongest item changes from "the ζ(7)/ζ(9) point" to: *your Eq. (22) — all six coefficients
and the inverse series — has been independently derived and machine-checked, and is correct.* For a
series whose predecessors were wrong, that is a useful thing to be told, and it is a confirmation, which
is a better opening than a list of misprints.
