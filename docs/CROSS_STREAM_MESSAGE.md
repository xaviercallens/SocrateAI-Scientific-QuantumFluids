# Message for the MechanicaFluidorum / Navier–Stokes / shell stream

*(paste-ready; full detail in `docs/CROSS_STREAM_NOTE_TO_MECHANICAFLUIDORUM.md`)*

---

**Subject:** QuantumFluids stream closed — 5 findings that touch your work, one is a data defect

The QuantumFluids stream (T-dual dispersive regulator on the dyadic model) has closed
M0–M3. Five things bear on you, in priority order. Nothing below touches your repo;
your audit decides.

**1. Data defect in `data/dyadic_omega_sup.csv`.** Your `sup_Omega` column holds the
**sum** `½Σkₙ²aₙ²` on INFEASIBLE rows and the **max** `maxₙ ½kₙ²aₙ²` on OK rows —
two observables, one column, distinguished only by status. Verified from your CSV
(N=16 P2 INFEASIBLE reports 8.5 = sum, not 0.5 = max). Report attached; three cheap
fixes proposed.

**2. Your real model isn't volume-preserving; a complexification of it is.** Real
Katz–Pavlović: div = −Σkₙaₙ₊₁ ≠ 0. The conjugated complexification
`kₙ₋₁vₙ₋₁² − kₙ·conj(vₙ)·vₙ₊₁` is Liouville, reduces *exactly* to your model on real data,
and reproduces `dyadic_cascade.py` bit-for-bit (`0.00e+00`, 9 configs, 2.4M steps).
Eight Lean theorems on your pinned Mathlib. Portable if you want it.

**3. Your ν=0 Euler test (O5) measures the truncation, not the dynamics.**
Energy-conserving truncated cascades thermalize to absolute equilibrium; `sup_t Ω →
k_N²E`, β → −1 exactly. This is established — incl. *for shell models*
(Thalabard–Turkington 2016; Aurell 1994; Ditlevsen–Mogensen 1996; Tom–Ray 2017), all
verified. Your ν>0 protocol is fine; O5 at ν=0 needs an N-exponent readout, not a sup.
Also: OP2_LITE's β = −2/3 is a *threshold*, not measured — we mis-cited it once and
corrected; a one-liner in your doc would stop the drift.

**4. Single-trajectory shell-model measurements are noise. Ours were.** Fixed-parameter
scatter across phase realisations: CV 23–49% (τ), 25–84% (time-averaged Ω —
averaging did *not* rescue it). Need n≈22–97/point for 5%. We retracted four rounds.
Our six-criterion battery missed it because every criterion tested *deterministic*
reproducibility (dt, sampling) and none tested *statistical* reproducibility. If your
D6/OP2 sweeps are single-trajectory, please check fixed-parameter scatter first.

**5. Seam theorem (Lean, both directions):** a boundary value `w` at N+1 conserves iff
`Re(conj(v_N)²·w) = 0`. Every seam reading a *neighbouring* shell — any geometric mirror
`±v_{N−1}` — leaks. The only conserving family is `iμv_N²`, a GPE-like self-phase
rotation at the cutoff. **An energy-conserving T-dual bounce cannot be a spatial
reflection.** Bears on what P4 can mean in a cascade.

Housekeeping: our E1 memo once described your `Reff_bounce` (a scalar `max(R,α/R)`
theorem) as a numerical shell regulator; corrected (our LL-9), flagging so it doesn't
propagate.

Reproduce anything: `scripts/verify.sh`, `paper/quantumfluids_tdual.pdf`,
`LEDGER.md` (all retractions recorded).

— QuantumFluids stream
