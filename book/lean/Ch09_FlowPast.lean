/-
Ch09_FlowPast.lean -- NEW for the book chapter 9 ("Flow past an obstacle").  Not part of the QuantumFluids library.

Elementary statements about the model whose reproduction the chapter reports (units hbar = m = mu = 1, density at
infinity n = 1, hence sound speed c = 1):

  * `bogEps_ge_sound`, `landau_uniform_gp`: the Bogoliubov dispersion eps(k) = k sqrt(1 + k^2/4) of the uniform
    fluid lies on or above the sound line, so its Landau velocity inf_k eps(k)/k is exactly the sound speed 1
    (it is approached as k -> 0, and never undercut).  The obstacle moves at 0.55 < 1: the *uniform-fluid* Landau
    criterion forbids any excitation.
  * `supersonic_iff`: in a steady flow with local flux j = n u and local sound speed sqrt n, the flow is locally
    supersonic (u > sqrt n) iff n^3 < j^2.  A penetrable obstacle that depletes the density below j^(2/3) therefore
    breaks the premise of the uniform-fluid criterion.
  * `sonic_speed_threshold`: with Bernoulli's relation n + u^2/2 + V = B at a point (no flux conservation needed), the flow
    is locally supersonic iff u^2 > (2/3)(B - V); the threshold speed depends on the potential V only.
  * `bernoulli_min`, `bernoulli_eq_iff`, `barrier_height_bound`: in a steady one-dimensional channel flow of conserved
    flux j = s^(3/2), Bernoulli's function j^2/(2 n^2) + n is bounded below by (3/2) s with equality exactly at the
    sonic density n = s; hence no steady state exists over a barrier higher than (1 - s)^2 (s + 2)/2.  The Bernoulli
    relation is a HYPOTHESIS of `barrier_height_bound` (it holds for the stationary hydrodynamic limit; nothing here
    derives it from the Gross-Pitaevskii equation).
  * `ramp_overshoot`: the finite sum behind the O(dt) velocity-ramp convention of the reference code:
    sum_{i=1}^n (a i h) h = a (n h)^2 / 2 + a h^2 n / 2, an overshoot of a h^2 n / 2 over the integral.

No statement here is about the Gross-Pitaevskii dynamics itself, nor about vortices.
Checked with Lean 4.34.0-rc2 and the Mathlib of tag v4.34.0-rc2 (`lake env lean`), no `sorry`.
-/
import Mathlib

namespace QuantumFluids.FlowPast

open Finset

/-- Bogoliubov dispersion of the uniform fluid in the units `hbar = m = mu = 1`, `n = 1`: `eps(k)^2 = (k^2/2)(k^2/2 + 2)`. -/
noncomputable def bogEps (k : ℝ) : ℝ := k * Real.sqrt (1 + k ^ 2 / 4)

/-- The dispersion lies on or above the sound line `c k` with `c = 1`. -/
theorem bogEps_ge_sound {k : ℝ} (hk : 0 ≤ k) : 1 * k ≤ bogEps k := by
  unfold bogEps
  have h1 : (1 : ℝ) ≤ Real.sqrt (1 + k ^ 2 / 4) := by
    rw [show (1 : ℝ) = Real.sqrt 1 by simp]
    exact Real.sqrt_le_sqrt (by nlinarith [sq_nonneg k])
  nlinarith

