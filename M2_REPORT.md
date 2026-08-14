# M2 Report — the W4 dispersive shell regulator

**Status:** complete, with a negative result as the substantive finding.
**Date:** 2026-08-14
**Owner ruling:** report the obstruction as the M2 finding (2026-08-14).

---

## 1. The finding

> **An energy-conserving regulator admits no well-posed peak-enstrophy observable, and
> all three of E1 §4's regulators are energy-conserving.** No dissipation ⇒ no attractor ⇒
> `sup_t Ω` (and every variant tried) fails to converge in the horizon, saturating instead
> at the truncation ceiling `k_N²E` — a property of the cutoff, not of the dynamics. The
> comparison W4 was designed to make therefore cannot be carried out in that form.

*(The statement above is the ADDENDUM's sharpened form. §§2–3 were written first, framing
this as a mismatch between a dissipative and a conserving regulator; §6a shows the
dissipative arm was a stand-in of mine, not one of E1 §4's three, so the obstruction is
experiment-wide rather than a mismatch. §§2–3 are left as written — the evidence there
stands and the narrowing is corrected, not concealed.)*

This is a negative result, and under the audited memo's own §6 framing it is a successful
outcome rather than a failure: *"three equal exponents ⇒ the cutoff mechanism is irrelevant
at this observable (a real and useful negative)."* The finding here is stronger than that
pre-registered negative — it is not that the mechanism leaves no trace in the exponent, but
that the exponent is not jointly definable.

**What it is not.** It is not a claim that no such observable exists. Seven were tried and
none worked; the reason they fail is now identified rather than incidental, which is what
makes the negative informative instead of merely inconclusive.

---

## 2. The mechanism

Dissipation removes energy, so the viscous system has an **attractor**: the cascade builds,
peaks, and decays, and "how large does Ω get" has a converged answer.

Dispersion is **energy-neutral by construction** — that is precisely what makes it
dispersive rather than dissipative (memo §3: the two regulators are the same `k²` term with
the coefficient rotated 90° in the complex plane). So the conservative system has **no
attractor**: it keeps exploring, and Ω keeps finding larger values, bounded only by the
truncation ceiling `k_N²E`. Measured: 66% of that ceiling at `T = 64`, still climbing.

The consequence is a **domain mismatch**, not a difficulty:

| observable family | viscous | dispersive |
|---|---|---|
| **amplitude** — "how large does Ω become" | well-defined, converged | horizon-divergent |
| **threshold** — "when does Ω reach θ·Ω(0)" | **undefined** (never reaches θ under damping) | well-defined |

Each family is well-posed on exactly the side where the other is not.

---

## 3. Evidence: seven candidates, three failure classes

All evaluated against the pre-registered battery
(`docs/designs/M2_OBSERVABLE_VALIDATION_BATTERY.md`).

