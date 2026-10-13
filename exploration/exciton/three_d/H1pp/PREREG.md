# H1'' — rigorously certified two-point LP lower bounds for the Gaussian energy (pre-registration, 2026-10-13)

Directory `three_d/H1pp/`. Successor of H1' (`../H1p/`), whose values are numerical and **not certified** (paper V v2,
10.5281/zenodo.23324893). H1' amendment A1 and `../H1p/DEV_NOTES.md` record why the H1 code cannot be certified: its LP
enforces f <= g and f̂ >= 0 with an absolute tolerance in double precision, so relative violations are huge where
g or e^{-t/2} underflow. This round is the "different construction" those notes call for.

## Literature (read before registering)

- Cohn & de Courcy-Ireland, arXiv:1603.09684 v6. Table 1.1 (α = π, ρ = 1) gives "the numerically optimized linear
  programming bound" d = 1: 0.08643481..., d = 2: 0.15959526..., d = 3: 0.22321782... The text calls these values
  numerically optimised; it gives no statement of rigorous verification. Its **Theorem 1.4** is a rigorous closed-form
  LP bound (Bessel-root interpolation), tabulated as d = 2: 0.15702654..., d = 3: 0.21736068... at α = π.
  Proposition 2.2 (LP bound, arbitrary configurations of density ρ) is the theorem we use.
- A search (alphaXiv, 2026-10-13: "rigorous LP lower bounds Gaussian core model") found computer-assisted
  results for other problems (Lennard-Jones lattice energies, Thomson N = 5, sphere-packing dual bounds), and no
  certified d = 2, 3 Gaussian-energy LP values. The search was not exhaustive; if certified values exist, ours are
  an independent check, not a first.

So the claim at stake is narrow: **interval-certified** two-point bounds, reproducing the published numerical values
from below, and certified d = 3 values at α = 2, 4, 8.

## Method (code: `rig2.py`, `hp_lp.py`, `rig.py` helpers; frozen at the commit of this file)

Ansatz and variables as H1: f̂ = e^{-t/2} Q(t), f = β^{d/2} e^{-u/2} R(u), Q = Σ c_k L_k^{(d/2-1)}, R = Σ (−1)^k c_k L_k,
t = 2π|y|²/β, u = 2πβ|x|² = 2bα|x|², b = πβ/α, f/g = β^{d/2} e^{-κu} R(u), κ = (1 − 1/b)/2.
Effective degree K_eff odd (K = 40 → c_40 = 0, K_eff = 39), top coefficient c_K_eff < 0 (Q → +∞, R → −∞).

1. **LP in 256-bit arithmetic** (python-flint arb midpoints; primal-dual interior point, Mehrotra; `hp_lp.py`).
   Rows, each normalised to unit max-norm: f/g <= 1 on u ∈ (0, u1] (3000 points, quadratic in u), u1 = 2b ln(10^12)
   (g(x1) = 1e-12); R(u) <= −10^-12 (normalised row units) on [u1, 4u1] (1500 linear points) and a log grid [4u1, 10^4 u1] (300 points);
   Q(t) >= 0 on t ∈ [0, 200] (4000 linear points), on [200, T(y = 12)] (1000 quadratic points) and a log grid beyond
   (150 points). No row is ever removed.
