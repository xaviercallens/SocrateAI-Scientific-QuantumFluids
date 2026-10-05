# Results: the negative-stiffness runs are not Onsager clusters — they carry O(1) unscreened vortex charge at the box scale

Pre-registration `PGPE_ONSAGER_PREREG.md` (commit 3556752, filed before computation). Analysis
`exploration/pgpe/analyze_onsager.py` → `data/generated/pgpe/onsager_clusters.json`; post hoc
`exploration/pgpe/onsager_posthoc_vortex_current.py` → `onsager_posthoc.json`. 18 runs (round 3 Parts C, C2, C3),
100 vortex-position samples each, no new simulation. Date 2026-10-04.

## Pre-registered verdicts

| | criterion | result |
|---|---|---|
| P1 | charge separation: AUC(S_q(k₁)) ≥ 0.9 at both sizes and S_q(k₁) > 1 in ≥ 6/7 A runs | **FAIL**: AUC 1.00 (L = 128), 0.75 (L = 192); S_q(k₁) = 0.001–0.018 in **every** run, A or N |
| P2 | like-sign clustering: AUC(f_ss) ≥ 0.9 at both sizes | **FAIL**: AUC 0.91 (128), 0.50 (192); f_ss = 0.3–1.6 % in every run |
| P3 | negative vortex temperature: z_E > 0 in ≥ 6/7 A, < 0 in ≥ 10/11 N | **FAIL**: z_E = −7.3 to −10.5 in **all 18** runs |
| P4 | the C → C2 cure lowers S_q(k₁) in all three cured trajectories; C2 e1.00_s11 highest | **PASS**: ×35, ×10, ×4 drops; e1.00_s11 is the highest of C2 (0.007 vs ≤ 0.0014) |
| C0 | L = 192 final fields at torus winding (0, 0) | **PASS** (6/6) |
| kill | AUC < 0.7 for both S_q and f_ss at either size | not triggered |

**H-Ons is refuted in both its weak and its strong form.** The anomalous runs contain no box-scale like-sign
clusters and no negative-temperature vortex configuration. All eighteen states — anomalous or not — are the same
kind of vortex matter: a **strongly screened, tightly bound pair gas** (nearest neighbour of opposite sign for
98–99.7 % of vortices; charge structure factor at the box scale 10²–10³ below that of uncorrelated charges; point-
vortex energy 7–10 standard deviations below random placement, i.e. a positive and fairly cold vortex temperature).
The rival H-plasma (`S_q ≈ 1`, `f_ss ≈ ½`) is refuted just as clearly. H-sector is excluded by C0.

## What the anomaly is (post hoc, labelled as such)

Point vortices of charge density `ρ_q(k) = Σ q_j e^{−ik·r_j}` drive a purely transverse current
`|J_T(k)|² = n²(2π)²|ρ_q(k)|²/k²`. Evaluated with `n = 1` on the same three shells `|k| = 1, √2, 2` (×2π/L) as the
current correlator, normalised the same way, this **parameter-free vortex-only `R_T`** tracks the measured `R_T`
across all 18 runs with **Pearson r = 0.996** (Spearman 0.977). In the seven anomalous runs
`R_T / R_T^vortex = 0.64 ± 0.04` (constant: an effective flowing density `n_eff ≈ 0.8`); in the eleven normal ones
it is 0.8–2.6, the vortex part being comparable to a phonon floor of ≈ 0.1–0.3.

So the negative-stiffness defect is **entirely carried by the vortices, and by a tiny part of them**: the residual,
unscreened vortex charge at the three longest wavelengths of the box, `|ρ_q(k)|² ~ 1` (one unit of net charge,
i.e. of order one vortex–antivortex pair separated by a distance comparable to `L`) against `|ρ_q|² ~ 0.1` in the
normal runs. Vortices whose nearest antivortex is farther than 4 healing lengths number 2–4 in the anomalous runs
and 0–1.2 in the normal `L = 128` runs (at `L = 192`, `e = 1.20` the dense normal runs reach 3.6–3.9, so this count
alone does not separate the classes). This is the Kosterlitz–Thouless picture made literal in a finite box: the
stiffness at scale `L` is destroyed by unbinding at scale `L`, and **a single box-scale pair suffices** to turn
`n_s/n` negative in the transverse–longitudinal estimator, while the hundreds of tightly bound thermal pairs are
irrelevant to it.

