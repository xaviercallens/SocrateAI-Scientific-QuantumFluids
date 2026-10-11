# Mathlib PR kit: completely monotone functions (2026-10-11)

Files (Mathlib module style, header and docstrings in Mathlib convention):

* `CompletelyMonotone/Basic.lean` (target: `Mathlib/Analysis/Calculus/CompletelyMonotone/Basic.lean`), PR A.
  `CompletelyMonotoneOn f s`, defined exactly like `AbsolutelyMonotoneOn` (a Taylor series witness with
  `(-1)^n * p x n (fun _ => 1) ≥ 0`); `contDiffOn`, `of_contDiff`, `iteratedDerivWithin_nonneg`,
  `iff_iteratedDerivWithin_nonneg` (under `UniqueDiffOn`), `add`, `smul`, and `completelyMonotoneOn_exp_neg_mul`.
* `CompletelyMonotone/ExpIntegral.lean` (target: `.../CompletelyMonotone/ExpIntegral.lean`), PR B (depends on PR A).
  `completelyMonotoneOn_integral_exp_neg_mul`: `t ↦ ∫ s in Ioi 0, exp (-(s*t)) * μ s` is completely monotone on `Ioi 0` for
  a nonnegative a.e.-strongly-measurable `μ` with finite integrals for all `t>0` (easy direction of Bernstein). Extracted and
  generalised from `GatedKernel.lean` lines 363-525; no dependence on any LaplaceTransform file (restate for `laplace` once
  PR #40582 lands).
* `CompletelyMonotoneCombinedTest.lean`: both files in one module, the file actually compiled.

## Compile status (honest)

* Built with Lean 4.34.1 / Mathlib v4.34.1 (`lake env lean`, qfenv environment): no errors, no warnings, no `sorry`;
  `#print axioms` for the five main declarations: `[propext, Classical.choice, Quot.sound]`.
* NOT yet tested on Mathlib master; NOT linted (Mathlib's `lake exe lint-style`, `#lint`, `shake`, import minimisation
  need a Mathlib checkout and were not run); the two-file split with `public import` is compiled only as one combined module.
* Not included (deliberately): `mul` (Leibniz), the Bernstein converse, a link to `AbsolutelyMonotoneOn` via `x ↦ f (-x)`.

## State of Mathlib master on 2026-10-11 (GitHub API)

* No `CompletelyMonotone` in the code search; no issue/PR with that name.
* `Mathlib/Analysis/Calculus/AbsolutelyMonotone.lean`: merged (PR #38026, Michael R. Douglas, AI-assisted with
  disclosure); the author's split PR #37879 listed "Bernstein backward direction" as a follow-up.
* Open PR #40582 `feat(Analysis): the one-sided Laplace transform` (author dennj, updated 2026-10-04): defines `laplace`,
  `LaplaceConvergent`, `HasLaplace`; contains no complete-monotonicity result. Coordinate with it before PR B.
* Open PR #40280 one-sided differentiation under the integral (mrdouglasny): possibly relevant to PR B.

## Steps for the submitter

1. Fork Mathlib, branch from master, place the two files, add `import` lines to `Mathlib.lean` (`lake exe mk_all`).
2. Build, then run the style/lint tooling of the current contribution guide; fix.
3. Post on Zulip first (see docs/designs/EXCITON_FLUID_OUTREACH_DRAFTS.md), agree the definition with Douglas/maintainers, then open PR A.
4. Disclose the AI assistance in the PR description, as in PR #38026.
