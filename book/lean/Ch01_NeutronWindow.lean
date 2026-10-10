/-
Ch01_NeutronWindow.lean -- NEW for the book "Quantum Fluids in Lean 4: a tribute to Henri Godfrin", chapter 1.

What a neutron can reach.  A neutron of wave vector `ki` scatters from a sample and leaves with wave vector `kf`.  The sample
receives the wave-vector transfer `Q = ki - kf` (momentum `ħ Q`) and the energy `E ki - E kf`, where the neutron kinetic energy is
`E k = ħ² ‖k‖² / (2 m)`.  Whatever the scattering angle, the three vectors `ki`, `kf`, `Q` form a triangle, so
the triangle inequality alone bounds what a spectrometer can see:

  * `q_bounds`                  :  |‖ki‖ - ‖kf‖| ≤ ‖Q‖ ≤ ‖ki‖ + ‖kf‖;
  * `transfer_le_window`        :  the energy given to the sample is at most  E_i - ħ² (‖ki‖ - ‖Q‖)² / (2m)
                                   (the parabola that bounds the kinematic region in the (Q, ħω) plane);
  * `min_incident_wavevector`   :  to create an excitation of energy ε at wave-vector transfer Q > 0 the incident wave number must satisfy
                                       ‖ki‖  ≥  Q/2 + m ε / (ħ² Q).
                                   Multiplying by ħ/m: the neutron speed must be at least  ħQ/2m  (recoil)  plus  ε/ħQ  (the phase velocity
                                   of the excitation).  This is the inequality behind the colour scale of the book's Figure 1.2.

Scope.  This is the NECESSARY condition: a point of the (Q, ε) plane below the parabola is not claimed to be reachable (that needs a
triangle with three prescribed sides, a separate and elementary construction that is not formalised here).  Nothing here is
a statement about any actual instrument, and nothing is a statement about helium: it is the geometry of a collision.
-/
import Mathlib

namespace QuantumFluids.NeutronWindow

variable {V : Type*} [NormedAddCommGroup V]

/-- Kinetic energy `ħ² ‖k‖² / (2 m)` of a neutron of wave vector `k`. -/
noncomputable def energy (hbar m : ℝ) (k : V) : ℝ := hbar ^ 2 * ‖k‖ ^ 2 / (2 * m)

/-- **The scattering triangle.** The wave-vector transfer `Q = ki - kf` is at least `|‖ki‖ - ‖kf‖|` and at most `‖ki‖ + ‖kf‖`. -/
theorem q_bounds (ki kf : V) :
    |‖ki‖ - ‖kf‖| ≤ ‖ki - kf‖ ∧ ‖ki - kf‖ ≤ ‖ki‖ + ‖kf‖ :=
  ⟨abs_norm_sub_norm_le ki kf, norm_sub_le ki kf⟩

/-- **The kinematic window.** The energy `E ki - E kf` given to the sample is at most `ħ² (2 ‖ki‖ Q - Q²) / (2m)` with `Q = ‖ki - kf‖`,
i.e. `E_i - ħ² (‖ki‖ - Q)² / (2m)`: a downward parabola in `Q`, with apex `E_i` at `Q = ‖ki‖`. -/
theorem transfer_le_window (hbar m : ℝ) (hm : 0 < m) (ki kf : V) :
    energy hbar m ki - energy hbar m kf
      ≤ hbar ^ 2 * (2 * ‖ki‖ * ‖ki - kf‖ - ‖ki - kf‖ ^ 2) / (2 * m) := by
  have h1 : |‖ki‖ - ‖ki - kf‖| ≤ ‖kf‖ := by
    have := abs_norm_sub_norm_le ki (ki - kf)
    rwa [sub_sub_cancel] at this
  have h2 : (‖ki‖ - ‖ki - kf‖) ^ 2 ≤ ‖kf‖ ^ 2 :=
    sq_le_sq' (abs_le.mp h1).1 (abs_le.mp h1).2
  have key : ‖ki‖ ^ 2 - ‖kf‖ ^ 2 ≤ 2 * ‖ki‖ * ‖ki - kf‖ - ‖ki - kf‖ ^ 2 := by nlinarith [h2]
  unfold energy
  rw [← sub_div, ← mul_sub]
  exact div_le_div_of_nonneg_right (mul_le_mul_of_nonneg_left key (sq_nonneg hbar)) (by positivity)

/-- **Least incident wave number.** To give the sample the wave-vector transfer `Q = ‖ki - kf‖ > 0` and the energy `ε = E ki - E kf`,
the incident wave number is at least `Q/2 + m ε / (ħ² Q)`.  Equivalently the neutron speed `ħ ‖ki‖ / m` is at least
`ħ Q / (2m) + ε / (ħ Q)`. -/
theorem min_incident_wavevector (hbar m : ℝ) (hbar0 : 0 < hbar) (hm : 0 < m) (ki kf : V) (hQ : 0 < ‖ki - kf‖) :
    ‖ki - kf‖ / 2 + m * (energy hbar m ki - energy hbar m kf) / (hbar ^ 2 * ‖ki - kf‖) ≤ ‖ki‖ := by
  have h := transfer_le_window hbar m hm ki kf
  have hden : 0 < hbar ^ 2 * ‖ki - kf‖ := by positivity
  have h3 : m * (energy hbar m ki - energy hbar m kf) / (hbar ^ 2 * ‖ki - kf‖) ≤ ‖ki‖ - ‖ki - kf‖ / 2 := by
    rw [div_le_iff₀ hden]
    have h4 := mul_le_mul_of_nonneg_left h hm.le
    have h5 : m * (hbar ^ 2 * (2 * ‖ki‖ * ‖ki - kf‖ - ‖ki - kf‖ ^ 2) / (2 * m))
        = (‖ki‖ - ‖ki - kf‖ / 2) * (hbar ^ 2 * ‖ki - kf‖) := by
      field_simp
    linarith
  linarith

end QuantumFluids.NeutronWindow

-- axiom audit
#print axioms QuantumFluids.NeutronWindow.q_bounds
#print axioms QuantumFluids.NeutronWindow.transfer_le_window
#print axioms QuantumFluids.NeutronWindow.min_incident_wavevector
