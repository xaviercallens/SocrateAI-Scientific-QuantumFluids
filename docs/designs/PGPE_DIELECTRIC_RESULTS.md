# Results H07: the finite-k dielectric relation on the equilibrated L = 192 states — D1 and D2 FAIL, D4 PASS

Pre-registration `PGPE_DIELECTRIC_PREREG.md` (with amendments D-A1, D-A2 and the fallback applied after the gates).
Primary data: the six L = 192 extension runs, window t ∈ [13 500, 14 500], 100 snapshots each
(`data/generated/pgpe/r3_C4/`, positions in `r3_C4/analysis/`). Analysis `exploration/pgpe/dielectric_modes.py RUNS`,
output `data/generated/pgpe/dielectric/primary_C4.json`. Date 2026-10-06 23:15. The snapshots were not read before
the gates and the fallback were settled; the equilibration analysis of these runs (E1–E3, `PGPE_ONSAGER_RESULTS.md`)
was run first and does not use the mode amplitudes.

| run | T | K | n_s/n | box-scale pair? (`R_T^v(k₁) > 0.45`) | D1: min coherence over shells | D2: Im/Re, k-ratio | `n_eff` (form-factor corrected) | residual `f` | D3 closest | D4 ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| e1.00_s11 | 0.505 | 10.0 | 0.81 | no | **0.06** | 0.19, 1.42 | 0.49 | 0.17 | `n_s/n` | 0.90 |
| e1.00_s12 | 0.506 | 9.6 | 0.77 | no | **0.06** | 0.32, 1.57 | 0.47 | 0.16 | `n_s/n` | 0.95 |
| e1.10_s11 | 0.604 | 3.5 | 0.34 | **yes (0.83)** | 0.42 | 0.12, 1.28 | 0.71 | 0.26 | `1 − f` | (0.81) |
| e1.10_s12 | 0.605 | 8.3 | 0.80 | no | 0.14 | 0.21, 1.21 | 0.51 | 0.19 | `n_s/n` | 0.88 |
| e1.20_s11 | 0.700 | 5.5 | 0.61 | no | 0.28 | 0.09, 1.18 | 0.57 | 0.25 | `n_s/n` | 0.84 |
| e1.20_s12 | 0.701 | 6.6 | 0.74 | no | 0.22 | 0.07, 1.33 | 0.53 | 0.20 | `n_s/n` | 0.79 |

- **D1 (the relation exists mode by mode, γ² ≥ 0.4 on every shell in ≥ 5 of 6): FAIL — 1 of 6.** In the five
  equilibrated runs the coherence between the transverse current and the detected vortex charge at the same
  wavevector and time is 0.06–0.28. The one run that passes is the one still carrying a box-scale pair.
- **D2 (one real, k-independent coefficient): FAIL — 1 of 6** (and not meaningful where D1 fails).
- **D3 (report only, by the fallback):** the regression coefficient, 0.47–0.57 in the equilibrated runs, is
  closest to `n_s/n` in 5 of 6 — but with coherence ≤ 0.28 the coefficient is not a measurement of how much current
  a vortex carries, and this is not read.
- **D4 (polarisability from pair statistics): PASS — 0.79–0.95 in all five runs without a box-scale pair.**
  `(2π)²⟨|ρ_q(k)|²⟩/(k²TL²)` is flat over the shells `|m|² = 4…16` (e.g. 0.073, 0.072, 0.076, 0.070 for e1.00_s11)
  and equals `(2π)²Σ_pairs d²/(2TL²)` from the minimum-cost matching of the detected vortices within 5–21 %, always
  below it. Disclosure: the first run of the analysis code multiplied the plateau by `k²` by mistake (ratios ≈ 0.01);
  the corrected formula is the one written in the pre-registration, and the correction was made before anything
  else was changed.

## Reading

**The pre-registered claim fails.** At thermal equilibrium at `T/T_BKT ≈ 0.6–0.85`, with 170–830 vortices in the
box almost all of them in tight pairs, the transverse current at a given wavevector and time is **not** the
point-vortex term of the detected charges plus an uncorrelated phonon part: the phonon normal fraction
(`f ≈ 0.16–0.26`) is the larger part of `R_T(k₁) ≈ 0.18–0.32`, and whatever the tight pairs contribute is not
coherent with their instantaneous charge density at that `k`. **CLAIM-069's correlation of 0.996 and the
five-minute probe's 0.987 were, as the pre-registration itself warned, correlations of run-averaged powers carried
by the runs that had a box-scale pair.** In those runs — and only there — the relation holds (coherence 0.42 here;
1.000 at T = 0 in the gates). So the diagnostic of PGPE_ONSAGER_RESULTS.md remains valid for what it was used for
(detecting one unscreened pair), and does not extend to a mode-by-mode dielectric function of the thermal pair gas.

**What survives, and is new here:** the bound-pair gas has a `k`-independent vortex charge structure factor
`⟨|ρ_q(k)|²⟩/k²` out to `k ξ ≈ 0.13`, and its value is the dipole polarisability computed from the measured pair
sizes, 5–21 % lower — the Kosterlitz–Thouless `ε − 1 ∝ Σ d²` read directly from vortex positions in a Bose field,
with a screening-of-dipoles-by-dipoles factor of 0.8–0.95 (D4). How much of the *stiffness* that polarisability
accounts for is exactly what D1's failure leaves open: the current carried by a tight pair is not the point-vortex
current (the gates found 0.7–0.9 of it at `d = 3–8`, and thermal pairs here are mostly `d < 3`).

Secondary (already seen at power level, labelled as such): the t ∈ [6000, 7000] window is not analysed mode by
mode here; nothing in it would change the verdict above, which is set by the equilibrated runs.
