# Pre-registration: are the negative-stiffness runs Onsager-clustered vortex states?

Filed 2026-10-04, **before** any of the observables below has been computed on any run. Analysis only — no new
simulation. Data: the vortex positions already on disk for round 3 Parts C (`L = 128`, window `t ∈ [3000, 4000]`),
C2 (`L = 128`, `[6000, 7000]`) and C3 (`L = 192`, `[6000, 7000]`), 100 samples per run, 18 runs.

## The anomaly

Across these 18 runs, seven reach a state with transverse current fluctuations larger than longitudinal ones
(`R_T > R_L`, hence a negative superfluid fraction `n_s/n = 1 − J_T/J_L`), with exponential `g1` and a depleted
condensate — while carrying **the same number of vortices** as their healthy partners at the same energy (C2
`e = 1.00`: 81 vs 77; C3 `e = 1.10`: 439 vs 433). Part C2 showed the defect is cured, at `L = 128`, by doubling the
warm-up in three of four cases; at `L = 192` it reappears in two of six runs. Its nature has never been diagnosed.

Class **A** (anomalous, `n_s/n < 0` from each run's own record): Part C `e1.00_s11, e1.00_s12, e1.10_s11,
e1.20_s11`; C2 `e1.00_s11`; C3 `e1.00_s11, e1.10_s11` — 7 runs. Class **N**: the other 11. (Fixed now from the
existing run records; C3 `e1.20_s12`, rejected for `R_L > 1.25` with positive `n_s/n`, is in N.)

## Hypothesis H-Ons

The A runs are **Onsager-clustered vortex states**: the same vortices, arranged with like signs grouped into
box-scale clusters — net vortex charge separated at the scale of the box — whose large-scale rotational flow is
the excess transverse current. Mechanism proposed: the random initial state's inverse energy cascade builds the
clusters (Billam et al. PRL 112, 145301 (2014); Simula et al. PRL 113, 165302 (2014); Gauthier/Johnstone 2019 in
experiment), and their dissolution into the thermal pair gas is slower in a larger box, which would make the
`L`-dependent equilibration failure of Parts C/C2/C3 a single phenomenon.

Rivals: **H-plasma** (a locally disordered, unbound vortex plasma — no charge separation, `S_q ≈ 1`, `f_ss ≈ ½`)
and **H-sector** (a hidden net torus winding — checked by the final-field winding, control C0).

## Observables (per sample, then averaged over the run's 100 samples)

1. **Vortex charge structure factor at the box scale**, `S_q(k₁) = ⟨|Σ_j q_j e^{i k·r_j}|²⟩ / N_v`, averaged over
   the four `k` of the first shell `|k| = 2π/L`. Uncorrelated charges: 1. A screened (bound-pair) gas: ≪ 1.
   Box-scale charge separation: ≫ 1. Note stated in advance: the transverse current at the lowest shell is the
   flow of exactly this charge density (`v_T(k) ∝ ρ_q(k)/k`), so a link between `S_q(k₁)` and `R_T` is close to
   kinematic; the content of P1 is that the anomaly is **carried by the vortices** (not by phonons) and that it
   is a box-scale charge separation.
2. **Same-sign nearest-neighbour fraction** `f_ss` (minimum-image distances): the fraction of vortices whose
   nearest vortex has the same sign. Bound-pair gas: well below ½; random: ≈ ½; clustered: above the N runs.
3. **Point-vortex energy against random placement**: `z_E = (E_pv − ⟨E_rand⟩)/σ_rand`, with `E_pv` the torus
   Weiss–McWilliams energy already stored, and `E_rand` the energy of the same charges placed uniformly at random
   (8 placements per sample, 10 samples per run, one per block). `E` above the random value means `dS/dE < 0`
   at the state: a **negative vortex temperature** (Onsager 1949).
4. **Onsager dipole** `D` (`observables.onsager_dipole`, as used in `onsager_dipole_analysis.py`) — reported, not
   used in a criterion (on a torus it is dominated by the two centroids' noise when `N_v` is large).

## Predictions and criteria (frozen)

`AUC(X)` = probability that a random A run exceeds a random N run on X, computed **within each box size**
(`L = 128`: A = 5, N = 7; `L = 192`: A = 2, N = 4).

- **P1 (charge separation).** `AUC(S_q(k₁)) ≥ 0.9` at both sizes, and `S_q(k₁) > 1` in at least 6 of the 7 A runs.
- **P2 (like-sign clustering).** `AUC(f_ss) ≥ 0.9` at both sizes.
- **P3 (negative vortex temperature — the strong form).** `z_E > 0` in at least 6 of 7 A runs **and**
  `z_E < 0` in at least 10 of 11 N runs.
- **P4 (history: the cure is cluster dissolution).** The three trajectories rejected in Part C and admitted in C2
  (`e1.00_s12, e1.10_s11, e1.20_s11`; same seed, same initial state, same integrator, later window) have
  `S_q(k₁)` lower in C2 than in C for **all three**; the one that stays rejected (`e1.00_s11`) has the highest
  `S_q(k₁)` of the six C2 runs.
- **C0 (control).** All `L = 192` final fields have torus winding `(0, 0)` (as all twelve `L = 128` ones do).

**Verdicts.** P1 ∧ P2 → *the negative-stiffness runs are box-scale clustered vortex states* (H-Ons, weak form);
additionally P3 → *they are Onsager negative-temperature states*; P4 → *the warm-up cure is the dissolution of
these clusters*. **Kill:** `AUC < 0.7` for both `S_q(k₁)` and `f_ss` at either size refutes H-Ons;
`S_q(k₁) ≤ 1` and `f_ss` within 0.02 of ½ in the A runs would instead support H-plasma. C0 failing on an A run
makes that run a sector case, analysed separately.

No threshold will be changed after the computation. Small samples (7 vs 11 runs, one or two seeds per point) are
stated now: the criteria are about separation of classes, not p-values.
