# Independent verification of the exciton-fluid Lean files — report of a separate model instance

**Provenance.** This is the report of an independent verifier instance (a subagent of the producer's session, same model
family, Claude Sonnet 5.5). The subagent could not write this file itself (its harness refused a report file), so the
producer's session saved the subagent's report **verbatim** below; only this provenance paragraph was added. Statement-fidelity
judgments are judgments, not proofs, and this is not human review. Where the report recommends changes, the producer's response
is recorded in `exploration/exciton/lean/VERIFICATION_RESPONSE_2026-10-11.md`.

Files covered: `ExcitonX1.lean`, `FourFlavour.lean`, `FourFlavourNegativeControl.lean`, `GradientFlow.lean`, `MeanField.lean`
(not `TorusBound.lean`, which was written later and is verified by a different instance, see
`VERIFICATION_TORUSBOUND_2026-10-11.md`).

---

## 10-LINE SUMMARY

1. NOTE: the requested file VERIFICATION_BY_INSTANCE_2026-10-10.md was NOT written. The harness refused report .md files from this subagent ("return findings as text"), so the full report below is its intended content; please save it.
2. I am a separate instance of the same model (Sonnet 5.5, subagent). This is not human review, and fidelity judgments are judgments, not proofs.
3. All four positive files compile with exit 0 under Lean 4.34.1 / Mathlib d13f23b7 (twice) and under 4.34.0-rc2 / 85e3a25. No Lean warnings, no sorry/native_decide/axiom/unsafe/opaque/implemented_by/set_option, and every #print axioms is {propext, Classical.choice, Quot.sound}.
4. FourFlavourNegativeControl.lean fails as intended in both environments. The residual goal after `ring` is `2gv·b/gX − 2gc·b/gX = 2gv·b/gX + 2gc·b/gX`. The sign-corrected twin compiles.
5. ExcitonX1: `AdmissiblePotential` is text-identical to upstream main (byte-identical to the LeanMaster fd4aeeb2 copy). The `Iff.rfl` guard compiles. The hypothesis is satisfiable (exp(-t), t^(-1/2) proved) and the conclusion is non-vacuous. `hR` of `bilayerDipole_admissible` is dischargeable (proved in a probe).
6. FourFlavour: H and E_i match Eqs. (2)-(3) of arXiv:2603.15443 exactly (I read the PDF). IIA/IIB match the main-text formulas. The paper's Methods line has the opposite sign for II_A (an inconsistency in the paper, not in Lean).
7. FourFlavour hypotheses are consistent (explicit minimisers proved). The genericity hypothesis E_i≠E_j is necessary for both T1 and T6 (explicit counterexamples proved).
8. Remark: `grand_potential_gap` and `critical_field` are pure algebraic identities that never mention H. I proved in a probe that the closed forms are exactly the minima of H on the two pair subspaces. The plan's "II_A is the ground state below B_c" is not in the file.
9. Not proved anywhere: the periodic-extension lemma X4, CM ⟹ PSD on the torus (hU is a hypothesis), the capacitor limit and the π of g_H = 4πd, existence/feasibility of minimisers, any statement about the experiment or the Rust solver.
10. Verdicts: ExcitonX1 VERIFIED; GradientFlow VERIFIED; FourFlavour VERIFIED WITH REMARKS; MeanField VERIFIED WITH REMARKS; NegativeControl VERIFIED as a control (fails as designed).

---

# FULL REPORT (intended content of VERIFICATION_BY_INSTANCE_2026-10-10.md)

## 0. Status
- Verifier: a separate instance of the same model family (Claude Sonnet 5.5, Agent-SDK subagent), spawned by the producer's session. This is an independent machine re-check plus statement-fidelity reading. It is not human review.
- No claim in the file headers was trusted. Every number below comes from logs in `/mnt/data/xdev-cache/lean-env/verify/` (outside the repo). I wrote nothing inside the repo.
- Files verified were byte-identical to the originals at copy time and at the end (sha256):
  - ExcitonX1.lean `968344a7…9264`
  - FourFlavour.lean `758d1aea…6456`
  - FourFlavourNegativeControl.lean `28dce072…3144dd`
  - GradientFlow.lean `248e9faf…ce2`
  - MeanField.lean `8defc6be…1160`
- `TorusBound.lean` appeared in the same directory at 00:00 local (another session). It is out of scope and not verified.

