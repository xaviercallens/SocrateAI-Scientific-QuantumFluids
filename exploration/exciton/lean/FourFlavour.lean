import Mathlib

/-! # The four-flavour mean-field model of Qi et al. (Nature 654, 2026; arXiv:2603.15443), Eqs. (2)-(3)

Flavours `0,1,2,3 = KK, K'K', KK', K'K` (electron valley, hole valley).  Grand-canonical energy

  `H(n) = Σ (E_i - μ) n_i + (g_H + g_X)/2 (Σ n_i)² - g_X (n₀n₁ + n₂n₃)`,   `n_i ≥ 0`.

Everything here is algebra about this model.  It is NOT a statement about the experiment: `g_X` and `Δ` are
phenomenological in the paper.  Scope notes are in docs/designs/EXCITON_FLUID_LEAN_SOLVER_PLAN.md §3.4.

Status: kernel-checked under Lean 4.34.0-rc2 / Mathlib 85e3a25, standard axioms only, no unproved goals.  Producer: the
session that wrote the plan; **verifier pending**.  `IIA_polarisation` and `IIB_polarisation` reproduce formulas printed
in the paper (a confirmation); `support_in_one_pair`, `critical_field` and `single_component_of_neg_gX` are not printed
in the arXiv v1 main text.  Not part of the audited library `lean_src/`. -/

namespace FourFlavour

noncomputable def H (gH gX μ : ℝ) (E : Fin 4 → ℝ) (n : Fin 4 → ℝ) : ℝ :=
  (∑ i, (E i - μ) * n i) + (gH + gX) / 2 * (∑ i, n i) ^ 2 - gX * (n 0 * n 1 + n 2 * n 3)

/-- Zeeman-shifted flavour energies, Eq. (3), with `b = μ_B B` and zero-field splitting `Δ`. -/
def Eflav (gc gv b Δ : ℝ) : Fin 4 → ℝ :=
  ![(gv - gc) * b - Δ, -(gv - gc) * b - Δ, -(gc + gv) * b, (gc + gv) * b]

def Feasible (n : Fin 4 → ℝ) : Prop := ∀ i, 0 ≤ n i

/-! ## Second differences and first-order conditions -/

/-- `H (n + w)` expanded around `n` (a quadratic polynomial, so this is exact). -/
lemma H_shift (gH gX μ : ℝ) (E n w : Fin 4 → ℝ) :
    H gH gX μ E (n + w) = H gH gX μ E n + (∑ i, (E i - μ) * w i)
      + (gH + gX) * (∑ i, n i) * (∑ i, w i) + (gH + gX) / 2 * (∑ i, w i) ^ 2
      - gX * (w 0 * n 1 + w 1 * n 0 + w 2 * n 3 + w 3 * n 2) - gX * (w 0 * w 1 + w 2 * w 3) := by
  simp only [H, Fin.sum_univ_four, Pi.add_apply]
  ring

/-- Midpoint inequality at a minimiser: if `n ± w` are feasible then `0 ≤ (gH+gX)(Σw)² - 2 gX (w₀w₁ + w₂w₃)`. -/
lemma midpoint {gH gX μ : ℝ} {E n : Fin 4 → ℝ}
    (hmin : ∀ m, Feasible m → H gH gX μ E n ≤ H gH gX μ E m) {w : Fin 4 → ℝ}
    (hp : Feasible (n + w)) (hm : Feasible (n - w)) :
    0 ≤ (gH + gX) * (∑ i, w i) ^ 2 - 2 * gX * (w 0 * w 1 + w 2 * w 3) := by
  have h1 := hmin _ hp
  have h2 := hmin _ hm
  have e1 := H_shift gH gX μ E n w
  have e2 := H_shift gH gX μ E n (-w)
  have e3 : n + -w = n - w := by ext i; simp [sub_eq_add_neg]
  rw [e3] at e2
  simp only [H, Fin.sum_univ_four, Pi.add_apply, Pi.neg_apply] at h1 h2 e1 e2 ⊢
  nlinarith [e1, e2]

