# LESSONS LEARNED: SocrateAI-Scientific-QuantumFluids

**Purpose:** Record insights from execution, both successes and failures, to guide future work and sister streams.

**Status:** Seeded from MechanicaFluidorum Stage-1. New entries added during M0–M4 execution.

---

## Inherited from MechanicaFluidorum / Stage 1

### LL-1: Citation verification is not optional

**Lesson:** Do not assume a paper's data-availability statement contains the DOI needed. Some older papers (pre-2018) reference data repositories that no longer exist or changed structure. Always check the journal's supplementary-materials page, publisher's data archive, and the author's institutional repository in parallel.

**Impact:** Adds ~10–15% time to M0 literature retrieval for pre-2015 papers.

**Recommendation:** Start with journals that enforce FAIR data policies (Phys. Rev. journals post-2020); flag pre-2010 papers for manual verification.

---

### LL-2: Unit tests for adapters must include negative controls

**Lesson:** A numor/netCDF parser that passes on the happy path (valid file → correct shape) will silently corrupt data if given a file with swapped axes or mismatched metadata (e.g., Q and ω reversed). Unit tests must include deliberately malformed inputs and assert that they are *rejected* (not silently reinterpreted).

**Impact:** Tier-B harnesses depend on this; a silent corruption in adapters cascades into wrong fit results.

**Recommendation:** Checklist for any adapter in src/quantumfluids/adapters/:
- [ ] Happy path (valid input → correct shape, correct values)
- [ ] Negative control: axis swap (should error or flag)
- [ ] Negative control: missing metadata (should error)
- [ ] Negative control: NaN/inf in data (should error or document handling)

---

### LL-3: Dyadic-lab instrument integration requires version pinning

**Lesson:** Importing a live instrument from a sister stream (MechanicaFluidorum) without pinning its version creates a hidden dependency that breaks if the upstream stream refactors. The W4 reproduction becomes unverifiable because the instrument's behavior changed.

**Impact:** M2–M3 coupling is fragile if not properly version-locked.

**Recommendation:** At M2, commit to a specific dyadic-lab git tag (e.g., `mf/instrument-v1.2.3`). Document the import in lean_src/: which file, which version, when last updated. Any upstream update requires deliberate re-audit of W4.

**Superseded in part by LL-9 (2026-08-14):** this lesson assumed the
thing to be version-pinned already existed. It didn't. Version-pinning
discipline is still correct advice for *whenever* a real instrument
exists to import — but check that first.

---

### LL-4: Dark-matter claims attract low-quality engagement

**Lesson:** Publishing speculation about dark matter (even in a clearly-marked narrative section) invites emails from non-experts and crackpots. This is not a research problem, but a time-management one.

**Recommendation:** Keep dark-matter speculation in docs/narrative/ under a clear "NOT peer-reviewed, for exploration only" banner. Offer no email contact for narrative sections; direct inquiries to the main SocrateAI issue tracker or a dedicated moderation queue.

---

### LL-5: Outreach timing matters

**Lesson:** Reaching out to senior researchers with a "proposal" or "preliminary results" is less effective than reaching out with "we've reproduced your Fig. 5 with independent data" or "we have a question about your instrument metadata." Concrete artifacts dramatically increase response rate and quality of reply.

**Impact:** M4 outreach should only proceed after M1 (dispersion-fit reproduction, with plots). Messaging matters.

**Recommendation:** See PLAN.md M4 prerequisite.

---

### LL-6: [Pending] Literature retrieval playbook (M0 blocking)

**Lesson:** (To be filled after M0 completion.) Strategy for successfully retrieving papers before 2015, especially experimental reports from non-US institutes.

**Status:** PENDING. Blocking M0 DoD.

---

## Stream-specific entries

### LL-7: Synthetic round-trip tests can hide unit errors that real data exposes

**Lesson:** `fit_dispersion.py`'s `REFERENCE_VALUES` table entered the
literature roton gap in Kelvin (8.65, 8.63, 8.64 — the conventional way
the literature quotes it) but labeled and used the field as `delta_meV`
directly, overstating Δ by the Boltzmann-constant factor (~11.6×). A
second, independent bug in `landau_model.py` had the ℏ²/(2m_He4)
conversion constant off by exactly 2× (a dropped factor of 2 in the
denominator). Neither was caught by the Tier-B test suite, because the
synthetic test data was generated using the *same* wrong constants it
was then checked against — the tests validated internal
self-consistency, not physical correctness.

