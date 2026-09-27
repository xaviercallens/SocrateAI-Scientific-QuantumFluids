/-
Quantized circulation: the defining property of a quantum fluid.

In a superfluid the velocity is a phase gradient, `u = (hbar/m) grad S`, so the circulation around a
closed loop is `(hbar/m)` times the total phase change. Because the wavefunction is single valued,
that phase change is a multiple of `2 pi`, and the circulation is therefore a multiple of

    kappa := h/m = 2 pi hbar / m          (the quantum of circulation)

This file proves that, in the discrete form in which it is actually computed from simulation or
experimental data: a loop of sample points, with the phase read at each. It is the statement that
`VortexWinding.loop_sum_eq_mul` was built for, and it is what makes a detected vortex a *quantized*
vortex rather than merely a phase defect.

WHAT IS PROVED
  * `circulation_quantized`  : around any closed loop of sample points, `Gamma = q * kappa`, `q` integer;
  * `circulation_eq_zero_iff`: the circulation vanishes exactly when the winding number does;
  * `abs_circulation_ge`     : a nonzero circulation has magnitude at least `kappa` -- there is no
                               fraction of a quantum;
  * `circulation_quantum_attained` : and `kappa` itself is attained, by an explicit four-point loop,
                               so the bound is sharp and not vacuous.

WHAT IS NOT PROVED: that the discrete loop sum equals the continuum line integral. That is a
statement about sampling a smooth phase (and it fails, by design, when a phase step reaches `pi` --
see `VortexWinding.pdiff_add_rev_eq_two_pi_iff`), not a statement about quantization.
-/

import VortexWinding

namespace QuantumFluids.Circulation

open Real QuantumFluids.VortexWinding

/-- The quantum of circulation `kappa = h/m = 2 pi hbar / m`. For ⁴He it is about
`9.97e-8 m^2/s`; no numerical value is asserted here. -/
noncomputable def kappa (hbar m : ℝ) : ℝ := 2 * π * hbar / m

/-- Discrete circulation of the Madelung velocity around a closed loop of sample points at which the
phase is `S 0, S 1, ..., S n = S 0`. -/
noncomputable def circulation (hbar m : ℝ) (S : ℕ → ℝ) (n : ℕ) : ℝ :=
  (hbar / m) * ∑ i ∈ Finset.range n, pdiff (S i) (S (i + 1))

/-- **Circulation is quantized.** Around any closed loop the circulation is an integer multiple of
the quantum `kappa`. -/
theorem circulation_quantized (hbar m : ℝ) (S : ℕ → ℝ) (n : ℕ) (hclosed : S n = S 0) :
    ∃ q : ℤ, circulation hbar m S n = (q : ℝ) * kappa hbar m := by
  obtain ⟨q, hq⟩ := loop_sum_eq_mul S n hclosed
  refine ⟨q, ?_⟩
  unfold circulation kappa
  rw [hq]
  ring

/-- The circulation vanishes exactly when the winding number does. -/
theorem circulation_eq_zero_iff (hbar m : ℝ) (hhbar : hbar ≠ 0) (hm : m ≠ 0) (S : ℕ → ℝ) (n : ℕ) :
    circulation hbar m S n = 0 ↔ ∑ i ∈ Finset.range n, pdiff (S i) (S (i + 1)) = 0 := by
  unfold circulation
  rw [mul_eq_zero]
  constructor
  · rintro (h | h)
    · exact absurd h (div_ne_zero hhbar hm)
    · exact h
  · intro h; right; exact h

