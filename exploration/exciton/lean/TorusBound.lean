import Mathlib

/-!
# X4 (torus bound), conditional on the upstream universal-optimality theorem

Exploration material for the exciton-fluid study (SocrateAI-Scientific-QuantumFluids, 2026-10-11).
Toolchain: Lean 4.34.1 / Mathlib v4.34.1 (the pin of the upstream project `openai/math`).
Producer: the session that wrote `docs/designs/EXCITON_FLUID_LEAN_SOLVER_PLAN.md`; **verifier pending**.

## What is proved here

The namespace `OAI` below carries a *verbatim copy* of the definitions of upstream's
`lean/ComparatorChallenges/TriangularEnergy.lean` (`LocallyFinite`, `diskPoints`, `diskCount`, `DensityOne`,
`AdmissiblePotential`, `diskEnergy`, `energy`, `triangularPoint`, `A`, `latticeEnergy`).  The upstream theorem

    universal_energy_minimum : latticeEnergy g ≤ energy g C ∧ latticeEnergy g = energy g A

is **not** reproved: its first conjunct is taken as the hypothesis `UniversalEnergyLowerBound`.  From it we prove,
using only Mathlib, the *periodic-extension step* that the exciton-fluid plan called X4:

* `periodic_universal_lower_bound` — abstract: a configuration made of `N` classes modulo an additive
  subgroup `Λ`, each class having asymptotic density `1/N` (so centred density one), satisfies
  `latticeEnergy g ≤ (1/N) Σᵢ pointEnergy g C (xᵢ)`, where `pointEnergy` is the full (possibly infinite) sum of
  the interaction of `xᵢ` with all other points of `C` (the energy per particle of the *periodic* system).
