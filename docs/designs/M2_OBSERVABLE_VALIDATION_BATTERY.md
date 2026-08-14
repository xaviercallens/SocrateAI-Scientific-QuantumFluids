# Pre-registered validation battery for the W4 observable

**Status: PRE-REGISTRATION. Written 2026-08-14, BEFORE the next comparison is run.**
Owner ruling 2026-08-14, following three consecutive observable failures: an observable
must clear this battery *before* any β comparison is run on it. Fixed here so it cannot
be adjusted after seeing results.

**Companion ruling (same date):** where the two enstrophy conventions (audit ruling O1)
disagree, **report both plainly with the disagreement stated, and no single headline** —
disagreement is neither hidden nor treated as automatically invalidating.

---

## Why this exists

Three observables were adopted and then withdrawn, each having looked clean until it was
measured against the *one specific axis* that broke it:

| observable | adopted because | withdrawn because |
|---|---|---|
| `sup_t Ω` | OP2_LITE §3's protocol | **diverges in the horizon** for a dispersive regulator (O7) |
| `Ω at first peak` | horizon-independent (0.00% at T=32→64) | **discontinuous in the swept parameter** — new local maxima appear as D falls (1,2,2,3), so it stops tracking the same feature |
| `max_{t≤T*} Ω` | horizon-independent *and* continuous | **β drifts 40% with T*** for the dispersive regulator (−1.062 → −1.496 as T* goes 1.5 → 4.0) |

The recurring error was not bad luck in choosing. It was declaring an observable sound on
the strength of the checks that happened to be convenient, and discovering the missing
check only after a result had been produced. **The battery converts that into a
pre-condition.**

---

## The battery

An observable qualifies **only if it passes every check below, for BOTH regulators
separately (viscous and dispersive) and BOTH enstrophy conventions.** A single failure
disqualifies it. Results are recorded whether they pass or fail.

### B1 — Horizon independence
Vary the run horizon `T` over at least a 4× range at fixed everything else. The
observable must change by **< 1%**.
*Rationale: this is O7. The observable must be a property of the model, not of how long
we watched.*

### B2 — Parameter monotonicity
Across the swept parameter, the observable must be **monotonic**.
*Rationale: this is the `first_peak` defect. Non-monotonicity signals that the observable
is not tracking a single physical feature across the sweep, so its log-log slope is not a
scaling exponent.*

### B3 — Stability in the observable's own free parameters
Any free parameter the observable introduces (a window `T*`, a threshold, a detection
tolerance) must be varied over at least a 2× range, and **β must change by < 5%**.
*Rationale: this is the windowed-sup defect. An observable whose answer depends on its own
tuning parameter reports that parameter, not the physics.*

### B4 — Discretisation convergence
Both discretisation parameters must be checked **independently**: the timestep (`dt` vs
`dt/2`) and, where the observable reads a trajectory, the trace sampling — in both
subsampling phases. Change must be **< 1%** for each.
*Rationale: passing one says nothing about the other. `sup_t Ω` passed dt-refinement at
0.00% on all twelve points of a run that was nonetheless entirely a horizon artifact.*

### B5 — Grid (N) independence, on the observable actually being used
Vary `N` and require the observable to have converged, **< 1%** between the two largest
`N`. Must be evaluated on the candidate observable, not a legacy one.
*Rationale: an earlier N-independence check silently used the retracted `sup_t Ω` and so
measured the O7 artifact rather than grid resolution.*

### B6 — Non-degeneracy
The observable must not collapse onto a parameter-independent constant anywhere in the
swept range — in particular it must not reduce to `Ω(0)`.
*Rationale: the `MIN_RISE` finding. A degenerate region contributes points that are
constant in the swept parameter, dragging the fitted slope toward zero and thereby
**manufacturing the pre-registered `β = 0` "mechanism is irrelevant" outcome.** This is
the only failure mode so far that biases toward a specific pre-registered conclusion.*

### B7 — Convention agreement is REPORTED, not required
Compute everything under both enstrophy conventions. Where they disagree, report both
with the disagreement stated explicitly and **no single headline number**
(owner ruling 2026-08-14). Disagreement does not disqualify an observable, but an
undisclosed disagreement invalidates a report.

