/-
  TopologicalProtection.lean -- why a winding number can act as a CAUSE: it is conserved by every
  evolution that avoids a phase slip, so it is a memory the dynamics cannot erase continuously.

  `VortexWinding.loop_sum_eq_mul` and `QuantizedCirculation` prove that the loop sum of principal phase
  differences is `2π` times an integer (quantization). Quantization alone does not make topology
  causal: an integer that could jump freely would carry no memory. What makes it causal is
  conservation. This file proves conservation, discrete and continuous:

  * `pdiff_shift`           : moving the two endpoint phases by `δa`, `δb` moves the principal
                              difference by `δb - δa`, as long as the result stays in `(-π, π]`;
  * `loop_sum_stable`       : a perturbation `δ` of the loop phases leaves the loop sum (hence the
                              winding number) unchanged, provided no edge is pushed through the branch
                              point -- the quantitative form of "small perturbations cannot change
                              topology";
  * `loop_sum_stable_of_small` : an explicit sufficient condition: every `|δ i| < ε` and every edge step
                              `|pdiff| < π - 2ε`;
  * `circulation_conserved` : the same for the superfluid circulation (a discrete Kelvin theorem whose
                              only ingredient is topology);
  * `loop_sum_const_of_no_slip` : **continuous-time protection.** For phases depending continuously on
                              time, if no edge step ever reaches the branch point `π` on `[t₀, t₁]`,
                              the loop sum at `t₁` equals the loop sum at `t₀`;
  * `slip_of_winding_change`: contrapositive: if the winding changed, some edge step hit `π` at some
                              intermediate time -- a phase slip (Anderson, RMP 38, 298 (1966)).
                              In the continuum limit, that is the passage of a zero of `ψ`, a vortex
                              core, across the loop.

  Negative control (in the scratch file of the round, not here): the stability statement is false
  without its hypothesis; `quarterLoop`-type examples show a winding change when one edge crosses `π`.

  NOT PROVED: the continuum limit (that a discrete edge step reaching `π` corresponds to a zero of a
  smooth `ψ` crossing the loop); anything about energy barriers or rates of phase slips.
-/
import VortexWinding
import QuantizedCirculation

namespace QuantumFluids.TopologicalProtection

open Real QuantumFluids.VortexWinding

/-- Shifting both endpoints moves the principal difference by the difference of the shifts, as long
as the shifted value is still a principal value. -/
theorem pdiff_shift (a b da db : ℝ) (h : pdiff a b + (db - da) ∈ Set.Ioc (-π) π) :
    pdiff (a + da) (b + db) = pdiff a b + (db - da) := by
  unfold pdiff
  rw [toIocMod_eq_iff]
  refine ⟨by rw [show -π + 2 * π = π by ring]; exact h, ?_⟩
  refine ⟨toIocDiv VortexWinding.two_pi_pos (-π) (b - a), ?_⟩
  have := toIocMod_add_toIocDiv_zsmul VortexWinding.two_pi_pos (-π) (b - a)
  linear_combination -this

/-- **Stability of the winding number.** If no edge is pushed through the branch point, the loop sum
of principal differences is unchanged by the perturbation `δ`. -/
theorem loop_sum_stable (θ δ : ℕ → ℝ) (n : ℕ) (hδ : δ n = δ 0)
    (h : ∀ i < n, pdiff (θ i) (θ (i + 1)) + (δ (i + 1) - δ i) ∈ Set.Ioc (-π) π) :
    ∑ i ∈ Finset.range n, pdiff (θ i + δ i) (θ (i + 1) + δ (i + 1))
      = ∑ i ∈ Finset.range n, pdiff (θ i) (θ (i + 1)) := by
  rw [Finset.sum_congr rfl (fun i hi => pdiff_shift _ _ _ _ (h i (Finset.mem_range.1 hi))),
    Finset.sum_add_distrib, Finset.sum_range_sub (fun i => δ i), hδ, sub_self, add_zero]

