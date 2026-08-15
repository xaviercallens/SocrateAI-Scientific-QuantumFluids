# M3 Report — the W4 comparison: closed without a quantitative result

**Status:** closed. No quantitative or ordinal W4 claim is established.
**Date:** 2026-08-15
**Owner decision:** stop after four failed measurement rounds (2026-08-15).

---

## 1. The outcome, stated plainly

**The W4 comparison — does a dispersive regulator differ measurably from a truncation
control — has not been answered, and this project did not answer it.** Four measurement
rounds were run under increasingly strict pre-registration. All four failed, and the
fourth failed for a reason that invalidates the first three as well: **the measurements
were single trajectories of a chaotic system, and the effect being sought is smaller than
the trajectory-to-trajectory scatter.**

This is not a negative *result* about the physics. It is a statement about what this setup
could resolve. The distinction matters and is kept throughout.

---

## 2. What was retracted, and why

| result | round | status | reason |
|---|---|---|---|
| β for `sup_t Ω` vs D | 1 (pre-relaunch) | retracted | horizon artifact — `sup_t Ω` degenerates to the `k_N²E` ceiling |
| β on first-peak observable | 2 | retracted | non-monotonic in the sweep; conventions disagreed |
| β for τ_f vs D | 3 | retracted | failed its own battery; later shown to be noise-fitting |
| ordinal censoring order | 3 | **retracted** | single-sample artifact: at D=0.05, 3 of 6 realisations censored, 3 attained |
| α for excess delay Δτ | 4 | killed | own pre-registered criterion, spread 4.88 vs 0.05 tolerance |
| "dispersion accelerates at small D" | 4 | withdrawn | 2–20% signal against 72–105% scatter |
| Option C sign-consistency | C | unestablished | also single-trajectory |

Every retraction is recorded in `LEDGER.md` with its reason; none was silently dropped.

---

## 3. The methodological finding (CLAIM-014) — the durable output of M3

At fixed D, with identical |aₙ|, identical energy, and only initial phases varied, the
thermalization time τ scatters by **72–105% of its mean** (CV 23–49%). At D = 0.05, **three
of six realisations were censored while three attained**. Rounds 3 and 4 used **n = 1**.

A 5% measurement of the mean requires **n ≈ 22–97 realisations per point** — one to two
orders of magnitude more compute than was spent.

**Why the validation battery missed it.** The battery grew to six criteria, each added
after a real failure. Every one tested *deterministic* reproducibility: the same trajectory
at finer timestep, finer trace sampling, or a neighbouring parameter on the same trajectory
family. **None tested statistical reproducibility across trajectories drawn from the same
physical ensemble.** In a chaotic system that is the binding constraint, so dt-refinement
passing at 0.00% on all twelve points of round 3 was silent about the thing that mattered —
it is the wrong limit. Criterion **B8** now exists and is specified to run *first*, being
cheap relative to a sweep and decisive about whether the sweep is worth running.

**It also unifies the failure history.** "Seven observables, six failure modes" was the
wrong reading. The parameter-discontinuity, own-parameter drift, non-monotonicity and B3′
failures are all consistent with one cause. (Horizon divergence is genuinely separate: that
concerns the `k_N²E` ceiling, not sampling.)

**And it explains a false corroboration.** The "acceleration at small D" appeared in all
four (f, convention) combinations, which read as mutual confirmation. It was not — those
sub-analyses shared a trajectory. *Consistency across sub-analyses is not evidence when they
share a source of noise.*

---

## 4. What stands

Everything analytic or deterministic is untouched by the sampling problem:

- **CLAIM-004** — Positive Control #1 at exactly `0.00e+00`: the complexified model
  reproduces MechanicaFluidorum's independent implementation bit-for-bit across ~2.4×10⁶
  RK4 steps. Deterministic; the exactness explained (powers of two preserve the mantissa).
- **CLAIM-007, CLAIM-011 (Tier A, Lean)** — exact energy conservation of the conjugated
  complexification, the invariant real subspace, and the **Liouville property**: the
  complexified flow preserves phase-space volume while the real Katz–Pavlović model does
  not. Eight theorems, axiom footprint `[propext, Classical.choice, Quot.sound]`.
- **CLAIM-010** — the conserving-seam condition `Re(conj(v_N)²·v_{N+1}) = 0`, which
  resolved W2's open question analytically and showed the complexification admits a
  conserving bounce with no real analogue.
- **CLAIM-005/008/009** — the `sup_t Ω` degeneracy and its extension to all three E1 §4
  regulators; these concern behaviour in `T` against a fixed ceiling, not sampling.
- **All of M1** — the Landau fit reproducing Godfrin et al.'s published data to 0.2–0.33%
  against six independently-attributed determinations. Deterministic.
- **The literature reframing** — the phenomenon identified as absolute-equilibrium
  thermalization, with ten verified citations ([LIT-011]–[LIT-020]) and an explicit
  novelty withdrawal: prior art exists for shell models (Thalabard–Turkington 2016 and
  others), so the observation is a re-expression, per Rule E-X.

**CLAIM-012 (equipartition) — does NOT stand as stated.** I drafted this section
asserting the analytic/deterministic results were unaffected, then tested the one entry
whose status I had only assumed. Time-averaging was hypothesised to self-average away the
trajectory noise. **It does not:** fixed-D ensemble CV is 25.5% (D=0) and **84.0%**
(D=0.02), the latter spanning 6.0–57.1 across four realisations. The reported percentages
(88.6% / 108.3% / 73.0%) are single-trajectory draws from those distributions and are
withdrawn, along with the "regulator's signature is in the transient" inference that rested
on 4× differences between single-trajectory quarter-means.

What survives is weak: at D = 0 the ensemble mean is 85.5% of the prediction with SEM
≈ 12.7% (n=4) — consistent with equipartition within about 1.1σ. The equipartition
*formula* is analytic and unaffected; its empirical verification at the claimed precision
is not.

This is the second time in this closing sequence that checking rather than asserting
changed the answer. The boundary of a retraction is not self-evident and should be
measured, not drawn by intuition about which results "feel" deterministic.

---

## 5. What it would take to answer the W4 question

Not another observable. **Ensemble measurement**: n ≈ 22–97 realisations per parameter
point, with B8 run first to size it, fitting ensemble means rather than single
trajectories. That is hours of compute at this grid size, and it may still find no
exponent — the effect, if real, is currently known only to be smaller than the resolution
of what was spent.

A cheaper intermediate exists and was declined: ~30 realisations at two D values, testing
only whether the *direction* survives averaging. Recorded here so a future reader knows the
option was considered rather than overlooked.

---

## 6. An honest note on the process

Four rounds is a lot of failure. The pre-registration discipline is what kept it from
becoming four rounds of *claims*: every round had its criteria fixed in advance, and every
round's failure was caught by its own criteria rather than by later embarrassment. The
round-4 kill criterion fired on a script that printed the verdict itself, written before the
data existed. The one thing that repeatedly escaped the discipline — statistical
reproducibility — is now a criterion.

The Liouville result, the seam algebra, and the literature reframing all came out of
follow-up questions asked *because* the measurement was failing. That is not compensation
for the failure, but it is where the value of M3 actually landed.
