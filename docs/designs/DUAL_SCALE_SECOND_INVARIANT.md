# Design memo (PRE-REGISTRATION, nothing run): does the dual-scale shell model have a second invariant?

**Date:** 2026-09-19. **Status:** proposed, awaiting owner audit (E-1: nothing is implemented before this is marked AUDITED in LEDGER.md).
**Origin:** CLAIM-022 (`lean_src/GPGalerkin.lean`) and the LL-15 check in `docs/OPENAI_NSE_LEVERAGE_FOR_QUANTUM_FLUIDS.md` §8.

## 1. The question, stated so it can fail

A truncated Galerkin Gross–Pitaevskii system has **two** conserved quantities: the mass `N = Σ|ψ_k|²` and the energy
`E = Σ ω_k|ψ_k|² + (g/2)Q`, with `Q = Σ_q|A_q|² ≥ 0` (CLAIM-022, Tier A: `Q` is a sum of squares, energy rate zero
algebraically). Positivity of `Q` is what turns conservation of `E` into a truncation-independent bound on the
ω-weighted (H¹) quantity.

Our complexified truncated Katz–Pavlović shell model has **one** known conserved quantity, `Σ|v_n|²` (CLAIM-007), plus the
Liouville property (CLAIM-011). Its enstrophy-like quantity `Ω = ½Σk_n²|v_n|²` is bounded only by `k_N² E`, which grows
with the cutoff `N`. That growth is precisely why the M2 exponent question was posed.

> **Q1.** Is there a second invariant of the truncated complexified shell model of the form
> `F = Ω + (positive quartic form in the |v_n|, v_n)` with nonzero Ω-coefficient?
> If yes, `Ω` is bounded uniformly in `N` (as for GP) and the dispersive regulator is regularizing for an identifiable reason.
> If no, the regulator is Hamiltonian-and-Liouville but has no coercive H¹ structure, and its degeneracy at large N is expected.

**LL-15 status.** The GP bound depends on a *positive quartic interaction energy*. The shell model has a *triadic* (quadratic)
coupling. So the bound does **not** transfer by analogy; Q1 asks whether the structure exists independently.

## 2. Candidate family (from the seam theorem, not invented)

CLAIM-016 (`seam_gpe_conserves`): the conserving seams are `v_{N+1} = iμ v_N²`. The top shell then feels
`−k_N conj(v_N) · iμ v_N² = −iμ k_N |v_N|² v_N`, a local Kerr self-phase term, whose Hamiltonian is proportional to `|v_N|⁴`, a positive quartic
in the top shell only. This suggests the search space `F ∈ span{ Σk_n²|v_n|², |v_n|²|v_m|², Re/Im(conj(v_a)conj(v_b)v_c v_d) }`
(U(1)-symmetric quartic monomials). It is a search space, not a claim that any member is conserved.

## 3. Pre-registered test (deterministic; no trajectories)

For fixed `N` (6, 8, 10) and seam `v_{N+1} = iμ v_N²` (μ ∈ {0.5, 1}), sample `S ≥ 200` random states `v ∈ ℂ^{N+1}`.
For each basis functional `φ_j`, compute its exact Lie derivative `L φ_j (v) = 2 Re Σ_n conj(∂φ_j/∂v_n)·(dv_n/dt)` in exact rational
arithmetic where the coefficients are rational, otherwise mpmath at 50 digits. Stack the `S × J` matrix `M`; a conserved `F` is a null vector of `M`.
Report the **numerical nullspace dimension** and whether any null vector has nonzero coefficient on `Ω`.

- **Positive control (backed by a theorem):** run the identical code on truncated GP with the Fourier-Galerkin nonlinearity of
  `GPGalerkin.lean` (small lattice). It **must** find the null vector `(ω-weighted energy) + (g/2)Q` (Lean: `energy_rate_zero`). If it does not, the code is wrong, and the run is void.
- **Negative control:** the same shell model with a *leaking* seam (a neighbour-reading seam, measured leak `|dE/dt| ~ 10²–10³`, CLAIM-016 corollary).
  There, even the mass functional must drop out of the nullspace. If it does not, the test cannot fail, and the run is void.
- **Kill criterion (fixed before running):** if for all `N` and `μ` no null vector has a nonzero Ω-coefficient (smallest relevant singular value
  above `1e-8·σ_max`, stable under doubling `S`), Q1 is answered **no in this span** and reported as such. Not "no invariant exists".

## 4. What each outcome would license

| Outcome | Licenses | Does not license |
|---|---|---|
| Null vector with Ω-coefficient, μ-independent structure | a Lean statement (exact identity) and a uniform-in-N bound on Ω from that invariant, if its quartic part is provably ≥ 0 | any claim about the untruncated model or about N → ∞ dynamics |
| Null vector but quartic part indefinite | conserved but not coercive: no bound | a regularity claim |
| No null vector in span | "the dual-scale cap supplies no second invariant of this form" | that none exists outside the span |

## 5. Explicitly out of scope
Time evolution, the M3 exponent, the untruncated (N → ∞) Katz–Pavlović blow-up, and any Navier–Stokes statement.
Single trajectories are not used anywhere (criterion B8).

## 6. Cost
Code: one small module plus tests (~150 lines). Compute: minutes. Lean: only if the outcome is positive.

---

## Addendum A1 — registered 2026-09-19 AFTER audit approval, BEFORE any code exists or runs

**Audit:** approved by the owner as written, 2026-09-19.

