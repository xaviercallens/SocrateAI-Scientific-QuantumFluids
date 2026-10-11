module

public import Mathlib.Analysis.Calculus.ContDiff.Operations
public import Mathlib.Analysis.Calculus.IteratedDeriv.Defs
public import Mathlib.Analysis.Calculus.IteratedDeriv.Lemmas
public import Mathlib.Analysis.Calculus.ParametricIntegral
public import Mathlib.Analysis.SpecialFunctions.Exp
public import Mathlib.Analysis.SpecialFunctions.ExpDeriv
public import Mathlib.Analysis.SpecialFunctions.Exponential
public import Mathlib.Analysis.SpecialFunctions.Pow.Real
public import Mathlib.MeasureTheory.Integral.DominatedConvergence

public section


open Set
open scoped ContDiff

/-- A function `f : ℝ → ℝ` is **completely monotone on a set `s`** if, heuristically, all iterated
derivatives satisfy `(-1)ⁿ f⁽ⁿ⁾ ≥ 0` on `s`. For technical reasons related to unique
differentiability, the precise definition is phrased as the existence of a Taylor series for `f` on
`s` whose `n`th term, evaluated at the all-ones tuple and multiplied by `(-1)ⁿ`, is nonnegative.
See `CompletelyMonotoneOn.iff_iteratedDerivWithin_nonneg` for the equivalence under
`UniqueDiffOn`. -/
def CompletelyMonotoneOn (f : ℝ → ℝ) (s : Set ℝ) : Prop :=
  ∃ p : ℝ → FormalMultilinearSeries ℝ ℝ ℝ,
    HasFTaylorSeriesUpToOn ∞ f p s ∧
    ∀ (n : ℕ) ⦃x : ℝ⦄, x ∈ s → 0 ≤ (-1 : ℝ) ^ n * p x n fun _ ↦ (1 : ℝ)

namespace CompletelyMonotoneOn

variable {f g : ℝ → ℝ} {s : Set ℝ}

/-- A completely monotone function on `s` is `C^∞` on `s`. -/
theorem contDiffOn (hf : CompletelyMonotoneOn f s) : ContDiffOn ℝ ∞ f s := by
  obtain ⟨_, hp, _⟩ := hf
  exact hp.contDiffOn

/-- A globally `C^∞` function whose signed iterated derivatives `(-1)ⁿ f⁽ⁿ⁾` are nonnegative on `s`
is completely monotone on `s`. The set `s` need *not* satisfy `UniqueDiffOn`. -/
theorem of_contDiff (hf : ContDiff ℝ ∞ f)
    (h : ∀ n : ℕ, ∀ x ∈ s, 0 ≤ (-1 : ℝ) ^ n * iteratedDeriv n f x) :
    CompletelyMonotoneOn f s := by
  refine ⟨ftaylorSeries ℝ f, (hf.ftaylorSeries).hasFTaylorSeriesUpToOn s, fun n x hx => ?_⟩
  have := h n x hx
  rw [iteratedDeriv_eq_iteratedFDeriv] at this
  exact this

/-- Under `UniqueDiffOn`, a Taylor witness for a completely monotone function agrees with
`iteratedDerivWithin`, so the signed derivative is nonnegative on `s`. -/
theorem iteratedDerivWithin_nonneg (hf : CompletelyMonotoneOn f s) (hs : UniqueDiffOn ℝ s)
    (n : ℕ) {x : ℝ} (hx : x ∈ s) : 0 ≤ (-1 : ℝ) ^ n * iteratedDerivWithin n f s x := by
  obtain ⟨p, hp, hp_nn⟩ := hf
  have heq : p x n = iteratedFDerivWithin ℝ n f s x :=
    hp.eq_iteratedFDerivWithin_of_uniqueDiffOn (mod_cast le_top) hs hx
  rw [iteratedDerivWithin_eq_iteratedFDerivWithin, ← heq]
  exact hp_nn n hx

