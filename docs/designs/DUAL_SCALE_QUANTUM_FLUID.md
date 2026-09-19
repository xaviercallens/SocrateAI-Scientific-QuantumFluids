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

For **each** of the 7 pressures `P ∈ {0, 0.51, 1.02, 2.01, 5.01, 10.01, 24.08}` bar (list corrected 2026-09-20 from the
data file's own `.meta`, before any run; the first draft mis-transcribed the last three):
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

## 5. Results (run 2026-09-20, after §1–§4 were committed as 1f8e2af)

### 5.0 Amendment A2 — the first run was VOID, as the pre-registration required

The first execution of M1–M5 on the 7-pressure table gave **M4 = FAIL**: the Bogoliubov positive control returned
`k_min/k* = 0.701`, `ℓ_min/(√2ξ) = 1.064` instead of the required `1, 1`. Per §3, *"the run is void"*. The cause is not a coding
error but a **violated control hypothesis** (MechanicaFluidorum LL-17): that table's wavenumber range is `[0.15, 2.21] Å⁻¹`,
while `k* = 3.1–4.4 Å⁻¹`. **The self-dual point lies outside the 7-pressure data**, so M2 and M3 cannot be performed on it at all —
and the control is what revealed this, not inspection. Amended scope:

- **M1–M5 at P = 0** move to the full-range file `DispersionP0allRange.txt` (`k ∈ [0.002, 3.600] Å⁻¹`, 1726 points), which does cover `k*`.
- **P4 only** is measured on the 7-pressure table, restricted to the roton region (`k ≈ 1.92 Å⁻¹`, inside its range), under a new
  control **C2**: the Bogoliubov reference must satisfy `ℓ_B(k)/(√2ξ) ≥ 1` at **every** `k` and every pressure. C2 **PASSES**.
- M2/M3 at pressures other than 0 are **not measured** and are not claimed.

### 5.1 Controls (amended scope)

| control | requirement | result |
|---|---|---|
| **M4** Bogoliubov, P=0 full range | `k_min/k* = 1`, `ℓ_min/(√2ξ) = 1`, duality err `0` | **PASS**: `0.9998`, `1.0000`, `2.2×10⁻⁵` (grid resolution) |
| **M5** pure phonon `ε = ħck` | minimum must be at an endpoint | **PASS**: endpoint, no interior minimum |
| **C2** Bogoliubov ratio at every k, 7 pressures | `≥ 1` | **PASS** (range `1.103 → 1.275` at the roton wavenumber) |
| **M1** `c` fit cross-check | should recover the literature `238.3 ± 0.1 m/s` | `238.8 m/s` on `k ≤ 0.05` (**0.2 %**); the fit drifts up with the window (`240.1 / 243.8 / 247.3` for `k ≤ 0.1 / 0.2 / 0.3`) because He-II has anomalous dispersion. The 7-pressure table starts at `k = 0.15`, so its `c(P)` carries a common `+4.7 %` bias; results below are given bias-corrected, and the trend is checked to be insensitive to it. |

### 5.2 He-II at P = 0, full range — DS-QF is refuted

| quantity | measured | DS-QF expects |
|---|---|---|
| interior minimum of `ℓ` in `[0.002, 3.600] Å⁻¹` | **none** — `ℓ` falls across every decade (`488 → 2.10 → 0.130 → 0.0210 Å`) and is still falling at the range edge | a minimum at `k*` |
| `ℓ_min/(√2 ξ)` (at the `3.6 Å⁻¹` edge) | **0.0316** — a factor **32 below** the would-be floor | `1` |
| `ℓ(k_roton)/(√2 ξ)`, `k = 1.92 Å⁻¹` | **0.0474** — a factor **21 below** | `≥ 1` |
| duality-map error `max|ℓ(k)/ℓ(k*²/k) − 1|` | **1.32 (132 %)** on the window `[2.51, 3.60] Å⁻¹` | `0` |

Robustness: with `c` fitted (240.1) instead of the literature value (238.3) the four numbers are `none`, `0.0314`, `0.0470`, `1.29` —
conclusions unchanged. The only structure in `dℓ/dk` is noise-level jitter where `ε(k)` is flat near the roton (126 sign
changes, all within the table's quoted precision); on every sub-interval `ℓ` decreases.

*Caveat, stated against our own result:* `ℓ` must eventually rise (free-particle behaviour gives `ℓ → k/k*²`), so a minimum exists
**somewhere beyond 3.6 Å⁻¹**. The measurement does not say "He-II has no minimum length"; it says the minimum is outside the
measured range and that `ℓ` there is already **32× below** the Bogoliubov floor — which is what refutes DS-QF as stated.

### 5.3 Pressure trend (P4 only, amended scope, bias-corrected `c(P)`)

| P (bar) | c (m/s) | k\* (Å⁻¹) | √2ξ (Å) | roton k | ε (meV) | `ℓ/(√2ξ)` | shortfall |
|---|---|---|---|---|---|---|---|
| 0 | 238.7 | 3.008 | 0.665 | 1.920 | 0.7413 | 0.0473 | 21.1× |
| 0.51 | 242.0 | 3.050 | 0.656 | 1.924 | 0.7381 | 0.0460 | 21.7× |
| 1.02 | 245.4 | 3.094 | 0.646 | 1.920 | 0.7357 | 0.0453 | 22.1× |
| 2.01 | 251.5 | 3.170 | 0.631 | 1.932 | 0.7301 | 0.0428 | 23.4× |
| 5.01 | 267.6 | 3.373 | 0.593 | 1.966 | 0.7138 | 0.0365 | 27.4× |
| 10.01 | 290.8 | 3.666 | 0.546 | 1.982 | 0.6882 | 0.0304 | 32.9× |
| 24.08 | 335.9 | 4.233 | 0.472 | 2.048 | 0.6256 | 0.0197 | 50.7× |

`ratio(24.08 bar)/ratio(0 bar) = 0.417` — the violation **deepens** monotonically with pressure, by a factor 2.4 over the range.
Identical (0.417) with uncorrected `c`, so the trend does not depend on the `c` bias.

### 5.4 Verdicts against the pre-registered predictions

| | prediction | outcome |
|---|---|---|
| **P1** | no interior minimum at any pressure | **CONFIRMED at P = 0** (and not blind — see §4). **Not measured** at other pressures: out of range (A2). |
| **P2** | duality map fails by ≫ 50 % | **CONFIRMED**: 132 % |
| **P3** | `ℓ(roton) < √2ξ` by more than 2× | **CONFIRMED, and under-predicted**: 21× |
| **P4** | violation deepens with pressure | **CONFIRMED**: 0.0473 → 0.0197, ratio 0.417 |

**DS-QF is refuted for superfluid ⁴He**, quantitatively and at every pressure measured. `DS-QF′` (§6) is what survives.

### 5.5 What is and is not new

The *physics* here is textbook: the roton lies far below the Bogoliubov curve because He-II is strongly correlated, and the roton
deepens with pressure toward the freezing line. **No novelty is claimed for that.** What this section adds is (i) the
dimensionless combination `ℓ(k)/(√2ξ)` in which the statement becomes a single falsifiable number, (ii) the measured values of
that number, 21× at SVP to 51× at 24 bar, and (iii) the Lean-checked bound (`DualLength.not_bogoliubov_of_lt`) that makes
"measured `ℓ < 2/k*` ⟹ not Bogoliubov at that `k`" a theorem rather than an inference.

## 6. What a refutation would license

DS-QF failing for He-II does **not** kill the dual-scale idea; it localises it. The proposal then becomes:

> **DS-QF′.** The dual-scale structure is a property of the *weakly interacting* regime (dilute BEC, Bogoliubov), where it
> holds exactly, and the measured deviation `ℓ(k_roton)/(√2 ξ)` is a dimensionless measure of how far a real superfluid is
> from that regime.

DS-QF′ is testable on cold-atom Bragg-spectroscopy data (not in this repo), and is consistent with this stream's shell-model
result: a dispersive regulator of order `k^σ` controls the norm of order `k^{σ-1}` uniformly in the cutoff
(`ShellHamiltonian.dispersive_norm_le`, CLAIM-023); Bogoliubov has `σ = 2`, so it controls `Σk|v|²` and not the enstrophy.