**Why it is a non-equilibrium remnant, and why it gets worse with `L`.** At `T ≈ 0.5–0.7` with `K ≈ 6–10`, the
Boltzmann weight of a pair of separation `~L` is `(L/ξ)^{−K}` (pair energy `2πn_s ln(L/ξ)`, `K = 2πn_s/T` in this programme's units) — `10⁻⁹` or less at `K ≥ 6`, `L/ξ ≥ 100`. A box-scale pair present
in these states is therefore left over from the relaxation of the random initial condition. In dissipative point-
vortex dynamics (thermal mutual friction `α`), a dipole of separation `d` moves at `Γ/(2πd)` and its members drift
together at `αΓ/(2πd)` each, so `d²` shrinks linearly and the pair lives `t ≈ π d₀²/(2αΓ) ∝ L²`. That gives one
mechanism for all three observations of round 3: Part C's failure at `L = 128` with `t_tr = 3000`, its cure by
`t_tr = 6000` (P4: the box-scale charge falls by 4–35× between the two windows of the same trajectories), and the
renewed failure at `L = 192` with the same `t_tr = 6000` — which `L²` scaling says should have been ≈ 13 500.

**Consequence for Part C3 (amendment R3-A3).** The three *admitted* `L = 192` runs also carry elevated box-scale
vortex charge: `R_T^vortex = 0.55–0.74`, against 0.08–0.44 for the admitted `L = 128` runs — at `e = 1.00`, 0.65
against 0.08 at the same temperature. A screened equilibrium pair gas gives an `L`-independent `R_T^vortex` (its
`|ρ_q(k)|²` scales as `k²`), so this jump is not equilibrium dielectric renormalisation; it is residual box-scale
charge. The lower `n_s/n` and hence the lower `ηK − 1` at `L = 192` are thus **mechanistically attributable to
incomplete equilibration**, which turns the caution recorded with the C3 verdict into an identified bias. The
pre-registered verdict ("saturation / non-monotone") is not changed — it was the outcome of the rule — but the
reading "the offset does not grow with `L`" should not be leaned on: the `L = 192` point is contaminated by the
same defect, in milder form, that admission removes in its strong form.

## What is claimed

- Pre-registered: the negative-stiffness states are **not** Onsager clusters, **not** negative-temperature states,
  **not** a vortex plasma, **not** a winding sector; the warm-up cure at `L = 128` coincides with a 4–35× fall of
  the box-scale vortex charge (P4).
- Post hoc: the transverse current anomaly is the flow of O(1) unscreened vortex charge at the box scale
  (r = 0.996, parameter-free); the admission filter is in effect a detector of box-scale vortex pairs.
- Interpretation, not established: slow decay of box-scale charge (a mutual-friction lifetime growing as `L^z`,
  `z ≈ 1.5–2`; the `L²` form is the AHNS/Bray dissipative one, see the literature gate below) as the cause of the
  size-dependent equilibration time. Tested by the prediction below.

Nothing here is new physics in itself (Kosterlitz–Thouless 1973; Ambegaokar–Halperin–Nelson–Siggia 1980 for
dissipative vortex-pair dynamics; the transverse-current definition of `n_s`). What is new is the diagnosis of a
specific, recurring numerical defect of finite-size BKT measurements with classical fields, with a parameter-free
quantitative account, and a mechanism that makes a testable prediction about how warm-up must scale with box size.

## Prediction for a follow-up run (registered here, before any such run exists)

Mechanism M: box-scale vortex pairs left by the initial relaxation shrink by mutual friction, lifetime `∝ L²`.
Test: **continue the six `L = 192` trajectories** from their `t = 7000` checkpoints (same integrator, no change)
to `t_end = 14 500`, sampling `[13 500, 14 500]` (`13 500 = 6000 × (192/128)²`).
- **E1:** admission (A4) **≥ 5/6**.
- **E2:** `R_T^vortex` of every admitted run **≤ 0.45** (the admitted `L = 128` range).
- **E3:** in the two anomalous runs (`e1.00_s11`, `e1.10_s11`), `R_T^vortex` falls by **≥ 2×** from the
  `[6000, 7000]` window.
- **Kill for M:** admission ≤ 3/6 at `t = 14 500`, or E3 failing in both anomalous runs (the defect would then be
  a long-lived metastable state, not slow annihilation).
- **Report only (no direction predicted):** R3-A3's offsets `ηK − 1` re-evaluated on the new window, alongside the
  `[6000, 7000]` ones; the R3-A3 verdict already recorded is not overwritten.

## Literature gate (2026-10-05, after the results above; changes their framing, not their numbers)

A prior-art search (full texts via alphaXiv) places each statement:

- **The vortex-only transverse current is a known quantity.** In the Coulomb-gas picture the helicity modulus is
  reduced by the variance of the vortex *polarisation* `P = Σ q_j r_j / N` and of the topological sector:
  Vallat & Beck, PRB 50, 4015 (1994); Faulkner, Bramwell & Holdsworth, JPCM 29, 085402 (2017), arXiv:1610.06692,
  Eq. 13; Faulkner's review arXiv:2412.12186. `|ρ_q(k)|²/k²` is the finite-`k` form of that polarisation term.
  The point-vortex spectrum built from `Σ κ_pκ_q J₀(k r_pq)` is in Bradley & Anderson, PRX 2, 041001 (2012).
  The transverse/longitudinal estimator `f_s = 1 − χ_T/χ_L` in PGPE, and **negative values of it**, are in
  Foster, Blakie & Davis, PRA 81, 023623 (2010), arXiv:0912.1675 (App. D, Fig. 2), where they are attributed to
  statistical noise in the `k → 0` extrapolation. **Not found in the literature:** attributing the negative or
  corrupted values to one residual, non-equilibrium box-scale pair, and using the vortex-only transverse current
  as a quantitative diagnostic of it. That is the part claimed here — phrased as: *the transverse-current anomaly
  is the finite-`k` Vallat–Beck/Faulkner polarisation term, carried by one non-equilibrium pair.*
- **The `L²` equilibration law is borrowed, not ours, and is probably not the right exponent for this dynamics.**
  Dissipative (model-A) XY: `t_eq ~ L² ln L` (Bray, Briant & Jervis, PRL 84, 1503 (2000), pair friction
  `∝ ln(R/a)` after Yurke et al. 1993; Jelić & Cugliandolo, J. Stat. Mech. P02032 (2011)). Conservative
  (Hamiltonian) XY: `t_eq ~ L²/ln L` (Nam, Baek, Kim & Lee, J. Stat. Mech. P11023 (2012)). Conservative PGPE —
  our dynamics: dynamic exponent `z ≈ 1.7–1.8` (≈ 1.5 near BKT), equilibrium once the coarsening length reaches
  `L` (Groszek & Billam, arXiv:2601.02687 (2026); Groszek, Comaron, Proukakis & Billam, PRR 3, 013212 (2021)).
  Scaled from `t = 6000` at `L = 128`, these give `t(192) ≈ 11 000–12 500` (conservative forms) or `≈ 14 600`
  (`L² ln L`). The registered window `[13 500, 14 500]` lies after all conservative-dynamics estimates, so the
  E1–E3 test checks **the mechanism (slow decay of box-scale charge), not the exponent**; a pass does not measure
  `z = 2`, and the text above should be read as "a time of order `L^z`, `z ≈ 1.5–2`".
- **The non-monotone offset is not an equilibrium effect.** Equilibrium KT theory makes the finite-size stiffness
  monotone in `L` (Prokof'ev & Svistunov, PRA 66, 043608 (2002), Eq. 32, `df_L/d ln L = −y² f_L² ≤ 0`;
  Hasenbusch, J. Phys. A 38, 5869 (2005), Eq. 31 and Table 1). No such non-monotone offset is reported in the
  equilibrium literature — consistent with reading the `L = 192` point as an equilibration artefact.