/-- Under `UniqueDiffOn`, a function is completely monotone on `s` iff it is `C^∞` on `s` with
every signed iterated derivative `(-1)ⁿ f⁽ⁿ⁾` within `s` nonnegative. -/
theorem iff_iteratedDerivWithin_nonneg (hs : UniqueDiffOn ℝ s) :
    CompletelyMonotoneOn f s ↔
      ContDiffOn ℝ ∞ f s ∧
        ∀ n : ℕ, ∀ x ∈ s, 0 ≤ (-1 : ℝ) ^ n * iteratedDerivWithin n f s x := by
  refine ⟨fun hf => ⟨hf.contDiffOn, fun n x hx => hf.iteratedDerivWithin_nonneg hs n hx⟩, ?_⟩
  rintro ⟨hcont, hnn⟩
  refine ⟨ftaylorSeriesWithin ℝ f s, hcont.ftaylorSeriesWithin hs, fun n x hx => ?_⟩
  have := hnn n x hx
  rw [iteratedDerivWithin_eq_iteratedFDerivWithin] at this
  exact this

/-! ### Closure properties -/

/-- The sum of two completely monotone functions is completely monotone. -/
theorem add (hf : CompletelyMonotoneOn f s) (hg : CompletelyMonotoneOn g s) :
    CompletelyMonotoneOn (f + g) s := by
  obtain ⟨p, hp, hp_nn⟩ := hf
  obtain ⟨q, hq, hq_nn⟩ := hg
  refine ⟨p + q, hp.add hq, fun n x hx => ?_⟩
  have e : ((p + q) x n) (fun _ ↦ (1 : ℝ)) = p x n (fun _ ↦ (1 : ℝ)) + q x n (fun _ ↦ (1 : ℝ)) :=
    rfl
  rw [e, mul_add]
  exact add_nonneg (hp_nn n hx) (hq_nn n hx)

/-- A nonnegative scalar multiple of a completely monotone function is completely monotone. -/
theorem smul {c : ℝ} (hf : CompletelyMonotoneOn f s) (hc : 0 ≤ c) :
    CompletelyMonotoneOn (c • f) s := by
  obtain ⟨p, hp, hp_nn⟩ := hf
  set T : ℝ →L[ℝ] ℝ := c • ContinuousLinearMap.id ℝ ℝ with hT
  have hcomp : (T ∘ f) = c • f := by ext x; simp [hT, smul_eq_mul]
  refine ⟨_, hcomp ▸ hp.continuousLinearMap_comp T, fun n x hx => ?_⟩
  simp only [ContinuousLinearMap.compContinuousMultilinearMap_coe, Function.comp_apply, hT,
    smul_apply, ContinuousLinearMap.id_apply, smul_eq_mul]
  have := mul_nonneg hc (hp_nn n hx)
  calc (0 : ℝ) ≤ c * ((-1 : ℝ) ^ n * p x n fun _ ↦ (1 : ℝ)) := this
    _ = _ := by ring

end CompletelyMonotoneOn

/-- `x ↦ exp (-(c * x))` is completely monotone for `c ≥ 0`. -/
theorem completelyMonotoneOn_exp_neg_mul {c : ℝ} (hc : 0 ≤ c) (s : Set ℝ) :
    CompletelyMonotoneOn (fun x => Real.exp (-(c * x))) s := by
  have hf : ContDiff ℝ ∞ (fun x : ℝ => Real.exp (-(c * x))) := by fun_prop
  refine CompletelyMonotoneOn.of_contDiff hf fun n x _ => ?_
  have h1 : (fun x : ℝ => Real.exp (-(c * x))) = fun x => Real.exp ((-c) * x) := by
    ext x; ring_nf
  rw [h1, iteratedDeriv_exp_const_mul]
  have : (-1 : ℝ) ^ n * ((-c) ^ n * Real.exp (-c * x)) = c ^ n * Real.exp (-c * x) := by
    rw [← mul_assoc, ← mul_pow]; simp
  rw [this]
  positivity

section


open MeasureTheory Filter Real
open scoped Topology

namespace CompletelyMonotoneLaplace

