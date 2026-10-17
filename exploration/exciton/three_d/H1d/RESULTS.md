# H1d results (PREREG.md; code frozen at 4e596f0; evaluator fix 1ee1714 before evaluation, DEVIATIONS.md; `evaluate.py`)

Runs: `launch.sh` 2026-10-17 09:33:31 (5 s after the freeze commit 4e596f0 at 09:33:26; first record 09:33:32) to 10:42, uninterrupted, 3 jobs in parallel on a machine shared with another project's
8-thread jobs (timings inflated). 31 (case, s, m) runs registered: **29 certified, 2 no record** — D3pi (8, 48) and D3a8 (6, 48),
where the HiGHS interior-point solver returned "model_status Unknown" (RuntimeError in `solve()`, logs/). They were not rerun
with other solver settings (unregistered); each case keeps ≥ 5 certified grids. Every certified grid has min μ ≈ 1e-8 (the ε
buffer), provably > 0 as an arb ball; the certified UB equals the float LP value to ≤ 3e-11 relative (largest at α = 8). Pre-run math/code review:
docs/designs/EXCITON_FLUID_VERIFIER_NOTES_H1d_math.md (no blocking item; independent brute-force evaluation agrees).

## Validation gates

| gate | UB* (certified, best grid) | reference | verdict |
|---|---|---|---|
| V1 d=1, α=π | 0.0864348174801 (2, 8) | E_Z(π) 0.0864348112133; UB*/E_Z − 1 = 7.3e-8 (ε-buffer cost); no grid below E_Z | **pass** (tol 1e-6) |
| V2 d=2, α=π | 0.160722743991 (8, 96) | E_A2 0.159595267; +0.71%; ≥ H1'' certified B | **pass** (consistency) |

No VOID: every certified UB is above the certified lower bound B of the same (d, α).

## Registered results (d = 3)

| α | UB* (certified upper bound on LP(α), rounded up) | best grid | B (certified lower, H1''', rounded down) | min(FCC, BCC) | UB* below min(FCC, BCC) by (rounded down) | sandwich (UB*−B)/B (rounded up) |
|---|---|---|---|---|---|---|
| π | 0.224286664108 | (6, 48) | 0.223217819358 | 0.231536266184 (FCC = BCC) | **3.13%** | 0.48% |
| 2 | 1.01164856407 | (6, 48) | 1.01101824668 | 1.01586281603 (BCC) | **0.414%** | 0.063% |
| 4 | 0.0734293569076 | (8, 48) | 0.0727564554394 | 0.0779676710 (FCC) | **5.82%** | 0.93% |
| 8 | 0.000410902080147 | (8, 48) | 0.000394760289342 | 0.000503241302 (FCC) | **18.3%** | 4.1% |

**Verdict at all four α: UB* < min(FCC, BCC).** Hence, rigorously, for the linear-programming (two-point) bound in the form
of CdCI Prop. 2.2 (Cohn–Kumar's bound as restated there), at density 1 in R^3: at α = 2, 4, 8 it lies strictly below
min(E_FCC, E_BCC), so it cannot prove FCC or BCC optimal there (we cite no proof that FCC/BCC are the best lattices; they are the
lattices compared throughout this programme). At α = π, FCC and BCC are not the putative ground state (Cohn–Kumar–Schürmann
report a lower FCC/BCC coexistence state, the CdCI "current record" 0.23153532 in our ordered-pair convention); the relevant
statement there is that UB* is 0.00724 below that record (rounded down), so the two-point bound cannot prove the coexistence state
optimal either. The gap itself was already visible numerically (CdCI Table 1.1 at α = π; H1' and H1''' at α = 2, 4, 8); what is
new here is a rigorous certificate for it. With the H1''' lower bounds the two-point bound is pinned:
LP(π) ∈ [0.2232178193, 0.2242866642], LP(2) ∈ [1.0110182466, 1.0116485641], LP(4) ∈ [0.07275645543, 0.07342935691],
LP(8) ∈ [0.0003947602893, 0.0004109020802]. The interval at α = π contains CdCI's numerically optimised 0.22321782.

Prediction (PREREG): V1, V2 pass; all four D3 below min(FCC, BCC), α = 2 with the smallest margin; D3pi below the CdCI record.
**All parts hold.** UB is not monotone in the grid (e.g. α = 2: (8, 48) gives 1.01187 > (6, 48) 1.01165); each grid's UB is
valid on its own, so the minimum is not a selection effect.

## Scope of the statement

Registered class 𝓗 (DESIGN.md): continuous radial h with |h|, |ĥ| = O((1+|x|)^{-d-δ}), ĥ ≥ 0, h ≤ g off 0.
**Post-registration lemma (scope only, no computation changed; pre-run review SF-1, checked by the author; kept separate from the registered claim):** the same UB
bounds ĥ(0) − h(0) for every h in the full class of CdCI Prop. 2.2 (continuous, integrable, positive definite, h ≤ g off 0;
no decay or radial assumption). Proof sketch: h_ε = h e^{-πε|x|²} keeps ĥ_ε = ĥ ∗ Gaussian ≥ 0, h_ε(0) = h(0) and h_ε ≤ g off 0
(where h > 0 the factor lowers it; where h ≤ 0, h_ε ≤ 0 < g), and ĥ_ε(0) → ĥ(0) by dominated convergence. For f = h_ε(·/s):
ĥ ≥ 0 with h continuous and integrable gives ĥ ∈ L¹ (Stein–Weiss, Ch. I, Cor. 1.26), so the periodisation P = Σ_k f̂(· + k) ∈ L¹(T^d) has Fourier coefficients f(n);
|h_ε(x)| ≤ h(0)e^{-πε|x|²} (|h| ≤ h(0) for positive definite h) makes Σ|f(n)| < ∞, so Σ f(n)e^{-2πi n·ξ} converges uniformly to a continuous F = P a.e.; hence F ≥ 0 everywhere and
F ≥ f̂ everywhere (f̂ continuous), which are steps 1–2; steps 3–5 are unchanged. Non-radial h: radialise (average over O(d)),
which preserves every hypothesis and ĥ(0), h(0). So the statements above hold for the two-point bound as CdCI define it. Not covered: the wider formulation of Cohn–Kumar's
original Prop. 9.3 (h = ĝ with g ∈ L¹, objective with a lim inf), which the reviewer indicates a similar damping argument
would reach; we do not claim it.

Not shown: anything about three-point or semidefinite bounds, the true minimal energy, or α other than π, 2, 4, 8; the
location of LP(α) inside the sandwich; whether the d = 2 bound (conjecturally sharp) is approached (0.71% gap at our grids).