Both bugs surfaced only when the pipeline was run against real
(digitized) published data and the fitted roton gap disagreed with the
literature table by a suspicious, precisely-factor-of-~11.6 amount.

**Impact:** Any pipeline with a literature-comparison step is only as
honest as the literature constants it was tested against. A synthetic
test that generates its own ground truth cannot catch an error shared
between the generator and the checker.

**Recommendation:** When writing a synthetic round-trip test for a
physical-quantity fit, hardcode the "true" parameters as literature
values computed independently of the module's own conversion constants
(e.g. compute meV from K by hand in the test, don't import the module's
conversion function to do it) — see `tests/test_dispersion_fit.py`
TRUE_C/TRUE_DELTA for the corrected version. Better still: as done here,
run the pipeline against *some* real external dataset (even a rough
digitized one) before trusting a literature-agreement claim, precisely
because it can catch unit/constant bugs synthetic tests structurally
cannot.

---

### LL-8: A rough digitized dataset can validate part of a pipeline and correctly fail on another part

**Lesson:** Running M1's dispersion fit against a hand-digitized version
of Fig. 5 (Godfrin & Krotscheck 2022) recovered the roton gap Δ and
momentum Q_m within 2% of literature, but failed to recover the phonon
sound velocity c by ~27%, stably across several region-width choices
(see M1_REPORT.md). This was not a pipeline bug (confirmed by scanning
`phonon_q_max` and finding a stable, not narrowing, discrepancy) — it is
a real limitation of visual digitization for a parameter (the Q→0
tangent slope) that is disproportionately sensitive to reading precision
at small values, versus a parameter (a curve minimum) that is robust to
the same reading precision.

**Impact:** A single Tier-C dataset does not uniformly validate or
invalidate a fitting pipeline — different fitted parameters can have
very different sensitivity to the same data-quality limitation.

**Recommendation:** Report per-parameter validation status, not a single
pass/fail for the whole pipeline. Do not adjust digitized data points to
force agreement with literature after the fact — a fit failure with a
documented, checked root cause (as here) is more valuable evidence than
a forced match. Re-test the same fitting code against Tier-B (raw
instrument) data once available, rather than assuming the Tier-C result
generalizes.

---

### LL-10: Citation discipline has to reach into source code, not just documents

**Lesson:** This stream has rigorous machinery for verifying citations in
*documents* — LITERATURE_LEDGER.md, the `[LL-6 pending]` tag, the M0
retrieval gate. None of it reached a Python dict. `fit_dispersion.py`'s
`REFERENCE_VALUES` carried Landau parameters recalled from memory and
attributed them to `"cowley_woods_1971"` and `"glyde_1998"`. Retrieval
later established that **neither paper reports those values**: Cowley &
Woods (1971) is a broad inelastic-scattering study that Godfrin et al.
(2021) explicitly exclude from their Table IV of roton parameters, and
Glyde et al. (1998) measures `2.0 ≤ Q ≤ 4.0 Å⁻¹` — entirely beyond the
roton, with no phonon region, so it *cannot* report a sound velocity and
reports no numerical Δ or Q_m at all. The numbers attributed to
Cowley–Woods appear to belong to Henshaw & Woods (1961) instead.

The values were plausible — within ~0.3% of the true ones — which is
precisely why this survived. A wildly wrong number would have failed the
M1 fit comparison immediately.

**Impact:** CLAIM-003's headline agreement figures were computed against
partly-invented reference values. The *conclusion* survived recomputation
against six correctly-attributed determinations (c within 0.198%, Δ within
0.03–0.33%, all inside tolerance) — but that was luck, not process.

**Recommendation:** any numeric constant in source code that represents a
published measurement needs the same provenance as a document citation:
the source, the table or page it came from, its uncertainty, and its
conditions — in a comment beside the value. Where a constant is a
*derived* or *quoted* value rather than the source's own measurement, say
so (Godfrin et al.'s `c` is an ultrasonic result quoted from Abraham
et al.; their P=0 `Δ_R` is itself taken from Stirling as a calibration
input, so agreeing with it is partly circular). Prefer values a source
tabulates over values recalled as "literature-typical". Cross-check at
least one against primary data you hold: the roton minimum of Godfrin's
own published dispersion table sits at 0.7413 meV / 1.9200 Å⁻¹, which
confirmed the corrected values and refuted the coded ones.

