# Pre-registration: kinetic benchmark (K1–K4), zero sound (H5), TDA instruments (D0, D1, D3)

**Written and committed BEFORE any of the code below exists or any number is computed.** The commit that
adds this file contains no solver, no result and no figure; `git log` is the evidence. Amendments go in
§9 with a date and a reason, never by editing a criterion in place. A void run stays void.

Approved scope (owner, 2026-09-21: "implement"): proposal `KINETIC_TOOL_AND_TDA_PROPOSAL.md` with its
recommended options — code in this repository, TDA items D0 + D1 + D3, D2 not attempted.

Literature gates for both halves are running in parallel and have **not** reported at the time of
writing. Their outcome can strike an item or change how it is *described*; it cannot change a
criterion below.

Units throughout the kinetic part: ω_p = v_th = λ_D = 1. Maxwellian f₀(v) = e^{−v²/2}/√(2π).

## 1. K1 — certified Landau root

- **Object.** D(ω,k) = 1 + k⁻²[1 + ζ Z(ζ)], ζ = ω/(√2 k), Z(ζ) = i√π e^{−ζ²} erfc(−iζ) (entire).
- **Method.** Arb ball arithmetic (`python-flint`). Interval-Newton: for a ball B ∋ m, if
  N(B) = m − D(m)/D′(B) ⊂ interior(B) then B contains exactly one zero. Z′ = −2(1 + ζZ).
- **Known answer.** Literature value at k = 0.5: ω ≈ 1.4156, γ ≈ −0.1533.
- **Pass.** A certified ball of radius ≤ 10⁻³⁰ whose midpoint rounds to those four-digit values.
- **Negative control (must fail).** The same test on a ball of radius 10⁻³ centred at
  1.4156 − 0.1433i (γ off by 0.01) must **not** certify a root.
- Also tabulate k = 0.3, 0.4 for use by K2.

## 2. K2 — Vlasov–Poisson solver

- **Scheme.** Strang splitting; x-advection by exact Fourier shift; v-advection by periodic-in-x,
  cubic-spline-in-v semi-Lagrangian interpolation; Poisson by FFT, zero mean field.
- **Run A.** f = (1 + 0.01 cos kx) f₀, k = 0.5, L = 4π, N_x = 64, N_v = 256, v_max = 6, Δt = 0.1.
  γ from a least-squares line through the local maxima of ln|E₁(t)| with 5 ≤ t ≤ 25; ω from the mean
  spacing of those maxima (spacing = π/ω).
  **Pass:** |γ − γ_K1| ≤ 2 % of |γ_K1| and |ω − ω_K1| ≤ 1 %.
- **Run B (discrimination).** Same at k = 0.4, L = 5π. Must match the k = 0.4 root by the same criteria
  **and** miss the k = 0.5 root by more than 20 %. A check that cannot tell two wavenumbers apart is not
  a check.
- **Run C (recurrence — a control that must *show the defect*).** Run A with N_v = 32
  (Δv = 0.375, T_R = 2π/(kΔv) = 33.51). **Pass:** the largest maximum of |E₁| in 25 < t < 45 lies within
  5 % of 33.51 and exceeds 10 % of |E₁(0)|.
- Conservation in Run A to t = 50: mass drift < 10⁻¹⁰ relative; total energy drift reported (no
  threshold — splines are not energy-conserving, and I do not know the number in advance).

## 3. K3 — plasma echo

Pulses as multiplicative density perturbations: mode k₁ at t = 0, mode k₂ at t = τ. k₀ = 0.5,
k₁ = k₀, k₂ = 3k₀, echo mode k₃ = k₂ − k₁ = 2k₀ = 1.0, τ = 10, amplitudes 0.01 each,
N_x = 64, N_v = 512, v_max = 6, Δt = 0.05.
**Predicted echo time t_e = τ k₂/(k₂ − k₁) = 15.0.**