**A1.1 Correction to §2 (symmetry).** §2 called the quartic monomials "U(1)-symmetric". The uniform phase `v_n → e^{iθ}v_n` is **not** a
symmetry of the flow (`v_{n-1}²` picks up `e^{2iθ}`). The symmetry is the **graded** phase `v_n → e^{i2ⁿθ}v_n`. The §3 span is run as
pre-registered anyway (it is what was approved), plus all single-shell quadratics `|v_n|²` (a superset, needed by the negative control).

**A1.2 Prediction, derived on paper before running (thought experiment: "ride the graded phase").**
Rescale `w_n = 2^{-n/2} v_n`. Then the complexified model is a Hamiltonian second-harmonic-generation chain
`i dw_n/dt = ∂H/∂conj(w_n)`, and in the original variables
```
H = Σ_n 2^{-n} [ D k_n² |v_n|²  +  k_n Im(conj(v_n)² v_{n+1}) ]   (+ ½ μ k_N 2^{-N} |v_N|⁴ with the seam v_{N+1} = iμ v_N²)
```
is conserved; `Σ|v_n|²` is the Noether charge of the graded phase (Manley–Rowe), and Liouville (CLAIM-011) is a corollary of Hamiltonian structure.
Predictions, fixed now:
- **P-a.** In the pre-registered span (quadratics + quartics) the nullspace is the mass only: **the §3 kill criterion fires** (no Ω-coefficient).
- **P-b.** In extension span E1 = pre-registered span + cubics `Re/Im(conj(v_n)² v_{n+1})`, nullspace dimension is 2 at D = 0 (mass, H) for the truncation seam
  and for the GPE seam, with the H coefficients exactly `2^{-n}k_n` on `Im`, zero on `Re`.
- **P-c.** On real data `H ≡ 0`: the real Katz–Pavlović model sees no trace of it.
- **P-d (consequence, to be proved not measured).** For `D > 0`, `k_n = 2ⁿ`: `D Σ 2ⁿ|v_n|² ≤ H + (2E)^{3/2}` with `E = ½Σ|v_n|²`: a bound on the
  H^{1/2}-type norm `Σ k_n|v_n|²` that is **uniform in the cutoff N**. It does *not* bound `Ω = ½Σk_n²|v_n|²`.
If P-b fails, the derivation above is wrong and is retracted. Novelty is **not** claimed: literature check pending (complex dyadic / SHG-chain models).

**A1.3 Deviation from §3 (precision).** Full span: float64 SVD (criterion as in §3). Exactness is obtained differently and more strongly: the candidate
invariant is checked as a **symbolic polynomial identity** (sympy, generic symbols), then in Lean.


---

## §5 RESULTS (run 2026-09-20)

### 5.0 Scope deviation, declared

The pre-registered `N ∈ {6, 8, 10}` was **not completed**. The first attempt was killed by its own 50-minute budget
(exit 143) — a *bookkeeping stop*, not a finding (MechanicaFluidorum LL-18). Cause, found and fixed: `lie_matrix`
cached every monomial's Lie derivative, `S × J` complex entries ≈ **1.25 GB at N = 10**, which made the machine thrash.
With the cache removed the same work takes seconds. Scope run: **`N ∈ {4, 5, 6}`**. `N = 8, 10` were **not attempted**
and nothing is claimed for them. Each case was run at two sample sizes (`2J` and `4J`) to check stability.

### 5.1 Controls

| control | requirement | result |
|---|---|---|
| positive (truncated GP, theorem-backed by `GPGalerkin.energy_rate_zero`) | the GP energy must lie in the nullspace | **PASS**, distance `2.2×10⁻¹⁵` |
| negative (leaking seam) | mass must **not** lie in the nullspace | **PASS**, distance `1.0` (fully outside) |

### 5.2 Outcome

| span | `N = 4, 5, 6`, all seams, `D = 0` and `0.3`, both sample sizes | verdict |
|---|---|---|
| **pre-registered** (quadratics + quartics) | nullspace dimension **2**, spanned by `{mass, mass²}` | **§3 kill criterion FIRES**: no null vector has an `Ω` coefficient |
| **extension E1** (+ cubics `Re/Im(conj(v_n)²v_{n+1})`) | nullspace dimension **3**, spanned by `{mass, mass², H}` | the predicted `H` is conserved |

`max‖known − proj(known)‖/‖known‖ = 1.9×10⁻¹³`, `max‖null − proj_known(null)‖ = 1.9×10⁻¹³`: the nullspace is **exactly**
the known invariants, nothing further hides in the span. Smallest retained singular-value gap `1.5×10⁻³`, far above the
`10⁻⁸` threshold; dimensions unchanged when the sample size is doubled.

### 5.3 Predictions vs outcome

| | prediction (A1.2) | outcome |
|---|---|---|
| **P-a** | kill criterion fires in the pre-registered span | **CONFIRMED** |
| **P-b** | with cubics, nullspace dim **2** = `{mass, H}` | **WRONG IN THE COUNT, RIGHT IN THE CONTENT**: dim **3** = `{mass, mass², H}`. The addendum forgot `mass²`, a trivial quartic consequence of mass conservation. `H` itself is exactly as predicted, coefficients `2⁻ⁿk_n` on `Im`, zero on `Re`. |
| **P-c** | `H ≡ 0` on real data | **CONFIRMED**, identically `0.0` |
| **P-d** | uniform-in-cutoff bound | proved in Lean (`ShellHamiltonian.dispersive_norm_le`), not measured |

The A1.2 derivation therefore stands; only its dimension count was off, and by a trivial invariant.
