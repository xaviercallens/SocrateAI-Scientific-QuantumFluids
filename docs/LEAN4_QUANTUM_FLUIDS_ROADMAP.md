# A Lean 4 formalization roadmap for quantum fluids

*What to build next, and what each of three existing Lean 4 developments can actually contribute.
Every claim about another tree below was checked against its files on 2026-09-21, not taken from its
README or from memory. Where something is not there, this says so.*

Status of this library at the time of writing: 136 theorems, 16 modules, Lean 4.34.0-rc2, Mathlib
`v4.34.0-rc2`, footprint `{propext, Classical.choice, Quot.sound}`, no `sorry` in any default target.

---

## 1. The three sources, honestly assessed

### 1.1 OpenAI `NavierStokesAndEuler` — already a dependency

| | |
|---|---|
| Toolchain | Lean 4.34.0-rc2 — **identical to ours**, which is the only reason an import works |
| Status here | Lake dependency pinned at `8937a8f…`; `MadelungNSE` imports `NavierStokes.ProblemStatement` |
| Licence | Apache-2.0 |

**Takes.** The PDE *vocabulary*: their definitions of spatial derivatives, divergence, Laplacian,
smoothness classes, and the periodic (torus) setting. `MadelungNSE.divergence_madelungVelocity` is
stated in their definitions, so a reader of their development can read ours without translation.

**Does not give.** Anything about Schrödinger-type or dispersive equations, complex order parameters,
vortices, or quantization. Their analytic machinery is built for one construction and is not a general
PDE library; importing more than `ProblemStatement` buys compile time, not theorems.

**Next concrete target (T3 below):** the Gross–Pitaevskii residual written in their vocabulary, parallel
to their Navier–Stokes residual, and the Madelung correspondence as a theorem *between the two
residuals* — not just between the velocity fields, which is what we have now.

### 1.2 Anthropic, *Fermat's Last Theorem in Lean 4* — a quarry, not a dependency

