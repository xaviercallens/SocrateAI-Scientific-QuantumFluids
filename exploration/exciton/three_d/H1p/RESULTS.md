# H1' results (2026-10-12): numerical two-point LP values, validated on published values — NOT certified

Registration: `PREREG.md` (d668109), amendment A1 (83a3500), amendment A2 (968dd32; owner's choice of a numerical,
non-rigorous reproduction after development showed rigorous certification at 1e-8 needs a different construction,
`DEV_NOTES.md`, 1ec3fe7). Driver `run_h1p.py`, code frozen at 91b1a97 (one fix before any run, see Deviations).
LP code `../H1/lp_bound.py` unchanged. Records `records/*.json` and `records/solutions/*.json`; logs `log_*.txt`,
`run.log`. Runs: stage 1 20:34, stage 2 after V1, stage 3 after V2/V3 (single-threaded, 4-6 parallel jobs).

**Nothing below is a certified lower bound.** Each value is the objective of a double-precision LP whose polished residual
constraint violations are <= 1.1e-9 (stages 2-3) and <= 1e-7 (stage 1); it can exceed the true LP optimum by much more than
that residual: here V2 exceeds the triangular-lattice energy (which no valid bound can) by 3.1e-9 with a residual of
8.9e-11 (35x), and V1 at α = 1 exceeds E_Z by 1.1e-9 with a residual of 6.2e-10; at 35x, V3's residual 5.1e-10 could
mean an excess of order 2e-8, comparable to its window. Gates are two-sided, as registered in A2.

## Gates (gate value: K = 40; K = 30 reported)

| gate | d | α | B (K = 40) | B (K = 30) | reference | B − reference | verdict |
|---|---|---|---|---|---|---|---|
| V1 | 1 | 1 | 0.7726372059140 | 0.7726372068320 | E_Z = 0.7726372048267 | +1.4e-9 rel. | **pass** (<= 1e-8) |
| V1 | 1 | π | 0.0864348114438 | 0.0864348114949 | E_Z = 0.0864348112133 | +2.7e-9 rel. | **pass** |
| V2 | 2 | π | 0.1595952701091 | 0.1595952702139 | published LP 0.15959526... (1603.09684 Table 1.1) | inside [0.15959525, 0.15959528] | **pass** |
| V3 | 3 | π | 0.2232178249307 | 0.2232173547129 | published LP 0.22321782... | inside [0.22321781, 0.22321784] | **pass** |

Residual violations max(f − g, −f̂) at K = 40: V1 α = 1: 6.2e-10; V1 α = π: 1.0e-7 (9.97e-8, just under the 1e-7
acceptance); V2: 8.9e-11; V3: 5.1e-10. Our own lattice sums: E_A2(π) = 0.1595952670, i.e. the d = 2 LP value exceeds the
triangular-lattice energy by 3.1e-9 — the non-rigorous slack, since a valid bound cannot exceed a configuration's energy.
At α = π, d = 3: min(E_FCC, E_BCC) = 0.2315362662 (equal, self-dual point); gap (0.2315362662 − B)/0.2315362662 = 3.59 %
(the published record 0.23153532, a coexistence phase, gives 3.59 % as well). K-dependence in d = 3: K = 30 is 4.7e-7
below K = 40; whether K = 40 is converged was not tested (K = 50 not registered).

## H1' (d = 3, α ∈ {2, 4, 8}; run only after V1–V3 passed)

| α | B (K = 40) | B (K = 30) | E_FCC | E_BCC | G = (min − B)/min (K = 40) |
|---|---|---|---|---|---|
| 2 | 1.011018287 | 1.011017952 | 1.017616896 | 1.015862816 | 4.77e-3 |
| 4 | 0.07275645512 | 0.07275614557 | 0.07796767103 | 0.07889601371 | 6.68e-2 |
| 8 | 0.0003947635566 | 0.0003947605553 | 0.0005032413016 | 0.0006026980499 | 0.2156 |

