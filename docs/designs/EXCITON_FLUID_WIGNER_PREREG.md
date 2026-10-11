# Exciton fluids: harmonic-phonon (Lindemann) estimate of crystallisation, pre-registration

Date 2026-10-11. Committed before the first run of any `wigner_*.py` script. Literature gate:
`EXCITON_FLUID_WIGNER_GATE.md` (sources S1-S5). Scripts and results: `exploration/exciton/results/wigner/`.

## Question

At what dimensionless density does the classical triangular lattice of the exact gated exciton kernel of Theorem 1
become unstable against zero-point motion, by the Lindemann criterion in the harmonic approximation, and how wrong is
that criterion on the one case where quantum Monte Carlo exists (bare 1/r^3, S1/S3)?

## Model (fixed before running)

* Units `hbar = M = 1`, lengths in the layer separation d. Pair potential `phi(x) = Lambda * u(x)`, `x = r/d`,
  `Lambda = r_0/d = d/a_M` (`a_M = epsilon hbar^2/(M e^2)`), and `u(x) = 2 [V_same - V_inter]` in units `e^2/(epsilon d)`
  as given by `S(s)` of `gate_image_cm_sym.py` with `d = 1`: `u(x) = int_0^inf S(s) exp(-s x^2) (pi s)^{-1/2} ds`.
  Gates at `z = +-h`, layers at `z = +-d/2`; gate separation `D = 2h`. Ungated limit `u = 2 (1/x - 1/sqrt(x^2+1))`,
  large-`x` asymptote `u -> x^{-3}`.
* Controls: (C1) the pure `phi = Lambda x^{-3}`; here `n r_0^2 = nu Lambda^2` with `nu = n d^2` and the result must depend
  on `n r_0^2` alone. (C2) ungated bilayer kernel (`D = infinity`), which has the `1/x` core.
* Crystal: triangular lattice, `n = 2/(sqrt(3) a_L^2)`. Dynamical matrix
  `D_ab(q) = sum_{R != 0} (1 - cos q.R) [ phi''(R) Rh_a Rh_b + (phi'(R)/R)(delta_ab - Rh_a Rh_b) ]`, `omega^2 = eig/M`.
  `<u^2> = (hbar/2N) sum_{q,s} 1/omega_s(q)` (u is the 2D vector, both polarisations), `gamma_h = sqrt(<u^2>)/a_L`
  (the same definition as S1). `U'` and `U''` from the same Laplace integral. BZ sampled with an N x N shifted grid in
  reciprocal-lattice coordinates; lattice sum cut at `R_c` with the continuum tail `-pi n R_c phi'(R_c)` on the trace.
* Scaling (exact in the harmonic model): `gamma_h(nu, Lambda, D) = gamma_h(nu, 1, D) Lambda^{-1/4}`. For 1/r^3:
  `gamma_h = c (n r_0^2)^{-1/4}`.
* Crystal side only. The harmonic approximation knows nothing about the liquid; it gives a necessary stability criterion,
  not a free-energy comparison.

## Pre-registered criterion values (stated before any number is seen)

* **gamma_c (A) = 0.23.** Reason: it is the DMC-measured Lindemann ratio at the transition of exactly the bare 1/r^3
  system (S1: 0.230(6)); it is the only value tied to this potential and bosonic statistics by a measurement. It is a
  full-anharmonic value being compared with a harmonic ratio, which is the part under test.
