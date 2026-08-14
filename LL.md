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

## Stream-specific entries (to be added during execution)

*None yet.*

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
