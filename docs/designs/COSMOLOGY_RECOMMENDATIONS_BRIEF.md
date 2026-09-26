# Brief: recommended directions for the cosmology stream, given the duality results and round 4

Written 2026-09-26, on request, while round-3 Part C2 (longer-equilibration diagnostic) runs in the
background. Synthesises: `paper/duality_sector.tex` + its 2026-09-26 addendum, `paper/cosmology_sectors.tex`,
`LITERATURE_REVIEW_SECTOR_LEAD.md` (four reports), round-4 results (`PGPE_R4_RESULTS.md`), and
`lean_src/ChargeLattice.lean`. No new claim is made here; this is a prioritised map of what the last round of
work opens up, ranked by what this repository can actually do versus what needs data or collaborators it
doesn't have.

## Where things stand, in one paragraph each

**Duality.** The criterion published in `duality_sector.tex` — a self-dual point pins a transition iff the two
sectors it exchanges are inequivalent phases on a discrete fixed-point set, and is otherwise a point on a
continuous moduli space with enhanced symmetry (compact boson) or a constraint on a fixed point that may or may
not be self-dual (SIT) — is now backed by an explicit mechanism, not just examples: non-invertible duality
defects and their anomaly-matching arguments (Aasen–Mong–Fendley; Choi–Córdova–Hsin–Lam–Shao;
Kaidi–Ohmori–Zheng; Shao; Hayashi–Tanizaki on Cardy–Rabinovici), added as a dated addendum. One real boundary
was found on the K3 side: Moore's `N(D) = h(D)` (entropy is a function of the sector) is exact for K3×T²
1/8-BPS dyons but does **not** generalise to 1/4-BPS T⁶/CHL dyons without an extra discrete invariant and
moduli-dependence (Dabholkar–Gaiotto–Nampuri; Sen) — footnoted in `cosmology_sectors.tex` and `ChargeLattice.lean`.

**Cosmology stream.** `ChargeLattice.lean` (15 theorems) states the K3×T² dyon discriminant and the
Bousso–Polchinski / Kaloper flux-lattice walk as elementary lattice facts. `cosmology_sectors.tex` reads three
domains through the "sector is the cause" lens: wave dark matter (sector = net circulation, pairs = interference
vortices, prediction: density cannot read the sector), dark energy (a walk on an integer lattice by
membrane/phase-slip nucleation), K3 (the attractor geometry is an *output* of the charges, closing the door on
any fluid↔K3 identification for good, not just as an unproven analogy).