- **K3a, field off (exact known answer).** Free streaming gives, to second order,
  ρ̂_{k₃}(t) = (α₁α₂/2)·exp(−[(k₂−k₁)t − k₂τ]²/2) for the cosine amplitude (derivation in the module
  docstring; the Gaussian is f̂₀). **Pass:** max over 10 ≤ t ≤ 20 of |measured − formula| ≤ 10⁻³ × peak.
  If the prefactor convention is off by a factor of 2 that is a derivation error of mine and will be
  reported as such, not absorbed.
- **K3b, field on.** **Pass:** time of max |ρ̂_{k₃}| in 10 < t < 25 within 5 % of 15.0. Amplitude: no
  prediction (collective shielding changes it; I do not know by how much).
- **Negative control.** With the second pulse omitted, |ρ̂_{k₃}| in 12 ≤ t ≤ 18 must stay below 1 % of
  the K3a peak.

## 4. K4, H5 — Lean (non-default target until proved; then default)

- **K4 `phase_mixing`.** For integrable g : ℝ → ℂ and k ≠ 0, t ↦ ∫ g(v) e^{−ikvt} dv → 0 as t → ∞
  (from Mathlib's Riemann–Lebesgue lemma). Plus: f(t,x,v) = e^{ik(x−vt)} g(v) solves ∂ₜf + v∂ₓf = 0;
  and the Maxwellian closed form e^{−k²t²/2}.
- **H5 `zero_sound_iff`.** With g(s) = (s/2)·ln((s+1)/(s−1)) − 1: ∃ s > 1, g(s) = 1/F ⟺ F > 0.
  Uniqueness (strict monotonicity) is a stretch goal, not promised.
- Standard axiom footprint, Comparator, and one negative control each (K4: drop `k ≠ 0`; H5: replace
  `F > 0` by `F ≥ 0`) that must fail to compile.

## 5. D0 — duality control for the TDA pipeline

- **Claim to reproduce (a theorem, nothing to discover).** For a function on a closed surface, finite
  H₀ sublevel pairs (b, d) of ρ correspond to finite H₁ sublevel pairs (−d, −b) of −ρ.
- **Test field.** A smooth random periodic 128² field (fixed seed), and one |ψ|² frame of the existing
  2D GP run. GUDHI `PeriodicCubicalComplex`.
- **Prediction P-D0a.** Using *dual* cubical constructions on the two sides (top-cells for ρ, vertices
  for −ρ), the multisets agree exactly (max bottleneck distance < 10⁻¹²).
- **Prediction P-D0b (the control's control).** Using the *same* construction on both sides they do
  **not** agree exactly — the two sides then use different pixel connectivities. If P-D0b "fails" (they
  agree anyway) I have misunderstood the constructions and D1/D3 are suspended until I understand why.
- The precise statement is being checked by the literature gate; if it says the correspondence needs
  padding or differs on the torus, that is recorded as an amendment *before* D1/D3 are run.

## 6. D1 — density-only vortex detection

- **Honest description.** H₀ sublevel persistence of a minimum *is* its depth below the merge saddle
  — prominence again. Nothing here is new mathematics. The deliverable is a **measured error rate**
  against ground truth that experiments cannot access (phase winding), for a detector with no tunable
  blob scale.
- **Data.** Own 2D GP solver, ξ/Δx = 8, the decaying-turbulence configuration already used
  (`run_own_gpe.py`), frames at t = 5, 10, 20.
- **Detector (fixed now).** H₀ sublevel class of ρ/n₀ with birth < 0.1 and persistence > 0.5; located
  at its birth cell. Matched one-to-one (Hungarian) to winding vortices within 1.0 ξ.
- **Criteria.** "Usable": precision ≥ 0.95 **and** recall ≥ 0.90 on the pooled frames.
- **Prediction.** Precision passes. **Recall fails**, because this project already measured that
  opposite-sign pairs sit as close as 0.3 ξ (paper §6), and two cores that close share one density
  minimum. Specifically: recall restricted to vortices whose nearest neighbour is > 2 ξ away ≥ 0.97;
  restricted to < 1 ξ, ≤ 0.6.
- **Negative control.** A vortex-free frame (smooth phase noise, amplitude low enough that winding
  finds 0 vortices; if it finds any, the control is void and redone at lower amplitude) must give
  0 detections.
- **Sensitivity (reported, not used to pick a threshold).** Precision/recall on the 5 × 5 grid
  birth ∈ {0.05…0.25}, persistence ∈ {0.3…0.7}.

## 7. D3 — phase-space holes

- **Honest description.** A phase-space hole is a local minimum of f: again H₀ sublevel persistence =
  depth. The instrument is an automatic counter; the claim is only that it counts correctly.
- **Setup.** Two-stream f₀ = ½[M(v − 2.4) + M(v + 2.4)], L = 2π/k, mode-1 seed 10⁻³,
  N_x = 128, N_v = 512, v_max = 8, Δt = 0.1, to t = 80. Run S1: k = 0.2. Run S2: L = 2π/0.1 with the
  seed in mode 2 (same physical wavelength, two periods in the box).
- **Growth rate (extends K1/K2).** Certified root of the two-stream dispersion relation; measured rate
  from ln|E| over the decade of growth ending at 10 % of saturation. **Pass:** within 5 %.
- **Hole count.** Holes = H₀ sublevel classes of f restricted to |v| < 2.4 with persistence
  > 0.1·max f. **Predictions:** S1 has exactly 1 at t = 60. S2 has exactly 2 at the first saturation
  peak; whether and when they merge by t = 80 is **not predicted**.
- **Negative control.** Run A of K2 (stable Maxwellian) at t = 50: 0 holes.
- **Exploratory (no pass/fail, labelled as such in any write-up).** Count of pairs with persistence in
  (10⁻⁶, 10⁻²)·max f versus t at N_v = 256 and 512, as a resolution-loss indicator.

## 8. What would make me stop

Any of: K1 negative control certifies; K2 Run B cannot discriminate; K3a misses by more than a
convention factor; P-D0b unexplained. Each is a stop-and-report, not a fix-and-rerun.

## 9. Amendments

**A1 — 2026-09-21, after the kinetic literature gate reported, before any code was written.**
Criteria in §§1–3, 5–7 are unchanged. Changes of *scope and description* only:

1. **K4 is not a contribution.** J. Bedrossian, *Formalization of Landau damping in the Vlasov–Poisson
   equations in Lean*, arXiv:2609.16801 (15 Sep 2026) formalizes the Mouhot–Villani nonlinear theorem on
   T^d for Gevrey s > 1/3, small backgrounds, reportedly sorry-free (I verified the arXiv record; I have
   **not** built the repository). Phase mixing for free transport is a corollary of what is proved
   there, and a one-line corollary of Mathlib's Riemann–Lebesgue lemma. K4 is kept only as a
   Mathlib-only lemma that K3a's closed form cites, and must be described as subsumed.
2. **My proposal was wrong** to say of nonlinear Landau damping in Lean that "no part of it is within
   reach". It was done six days before I wrote that. Erratum added to the proposal.
3. **Where this work can still sit.** That paper treats small backgrounds and states that large
   backgrounds "would require formalizing a great deal of complex analysis theory surrounding Laplace
   transforms" — i.e. the dispersion relation and Penrose criterion are absent. K1 (a certified root of
   exactly that dispersion relation) is complementary numerics, not competing formalization. K5
   (Penrose *statements* without proofs) is dropped: an unproved statement next to a proved
   Mouhot–Villani is not worth printing.
4. **H5 gains a 2D case**, because the gate pointed out that Godfrin et al., Nature 483, 576 (2012) is a
   *two-dimensional* ³He monolayer and the logarithmic formula is 3D. **H5-2D `zero_sound_2d_iff`:**
   with Ω₂(s) = 1 − s/√(s²−1) for s > 1, the condition 1 + F·Ω₂(s) = 0 has a root s > 1 ⟺ F > 0, and
   then s = (1+F)/√(1+2F). (Closed form derived by hand just now; if Lean disagrees, Lean wins and the
   discrepancy is reported.) Negative control as for H5.
5. K2 and K3 are validation and demonstration only (every Vlasov code runs them); their role in any
   write-up is to show the solver's failure modes are pinned, not to claim a result.