## 1. Environment and commands
- Primary: `lean --version` → `Lean (version 4.34.1, x86_64-unknown-linux-gnu, commit 5045d0056413266e57c625dcd7c365b10e377c52, Release)`.
- Mathlib from `/mnt/data/xdev-cache/lean-env/qfenv/lake-manifest.json`: `d13f23b723b8a846827a245b89c10fc7d3f11612` (tag v4.34.1). Batteries f2effa3d…, aesop 355695d5…, plausible 118aa17e….
- Cross-check: `Lean (version 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d)`, Mathlib `85e3a25e006c35636f0e53b0e9296caca2685bc0`.
- Machine: 8 cores, 31 GB RAM.
- Commands:
  ```
  mkdir -p /mnt/data/xdev-cache/lean-env/verify
  cp <repo>/exploration/exciton/lean/{ExcitonX1,FourFlavour,MeanField,GradientFlow,FourFlavourNegativeControl}.lean /mnt/data/xdev-cache/lean-env/verify/
  export ELAN_HOME=/mnt/data/home/xavkal/.elan
  cd /mnt/data/xdev-cache/lean-env/qfenv && nice -n 5 lake env lean /mnt/data/xdev-cache/lean-env/verify/<File>.lean     # one file at a time
  cd ~/xdev/OpenAINavierStokesEuler/NavierStokesAndEuler && nice -n 5 lake env lean /mnt/data/xdev-cache/lean-env/verify/<File>.lean   # cross-check
  curl -sSL https://raw.githubusercontent.com/openai/math/main/lean/ComparatorChallenges/TriangularEnergy.lean
  curl -sSL https://arxiv.org/pdf/2603.15443 ; pdftotext / pdftoppm (pages 5, 6, 10 read as images)
  ```
- grep for `sorry|native_decide|axiom|unsafe|opaque|implemented_by|set_option|macro|elab|syntax|notation|instance|attribute|partial|decide`: no hits other than `noncomputable def` and docstring mentions of "Classical.choice". I also read all five files in full.
- Incident (not a file defect): my first attempt at 21:15 UTC failed for all five files with `object file '…/batteries/…/Batteries/Data/Array/Scan.olean' … does not exist`.
  - Cause: another session's `lake update && lake build` in `/mnt/data/xdev-cache/lean-env/qf_lib` (its `packagesDir` points at qfenv's packages) was rebuilding the shared packages.
  - Logs are kept as `*.attempt0_env_error.log`. The official runs below were made after the packages were consistent again.
  - The machine was thrashing during pass 1 (load average 20–27, page-cache eviction), so pass-1 wall times are inflated. Pass 2 ran at load ≈ 8.

## 2. Results

| file | compiled, primary env (exit; wall pass 1 / pass 2) | cross-check env (exit; wall) | `#print axioms` | forbidden constructs | Lean warnings |
|---|---|---|---|---|---|
| ExcitonX1.lean | yes (0); 428 s / 26 s | yes (0); 182 s | 5/5 theorems ⊆ std3 | none | none |
| FourFlavour.lean | yes (0); 294 s / 167 s | yes (0); 322 s | 7/7 named theorems ⊆ std3; 8 helper lemmas printed by my probe ⊆ std3 | none | none |
| MeanField.lean | yes (0); 130 s / 29 s | yes (0); 52 s | 4/4 ⊆ std3 | none | none |
| GradientFlow.lean | yes (0); 77 s / 28 s | yes (0); 59 s | 2/2 ⊆ std3 (+ `deriv_energy` via probe) | none | none |
| FourFlavourNegativeControl.lean | NO (exit 1, intended); 26 s / 17 s | NO (exit 1); 72 s | n/a | none | n/a |

- std3 = {propext, Classical.choice, Quot.sound}. No `sorryAx` appears anywhere in the producer's files.
- Theorem lists:
  - ExcitonX1: `antitone_signed_iteratedDeriv`, `admissible_sub_shift`, `admissible_const_mul`, `bilayerDipole_admissible`, `gem4_not_admissible`.
  - FourFlavour: `support_in_one_pair`, `IIA_polarisation`, `IIB_polarisation`, `intravalley_density`, `grand_potential_gap`, `critical_field`, `single_component_of_neg_gX`.
  - MeanField: `uniform_minimises`, `telescoping_integral`, `bilayer_hartree`, `variational_lower_bound`.
  - GradientFlow: `energy_antitone`, `energy_monotone_ascent`.
