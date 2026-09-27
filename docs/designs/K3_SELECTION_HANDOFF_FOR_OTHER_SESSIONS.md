# K3 selection: what this repository's duality work found, and how to use it correctly

**Audience: another Claude Code session** working on K3×T² compactifications, vacuum/moduli selection, or
dark-matter/dark-energy cosmology in a sibling repository (this was written after a scan of
`SocrateAI-Scientific-AutoEvolve-K3xT2`, `SocrateAI-Scientific-Hypergraph-K3*T2`,
`SocrateAI-Scientific-Quantum-K3*T2` and `SocrateAI-Scientific-Videoo-K3*T2` on this machine, 2026-09-26). It is
self-contained: read it before extending any "K3 selects the vacuum" or "duality causes/explains the observed
parameters" claim. Source repository:
[SocrateAI-Scientific-QuantumFluids](https://github.com/xaviercallens/SocrateAI-Scientific-QuantumFluids),
released as `paper/duality_sector.tex` and `paper/cosmology_sectors.tex` (Zenodo DOI
10.5281/zenodo.22976724, v1.13.0). Lean sources: `lean_src/CompactBoson.lean`, `lean_src/ChargeLattice.lean`,
`lean_src/SectorDuality.lean` (all Comparator-accepted, two independent kernels).

## 1. The one-sentence result, and why it is not a slogan

**A duality is a reindexing of a lattice of sectors that preserves a spectrum; it is not itself a physical
cause. The sector — an integer that crosses a threshold, proliferates, annihilates, or is imposed — is what
acts.** This was tested, not assumed, across five domains (compact-boson T-duality, Kramers–Wannier/Ising,
string-gas cosmology, superconductor–insulator transition, quantum Hall $\Gamma_0(2)$) and is now backed by an
explicit mechanism from the non-invertible-symmetry literature (Aasen–Mong–Fendley 2016; Gaiotto–Kapustin–
Seiberg–Willett 2015; Choi–Córdova–Hsin–Lam–Shao 2022; Kaidi–Ohmori–Zheng 2022; Shao's 2023 TASI lectures;
Hayashi–Tanizaki 2022 on Cardy–Rabinovici) — every DOI/arXiv ID cited in `duality_sector.tex` and its
2026-09-26 addendum was independently verified against Crossref before use.

## 2. What this means for K3, precisely (Moore 1998, hep-th/9807087)

For type II string theory on K3 × T², a BPS dyon is a charge vector $\gamma = (p, q) \in H^2(\mathrm{K3},
\mathbb Z)$. **The attractor mechanism fixes the K3's complex structure from the charges**:
$$\Omega \propto q - \bar\tau p, \qquad \tau = \frac{p\cdot q + \sqrt{D}}{p^2}, \qquad D(p,q) = (p\cdot q)^2 - p^2 q^2.$$
The horizon area and the BPS degeneracy read **one integer**, $D$: $A/4\pi = \sqrt{-D}$,
$\log\dim\mathcal H_{\rm BPS} = \pi\sqrt{-D} + \cdots$ (Dijkgraaf–Verlinde–Verlinde 1997). The U-duality group
(here $SL(2,\mathbb Z)\times O(6,22;\mathbb Z)$) acts on the charges and **preserves** $D$ — this is machine-checked
in this repo, for a general bilinear form, as `ChargeLattice.disc_sl2_invariant`. But the number of
U-inequivalent charge vectors at the *same* $D$ is the class number $h(D)$ (Moore's own theorem,
$N(D) = h(D)$): many sectors, one entropy, and no symmetry of string theory permutes them into each other.

**The consequence for "K3 selection":**

* The K3 that appears in this construction is an **output of the charges**, not an input a moduli-scan can
  freely dial to match observed cosmological parameters. If a project's pipeline treats a *chosen* K3 geometry
  (or a point in its moduli space) as producing a specific 4D observable (an FRW equation-of-state parameter,
  $H_0$, $S_8$, $\Omega_m$), that is a **different physics question** from the one Moore's attractor equations
  answer. The attractor mechanism is about a BPS black hole's horizon data as a function of its charges in a
  fixed compactification; it says nothing about which K3 (or which point in its moduli space) a 4D effective
  theory's cosmological constant, matter density, or clustering amplitude select. Conflating the two is the
  single most consequential mistake to check for.
* If a pipeline's actual mechanism is moduli stabilisation (flux compactification, a KKLT/LVS-type potential,
  or a discretuum scan à la Bousso–Polchinski) rather than the BPS attractor equations, say so explicitly and
  cite that literature instead — **`ChargeLattice.lean`'s Bousso–Polchinski and Kaloper theorems already give
  a machine-checked treatment of the flux-lattice-walk mechanism** (`bp_step`, `bp_min_at_zero`,
  `kaloper_terminates`) if that is the intended physics; it is a different lattice from the K3 dyon lattice
  and should not be presented as the same computation.
* **A real, checked boundary, found 2026-09-26**: Moore's $N(D) = h(D)$ is exact for **1/8-BPS K3×T² dyons**
  only. For **1/4-BPS dyons on heterotic/$T^6$ or CHL orbifolds** (a different, related but distinct setting),
  Dabholkar–Gaiotto–Nampuri (hep-th/0702150) show the continuous-duality invariants alone "do not uniquely
  specify the state" — an extra discrete invariant ($I = \gcd(Q_e\wedge Q_m)$) is needed — and Sen (0705.3874)
  shows the degeneracy additionally jumps across walls of marginal stability in moduli space (reproduced by
  two-centred black hole solutions appearing/disappearing). **If a K3-selection pipeline's charge lattice is
  not literally Moore's K3×T² setting, "the entropy/selection is a function of the sector" needs this
  qualification, not a citation of Moore alone.**
