# Leveraging Dong et al., Nature Physics 2026 (hybrid feedback control, many-body mixed phase space)

Owner-provided paper, read 2026-10-06 (abstract, Fig. 3 caption, Methods "Algorithmic structure", outlook); in
the literature database as `Dong2026` (manifest `user_provided.json`, PDF stored). What it does: on a 24-qubit
processor, evolve for a short Δt, then project back onto a low-entanglement variational manifold by optimising a
measured imbalance (a discrete TDVP step done by measurement); the loop converges autonomously to stable periodic
orbits that coexist with chaos — a many-body analogue of a KAM mixed phase space.

This is a spin-chain experiment, not a fluid. The transfer is structural, and it changes how two of our running
measurements should be read.

## 1. Our transport coefficients are TDVP leak rates

The point-vortex model is a variational projection of the Gross–Pitaevskii flow onto the 2N-dimensional manifold
of vortex positions (rigorously: Jerrard–Spirn, Kurzke–Melcher–Moser–Spirn; our `DissipativeVortexDynamics.lean`
is the dissipative version). The full field leaves that manifold: the leak is the phonon part, and its rate, summed
over the configuration, is exactly `−dH/dt = (α/2)|∇H|²` — our energy estimator of friction. So α (and α′, η) are
the statistics of the TDVP error of the vortex manifold in a chaotic bath. Dong et al. measure the opposite
process (how much coherence survives projection); we measure the leak with no projection step at all, because the
bath is physical. The same object, read from both ends. This framing belongs in the paper's discussion
(`paper/vortex_transport.tex`, Section 2), not as a result.

## 2. Regular island vs. diffusion — this is the Einstein test's interpretation question

Dong et al.'s stabilised orbits are regular islands: bounded, quasi-periodic motion embedded in chaos. Our
transport data show something the pre-registration treated as a nuisance: at T/T_BKT = 0.14 the residual motion of
the vortices about their point-vortex prediction grows with exponent **0.71** over lags 20–400 (registered window
for "diffusion": 0.8–1.2; η therefore not quoted). Sub-diffusion over two decades of lag is what a trajectory on a
KAM-like island, perturbed by a weakly coupled bath, looks like — not Brownian motion. Likewise both single pairs
(W1) stopped shrinking and one re-expanded: a periodic orbit (translating dipole at fixed d) that the wind
stabilises, the classical counterpart of their Fig. 3b convergence to a closed orbit.

**Pre-registerable, on data that exist or arrive tonight (no new simulation):**
- **I1.** The residual MSD exponent `γ(T)` at the three admitted temperatures (0.14, 0.27, 0.43 T_BKT) from the
  production tracks. Prediction (mixed-phase-space reading): `γ` rises with T toward 1 and the Einstein ratio
  `R_E` is only meaningful where `γ ≥ 0.8`. Rival (Brownian reading): `γ ≈ 1` at every T and the 0.71 is a
  short-time artefact that disappears for lags ≥ 100.
- **I2.** For the W1 pairs, the separation's power spectrum over t ∈ [2000, 4000]: discrete lines (quasi-periodic
  island) vs. a continuous 1/f²-type spectrum (random walk). Decision: more than 50 % of the variance in the three
  largest lines → island.
Both go in an amendment to `PGPE_EINSTEIN_PREREG.md` before the warm analysis is run.

## 3. The classical analogue of their protocol: evolve-and-reproject

Their loop, translated: (i) evolve the PGPE for Δt; (ii) detect vortices; (iii) re-imprint them with the clean
Bernoulli imprint into the condensate (projection back onto the vortex manifold, discarding phonons); repeat.
This gives, per step, the energy leaked (friction at zero bath temperature plus imprint error), and in the limit of
small Δt the pure manifold dynamics. Uses: a direct check that the T = 0 pair does not move off the manifold
(expected leak → 0), a map of which vortex configurations are stable orbits under the projected flow (translating
dipole; co-rotating pair; the 4-vortex antiparallel configuration, which exchanged partners in G2), and a
measurement of how Δt deforms the orbit — the same Δt-dependence they report. Cost: minutes per configuration at
L = 64. Not pre-registered; a tool, not a claim.

## 4. Autonomy

Their protocol is an algorithmic search for regular trajectories with the device in the loop; our
`exploration/autoresearch/` loop is an algorithmic search for testable hypotheses with the data in the loop. Both
replace a human's prior by a scalar objective and a keep/discard rule. Worth one sentence in the methods.

## Not transferable

Entanglement, imbalance revivals, scars, ETH: no classical-field counterpart. The 0.71 exponent is one
temperature from eight runs; I1 is the test, not this note.
