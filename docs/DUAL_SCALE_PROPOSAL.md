# A dual-scale proposal for quantum fluids

**Date:** 2026-09-20. **Status:** consolidated proposal. Every quantitative statement below is either Lean-kernel-checked
(**A**), measured in this repository from Tier-B published data (**B**), or explicitly flagged as open (**C**). Claims:
CLAIM-021, -023, -024. Design memos: `designs/DUAL_SCALE_QUANTUM_FLUID.md`, `designs/DUAL_SCALE_SECOND_INVARIANT.md`.

> **One sentence.** A quantum fluid has a *dual length* `ℓ(k) = ε(k)²/(ħ²c²k³)` whose two limits are the phonon and
> free-particle branches; for a weakly interacting condensate `ℓ = 1/k + k/k*²` exactly, bounded below by `√2 ξ` and
> invariant under `k ↦ k*²/k` — and superfluid ⁴He violates that bound by a factor **21 at saturated vapour pressure,
> rising to 51 at 24 bar**, which localises the dual-scale regime to weak interaction and turns the violation into a
> measurable correlation strength.

---

## 1. What is proposed

The dual-scale idea in this programme has always been the shape `R_eff = R + α′/R ≥ 2√α′`: an effective scale with a
floor. Stated that way it is an analogy. The proposal here replaces it with a **measurable functional of a measured
dispersion**:

```
                       ε(k)²                     1       k                    2mc              ħ
        ℓ(k)  :=  ─────────────── ,     ℓ_B(k) = ─── + ───── ,      k*  :=  ───── ,    √2 ξ = ────
                     ħ² c² k³                     k     k*²                    ħ               mc
```

`ℓ` needs only `ε(k)` (neutron scattering) and `c` (the `k → 0` slope). Its phonon limit is `1/k`; its free-particle
limit is `k/k*²`. For the Bogoliubov dispersion — which is *Pythagorean* in those two branches,
`ε² = (ħck)² + (ħ²k²/2m)²` — the second equality is **exact**, so the `R + α′/R` shape is not an analogy but an identity,
with `R = 1/k` and `α′ = 1/k*²`.

**No string-theory content is claimed.** The shape is AM–GM on two positive terms. The upstream project withdrew its
T-duality framing in 2026-09; this proposal does not reinstate it. What makes the shape worth stating is that it is
falsifiable.

## 2. What is proved [A] — `lean_src/DualLength.lean`, 12 theorems, axioms `{propext, Classical.choice, Quot.sound}`

| theorem | content |
|---|---|
| `dualLength_phonon`, `dualLength_free` | the two limits are exactly `1/k` and `k/k*²` |
| `dualLength_bogoliubov` | `ℓ_B = 1/k + k/k*²` exactly |
| `dual_involutive`, `ell_dual_invariant` | `k ↦ k*²/k` is an involution and `ℓ_B` is invariant under it — it exchanges the phonon and free-particle terms |
| `ell_ge`, `ell_eq_iff` | `ℓ_B ≥ 2/k* = √2 ξ`, **with equality exactly at the self-dual point** `k = k*` |
| `ell_ge_iff_envelope`, `bogoliubov_envelope` | equivalently `ε(k)² ≥ (2ħ²c²/k*) k³`: the dispersion never dips below a **`k^{3/2}` envelope**, tangent at `k*` |
| `dualLength_feynman`, `feynman_ge_iff` | under Feynman's relation `ε_F = ħ²k²/(2mS)`, `ℓ_F = k/(k*²S²)`, and the bound is **exactly** `S(k) ≤ √(k/2k*)` |
| `not_bogoliubov_of_lt`, `not_bogoliubov_of_structure_factor` | **falsification lemmas**: a measured `ℓ < 2/k*`, or a measured `S > √(k/2k*)` together with Feynman's variational inequality, *proves* the dispersion is not Bogoliubov at that `k` |

