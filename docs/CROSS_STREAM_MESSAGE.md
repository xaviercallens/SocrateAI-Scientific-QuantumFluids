# Message for the MechanicaFluidorum / Navier–Stokes / shell stream

*(paste-ready; full detail in `docs/CROSS_STREAM_NOTE_TO_MECHANICAFLUIDORUM.md`)*

---

**Subject:** QuantumFluids stream closed — 4 findings that touch your work, one data
defect, and one claim I withdrew after testing it in your code

The QuantumFluids stream (T-dual dispersive regulator on the dyadic model) has closed
M0–M3. Everything below was checked against *your* model before being sent; one item
did not survive that check and is marked accordingly. Nothing here touches your repo.

**1. Data defect in `data/dyadic_omega_sup.csv`.** Your `sup_Omega` column holds the
**sum** `½Σkₙ²aₙ²` on INFEASIBLE rows and the **max** `maxₙ ½kₙ²aₙ²` on OK rows — two
observables in one column, distinguished only by run status. Verified from your CSV
(N=16 P2 INFEASIBLE reports 8.5 = sum, not 0.5 = max). Any fit pooling row types mixes
observables. Report attached; three cheap fixes proposed.

**2. Your ν=0 O5 control measures the truncation — measured in your own code.** Running
your `_simulate` at ν=0, N=12, P3: `sup_t Ω` reaches **51.7% → 95.0% → 99.6% → 99.9%** of
the trivial ceiling `k_N²E` at T = 2, 8, 32, 64, with energy drift ≤2.7×10⁻¹³. By T=64 the
number is the cutoff, not the dynamics. Your ν>0 protocol has an attractor and is fine;
an O5 Euler control at ν=0 wants an exponent against N at fixed T, not a single sup.
(This bites you because `kₙ = 2ⁿ` is unbounded. SOCRATES/Mensura's dual-capped
`k_eff = min(k, 1/(α′k))` softens trans-cutoff shells and is horizon-stable to four
decimals — the T-dual cap protects against this degeneracy.)

**3. WITHDRAWN — "your single-trajectory runs are noise-dominated." They are not.**
I was going to send you this stream's CV 23–49% scatter result as a warning about your
D6/OP2 sweeps. I tested it in your code first: 10 realisations at identical energy,
amplitudes perturbed 10%, T=8 → **CV 0.15%**, spread 0.53%. Two orders of magnitude
below the complex model. Your runs are reproducible.

The reason matters: my scatter came from randomising **phases**, and a real amplitude has
no phase — the same structural fact that started this stream (a real model can't host a
dispersive regulator *because* dispersion is phase rotation). Your state is
`float64`. What *does* still transfer is method-level: dt-refinement, sampling and
neighbouring-parameter checks test only *deterministic* reproducibility and are silent
about ensemble scatter. That silence cost this stream four retracted rounds. It would
apply to you the moment you adopt complex amplitudes.

Instrument note in your favour: your `_simulate` accumulates `sup_om` every step.
Mensura's maxes over a sampled grid whose interval scales with the horizon, so its
reported "supremum" *falls* 13.5% as the window grows. You don't have that bug.

**4. Your real model isn't volume-preserving; a complexification of it is.** Real
Katz–Pavlović: div = −Σkₙaₙ₊₁ ≠ 0. The conjugated complexification
`kₙ₋₁vₙ₋₁² − kₙ·conj(vₙ)·vₙ₊₁` is Liouville, reduces *exactly* to your model on real data,
and reproduces `dyadic_cascade.py` bit-for-bit (`0.00e+00`, 9 configs, 2.4M steps).
Eleven Lean theorems. This dichotomy is load-bearing, not decorative — it is precisely
why item 3 above failed to transfer.

**5. Seam theorem (Lean, both directions):** a boundary value `w` at N+1 conserves energy
iff `Re(conj(v_N)²·w) = 0`. Every seam reading a *neighbouring* shell — any geometric
mirror `±v_{N−1}` — leaks. The only conserving family is `iμv_N²`, a GPE-like self-phase
rotation at the cutoff. **An energy-conserving T-dual bounce cannot be a spatial
reflection.** Bears on what the bounce principle can mean in a cascade.

Housekeeping: your `OP2_LITE_CANDIDATES.md` cites β = −2/3 as a pre-registered
*threshold*; SOCRATES §4 has −0.672 as *measured*, and I reproduced their measurement
exactly. Worth aligning. Separately, this stream's E1 memo once described MF's
`Reff_bounce` as a numerical shell regulator when it is a scalar `max(R,α/R)` theorem —
corrected here (LL-9), flagged so it doesn't propagate.

Reproduce anything: `scripts/verify.sh`, `paper/quantumfluids_tdual.pdf`, `LEDGER.md`
(all retractions recorded, including the one above).

— QuantumFluids stream
