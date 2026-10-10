# Exciton-fluid Lean files (exploration, not part of the audited library `lean_src/`)

Written 2026-10-10/11 for `docs/designs/EXCITON_FLUID_LEAN_SOLVER_PLAN.md` and the technical note
`paper/exciton_fluid_phase1.tex`. Lean 4.34.1 / Mathlib tag v4.34.1 (`d13f23b7`, the pin of `openai/math`); the first
four files also compile under Lean 4.34.0-rc2 / Mathlib `85e3a25` (the QuantumFluids library's pin until the alignment of
2026-10-11). **Producer: the session that wrote the plan. Verifiers: two separate instances of the same model (not human
review), reports below.**

| file | what | axioms | independent check |
|---|---|---|---|
| `ExcitonX1.lean` | X1 `admissible_sub_shift` (differencing preserves complete monotonicity); `admissible_const_mul`; `bilayerDipole_admissible` (given the Riesz s = 1 case, discharged unconditionally by `VerifierProbe.bilayer_unconditional`); control `gem4_not_admissible` | standard three | `VERIFICATION_BY_INSTANCE_2026-10-10.md`: VERIFIED |
| `FourFlavour.lean` | the four-flavour mean-field model of Qi et al. (Nature 654, 2026; text read: arXiv v1) Eqs. 2–3: T1 `support_in_one_pair`, T2/T3 `IIA_polarisation`, `IIB_polarisation`, `intravalley_density`, T4/T5 `grand_potential_gap`, `critical_field` (equality case; the closed forms are the minima: `VerifierProbe.omegaA_identity`, `omegaB_identity`), T6 `single_component_of_neg_gX`. T4 is not a separate theorem | standard three | same report: VERIFIED WITH REMARKS |
| `FourFlavourNegativeControl.lean` | wrong-sign polarisation; **meant to fail** (and does: `ring` residual `−g_c` vs `+g_c`) | – | same report: VERIFIED as a control |
| `GradientFlow.lean` | the energy is non-increasing along a gradient flow `γ' = −∇f(γ)` (`energy_antitone`); `energy_monotone_ascent` is a *sign control*. The invariant monitored as "L2" in Phase 1 | standard three | same report: VERIFIED |
| `MeanField.lean` | X6 `uniform_minimises` (positive semidefiniteness is a hypothesis); `telescoping_integral`; `bilayer_hartree` (`∫₀^{d²} 2t^{-1/2} = 4d`; the `π` and the limit are not formalised); `variational_lower_bound` (schema) | standard three | same report: VERIFIED WITH REMARKS |
| `TorusBound.lean` | **X4, conditional**: with the first conjunct of upstream's `universal_energy_minimum` as the hypothesis `UniversalEnergyLowerBound` (definitions copied verbatim), `periodic_universal_lower_bound`, `torus_lower_bound_unit`, `torus_lower_bound` (density ρ, potential `g(·/ρ)`), `torus_energy_per_particle`, `admissible_comp_div` | standard three | `VERIFICATION_TORUSBOUND_2026-10-11.md`: VERIFIED WITH REMARKS (conditional on the upstream theorem, which was not checked) |

Each file ends with a `VerifierProbe` section (or, in `TorusBound.lean`, none) written by the verifier and integrated
verbatim: instances showing that hypotheses are satisfiable, counterexamples showing that the genericity/PSD hypotheses cannot
be dropped, and the `rpow` admissibility. `VERIFICATION_RESPONSE_2026-10-11.md` maps every remark to the action taken.

**What is not proved here:** the upstream theorem itself (AI-generated, Comparator-accepted on another machine, unrefereed);
the quantum (expectation) step of the lower bound; Schoenberg/Bernstein (completely monotone ⟹ positive definite); the capacitor
limit; existence of minimisers in the four-flavour model; anything about the experiment or the Rust solver.

Re-run (Lean 4.34.1 environment on the second disk, one file at a time):

```
export ELAN_HOME=/mnt/data/home/xavkal/.elan
cd /mnt/data/xdev-cache/lean-env/qfenv          # lakefile.toml: Mathlib v4.34.1 (d13f23b7)
nice lake env lean <abs path>/ExcitonX1.lean    # ~25 s; likewise GradientFlow, MeanField, TorusBound; FourFlavour ~3 min
```

`ExcitonX1.lean` and `TorusBound.lean` use verbatim local copies of upstream's `AdmissiblePotential` (and, in
`TorusBound.lean`, of the whole definition block). The files are statements about a model and about a class of potentials; they
are not statements about the experiment, and `g_X` and `Δ` of the four-flavour model are phenomenological in the paper.