---

### LL-11: Check that an observable converges before fitting an exponent to it

**Lesson:** The W4 experiment fits `β` from `sup_t Ω`. The first
exploratory run produced a clean, tempting result — `β_ν = −0.91` vs
`β_D = −0.63`, 95% CIs disjoint under both enstrophy conventions, r² > 0.96,
zero excluded points. It was invalid. `sup_t Ω` does not converge in the
horizon `T` for a purely dispersive regulator: at `ν = 0` the dynamics is
energy-conserving, so there is no attractor and the enstrophy keeps finding
new maxima up to the truncation ceiling `k_N²E`. Measured at N=4: the
viscous value is stable from `T = 2` through `T = 64`, while the dispersive
value climbs monotonically across the same range and is still climbing at
the end. `β_ν` was a model property; `β_D` was a property of the horizon
I happened to pick.

Every quality signal looked good. High r², tight CIs, and — the most
seductive one — the dt-refinement inclusion criterion passed at **0.00%**
for all twelve points. That criterion tests convergence in the *timestep*.
Nothing in the pre-registered protocol tested convergence in the *horizon*.

**Impact:** would have produced a headline result that was an artifact of
an arbitrary parameter, passing every check the protocol specified.

**Recommendation:** before fitting an exponent to a `sup over t` quantity,
demonstrate that the quantity has converged in `t` — for **every** regulator
separately, since the convergence mechanism may differ between them (here,
dissipation is what produces convergence, so the regulator being tested is
exactly the one that removes it). Add a horizon-refinement check alongside
the timestep-refinement check; the two are independent, and passing one says
nothing about the other. More generally: an inclusion criterion is only
evidence about the specific limit it takes.

---

### LL-9: A cross-repo "import this" plan needs to check the other repo before it's load-bearing

**Lesson:** EXPRESSION_MEMO_E1.md §4 described a "MechanicaFluidorum
exponent instrument" and a "W2 (reflective seam) regulator, already
proposed in MechanicaFluidorum" as things M2 would import. Neither
existed. MechanicaFluidorum has a real Tier-C shell-model script
(`exploration/dyadic_cascade.py`) and an *un-implemented* design memo
for an exponent-fitting protocol — but no regulator abstraction, no
fitting harness, and nothing named "W2" anywhere. The phrase "already
proposed in MechanicaFluidorum" was QuantumFluids describing its own
aspiration, written in a way that read back as a citation to an
external fact once enough time had passed and enough documents referred
to it.

This was caught only because a scoped Explore-agent search was run
*before* M2 code was written, specifically to locate the file paths and
interface being planned around — not because anyone doubted the claim.

**Impact:** Building M2 on the assumed-existing instrument would have
produced code that imports nothing real, silently reimplementing
whatever it needed while the documentation kept saying "imported" — the
exact double-bookkeeping failure Rule E-X and LL-3 exist to prevent, just
arrived at from the opposite direction (assuming an external artifact
exists, rather than reusing a name for two different local claims).

**Recommendation:** Before any milestone whose plan says "import X from
[sister repo]," actually go look at [sister repo] for X — a cheap,
scoped search, not a full audit — and update the plan with what's
actually there before writing integration code. Do this as a standing
practice at the start of any cross-repo milestone, not only when
something feels suspicious. See MEMO_ROSETTA.md / MATHESIS_INTEGRATION.md
for the (verified, real) Mathesis import pattern this should be checked
against as a positive example — Mathesis's Duality.lean theorems were
independently confirmed to exist and be kernel-checked before QuantumFluids
built on them.

---

## Decision log

| Decision | Date | Rationale | Owner |
|---|---|---|---|
| Keep "QuantumFluids" naming (vs. "MechanicaFluidorum-Quantum") | 2026-08-14 | Distinct domain focus: condensed-matter physics vs. classical hydrodynamics. Per RES-1. | Proposal author |

---

## Cross-stream impact notes

- **MechanicaFluidorum:** This stream does NOT resolve MF obstruction O5 (GPE–NS well-posedness). LL-3 requires version pinning of dyadic-lab imports.
- **Mathesis:** This stream imports Tier-A Duality and Scale.Reff frameworks. No new foundational theorems proposed unless audited.
- **Poly-Algebraic-Calculus:** Naming separation (RES-1) is maintained. No re-use of that name.
