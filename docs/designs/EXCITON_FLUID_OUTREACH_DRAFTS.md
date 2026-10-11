# Outreach drafts (2026-10-11): mathematician, Lean community, Mathlib, experimental group

Nothing here has been sent or posted. Review, edit, and send under your own name. All texts disclose the AI authorship,
because the Lean file and the note were produced with an AI system and checked by other instances of it.

Facts to keep straight in every message:
* The note is `paper/gated_kernel_note.tex` (4 pages). Its Theorem 1 is elementary and may be known (a Dirichlet Green function in a
  product domain is a non-negative mixture of 2D heat kernels, applied to a neutral charge combination).
* The Lean file is `exploration/exciton/lean/GatedKernel.lean` (1083 lines, 52 theorems, no `sorry`, axioms `propext`,
  `Classical.choice`, `Quot.sound`), Lean 4.34.1 / Mathlib v4.34.1. It does NOT prove universal optimality of the triangular lattice.
* The planar universal-optimality claim comes from an AI-generated, unrefereed repository; do not call it proved.
* Zenodo records: paper I 10.5281/zenodo.23294615, II 10.5281/zenodo.23297479, III 10.5281/zenodo.23298292.

---

## 1. Cover email to the mathematician (Frédéric Legoll; you wrote "Legoff": check the spelling before sending)

Subject: A short note on complete monotonicity of image-charge interactions in a slab: is it known?

Dear Professor Legoll,

I am an independent researcher (SocrateAI Research). I am writing with a short note (4 pages, attached) and a Lean 4 file, and one
precise question: is the following statement already in the literature?

*For two neutral charge pairs (electron/hole planes at heights z_e, z_h) in a slab between two grounded perfect conductors, the pair
interaction U(r) built from the Dirichlet Green function is completely monotone in r^2; indeed U(r) = ∫ e^{-r²σ} μ(σ) dσ with
μ ≥ 0 bounded.* The proof in the note uses the product structure of the slab's Dirichlet heat kernel and the positive definiteness of the
transverse factor (a sum of squares), and extends to any laterally homogeneous layered dielectric.

One unconditional consequence (Proposition 3 of the note): since U is a non-negative mixture of Gaussians, the classical minimality of
the triangular lattice for theta functions among Bravais lattices (Montgomery 1988; Rankin, Cassels, Ennola, Diananda) gives that the
triangular lattice minimises the U-energy among lattices, for all geometries. I would be grateful if you could confirm that reduction.

Why I ask: complete monotonicity in r² is the hypothesis of the Cohn–Kumar universal-optimality framework. A planar statement
(triangular lattice) is claimed in an AI-generated, unrefereed repository; I do not treat it as proved, and the note says so. Our result is
only the hypothesis check.

Full disclosure: the note and the Lean file were produced with an AI system and checked by other instances of it. I have not had a
human mathematician read them, which is the purpose of this email. If it is routine or known, a pointer to the reference is the most
useful answer; if there is an error, even better.

Attached: gated_kernel_note.pdf. Lean file and the numerical check are in the repository:
https://github.com/xaviercallens/SocrateAI-Scientific-QuantumFluids (exploration/exciton/lean/GatedKernel.lean,
exploration/exciton/python/gated_note_check.py).

With thanks for your time,
Xavier Callens

---

## 2. Lean Zulip (leanprover.zulipchat.com), stream "mathlib4" or "Is there code for X?" or "new members"

Subject: Complete monotonicity of a Laplace transform / image-charge kernel: Lean file, and a proposal for `CompletelyMonotoneOn`