/-- **Landau velocity of the uniform Gross-Pitaevskii fluid is the sound speed.** `eps(k)/k >= 1` for every `k > 0`,
and for every `delta > 0` some `k > 0` has `eps(k)/k < 1 + delta`. -/
theorem landau_uniform_gp :
    (∀ k : ℝ, 0 < k → 1 ≤ bogEps k / k) ∧
    (∀ δ : ℝ, 0 < δ → ∃ k : ℝ, 0 < k ∧ bogEps k / k < 1 + δ) := by
  refine ⟨fun k hk => ?_, fun δ hδ => ?_⟩
  · rw [le_div_iff₀ hk]
    simpa using bogEps_ge_sound hk.le
  · refine ⟨Real.sqrt (2 * δ), Real.sqrt_pos.mpr (by positivity), ?_⟩
    have hk : (0 : ℝ) < Real.sqrt (2 * δ) := Real.sqrt_pos.mpr (by positivity)
    have hsq : Real.sqrt (2 * δ) ^ 2 = 2 * δ := Real.sq_sqrt (by positivity)
    have e : bogEps (Real.sqrt (2 * δ)) / Real.sqrt (2 * δ) = Real.sqrt (1 + δ / 2) := by
      unfold bogEps
      rw [hsq, mul_div_cancel_left₀ _ hk.ne']
      congr 1
      ring
    rw [e, Real.sqrt_lt' (by positivity)]
    nlinarith [sq_nonneg δ]

/-- **Local supersonic criterion.** For a steady one-dimensional flow of density `n > 0` and flux `j = n u > 0`
(so `u = j / n`) and local sound speed `sqrt n`: `sqrt n < j / n` iff `n^3 < j^2`. -/
theorem supersonic_iff {n j : ℝ} (hn : 0 < n) (hj : 0 < j) :
    Real.sqrt n < j / n ↔ n ^ 3 < j ^ 2 := by
  rw [lt_div_iff₀ hn]
  have hs : (Real.sqrt n * n) ^ 2 = n ^ 3 := by
    rw [mul_pow, Real.sq_sqrt hn.le]; ring
  rw [← hs]
  exact (sq_lt_sq₀ (by positivity) hj.le).symm

/-- **Local sonic speed in the stationary hydrodynamic limit.**  If the density `n`, the speed `u` and the potential `V`
at a point obey Bernoulli's relation `n + u^2/2 + V = B` (`B = 1 + v^2/2` for a fluid of density `1` at speed `v`
far from the obstacle), the flow is locally supersonic (`n < u^2`) iff `u^2 > (2/3) (B - V)`.  No conservation of flux
is needed; for `V = 0` this is the critical speed `u^2 = 2/3 + v^2/3` of the flow past a disk (Josserand, Pomeau, Rica). -/
theorem sonic_speed_threshold {n u V B : ℝ} (hB : n + u ^ 2 / 2 + V = B) :
    n < u ^ 2 ↔ 2 / 3 * (B - V) < u ^ 2 := by
  constructor <;> intro h <;> linarith

/-- **Bernoulli's function at fixed flux is minimised at the sonic point.**  In a steady one-dimensional flow of flux
`j` write `j^2 = s^3` (`s > 0` is the *sonic density*, the density at which `u = sqrt n`).  The energy per particle
`j^2/(2 n^2) + n` of a state of density `n > 0` is at least `(3/2) s`, with equality exactly at `n = s`. -/
theorem bernoulli_min {s n : ℝ} (hs : 0 < s) (hn : 0 < n) :
    3 / 2 * s ≤ s ^ 3 / (2 * n ^ 2) + n := by
  have h : s ^ 3 / (2 * n ^ 2) + n - 3 / 2 * s = (n - s) ^ 2 * (2 * n + s) / (2 * n ^ 2) := by
    field_simp
    ring
  have h0 : 0 ≤ (n - s) ^ 2 * (2 * n + s) / (2 * n ^ 2) := by positivity
  linarith

/-- The equality case of `bernoulli_min`: the minimum is attained only at the sonic point `n = s`. -/
theorem bernoulli_eq_iff {s n : ℝ} (hs : 0 < s) (hn : 0 < n) :
    s ^ 3 / (2 * n ^ 2) + n = 3 / 2 * s ↔ n = s := by
  have h : s ^ 3 / (2 * n ^ 2) + n - 3 / 2 * s = (n - s) ^ 2 * (2 * n + s) / (2 * n ^ 2) := by
    field_simp
    ring
  constructor
  · intro he
    have h0 : (n - s) ^ 2 * (2 * n + s) / (2 * n ^ 2) = 0 := by rw [← h]; linarith
    have h1 : (n - s) ^ 2 * (2 * n + s) = 0 := by
      have hn2 : (2 * n ^ 2) ≠ 0 := by positivity
      exact (div_eq_zero_iff.mp h0).resolve_right hn2
    have h2 : (n - s) ^ 2 = 0 := by
      have hp : (2 * n + s) ≠ 0 := by positivity
      exact (mul_eq_zero.mp h1).resolve_right hp
    have : n - s = 0 := by simpa using h2
    linarith
  · intro he
    subst he
    field_simp
    ring

/-- **Hydraulic choking.**  In a steady one-dimensional flow with flux `j = s^(3/2)` and the Bernoulli constant of the
unperturbed fluid (density `1` and speed `j` far upstream, `hbar = m = mu = 1`), the potential `V` at any point where the
density is `n > 0` satisfies `V <= (1 - s)^2 (s + 2) / 2`.  No steady state exists over a barrier higher than that. -/
theorem barrier_height_bound {s n V : ℝ} (hs : 0 < s) (hn : 0 < n)
    (hB : s ^ 3 / (2 * n ^ 2) + n + V = 1 + s ^ 3 / 2) :
    V ≤ (1 - s) ^ 2 * (s + 2) / 2 := by
  have h := bernoulli_min hs hn
  have e : (1 - s) ^ 2 * (s + 2) / 2 = 1 + s ^ 3 / 2 - 3 / 2 * s := by ring
  rw [e]
  linarith

/-- **The O(dt) ramp convention.** Holding the velocity `a t` at the *end* of each of `n` steps of size `h` overshoots
the integral `a (n h)^2 / 2` by exactly `a h^2 n / 2`. -/
theorem ramp_overshoot (a h : ℝ) (n : ℕ) :
    ∑ i ∈ range n, a * (((i : ℝ) + 1) * h) * h - a * ((n : ℝ) * h) ^ 2 / 2 = a * h ^ 2 * n / 2 := by
  induction n with
  | zero => simp
  | succ m ih =>
    rw [sum_range_succ]
    push_cast
    nlinarith [ih]

#print axioms bogEps_ge_sound
#print axioms landau_uniform_gp
#print axioms supersonic_iff
#print axioms sonic_speed_threshold
#print axioms bernoulli_min
#print axioms bernoulli_eq_iff
#print axioms barrier_height_bound
#print axioms ramp_overshoot

end QuantumFluids.FlowPast