/-- First-order condition along a zero-sum direction with vanishing quadratic form. -/
lemma first_order {gH gX μ : ℝ} {E n : Fin 4 → ℝ}
    (hmin : ∀ m, Feasible m → H gH gX μ E n ≤ H gH gX μ E m) {w : Fin 4 → ℝ}
    (hp : Feasible (n + w)) (hm : Feasible (n - w)) (hsum : w 0 + w 1 + w 2 + w 3 = 0)
    (hq : w 0 * w 1 + w 2 * w 3 = 0) :
    (∑ i, (E i - μ) * w i) - gX * (w 0 * n 1 + w 1 * n 0 + w 2 * n 3 + w 3 * n 2) = 0 := by
  have h1 := hmin _ hp
  have h2 := hmin _ hm
  have e1 := H_shift gH gX μ E n w
  have e2 := H_shift gH gX μ E n (-w)
  have e3 : n + -w = n - w := by ext i; simp [sub_eq_add_neg]
  rw [e3] at e2
  have hs : ∑ i, w i = 0 := by simpa [Fin.sum_univ_four] using hsum
  have hs' : ∑ i, (-w) i = 0 := by simp [Fin.sum_univ_four, Pi.neg_apply]; linarith
  rw [hs, hq] at e1
  simp only [Pi.neg_apply, Fin.sum_univ_four] at e2 hs'
  have hq' : (-w 0) * (-w 1) + (-w 2) * (-w 3) = 0 := by nlinarith [hq]
  rw [hs', hq'] at e2
  simp only [Fin.sum_univ_four] at e1 e2 ⊢
  nlinarith [e1, e2, h1, h2]

