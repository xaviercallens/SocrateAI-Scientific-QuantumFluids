# Results, round 4: the sector versus the pairs

Pre-registration `PGPE_R4_PREREG.md` (amendments R4-A0–A2). Part A data `data/generated/cosmo/random_phase_halo*.json`;
Part B data `data/generated/pgpe/r4/`, log `r4.log` (launched automatically after round-3 Part C).

## Part A — Hui et al.'s random-phase halo model read with our instrument (complete)

L = 64, N = 512, λ_dB = 4, expected density π/λ_dB² = 0.1963.

| # | 20 realisations (run before the commit, R4-A0) | 100 realisations (R4-A2) | verdict |
|---|---|---|---|
| A1 n_v/(π/λ²) | 0.987 (density 0.1937 ± 0.0042) | 0.990 | **PASS** (Hui et al. 2020's 2D density reproduced to 1 %) |
| A2 fraction with \|q\| ≥ 2 | 0 | 0 | **PASS** (only ±1 windings) |
| A3 Var W(R) ∝ R^α | α = 1.012 | α = 1.004 | **PASS** on α: perimeter law, not area law — a window sees only the pairs its boundary cuts |
| A3 ⟨W(R)⟩ = 0 | pooled s.e.m. (as written): fail at R = L/2 (−0.124 ± 0.032); independent s.e.m. (R4-A1): −0.124 ± 0.053, 2.3 σ, fail | means 0.011, 0.002, −0.029, 0.006, −0.007 with independent s.e.m. 0.010–0.031: all < 2 σ | **FAIL as written** (the pooled s.e.m. is not a valid error for overlapping windows); **PASS under R4-A1 with 100 realisations** |
| A4 imposed sector W₀ ∈ {1, 3, 6} | W_x (median over rows) = W₀ exactly; n_v ratio 1.000; max density change 10⁻²² | — | recorded (an identity of the model): the phase instrument reads the sector, the density does not see it, the vortex count does not change |

**Reading.** Our plaquette instrument reproduces the published vortex density of the random-phase halo model to
1 %, finds only unit windings as Hui et al. state, and measures what `ScaleResolvedWinding` predicts: the net
winding of a window of side R fluctuates like its perimeter (α ≈ 1.0), so at R ≫ λ_dB the interference vortices
are dipoles whose net charge averages to zero — they are pairs, not a sector. A4 shows the instrument reading an
imposed sector exactly while the density is untouched to machine precision. The one honest blemish: the A3 mean
test was written with an invalid error bar; corrected (R4-A1) and tested on more samples (R4-A2), it passes; the
fail-as-written is recorded.

## Part B — torus PGPE (running after round-3 Part C)

Construction checks before launch (no evolution): on all three bases the corrected 16-pair generator gives torus
winding (0, 0) with 30/38/36 vortices detected (neutral); the boost gives (3, 0); the boost alone retains 153/84/85
of the 177.8 superflow energy (the projector clips the shifted bath edge), restored by `heat` to E₀ + 177.8 exactly
(prereg arm definition); S_band(V3)/S_band(0) at t = 0 = 1.007/1.053/1.023; f_K = 0.91/0.57/0.64.