* **gamma_c (B) = gamma_h(1/r^3 at n r_0^2 = 290).** The "calibrated" criterion: the harmonic ratio at the QMC critical
  density of the control. Zero error on the control by construction; its uncertainty is carried by `n_c = 290(30)` (and by
  S3's `324 (196-484)` as an alternative anchor). This is the one used to transfer to gated kernels, as in S5.
* Sensitivity set (reported, not used for claims): gamma_c in {0.10, 0.15, 0.20, 0.25}. The generic 0.1-0.2 range is
  listed because it is the textbook range; it carries no argument for this system.

## Predictions registered before running

* P0 (code check, hard gate): the code's classical triangular-lattice 1/r^3 energy per particle equals
  `4.446 (n r_0^2)^{3/2}` of S1 to 0.2%; and the Laplace-integral kernel equals the direct real-space image sum to
  relative 1e-6 at five test radii for D/d in {1.5, 3, 10}. If either fails, nothing downstream is reported.
* P1 (calibration, direction): the harmonic ratio underestimates the true (anharmonic) ratio at a given density, so with
  criterion A the harmonic estimate `n_c^h(A)` lies **below** 290, i.e. `n_c^h(A)/290 < 1`. Not predicted: its size.
* P2 (calibration usefulness gate): transfer to gated kernels is called "order-of-magnitude usable" only if
  `n_c^h(A)/290` lies in [0.5, 2]; otherwise the gated estimates are reported as qualitative with that statement.
* P3 (control consistency): C1 collapses onto one curve in `n r_0^2` (variation across `nu` below 1e-3).
* P4 (gated direction): at fixed `n r_0^2`, finite `D/d` gives a larger `gamma_h` than the 1/r^3 kernel in the dilute
  limit (finite range), i.e. a larger critical `n r_0^2` than 290; and `gamma_h(nu)` at fixed Lambda is monotone
  decreasing in nu on the dipole side. Refutation of either is reported as such.

## Outputs

1. Calibration table: `n_c^h` for 1/r^3 under A, B and the sensitivity set; ratio to 290 and to 324; stated error.
2. Gated table: for `D/d` in {1.2, 1.5, 2, 3, 5, 10, 20, infinity}: `gamma_h(nu, Lambda=1)` on a log grid
   `nu in [0.05, 200]`; and for `Lambda in {0.5, 1, 2, 5, 10, 30, 100}` the harmonic-stability density `nu_c(Lambda, D/d)`
   under B, expressed also as `n_c r_0^2 = nu_c Lambda^2`, with an error band from 290(30) (low/high anchors) and a
   second band from the Lindemann value differing between potentials (0.23 vs 0.24, S1-quoted; factor 4 in Lambda).
   Cases with no root in the grid are reported as "no crystal above Lambda", not extrapolated.
3. Physical mapping, as assumptions only: `Lambda = (d/a_B)(M/m_e)/epsilon` for d in nm; table for
   `d = 1 nm, M = 1 m_e, epsilon = 4.5` and a neighbour set (d = 0.7, 2 nm; M = 0.5, 1.5 m_e; epsilon = 3, 6). None of
   these is a measured value of a specific device; all are placeholders to be replaced.

## Limits, written before the result

* No claim of a precise critical density. The estimate carries at least the calibration error and the 20% class
  error seen in S5 for the same method on the Coulomb problem.
* No claim about the thermal melting temperature: not computed and not calibrated. A harmonic 2D crystal has a
  logarithmically divergent `<u^2>` at T > 0, so the harmonic Lindemann ratio does not exist there.
* Cannot do: locate a first-order transition, the liquid side, the low-density re-entrant boundary quantitatively
  (only a "no harmonic crystal" signal), supersolidity, exchange (bosons are treated as distinguishable particles on
  lattice sites), composite-exciton physics at spacing comparable to d (S4).
* The kernel is the ideal-metal, point-charge, rigid-exciton kernel of Theorem 1, nothing else.

## Amendments

**A1 (2026-10-11, before any registered run; found while debugging the lattice code).** The scaling sentence in
"Model" is wrong in its exponent. Dimensional analysis: eigenvalues of D scale as `Lambda/a^5`, so
`<u^2> ~ a^{5/2} Lambda^{-1/2}` and `gamma_h ~ (a/Lambda)^{1/4} ~ Lambda^{-1/4} nu^{-1/8}`; for the bare 1/r^3 kernel
`gamma_h = c (n r_0^2)^{-1/8}` (not `-1/4`), hence `n_c ~ gamma_c^{-8}`: a 2.6% uncertainty in gamma_c (S1's 0.006 on 0.230)
is a 21% uncertainty in `n_c`. The `Lambda^{-1/4}` statement and all criterion definitions are unchanged. P3 ("collapse
in `n r_0^2`") is exact by scale invariance for the 1/r^3 kernel; it is kept as a numerical-convergence check (lattice
cut, BZ grid), with the pass level 1e-3. Numerical method: BZ midpoint error is `O(1/N_q)` because of the `1/omega ~ 1/q`
acoustic singularity; the reported value is the Richardson extrapolation `2 g(2N) - g(N)` with N = 32, 64; lattice cut
`R_c = 40 a_L` plus the continuum tail. No registered number had been computed when this was written.

**A2 (2026-10-11, written after the registered grid scan, calibration and P0 had been run; a deviation, not a
pre-registered step).** What was seen: P0 and P3 passed; P1 (direction) was refuted (`gamma_h(290) = 0.263` is larger
than the DMC `0.230`, so `n_c^h(A) = 847`, ratio 2.9 to 290, P2 failed); on the registered grid (`nu` 0.05-200,
`Lambda` <= 100) the ungated and gated bilayer kernels show a harmonic-stable window only for `Lambda = 100`, and
`gamma_h(nu)` has an interior minimum (not monotone) because of the `2/x` core. Added after seeing this, exploratory:
(i) `wigner_refine.py` finds by root-finding (brentq on log nu, Richardson with N = 16, 32, lattice cut 40 a) the
window edges `nu_lo, nu_hi` of criterion B for `D/d in {2, 3, 5, 10, 20, inf}` and `Lambda in {50, 100, 300, 1000}`,
beyond the registered `nu` grid (down to 1e-3, up to 1e3); (ii) a post-hoc comparison with S4's `d_c = 9.1 a_B*`
using S4's text (`a_B* = hbar^2/(e^2 m_qe)`, `m_h/m_e = 2.46`, hence `Lambda = d (m_qe + m_qh)/(m_qe a_B*) = 3.46 d/a_B*`),
which is not a registered comparison and compares different models (S4: composite excitons, finite T).
Results from these two items are labelled exploratory in the report.