/-- An explicit sufficient condition: perturbations smaller than `ε` at every site cannot change the
winding of a loop whose every edge step is below `π - 2ε`. -/
theorem loop_sum_stable_of_small (θ δ : ℕ → ℝ) (n : ℕ) (ε : ℝ) (hδ : δ n = δ 0)
    (hsmall : ∀ i ≤ n, |δ i| < ε) (hedge : ∀ i < n, |pdiff (θ i) (θ (i + 1))| < π - 2 * ε) :
    ∑ i ∈ Finset.range n, pdiff (θ i + δ i) (θ (i + 1) + δ (i + 1))
      = ∑ i ∈ Finset.range n, pdiff (θ i) (θ (i + 1)) := by
  refine loop_sum_stable θ δ n hδ (fun i hi => ?_)
  have h1 := hsmall i hi.le; have h2 := hsmall (i + 1) hi; have h3 := hedge i hi
  rw [abs_lt] at h1 h2 h3
  constructor <;> linarith

/-- **A discrete Kelvin theorem from topology alone.** Under the same no-slip condition the
superfluid circulation around the loop is conserved. -/
theorem circulation_conserved (hbar m : ℝ) (θ δ : ℕ → ℝ) (n : ℕ) (hδ : δ n = δ 0)
    (h : ∀ i < n, pdiff (θ i) (θ (i + 1)) + (δ (i + 1) - δ i) ∈ Set.Ioc (-π) π) :
    Circulation.circulation hbar m (fun i => θ i + δ i) n = Circulation.circulation hbar m θ n := by
  unfold Circulation.circulation
  rw [loop_sum_stable θ δ n hδ h]

/-- `pdiff` is continuous in its arguments wherever the principal value is not the branch point `π`. -/
theorem continuousAt_pdiff {a b : ℝ} (h : pdiff a b ≠ π) :
    ContinuousAt (fun p : ℝ × ℝ => pdiff p.1 p.2) (a, b) := by
  have hmod : ¬ (b - a) ≡ -π [PMOD 2 * π] := by
    intro hm
    apply h
    have := (AddCommGroup.modEq_iff_toIocMod_eq_right VortexWinding.two_pi_pos).1 hm.symm
    unfold pdiff; rw [this]; ring
  have hc := continuousAt_toIocMod VortexWinding.two_pi_pos (-π) hmod
  have hf : ContinuousAt (fun p : ℝ × ℝ => p.2 - p.1) (a, b) :=
    (continuous_snd.sub continuous_fst).continuousAt
  show ContinuousAt (fun p : ℝ × ℝ => toIocMod VortexWinding.two_pi_pos (-π) (p.2 - p.1)) (a, b)
  exact ContinuousAt.comp (g := toIocMod VortexWinding.two_pi_pos (-π)) hc hf

/-- The loop sum, as a function of time. -/
noncomputable def loopSum (θ : ℝ → ℕ → ℝ) (n : ℕ) (t : ℝ) : ℝ :=
  ∑ i ∈ Finset.range n, pdiff (θ t i) (θ t (i + 1))