2. **Cutting planes from exact objects:** coefficients made exact (dyadic rationals); the critical points of f/g
   (real roots of R' − κR, rigorously isolated by flint) with f/g > 1 − 1e-9 are added with a cluster of neighbours;
   intervals where R > 0 beyond u1 or Q < 0 (between rigorously isolated real roots) receive 11 rows each; local
   maxima of f/g within 1e-12 of 1 on a 20 000-point fine grid are added too. **Every round's coefficient vector is
   certified** (step 3, box limit 2·10^5 per check); the reported value is the **best certified B over rounds**
   (any certified vector gives a valid bound, so this selection cannot invalidate it). Rounds stop when the maximum of
   f/g − 1 is <= 1e-30 and the LP value changes by < 1e-25, or at the round cap; the best vector is then
   re-certified with the full box limit (5·10^6).
3. **Certificate** (exact rationals + arb interval arithmetic, `HPRig.certify`):
   (a) R < 0 beyond U = max(u1, 1.0001·(largest real root of R) + 1), proved by root isolation and the sign at U;
   (b) f/g <= 1 + τ0 on [0, U] by bisection with a centred-form enclosure; τ0 starts at 2 × the sampled excess + 1e-35
       and is multiplied by 16 on failure (give up above 1e-6: "not certified");
   (c) f̂ + δ e^{-π|y|²/(λβ)} >= 0 with λ from the ladder λ0·2^j, j = 0..6, λ0 = max(2, smallest integer >= 1/b + 1)
       (every λ >= 1/b is valid; the λ with the largest estimated B is proved first, the next ones on failure):
       Q > 0 off the rigorously isolated root intervals; on intervals where Q < 0 (and on all root balls)
       Q(t) + δ e^{(1 − 1/λ)t/2} >= 0 is proved by bisection with Taylor-shift enclosures; δ = 4 × the sampled worst
       value of −Q(t)e^{−(1 − 1/λ)t/2} + 1e-60;
   (d) the lift adds at most δ(λβ)^{d/2} to f/g everywhere (λ >= 1/b), so τ = τ0 + δ(λβ)^{d/2};
   (e) **B = [Q(0) + δ − β^{d/2}R(0) − δ(λβ)^{d/2}] / (1 + τ)**, the lower end of the arb ball is the certified bound.
   Validity: f continuous, integrable, radial; f̂ + lift >= 0; f_total <= (1 + τ) g for x ≠ 0 ⇒ Proposition 2.2 of
   1603.09684 applied to f_total/(1 + τ).

## Settings (registered)

K = 40 (K_eff = 39) for every gate; K = 30 (K_eff = 29) also run and reported. gcut = 1e-12; round cap 25.
b = the H1' K = 40 best value (`../H1p/records/solutions/*_K40.json`, snapped to a rational with denominator <= 100):
V1a (d = 1, α = 1): 1.3416 → 106/79; V1b (d = 1, α = π): 1.0954 → 23/21; V2 (d = 2, α = π): 1;
V3 (d = 3, α = π): 17/20; H2 (α = 2): 106/79; H4 (α = 4): 7/10; H8 (α = 8): 0.2928 → 29/99.
The certificate is valid for any b, so b only affects the value; no other b is run in this registration.
α = π is represented exactly (arb π); α ∈ {1, 2, 4, 8} exactly.

## Void conditions (a violation is a bug, not a result)

B > E_Z(α) (d = 1, 60-digit sum); B > E_A2(π) (d = 2); B > min(E_FCC, E_BCC)(α) (d = 3, lattice sums of
`../H1/lp_bound.py`, double precision: a violation by less than 1e-12 relative is reported, not voided).

## Gates (in order; a failed gate stops the later ones)

For wall-clock reasons all 14 runs (7 cases × K ∈ {40, 30}) are launched in parallel (`run_h1pp.py`, evaluation
`evaluate.py`, gate on K = 40). If a gate fails, the later cases' numbers are reported only as "gated", not as
registered results.

- **V1 (d = 1, α ∈ {1, π}):** B certified and E_Z − B <= 1e-8 · E_Z.
- **V2 (d = 2, α = π):** B certified and B >= 0.15959526 − 1e-8.
- **V3 (d = 3, α = π):** B certified and B >= 0.22321782 − 1e-8. Also reported: B − 0.21736068 (CdCI Theorem 1.4).
- **H1'' (d = 3, α ∈ {2, 4, 8}), only if V1–V3 pass:** certified B and G = (min(E_FCC, E_BCC) − B)/min(...). Read as
  H1/H1': G > 1e-3 at all three α → two-point bounds insufficient at these α (certified). **Prediction:** G > 1e-3
  at all three, and B within 1e-6 relative below the H1' numerical values (1.011018287, 0.07275645512,
  0.0003947635566).

"Certified" means the certificate steps (a)–(e) completed. A case whose certificate fails is reported as "not
certified", with the failing step; it fails its gate.

## Development (non-gate parameters only)

d = 1, α = 2, b = 3/2; d = 3, α = 3, b = 1 (K = 30 and 40); d = 2, α = 2, b = 1 (K = 40) (`dev/`, logs
`dev/dev*.log`). Findings: `DEV_NOTES.md`.
