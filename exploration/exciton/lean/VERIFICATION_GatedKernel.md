# Verification report: `GatedKernel.lean`

Subject: `exploration/exciton/lean/GatedKernel.lean` (1083 lines, 52 `theorem`s, sha256
`3ef8152e8e6d9add956796b873a3e492d2d386431aa436ceb2d417422088d578`).
Date: 2026-10-11. Producer: one Claude Sonnet 5.5 session. **No independent verifier has read this file yet**
(unlike `ExcitonX1.lean` and `TorusBound.lean`); the machine check below is the Lean kernel's, the reading of the
statements is the producer's own. Per the project rule, an adversarial reviewer instance should read it before any
deposit.

Source theorem: `docs/designs/EXCITON_FLUID_GATE_IMAGE_CM.md`, "Statement" and "Proof". That note states "not formalised in
Lean"; this file is that formalisation.

## 1. Verdict in one paragraph

All three tiers were reached. T1 (trigonometric core, image bookkeeping) and T2 (positivity of the Laplace measure,
with the Poisson identity *derived*, not assumed) are proved unconditionally. T3 is proved in full: the image series of
`V_ee + V_hh - 2 V_eh` equals the Laplace transform of the non-negative density `mu(s) = (pi s)^(-1/2) S(s)` for every
`t > 0`, and that function satisfies the library's `AdmissiblePotential` (a verbatim copy of upstream's definition:
smooth on `(0,inf)`, non-negative, `(-1)^r g^(r) >= 0` for all `r`). No `sorry`, no new axiom, no hypothesis other than
`0 < h1 + h2`. All 17 `#print axioms` lines show exactly `[propext, Classical.choice, Quot.sound]`.

## 2. Compile command and output

```
export ELAN_HOME=/mnt/data/home/xavkal/.elan
cd /mnt/data/xdev-cache/lean-env/qfenv          # lakefile.toml: Mathlib v4.34.1 (d13f23b7), see LEAN_TOOLCHAIN_ALIGNMENT_v4_34_1.md
lake env lean --version
  -> Lean (version 4.34.1, x86_64-unknown-linux-gnu, commit 5045d0056413266e57c625dcd7c365b10e377c52, Release)
nice lake env lean /home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/exploration/exciton/lean/GatedKernel.lean
  -> exit 0; no warning, no error; 17 lines "depends on axioms: [propext, Classical.choice, Quot.sound]";
     real 1m44s on a machine with load average ~13 (about 1 min when idle). One lean process at a time.
```

`grep -n "sorry\|^axiom\|admit" GatedKernel.lean` returns only the docstring phrase "no `sorry`".
The file imports `Mathlib` only; it does not import `ExcitonX1.lean` (it carries its own verbatim copy of
`AdmissiblePotential`, as `TorusBound.lean` does).

## 3. Theorems, tier, and what is hypothesis versus proved

Hypotheses are real-number side conditions only (`0 < s`, `0 < t`, `0 < h1 + h2`, `0 < P`). **No theorem takes the Poisson
identity, a summability statement or a measure-theoretic fact as a hypothesis.**