/-- **Continuous-time topological protection.** If every site phase depends continuously on time,
the loop is closed at every time, and no edge step reaches the branch point `π` during `[t₀, t₁]`,
then the loop sum -- `2π` times the winding number -- is the same at `t₁` as at `t₀`. -/
theorem loop_sum_const_of_no_slip (θ : ℝ → ℕ → ℝ) (n : ℕ) {t₀ t₁ : ℝ} (ht : t₀ ≤ t₁)
    (hcont : ∀ i ≤ n, Continuous (fun t => θ t i))
    (hclosed : ∀ t, θ t n = θ t 0)
    (hslip : ∀ t ∈ Set.Icc t₀ t₁, ∀ i < n, pdiff (θ t i) (θ t (i + 1)) ≠ π) :
    loopSum θ n t₁ = loopSum θ n t₀ := by
  -- continuity of the loop sum on [t₀, t₁]
  have hc : ContinuousOn (loopSum θ n) (Set.Icc t₀ t₁) := by
    intro t htm
    apply ContinuousAt.continuousWithinAt
    unfold loopSum ContinuousAt
    refine tendsto_finsetSum _ (fun i hi => ?_)
    have hi' := Finset.mem_range.1 hi
    have hpair : Continuous (fun s => (θ s i, θ s (i + 1))) :=
      (hcont i hi'.le).prodMk (hcont (i + 1) hi')
    exact ContinuousAt.comp (g := fun p : ℝ × ℝ => pdiff p.1 p.2)
      (f := fun s => (θ s i, θ s (i + 1))) (x := t)
      (continuousAt_pdiff (hslip t htm i hi')) hpair.continuousAt
  -- integrality at every time
  have hint : ∀ t, ∃ m : ℤ, loopSum θ n t = (m : ℝ) * (2 * π) := fun t =>
    loop_sum_eq_mul (θ t) n (hclosed t)
  obtain ⟨m₀, hm₀⟩ := hint t₀
  obtain ⟨m₁, hm₁⟩ := hint t₁
  have hpi : (0 : ℝ) < 2 * π := VortexWinding.two_pi_pos
  -- if the integers differ, the intermediate value theorem produces a non-integer value
  by_contra hne
  have hmne : m₀ ≠ m₁ := by rintro rfl; exact hne (by rw [hm₀, hm₁])
  rcases lt_or_gt_of_ne hmne with hlt | hlt
  · have hv : ((m₀ : ℝ) + 1 / 2) * (2 * π) ∈ Set.Icc (loopSum θ n t₀) (loopSum θ n t₁) := by
      rw [hm₀, hm₁]
      have : (m₀ : ℝ) + 1 ≤ m₁ := by exact_mod_cast hlt
      constructor <;> nlinarith
    obtain ⟨s, hs, hsv⟩ := intermediate_value_Icc ht hc hv
    obtain ⟨k, hk⟩ := hint s
    rw [hk] at hsv
    have hk' : (k : ℝ) = m₀ + 1 / 2 := by
      have := mul_right_cancel₀ hpi.ne' hsv; linarith
    have h1 : (m₀ : ℝ) < k := by linarith
    have h2 : (k : ℝ) < m₀ + 1 := by linarith
    have h1' : m₀ < k := by exact_mod_cast h1
    have h2' : k < m₀ + 1 := by exact_mod_cast h2
    omega
  · have hv : ((m₁ : ℝ) + 1 / 2) * (2 * π) ∈ Set.Icc (loopSum θ n t₁) (loopSum θ n t₀) := by
      rw [hm₀, hm₁]
      have : (m₁ : ℝ) + 1 ≤ m₀ := by exact_mod_cast hlt
      constructor <;> nlinarith
    obtain ⟨s, hs, hsv⟩ := intermediate_value_Icc' ht hc hv
    obtain ⟨k, hk⟩ := hint s
    rw [hk] at hsv
    have hk' : (k : ℝ) = m₁ + 1 / 2 := by
      have := mul_right_cancel₀ hpi.ne' hsv; linarith
    have h1 : (m₁ : ℝ) < k := by linarith
    have h2 : (k : ℝ) < m₁ + 1 := by linarith
    have h1' : m₁ < k := by exact_mod_cast h1
    have h2' : k < m₁ + 1 := by exact_mod_cast h2
    omega

/-- **A change of topology requires a phase slip.** If the winding differs between `t₀` and `t₁`, some
edge step reached the branch point at some intermediate time. -/
theorem slip_of_winding_change (θ : ℝ → ℕ → ℝ) (n : ℕ) {t₀ t₁ : ℝ} (ht : t₀ ≤ t₁)
    (hcont : ∀ i ≤ n, Continuous (fun t => θ t i)) (hclosed : ∀ t, θ t n = θ t 0)
    (hchange : loopSum θ n t₁ ≠ loopSum θ n t₀) :
    ∃ t ∈ Set.Icc t₀ t₁, ∃ i < n, pdiff (θ t i) (θ t (i + 1)) = π := by
  by_contra hno
  push Not at hno
  exact hchange (loop_sum_const_of_no_slip θ n ht hcont hclosed hno)

/-! ### The barrier: on an XY ring a phase slip costs a finite energy (mountain pass)

The XY ring `E = -J Σ cos(θ_{i+1} - θ_i)` is the lattice model of a superfluid ring (and the classical
model whose 2D version has the BKT transition). Protection needs more than conservation: it needs the
forbidden event to cost energy. It does: at the moment of the slip one bond sits at `π`, where it
contributes `+J` instead of at least `-J`. -/

/-- XY energy of a ring of `n` sites. -/
noncomputable def xyEnergy (J : ℝ) (θ : ℕ → ℝ) (n : ℕ) : ℝ :=
  -J * ∑ i ∈ Finset.range n, Real.cos (θ (i + 1) - θ i)

/-- The bond energy only sees the phase difference modulo `2π`. -/
theorem cos_pdiff (a b : ℝ) : Real.cos (pdiff a b) = Real.cos (b - a) := by
  rw [pdiff_eq, zsmul_eq_mul]
  exact Real.cos_sub_int_mul_two_pi (b - a) _

/-- **Energy at a phase slip.** If one bond of the ring sits at the branch point `π`, the XY energy is
at least `-(n - 2) J`. -/
theorem slip_energy_ge (J : ℝ) (hJ : 0 ≤ J) (θ : ℕ → ℝ) (n j : ℕ) (hj : j < n)
    (hπ : pdiff (θ j) (θ (j + 1)) = π) :
    -((n : ℝ) - 2) * J ≤ xyEnergy J θ n := by
  unfold xyEnergy
  have hmem : j ∈ Finset.range n := Finset.mem_range.2 hj
  rw [← Finset.add_sum_erase _ _ hmem]
  have hjterm : Real.cos (θ (j + 1) - θ j) = -1 := by
    rw [← cos_pdiff, hπ, Real.cos_pi]
  have hrest : ∑ i ∈ (Finset.range n).erase j, Real.cos (θ (i + 1) - θ i) ≤ (n : ℝ) - 1 := by
    calc ∑ i ∈ (Finset.range n).erase j, Real.cos (θ (i + 1) - θ i)
        ≤ ∑ _i ∈ (Finset.range n).erase j, (1 : ℝ) := Finset.sum_le_sum (fun i _ => Real.cos_le_one _)
      _ = (n : ℝ) - 1 := by
        rw [Finset.sum_const, Finset.card_erase_of_mem hmem, Finset.card_range, nsmul_eq_mul, mul_one]
        rw [Nat.cast_sub (Nat.one_le_of_lt hj)]; simp
  rw [hjterm]
  nlinarith

/-- **Mountain pass for a phase slip.** Along any continuous evolution of the XY ring that changes the
winding number, the energy reaches at least `-(n - 2) J` at some intermediate time. -/
theorem mountain_pass (J : ℝ) (hJ : 0 ≤ J) (θ : ℝ → ℕ → ℝ) (n : ℕ) {t₀ t₁ : ℝ} (ht : t₀ ≤ t₁)
    (hcont : ∀ i ≤ n, Continuous (fun t => θ t i)) (hclosed : ∀ t, θ t n = θ t 0)
    (hchange : loopSum θ n t₁ ≠ loopSum θ n t₀) :
    ∃ t ∈ Set.Icc t₀ t₁, -((n : ℝ) - 2) * J ≤ xyEnergy J (θ t) n := by
  obtain ⟨t, ht', j, hj, hπ⟩ := slip_of_winding_change θ n ht hcont hclosed hchange
  exact ⟨t, ht', slip_energy_ge J hJ (θ t) n j hj hπ⟩

/-- The uniformly twisted ring `θ_i = 2π i / n` has winding one. -/
theorem twisted_loopSum (n : ℕ) (hn : 2 ≤ n) :
    ∑ i ∈ Finset.range n, pdiff (2 * π * i / n) (2 * π * (i + 1 : ℕ) / n) = 2 * π := by
  have hn0 : (0 : ℝ) < n := by exact_mod_cast (by omega : 0 < n)
  have hstep : ∀ i : ℕ, pdiff (2 * π * i / n) (2 * π * (i + 1 : ℕ) / n) = 2 * π / n := by
    intro i
    have hd : 2 * π * ((i + 1 : ℕ) : ℝ) / n - 2 * π * i / n = 2 * π / n := by push_cast; field_simp; ring
    unfold pdiff
    rw [hd, toIocMod_eq_iff]
    refine ⟨⟨?_, ?_⟩, 0, by simp⟩
    · have : 0 < 2 * π / n := by positivity
      linarith [Real.pi_pos]
    · rw [show -π + 2 * π = π by ring, div_le_iff₀ hn0]
      have h2 : (2 : ℝ) ≤ n := by exact_mod_cast hn
      nlinarith [Real.pi_pos]
  rw [Finset.sum_congr rfl (fun i _ => hstep i), Finset.sum_const, Finset.card_range, nsmul_eq_mul]
  field_simp

/-- Its XY energy is `-n J cos(2π/n)`. -/
theorem twisted_energy (J : ℝ) (n : ℕ) :
    xyEnergy J (fun i => 2 * π * i / n) n = -(n : ℝ) * J * Real.cos (2 * π / n) := by
  unfold xyEnergy
  have : ∀ i : ℕ, Real.cos (2 * π * ((i + 1 : ℕ) : ℝ) / n - 2 * π * i / n) = Real.cos (2 * π / n) := by
    intro i; congr 1; push_cast; ring
  rw [Finset.sum_congr rfl (fun i _ => this i), Finset.sum_const, Finset.card_range, nsmul_eq_mul]
  ring

/-- **The barrier is positive for rings of at least 10 sites**: leaving the twisted winding-one state
by a phase slip costs at least `n J cos(2π/n) - (n-2) J ≥ 2J - 2π²J/n > 0`. So the winding is not
only conserved without slips; slips are activated, which is what makes a persistent current persist. -/
theorem barrier_pos (J : ℝ) (hJ : 0 < J) (n : ℕ) (hn : 10 ≤ n) :
    xyEnergy J (fun i => 2 * π * i / n) n < -((n : ℝ) - 2) * J := by
  rw [twisted_energy]
  have hn0 : (10 : ℝ) ≤ n := by exact_mod_cast hn
  have hpos : (0 : ℝ) < n := by linarith
  have hc := Real.one_sub_sq_div_two_le_cos (x := 2 * π / n)
  have hpi : π < 3.15 := Real.pi_lt_d2
  have hpi2 : π ^ 2 < 10 := by nlinarith [Real.pi_pos]
  -- n cos(2π/n) ≥ n - 2π²/n > n - 2
  have key : (n : ℝ) - 2 < n * Real.cos (2 * π / n) := by
    have h1 : (n : ℝ) * (1 - (2 * π / n) ^ 2 / 2) = n - 2 * π ^ 2 / n := by field_simp
    have h2 : 2 * π ^ 2 / n < 2 := by rw [div_lt_iff₀ hpos]; nlinarith
    nlinarith [mul_le_mul_of_nonneg_left hc hpos.le]
  nlinarith

end QuantumFluids.TopologicalProtection

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.TopologicalProtection.pdiff_shift
#print axioms QuantumFluids.TopologicalProtection.loop_sum_stable
#print axioms QuantumFluids.TopologicalProtection.loop_sum_stable_of_small
#print axioms QuantumFluids.TopologicalProtection.circulation_conserved
#print axioms QuantumFluids.TopologicalProtection.continuousAt_pdiff
#print axioms QuantumFluids.TopologicalProtection.loop_sum_const_of_no_slip
#print axioms QuantumFluids.TopologicalProtection.slip_of_winding_change
#print axioms QuantumFluids.TopologicalProtection.cos_pdiff
#print axioms QuantumFluids.TopologicalProtection.slip_energy_ge
#print axioms QuantumFluids.TopologicalProtection.mountain_pass
#print axioms QuantumFluids.TopologicalProtection.twisted_loopSum
#print axioms QuantumFluids.TopologicalProtection.twisted_energy
#print axioms QuantumFluids.TopologicalProtection.barrier_pos