Hi all. I have a 1083-line Lean 4 file (Lean 4.34.1, Mathlib v4.34.1, `import Mathlib` only, no `sorry`, only the three standard axioms)
that formalises: a sum of image-charge terms in a slab between two grounded planes equals the Laplace transform ∫₀^∞ e^{-ts} μ(s) ds of
an explicit non-negative bounded density, hence is smooth with (-1)^r g^{(r)} ≥ 0 for all r. The Poisson summation step is derived from
`Complex.tsum_exp_neg_quadratic` (so Mathlib's Gaussian/theta API did the heavy lifting).

Two honest points. (1) The file and the accompanying note were produced with an AI system (Claude) and checked by a second instance;
no human Lean expert has read it, which is why I am posting. (2) The mathematics is elementary and may be known; the Lean content
that might be of general interest is small and generic: a definition of completely monotone functions and "Laplace transform of a
non-negative density is completely monotone" (the easy direction of Bernstein), differentiation under the integral to all orders.

Question: Mathlib has `AbsolutelyMonotoneOn` (Analysis/Calculus/AbsolutelyMonotone.lean) but I found no completely monotone class and
no Laplace transform of measures in v4.34.1. Is anyone working on this, or would a PR adding `CompletelyMonotoneOn` (defined parallel to
`AbsolutelyMonotoneOn`) and the easy-Bernstein lemma be welcome? Is there a preferred formulation (via `AbsolutelyMonotoneOn` of
`x ↦ f (-x)`, or an `iteratedDerivWithin` formulation)?

Repository (file and verification notes): https://github.com/xaviercallens/SocrateAI-Scientific-QuantumFluids,
path `exploration/exciton/lean/GatedKernel.lean`; short math note attached/linked. Reviews of the statement fidelity (does `Uimg` encode the
image series correctly?) would be especially welcome.

---

## 3. r/lean4 post

Title: "A Lean 4 formalisation (AI-assisted, no sorry) that an image-charge kernel is a Laplace transform of a non-negative density: request for review"

Body: I would like human eyes on a 1083-line Lean 4 file (Lean 4.34.1, Mathlib v4.34.1) proving that the electrostatic interaction between
two neutral electron–hole pairs between two grounded planes is completely monotone in r². Route: Gaussian lattice sums, Poisson summation
(derived from Mathlib's Jacobi-theta/Gaussian results, not assumed), a trigonometric core 2−cos2a−cos2b−2cos(b−a)+2cos(a+b) =
2(sin a − sin b)² ≥ 0, then differentiation under the integral to all orders. 52 theorems, no `sorry`/`axiom`/`native_decide`, 17
`#print axioms` all standard.

Disclosure: written with an AI system and verified by another AI instance (it recomputed the kernel with its own image sum and compiled
it); no human Lean reviewer yet. The result is mathematically elementary and the planar optimality theorem it is meant to feed is
**not** proved here (that statement is unrefereed). Feedback on statement fidelity and style is what I am after; I will also ask on Zulip
about contributing a small `CompletelyMonotoneOn` API to Mathlib.

Link: repository path above.

---

## 4. Mathlib contribution plan (what I recommend; the PRs must come from your GitHub account)

`GatedKernel.lean` itself is domain-specific and should NOT be PR'd as is (Mathlib wants general lemmas, small PRs, and
conventional naming). The generic pieces are in lines 363–525 of the file (`AdmissiblePotential`, `pow_exp_le`, `LaplaceData`,
`LaplaceData.int_pow`, `.hasDerivAt`, `lap_iteratedDeriv`, `lap_contDiffOn`, `lap_admissible`).

Steps (do 0 first; it decides whether anything else is useful):

0. **Duplicate check.** Search Mathlib master and the open PRs/Zulip for `CompletelyMonotone`, `LaplaceTransform`,
   `Bernstein`. The pinned v4.34.1 tree has `Mathlib/Analysis/Calculus/AbsolutelyMonotone.lean` (Douglas, 2025) and no completely
   monotone class; master may differ. Read the current Mathlib contribution guide and its policy on AI-assisted contributions, and
   disclose the AI assistance in the PR.
1. **PR A (small).** `Mathlib/Analysis/Calculus/CompletelyMonotone.lean`: `CompletelyMonotoneOn f s` parallel to
   `AbsolutelyMonotoneOn` (e.g. `∀ n, ∀ x ∈ s, 0 ≤ (-1)^n * iteratedDerivWithin n f s x` on a set with unique derivatives, or
   via a Taylor-series formulation as in the existing file), plus API: `contDiffOn`, `add`, `smul`, `mul` (product of CM functions),
   `comp` with an absolutely monotone map is optional. Agree the formulation on Zulip first.
2. **PR B.** Laplace transform of a non-negative measurable density with finite exponential moments is completely monotone on `Ioi 0`
   (generalise `LaplaceData`; use `hasDerivAt_integral_of_dominated_loc_of_deriv_le`). This is the easy direction of Bernstein's theorem.
3. **PR C (optional).** A lemma on Gaussian lattice sums with a shift (`gsum_poisson`), if the existing
   Gaussian/theta Poisson API (the file builds it from `Complex.tsum_exp_neg_quadratic`) lacks the real-shifted cosine form;
   check the current API first.
4. Keep the physics file (image charges, `Uimg`, `Sexc_nonneg`) in the repository, or in a separate downstream project; cite
   Mathlib's new CM API once merged.

Draft PR A description:

> **feat(Analysis/Calculus): completely monotone functions**
> Adds `CompletelyMonotoneOn`, parallel to `AbsolutelyMonotoneOn`, with basic API (smoothness, closure under addition, scalar
> multiplication by nonnegatives, product). Motivation: Laplace transforms of nonnegative measures are completely monotone; this is the
> easy direction of Bernstein's theorem (follow-up PR). AI-assisted drafting; reviewed and tested by the submitter.
> Discussion: [Zulip thread link].

Practical: fork Mathlib, branch from master, run `lake build` on the new file and `lake exe lint-style`/`#lint` as in the
contribution guide, link the Zulip thread in the PR, expect several review rounds and a likely rewrite of the definition.
Do not claim the planar universal-optimality theorem in any PR text.

---

## 5. One-page summary for the experimental dipolar-exciton group (and the fluid-dynamics/mechanics forum thread)

**What we are asking.** Only one item of a six-item protocol (L1 of paper I, 10.5281/zenodo.23294615) can be falsified by a
measurement: *the interaction strength of dipolar excitons against gate separation D, in a dual-gated bilayer.*

**The prediction, stated plainly.** In the weak-correlation (mean-field) regime, the blueshift slope of the photoluminescence peak with
exciton density is the zero-wavevector coefficient of the gated kernel,

  dE/dn = Ũ(0) = (4π e² d/ε)(1 − d/D)  (uniform ε; for hBN stacks use the piecewise-ε factor),

increasing with D, with the single-gate device approaching the ungated 4π d. This is a capacitor-type formula (textbook), not a new result
and not a test of any lattice theorem. Its value for us is as a falsification check of the *ideal grounded-plane image-charge model*
(and hence of the completely monotone structure we proved for that model) on a real device.

**Pass/fail.** Compare the trend with D and the single-gate control, not the absolute value: fail if the slope is independent of D
within 10% over D/d ∈ [3, 20] in the weak-correlation regime, or if the trend is opposite. In the strongly correlated regime the slope
is the classical lattice value, 0–0.6 of Ũ(0) over nd² = 0.003–0.3, D/d = 3–50 (reviewer's mode sum), so the weak-correlation
regime must be established first (L2: structure factor versus density and temperature; calibration, no number predicted).

**Confounders.** Correlation corrections depending on D and n, density calibration (calibrate independently of the PL blueshift),
heating, lateral inhomogeneity, finite gate screening, non-ideal gates.

**What is not claimed.** No exciton Bose–Einstein condensation, no phase boundary, no comparison with data; all model parameters
in the numerical papers are dimensionless placeholders; the lattice-optimality theorem we depend on for the *structural* statement is
unrefereed. The honest value of the exercise is to see whether an ideal-image-charge description of gated dipolar excitons holds
up quantitatively, not to confirm a deep theorem.

Documents: paper I (protocol, Section "Laboratory protocol"), papers II and III (numerics, negative results), the 4-page note.
