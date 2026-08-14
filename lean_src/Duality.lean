/-
=============================================================================
MATHESIS — Duality/SelfDual.lean
The Abstract Self-Dual Bound and Its First Instances (Rung 0 + Rung 1)
=============================================================================

Status  : DRAFT pending human audit (Mathesis L4.4).
Rules   : zero `axiom` declarations (L4.1); every claim kernel-checked or
          explicitly commented as TARGET; footprint audited at end of file.
Purpose : "One theorem, many instances." The programme's dual-scale bound
          (Reff_ge_sqrt), the finite-Fourier support balance, the EOQ
          inventory bound, and the Kramers–Wannier critical point are all
          instances of two elementary facts about products and duals:

            (multiplicative)  C ≤ x·y            →  √C ≤ max(x,y)
            (additive twin)   2·√(x·y) ≤ x + y   (AM–GM, two terms)
            (fixed point)     x = C/x  ↔  x = √C     (x > 0)

          Physics enters only through WHICH product is conserved; the
          mathematics of the bound is domain-free. That is the precise
          sense in which the dual-scale principle "generalizes".

Integration note (QuantumFluids):
  This Duality module is imported by Mathesis (Stream 0). QuantumFluids
  applies it to the quantum-fluid case: the conserved product is
  R · (α'/R) = α' (roton gap × length scale → kinematic viscosity).
  See docs/ROSETTA_ROW.md for term mapping.

=============================================================================
-/

import Mathlib

namespace Mathesis.Duality

/-! ## Part A — The abstract core (Tier A) -/

/-- **A.1 (Self-dual lower bound).** If a product is bounded below by `C`,
the larger factor is at least `√C`. The entire "no scale below `√α'`"
phenomenon, stripped of physics. -/
theorem sqrt_le_max_of_le_mul {C x y : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y)
    (h : C ≤ x * y) : Real.sqrt C ≤ max x y := by
  have hmax : 0 ≤ max x y := le_max_of_le_left hx
  have h2 : C ≤ (max x y) ^ 2 := by
    calc C ≤ x * y := h
      _ ≤ max x y * max x y :=
          mul_le_mul (le_max_left x y) (le_max_right x y) hy hmax
      _ = (max x y) ^ 2 := (pow_two _).symm
  calc Real.sqrt C ≤ Real.sqrt ((max x y) ^ 2) := Real.sqrt_le_sqrt h2
    _ = max x y := Real.sqrt_sq hmax

/-- **A.2 (Dual upper bound).** Symmetrically, the smaller factor is at
most `√C` when the product is at most `C`. -/
theorem min_le_sqrt_of_mul_le {C x y : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y)
    (h : x * y ≤ C) : min x y ≤ Real.sqrt C := by
  have hmin : 0 ≤ min x y := le_min hx hy
  have h2 : (min x y) ^ 2 ≤ C := by
    calc (min x y) ^ 2 = min x y * min x y := pow_two _
      _ ≤ x * y := mul_le_mul (min_le_left x y) (min_le_right x y) hmin hx
      _ ≤ C := h
  calc min x y = Real.sqrt ((min x y) ^ 2) := (Real.sqrt_sq hmin).symm
    _ ≤ Real.sqrt C := Real.sqrt_le_sqrt h2

/-- **A.3 (The sandwich).** An exactly conserved product pins `√C` between
the two dual factors: `min ≤ √C ≤ max`. -/
theorem sqrt_between_duals {C x y : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y)
    (h : x * y = C) : min x y ≤ Real.sqrt C ∧ Real.sqrt C ≤ max x y :=
  ⟨min_le_sqrt_of_mul_le hx hy h.le, sqrt_le_max_of_le_mul hx hy h.ge⟩

/-- **A.4 (Additive twin: two-term AM–GM).** The same conserved product,
read additively: total cost/energy is at least `2√(xy)`. -/
theorem two_sqrt_mul_le_add {x y : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y) :
    2 * Real.sqrt (x * y) ≤ x + y := by
  have h1 : Real.sqrt (x * y) = Real.sqrt x * Real.sqrt y := Real.sqrt_mul hx y
  nlinarith [sq_nonneg (Real.sqrt x - Real.sqrt y), Real.sq_sqrt hx,
             Real.sq_sqrt hy, Real.sqrt_nonneg x, Real.sqrt_nonneg y]

/-- **A.5 (Self-dual fixed point).** For `x > 0`, being one's own dual is
exactly being the fundamental scale: `x = C/x ↔ x = √C`. -/
theorem self_dual_fixed_point {C x : ℝ} (hC : 0 < C) (hx : 0 < x) :
    x = C / x ↔ x = Real.sqrt C := by
  constructor
  · intro h
    have hx' : x ≠ 0 := hx.ne'
    have h2 : x * x = C := by
      field_simp at h
      linarith
    rw [← h2, Real.sqrt_mul_self hx.le]
  · intro h
    subst h
    rw [eq_div_iff (Real.sqrt_pos.mpr hC).ne', Real.mul_self_sqrt hC.le]

/-! ## Part B — Instances (each one line of physics, zero new analysis) -/

/-- **B.1 (Dual-scale metric).** `Reff_ge_sqrt` re-derived as an instance of
A.1: the conserved product is `R · (α'/R) = α'`. Upon Mathesis
consolidation this becomes THE proof, replacing the bespoke one.

**QuantumFluids application:** R is the length scale (coherence length ξ),
α' is the kinematic viscosity. The bound √α' ≤ max(ξ, α'/ξ) shows that
neither ξ nor the quantum-pressure scale can go below √α'. -/
theorem Reff_ge_sqrt_of_selfDual {α R : ℝ} (hα : 0 < α) (hR : 0 < R) :
    Real.sqrt α ≤ max R (α / R) := by
  have hprod : R * (α / R) = α := by
    rw [mul_comm]; exact div_mul_cancel₀ α hR.ne'
  exact sqrt_le_max_of_le_mul hR.le (div_nonneg hα.le hR.le) hprod.ge

/-- **B.2 (Finite support balance — the Donoho–Stark consequence).**
Whenever two support sizes obey a product lower bound `N ≤ a·b` (as the
Donoho–Stark uncertainty principle asserts for a nonzero vector and its
finite Fourier transform), the larger support is at least `√N`.
The product hypothesis is a parameter here; discharging it is TARGET T-DS.

**Physics comment:** This is the mechanism underlying the dual-scale bound:
a product constraint in Fourier space forces a minimum scale. -/
theorem support_balance {a b N : ℕ} (h : N ≤ a * b) :
    Real.sqrt (N : ℝ) ≤ max (a : ℝ) (b : ℝ) :=
  sqrt_le_max_of_le_mul (Nat.cast_nonneg a) (Nat.cast_nonneg b)
    (by exact_mod_cast h)

/-- **B.3 (Operations research: the EOQ bound).** Ordering cost `DK/Q` and
holding cost `hQ/2` have conserved product `DKh/2`; total cost is bounded
below by `2√(DKh/2)`, attained at the self-dual lot size. A century-old
industrial instance of A.4 — the dual-scale bound running in production.

**Cross-domain note:** This is the same structure as DMBT kinetic energy
minimization in quantum fluids: phonon-energy and roton-energy terms trade
off with a fixed product, attaining a minimum at their geometric mean. -/
theorem eoq_lower_bound {D K h Q : ℝ}
    (hD : 0 < D) (hK : 0 < K) (hh : 0 < h) (hQ : 0 < Q) :
    2 * Real.sqrt (D * K * h / 2) ≤ D * K / Q + h * Q / 2 := by
  have hxy : (D * K / Q) * (h * Q / 2) = D * K * h / 2 := by
    field_simp
    ring
  calc 2 * Real.sqrt (D * K * h / 2)
      = 2 * Real.sqrt ((D * K / Q) * (h * Q / 2)) := by rw [hxy]
    _ ≤ D * K / Q + h * Q / 2 :=
        two_sqrt_mul_le_add (by positivity) (by positivity)

/-! ## Part C — Rung 1: the Kramers–Wannier self-dual point (Tier A) -/

/-- **C.1 (Kramers–Wannier critical coupling).** The 2D Ising duality pairs
couplings by `sinh(2K)·sinh(2K*) = 1`. At the self-dual point the fixed-point
equation `sinh(2K)² = 1` (with `K > 0`) forces
`K = log(1 + √2)/2` — the exact critical coupling, located purely by
self-duality. The statistical-mechanics twin of A.5.

**Connection to QuantumFluids:** The Kramers–Wannier duality is analogous
to the macro–micro duality in quantum fluids: both systems have a
self-dual critical point where the two "faces" (low-T and high-T spins;
hydrodynamic and excitation pictures) coincide. -/
theorem kramers_wannier_self_dual {K : ℝ} (hK : 0 < K)
    (hfix : Real.sinh (2 * K) * Real.sinh (2 * K) = 1) :
    K = Real.log (1 + Real.sqrt 2) / 2 := by
  have hpos : 0 < Real.sinh (2 * K) := Real.sinh_pos.mpr (by linarith)
  have h2 : (Real.sinh (2 * K) - 1) * (Real.sinh (2 * K) + 1) = 0 := by
    linear_combination hfix
  have h1 : Real.sinh (2 * K) = 1 := by
    rcases mul_eq_zero.mp h2 with h | h
    · linarith
    · linarith
  have h3 : 2 * K = Real.arsinh 1 := by
    have h4 := Real.arsinh_sinh (2 * K)
    rw [← h4, h1]
  have h5 : Real.arsinh 1 = Real.log (1 + Real.sqrt 2) := by
    rw [Real.arsinh]
    norm_num
  rw [h5] at h3
  linarith

/-! ## TARGETS (statement-level; not asserted; no axioms simulated)

TARGET T-DS (Donoho–Stark on ZMod N — discharges B.2's hypothesis):
  For nonzero `x : ZMod N → ℂ`,
    `N ≤ card (support x) * card (support (dft x))`.
  Route: ‖x̂‖∞ ≤ √|supp x|·‖x‖₂ (Cauchy–Schwarz over the support),
  Plancherel on ZMod, then the support count on x̂. Requires
  `Mathlib.Analysis.Fourier.ZMod` (dft + Parseval); promote after the
  library check. Refinement worth recording (Tao 2005, N prime):
  `card (supp x) + card (supp x̂) ≥ N + 1` — the duality bound HARDENS on
  primes: arithmetic structure strengthening a dual constraint, which is
  the programme's thesis in one line. [LL-6 pass required before citing.]

TARGET T-KW2 (Kramers–Wannier involution): package `K ↦ K*` with
  `sinh(2K)·sinh(2K*) = 1` as an explicit involution on (0,∞) and prove
  A.5-style uniqueness of its fixed point; Tier B finite-lattice partition
  identities go to the exact-arithmetic harness, not here.

TARGET T-QF1 (QuantumFluids instantiation): Import this Duality module and
  instantiate the dual-scale bound on the quantum-fluid product (roton gap
  Δ × length scale ξ = kinematic viscosity α'). Cross-check against DMBT
  phenomenology in EXPRESSION_MEMO_E1.md §3.
-/

/-! ## Audit certificates
Expected on every line: [propext, Classical.choice, Quot.sound] and nothing
else. -/

#print axioms sqrt_le_max_of_le_mul
#print axioms min_le_sqrt_of_mul_le
#print axioms sqrt_between_duals
#print axioms two_sqrt_mul_le_add
#print axioms self_dual_fixed_point
#print axioms Reff_ge_sqrt_of_selfDual
#print axioms support_balance
#print axioms eoq_lower_bound
#print axioms kramers_wannier_self_dual

end Mathesis.Duality