---

## Retrospective application to the four candidates tested so far

Recorded now, at pre-registration time, so the battery is visibly calibrated against
known outcomes rather than tuned to admit a favoured candidate.

| | B1 horizon | B2 monotonic | B3 own-params | B4 discretisation | B5 grid | B6 non-degenerate |
|---|---|---|---|---|---|---|
| `sup_t Ω` | ❌ 10.35% | ✅ | n/a | ✅ | not tested | ✅ |
| `Ω at first peak` | ✅ 0.00% | ❌ non-monotonic | ✅ | ✅ | not tested | ❌ needs MIN_RISE guard |
| `max_{t≤T*} Ω` | ✅ by construction | ⚠ fails at T*=1.5 | ❌ 40% drift | ✅ | not tested | ✅ |
| time-averaged Ω | ❌ 49.99% | not reached | — | — | — | — |
| `max_t dΩ/dt` | ❌ 19.31% | not reached | — | — | — | — |

**No candidate currently passes.** Every failure is on the *dispersive* side; the viscous
regulator passes every check for every candidate tried.

---

## The pattern this exposes, which the owner should see before a fourth candidate

All five failures share one root: **a purely dispersive regulator has no attractor.**
Dissipation removes energy, so the viscous system settles and any "how large does Ω get"
question has a converged answer. Dispersion is energy-neutral by construction (memo §3),
so the conservative system keeps exploring and Ω keeps finding larger values — measured
to 66% of the `k_N²E` ceiling at `T = 64` and still climbing.

Consequently **any observable of the form "how big does Ω become" inherits a
horizon dependence on the dispersive side**, and the ways out are limited to:

- picking a *specific dynamical feature* (first peak) — which is horizon-stable but need
  not persist across the parameter sweep, exactly the observed failure; or
- picking a *fixed window or time* — which is well-defined but reports the window.

That is not a list of bad luck; it is a structural consequence of comparing a system with
an attractor against one without. **It is legitimate grounds to revisit whether
peak-enstrophy is the right framing at all**, which was option (c) in the 2026-08-14
decision and was not selected. This document does not re-decide that — it records that the
evidence bearing on it has since strengthened from three failures to five, with a
common and now-identified mechanism.

---

## Round 2 (2026-08-14): timescale observables — also fail, and reveal a new failure class

The five candidates above were all **amplitude** observables ("how large does Ω become"),
and all failed on the *dispersive* side. The obvious response was to try **timescales**
("when does something happen"), which are bounded for both regulators regardless of whether
the amplitude converges. Two were run through the battery (`exploration/run_battery.py`):

| candidate | viscous | dispersive |
|---|---|---|
| `t_peak` — time of first local maximum | **PASS** both conventions | **FAIL** B2 non-monotonic; r² = 0.24 / 0.10 |
| `t_cross(θ)` — first `t` with `Ω ≥ θ·Ω(0)` | **UNDEFINED** — Ω never reaches 4·Ω(0) under strong damping | PASS [sum]; FAIL [max]; **B3 drift 161%** |

Two things here are new and more informative than another failure.

**(i) `t_peak` has no power law to fit on the dispersive side at all.** r² of 0.24 and 0.10
— not a marginal fit, no relationship. So it is not merely non-monotonic; there is no
exponent there to measure.

**(ii) `t_cross` REVERSES the asymmetry.** Every previous failure was on the dispersive
side, which invited the reading "the dispersive case is awkward, keep looking." But
`t_cross` is perfectly well-behaved for the dispersive regulator and **undefined for the
viscous one** — under strong damping the cascade never quadruples the initial enstrophy, so
there is no crossing time to measure.

That reframes the problem. It is not that one side is difficult. It is that
**the two regulators do not share a common domain on which a single observable is
well-posed**:

- amplitude observables are well-defined and convergent for the *viscous* regulator, and
  horizon-divergent for the *dispersive* one;
- threshold-crossing observables are well-defined for the *dispersive* regulator, and
  undefined for the *viscous* one.

The underlying dynamics differ in kind, not degree: the dissipative system has an attractor
and decays; the conservative system has none and explores upward toward the truncation
ceiling. An observable that is bounded, monotonic, parameter-stable and *defined* for both
may not exist.

