# Pre-registration, round 2: a causal test of "topology sets the physics", a finer look at the jump, and finite size

Follows `docs/designs/PGPE_BKT_RESULTS.md` (CLAIM-038). Written and committed before any round-2 code is
run. Same solver (`exploration/pgpe/pgpe.py`, K1–K7 passed), same units (ħ = m = g = n = 1), grid spacing
`dx = 0.5`, `k_cut = k_max/2`. Changes after this commit are dated amendments.

Round 1 left one **post hoc** observation on two runs: at the same thermometer reading, runs carrying
≈ 10 unbound quench vortices had condensate ≈ 0.2 and η ≈ 0.5, and the same runs after the vortices
annihilated had 0.63 and 0.11. Two runs, compared across time within one trajectory, do not make a causal
test. Part I is that test.

## Part I — intervention: inject free vortices at fixed E, N, P versus an energy-matched phonon control

**Bases.** The saved equilibrated final states of round 1:
* `e0.90_s11_t4000_final.npy` and `e0.90_s12_t4000_final.npy` (ordered, T ≈ 0.45, condensate ≈ 0.63);
* `e0.60_s11_t4000_final.npy` (T ≈ 0.11, condensate ≈ 0.91).

**Arms**, from each base:
* **V (vortex arm).** Imprint 4 vortex–antivortex pairs:
  * pair separation `d = 16` (= L/4) on a 2×2 arrangement, with alternating dipole orientation so that `Σ q_j r_j = 0`;
  * the phase is the exact doubly periodic one, `θ = Σ_j q_j Im log ϑ₁(π(z − z_j)/L | τ = i)`, which is single-valued on the torus when `Σ q_j = 0` and `Σ q_j r_j = 0`;
  * the amplitude is multiplied by the core factor `Π_j ρ_j/√(ρ_j² + 2)`, with `ρ_j` the periodic distance;
  * then project, and renormalise to the base norm.
* **P (phonon control).** Add `ε·P[η]`, with `η` a random complex field supported on `|k| ∈ [0.2, 1] k_cut`. Renormalise to the base norm, and choose `ε` by bisection so that `E_P = E_V`.
* **0 (untouched)**, for the two e = 0.90 bases only: the base continued with no change.

That makes 8 runs. Each runs to `t = 1500`, sampling every Δt = 10, with block averages over 100 time units.

**Controls (must pass before any arm is compared).**

| # | Statement | Criterion |
|---|---|---|
| C1 | The winding detector (`VortexWinding.lean` rule) finds exactly the imprinted 8 vortices, with the right charges, when the V imprint is applied to the uniform state | exact |
| C2 | Energy matching | `|E_V − E_P| / E_V ≤ 1e-4`; norm equal to `1e-10` |
| C3 | Momentum | `|P_V|/N` and `|P_P|/N` ≤ `0.05 · 2π/L` |
| C4 | Arm 0 is stationary | first- and last-block condensate agree within 0.05 |

**Predictions (per base, comparing V and P over the block average `t ∈ [50, 250]`).**

| # | Statement | Criterion |
|---|---|---|
| I1 | Free vortices suppress the condensate | `cond_V < cond_P − 0.15` (e = 0.90 bases); `cond_V < cond_P − 0.15` (e = 0.60 base) |
| I2 | The thermometer is blind to it | `|T_V − T_P| / T_P ≤ 0.05` |
| I3 | The TDA instrument sees it | `Q_V ≥ Q_P + 0.2` |
| I4 | g₁ coherence is lost | `η_V ≥ 1.5 η_P`, with η from the noise-aware window of Part IV |
| I5 | Reported, not predicted | whether V relaxes to P by `t ∈ [1000, 1500]` (condensate within 0.05); and how the condensate difference tracks the difference in vortex count block by block |

Verdict: I1–I4 PASS/FAIL per base. The causal statement "at fixed E, N, P and measured T, the vortex
topology sets condensate and coherence" is claimed only if I1, I2 and I4 pass on all three bases.
**Literature status:** the underlying physics is standard; I claim no novelty. Examples:
* phase imprinting of vortices in BECs is an established technique;
* the destruction of quasi-long-range order by free vortices is the BKT mechanism itself.

What is new to this project is the controlled, energy-matched comparison with its own instruments.

## Part II — a finer look at the jump: a heating ladder from the ordered state

Round 1's jump sat between e = 0.90 and 1.20, one grid step, and round 1 showed that quench starts leave
vortices that do not relax in `t = 1500`. Round 2 therefore starts every point from an ordered state and
heats it.

* **Bases:** the two e = 0.90 t = 4000 finals.
* **Heating:** the P-arm construction, targeting `e ∈ {1.00, 1.05, 1.10, 1.15, 1.20}`. That gives 2 seeds × 5 = 10 runs, each with a transient of 500 and sampling over `[500, 1500]`.

| # | Statement | Criterion |
|---|---|---|
| C5 | Ladder vs quench at e = 1.20: `n_s λ²` and η agree with round 1's e = 1.20 row | within 25 % and 20 %, respectively |
| L1 | `n_s λ² = 4` crossing located within the ladder | the crossing lies strictly between two ladder energies; report `T_BKT` |
| L2 | η at the crossing | `0.25 ± 0.08` |
| L3 | `η · n_s λ² = 1` at every ladder energy with `n_s λ² > 4` | within `[0.75, 1.33]` |

## Part III — finite size (round 1's B5, not run there)

* **Setup:** `L = 32`, grid 64² (same `dx`, so the same physical cutoff).
* **Runs:** quench starts at `e ∈ {0.90, 1.00, 1.10, 1.20, 1.40}`, 3 seeds, `t = 4000` (round-1 A3 lesson), sampling over the last 1000.
* **Admission:** A4 (`R_L ≤ 1.25`, `R_T ≤ 1.1 R_L`).

| # | Statement | Criterion |
|---|---|---|
| F1 | The `n_s λ² = 4` crossing temperature at L = 32 vs L = 64 (the Part II value) | reported; BKT predicts a slow (logarithmic) drift, with the smaller box crossing at a **higher** T. PASS if `T_BKT(32) ≥ T_BKT(64)` |
| F2 | The stiffness drop is sharper in the larger box | the slope `|d(n_s λ²)/dT|` at the crossing is larger at L = 64 than at L = 32 |

## Part IV — analysis change fixed now: the noise-aware g₁ window

Round 1's B1/D3 failures came from fitting g₁ where it had reached its noise floor. From round 2 on:
* g₁ is fitted on `r ∈ [2, r_max]`, with `r_max = min(L/4, first r where g₁ < 0.05)`;
* a fit with fewer than 6 points is reported as "no decay law measurable" and neither law wins.

Round 1's data will be **re-analysed** with this window, labelled as a post-hoc re-analysis, and the
original verdicts stay on record.

## Not in this round

* A second cutoff (B4's open item).
* Any Lean.
* Any claim about helium, astrophysics or the Fricke involution. Round 1 settled that the physical BKT point is not the self-dual point.

Compute: about 8 + 10 runs at 128², plus 15 at 64² (t = 4000), ≈ 6–7 h on this machine.
