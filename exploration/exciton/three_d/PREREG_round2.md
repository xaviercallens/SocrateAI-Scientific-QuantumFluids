# 3D programme, round 2 (pre-registration, 2026-10-12)

Order decided by the owner on 2026-10-12 after the memo `docs/designs/AXES_3D_COHN_KUMAR_2026-10.md`:
F1 (α-homotopy, proved control) → T2/T1 (Gaussian mixtures across the self-dual point; formal self-duality) → H1 (LP gap in d = 3).
Everything below is fixed before any run. Deviations go in a dated section of each RESULTS.md. Negative results are kept.
No statement relies on the unrefereed planar lattice theorem.

## F1 — homotopy in α on S³ (directory `F1/`)
Setting: N points on the unit S³, Gaussian chordal kernel e^{-a d²}. Reference: Experiment C (`C/`), where plain L-BFGS from
random starts reaches the 600-cell (proved universally optimal for N = 120, Cohn–Kumar 2007) in 0/50 (a = 2), 6/50 (a = 4),
0/50 (a = 1, distinct local minima within 2e-8), 50/50 (a = 0.5).
Method under test: start at a₀ = 0.25 (L-BFGS to convergence, same seeds as C), then follow the minimiser along a geometric
ladder a₀ → a_target with ratio 2^{1/4} (L-BFGS re-converged at each rung, warm start). Budget: report total gradient
evaluations; compare with C's plain runs at the same seed.
Gate F1a: for N = 120 and a ∈ {1, 2, 4}, ≥ 45/50 seeds end within 1e-8 relative of E₆₀₀ (coordinates checked: min chord
within 1e-6 of 2 sin(π/10)).
Gate F1b (equal compute): plain L-BFGS given the same number of gradient evaluations as the homotopy (restarts allowed) does
NOT reach ≥ 45/50 at a ∈ {2, 4}. If it does, the homotopy has no merit.
Control 2: N = 24, a ∈ {1, 2, 4}. Report whether the homotopy returns the 24-cell or something lower (the 24-cell is not
universally optimal on S³ per Cohn–Conway–Elkies–Kumar 2007, a statement from memory to be checked before it is cited).
Stop: F1a fails at every a → the 3D structure searches of this programme are declared unreliable and T1/T2 are run only as
"no counterexample found with an unreliable search".

## T2 — Gaussian mixtures across the self-dual point (directory `T12/`)
Kernel f(r) = e^{-a₁ r²} + λ e^{-a₂ r²} at unit density, (a₁, a₂) ∈ {(π/2, 2π), (π/4, 4π), (2, 5)}; for each pair λ* is the
value where E_FCC = E_BCC (computed first, bisection to 1e-12) and λ ∈ λ*·{0.9, 0.97, 1, 1.03, 1.1}.
Search: Experiment B engine (free 9-parameter cell + N ∈ {2, 4, 8, 12, 16} points), 100 restarts for N ≤ 4, 60 for N = 8,
40 for N = 12, 16 (as actually used in round 1, disclosed there). Energies as in `AB/lattsum.py` (Ewald, tails ≤ 1e-15).
Gate T2: any configuration below min(E_FCC, E_BCC, E_HCP) by > 1e-8 relative, re-minimised independently from its own
coordinates with a different cutoff/splitting and still below → reported as a finding with coordinates; otherwise negative.

## T1 — formally self-dual periodic configurations at α = π (directory `T12/`)
Definition used (Cohn–Kumar–Schürmann 2009, from memory; to be re-read and quoted before the result is written up): a
periodic configuration P with N points per cell of lattice Λ is formally self-dual if its average pair sum satisfies the
Poisson-type identity Σ_f(P) = Σ_{f̂}(P) for all Schwartz f, equivalently |Σ_j e^{2πi k·x_j}|²/N as a function on Λ* equals the
pair-density of P on Λ (the "structure factor equals the pair correlation" condition).
Search: N ∈ {2, 4, 8}, random starts, minimise the L² mismatch of the two sides on a finite set of shells (first 40 shells)
with the cell free; accept candidates with mismatch < 1e-10; then compute their Gaussian energy at α = π.
Gate T1: a formally self-dual configuration that is not a lattice and whose energy at α = π is below E_FCC(π) = E_BCC(π)
= 0.231536266184 by > 1e-8 → finding (re-verified as in T2). Expectation: none (the lattice fixed point is a maximum on the
Bain path, `AB/bain_selfdual.py`).

## H1 — two-point LP bound for Gaussian energy in d = 3 (directory `H1/`)
Cohn–Kumar linear programming bound: if f: R³ → R is radial, f(x) ≤ e^{-α|x|²} for all x ≠ 0 and f̂ ≥ 0, f̂(0) ≥ 0 ... the energy
per particle of any unit-density configuration is ≥ f̂(0) − f(0). (Exact statement to be transcribed from Cohn–Kumar 2007
Prop. 9.3 / CKMRV 2022 §1 before coding; the inequality direction and normalisations are checked against d = 1 (Z) and d = 2
(A₂ numerics) first.)
Ansatz: f̂(y) = e^{-π|y|²/β} p(|y|²) with p a polynomial of degree ≤ 30, constraints discretised on |x| ∈ [0, 6] (2000 points)
plus a tail bound; LP solved with scipy.optimize.linprog or cvxpy if installed (report which). Verification: the optimal f is
re-checked on 10⁵ random points for f ≤ potential.
Report for α ∈ {2, π, 4, 8}: LP bound, min(E_FCC, E_BCC), relative gap.
Gate H1: gap < 1e-6 at some α → "LP has a chance at that α in d = 3" (hand to a specialist); gap > 1e-3 at all α → two-point
methods are declared insufficient for the 3D Gaussian-core conjecture at these α. In between: inconclusive.
Sanity gate H0 (must pass first): d = 2, α = π, same code gives a bound within 1e-6 of the triangular-lattice energy? (No:
the 2D LP bound is NOT known to be sharp either; so H0 is instead: d = 8 is out of reach, so use d = 1 where Z is universally
optimal and the LP bound is sharp — the code must reproduce E_Z(α) to 1e-8 at α ∈ {1, π}.)

## Article V
Drafted in parallel (`paper/exciton_fluid_gated_V.tex`): L1 (KK evaluator), round 1 (A, B, C, D), L3, the memo's axes and the
Bain test, round 2 (F1, T1/T2, H1) as they close. Negative results included. Hostile review before any deposit.
