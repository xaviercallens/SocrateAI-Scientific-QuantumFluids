# Exciton fluids: proof, physics and solver — a study and an implementation plan

> **Update 2026-10-11 (supersedes the status sentence below).** Phases 1 and 2 were run as pre-registered, the Lean files were
> re-checked by two separate instances, the library was aligned to Lean 4.34.1, and the results were written up as a technical
> note (Zenodo, concept DOI 10.5281/zenodo.23289026). Read `docs/designs/EXCITON_FLUID_PHASE1_RESULTS.md`,
> `EXCITON_FLUID_PHASE2_RESULTS.md`, `exploration/exciton/README.md` and the status section at the end of
> `EXCITON_FLUID_LEAN_HANDOFF.md`. Two things changed the plan: the experiment's own four-flavour model is the Lean target
> (not a driven-dissipative GPE), and the control kernel of Phase 2 was ill-posed (unbounded functional). WP3's X4 is done
> conditionally on the upstream theorem.

**Status: STUDY AND PLAN, revision 2. No solver experiment has been run and nothing is released.** Revision 2 records
what changed when the owner supplied the Lean material (§0); the Lean statements of §3.4 and the keystone lemma X1
have since been compiled in the QuantumFluids pin (producer: this session, **verifier pending**).
Numbers marked *(computed here)* come from throw-away scripts run while writing this document (Appendix B lists them);
everything else is quoted from the sources named in §11. Drafted with AI assistance, like the rest of the programme;
owner review pending.

Date 2026-10-10 (after the release of v1.20.0). Requested by X. Callens: "study and do not implement on leveraging
rusty-SUNDIALS with Lean 4 … prepare, and I will provide the GitHub repo and the Lean 4 material … an implementation
plan as md combining, as the book, the Lean 4 formalization, the physics and the solvers".
Related: the book (concept DOI 10.5281/zenodo.23272153), `docs/designs/RUSTY_SUNDIALS_EVOLUTION_PLAN.md`,
`docs/designs/PGPE_EXTERNAL_REPRODUCTION.md`, LL-15 (check dependencies, not analogy).

---

## 0. Revision 2: what the LeanMaster delivery changed (2026-10-10, evening)

