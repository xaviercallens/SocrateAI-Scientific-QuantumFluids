# A dual-scale proposal for quantum fluids, stated so measurement can refute it

**Date:** 2026-09-20. **Status:** PRE-REGISTRATION. §1–§3 are definitions and predictions written **before** the
7-pressure analysis and the duality-map test exist. §4 records exactly what was already known when this was written.
**Audit:** required before the results are interpreted (E-1). Nothing in §5 may be filled in before §1–§4 are committed.

---

## 1. The definition

For a quantum fluid with excitation dispersion `ε(k)`, sound speed `c` and mass `m`, define the **dual length**

```
    ℓ(k)  :=  ε(k)² / (ħ² c² k³)                          [dimensions: length]
```

`ℓ` is model-independent and directly measurable: `ε(k)` is what neutron scattering reports, `c` is the `k → 0` slope.
Its two limits are exactly the two branches of the dual-scale form:

| regime | dispersion | `ℓ(k)` |
|---|---|---|
| phonon (`k → 0`) | `ε = ħck` | `1/k` |
| free particle (`k → ∞`) | `ε = ħ²k²/2m` | `k/k*²`, with `k* := 2mc/ħ` |

**Bogoliubov.** The Bogoliubov dispersion is Pythagorean in these two branches,
`ε² = (ħck)² + (ħ²k²/2m)²`, hence **exactly**

```
    ℓ_B(k)  =  1/k  +  k/k*²      — the R + α'/R form with R = 1/k, α' = 1/k*²
```

so `ℓ_B` is invariant under the involution `k ↦ k*²/k` (which exchanges the phonon and free-particle terms), and

```
    ℓ_B(k)  ≥  2/k*  =  ħ/(mc)  =  √2 ξ ,      equality iff k = k* = √2/ξ
```

with `ξ := ħ/(√2 m c)` the healing length. **This is the dual-scale statement for a quantum fluid**: a lower bound on an
effective length, saturated at a self-dual wavenumber, arising from the exchange of two physical branches.

**No string-theory content is claimed.** The `R + α'/R` shape here is AM–GM on two positive terms; the upstream
programme has withdrawn T-duality language (`OpenAINavierStokesEuler/REVIEW_AND_NEW_DIRECTION.md`, 2026-09-15) and this memo
does not reintroduce it. The interest is that the shape is **measurable**, not that it is stringy.

## 2. The hypothesis, and what would refute it

> **DS-QF.** For a quantum fluid, `ℓ(k)` attains an interior minimum `ℓ_min > 0` at a wavenumber `k_min`, and
> `ℓ_min ≈ √2 ξ`, `k_min ≈ k*`, with `ℓ` approximately invariant under `k ↦ k*²/k`.

Refuted if `ℓ(k)` has no interior minimum in the measured range, or if `ℓ_min` and `√2 ξ` (equivalently `k_min` and `k*`)
disagree by more than a factor of 1.5, or if the duality map fails by more than 50%.

## 3. Pre-registered tests (on Godfrin et al. 2021 ancillary tables, Tier B data already in `data/external/`)

For **each** of the 7 pressures `P ∈ {0, 0.51, 1.02, 2.01, 5.04, 10.02, 19.98}` bar:
- **M1.** Fit `c(P)` from the low-`k` phonon region with this repo's own validated harness (`dispersion_fit`, CLAIM-003),
  restricted to `k ≤ 0.3 Å⁻¹`. Report fit and residual. Derive `k*(P) = 2mc/ħ`, `ξ(P)`.
- **M2.** Compute `ℓ(k)` on the tabulated grid. Report whether the minimum is interior or at an endpoint,
  `k_min`, `ℓ_min`, and the ratios `k_min/k*`, `ℓ_min/(√2 ξ)`.
- **M3.** Duality-map test: for every `k` with both `k` and `k*²/k` in range, report `max |ℓ(k)/ℓ(k*²/k) − 1|`.
- **M4.** Bogoliubov reference: the same three numbers for `ℓ_B` computed from the same `c(P)` (must give
  `k_min/k* = 1`, `ℓ_min/(√2 ξ) = 1`, duality error `0` — **this is the positive control**: if it does not, the code is wrong
  and the run is void).
- **M5.** Negative control: feed the harness a pure phonon dispersion `ε = ħck`. `ℓ = 1/k` is monotone, so the
  "interior minimum" detector **must** report an endpoint. If it reports an interior minimum, the detector cannot fail and the run is void.

**Predictions, fixed now (P=0 partly known, see §4):**
- **P1.** No interior minimum at any pressure: the roton and the ~1.1 meV plateau make `ℓ` decrease monotonically at large `k`.
- **P2.** The duality map fails by ≫ 50%.
- **P3.** `ℓ` at the roton wavenumber is **below** `√2 ξ` — the would-be minimum length is violated in real He-II — by a factor > 2.
- **P4.** The violation deepens with pressure (the roton deepens: CLAIM-015 measured `Δ` falling `−0.67 %/bar`).

## 4. Honest disclosure of prior knowledge

An exploratory computation on 2026-09-19 (GE-3 in `docs/GEDANKEN_DUAL_SCALE.md`) already found, **for P = 0 only** and with
`c` taken from the literature rather than fitted, that `min ε²/k³` over `k > 0.2 Å⁻¹` falls at the range edge (3.6 Å⁻¹),
i.e. no interior minimum. **P1 at P = 0 is therefore not a blind prediction.** Everything else — the seven pressures,
the fitted `c(P)`, M3, P2, P3, P4 — is unrun at the time of writing.

## 5. Results

*(empty until §1–§4 are committed and the run is executed)*

## 6. What a refutation would license

DS-QF failing for He-II does **not** kill the dual-scale idea; it localises it. The proposal then becomes:

> **DS-QF′.** The dual-scale structure is a property of the *weakly interacting* regime (dilute BEC, Bogoliubov), where it
> holds exactly, and the measured deviation `ℓ(k_roton)/(√2 ξ)` is a dimensionless measure of how far a real superfluid is
> from that regime.

DS-QF′ is testable on cold-atom Bragg-spectroscopy data (not in this repo), and is consistent with this stream's shell-model
result: a dispersive regulator of order `k^σ` controls the norm of order `k^{σ-1}` uniformly in the cutoff
(`ShellHamiltonian.dispersive_norm_le`, CLAIM-023); Bogoliubov has `σ = 2`, so it controls `Σk|v|²` and not the enstrophy.
