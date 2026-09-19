/-
The second invariant of the complexified dyadic shell model (design memo
docs/designs/DUAL_SCALE_SECOND_INVARIANT.md, addendum A1; CLAIM-023).

With `w_n = 2^(-n/2) v_n` the model of `QuantumFluidsShell.lean` is a Hamiltonian
second-harmonic-generation chain. In the original variables the cubic functional
  `H(v) = Σ_n g_n · Im(conj(v_n)² v_{n+1})`,   `g_{n+1} · 2 k_n = g_n · k_{n+1}`   (e.g. `g_n = 2^(-n) k_n`)
is conserved by the truncated flow.

WHAT IS PROVED. The first variation of `H` along the vector field `shellBc` telescopes:
`Σ_{n≤N} g_n · dT_n = -(g_N k_{N+1}) · Im(conj(v_N)² conj(v_{N+1}) v_{N+2})`, hence vanishes when
`v_{N+2} = 0` (truncation at shell `N+1`). `dT_n` is the derivative of `T_n = Im(conj(v_n)² v_{n+1})`
in the direction `B`, written out by the product rule.

WHAT IS NOT PROVED. The chain-rule step identifying `dT_n` with `d/dt T_n` along a solution; the
dispersive (`D`) and GPE-seam (`μ`) extensions (checked as exact polynomial identities in
exploration/second_invariant/symbolic_check.py, not in Lean); any bound or regularity statement.
-/

import QuantumFluidsShell

namespace QuantumFluids.ShellComplex

open Complex

/-- First variation of `T_n = Im(conj(v_n)² v_{n+1})` along the vector field `shellBc`. -/
noncomputable def dT (k : ℕ → ℝ) (v : ℕ → ℂ) (n : ℕ) : ℝ :=
  (2 * (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (shellBc k n v) * v (n + 1)
    + (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * shellBc k (n + 1) v).im

/-- The four-shell flux `X_n = Im(conj(v_n)² conj(v_{n+1}) v_{n+2})`. -/
noncomputable def flux4 (v : ℕ → ℂ) (n : ℕ) : ℝ :=
  ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v (n + 1)) * v (n + 2)).im

/-- Pure algebra behind every interior term. -/
theorem im_core (a b c d : ℂ) (p q r : ℝ) :
    (2 * (starRingEnd ℂ) b * (starRingEnd ℂ) ((p : ℂ) * (a * a) - (q : ℂ) * (starRingEnd ℂ) b * c) * c
      + (starRingEnd ℂ) b * (starRingEnd ℂ) b * ((q : ℂ) * (b * b) - (r : ℂ) * (starRingEnd ℂ) c * d)).im
    = 2 * p * ((starRingEnd ℂ) a * (starRingEnd ℂ) a * (starRingEnd ℂ) b * c).im
      - r * ((starRingEnd ℂ) b * (starRingEnd ℂ) b * (starRingEnd ℂ) c * d).im := by
  simp only [map_sub, map_mul, Complex.conj_conj, Complex.conj_ofReal]
  simp [Complex.mul_im, Complex.mul_re, Complex.add_im, Complex.sub_im, Complex.sub_re]
  ring

theorem dT_zero (k : ℕ → ℝ) (v : ℕ → ℂ) : dT k v 0 = -(k 1 * flux4 v 0) := by
  have h := im_core 0 (v 0) (v 1) (v 2) 0 (k 0) (k 1)
  simp only [dT, flux4, shellBc]
  simp only [mul_zero, Complex.ofReal_zero, zero_mul, zero_sub, map_zero, Complex.zero_im] at h
  rw [← h]

theorem dT_succ (k : ℕ → ℝ) (v : ℕ → ℂ) (m : ℕ) :
    dT k v (m + 1) = 2 * k m * flux4 v m - k (m + 2) * flux4 v (m + 1) := by
  simpa [dT, flux4, shellBc] using im_core (v m) (v (m + 1)) (v (m + 2)) (v (m + 3)) (k m) (k (m + 1)) (k (m + 2))

/-- **Telescoping of the cubic Hamiltonian's rate.** -/
theorem sum_dT (k g : ℕ → ℝ) (v : ℕ → ℂ) (hg : ∀ n, g (n + 1) * (2 * k n) = g n * k (n + 1)) :
    ∀ N : ℕ, ∑ n ∈ Finset.range (N + 1), g n * dT k v n = -(g N * k (N + 1) * flux4 v N)
  | 0 => by simp [dT_zero]; ring
  | N + 1 => by
      rw [Finset.sum_range_succ, sum_dT k g v hg N, dT_succ]
      have := hg N
      linear_combination (flux4 v N) * this

/-- **The cubic Hamiltonian is conserved by the truncated flow (algebraic core).**
Shells `0..N+1`, truncation `v_{N+2} = 0`. -/
theorem hamiltonian_rate_zero (k g : ℕ → ℝ) (v : ℕ → ℂ)
    (hg : ∀ n, g (n + 1) * (2 * k n) = g n * k (n + 1)) (N : ℕ) (hbc : v (N + 2) = 0) :
    ∑ n ∈ Finset.range (N + 1), g n * dT k v n = 0 := by
  rw [sum_dT k g v hg N]; simp [flux4, hbc]

/-- The weights `g_n = 2^(-n) k_n` satisfy the compatibility condition, for every `k`. -/
theorem weights_ok (k : ℕ → ℝ) (n : ℕ) :
    ((1 / 2 : ℝ) ^ (n + 1) * k (n + 1)) * (2 * k n) = ((1 / 2 : ℝ) ^ n * k n) * k (n + 1) := by
  rw [pow_succ]; ring

