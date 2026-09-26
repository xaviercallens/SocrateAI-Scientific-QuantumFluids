# Brainstorm: extending and communicating "duality is a structure; the sector is the cause"

Written 2026-09-26, on request, while round-3 C2 runs in the background. This is options, not commitments —
ranked by how well each fits the programme's own discipline (a real dependency chain, checked against the
literature, machine-checked where it can be; LL-15: check dependencies, not analogy) rather than by novelty
alone. Nothing here is started without a separate go-ahead.

## Part A — extending the theory

### A1. High confidence: natural sixth, seventh, eighth cases for the cross-domain table

These sit right next to what is already proven and would slot into the same criterion
(`duality_sector.tex` §3) without new machinery.

1. **RCFT modular data (Verlinde formula).** `SectorDuality.lean`'s finite-group Fourier transform *is* a
   toy instance of the real object: in a rational CFT, the primaries are the sectors, the modular $S$-matrix is
   the duality (Verlinde's formula gives the fusion coefficients as an $S$-matrix Fourier transform on the
   sector set), and $T$ generates the modular group already touched via `Fricke.lean`/`QHFricke.lean`'s
   $\Gamma_0(N)$. This closes a loop already half-open in this repository: formalising Verlinde's formula for a
   small worked RCFT (e.g. the Ising model's three primaries, or a $\widehat{su}(2)_k$ WZW model) would be a
   genuine, well-scoped seventh case, and Moore–Seiberg data is exactly the general framework GKSW cites.
2. **Particle–vortex / level-rank duality in the fractional quantum Hall effect** (Son's composite Dirac
   fermion, 2015; Seiberg–Senthil–Wang–Witten "duality web," 2016). Directly adjacent to the already-treated
   Lütken–Ross $\Gamma_0(2)$ material: the sector is the Landau-level filling / Chern number, the duality maps
   a theory of electrons to a theory of vortices at a different filling. Well-documented, citable literature;
   would extend the "quantum Hall: organisation, not cause" paragraph with a second, structurally different
   duality in the same physical system.
3. **AdS$_3$/CFT$_2$ black hole microstate counting (Strominger–Vafa).** A direct sequel to the K3 dyon
   section: the D1–D5 system's U-duality invariants and microstate degeneracy are governed by the same kind
   of charge-lattice discriminant as `ChargeLattice.lean` already states abstractly. This would not be a new
   physical claim, just the next worked instance of the same lattice statement — plausibly extendable with the
   *existing* Lean file (the discriminant theorems are already stated for a generic bilinear form).

### A2. Medium confidence: real literature work needed, worth scoping carefully before starting

4. **Seiberg duality in 4D $\mathcal N=1$ gauge theories** (electric–magnetic duality of a different flavour
   from T-duality — Coulomb vs. confining branch as the "sector"). Well-established but denser literature
   (Seiberg 1994 onward); would need its own literature-gate pass before any claim.
5. **Topological superconductors and the tenfold way** (Kitaev's classification; Majorana zero modes; fermion
   parity as the protected sector). Less clean as a "duality" story (more a classification than an exchange
   symmetry) — would need to check whether a genuine duality (not just a symmetry classification) is the right
   frame before forcing it into this programme's vocabulary.

### A3. Flagged, not recommended without a much stronger case first

6. Any "duality" framing of neural-network weight-space symmetries, or of biological/neural "topological
   sectors": these are **fashionable analogies without an established rigorous correspondence** to the
   Fourier-on-a-sector-group structure this programme actually proves things about. Per this project's own
   LL-15 rule (check dependencies, not analogy — the retraction record in `RETRACTIONS.md` exists because of
   exactly this failure mode once already), these should not be pursued unless a real, citable, checkable
   dependency chain is found first — not merely a suggestive resemblance.

## Part B — communicating what already exists

### B1. arXiv (checked, not yet done — a real gap)

The four papers (`causal_topology`, `astro_topological_measurement`, `sector_temperature`, `duality_sector`,
`cosmology_sectors`) are on Zenodo and Hugging Face only. **Due diligence done 2026-09-26**: no prior arXiv or
INSPIRE record exists for "Callens, Xavier" (INSPIRE search: 0 hits). This matters practically: arXiv's
hep-th/cond-mat categories require **endorsement** from an existing arXiv author in that category for a first
submission — this is a real hurdle, not a formality, and should be planned for (identifying an endorser,
likely via the arXiv endorsement request flow, or submitting first to a category with lower barriers such as
`physics.gen-ph` or `physics.pop-ph` if endorsement cannot be arranged, with the tradeoff that those categories
get less attention from the target community). Worth doing regardless, because arXiv is what makes a paper
*discoverable and citable* by the SymTFT/generalized-symmetries community the 2026-09-26 addendum already
engages with — Zenodo DOIs are citable but are not searched the way arXiv is.

### B2. The natural reader community already exists, and is already cited

The addendum to `duality_sector.tex` cites Aasen–Mong–Fendley, Gaiotto–Kapustin–Seiberg–Willett,
Choi–Córdova–Hsin–Lam–Shao, Kaidi–Ohmori–Zheng, Shao, and Hayashi–Tanizaki — this is precisely the "generalized
/ categorical symmetries" community (much of it associated with the Simons Collaboration on Global Categorical
Symmetries). They would very plausibly find the cross-domain criterion and the machine-checked instances
interesting, *and* would be the right audience to stress-test the DGN/Sen K3 boundary and the criterion itself.
**Recommended low-risk step**: once on arXiv, this is the kind of paper that gets noticed by that community
through ordinary channels (arXiv listings, citations) without needing direct outreach — this project's own
pattern (per memory) is to hold direct author contact until a claim is fully checked (Godfrin: "contact on
hold until PRB version of record is read"); the same caution should apply here — publish and let it be found,
rather than emailing authors unsolicited about work that engages with theirs.

### B3. Cheap, low-risk feedback channels

- **Physics Stack Exchange / MathOverflow**: post the sharpest single claim (e.g. "when does a self-dual point
  pin a phase transition?") as a well-posed question referencing the criterion, without claiming priority —
  a cheap way to get expert pushback before a wider audience sees it in a paper.
- **A short, honest "what this is and isn't" note** could preempt the most likely objection (that this is
  "just" Savit 1980 restated) by stating explicitly, as the papers already do, that the mathematics is
  elementary and the contribution is the machine-checked distinction and the criterion — this framing already
  exists in the papers' own text and should carry over to any shorter public-facing version.

### B4. A more accessible, non-paper format (an option, not started)

If the goal is to reach people who will not read a LaTeX paper: a single interactive page (this session's
Artifact tool, `artifact-design` skill) walking through the cross-domain table and the criterion — e.g. an
explorable version of "here is a self-dual point; is it forced to be a transition?" with the five worked cases
as clickable examples, and the compact-boson radius plot ($\sqrt2$ vs $2\sqrt2$) as a live figure. This is
explicitly **not started** — it is the kind of public-facing artifact this session's tools support, and would
need the owner's go-ahead on scope (a static explainer vs. something with live computation) before building.

## What this does not do

No item here is executed without a separate decision to proceed. Nothing in Part A commits to a new physical
claim; nothing in Part B commits to contacting anyone. This is the option set, organised by how well each
option matches the programme's own standard of evidence, not by which is most exciting to try.
