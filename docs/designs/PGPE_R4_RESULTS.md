# Results, round 4: the sector versus the pairs

Pre-registration `PGPE_R4_PREREG.md` (amendments R4-A0–A3). Part A data
`data/generated/cosmo/random_phase_halo*.json` (`PGPE_R4_PREREG.md` carries those results already). Part B data
`data/generated/pgpe/r4/`, log `r4.log`, analysis `exploration/pgpe/analyze_r4.py` →
`data/generated/pgpe/r4_verdicts.json`. Twelve runs (0/V3/P16/V3P16 × three bases), t = 1500, energy drift
≤ 2.2×10⁻⁷ on all twelve. Launched 2026-09-26 11:37 (after a stuck watcher delayed the launch by ≈15 min past
Part C's completion — see the pgrep-self-match note below), finished 13:37, ≈ 55–62 min per run.

## Construction check (before any evolution)

On all three bases the corrected 16-pair generator (`many_pair_config_exact`) imprints torus winding exactly
(0, 0); the boost gives exactly (3, 0). The boost alone retains 84–153 of the 177.8 target superflow energy
(the projector clips the shifted bath's far edge, base-dependent), restored by `heat` to `E₀ + 177.8` exactly on
every arm (see `boost_check` in each V3/V3P16 JSON) — the V3 arm is, as pre-registered, "the base's energy
content + the superflow energy," not merely "the base boosted."

## B1 — the sector is invisible in density (PASS, 3/3)

`|S_band(V3)/S_band(0) − 1|` over t ∈ [500, 1500]:

| base | S_band(0) | S_band(V3) | ratio | criterion (≤ 0.15) |
|---|---|---|---|---|
| e=0.60 | 0.0119 | 0.0120 | **0.3 %** | PASS |
| e=0.90 s11 | 0.0458 | 0.0474 | **3.6 %** | PASS |
| e=0.90 s12 | 0.0468 | 0.0480 | **2.6 %** | PASS |

The V3 arm carries substantially more energy than the untouched base (+177.8, delivered as a directed
superflow plus the phonons `heat` adds to reach it exactly) and yet the core/pair-scale density power spectrum
moves by at most a few percent. **PASS on every base, cleanly.**

## B2 — the pairs are visible in density (FAIL as written on 2/3; large effect present on all 3)

`S_band(P16)/S_band(0) − 1` over t ∈ [0, 300]:

| base | ratio | criterion (≥ 0.30) |
|---|---|---|
| e=0.60 | **+118.0 %** | PASS |
| e=0.90 s11 | +25.0 % | **FAIL** |
| e=0.90 s12 | +21.2 % | **FAIL** |

**FAIL as pre-registered on two of three bases.** The direction and the size of the effect are not in doubt —
16 injected pairs raise the density power at the core scale by a fifth to more than double, an order of
magnitude larger than B1's sector-only change — but the pre-set 30 % threshold, chosen before any run, was not
met at e = 0.90. The likely reason, reported not corrected: at e = 0.60 the base is nearly quiescent (T_b ≈
0.08, few thermal pairs) so 16 injected pairs dominate the band; at e = 0.90 the base already carries a
substantial thermal pair population (`n_v` ≈ 40–46 at the base energy, against 25 at e = 0.60), so the same
16 injected pairs are a smaller *relative* addition to an already-populated band. Composite verdict: **B2 FAILS
as written**; the qualitative claim it was meant to establish ("pairs move the density; the sector does not") is
supported by the tenfold gap between B1's percent-level and B2's ten-to-hundred-percent-level ratios, but the
specific numerical threshold was not calibrated to the base's own thermal pair content and should be in any
future round.

## B3 — the sector is read by the phase and the momentum (PASS, 2/2 evaluated; e=0.60 reported)

| base | W_x = 3 (V3) | W_x = 3 (V3P16) | W_x = 0 (arm 0) | W_x = 0 (P16) | f_K(V3) | criterion |
|---|---|---|---|---|---|---|
| e=0.90 s11 | 100 % | 100 % | 100 % | 100 % | 0.667 | **PASS** |
| e=0.90 s12 | 100 % | 100 % | 100 % | 100 % | 0.658 | **PASS** |
| e=0.60 (reported) | 100 % | 100 % | 100 % | 100 % | 0.916 | — |

The torus winding is exact and unslipped on every sample of every run (no phase slip in 1500 time units on
these clean-boost arms — unlike round 3's accidental e = 0.60 sector, which decayed from winding 2 to 0 by
slips; the difference is plausibly the construction, a smooth Fourier phase boost here versus an
imprinted-vortex phase there, but this is not tested). The momentum fraction at the imposed wavenumber is far
above the 0.15 threshold on every base (0.66–0.92) — the sector is read cleanly by both instruments the
pre-registration named.

## B4 — density reads cores, not net winding (PASS, 3/3, the crux comparison)

`|S_band(V3P16)/S_band(P16) − 1|` over t ∈ [0, 300]:

| base | S_band(P16) | S_band(V3P16) | ratio | criterion (≤ 0.15) |
|---|---|---|---|---|
| e=0.60 | 0.0249 | 0.0247 | **1.1 %** | PASS |
| e=0.90 s11 | 0.0583 | 0.0599 | **2.6 %** | PASS |
| e=0.90 s12 | 0.0558 | 0.0579 | **3.7 %** | PASS |

**The core prediction, confirmed cleanly on all three bases.** The same sixteen pairs carry statistically the
same density signature whether or not a winding-3 sector current is superposed on them, at a tenth of B2's own
effect size. Together with B1: **on this torus, a density-only observable cannot distinguish a rotating
(sector-carrying) configuration from a non-rotating one at matched core content** — the transplanted version of
Zhou et al.'s and Brax & Valageas's still-open question (`LITERATURE_REVIEW_SECTOR_LEAD.md`) answered, on the
torus, in the predicted direction.

## B5 — reported, not predicted

**Pair decay, P16 vs V3P16** (`n_v(t)`, blocks of 100 time units):
* e = 0.60: 25.4→8.0 (P16) vs 25.2→8.0 (V3P16) — indistinguishable.
* e = 0.90 s11: 46.4→17.4 (P16) vs 46.8→13.0 (V3P16) — decays *faster* with the sector present.
* e = 0.90 s12: 40.4→10.4 (P16) vs 38.6→16.8 (V3P16) — decays *slower* with the sector present.

**Bath heating, P16 vs V3P16** (`T_b`, first→last block): e = 0.60: +0.036 (P16) vs +0.041 (V3P16), matched;
e = 0.90 s11: +0.051 (P16) vs +0.089 (V3P16), larger with the sector; e = 0.90 s12: +0.033 (P16) vs +0.009
(V3P16), smaller with the sector. **No consistent sign**: whether the sector speeds, slows, or does not affect
pair annihilation and bath heating differs by base and by seed, with a single seed per arm. Not resolvable at
this statistics; a genuine effect, if any, needs several seeds per arm to separate from run-to-run noise.

**Post hoc, 2026-09-26: Gauthier et al.'s Onsager-cluster order parameter** (Science 364, 1264; the periodic
adaptation of `observables.onsager_dipole`, applied to the same `*_samples.npz` already on disk — no new run;
cosmology brief Tier 1 item 2), mean over the run:

| base | arm 0 | arm V3 | arm P16 | arm V3P16 |
|---|---|---|---|---|
| e = 0.60 | n/a (0 vortices) | n/a (0 vortices) | 0.203 | 0.220 |
| e = 0.90 s11 | 0.015 | 0.015 | 0.149 | 0.054 |
| e = 0.90 s12 | 0.010 | 0.013 | 0.057 | 0.060 |

**Confirms B1 by a second, independent instrument**: arm 0 and arm V3 (sector alone, no injected pairs) are
statistically indistinguishable (0.015 vs 0.015; 0.010 vs 0.013) — the imposed current changes the real-space
clustering geometry of the (essentially absent, at e = 0.90, thermal) vortex population no more than it changes
its density spectrum. For P16 vs V3P16 (pairs, with and without the sector): matched at e = 0.60 (0.203 vs
0.220, consistent with B4) and at e = 0.90 s12 (0.057 vs 0.060), but a factor of 2.8 lower with the sector
present at e = 0.90 s11 (0.149 → 0.054) — the same base/seed where the sector also *sped up* pair decay and
*increased* bath heating (above). **No consistent sign across bases/seeds**, same conclusion as the other B5
items: a real secondary effect at s11, if it is one, needs more seeds to separate from noise; not claimed here.

## Composite reading

| # | Verdict |
|---|---|
| B1 (sector invisible in density) | **PASS, 3/3** |
| B2 (pairs visible in density, ≥ 30 %) | **FAIL as written, 2/3** (large effect present on all 3, threshold not calibrated to base thermal content) |
| B3 (sector read by phase/momentum) | **PASS, 2/2 evaluated** |
| B4 (density blind to the sector at fixed pair content) | **PASS, 3/3** |

Three of the four pre-registered comparisons pass cleanly; the one that fails (B2) fails on a threshold, not on
direction or on order of magnitude, and the failure mode (base-dependent thermal pair background) is itself
informative for any future round's design. The prediction the whole round-4 protocol was built to test — that a
density observable cannot read a halo's net circulation, only its core content — holds on this torus.

## Infrastructure note

A background chain-watcher (`while pgrep -f "run_r3.py --parts C" ...; done; launch round 4`) never fired: its
own shell command line contains the literal string it searches for, so `pgrep -f` matched the watcher itself
forever. Part C finished at ≈ 11:20–11:28; round 4 was launched manually at 11:37 after the stall was found by a
direct check. Two other watchers with the same bug (one from this round, one idle since round 2) were also
found and killed. Recorded as project feedback (`feedback-pgrep-self-match-watchers` memory): future chain
watchers poll the target's output file content, not `pgrep -f` on its own invocation text.