| candidate | family | outcome |
|---|---|---|
| `sup_t Ω` (the memo's original) | amplitude | **horizon divergence** — 10.35% drift T=32→64, dispersive |
| time-averaged Ω | amplitude | **horizon divergence** — 49.99%, viscous (decays ~1/T) |
| `max_t dΩ/dt` | amplitude | **horizon divergence** — 19.31%, dispersive |
| Ω at first peak | amplitude | **parameter discontinuity** — new local maxima appear as D falls (1,2,2,3), so it stops tracking one feature |
| `max_{t≤T*} Ω` | amplitude | **own-parameter drift** — β −1.062 → −1.496 as T* 1.5 → 4.0 |
| `t_peak` | timescale | **no power law** on dispersive — r² = 0.24 / 0.10; passes the whole battery on viscous |
| `t_cross(θ)` | timescale | **undefined for viscous**; B3 drift 161% |

Failure classes: **horizon divergence**, **parameter discontinuity**, **domain non-overlap**.

The last is the one that settles it. Every failure before `t_cross` was on the dispersive
side, which invited "the dispersive case is awkward, keep looking." `t_cross` reverses the
asymmetry — well-behaved for dispersive, undefined for viscous — showing the problem is
not that one side is hard but that the two sides do not overlap.

---

## 4. What M2 built, and what stands independently of the above

The negative result concerns the *measurement*, not the *model*. The model and its
infrastructure are validated and stand on their own:

- **A structural obstruction identified and resolved** (memo §1–2). A real-amplitude shell
  model *cannot* host a dispersive regulator: any real linear term either damps or forces,
  never stays energy-neutral. Dispersion is phase rotation and a real amplitude has no
  phase. The resolution is a conjugated complexification,
  `B_n = k_{n−1}a_{n−1}² − k_n conj(a_n) a_{n+1}`, which conserves `½Σ|a_n|²` exactly while
  reducing **exactly** to the real Katz–Pavlović model on real data.
- **CLAIM-004 — Positive Control #1 passed at `0.00e+00`.** At `D = 0` the complexified
  model reproduces MechanicaFluidorum's independently-written implementation *bit-for-bit*
  across ~2.4×10⁶ RK4 steps, all nine configurations, both `sup_Ω` and `E_final`. The
  exactness was explained rather than assumed: `k_n = 2ⁿ` are exact powers of two, so
  differently-associated products stay bit-identical.
- **Tier B harnesses**, 126 tests, including mutation testing of the production module
  (three injected bugs, all caught) and negative controls establishing that each guard
  actually fires.
- **CLAIM-007 (Tier A) — the complexification's Lean formalisation**, closing audit
  ruling O2: exact energy conservation and the invariant-subspace property, kernel-checked.

---

## 5. Corrections made during M2

Recorded because the process matters as much as the result:

- **ERRATUM E1.** The memo's O5 falsification trap demanded the truncated inviscid model
  blow up. It cannot: energy conservation gives `|aₙ| ≤ √(2E)`, so a *truncated* model is
  globally bounded — Katz–Pavlović is a theorem about the *infinite* system. As written the
  trap could never fire and would have condemned a correct implementation.
- **LL-10.** `REFERENCE_VALUES` carried Landau parameters recalled from memory and
  misattributed to two papers that do not report them. Corrected against six properly
  attributed determinations; CLAIM-003's conclusion survived and is now better supported.
- **LL-11 / CLAIM-R1, R2.** Two β results were produced and retracted before promotion —
  the first a horizon artifact, the second non-monotonic with the two enstrophy conventions
  disagreeing. Both are archived with invalidation notices.
- **MIN_RISE.** Over-damped runs returned `Ω(0)` as a "peak". Since `Ω(0)` is *constant in
  the swept parameter*, admitting those points drags the fitted slope toward zero —
  manufacturing the pre-registered `β = 0` conclusion. The only failure mode encountered
  that biases toward a specific pre-registered answer.

---

## 6. Open items carried forward

- **O2 (Lean).** ✅ **CLOSED.** `lean_src/QuantumFluidsShell.lean` —
  `shellBc_energy_conservation` and `shellBc_real`, kernel-checked with axiom footprint
  `[propext, Classical.choice, Quot.sound]` against the same pinned Mathlib revision
  MechanicaFluidorum uses (CLAIM-007). Scope: the algebraic identity only.
- **O6.** The three regulators do not share a common `α′` axis (dimensional; `η² ~ ν^{3/2}`
  needs `ε`, `ξ² = D²/c²` needs `c`). Moot for the primary comparison, which is now not
  being made in that form.
- **W2 (bounce regulator).** Still undesigned as a regulator, but the *conservation*
  question is now **resolved** — see §6a. A seam conserves iff
  `Re(conj(v_N)²·v_{N+1}) = 0`; on real data only truncation qualifies, while the
  complexified model admits `v_{N+1} = i·μ·v_N²`. Either way W2 is caught by the §6a
  obstruction (conserving) or measures an artifact (non-conserving).
- **M1-DATA-001.** Raw ILL numor access still pending; not blocking.

---

## 6a. ADDENDUM (2026-08-14): the obstruction covers ALL THREE of E1 §4's regulators

Written after §1–6, on a question the Lean formalisation made precise: does the
obstruction apply only to the dispersive arm, or to the experiment as a whole?

**It applies to all three.** The reason is that E1 §4's three regulators are *all
energy-conserving*. None of them dissipates:

| E1 §4 regulator | conserves energy? | why |
|---|---|---|
| truncation (the control) | **yes, exactly** | `v_{N+1} = 0` makes the telescoping outflux vanish |
| bounce (W2) | **only for special seams** — see below | |
| dispersive (W4) | **yes, exactly** | `−iDk²a` is energy-neutral by construction |

The `sup_t Ω` obstruction follows from energy conservation, not from dispersion
specifically: no dissipation ⇒ no attractor ⇒ the enstrophy keeps exploring up to the
`k_N²E` ceiling. **Measured for the truncation control** (`ν = D = 0`, profile P3):

| T | N=4 | N=5 | N=6 |
|---|---|---|---|
| 2 | 104.10 | 384.67 | 1439.96 |
| 8 | 149.60 | 600.34 | 2409.23 |
| 32 | **157.76** | **634.78** | **2540.02** |

Still climbing at `T = 32`, at 99.2% of the ceiling.

**Worse: the truncation control's β converges to the trivial bound.** Since
`sup_t Ω → k_N²E = 4^N E` and `α′ = 4^{−N}`, the exponent tends to **−1 exactly**, which
is just the energy-conservation bound restated. Measured:

| T | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|
| β vs α′ | −0.948 | −0.990 | −1.002 | −1.003 | −1.002 |

So even at a fixed horizon the control is measuring `sup Ω ≤ k_N²E`, carrying **no
dynamical information**.

**Why this was not visible earlier.** The comparisons in §3 used a *viscous* regulator as
one arm, and it behaved perfectly — passing every battery check. But **viscosity is not one
of E1 §4's three regulators.** It was introduced as a dimensionally-matched stand-in for
comparison against `D`. It is the only *dissipative* thing in the study, which is exactly
why it was the only well-behaved arm. The apparent pattern "one side works, one doesn't"
was an artifact of that substitution.

### The W2 bounce regulator, resolved

Memo §5 left open whether any reflective seam preserves `Σ|aₙ|²`. The Lean telescoping
theorem answers it exactly: the energy pairing is `−k_N·Re(conj(v_N)²·v_{N+1})`, so **a
seam conserves energy iff `Re(conj(v_N)²·v_{N+1}) = 0`** — i.e. iff `v_{N+1}` is orthogonal
to `v_N²` under the real inner product `Re(conj(x)y)`. Two consequences:

- **On real data, truncation is the only conserving boundary condition.** The expression
  reduces to `v_N²·v_{N+1}`, zero only when the reflected value is. A naive real reflective
  seam (`v_{N+1} = v_{N−1}`) **leaks energy**, so a W2 built that way would measure broken
  conservation rather than the bounce — precisely the failure OP2_LITE flags for its
  Candidate A.
- **In the complexified model a conserving seam does exist**: `v_{N+1} = i·μ·v_N²` gives
  `conj(v_N)²·(iμv_N²) = iμ|v_N|⁴`, purely imaginary, so the pairing is exactly zero. This
  has **no real analogue** — an unanticipated second dividend of the complexification, which
  was adopted for the dispersive regulator alone.

Both are pinned by tests (`tests/test_shell_dynamics.py`, seam section). But note the sting:
a *conserving* W2 seam inherits the very obstruction described above, while a
*non-conserving* one measures an artifact. W2 is caught either way.

---

## 6b. SECOND ADDENDUM (2026-08-14, top-tier review): the finding has a name, a mechanism theorem, and a validated statistical prediction

Three results from the review pass, each verified before being written down.

### (i) The phenomenon is (candidate-)known: thermalization to absolute equilibrium

"Spectrally truncated conservative system relaxes toward an equipartition-like state,
and sup-type observables measure the truncated equilibrium rather than the cascade" is,
to the best of available recollection, the *absolute equilibrium / thermalization*
phenomenon studied for truncated Euler and truncated GPE. Candidate anchors — **all
[RETRIEVAL IN PROGRESS], none citable until verified (LL-10)**: T.D. Lee (~1952,
equipartition ensembles for truncated ideal hydrodynamics); Kraichnan (~1973, absolute
equilibrium); Cichowlas et al. (~PRL 2005, truncated Euler thermalizes, transient acts
dissipative); Connaughton et al. (~PRL 2005, condensation of classical nonlinear waves);
Davis–Morgan–Burnett (~PRL 2001, classical-field GPE thermalization); Krstulovic–Brachet
(~PRL 2011, truncated GPE). A dedicated search for *shell-model-specific* absolute
equilibrium work is part of the retrieval task — if it exists, §1's finding is a
re-expression of it and will be recorded as such (Rule E-X).

Under this reading, the M2 negative sharpens into a positive research direction: **the
cascade physics lives in the pre-thermalization transient**, and the natural observable
is a *thermalization time*, not a peak amplitude.

### (ii) New result: the complexification restores the Liouville property

The realified flow of the **conjugated complexified** model has phase-space divergence
**exactly zero** — verified numerically (max |div| = 4×10⁻⁹ over random states, both with
and without the dispersive term) and provable shell-by-shell: `dv_n/dt` depends on `v_n`
only through `−k_n conj(v_n) v_{n+1}` (an ℝ-linear map with zero trace, for every
`v_{n+1}`) and the dispersive rotation `−iDk_n² v_n` (trace `2·Re(−iDk²) = 0`). The
**real** Katz–Pavlović model, by contrast, has divergence `−Σ k_n a_{n+1} ≠ 0` (verified
numerically to 4 decimals against the analytic formula).

Consequences: volume preservation on the compact energy sphere ⇒ Poincaré recurrence and
a legitimate statistical-mechanics description — the "no attractor" observation upgraded
from empirical remark to mechanism. This is the **third** unanticipated dividend of the
conjugation (after the invariant real subspace and the conserving seam), and a genuine
qualitative property of the deformation that memo §2c should carry: the real model's flow
*contracts* phase-space volume along cascade states; the complexified one cannot. The
shell-local trace identities are formalised in Lean (see `lean_src/QuantumFluidsShell.lean`,
Liouville section); the assembly into the full field's divergence is the numerically
verified, hand-derived part.

### (iii) A quantitative equilibrium prediction, checked

Liouville + energy as (sole known) invariant ⇒ microcanonical equipartition on the
energy sphere: `⟨|v_n|²⟩ = 2E/(N+1)`, hence

```
⟨Ω_sum⟩_eq = E·(4^{N+1} − 1) / (3(N+1))     = 42.625  at N = 4, E = 0.625
```

Measured second-half time averages (complex-phase initial data, single trajectories):

| regulator | Q1 mean | Q4 mean | 2nd-half mean | % of prediction |
|---|---|---|---|---|
| truncation (ν = D = 0) | 32.3 | 35.8 | 37.8 | 88.6% |
| dispersive D = 0.02 | 65.5 | 42.6 | 46.2 | 108.3% |
| dispersive D = 0.1 | 17.6 | 30.8 | 31.1 | 73.0% — quarters still climbing |

Five-shell, single-trajectory caveats apply (±20–30% expected; unknown additional
invariants would shift the prediction and are an open question). The decisive pattern:
**first-quarter means differ by 4× across regulators while late-time means converge
toward one predicted value.** The regulator's signature is in the transient — measured,
not argued. This also retroactively explains the `mean` candidate's battery failure: it
was *relaxing toward equilibrium*, not misbehaving.

---

## 7. Recommended next step

If the W4 question is to be pursued further, the honest reformulation is **not** another
observable. It is to give the conservative regulators an attractor — a small pre-registered
`ν` floor — so that `sup_t Ω` converges, then sweep each regulator's own parameter at fixed
`ν`.

Per §6a this floor is needed for **all three** regulators, not just the dispersive one: the
truncation control is equally conservative and its β otherwise degenerates to the trivial
energy bound `−1`. That is a larger change to E1 §4's design than it first appears, and it
means the comparison becomes "dispersion-on-top-of-dissipation vs truncation-on-top-of-
dissipation" — well-posed, but a different question from the one E1 §4 asked. The floor also
becomes a free parameter requiring its own B3 stability check.

That is a design decision for the owner, not a continuation of M2.
