# Gated bilayer dipole kernels are completely monotone in r² (image-charge series)

Date 2026-10-11. Answers the open point recorded in the exciton note (§Limitations): for a dual-gated device the complete
monotonicity of the exciton–exciton kernel was supported only by numerical evidence. **Status: proved on paper below for ideal
grounded metal gates and a homogeneous (possibly anisotropic) dielectric; not formalised in Lean; numerics reproduce it.**

## Statement

Grounded perfect-conductor planes at `z = +h₁` and `z = −h₂` (`h₁ + h₂ > 0`), a vacuum or homogeneous dielectric between them (a
uniform ε is a prefactor; an anisotropic ε rescales `z` by a constant), an electron layer at `z = z_e` and a hole layer at
`z_h = z_e + d`, with both layers strictly between the gates. The exciton–exciton kernel is `U = V_ee + V_hh − 2V_eh` with `V`
the Green function of the box (the image series). Then `U(r)`, as a function of `t = r²`, is completely monotone on `(0, ∞)`:
`U = ∫₀^∞ e^{−st} μ(s) ds` with `μ ≥ 0`. By Bernstein's theorem this is exactly the hypothesis of the Cohn–Kumar criterion used in
the note, so the gates **cannot** be engineered to break it within this model. The single-gate and gate-free limits
(`h₂ → ∞`, `h₁, h₂ → ∞`) are pointwise limits of completely monotone functions and are completely monotone.

## Proof

Period `P = 2(h₁ + h₂)`. A unit charge at height `z₀` produces, at height `z` and in-plane distance `r`, the potential
`V(z, z₀; r) = Σ_{n∈ℤ} [ (r² + (z − z₀ − Pn)²)^{−1/2} − (r² + (z − 2h₁ + z₀ − Pn)²)^{−1/2} ]`
(images at `z₀ + Pn` with sign +, at `2h₁ − z₀ + Pn` with sign −).
Use `(t + a²)^{−1/2} = π^{−1/2} ∫₀^∞ e^{−s(t + a²)} s^{−1/2} ds` termwise: `μ(s) = (π s)^{−1/2} S(s)`, where `S(s)` is the sum
over `n` of `e^{−s a²}` with the signs of `V_ee + V_hh − 2V_eh`. Poisson summation,
`Σ_n e^{−s(c+Pn)²} = (π/s)^{1/2} P^{−1} Σ_{m∈ℤ} e^{−π²m²/(P²s)} cos(2πmc/P)`, gives
`S(s) = (π/s)^{1/2} P^{−1} Σ_{m∈ℤ} e^{−π²m²/(P²s)} S_m`, with, writing `α = 2πm/P`, `a = α(z_e − h₁)`, `b = α(z_h − h₁)`
(so `αd = b − a`):

`S_m = 2 − cos 2a − cos 2b − 2cos(b − a) + 2cos(a + b)`.

Since `cos 2a + cos 2b = 2cos(a + b)cos(a − b)`,

**`S_m = 2 (1 − cos(b − a)) (1 + cos(a + b)) ≥ 0`**,

and `S_0 = 0` (charge neutrality of the exciton). Hence `S(s) ≥ 0` for every `s > 0`, term by term, so `μ ≥ 0`. ∎

Remark: each image series alone has indefinite sign in `m`; only the neutral combination `V_ee + V_hh − 2V_eh` factorises.

## Numerical check

`exploration/exciton/python/gate_image_cm_sym.py`, `gate_image_cm_general.py`: `S(s)` on `10⁻¹⁰ ≤ s ≤ 10⁴` (200 001 points,
Poisson form for small `s`, direct sum otherwise) for symmetric gates `h/d ∈ {0.51 … 50}` (minimum `−1.8×10⁻¹⁵`, rounding) and for
300 random asymmetric geometries (`h₁, h₂ ∈ [d, 31d]`, layers anywhere inside; minimum of `S` relative to `2(1 − e^{−sd²})`:
`−2.4×10⁻¹¹`, rounding) and for the single-gate limit: no negative value above rounding. The proof makes this expected; the
numerics check the algebra, they are not independent evidence of the theorem.

## What this does and does not settle

* Settles: for ideal metal gates the kernel family of a dual-gated bilayer is inside the Cohn–Kumar class for every gate
  distance and layer placement. "Engineering the gates to break complete monotonicity" is excluded within this model.
* Does **not** settle: (a) non-ideal gates: a dielectric interface (hBN, SiO₂, with `κ = (ε₁−ε₂)/(ε₁+ε₂)`, `|κ| < 1`) gives image
  weights `κⁿ` and the Poisson form is no longer a pure cosine series: not proved, not tested; (b) finite in-plane screening of
  the gate (2D gate, Thomas–Fermi): a different kernel; (c) the Cohn–Kumar theorem itself is imported (the note's conditional
  Lean statement), so "the triangular lattice is optimal for the gated kernel" stays conditional on it; (d) quantum states:
  complete monotonicity is a statement about the *classical* ground state; it does not locate where the quantum fluid freezes.
* Lean: not done. A formalisation needs Mathlib's Poisson summation for the Gaussian (Jacobi theta) and the Laplace-transform
  representation; feasible, not cheap. After Poisson the argument is two lines of trigonometry.