**Gate H1': G > 1e-3 at all three α → numerically, at K <= 40 (primal solutions only, no upper bound on the LP
optimum), two-point (LP) bounds are insufficient for the 3D Gaussian-core question at
these α, as registered; the prediction (G > 1e-3 at all three) is met.** The gap grows with α (0.48 %, 3.6 % at π,
6.7 %, 21.6 %), consistent with the LP bound degrading towards the sphere-packing limit. Residual violations at K = 40:
1.1e-9, 1.1e-10, 2.0e-10. min(E_FCC, E_BCC) is the lattice reference; the true minimum may lie slightly below it
(at α = π the lowest known state, a coexistence phase reported by Cohn–Kumar–Schürmann 2009, is 9.5e-7 lower in
absolute terms, 4e-6 relative). At α = 4 and 8, G is large enough that this cannot matter; at α = 2 (G = 4.8e-3) the
reading assumes no non-lattice state lies more than about 0.4 % below BCC, which we have not checked.

## Reading

- Our LP code, run as in H1 but accepted at a looser, stated tolerance, reproduces the three published α = π values
  (d = 1, 2, 3) within the registered windows: d = 1 and d = 3 agree to the printed 8 digits, d = 2 does not
  (0.159595270 vs printed 0.15959526...; it passes only because A2's window is ±1e-8 around the truncated value).
  At K = 30 the d = 3 value (0.2232173547) would fail V3 by 4.6e-7 (below the window's lower edge 0.22321781); the pass relies on K = 40, the registered gate value. That repairs H1's sanity-gate failure *numerically*; it does not certify.
- H1's registered question at α = π was already answered in print (3.6 % gap); at α = 2, 4, 8 the gaps are 0.48 %,
  6.7 % and 21.6 % — numbers we did not find published (search not exhaustive). The two-point bound does not settle the
  3D Gaussian-core conjecture at any α tested; this is expected from the literature and is not a new kind of result.
- Rigorous certification at 1e-8 remains open (`DEV_NOTES.md`).

## Deviations

0. Prior knowledge at gate parameters: the V1 K = 30 runs are bit-identical to H1's published values
   (0.7726372068319629, 0.08643481149488239), so those outcomes were known before A2; A2's 1e-7 acceptance was set after
   seeing H1's α = π violations (2.1e-8 to 4.6e-8, `../H1/RESULTS.md`). At K = 40 (the gate value) all three full-setting
   β values for V1 at α = π lie within 3e-9 relative of E_Z, so the pass does not depend on that threshold. Choosing β by
   maximum value favours the most-violating accepted solution (V1 α = 1, K = 40: chosen B is 1.1e-9 above E_Z, another
   accepted β gives 4.7e-11 below). A1's pre-check read H1's existing d = 1, α = 1 solution (a gate parameter); development
   runs were otherwise at d = 1, α = 2 only, and their outputs were not kept beyond `DEV_NOTES.md`. Runs were launched
   with OMP_NUM_THREADS=1 on the command line (not set in `run_h1p.py`). For α = 8, K = 40 the chosen β is the lowest of
   the three FULL candidates, so the β optimum is not bracketed (irrelevant at G = 0.216).

1. Amendments A1 and A2 (both committed before any registered run) replaced the certified procedure by a numerical one;
   the gates' reference values and order were kept, the gates became two-sided.
2. `run_h1p.py` as first frozen (968dd32) did not apply the 1e-7 acceptance at FULL settings (`run_h1.admissible` binds its
   default tolerance at definition); fixed in 91b1a97 before any run.
3. The coarse-scan acceptance (1e-6, from H1) was kept, so some coarse values that rank β are less accurate than the full
   ones; only FULL-setting values are reported as results.
4. For α = 8, K = 40 the coarse scan's best was at the grid edge and was extended twice (as H1's code does); the final
   values come from FULL runs around the extended optimum.
