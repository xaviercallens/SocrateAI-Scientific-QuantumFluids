# Exciton-fluid Lean files (exploration, not part of the audited library)

Written 2026-10-10 for `docs/designs/EXCITON_FLUID_LEAN_SOLVER_PLAN.md`. Lean 4.34.0-rc2, Mathlib `85e3a25`
(the QuantumFluids pin). **Producer: the session that wrote the plan. Verifier: pending.** Nothing here is cited as
verified until a separate instance has re-checked it (handoff H1: `docs/designs/EXCITON_FLUID_LEAN_HANDOFF.md`).

| file | what | axioms |
|---|---|---|
| `ExcitonX1.lean` | X1 `admissible_sub_shift` (differencing preserves complete monotonicity); `admissible_const_mul`; `bilayerDipole_admissible` (given the Riesz s = 1 case); control `gem4_not_admissible` | standard three |
| `FourFlavour.lean` | the four-flavour mean-field model of Qi et al. (Nature 654, 2026) Eqs. 2–3: T1 `support_in_one_pair`, T2/T3 `IIA_polarisation`, `IIB_polarisation`, `intravalley_density`, T5 `grand_potential_gap`, `critical_field`, T6 `single_component_of_neg_gX` | standard three |
| `FourFlavourNegativeControl.lean` | wrong-sign polarisation; **meant to fail** | — |

Re-run (read-only use of a built Mathlib at the pin; this machine: the OpenAI Navier–Stokes tree, which holds
`85e3a25`), one file at a time, under the heavy lock:

```
cd ~/xdev/OpenAINavierStokesEuler/NavierStokesAndEuler
flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice lake env lean <abs path>/ExcitonX1.lean      # ~20 s
flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice lake env lean <abs path>/FourFlavour.lean    # ~2 min
```

`ExcitonX1.lean` uses a verbatim local copy of upstream's `OAI.TriangularUniversal.AdmissiblePotential`. The files
are statements about a model and about a class of potentials; they are not statements about the experiment, and `g_X`
and `Δ` of the four-flavour model are phenomenological in the paper.
