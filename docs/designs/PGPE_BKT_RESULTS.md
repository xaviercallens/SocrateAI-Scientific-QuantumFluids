# Results: PGPE classical-field BKT gate, the duality checks and the topology closed loop

> **Erratum (2026-09-25, round 2, `PGPE_R2_RESULTS.md` C5).** The transition temperature quoted below,
> T_BKT ≈ 0.72, was interpolated between quench-started states; the round-2 heating ladder shows the
> quench e = 1.20 state had half the stiffness of the equilibrated one at the same vortex count. The value
> is **withdrawn** in favour of T_BKT(L = 64) = 0.821 (η = 0.31 there). D1/D2 verdicts below stand on the
> e = 0.6/0.9 points, which were re-equilibrated to t = 4000; B4's +47 % becomes +29 % with the corrected T.

Pre-registration: `docs/designs/PGPE_BKT_PREREG.md` (7de1f11) with amendments A1 (f4e1c10, before any
thermal run), A2 (58aa0e2, before any thermal run), **A3 (573f83d, data-triggered after 6 of 36
trajectories)** and **A4 (bcc0f56, post hoc after all 36)**. Data: `data/generated/pgpe/sweep/*.json`
(36 runs to t = 1500, 7 extensions to t = 4000); analysis `exploration/pgpe/analyze_sweep.py {A3,A4}`,
outputs `data/generated/pgpe/analysis_final_{A3,A4}.txt`. Lean: `lean_src/QHFricke.lean`.

## 1. Gate verdicts on the external feedback (A2.1, before any data)

| Feedback item | Verdict |
|---|---|
| K3 mirror: Fricke `W_N` is the Dolgachev–Nikulin mirror involution on Γ₀(N)⁺ | Correct (Dolgachev Thm 7.1, already read, `Fricke.lean`). Nothing in this repository is a K3 surface. |
| BKT at the self-dual radius `R ↔ α′/R` | **Incorrect.** Self-dual point: `Δ_e = Δ_m = 1/2`, `η = 1`. BKT: unit vortex marginal, `Δ_m = 2`, `η = 1/4`, stiffness four times the self-dual one. Films and cold atoms measure the Nelson–Kosterlitz jump (`η = 1/4`), not self-duality. |
| Quantum Hall: Γ₀(2) on σ | Correct as a proposal with experimental support (Lütken–Ross; `ρ_H = 0.282 ± 0.002` vs 7/25). **But the Fricke element is not a Hall symmetry**: `W₂` sends every plateau to a point with no odd-denominator representation. Proved, `QHFricke.lean`. |
| Seiberg–Witten Γ(2) | A theorem about N=2 SU(2) gauge theory; no instrument here. |
| "Fricke links astrophysics (macro) and quantum fluids (micro)" | No support found; the α′ = ℓ_P c/H₀ identification stays excluded. |
| TDA detects BKT | Published (Cole–Loges–Shiu arXiv:2009.14231; Sale–Giansiracusa–Lucini arXiv:2109.10960). Used here as an instrument, not a claim. |

**`QHFricke.lean`** (6 theorems; Comparator: nanoda and the Lean kernel accept; standard axioms; three
negative controls fail):
* `M = (1,−1;2,−1) ∈ Γ₀(2)`, `M² = −1`, and `M` fixes `(1+i)/2`;
* Γ₀(2) preserves the odd-denominator class;
* `W₂(σ⊗) = σ⊗ − 1`: Fricke fixes the critical point's orbit on Γ₀(2)\H;
* for `q` odd and `p ≠ 0`, `−q/(2p) ≠ r/s` for every odd `s`.

The Fricke involution meets quantum Hall physics at the critical point, and nowhere else.

## 2. What happened on the way (the part that was not planned)

1. **The thermometer passes while the topology has not relaxed.** At `e = 0.90`, t = 1500, seeds 11 and 12
   carried ≈ 10–12 vortices with `Q = 0.67` (largely unbound). The transverse current correlator at the
   smallest shell was ≈ 4 n T A, so the estimator gave `n_s/n = −3.0` and `−3.2`. Seed 13 at the same
   energy had already lost its free vortices. K7 (equipartition on `[0.4, 1] k_cut`, halves within 5 %)
   passed on all three.
