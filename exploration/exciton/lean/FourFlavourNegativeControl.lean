import Mathlib

/-! NEGATIVE CONTROL (meant to FAIL to compile).

The polarisation of phase II_A (`FourFlavour.IIA_polarisation`) with the sign of `g_c` flipped.  The right-hand side
`2 (g_v - g_c) b / g_X` is replaced by `2 (g_v + g_c) b / g_X`.  A checker that accepted this would be worthless.
Expected result: an error from `ring` (the statement is false for `g_c ≠ 0`). -/

def Eflav (gc gv b Δ : ℝ) : Fin 4 → ℝ :=
  ![(gv - gc) * b - Δ, -(gv - gc) * b - Δ, -(gc + gv) * b, (gc + gv) * b]

theorem IIA_polarisation_wrong_sign {gH gX gc gv μ b Δ n0 n1 : ℝ} (hgX : gX ≠ 0)
    (h0 : (Eflav gc gv b Δ 0 - μ) + (gH + gX) * (n0 + n1) - gX * n1 = 0)
    (h1 : (Eflav gc gv b Δ 1 - μ) + (gH + gX) * (n0 + n1) - gX * n0 = 0) :
    n1 - n0 = 2 * (gv + gc) * b / gX := by
  have h : n1 - n0 = (Eflav gc gv b Δ 0 - Eflav gc gv b Δ 1) / gX := by
    field_simp
    linarith
  simp only [Eflav, Matrix.cons_val_zero, Matrix.cons_val_one] at h
  rw [h]
  ring
