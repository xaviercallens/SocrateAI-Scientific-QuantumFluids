/-
  ContinuumWinding.lean -- "Rome": the discrete winding number equals the continuum degree.

  `VortexWinding.lean` proves that the sampled loop sum of principal phase differences is an integer
  multiple of `2π`, and leaves open, explicitly, whether that integer is the TRUE topological charge of
  the continuum field ("a statement about sampling, not about the algorithm"). This file closes that
  gap for a closed loop of field values.

  * `pdiff_congr`          : the principal difference depends only on the two angles, not on the
                             representatives `arg` happens to return;
  * `sum_pdiff_telescope`  : when every true phase step is a principal value the loop sum telescopes to
                             the total phase change;
  * `discrete_eq_degree`   : for any continuous closed loop of ANGLES `γ : C(I, Real.Angle)` there is an
                             integer `w` (the degree: the total change of a continuous lift, divided by
                             `2π`) and a sampling threshold `n₀` such that, for every `n ≥ n₀` and every
                             choice of representatives of the `n` sampled angles, the discrete loop sum
                             is exactly `2π w`. The lift is Mathlib's path lifting through the covering
                             `ℝ → ℝ/2πℤ`; the threshold comes from Heine–Cantor;
  * `detector_correct`     : for a continuous, nowhere-vanishing, closed loop of FIELD VALUES
                             `c : C(I, ℂ)`, the phase-winding detector applied to `arg (c (i/n))`
                             returns `2π w` for all `n ≥ n₀`.

  What this settles: the number a GPE code computes around a plaquette is the degree of `ψ/|ψ|`
  along that plaquette's boundary, once the grid resolves the phase (no true step of size ≥ π). What
  a phase slip is in the continuum: the hypothesis `c t ≠ 0` failing -- a zero of `ψ` on the loop,
  where the angle loop, and with it the lift and the degree, cease to exist.

  NOT PROVED: any statement about the field OFF the loop (that the degree counts zeros inside, the
  argument principle) -- Mathlib's pinned version has no argument principle for general continuous
  maps, and the plaquette-additivity of `ScaleResolvedWinding.lean` is the discrete substitute; any
  quantitative link between the grid spacing and `n₀` (that needs a modulus of continuity of `ψ`).
-/
import VortexWinding
import QuantizedCirculation

namespace QuantumFluids.ContinuumWinding

open Real QuantumFluids.VortexWinding unitInterval

/-- The principal difference sees only the angles. -/
theorem pdiff_congr {a a' b b' : ℝ} (ha : (a : Real.Angle) = a') (hb : (b : Real.Angle) = b') :
    pdiff a b = pdiff a' b' := by
  obtain ⟨k, hk⟩ := Real.Angle.angle_eq_iff_two_pi_dvd_sub.1 ha
  obtain ⟨l, hl⟩ := Real.Angle.angle_eq_iff_two_pi_dvd_sub.1 hb
  unfold pdiff
  have : b - a = (b' - a') + (l - k) • (2 * π) := by rw [zsmul_eq_mul]; push_cast; linarith
  rw [this, toIocMod_add_zsmul]

/-- When every true step is a principal value, the loop sum telescopes to the total change. -/
theorem sum_pdiff_telescope (Γ : ℕ → ℝ) (n : ℕ) (h : ∀ i < n, Γ (i + 1) - Γ i ∈ Set.Ioc (-π) π) :
    ∑ i ∈ Finset.range n, pdiff (Γ i) (Γ (i + 1)) = Γ n - Γ 0 := by
  rw [Finset.sum_congr rfl (fun i hi => Circulation.pdiff_of_mem (h i (Finset.mem_range.1 hi)))]
  exact Finset.sum_range_sub Γ n

/-- Two reals with the same angle differ by an integer number of turns. -/
theorem degree_int (x y : ℝ) (h : (x : Real.Angle) = y) : ∃ w : ℤ, x - y = (w : ℝ) * (2 * π) := by
  obtain ⟨k, hk⟩ := Real.Angle.angle_eq_iff_two_pi_dvd_sub.1 h
  exact ⟨k, by rw [hk]; ring⟩

/-- The `i`-th of `n` uniform sample points of the unit interval. -/
noncomputable def sample (n i : ℕ) : I := Set.projIcc 0 1 zero_le_one ((i : ℝ) / n)

theorem sample_zero (n : ℕ) : sample n 0 = 0 := by
  simp [sample]

