/-
  SectorTemperature.lean -- what "topological sectors carry their own temperature" means, exactly,
  and why a thermometer that averages over sectors cannot read "the" temperature of a mixed state.

  Round 2 of the PGPE programme found that two boxes with the same energy, one carrying an injected
  winding configuration and one not, read different temperatures. Thought experiment F says this is
  expected: the microcanonical entropy depends on the sector, S(E, W), so ∂S/∂E does too. This file
  makes the finite, discrete version of that statement a theorem, with no physics attached beyond the
  definitions.

  Setting. A finite set of microstates `Ω`, an energy level `ε : Ω → ℕ` (energies binned to integers),
  a sector label `w : Ω → ℤ` (a winding number). The sector count `n w E` is the number of microstates
  in sector `w` at energy `E`; the global count `N E` is the sum over sectors. The discrete inverse
  temperature of a sector is the ratio of its counts at adjacent energies, `n w (E+1) / n w E`
  (that is `exp(S_w(E+1) − S_w(E))`, Boltzmann's `exp(β)` for unit energy steps); the global one is
  `N (E+1) / N E`.

  * `count_sum`            : the global count is the sum of the sector counts;
  * `entropy_ge_sector`    : global entropy ≥ every sector entropy (log of counts);
  * `mediant_le`, `le_mediant`: **the global inverse temperature lies between the smallest and the
                             largest sector inverse temperature** (the mediant inequality for ratios
                             of nonnegative sums). In words: a thermometer that does not know the
                             sector reads a weighted mean of sector temperatures, and two states of the
                             same energy in different sectors need not, and in general do not, share
                             it. Equal energy does not imply equal temperature once a conserved label
                             exists.
  * `global_eq_sector_of_single` : if only one sector is populated at both energies, the global
                             reading is that sector's reading -- the case with no topology.
  * `sector_invariant`     : the sectors are invariant sets of any evolution that never lets a loop
                             step reach the branch point (from `TopologicalProtection`): the label is
                             conserved, so the restriction of the dynamics to a sector is well defined,
                             which is what gives `S(E, W)` a physical meaning.

  NOT PROVED, NOT CLAIMED: that the equipartition thermometer of the PGPE runs reads the global ratio,
  the bath ratio, or anything else (that is a statement about an estimator on a continuum field);
  ergodicity within a sector; any value of any temperature.
-/
import Mathlib
import TopologicalProtection

namespace QuantumFluids.SectorTemperature

open Finset

variable {Ω : Type*} [Fintype Ω]

/-- Number of microstates in sector `w` at energy level `E`. -/
def sectorCount (ε : Ω → ℕ) (w : Ω → ℤ) (W : ℤ) (E : ℕ) : ℕ :=
  (univ.filter (fun x => ε x = E ∧ w x = W)).card

/-- Number of microstates at energy level `E`, all sectors. -/
def globalCount (ε : Ω → ℕ) (E : ℕ) : ℕ :=
  (univ.filter (fun x => ε x = E)).card

/-- The finite set of sectors that occur. -/
def sectors (w : Ω → ℤ) : Finset ℤ := univ.image w

/-- **The global count is the sum of the sector counts.** -/
theorem count_sum (ε : Ω → ℕ) (w : Ω → ℤ) (E : ℕ) :
    globalCount ε E = ∑ W ∈ sectors w, sectorCount ε w W E := by
  unfold globalCount sectorCount sectors
  rw [Finset.card_eq_sum_card_fiberwise (f := w) (t := univ.image w)]
  · refine Finset.sum_congr rfl (fun W _ => ?_)
    congr 1; ext x; simp [and_comm]
  · intro x hx; simp

/-- The sector count never exceeds the global count. -/
theorem sectorCount_le (ε : Ω → ℕ) (w : Ω → ℤ) (W : ℤ) (E : ℕ) :
    sectorCount ε w W E ≤ globalCount ε E := by
  unfold sectorCount globalCount
  exact Finset.card_le_card (fun x hx => by simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hx ⊢; exact hx.1)

/-- Global entropy dominates every sector entropy (counts, hence logs; `Real.log 0 = 0`). -/
theorem entropy_ge_sector (ε : Ω → ℕ) (w : Ω → ℤ) (W : ℤ) (E : ℕ) :
    Real.log (sectorCount ε w W E) ≤ Real.log (globalCount ε E) := by
  have h := sectorCount_le ε w W E
  rcases Nat.eq_zero_or_pos (sectorCount ε w W E) with h0 | hpos
  · rw [h0, Nat.cast_zero, Real.log_zero]
    exact Real.log_natCast_nonneg _
  · exact Real.log_le_log (by exact_mod_cast hpos) (by exact_mod_cast h)

/-! ### The mediant inequality: the global ratio is bracketed by the sector ratios -/

/-- Mediant, upper bound: if every `a i / b i ≤ r` (with `b i > 0`), then `(Σ a) / (Σ b) ≤ r`. -/
theorem mediant_le {ι : Type*} (s : Finset ι) (a b : ι → ℝ) (r : ℝ) (hs : s.Nonempty)
    (hb : ∀ i ∈ s, 0 < b i) (h : ∀ i ∈ s, a i / b i ≤ r) :
    (∑ i ∈ s, a i) / (∑ i ∈ s, b i) ≤ r := by
  have hB : 0 < ∑ i ∈ s, b i := Finset.sum_pos hb hs
  rw [div_le_iff₀ hB, Finset.mul_sum]
  refine Finset.sum_le_sum (fun i hi => ?_)
  have := h i hi
  rw [div_le_iff₀ (hb i hi)] at this
  linarith

/-- Mediant, lower bound: if every `a i / b i ≥ r`, then `(Σ a) / (Σ b) ≥ r`. -/
theorem le_mediant {ι : Type*} (s : Finset ι) (a b : ι → ℝ) (r : ℝ) (hs : s.Nonempty)
    (hb : ∀ i ∈ s, 0 < b i) (h : ∀ i ∈ s, r ≤ a i / b i) :
    r ≤ (∑ i ∈ s, a i) / (∑ i ∈ s, b i) := by
  have hB : 0 < ∑ i ∈ s, b i := Finset.sum_pos hb hs
  rw [le_div_iff₀ hB, Finset.mul_sum]
  refine Finset.sum_le_sum (fun i hi => ?_)
  have := h i hi
  rw [le_div_iff₀ (hb i hi)] at this
  linarith

/-- Discrete inverse-temperature factor `exp β` of sector `W` at energy `E`: ratio of counts at `E+1`
and `E`. -/
noncomputable def sectorRatio (ε : Ω → ℕ) (w : Ω → ℤ) (W : ℤ) (E : ℕ) : ℝ :=
  (sectorCount ε w W (E + 1) : ℝ) / sectorCount ε w W E

/-- The global factor. -/
noncomputable def globalRatio (ε : Ω → ℕ) (E : ℕ) : ℝ :=
  (globalCount ε (E + 1) : ℝ) / globalCount ε E

/-- **Sector temperatures bracket the global temperature.** If every sector present at `E` has a
positive count there, and every sector ratio lies in `[r₁, r₂]`, then so does the global ratio. A
thermometer blind to the sector reads a mediant of the sector readings. -/
theorem globalRatio_mem (ε : Ω → ℕ) (w : Ω → ℤ) (E : ℕ) (r₁ r₂ : ℝ)
    (hne : (sectors w).Nonempty)
    (hpos : ∀ W ∈ sectors w, 0 < sectorCount ε w W E)
    (hlo : ∀ W ∈ sectors w, r₁ ≤ sectorRatio ε w W E)
    (hhi : ∀ W ∈ sectors w, sectorRatio ε w W E ≤ r₂) :
    r₁ ≤ globalRatio ε E ∧ globalRatio ε E ≤ r₂ := by
  unfold globalRatio
  rw [count_sum ε w (E + 1), count_sum ε w E]
  push_cast
  have hb : ∀ W ∈ sectors w, (0 : ℝ) < sectorCount ε w W E := fun W hW => by exact_mod_cast hpos W hW
  exact ⟨le_mediant _ _ _ r₁ hne hb hlo, mediant_le _ _ _ r₂ hne hb hhi⟩

/-- With a single populated sector, the global reading is the sector reading: no topology, no
discrepancy. -/
theorem global_eq_sector_of_single (ε : Ω → ℕ) (w : Ω → ℤ) (W₀ : ℤ) (E : ℕ)
    (hsingle : ∀ x, w x = W₀) :
    globalRatio ε E = sectorRatio ε w W₀ E := by
  unfold globalRatio sectorRatio globalCount sectorCount
  congr 2 <;> · congr 1; ext x; simp [hsingle x]

/-! ### Sectors are invariant under no-slip evolution -/

open QuantumFluids.TopologicalProtection in
/-- **The sector of a loop is invariant** under any evolution of its phases that is continuous in
time and never lets a step reach the branch point: the loop sum at `t₁` equals the loop sum at
`t₀`, so the state stays in the sector `{loopSum = c}` it started in. This is what makes the
restriction of the dynamics to a sector -- and hence `S(E, W)` -- well defined. -/
theorem sector_invariant (θ : ℝ → ℕ → ℝ) (n : ℕ) {t₀ t₁ : ℝ} (ht : t₀ ≤ t₁)
    (hcont : ∀ i ≤ n, Continuous (fun t => θ t i)) (hclosed : ∀ t, θ t n = θ t 0)
    (hslip : ∀ t ∈ Set.Icc t₀ t₁, ∀ i < n, VortexWinding.pdiff (θ t i) (θ t (i + 1)) ≠ Real.pi)
    (c : ℝ) (h₀ : loopSum θ n t₀ = c) :
    loopSum θ n t₁ = c := by
  rw [loop_sum_const_of_no_slip θ n ht hcont hclosed hslip, h₀]

end QuantumFluids.SectorTemperature

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.SectorTemperature.count_sum
#print axioms QuantumFluids.SectorTemperature.sectorCount_le
#print axioms QuantumFluids.SectorTemperature.entropy_ge_sector
#print axioms QuantumFluids.SectorTemperature.mediant_le
#print axioms QuantumFluids.SectorTemperature.le_mediant
#print axioms QuantumFluids.SectorTemperature.globalRatio_mem
#print axioms QuantumFluids.SectorTemperature.global_eq_sector_of_single
#print axioms QuantumFluids.SectorTemperature.sector_invariant
