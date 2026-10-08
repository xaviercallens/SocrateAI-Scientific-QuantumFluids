# Friction law against cutoff — results log (`PGPE_FRICTION_LAW_PREREG.md`; FL3 in `FRICTION_LAW_THEORY_NOTE.md`)

Started 2026-10-08 after the counterflow control refuted the box mechanism (CLAIM-092). Everything below is appended
as it lands; verdicts FL1/FL2 are taken only when all runs of both arms are in. Data: `data/generated/pgpe/transport/fl/`.

## Bases (energy scan, heat route from the equilibrated e = 0.60 state; 1000 t.u. transient + 500 measured)

| cutoff | grid | e | T | n_s/n | ρ_n/ρ | raw n_v | admitted (n_v < 0.5) | used |
|---|---|---|---|---|---|---|---|---|
| k_cut = 2π/3 | N = 128, dx = ξ/2 | 0.545 | 0.100 | 0.9846 | 0.0154 | 0.00 | yes | **T ≈ 0.11 arm** |
| | | 0.56 | 0.137 | 0.9829 | 0.0171 | 0.00 | yes | spare |
| | | 0.60 | 0.216 | 0.9603 | 0.0397 | 0.00 | yes | **T ≈ 0.22 arm** |
| | | 0.62 | 0.273 | 0.9477 | 0.0523 | 0.00 | yes | spare |
| | | 0.66 | 0.362 | 0.9275 | 0.0725 | 0.08 | yes | spare |
| k_cut = 2π | N = 256, dx = ξ/4 | 0.80 | 0.082 | 0.9577 | 0.0423 | 0.00 | yes | spare |
| | | 0.95 | 0.127 | 0.9291 | 0.0709 | 0.04 | yes | **T ≈ 0.11 arm** (15 % above target) |
| | | 1.10 | 0.173 | 0.9198 | 0.0802 | 0.08 | yes | spare |
| | | 1.25 | running | | | | | **T ≈ 0.22 arm** (if admitted) |
| k_cut = π (reference, A1) | N = 128 | 0.60 / 0.70 / 0.80 | 0.110 / 0.220 / 0.353 | 0.971 / 0.947 / 0.906 | 0.029 / 0.053 / 0.094 | 0 | yes | published arm |

Observation already worth recording: at equal temperature the normal fraction grows strongly with the cutoff
(T ≈ 0.11–0.13: ρ_n/ρ = 0.015, 0.029, 0.071 at k_cut = 2π/3, π, 2π), as the Landau sum over more modes requires.
FL2 asks whether α tracks it.

## Known answers (T = 0 control of A1 at each cutoff: uniform condensate, antiparallel d₀ = 10, 400 t.u.)

| cutoff | α̂ (regression / energy) | 1 − α̂′ | η̂ | pair speed | separation oscillation |
|---|---|---|---|---|---|
| π (G1, published) | 4.1×10⁻⁴ (energy) | 0.9986 | −1×10⁻⁶ | 0.1065 | 9.7 ↔ 10.6 |
| 2π/3 | 1.8×10⁻⁴ / 3.8×10⁻⁴ | 0.9995 | 2.9×10⁻⁵ (clause ≤ 2×10⁻⁵: **marginal**, reported) | 0.1068 | identical to 0.5 % |
| 2π | 2.4×10⁻⁴ / 4.7×10⁻⁴ | 0.9991 | 0 | 0.1065 | identical to 0.5 % |

The T = 0 dynamics of the pair is cutoff-independent to 0.3 % in speed and to 0.5 % in the four-vortex separation
oscillation: the instrument's known answers hold at all three cutoffs. The η floor at 2π/3 is 1.5 times the
clause; it is 10–100 times below the thermal η of the campaign and is carried as a caveat, not a failure.

## Thermal runs (appended as they land; `analyze_transport.summarise`, registered cuts)

### k_cut = 2π/3, T = 0.100 (ρ_n/ρ = 0.0154), d₀ = 8 — first two seeds (08:30, preliminary)

α_energy = 0.0044 ± 0.0011, α_regression = 0.0048 ± 0.0011, 1 − α′ = 1.0169 ± 0.0009, η = 3.8×10⁻⁴,
MSD exponent 0.74. One of the two runs ended in a partner exchange (d → 41; the registered validity cut applies).
**c = α/(ρ_n/ρ) = 0.29–0.31**, against 0.232 at k_cut = π and the Born rival's 0.155 at this cutoff. Two runs
only; the direction (coefficient *up* when the short-wavelength modes are removed) is opposite to the Born
scaling, which predicted a fall.

### k_cut = 2π/3, T = 0.100 (ρ_n/ρ = 0.0154) — arm complete (10:10, 6 runs, all to t = 2000)

| | all 6 | d₀ = 8 (3) | d₀ = 12 (3) |
|---|---|---|---|
| α_energy | 0.0049 ± 0.0008 | 0.0048 ± 0.0008 | 0.0065 ± 0.0009 |
| α_regression | 0.0058 ± 0.0007 | 0.0052 ± 0.0008 | 0.0078 ± 0.0011 |
| 1 − α′ | 1.0170 ± 0.0009 | | |
| η | 3.2×10⁻⁴ ± 0.5 | | |
| MSD exponent | 0.73 ± 0.02 | | |

**c = α/(ρ_n/ρ) = 0.32 ± 0.05 (energy), 0.38 ± 0.05 (regression)** against 0.232 ± 0.014 at k_cut = π: the
coefficient is 40–60 % *higher* at the coarser cutoff. Direction opposite to the Born rival (0.155, i.e. −33 %);
magnitude outside FL2's 20 % band on the high side. Two things to carry into the reading, not to explain away:
(i) α is larger for d₀ = 12 than for d₀ = 8 by ~35 % here, whereas at k_cut = π it was independent of pair size;
(ii) α′ = −0.017 ± 0.001, a small transverse coefficient of anti-Iordanskii sign, where k_cut = π gave zero within
1 %. Both are at one temperature of one cutoff; the T = 0.216 arm (running) and the fine arm decide whether they
are cutoff effects.

L = 128, e = 0.60 base (for the bottleneck direction) finished: T = 0.1097, n_s/n = 0.969, no thermal vortex (11.8 h).