/-- A positive margin that fits all three requirements. -/
lemma exists_margin {a b c : ℝ} (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :
    ∃ ε : ℝ, 0 < ε ∧ ε ≤ a ∧ ε ≤ b ∧ 2 * ε ≤ c :=
  ⟨min a (min b (c / 2)), lt_min ha (lt_min hb (by linarith)), min_le_left _ _,
    (min_le_right _ _).trans (min_le_left _ _), by
      have := (min_le_right a (min b (c / 2))).trans (min_le_right b (c / 2)); linarith⟩

/-! ## Coordinate forms -/

lemma feasible_of_coords {m : Fin 4 → ℝ} (h0 : 0 ≤ m 0) (h1 : 0 ≤ m 1) (h2 : 0 ≤ m 2) (h3 : 0 ≤ m 3) :
    Feasible m := by
  intro i
  fin_cases i <;> assumption

lemma midpoint4 {gH gX μ : ℝ} {E n : Fin 4 → ℝ}
    (hmin : ∀ m, Feasible m → H gH gX μ E n ≤ H gH gX μ E m) (a b c d : ℝ)
    (p0 : 0 ≤ n 0 + a) (p1 : 0 ≤ n 1 + b) (p2 : 0 ≤ n 2 + c) (p3 : 0 ≤ n 3 + d)
    (m0 : 0 ≤ n 0 - a) (m1 : 0 ≤ n 1 - b) (m2 : 0 ≤ n 2 - c) (m3 : 0 ≤ n 3 - d) :
    0 ≤ (gH + gX) * (a + b + c + d) ^ 2 - 2 * gX * (a * b + c * d) := by
  have hp : Feasible (n + ![a, b, c, d]) :=
    feasible_of_coords (by simpa using p0) (by simpa using p1) (by simpa using p2) (by simpa using p3)
  have hm : Feasible (n - ![a, b, c, d]) :=
    feasible_of_coords (by simpa using m0) (by simpa using m1) (by simpa using m2) (by simpa using m3)
  have := midpoint hmin hp hm
  simpa [Fin.sum_univ_four] using this

lemma first_order4 {gH gX μ : ℝ} {E n : Fin 4 → ℝ}
    (hmin : ∀ m, Feasible m → H gH gX μ E n ≤ H gH gX μ E m) (a b c d : ℝ)
    (p0 : 0 ≤ n 0 + a) (p1 : 0 ≤ n 1 + b) (p2 : 0 ≤ n 2 + c) (p3 : 0 ≤ n 3 + d)
    (m0 : 0 ≤ n 0 - a) (m1 : 0 ≤ n 1 - b) (m2 : 0 ≤ n 2 - c) (m3 : 0 ≤ n 3 - d)
    (hs : a + b + c + d = 0) (hq : a * b + c * d = 0) :
    (E 0 - μ) * a + (E 1 - μ) * b + (E 2 - μ) * c + (E 3 - μ) * d
      - gX * (a * n 1 + b * n 0 + c * n 3 + d * n 2) = 0 := by
  have hp : Feasible (n + ![a, b, c, d]) :=
    feasible_of_coords (by simpa using p0) (by simpa using p1) (by simpa using p2) (by simpa using p3)
  have hm : Feasible (n - ![a, b, c, d]) :=
    feasible_of_coords (by simpa using m0) (by simpa using m1) (by simpa using m2) (by simpa using m3)
  have := first_order hmin hp hm (w := ![a, b, c, d]) (by simpa using hs) (by simpa using hq)
  simpa [Fin.sum_univ_four] using this

/-! ## T1: a minimiser condenses at most one exchange pair (generic case) -/

theorem support_in_one_pair {gH gX μ : ℝ} {E : Fin 4 → ℝ} (hgX : 0 < gX)
    (hE : ∀ i ∈ ({0, 1} : Finset (Fin 4)), ∀ j ∈ ({2, 3} : Finset (Fin 4)), E i ≠ E j)
    {n : Fin 4 → ℝ} (hn : Feasible n)
    (hmin : ∀ m, Feasible m → H gH gX μ E n ≤ H gH gX μ E m) :
    (n 2 = 0 ∧ n 3 = 0) ∨ (n 0 = 0 ∧ n 1 = 0) := by
  have h0 := hn 0
  have h1 := hn 1
  have h2 := hn 2
  have h3 := hn 3
  by_contra hcon
  have hc1 : n 2 = 0 → n 3 ≠ 0 := fun a b => hcon (Or.inl ⟨a, b⟩)
  have hc2 : n 0 = 0 → n 1 ≠ 0 := fun a b => hcon (Or.inr ⟨a, b⟩)
  -- concavity along zero-sum directions with positive `a*b + c*d`
  have concave : ∀ a b c d : ℝ, 0 ≤ n 0 + a → 0 ≤ n 1 + b → 0 ≤ n 2 + c → 0 ≤ n 3 + d →
      0 ≤ n 0 - a → 0 ≤ n 1 - b → 0 ≤ n 2 - c → 0 ≤ n 3 - d →
      a + b + c + d = 0 → 0 < a * b + c * d → False := by
    intro a b c d p0 p1 p2 p3 m0 m1 m2 m3 hs hq
    have hmid := midpoint4 hmin a b c d p0 p1 p2 p3 m0 m1 m2 m3
    rw [hs] at hmid
    nlinarith [hmid, hq, hgX]
  -- a full pair plus one member of the other pair
  have opA : 0 < n 0 → 0 < n 1 → 0 < n 2 → False := fun p0 p1 p2 => by
    obtain ⟨ε, hε, ha, hb, hc⟩ := exists_margin p0 p1 p2
    exact concave ε ε (-2 * ε) 0 (by linarith) (by linarith) (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by ring) (by nlinarith [mul_pos hε hε])
  have opB : 0 < n 0 → 0 < n 1 → 0 < n 3 → False := fun p0 p1 p3 => by
    obtain ⟨ε, hε, ha, hb, hc⟩ := exists_margin p0 p1 p3
    exact concave ε ε 0 (-2 * ε) (by linarith) (by linarith) (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by ring) (by nlinarith [mul_pos hε hε])
  have opC : 0 < n 2 → 0 < n 3 → 0 < n 0 → False := fun p2 p3 p0 => by
    obtain ⟨ε, hε, ha, hb, hc⟩ := exists_margin p2 p3 p0
    exact concave (-2 * ε) 0 ε ε (by linarith) (by linarith) (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by ring) (by nlinarith [mul_pos hε hε])
  have opD : 0 < n 2 → 0 < n 3 → 0 < n 1 → False := fun p2 p3 p1 => by
    obtain ⟨ε, hε, ha, hb, hc⟩ := exists_margin p2 p3 p1
    exact concave 0 (-2 * ε) ε ε (by linarith) (by linarith) (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by ring) (by nlinarith [mul_pos hε hε])
  -- one member of each pair, partners empty: first-order condition forces `E i = E j`
  have x02 : 0 < n 0 → 0 < n 2 → n 1 = 0 → n 3 = 0 → False := fun p0 p2 z1 z3 => by
    have hp : 0 < min (n 0) (n 2) := lt_min p0 p2
    have l1 := min_le_left (n 0) (n 2)
    have l2 := min_le_right (n 0) (n 2)
    have key := first_order4 hmin (min (n 0) (n 2)) 0 (-(min (n 0) (n 2))) 0 (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by ring) (by ring)
    rw [z1, z3] at key
    exact hE 0 (by simp) 2 (by simp) (by nlinarith [key, hp])
  have x03 : 0 < n 0 → 0 < n 3 → n 1 = 0 → n 2 = 0 → False := fun p0 p3 z1 z2 => by
    have hp : 0 < min (n 0) (n 3) := lt_min p0 p3
    have l1 := min_le_left (n 0) (n 3)
    have l2 := min_le_right (n 0) (n 3)
    have key := first_order4 hmin (min (n 0) (n 3)) 0 0 (-(min (n 0) (n 3))) (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by ring) (by ring)
    rw [z1, z2] at key
    exact hE 0 (by simp) 3 (by simp) (by nlinarith [key, hp])
  have x12 : 0 < n 1 → 0 < n 2 → n 0 = 0 → n 3 = 0 → False := fun p1 p2 z0 z3 => by
    have hp : 0 < min (n 1) (n 2) := lt_min p1 p2
    have l1 := min_le_left (n 1) (n 2)
    have l2 := min_le_right (n 1) (n 2)
    have key := first_order4 hmin 0 (min (n 1) (n 2)) (-(min (n 1) (n 2))) 0 (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by ring) (by ring)
    rw [z0, z3] at key
    exact hE 1 (by simp) 2 (by simp) (by nlinarith [key, hp])
  have x13 : 0 < n 1 → 0 < n 3 → n 0 = 0 → n 2 = 0 → False := fun p1 p3 z0 z2 => by
    have hp : 0 < min (n 1) (n 3) := lt_min p1 p3
    have l1 := min_le_left (n 1) (n 3)
    have l2 := min_le_right (n 1) (n 3)
    have key := first_order4 hmin 0 (min (n 1) (n 3)) 0 (-(min (n 1) (n 3))) (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by ring) (by ring)
    rw [z0, z2] at key
    exact hE 1 (by simp) 3 (by simp) (by nlinarith [key, hp])
  rcases h0.lt_or_eq with p0 | z0
  · rcases h1.lt_or_eq with p1 | z1
    · rcases h2.lt_or_eq with p2 | z2
      · exact opA p0 p1 p2
      · rcases h3.lt_or_eq with p3 | z3
        · exact opB p0 p1 p3
        · exact hc1 z2.symm z3.symm
    · rcases h2.lt_or_eq with p2 | z2
      · rcases h3.lt_or_eq with p3 | z3
        · exact opC p2 p3 p0
        · exact x02 p0 p2 z1.symm z3.symm
      · rcases h3.lt_or_eq with p3 | z3
        · exact x03 p0 p3 z1.symm z2.symm
        · exact hc1 z2.symm z3.symm
  · rcases h1.lt_or_eq with p1 | z1
    · rcases h2.lt_or_eq with p2 | z2
      · rcases h3.lt_or_eq with p3 | z3
        · exact opD p2 p3 p1
        · exact x12 p1 p2 z0.symm z3.symm
      · rcases h3.lt_or_eq with p3 | z3
        · exact x13 p1 p3 z0.symm z2.symm
        · exact hc1 z2.symm z3.symm
    · exact hc2 z0.symm z1.symm

/-! ## T2, T3: polarisation and density in each phase (from the stationarity equations) -/

theorem intravalley_polarisation {gH gX μ E0 E1 n0 n1 : ℝ} (hgX : gX ≠ 0)
    (h0 : (E0 - μ) + (gH + gX) * (n0 + n1) - gX * n1 = 0)
    (h1 : (E1 - μ) + (gH + gX) * (n0 + n1) - gX * n0 = 0) :
    n1 - n0 = (E0 - E1) / gX := by
  field_simp
  linarith

theorem intravalley_density {gH gX μ E0 E1 n0 n1 : ℝ} (hd : 2 * (gH + gX) - gX ≠ 0)
    (h0 : (E0 - μ) + (gH + gX) * (n0 + n1) - gX * n1 = 0)
    (h1 : (E1 - μ) + (gH + gX) * (n0 + n1) - gX * n0 = 0) :
    n0 + n1 = (2 * μ - E0 - E1) / (2 * (gH + gX) - gX) := by
  rw [eq_div_iff hd]
  linarith

/-- Phase II_A (KK + K'K'): the paper's formula `n₂ − n₁ = 2 (g_v − g_c) μ_B B / g_X` (1-indexed). -/
theorem IIA_polarisation {gH gX gc gv μ b Δ n0 n1 : ℝ} (hgX : gX ≠ 0)
    (h0 : (Eflav gc gv b Δ 0 - μ) + (gH + gX) * (n0 + n1) - gX * n1 = 0)
    (h1 : (Eflav gc gv b Δ 1 - μ) + (gH + gX) * (n0 + n1) - gX * n0 = 0) :
    n1 - n0 = 2 * (gv - gc) * b / gX := by
  have h := intravalley_polarisation hgX h0 h1
  simp only [Eflav, Matrix.cons_val_zero, Matrix.cons_val_one] at h
  rw [h]; ring

/-- Phase II_B (KK' + K'K): `n₃ − n₄ = 2 (g_c + g_v) μ_B B / g_X` (1-indexed). -/
theorem IIB_polarisation {gH gX gc gv μ b Δ n2 n3 : ℝ} (hgX : gX ≠ 0)
    (h2 : (Eflav gc gv b Δ 2 - μ) + (gH + gX) * (n2 + n3) - gX * n3 = 0)
    (h3 : (Eflav gc gv b Δ 3 - μ) + (gH + gX) * (n2 + n3) - gX * n2 = 0) :
    n2 - n3 = 2 * (gc + gv) * b / gX := by
  have h := intravalley_polarisation hgX h2 h3
  simp only [Eflav] at h
  have e2 : (![(gv - gc) * b - Δ, -(gv - gc) * b - Δ, -(gc + gv) * b, (gc + gv) * b] : Fin 4 → ℝ) 2
      = -(gc + gv) * b := rfl
  have e3 : (![(gv - gc) * b - Δ, -(gv - gc) * b - Δ, -(gc + gv) * b, (gc + gv) * b] : Fin 4 → ℝ) 3
      = (gc + gv) * b := rfl
  rw [e2, e3] at h
  have : n2 - n3 = -(n3 - n2) := by ring
  rw [this, h]; ring

/-! ## T5: the first-order transition -/

/-- Difference of the two grand potentials `Ω_B − Ω_A` (closed forms of §3.4 of the plan). -/
theorem grand_potential_gap {gH gX gc gv μ b Δ : ℝ} (hgX : gX ≠ 0) (hD : 2 * gH + gX ≠ 0) :
    (-(μ ^ 2) / (2 * gH + gX) - ((gc + gv) * b) ^ 2 / gX) -
        (-((μ + Δ) ^ 2) / (2 * gH + gX) - ((gv - gc) * b) ^ 2 / gX) =
      Δ * (2 * μ + Δ) / (2 * gH + gX) - 4 * gc * gv * b ^ 2 / gX := by
  field_simp
  ring

/-- The critical field: `Ω_A = Ω_B` iff `(μ_B B)² = g_X Δ (2μ + Δ) / (4 g_c g_v (2 g_H + g_X))`. -/
theorem critical_field {gH gX gc gv μ b Δ : ℝ} (hgX : 0 < gX) (hD : 0 < 2 * gH + gX)
    (hcv : 0 < 4 * gc * gv) :
    Δ * (2 * μ + Δ) / (2 * gH + gX) - 4 * gc * gv * b ^ 2 / gX = 0 ↔
      b ^ 2 = gX * Δ * (2 * μ + Δ) / (4 * gc * gv * (2 * gH + gX)) := by
  rw [sub_eq_zero, div_eq_div_iff hD.ne' hgX.ne', eq_div_iff (by positivity)]
  constructor <;> intro h <;> nlinarith [h]

/-! ## T6: negative control, `g_X < 0` gives a single-component (ferromagnetic) condensate -/

theorem single_component_of_neg_gX {gH gX μ : ℝ} {E : Fin 4 → ℝ} (hgX : gX < 0)
    (hE : ∀ i ∈ ({0, 1} : Finset (Fin 4)), ∀ j ∈ ({2, 3} : Finset (Fin 4)), E i ≠ E j)
    {n : Fin 4 → ℝ} (hn : Feasible n)
    (hmin : ∀ m, Feasible m → H gH gX μ E n ≤ H gH gX μ E m) :
    ∀ i j : Fin 4, i ≠ j → n i = 0 ∨ n j = 0 := by
  have h0 := hn 0
  have h1 := hn 1
  have h2 := hn 2
  have h3 := hn 3
  -- inside a pair, two occupied flavours are not a minimum (the form is concave along `e_i - e_j`)
  have pair01 : n 0 = 0 ∨ n 1 = 0 := by
    by_contra hcon
    have hc1 : n 0 ≠ 0 := fun h => hcon (Or.inl h)
    have hc2 : n 1 ≠ 0 := fun h => hcon (Or.inr h)
    have p0 : 0 < n 0 := lt_of_le_of_ne h0 (Ne.symm hc1)
    have p1 : 0 < n 1 := lt_of_le_of_ne h1 (Ne.symm hc2)
    have hp : 0 < min (n 0) (n 1) := lt_min p0 p1
    have l1 := min_le_left (n 0) (n 1)
    have l2 := min_le_right (n 0) (n 1)
    have hmid := midpoint4 hmin (min (n 0) (n 1)) (-(min (n 0) (n 1))) 0 0 (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith)
    nlinarith [hmid, mul_neg_of_neg_of_pos hgX (mul_pos hp hp)]
  have pair23 : n 2 = 0 ∨ n 3 = 0 := by
    by_contra hcon
    have hc1 : n 2 ≠ 0 := fun h => hcon (Or.inl h)
    have hc2 : n 3 ≠ 0 := fun h => hcon (Or.inr h)
    have p2 : 0 < n 2 := lt_of_le_of_ne h2 (Ne.symm hc1)
    have p3 : 0 < n 3 := lt_of_le_of_ne h3 (Ne.symm hc2)
    have hp : 0 < min (n 2) (n 3) := lt_min p2 p3
    have l1 := min_le_left (n 2) (n 3)
    have l2 := min_le_right (n 2) (n 3)
    have hmid := midpoint4 hmin 0 0 (min (n 2) (n 3)) (-(min (n 2) (n 3))) (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith)
    nlinarith [hmid, mul_neg_of_neg_of_pos hgX (mul_pos hp hp)]
  -- across the pairs, a first-order condition forces `E_i = E_j`
  have c02 : n 0 = 0 ∨ n 2 = 0 := by
    by_contra hcon
    have p0 : 0 < n 0 := lt_of_le_of_ne h0 (Ne.symm fun h => hcon (Or.inl h))
    have p2 : 0 < n 2 := lt_of_le_of_ne h2 (Ne.symm fun h => hcon (Or.inr h))
    have z1 : n 1 = 0 := pair01.resolve_left (ne_of_gt p0)
    have z3 : n 3 = 0 := pair23.resolve_left (ne_of_gt p2)
    have hp : 0 < min (n 0) (n 2) := lt_min p0 p2
    have l1 := min_le_left (n 0) (n 2)
    have l2 := min_le_right (n 0) (n 2)
    have key := first_order4 hmin (min (n 0) (n 2)) 0 (-(min (n 0) (n 2))) 0 (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by ring) (by ring)
    rw [z1, z3] at key
    exact hE 0 (by simp) 2 (by simp) (by nlinarith [key, hp])
  have c03 : n 0 = 0 ∨ n 3 = 0 := by
    by_contra hcon
    have p0 : 0 < n 0 := lt_of_le_of_ne h0 (Ne.symm fun h => hcon (Or.inl h))
    have p3 : 0 < n 3 := lt_of_le_of_ne h3 (Ne.symm fun h => hcon (Or.inr h))
    have z1 : n 1 = 0 := pair01.resolve_left (ne_of_gt p0)
    have z2 : n 2 = 0 := pair23.resolve_right (ne_of_gt p3)
    have hp : 0 < min (n 0) (n 3) := lt_min p0 p3
    have l1 := min_le_left (n 0) (n 3)
    have l2 := min_le_right (n 0) (n 3)
    have key := first_order4 hmin (min (n 0) (n 3)) 0 0 (-(min (n 0) (n 3))) (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by ring) (by ring)
    rw [z1, z2] at key
    exact hE 0 (by simp) 3 (by simp) (by nlinarith [key, hp])
  have c12 : n 1 = 0 ∨ n 2 = 0 := by
    by_contra hcon
    have p1 : 0 < n 1 := lt_of_le_of_ne h1 (Ne.symm fun h => hcon (Or.inl h))
    have p2 : 0 < n 2 := lt_of_le_of_ne h2 (Ne.symm fun h => hcon (Or.inr h))
    have z0 : n 0 = 0 := pair01.resolve_right (ne_of_gt p1)
    have z3 : n 3 = 0 := pair23.resolve_left (ne_of_gt p2)
    have hp : 0 < min (n 1) (n 2) := lt_min p1 p2
    have l1 := min_le_left (n 1) (n 2)
    have l2 := min_le_right (n 1) (n 2)
    have key := first_order4 hmin 0 (min (n 1) (n 2)) (-(min (n 1) (n 2))) 0 (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by ring) (by ring)
    rw [z0, z3] at key
    exact hE 1 (by simp) 2 (by simp) (by nlinarith [key, hp])
  have c13 : n 1 = 0 ∨ n 3 = 0 := by
    by_contra hcon
    have p1 : 0 < n 1 := lt_of_le_of_ne h1 (Ne.symm fun h => hcon (Or.inl h))
    have p3 : 0 < n 3 := lt_of_le_of_ne h3 (Ne.symm fun h => hcon (Or.inr h))
    have z0 : n 0 = 0 := pair01.resolve_right (ne_of_gt p1)
    have z2 : n 2 = 0 := pair23.resolve_right (ne_of_gt p3)
    have hp : 0 < min (n 1) (n 3) := lt_min p1 p3
    have l1 := min_le_left (n 1) (n 3)
    have l2 := min_le_right (n 1) (n 3)
    have key := first_order4 hmin 0 (min (n 1) (n 3)) 0 (-(min (n 1) (n 3))) (by linarith) (by linarith)
      (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by linarith) (by ring) (by ring)
    rw [z0, z2] at key
    exact hE 1 (by simp) 3 (by simp) (by nlinarith [key, hp])
  intro i j hij
  fin_cases i <;> fin_cases j <;>
    first
      | exact absurd rfl hij
      | exact pair01
      | exact pair01.symm
      | exact pair23
      | exact pair23.symm
      | exact c02
      | exact c02.symm
      | exact c03
      | exact c03.symm
      | exact c12
      | exact c12.symm
      | exact c13
      | exact c13.symm

end FourFlavour

#print axioms FourFlavour.support_in_one_pair
#print axioms FourFlavour.IIA_polarisation
#print axioms FourFlavour.IIB_polarisation
#print axioms FourFlavour.intravalley_density
#print axioms FourFlavour.grand_potential_gap
#print axioms FourFlavour.critical_field
#print axioms FourFlavour.single_component_of_neg_gX
