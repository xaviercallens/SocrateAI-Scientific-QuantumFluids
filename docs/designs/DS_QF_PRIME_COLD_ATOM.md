# Observational programme: testing DS-QF′ on a dilute Bose-Einstein condensate

**Date:** 2026-09-20. **Status:** PRE-REGISTRATION. Written before any dataset is in hand and before
any number is computed. **Audit required before §6 is filled** (E-1).
**Depends on:** CLAIM-024 (DS-QF refuted for ⁴He), `docs/DUAL_SCALE_PROPOSAL.md` §4.

---

## 1. The claim that needs an observation

DS-QF′ is currently the weakest link in the whole programme: it is a **proposal with zero supporting
evidence**. It says the dual-scale structure is a property of the *weakly interacting* regime — where
`ℓ(k) = ε(k)²/(ħ²c²k³) ≥ √2 ξ` holds, exactly, for the Bogoliubov dispersion — and that
`ℓ/(√2ξ)` measures the distance from that regime. Superfluid ⁴He sits at **0.047** (21× below).

The whole proposal therefore rests on one untested assertion: **that something actually sits near 1.**
If nothing does, DS-QF′ is not a localisation of the dual-scale idea, it is the end of it.

A dilute BEC is the natural test because it is where Bogoliubov theory is quantitatively accurate and
where `ξ` is large enough that the crossover wavenumber `k* = √2/ξ` is experimentally reachable by
Bragg spectroscopy.

## 2. The observable, and the one thing that makes data useless

`ℓ(k)` requires `ε(k)` and `c`. The bound is **saturated at `k = k*`**, so:

> **Data confined to the phonon regime `k ≪ k*` cannot test this at all.** There `ℓ ≈ 1/k`, which is
> large and says nothing. Any dataset that does not reach `k ≳ k*` is rejected before analysis.

This is recorded first because it is the most likely way this programme wastes effort: most BEC
spectroscopy is *deliberately* in the phonon regime.

## 3. Pre-registered predictions

Let `R := min_k ℓ(k)/(√2 ξ)` over the measured range, and `κ := k_min/k*` the wavenumber where the
minimum falls. Fixed now:

- **C1.** For a dilute BEC (`n a_s³ ≲ 10⁻⁴`): `R ∈ [0.7, 1.4]`.
- **C2.** `κ ∈ [0.6, 1.6]` — the minimum sits near the self-dual point, not at a range edge.
- **C3.** `R` exceeds the measured ⁴He value by at least **10×** (i.e. `R ≥ 0.47`). This is the
  discriminating comparison and it is the one that matters, because it needs no theory input.
- **C4.** If two or more datasets at different gas parameters are available, `R` decreases as
  `n a_s³` increases.

**Deliberately not predicted:** the coefficient of the leading Lee–Huang–Yang/Beliaev correction to
`R = 1 − O(√(n a_s³))`. This repository has not verified a literature value for it, so no quantitative
correction is claimed and C1's window is set wide enough not to depend on one.

## 4. Refutation criterion (the point of the exercise)

> **DS-QF′ is refuted if a dilute BEC with `n a_s³ ≲ 10⁻⁴` gives `R ≤ 0.3`.**

That would mean the dual-scale floor fails even where Bogoliubov theory is accurate, so it is not a
property of weak coupling and the localisation in `DUAL_SCALE_PROPOSAL.md` §4 collapses. The correct
response would then be to withdraw DS-QF′ entirely, not to narrow it again.

## 5. Controls — a run failing any of these is void

| control | requirement |
|---|---|
| **B-REF** Bogoliubov reference on the *same* `k` grid, from the same `c` and `m` | must return `R = 1.000` and `κ = 1.000`. This is the control that voided the first ⁴He run by revealing `k*` lay outside the data range; it is reused unchanged. |
| **XI-CONSISTENCY** two independent routes to `ξ` | `ξ = ħ/(√2 m c)` from the sound speed, and `ξ = 1/√(8π n a_s)` from density and scattering length, must agree to **20 %**. If they disagree, the published parameters are mutually inconsistent and the dataset is unusable — *not* to be patched by choosing whichever `ξ` is convenient. |
| **PHONON** low-`k` sanity | in the measured low-`k` region `ε/(ħk)` must approach `c` to within 10 %, else the quoted `c` does not belong to this dataset. |
| **DIGITISE** (only if a figure is digitised) | two independent digitisations of the same figure; per-point spread must be below 5 % of `ε`, and both must give the same verdict on C1–C3. A verdict that flips between digitisations is not a result. |

## 6. Data

*(empty until a dataset is recorded here with citation, licence, `k` range in units of `k*`, and the
recoverable parameters)*

If no dataset reaches `k ≳ k*`, that is the reported outcome: **DS-QF′ remains untested**, and the
programme says so rather than testing the phonon regime and calling it a confirmation.

## 7. Scope

Snapshot spectra only — no dynamics. Nothing here bears on Navier–Stokes, on ⁴He beyond the already
published comparison, or on the shell-model work. No novelty is claimed for Bogoliubov theory or for
Bragg spectroscopy; the only new object is the ratio `R` and its value.
