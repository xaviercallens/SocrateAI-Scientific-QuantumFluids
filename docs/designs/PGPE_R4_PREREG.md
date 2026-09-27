# Pre-registration, round 4: the sector versus the pairs — does a density observable read the winding?

Follows `docs/designs/COSMOLOGY_SECTORS_PROPOSAL.md` §1 and §4 (owner: "oui je le veux", 2026-09-25 22:50).
Committed before any round-4 run. Same solver, same units, same bases as rounds 2–3. Changes after this
commit are dated amendments. Part A is a numpy model with a published known answer; Part B is the torus PGPE.

## The question, transplanted from the halo to the torus

In wave dark matter, lensing reads the projected **density**. A vortex lattice in a rotating halo (Zhou et al.
2025) has net circulation W ≠ 0 — a sector; interference rings (Hui et al. 2020) have net winding 0 — pairs.
Both have cores that are density holes. The sector reading (`ScaleResolvedWinding`: W(R) = net enclosed charge)
predicts: **a density observable reads cores, i.e. pairs; the sector is read only by the phase (W at scale R) or
by the momentum distribution.** On the torus a sector is a uniform superflow with no core at all, so the
prediction becomes sharp: the sector changes the density spectrum by nothing, the pairs change it by much, and a
sector added on top of pairs changes their density signature by nothing.

## Part A — Hui et al.'s random-phase model with our instrument (known answer: π/λ_dB² vortices per area)

`exploration/cosmo/random_phase_halo.py`. Ψ = Σ_k A_k e^{iB_k} e^{ik·x}, A_k ∝ exp(−k²/k₀²), B_k uniform,
2D periodic box L = 64, N = 512 (dx = 0.125), λ_dB = √2·2π/k₀ = 4 (k₀ = 2.221); 20 realisations. Vortices by
the plaquette rule of `VortexWinding.lean`; W(R) = net charge in a square window of side R.

| # | Statement | Criterion |
|---|---|---|
| A1 | vortex density is Hui's | mean over realisations of n_v/(π/λ_dB²) ∈ [0.85, 1.15] (Hui et al. 2020 §4.2: ⟨n⟩ = π/λ_dB² in 2D) |
| A2 | only unit windings | fraction of detected plaquettes with |q| ≥ 2 is < 10⁻³ |
| A3 | pairs are invisible at large R: perimeter law | Var W(R) over windows and realisations, fitted as R^α on R ∈ [2λ, L/2]: α ∈ [0.8, 1.2] passes; α ≥ 1.6 (area law) fails; ⟨W(R)⟩ compatible with 0 (|mean| < 2 s.e.m.) |
| A4 | instrument check on an imposed sector | multiply Ψ by e^{2πi W₀ x/L}, W₀ ∈ {1, 3, 6}: the row-wise loop sum (median over rows) returns W₀ exactly, n_v unchanged, density field unchanged to machine precision (this is an identity of the model; it is recorded to show what the instrument reads, not as physics) |

## Part B — torus PGPE: four arms on three bases

Bases `e0.60_s11`, `e0.90_s11`, `e0.90_s12` (round-1 finals). 128², L = 64, t = 1500, positions and the density
spectrum saved every 10, blocks of 100. Twelve runs, ≈ 1.8 h each at 6 processes → two batches; **launched after
round-3 Part C finishes** (same machine, 8 cores).

**Arms.**
* **0**: the base continued.
* **V3**: the base multiplied by e^{2πi·3x/L} (a winding-3 torus current, +½N(2π·3/L)² = 177.8 of pure superflow
  energy, the value observed as the E_inc plateau excess of round-3 s12), projected, renormalised. The projector
  clips the far edge of the shifted bath (a construction check before any run found 84–153 of the 177.8 surviving,
  base-dependent), so the arm is completed by `heat` (random phonons on |k| ∈ [0.2, 1] k_cut, as the round-2 P arm)
  to E₀ + 177.8 exactly: **V3 = the base's energy content + the superflow energy**. The clipped and restored
  energies are recorded per run.
* **P16**: 16 neutral pairs of separation 8 imprinted with the **corrected generator** `many_pair_config_exact`
  (unwrapped positions, Σq = 0 and Σq r = 0 exactly; the round-3 generator wrapped positions modulo L and thereby
  imprinted accidental windings, amendment R3-A1). The imprint's torus winding is measured and must be (0, 0).
* **V3P16**: P16 then V3 (boost, then heat to E(P16) + 177.8).

**Instruments.** Density spectrum S(k) = ⟨|ρ_k|²⟩ shell-averaged; the band statistic S_band = Σ_{0.3 ≤ |k| ≤ 1.2}
|ρ_k|² (the core/pair scale: ξ = 1, d = 8; k_cut = 1.57), averaged over the stated window. Torus winding W_x =
median over rows of the loop sum of principal-value phase differences along x, divided by 2π (integer per row).
Momentum fraction f_K = |c_K|²/Σ|c|² at K = (2π·3/L, 0). N_v, T_b, E_inc as in round 3.

