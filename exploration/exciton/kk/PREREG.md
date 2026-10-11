# L1 — KK-tower evaluator for the gated kernel (pre-registration, 2026-10-11)

Kernel: U(r) = V_ee + V_hh − 2 V_eh between two grounded planes (constant ε), parameters (h1,h2,z_e,z_h), ℓ = h1+h2.
Two exact representations (note, Thm 1 / Prop 2):
* modal: U(r) = (4/ℓ) Σ_{m≥1} (φ_m(z_e) − φ_m(z_h))² K0(mπ r/ℓ)  (terms decay like e^{−mπ r/ℓ});
* images: U(r) = Σ_n [images of the three pair terms], period P = 2ℓ (terms decay algebraically; difference of ± charges ~ n^{-3}).

Evaluator under test: modal sum truncated adaptively at term < 1e-16·|partial sum|, used for r ≥ r_c; image sum with explicit
Euler–Maclaurin tail for r < r_c; r_c chosen by minimising cost (to be reported, not tuned on the test set).

Reference: mpmath, 40 digits, modal sum with enough terms (never the same code path as the evaluator).

Test set (fixed now): (h1,h2,z_e,z_h) ∈ {(1,1.5,0.3,−0.4), (0.5,0.5,0.1,−0.2), (1,3,0.9,−2.0), (2,0.4,1.5,−0.2)};
r/ℓ ∈ 40 log-spaced points in [0.01, 20]; plus 1e4 uniformly random r for timing.

Gates:
* G1 accuracy: max relative error vs reference ≤ 1e-12 over all test points (≥ 1e-13 relative tolerance on the reference itself).
* G2 speed: wall-clock per 1e4 evaluations ≥ 5× faster than the naive truncated image sum that reaches 1e-12 on the same points,
  for r ≥ 0.3 d where d = min(h1,h2) (as in PROJET L1); also report speed vs image-sum-with-tail-correction (the fair baseline).
* Stop: speed gain < 2× vs the fair baseline → report as negative; do not extend.

Honest scope: Python/NumPy prototype; the Rust crate is only built if G1 and G2 (fair baseline) hold. No Lean content here.