The owner pointed to LeanMaster v3.48.0 (`contrib/openai_math_corollaries/`, produced on a second server from the
AutoevolveAI worktree `worktree-openai-math-discovery`, merged as PR #3, 4f2ce235). I read it from a fresh sparse clone
of the tag. The GitHub account `callensxavier` has one unrelated public repository; the work is under `xaviercallens`.

**Checked here.** The sha256 manifest (1,586 files) matches the files on disk and no file is missing or extra; a scan for
token patterns found none. `TRI_CMP/result.json`: verdict `COMPARATOR_ACCEPTS` for
`OAI.Analysis.Triangular.Energy.Universal` against `ComparatorChallenges.TriangularEnergy` (same statement; axioms
propext, Quot.sound, Classical.choice; 140 min), with the stated limits: statement adequacy not human-audited, no
external kernel (nanoda not run), the other triangular roots not run. `audit/triangular/D1/compile_Axioms.json`: D1,
D1b, D2 and their controls depend only on the three standard axioms; the planted `ctl_sorry` and `ctl_axiom` are
flagged. A statement-fidelity audit against CKMRV Definitions 1.1–1.3 exists (`audit/triangular/statement_fidelity.md`),
by the producing agent: not independent. Pins: Lean 4.34.1, Mathlib `d13f23b7`, openai/math `adc7f124` (files
unchanged at `fd4aeeb2`); LeanMaster's own library is `v4.34.0-rc2`, the QuantumFluids pin, and the contribution is
explicitly outside its five gates and not Tier A.

**What it changes in this plan.**

1. **Gate G-U is largely met by a record, not by me.** The Comparator and axiom audits were run on the second server;
   I re-check only what is cheap (manifest, axiom lists). An independent re-run (140 min) is optional.
2. **D1/D1b/D2 import the upstream modules directly** (`import OAI.Analysis.Triangular.Energy.Universal`), they are not
   hypothesis-passing. Track M Lean work that needs the upstream definitions therefore lives in that environment
   (§4a); QuantumFluids quotes statements verbatim. Their names: `TriangularRiesz.riesz_admissible`,
   `triangular_riesz_optimal`, `latticeEnergy_riesz_lt_top`, `TriangularDensity.universal_any_density`,
   `triangular_optimal_any_density`, `attained`, `unscaled_false`, `TriangularControls.*`.
3. **Label clash.** Their pending D3 is *CKMRV Definition 1.3 at every density, with the vacancy configuration
   A∖{0} as a second, non-isometric minimiser*; their earlier D3 candidate (Yukawa, costed ~50 %) is not it. This
   plan's new lemmas are therefore labelled **X1–X6** (was D3a–D6).
4. **Non-uniqueness is now a fact, not a caveat**: in the infinite-configuration formulation the minimiser is not
   unique (a vacancy changes neither the density nor the `liminf`). Any physical uniqueness claim needs a periodic
   class or a rigidity argument; §3.2 item 3 stands and is sharpened.
5. **L3 and part of L5 exist in practice**: BAOCert (rational interval arithmetic with a soundness theorem, integer
   certificates by `decide +kernel`, a tampered-table control) and `scripts/mcp_crosscheck_p2.py`, which uses the
   rusty-SUNDIALS `sundials-mcp` server **from a PR #63 worktree** as an untrusted cross-check of the certified
   enclosures. PR #63 Part B (stdout → stderr) matters to them: merging it is more useful than I had assumed.
6. **I proved the keystone lemma and the four-flavour theorems** (they were cheap: ≈ 20 s and ≈ 2 min compiles in the
   QuantumFluids pin), which moves them from paper-level to kernel-checked, with the producer/verifier caveat:
   `exploration/exciton/lean/ExcitonX1.lean` (X1, bilayer admissibility given D1, the GEM-4 control) and
   `FourFlavour.lean` (T1, T2, T3, density, T5 gap and critical field, T6), standard axioms only, plus
   `FourFlavourNegativeControl.lean` which fails as intended. The brief for the second server is
   `docs/designs/EXCITON_FLUID_LEAN_HANDOFF.md`.

---

## 1. Summary

**The physical system** is not quite the one in the briefing. The result behind it is R. Qi, …, A. H. MacDonald,
F. Wang, *Two-component exciton condensates in an electron–hole bilayer*, Nature 654 (2026), arXiv:2603.15443:
a MoSe₂/hBN/WSe₂ electron–hole bilayer (interlayer distance d ≈ 2 nm) with **electrically injected, equilibrium**
dipolar excitons, four spin–valley flavours, and evidence for a **two-component BEC** from the spin–valley
susceptibility (magnetic circular dichroism); BKT temperature up to ≈ 1.8 K near the exciton Mott density
n ≈ 0.75 × 10¹² cm⁻². Counterflow transport and interferometry are not available (the authors call counterflow
"experimentally inaccessible in current TMD bilayers"); the evidence is thermodynamic, and the susceptibility
difference is used as a proxy of the superfluid density. That changes the model: the natural description is the authors' **four-flavour mean-field Hamiltonian** (their Eq. 2–3),
not a pumped, decaying driven-dissipative Gross–Pitaevskii equation.

**The mathematics** is the planar universal-optimality theorem of OpenAI (23 and 26 September 2026): for every smooth
completely monotone interaction of the squared distance, the triangular lattice minimises the lower energy per
particle among all locally finite planar configurations of centred density one. AI-generated, not peer-reviewed,
with a Lean formalization whose Comparator configuration permits only the three standard axioms.

**What the two have to do with each other** (dependency check, §3.3). The theorem applies — rigorously, on paper here
and to be kernel-checked — to the *classical point-particle limit* of the exciton–exciton direct interaction:

* the bilayer dipole kernel, and in fact `g(t) − g(t + d²)` for **any** completely monotone single-layer potential
  `g` (Coulomb, Yukawa, Keldysh), is completely monotone (a five-line proof, Appendix A.1, **kernel-checked as X1**, §0);
* hence (i) a rigorous lower bound `e_lat(ρ) ≤ e₀(ρ)` on the ground-state energy per particle, (ii) positivity of the
  Fourier transform, so the Gross–Pitaevskii minimiser is the uniform state and the Bogoliubov spectrum has no roton
  (Appendix A.3), (iii) the value of the classical minimum in the strong-coupling limit.

**What it does not do.** In the experimental window the lower bound is far from the Hartree upper bound: `e_H/e_lat`
= 22, 13, 10, 8 at n = 0.1, 0.3, 0.5, 0.75 × 10¹² cm⁻² for d = 2 nm *(computed here)*. The observed phases are
governed by exchange and flavour physics that the theorem says nothing about. Its role is structural, and as an
independent test of the solver — not a prediction of the phase diagram.

**What does govern the observed phases** is a four-variable quadratic energy. Lean can prove, exactly, the
at-most-two-flavours theorem, the polarisation formulas the authors quote, the density in each phase and the critical
field of the first-order transition (§3.4) — **now compiled, verifier pending** (§0); the solver reproduces them and
extends to spatial structure.

**The solver**: rusty-SUNDIALS has **no ARKode** and its CVODE has a **dense direct linear solver only**. The existing
`qf-gpe2d` (split-step) and `qf-pgpe` (projected GP, IF-RK4, damping layers) engines are the base; CVODE is the
independent reference integrator on small systems (N-particle gradient flows, the four-amplitude flow, 16×16
fields). Whether an implicit or ImEx method is needed is a *measurement* (§5, WP7), not an assumption.

**Recommendation.** Two tracks, in this order, with an owner review after each phase:
**Track P** (physics model, short, high yield: four-flavour theorems + solver) and **Track M** (upstream-based:
kernel catalogue on top of the LeanMaster D1/D1b/D2, torus bound, N-particle experiments in which the *theorem
certifies the solver's output*). The driven-dissipative extension of the briefing and the Hugging Face/AI layer are optional
and gated. The exciton material is a companion note first, and a Part VI of a second edition only afterwards (§8).

**Needed from you:** §10 (a go for Phase 1 and where it runs, home for the new modules, solver choice). Also pending
from earlier today: rusty-SUNDIALS PR #63 (merge) and PR #68 (close), which the permission system declined (§3.5).

---

## 2. The triad in this study

| instrument | here | trust anchor | how it fails |
|---|---|---|---|
| **experiment / physics** | Qi et al. 2026 (their data and their model); the literature on dipolar fluids | the published, peer-reviewed version of record; primary sources | arXiv ≠ version of record; phenomenological parameters; analogy mistaken for dependency |
| **proof** | Lean 4 + Mathlib: the upstream theorem (imported on the second server, quoted verbatim here), the owner's corollaries D1–D2, new X1–X6 and the four-flavour theorems T1–T6 | the Lean kernel; standard axioms only; negative controls | vacuous or mis-normalised statements (KTFlow, Ch. 6), a theorem true of hypotheses the physics does not meet |
| **simulation** | rusty-SUNDIALS: CVODE, `qf-gpe2d`, `qf-pgpe` | known answers, convergence order, independent second integrator | stale builds (first-order Adams, Ch. 10), silent defects, wrong model |

The pattern is the book's: an untrusted generator (an AI-written proof, an AI-assisted solver, a language model's
parameter guess) behind a trusted checker (the kernel, a known answer, a second instrument), with planted negative
controls to show the checkers can fail.

---

## 3. What the study found

### 3.1 The experiment, from the source — and where the briefing differs

Read: arXiv:2603.15443 v1 (16 March 2026), main text and Methods. **Not read: the Nature version of record and the
Extended Data** (Extended Data Figs 4, 6, 7 carry the quantitative model details). Read them before any claim (the
Godfrin lesson: the Eq. (22) check was against the arXiv version only).

| briefing says | source says | consequence for the plan |
|---|---|---|
| BEC "made entirely of excitons" in stacked MoSe₂/WSe₂ | MoSe₂ (electrons) / hBN spacer / WSe₂ (holes); interlayer excitons, d ≈ 2 nm; hBN spacer 1–3 nm (device D1: 5-layer), graphite gates, 5–10 nm hBN gate dielectric | the kernel has two length scales (d, gate distance h) that matter at the interparticle spacing (12–15 nm at n = 0.75–0.5 × 10¹² cm⁻²) |
| excitons "decay into photons and must be replenished by a laser"; driven-dissipative GPE | the authors stress that *optically generated* excitons are too short-lived for equilibrium condensation; theirs are electrically injected, "equilibrium exciton fluids" | driven-dissipative GPE is the right model for optically pumped systems and polaritons, **not** for this experiment; kept as an optional extension (WP7) |
| "simulate applying a voltage across the grid" | the control knobs are the interlayer bias V_B (exciton density) and the symmetric gate V_G (Fermi level, e–h imbalance); T from 0.01 K; B up to tesla | in a model the knobs are μ (or n), the imbalance, and B — not a voltage drop across the grid |
| "zero-heat-loss quantum microchips, optical computers" | not in the paper; "modest in absolute terms" is the authors' own phrase for T_BKT | not used in the plan |
| "pre-trained GNNs (MACE, ALIGNN) predict the exciton binding energy" | MACE-MP-0 is a universal *interatomic potential* (energies, forces, stresses of bulk crystals); I found no ALIGNN output for exciton binding energies. Binding energy needs GW-BSE, a model Hamiltonian, or experiment (the paper: bound "until nearly 100 K") | the AI layer is not a route to the binding energy; see §3.6 |
| "datasets of MoSe₂/WSe₂ on Hugging Face (Materials Project, Matbench, Alexandria)" | `LeMaterial/LeMat-Bulk` on Hugging Face unifies Materials Project, Alexandria and OQMD (6.7 M *bulk* entries) | real, but bulk crystals: monolayer and heterobilayer properties are not there |
| "ARKode" | rusty-SUNDIALS has no ARKode crate (§3.5) | solver strategy S1–S3 in WP7 |

What the paper does establish (all from the arXiv text): four exciton flavours (two intravalley, two intervalley;
spin locked to valley); at B = 0 the ground state is a coherent superposition of two condensed intravalley flavours
(phase II_A); a weak field drives a first-order quantum phase transition to a two-component intervalley condensate
(II_B); at ≈ 1 T a fully polarised single-component condensate (I). The charge gap of the excitonic insulator
(~30 meV at low density) closes at n_Mott ≈ 0.75 × 10¹² cm⁻². BKT: k_BT ≈ 1.3 ħ²n/m_x for a single-flavour dilute gas
(≈ 6 K at 0.5 × 10¹² cm⁻² *(re-computed here: 5.7 K)*), reduced by about half for two components; the measured
maximum is ≈ 1.8 K. The authors say that earlier optical, capacitance and drag studies "do not distinguish a coherent
condensate from a classical exciton gas lacking phase coherence" and that counterflow is inaccessible in current TMD
bilayers; their own evidence is thermodynamic (the spin–valley susceptibility) and is read through the model of §3.4.

### 3.2 The upstream theorem, exactly

Source: `openai/math` (719 manuscripts in 372 families; README: "~42 % top-line results formalized", "some of the
unformalized results could have issues"). Family 090; manuscripts *Universal optimality of the triangular lattice*
(23 Sept 2026) and *An atomic certificate for triangular-lattice universal optimality* (26 Sept 2026); Lean scope note
`lean/docs/090.md`; Comparator challenge `ComparatorChallenges/TriangularEnergy.lean` with
`solution_module = OAI.Analysis.Triangular.Energy.Universal`, theorem `OAI.AtomicTriangular.universal_energy_minimum`,
`permitted_axioms = [propext, Quot.sound, Classical.choice]`. Toolchain of the upstream library: `v4.34.1`
(QuantumFluids is pinned at `v4.34.0-rc2`, Mathlib `85e3a25`).

Statement, as in the Lean challenge (note that the *challenge* file contains `sorry` by design; the solution module is
the proof):

```lean
abbrev Plane := EuclideanSpace ℝ (Fin 2)
def LocallyFinite (C : Set Plane) := ∀ R, (C ∩ Metric.closedBall 0 R).Finite
def DensityOne   (C : Set Plane) := Tendsto (fun R => (diskCount C R : ℝ) / (π * R^2)) atTop (𝓝 1)
def AdmissiblePotential (g : ℝ → ℝ) :=
  ContDiffOn ℝ ⊤ g (Set.Ioi 0) ∧ (∀ t > 0, 0 ≤ g t) ∧ ∀ r t, 0 < t → 0 ≤ (-1)^r * iteratedDeriv r g t
def diskEnergy g C R := (diskCount C R)⁻¹ * ∑ x ∈ diskPoints C R, ∑ y ∈ (diskPoints C R).erase x, ofReal (g (‖x-y‖^2))
def energy g C := liminf (diskEnergy g C) atTop            -- in ℝ≥0∞
-- A = triangular lattice of covolume one;  latticeEnergy g = ∑' a : {x // x ∈ A ∧ x ≠ 0}, ofReal (g (‖a‖^2))
theorem universal_energy_minimum (g) (C) (hg : AdmissiblePotential g) (hC : LocallyFinite C) (hd : DensityOne C) :
    latticeEnergy g ≤ energy g C ∧ latticeEnergy g = energy g A
```

Things a reader must not lose:

1. **Ordered pairs.** The energy counts ordered pairs: it is *twice* the usual pair energy per particle. Physical
   `e_lat(ρ) = ½ Σ_{a ∈ A_ρ∖0} V(|a|)`. A factor-2 slip here is exactly what the solver's lattice sum will catch.
2. **Centred-disk density and `liminf`**: infinite configurations, not tori. A bound on a finite periodic box needs a
   (new) periodic-extension lemma (X4).
3. **Value, not minimisers.** The manuscript says it "identifies the minimum value, not all minimizers". Uniqueness of
   the triangular minimiser is *not* part of the theorem and is **false in this formulation**: the vacancy
   configuration `A∖{0}` has the same density and the same `liminf` energy (the pending D3 of the LeanMaster
   contribution). Do not write "the ground state is the triangular lattice".
4. **Universal over the *class*, not per potential.** "Sharp auxiliary functions for every Gaussian", positive
   mixtures give every completely monotone potential; "a sharp auxiliary for each mixed potential … is not claimed".
5. **Infinite energies are allowed** (singular potentials, divergent lattice sums): the comparison then says every
   configuration has infinite energy. Finite lattice energy needs decay faster than t⁻¹ (s > 2): the user's D1b.
6. Predecessors (from the manuscript's own bibliography): Montgomery 1988 (Gaussian minimum among *lattices*);
   Rankin, Cassels, Ennola, Diananda (Epstein zeta among lattices); Faulhuber–Shafkulovska–Zlotnikov 2024, Hardin–Tenpas
   2025, Leblé 2025 (restricted competitor classes); Cohn–Kumar 2007 (conjecture), Cohn–Kumar–Miller–Radchenko–Viazovska
   2022 (dimensions 8 and 24). The "honeycomb" of the briefing is the Voronoi cell, not the lattice: the minimiser is
   the triangular (hexagonal) lattice.
7. **Proof technique**: sharp Gaussian Fourier minorants from an atomic interpolation certificate, with a *finite
   certificate* that the manuscript encloses by 512-bit Arb balls and exact rational arithmetic (its Section 3 and
   Appendices A and C). A Lean proof of such a certificate is exactly where `native_decide`/`Lean.ofReduceBool` tends to
   appear; the Comparator config forbids it, and checking that is a gate in WP0, not a given.

Status for our purposes: **an external hypothesis, Comparator-accepted on the second server** (§0). On that server the
corollaries import the upstream modules directly and their `#print axioms` includes the upstream proof. In
QuantumFluids the statement is quoted verbatim and never re-proved: the upstream library is one large project (its
README advises compiling small portions) and the root disk here is 96 % full. Mathlib-only results (X1, T1–T6) are
independent of it.

### 3.3 Where the theorem and exciton fluids actually meet (LL-15: dependencies, not analogy)

The theorem's hypotheses: a *radial* pair interaction that is a *completely monotone function of r²*, point particles,
classical energy, density fixed. Test of each physical kernel:

| kernel | g(t), t = r² | completely monotone? | basis | lattice energy finite? |
|---|---|---|---|---|
| Riesz | t^(−s/2) | yes, s > 0 | closed form (user's D1) | iff s > 2 (D1b) |
| single-layer Coulomb | t^(−1/2) | yes | Riesz, s = 1 | no (needs background: the jellium theorems of the same family) |
| **bilayer direct dipole–dipole** | 2[t^(−1/2) − (t + d²)^(−1/2)] | **yes** | `g(t) − g(t+d²)` lemma (A.1); also Laplace mixture with density s^(−1/2)(1 − e^(−sd²)) ≥ 0 | yes (tail ∝ t^(−3/2), s = 3) |
| **`g(t) − g(t + d²)` for any admissible `g`** | — | **yes** | (−1)^r g^(r) is non-increasing (A.1) | iff decay faster than t^(−1) |
| Yukawa | e^(−κ√t)/√t | yes | Lévy-mixture of Gaussians × CM | yes |
| Keldysh–Rytova | H₀(√t/r₀) − Y₀(√t/r₀) | yes | positive mixture of e^(−u√t/r₀)/√(1+u²), identity verified numerically *(computed here, 3·10⁻³¹)* | decays as 1/r: not by itself (the bilayer difference is) |
| **dual-gated bilayer** (image series, gates at ±h) | V_xx = G_ee + G_hh − 2G_eh | **numerically yes**: derivatives to order 5 at 7 values of t, h ∈ {5, 7.5, 10} nm, d = 2 nm *(computed here; not a proof)* | open: proof or counterexample is gate A-2 of WP2 | yes (exponential decay) |
| exchange and correlation terms | — | **no** (not of this form) | outside the theorem | — |
| non-CM controls | e^(−t²) (GEM-4, cluster crystals), Gaussian − Gaussian, tilted dipoles (not radial) | no | (4t² − 2)e^(−t²) < 0 at t = ½ | — |

Schoenberg's theorem gives the meaning of the condition: *completely monotone in r²* ⇔ positive definite in **every**
dimension. Positive definiteness in the plane (which is all the mean-field statements below use) is weaker.

Consequences, each with its status:

* **C1 — lower bound.** For N bosons on a torus with the periodised kernel and any (normalised) wave function,
  `E ≥ ⟨U⟩ ≥ N e_lat(ρ)` because the kinetic energy is non-negative and the periodic extension of any N-point
  configuration has centred density ρ. Needs: the upstream theorem, density scaling (D2), a periodic
  extension lemma (X4, the hardest new item), and the trivial variational step (X5). The *open-system* statement is a
  different theorem (boundary terms) and is not claimed.
* **C2 — no mean-field crystallisation; stability.** All Fourier coefficients of a CM kernel are ≥ 0, so
  `∬ n U n = Σ_k Ũ(k)|ñ(k)|² ≥ Ũ(0)N²/L²`: the **uniform state is the GP minimiser**, `e_GP = e_H = ½ρŨ(0)`
  exactly, and `ω_k² = ε_k(ε_k + 2nŨ(k)) > 0` (no roton). For the bilayer kernel `Ũ(k) = (e²/ε₀εk)(1 − e^(−kd))`,
  `Ũ(0) = e²d/ε₀ε` — the capacitor formula, and the paper's `g_H = 8πd` in atomic units (Appendix A.2).
  Consequence for the solver: a GP code *cannot* find the crystal for these kernels; that is a theorem, not a bug.
* **C3 — the value of the classical minimum** (not its minimiser, §3.2 item 3).
* **The sandwich.** `e_lat(ρ) ≤ e₀(ρ) ≤ e_H(ρ)`. Width *(computed here, bilayer kernel, units e²/4πε₀ε = 1, d = 1)*:
  `e_H/e_lat` = 44.7, 14.2, 4.64, 2.87, 1.87, 1.44 at ρd² = 10⁻³, 10⁻², 0.1, 0.3, 1, 3 (the first entry read 43.8 in revision 1: short lattice cutoff; corrected by Phase 1 KA-4). At d = 2 nm and
  n = 0.1, 0.3, 0.5, 0.75 × 10¹² cm⁻² (ρd² = 0.004–0.03) the ratio is 22.4, 13.0, 10.1, 8.3. The experiment is deep in
  the quantum-fluid regime; the bound is far from tight there and tight only in the crystal limit, which the Mott
  transition pre-empts. State this in every chapter that uses it.
* **Where the theorem's own domain is cheap to test.** For a torus commensurate with the triangular lattice
  (L_x = n_x a, L_y = n_y√3 a, N = 2n_xn_y, e.g. 6 × 3, N = 36) the bound is *attained*: a solver that reaches
  `N e_lat` is **certified globally optimal by the theorem** — the proof checks the solver, the reverse of the usual
  direction. For incommensurate tori the gap to `N e_lat` is a frustration (defect) energy, a physical observable.

### 3.4 The experiment's own model — and why it is the better Lean target

Qi et al. Eq. (2)–(3) (arXiv v1), flavours 1 = KK, 2 = K′K′ (intravalley), 3 = KK′, 4 = K′K (intervalley):

```
H = Σ_i (E_i − μ) n_i + ((g_H + g_X)/2) (Σ_i n_i)² − g_X (n₁n₂ + n₃n₄),      n_i = ψ_i†ψ_i ≥ 0
E₁ = (g_v − g_c) μ_B B − Δ,  E₂ = −(g_v − g_c) μ_B B − Δ,  E₃ = −(g_c + g_v) μ_B B,  E₄ = +(g_c + g_v) μ_B B
g_H = 8πd (a.u.: a_B = 1.5 nm, Ry = 67 meV),  g_c ≈ 3, g_v ≈ 6,  phenomenological g_X = 1 (a.u.), Δ = 1 μeV
```

The momentum dependence is neglected (uniform condensate). Hartree–Fock gives g_X < 0 (ferromagnetic), contradicting
the data; the authors fit g_X > 0. **These are phenomenological parameters: agreement of magnitude with the data is
not independent evidence.**

A four-variable quadratic program is exactly what Lean is good at. Theorems (all algebra; proofs by contradiction along
segments of concavity, `nlinarith`/`polyrith` for the closed forms):

| id | statement (g_X > 0 unless noted) |
|---|---|
| **T1** | every minimiser has its support inside one exchange pair, {1,2} or {3,4} (cross-pair supports only on the degenerate set E_i = E_j): along (1,1,−1,−1) the energy is strictly concave with coefficient −2g_X |
| **T2** | on support {1,2}: n₂ − n₁ = 2(g_v − g_c)μ_B B / g_X (the paper's formula) and N = 2(μ + Δ)/(2g_H + g_X) |
| **T3** | on support {3,4}: n₃ − n₄ = 2(g_c + g_v)μ_B B / g_X (the paper's formula) and N = 2μ/(2g_H + g_X) |
| **T4** | grand potentials Ω_A = −(μ+Δ)²/(2g_H+g_X) − β_A²/g_X, Ω_B = −μ²/(2g_H+g_X) − β_B²/g_X, with β_A = (g_v−g_c)μ_B B, β_B = (g_c+g_v)μ_B B |
| **T5** | first-order transition at (μ_B B_c)² = g_X Δ(2μ + Δ) / (4 g_c g_v (2g_H + g_X)); II_A is the ground state below B_c. Consequence: B_c ∝ √n at fixed Δ — the trend in the paper ("II_A persists to higher fields with increasing density") |
| **T6** | negative control, g_X < 0: every minimiser is single-component (the paper's Hartree–Fock ferromagnet) |

T2, T3 reproduce formulas the paper prints (a confirmation, not a finding — label them so, as for Eq. (22)); T1, T4,
T5, T6 are, as far as I read, not printed in the main text (the closed-form B_c may be in Extended Data Fig. 7).
*Checked here by brute force (computed here):* with the quoted parameters at n = 0.5 × 10¹² cm⁻² (g_H = 33.5 Ry a_B²,
μ = 25.6 meV) the closed-form B_c ≈ 56 mT; a numerical minimisation switches from II_A to II_B between 40 and 56 mT;
n₂ − n₁ at 10 mT agrees with T2. The paper's windows are "|B| < 30 mT (II_A)" and "30–70 mT (II_B)" at that density:
same order, as expected from parameters chosen to describe the data.

The bridge to Track M is one line: `g_H` is the zero-momentum Fourier transform of the direct bilayer kernel (A.2); the
four-flavour Hartree energy `½ g_H N²` is the model's `e_H`, so `N e_lat ≤ E₀ ≤ ½ g_H N²` is a statement about the
same quantity from both sides.

### 3.5 rusty-SUNDIALS: what exists and what does not

State examined: `rusty-SUNDIALS-c3` at 5db8041 and `main` = v11.6.0 (6545abf), read-only.

| item | state | consequence |
|---|---|---|
| CVODE | BDF 1–5, Adams 1–12 (LLNL `cvSetAdams`, carried into main by #69); **dense Newton/LU only**, analytic or finite-difference Jacobian, no Krylov, no matrix-free | dimension ≲ a few hundred: N-particle flows (2N ≤ 400), the four-amplitude flow; a 16 × 16 PGPE as reference (the existing cross-check) |
| ARKode (ARKStep, ImEx, MRI) | **absent** | the briefing's "ARKode" cannot be used; S1–S3 in WP7 |
| IDA, nvector (serial/parallel/simd), sundials-mcp | present | not needed here |
| `qf-gpe2d` | split-step Fourier, single component, local `g|ψ|²`, periodic, imaginary time, 7 tests + Python cross-check 1e-10 | base for the nonlocal-kernel and four-component extensions |
| `qf-pgpe` | projected GP (IF-RK4, order 4 verified against CVODE), vortex/transport/thermal/scattering toolkits, `FlowSolver` with damping layers Γ(x,y) and a unitary potential V | base for finite-T/BKT and for a damping term |
| open defects | #63 *Part B* (the three "ERROR FAIL" lines print to stdout, which corrupts the sundials-mcp stdio stream) is not in main; stale first-order Adams in the shared venv (CLAIM-109; build 5db8041 in `/mnt/data/xdev-cache/rs_py_5db8041`); an intermittent Adams defect seen by the Chapter-8 author, not investigated; `CvodeSolver.solve` cannot integrate backwards | gate S0 of WP4/WP5: re-measure before use |
| in-tree Lean (`proofs/`, `formal_proofs/`) | 75 files; 17 contain the token `sorry` (comments included), 17 declare an `axiom`, 13 use `native_decide`; CI runs only `lean --run cvode.lean` | specification skeletons over `Float`, **not a trust anchor**; the audited QuantumFluids library (Mathlib, no `sorry`, standard axioms) is |
| local clone `~/xdev/rusty-SUNDIALS` | 20 commits behind origin, uncommitted edits to `crates/cvode/src/solver.rs`, untracked cosmology/leanflow examples | not mine, not touched; builds for this study must use the clean clone |

PR housekeeping (a call to do it was declined by the permission system, so nothing was changed):
**#68** is superseded by #69 (its title says "supersedes #68"), conflicts with main and fails CI → close as superseded.
**#63** carries, besides the Adams fix that is already in main (three of its files are byte-identical), the
stdout→stderr diagnostics, `crates/cvode/tests/diagnostics_stderr.rs` and the sundials-mcp stdio tests; it is
mergeable but behind main → update the branch, wait for CI, squash-merge under a title that describes Part B only.
The `qf-pgpe` README refers to "the Adams-order fix of PR #63" as if merged; merging closes that loop.
Main equals v11.6.0, so a merged #63 would be one unreleased commit.

### 3.6 The data/AI layer

Honest roles, in order of usefulness:

1. **Provenance, not prediction.** Structural inputs (lattice constants, in-plane mismatch, twist-dependent registry)
   from `LeMat-Bulk` or C2DB-type 2D databases, each with dataset id, version, hash, method and uncertainty in a
   *provenance ledger* that every solver run records. The Qi et al. model needs none of it (its inputs are a_B, Ry,
   g_c, g_v, d, and two phenomenological constants).
2. **Untrusted generator, interval checker.** Any ML-predicted parameter enters only as an interval; downstream
   statements are made for the whole interval (sensitivity scan), and a Lean/`norm_num` check enforces the
   dimensionless constraints (e.g. T5's positivity conditions).
3. **Publication.** Certificates and solver outputs as a Hugging Face dataset, as the programme already does
   (`callensxavier/socrateai-quantumfluids-causal-topology`).
4. **Not** the exciton binding energy from MACE/ALIGNN.

---

## 4. How Lean and the solver meet

| # | mechanism | cost | maturity in this repo | used in |
|---|---|---|---|---|
| **L1** | Lean-derived known answers (closed forms) → solver tests | low | the book's Ch. 5, 6, 8, 10 | everywhere |
| **L2** | Lean-verified invariants as runtime monitors (energy non-increasing along gradient flow; norm balance; positivity) | low | Ch. 3, 9 (norm/energy checks) | WP4–WP7 |
| **L3** | certificate checkers: the solver emits rational/interval data, Lean checks inequalities by `norm_num`/`decide +kernel` | medium | `WassersteinCertificate.lean` here; **BAOCert** (integer tables, soundness theorem, tampered-table control) and the `sundials-mcp` cross-check on the second server | WP4 (the torus certificate), H7 |
| **L4** | Lean-generated artefacts consumed by Rust: Butcher tableaux with proved order conditions, kernel tables | medium | `exploration/godfrin/gen_phonon_series_lean.py` goes Python → Lean; the reverse is new | optional WP-S |
| **L5** | verified a-posteriori error bounds for the small ODEs (interval arithmetic) | high | BAOCert does it for one integral (monotone integrand, cell bounds); not for ODE solves | stretch, not planned |

Trust boundary, stated once: **no statement here is about the Rust code.** Lean proves statements about models and
invariants; the solver is tested against them. The bridge `examples/leanflow_bridge.rs` of the owner's local clone
re-types a Lean-proved inequality as a Rust function; nothing connects the two, so that is the pattern to avoid. The
rule is **one source of truth**: constants and test oracles are exported from the Lean elaboration (or computed by an
independent script and compared mechanically with the Lean statement, as `facts/appA_citation_check.md` does for the
book), never retyped.

### 4a. Two servers, one contract

| | server A (this machine, QuantumFluids) | server B (LeanMaster / AutoevolveAI sessions) |
|---|---|---|
| runs | physics, rusty-SUNDIALS experiments, book; Mathlib-only Lean at the QuantumFluids pin (rc2), ≈ 2 min per file | the upstream-pinned stack (Lean 4.34.1, Mathlib `d13f23b7`), Comparator (140 min), BAOCert, `sundials-mcp` cross-checks |
| constraint | root disk 96 % full (data under `/mnt/data`); never `lake update` here | RAM and swap contention between sessions |
| owns | WP4–WP6 solver side, kernels' numerical tests, T1–T6 (done, verifier pending), the plan and the book | H1–H7 of the handoff (re-verification, bilayer corollaries of D1/D2, periodic configurations, certified numerics) |
| exchanges | quotes Lean statements verbatim from a manifest (name, file, sha256, axioms) | receives `docs/designs/EXCITON_FLUID_LEAN_HANDOFF.md`; returns files, `compile_*.json`, `verification.md` |

The contract: (1) the manifest above, regenerated at every hand-back; (2) certificates in the BAOCert convention
(common denominator `D`, integer `lo`/`hi` tables, a named claim) from the solver to server B, never the reverse;
(3) producer ≠ verifier on both sides; (4) every result carries its toolchain pin; (5) nothing is merged into
LeanMaster's `main`, and no Tier A label is used, without the owner.

---

## 5. Work packages

Names are proposals; modules go where the owner decides (§10, Q3). Sizes: S ≤ 1 agent-hour, M 2–4, L 5–8 (first
edition: ≈ 12 agent-hours for ten chapters).

### WP0 — Intake and gates (S)

* **Done (§0):** material received and checked (manifest, verdicts, axiom lists). **Still to do:** read the Nature
  version of record and the Extended Data of Qi et al.
* Upstream: nothing to build here. The Comparator run and the axiom audit are the second server's record (TRI_CMP,
  `COMPARATOR_ACCEPTS`, 140 min, standard axioms, nanoda not run).
* **Gate G-U (revised):** the formal statement equals the manuscript's Theorem 1.1 (mechanical diff of definitions,
  done by the producing agent, not independent: redo it once from the two sources); axioms ⊆ {propext,
  Classical.choice, Quot.sound}; no `native_decide`. Status: met by the record, with the caveats the record states. If a
  later check fails, the plan continues with the upstream as an *unverified* hypothesis and says so in every box.
* Literature gate (the programme's rule): QMC results for 2D dipolar bosons (Astrakharchik et al. arXiv:0707.4630;
  Mora–Parcollet–Waintal PRB 76, 064511; Büchler et al. PRL 98, 060404) — copy the crystallisation density and its
  definition from the primary sources; bilayer exciton literature for the exchange/correlation corrections to the
  capacitor formula.
* **Gate S0:** re-measure CVODE order (Adams and BDF) and the `qf-pgpe` cross-check on the chosen build.

### WP1 — Lean: upstream interface and the owner's D1, D1b, D2 (S; exists, to be consumed)

* The owner's D1, D1b, D2 and controls exist (LeanMaster `contrib/…/lean/Triangular/`, §0); QuantumFluids quotes them
  through the manifest. No new work except the two items below, both on server B (handoff H3).
* Normalisation lemma: `latticeEnergy g = 2 · e_lat` (ordered pairs), with the density scaling
  `g_ρ(t) = g(t/ρ)` (D2).
* Negative controls: `unscaled_false` already exists for density; add the ordered/unordered confusion — must fail.

### WP2 — Lean: kernel catalogue (M)

* **X1** `admissible_sub_shift`: `AdmissiblePotential g → c > 0 → AdmissiblePotential (fun t => g t − g (t + c))`
  (A.1). **Proved** in `exploration/exciton/lean/ExcitonX1.lean` (rc2 pin, standard axioms; verifier pending), with
  `admissible_const_mul`, `bilayerDipole_admissible` (given D1 at s = 1) and the control `gem4_not_admissible`. To do on
  server B: port to the upstream pin and discharge the D1 hypothesis (handoff H1, H2), then the corollaries
  `triangular_bilayer_optimal`, `bilayer_any_density`, `latticeEnergy_bilayer_lt_top`.
* **X2** `admissible_laplace` (Yukawa, Keldysh): Laplace transform of a finite positive measure is admissible
  (differentiation under the integral; Mathlib's mgf derivative lemma if present). Their own estimate for Yukawa was
  ~50 % (Bernstein/Faà di Bruno absent). Optional (handoff H4); the Keldysh kernel can be a *hypothesis*; the
  Struve–Neumann identity (DLMF §11.5) is checked numerically *(done here, 3·10⁻³¹)*, not proved.
* **X3** Fourier positivity of Gaussian mixtures: replaced by the *hypothesis form* of X6 (handoff H6); that completely
  monotone kernels are positive definite is classical (Schoenberg, Bernstein) and tested numerically by the solver.
* **X6** `uniform_minimises`: for a positive-definite `U` on a finite abelian group the interaction energy is minimised by
  the uniform density (write `n = n̄ + f`, `Σf = 0`; no Fourier transform needed); Bogoliubov `ω² > 0` extends the
  book's Ch. 5 (`bogEps`).
* **Gate A-2 (applicability of the real device kernel):** prove or refute that the dual-gated kernel is completely
  monotone. Numerical evidence says yes to order 5; an interval-arithmetic proof of the sign pattern or a Laplace
  representation of the image series is the deliverable; a counterexample would mean the theorem does not apply to the
  device without modification — itself a result.
* Negative controls: GEM-4 `e^(−t²)` not admissible (**done**, X1 file); the bilayer kernel with the wrong sign;
  Gaussian − Gaussian.

### WP3 — Lean: torus bound and quantum lower bound (L, riskiest new Lean)

* **X4** `periodic_energy_eq_cell_average`: for a configuration periodic under a full-rank lattice with N points per
  cell, centred density = N/area and `energy = per-cell average` (lattice-point counting plus a boundary-layer
  estimate; the divergent case is trivial). On server B (handoff H5). **Fallback** if too heavy: state C1
  *conditional* on X4 as a hypothesis and say so.
* **X5** `quantum_lower_bound`: for any probability density on the N-point torus and any kinetic functional ≥ 0,
  `E ≥ N e_lat(ρ)`; modelled at the level of expectations (no operator theory).
* Explicit **non-claim** in the docstring: not the open system, not uniqueness, not tight at the experimental density.

### WP4 — Solver E1: the theorem's own domain (M)

* N-particle gradient flow `ẋ = −∇E` on a rectangular torus under CVODE BDF (2N ≤ 400, analytic Hessian-vector or
  finite-difference Jacobian), periodised kernels by tail-corrected sums or Ewald with documented error; 200+ random
  starts per (kernel, N, aspect).
* Kernels: CM — Riesz s = 3, bilayer (d = 1, several ρd²), Yukawa, Gaussian, gated bilayer; non-CM controls — GEM-4,
  Gaussian − Gaussian.
* L2 monitor: `E` non-increasing along every trajectory (a Lean lemma for gradient flows of C¹ functions).
* L3 certificate: for commensurate tori the solver's energy, an *upper* bound, equals the upstream *lower* bound to
  1e-9 → the theorem certifies the optimum; for incommensurate tori report the frustration energy.
* Observe, do not assert: whether non-lattice minimisers of equal energy exist (the theorem is silent).

### WP5 — Solver E2: nonlocal-kernel mean field (M)

* `qf-gpe2d` extension: the nonlinear half-step uses `U ∗ |ψ|²` by FFT (a regression test: a constant `Ũ` reproduces
  the current outputs bit for bit). Kernel `Ũ(k) = (e²/ε₀εk)(1 − e^(−kd))` with the `k → 0` limit set analytically.
* Known answers: `Ũ(0) = e²d/ε₀ε`; the GP minimiser is uniform (X6); sound speed `c² = nŨ(0)/m`; Bogoliubov
  `ω(k)` from linearising the solver's own right-hand side vs the formula.
* Negative control (kernel with negative Fourier lobes: GEM-4, or a soft-core with a tail): density modulation
  appears, energy < `e_H`, instability band predicted by `ω² < 0`.
* The sandwich table of §3.3 reproduced from an independent lattice sum (Epstein zeta factorisation, A.4).

### WP6 — Track P: the four-flavour model (M)

* `FourFlavour.lean`: T1–T6 (§3.4) — **proved here** (standard axioms; verifier pending; parameters as arguments, a
  `structure` for the paper's values still to add); T2, T3 labelled confirmations; the negative control fails as intended.
* Solver: CVODE on the four-amplitude imaginary-time flow (4 variables, dense is fine); a B-scan with continuation up
  and down shows the hysteresis window of the first-order transition; compare B_c to T5 (1e-6 relative).
* Exploratory, labelled as such: four-component split-step in 2D (`qf-gpe2d` with the coupling matrix of Eq. 2),
  uniform-field domain walls between II_A and II_B regions (twist-angle inhomogeneity is mentioned in the paper),
  collective flavour modes. Not tested against data.
* Optional **WP-T**: T_BKT of a classical-field two-component gas with the programme's thermal toolkit vs
  the paper's Eq. (1) and the universal jump `n_s λ_T² = 4`.

### WP7 — Optional: the briefing's driven-dissipative model, and the solver decision (M–L)

* Model: `iħ∂ψ = [−ħ²∇²/2m + V + g|ψ|² + g_R n_R + (iħ/2)(R n_R − γ)]ψ`,
  `∂n_R = P − (γ_R + R|ψ|²) n_R` (Wouters–Carusotto, polaritons and optically pumped excitons). Known answers:
  threshold `P_th = γγ_R/R`, `|ψ|² = P/γ − γ_R/R`, the diffusive Goldstone mode. Lean: positivity invariance of
  `n_R ≥ 0` for `P ≥ 0`, norm balance, Routh–Hurwitz for the per-k 3 × 3 Jacobian.
* **Gate S0′ (stiffness):** measure the ratio of fastest to slowest rate for the physical parameters and the grid;
  compare IF-RK4/split-step cost at the target accuracy with an implicit alternative. For interlayer excitons
  (lifetime ≫ dynamics) the problem is probably *not* stiff.
* Only if S0′ says so: **S2** a new `arkode`-lite crate (ImEx RK with an FFT-diagonal implicit solve; Butcher tableaux
  with order conditions proved in Lean and exported, L4) or **S3** Krylov and matrix-free Jacobians in `cvode`. Default:
  **S1**, no new solver machinery.

### WP8 — Optional: data/AI layer (S–M, owner-gated)

Provenance ledger and interval inputs (§3.6) only; no model in the loop of any claim.

### WP9 — Write-up and publication (M)

Companion technical note first, with registered gates and the honest boxes; then two or three chapters (§8).

---

## 6. Pre-registration skeleton

Register in `docs/designs/` *before* any run (the programme's practice); claim ids to be assigned at that time.

| id | claim | gate (all tolerances to be fixed at registration) | falsifier / negative control |
|---|---|---|---|
| KA-1 | lattice sums | direct summation equals `6ζ(s/2)L(s/2, χ₋₃)`; for r⁻³ at unit spacing 11.0341757349 | wrong factor 2 caught |
| KA-2 | Hartree integral | `∫V d²r = 4π d` (units), `Ũ(0) = e²d/ε₀ε` to 1e-10 | wrong shift in `g(t) − g(t+d²)` |
| EX-1 | **no CM configuration below `e_lat`** (numerical test of the upstream theorem, not proof) | over ≥ 200 starts per case, none below `e_lat(1 − 10⁻¹²)`; commensurate torus: some start reaches `e_lat(1 + 10⁻⁹)` | any violation → solver bug, hypothesis mismatch (ordered/unordered, density), or an error upstream: investigate in that order |
| EX-2 | hypotheses are needed | GEM-4 (and Gaussian − Gaussian) reaches ≥ 1 % below `e_lat` at a registered density | none found → the control is mis-specified |
| EX-3 | GP minimiser is uniform; `ω² > 0` | solver `ω(k)` within 1e-4 of the formula; imaginary parts zero | non-CM kernel must show `ω² < 0` |
| EX-4 | sandwich | `e_lat ≤ e_H` at every tabulated density; table reproduced to 1e-6 | — |
| FF-1 | T1–T6 compile, standard axioms | **met by the producer** (rc2 pin); verifier pending | T6 needs `g_X < 0`; the wrong-sign control fails (done) |
| FF-2 | solver reproduces T2, T3, T5 | 1e-10 (T2, T3), 1e-6 (B_c); hysteresis window found | — |
| AP-2 | gated kernel completely monotone | proof, or a counterexample with certified enclosure | — |

Explicit non-claims: no new exciton physics; the Lean theorems are about models, not about the experiment; no
"best solver"; no statement that Qi et al. or OpenAI reviewed or endorse anything; **no contact with either group
without the owner's explicit say-so** (the Godfrin rule applies here).

---

## 7. Sequencing, cost and resources

| phase | content | owner review |
|---|---|---|
| 0 | WP0 (+ PR housekeeping) | gate G-U, G-S0, inputs received |
| 1 | WP6 (Track P, solver side), WP4; on server B: handoff H1–H3, H6 | after FF-2 and EX-1 |
| 2 | WP5; on server B: H5 (X4), X2, A-2, H7 | after EX-3, EX-4 and A-2 |
| 3 | WP7, WP8, WP-T (only if wanted) | — |
| 4 | WP9 | publication decision |

Rough budget: Phase 1 ≈ 6–8 agent-hours, Phase 2 ≈ 6–10, Phase 3 ≈ 4–8, Phase 4 ≈ 3–5. Two waves with few writers,
and **check the spend limit before any fan-out** (the second-edition fan-out of eight agents stopped at the monthly
limit, reset 11:00 Europe/Paris). Compute is CPU only: WP4 minutes; WP5–WP6 2D runs ≲ 1 h each under
`flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice`. Disk: never `lake update` in this repo; the upstream clone and its
build go under `/mnt/data/xdev-cache/`; measure first. Mathlib version skew (rc2 vs 4.34.1) is handled by keeping
Mathlib-only files portable (the two proved files are; one local definition is a verbatim copy, guarded by an `Iff.rfl`
check on server B) and by the statement-versus-statement diff, which is mechanical.

---

## 8. Book integration and publication path

* **Where.** Not on the critical path of the second edition. Recommended: a *companion technical note* (own Zenodo
  record, registered gates, ledger claims) first; then a **Part VI "Excitons: a quantum fluid in a solid"** of the
  second edition with three chapters — (16) *Four flavours*: the model, T1–T6, the solver, the experiment; (17) *How far
  from a crystal?*: the theorem, the kernel catalogue, the sandwich, the torus certificate; (18) *Trusting a theorem you
  did not prove*: conditional statements, Comparator and the statement-fidelity audit, negative controls, the numerical test of an AI-generated theorem.
  An optional chapter on driven-dissipative fluids only if WP7 is executed.
* **Template.** Each chapter keeps the book's boxes: `leanbox`, `rustbox`, `honestbox`, three exercises; the
  `godfrinbox` becomes a new neutral `expbox` ("Experiment: Qi et al.") in `qfbook.sty`. The dedication stays to
  Godfrin; the preface of Part VI must say that this part is not about his measurements, that neither he nor the
  authors cited have reviewed it, and that the upstream theorem is AI-generated and unrefereed.
* **Release path.** New version of the existing book record (`scripts/zenodo_deposit_paper.py --new-version-of
  23272154`) for the edition; the note is a separate record (`--reserve` first, cite the concept DOI in the colophon).

---

## 9. Risks and honest limits

| risk | mitigation |
|---|---|
| upstream theorem wrong or mis-stated (AI-generated, unrefereed, "some unformalized results could have issues") | conditional statements; Comparator and axiom audit (G-U, record of server B); statement-fidelity audit (producer's, not independent); EX-1 as an independent numerical test; every box says it |
| analogy mistaken for dependency (LL-15) | §3.3 table; every use states which hypothesis of the theorem the physics meets |
| the bound is uninformative at experimental densities | stated up front (ratio 8–22); framed as structure and solver test |
| arXiv ≠ version of record; phenomenological parameters | read the Nature version and Extended Data in WP0; label agreement "not independent" |
| normalisation slips (ordered pairs, density scaling) | planted negative controls; solver lattice sum as the cross-check |
| solver defects (Adams, stale venv, stdout diagnostics) | gate S0; build 5db8041 or a recorded newer commit; record `rusty_sundials.__file__` |
| scope creep (DD-GPE, ARKode, AI layer) | all optional and gated; default S1 |
| Lean cost of X4 | fallback to a conditional statement, said so |
| the new Lean files have no independent verifier yet | marked "verifier pending" everywhere; handoff H1 asks for a separate instance; nothing is cited as verified until then |
| three layers of AI assistance (math, Lean, code) | untrusted-generator/trusted-checker everywhere; negative controls; independent second instrument |

---

## 10. What I need from you

**Material: received (§0)** — LeanMaster v3.48.0 `contrib/openai_math_corollaries/`, with the pins and audit logs. Still
open from it: (a) which upstream commit family 090 was verified against — the contribution says `adc7f124`, files
unchanged at `fd4aeeb2` (7 Oct), while your fork `xaviercallens/xOpenAImath` is a single commit of 2026-10-06 and
predates that update; (b) the status of their pending D3; (c) the Nature version of record of Qi et al. and its
Extended Data (I have only arXiv v1).

**Decisions:**

| # | question | my recommendation |
|---|---|---|
| Q1 | tracks | Track P first (short, high yield), then M |
| Q2 | where do the new Lean modules live | T1–T6 and X1 (Mathlib-only, rc2): stay in `exploration/exciton/lean/` until a separate instance has verified them, then either `lean_src/` here (our audit) or LeanMaster proper (its five gates, a *Tier A* candidate since LeanMaster is also on rc2). Everything that imports openai/math (H2, H5, H7): the contribution tree on server B |
| Q3 | solver path | S1 only; revisit after gate S0′ |
| Q4 | driven-dissipative extension (WP7) | defer |
| Q5 | Hugging Face/AI layer (WP8) | provenance ledger only, defer the rest |
| Q6 | publication | companion note, then Part VI |
| Q7 | rusty-SUNDIALS PRs | update/merge #63 (Part B), close #68 as superseded — say go and I will do it, or run the `gh` commands yourself |
| Q8 | budget | two waves, spend limit checked first |
| Q9 | go for Phase 1 | yes: the solver side (WP4, WP6) here, the handoff H1–H3, H6 on server B; I will not start a fan-out without your word |

---

## 11. References

*Read or fetched in this session.* R. Qi, Q. Li, J. Nie, R. Xia, H. Kim, H. Lim, J. Xie, T. Taniguchi, K. Watanabe,
M. F. Crommie, A. H. MacDonald, F. Wang, *Two-component exciton condensates in an electron–hole bilayer*, Nature 654
(8119), June 2026, doi:10.1038/s41586-026-10636-y (bibliographic data via OSTI); arXiv:2603.15443 v1 *Observation of
two-component exciton condensates in an excitonic insulator* (16 Mar 2026), main text and Methods read.
OpenAI, *Universal optimality of the triangular lattice* (23 Sept 2026) and *An atomic certificate for
triangular-lattice universal optimality* (26 Sept 2026), `github.com/openai/math`: README, `CONTENTS.md` family 090,
`lean/docs/090.md`, `lean/ComparatorChallenges/TriangularEnergy.{lean,json}`, `lean/lean-toolchain`; the first
manuscript's text read to §2 and its bibliography. C. Mora, O. Parcollet, X. Waintal, *Quantum melting of a crystal of
dipolar bosons*, Phys. Rev. B 76, 064511 (2007) (abstract). `LeMaterial/LeMat-Bulk` (Hugging Face blog and dataset
page, via search).

*As listed in the upstream manuscript's bibliography, not re-checked:* H. Cohn, A. Kumar, J. Amer. Math. Soc. 20(1),
99–148 (2007); H. Cohn, A. Kumar, S. D. Miller, D. Radchenko, M. Viazovska, Ann. of Math. 196(3), 983–1082 (2022);
H. L. Montgomery, Glasgow Math. J. 30(1), 75–85 (1988); M. Faulhuber, I. Shafkulovska, I. Zlotnikov, Proc. AMS Ser. B
11, 664–679 (2024); D. P. Hardin, N. J. Tenpas, Discrete Analysis 2025, no. 26; T. Leblé, arXiv:2511.03353 (2025);
A. B. Lauritsen, J. Math. Phys. 62, 083305 (2021); M. Lewin, E. H. Lieb, R. Seiringer, Phys. Rev. B 100, 035127 (2019).

*From memory — verify before citing:* G. E. Astrakharchik et al., arXiv:0707.4630 (title and authors from a search;
numbers not read); H. P. Büchler et al., Phys. Rev. Lett. 98, 060404 (2007); M. Wouters, I. Carusotto, Phys. Rev. Lett.
99, 140402 (2007); I. Carusotto, C. Ciuti, Rev. Mod. Phys. 85, 299 (2013); L. V. Keldysh, JETP Lett. 29, 658 (1979);
N. S. Rytova (1967); DLMF §11.5 (integral representation of H_ν − Y_ν; equation number); D. R. Nelson, J. M.
Kosterlitz, Phys. Rev. Lett. 39, 1201 (1977); I. J. Schoenberg, Trans. AMS 44, 522 (1938); I. Batatia et al. (MACE-MP-0).

---

## Appendix A — proofs and derivations (paper level)

**A.1 Differencing preserves complete monotonicity** *(kernel-checked: `exploration/exciton/lean/ExcitonX1.lean`)*. Let `g` be admissible and `h_r(t) = (−1)^r g^(r)(t) ≥ 0`.
Then `h_r' = −h_{r+1} ≤ 0`, so each `h_r` is non-increasing on (0, ∞). For `c > 0` set `f(t) = g(t) − g(t + c)`.
Then `(−1)^r f^(r)(t) = h_r(t) − h_r(t + c) ≥ 0` for every `r ≥ 0` (for `r = 0` this is `f ≥ 0`); `f` is smooth on
(0, ∞). Hence `f` is admissible. With `g(t) = t^(−1/2)` and `c = d²` this is the bilayer dipole kernel. ∎

**A.2 The capacitor formula as a telescoping integral.** In 2D, `d²r = π dt` for `t = r²`. For `f(t) = g(t) − g(t + d²)`
with `g(T) → 0`: `Ũ(0) = ∫ V d²r = π ∫₀^∞ [g(t) − g(t + d²)] dt = π ∫₀^{d²} g(t) dt`. For `g = 2t^(−1/2)` (units
e²/4πε₀ε = 1) this is `π · 4d = 4πd`, i.e. `e²d/(ε₀ε)`; with `e²/4πε₀ε = 2 Ry a_B` it is `8π Ry a_B d`, the
paper's `g_H = 8πd`. Verified by quadrature to 17 digits *(computed here)*. For a Keldysh single-layer `g` the same
identity gives the mean-field coupling with screening.

**A.3 Mean-field consequences of a non-negative Fourier transform.** On the torus, `∬ n(x)U(x−y)n(y) = (1/L²)
Σ_k Ũ(k)|ñ(k)|² ≥ Ũ(0)|ñ(0)|²/L² = Ũ(0)N²/L²` when all `Ũ(k) ≥ 0`, with equality iff `n` is uniform (when
`Ũ(k) > 0`). The kinetic term is ≥ 0 and vanishes for the uniform state, so the uniform state minimises the GP
functional. Linearising about it gives `ω_k² = ε_k(ε_k + 2nŨ(k))`, positive for all k.

**A.4 The lattice sum.** `Σ′_{(m,n)} (m² + mn + n²)^(−s) = 6 ζ(s) L(s, χ₋₃)`, χ₋₃ the character mod 3. Checked
numerically at s = 2 and 3 *(computed here, direct sum to 400 vs closed form: agree to the truncation error)*. The
triangular lattice of nearest-neighbour distance `a` has `Σ′ r^(−p) = a^(−p) · 6 ζ(p/2) L(p/2, χ₋₃)`; for p = 3,
a = 1: 11.0341757349…

**A.5 First-order transition of the four-flavour model.** On support {1,2}, stationarity gives
`(E₁ − μ) + aN − g_X n₂ = 0` and `(E₂ − μ) + aN − g_X n₁ = 0`, `a = g_H + g_X`; subtracting yields T2 and adding yields
`N = (2μ − E₁ − E₂)/(2a − g_X)`. On {3,4}, identically, T3. For a homogeneous quadratic the minimum is
`Ω = ½ Σ (E_i − μ) n_i`, which gives T4; equating Ω_A and Ω_B gives T5.

## Appendix B — numbers computed in this study

Scripts (scratch, not committed): `study_checks.py`, `study_checks2.py`, `study_gated_cm.py` in the session scratchpad;
mpmath (30–40 digits) and numpy/scipy. The Lean files are committed (`exploration/exciton/lean/`).

| quantity | value |
|---|---|
| Σ′ r⁻³, triangular, a = 1 | 11.0341757349148097682794… |
| Σ′ (m²+mn+n²)⁻³ direct (|m|,|n| ≤ 400) / closed form | 6.375881552748 / 6.375881552830 |
| ∫ V d²r, bilayer, d = 1 | 12.566370614359173 (= 4π) |
| H₀(x) − Y₀(x) vs (2/π)∫e^(−xu)/√(1+u²)du, x = 0.1, 1, 5 | agree to 2·10⁻³¹ |
| (−1)^k g^(k) ≥ 0, ungated bilayer, k ≤ 8, 5 values of t | holds |
| same, dual-gated V_xx and G_ee, h = 5, 7.5, 10 nm, d = 2 nm, k ≤ 5, 7 values of t | holds (not a proof) |
| e_H/e_lat, ρd² = 10⁻³, 10⁻², 0.1, 0.3, 1, 3 | 44.7, 14.2, 4.64, 2.87, 1.87, 1.44 (corrected after Phase 1; independent numpy and Rust sums agree to 9e-14) |
| e_H/e_lat at d = 2 nm, n = 0.1, 0.3, 0.5, 0.75 × 10¹² cm⁻² | 22.4, 13.0, 10.1, 8.3 |
| four-flavour model, n = 0.5 × 10¹² cm⁻², paper's parameters | g_H = 33.5 Ry a_B², μ = 25.6 meV, B_c ≈ 56 mT, II_A → II_B between 40 and 56 mT |
| k_BT_BKT = 1.3ħ²n/m₀ at 0.5 × 10¹² cm⁻² | 5.7 K (paper: ≈ 6 K) |
| rusty-SUNDIALS in-tree Lean | 75 files; `sorry` token in 17, `axiom` in 17, `native_decide` in 13 |
| Lean, QuantumFluids pin (4.34.0-rc2, Mathlib 85e3a25), `exploration/exciton/lean/` | `ExcitonX1.lean`: 5 theorems; `FourFlavour.lean`: 7 named theorems plus helpers; every `#print axioms` ⊆ {propext, Classical.choice, Quot.sound}; no `sorry` token; the negative control fails with the expected `ring` residual (`−g_c` against `+g_c`); verifier pending |
| LeanMaster v3.48.0 contribution, checked here | manifest 1,586 entries: 0 missing, 0 mismatched, 0 extra; token-pattern scan: none; TRI_CMP `COMPARATOR_ACCEPTS`; D1/D1b/D2 axioms standard (their log) |
