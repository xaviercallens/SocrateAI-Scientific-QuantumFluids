/-
The dual length of a quantum fluid (design memo docs/designs/DUAL_SCALE_QUANTUM_FLUID.md; CLAIM-024).

For a fluid with excitation energy `ε(k)`, sound speed `c` and `hc := ħc`, define

    ℓ(k) := ε(k)² / (hc² k³).

`ℓ` is measurable: `ε` is what neutron scattering reports and `c` is the `k → 0` slope.
This file proves, for the Bogoliubov dispersion `ε² = (hc·k)² + (hc·k²/ks)²` with
`ks = 2mc/ħ`:

  * `dualLength_bogoliubov` : ℓ = 1/k + k/ks²  — the `R + α'/R` form, with `R = 1/k`, `α' = 1/ks²`;
  * `ell_dual_invariant`    : ℓ is invariant under the involution `k ↦ ks²/k`, which exchanges
                              the phonon and free-particle terms;
  * `ell_ge`, `ell_eq_iff`  : ℓ ≥ 2/ks, with equality exactly at the self-dual point `k = ks`;
  * `dualLength_phonon`, `dualLength_free` : the two limits are exactly `1/k` and `k/ks²`;
  * `not_bogoliubov_of_lt`  : a MEASURED ℓ below `2/ks` refutes the Bogoliubov form at that `k`.
    This is the lemma the He-II measurement uses (measured ℓ/(2/ks) = 0.047 at the roton).

NOT claimed: anything about string theory or T-duality (the shape is AM-GM on two positive terms);
anything about the real ⁴He dispersion, which is measured data, not a theorem; any dynamical statement.
-/

import Mathlib

namespace QuantumFluids.DualLength

/-- `ℓ(k) = ε² / (hc² k³)`, the dual length, written with `ε²` as the argument since only the
square appears. -/
noncomputable def dualLength (hc k epsSq : ℝ) : ℝ := epsSq / (hc ^ 2 * k ^ 3)

/-- Bogoliubov: `ε² = (hc k)² + (hc k²/ks)²`, the Pythagorean sum of the phonon and
free-particle branches. -/
noncomputable def bogoliubovSq (hc ks k : ℝ) : ℝ := (hc * k) ^ 2 + (hc * k ^ 2 / ks) ^ 2

/-- The dual-scale shape `R + α'/R` with `R = 1/k` and `α' = 1/ks²`. -/
noncomputable def ell (ks k : ℝ) : ℝ := 1 / k + k / ks ^ 2

/-- **The phonon branch gives exactly `1/k`.** -/
theorem dualLength_phonon {hc k : ℝ} (hhc : hc ≠ 0) (hk : k ≠ 0) :
    dualLength hc k ((hc * k) ^ 2) = 1 / k := by
  unfold dualLength; field_simp

/-- **The free-particle branch gives exactly `k/ks²`.** -/
theorem dualLength_free {hc ks k : ℝ} (hhc : hc ≠ 0) (hk : k ≠ 0) (hks : ks ≠ 0) :
    dualLength hc k ((hc * k ^ 2 / ks) ^ 2) = k / ks ^ 2 := by
  unfold dualLength; field_simp

/-- **The dual length of the Bogoliubov dispersion is the `R + α'/R` form.** -/
theorem dualLength_bogoliubov {hc ks k : ℝ} (hhc : hc ≠ 0) (hk : k ≠ 0) (hks : ks ≠ 0) :
    dualLength hc k (bogoliubovSq hc ks k) = ell ks k := by
  unfold dualLength bogoliubovSq ell; field_simp

/-- **Duality.** `k ↦ ks²/k` is an involution on positive wavenumbers … -/
theorem dual_involutive {ks k : ℝ} (hk : k ≠ 0) (hks : ks ≠ 0) :
    ks ^ 2 / (ks ^ 2 / k) = k := by
  field_simp

/-- … and `ℓ` is invariant under it: the map exchanges the phonon and free-particle terms. -/
theorem ell_dual_invariant {ks k : ℝ} (hk : k ≠ 0) (hks : ks ≠ 0) :
    ell ks (ks ^ 2 / k) = ell ks k := by
  unfold ell; field_simp; ring

/-- **The dual-scale bound.** `ℓ(k) ≥ 2/ks` for every positive `k`: an effective length that
cannot go below `2/ks = ħ/(mc) = √2 ξ`. -/
theorem ell_ge {ks k : ℝ} (hk : 0 < k) (hks : 0 < ks) : 2 / ks ≤ ell ks k := by
  have key : ell ks k - 2 / ks = (k - ks) ^ 2 / (k * ks ^ 2) := by
    unfold ell; field_simp; ring
  have : 0 ≤ (k - ks) ^ 2 / (k * ks ^ 2) := by positivity
  linarith

/-- **The bound is saturated exactly at the self-dual point** `k = ks`, the fixed point of the
involution. -/
theorem ell_eq_iff {ks k : ℝ} (hk : 0 < k) (hks : 0 < ks) : ell ks k = 2 / ks ↔ k = ks := by
  have key : ell ks k - 2 / ks = (k - ks) ^ 2 / (k * ks ^ 2) := by
    unfold ell; field_simp; ring
  have hpos : 0 < k * ks ^ 2 := by positivity
  constructor
  · intro h
    have h0 : (k - ks) ^ 2 / (k * ks ^ 2) = 0 := by linarith
    have h1 : (k - ks) ^ 2 = 0 := by
      rcases div_eq_zero_iff.mp h0 with h | h
      · exact h
      · exact absurd h (ne_of_gt hpos)
    have := pow_eq_zero_iff (n := 2) (by norm_num) |>.mp h1
    linarith
  · intro h
    subst h
    have : ell k k - 2 / k = 0 := by rw [key]; simp
    linarith

/-- **The falsification lemma.** If the measured dual length at some `k` is strictly below `2/ks`,
then the dispersion at that `k` is not Bogoliubov. This is the form in which the He-II data
(measured `ℓ/(2/ks) = 0.047` at the roton) refutes the dual-scale hypothesis for that fluid. -/
theorem not_bogoliubov_of_lt {hc ks k epsSq : ℝ} (hhc : hc ≠ 0) (hk : 0 < k) (hks : 0 < ks)
    (hmeas : dualLength hc k epsSq < 2 / ks) : epsSq ≠ bogoliubovSq hc ks k := by
  intro h
  rw [h, dualLength_bogoliubov hhc (ne_of_gt hk) (ne_of_gt hks)] at hmeas
  exact absurd hmeas (not_lt.mpr (ell_ge hk hks))

end QuantumFluids.DualLength

#print axioms QuantumFluids.DualLength.dualLength_phonon
#print axioms QuantumFluids.DualLength.dualLength_free
#print axioms QuantumFluids.DualLength.dualLength_bogoliubov
#print axioms QuantumFluids.DualLength.ell_dual_invariant
#print axioms QuantumFluids.DualLength.ell_ge
#print axioms QuantumFluids.DualLength.ell_eq_iff
#print axioms QuantumFluids.DualLength.not_bogoliubov_of_lt