* `torus_lower_bound_unit` — for a `ℤ`-lattice `L` of covolume `N` (Mathlib's `ZLattice`), `N` pairwise
  inequivalent points.
* `torus_lower_bound` — at density `ρ` (`covolume L * ρ = N`), for the rescaled potential `t ↦ g (t / ρ)`
  (`admissible_comp_div` shows that this rescaling preserves admissibility).
* `torus_energy_per_particle` — the same with the physical factor `½`.

## What is not proved, and conventions

* The upstream theorem itself (AI-generated, Comparator-accepted on another machine; not refereed).
* Energies are in `[0, ∞]` and count **ordered** pairs, as upstream: the physical energy per particle is half.
* Points of different classes are assumed inequivalent modulo `L` (otherwise two bosons would sit at the same
  point of the torus and `g 0` would enter, which the admissible class does not define).
* The *quantum* lower bound (kinetic energy `≥ 0`, expectation over a probability density) is the trivial
  integration of the pointwise bound and is not formalised here.
* `Λ`-periodicity is exact; there is no statement for open systems or traps.
-/

open Filter Topology
open scoped ENNReal

namespace OAI

noncomputable section
open scoped BigOperators Topology ENNReal
open Classical Filter

namespace TriangularUniversal

abbrev Plane := EuclideanSpace ℝ (Fin 2)

def LocallyFinite (C : Set Plane) : Prop :=
  ∀ R : ℝ, (C ∩ Metric.closedBall (0 : Plane) R).Finite

def diskPoints (C : Set Plane) (R : ℝ) : Finset Plane :=
  if h : (C ∩ Metric.closedBall (0 : Plane) R).Finite then h.toFinset else ∅

def diskCount (C : Set Plane) (R : ℝ) : ℕ := (diskPoints C R).card

def DensityOne (C : Set Plane) : Prop :=
  Tendsto (fun R : ℝ => (diskCount C R : ℝ) / (Real.pi * R ^ 2))
    atTop (𝓝 1)

def AdmissiblePotential (g : ℝ → ℝ) : Prop :=
  ContDiffOn ℝ (⊤ : ℕ∞) g (Set.Ioi 0) ∧
  (∀ t : ℝ, 0 < t → 0 ≤ g t) ∧
  ∀ (r : ℕ) (t : ℝ), 0 < t → 0 ≤ (-1 : ℝ) ^ r * iteratedDeriv r g t

def diskEnergy (g : ℝ → ℝ) (C : Set Plane) (R : ℝ) : ℝ≥0∞ :=
  (diskCount C R : ℝ≥0∞)⁻¹ *
    ∑ x ∈ diskPoints C R, ∑ y ∈ (diskPoints C R).erase x,
      ENNReal.ofReal (g (‖x - y‖ ^ 2))

def energy (g : ℝ → ℝ) (C : Set Plane) : ℝ≥0∞ :=
  Filter.liminf (diskEnergy g C) atTop

end TriangularUniversal

namespace AtomicTriangular

abbrev Plane := EuclideanSpace ℝ (Fin 2)

def b : ℝ := Real.sqrt 3 / 2

def triangularPoint (jk : ℤ × ℤ) : Plane :=
  (Real.sqrt b)⁻¹ •
    (EuclideanSpace.single 0 ((jk.1 : ℝ) + (jk.2 : ℝ) / 2) +
      EuclideanSpace.single 1 ((jk.2 : ℝ) * b))

def A : Set Plane := Set.range triangularPoint

abbrev LocallyFinite := TriangularUniversal.LocallyFinite
abbrev diskPoints := TriangularUniversal.diskPoints
abbrev diskCount := TriangularUniversal.diskCount
abbrev DensityOne := TriangularUniversal.DensityOne
abbrev AdmissiblePotential := TriangularUniversal.AdmissiblePotential
abbrev diskEnergy := TriangularUniversal.diskEnergy
abbrev energy := TriangularUniversal.energy

/-- The full nonzero-lattice energy, allowing a divergent series. -/
def latticeEnergy (g : ℝ → ℝ) : ℝ≥0∞ :=
  ∑' a : {x : Plane // x ∈ A ∧ x ≠ 0}, ENNReal.ofReal (g (‖a.val‖ ^ 2))

end AtomicTriangular

/-- The first conjunct of upstream's `AtomicTriangular.universal_energy_minimum`, taken as a hypothesis. -/
def UniversalEnergyLowerBound : Prop :=
  ∀ (g : ℝ → ℝ) (C : Set AtomicTriangular.Plane),
    AtomicTriangular.AdmissiblePotential g → AtomicTriangular.LocallyFinite C →
    AtomicTriangular.DensityOne C → AtomicTriangular.latticeEnergy g ≤ AtomicTriangular.energy g C

namespace TorusBound
open TriangularUniversal

/-- The class of `v` modulo the period group `Λ`. -/
def orbit (Λ : AddSubgroup Plane) (v : Plane) : Set Plane := (fun m => v + m) '' (Λ : Set Plane)

/-- The `Λ`-periodic configuration generated by the `N` base points `x`. -/
def cfg {N : ℕ} (Λ : AddSubgroup Plane) (x : Fin N → Plane) : Set Plane := ⋃ i, orbit Λ (x i)

/-- Interaction (ordered-pair convention, values in `[0,∞]`) of the point `p` with the *other* points of `C`. -/
def pointEnergy (g : ℝ → ℝ) (C : Set Plane) (p : Plane) : ℝ≥0∞ :=
  ∑' q : Plane, Set.indicator {q : Plane | q ∈ C ∧ q ≠ p} (fun q => ENNReal.ofReal (g (‖p - q‖ ^ 2))) q

theorem mem_diskPoints_iff {C : Set Plane} {R : ℝ} (h : (C ∩ Metric.closedBall (0 : Plane) R).Finite)
    {p : Plane} : p ∈ diskPoints C R ↔ p ∈ C ∧ ‖p‖ ≤ R := by
  unfold diskPoints
  rw [dif_pos h, Set.Finite.mem_toFinset]
  simp [Set.mem_inter_iff, Metric.mem_closedBall, dist_zero_right]

theorem mem_of_mem_diskPoints {C : Set Plane} {R : ℝ} {p : Plane} (hp : p ∈ diskPoints C R) : p ∈ C := by
  unfold diskPoints at hp
  split_ifs at hp with h
  · exact ((Set.Finite.mem_toFinset h).1 hp).1
  · simp at hp

theorem mem_cfg_iff_add {N : ℕ} {Λ : AddSubgroup Plane} {x : Fin N → Plane} {m : Plane} (hm : m ∈ Λ)
    (q : Plane) : q + m ∈ cfg Λ x ↔ q ∈ cfg Λ x := by
  unfold cfg orbit
  simp only [Set.mem_iUnion, Set.mem_image, SetLike.mem_coe]
  constructor
  · rintro ⟨i, l, hl, h⟩
    refine ⟨i, l - m, Λ.sub_mem hl hm, ?_⟩
    calc x i + (l - m) = (x i + l) - m := by abel
      _ = q := by rw [h, add_sub_cancel_right]
  · rintro ⟨i, l, hl, h⟩
    refine ⟨i, l + m, Λ.add_mem hl hm, ?_⟩
    rw [← h]; abel

theorem pointEnergy_translate (g : ℝ → ℝ) {N : ℕ} {Λ : AddSubgroup Plane} {x : Fin N → Plane}
    {m : Plane} (hm : m ∈ Λ) (p : Plane) :
    pointEnergy g (cfg Λ x) (p + m) = pointEnergy g (cfg Λ x) p := by
  unfold pointEnergy
  rw [← (Equiv.addRight m).tsum_eq]
  congr 1
  funext q
  simp only [Equiv.coe_addRight, Set.indicator_apply, Set.mem_setOf_eq]
  by_cases hq : q ∈ cfg Λ x ∧ q ≠ p
  · have h1 : q + m ∈ cfg Λ x ∧ q + m ≠ p + m :=
      ⟨(mem_cfg_iff_add hm q).2 hq.1, fun h => hq.2 (add_right_cancel h)⟩
    rw [if_pos h1, if_pos hq]
    have : p + m - (q + m) = p - q := by abel
    rw [this]
  · have h1 : ¬ (q + m ∈ cfg Λ x ∧ q + m ≠ p + m) := by
      rintro ⟨h2, h3⟩
      exact hq ⟨(mem_cfg_iff_add hm q).1 h2, fun h => h3 (by rw [h])⟩
    rw [if_neg h1, if_neg hq]

theorem pointEnergy_orbit (g : ℝ → ℝ) {N : ℕ} {Λ : AddSubgroup Plane} {x : Fin N → Plane} {i : Fin N}
    {p : Plane} (hp : p ∈ orbit Λ (x i)) :
    pointEnergy g (cfg Λ x) p = pointEnergy g (cfg Λ x) (x i) := by
  obtain ⟨m, hm, rfl⟩ := hp
  exact pointEnergy_translate g hm (x i)

theorem diskEnergy_le (g : ℝ → ℝ) (C : Set Plane) (R : ℝ) :
    diskEnergy g C R ≤ (diskCount C R : ℝ≥0∞)⁻¹ * ∑ p ∈ diskPoints C R, pointEnergy g C p := by
  unfold diskEnergy
  refine mul_le_mul' le_rfl (Finset.sum_le_sum fun p hp => ?_)
  calc ∑ y ∈ (diskPoints C R).erase p, ENNReal.ofReal (g (‖p - y‖ ^ 2))
      = ∑ y ∈ (diskPoints C R).erase p,
          Set.indicator {q : Plane | q ∈ C ∧ q ≠ p} (fun q => ENNReal.ofReal (g (‖p - q‖ ^ 2))) y := by
        refine Finset.sum_congr rfl fun y hy => ?_
        have hy' : y ∈ {q : Plane | q ∈ C ∧ q ≠ p} :=
          ⟨mem_of_mem_diskPoints (Finset.mem_of_mem_erase hy), Finset.ne_of_mem_erase hy⟩
        rw [Set.indicator_of_mem hy']
    _ ≤ pointEnergy g C p := ENNReal.sum_le_tsum _

theorem orbit_disjoint {N : ℕ} {Λ : AddSubgroup Plane} {x : Fin N → Plane}
    (hsep : ∀ i j, i ≠ j → x i - x j ∉ Λ) {i j : Fin N} (hij : i ≠ j) :
    Disjoint (orbit Λ (x i)) (orbit Λ (x j)) := by
  rw [Set.disjoint_left]
  rintro p ⟨m, hm, rfl⟩ ⟨m', hm', h⟩
  have h' : x j + m' = x i + m := h
  apply hsep i j hij
  have e : x i - x j = m' - m := by
    calc x i - x j = (x i + m) - m - x j := by abel
      _ = (x j + m') - m - x j := by rw [h']
      _ = m' - m := by abel
  rw [e]
  exact Λ.sub_mem hm' hm

theorem diskPoints_cfg {N : ℕ} {Λ : AddSubgroup Plane} {x : Fin N → Plane}
    (hfin : ∀ (i : Fin N) (R : ℝ), (orbit Λ (x i) ∩ Metric.closedBall (0 : Plane) R).Finite) (R : ℝ) :
    diskPoints (cfg Λ x) R = Finset.univ.biUnion (fun i => diskPoints (orbit Λ (x i)) R) := by
  have hcfg : (cfg Λ x ∩ Metric.closedBall (0 : Plane) R).Finite := by
    unfold cfg
    rw [Set.iUnion_inter]
    exact Set.finite_iUnion (fun i => hfin i R)
  ext p
  rw [mem_diskPoints_iff hcfg, Finset.mem_biUnion]
  constructor
  · rintro ⟨hp, hpR⟩
    obtain ⟨i, hi⟩ := Set.mem_iUnion.1 (show p ∈ ⋃ i, orbit Λ (x i) from hp)
    exact ⟨i, Finset.mem_univ i, (mem_diskPoints_iff (hfin i R)).2 ⟨hi, hpR⟩⟩
  · rintro ⟨i, -, hi⟩
    rw [mem_diskPoints_iff (hfin i R)] at hi
    exact ⟨Set.mem_iUnion.2 ⟨i, hi.1⟩, hi.2⟩

theorem pairwiseDisjoint_diskPoints {N : ℕ} {Λ : AddSubgroup Plane} {x : Fin N → Plane}
    (hsep : ∀ i j, i ≠ j → x i - x j ∉ Λ) (R : ℝ) :
    ((Finset.univ : Finset (Fin N)) : Set (Fin N)).PairwiseDisjoint (fun i => diskPoints (orbit Λ (x i)) R) := by
  intro i _ j _ hij
  refine Finset.disjoint_left.2 fun p hpi hpj => ?_
  exact Set.disjoint_left.1 (orbit_disjoint hsep hij) (mem_of_mem_diskPoints hpi)
    (mem_of_mem_diskPoints hpj)

theorem diskCount_cfg {N : ℕ} {Λ : AddSubgroup Plane} {x : Fin N → Plane}
    (hsep : ∀ i j, i ≠ j → x i - x j ∉ Λ)
    (hfin : ∀ (i : Fin N) (R : ℝ), (orbit Λ (x i) ∩ Metric.closedBall (0 : Plane) R).Finite) (R : ℝ) :
    diskCount (cfg Λ x) R = ∑ i, diskCount (orbit Λ (x i)) R := by
  unfold diskCount
  rw [diskPoints_cfg hfin R, Finset.card_biUnion (pairwiseDisjoint_diskPoints hsep R)]

theorem sum_pointEnergy_cfg (g : ℝ → ℝ) {N : ℕ} {Λ : AddSubgroup Plane} {x : Fin N → Plane}
    (hsep : ∀ i j, i ≠ j → x i - x j ∉ Λ)
    (hfin : ∀ (i : Fin N) (R : ℝ), (orbit Λ (x i) ∩ Metric.closedBall (0 : Plane) R).Finite) (R : ℝ) :
    ∑ p ∈ diskPoints (cfg Λ x) R, pointEnergy g (cfg Λ x) p
      = ∑ i, (diskCount (orbit Λ (x i)) R : ℝ≥0∞) * pointEnergy g (cfg Λ x) (x i) := by
  rw [diskPoints_cfg hfin R, Finset.sum_biUnion (pairwiseDisjoint_diskPoints hsep R)]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [Finset.sum_congr rfl (fun p hp => pointEnergy_orbit g (mem_of_mem_diskPoints hp)),
    Finset.sum_const, nsmul_eq_mul]
  rfl

theorem tendsto_ratio {N : ℕ} (hN : 0 < N) {Λ : AddSubgroup Plane} {x : Fin N → Plane}
    (hsep : ∀ i j, i ≠ j → x i - x j ∉ Λ)
    (hfin : ∀ (i : Fin N) (R : ℝ), (orbit Λ (x i) ∩ Metric.closedBall (0 : Plane) R).Finite)
    (hcnt : ∀ i, Tendsto (fun R : ℝ => (diskCount (orbit Λ (x i)) R : ℝ) / (Real.pi * R ^ 2)) atTop
      (𝓝 (1 / (N : ℝ)))) :
    DensityOne (cfg Λ x) ∧
    ∀ i, Tendsto (fun R : ℝ => (diskCount (orbit Λ (x i)) R : ℝ≥0∞) * (diskCount (cfg Λ x) R : ℝ≥0∞)⁻¹)
      atTop (𝓝 ((N : ℝ≥0∞)⁻¹)) := by
  have hN' : (N : ℝ) ≠ 0 := by positivity
  have hD : ∀ R : ℝ, (diskCount (cfg Λ x) R : ℝ) / (Real.pi * R ^ 2)
      = ∑ i, (diskCount (orbit Λ (x i)) R : ℝ) / (Real.pi * R ^ 2) := by
    intro R
    rw [diskCount_cfg hsep hfin R]
    push_cast
    rw [Finset.sum_div]
  have hDO : Tendsto (fun R : ℝ => (diskCount (cfg Λ x) R : ℝ) / (Real.pi * R ^ 2)) atTop (𝓝 1) := by
    simp_rw [hD]
    have h := tendsto_finsetSum (Finset.univ : Finset (Fin N)) (fun i _ => hcnt i)
    have h1 : (∑ _i : Fin N, (1 / (N : ℝ))) = 1 := by
      rw [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
      field_simp
    rwa [h1] at h
  refine ⟨hDO, fun i => ?_⟩
  have hpos : ∀ᶠ R : ℝ in atTop, 0 < (diskCount (cfg Λ x) R : ℝ) := by
    filter_upwards [hDO.eventually (lt_mem_nhds (zero_lt_one' ℝ)), eventually_gt_atTop (0 : ℝ)] with R h1 h2
    have hq : 0 < Real.pi * R ^ 2 := by positivity
    exact (div_pos_iff_of_pos_right hq).1 h1
  have h1 : Tendsto (fun R : ℝ => ((diskCount (orbit Λ (x i)) R : ℝ) / (Real.pi * R ^ 2)) /
      ((diskCount (cfg Λ x) R : ℝ) / (Real.pi * R ^ 2))) atTop (𝓝 ((1 / (N : ℝ)) / 1)) :=
    (hcnt i).div hDO one_ne_zero
  have h2 := ENNReal.tendsto_ofReal h1
  have h3 : ENNReal.ofReal ((1 / (N : ℝ)) / 1) = (N : ℝ≥0∞)⁻¹ := by
    rw [div_one, one_div, ENNReal.ofReal_inv_of_pos (by positivity), ENNReal.ofReal_natCast]
  rw [h3] at h2
  refine h2.congr' ?_
  filter_upwards [hpos, eventually_gt_atTop (0 : ℝ)] with R hR hR0
  have hq : Real.pi * R ^ 2 ≠ 0 := by positivity
  rw [div_div_div_cancel_right₀ hq, ENNReal.ofReal_div_of_pos hR, ENNReal.ofReal_natCast,
    ENNReal.ofReal_natCast, div_eq_mul_inv]

theorem periodic_universal_lower_bound (hUO : UniversalEnergyLowerBound)
    {N : ℕ} (hN : 0 < N) (Λ : AddSubgroup Plane) (x : Fin N → Plane)
    (hsep : ∀ i j, i ≠ j → x i - x j ∉ Λ)
    (hfin : ∀ (i : Fin N) (R : ℝ), (orbit Λ (x i) ∩ Metric.closedBall (0 : Plane) R).Finite)
    (hcnt : ∀ i, Tendsto (fun R : ℝ => (diskCount (orbit Λ (x i)) R : ℝ) / (Real.pi * R ^ 2)) atTop
      (𝓝 (1 / (N : ℝ))))
    {g : ℝ → ℝ} (hg : AdmissiblePotential g) :
    AtomicTriangular.latticeEnergy g ≤ (N : ℝ≥0∞)⁻¹ * ∑ i, pointEnergy g (cfg Λ x) (x i) := by
  obtain ⟨hDO, hratio⟩ := tendsto_ratio hN hsep hfin hcnt
  have hLF : LocallyFinite (cfg Λ x) := by
    intro R
    unfold cfg
    rw [Set.iUnion_inter]
    exact Set.finite_iUnion (fun i => hfin i R)
  have h1 : AtomicTriangular.latticeEnergy g ≤ energy g (cfg Λ x) := hUO g _ hg hLF hDO
  have hbound : ∀ R : ℝ, diskEnergy g (cfg Λ x) R ≤
      ∑ i, ((diskCount (orbit Λ (x i)) R : ℝ≥0∞) * (diskCount (cfg Λ x) R : ℝ≥0∞)⁻¹) *
        pointEnergy g (cfg Λ x) (x i) := by
    intro R
    refine (diskEnergy_le g _ R).trans ?_
    rw [sum_pointEnergy_cfg g hsep hfin R, Finset.mul_sum]
    refine Finset.sum_le_sum fun i _ => le_of_eq ?_
    ring
  have htend : Tendsto (fun R : ℝ => ∑ i, ((diskCount (orbit Λ (x i)) R : ℝ≥0∞) *
      (diskCount (cfg Λ x) R : ℝ≥0∞)⁻¹) * pointEnergy g (cfg Λ x) (x i)) atTop
      (𝓝 (∑ i, (N : ℝ≥0∞)⁻¹ * pointEnergy g (cfg Λ x) (x i))) := by
    refine tendsto_finsetSum _ fun i _ => ?_
    exact ENNReal.Tendsto.mul_const (hratio i) (Or.inl (by simp [hN.ne']))
  have h2 : energy g (cfg Λ x) ≤ ∑ i, (N : ℝ≥0∞)⁻¹ * pointEnergy g (cfg Λ x) (x i) := by
    unfold energy
    calc Filter.liminf (diskEnergy g (cfg Λ x)) atTop
        ≤ Filter.liminf (fun R : ℝ => ∑ i, ((diskCount (orbit Λ (x i)) R : ℝ≥0∞) *
            (diskCount (cfg Λ x) R : ℝ≥0∞)⁻¹) * pointEnergy g (cfg Λ x) (x i)) atTop :=
          Filter.liminf_le_liminf (Filter.Eventually.of_forall hbound)
      _ = _ := htend.liminf_eq
  rw [← Finset.mul_sum] at h2
  exact h1.trans h2



section lattice

variable (L : Submodule ℤ Plane) [DiscreteTopology L] [IsZLattice ℝ L]

theorem finite_lattice_inter_closedBall (R : ℝ) :
    ((L : Set Plane) ∩ Metric.closedBall (0 : Plane) R).Finite := by
  have : DiscreteTopology L.toAddSubgroup := inferInstanceAs (DiscreteTopology L)
  have hc : IsClosed (L : Set Plane) := by
    rw [← Submodule.coe_toAddSubgroup]
    exact AddSubgroup.isClosed_of_discreteTopology
  rw [Set.inter_comm]
  exact Metric.finite_isBounded_inter_isClosed DiscreteTopology.isDiscrete Metric.isBounded_closedBall hc

theorem tendsto_card_lattice_ball :
    Tendsto (fun R : ℝ => (((L : Set Plane) ∩ Metric.closedBall (0 : Plane) R).ncard : ℝ) / R ^ 2) atTop
      (𝓝 (Real.pi / ZLattice.covolume L)) := by
  have hX : ∀ ⦃x : Plane⦄ ⦃r : ℝ⦄, x ∈ (Set.univ : Set Plane) → 0 < r → r • x ∈ (Set.univ : Set Plane) :=
    fun _ _ _ _ => Set.mem_univ _
  have h₁ : ∀ (x : Plane) ⦃r : ℝ⦄, 0 ≤ r →
      ‖r • x‖ ^ 2 = r ^ Module.finrank ℝ Plane * ‖x‖ ^ 2 := by
    intro x r hr
    rw [norm_smul, Real.norm_eq_abs, abs_of_nonneg hr, finrank_euclideanSpace_fin]
    ring
  have hS : ∀ R : ℝ, 0 ≤ R →
      {x : Plane | x ∈ (Set.univ : Set Plane) ∧ ‖x‖ ^ 2 ≤ R ^ 2} = Metric.closedBall (0 : Plane) R := by
    intro R hR
    ext x
    simp only [Set.mem_univ, true_and, Set.mem_setOf_eq, Metric.mem_closedBall, dist_zero_right]
    constructor
    · intro h; nlinarith [norm_nonneg x]
    · intro h; nlinarith [norm_nonneg x]
  have hS1 : {x : Plane | x ∈ (Set.univ : Set Plane) ∧ ‖x‖ ^ 2 ≤ 1} = Metric.closedBall (0 : Plane) 1 := by
    simpa using hS 1 zero_le_one
  have key := ZLattice.covolume.tendsto_card_le_div' L (X := (Set.univ : Set Plane))
    (F := fun y : Plane => ‖y‖ ^ 2) hX h₁
    (by rw [hS1]; exact Metric.isBounded_closedBall)
    (by rw [hS1]; exact measurableSet_closedBall)
    (by rw [hS1, frontier_closedBall _ one_ne_zero]
        exact MeasureTheory.Measure.addHaar_sphere MeasureTheory.volume _ 1)
  have hvol : MeasureTheory.volume.real (Metric.closedBall (0 : Plane) 1) = Real.pi := by
    rw [MeasureTheory.measureReal_def, EuclideanSpace.volume_closedBall_fin_two]
    simp [ENNReal.toReal_mul, ENNReal.toReal_pow, ENNReal.toReal_ofReal, Real.pi_pos.le]
  rw [hS1, hvol] at key
  have key2 := key.comp (tendsto_pow_atTop (two_ne_zero) : Tendsto (fun R : ℝ => R ^ 2) atTop atTop)
  refine key2.congr' ?_
  filter_upwards [eventually_ge_atTop (0 : ℝ)] with R hR
  simp only [Function.comp_apply]
  rw [hS R hR, Set.inter_comm, Nat.card_coe_set_eq]

theorem finite_shift (v : Plane) (R : ℝ) : ((L : Set Plane) ∩ {m | ‖v + m‖ ≤ R}).Finite := by
  refine (finite_lattice_inter_closedBall L (R + ‖v‖)).subset ?_
  rintro m ⟨hm, hmR⟩
  refine ⟨hm, ?_⟩
  simp only [Metric.mem_closedBall, dist_zero_right]
  have : ‖m‖ ≤ ‖v + m‖ + ‖v‖ := by
    calc ‖m‖ = ‖(v + m) - v‖ := by rw [add_sub_cancel_left]
      _ ≤ ‖v + m‖ + ‖v‖ := norm_sub_le _ _
  simp only [Set.mem_setOf_eq] at hmR
  linarith

theorem tendsto_shift_count (v : Plane) :
    Tendsto (fun R : ℝ => (((L : Set Plane) ∩ {m | ‖v + m‖ ≤ R}).ncard : ℝ) / R ^ 2) atTop
      (𝓝 (Real.pi / ZLattice.covolume L)) := by
  have h0 := tendsto_card_lattice_ball L
  set c := Real.pi / ZLattice.covolume L with hc
  set s := ‖v‖ with hs
  have hs0 : 0 ≤ s := norm_nonneg v
  -- upper sequence
  have hup : Tendsto (fun R : ℝ => (((L : Set Plane) ∩ Metric.closedBall (0 : Plane) (R + s)).ncard : ℝ) / R ^ 2)
      atTop (𝓝 c) := by
    have h1 : Tendsto (fun R : ℝ => (((L : Set Plane) ∩ Metric.closedBall (0 : Plane) (R + s)).ncard : ℝ)
        / (R + s) ^ 2) atTop (𝓝 c) := h0.comp (tendsto_atTop_add_const_right atTop s tendsto_id)
    have h2 : Tendsto (fun R : ℝ => (1 + s / R) ^ 2) atTop (𝓝 1) := by
      have h := ((tendsto_const_nhds (x := (1 : ℝ))).add
        ((tendsto_const_nhds (x := s)).div_atTop tendsto_id) :
          Tendsto (fun R : ℝ => 1 + s / R) atTop (𝓝 (1 + 0))).pow 2
      simpa using h
    have h3 := h1.mul h2
    rw [mul_one] at h3
    refine h3.congr' ?_
    filter_upwards [eventually_gt_atTop (0 : ℝ)] with R hR
    have hR' : R + s ≠ 0 := by positivity
    field_simp
  have hlow : Tendsto (fun R : ℝ => (((L : Set Plane) ∩ Metric.closedBall (0 : Plane) (R - s)).ncard : ℝ) / R ^ 2)
      atTop (𝓝 c) := by
    have h1 : Tendsto (fun R : ℝ => (((L : Set Plane) ∩ Metric.closedBall (0 : Plane) (R - s)).ncard : ℝ)
        / (R - s) ^ 2) atTop (𝓝 c) := by
      have : Tendsto (fun R : ℝ => R - s) atTop atTop := tendsto_atTop_add_const_right atTop (-s) tendsto_id |>.congr
        (fun R => by simp [sub_eq_add_neg])
      exact h0.comp this
    have h2 : Tendsto (fun R : ℝ => (1 - s / R) ^ 2) atTop (𝓝 1) := by
      have h := ((tendsto_const_nhds (x := (1 : ℝ))).sub
        ((tendsto_const_nhds (x := s)).div_atTop tendsto_id) :
          Tendsto (fun R : ℝ => 1 - s / R) atTop (𝓝 (1 - 0))).pow 2
      simpa using h
    have h3 := h1.mul h2
    rw [mul_one] at h3
    refine h3.congr' ?_
    filter_upwards [eventually_gt_atTop s, eventually_gt_atTop (0 : ℝ)] with R hRs hR
    have hR' : R - s ≠ 0 := by linarith
    field_simp
  refine tendsto_of_tendsto_of_tendsto_of_le_of_le' hlow hup ?_ ?_
  · filter_upwards [eventually_gt_atTop (0 : ℝ)] with R hR
    refine div_le_div_of_nonneg_right ?_ (by positivity)
    exact_mod_cast Set.ncard_le_ncard (Set.inter_subset_inter_right _ (fun m hm => by
      simp only [Metric.mem_closedBall, dist_zero_right, Set.mem_setOf_eq] at hm ⊢
      calc ‖v + m‖ ≤ ‖v‖ + ‖m‖ := norm_add_le _ _
        _ ≤ R := by linarith)) (finite_shift L v R)
  · filter_upwards [eventually_gt_atTop (0 : ℝ)] with R hR
    refine div_le_div_of_nonneg_right ?_ (by positivity)
    exact_mod_cast Set.ncard_le_ncard (Set.inter_subset_inter_right _ (fun m hm => by
      simp only [Metric.mem_closedBall, dist_zero_right, Set.mem_setOf_eq] at hm ⊢
      have : ‖m‖ ≤ ‖v + m‖ + ‖v‖ := by
        calc ‖m‖ = ‖(v + m) - v‖ := by rw [add_sub_cancel_left]
          _ ≤ ‖v + m‖ + ‖v‖ := norm_sub_le _ _
      linarith)) (finite_lattice_inter_closedBall L (R + s))

theorem orbit_inter_ball (v : Plane) (R : ℝ) :
    orbit L.toAddSubgroup v ∩ Metric.closedBall (0 : Plane) R
      = (fun m => v + m) '' ((L : Set Plane) ∩ {m | ‖v + m‖ ≤ R}) := by
  ext p
  simp only [orbit, Set.mem_inter_iff, Set.mem_image, Metric.mem_closedBall, dist_zero_right,
    Set.mem_setOf_eq, SetLike.mem_coe, Submodule.mem_toAddSubgroup]
  constructor
  · rintro ⟨⟨m, hm, rfl⟩, hp⟩
    exact ⟨m, ⟨hm, hp⟩, rfl⟩
  · rintro ⟨m, ⟨hm, hp⟩, rfl⟩
    exact ⟨⟨m, hm, rfl⟩, hp⟩

theorem orbit_finite (v : Plane) (R : ℝ) :
    (orbit L.toAddSubgroup v ∩ Metric.closedBall (0 : Plane) R).Finite := by
  rw [orbit_inter_ball]
  exact (finite_shift L v R).image _

theorem diskCount_orbit (v : Plane) (R : ℝ) :
    diskCount (orbit L.toAddSubgroup v) R = ((L : Set Plane) ∩ {m | ‖v + m‖ ≤ R}).ncard := by
  have h := orbit_finite L v R
  unfold diskCount diskPoints
  rw [dif_pos h, ← Set.ncard_eq_toFinset_card _ h, orbit_inter_ball,
    Set.ncard_image_of_injective _ (add_right_injective v)]

theorem orbit_density_tendsto (v : Plane) :
    Tendsto (fun R : ℝ => (diskCount (orbit L.toAddSubgroup v) R : ℝ) / (Real.pi * R ^ 2)) atTop
      (𝓝 (1 / ZLattice.covolume L)) := by
  have h := (tendsto_shift_count L v).div_const Real.pi
  have hπ : Real.pi ≠ 0 := Real.pi_ne_zero
  have hV : ZLattice.covolume L ≠ 0 := (ZLattice.covolume_pos L MeasureTheory.volume).ne'
  have e : Real.pi / ZLattice.covolume L / Real.pi = 1 / ZLattice.covolume L := by field_simp
  rw [e] at h
  refine h.congr fun R => ?_
  rw [diskCount_orbit, div_div, mul_comm]

end lattice





/-! ## Rescaling the potential: `g ↦ g(·/ρ)` preserves admissibility -/

theorem admissible_comp_div {g : ℝ → ℝ} (hg : AdmissiblePotential g) {ρ : ℝ} (hρ : 0 < ρ) :
    AdmissiblePotential (fun t => g (t / ρ)) := by
  obtain ⟨h1, h2, h3⟩ := hg
  have hopen : IsOpen (Set.Ioi (0 : ℝ)) := isOpen_Ioi
  have hU : UniqueDiffOn ℝ (Set.Ioi (0 : ℝ)) := hopen.uniqueDiffOn
  have hmaps : Set.MapsTo (fun t : ℝ => ρ⁻¹ * t) (Set.Ioi 0) (Set.Ioi 0) :=
    fun t ht => mul_pos (inv_pos.2 hρ) ht
  have hfun : (fun t : ℝ => g (t / ρ)) = fun t => g (ρ⁻¹ * t) := by
    funext t; rw [div_eq_inv_mul]
  refine ⟨?_, ?_, ?_⟩
  · rw [hfun]
    exact h1.comp (contDiffOn_const.mul contDiffOn_id) hmaps
  · intro t ht
    exact h2 _ (div_pos ht hρ)
  · intro r t ht
    rw [hfun]
    have hle : (r : WithTop ℕ∞) ≤ ((⊤ : ℕ∞) : WithTop ℕ∞) := by exact_mod_cast le_top
    have h1r : ContDiffOn ℝ r g (Set.Ioi 0) := h1.of_le hle
    have e := iteratedDerivWithin_comp_const_smul (n := r) (f := g) (s := Set.Ioi 0) (x := t) ht hU h1r
      ρ⁻¹ hmaps
    have e1 : iteratedDeriv r (fun t => g (ρ⁻¹ * t)) t
        = iteratedDerivWithin r (fun t => g (ρ⁻¹ * t)) (Set.Ioi 0) t :=
      (iteratedDerivWithin_of_isOpen hopen ht).symm
    have e2 : iteratedDerivWithin r g (Set.Ioi 0) (ρ⁻¹ * t) = iteratedDeriv r g (ρ⁻¹ * t) :=
      iteratedDerivWithin_of_isOpen hopen (hmaps ht)
    rw [e1, e, e2, smul_eq_mul]
    have h4 := h3 r (ρ⁻¹ * t) (hmaps ht)
    have h5 : 0 ≤ (ρ⁻¹) ^ r := by positivity
    calc (0 : ℝ) ≤ (ρ⁻¹) ^ r * ((-1 : ℝ) ^ r * iteratedDeriv r g (ρ⁻¹ * t)) := mul_nonneg h5 h4
      _ = (-1 : ℝ) ^ r * ((ρ⁻¹) ^ r * iteratedDeriv r g (ρ⁻¹ * t)) := by ring

/-! ## Rescaling a configuration -/

/-- The configuration `s • C`. -/
def smulSet (s : ℝ) (C : Set Plane) : Set Plane := (fun p => s • p) '' C

theorem smulSet_inter_ball {s : ℝ} (hs : 0 < s) (C : Set Plane) (R : ℝ) :
    smulSet s C ∩ Metric.closedBall (0 : Plane) R = (fun p => s • p) '' (C ∩ Metric.closedBall (0 : Plane) (R / s)) := by
  ext p
  simp only [smulSet, Set.mem_inter_iff, Set.mem_image, Metric.mem_closedBall, dist_zero_right]
  constructor
  · rintro ⟨⟨q, hq, rfl⟩, hp⟩
    refine ⟨q, ⟨hq, ?_⟩, rfl⟩
    rw [norm_smul, Real.norm_eq_abs, abs_of_pos hs] at hp
    rw [le_div_iff₀ hs]
    linarith
  · rintro ⟨q, ⟨hq, hqR⟩, rfl⟩
    refine ⟨⟨q, hq, rfl⟩, ?_⟩
    rw [norm_smul, Real.norm_eq_abs, abs_of_pos hs]
    rw [le_div_iff₀ hs] at hqR
    linarith

theorem diskCount_eq_ncard (C : Set Plane) (R : ℝ) :
    diskCount C R = (C ∩ Metric.closedBall (0 : Plane) R).ncard := by
  by_cases h : (C ∩ Metric.closedBall (0 : Plane) R).Finite
  · unfold diskCount diskPoints
    rw [dif_pos h, ← Set.ncard_eq_toFinset_card _ h]
  · unfold diskCount diskPoints
    rw [dif_neg h, Set.Infinite.ncard h]
    rfl

theorem diskCount_smulSet {s : ℝ} (hs : 0 < s) (C : Set Plane) (R : ℝ) :
    diskCount (smulSet s C) R = diskCount C (R / s) := by
  rw [diskCount_eq_ncard, diskCount_eq_ncard, smulSet_inter_ball hs,
    Set.ncard_image_of_injective _ (smul_right_injective Plane hs.ne')]

theorem pointEnergy_smul {s : ℝ} (hs : 0 < s) (g : ℝ → ℝ) (C : Set Plane) (p : Plane) :
    pointEnergy (fun t => g (t / s ^ 2)) (smulSet s C) (s • p) = pointEnergy g C p := by
  unfold pointEnergy
  let e : Plane ≃ Plane := MulAction.toPerm (Units.mk0 s hs.ne')
  rw [← e.tsum_eq]
  congr 1
  funext q
  have he : e q = s • q := rfl
  rw [he]
  have hinj : Function.Injective (fun p : Plane => s • p) := smul_right_injective Plane hs.ne'
  simp only [Set.indicator_apply, Set.mem_setOf_eq]
  have hmem : s • q ∈ smulSet s C ↔ q ∈ C := by
    constructor
    · rintro ⟨q', hq', h⟩
      exact (hinj h) ▸ hq'
    · intro hq
      exact ⟨q, hq, rfl⟩
  have hne : s • q ≠ s • p ↔ q ≠ p := by
    constructor
    · intro h h'; exact h (by rw [h'])
    · intro h h'; exact h (hinj h')
  have hnorm : ‖s • p - s • q‖ ^ 2 = s ^ 2 * ‖p - q‖ ^ 2 := by
    rw [← smul_sub, norm_smul, Real.norm_eq_abs, abs_of_pos hs]; ring
  by_cases hq : q ∈ C ∧ q ≠ p
  · rw [if_pos ⟨hmem.2 hq.1, hne.2 hq.2⟩, if_pos hq, hnorm]
    congr 3
    field_simp
  · rw [if_neg (fun h => hq ⟨hmem.1 h.1, hne.1 h.2⟩), if_neg hq]


section final

variable (L : Submodule ℤ Plane) [DiscreteTopology L] [IsZLattice ℝ L]

/-- **Torus bound, unit density.**  `N` points, pairwise inequivalent modulo the lattice `L` of covolume `N`
(centred density one); the periodic configuration `cfg L x` generated by them satisfies, for every
admissible `g`, `latticeEnergy g ≤ (1/N) Σᵢ pointEnergy g (cfg L x) (xᵢ)` (ordered-pair convention; the
physical energy per particle is half of each side).  Conditional on the upstream theorem `hUO`. -/
theorem torus_lower_bound_unit (hUO : UniversalEnergyLowerBound)
    {N : ℕ} (hN : 0 < N) (hcov : ZLattice.covolume L = N)
    (x : Fin N → Plane) (hsep : ∀ i j, i ≠ j → x i - x j ∉ L)
    {g : ℝ → ℝ} (hg : AdmissiblePotential g) :
    AtomicTriangular.latticeEnergy g ≤
      (N : ℝ≥0∞)⁻¹ * ∑ i, pointEnergy g (cfg L.toAddSubgroup x) (x i) := by
  refine periodic_universal_lower_bound hUO hN L.toAddSubgroup x
    (fun i j hij h => hsep i j hij h) (fun i R => orbit_finite L (x i) R) ?_ hg
  intro i
  have h := orbit_density_tendsto L (x i)
  rwa [hcov] at h

/-- **Torus bound at density `ρ = N / covolume`.**  The lattice energy of the *rescaled* potential
`t ↦ g (t / ρ)` (i.e. of the triangular lattice at density `ρ`) is a lower bound for the energy per
particle of any `N`-point configuration on the torus `ℝ² / L` with `covolume L * ρ = N`. -/
theorem torus_lower_bound (hUO : UniversalEnergyLowerBound)
    {N : ℕ} (hN : 0 < N) {ρ : ℝ} (hρ : 0 < ρ) (hcov : ZLattice.covolume L * ρ = N)
    (x : Fin N → Plane) (hsep : ∀ i j, i ≠ j → x i - x j ∉ L)
    {g : ℝ → ℝ} (hg : AdmissiblePotential g) :
    AtomicTriangular.latticeEnergy (fun t => g (t / ρ)) ≤
      (N : ℝ≥0∞)⁻¹ * ∑ i, pointEnergy g (cfg L.toAddSubgroup x) (x i) := by
  obtain ⟨s, hs, rfl⟩ : ∃ s : ℝ, 0 < s ∧ s ^ 2 = ρ := ⟨Real.sqrt ρ, Real.sqrt_pos.2 hρ, Real.sq_sqrt hρ.le⟩
  let Λ' : AddSubgroup Plane := L.toAddSubgroup.map (DistribSMul.toAddMonoidHom Plane s)
  let x' : Fin N → Plane := fun i => s • x i
  have hinj : Function.Injective (fun p : Plane => s • p) := smul_right_injective Plane hs.ne'
  have horb : ∀ i, orbit Λ' (x' i) = smulSet s (orbit L.toAddSubgroup (x i)) := by
    intro i
    ext p
    simp only [orbit, smulSet, Set.mem_image, SetLike.mem_coe, Λ', AddSubgroup.mem_map,
      DistribSMul.toAddMonoidHom_apply, x']
    constructor
    · rintro ⟨m', ⟨l, hl, rfl⟩, rfl⟩
      exact ⟨x i + l, ⟨l, hl, rfl⟩, by simp [smul_add]⟩
    · rintro ⟨q, ⟨l, hl, rfl⟩, rfl⟩
      exact ⟨s • l, ⟨l, hl, rfl⟩, by simp [smul_add]⟩
  have hcfg : cfg Λ' x' = smulSet s (cfg L.toAddSubgroup x) := by
    unfold cfg
    simp only [horb]
    unfold smulSet
    rw [Set.image_iUnion]
  have hsep' : ∀ i j, i ≠ j → x' i - x' j ∉ Λ' := by
    intro i j hij h
    simp only [Λ', AddSubgroup.mem_map, DistribSMul.toAddMonoidHom_apply, x'] at h
    obtain ⟨l, hl, hl'⟩ := h
    apply hsep i j hij
    have : l = x i - x j := by
      apply hinj
      simp only [hl', smul_sub]
    rw [← this]
    exact hl
  have hfin' : ∀ (i : Fin N) (R : ℝ), (orbit Λ' (x' i) ∩ Metric.closedBall (0 : Plane) R).Finite := by
    intro i R
    rw [horb, smulSet_inter_ball hs]
    exact (orbit_finite L (x i) (R / s)).image _
  have hcnt' : ∀ i, Tendsto (fun R : ℝ => (diskCount (orbit Λ' (x' i)) R : ℝ) / (Real.pi * R ^ 2)) atTop
      (𝓝 (1 / (N : ℝ))) := by
    intro i
    have h1 := (orbit_density_tendsto L (x i)).comp (tendsto_id.atTop_div_const hs)
    have h2 := h1.mul_const (1 / s ^ 2)
    have hV : (1 : ℝ) / ZLattice.covolume L * (1 / s ^ 2) = 1 / (N : ℝ) := by
      have hV0 : ZLattice.covolume L ≠ 0 := (ZLattice.covolume_pos L MeasureTheory.volume).ne'
      have hs0 : s ≠ 0 := hs.ne'
      rw [← hcov]
      field_simp
    rw [hV] at h2
    refine h2.congr' ?_
    filter_upwards [eventually_gt_atTop (0 : ℝ)] with R hR
    simp only [Function.comp_apply, id_eq]
    rw [horb, diskCount_smulSet hs]
    have hπ : Real.pi ≠ 0 := Real.pi_ne_zero
    have hs0 : s ≠ 0 := hs.ne'
    have hR0 : R ≠ 0 := hR.ne'
    field_simp
  have hg' : AdmissiblePotential (fun t => g (t / s ^ 2)) := admissible_comp_div hg (pow_pos hs 2)
  have h := periodic_universal_lower_bound hUO hN Λ' x' hsep' hfin' hcnt' hg'
  have e : ∑ i, pointEnergy (fun t => g (t / s ^ 2)) (cfg Λ' x') (x' i)
      = ∑ i, pointEnergy g (cfg L.toAddSubgroup x) (x i) :=
    Finset.sum_congr rfl fun i _ => by
      rw [hcfg]
      exact pointEnergy_smul hs g _ (x i)
  rw [e] at h
  exact h

/-- The same statement for the physical energy per particle `e = ½ Σ_{pairs}` (unordered pairs): half of
the lattice energy bounds half of the torus energy. -/
theorem torus_energy_per_particle (hUO : UniversalEnergyLowerBound)
    {N : ℕ} (hN : 0 < N) {ρ : ℝ} (hρ : 0 < ρ) (hcov : ZLattice.covolume L * ρ = N)
    (x : Fin N → Plane) (hsep : ∀ i j, i ≠ j → x i - x j ∉ L)
    {g : ℝ → ℝ} (hg : AdmissiblePotential g) :
    (2 : ℝ≥0∞)⁻¹ * AtomicTriangular.latticeEnergy (fun t => g (t / ρ)) ≤
      (N : ℝ≥0∞)⁻¹ * ((2 : ℝ≥0∞)⁻¹ * ∑ i, pointEnergy g (cfg L.toAddSubgroup x) (x i)) := by
  have h := torus_lower_bound L hUO hN hρ hcov x hsep hg
  calc (2 : ℝ≥0∞)⁻¹ * AtomicTriangular.latticeEnergy (fun t => g (t / ρ))
      ≤ (2 : ℝ≥0∞)⁻¹ * ((N : ℝ≥0∞)⁻¹ * ∑ i, pointEnergy g (cfg L.toAddSubgroup x) (x i)) :=
        mul_le_mul' le_rfl h
    _ = _ := by ring

end final

end TorusBound

end

end OAI

open OAI OAI.TorusBound in
#print axioms periodic_universal_lower_bound
open OAI OAI.TorusBound in
#print axioms torus_lower_bound_unit
open OAI OAI.TorusBound in
#print axioms torus_lower_bound
open OAI OAI.TorusBound in
#print axioms torus_energy_per_particle
open OAI OAI.TorusBound in
#print axioms admissible_comp_div