Vendored under `SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/anthropics-flt`
(upstream `github.com/anthropics/fermats-last-theorem`, single commit `aa2d8b3`, 2026-09-03,
`NOTICE`: "Copyright 2026 Anthropic, PBC", Apache-2.0; `README`: "Research artifact. Not maintained and
not accepting contributions."). The sibling directory `xaviercallens-xflt` is **byte-identical**
(`diff -rq` empty) — it is a mirror, not a second source, and must not be counted twice.

Attribution, because it is easy to get wrong: this is Anthropic's repository, and it is *not* a fork of
the Imperial College FLT project — but it vendors 104 files derived from that project (Buzzard and
contributors) plus flt-regular and Mathlib text, listed file by file in its `ATTRIBUTION.md`. Anything
ported from it must carry that attribution through.

| | |
|---|---|
| Toolchain | Lean **4.33.1**, Mathlib `db584cd…` — **one release behind ours; cannot be a Lake dependency** |
| Size | 60,478 `.lean` files, 13.5 M lines, 1.9 GB; 0 `axiom`, `sorry` only in the Comparator challenge file |
| Verification | `FinalCheck.lean` guards the axiom footprint; Comparator config present (documents ~15 h, ~230 GB RSS) |

It is a number-theory development, and most of what sounds relevant is not:

| Sounds relevant | What it actually is | Use to us |
|---|---|---|
| "winding" | modular-symbol winding elements (`Def_AutomorphicForm_WindingDatum`) | **none** — not the topological winding number |
| zeta, Gamma, Mellin | archimedean L-factors, Tate / Langlands–Tunnell | **none** — `riemannZeta` occurs in one file |
| Schwartz space | Schwartz–Bruhat (locally constant, p-adic) | **none** |
| Haar measure | adelic / topological rings | **none** |
| PDE, Laplacian, distributions, Lagrange inversion | — | **not found** |

Three items are genuinely general analysis, sorry-free, and absent from Mathlib in this form:

1. **Fourier inversion on the n-torus** —
   `MeasureTheory.hasSum_fourierCoeff_pi_mul_cexp_of_continuous_of_periodic_of_summable`:
   for continuous 1-periodic `F : (Fin c → ℝ) → ℂ` with summable Fourier-coefficient norms, the Fourier
   series `HasSum` to `F θ` pointwise. *This is the missing bridge between `GPGalerkin` (algebra on a
   finite mode set) and a field on the periodic box.*
2. **Sobolev sup-norm bound on a cube** —
   `Sobolev.exists_forall_norm_le_mul_sum_sqrt_integral_norm_iteratedFDeriv_sq_of_contDiff_box`:
   `‖f x‖ ≤ c · Σ_{k≤n} √∫_box ‖D^k f‖²`. *This is what turns an energy bound into a pointwise bound —
   in particular, a bound that keeps |ψ| away from zero, i.e. keeps the Madelung transform defined.*
3. **L² kernel operators with the Schur bound** —
   `Def_Mathlib_MeasureTheory_Function_L2KernelOperator`. Relevant to nonlocal interaction terms
   (dipolar condensates, the nonlocal helium models); lowest priority.

**Porting cost, stated plainly.** The theorem files end in `by p2m_exact_reverting @P2MW.S_…`: the
proofs live in machine-generated `P2M/Sol/` files and depend on `P2M/Util.lean`. A port is therefore
"copy the statement, the `Sol` file and whatever it transitively needs, re-prove what breaks on
4.34" — for item 1 the solution file is ~130 lines, for item 2 ~370. Gate before starting: build the
candidate file standalone against our Mathlib pin and count the failures. If item 1 needs more than a
day, prove it directly from Mathlib's `AddCircle` Fourier theory instead and cite theirs as prior
formalization.

**Methodology worth copying now (no port needed):** `formalization.yaml` (machine-readable statement
of what is claimed), `ATTRIBUTION.md` per-file provenance, and `FinalCheck.lean` — a single file whose
`#guard_msgs` on `#print axioms` makes the footprint a *build failure* rather than a convention. Ours is
a script (`regen_axiom_audit.py --check`); theirs is stronger because it cannot be skipped.

### 1.3 LeanMaster — process, and one tool

`SocrateAI-Scientific-Agora-LeanMaster` (Lean 4.33.1) formalizes double field theory and moonshine
arithmetic; there is no shared mathematics with quantum fluids. What transfers:

- **The tier ledger** — Tier A (kernel-checked) / Tier L (literature) / Tier C (own conjecture), with the
  rule that a Tier-A claim may depend only on Tier-A claims. Our `LEDGER.md` has the content but not the
  tiers; adding them would make §6 of the paper checkable line by line.
- **The tactic-position-aware `sorry` grep** (its `README` §10) — a plain substring search is wrong, as
  it notes; ours is a plain search plus the build. Adopt theirs.
- **`leangraph`** — dependency DAG extraction. **Known defect, reported, not yet fixed upstream:** it
  counts `#print axioms X` lines as dependencies on `X`, which on this library produced 88 spurious
  edges and a false cycle; with those lines stripped the graph has 64 edges and is a DAG. Use only with
  audit blocks stripped until fixed.
- **External rebuild** — the single most productive verification step in this project's history was a
  LeanMaster reviewer rebuilding our tag from a clean clone (two real defects). Keep it as a release gate.
- An **MCP server was looked for and not found** in that repository. If one exists elsewhere it has not
  been evaluated, and nothing here depends on it.

---

## 2. Targets, in order

Ordering rule: a target ranks higher if an experimentalist or a simulation author could *use* the
theorem, and lower if it only restates known mathematics more formally. Each target has a literature
gate (run first — see `RETRACTIONS.md` for why) and a kill criterion.

| # | Target | Builds on | Leverages | Kill criterion |
|---|---|---|---|---|
| **T1** | **Sampling theorem for vortex detection**: for a C¹ phase on a loop, if every sampled step is `< π` then the discrete `pdiff` sum equals the continuum circulation | `VortexWinding`, `QuantizedCirculation` | Mathlib only; (ATLAS has the continuum winding number is an integer, on 4.29 — cite, don't import) | if the hypothesis needed is a modulus-of-continuity bound nobody can check on data, state that and stop |
| **T2** | **Conservation along solutions** of truncated GP: upgrade `GPGalerkin` rate identities to `d/dt N = 0`, `d/dt E = 0` for a solution of the ODE | `GPGalerkin` | Mathlib ODE / `HasDerivAt`; the pattern of `MadelungSplit.hasDerivAt_line` | none expected — this is routine and overdue |
| **T3** | **GP residual in the NSE vocabulary**, Madelung correspondence between residuals | `MadelungNSE`, `MadelungSplit` | **OpenAI NSE** `ProblemStatement` | if their residual definition bakes in incompressibility in a way that cannot host a density, report the obstruction — that is itself a finding about the two formalisms |
| **T4** | **From modes to fields**: a finite Galerkin state defines a continuous periodic field whose Fourier coefficients are the modes | `GPGalerkin` | **FLT item 1** (torus Fourier inversion), or Mathlib `AddCircle` | port gate above |
| **T5** | **Madelung stays defined**: an energy bound gives `inf |ψ| > 0` on a cube for small enough data | `MadelungSplit` | **FLT item 2** (Sobolev sup bound) | if the constant is non-explicit (it is: `∃ c`), the result is qualitative only — say so in the statement's docstring |
| **T6** | **Asymptotic validity of the phonon series**: the term-by-term `C_V` of `PhononSpecificHeat` is an asymptotic expansion of the integral with a dispersion that agrees with the series to `O(k⁸)` | `PhononSpecificHeat` | Mathlib asymptotics; Watson's lemma is **not** in Mathlib — check before starting | if it needs Watson's lemma in generality, that is a Mathlib contribution, not a project target; scope to polynomial-times-Bose only |
| T7 | Roton contribution to `C_V` (Landau's `e^{-Δ/T}` form with its prefactor) | `BoseIntegral` | Gaussian integrals in Mathlib | literature gate: textbook result, value is only in completing [G21] §VI |
| T8 | Kelvin's theorem / Onsager–Feynman for the Madelung fluid away from zeros of ψ | T3, T5 | NSE vocabulary | needs line integrals of time-dependent fields; defer until T3 lands |

**Closed since the last roadmap:** the six coefficients of Godfrin et al. Eq. (22)
(`docs/designs/PHONON_SERIES_A_TO_L.md`).

**Explicitly not targets.** Anything whose statement is "quantum fluids exhibit a new length/scale/
invariant". Three such proposals were made in this project; all three were retracted (R1, R2) or refuted.
The library's value is checking what others state, not generating statements.

---

## 3. Infrastructure changes to make first (cheap, each under an hour)

1. `FinalCheck.lean` with `#guard_msgs` on the footprint of the headline theorems (pattern from FLT).
2. Tier column in `LEDGER.md` (pattern from LeanMaster).
3. `formalization.yaml` at the repository root.
4. Generated files carry a header naming their generator, and CI-equivalent check that regenerating is a
   no-op (`PhononSeries.lean` is the first generated proof file in the tree).
