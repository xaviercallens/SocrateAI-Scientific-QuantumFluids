# Exciton fluids: harmonic Lindemann estimate of quantum crystallisation, report

Date 2026-10-11. Literature gate: `EXCITON_FLUID_WIGNER_GATE.md`. Pre-registration and amendments A1, A2:
`EXCITON_FLUID_WIGNER_PREREG.md`. Code and numbers: `exploration/exciton/results/wigner/`
(`wigner_lib.py`, `wigner_p0_checks.py`, `wigner_calibration.py`, `wigner_gated_scan.py`, `wigner_analyse.py`,
`wigner_refine.py`; `p0_checks.json`, `calibration.json`, `gated_scan.json`, `analysis.json`, `refine.json`).
This is an ESTIMATE with a calibration error attached, not a critical density. No Monte Carlo was run.

## Verdicts on the registered items

| Item | Result |
|---|---|
| P0 lattice code vs S1's `E_triang/N = 4.446 (n r_0^2)^{3/2}` | 4.4464, deviation 8e-5: pass |
| P0 Laplace kernel vs independent image series (D/d = 1.5, 3, 10) | relative difference <= 2.4e-8 where `|U| >= 1e-10`: pass |
| P3 collapse in `n r_0^2` of the 1/r^3 control | spread 3e-14 (exact by scale invariance): pass, trivial |
| P1 direction (harmonic ratio below the true one) | **refuted**: `gamma_h(290) = 0.263` against DMC `0.230(6)` |
| P2 usability of criterion A (`n_c^h(A)/290` in [0.5, 2]) | **failed**: `n_c^h(A) = 847` (690-1047 from the 0.006 error), ratio 2.9 |
| P4 gate raises `gamma_h` / critical density | confirmed (finite D: larger `gamma_h` at fixed `nu`; critical `n r_0^2` above 290, table below) |
| P4 monotone in `nu` | **refuted** for all bilayer kernels: interior minimum (the `2/x` core), monotone only for pure 1/r^3 |

## Calibration (the deliverable's error)

`gamma_h = c (n r_0^2)^{-1/8}`, `c = 0.5342` (BZ/lattice-cut variation 4e-4 relative, i.e. 0.3% in `n_c`).

* Criterion A (`gamma_c = 0.23`, the DMC value of S1): harmonic estimate `n_c^h = 850` (690-1050) against QMC 290(30)
  and S3's 324 (196-484): off by a factor 2.6-2.9. Because `n_c ~ gamma_c^{-8}`, the criterion is extremely steep:
  `gamma_c` = 0.25 gives 435, 0.20 gives 2600, the textbook 0.15 gives 2.6e4 and 0.10 gives 6.6e5. The generic
  0.1-0.2 range is useless for this system.
* Criterion B (`gamma_c = gamma_h(290) = 0.263`, with 0.260-0.267 for 320-260): zero error on the control by
  construction. The 0.230 versus 0.263 gap is also a statement that the harmonic ratio and the DMC-measured ratio
  differ by a factor 1.14; I did not establish why (anharmonicity, the DMC estimator, or a definition detail of
  `<(r - r_c)^2>` in S1 are all possible; I did not check S1's estimator).
* Precedent for the transfer step (S5, Coulomb electrons, same method): critical gate distance 35 harmonic/HV against 29 DMC.
  I take 20% in the controlling quantity as the class error of the transfer, in addition to the anchor spread.

## Gated estimates (criterion B; exploratory edges from A2)

Dimensionless setup: `Lambda = r_0/d = d/a_M`, `a_M = epsilon hbar^2/(M e^2)`, `nu = n d^2`, `n r_0^2 = nu Lambda^2`,
`D = 2h` gate separation, `d` layer separation.

1. **A rigid-exciton crystal needs a large coupling.** The smallest `Lambda` with any harmonic-stable density:
   `Lambda_min = 49` ungated (46-51 over the 260-320 anchors; 83 if criterion A is used), 52 at D/d = 3, 65 at 2,
   104 at 1.5, 246 at 1.2, all at `nu ~ 0.4-12`. For D/d >= 5 gates change `Lambda_min` by less than 2%.
2. **Gates can only hurt.** At fixed `Lambda` the lower window edge (the crystallisation density) rises with decreasing
   D/d: for `Lambda = 300`, `n_c r_0^2` = 294 (ungated, reproducing the 1/r^3 value by construction),
   419 (D/d = 20), 944 (10), 2.7e3 (5), 6.7e3 (3), 1.6e4 (2). The finite range of the interaction is the cause.
3. **A second, upper edge** (`nu_hi ~ 4` at `Lambda = 100`, ~40 at 300): the `2/x` core of the classical kernel makes
   `gamma_h` grow with density. At `nu ~ 4` the spacing is `0.5 d`; the rigid-exciton picture is not valid there, and S4
   (composite excitons) has its own two-sided window. I do not interpret `nu_hi` physically.
4. **Physical mapping (assumptions only).** `Lambda = (d/0.0529 nm)(M/m_e)/epsilon`. Central assumption
   `d = 1 nm`, `M = 1 m_e`, `epsilon = 4.5`: `Lambda = 4.2`, below `Lambda_min` by a factor 12; over the assumed grid
   `d` 0.7-2 nm, `M` 0.5-1.5 m_e, `epsilon` 3-6, `Lambda` runs 1.1-19 < 46. Under this estimate no density gives a
   harmonic-stable rigid-exciton crystal for such a bilayer. With `M = 1 m_e`, `epsilon = 4.5`, `Lambda_min = 49`
   corresponds to `d ~ 12 nm`. These parameter values are placeholders, not a specific device.
5. **Post hoc comparison (exploratory, A2).** S4 (composite excitons, PIMC, finite T, ZnSe masses) reports no crystal
   for `d <= 9.1 a_B*`, i.e. `Lambda = 9.1 x 3.46 = 31` in my units (my conversion, using their `m_h/m_e = 2.46`);
   my estimate gives 46-51. Same order, harmonic estimate 1.5x more demanding; the models differ and I treat this as
   a consistency remark, not a validation.

## What the harmonic estimate cannot do

* It gives no first-order transition, no liquid-side information, no free-energy comparison, no coexistence,
  no supersolid, no exchange (bosons are distinguishable lattice particles), no composite-exciton physics at
  spacing ~ d, no screening by the gates' own response (ideal grounded metal only, as in Theorem 1).
* No claim about a thermal melting temperature: not computed, not calibrated; a harmonic 2D crystal has a
  logarithmically divergent `<u^2>` at T > 0. S3's `T_m ~ 0.09 D/a^3` is quoted from a reference I did not read.
* The 20% transfer error is borrowed from a different system (S5); for this kernel it is an assumption.
* No QMC data exist (in my search) for the gated kernel, so the estimate is not tested against any.

## Honest summary

The pre-registered expectation (harmonic criterion errs on the low side, so `n_c^h < 290`) was wrong: it errs on the
high side by a factor ~2.9 with the QMC ratio. The calibrated-on-control transfer says: a classical ideal-metal-gated
dipolar bilayer needs `d/a_M` of order 50 or more to crystallise (about 12 nm at the placeholder mass and permittivity),
and screening by close gates raises the crystallisation density steeply. An hBN-spaced device with `d ~ 1 nm` is far
below it in this rigid-exciton model; whether the real composite system does better (S4 suggests the threshold can
be lower than the harmonic one by 1.5x) is not decided here.