2. **A3 was wrong in its premise, and A4 corrected it.** A3 admitted runs by `⟨|J_L|²⟩ = n T A` and called
   it an exact sum rule. For a classical field it holds only in the ordered, hydrodynamic regime. In the
   incoherent regime the ideal Rayleigh–Jeans value is `Σ_k ((k+q/2)·q̂)² n_k n_{k+q}`. With each run's
   fitted `(T, b)` it reproduces the measured `R_L` within 5 % at `e = 2.4–3.2`, e.g. 0.318 vs 0.320.
   A4 keeps the two signals no equilibrium regime produces: `R_L > 1.25` and `R_T > 1.1 R_L`.
   Verdicts are reported under both A3 and A4.
3. **The extensions confirm the reading.** All seven A4-excluded runs were re-run to t = 4000, and all
   seven are admitted afterwards:
   * `e = 0.60`: `R_L` goes from 1.6–2.3 to 1.04–1.08, the hydrodynamic value;
   * `e = 0.90` seeds 11 and 12: the free vortices annihilated.

### A same-temperature comparison: topology, not temperature, set the observables (post hoc, n = 2)

At `e = 0.90`, seeds 11 and 12 compared at t = 1500 and at t = 4000:

| run | T | ⟨N_v⟩ | Q | condensate | η (g₁) | n_s/n |
|---|---|---|---|---|---|---|
| s11, t = 1500 | 0.443 | 11.7 | 0.67 | 0.18 | 0.52 | −3.2 (invalid) |
| s11, t = 4000 | 0.443 | 7.5 | 0.22 | 0.62 | 0.12 | 0.59 |
| s12, t = 1500 | 0.446 | 9.5 | 0.67 | 0.23 | 0.44 | −3.0 (invalid) |
| s12, t = 4000 | 0.458 | 5.8 | 0.21 | 0.64 | 0.10 | 0.83 |

* The thermometer barely moved: 0.443 → 0.443 for seed 11, and 0.446 → 0.458 for seed 12.
* What changed is the vortex topology: a few free vortices became bound or annihilated, and Q fell from 0.67 to 0.22.
* With it, the condensate tripled, η fell fourfold, and the stiffness became measurable.

This is the clearest statement in this round that the topology carries the physics the thermometer does
not see. It is an observation, not a pre-registered test: two runs, and the comparison is across time within a trajectory.

## 3. Pre-registered verdicts (final data, seed means over admitted runs)

| e | T | n_s/n | n_s λ² | η | ℓ | Q | ⟨N_v⟩ | cond |
|---|---|---|---|---|---|---|---|---|
| 0.60 | 0.116 | 0.971 | 52.5 | 0.020 | 390 | – | 0.0 | 0.912 |
| 0.90 | 0.449 | 0.661 | 9.25 | 0.116 | 67 | 0.23 | 7.0 | 0.626 |
| 1.20 | 0.767 | 0.371 | 3.04 | 0.349 | 22 | 0.22 | 93 | 0.299 |
| 1.40 | 0.958 | 0.014 | 0.09 | 0.863 | 8.6 | 0.33 | 211 | 0.067 |
| 1.60 | 1.160 | 0.028 | 0.15 | 1.80 | 4.1 | 0.40 | 342 | 0.018 |
| 2.00 | 1.690 | 0.022 | 0.08 | 2.98 | 2.6 | 0.46 | 603 | 0.004 |
| 3.20 | 7.354 | −0.012 | −0.01 | 1.84 | 4.3 | 0.53 | 1287 | 0.000 |

(Full table, including e = 1.8, 2.2, 2.4, 2.6 and 2.8, in `analysis_final_A4.txt`.)

