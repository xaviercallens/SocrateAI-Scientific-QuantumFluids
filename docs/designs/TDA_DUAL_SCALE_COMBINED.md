# Combining the two probes: does the real-space floor track the Fourier-space floor?

**Date:** 2026-09-20. **Status:** PRE-REGISTRATION. **Audit required before §5 is filled** (E-1).
**Depends on:** CLAIM-024 (dual length, refuted for ⁴He), CLAIM-T2 (TDA floor, split verdict),
`docs/designs/TDA_VORTEX_FLOOR.md`.

---

## 1. Why combining them is worth more than either alone

The programme now has **two dimensionless ratios to the same length `ξ`**, obtained by completely
unrelated means:

| probe | space | quantity | measured so far |
|---|---|---|---|
| dual length | Fourier | `R = min_k ℓ(k)/(√2 ξ)` from the **dispersion** | ⁴He: **0.047** |
| TDA floor | real | `F = (min inter-vortex separation)/ξ` from **persistent homology of a vortex configuration** | Polanco generalised-GP: **0.943** |

They share no instrument, no data, no fitted parameter and no step of reasoning. DS-QF′ makes a
prediction *about the pair*:

> **CDS.** `R` and `F` co-vary across systems. A fluid whose dispersion respects the dual-scale floor
> should also show a real-space vortex floor near `ξ`, and a fluid that violates one should violate the
> other.

That is a much harder claim to satisfy by accident than either half, which is the point of stating it.

## 2. The one point already available, and what is missing

The Polanco dataset is a **roton-bearing generalised (nonlocal) Gross–Pitaevskii** model — deliberately
intermediate between Bogoliubov and ⁴He. Its published parameters are `χ = 0.1`, `γ = 2.8`,
`k_rot ξ = 1.638`.

- Its **`F` is measured**: `0.943` (threshold-free tracing, CLAIM-T2).
- Its **`R` is not**, because the nonlocal model's dispersion relation `ε(k)` is not in this repository.

**Blocking item.** Obtain the analytic dispersion of that model from its source (Polanco/Müller/
Krstulovic and the nonlocal-GP literature: Berloff–Roberts-type kernels). Then `R` follows from the
same code that produced the ⁴He number, and the pair `(R, F)` becomes one point.

This is deliberately *not* attempted by guessing the kernel. A wrong dispersion would produce a
confident, wrong `R`, and the whole value of the combination is that the two sides are independent.

## 3. Pre-registered predictions

- **D1.** For the Polanco model, `R` lies strictly between the Bogoliubov value `1` and the ⁴He value
  `0.047` — it has a roton, so it must violate the floor, but as a weakly-nonlocal GP it should violate
  it far less than ⁴He. Quantitative bracket fixed now: **`0.1 < R < 0.9`**.
- **D2.** Sign agreement: `F` (0.943) sits near 1 while `R` sits below 1, so this single system is
  *already* consistent with CDS only if `R` is at the upper end of D1's bracket. **If `R < 0.3` while
  `F = 0.943`, that is evidence against CDS**, since the two probes would then disagree sharply on the
  same fluid. Recorded now so it cannot be explained away later.
- **D3.** With a second system (a plain local GP, `ξ/Δx ≥ 5`, no roton): expect `R ≈ 1` **and**
  `F ≈ 1`. Both near 1 in the same system would be the first genuine confirmation of CDS.
- **D4.** ⁴He would give `R = 0.047`; its `F` is **not measurable** (`ξ/d = 0.132`, the core is smaller
  than the interatomic spacing — `TDA_VORTEX_FLOOR.md` §T5). So ⁴He supplies one coordinate only, and
  cannot be used as a CDS data point. Stated to prevent it being used as one.

## 4. Controls

| control | requirement |
|---|---|
| **B-REF** (reused) | the Bogoliubov reference must return `R = 1.000` on each system's own `k` grid |
| **TRACE** (reused) | `F` from threshold-free cube-adjacency tracing only; the proximity-segmentation statistic is **not** admissible, having been shown to track its own threshold (CLAIM-T1) |
| **RES** | each system used for `F` must have `ξ/Δx ≥ 5`; the Polanco point (`ξ/Δx = 1.5`) is carried with an explicit caveat and **may not be the sole support** for any CDS conclusion |
| **INDEP** | `R` and `F` must be computed from different files, or different quantities in the same file, with no shared fitted parameter beyond `ξ` itself. `ξ` is shared by construction — that is unavoidable and is exactly why an *error* in `ξ` would correlate the two spuriously, so `ξ` is taken from the authors' own metadata, never fitted here. |

`INDEP` is the control this design most expects to be challenged on: the two probes are only
independent *given* `ξ`. A systematic error in `ξ` moves `R` and `F` in the same direction and could
manufacture CDS. Hence `ξ` must come from published metadata, and any system where it has to be
inferred is excluded.

## 5. Results

*(empty)*

## 6. What each outcome licenses

| outcome | licenses | does not license |
|---|---|---|
| `R` and `F` both near 1 in a weakly interacting system, both low in a correlated one | CDS supported; the dual-scale localisation has two independent witnesses | any claim about Navier–Stokes, or about systems outside the tested range |
| they disagree on the same fluid | **CDS refuted**; the two floors measure different physics, and `DUAL_SCALE_PROPOSAL.md` must say so | discarding either probe individually — each remains valid on its own terms |
| the nonlocal dispersion cannot be obtained | the combination stays at zero data points; reported as blocked, not as pending | any interpolation of `R` from the roton parameters alone |

## 7. Scope

Two-probe correlation only. No dynamics. No novelty claim: persistent homology of vortex tangles has a
literature, and so does Bogoliubov theory; the untested object is the *correlation between the two
ratios*, and even that is a modest claim until there are at least two systems.
