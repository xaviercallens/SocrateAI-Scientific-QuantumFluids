# Proposal: a numerical and formal tool for kinetic theory and quantum fluids, and what TDA can honestly add

**Status: PROPOSAL — awaiting owner review. Nothing here is implemented, and nothing will be until it
is approved.** Written 2026-09-21 in response to the request to review, improve and leverage
`SocrateAI-Scientific-Agora-Physique-Cinetique` as a tool for C. Villani and H. Godfrin, and to extend
the use of GUDHI/TDA toward identifying duality.

The analysis below was made on a read-only clone (HEAD `217f94a`); the three most consequential
findings were re-verified by hand, not taken from the automated report.

---

## 1. The repository as it stands — it cannot be shown to either scientist

This section is blunt because the cost of being wrong here is reputational and falls on the owner.

| | Finding | Verified |
|---|---|---|
| Size | 454 lines Python, 200 lines Lean (116 with content), 156 lines TeX | yes |
| Solvers | **None.** No Vlasov–Poisson, Boltzmann, BGK, spectral, PIC or semi-Lagrangian code; no numpy. Only sympy series manipulations | yes |
| Lean | Lean 4.31.0. Seven theorems, all ℚ arithmetic on literals. No reals, functions, integrals, PDE | yes |
| Vacuous theorems | `ripplon_L_star_is_4 : BakryEmery_L_star 2 = 4` with `def BakryEmery_L_star d := 2*d`, proof `rfl`. `admissible_singularity_limit (h : γ < gamma_bound) : γ < 16063/8232` with `gamma_bound := 16063/8232`, proof `exact h` | **yes, read the file** |
| The "nonlinear echo" | The sequence 1/2, −1/18, 13/4050 is the Taylor series of **Si(t)²/2** — from ρ¹ = sinc t, E = ∫ρ¹, ρ² = ∫ρ¹E. No two pulses, no wavenumbers, no delay, no phase space. A plasma echo is a large-time effect; a Taylor series at t = 0 cannot contain one | **yes, recomputed** |
| Inconsistencies | Lindhard coefficients differ between Lean (1/3, 19/45), Python (2/3, 2/15) and TeX; roton bound 1.567 in README vs 1.9513 elsewhere; manifold T² in code vs ℝP¹ in docs | reported, not re-verified |
| Data | A JSON result labelled "True 1D1V Vlasov–Poisson phase space simulation" that no code produces | reported |
| Claims | "absolute mathematical certainty"; "établit formellement que la dynamique … est protégée … par les constantes de Bakry-Émery"; "L'IA a retrouvé de manière autonome…" (the code hard-codes the series) | reported |
| Hygiene | No LICENSE; CI file in a subdirectory where GitHub does not run it; no ledger or retractions | yes (LICENSE) |

**The blocking problem is not technical.** The code defines `AgentGodfrin` and `AgentVillani` and prints
lines of the form `[Godfrin Output] …`, attributing generated output to two living scientists who have
not seen it. Whatever the intent, shown to either of them this reads as words put in their mouths. It
must be removed before anything else, and I would not help prepare any contact while it is there.

**Assessment.** The idea underneath — exact rational arithmetic where floating point loses structure,
with a proof assistant checking the result — is sound and is exactly what `PhononSeries` in this
repository just did successfully. The present repository does not yet do it: the Lean proves
arithmetic about constants that were typed in, not about the physics they are said to come from.
This is the same failure this project recorded as R1/R2 (correct, machine-checked, and not a
contribution), one level more severe, because here the statements are not even about the objects named.

## 2. What a tool each of them could actually use looks like

A mathematician working on Landau damping and an experimentalist measuring excitations in helium have
almost no needs in common. One tool for both is a framing error; propose **two thin tools on one
discipline** (ledger, negative controls, known-answer validation, no claim without a measured number).

### 2.1 Kinetic side — a *verified benchmark*, not a discovery engine

