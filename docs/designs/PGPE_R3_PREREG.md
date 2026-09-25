# Pre-registration, round 3: two thermometers, coarsening after a many-pair intervention, and the 1/ln L test

Follows `PGPE_R2_RESULTS.md`, `CAUSAL_TOPOLOGY_DEEP_NOTES.md` §§2, 6, 9, 12, 13 and `paper/sector_temperature.tex`
(v1.11.0, DOI 10.5281/zenodo.22951842). Committed before any round-3 run. Same solver and units. Changes after
this commit are dated amendments.

## Instruments, fixed now

* **Bath thermometer** `T_b`: the two-window equipartition fit of round 1 (window `[0.6, 1.0] k_cut`).
* **Vortex thermometer** `T_v`: torus point-vortex energy (Weiss–McWilliams) of the detected, neutral, `P ≈ 0`
  configuration, inverted through the canonical calibration `vortex_thermometer_cal.json` (4000 sweeps; closure
  passed at N = 4–16; extended to N = 18–24 before any reading, same script, same criterion: closure within 10 %
  at every size used). **Validity: `β_WM ≥ 0.3` only** (the fluctuation identity fails at `β ≤ 0`, notes §13); a
  configuration whose energy maps to `β_WM < 0.3` is reported as "hot, unreadable"; one below the coldest calibrated
  point as "cold, unreadable". Units: `T_v,phys = π / β_WM`.
* **Energy budget**: field decomposition of notes §12 (kinetic per k-band; Nore–Abid–Brachet incompressible part).
* Blocks of 100 time units, samples every 10, as in round 2.

## Part A — two thermometers on the intervention arms

Re-run the round-2 arms **V and P** on the three bases (`e0.60_s11`, `e0.90_s11`, `e0.90_s12`), identical
construction (same seeds, same imprint, same energy matching, controls C1–C3 re-checked), now saving vortex
positions and charges every 10 time units. Six runs, t = 1500.

| # | Statement | Criterion |
|---|---|---|
| P1 | `T_v > T_b` at the start | in block 1 (t ∈ [0, 100)), on every base, either `T_v > 1.5 T_b` or "hot, unreadable" (`β_WM < 0.3`); a readable `T_v ≤ 1.5 T_b` on any base fails P1 |
| P2 | the two temperatures approach each other | over the readable blocks of each V arm (≥ 8 required, else "not evaluable"), Spearman ρ of `|T_v − T_b|` against block index `< −0.7` on at least two of three bases |
| P3 | the bath's loss is the flow's gain | over t ∈ [0, 300), `ΔE_bath = E_kin(k ≥ 0.4 k_cut)[V] − same[P]` and `ΔE_flow = E_incompressible[V] − same[P]`: `|ΔE_bath + ΔE_flow| ≤ 0.3 |ΔE_flow|` on every base (P arm as reference: same total energy) |
| P4 | phonons make no flow | on each P arm, `E_incompressible` stays within 15 % of its t = 0 value in every block |
| A5 | reported, not predicted | `T_v(t)` and `T_b(t)` curves; the block at which `T_v` first becomes readable; N_v(t) |

The causal statement that would follow from P1–P3 on all bases: "the injected label carries its own temperature,
higher than the bath's, and the bath's cooling is the transfer of energy into the label's flow field". P4 is the
control that the phonon arm does not do the same.

## Part D — many-pair intervention and coarsening

On the same three bases, imprint **16 pairs** of separation 8 with dipole vectors in cancelling groups (so that
`Σ q = 0` and `Σ q r = 0`, the single-valuedness conditions), same core factor, projection, renormalisation. No
energy matching (this part is not a matched pair; it is a quench of the vortex subsystem). Three runs, t = 1500,
positions saved every 10.

| # | Statement | Criterion |
|---|---|---|
| D1 | power-law decay of the free-vortex number | `N_free(t) = N_v(t) − N_thermal` (N_thermal = the base's mean N_v) fits `t^{−2/z}` over a window of at least one decade in t with `2/z ∈ [1.0, 1.33]`, i.e. `z ∈ [1.5, 2.0]` (Groszek–Billam 2026, conservative PGPE) on at least two of three bases; a fit with `z < 1.3` or `z > 2.5`, or no decade of power law, fails |
| D2 | the bath cools during coarsening, then recovers | `T_b(block 1) < T_b(base)` and `T_b(last block) > T_b(block 1)` on every base |
| D3 | reported | `T_v(t)` where readable; the energy budget per block |

## Part C — finite size L = 128 (256² grid, same dx and cutoff)

Quench starts at e ∈ {1.00, 1.10, 1.20}, two seeds, t = 4000, sampling over the last 1000; admission A4. Six
runs, ≈ 7 h wall. Launched after A and D.

| # | Statement | Criterion |
|---|---|---|
| C1 | the duality offset falls with L | mean over the three energies of `η·n_sλ² − 1` at L = 128 is smaller than at L = 64 (round-2 ladder, same energies: 0.12, 0.12, 0.20), with ratio in `[0.6, 1.0]` (Hasenbusch: ∝ 1/(ln L + C)) |
| C2 | the jump moves down with L | `T_BKT(128) ≤ T_BKT(64) = 0.821`, if the crossing lies within e ∈ [1.00, 1.20]; else "not bracketed" |
| C3 | reported | `n_sλ²(T)` at L = 128 overlaid on L = 32, 64 and on Christodoulou et al. |

## Kill rules

* Any calibration size used for a reading fails closure (10 %) → no `T_v` quoted at that size.
* Controls C1–C3 of round 2 fail on the re-run → Part A void.
* Energy drift `> 10⁻⁵` on any run → that run void.

## Not in this round

The canonical two boxes (SPGPE reservoir) — it needs a new solver with its own known answers; recorded as round 4.
The negative-temperature branch of the thermometer (cluster moves). The Sunami 2023 Kibble–Zurek data. Any Lean.
Any claim of novelty: D1 tests a published exponent; P1–P3 test an established picture with our own instrument.

## Amendment R3-A1 (2026-09-25 21:50, after the Part D runs, before their verdicts were written up)

`many_pair_config` enforced `Σ q r ∈ L·ℤ²` (enough for a single-valued θ-function phase) but not `Σ q r = 0`.
`Σ q r = L·(m, n)` imprints, in addition to the pairs, a **net phase winding (n, m) around the torus cycles** — a
persistent current. Recorded from the generator with the run seeds: e0.60 → (2, 0); e0.90 s11 → (0, 0);
e0.90 s12 → (1, −3). D1 is therefore evaluated as pre-registered only on the zero-winding arm (s11); the other two
arms are reported as what they are — accidental interventions on the torus winding sector — with their final
windings measured by the loop sum along the cycles. Future generators must subtract the net dipole exactly.