**Seven candidates, three distinct failure classes** (horizon divergence, parameter
discontinuity, domain non-overlap). This is recorded as strengthened evidence for
revisiting the framing — option (c) of the 2026-08-14 decision — not as a claim that no
observable exists.

---

## What passing looks like

An observable clearing B1–B6 on both regulators, with B7 reported. Until one does, no β
comparison is run and no claim is filed.

---

## Amendments (pre-registered 2026-08-14, BEFORE round 3 is run)

Two metric defects in the battery itself, found by the Fable review, fixed before any
further use:

**B3′ — absolute floor for near-zero slopes.** B3's relative-drift metric explodes when
the underlying slopes are near zero: round 2 reported "161% drift" for `t_cross` from
comparing β = 0.005 against β = 0.047 — both tiny. Amended criterion: when any variant's
|β| < 0.1, B3 uses the **absolute** difference, requiring max|Δβ| ≤ 0.05; otherwise the
relative criterion stands.

**B5′ — ratio form for intrinsically N-dependent observables.** B5 as written ("< 1%
between the two largest N") presumes the observable approximates an N-independent limit.
A thermalization time to a *ceiling-relative* threshold intrinsically depends on N (the
ceiling itself is `k_N²E`). Amended: for such observables B5 applies to the **normalized
ratio** `O(param)/O(baseline)` at each N — the regulator-induced *delay factor* — and
requires the β fitted to that ratio to be stable across consecutive N (|Δβ| ≤ 0.05).

**Fit reporting (from review F5).** All sweeps are deterministic; t-distribution CIs are
not sampling uncertainty but lack-of-fit gauges, and are relabeled as such. Every fit
additionally reports **windowed-slope stability**: β over the first half and second half
of the sweep range separately. A "distinguishable" conclusion requires the windows to
agree within the sweep and the arms to differ by more than the window spread.

---

## Round 3 pre-registration (2026-08-14): thermalization time, all-conservative family

**Motivation** (M2_REPORT §6a/§6b): all three of E1 §4's regulators are conservative; the
regulator's signature is in the pre-thermalization transient; timescales are well-defined
for every conservative arm (each trajectory climbs toward the ceiling).

- **Observable:** `τ_f` = first time `Ω_sum(t)` reaches `f · k_N²E` (linear interpolation
  between bracketing samples), for **f ∈ {1/8, 1/4, 1/2}** — f is the B3′-checked free
  parameter.
- **Arms:** pure truncation (baseline, D = 0) and dispersive (sweep D over
  {0.2, 0.15, 0.1, 0.07, 0.05, 0.035, 0.025, 0.018}) at ν = 0. The bounce arm waits for
  the W2 design memo's audit (exploratory Tier C preview only).
- **Initial data — common to all arms, pre-registered:** P3 with per-shell phases
  `e^{i·0.7n}` (same |aₙ|, same E). Rationale: the real subspace is a measure-zero,
  *non-Liouville* skeleton inside the volume-preserving complex flow; generic complex
  data is the regime where the statistical description (and the equipartition ceiling)
  applies, and using identical data for every arm removes initial-condition confounds.
- **Grids:** N ∈ {4, 5} primary; N = 6 at three D values for the B5′ ratio check.
- **Horizons:** ladder up to T = 64; a configuration whose crossing does not occur is
  EXCLUDED WITH ITS REASON, never assigned the endpoint.
- **Discretisation (B4):** dt vs dt/2 within 1%; two-phase 2× trace-subsample agreement
  of τ within 1%.
- **Conventions (B7):** τ computed from Ω_sum is primary-reported; Ω_max version recorded
  and reported alongside; disagreement stated plainly with no single headline.
- **Interpretation, fixed in advance:** β from `τ_f ∝ D^β`. β ≈ 0 with the delay ratio
  ≈ 1 across the sweep ⇒ dispersion does not delay thermalization at these scales (a real
  negative). β > 0 stable across f, N, windows ⇒ dispersion delays thermalization with a
  measurable exponent — the first well-posed quantitative signature distinguishing the
  dispersive cutoff from bare truncation.
