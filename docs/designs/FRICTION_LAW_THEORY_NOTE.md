# Why α ∝ ρ_n in a classical field, and what the coefficient measures (FL3 of `PGPE_FRICTION_LAW_PREREG.md`)

Written 2026-10-07 21:10, before any friction-law run, as the "computed before the runs" item FL3. Units
`ħ = m = 1`, `c = 1` (`gn = 1`), circulation `κ = 2π`, healing length `ξ = 1`.

## Kinetic argument

A vortex moving at velocity `v` through a gas of excitations with occupation `n_k` (number per mode, isotropic)
and transport (momentum-transfer) cross-section `σ_tr(k)` — a length in two dimensions — feels, to first order in
`v`, the drag `F = −D v` with
```
D = ½ ∫ d²k/(2π)² (−∂n_k/∂ε_k) k² c_g(k) σ_tr(k),
```
where `c_g` is the group velocity and the ½ is the two-dimensional angular average of `(k̂·v̂)²`. The normal
density of the same gas is the Landau expression
```
ρ_n = ½ ∫ d²k/(2π)² (−∂n_k/∂ε_k) k².
```
Both are integrals of `k²(−∂n/∂ε)` over the modes; they differ by the factor `c_g σ_tr` in the integrand. For a
**Rayleigh–Jeans** bath, `n_k = T/ε_k` and `−∂n/∂ε = T/ε_k²`, so with the phonon dispersion `ε = ck`
```
ρ_n = (T/2c²) · (k_c²/4π),       D = (T/2c²) · (1/2π) ∫₀^{k_c} k dk · c_g(k) σ_tr(k) = ρ_n · ⟨c_g σ_tr⟩_disk ,
```
with `⟨·⟩_disk` the **uniform average over the disk `|k| < k_c`** (each mode has the same energy `T`, so the
Rayleigh–Jeans bath weights all modes equally in `k²(−∂n/∂ε)`). With the Bogoliubov dispersion the weights change
by `k²/ε_k²·dε/dk` on both sides and the statement `D/ρ_n = ⟨c_g σ_tr⟩` survives with the same weight in numerator
and denominator.

Force balance for a weakly damped vortex, `ρ_s κ ẑ×(v_L − v_s) = D (v_n − v_L)`, gives `α = D/(ρ_s κ)` at
leading order. Hence
```
α / (ρ_n/ρ) = (ρ/ρ_s) · ⟨c_g σ_tr⟩ / κ .
```
**The friction law `α ∝ ρ_n` is what any isotropic scattering bath gives; the coefficient is the mode-averaged
transport cross-section of the vortex, in units of `κ/c`.** With our measured `0.232 ± 0.014` and
`ρ_s/ρ = 0.95` (mean of the three bases): `⟨c_g σ_tr⟩ = 0.232 × 2π × 0.95 = 1.39 ± 0.08` — the classical-field
vortex has a mode-averaged transport cross-section of **1.4 healing lengths** (c = 1).

## What this predicts for the cutoff dependence (the FL2 question)

The coefficient depends on the cutoff only through the disk average of `σ_tr(k)`.
- Long-wavelength phonons (`kξ ≪ 1`): Born scattering off the vortex velocity field (Pitaevskii 1959; Sonin,
  PRB 55, 485 (1997), Eqs. 40 and 44, read 2026-10-07 21:40): amplitude
  `a(φ) = ½√(k/2π)(κ/c) e^{iπ/4} sinφ cosφ/(1−cosφ)`, so `σ(φ)(1−cosφ) = (kκ²/8πc²)(1+cosφ)cos²φ` and the
  transport cross-section is
  ```
  σ_∥(k) = κ² k / (8 c²)      (Born, valid for κk/c = 2πkξ ≪ 1)
  ```
  — it **grows linearly with `k`** (the small-angle divergence is integrable in `σ_∥`). The transverse one is
  `σ_⊥ = κ/c`, `k`-independent, which is the Iordanskii force `D′ = ρ_n κ` that our `α′ ≈ 0` excludes.
  Sonin's own validity condition is the Born parameter `κk/c ≪ 1`, i.e. `kξ ≪ 1/2π ≈ 0.16`: in our disk
  (`k_c = π`) fewer than **3 %** of the modes satisfy it. Extrapolating the Born law over the whole disk anyway
  gives `⟨σ_∥⟩ = κ²⟨k⟩/(8c²) = κ²k_c/(12c²) = π³/3 ≈ 10 ξ` at `k_c = π` — **seven times the measured 1.4 ξ**
  (more with `c_g > c` at `kξ > 1`). So the measured coefficient is already far below the long-wavelength law: the
  cross-section of the short-wavelength modes that dominate the bath is much smaller than the Born extrapolation.
  If the Born law *did* hold to the cutoff the coefficient would scale **linearly with the cutoff**:
  `c(2π/3) : c(π) : c(2π) = 0.67 : 1 : 2`.