- The one first-pass cross-check negative-control run was aborted by me (SIGTERM at 1265 s, page-cache thrash). The re-run gave exit 1 as shown.

## 3. Statement fidelity

### 3.1 ExcitonX1.lean
- **Definition.**
  - `ExcitonX1.AdmissiblePotential` is text-identical to upstream's `OAI.TriangularUniversal.AdmissiblePotential` (python diff of the definition block).
  - My downloaded `main` copy has sha256 `af51979c…0616`, byte-identical to the LeanMaster-pinned copies under `upstream/openai-math-fd4aeeb2/…` and `…/LT_D/lock_root/…`.
  - A probe built from the upstream file text plus ExcitonX1 compiles `example (g) : ExcitonX1.AdmissiblePotential g ↔ OAI.TriangularUniversal.AdmissiblePotential g := Iff.rfl`. It also transfers `admissible_sub_shift` to the upstream predicate. All std3.
  - `(⊤ : ℕ∞)` in `ContDiffOn` is C^∞ (not analytic), as intended.
- **`admissible_sub_shift`.**
  - Says what its docstring says: g admissible and c>0 give `t ↦ g t − g(t+c)` admissible.
  - Hypothesis satisfiable: probes prove `exp(-t)` and `t^(-1/2)` admissible (the latter via `Real.iter_deriv_rpow_const` and an induction on the sign of `descPochhammer ℝ k` at −1/2).
  - Conclusion non-vacuous: for g = exp(−t) and c = 1 it gives an admissible function with value e⁻¹−e⁻² > 0.
  - The predicate has negative instances: the constant −1, and `gem4_not_admissible`.
  - c>0 is needed: for c<0 and g = exp(−t), g(t)−g(t+c) < 0.
- **`gem4_not_admissible`.** True by hand: (exp(−t²))'' = (4t²−2)e^{−t²}, which is −e^{−1/4} < 0 at t = 1/2. The control fails only at r = 2.
- **`bilayerDipole_admissible`.**
  - The model: bilayerDipole(d)(t=r²) = 2[1/r − 1/√(r²+d²)]. This is e–e + h–h repulsion minus 2 e–h attraction in units e²/4πε₀ε = 1, which is right.
  - Conditional on `hR : AdmissiblePotential (riesz 1)`. My probe proves `riesz 1` admissible and `bilayerDipole 1` admissible unconditionally, Mathlib only.
  - `TriangularRiesz.riesz_admissible` cited in the docstring was not found on disk by me. The probe makes it unnecessary for s = 1.

### 3.2 FourFlavour.lean (vs arXiv:2603.15443v1, read from PDF pp. 5–6 and Methods p. 10)
- **Eq. (2).** H = Σ(E_i−μ)n_i + (g_H+g_X)/2 (Σn_i)² − g_X(n₁n₂+n₃n₄). Lean `H` matches, with indices 1..4 ↦ 0..3 and pairs (0,1), (2,3).
- **Eq. (3).** E₁=(−g_c+g_v)μ_B B−Δ, E₂=(+g_c−g_v)μ_B B−Δ, E₃=(−g_c−g_v)μ_B B, E₄=(+g_c+g_v)μ_B B. Lean `Eflav gc gv b Δ = ![(gv−gc)b−Δ, −(gv−gc)b−Δ, −(gc+gv)b, (gc+gv)b]` matches. Flavour order KK, K'K', KK', K'K matches.
- **Polarisations.**
  - Main text: II_A n₂−n₁ = 2(g_v−g_c)μ_B B/g_X; II_B n₃−n₄ = 2(g_c+g_v)μ_B B/g_X. Lean `IIA_polarisation` (n1−n0) and `IIB_polarisation` (n2−n3) match.
  - Methods p. 10: the Ginzburg–Landau line carries −(g_v−g_c)μ_B B(n₁−n₂) and states n₁−n₂ = 2(g_v−g_c)μ_B B/g_X. This is the opposite sign for II_A relative to Eq. (3) and the main text. With Eq. (3) as printed the stationarity condition gives n₂−n₁ = +2(g_v−g_c)μ_B B/g_X, which is what Lean proves.
  - So the paper (v1) is internally inconsistent in the Methods for II_A; Lean follows Eq. (2)–(3) and the main text.
