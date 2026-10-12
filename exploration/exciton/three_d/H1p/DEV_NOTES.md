# H1' development notes (2026-10-12) — no registered run has been made

All runs below are development runs at non-gate parameters (d = 1, α = 2), as amendment A1 requires.

1. `dev/dev_scan.py`: the double LP (H1 code, K = 30, 4 cutting-plane rounds) gives 0.27134153 ± 2e-10 for every
   b ∈ {0.3, ..., 1.3}; E_Z(2) = 0.2713415222. The LP is flat in b.
2. Contacts of the double LP at b = 1/2, K = 30 (60-digit evaluation of its coefficients): f touches g at u = 2, 8, 18
   (x = 1, 2, 3) and f̂ vanishes at t = 19.74, 78.96 (y = 1, 2) to within 1e-8; beyond, the LP has no control
   (relative violation (f − g)/g = 2.9e43 at x = 8). So the optimum found is a degenerate face resolved only at a few
   contacts, not a vertex with K + 1 contacts: amendment A1's "K + 1 most active contacts" step is ill-posed.
3. `dev/newton_polish_proto.py`: square systems with p touches and q double zeros of f̂, degree K = p + q − 1
   (q double roots need K >= 2q; κ < 0 needs odd K): exact interpolation at the lattice points with b = 13/10, K = 6
   reproduces E_Z(2) to 1e-21, but that f is not admissible (max (f − g)/g = 0.81, min Q = −309). A damped Newton on
   value + derivative conditions stalls (residual 0.1-2.6 for b = 13/10, diverges for b = 1/2) in all six configurations.

Conclusion for the owner: certification at the registered 1e-8 level needs a different construction (e.g. exact solve
of the LP's optimal basis on the grid plus rigorous bounds on the dips between grid points, or an SDP/sum-of-squares
formulation, for which no solver is installed). The gates have not been run.