/-- On real data the Hamiltonian density vanishes: the real Katz-Pavlović model cannot see it. -/
theorem T_real (v : ℕ → ℂ) (hv : ∀ n, (v n).im = 0) (n : ℕ) :
    ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im = 0 := by
  simp [Complex.mul_im, hv]

/-- **Cutoff-uniform bound on the cubic part.** With `S = Σ_{n ≤ N+1} |v_n|²` (twice the energy),
`|Σ_{n ≤ N} c_n Im(conj(v_n)² v_{n+1})| ≤ √S · S` whenever `|c_n| ≤ 1` (e.g. `c_n = 2^(-n) k_n` for `k_n = 2ⁿ`).
The right-hand side does not depend on `N` except through the conserved `S`. -/
theorem cubic_bound (c : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hc : ∀ n, |c n| ≤ 1) :
    |∑ n ∈ Finset.range (N + 1), c n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im|
      ≤ Real.sqrt (∑ n ∈ Finset.range (N + 2), Complex.normSq (v n))
        * ∑ n ∈ Finset.range (N + 2), Complex.normSq (v n) := by
  set S := ∑ n ∈ Finset.range (N + 2), Complex.normSq (v n) with hS
  have hS0 : 0 ≤ S := Finset.sum_nonneg (fun n _ => Complex.normSq_nonneg _)
  have hterm : ∀ n ∈ Finset.range (N + 1),
      |c n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im|
        ≤ Real.sqrt S * Complex.normSq (v n) := by
    intro n hn
    have h1 : |((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im|
        ≤ Complex.normSq (v n) * ‖v (n + 1)‖ := by
      refine (Complex.abs_im_le_norm _).trans (le_of_eq ?_)
      rw [norm_mul, norm_mul, Complex.norm_conj, Complex.normSq_eq_norm_sq]; ring
    have h2 : ‖v (n + 1)‖ ≤ Real.sqrt S := by
      rw [← Real.sqrt_sq (norm_nonneg (v (n + 1))), ← Complex.normSq_eq_norm_sq]
      refine Real.sqrt_le_sqrt ?_
      have hmem : n + 1 ∈ Finset.range (N + 2) := by
        rw [Finset.mem_range] at hn ⊢; omega
      exact Finset.single_le_sum (f := fun m => Complex.normSq (v m))
        (fun m _ => Complex.normSq_nonneg _) hmem
    rw [abs_mul]
    calc |c n| * |((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im|
        ≤ 1 * (Complex.normSq (v n) * ‖v (n + 1)‖) :=
          mul_le_mul (hc n) h1 (abs_nonneg _) zero_le_one
      _ ≤ Real.sqrt S * Complex.normSq (v n) := by
          rw [one_mul, mul_comm]
          exact mul_le_mul_of_nonneg_right h2 (Complex.normSq_nonneg _)
  calc _ ≤ ∑ n ∈ Finset.range (N + 1),
          |c n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im| :=
        Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ n ∈ Finset.range (N + 1), Real.sqrt S * Complex.normSq (v n) := Finset.sum_le_sum hterm
    _ = Real.sqrt S * ∑ n ∈ Finset.range (N + 1), Complex.normSq (v n) := by rw [Finset.mul_sum]
    _ ≤ Real.sqrt S * S := by
        refine mul_le_mul_of_nonneg_left ?_ (Real.sqrt_nonneg _)
        rw [hS, Finset.sum_range_succ _ (N + 1)]
        linarith [Complex.normSq_nonneg (v (N + 1))]

/-- **Uniform-in-cutoff control of the dispersive norm.** If `Hval = Σ_{n≤N+1} q_n |v_n|² + Σ_{n≤N} c_n T_n`
with `|c_n| ≤ 1`, then `Σ q_n |v_n|² ≤ Hval + √S · S`. With `q_n = 2^(-n) ω_n`: for `ω_n = D k_n²`, `k_n = 2ⁿ` this is
`D Σ k_n |v_n|²`; for `ω_n = D k_n³` it is `D Σ k_n² |v_n|² = 2DΩ`. `Hval` and `S` are conserved (algebraic cores:
`hamiltonian_rate_zero`, `shellBc_energy_conservation`), so the bound is uniform in `N`. -/
theorem dispersive_norm_le (q c : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (Hval : ℝ) (hc : ∀ n, |c n| ≤ 1)
    (hH : Hval = ∑ n ∈ Finset.range (N + 2), q n * Complex.normSq (v n)
      + ∑ n ∈ Finset.range (N + 1), c n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im) :
    ∑ n ∈ Finset.range (N + 2), q n * Complex.normSq (v n)
      ≤ Hval + Real.sqrt (∑ n ∈ Finset.range (N + 2), Complex.normSq (v n))
        * ∑ n ∈ Finset.range (N + 2), Complex.normSq (v n) := by
  have h := cubic_bound c v N hc
  have := neg_abs_le (∑ n ∈ Finset.range (N + 1),
    c n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im)
  linarith

end QuantumFluids.ShellComplex

#print axioms QuantumFluids.ShellComplex.im_core
#print axioms QuantumFluids.ShellComplex.sum_dT
#print axioms QuantumFluids.ShellComplex.hamiltonian_rate_zero
#print axioms QuantumFluids.ShellComplex.weights_ok
#print axioms QuantumFluids.ShellComplex.T_real
#print axioms QuantumFluids.ShellComplex.cubic_bound
#print axioms QuantumFluids.ShellComplex.dispersive_norm_le