- **Density.** Methods n₁+n₂ = (μ+Δ)/(g_H+g_X/2) equals Lean `intravalley_density` with E₀+E₁ = −2Δ.
- **Closed forms.** Ω_A = −(μ+Δ)²/(2g_H+g_X) − ((g_v−g_c)b)²/g_X and Ω_B = −μ²/(2g_H+g_X) − ((g_c+g_v)b)²/g_X. Hand derivation and the probes confirm them as the minima of H on the two pair subspaces.
- **Critical field and the paper's ~50 mT.**
  - The formula b² = g_X Δ(2μ+Δ)/(4g_c g_v(2g_H+g_X)) with the paper's parameters (g_H=8π, g_X=1, Δ=1 μeV, Ry=66.64 meV, a_B=1.543 nm) gives B_c = 36, 44, 51, 57 mT at n_x = 0.2, 0.3, 0.4, 0.5×10¹² cm⁻².
  - This is consistent with the paper's "energy crossing at ~50 mT" (ED Fig. 7c), though the density used there is not stated.
- **Theorem-by-theorem.**
  - `support_in_one_pair` (g_X>0, E_i≠E_j across pairs, n global minimiser on the orthant ⟹ support inside {0,1} or {2,3}) is correct and non-trivial. By hand: the second difference along (ε,ε,−2ε,0) etc. is −2g_Xε² < 0, and the first-order condition forces E_i = E_j for cross-pair two-supports.
  - Hypotheses are consistent: probe `nw_minimiser`/`witness_T1` applies the actual theorem to g_H=g_X=μ=1, E=(0,0,1,1), n=(1/3,1/3,0,0).
  - Caveat: if 2g_H+g_X ≤ 0, H is unbounded below and the theorem is vacuous there (no minimiser).
  - The hypothesis `hE` fails exactly on the four lines Δ = ±2g_v b and Δ = ±2g_c b of the (b,Δ) plane (b=μ_B B); for Δ=1 μeV, g_v=6, g_c=3 that is B ≈ 1.4 mT and 2.9 mT. The theorem is silent there ("generic case").
  - `single_component_of_neg_gX` is correct and non-vacuous: probe `nsc_minimiser`/`witness_T6` with g_H=2, g_X=−1, μ=1, E=(0,0,1,1), n=(1,0,0,0).
  - `IIA_polarisation`, `IIB_polarisation`, `intravalley_density`: hypotheses are the stationarity equations ∂H/∂n_i = 0 at a point with the other pair at 0.
    - They are jointly satisfiable for all parameters with g_X≠0 and 2g_H+g_X≠0 (probe `IIA_hyps_satisfiable`).
    - They are not derived from minimality and assert no n≥0 or phase membership; this is stated in the section header only.
  - `grand_potential_gap`: a rational-function identity, true. It never mentions H (see §6).
  - `critical_field`: a correct equivalence (equality case only), with non-contradictory hypotheses.
- **Header wording.** The header says `support_in_one_pair`, `critical_field` and `single_component_of_neg_gX` are "not printed in the arXiv v1 main text". The paper does print qualitative forms: Methods "no more than two flavors condense simultaneously", and main text "negative g_X leads to a ferromagnetic single-component condensate". The Lean statements are the rigorous (and, for T1, sharper: exchange-pair structure) versions. The `critical_field` formula is not printed.

### 3.3 MeanField.lean
- **`uniform_minimises`.**
  - States E[uniform with the same total mass] ≤ E[n] for every real n on a finite abelian group, given the whole quadratic form of U is PSD.
  - Satisfiable: probe `hU_indicator` (U = indicator of 0, any finite abelian group incl. ZMod n) and `uniform_minimises_instance` (the Cauchy–Schwarz case).
  - Not removable: on Fin 2 = ZMod 2 with U(0)=0, U(1)=1, `Ubad_not_psd` holds (f=(1,−1) gives −2). For n=(1,0) the uniform energy is 1/2 > 0, so the conclusion is false (`conclusion_fails_for_Ubad`).
