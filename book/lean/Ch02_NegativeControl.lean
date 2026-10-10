/-
  Ch02_NegativeControl.lean -- this file is MEANT to fail.  It contains two false statements; the compiler's
  refusal (quoted in Chapter 2) is the point.  It is not part of any build.
-/
import Mathlib

-- (a) the certificate of `one_add_nilpotent_inv` with a mistyped coefficient (+1 instead of -1)
example {R : Type*} [CommRing R] (e : R) (h : e ^ 2 = 0) : (1 + e) * (1 - e) = 1 := by
  linear_combination (1 : R) * h

-- (b) a false statement about numbers
example : (2 : ℝ) + 2 = 5 := by norm_num