| theorem | tier | statement | status |
|---|---|---|---|
| `trig_core` | T1 | `2 - cos 2a - cos 2b - 2cos(b-a) + 2cos(a+b) = 2(1-cos(b-a))(1+cos(a+b))` | proved |
| `trig_core_sq` | T1 | `2(1-cos(b-a))(1+cos(a+b)) = 2(sin a - sin b)^2` | proved |
| `trig_core_nonneg` | T1 | the combination is `>= 0` for all reals `a b` | proved |
| `image_plane_top`, `image_plane_bottom` | T1 | for any even kernel `f`, on the plane `z = h1` (resp. `z = -h2`, period `P = 2(h1+h2)`) the image offsets `z - 2h1 + z0 - Pn` are a bijective (`ℤ ≃ ℤ`) re-indexing of the direct offsets `z - z0 - Pn` (`n -> -n`, resp. `n -> -n-1`) | proved |
| `gGreen_top`, `gGreen_bottom` | T1 | the Gaussian lattice Green function `gGreen s h1 h2 z z0 = sum_n e^{-s(z-z0-Pn)^2} - sum_n e^{-s(z-2h1+z0-Pn)^2}` vanishes on both planes | proved (the sums are Lean `tsum`s; the equality is by the bijection, so it holds also where `tsum` is the junk value `0`: it is a statement about the multisets, which is what the bookkeeping claim needs) |
| `gsum_poisson` | T2 | `sum_n e^{-s(c-Pn)^2} = sqrt(pi/s)/P * sum_m e^{-pi^2 m^2/(P^2 s)} cos(2 pi m c/P)` for `s,P > 0`, every real `c` | **proved**, from `Complex.tsum_exp_neg_quadratic` (Mathlib); summability from `summable_jacobiTheta₂_term_iff` |
| `summable_gauss`, `summable_gauss_lin`, `summable_gsum_term`, `summable_wgt_cos` | T2 | the Gaussian series over `ℤ` (and shifted/modulated versions) are summable | proved |
| `Sm_nonneg`, `Sm_zero`, `Sm_le_eight` | T2 | `S_m >= 0` (by `trig_core_nonneg`), `S_0 = 0`, `S_m <= 8` | proved |
| `Sexc_eq_gsum` | T2 | `S(s)` of `V_ee + V_hh - 2V_eh` written with the six lattice sums | proved (definitional unfolding) |
| `Sexc_poisson` | T2 | `S(s) = sqrt(pi/s)/P * sum_m e^{-pi^2 m^2/(P^2 s)} S_m` | proved |
| `Sexc_nonneg` | T2 | `S(s) >= 0` for all `s > 0`, all `h1 + h2 > 0`, **all real** `z_e, z_h` | proved |
| `pow_exp_le`, `LaplaceData.int_pow`, `LaplaceData.hasDerivAt`, `lap_iteratedDeriv`, `lap_contDiffOn` | T3 | derivatives of all orders of `t -> int_0^inf e^{-st} mu(s) ds` under the integral sign; `iteratedDeriv r = (-1)^r int s^r e^{-st} mu` | proved |
| `lap_admissible` | T3 | Laplace transform of a measurable `mu >= 0` with `int e^{-st} mu < inf` for all `t>0` is `AdmissiblePotential` (the easy direction of Bernstein) | proved |
| `muExc_nonneg`, `muExc_poisson`, `muExc_le_large`, `muExc_le_small`, `muExc_bounded`, `muExc_continuousOn`, `muExc_laplaceData` | T3 | `mu(s) = (pi s)^(-1/2) S(s)` is non-negative, continuous, **bounded** on `(0,inf)` (for `s >= 1` by the three-term bound; for `s <= 1` by the Poisson form, `mu <= 8 K/(P gamma_0)`), hence a legitimate Bernstein density | proved |
| `gatedKernel_admissible` | T3 | `t -> int_0^inf e^{-st} mu(s) ds` is `AdmissiblePotential` | proved |
| `atom`, `integrableOn_atom`, `integral_atom`, `atom_sub_norm_integral` | T3 | `int_0^inf (pi s)^(-1/2) e^{-s(t+x^2)} ds = (t+x^2)^(-1/2)` (Gamma(1/2)) and `int |atom_x - atom_y| = |k_x - k_y|` (constant sign in `s`) | proved |
| `kdiff_le`, `kdiff_summable` | T3 | `|(t+x^2)^(-1/2) - (t+y^2)^(-1/2)| <= 12 |c'-c|/P^2 * n^(-2)` for `P|n| >= 2(|c|+|c'|)+1`; summable over `ℤ` | proved |
| `Fn_integrable`, `Fn_integral`, `Fn_norm_integral_le`, `Fn_tsum` | T3 | termwise integrals, the `L^1` bound `2|k0-k3| + |k1-k4| + |k2-k4|`, and the pointwise sum equals `(pi s)^(-1/2) e^{-st} * (combination of gsum)` | proved |
| `Uimg_summable` | T3 | the grouped image series is summable (so `tsum` is genuine) | proved |
| `Uimg_eq_lap` | T3 | `Uimg t h1 h2 ze zh = int_0^inf e^{-st} mu(s) ds` for all `t > 0` | proved (interchange via `integral_tsum_of_summable_integral_norm`) |
| `admissible_congr` | T3 | `AdmissiblePotential` transfers along equality on `(0,inf)` (uses `EventuallyEq.iteratedDeriv_eq`) | proved |
| **`imageSeries_admissible`** | T3 | **`t -> Uimg t h1 h2 ze zh` is `AdmissiblePotential` for every `h1 + h2 > 0` and every `z_e, z_h`** | proved |

Definition of `Uimg` (the object whose complete monotonicity is claimed), with `P = 2(h1+h2)`,
`k(c, n) = (t + (c - P n)^2)^(-1/2)`:

```
Uimg t = sum_{n in Z} [ 2 k(0,n) - k(ze-2h1+ze, n) - k(zh-2h1+zh, n) - 2 k(zh-ze, n) + 2 k(zh-2h1+ze, n) ]
```

