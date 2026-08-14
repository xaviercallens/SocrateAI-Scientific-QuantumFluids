# EXPRESSION MEMO E1: Quantum Fluids as the Realized Instance of Dual-Scale Regularization

**Status:** expression memo (Rule E-X: express before extend — every entry below first restates an ESTABLISHED result in the programme's language, and only then states what is conjectured).

**Citation status:** Every citation in this memo is `[LL-6 pending]`: written from memory, none may be cited in a tiered artifact before retrieval (see LITERATURE_LEDGER.md, §4).

**Quarantine:** No claim about classical Navier–Stokes is made or implied by any Tier A/B row; the bridge statements are Tier C and labeled as such (see §3, §4).

---

## 1. The Claim of This Memo, in One Sentence

> There exists a real fluid in which the programme's four atomic principles are not hypotheses but **measured facts** — the superfluid — and the honest expression of that fact repositions Hypothesis U as the classical sibling of an open problem the quantum-fluids community already owns.

---

## 2. The Dictionary: Established Physics → Programme Language

### E1.1 — Quantum Pressure & Healing Length (P1: Self-Dual Bound)

| Established result | Tier | Programme reading |
|---|---|---|
| **Gross–Pitaevskii (GPE) dynamics.** Madelung transform splits GPE into fluid equations plus a quantum-pressure term active at the healing length ξ = ℏ/√(mα'), where α' is kinematic viscosity and m is particle mass. The healing length is the length scale below which quantum effects dominate. [LL-6: Madelung 1927; Gérard 2006 / Bethuel–Saut for GPE well-posedness classes] | A | The quantum-pressure term is a **regulator confined below a fundamental length** — the ξ-incarnation of the sub-√α′ deformation, with inertial invisibility above ξ (P1 + the Reff_inertial requirement from Mathesis). The bound √α' ≤ max(ξ, α'/ξ) is not a theorem here; it is **Nature's choice**. |

**Physics note:** The healing length is the coherence length of the order parameter. Below ξ, quantum phase information matters; above ξ, the fluid looks classical.

---

### E1.2 — Circulation Quantization & Vortex Cascade (P4: Bounce + P3: Discrete Pins Continuous)

| Established result | Tier | Programme reading |
|---|---|---|
| **Circulation quantization.** Γ = n·ℏ/m (n integer); vortex cores have fixed size ~ξ and cannot collapse. Quantum-turbulence cascade terminates in reconnections of quantized vortices; it does not cascade to ever-smaller vortex cores. [LL-6: Onsager 1949; Feynman 1955; Barenghi–Skrbek–Sreenivasan PNAS 2014 review] | A | **P4 (no-collapse / bounce)** and **P3 (continuous circulation pinned by an integer)** — both running in a laboratory fluid at K = 1.8 K. The cascade has a bottom rung, and it is **topological** (quantization), not merely viscous. Vortex reconnections are the deflection mechanism (bounce) at the scale floor. |

**Experiment:** Direct numerical simulations and neutron-scattering experiments (Godfrin et al. 2021, LIT-002) show the phonon-roton excitation spectrum; the quantum-turbulence studies (Polanco et al. 2025, Institut Néel, LIT-004) image vortex structures.

---

### E1.3 — Cooper Pairing & Flux Quantization (P2: Sym² Lock, Analogy)

| Established result | Tier | Programme reading |
|---|---|---|
| **Cooper pairing.** Two microscopic fermionic modes (e.g., electrons near the Fermi surface) bind into one macroscopic bosonic mode (Cooper pair, charge 2e). Flux quantization Φ = n·h/(2e) is metrology-grade. [LL-6: BCS 1957; Deaver–Fairbank / Doll–Näbauer 1961] | A (physics); C (analogy) | **Structural analogue of Sym² lock (P2):** macroscopic degrees of freedom generated as pair-composites of microscopic ones, with the composite charge 2e read directly off the quantization. The analogy to hydrodynamic modes as Sym² of excitations is **Tier C** (exploratory); the cited BCS physics is **Tier A**. |

**Caveat:** Superconductors (fermionic) and superfluids (bosonic, e.g., ⁴He) are different phases, but both instantiate topological quantization. The analogy is suggestive, not proven.

---

### E1.4 — Semiclassical Limit & Open Problem (Hypothesis U's Sibling)

| Established result | Tier | Programme reading |
|---|---|---|
| **The vanishing-ξ limit.** The semiclassical limit of quantum hydrodynamics toward classical hydrodynamics is a hard open analysis problem: vortex-filament limits, ξ → 0 asymptotics, uniform regularity bounds. [LL-6: quantum-hydrodynamic-limit literature to be assembled; Bethuel–Saut, Spirn, Schweyer recent works] | A (open problem, not solved) | **Hypothesis U's sibling**, restated in fluid language. α' → 0 (this programme: Navier–Stokes limit of T-dual regularization) and ξ → 0 (quantum fluids: classical hydrodynamics limit of GPE) are the **same epistemic object:** a regularized family, globally well-behaved at fixed cutoff, whose uniform control in the vanishing-cutoff limit is the open core. Neither limit is known. |

**Implication:** The programme's obstruction O5 (well-posedness of NS does not follow from GPE) is not a programme failure; it is the quantum-fluids community's **known open problem** restated in the programme's language.

---

## 3. What the Expression Buys (and What It Does Not)

### Buys

**(i) Citable grounding in nature.**  
The sentence "nature already implements a topological cascade cutoff" becomes **citable** — in helium II and BECs, not in water, and that **qualification is what makes it defensible**. No overreach to classical water; the physics is specific to the quantum case.

**(ii) No isolation.**  
The programme stops being isolated. Its open problem (the ξ → 0 limit, or α' → 0 for T-duality) has a **named sibling with an active community** and partial results to import or contrast. The quantum-fluids community has 50+ years of experimental and computational work on this exact limit; that work is now accessible as a comparison point, not a claim.

**(iii) One concrete, falsifiable experiment (W4).**  
An experiment that costs one model variant, not a new theory (see §4).

### Does NOT Buy

**No transfer of regularity from GPE to Navier–Stokes.**  
The quantum regulator (quantum pressure) is **dispersive** (energy-preserving, complex dispersion relation), not dissipative (viscous, real damping). The two limits (ξ → 0, α' → 0) may fail or succeed **independently**. Any claim that GPE regularity implies NS regularity dies at obstruction O5 review (see MechanicaFluidorum §4.1).

**Quarantine maintained.**  
This expression memo does not dissolve the quarantine; it sharpens it. The quantum-fluids instantiation is a **sibling problem**, not a bridge to NS.

---

## 4. W4 (Pre-Registered Experiment Proposal): Dispersive vs. Truncation Regularization

**⚠️ Corrected 2026-08-14 (M2 scoping investigation):** the paragraphs
below originally described a "MechanicaFluidorum exponent instrument"
and a "W2 (reflective seam, already proposed in MechanicaFluidorum)"
regulator as existing artifacts to import. **Neither exists.** A targeted
search of MechanicaFluidorum (Explore agent, 2026-08-14) found:
- A real, working Tier-C dyadic shell-model simulation
  (`exploration/dyadic_cascade.py`, ad-hoc script, no regulator
  abstraction, "no claims" banner) — usable as a numerical starting
  point, not an instrument.
- A design memo for a peak-enstrophy exponent-fitting protocol
  (`docs/designs/OP2_LITE_CANDIDATES.md`) that explicitly states "No
  code is written" — a pre-registered design, not an implementation.
- No file, function, or object named "W2," "exponent instrument," or
  "CIC"/"Certified Interval Criterion" anywhere in MechanicaFluidorum or
  Mathesis. The `Reff_bounce` Lean theorem (`CallensDualScale.lean`) is
  a scalar real-analysis result (`max(R, α/R)`), not a numerical shell-
  model regulator, despite the name-association with "T-dual bounce."

This was this stream's own aspirational description of itself, stated as
though already true elsewhere — exactly the "two-definitions-under-one-
name" and "building on a fiction" failure the programme's own governance
(Rule E-X, LL-3) exists to catch. See LL-9 in LL.md for the lesson.
**The design below is retained as the physics proposal it always was;
the "already exists, just import it" framing is removed.** M2 must build
the regulator abstraction and exponent-fitting harness as new work,
informed by (not assumed identical to) MechanicaFluidorum's real Tier-C
script and OP2_LITE design pattern. See PLAN.md M2 for the corrected
task breakdown and a decision point on where this harness should live.

### Design Overview

Build a dispersively regularized variant of the dyadic shell cascade: the
Katz–Pavlović nonlinearity plus a **quantum-pressure analogue** term
active below a healing scale ξ.

**Construction status:** candidate is a two-field (phase/amplitude) shell
system whose amplitude equation acquires the Madelung-type quantum-
pressure correction. **To be drafted and human-audited before any run**
(see Actions, §5) — this now includes designing the regulator interface
and exponent-fitting harness itself, not just the physics term.

### Three Regulators, One Instrument

Run a peak-enstrophy exponent-fitting harness (to be built — see above)
on three regulators of the **same bare cascade**:

1. **T-dual truncation** (control)
   - Regulator: standard truncation cutoff at a fixed shell index
   - Represents: a geometric cutoff with no internal structure
   - Note: β_control = −2/3 appears in MechanicaFluidorum's
     `OP2_LITE_CANDIDATES.md` as a *pre-registered threshold*, not a
     measured/calibrated result from a run — do not cite it as an
     empirical value until independently measured

2. **T-dual bounce** ("W2", reflective seam)
   - Regulator: reflective boundary condition at some mode wavenumber
   - Represents: a bounce mechanism (reflection/inversion symmetry)
   - Status: proposed here, not implemented anywhere yet

3. **Dispersive / quantum-pressure** (W4 — this proposal)
   - Regulator: healing-length-scale quantum-pressure term
   - Represents: dispersive regularization (energy-preserving)

### Pre-Registered Readout

**Observable:** Peak-enstrophy exponent β(ξ) or β(α') per regulator.

**Experimental protocol:**
- Identical four-arm sampling controls (same initial conditions, same box, same time window)
- Certified Interval Criterion (CIC) per Mathesis/MENSURA framework
- Report β with 95% confidence intervals
- File results in LEDGER.md immediately

### Fixed-in-Advance Interpretations

**Scenario 1: Three equal exponents.**  
⇒ The cutoff mechanism is **irrelevant at this observable** (a real and useful negative result).

**Scenario 2: Dispersive regulator flattening β where truncation does not.**  
⇒ The regularization mechanism **carries information the exponent sees**. This is the first experimental daylight between "a cutoff" and "**this cutoff**" — which is exactly the daylight the programme's geometry claims exists.

### Why This Matters

The experiment is not attempting to resolve ξ → 0 (known open problem). It is asking: **at fixed ξ**, does the *type* of regulator leave a signature in a measured exponent? If yes, that signature is the programme's first measured datum in quantum fluids.

---

## 5. Actions

### A1. Literature Retrieval (LL-6 blocking)
Retrieve and date every `[LL-6 pending]` reference in §2:
- Madelung (1927) — Zeitschrift für Physik
- Onsager (1949) — Nuovo Cimento
- Feynman (1955) — Progress in Low Temperature Physics
- BCS (1957) — Physical Review
- Deaver–Fairbank (1961) & Doll–Näbauer (1961) — Phys. Rev. Lett.
- Barenghi–Skrbek–Sreenivasan (2014) — PNAS
- Bethuel–Saut (GPE well-posedness) — archival or textbook
- Godfrin et al. (2021) — PRB 103:104516 (already VERIFIED, LIT-002)
- Polanco et al. (2025) — PNAS 122(27) (already VERIFIED, LIT-004)

**Owner:** M0 milestone, target 2026-08-31. See LITERATURE_LEDGER.md for retrieval paths.

### A2. W4 Shell Construction (Design Memo, Pre-Audit)
Draft a design memo (E-1: definition first, audit before code) specifying:
1. The two-field (phase/amplitude) shell Hamiltonian
2. Madelung-correction term (quantum-pressure analogue)
3. Dimension consistency checks
4. Comparison against DMBT literature values
5. Proposed healing length ξ (as a free parameter for W4)

**Owner:** M2 milestone, target before W4 run. Will undergo human audit (checklist: term signs, ξ interpretation, fidelity to E1.1).

### A3. Related-Work Paragraph (NS Article)
One paragraph in the NS article's related-work section (after E1 is promoted):
- Express E1.2/E1.4 (quantum-fluids sibling problem)
- Replace any temptation to cite quantum fluids as *evidence* with citing them as the *realized sibling*
- Cite LIT-001 (Godfrin & Krotscheck 2022) as the entry point to the quantum-fluids literature

**Owner:** M4 milestone (post-W4 results). Tone: recognition of a parallel open problem, not a solution claim.

### A4. Rosetta Table Sync
Keep row entries in MEMO_ROSETTA.md (especially the **Quantum Fluids** row) in sync with revisions to E1 as literature retrieval completes.

**Owner:** Continuous during M0. When A1 completes, the Quantum Fluids row status changes from `[LL-6 pending]` to `VERIFIED`, and the Action column updates.

---

## 6. Appendix: Tier Labeling Convention

| Tier | Meaning | Example from this memo |
|---|---|---|
| **Tier A** | Citation-verified, established result | Madelung 1927; Onsager 1949; Feynman 1955; Godfrin et al. 2021 (once [LL-6] retrieved) |
| **Tier B** | Unit-testable, reproducible within this programme | W4 shell model once constructed and audited; enstrophy exponent measurement |
| **Tier C** | Narrative, exploratory, not verifiable by external citation or test | The Sym² analogy between BCS and hydrodynamic modes (E1.3); any speculation beyond named experiments |

---

## 7. Cross-References

- **Mathesis.Duality.lean** (lean_src/): Core theorems P1–P4
- **MEMO_ROSETTA.md** (docs/): Quantum Fluids row (status: Tier A physics → programme reading)
- **LITERATURE_LEDGER.md** (docs/): Citation registry; [LL-6 pending] items from this memo
- **PLAN.md** (root): Milestones M0–M4; M0 unlocks all [LL-6 pending]
- **LEDGER.md** (root): Claims filed post-M1/M3
- **LL.md** (root): Lessons learned, especially LL-6 (pending literature assembly)

---

**Version:** 2026-08-14 (proposal stage, awaiting M0 retrieval)  
**Status:** Ready for literature audit; no claims filed until [LL-6 pending] → VERIFIED  
**Next action:** A1 (literature retrieval), blocking A2–A4