theorem sample_self (n : ℕ) (hn : 0 < n) : sample n n = 1 := by
  have : ((n : ℕ) : ℝ) / n = 1 := div_self (by exact_mod_cast hn.ne')
  simp [sample, this]

theorem sample_val (n i : ℕ) (hi : i ≤ n) (hn : 0 < n) : (sample n i : ℝ) = (i : ℝ) / n := by
  have hn' : (0 : ℝ) < n := by exact_mod_cast hn
  have hmem : (i : ℝ) / n ∈ Set.Icc (0 : ℝ) 1 := by
    constructor
    · positivity
    · rw [div_le_one hn']; exact_mod_cast hi
  rw [sample, Set.projIcc_of_mem _ hmem]

/-- Consecutive samples are `1/n` apart. -/
theorem dist_sample (n i : ℕ) (hi : i < n) :
    dist (sample n (i + 1)) (sample n i) = 1 / n := by
  have hn : 0 < n := by omega
  rw [Subtype.dist_eq, Real.dist_eq, sample_val n (i + 1) hi hn, sample_val n i hi.le hn]
  have hn' : (0 : ℝ) < n := by exact_mod_cast hn
  rw [abs_of_nonneg (by rw [sub_nonneg]; gcongr; simp)]
  push_cast; field_simp; ring

local instance : Fact ((0 : ℝ) < 2 * π) := ⟨Real.two_pi_pos⟩

/-- **The discrete winding number is the degree.** -/
theorem discrete_eq_degree (γ : C(I, Real.Angle)) (hclosed : γ 1 = γ 0) :
    ∃ w : ℤ, ∃ n₀ : ℕ, 0 < n₀ ∧ ∀ n ≥ n₀, ∀ θ : ℕ → ℝ,
      (∀ i ≤ n, (θ i : Real.Angle) = γ (sample n i)) →
      ∑ i ∈ Finset.range n, pdiff (θ i) (θ (i + 1)) = (w : ℝ) * (2 * π) := by
  -- a continuous lift through the covering ℝ → ℝ/2πℤ
  obtain ⟨e, he⟩ := QuotientAddGroup.mk_surjective (γ 0)
  have cov : IsCoveringMap ((↑) : ℝ → AddCircle (2 * π)) := AddCircle.isCoveringMap_coe (2 * π)
  let Γ : C(I, ℝ) := cov.liftPath γ e he.symm
  have hlift : ∀ t, (Γ t : Real.Angle) = γ t := fun t => congrFun (cov.liftPath_lifts γ e he.symm) t
  -- its degree
  obtain ⟨w, hw⟩ := degree_int (Γ 1) (Γ 0) (by rw [hlift, hlift, hclosed])
  -- Heine–Cantor: a mesh below which every step is below π
  have hu : UniformContinuous Γ := CompactSpace.uniformContinuous_of_continuous Γ.continuous
  obtain ⟨δ, hδ, hδ'⟩ := Metric.uniformContinuous_iff.1 hu π Real.pi_pos
  obtain ⟨n₀, hn₀⟩ := exists_nat_gt (1 / δ)
  refine ⟨w, n₀ + 1, Nat.succ_pos _, fun n hn θ hθ => ?_⟩
  have hnpos : 0 < n := by omega
  have hstep : ∀ i < n, Γ (sample n (i + 1)) - Γ (sample n i) ∈ Set.Ioc (-π) π := by
    intro i hi
    have hd : dist (sample n (i + 1)) (sample n i) < δ := by
      rw [dist_sample n i hi]
      have h1 : (1 : ℝ) / δ < n := by
        calc (1 : ℝ) / δ < n₀ := hn₀
          _ ≤ n := by exact_mod_cast (by omega : n₀ ≤ n)
      have hn' : (0 : ℝ) < n := by exact_mod_cast hnpos
      rw [div_lt_iff₀ hn']; rw [div_lt_iff₀ hδ] at h1; linarith
    have := hδ' hd
    rw [Real.dist_eq, abs_lt] at this
    exact ⟨this.1, this.2.le⟩
  calc ∑ i ∈ Finset.range n, pdiff (θ i) (θ (i + 1))
      = ∑ i ∈ Finset.range n, pdiff (Γ (sample n i)) (Γ (sample n (i + 1))) := by
        refine Finset.sum_congr rfl (fun i hi => ?_)
        have hi' := Finset.mem_range.1 hi
        exact pdiff_congr ((hθ i hi'.le).trans (hlift _).symm) ((hθ (i + 1) hi').trans (hlift _).symm)
    _ = Γ (sample n n) - Γ (sample n 0) := sum_pdiff_telescope (fun i => Γ (sample n i)) n hstep
    _ = Γ 1 - Γ 0 := by rw [sample_self n hnpos, sample_zero]
    _ = (w : ℝ) * (2 * π) := hw

/-- **The phase-winding vortex detector is correct.** For a continuous, nowhere-vanishing, closed loop
of field values, the sampled principal-branch loop sum of `arg` equals `2π` times the degree of the
loop, for every fine enough uniform sampling. -/
theorem detector_correct (c : C(I, ℂ)) (hne : ∀ t, c t ≠ 0) (hclosed : c 1 = c 0) :
    ∃ w : ℤ, ∃ n₀ : ℕ, 0 < n₀ ∧ ∀ n ≥ n₀,
      ∑ i ∈ Finset.range n, pdiff (Complex.arg (c (sample n i))) (Complex.arg (c (sample n (i + 1))))
        = (w : ℝ) * (2 * π) := by
  let γ : C(I, Real.Angle) := ⟨fun t => (Complex.arg (c t) : Real.Angle), by
    rw [continuous_iff_continuousAt]
    intro t
    exact (Complex.continuousAt_arg_coe_angle (hne t)).comp c.continuous.continuousAt⟩
  obtain ⟨w, n₀, hn₀, h⟩ := discrete_eq_degree γ (by simp [γ, hclosed])
  exact ⟨w, n₀, hn₀, fun n hn => h n hn (fun i => Complex.arg (c (sample n i))) (fun i _ => rfl)⟩

end QuantumFluids.ContinuumWinding

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.ContinuumWinding.pdiff_congr
#print axioms QuantumFluids.ContinuumWinding.sum_pdiff_telescope
#print axioms QuantumFluids.ContinuumWinding.degree_int
#print axioms QuantumFluids.ContinuumWinding.sample_zero
#print axioms QuantumFluids.ContinuumWinding.sample_self
#print axioms QuantumFluids.ContinuumWinding.sample_val
#print axioms QuantumFluids.ContinuumWinding.dist_sample
#print axioms QuantumFluids.ContinuumWinding.discrete_eq_degree
#print axioms QuantumFluids.ContinuumWinding.detector_correct
