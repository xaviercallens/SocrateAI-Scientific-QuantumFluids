# M2 Report — the W4 dispersive shell regulator

**Status:** complete, with a negative result as the substantive finding.
**Date:** 2026-08-14
**Owner ruling:** report the obstruction as the M2 finding (2026-08-14).

---

## 1. The finding

> **A dissipative and an energy-conserving regulator do not admit a common well-posed
> peak-enstrophy observable.** The comparison W4 was designed to make — β measured for a
> dispersive regulator against β for a dissipative one — cannot be carried out in that form,
> because no observable tested is simultaneously bounded, monotonic, parameter-stable, and
> *defined* for both.

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
- **The complexification's Lean formalisation** — closing audit ruling O2 — in progress
  (§6).

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

- **O2 (Lean).** The conjugated complexification's energy-conservation identity is being
  formalised, mirroring MechanicaFluidorum's real-model `shellB_energy_conservation`. Until
  it lands, W4 carries no Tier A backing.
- **O6.** The three regulators do not share a common `α′` axis (dimensional; `η² ~ ν^{3/2}`
  needs `ε`, `ξ² = D²/c²` needs `c`). Moot for the primary comparison, which is now not
  being made in that form.
- **W2 (bounce regulator).** Never designed. Whether any reflective seam preserves
  `Σ|aₙ|²` is unresolved — the dyadic energy cancellation is a telescoping identity that
  depends on the `a_{N+1} = 0` boundary convention.
- **M1-DATA-001.** Raw ILL numor access still pending; not blocking.

---

## 7. Recommended next step

If the W4 question is to be pursued further, the honest reformulation is **not** another
observable. It is to make the two systems comparable in kind — e.g. by giving the dispersive
regulator a small pre-registered `ν` floor so it acquires an attractor, and then sweeping
`D` at fixed `ν`. That measures dispersion-on-top-of-dissipation rather than dispersion
alone, and the floor becomes a free parameter needing its own B3 stability check — but it is
well-posed, which the current formulation is not.

That is a design decision for the owner, not a continuation of M2.
