# Results, round 2: the energy-matched intervention (Part I), the heating ladder (Part II), finite size (Part III)

Pre-registration `PGPE_R2_PREREG.md` (f8e9773) with amendments R2-A1 (after controls, before arms),
R2-A2 (before output), R2-A3 (pre-data, at 70 min). Data `data/generated/pgpe/r2/*.json`, log
`data/generated/pgpe/r2.log`, analysis `exploration/pgpe/analyze_r2.py`, figure
`paper/figures/causal_intervention.pdf`. Parts II and III: **pending** (runs in progress).

## Part I — intervention: four free vortex pairs vs the same energy as phonons

All controls passed before any arm was run (C1 exact, C1b periodicity 0 vs 0.294524 as predicted, C2
`|ΔE|/E ≤ 2e-16`, C3 `|P|/N ≤ 0.025·2π/L`); C4 (arm 0 stationary) passed on both e = 0.90 bases
(condensate first/last block 0.625/0.641 and 0.660/0.660). Energy drift over t = 1500: `≤ 2.2e-7`.

### Pre-registered verdicts (window t ∈ [100, 300), per R2-A2)

| Base | I1: cond_P − cond_V ≥ 0.15 | I2: \|T_V − T_P\|/T_P ≤ 0.05 | I3: Q_V − Q_P ≥ 0.2 | I4: η_V/η_P ≥ 1.5 |
|---|---|---|---|---|
| e = 0.60 s11 | **0.734** PASS | 0.161 FAIL (T_V < T_P) | not evaluable (arm P has no vortices, Q undefined) | **43.7** PASS |
| e = 0.90 s11 | **0.565** PASS | 0.055 FAIL (T_V < T_P) | **0.656** PASS | **10.7** PASS |
| e = 0.90 s12 | **0.488** PASS | 0.092 FAIL (T_V < T_P) | **0.553** PASS | **8.6** PASS |

Window means: V/P condensate 0.168/0.902, 0.073/0.638, 0.139/0.627; V/P thermometer 0.086/0.102,
0.392/0.415, 0.389/0.429; V/P η 0.977/0.022, 1.078/0.101, 0.937/0.108 (V exponential, P algebraic on
every base). Arm 0 over the same window: T = 0.462, 0.463; condensate 0.647, 0.662.

**The pre-registered composite claim** ("at fixed E, N, P *and measured T*, the vortex topology sets
condensate and coherence", requiring I1, I2, I4 on all three bases) **is not made**: I2 fails on all
three bases.

### The I2 failure, read against R2-A3 (pre-data) and then post hoc

R2-A3 fixed three readings. The observed one is none of them: `T_V < T_P` on every base, by 5.5 %,
9.2 % and 16 % — **more** than the energy surplus (1.5 %, 1.5 %, 3.3 %). So this is not energy
bookkeeping alone, and it is reported as a third case.

Post-hoc checks, both labelled as such:
1. *Coherent core spectrum contaminating the thermometer window?* **Refuted**: the high-k occupation of
   the imprint applied to the uniform state is `7×10⁻⁵`, against a thermal occupation of
   `3×10⁻² – 1.3×10⁻¹` in the same window (500–2000× smaller).
2. *Doppler smearing by the vortex flow?* The two thermometer windows disagree by similar amounts in V
   and P (lo/hi 0.83–0.93 vs 0.88–0.94): **inconclusive**.
3. *Comparison with the untouched arm.* P is warmer than arm 0 by +3.5 % and +1.5 % (the surplus heats
   the bath, as R2-A3 said); V is **colder than arm 0** by −4 % on both e = 0.90 bases. With total energy
   conserved to `2×10⁻⁷`, the thermal energy lost by the bath went into the vortex system: ⟨N_v⟩ in V
   is 14–16 against 8 imprinted plus ≈ 5 thermal, i.e. the injected configuration nucleated further
   pairs and scrambled the condensate into low-k quasi-condensate structure, drawing on the bath.

The reading that survives: the thermometer is probably **correct**, and the topological configuration
**cools the bath**. That cooling works *against* the observed effect — a colder gas should carry more
condensate, and V carries 5–10× less. So the difference between the arms cannot be attributed to
temperature; the temperature difference has the wrong sign for that. This is a stronger statement than
the pre-registered one, and it is post hoc.

### Effect per unit energy (the pre-declared effect size)

Same ΔE in V and P. Condensate change relative to arm 0 (e = 0.90): V −0.574 and −0.523; P −0.009 and
−0.035. η: V ×10.9 and ×10.4 relative to arm 0; P ×0.99 and ×1.2. The same energy produces a 15–60×
larger condensate effect and a 9–11× larger coherence effect when delivered as topology.

### I5 (reported, not predicted)

* **No relaxation within t = 1500** on any base: late-window (t ≥ 1000) condensate V/P = 0.289/0.891,
  0.085/0.643, 0.061/0.661.
* **At e = 0.60 the eight imprinted vortices persist for the whole run with zero annihilations**
  (⟨N_v⟩ = 8.0 in every block). At T = 0.1 the pairs of separation 16 are protected for at least 1500
  time units: topological protection observed directly.
* In the last three blocks at e = 0.60 the condensate recovers (0.29 → 0.45) while N_v stays 8.0 and
  Q falls (0.88 → 0.67): the dipoles are contracting. The scale-resolved winding at large R changes,
  the count does not — thought experiment B in the data.
* Block-by-block correlation of Δcond with ΔN_v: −0.26 (s11), +0.58 (s12), undefined at e = 0.60
  (N_v constant). No consistent tracking of the count; the condensate follows the *arrangement*, not
  the number.
* The transverse-current estimator is invalid in V (R_T = 5.5–38, "n_n > n"), as in round 1 when free
  vortices are present; reported, not used.

## Part II — heating ladder: pending

## Part III — finite size L = 32: pending

## Part IV — post-hoc re-analysis of round 1 with the noise-aware g₁ window

Fitting only where g₁ > 0.05 removes the artifact at e ≥ 2.2 (no law measurable there, as it should
be). It does not rescue D3: at e = 2.0 the window is [2, 5.25], a factor 2.6 in r, and both laws fit;
the last "algebraic" energy is 2.0 with η = 2.0. D3 stays FAIL. B1's high-T half becomes "no law
measurable" rather than a false algebraic win.