**Round 4 (this repo's own numerics).** The wave-DM prediction was tested on our torus and held on 3 of 4
pre-registered comparisons (B1, B3, B4 clean passes; B2 a threshold miss, not a direction miss) — see
`PGPE_R4_RESULTS.md`. This is evidence *for the method*, not for any statement about real dark matter.

**Round 3 Part C / C2.** L = 128 failed the L≤64 admission criterion outright (reported honestly as a failure,
not extended); C2, a longer-equilibration rerun, is in flight to test whether that was an artifact.

## Recommended directions, ranked

### Tier 1 — inside this repository's competence, well-scoped, do next

1. **Formalise the anomaly-matching criterion (from the addendum) as a Lean statement**, at the level the
   literature review already scoped it: a finite abelian group of sectors, a duality as a bijection (as
   `CompactBoson.partition_dual` already is), and a criterion function on whether the two sectors it exchanges
   are equal — a discrete, checkable statement, not the full physics of anomaly inflow. This turns the
   addendum's prose into the same kind of machine-checked object as the rest of the programme, closing the gap
   between "cited" and "proved" that the addendum itself flags.
2. **Add the Gauthier et al. dipole-moment order parameter to our own vortex analysis pipeline**
   (`D = N^{-1}|Σ sgn(Γ_j) x_j|`, `observables.py`), and recompute it on round 2/3/4's existing vortex-position
   data (`*_samples.npz`, already on disk — no new runs needed). This gives a second, independently-motivated
   sector statistic to cross-check against `W(R)`; if the two agree everywhere they've been compared, that is
   itself worth a line in the next paper version. Cheapest, highest-value item on this list — hours, not runs.
3. **Recalibrate round 4's B2 threshold** (the pair-visibility criterion, 30 %, missed at e = 0.90 because the
   base's own thermal pair population dilutes the injected sixteen) **against each base's own thermal pair
   density** rather than a fixed number, and re-evaluate the existing round-4 data (no new runs) before
   deciding whether a round 5 is needed at all.
4. **Correct the K1–K5 Lean gap the rusty-SUNDIALS work surfaced is not this repo's** but the pattern is: the
   qf-pgpe Rust port (PR #56 on rusty-SUNDIALS) ported K1/K3/K4 as *tests*, not proofs — if a faster Rust engine
   becomes available (once #55/#56 are reviewed), the L = 128 equilibration question could be *scanned* (several
   `t_tr` values, not just one doubling) at a small fraction of the ~14–24 h/run Python cost. Track PR status
   before committing to more Python C-runs beyond C2.

### Tier 2 — needs data or code this repo does not have, but is a clear, citable next step

5. **The Ω = 0 compensated-vortex halo test**, in a real 3D self-gravitating simulation (Zhou et al. 2025's or
   Brax & Valageas 2025's own method) — both papers pose exactly this as their own open problem, and round 4
   answered the torus version. This is the single most valuable extension of the wave-DM direction, and it is
   explicitly not ours to run (no gravity solver, no 3D code here); the honest next step is a **collaboration
   proposal**, not a repo task: write to one of the two groups (or replicate their published method
   independently) rather than attempt a 3D gravitational GPE solver from scratch.
   **Checked 2026-09-26 (Zenodo, GitHub, Hugging Face; "download if needed"):** neither paper carries a code or
   data availability statement, and neither is findable as a dataset on Zenodo or Hugging Face under any search
   phrasing tried. Zhou et al. build on **BEC2HPC** (Gaidamour, Tang & Antoine, Comput. Phys. Commun. 265,
   108007), a published parallel spectral solver; one GitHub repository named `BEC2HPC-FFT` was found
   (0 stars, no description, unclear authorship link to the paper) — **not verified as the genuine release and
   not used**; treat any future use of it as needing independent verification first, per this project's own
   literature-gate rule. No usable download materialised; the recommendation stands as written (collaboration,
   not a repo task).
6. **The dark-energy roll-vs-cascade test** (Koren, Tsai & Wang's CMB-fluctuation bound,
   `r ≲ 10⁻⁵(β/H⋆)²`) needs real CMB data and a likelihood pipeline (CAMB/CLASS + a sampler) this repository
   does not have and should not attempt to rebuild. The correct next step, if this direction is pursued, is to
   **read that paper's own pipeline** and ask whether its published bound already constrains Kaloper's or the
   QCD-sector model's own parameter space (a literature-only task, no new numerics) before any attempt at an
   independent reanalysis.
   **Checked 2026-09-26:** one GitHub repository (`bao-x-reconstruction`, "BAO-only reconstruction of
   dark-energy density X(z) from DESI DR1/DR2... reproducing all published figures") was found and is **not
   used**: zero stars, no verifiable authorship, created within the last year, and its repository contents
   could not even be listed cleanly. A single unverified, anonymous repository claiming to reproduce a
   published analysis is not a citable source; using it would violate the same literature-gate rule that has
   protected every other claim in this programme. If this direction is pursued, the correct source remains the
   published papers' own supplementary data (DESI DR2's own public chains, when read through a real pipeline),
   not an unverified third-party reproduction.

### Tier 3 — open, interesting, and explicitly not recommended to start now

7. **Ising/SO(3)-Yang–Mills/Cardy–Rabinovici as a fourth Lean cross-domain case** beyond the compact boson —
   possible, but each is a nontrivial formalisation on its own (lattice gauge theory, θ-angle periodicity) with
   no existing Mathlib scaffolding comparable to `CompactBoson`'s; scope this only as its own round if the
   owner wants the cross-domain table to grow, not as a quick addition.
8. **A 3D wave-DM code from scratch** — explicitly against this repo's own stated boundary
   (`COSMOLOGY_SECTORS_PROPOSAL.md`: "will not run GPP halo simulations"); nothing in this review changes that
   boundary, and Tier 2 item 5 is the right-sized alternative.

## What NOT to do, restated

No cosmological number gets claimed regardless of any of the above (Ω, w(z), a boson mass, a lensing amplitude).
No revival of a fluid↔K3 identification — the DGN/Sen boundary found this round makes the "entropy is a
function of the sector" slogan *more* precise, not more general; it is not license to extend it past K3×T².
