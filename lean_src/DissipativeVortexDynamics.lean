/-
  DissipativeVortexDynamics.lean -- the dissipative point-vortex model behind the friction, transverse-force
  and Einstein-relation measurements (docs/designs/PGPE_FRICTION_PREREG.md amendment A1,
  PGPE_ALPHAPRIME_PREREG.md, PGPE_EINSTEIN_PREREG.md).

  Model (hbar = m = 1, circulation 2 pi, normal fluid at rest): a vortex of charge q moves at
      v = (1 - alpha') v_s  -  alpha q  z x v_s,
  v_s the superfluid velocity induced at its position by the other vortices. With the vortex Hamiltonian H
  (plane: -sum q_i q_j ln r_ij^2; torus: the Weiss-McWilliams sum) one has v_s,i = -(q_i/2) z x grad_i H, so the
  whole configuration obeys   r' = A(grad H) - (alpha/2) grad H   with A pointwise skew (it contains alpha').

  1. `energy_dissipation`: for ANY such flow, d/dt H(r(t)) = -gamma |grad H|^2, whatever the skew part.
     Consequences used by the analysis: (i) alpha = -(dH/dt) / (2 sum_i |v_s,i|^2) is an estimator of the
     longitudinal friction valid for any number of vortices on the plane or the torus; (ii) it does not depend
     on alpha' -- longitudinal and transverse coefficients are measured by orthogonal observables.
  2. Plane dipole, in coordinates: |d|^2 = |d_0|^2 - 4 alpha t (`dipole_sq_law`), lifetime below
     |d_0|^2/(4 alpha) (`dipole_lifetime_bound`), and the centre moves at speed (1 - alpha')/|d| perpendicular to
     the pair axis (`centre_velocity_identity`): the translation speed measures alpha', the shrinking alpha.
  3. `wind_stall`: in a closed box the pair's impulse goes to the phonons, whose drift u reduces the drive:
     d' = -2 alpha (1/d - w (d_0 - d)), w = 2 pi rho_s/(rho_n L^2). When w d_0^2 > 4 the right-hand side has
     two positive zeros a < b (a + b = d_0, a b = 1/w) and the pair NEVER gets below b: it stalls instead of
     annihilating. The pre-registered wind hypothesis W predicts b from measured rho_n with no free parameter.

  Elementary calculus; nothing here is new mathematics (the gradient-flow structure of dissipative vortex
  motion is classical: Ambegaokar-Halperin-Nelson-Siggia 1980; Kurzke-Melcher-Moser-Spirn 2009 for the
  mixed flow). What is formal is that the estimators used on the data are identities of the model.
-/
import Mathlib

open Set

namespace DissipativeVortexDynamics

/-! ### 1. Energy dissipation for a skew + gradient flow (any number of vortices, plane or torus) -/

section general

variable {X : Type*} [NormedAddCommGroup X] [InnerProductSpace ℝ X] [CompleteSpace X]

/-- `r' = A(∇H) − γ ∇H` with `A` pointwise skew gives `d/dt H(r) = −γ ‖∇H‖²`. -/
theorem energy_dissipation (H : X → ℝ) (gradH : X → X) (hH : ∀ x, HasGradientAt H (gradH x) x)
    (A : X → X) (hA : ∀ v, inner ℝ v (A v) = 0) (γ : ℝ) (r : ℝ → X)
    (hr : ∀ t, HasDerivAt r (A (gradH (r t)) - γ • gradH (r t)) t) (t : ℝ) :
    HasDerivAt (fun t => H (r t)) (-γ * ‖gradH (r t)‖ ^ 2) t := by
  have h := (hH (r t)).hasFDerivAt.comp_hasDerivAt t (hr t)
  have e : (InnerProductSpace.toDual ℝ X (gradH (r t))) (A (gradH (r t)) - γ • gradH (r t))
      = -γ * ‖gradH (r t)‖ ^ 2 := by
    rw [InnerProductSpace.toDual_apply_apply, inner_sub_right, hA, inner_smul_right,
      real_inner_self_eq_norm_sq]; ring
  rw [e] at h
  exact h

/-- With `γ ≥ 0` the vortex energy never increases. -/
theorem energy_antitone (H : X → ℝ) (gradH : X → X) (hH : ∀ x, HasGradientAt H (gradH x) x)
    (A : X → X) (hA : ∀ v, inner ℝ v (A v) = 0) {γ : ℝ} (hγ : 0 ≤ γ) (r : ℝ → X)
    (hr : ∀ t, HasDerivAt r (A (gradH (r t)) - γ • gradH (r t)) t) :
    Antitone (fun t => H (r t)) := by
  have hd := energy_dissipation H gradH hH A hA γ r hr
  refine antitone_of_deriv_nonpos (fun t => (hd t).differentiableAt) (fun t => ?_)
  rw [(hd t).deriv]
  nlinarith [sq_nonneg ‖gradH (r t)‖]

/-- The dissipation rate is the same for two flows that differ only in their skew parts (hence it carries no
information on `α'`): stated at a common configuration. -/
theorem dissipation_indep_of_skew (H : X → ℝ) (gradH : X → X) (hH : ∀ x, HasGradientAt H (gradH x) x)
    (A B : X → X) (hA : ∀ v, inner ℝ v (A v) = 0) (hB : ∀ v, inner ℝ v (B v) = 0) (γ : ℝ)
    (r s : ℝ → X) (hr : ∀ t, HasDerivAt r (A (gradH (r t)) - γ • gradH (r t)) t)
    (hs : ∀ t, HasDerivAt s (B (gradH (s t)) - γ • gradH (s t)) t) (t : ℝ) (hrs : r t = s t) :
    deriv (fun t => H (r t)) t = deriv (fun t => H (s t)) t := by
  rw [(energy_dissipation H gradH hH A hA γ r hr t).deriv,
    (energy_dissipation H gradH hH B hB γ s hs t).deriv, hrs]

end general

/-! ### 2. The plane dipole in coordinates

`p = (px, py)` the `+` vortex, `m = (mx, my)` the `−` vortex, `d = p − m`, `r2 = |d|²`. The superfluid velocity
at either vortex is `V = (dy, −dx)/r2`. -/

section dipole

variable (px py mx my : ℝ → ℝ) (α α' : ℝ)

/-- squared separation -/
noncomputable def r2 (t : ℝ) : ℝ := (px t - mx t) ^ 2 + (py t - my t) ^ 2

variable {px py mx my α α'} {T : ℝ}
  (hpx : ∀ t ∈ Icc (0 : ℝ) T, HasDerivAt px
    ((1 - α') * (py t - my t) / r2 px py mx my t - α * (px t - mx t) / r2 px py mx my t) t)
  (hpy : ∀ t ∈ Icc (0 : ℝ) T, HasDerivAt py
    (-(1 - α') * (px t - mx t) / r2 px py mx my t - α * (py t - my t) / r2 px py mx my t) t)
  (hmx : ∀ t ∈ Icc (0 : ℝ) T, HasDerivAt mx
    ((1 - α') * (py t - my t) / r2 px py mx my t + α * (px t - mx t) / r2 px py mx my t) t)
  (hmy : ∀ t ∈ Icc (0 : ℝ) T, HasDerivAt my
    (-(1 - α') * (px t - mx t) / r2 px py mx my t + α * (py t - my t) / r2 px py mx my t) t)
  (hpos : ∀ t ∈ Icc (0 : ℝ) T, r2 px py mx my t ≠ 0)
include hpx hpy hmx hmy hpos

/-- `d/dt |d|² = −4α`, whatever `α'`. -/
theorem r2_hasDerivAt (t : ℝ) (ht : t ∈ Icc (0 : ℝ) T) : HasDerivAt (r2 px py mx my) (-4 * α) t := by
  have hx := ((hpx t ht).sub (hmx t ht)).pow 2
  have hy := ((hpy t ht).sub (hmy t ht)).pow 2
  have h := hx.add hy
  have hne := hpos t ht
  unfold r2 at hne ⊢
  refine h.congr_deriv ?_
  simp only [r2, Pi.sub_apply]
  field_simp
  ring

/-- The `d²` law on the whole interval of existence. -/
theorem dipole_sq_law (t : ℝ) (ht : t ∈ Icc (0 : ℝ) T) :
    r2 px py mx my t = r2 px py mx my 0 - 4 * α * t := by
  have hT : (0 : ℝ) ≤ T := ht.1.trans ht.2
  have key : ∀ x ∈ Icc (0 : ℝ) T, HasDerivAt (fun s => r2 px py mx my s + 4 * α * s) 0 x := fun x hx => by
    have h := (r2_hasDerivAt hpx hpy hmx hmy hpos x hx).add ((hasDerivAt_id x).const_mul (4 * α))
    refine h.congr_deriv ?_
    ring
  have hc : ContinuousOn (fun s => r2 px py mx my s + 4 * α * s) (Icc 0 T) :=
    fun x hx => (key x hx).continuousAt.continuousWithinAt
  have := constant_of_has_deriv_right_zero hc
    (fun x hx => (key x ⟨hx.1, hx.2.le⟩).hasDerivWithinAt) t ht
  simp only [mul_zero, add_zero] at this
  linarith

/-- A pair with `α > 0` cannot survive to `|d_0|²/(4α)`: the lifetime is bounded by the `d²` law. -/
theorem dipole_lifetime_bound (hα : 0 < α) (hT : 0 ≤ T) : T < r2 px py mx my 0 / (4 * α) := by
  have hlaw := dipole_sq_law hpx hpy hmx hmy hpos T ⟨hT, le_refl T⟩
  have hTpos : 0 < r2 px py mx my T := by
    have := hpos T ⟨hT, le_refl T⟩
    have h0 : 0 ≤ r2 px py mx my T := by unfold r2; positivity
    exact lt_of_le_of_ne h0 (Ne.symm this)
  rw [lt_div_iff₀ (by positivity)]
  linarith

/-- The centre `c = (p + m)/2` moves at `(1 − α') (dy, −dx)/|d|²`: perpendicular to the pair axis, at speed
`(1 − α')/|d|`, whatever `α`. The scalar identity `c' · (dy, −dx) = 1 − α'` is the estimator of `α'`. -/
theorem centre_velocity_identity (t : ℝ) (ht : t ∈ Icc (0 : ℝ) T) :
    ∃ cx' cy' : ℝ, HasDerivAt (fun s => (px s + mx s) / 2) cx' t ∧ HasDerivAt (fun s => (py s + my s) / 2) cy' t ∧
      cx' * (py t - my t) - cy' * (px t - mx t) = 1 - α' ∧
      cx' * (px t - mx t) + cy' * (py t - my t) = 0 ∧
      (cx' ^ 2 + cy' ^ 2) * r2 px py mx my t = (1 - α') ^ 2 := by
  have hne := hpos t ht
  refine ⟨(1 - α') * (py t - my t) / r2 px py mx my t, -(1 - α') * (px t - mx t) / r2 px py mx my t, ?_, ?_, ?_, ?_, ?_⟩
  · refine (((hpx t ht).add (hmx t ht)).div_const 2).congr_deriv ?_
    ring
  · refine (((hpy t ht).add (hmy t ht)).div_const 2).congr_deriv ?_
    ring
  · have e : r2 px py mx my t = (px t - mx t) ^ 2 + (py t - my t) ^ 2 := rfl
    field_simp
    rw [e]; ring
  · field_simp
    ring
  · have e : r2 px py mx my t = (px t - mx t) ^ 2 + (py t - my t) ^ 2 := rfl
    field_simp
    rw [e]; ring

end dipole

/-! ### 3. The phonon wind of a closed box: stall instead of annihilation -/

/-- `d' = −c (d − a)(d − b)/d` with `0 < a < b`, `c > 0` (this is `d' = −2α(1/d − w(d_0 − d))` with
`a + b = d_0`, `a b = 1/w`, `c = 2 α w`). A pair that starts at or above `b` stays at or above `b` for ever. -/
theorem wind_stall {a b c : ℝ} (ha : 0 < a) (hab : a < b) (hc : 0 < c) (d : ℝ → ℝ)
    (hd : ∀ t, HasDerivAt d (-c * (d t - a) * (d t - b) / d t) t) (h0 : b ≤ d 0) :
    ∀ t, 0 ≤ t → b ≤ d t := by
  intro t ht
  by_contra hlt
  push Not at hlt
  set ε := min ((b - d t) / 2) ((b - a) / 2) with hε
  have hεpos : 0 < ε := lt_min (by linarith) (by linarith)
  have hε1 : ε ≤ (b - d t) / 2 := min_le_left _ _
  have hε2 : ε ≤ (b - a) / 2 := min_le_right _ _
  have hfence : ∀ ⦃x⦄, x ∈ Icc (0 : ℝ) t → (fun s => -d s) x ≤ (fun _ => -(b - ε)) x := by
    refine image_le_of_deriv_right_lt_deriv_boundary (f' := fun s => -(-c * (d s - a) * (d s - b) / d s))
      (B' := fun _ => 0) (fun x _ => (hd x).neg.continuousAt.continuousWithinAt)
      (fun x _ => (hd x).neg.hasDerivWithinAt) (show -d 0 ≤ -(b - ε) by linarith)
      (fun x => hasDerivAt_const x _) ?_
    intro x _ hx
    have hx' : -d x = -(b - ε) := hx
    have hdx : d x = b - ε := by linarith
    have hpos : 0 < d x := by rw [hdx]; linarith
    have h1 : d x - a > 0 := by rw [hdx]; linarith
    have h2 : d x - b < 0 := by rw [hdx]; linarith
    have : 0 < -c * (d x - a) * (d x - b) / d x := by
      apply div_pos _ hpos
      nlinarith [mul_pos hc h1]
    show -(-c * (d x - a) * (d x - b) / d x) < 0
    linarith
  have h' : -d t ≤ -(b - ε) := hfence ⟨ht, le_refl t⟩
  linarith

/-- General form (torus drive, PGPE_COUNTERFLOW_PREREG.md): `d' = −c · g(d)` for ANY drive `g` that is negative on an
interval `(a, b)` just below the stall point `b` -- e.g. `g(d) = v_pair(d) − u(d)` with the torus pair speed and the
measured momentum factor. A pair starting at or above `b` never falls below `b`. -/
theorem stall_of_drive_sign {a b c : ℝ} (hab : a < b) (hc : 0 < c) (g : ℝ → ℝ) (hg : ∀ x, a < x → x < b → g x < 0)
    (d : ℝ → ℝ) (hd : ∀ t, HasDerivAt d (-c * g (d t)) t) (h0 : b ≤ d 0) :
    ∀ t, 0 ≤ t → b ≤ d t := by
  intro t ht
  by_contra hlt
  push Not at hlt
  set ε := min ((b - d t) / 2) ((b - a) / 2) with hε
  have hεpos : 0 < ε := lt_min (by linarith) (by linarith)
  have hε1 : ε ≤ (b - d t) / 2 := min_le_left _ _
  have hε2 : ε ≤ (b - a) / 2 := min_le_right _ _
  have hfence : ∀ ⦃x⦄, x ∈ Icc (0 : ℝ) t → (fun s => -d s) x ≤ (fun _ => -(b - ε)) x := by
    refine image_le_of_deriv_right_lt_deriv_boundary (f' := fun s => -(-c * g (d s)))
      (B' := fun _ => 0) (fun x _ => (hd x).neg.continuousAt.continuousWithinAt)
      (fun x _ => (hd x).neg.hasDerivWithinAt) (show -d 0 ≤ -(b - ε) by linarith)
      (fun x => hasDerivAt_const x _) ?_
    intro x _ hx
    have hx' : -d x = -(b - ε) := hx
    have hdx : d x = b - ε := by linarith
    have hneg : g (d x) < 0 := hg _ (by rw [hdx]; linarith) (by rw [hdx]; linarith)
    have : 0 < -c * g (d x) := by nlinarith
    show -(-c * g (d x)) < 0
    linarith
  have h' : -d t ≤ -(b - ε) := hfence ⟨ht, le_refl t⟩
  linarith

/-- The plane case is the instance `g(x) = (x − a)(x − b)/x` of the general theorem. -/
example {a b c : ℝ} (ha : 0 < a) (hab : a < b) (hc : 0 < c) (d : ℝ → ℝ)
    (hd : ∀ t, HasDerivAt d (-c * ((d t - a) * (d t - b) / d t)) t) (h0 : b ≤ d 0) : ∀ t, 0 ≤ t → b ≤ d t :=
  stall_of_drive_sign hab hc (fun x => (x - a) * (x - b) / x)
    (fun x hax hxb => div_neg_of_neg_of_pos (mul_neg_of_pos_of_neg (by linarith) (by linarith)) (by linarith)) d hd h0

/-- Negative control: the hypothesis `b ≤ d 0` cannot be dropped -- the constant flow at the lower zero `a` is a
solution that stays strictly below `b`. -/
example {a b c : ℝ} (hab : a < b) :
    (∀ t : ℝ, HasDerivAt (fun _ : ℝ => a) (-c * (a - a) * (a - b) / a) t) ∧ ¬ (b ≤ a) := by
  refine ⟨fun t => ?_, not_le.mpr hab⟩
  simpa using hasDerivAt_const t a

end DissipativeVortexDynamics