Negative controls: replacing the floor `2/ks` by `3/ks`, or the structure-factor bound `k/(2ks)` by `k/ks`, makes the file
fail to compile. All 12 theorems were independently re-checked by **Comparator** (Lean kernel + `nanoda`, axiom whitelist).

The third row is the one that turns the proposal into physics: the bound is a statement about the **static structure
factor**, the standard measure of correlation in a liquid, and can therefore be tested by diffraction alone, without any
dispersion measurement.

## 3. What is measured [B] — and it refutes the hypothesis for ⁴He

Data: Godfrin et al. 2021 ancillary tables (Tier B, already in `data/external/`). Controls — Bogoliubov reference
(`k_min/k* = 0.9998`, `ℓ_min/√2ξ = 1.0000`, duality error `2×10⁻⁵`), pure-phonon negative control (endpoint, as required),
and an independent recovery of `c = 238.8 m/s` against the literature `238.3` (0.2 %) — all pass. An earlier run was
**declared void by its own control** because `k*` lay outside that table's range; see §5.0 of the design memo.

**At saturated vapour pressure, full range `k ∈ [0.002, 3.600] Å⁻¹` (1726 points):**

| quantity | DS-QF expects | measured |
|---|---|---|
| interior minimum of `ℓ` | at `k = k*` | **none** — `ℓ` falls across every decade and is still falling at the range edge |
| `ℓ/(√2ξ)` at the roton (`1.92 Å⁻¹`) | `≥ 1` | **0.047** — the roton lies **4.6× below the `k^{3/2}` envelope** |
| `ℓ_min/(√2ξ)` (range edge) | `1` | **0.032** (5.6× below in energy) |
| duality error `max|ℓ(k)/ℓ(k*²/k) − 1|` | `0` | **132 %** |

**Pressure dependence** (7 pressures, roton region; the trend is independent of a common `c` calibration bias):

| P (bar) | 0 | 0.51 | 1.02 | 2.01 | 5.01 | 10.01 | 24.08 |
|---|---|---|---|---|---|---|---|
| `ℓ/(√2ξ)` | 0.0473 | 0.0460 | 0.0453 | 0.0428 | 0.0365 | 0.0304 | 0.0197 |
| `ε/ε_envelope` | 0.218 | 0.214 | 0.213 | 0.207 | 0.191 | 0.174 | **0.140** |
| shortfall in `ℓ` | 21× | 22× | 22× | 23× | 27× | 33× | **51×** |

All four pre-registered predictions (P1–P4) are confirmed; the violation *deepens monotonically* toward the freezing line.

**The physics is textbook and no novelty is claimed for it**: the roton lies far below the weakly-interacting curve
because ⁴He is strongly correlated, and it deepens with pressure. What is new here is only that the statement is
compressed into *one dimensionless number with a Lean-checked meaning*.

## 4. What survives: DS-QF′

> **DS-QF′.** The dual-scale structure is a property of the **weakly interacting** regime, where it is exact, and
> `ℓ(k)/(√2ξ)` — equivalently `S(k)/√(k/2k*)` — is a dimensionless measure of how far a real quantum fluid departs from it.

This is not a retreat to safety: it is sharper than DS-QF, because it predicts *where* the structure should hold and
supplies the number that says how badly it fails where it does not. It is testable, and this repository cannot test it:

- **[C, open] Cold atoms.** In a dilute BEC (`na³ → 0`) Bragg spectroscopy measures `ε(k)` across `k*`. DS-QF′ predicts
  `min_k ℓ/(√2ξ) → 1` as the gas parameter vanishes, with a leading correction of the Lee–Huang–Yang/Beliaev form.
  **The coefficient of that correction is not stated here** — it needs a literature value this repo has not verified.