lemma pow_exp_le (r : ℕ) {a s : ℝ} (ha : 0 < a) (hs : 0 ≤ s) :
    s ^ r * exp (-(s * a)) ≤ (r.factorial : ℝ) * (2 / a) ^ r * exp (-(s * (a / 2))) := by
  have hx : 0 ≤ s * (a / 2) := by positivity
  have h1 := Real.pow_div_factorial_le_exp (s * (a / 2)) hx r
  have hf : (0 : ℝ) < r.factorial := by exact_mod_cast r.factorial_pos
  have h2 : (s * (a / 2)) ^ r ≤ r.factorial * exp (s * (a / 2)) := by
    rw [div_le_iff₀ hf] at h1; linarith
  have h3 : s ^ r = (2 / a) ^ r * (s * (a / 2)) ^ r := by
    rw [← mul_pow]; congr 1; field_simp
  have h4 : exp (-(s * a)) = exp (-(s * (a / 2))) * exp (-(s * (a / 2))) := by
    rw [← exp_add]; congr 1; ring
  calc s ^ r * exp (-(s * a)) = (2 / a) ^ r * ((s * (a / 2)) ^ r * exp (-(s * (a / 2)))) * exp (-(s * (a / 2))) := by
        rw [h3, h4]; ring
    _ ≤ (2 / a) ^ r * ((r.factorial * exp (s * (a / 2))) * exp (-(s * (a / 2)))) * exp (-(s * (a / 2))) := by
        gcongr
    _ = _ := by
        have : exp (s * (a / 2)) * exp (-(s * (a / 2))) = 1 := by rw [← exp_add]; simp
        calc _ = (2 / a) ^ r * (r.factorial * (exp (s * (a / 2)) * exp (-(s * (a / 2))))) * exp (-(s * (a / 2))) := by ring
          _ = _ := by rw [this]; ring

section Laplace

variable {μ : ℝ → ℝ}

/-- `(-1)^r`-signed `r`-th moment Laplace transform `t ↦ ∫_0^∞ (-s)^r e^{-st} μ(s) ds`. -/
noncomputable def lap (μ : ℝ → ℝ) (r : ℕ) (t : ℝ) : ℝ :=
  ∫ s in Ioi (0 : ℝ), (-s) ^ r * (exp (-(s * t)) * μ s)

structure LaplaceData (μ : ℝ → ℝ) : Prop where
  nonneg : ∀ s, 0 < s → 0 ≤ μ s
  meas : AEStronglyMeasurable μ (volume.restrict (Ioi (0 : ℝ)))
  integrable : ∀ t, 0 < t → IntegrableOn (fun s => exp (-(s * t)) * μ s) (Ioi (0 : ℝ))