/-- **There is no fraction of a quantum.** A nonzero circulation has magnitude at least `kappa`. -/
theorem abs_circulation_ge (hbar m : ℝ) (hhbar : 0 < hbar) (hm : 0 < m) (S : ℕ → ℝ) (n : ℕ)
    (hclosed : S n = S 0) (hne : circulation hbar m S n ≠ 0) :
    kappa hbar m ≤ |circulation hbar m S n| := by
  obtain ⟨q, hq⟩ := circulation_quantized hbar m S n hclosed
  have hk : 0 < kappa hbar m := by
    unfold kappa; have := pi_pos; positivity
  have hq0 : q ≠ 0 := by
    intro h; rw [h] at hq; simp at hq; exact hne hq
  have h1 : (1 : ℝ) ≤ |(q : ℝ)| := by
    rw [← Int.cast_abs]
    exact_mod_cast Int.one_le_abs (by omega)
  calc kappa hbar m = 1 * kappa hbar m := by ring
    _ ≤ |(q : ℝ)| * kappa hbar m := by exact mul_le_mul_of_nonneg_right h1 hk.le
    _ = |(q : ℝ) * kappa hbar m| := by rw [abs_mul, abs_of_pos hk]
    _ = |circulation hbar m S n| := by rw [hq]

/-- If the true phase difference already lies in `(-π, π]`, `pdiff` returns it unchanged. -/
theorem pdiff_of_mem {a b : ℝ} (h : b - a ∈ Set.Ioc (-π) π) : pdiff a b = b - a := by
  unfold pdiff
  refine (toIocMod_eq_self VortexWinding.two_pi_pos).mpr ?_
  rw [show -π + 2 * π = π from by ring]
  exact h

/-- If it lies one turn below, `pdiff` wraps it up by `2π`. -/
theorem pdiff_of_wrap {a b : ℝ} (h : b - a + 2 * π ∈ Set.Ioc (-π) π) :
    pdiff a b = b - a + 2 * π := by
  unfold pdiff
  rw [← toIocMod_add_right VortexWinding.two_pi_pos (-π) (b - a)]
  refine (toIocMod_eq_self VortexWinding.two_pi_pos).mpr ?_
  rw [show -π + 2 * π = π from by ring]
  exact h

/-- A four-point loop whose phase advances a quarter turn at a time. -/
noncomputable def quarterLoop : ℕ → ℝ := fun i => (i % 4 : ℕ) * (π / 2)

/-- **The quantum is attained**, so `abs_circulation_ge` is sharp rather than vacuous. The witness is
an explicit four-point loop; its closing step wraps by `2π`, which is exactly the branch behaviour
`pdiff` exists to handle. -/
theorem circulation_quantum_attained (hbar m : ℝ) :
    circulation hbar m quarterLoop 4 = kappa hbar m := by
  have hpi := pi_pos
  have e0 : pdiff (quarterLoop 0) (quarterLoop 1) = π / 2 := by
    have : quarterLoop 1 - quarterLoop 0 = π / 2 := by simp [quarterLoop]; try ring
    rw [pdiff_of_mem (by rw [this]; constructor <;> linarith), this]
  have e1 : pdiff (quarterLoop 1) (quarterLoop 2) = π / 2 := by
    have : quarterLoop 2 - quarterLoop 1 = π / 2 := by simp [quarterLoop]; try ring
    rw [pdiff_of_mem (by rw [this]; constructor <;> linarith), this]
  have e2 : pdiff (quarterLoop 2) (quarterLoop 3) = π / 2 := by
    have : quarterLoop 3 - quarterLoop 2 = π / 2 := by simp [quarterLoop]; try ring
    rw [pdiff_of_mem (by rw [this]; constructor <;> linarith), this]
  have e3 : pdiff (quarterLoop 3) (quarterLoop 4) = π / 2 := by
    have h : quarterLoop 4 - quarterLoop 3 = -(3 * π / 2) := by simp [quarterLoop]; try ring
    rw [pdiff_of_wrap (by rw [h]; constructor <;> linarith), h]
    ring
  unfold circulation kappa
  rw [show (4 : ℕ) = 3 + 1 from rfl, Finset.sum_range_succ, Finset.sum_range_succ,
    Finset.sum_range_succ, Finset.sum_range_one, e0, e1, e2, e3]
  ring

end QuantumFluids.Circulation

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.Circulation.circulation_quantized
#print axioms QuantumFluids.Circulation.circulation_eq_zero_iff
#print axioms QuantumFluids.Circulation.abs_circulation_ge
#print axioms QuantumFluids.Circulation.pdiff_of_mem
#print axioms QuantumFluids.Circulation.pdiff_of_wrap
#print axioms QuantumFluids.Circulation.circulation_quantum_attained