i.e. `V_ee + V_hh - 2V_eh`, each `V` being the image series of the note (direct images at offset `z - z0 - Pn`, sign `+`;
reflected images at `z - 2h1 + z0 - Pn`, sign `-`), summed `n` by `n` so that the series converges absolutely
(`Uimg_summable`). A hand check that this is the intended object (not a proof): direct summation of `Uimg` in
Python for `h1 = h2 = 1e4`, `d = 0.5`, `t in {0.01, 0.1, 1, 4, 25}` reproduces `2/sqrt(t) - 2/sqrt(t+d^2)` to 10
digits, and for `h1 = 1, h2 = 1.5`, `t in [0.05, 10]` (400 points) the first, second and third finite differences have the
signs `-, +, -`. These numerics are a fidelity sanity check of the definition, not evidence for the theorem.

## 4. Negative controls (fail by design, and do)

| theorem | what it shows |
|---|---|
| `wrong_sign_not_nonneg` | `0 <= 2 - cos 2a - cos 2b - 2cos(b-a) - 2cos(a+b)` (sign of the `cos(a+b)` image term flipped) is false: `a = b = 0` gives `-4` |
| `wrong_sign_not_identity` | the factorisation `= 2(1-cos(b-a))(1-cos(a+b))` is false for the same wrong sign (`a = b = 0`: `-4` versus `0`) |
| `unneutral_not_nonneg` | dropping the `V_hh` term (a non-neutral combination `V_ee - 2V_eh`, mode factor `1 - cos 2a - 2(cos(b-a) - cos(a+b))`) is not non-negative: `a = b = pi/2` gives `-2`. This is the Lean form of the note's remark that only the neutral combination factorises |

Each is proved as `¬ ∀ ...` by instantiation and `norm_num`; the three `#print axioms` lines show the standard axioms.

## 5. What is not proved, and the limits of the statement

1. **Model.** Perfect grounded planes, homogeneous dielectric (a prefactor), point charges in the layers, Coulomb `1/R`.
   Not covered: dielectric-interface gates (`kappa^n` image weights), finite in-plane screening of the gates, quantum
   states. These are the note's own non-claims (a), (b), (d); they are untouched.
2. **Cohn-Kumar is not proved or used.** The statement "the triangular lattice is optimal for the gated kernel" stays
   conditional on the imported theorem (`TorusBound.lean` states the conditional form). What this file closes is the
   note's "Lean: not done" remark for the *complete-monotonicity* claim only.
3. **Bernstein's converse is not needed and not proved.** What is used and proved is the easy direction (Laplace
   transform of a non-negative density is completely monotone), in the library's own convention. The note's wording
   "by Bernstein's theorem this is exactly the hypothesis of Cohn-Kumar" is consistent with that, but the equivalence of
   "completely monotone in the sense of `AdmissiblePotential`" with "Laplace transform of a measure" is not formalised.
4. **Layer positions.** The theorem holds for all real `z_e, z_h`, not just between the gates; `Sm_nonneg` never uses
   betweenness. Read physically it applies when `-h2 < z_e, z_h < h1`. The positions `h1 - z_e` etc. enter only through
   cosines.
5. **Green function.** The identification of `Uimg` with "the Green function of the grounded box" rests on the explicit
   image formula (positions/signs as in the note; `image_plane_top/bottom` and `gGreen_top/bottom` check the vanishing on
   the planes). Uniqueness of the Dirichlet Green function is not formalised.
6. **Non-triviality.** `AdmissiblePotential` is satisfied by `0`. This file does not prove `Uimg > 0`; the numerics of
   section 3 show it is positive and the representation shows `Uimg >= 0`, but a strict-positivity theorem is not stated.
7. **Review.** Producer-only so far (see the top). The `LaplaceData` structure and the `Uimg` definition are the two places
   where a reader should check that the Lean statement is the one intended; the docstrings and this report give the
   mapping.

## 6. Provenance of the proof (for reviewers)

* Poisson step: `Complex.tsum_exp_neg_quadratic` with `a = s P^2/pi`, `b = s c P/pi`, real part taken after proving the
  summability of the transformed series via `jacobiTheta₂_term` (`summable_gauss`).
* Differentiation under the integral: `hasDerivAt_integral_of_dominated_loc_of_deriv_le` with the dominating function
  `C e^{-s t0/4} mu(s)` obtained from `s^k e^{-as} <= k! (2/a)^k e^{-as/2}` (`pow_exp_le`, from
  `Real.pow_div_factorial_le_exp`).
* Interchange of `sum_n` and `int ds`: `integral_tsum_of_summable_integral_norm`; the `L^1` norm of each grouped term is
  bounded by first differences of atoms, which have constant sign in `s`, so `int |.| = |difference of the t-space
  values|`, and those are `O(n^-2)` (`kdiff_le`).
* Mathlib name churn met: `tsum_le_tsum` is now `Summable.tsum_le_tsum`; `push_neg` is deprecated (not used in the final file).
* Intermediate pieces were compiled as separate scratch modules (in the session scratchpad, outside the repository); the
  final file was compiled whole, once after each edit, as in section 2.
