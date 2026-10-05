/-
  EinsteinRelation.lean -- companion of docs/designs/PGPE_EINSTEIN_PREREG.md.

  The stochastic point-vortex model adds to the dissipative dipole law `d' = −2α d/|d|²` an isotropic noise of
  diffusion constant `D` on the separation vector (`D = 2η`, η the diffusion constant of one vortex). Its
  Fokker–Planck probability current for a density `p` is `J = b p − D ∇p`, `b = −2α d/|d|²`.

  * `zero_flux_iff`: the Kosterlitz–Thouless pair distribution `p = |d|^{−K}` carries zero current at every
    separation if and only if `D K = 2α`. So the three quantities measured by the programme -- the friction α
    (shrinking of a pair), the diffusion D (random walk of the separation) and the stiffness K (current
    correlators, or the pair-size exponent) -- are tied by one identity, and the pre-registered ratio
    `2α/(D K)` equals 1 exactly when the vortex gas can be in detailed-balance equilibrium at stiffness K.
  * `einstein_vortex`: with `K = 2π ρ/T` and `D = 2η` this is `η = α T/(2π ρ)` (hbar = m = k_B = 1), the
    relation proposed for test by Mehdi, Hope, Szigeti and Bradley (2022).
  * `flux_gibbs`: the same statement for any one-dimensional potential, `μ E' ρ + D ρ' = (μ − D/T) E' ρ` for
    `ρ = e^{−E/T}`.

  Textbook statistical mechanics (Einstein 1905); the content is that the test statistic of the
  pre-registration is an identity of the model, with the equilibrium law it presupposes made explicit.
-/
import Mathlib

open Real

namespace EinsteinRelation

/-- The pair distribution `|d|^{−K}`, as a function of the two coordinates. -/
noncomputable def p (K x y : ℝ) : ℝ := (x ^ 2 + y ^ 2) ^ (-K / 2)

/-- `∂p/∂x = −K x/(x² + y²) · p`. -/
theorem hasDerivAt_p_x (K x y : ℝ) (h : x ^ 2 + y ^ 2 ≠ 0) :
    HasDerivAt (fun x => p K x y) (-K * x / (x ^ 2 + y ^ 2) * p K x y) x := by
  have h1 : HasDerivAt (fun x : ℝ => x ^ 2 + y ^ 2) (2 * x) x := by
    simpa using ((hasDerivAt_id x).pow 2).add_const (y ^ 2)
  have h2 := h1.rpow_const (p := -K / 2) (Or.inl h)
  unfold p
  refine h2.congr_deriv ?_
  rw [rpow_sub_one h]
  field_simp

/-- `∂p/∂y = −K y/(x² + y²) · p`. -/
theorem hasDerivAt_p_y (K x y : ℝ) (h : x ^ 2 + y ^ 2 ≠ 0) :
    HasDerivAt (fun y => p K x y) (-K * y / (x ^ 2 + y ^ 2) * p K x y) y := by
  have h1 : HasDerivAt (fun y : ℝ => x ^ 2 + y ^ 2) (2 * y) y := by
    simpa using ((hasDerivAt_id y).pow 2).const_add (x ^ 2)
  have h2 := h1.rpow_const (p := -K / 2) (Or.inl h)
  unfold p
  refine h2.congr_deriv ?_
  rw [rpow_sub_one h]
  field_simp

/-- The two components of the probability current `b p − D ∇p` for the drift `b = −2α d/|d|²`. -/
noncomputable def Jx (α D K x y : ℝ) : ℝ :=
  -2 * α * x / (x ^ 2 + y ^ 2) * p K x y - D * (-K * x / (x ^ 2 + y ^ 2) * p K x y)

noncomputable def Jy (α D K x y : ℝ) : ℝ :=
  -2 * α * y / (x ^ 2 + y ^ 2) * p K x y - D * (-K * y / (x ^ 2 + y ^ 2) * p K x y)

theorem Jx_eq (α D K x y : ℝ) : Jx α D K x y = (D * K - 2 * α) * (x / (x ^ 2 + y ^ 2) * p K x y) := by
  unfold Jx; ring

theorem Jy_eq (α D K x y : ℝ) : Jy α D K x y = (D * K - 2 * α) * (y / (x ^ 2 + y ^ 2) * p K x y) := by
  unfold Jy; ring

/-- Zero probability current at every separation iff `D K = 2α`. -/
theorem zero_flux_iff (α D K : ℝ) :
    (∀ x y : ℝ, x ^ 2 + y ^ 2 ≠ 0 → Jx α D K x y = 0 ∧ Jy α D K x y = 0) ↔ D * K = 2 * α := by
  constructor
  · intro h
    have h1 := (h 1 0 (by norm_num)).1
    rw [Jx_eq] at h1
    have hp : p K 1 0 = 1 := by unfold p; norm_num
    rw [hp] at h1
    norm_num at h1
    linarith
  · intro h x y _
    rw [Jx_eq, Jy_eq, h]
    constructor <;> ring

/-- In vortex units: stiffness `K = 2πρ/T`, separation diffusion `D = 2η`. Detailed balance of the pair gas
holds iff `η = α T/(2πρ)`. -/
theorem einstein_vortex (α η ρ T : ℝ) (hρ : 0 < ρ) (hT : 0 < T) :
    (∀ x y : ℝ, x ^ 2 + y ^ 2 ≠ 0 → Jx α (2 * η) (2 * π * ρ / T) x y = 0 ∧ Jy α (2 * η) (2 * π * ρ / T) x y = 0)
      ↔ η = α * T / (2 * π * ρ) := by
  rw [zero_flux_iff]
  have hπ := pi_pos
  constructor
  · intro h
    field_simp at h ⊢
    linarith
  · intro h
    rw [h]
    field_simp

/-- One-dimensional form for any potential: with `ρ = e^{−E/T}`, the current `μ E' ρ + D ρ'` is
`(μ − D/T) E' ρ`; it vanishes wherever `E' ≠ 0` iff `D = μ T`. -/
theorem flux_gibbs (E : ℝ → ℝ) (E' μ D T x : ℝ) (hT : T ≠ 0) (hE : HasDerivAt E E' x) :
    ∃ ρ' : ℝ, HasDerivAt (fun x => exp (-E x / T)) ρ' x ∧
      μ * E' * exp (-E x / T) + D * ρ' = (μ - D / T) * E' * exp (-E x / T) := by
  refine ⟨exp (-E x / T) * (-E' / T), (hE.neg.div_const T).exp, ?_⟩
  field_simp
  ring

/-- Negative control: with `D K ≠ 2α` the current does not vanish (at separation `(1, 0)`). -/
example : Jx 1 1 1 1 0 ≠ 0 := by
  rw [Jx_eq]
  have hp : p 1 1 0 = 1 := by unfold p; norm_num
  rw [hp]; norm_num

end EinsteinRelation