| # | Statement | Criterion |
|---|---|---|
| B1 | the sector is invisible in density | over t ∈ [500, 1500], \|S_band(V3)/S_band(0) − 1\| ≤ 0.15 on every base |
| B2 | the pairs are visible in density | over t ∈ [0, 300], S_band(P16)/S_band(0) − 1 ≥ 0.30 on every base |
| B3 | the sector is read by the phase and the momentum | on the e = 0.90 bases, W_x = 3 on ≥ 95 % of samples in V3 and V3P16, and W_x = 0 on ≥ 95 % in 0 and P16; f_K ≥ 0.15 in V3 over t ∈ [500, 1500]; at e = 0.60 the same quantities are reported (round-3 e0.60 lost its winding by slips) |
| B4 | density reads cores, not net winding | over t ∈ [0, 300], \|S_band(V3P16)/S_band(P16) − 1\| ≤ 0.15 on every base — the same pairs carry the same density signature whether or not a sector is present |
| B5 | reported, not predicted | N_v(t) in P16 vs V3P16 (does the current change the pairs' annihilation?); W_x(t) in V3P16 (does the presence of pairs let the winding slip?); T_b(t); energy drift |

**What a pass means.** B1 + B2 + B4 together: a density-only observable (a lensing map) cannot distinguish a
halo with net circulation from one without at equal core content; the sector is a phase/momentum observable.
Transplanted to Zhou et al. vs Hui et al.: what lensing can see is the *regularity* of a lattice (a spatial
correlation of cores) or a *count* of cores, never W itself; the claim "vortices seen ⇒ rotating condensate
sector" needs the phase, or a regularity statistic, as its instrument.

**What a fail means.** If B1 fails (the current changes the density spectrum at fixed core content), the
superflow couples to density through the projector or through the interaction in a way the reading did not
anticipate, and the "sector invisible in density" statement is false on this torus; reported as such.

## Kill rules

* Energy drift > 10⁻⁵ on any run → that run void.
* `many_pair_config_exact` imprint with W_x or W_y ≠ 0 on any base → Part B void until the generator is fixed.
* Part A: A1 fails → the instrument does not reproduce the published density; A3/A4 not evaluated.

## Not in this round

Gravity, rotation, three dimensions, any halo simulation (Zhou et al. and Hui et al. have them). Any
cosmological number. Any Lean beyond what exists (the plaquette rule, W(R) = net charge).

## Amendments

**R4-A0 (2026-09-25 23:05, disclosure).** Part A (`random_phase_halo.py`, 20 realisations) was executed at 22:58,
after this document and the script were written but **before** this commit. The criteria A1–A4 were not changed
after the run. Recorded because the rule is "committed before any run" and it was not met for Part A.

**R4-A1 (2026-09-25 23:05, after seeing the 20-realisation result).** The A3 "mean compatible with 0" test used
the s.e.m. pooled over 200 windows per realisation; windows within a realisation overlap, so that s.e.m. is too
small (at R = L/2 it is the s.e.m. of essentially 20 values). The independent estimate uses the 20 per-realisation
means. Both are reported; the criterion (|mean| < 2 s.e.m.) is unchanged. With 20 realisations: α = 1.01 (pass);
mean at R = L/2 = −0.124 with pooled s.e.m. 0.032 (fail as written) and independent s.e.m. 0.053 (2.3 σ, fail).

**R4-A2 (2026-09-25 23:08).** Rerun with 100 realisations (`NREAL=100`, output `random_phase_halo_n100.json`),
same criteria, to test whether the 2.3 σ offset is a fluctuation of 20 samples. The 20-realisation file is kept.

## Amendment R4-A3 (2026-09-26, literature review; no criterion changed)

The density π/λ_dB² and the screening behind A3 are not specific to dark matter: they are Berry & Dennis's
1998–2003 theorems for any isotropic random wave field (Berry & Dennis 2000, Proc. R. Soc. A 456, 2059, DOI
10.1098/rspa.2000.0602; Dennis 2003, J. Phys. A 36, 6611, DOI 10.1088/0305-4470/36/24/301; Foltin 2003, DOI
10.1088/0305-4470/36/6/316) — cited now as the primary source alongside Hui et al.'s numerical confirmation of
them in the wave-dark-matter context. One precision correction: the screening is **power-law, not exponential**
(Houston, Gradhand & Dennis, arXiv:1612.01839, show the naive "screening-length" second moment diverges for the
isotropic random-wave model); our A3 criterion (a fitted power α, not a fitted length scale) already matches
this, no change to the criterion. On our doubly-periodic torus, the boundary-leak exception found in ring-BEC
experiments (Eckel et al. 2014, Nature, DOI 10.1038/nature12958 — a pair with one member crossing a physical
boundary is the microscopic mechanism for a discrete change in net winding) does not apply: there is no boundary
for a member to cross, so "pairs are invisible to W(R)" is expected to hold without qualification here; the
caveat is recorded for any future non-periodic (halo) extension of this protocol.