* **No fluid↔K3 identification is licensed by anything in this stream.** This program spent three
  pre-registered rounds (`docs/designs/PGPE_R2_PREREG.md` onward) testing and retracting exactly that kind of
  identification (a superfluid's dual-length involution as literal K3×T² mirror symmetry); the attractor
  theorem is *why* it fails structurally — a fluid has no charge vector $(p,q)$, only an integer winding, so
  there is no input to Moore's equations for it to produce a K3 from. This is stated as a closed question, not
  a live one, in `cosmology_sectors.tex` §3.

## 3. The Fricke/mirror involution: what it is, precisely

The Dolgachev–Nikulin mirror involution $W_N$ on $\Gamma_0(N)+N$ (Dolgachev 1996, alg-geom/9502005) exchanges
lattice polarisations $M \leftrightarrow M^\perp$ inside $\mathrm{II}_{3,19}$. This is a reindexing of the
*same kind* as `CompactBoson.partition_dual` (§1's thesis, machine-checked): it preserves structure and moves
no dyon's entropy. It is **not** a Hall-system symmetry (`QHFricke.lean`: the Fricke element fixes the
critical orbit's *location* but maps every plateau off the odd-denominator class it would need to preserve to
be a genuine symmetry of the physics) and it is **not** a bridge between a superfluid's dual-length involution
and K3 mirror symmetry (the earlier, retracted identification). If a K3-selection project uses Fricke
involutions as part of its moduli-space structure, that use is *consistent* with what this repo found — the
involution is real, checked, and structurally meaningful — but it organises the lattice; it is not itself why
any particular point is physically selected.

## 4. Concrete checklist before publishing a K3-selection or duality-causes-cosmology claim

1. **Is the mechanism actually the BPS attractor equations (Moore), or moduli stabilisation / a flux
   discretuum (Bousso–Polchinski, KKLT)?** These are different physics; name which one is being used, and do
   not present K3-attractor machinery as if it computed a 4D FRW observable directly.
2. **If BPS attractors: is the setting literally K3×T² (1/8-BPS)?** If it is heterotic/$T^6$ or a CHL orbifold
   (1/4-BPS), the entropy/selection additionally depends on the Dabholkar–Gaiotto–Nampuri discrete invariant
   and the moduli-space chamber (Sen) — state this, or the claim is not the theorem being cited.
3. **Is a specific numerical cosmological parameter ($w_0$, $H_0$, $\Omega_m$, $S_8$, …) being claimed as
   "selected" by a topological/duality argument?** If so, the causal chain from (charge lattice → K3 geometry
   → 4D effective couplings → that specific number) needs to be stated explicitly and each link's own
   literature cited; a topological "sector is the cause" argument (§1) supports *that a sector, not a duality,
   does the causal work at whichever link it appears* — it does not by itself license skipping links or
   quoting a number without the pipeline that produced it.
4. **Is a duality (Fricke, mirror symmetry, any $SL(2,\mathbb Z)$-type structure) being cited as the reason a
   particular point is physical?** Apply this repo's criterion (`duality_sector.tex` §3 + 2026-09-26 addendum):
   a self-dual point is forced to be physically distinguished only when it separates two *inequivalent* sectors
   on a *discrete* fixed-point set (Ising, $SO(3)$ Yang–Mills at $\theta=\pi$); on a *continuous* moduli space
   (the compact boson's radius; presumably a K3 moduli direction) a self-dual point is generically just a point
   of enhanced symmetry, not a forced transition or a forced selection.
5. **Run the literature gate.** Every claim in this repo that survived was checked against Crossref/arXiv
   before being written down; several were retracted after this check (`RETRACTIONS.md`,
   `LEDGER.md`'s CLAIM history). If a sibling project's README states a result "to 3 significant figures" from
   a "deterministic" topological selection, that precision claim itself needs the same check: does the actual
   pipeline (as opposed to the framing) produce that number deterministically from the stated inputs, or is
   there a fit, a prior, or a calibration step folded in?

## 5. What to read, in order

1. `paper/duality_sector.tex` (the criterion, machine-checked cases, the 2026-09-26 addendum).
2. `paper/cosmology_sectors.tex` (K3 §3; the boundary footnote; the dark-matter and dark-energy sector
   readings with their own falsifiable predictions and honest exclusions).
3. `lean_src/ChargeLattice.lean` (the actual Lean statements: `disc_sl2_invariant`, `bp_step`,
   `kaloper_terminates`) and `lean_src/SectorDuality.lean` (the finite-group algebraic backbone).
4. `docs/designs/LITERATURE_REVIEW_SECTOR_LEAD.md` (four-part review; the Dabholkar–Gaiotto–Nampuri/Sen
   boundary section in particular).
5. `docs/designs/COSMOLOGY_RECOMMENDATIONS_BRIEF.md` (this repo's own prioritised next steps — useful context
   for what has already been tried and what remains open).

## 6. What this repo will not do, and does not ask any other session to do on its behalf

No cosmological number is claimed here (no $\Omega$, no $w(z)$, no $H_0$, no boson mass). This handoff does not
assert that any sibling project's specific results are wrong — their methodology was not read in the depth a
verdict would require, only their public framing. It states what this programme's own hard-won boundaries are,
so that a session working on K3 selection elsewhere can check its own pipeline against them before extending a
claim that touches the same mathematics.
