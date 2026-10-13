# H1'' development notes (2026-10-12/13) — non-gate parameters only (d = 1, α = 2, b = 3/2; d = 3, α = 3, b = 1; K = 30)

Scripts in `dev/` (`dev1.py`, `dev2.py`, `dev3.py`, `recert.py`), logs `dev/*.log`. No gate case was run.

1. **Double-precision LP with relative rows fails** (`rig.py`, `dev1.py`). Rewriting f <= g as f/g <= 1 removes the
   absolute-tolerance problem but the LP is then ill-conditioned: near x1 (g = 1e-14) the O(1) terms of f must cancel
   to 1e-14, i.e. about 23 significant digits, and double precision has 16. The exact f/g reached 6e5 between grid
   points. A second double variant (split at u1, R <= -m beyond) behaved the same.
2. **High-precision interior-point LP** (`hp_lp.py`, 256-bit arb midpoints, Mehrotra predictor-corrector) converges to
   duality gap < 1e-30 in 30-120 iterations on 4-7k rows (tested on a random LP against HiGHS: equal to 1e-15).
3. **Exact checks catch what sampled checks miss.** With the 256-bit LP the bound first came out 2.2e-5 *above* E_Z
   (d = 1) — impossible for a valid bound. Cause: flint returns real roots as `acb` with exactly zero imaginary part;
   the first filter kept only `arb` roots and so saw none (fixed; cross-checked against sympy root counts). Then f/g
   exceeded 1 by 6e-7 in a spike at the contact x = 3 that a 20 000-point fine grid missed. Fix: cutting planes at
   the **exact critical points** of f/g (real roots of R' − κR), which contain every local maximum.
4. **R beyond u1 has near-double roots** (e.g. u = 96, x = 4 in d = 1): the LP pushes f to 0 at far contacts. R <= 0
   is stronger than needed there; the certificate now proves f/g <= 1 + τ0 by bisection on [0, U], U beyond the largest
   real root of R, and R < 0 only beyond U.
5. **Box enclosures.** The plain centred form (Horner on a ball) overestimates by the size of the cancelling terms
   (~1e10 at u ~ 50), so bisection needed millions of boxes. Taylor shift at the box midpoint (`make_encloser`:
   P(m + h) by exact composition, e^{ch} by a degree-60 Taylor polynomial with a rigorous remainder) brings the d = 3
   certificate to 823 + 21 boxes, 0.5 s.
6. **Result at d = 3, α = 3, b = 1, K = 30** (non-gate): high-precision LP 0.26867034898061 after 14 rounds;
   certified B = 0.268670348980408 (τ = 7.5e-13, δ = 2.2e-27), i.e. 2e-13 below the LP value; min(E_FCC, E_BCC) =
   E_BCC = 0.27708637, gap 3.0 %. (That solution file was later overwritten by the 6-round run of item 12.)
7. **d = 1 is harder** (the bound is sharp: f touches g at every integer, f̂ has double zeros at every non-zero integer).
   After 14 rounds the LP value was 0.271341522188990 (E_Z = 0.271341522189015, i.e. 2.5e-14 below), but new f/g
   spikes beyond u1 (up to 4e-4) and moving f̂ dips between the sparse grid points kept appearing; the certificate
   closed with τ = 2.5e-3 and B = 0.27017 <= E_Z (valid, loose). Changes: denser grids (f/g: 3000 points on (0, u1];
   R: 1500 linear points on [u1, 4u1] + 300 log; Q: 4000 linear points on t <= 200 + 1000 quadratic + 150 log).
8. **Tail margin.** With R <= −1e-40 beyond u1 the far-tail f/g spikes shrank only ~3x per round (d = 1); with
   R <= −1e-12 (normalised units) the first-round violation fell from ~1e4 to 6e-3. Adopted (cost: f < 0 strictly where
   g < 1e-12).
9. **Row pruning** (dropping rows with slack > 1e-4) made violations reappear round after round; removed.
10. **Lift width.** f̂ dips at large t (e.g. Q = −3.5e4 at t = 74, i.e. f̂ = −3e-12) need δ ~ dip·e^{(1−1/λ)t/2};
    λ = 2 made τ ~ 1e-1. A ladder λ0·2^j with the best estimated B proved first brings it to the level set by the small-t
    dips. Every round's coefficients are now certified and the best certified B kept.
11. **Speed.** One LP round (10k rows, K = 30) took 926 s, 75 % in Python-level element access; building the scaled
    matrix from row lists cut that part 2.5x; the 10k x 30 arb matrix product (~2 s per IPM iteration) now dominates.
12. Last d = 3, α = 3, K = 30 quick run (6 rounds): certified B = 0.268670168254 (τ = 6.7e-7) at round 5; the LP
    value is 0.26867034898. d = 1, α = 2 with margin 1e-12 (5 rounds): certified B rose to 0.2699 (round 1) and
    oscillated; the λ ladder applied to the round-13 vector of the earlier run gives 0.271113 (τ = 8.1e-4, from f/g).
    Whether V1's 1e-8 is reachable within 25 rounds is not known at registration.