| # | Deliverable | Known answer it must reproduce | Why it is useful |
|---|---|---|---|
| K1 | Landau root of the linearised Vlasov–Poisson dispersion relation, with a **certified interval enclosure** (Arb via `python-flint`) | γ ≈ −0.1533, ω ≈ 1.4156 at k = 0.5 (Maxwellian) | the standard test of every Vlasov code, almost never given with a rigorous error bar |
| K2 | 1D1V semi-Lagrangian Vlasov–Poisson solver (cubic spline, Strang splitting) | measured damping rate within the K1 enclosure ± fit error; two-stream growth rate; recurrence time T_R = 2π/(kΔv) — the solver must *exhibit* recurrence, a control that fails if velocity resolution is misreported | reference implementation with its failure modes pinned as tests, as `solver2d.py` does for GP |
| K3 | A **real** plasma echo: pulses at (k₁, t=0) and (k₂, t=τ), response at k₃ = k₂ − k₁ | echo time t = τ·k₂/(k₂ − k₁) (Gould–O'Neil–Malmberg) | this is where exact arithmetic has genuine merit: the second-order response is a closed-form integral; derive it symbolically and compare with K2 |
| K4 | Lean: **phase mixing for free transport** — for f₀ with integrable velocity profile, the k-th density mode is f̂₀(k, kt) and tends to 0 as t → ∞ | — (theorem) | provable *today*: it is the Riemann–Lebesgue lemma, which Mathlib has. A true statement about a function, however modest — the first in that repository |
| K5 | Lean: *statements* (proofs open, labelled as such, in a non-default target) of the Penrose stability criterion and linear Landau damping | — | a precise formal statement is itself useful to a mathematician; an unproved one must never sit in a default target |

Explicitly **out of scope**: nonlinear Landau damping (Mouhot–Villani) in Lean. It is a ~180-page
analytic proof in Gevrey/analytic norms; no part of it is within reach, and saying otherwise to its
author would end the conversation.

### 2.2 Helium side — mostly already built, in *this* repository

| # | Deliverable | Status |
|---|---|---|
| H1 | Phonon C_V series, all six coefficients, machine-checked | **done** (`PhononSpecificHeat`) |
| H2 | Three-phonon decay thresholds from published coefficients, and from the raw table | done (`exploration/godfrin/`) |
| H3 | ρ_n(T), C_V(T) from the published dispersion tables with the integration cut-off exposed | partly done; package as a function with units |
| H4 | **³He: Lindhard/RPA S(Q,ω)** with Landau parameters F₀ˢ, F₁ˢ at given pressure; zero-sound dispersion and where it enters the particle–hole continuum; real units; convolution with an instrument resolution function | **new** — this is the one piece of the kinetic repository's subject matter that serves an experimentalist, and the one place the two halves genuinely meet (collisionless kinetic theory of a Fermi liquid *is* a Vlasov-type equation; zero-sound Landau damping is the same mathematics as K1) |
| H5 | Lean: Lindhard function static limit and the zero-sound condition `1 + F₀ˢ·Ω(s) = 0` has a root s > 1 iff F₀ˢ > 0 | new; a real `iff`, of the same kind as `three_phonon_open_iff` |

H4/H5 + K1 is the honest bridge between the two names: **Landau damping of zero sound in ³He**.

### 2.3 Preconditions — before any of the above

1. Remove the person-named agents and every `[Name Output]` line. Roles, not people
   (`LinearResponseStage`, `KineticStage`).
2. Retract the echo claim, the "protected by Bakry–Émery constants" claim and "autonomously
   rediscovered" in a `RETRACTIONS.md`; delete or relabel the two vacuous theorems.
3. LICENSE; move CI to the repository root; remove the orphan JSON.
4. Migrate to Lean 4.34.0-rc2 (same pin as here) so the two libraries can share code.
5. Decide: separate repository, or a `kinetic/` package in this one. **Recommendation: this one** — it
   already has the ledger, Comparator pipeline, test harness and the GP solver, and H1–H3 live here.

## 3. TDA and duality — what can be claimed, given this project's record

Record first. Three TDA-flavoured proposals have been made here: the vortex-separation floor (refuted:
vortices sit *closer* than Poisson), the dual-scale combination (withdrawn), and persistence of ε(k)
(stopped at the literature gate: it is topographic prominence, 0.4501 = 0.4501 meV). Base rate for the
next "TDA reveals X" is therefore poor, and the proposals below are framed as **instruments with
known-answer controls**, not as discoveries.

**What "identify duality" can mean rigorously.** TDA cannot discover a duality. It computes invariants.
A duality is a map between two descriptions; it *predicts a relation between their invariants*; TDA can
test that prediction. So each item below names the duality, the predicted relation, and what would
falsify it.

| # | Duality | Predicted relation between persistence diagrams | Status of the prediction | Value |
|---|---|---|---|---|
| D0 | **Alexander duality** (mathematics, not physics): sublevel sets of ρ vs superlevel sets of ρ on a periodic 2D box | H₀ sublevel diagram of ρ (vortex cores as minima) ↔ H₁ superlevel diagram (holes in the bulk), by the symmetry theorem of extended persistence (Cohen-Steiner–Edelsbrunner–Harer) | **theorem** | a *pipeline control with a known answer*. If GUDHI cubical complexes on our data do not reproduce it, the pipeline is wrong. Run first. Nothing to discover — that is the point |
| D1 | **Density-only vortex detection.** Experiments image \|ψ\|², never the phase; `VortexWinding` needs the phase | H₀ sublevel persistence of ρ separates vortex cores (persistence ≈ n₀, depth to zero) from sound-wave dips (small persistence) without a threshold; validate against phase winding on our GP runs where both are available | testable; **literature gate likely finds prior art** (persistent homology of a GP gas with vortices is published — see paper §8) | a tool feature for absorption images, with a measured false-positive/negative rate against ground truth. Not novelty |
| D2 | **Boson–vortex (particle–vortex) duality in 2D**: superfluid ↔ Coulomb gas of vortices; BKT transition = pair unbinding | H₀ persistence of the *signed* vortex point cloud: below T_BKT deaths concentrate at the pair scale, above they spread to the inter-vortex scale; the dual description predicts the crossover coincides with the jump in superfluid stiffness | testable on a stochastic/projected GP run (needs a finite-temperature solver we do not have). **Prior art exists for the XY model** (persistent-homology detection of BKT, c. 2021–22) — to be pinned down at the gate | if the gate passes: a transfer of a known method to GP. If not: cite and stop, as in paper §8 |
| D3 | **Phase-space holes (kinetic side).** Two-stream saturation forms BGK vortices in (x, v) | H₁ of superlevel sets of f(x,v): one long-lived class per trapped-particle island; persistence ≈ island depth; filamentation appears as a growing cloud of short-lived classes, giving a resolution-independent measure of when the solver stops resolving f | testable with K2 | the one place TDA and the kinetic tool meet. Gate first |
| D4 | The k ↦ k*²/k "dual length" | — | **retracted (R2). Not to be revived** by dressing it in persistence diagrams | none |

**Pre-registration requirement.** D1–D3 each need, *before* code: the statistic, the null, the
negative control that must fail, and the literature gate result. The A–L check this week was run
without pre-registration; it survived because a symbolic match cannot be tuned. A persistence-diagram
comparison can be tuned in a dozen ways, and would not survive the same lapse.

## 4. Proposed workflow (for approval — not started)

Seven agents, within the session's size guideline. Gates are hard stops that return to the owner.

| Phase | Agents | Output | Gate |
|---|---|---|---|
| 0. Preconditions | 1 | PR on the kinetic repo: agents renamed, retractions, LICENSE, CI | **owner approves the PR** — it edits a repository I have not been asked to modify |
| 1. Literature | 2 (kinetic; TDA) | prior-art memo for K1–K5, D1–D3 | any item that is a renaming is struck, as in paper §8 |
| 2. Known answers | 2 | K1 enclosure; D0 control | K1 must bracket −0.1533; D0 must hold. Else stop |
| 3. Build | 2 (K2+K3; H4) | solvers with failure-mode tests | measured rate inside K1 enclosure |
| 4. Formal | 1 | K4, H5 proved; K5 stated, non-default | Comparator, negative controls |
| 5. Adversarial review | 1, fresh context | "what would a kinetic theorist / a neutron scatterer object to in ten minutes" | owner decides on contact |

**Contact.** Neither scientist should be approached on the strength of the kinetic repository. The
Godfrin hold stands (`docs/FOR_GODFRIN.md` §0). For Villani there is at present nothing to send; after
Phase 4, K1 + K2 + K4 would be a modest, correct, checkable package, and should be described as exactly
that.

## 5. Decisions needed from the owner

1. Approve removing the person-named agents from the kinetic repository (precondition for everything).
2. Kinetic code: into this repository as `src/quantumfluids/kinetic/` (recommended), or kept separate?
3. Which TDA items to pre-register: D0 only / D0+D1 / D0+D1+D3 (recommended) / all including D2, which
   needs a finite-temperature solver.
4. Approve the workflow in §4, or a smaller first cut (Phases 0–2 only: recommended, since Phase 2 is
   where we learn whether the rest is worth building).