- Short wavelengths (`kξ ≳ 1`), which dominate the disk average for our cutoffs (`k_c = π`, so 90 % of the modes
  have `kξ > 1`): the excitation sees the density-depleted core, and the transport cross-section saturates at the
  **geometric** scale of the core, a few `ξ`. Then `⟨σ_tr⟩` is nearly cutoff-independent for `k_c ≳ 2/ξ`, and the
  coefficient is nearly universal across cutoffs in that range.
- Our value, `⟨σ_tr⟩ = 1.4ξ`, is of the geometric size, which is the second regime.

**Registered expectation for FL3 (recorded here before the runs):** the coefficient `c = α/(ρ_n/ρ)` is nearly
unchanged across the three cutoffs — a spread of order 10–30 %, at the edge of FL2's 20 % criterion, with the weak
ordering `c(2π/3) ≤ c(π) ≤ c(2π)` (the Born-regime modes, which have the smallest cross-sections per unit `k` only
at the very smallest `k`, weigh slightly more at the lowest cutoff). The sharp rival, from Sonin's Born law
extended to the cutoff, is `c ∝ k_c`: `0.67 : 1 : 2`, a spread of 110 %. The two are separated by any measurement
at the 20 % level, which the existing estimators give.

## What would settle `σ_tr(k)` directly (not part of the campaign; recorded as the obvious follow-up)

Scatter a monochromatic Bogoliubov wave of wavenumber `k` off a single vortex at `T = 0` in a large box and measure
the momentum transferred to the vortex (or the angular distribution of the scattered wave). This gives `σ_tr(k)`
mode by mode and would turn the friction law into a prediction with no measured input; it is the classical
counterpart of the phonon-scattering calculations of Pitaevskii (1959), Iordanskii (1966) and Sonin (1997), done
on the compressible core instead of a point vortex.

## Consistency check of the "same weight" premise (computed 2026-10-07 21:45, report only)

The Landau normal density of a Rayleigh–Jeans Bogoliubov bath on the actual PGPE mode set (`ρ_n = ½L⁻²Σ_k T k²/ε_k²`,
`ε_k² = k² + k⁴/4`, disk `|k| ≤ π`) against the measured `1 − n_s/n` of the three transport bases:

| base | T | measured ρ_n/ρ | Landau RJ–Bogoliubov | ratio |
|---|---|---|---|---|
| L = 96, e = 0.60 | 0.110 | 0.0293 | 0.0218 | 1.35 |
| L = 64, e = 0.70 | 0.220 | 0.0534 | 0.0434 | 1.23 |
| L = 64, e = 0.80 | 0.353 | 0.0945 | 0.0697 | 1.36 |

The free-quasiparticle formula accounts for 74–81 % of the measured normal density, consistently across
temperature; the remainder is interaction (the condensate density is below `n`, the modes are not free Bogoliubov
modes at `mg = 1`). The kinetic reading therefore holds at the 25 % level, and the inferred `⟨σ_tr⟩ = 1.4 ξ` carries
that systematic in addition to its statistical error. It does not affect the FL3 rival (a factor 7 and a factor 2
scaling against a 25 % systematic).

## Caveats

The kinetic argument assumes independent excitations scattering off a vortex at rest in the bath frame, a Markovian
bath and no back-action; the sub-diffusion at short lags shows the last two are not exact at `0.14 T_BKT`. It is a
reading of the measured law, not a derivation of its coefficient.