- **`telescoping_integral`.** The identity is right and its hypothesis is satisfiable (probe `telescoping_instance` with g = 2t^(−1/2), via `intervalIntegrable_rpow'`).
- **`bilayer_hartree`.** ∫₀^{d²} 2t^(−1/2) dt = 4d for d>0 is right (d>0 needed; otherwise 4|d|). The docstring's "i.e. g_H = 4πd" additionally needs the polar-coordinate factor π and the R→∞ limit (g→0), neither of which is in Lean. The units remark is consistent with the paper: 4πd in e²/4πε₀ε=1 is 8πd in Rydberg units.
- **`variational_lower_bound`.** Correct but is just monotonicity of the integral for a probability measure. No quantum mechanics is encoded; the docstring does call it a schema.

### 3.4 GradientFlow.lean
- **`energy_antitone`** says what it claims, with hypotheses on all of ℝ. The instance is proved in a probe: f = x²/2 on ℝ, γ = exp(−t), `gradient_flow_instance`. `energy_monotone_ascent` also has an instance (`ascent_instance`).
- **Scope.** It is about exact flows defined for all t∈ℝ. Numerical CVODE solutions, finite intervals and the Rust code are not covered; the docstring says a numerical solution "may violate it only by its tolerance". `energy_monotone_ascent` is a theorem about the opposite sign, not a failing check.

## 4. Negative control
Primary env, exit 1:
```
FourFlavourNegativeControl.lean:15:40: error: unsolved goals
h : n1 - n0 = ((gv - gc) * b - Δ - (-(gv - gc) * b - Δ)) / gX
⊢ gv * b * gX⁻¹ * 2 - gc * b * gX⁻¹ * 2 = gv * b * gX⁻¹ * 2 + gc * b * gX⁻¹ * 2
```
- It is preceded by `ring`'s "Try this: ring_nf / The `ring` tactic failed to close the goal".
- `ring` falls back to `ring_nf` and the `by` block ends with unsolved goals. That is the expected failure and it is the sign of g_c.
- `field_simp; linarith`, `simp only` and `rw [h]` all succeed.
- Same in the older env and in pass 2.
- Twin: the identical script with only `+ gc` → `− gc` in the statement compiles (exit 0, std3). The failure is attributable to the flipped sign alone.
- Remark: the control retypes `Eflav` locally (it does not import FourFlavour), so it would not notice a change in the real `Eflav`.

## 5. Attempts to break things (machine-checked in probes, all std3 unless stated)
Probe files are in `/mnt/data/xdev-cache/lean-env/verify/probes/`.
- X1: `exp_neg_admissible`, `rpow_neg_half_admissible`, `riesz1_admissible`, `bilayer_unconditional`, `sub_shift_nonvacuous`, `neg_one_not_admissible`, `local_iff_upstream`, `upstream_sub_shift`. The only Lean warning anywhere is `declaration uses sorry` for the downloaded upstream challenge theorem `universal_energy_minimum` in the concatenated probe. It is the external hypothesis, unused by ExcitonX1 and not in the producer's files.
- FourFlavour:
  - `hE_needed`: E=(0,10,0,10), g_H=g_X=μ=1, n=(1/4,0,1/4,0) is a global minimiser spanning both pairs, so T1's genericity hypothesis cannot be dropped.
  - `hE_needed_T6`: E=(0,5,0,5), g_H=2, g_X=−1, μ=1, n=(1/2,0,1/2,0) is a global minimiser with two nonzero components, so the genericity hypothesis cannot be dropped from T6 either.
  - `omegaA_identity` and `omegaB_identity`: H on the pair subspaces equals Ω + (2g_H+g_X)/4(Δs)² + g_X/4(Δd)². The closed forms in `grand_potential_gap` are exactly the minima for g_X>0, 2g_H+g_X>0.
- MeanField and GradientFlow: instances and counterexamples as in §3.3–3.4.
- Independent numerics (numpy, `verify/numerics/check_model.py`, not Lean):
  - T1: 1977 random parameter sets with g_X>0; supports of the exact minimiser (face enumeration) lie in one pair in all cases, 0 violations.
  - T6: 1485 random sets with g_X<0; all single-component.
  - Ω_A closed form vs H at the stationary point: max error 1.8e-15 over 1808 feasible samples.
  - The numeric critical-field values of §3.2.