| # | A3 as written | A4 | Value / reason |
|---|---|---|---|
| B1 both g₁ regimes | PASS | **FAIL** | A4 admits e ≥ 2.0, where g₁ reaches noise by r ≈ 2–6 inside the fixed window [2, 16]. The "algebraic beats exponential" comparison is then a fit to noise (14 positive points of 28 at e = 3.2). The failure is in my window choice, not in the physics. |
| B2 f_free > 0.5 | FAIL | FAIL | `f_free` ≤ 0.13 everywhere. At high T the vortex density (up to 1300 in 64²) puts an opposite charge within the pre-set 3 ξ of nearly every vortex, so the statistic cannot see unbinding. |
| B3 n_s λ² = 4 crossing near T_× | PASS | PASS | `T_BKT = 0.718` by interpolation between e = 0.9 (9.25) and e = 1.2 (3.04); `T_×` at e = 1.4. |
| B4 Prokof'ev number | FAIL | FAIL | `n λ² = 8.76` at T_BKT vs `ln 380 = 5.94` (+47 %). The pre-set cutoff check (`k_cut = 0.5 k_max`) is now the base run after A1, so the cutoff dependence was **not** quantified. |
| B5 finite size L = 32 | not run | not run | — |
| D1 η·n_s λ² = 1 | PASS | PASS | 1.047 (e = 0.6), 1.072 (e = 0.9). |
| D2 η = 1/4 at the jump | PASS | PASS | 0.313 (tolerance ±0.08: inside, at 0.063 from 1/4). |
| D3 self-dual point is not the transition | PASS | **FAIL** | Same g₁-window artifact as B1. Under A3: η = 0.349 at the last algebraic energy. |
| T1 part 1: Q ≤ 0.5 at low T | PASS | PASS | 0.226 |
| T1 part 2: Q ≥ 0.8 at high T | FAIL | FAIL | Q saturates at ≈ 0.53. My prediction assumed an unbound plasma looks like shuffled charges; a dense screened plasma (and grid-scale noise vortices) does not. |
| T1 part 3: Q's rise at T_BKT | PASS | PASS | Largest rise between e = 1.2 and 1.4 (0.22 → 0.33); the crossing lies between 0.9 and 1.2, so it is within one step. |

**K7 caveat.** At e = 0.60, two seeds fall outside the thermometer's 10 % two-window agreement (0.82, 0.88)
and two outside the 5 % halves (6 %). The kill clause "not stationary at any energy" is ambiguous. Under
the strict reading, e = 0.60 is dropped; D1 then rests on e = 0.9 alone (1.072, PASS), and no other
verdict changes.

## 4. What this round establishes, and what it does not

**Established:**
1. In this classical-field model the stiffness drops from `n_s λ² ≈ 9` to ≈ 3, then to ≈ 0, between T = 0.45 and 0.96.
2. The spin-wave duality relation `η · n_s λ² = 1` holds to 5–7 % in the ordered phase.
3. `η ≈ 0.31` at the interpolated jump. This is the Nelson–Kosterlitz value within the pre-set tolerance, not the self-dual value 1.
4. The W₁ dipole-matching statistic moves off its bound-pair value where the stiffness collapses.

These are known physics (Nelson–Kosterlitz 1977; classical-field BKT studies), reproduced with this
project's own solver and instruments. **No novel physics is claimed.**

**Not established:**
* the location of the jump to better than one energy step. The grid between e = 0.9 and 1.2 is coarse, and the jump is finite-size smoothed;
* the cutoff dependence (B4);
* finite size (B5);
* any statement tying the Fricke involution to BKT. The self-duality of the compact boson is exact but is not where the transition sits;
* any statement about helium films, or about astrophysics.

**Process record:**
* One amendment, A3, rested on a false premise of mine and was corrected post hoc (A4), with both versions reported.
* Two pre-registered instruments failed for design reasons: the g₁ fit window at high T, and the fixed 3 ξ pairing radius at high vortex density.
* One prediction failed outright (T1 part 2).
* The prereg's compute estimate was wrong by ≈ 15×.