- **[C, open] Structure factor.** `S(k) ≤ √(k/2k*)` is testable by diffraction alone. At the ⁴He roton the bound requires
  `S ≤ 0.565`. This repo holds **no `S(k)` data**, and the dispersion measurement does *not* by itself imply the `S`
  violation (Feynman's inequality runs the other way: measured `ε` only gives `S ≤ 2.60` there). Stated as an
  independent test, not as a result.

## 5. The dynamical counterpart [A] — what a dual-scale regulator actually buys

The same question in the stream's shell model has a matching answer, and it is a *negative* one worth stating plainly.
Under `w_n = 2^{-n/2}v_n` the complexified truncated dyadic model is a **Hamiltonian second-harmonic-generation chain**
(CLAIM-023, `lean_src/ShellHamiltonian.lean`, 7 theorems, Comparator-checked). Consequences:

- a **second invariant** `H = Σ 2⁻ⁿ[ω_n|v_n|² + k_n Im(conj(v_n)²v_{n+1})]`, conserved for arbitrary real dispersion `ω_n`
  (exact symbolic identity; Lean for the cubic part);
- the Liouville property (CLAIM-011) is a *corollary* of Hamiltonian structure, and energy conservation (CLAIM-007) is
  the Manley–Rowe relation;
- `H ≡ 0` identically on real data — **the phase is what carries the second conservation law**, which is the precise sense
  in which a quantum fluid is the easier laboratory;
- **the σ-rule** (`dispersive_norm_le`): a dispersive regulator of order `k^σ` controls the norm of order `k^{σ-1}`
  uniformly in the cutoff. Quantum pressure has `σ = 2`, so it controls `Σk_n|v_n|²` and **not** the enstrophy. Reaching
  enstrophy would need `σ = 3`.

A deterministic nullspace search (`N = 4,5,6`, both seams, with controls passing) confirms there is **no** invariant of the
pre-registered form "enstrophy + positive quartic": the nullspace is exactly `{mass, mass², H}`. So a Hamiltonian,
volume-preserving, energy-conserving regulator is **not thereby regularising**; the extra ingredient the
Gross–Pitaevskii system has, and this one lacks, is a *positive* interaction energy (CLAIM-022: `Q = Σ_q|A_q|² ≥ 0` for
every truncation).

## 6. Honest summary of status

| | status |
|---|---|
| `ℓ`, its limits, duality, floor, envelope, structure-factor form, falsification lemmas | **proved** [A], Comparator-checked |
| DS-QF for ⁴He | **refuted** [B], quantitatively, at 7 pressures |
| DS-QF′ (weak-coupling regime; `ℓ/√2ξ` as a correlation measure) | **proposed, untested** [C] — needs cold-atom or `S(k)` data |
| LHY/Beliaev correction coefficient | **not stated**; needs a verified literature value |
| σ-rule and the absence of a coercive second invariant in the shell model | **proved** [A] + deterministic search [B] |
| `σ = 3` regulator giving a cutoff-uniform enstrophy bound | **open** [C]; conservation is exact-symbolic, the bound is not yet in Lean |
| novelty of any of the physics | **not claimed**; literature check on Hamiltonian/SHG-chain dyadic models still pending |

## 7. Next steps, in order

1. **Literature check** before any novelty language, on two fronts: complex dyadic / SHG-chain models (§5), and whether
   `ε²/k³` has been used as a diagnostic (§1).
2. **`σ = 3` in Lean**: `2DΩ ≤ H + (2E)^{3/2}`, the first cutoff-uniform enstrophy bound in this stream, then the O5 trap argument.
3. **Cold-atom test of DS-QF′** — the single measurement that would convert §4 from proposal to result.
4. **GE-5** (`docs/GEDANKEN_DUAL_SCALE.md`): echo time as a cutoff-detecting observable, ensemble-only, needs its own pre-registration.

---

## 8. The σ-rule instantiated (2026-09-20) — and a correction to §7's own claim about it

`lean_src/SigmaRule.lean`, 6 theorems, axioms `{propext, Classical.choice, Quot.sound}`, negative
control (claiming `σ = 2` controls enstrophy) fails to compile.

### 8.1 What was proved

On dyadic wavenumbers `k_n = 2ⁿ`, the graded weight `2⁻ⁿ` that makes `H` conserved eats exactly one
dyadic power (`gw_mul_kdy_pow`). Instantiating `dispersive_norm_le`:

| dispersion | controlled quantity | is it the enstrophy? |
|---|---|---|
| `ω_n = D k_n²` (quantum pressure) | `D Σ k_n|v_n|²` | **no** — one power short |
| `ω_n = D k_n³` | `D Σ k_n²|v_n|² = 2DΩ` | **yes** |

So `enstrophy_le_sigma_three`: **`2DΩ ≤ H + √S·S`**, with `H` and `S` conserved — the right-hand side
does not depend on the cutoff `N` except through conserved quantities. That is a genuine
cutoff-uniform enstrophy bound for the `σ = 3` regulator, and `halfNorm_le_sigma_two` states the
`σ = 2` shortfall explicitly rather than by implication.

### 8.2 Correction: this does **not** have the leverage on O5 that §7 claimed

§7 listed the σ-rule as "the one result here that could matter to something unsolved," pointing at
MechanicaFluidorum's O5 uniformity obstruction. **Working the bound out in full shows that overstated
it, and the overstatement is retracted here.**

Dividing through gives `Ω ≤ (H + (2E)^{3/2}) / (2D)`. The constant is **`1/D`**, so the bound
*diverges as `D → 0`* — exactly the failure mode MechanicaFluidorum's own Q1 adjudication
(2026-09-10) identified when it discarded the smooth Helmholtz filter: *"every bound derived would
carry a `1/α'` constant. When we attempt the Millennium limit `α' → 0`, those bounds explode, proving
absolutely nothing."* Their Q2 then retired that whole work package. **That verdict applies to this
result, and is not contested.**

The distinction worth keeping separate, because conflating the two is O5's whole subject:

| limit | does the bound survive? |
|---|---|
| cutoff `N → ∞` at fixed `D` | **yes** — this is what is proved |
| regulator removal `D → 0` | **no** — the constant is `1/D` |

A Millennium-relevant statement needs both. So the honest value of §8.1 is **illustrative, not
progressive**: it exhibits concretely what "cutoff-uniform at fixed regulator strength" looks like,
and why that is not enough — in a model small enough that the whole thing is machine-checked. It is
not a step toward the Millennium problem, and it should not be sent to MechanicaFluidorum as one.

### 8.3 No conflict with Katz–Pavlović

For `D > 0` the term `−i D k_n³ v_n` takes real data out of the reals immediately, and on real data
the cubic part of `H` vanishes identically (`ShellHamiltonian.T_real`). Real Katz–Pavlović blow-up
solutions are therefore not solutions of this system at all, so no contradiction with the published
blow-up theorem is implied. This was the O5 trap flagged in `GEDANKEN_DUAL_SCALE.md` step 2; it does
not fire.

## 9. Bridge to the OpenAI Navier–Stokes formalisation

`lean_src/MadelungNSE.lean` imports `NavierStokes.ProblemStatement` from
`openai/NavierStokesAndEuler @ 8937a8f` (Apache-2.0) — possible only because the 2026-09-19 toolchain
migration put both trees on Lean 4.34.0-rc2 and Mathlib `85e3a25`. The pinned commit is the one whose
four headline theorems MechanicaFluidorum audited.

Proved in *their* vocabulary: `divergence_pressureGradient` — the divergence of their
`pressureGradient` is the scalar Laplacian, `∇·(∇φ) = Δφ`. They never needed it (pressure enters their
residual only as a gradient), so it is genuinely added, and it is the identity that lets the Madelung
continuity equation be written in their formalism. `divergence_madelungVelocity` then gives
`∇·u = (ħ/m)ΔS` for `u = (ħ/m)∇S`.

Scope: kinematics only. No dynamics, no Gross–Pitaevskii equation, no claim touching their blow-up
theorems or Navier–Stokes regularity. Second differentiability of the phase is a genuine hypothesis
and is exactly what fails on a vortex line.