## 6. What is NOT proved (do not over-read the files)
- The periodic-extension lemma (plan item X4) and the torus lower bound C1.
- CM ⟹ positive definite (Schoenberg/Bernstein) and its periodised/discretised version. `hU` in `uniform_minimises` is a hypothesis.
- The capacitor limit Ũ(0) = π∫₀^{d²}g (polar-coordinate π, R→∞, g→0). Only the finite integral identities are proved.
- The upstream theorem `universal_energy_minimum` itself (the downloaded upstream file has it as a `sorry` challenge statement). ExcitonX1 uses only the definition; any corollary inherits upstream's status.
- In the four-flavour model:
  - existence of minimisers;
  - feasibility (n ≥ 0) of the closed-form phase solutions;
  - that H on the pair subspaces has the closed-form minima (not in the file; my probe proves it);
  - the plan's "II_A is the ground state below B_c" (only the equality is proved);
  - derivation of the stationarity equations from minimality;
  - the plan's T4 as a separate theorem.
- Anything about the experiment: g_X and Δ are phenomenological in the paper. Anything about the Rust/CVODE solver, or numerical solutions satisfying the L2 monitor.
- That `energy_antitone` applies to the Phase-1 flows. The theorem is for any Euclidean gradient flow on all of ℝ, and the ψ-flow of the four-flavour prereg is of that form with f = H(ψ²)/2, but that bridge is not in Lean.

## 7. Statements I would change (the handoff asks for this)
1. FourFlavour header: replace "not printed in the arXiv v1 main text" with "the paper prints qualitative versions; the exchange-pair structure and the critical-field formula are not printed". Also "Nature 654, 2026" could not be confirmed from the arXiv listing (v1, 16 Mar 2026, no journal-ref field).
2. `grand_potential_gap`: add "rational-function identity; H is not involved" to the docstring, or add the two Ω-identities from my probe.
3. `critical_field`: say "Ω_B − Ω_A = 0 iff …" (equality only).
4. `IIA/IIB_polarisation`, `intravalley_density`: add "hypotheses are the stationarity equations; no feasibility asserted".
5. MeanField header: "i.e. g_H = 4πd" is a prose step (π and a limit).
6. ExcitonX1 docstring: "interlayer excitons separated by d" should read "layers separated by d; in-plane separation r = √t".
7. Optionally add `rpow_neg_half_admissible` (probe) to remove the assumption `hR`.
8. GradientFlow: call `energy_monotone_ascent` a "sign control", not a negative control.
9. Mention the four lines Δ = ±2g_v b, ±2g_c b where `support_in_one_pair` does not apply.
10. README: T4 is not a separate theorem.

## 8. Verdicts
- **ExcitonX1.lean: VERIFIED.** Compiles in both environments with std3 axioms; definition identical to upstream and `Iff.rfl` guard compiles; statements mean what they say; hypotheses satisfiable and conclusions non-vacuous. Only caveat: `bilayerDipole_admissible` is conditional on `hR`, discharged by my probe.
- **GradientFlow.lean: VERIFIED.** Statements correct and instantiable; scope limited to exact flows on ℝ.
- **FourFlavour.lean: VERIFIED WITH REMARKS.**
  - The model matches the paper's Eqs. (2)–(3) and the printed formulas; all seven theorems are kernel-checked, std3, and non-vacuous.
  - Remarks: the header sentence in §7(1); the closed-form/H link and T5 inequality are outside the file; polarisation and density results are conditional on stationarity; T1/T6 need genericity, which fails on four lines of the (b,Δ) plane.
- **MeanField.lean: VERIFIED WITH REMARKS.**
  - Correct and non-vacuous.
  - Remarks: PSD is a hypothesis (CM ⟹ PSD not proved); "g_H = 4πd" needs π and a limit; the variational statement is a pure schema.
- **FourFlavourNegativeControl.lean: VERIFIED as a control.** Fails with the expected sign-of-g_c ring failure in both environments; the corrected twin compiles.

## 9. Limitations of this verification
- Same model as producer: shared blind spots are possible.
- The Lean kernel acceptance and `#print axioms` are the load-bearing evidence.
- My paper reading is of arXiv v1 only; the published version was not consulted.
- I could not locate `TriangularRiesz.riesz_admissible` on disk, so the docstring's pointer is unverified.
- A heavily loaded, concurrently rebuilt environment was used; results were reproduced in a second pass and in a second environment.

Artifacts (outside the repo): `/mnt/data/xdev-cache/lean-env/verify/{*.log, probes/, numerics/check_model.py, upstream_dl/TriangularEnergy.lean, arxiv_dl/qi.txt}`.
