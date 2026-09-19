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