theorem LaplaceData.int_pow (h : LaplaceData μ) (r : ℕ) {t : ℝ} (ht : 0 < t) :
    IntegrableOn (fun s => (-s) ^ r * (exp (-(s * t)) * μ s)) (Ioi (0 : ℝ)) := by
  have hC := (h.integrable (t / 2) (by positivity)).const_mul ((r.factorial : ℝ) * (2 / t) ^ r)
  refine Integrable.mono' hC ?_ ?_
  · exact (by fun_prop : Continuous fun s : ℝ => (-s) ^ r).aestronglyMeasurable.mul
      ((by fun_prop : Continuous fun s : ℝ => exp (-(s * t))).aestronglyMeasurable.mul h.meas)
  · refine (ae_restrict_iff' measurableSet_Ioi).2 (Eventually.of_forall fun s hs => ?_)
    have hs' : 0 < s := hs
    have hm := h.nonneg s hs'
    rw [norm_mul, norm_pow, norm_neg, Real.norm_of_nonneg hs'.le, norm_mul,
      Real.norm_of_nonneg (exp_pos _).le, Real.norm_of_nonneg hm]
    calc s ^ r * (exp (-(s * t)) * μ s) = (s ^ r * exp (-(s * t))) * μ s := by ring
      _ ≤ ((r.factorial : ℝ) * (2 / t) ^ r * exp (-(s * (t / 2)))) * μ s :=
          mul_le_mul_of_nonneg_right (pow_exp_le r ht hs'.le) hm
      _ = _ := by ring

theorem LaplaceData.hasDerivAt (h : LaplaceData μ) (r : ℕ) {t0 : ℝ} (ht0 : 0 < t0) :
    HasDerivAt (lap μ r) (lap μ (r + 1) t0) t0 := by
  have hmeas : ∀ (k : ℕ) (t : ℝ), AEStronglyMeasurable
      (fun s => (-s) ^ k * (exp (-(s * t)) * μ s)) (volume.restrict (Ioi (0 : ℝ))) := fun k t =>
    (by fun_prop : Continuous fun s : ℝ => (-s) ^ k).aestronglyMeasurable.mul
      ((by fun_prop : Continuous fun s : ℝ => exp (-(s * t))).aestronglyMeasurable.mul h.meas)
  set C : ℝ := ((r + 1).factorial : ℝ) * (2 / (t0 / 2)) ^ (r + 1) with hC
  have hint := (h.integrable (t0 / 2 / 2) (by positivity)).const_mul C
  have hbd : ∀ᵐ s ∂(volume.restrict (Ioi (0 : ℝ))), ∀ x ∈ Metric.ball t0 (t0 / 2),
      ‖(-s) ^ (r + 1) * (exp (-(s * x)) * μ s)‖ ≤ C * (exp (-(s * (t0 / 2 / 2))) * μ s) := by
    refine (ae_restrict_iff' measurableSet_Ioi).2 (Eventually.of_forall fun s hs x hx => ?_)
    have hs' : 0 < s := hs
    have hm := h.nonneg s hs'
    have hx' : t0 / 2 < x := by
      have := (Metric.mem_ball.1 hx); rw [Real.dist_eq, abs_lt] at this; linarith
    rw [norm_mul, norm_pow, norm_neg, Real.norm_of_nonneg hs'.le, norm_mul,
      Real.norm_of_nonneg (exp_pos _).le, Real.norm_of_nonneg hm]
    have e1 : exp (-(s * x)) ≤ exp (-(s * (t0 / 2))) := by
      apply exp_le_exp.2; nlinarith
    calc s ^ (r + 1) * (exp (-(s * x)) * μ s)
        = (s ^ (r + 1) * exp (-(s * x))) * μ s := by ring
      _ ≤ (s ^ (r + 1) * exp (-(s * (t0 / 2)))) * μ s := by gcongr
      _ ≤ (C * exp (-(s * (t0 / 2 / 2)))) * μ s :=
          mul_le_mul_of_nonneg_right (pow_exp_le (r + 1) (by positivity) hs'.le) hm
      _ = _ := by ring
  have hdf : ∀ᵐ s ∂(volume.restrict (Ioi (0 : ℝ))), ∀ x ∈ Metric.ball t0 (t0 / 2),
      HasDerivAt (fun t : ℝ => (-s) ^ r * (exp (-(s * t)) * μ s))
        ((-s) ^ (r + 1) * (exp (-(s * x)) * μ s)) x := by
    refine Eventually.of_forall fun s x _ => ?_
    have h1 : HasDerivAt (fun t : ℝ => -(s * t)) (-(s * 1)) x :=
      ((hasDerivAt_id x).const_mul s).neg
    have h2 := (h1.exp).mul_const (μ s) |>.const_mul ((-s) ^ r)
    convert h2 using 1
    ring
  have key := hasDerivAt_integral_of_dominated_loc_of_deriv_le
    (μ := volume.restrict (Ioi (0 : ℝ)))
    (F := fun t s => (-s) ^ r * (exp (-(s * t)) * μ s))
    (F' := fun t s => (-s) ^ (r + 1) * (exp (-(s * t)) * μ s))
    (bound := fun s => C * (exp (-(s * (t0 / 2 / 2))) * μ s))
    (s := Metric.ball t0 (t0 / 2)) (Metric.ball_mem_nhds _ (by positivity))
    (Eventually.of_forall fun t => hmeas r t) (h.int_pow r ht0) (hmeas (r + 1) t0)
    hbd hint hdf
  exact key.2

theorem lap_iteratedDeriv (h : LaplaceData μ) (r : ℕ) :
    ∀ t : ℝ, 0 < t → iteratedDeriv r (lap μ 0) t = lap μ r t := by
  induction r with
  | zero => intro t _; simp
  | succ r ih =>
    intro t ht
    rw [iteratedDeriv_succ]
    have hev : iteratedDeriv r (lap μ 0) =ᶠ[𝓝 t] lap μ r :=
      Filter.eventually_of_mem (isOpen_Ioi.mem_nhds ht) (fun x hx => ih x hx)
    rw [hev.deriv_eq]
    exact (h.hasDerivAt r ht).deriv

theorem lap_contDiffOn (h : LaplaceData μ) :
    ∀ (n : ℕ) (r : ℕ), ContDiffOn ℝ n (lap μ r) (Ioi (0 : ℝ)) := by
  intro n
  induction n with
  | zero =>
    intro r
    refine contDiffOn_zero.2 ?_
    exact fun t ht => (h.hasDerivAt r ht).continuousAt.continuousWithinAt
  | succ n ih =>
    intro r
    have hc : ((n + 1 : ℕ) : WithTop ℕ∞) = (n : WithTop ℕ∞) + 1 := by push_cast; rfl
    rw [hc, contDiffOn_succ_iff_deriv_of_isOpen isOpen_Ioi]
    refine ⟨fun t ht => (h.hasDerivAt r ht).differentiableAt.differentiableWithinAt, ?_, ?_⟩
    · intro hn
      exact absurd hn (by exact_mod_cast WithTop.coe_ne_top)
    · refine (ih (r + 1)).congr (fun t ht => ?_)
      exact (h.hasDerivAt r ht).deriv

end Laplace

end CompletelyMonotoneLaplace

open CompletelyMonotoneLaplace in
/-- **Bernstein, the easy direction.** The Laplace-type integral of a nonnegative measurable
density, finite for all `t > 0`, is completely monotone on `Ioi 0`. -/
theorem completelyMonotoneOn_integral_exp_neg_mul {μ : ℝ → ℝ}
    (hnn : ∀ s, 0 < s → 0 ≤ μ s)
    (hmeas : AEStronglyMeasurable μ (volume.restrict (Ioi (0 : ℝ))))
    (hint : ∀ t, 0 < t → IntegrableOn (fun s => exp (-(s * t)) * μ s) (Ioi (0 : ℝ))) :
    CompletelyMonotoneOn (fun t => ∫ s in Ioi (0 : ℝ), exp (-(s * t)) * μ s) (Ioi 0) := by
  have h : LaplaceData μ := ⟨hnn, hmeas, hint⟩
  have hf : (fun t => ∫ s in Ioi (0 : ℝ), exp (-(s * t)) * μ s) = lap μ 0 := by
    ext t; simp [lap]
  rw [hf]
  refine (CompletelyMonotoneOn.iff_iteratedDerivWithin_nonneg
    (isOpen_Ioi.uniqueDiffOn)).2 ⟨?_, fun n t ht => ?_⟩
  · have : ContDiffOn ℝ (⊤ : ℕ∞) (lap μ 0) (Ioi (0 : ℝ)) := by
      rw [show ((⊤ : ℕ∞) : WithTop ℕ∞) = ∞ from rfl]
      exact contDiffOn_infty.2 (fun n => lap_contDiffOn h n 0)
    exact this
  · rw [iteratedDerivWithin_of_isOpen isOpen_Ioi ht, lap_iteratedDeriv h n t ht]
    unfold lap
    rw [← integral_const_mul]
    refine setIntegral_nonneg measurableSet_Ioi (fun s hs => ?_)
    have := hnn s hs
    have e : (-1 : ℝ) ^ n * ((-s) ^ n * (exp (-(s * t)) * μ s)) = s ^ n * (exp (-(s * t)) * μ s) := by
      rw [← mul_assoc, ← mul_pow]; simp
    rw [e]
    have : 0 < s := hs
    positivity

end
