# Independent verification of `TorusBound.lean`

Subject: `exploration/exciton/lean/TorusBound.lean` (706 lines, sha256
`977524f72f398469c74da85aaa698832169dc95f6b57c178fb2e544cfaa41f57`; re-hashed at the end of the
verification, unchanged).
Date: 2026-10-11.

**Who verified.** A separate instance of the same model family as the producer (Claude Sonnet 5.5),
started with no shared context. This is a machine-assisted independent check, **not human review**, and it
is **not a refereeing of the upstream theorem** (see section 9).

## 0. Verdict

**VERIFIED WITH REMARKS.**

* The file compiles (exit 0, 0 errors, 24 lint/deprecation warnings, no `sorry`); all five named theorems
  depend only on `propext`, `Classical.choice`, `Quot.sound`; no forbidden token occurs.
* The 55-line block of definitions copied from upstream is **line-for-line identical** to upstream
  (and definitionally equal to it, machine-checked by `rfl` against a renamed copy of upstream's file; the
  check has detection power, shown by a mutation control).
* `UniversalEnergyLowerBound` is exactly the first conjunct of upstream's `universal_energy_minimum`
  (machine-checked by `Iff.rfl` and by deriving it from upstream's statement).
* The five theorems say what the docstrings say. Their hypotheses are jointly satisfiable
  (Lean examples with N = 1, N = 2 and density 2), and they are not decorative (numerical controls show the
  conclusion is false without `hsep` or with a wrong covolume).
* Everything is **conditional** on `UniversalEnergyLowerBound`, which I did not and could not verify.

Remarks (none blocking): section 10.

## 1. Environment and commands

```
export ELAN_HOME=/mnt/data/home/xavkal/.elan
cd /mnt/data/xdev-cache/lean-env/qfenv
lake env lean --version
  -> Lean (version 4.34.1, x86_64-unknown-linux-gnu, commit 5045d0056413266e57c625dcd7c365b10e377c52, Release)
cat lean-toolchain            -> leanprover/lean4:v4.34.1
lake-manifest.json (mathlib)  -> rev d13f23b723b8a846827a245b89c10fc7d3f11612, inputRev v4.34.1
nice -n 3 lake env lean /mnt/data/xdev-cache/lean-env/verify2/TorusBound_copy.lean        # main compile
nice -n 3 lake env lean -DautoImplicit=false -DrelaxedAutoImplicit=false <same copy>       # no auto-bound
nice -n 3 lake env lean /mnt/data/xdev-cache/lean-env/verify2/work/Fidelity.lean           # upstream vs file
nice -n 3 lake env lean /mnt/data/xdev-cache/lean-env/verify2/work/FidelityControl.lean    # mutation control
nice -n 3 lake env lean /mnt/data/xdev-cache/lean-env/verify2/work/NonVacuity3.lean        # non-vacuity
```

The copy was byte-identical to the original (same sha256). No `lake update`, no `rm`, no `mv`; nothing
written in the repo except this report. All scratch files and logs are in
`/mnt/data/xdev-cache/lean-env/verify2/` (`work/*.lean`, `work/*.log`, `upstream/`, `py/`).

Upstream (fetched by me with `curl` from `raw.githubusercontent.com`, not reusing anyone's download):

* `openai/math` HEAD at fetch time: `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`
  (merge of PR #1 "Update manuscripts and Lean formalizations", 2026-10-08).
* `lean/ComparatorChallenges/TriangularEnergy.lean`: 74 lines, 2500 bytes, sha256
  `af51979c7baecd3e9852637bbba29eff96cbb09cec84e15eff7d686f1a770616`; identical content on `main` and at
  `fd4aeeb`; the only commit touching this path is `adc7f1241b42e322a6451854ab7e4b4c146bf78a`
  ("Initial commit", 2026-10-06).
* It is a *challenge file*: the definitions plus `theorem universal_energy_minimum ... := by sorry`.
  `TriangularEnergy.json`: solution module `OAI.Analysis.Triangular.Energy.Universal`, theorem
  `OAI.AtomicTriangular.universal_energy_minimum`, permitted axioms {propext, Quot.sound, Classical.choice}.
* Upstream pin: `lean/lean-toolchain` = `leanprover/lean4:v4.34.1`; `lean/lake-manifest.json` Mathlib rev
  `d13f23b7...` = the rev of the environment used here. The file was therefore compiled against exactly
  upstream's pin, as its docstring says.

## 2. Task 1: compile, axioms, forbidden tokens

| Item | Result |
|---|---|
| Exit code | 0 |
| Wall time | 29 s (warm Mathlib oleans; load average 7.6 at start; `nice -n 3`) |
| Errors | 0 |
| `declaration uses sorry` | 0 |
| Warnings | 24 (all lints, see below) |
| `-DautoImplicit=false -DrelaxedAutoImplicit=false` | exit 0, 37 s, same 24 warnings, same axioms (no accidentally auto-bound variable in any statement) |
| `periodic_universal_lower_bound` axioms | propext, Classical.choice, Quot.sound |
| `torus_lower_bound_unit` axioms | propext, Classical.choice, Quot.sound |
| `torus_lower_bound` axioms | propext, Classical.choice, Quot.sound |
| `torus_energy_per_particle` axioms | propext, Classical.choice, Quot.sound |
| `admissible_comp_div` axioms | propext, Classical.choice, Quot.sound |

Warnings (24): 19 deprecations (7 `Set.mem_setOf_eq`, 4 `if_pos`, 4 `if_neg`, 3 `dif_pos`, 1 `dif_neg`),
3 unused simp arguments (lines 315, 369, 369), 2 unused automatically-included section variables
(`finite_lattice_inter_closedBall`: `[IsZLattice ℝ L]`; `orbit_inter_ball`: `[DiscreteTopology L]`,
`[IsZLattice ℝ L]`). None affects meaning; the deprecations will need renaming on a later Mathlib.

Forbidden-token grep on the original file (case-sensitive, comments included):
`sorry` 0, `native_decide` 0, `axiom` 0 (the only hits are the five `#print axioms` commands),
`unsafe` 0, `opaque` 0, `implemented_by` 0, `set_option` 0, `decide :=` 0, `admit` 0, `extern` 0,
`partial` 0, `attribute` 0, `instance` 0, `macro`/`syntax`/`notation`/`elab` 0, `private` 0.
`noncomputable section` occurs once (upstream's own).

## 3. Task 2a: definition-by-definition comparison with upstream

Procedure: (i) textual diff of the block `namespace TriangularUniversal ... def latticeEnergy`
(TorusBound.lean lines 51-105 against upstream lines 9-63), whitespace included:
**identical, 0 differing lines** (55 lines each); (ii) machine check: a combined file with upstream's
challenge file (namespace `OAI` renamed `OAIup`, theorem left as `sorry`) followed by the TorusBound file,
then `rfl` between corresponding constants (`work/Fidelity.lean`, exit 0).

| Entity | TorusBound.lean | Text vs upstream | `rfl` vs upstream |
|---|---|---|---|
| `TriangularUniversal.Plane` (abbrev `EuclideanSpace ℝ (Fin 2)`) | 53 | identical | ok |
| `LocallyFinite` | 55-56 | identical | ok |
| `diskPoints` (`if h : (C ∩ closedBall 0 R).Finite then h.toFinset else ∅`) | 58-59 | identical | ok |
| `diskCount` | 61 | identical | ok |
| `DensityOne` (`Tendsto (diskCount/(π R²)) atTop (𝓝 1)`) | 63-65 | identical | ok |
| `AdmissiblePotential` (`ContDiffOn ℝ (⊤ : ℕ∞) g (Ioi 0)`, `0 ≤ g t`, `0 ≤ (-1)^r iteratedDeriv r g t`) | 67-70 | identical | ok |
| `diskEnergy` (`(count)⁻¹ * ∑ x, ∑ y ∈ erase x, ofReal (g (‖x-y‖^2))`) | 72-75 | identical | ok |
| `energy` (`Filter.liminf (diskEnergy g C) atTop`) | 77-78 | identical | ok |
| `AtomicTriangular.Plane` | 84 | identical | ok |
| `b := √3 / 2` | 86 | identical | ok |
| `triangularPoint` (`(√b)⁻¹ • (single 0 (j+k/2) + single 1 (k b))`) | 88-91 | identical | ok |
| `A := Set.range triangularPoint` | 93 | identical | ok |
| `abbrev` x7 (`LocallyFinite`, `diskPoints`, `diskCount`, `DensityOne`, `AdmissiblePotential`, `diskEnergy`, `energy`) | 95-101 | identical | ok (3 spot-checked) |
| `latticeEnergy` (`∑' a : {x // x ∈ A ∧ x ≠ 0}, ofReal (g (‖a‖^2))`, with its docstring) | 103-105 | identical | ok |

Differences outside the verbatim block (the only ones):

1. TorusBound.lean has, before `namespace OAI`, the extra lines `open Filter Topology` and
   `open scoped ENNReal` (upstream has no top-level opens). Inside `noncomputable section` both files have
   the same two lines `open scoped BigOperators Topology ENNReal` and `open Classical Filter` (TorusBound
   lines 48-49). The extra opens only affect the file's own new theorems, not the copied definitions
   (the `rfl` checks pass, so the copied definitions elaborate to the same terms).
2. Upstream's `theorem universal_energy_minimum` is absent (replaced by `def UniversalEnergyLowerBound`,
   task 2b).
3. A module docstring and the new `TorusBound` namespace.

`atTop`, `𝓝`, `ℝ≥0∞`, `ENNReal.ofReal`, `⁻¹` (ENNReal inverse, `0⁻¹ = ∞`), `liminf` and the
"toFinset-else-empty" convention are all the same terms as upstream.

**Mutation control (does the `rfl` check have teeth?).** In a copy of the block I injected five one-token
mutations (drop `.erase x`; drop `π` in `DensityOne`; drop `^2` in `latticeEnergy`; drop the sign
`(-1)^r`; `b := √3/3`). `work/FidelityControl.lean` then failed (as it should) on exactly the eight
dependent constants (`DensityOne`, `AdmissiblePotential`, `diskEnergy`, `energy`, `b`,
`triangularPoint`, `A`, `latticeEnergy`) and passed on the four untouched ones. So the passing check for the
real file is meaningful.

## 4. Task 2b: `UniversalEnergyLowerBound` against the first conjunct

Upstream: `theorem universal_energy_minimum (g : ℝ → ℝ) (C : Set Plane) (hg : AdmissiblePotential g)
(hC : LocallyFinite C) (hd : DensityOne C) : latticeEnergy g ≤ energy g C ∧ latticeEnergy g = energy g A`.

File: `def UniversalEnergyLowerBound : Prop := ∀ g C, AdmissiblePotential g → LocallyFinite C →
DensityOne C → latticeEnergy g ≤ energy g C` (same quantifiers, same hypothesis order, same types; the
`Plane`s and predicates are `abbrev`s of the `TriangularUniversal` ones).

Machine-checked in `work/Fidelity.lean` (appended after upstream's statement):

```lean
example : OAI.UniversalEnergyLowerBound ↔
    ∀ (g : ℝ → ℝ) (C : Set OAIup.AtomicTriangular.Plane),
      OAIup.AtomicTriangular.AdmissiblePotential g → OAIup.AtomicTriangular.LocallyFinite C →
      OAIup.AtomicTriangular.DensityOne C →
      OAIup.AtomicTriangular.latticeEnergy g ≤ OAIup.AtomicTriangular.energy g C := Iff.rfl
example : OAI.UniversalEnergyLowerBound := by
  intro g C hg hC hd
  exact (OAIup.AtomicTriangular.universal_energy_minimum g C hg hC hd).1
```

Both compile. The hypothesis is therefore exactly the first conjunct, no stronger and no weaker; the
second conjunct (`latticeEnergy g = energy g A`) is not used.

## 5. Task 2c: the new definitions

| Definition | Lean | Meaning | Matches docstring? |
|---|---|---|---|
| `orbit Λ v` | `(fun m => v + m) '' (Λ : Set Plane)` | the coset `v + Λ` | yes |
| `cfg Λ x` | `⋃ i : Fin N, orbit Λ (x i)` | union of the N cosets `x i + Λ`: the Λ-periodic configuration generated by N points | yes |
| `pointEnergy g C p` | `∑' q : Plane, indicator {q | q ∈ C ∧ q ≠ p} (fun q => ofReal (g (‖p - q‖^2))) q` | `∑_{q ∈ C, q ≠ p} g(‖p-q‖²)` in `[0,∞]`: interaction of `p` with every other point of `C`, own periodic images included, ordered-pair convention | yes |
| `smulSet s C` | `(fun p => s • p) '' C` | the dilated set `sC` | yes |

Remarks. `tsum` in `ℝ≥0∞` is the unconditional supremum of finite partial sums, so there is no
summability proviso and an uncountable index type is harmless (the support is countable anyway).
`cfg` is a `Set`, so multiplicities are not recorded; this is harmless exactly under `hsep`, which makes the
N cosets pairwise disjoint (`orbit_disjoint`) and the translation `m ↦ v + m` is injective. The point
`x i` belongs to `cfg` and is excluded from its own sum by `q ≠ p`, while its images `x i + m`, `m ≠ 0`,
are included. This is the standard periodic-image (Ewald-type) convention, not the minimum-image one.

## 6. Task 2d: the five theorems in plain language

Notation: `P = ℝ²` with the Euclidean norm; `A` is the triangular lattice of density 1 (one point per
unit area, checked numerically: count/(πR²) = 0.993 at R = 10, 1.003 at R = 20);
`latticeEnergy g = ∑_{a ∈ A, a ≠ 0} g(|a|²)` in `[0,∞]`; "admissible" means: `g` is C^∞ on `(0,∞)`,
`g ≥ 0` there and `(-1)^r g^{(r)} ≥ 0` there for all `r` (completely monotone in `t = distance²`).

1. **`admissible_comp_div`.** If `g` is admissible and `ρ > 0`, then `t ↦ g(t/ρ)` is admissible.
   Lean statement: exactly that. (Mathematically true: `(-1)^r (d/dt)^r g(t/ρ) = ρ^{-r} (-1)^r g^{(r)}(t/ρ)`.)

2. **`periodic_universal_lower_bound`.** *Assume hUO.* Let `N ≥ 1`, `Λ ⊂ P` an additive subgroup,
   `x_0..x_{N-1}` pairwise inequivalent modulo `Λ`, each coset `x_i + Λ` having finite intersection with
   every closed disc, and each coset of asymptotic density `1/N`
   (`|(x_i+Λ) ∩ B(0,R)| / (πR²) → 1/N`). Then for every admissible `g`:
   `latticeEnergy g ≤ (1/N) ∑_i ∑_{q ∈ C∖{x_i}} g(|x_i - q|²)`, `C = ⋃_i (x_i + Λ)`.
   Lean statement: exactly that.

3. **`torus_lower_bound_unit`.** *Assume hUO.* Let `L ⊂ P` be a discrete full-rank `ℤ`-lattice with
   `covolume L = N`, `N ≥ 1`, and `x_0..x_{N-1}` pairwise inequivalent modulo `L`. Then for every admissible
   `g`: `latticeEnergy g ≤ (1/N) ∑_i pointEnergy g (cfg L x) (x_i)`: N points per cell of area N, i.e.
   unit density, periodic images included. Lean statement: exactly that (`ZLattice.covolume L` is taken
   with respect to `MeasureTheory.volume`, confirmed from the elaborated type, and `covolume ℤ² = 1`
   is proved in section 7).

4. **`torus_lower_bound`.** Same with `covolume L * ρ = N`, `ρ > 0`, conclusion
   `latticeEnergy (fun t => g (t/ρ)) ≤ (1/N) ∑_i pointEnergy g (cfg L x) (x_i)`: the triangular lattice of
   density `ρ` (energy `∑ g(|a|²/ρ)`) is a lower bound for the periodic energy of N points per cell at
   density `ρ`. Lean statement: exactly that. Consistency of the scaling checked by hand and numerically
   (section 8, ii).

5. **`torus_energy_per_particle`.** Both sides of (4) multiplied by `1/2`:
   `(1/2) latticeEnergy (g(·/ρ)) ≤ (1/N) ((1/2) ∑_i pointEnergy ...)`, the physical energy per particle with
   each unordered pair counted once. Lean statement: that; the "unordered pairs" reading is an
   interpretation of the factor `1/2` (standard), not something encoded in the statement.

Hypotheses:

* `hsep` (`x i - x j ∉ L` for `i ≠ j`): the right one; without it two classes coincide on the torus
  (not covered by the admissible class: `g 0` undefined), and the conclusion would be **false** (numerical
  control, section 8).
* `covolume L = N` (or `covolume L * ρ = N`): the right one (N particles per cell, density `N/covol`);
  with a wrong value the conclusion is false (section 8).
* `0 < N`: needed for `1/N` and `Fin N` non-empty; for `N = 0` the covolume hypothesis would already be
  inconsistent (`covolume > 0`).
* `[DiscreteTopology L] [IsZLattice ℝ L]`: Mathlib's lattice hypotheses; satisfiable (section 7).
* `hρ : 0 < ρ` is redundant (follows from `hcov` and `hN` since `covolume > 0`), harmless.
* In `periodic_universal_lower_bound`, `hfin` is implied by `hcnt` (an infinite class in a ball would
  give `diskCount = 0` for all larger radii, contradicting density `1/N > 0`) but is stated separately;
  harmless, and discharged by `orbit_finite` in the lattice theorems.

## 7. Task 3: non-vacuity (Lean, compiled)

Appended to a full copy of the file (`work/NonVacuity3.lean`); exit 0, 0 errors, 0 `sorry`; every new
theorem depends only on {propext, Classical.choice, Quot.sound}. `hUO` stays an explicit hypothesis (it
cannot be discharged). What is shown: all non-`hUO` hypotheses of the real theorems hold for concrete data,
with the real instances found by `inferInstance`.

Results:

* `covol_L1 : ZLattice.covolume L1 = 1` for `L1 = span ℤ (range (basisFun (Fin 2) ℝ))` (ℤ²).
* `covol_L2 : ZLattice.covolume L2 = 2` for `L2 = span ℤ {(2,0), (0,1)}`.
* `nv_unit_N1`: `torus_lower_bound_unit` applied with `L1`, `N = 1`, `x = 0` (`hsep` vacuous).
* `nv_unit_N2`: `torus_lower_bound_unit` applied with `L2`, `N = 2`, `x = (0, (1,0))`, `hsep` proved
  (`±(1,0) ∉ L2`, because `2 c = ±1` has no integer solution).
* `nv_rho2`: `torus_lower_bound` applied with `L1`, `N = 2`, `ρ = 2` (covolume 1 times 2 = 2),
  `x = (0, (1/2,1/2))`, `hsep` proved.
* `adm_exp`: `fun t => exp (-t)` is `AdmissiblePotential`; `adm_zero`: the zero potential too.
* Non-triviality of the conclusion for `g = exp(-t)`, `L1`, `N = 1`: `pe_exp_ne_top` shows
  `pointEnergy g (cfg ℤ² {0}) 0 ≠ ⊤` (via Mathlib's `ZLattice.summable_norm_zpow`, bound
  `exp(-r²) ≤ r⁻³`) and `latticeEnergy_exp_pos` shows `0 < latticeEnergy g`. So the instance of the
  theorem is a genuine inequality between a positive number and a finite number
  (`0 < latticeEnergy ≤ pointEnergy < ∞`), not `x ≤ ∞`. Numerically `2.14180 ≤ 2.14224`.

The compiled code (the part of `work/NonVacuity3.lean` after the original file; the first compile attempt
failed only because my `L1` was a `def` instead of an `abbrev`, a defect of my scaffolding, fixed):

```lean
open OAI OAI.TorusBound
open scoped ENNReal

namespace VerifierNV

abbrev P := OAI.TriangularUniversal.Plane

noncomputable abbrev b0 : Module.Basis (Fin 2) ℝ P := (EuclideanSpace.basisFun (Fin 2) ℝ).toBasis
noncomputable abbrev L1 : Submodule ℤ P := Submodule.span ℤ (Set.range b0)

example : DiscreteTopology L1 := inferInstance
example : IsZLattice ℝ L1 := inferInstance

theorem vol_fd_b0 : MeasureTheory.volume.real (ZSpan.fundamentalDomain b0) = 1 := by
  rw [MeasureTheory.measureReal_def,
    MeasureTheory.measure_congr (ZSpan.fundamentalDomain_ae_parallelepiped b0 MeasureTheory.volume)]
  have h := (EuclideanSpace.basisFun (Fin 2) ℝ).volume_parallelepiped
  have h' : MeasureTheory.volume (parallelepiped (⇑b0)) = 1 := by
    simpa [b0] using h
  rw [h']; simp

theorem covol_L1 : ZLattice.covolume L1 = 1 := by
  rw [ZLattice.covolume_eq_measure_fundamentalDomain L1 MeasureTheory.volume
    (ZSpan.isAddFundamentalDomain b0 MeasureTheory.volume)]
  exact vol_fd_b0

theorem nv_unit_N1 (hUO : UniversalEnergyLowerBound) {g : ℝ → ℝ}
    (hg : TriangularUniversal.AdmissiblePotential g) :
    AtomicTriangular.latticeEnergy g ≤ ((1 : ℕ) : ℝ≥0∞)⁻¹ *
      ∑ i : Fin 1, pointEnergy g (cfg L1.toAddSubgroup (fun _ : Fin 1 => (0 : P)))
        ((fun _ : Fin 1 => (0 : P)) i) :=
  torus_lower_bound_unit L1 hUO (N := 1) Nat.one_pos (by rw [covol_L1]; norm_num)
    (fun _ => 0) (fun i j hij => absurd (Subsingleton.elim i j) hij) hg

noncomputable def w2 : Fin 2 → ℝˣ := ![Units.mk0 2 two_ne_zero, 1]
noncomputable abbrev b2 : Module.Basis (Fin 2) ℝ P := b0.unitsSMul w2
noncomputable abbrev L2 : Submodule ℤ P := Submodule.span ℤ (Set.range b2)

example : DiscreteTopology L2 := inferInstance
example : IsZLattice ℝ L2 := inferInstance

theorem covol_L2 : ZLattice.covolume L2 = 2 := by
  rw [ZLattice.covolume_eq_measure_fundamentalDomain L2 MeasureTheory.volume
    (ZSpan.isAddFundamentalDomain b2 MeasureTheory.volume),
    ZSpan.measureReal_fundamentalDomain b2 MeasureTheory.volume b0, vol_fd_b0]
  have hdet : b0.det b2 = 2 := by
    rw [Module.Basis.det_apply, b2, Module.Basis.toMatrix_unitsSMul]
    simp [Matrix.det_diagonal, Fin.prod_univ_two, w2]
  rw [hdet]; norm_num

noncomputable def e0 : P := EuclideanSpace.single (0 : Fin 2) (1 : ℝ)

theorem e0_not_mem_L2 : e0 ∉ L2 := by
  intro h
  rw [L2, Submodule.mem_span_range_iff_exists_fun] at h
  obtain ⟨c, hc⟩ := h
  have h0 := congrArg (fun v : P => v 0) hc
  simp [Fin.sum_univ_two, b2, b0, w2, Module.Basis.unitsSMul_apply, e0] at h0
  have h2 : (2 * c 0 : ℤ) = 1 := by
    have : (2 * (c 0 : ℝ)) = 1 := by linarith
    exact_mod_cast this
  omega

theorem neg_e0_not_mem_L2 : -e0 ∉ L2 := fun h => e0_not_mem_L2 (by simpa using L2.neg_mem h)

noncomputable def x2 : Fin 2 → P := ![0, e0]

theorem hsep_x2 : ∀ i j : Fin 2, i ≠ j → x2 i - x2 j ∉ L2 := by
  intro i j hij
  fin_cases i <;> fin_cases j
  · exact absurd rfl hij
  · simpa [x2] using neg_e0_not_mem_L2
  · simpa [x2] using e0_not_mem_L2
  · exact absurd rfl hij

theorem nv_unit_N2 (hUO : UniversalEnergyLowerBound) {g : ℝ → ℝ}
    (hg : TriangularUniversal.AdmissiblePotential g) :
    AtomicTriangular.latticeEnergy g ≤ ((2 : ℕ) : ℝ≥0∞)⁻¹ *
      ∑ i : Fin 2, pointEnergy g (cfg L2.toAddSubgroup x2) (x2 i) :=
  torus_lower_bound_unit L2 hUO (N := 2) (by norm_num) (by rw [covol_L2]; norm_num) x2 hsep_x2 hg

noncomputable def h2pt : P := EuclideanSpace.single (0 : Fin 2) (1 / 2 : ℝ) +
  EuclideanSpace.single (1 : Fin 2) (1 / 2 : ℝ)

theorem h2pt_not_mem_L1 : h2pt ∉ L1 := by
  intro h
  rw [L1, Submodule.mem_span_range_iff_exists_fun] at h
  obtain ⟨c, hc⟩ := h
  have h0 := congrArg (fun v : P => v 0) hc
  simp [Fin.sum_univ_two, b0, h2pt] at h0
  have h2 : (2 * c 0 : ℤ) = 1 := by
    have : (2 * (c 0 : ℝ)) = 1 := by linarith
    exact_mod_cast this
  omega

theorem neg_h2pt_not_mem_L1 : -h2pt ∉ L1 := fun h => h2pt_not_mem_L1 (by simpa using L1.neg_mem h)

noncomputable def x3 : Fin 2 → P := ![0, h2pt]

theorem hsep_x3 : ∀ i j : Fin 2, i ≠ j → x3 i - x3 j ∉ L1 := by
  intro i j hij
  fin_cases i <;> fin_cases j
  · exact absurd rfl hij
  · simpa [x3] using neg_h2pt_not_mem_L1
  · simpa [x3] using h2pt_not_mem_L1
  · exact absurd rfl hij

theorem nv_rho2 (hUO : UniversalEnergyLowerBound) {g : ℝ → ℝ}
    (hg : TriangularUniversal.AdmissiblePotential g) :
    AtomicTriangular.latticeEnergy (fun t => g (t / 2)) ≤ ((2 : ℕ) : ℝ≥0∞)⁻¹ *
      ∑ i : Fin 2, pointEnergy g (cfg L1.toAddSubgroup x3) (x3 i) :=
  torus_lower_bound L1 hUO (N := 2) (by norm_num) (ρ := 2) (by norm_num)
    (by rw [covol_L1]; norm_num) x3 hsep_x3 hg

theorem adm_exp : TriangularUniversal.AdmissiblePotential (fun t : ℝ => Real.exp (-t)) := by
  refine ⟨?_, fun t _ => (Real.exp_pos _).le, ?_⟩
  · exact (Real.contDiff_exp.comp contDiff_neg).contDiffOn
  · intro r t ht
    have h1 : iteratedDeriv r (fun t : ℝ => Real.exp (-t)) = fun t => (-1 : ℝ) ^ r * Real.exp (-t) := by
      have := iteratedDeriv_exp_const_mul r (-1 : ℝ)
      simpa using this
    rw [h1]
    have : (-1 : ℝ) ^ r * ((-1 : ℝ) ^ r * Real.exp (-t)) = Real.exp (-t) := by
      rw [← mul_assoc, ← mul_pow]; simp
    rw [this]; exact (Real.exp_pos _).le

theorem adm_zero : TriangularUniversal.AdmissiblePotential (fun _ : ℝ => (0 : ℝ)) := by
  refine ⟨?_, fun t _ => le_rfl, ?_⟩
  · exact (contDiff_const (𝕜 := ℝ) (c := (0 : ℝ))).contDiffOn
  · intro r t ht
    have h0 : iteratedDeriv r (fun _ : ℝ => (0 : ℝ)) t = 0 := by
      cases r with
      | zero => simp
      | succ n => simp [iteratedDeriv_succ]
    rw [h0]; simp

theorem pe_exp_ne_top :
    pointEnergy (fun t : ℝ => Real.exp (-t)) (cfg L1.toAddSubgroup (fun _ : Fin 1 => (0 : P))) 0 ≠ ⊤ := by
  have hcfg : cfg L1.toAddSubgroup (fun _ : Fin 1 => (0 : P)) = (L1 : Set P) := by
    ext q
    simp [cfg, orbit]
  unfold pointEnergy
  rw [hcfg]
  set S : Set P := {q : P | q ∈ (L1 : Set P) ∧ q ≠ 0} with hS
  set f : P → ℝ≥0∞ := fun q => ENNReal.ofReal (Real.exp (-(‖(0 : P) - q‖ ^ 2))) with hf
  change ∑' q : P, Set.indicator S f q ≠ ⊤
  have h1 : (∑' q : P, Set.indicator S f q) = ∑' q : S, f q := (tsum_subtype S f).symm
  have hrank : Module.finrank ℤ L1 = 2 := by
    rw [ZLattice.rank ℝ L1, finrank_euclideanSpace_fin]
  have hsum : Summable (fun z : L1 => ‖(z : P)‖ ^ (-3 : ℤ)) :=
    ZLattice.summable_norm_zpow (L := L1) (-3) (by rw [hrank]; norm_num)
  have hne : (∑' z : L1, ENNReal.ofReal (‖(z : P)‖ ^ (-3 : ℤ))) ≠ ⊤ := by
    rw [← ENNReal.ofReal_tsum_of_nonneg (fun z => by positivity) hsum]
    exact ENNReal.ofReal_ne_top
  let ι : S → L1 := fun q => ⟨q.1, q.2.1⟩
  have hι : Function.Injective ι := fun a b h => Subtype.ext (congrArg (fun z : L1 => (z : P)) h)
  have hterm : ∀ q : S, f q ≤ ENNReal.ofReal (‖(ι q : P)‖ ^ (-3 : ℤ)) := by
    intro q
    apply ENNReal.ofReal_le_ofReal
    have hq0 : (q : P) ≠ 0 := q.2.2
    have hr : 0 < ‖(q : P)‖ := norm_pos_iff.2 hq0
    set r := ‖(q : P)‖ with hrdef
    have h0 : ‖(0 : P) - q‖ = r := by simp [hrdef]
    rw [h0]
    have hexp : r ^ 3 ≤ Real.exp (r ^ 2) := by
      have := Real.quadratic_le_exp_of_nonneg (sq_nonneg r)
      nlinarith [sq_nonneg (r * (1 - r)), sq_nonneg r, sq_nonneg (r ^ 2)]
    have hpos3 : 0 < r ^ 3 := pow_pos hr 3
    show Real.exp (-(r ^ 2)) ≤ r ^ (-3 : ℤ)
    rw [zpow_neg, show (3 : ℤ) = ((3 : ℕ) : ℤ) from rfl, zpow_natCast, Real.exp_neg]
    exact inv_anti₀ hpos3 hexp
  have hle : ∑' q : S, f q ≤ ∑' z : L1, ENNReal.ofReal (‖(z : P)‖ ^ (-3 : ℤ)) := by
    calc ∑' q : S, f q ≤ ∑' q : S, ENNReal.ofReal (‖(ι q : P)‖ ^ (-3 : ℤ)) :=
          ENNReal.tsum_le_tsum hterm
      _ ≤ _ := ENNReal.tsum_comp_le_tsum_of_injective hι
          (fun z : L1 => ENNReal.ofReal (‖(z : P)‖ ^ (-3 : ℤ)))
  rw [h1]
  exact ne_top_of_le_ne_top hne hle

theorem latticeEnergy_exp_pos : 0 < AtomicTriangular.latticeEnergy (fun t : ℝ => Real.exp (-t)) := by
  unfold AtomicTriangular.latticeEnergy
  have hne : AtomicTriangular.triangularPoint (1, 0) ≠ 0 := by
    intro h
    have h0 := congrArg (fun v : P => v 0) h
    have hb : 0 < AtomicTriangular.b := by
      unfold AtomicTriangular.b; positivity
    have hsb : 0 < Real.sqrt AtomicTriangular.b := Real.sqrt_pos.2 hb
    simp [AtomicTriangular.triangularPoint] at h0
    exact (ne_of_gt hsb) (by simpa using h0)
  let a : {x : P // x ∈ AtomicTriangular.A ∧ x ≠ 0} :=
    ⟨AtomicTriangular.triangularPoint (1, 0), ⟨⟨(1, 0), rfl⟩, hne⟩⟩
  refine lt_of_lt_of_le ?_ (ENNReal.le_tsum a)
  exact ENNReal.ofReal_pos.2 (Real.exp_pos _)

end VerifierNV
```

Elaborated statements (from `#check @...` in the same run), confirming the printed types:
`torus_lower_bound_unit : ∀ (L : Submodule ℤ Plane) [DiscreteTopology ↥L] [IsZLattice ℝ L],
UniversalEnergyLowerBound → ∀ {N : ℕ}, 0 < N → ZLattice.covolume L MeasureTheory.volume = ↑N →
∀ (x : Fin N → Plane), (∀ i j, i ≠ j → x i - x j ∉ L) → ∀ {g}, AdmissiblePotential g →
latticeEnergy g ≤ (↑N)⁻¹ * ∑ i, pointEnergy g (cfg L.toAddSubgroup x) (x i)`;
`torus_lower_bound` has `ZLattice.covolume L volume * ρ = ↑N` and `latticeEnergy fun t => g (t / ρ)`.

## 8. Task 4: attempts to break it

**(i) `hcnt` (density `1/N` per class).** In `periodic_universal_lower_bound` it is a hypothesis, used
only through `tendsto_ratio` to get `DensityOne (cfg Λ x)` (the class counts add up because the orbits are
disjoint under `hsep`; `∑ 1/N = 1`) and `count_i / count → 1/N` in `ℝ≥0∞`. It is *derived*, not assumed, in
`torus_lower_bound_unit`: lines 599-602 apply `orbit_density_tendsto L (x i)`, which gives
`count_i(R)/(πR²) → 1/covolume L` (squeeze between the counts of `L ∩ B(R ± ‖v‖)`, each `~ πR²/covol` by
Mathlib's `ZLattice.covolume.tendsto_card_le_div'`), then `rwa [hcov]`. In `torus_lower_bound` it is derived
for the dilated group (`hcnt'`: `count(R/s)/(π R²) → (1/covol)(1/s²) = 1/(covol ρ) = 1/N`). Outcome: sound.
Checked the ENNReal corner: at radii where `diskCount = 0`, `0⁻¹ = ∞` and `∞ * 0 = 0`, so the inequality
`diskEnergy ≤ ∑ (count_i * count⁻¹) * pointEnergy` is unaffected; `ENNReal.Tendsto.mul_const` is applied
with `a = N⁻¹ ≠ 0` (the `0 * ∞` case is excluded by that side condition), so `pointEnergy = ∞` gives the
trivially true `... ≤ ∞`, not a wrong value.

**(ii) Scaling in `torus_lower_bound`.** By hand: `s = √ρ`; `s·cfg` has density `ρ/s² = 1`; for the
potential `g' = g(·/s²)` one has `g'(|sp - sq|²) = g(|p - q|²)`, so the periodic energy of `s·cfg` under
`g'` equals that of `cfg` under `g` (this is `pointEnergy_smul`), and `hUO`-based bound for `s·cfg` gives
`latticeEnergy g' ≤ energy(cfg, g)` with `g' = g(·/ρ)`; the triangular lattice of density `ρ` is `A/√ρ`, whose
energy is `∑ g(|a|²/ρ)`: consistent. Not a vacuous rescaling: the group is the image `s•L` (`Λ'`), the
points are `s • x i`, `horb` and `hcfg` prove `cfg Λ' x' = s • cfg L x`, `hsep'` is derived by injectivity of
`s•`. Numerical confirmation (independent Python, `py/numcheck*.py`, uses the exact `triangularPoint`
formula): script 1 = 50 (configuration, potential) pairs (ℤ² N=1, 2ℤ×ℤ N=2, ℤ² N=2 at density 2,
2ℤ² at density 1/4, and 6 random lattices with 1-4 random points; potentials `e^{-t}`, `e^{-t/2}`,
`t^{-2}`, `t^{-3}`, `e^{-3t}+t^{-4}`); script 2 = 282 pairs (random lattices, 1-5 random points, the same
potentials plus `e^{-t/10}`, Gauss-reduced basis). No violation of
`latticeEnergy(g(·/ρ)) ≤ periodic energy` survives. The apparent violations that appeared (script 1, one
skewed lattice, ratio 0.998 and 0.968; script 2, three cases at `e^{-t/10}`) were truncation artifacts of
the image sum: with a Gauss-reduced basis (case of script 1) the two sides agree to 6 digits, and the
three script-2 cases agree to 1e-13 at cut-off K ≥ 150.
Control with the wrong convention `g(t·ρ)`: fails for ρ = 1/4 (11.57 > 0.0746).

**Necessity controls (numerical, `g = e^{-t}`, `latticeEnergy g = 2.14180`).**
(a) Without `hsep`: N = 2, both points equal, `L = √2 ℤ²` (covolume 2): the claim would read
`2.14180 ≤ 0.61631`: false. (b) With a wrong covolume: `L = ℤ²`, N = 1 but ρ = 2: `5.28319 ≤ 2.14224`:
false. So these hypotheses carry real content.

**(iii) Does anything assume more than the docstring says?** I looked for hidden assumptions and found
none beyond: the hypotheses `hfin`, `hρ` (redundant, see section 6) and the module's own list. Specific
points checked: `AdmissiblePotential` only constrains `g` on `(0,∞)`, and only values at `‖p-q‖² > 0`
are ever used (`q ≠ p`), so no value of `g` at `0` or negative arguments enters; `ofReal` truncation never
acts (admissible `g ≥ 0` on `(0,∞)`); the else-branch `∅` of `diskPoints` never fires for the
configurations at hand (`hfin`/`orbit_finite` give finiteness for every radius); `ncard` of infinite
sets (= 0) never enters a quantitative step: the counting lemmas are applied to sets proved finite
(`finite_lattice_inter_closedBall`, `finite_shift`), and the one general lemma (`diskCount_eq_ncard`)
treats the infinite case explicitly and consistently with the `else ∅` convention (both give 0);
real division by zero only occurs at radii that are irrelevant for `atTop`; `liminf` is the same as
upstream's; no `Classical` instance mismatch (same `open Classical` as upstream; no `set_option`).
Compiling with `autoImplicit=false` excludes a silently auto-bound variable in a statement.

## 9. Task 5: what this file does NOT prove (do not over-read)

1. **The upstream theorem is not proved here.** Everything is conditional on
   `UniversalEnergyLowerBound`, i.e. on the first conjunct of upstream's `universal_energy_minimum`:
   universal optimality of the triangular lattice among *all* locally finite density-one planar
   configurations, for *every* admissible potential. I did not verify it. To my knowledge (training data up
   to mid-2026) this was the open Cohn-Kumar conjecture in dimension 2; upstream's repository claims a Lean
   proof (solution module `OAI.Analysis.Triangular.Energy.Universal`; the 15 modules under
   `lean/OAI/Analysis/Triangular/Energy/` contain no `sorry`/`axiom`/`native_decide`/`unsafe`/`opaque`
   token; I did not build them, did not audit their other imports, and did not check the Comparator claim).
   The conclusions of this file are exactly as reliable as that claim. The numerical test above is
   consistent with it and proves nothing about it.
2. The second conjunct (`latticeEnergy g = energy g A`: attainment) and any statement on minimisers,
   equality cases or uniqueness are not proved or used.
3. **The quantum step is absent**: no Hamiltonian, wavefunction, kinetic energy, expectation value,
   boson/fermion statistics or ground-state energy is defined. The file is a classical, pointwise
   (configuration-space) inequality. Turning it into `E_0 ≥ N · (1/2) latticeEnergy(g(·/ρ))` also needs a
   convention at coincident points (a null set, where `g 0` is not defined by the admissible class), which
   is not in the file; "trivial integration" is plausible but not formalised.
4. **Only exact lattice periodicity.** Configurations are `⋃ (x_i + Λ)` with `Λ` a full-rank lattice
   (forced by `hcnt`). Nothing for open systems, traps, aperiodic configurations, boundary effects,
   finite-size corrections, or the minimum-image convention with truncated potentials.
5. The inequality is a lower bound valid for any torus shape `L`; it says nothing about whether it is
   attained on a given torus (it is not, in general, when `L` is incommensurate with a triangular
   arrangement of N points).
6. Only the plane and only completely monotone functions of the squared distance: not Lennard-Jones,
   hard cores, other dimensions, or non-admissible potentials. For slowly decaying `g` (e.g.
   `g(t) = t^{-1/2}`, the 2D Coulomb `1/r`) both sides are `+∞` and the statement is empty.
7. No numerical value of any energy is claimed or computed in Lean (apart from the finiteness and
   positivity facts in section 7 for `g = e^{-t}`).

## 10. Remarks (non-blocking)

* The module docstring still says "verifier pending"; it can be updated to point at this report, with the
  caveat of section 9.1.
* The docstring list of copied definitions omits `b` and the seven `abbrev`s; they are copied too
  (verified identical).
* `hfin` (in `periodic_universal_lower_bound`) and `hρ` (in `torus_lower_bound`,
  `torus_energy_per_particle`) are logically redundant; harmless.
* 19 deprecation warnings (`Set.mem_setOf_eq`, `if_pos`, `if_neg`, `dif_pos`, `dif_neg`) and 5 other lints
  will need touching on a later Mathlib; none matters at the pinned version.
* Statement (4)/(5) are stated with `latticeEnergy (fun t => g (t / ρ))`; a reader should remember
  that this is the energy of the triangular lattice *of density ρ*, not of the unit-density one.

## 11. Final verdict

**VERIFIED WITH REMARKS.** As a statement about Lean: the file compiles against upstream's exact toolchain
pin with standard axioms only; the copied definitions equal upstream's; the hypothesis is exactly the first
conjunct of upstream's theorem; the five theorems state what their docstrings say; their hypotheses are
satisfiable and necessary; the conclusion is a genuine inequality in at least one concrete case. As a
statement about mathematics: the result is *conditional* on the upstream theorem, which this verification
did not establish.

*Independent instance of the same model; not human review.*
