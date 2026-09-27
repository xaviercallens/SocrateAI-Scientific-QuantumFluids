# Deep literature review, "the sector is the cause" applied to cosmology — four parallel reviews

Commissioned 2026-09-25 ("fait une litterature review approfondit en parallele qui peut nous aider maintenant
qu on a une piste"), while round 4 ran. Four subagents, alphaXiv + Crossref verification (every DOI below was
independently re-checked against `curl https://api.crossref.org/works/<doi>` by this session, not only by the
subagent). Three reports landed (DM vortex observables; duality as topological defect; discrete dark energy);
the fourth (random-wave vortex statistics) is appended when it arrives. First two attempts on all four failed
on Fable 5.1's monthly spend limit (HTTP 429) and were relaunched on Sonnet 5 — no content lost.

**How to read this document.** Per report: verified citations, what is established, how it bears on our
reading, and one actionable item. At the end, a single **"corrections applied"** section lists every place this
review changed a claim already on `master` (a citation, a caveat, a bib entry) and the commit that did it.

---

## Report 1 — DM vortex observables: is any halo observable phase-sensitive?

**Question posed.** Round 4's prediction is that a density-only observable (lensing, a projected map) reads
vortex *cores* — the same for a lattice vortex (sector) and an interference vortex (pair) — while the sector
itself is read only by the phase or the momentum distribution.

### Density-only heating/friction observables (confirm the prediction)
- **Hui, Ostriker, Tremaine, Witten 2017**, *Ultralight scalars as cosmological dark matter*, Phys. Rev. D 95,
  043541, DOI 10.1103/PhysRevD.95.043541 (arXiv:1610.08297). Quasiparticle heating framework from the density
  power spectrum; foundational, not itself sector-sensitive.
- **Bar-Or, Fouvry & Tremaine 2019**, *Relaxation in a Fuzzy Dark Matter Halo*, ApJ 871, 28, DOI
  10.3847/1538-4357/aaf28c (arXiv:1809.07673). Diffusion coefficients built purely from the density correlation
  function; **a vortex pair and a sector vortex embedded in the same random-phase field contribute identically**
  to this heating rate.
- **Church, Mocz & Ostriker 2019**, *Heating of Milky Way disc stars...*, MNRAS 485, 2861, DOI
  10.1093/mnras/stz534 (arXiv:1809.04744). "Wavelet" heating from the density power spectrum of granules; no
  circulation term.
- **Dalal & Kravtsov 2022**, *Excluding fuzzy dark matter with sizes and stellar kinematics...*, Phys. Rev. D
  106, 063517, DOI 10.1103/PhysRevD.106.063517 (arXiv:2203.05750). The FDM mass bound (m > 3×10⁻¹⁹ eV) comes
  entirely from granule *density* contrast heating Segue 1/2; density-only.

**Reading.** Every quantitative dynamical-heating observable found is a functional of the density power
spectrum alone. None depends on the sign or existence of net circulation — directly confirms the "pair-blind"
half of the prediction.

### Lensing (confirms the prediction; one open gap)
- **Chan, Schive, Wong, Chiueh, Broadhurst 2020**, *Multiple Images and Flux Ratio Anomaly of Fuzzy
  Gravitational Lenses*, Phys. Rev. Lett. 125, 111102, DOI 10.1103/PhysRevLett.125.111102 (arXiv:2002.10473).
  Attributes the anomaly to "large-amplitude, small-scale density fluctuations... δρ/ρ ∼ 1"; no vortex/circulation
  concept anywhere. Pure density-granule paper.
- **Amruth, Broadhurst et al. 2023**, *Einstein rings modulated by wavelike dark matter...*, Nature Astronomy 7,
  736, DOI 10.1038/s41550-023-01943-9 (arXiv:2304.09895). Notes "there is no counterpart in ϱ_DM for the equally
  pervasive under-dense fluctuations in ψ_DM" — the closest approach in this literature to flagging vortex-like
  under-densities as distinct — but never computes a circulation statistic; a Gaussian random field of density
  only.
- **Laroche, Gilman, Li, Bovy & Du 2022**, MNRAS 517, 1867, DOI 10.1093/mnras/stac2677. Same density-power-
  spectrum category.
- **Zhou, Leung, Poon & Chu 2025**, arXiv:2512.03357 (arXiv-only; no journal DOI yet). **The key paper.** They
  define vortices properly by circulation (∮v·dl = 2jπ) but their lensing observable is entirely the projected
  column density, and — this is the gap that matters — **every simulated case has Ω > 0 baked into the initial
  condition; they never run an Ω = 0 halo with a compensated (net-zero) vortex population at matched energy.**
  Quoted: *"It will be important for a future study to identify ways to distinguish if the magnification
  anomalies are caused by underdensity 'holes' (due to vortices) or overdensity subhalos."* **This is our exact
  question, posed as an open problem by the paper whose method our round-4 design is closest to, and left
  untested by them.** Optimal signal needs σ_PSF ≲ 10 mas (VLBI); gone by 70 mas (HST-like) — consistent with
  what we already cite.
- **Hui 2021** (solo review, see below), footnote 24: *"an underdensity, such as around a vortex ring, would
  effectively cause a deflection of the opposite sign compared to an overdensity"* — the clearest single
  statement that a vortex's lensing signature is treated as a **signed density perturbation**, not a
  phase/circulation observable, in the literature as it stands.

**Not found:** Powell et al. 2023 (as cited in our brief) — could not be located under that exact citation;
Banik & Zhao — not located under the search terms used. Neither is load-bearing for our claims; flagged, not
guessed.

### Angular momentum: sector count vs. dispersion support (a misattribution corrected)
- **Hui 2021** (solo, not "Hui et al."), *Wave Dark Matter*, Annu. Rev. Astron. Astrophys. 59, DOI
  10.1146/annurev-astro-120920-010024 (arXiv:2101.11735). Gives the universal vortex-density statistic we tested
  in Part A: *"on average there is about one vortex ring per de Broglie volume in a virialized halo. This has
  been verified analytically in the random phase halo model, and in numerical wave simulations."* — a fixed,
  circulation-blind background population (the "pairs"), exactly the object our Part A instrument measured.
- **Schobesberger, Rindler-Daller & Shapiro 2021**, *Angular Momentum and the Absence of Vortices in the Cores
  of Fuzzy Dark Matter Haloes*, MNRAS 505, 802, DOI 10.1093/mnras/stab1153 (arXiv:2101.04958). The quantitative
  source of "dispersion-supported, angular momentum without a vortex in the core": *"for typical halo spin
  parameters, angular momentum per particle is below ℏ, the minimum required even for one singly-quantized
  vortex in the centre. Even for larger angular momentum, however, vortex formation is not energetically
  favoured."* Vortices, when present, live in the turbulent envelope, not the soliton core (citing Schive 2014,
  Schwabe 2016, Mocz 2017), and their statistics there are "not well-studied." **Added, not corrected**: this
  argument was not yet in `COSMOLOGY_SECTORS_PROPOSAL.md` (the task brief to this review's subagent paraphrased
  it loosely as "Hui et al. 2020 §7," which is not a citation this repository had committed); it is now added
  with the proper citation (Rindler-Daller & Shapiro 2012 + Hui's 2021 review + this paper).
- **Gap confirmed**: no paper in Schive, Mocz, Veltmaat, Nori–Baldi, or May–Springel reports a **net circulation
  or signed vortex-count imbalance** in a cosmological ULDM halo — every published statistic is an abundance
  (magnitude, sign-blind) measure. **No one has yet measured the observable that would isolate the sector in a
  realistic halo** — the gap our round-4 protocol targets, transplanted to the torus because we have no gravity
  solver.

### Reconciling fuzzy vs. Thomas–Fermi regimes (Task 4)
Fuzzy (non-self-interacting): vortex cores have size ∼λ_dB and δρ/ρ ∼ 1, statistically identical to every other
interference granule — no separate "vortex regime" of contrast exists, so no lensing method singles them out
(consistent with the generic, undifferentiated GRF treatment in Chan/Amruth). Thomas–Fermi (self-interacting,
Zhou et al.): the core scale R₀ = π√(g/4πGm²) is independent of λ_dB and can be macroscopic, so a regular,
low-multiplicity vortex lattice sits on a comparatively smooth background and *can* produce a resolvable ∼10 mas
signature. **Zhou et al.'s detectability claim is conditional on strong self-interaction, not a generic FDM
prediction** — a caveat now added where we cite them.

**Top 5 (this report):** Zhou 2025 (arXiv:2512.03357, most actionable — extend with an Ω=0 control); Hui 2021
review (DOI 10.1146/annurev-astro-120920-010024); Schobesberger 2021 (DOI 10.1093/mnras/stab1153); Amruth 2023
(DOI 10.1038/s41550-023-01943-9); Álvarez-Rios, Tena-Contreras & Guzmán 2025, *Kinematic Imprints of vortex-lines
of BEC Dark Matter on Baryonic Matter*, Phys. Rev. D, DOI 10.1103/x9mt-wprk (arXiv:2506.17535) — a genuine
circulation-defined vortex, but their diagnostic (a Laplacian-of-Gaussian filter on projected gas *density*) is
still density-mediated, not phase-mediated; no matched vortex-pair control run either.

**No published result tests or contradicts "lensing cannot read net circulation" — the gap is real and open.**

---

## Report 2 — Duality as a topological defect: the modern literature, and two real corrections

### Duality-as-Fourier-transform-on-sectors, machine-checkable
- **Gaiotto, Kapustin, Seiberg, Willett 2015**, *Generalized Global Symmetries*, JHEP 02 (2015) 172, DOI
  10.1007/jhep02(2015)172 (arXiv:1412.5148). *"Such higher-form symmetries are important in the context of
  duality, where several different Lagrangians describe the same theory... the S-operation is a discrete Fourier
  transform of ℤ_M via Poincaré duality between H^{q+1}(M,G) and H^{d-q-1}(M,Ĝ)."* **Directly supports** our
  thesis at the sharpest level found: duality = Poisson/Fourier reindexing of a sum over sectors; physics
  (anomalies, symmetry breaking) is a separate structure layered on top. Actionable: the S/T action on a finite
  abelian sector group is close to a Lean statement in the style of `CompactBoson.partition_dual`.

### The sharp mechanism for "self-dual point = transition, or not"
- **Aasen, Mong & Fendley 2016**, *Topological Defects on the Lattice I: The Ising Model*, J. Phys. A 49,
  354001, DOI 10.1088/1751-8113/49/35/354001 (arXiv:1601.07185). *"Duality is not a symmetry in the traditional
  sense; while a duality transformation can be implemented by an operator commuting with the transfer
  matrix/Hamiltonian, this operator is not unitary or even invertible."* The cleanest one-line physics citation
  for "duality is a structure, not a cause."
- **Choi, Córdova, Hsin, Lam & Shao 2022**, *Non-invertible duality defects in 3+1 dimensions*, Phys. Rev. D
  105, 125016, DOI 10.1103/physrevd.105.125016 (arXiv:2111.01139). Explicit lattice Poisson resummation
  exhibiting the defect as a Chern–Simons coupling between a lattice and its dual. For 3+1d ℤ₂ lattice gauge
  theory at its self-dual point, a **general anomaly-matching (SPT) argument forces the IR phase to be
  non-trivially gapped** — matching the known first-order confinement/deconfinement transition. This *sharpens*
  our criterion: it is not the duality itself but a provable anomaly obstruction that forbids the trivial phase
  at some self-dual points.
- **Kaidi, Ohmori & Zheng 2022**, *Kramers–Wannier-like Duality Defects in (3+1)d Gauge Theories*, Phys. Rev.
  Lett. 128, 111601, DOI 10.1103/physrevlett.128.111601 (arXiv:2111.01141). SO(3) Yang–Mills at θ = ±π: *"This
  suggests that there should be a phase transition at these fixed values of theta."* Explicit phase diagram: the
  two sides of the self-dual point are a ℤ₂ TQFT and a trivial gapped phase — **physically inequivalent sectors**,
  which is why the self-dual point is a transition. A clean new cross-domain table entry: *self-dual point =
  transition exactly when the two sectors it exchanges are inequivalent phases.*
- **Shao, TASI lectures "What's Done Cannot Be Undone"**, arXiv:2308.00747 (lecture notes; no independent
  journal DOI). Footnote 33: *"Away from the critical point, Kramers–Wannier 'duality' is not a duality relating
  two equivalent descriptions of a single system. Rather, it is a map from the high-temperature phase to the
  low-temperature phase."* And, on the Maxwell-theory/compact-boson analogue: *"At the self-dual point τ = i,
  the duality defect reduces to an invertible ℤ₄ symmetry."* This is the mechanism behind our already-published
  observation (BKT ≠ self-dual radius): the compact boson's self-dual points sit on a **continuous moduli
  space** with enhanced (sometimes invertible) symmetry, never a transition; Ising/ℤ₂-gauge-theory/SO(3)-YM
  self-dual points sit **between two gapped, inequivalent phases**, forcing a transition. Two structurally
  different kinds of self-duality, now with an explicit categorical criterion instead of only a numerical
  observation (√2 ≠ 2√2).

### Cardy–Rabinovici: SL(2,ℤ) self-duality is not naive
- **Cardy & Rabinovici 1982**, Nucl. Phys. B205, DOI 10.1016/0550-3213(82)90463-1. The founding SL(2,ℤ) phase
  diagram of the ℤ_N clock/Coulomb-gas model.
- **Hayashi & Tanizaki 2022**, *Non-invertible self-duality defects of the Cardy–Rabinovici model...*,
  arXiv:2204.07440. *"Naively, these operations seem to act as the self-duality of the model, but it is not the
  case."* Genuine self-duality needs gauging the electric one-form symmetry with a discrete θ-term. At the
  ST⁻¹ fixed point τ* = e^{iπ/3}, three first-order transition lines meet, cyclically exchanging the Higgs,
  monopole-confinement and dyon-confinement phases, and a **mixed gravitational anomaly (evaluated on K3) rules
  out a trivially gapped phase there** — an anomaly argument, not the duality symmetry itself. **Correction
  applied**: any future statement treating "SL(2,ℤ) self-dual points" as automatically well-defined dualities
  should note this subtlety (duality-as-written requires gauging first).

### K3/dyon degeneracy: our K3×T² statement confirmed; a real boundary found for where it stops
- **Moore 1998**, arXiv:hep-th/9807087 (no independent journal DOI — long report). Re-verified: *"N(D) = h(D)"*
  for primitive K3×T² charges. **This confirms, unchanged, our `ChargeLattice.lean`/`cosmology_sectors.tex`
  statement** ("entropy is a function of D; the class number h(D) counts inequivalent sectors with the same
  entropy") — it is literally Moore's own theorem in the setting we cited.
- **Dabholkar, Gaiotto & Nampuri 2008**, *Comments on the Spectrum of CHL Dyons*, JHEP 01 (2008) 023, DOI
  10.1088/1126-6708/2008/01/023 (arXiv:hep-th/0702150). For the *different* setting of 1/4-BPS dyons on
  heterotic/T⁶ (not Moore's 1/8-BPS K3×T² case): *"the three [continuous-duality] invariants... do not uniquely
  specify the state and the degeneracy will depend on additional data."* They exhibit an extra discrete
  invariant I = gcd(Q_e ∧ Q_m) (genus = I+1 of the dual M5-brane realization) not captured by the quartic
  discriminant Δ.
- **Sen 2007**, *Two Centered Black Holes and N=4 Dyon Spectrum*, JHEP 09 (2007) 045, DOI
  10.1088/1126-6708/2007/09/045 (arXiv:0705.3874). The degeneracy **jumps across walls of marginal stability in
  moduli space** — reproduced by the appearance/disappearance of two-centred black-hole solutions — i.e. it is
  explicitly moduli-dependent, not a pure function of duality-invariant charge data.
- **Boundary drawn.** Our K3×T² claim (Moore's 1/8-BPS setting) needs no correction. The generic slogan
  "entropy is a function of the sector" is too strong if extended, unqualified, to 1/4-BPS T⁶/CHL dyons: there
  the sector must include the extra discrete invariant I, and even then the count can be moduli-dependent. Noted
  as a footnote/caveat wherever the slogan appears outside Moore's exact setting.

### Philosophy of physics
- **de Haro & Butterfield 2019**, *On Symmetry and Duality*, Synthese, DOI 10.1007/s11229-019-02258-x
  (arXiv:1905.05966). *"Duality does not imply physical equivalence. Two theories can be duals... without their
  making the very same claims about the world."* The cleanest available philosophical anchor for "duality is a
  structure, not itself a physical claim."
- **Rickles 2017**, *Dual theories: 'Same but different' or 'different but same'?*, Stud. Hist. Phil. Mod. Phys.,
  DOI 10.1016/j.shpsb.2015.09.005. Title alone states the tension our reading resolves structurally.
- **Matsubara 2011/2013**, *Realism, underdetermination and string theory dualities*, Synthese, DOI
  10.1007/s11229-011-0041-3.
- **Huneman 2010**, *Topological explanations and robustness in biological sciences*, Synthese, DOI
  10.1007/s11229-010-9842-z. The verified anchor for "topological explanation is non-causal" — replaces the
  unverified "Ross 2020 / Kostić" pairing our brief asked for (not found; do not cite as confirmed).

**Top 5:** Aasen–Mong–Fendley (10.1088/1751-8113/49/35/354001); de Haro & Butterfield
(10.1007/s11229-019-02258-x); Choi–Córdova–Hsin–Lam–Shao + Shao TASI (10.1103/physrevd.105.125016,
arXiv:2308.00747); Hayashi–Tanizaki on Cardy–Rabinovici (arXiv:2204.07440); Dabholkar–Gaiotto–Nampuri + Sen
(10.1088/1126-6708/2008/01/023, 10.1088/1126-6708/2007/09/045).

**Places the thesis was too strong, now qualified:** (1) "entropy is a function of D" — fine for Moore's
K3×T² setting, false in general for 1/4-BPS T⁶/CHL dyons without the extra invariant I and moduli-dependence;
(2) Cardy–Rabinovici SL(2,ℤ) self-duality requires gauging first, is not naive; (3) "Ross 2020" on topological
explanation is unverified — use Huneman 2010 instead.

---

## Report 3 — Discrete dark energy: the roll-vs-cascade question, sharpened

### DESI DR2 and non-parametric w(z)
- **DESI Collaboration 2025**, *DESI DR2 Results II*, Phys. Rev. D 112, 083515, DOI 10.1103/tr6y-kpc6
  (arXiv:2503.14738). w0 = −0.838 ± 0.055, wa = −0.62 (+0.22/−0.19) with Pantheon+; significance vs ΛCDM
  2.8σ–4.2σ depending on the SN sample. Their own 3-bin piecewise-constant w(z) is *consistent with* CPL — no
  separate step signal in the official reconstruction.
- **Lodha et al. 2025**, *Extended Dark Energy analysis using DESI DR2 BAO*, Phys. Rev. D 112, 083511, DOI
  10.1103/w4c6-1r5j (arXiv:2503.14743). Explicit binned (3–8 bins) and Gaussian-process reconstructions:
  *"introducing additional degrees of freedom does not significantly improve the fit... would be disfavored from
  a model comparison perspective."* **No step-like model beats CPL at equal complexity.**
- **Wang, Feng & Lu 2026**, arXiv:2608.08007. The sharpest published per-bin precision: 7 bins jointly on
  CMB+BAO+SN via simulation-based inference; only the lowest bin (w0 = −0.90 ± 0.05) deviates (∼2σ), bins at
  z ≳ 1.4 are unconstrained.
- **Ibarra-Uriondo & Bouhmadi-López 2026**, arXiv:2602.12347. Explicitly compares a discrete-step "ladder"
  Λ_sCDM model (N = 8 Heaviside steps) against smooth AdS-to-dS interpolations: *"the transition is inferred to
  span a redshift interval of roughly ≲ 3.5–4.5, pointing to a gradual evolution rather than a sharp transition,
  in contrast with earlier expectations."* DESI BAO alone pushes any abrupt sign-flip to z† > 2.41 (95% CL),
  **beyond the DESI-probed range** — current data disfavour a discrete sign-flip inside the measured window.

### Bubble nucleation phenomenology — the sharpest available discriminator
- **Kaloper 2025**, *Discretely Evanescent Dark Energy*, **now published**: JCAP 11 (2025) 075, DOI
  10.1088/1475-7516/2025/11/075 (arXiv:2506.04317). Concrete numbers confirmed: bubble radius at nucleation
  ∼ mm; percolation condition Γ/Ĥ⁴ ≳ 0.24; Ω_GW < 10⁻⁹ at f ≲ 10⁻¹² Hz (below the nHz PTA band — the paper's own
  proposed PTA test is optimistic, not yet demonstrated feasible). **Bib DOI corrected from arXiv-only to this
  published DOI.**
- **Koren, Tsai & Wang 2025**, *Boiling After the Dust Settles*, arXiv:2509.07076. **The sharpest currently
  available roll-vs-cascade test found in this review**: for a completed first-order transition at z ≲ 0.3
  releasing a fraction r of the dark energy, the CMB-anisotropy bound from spatial fluctuations in the local
  completion time gives **r ≲ 10⁻⁵ (β/H⋆)²** — e.g. ≲ 1% of the DE budget for β/H⋆ ≲ 25 — versus only ∼65%
  reach from the background (BAO) bound alone. *"This works precisely because a genuine roll... produces no
  patchy/stochastic anisotropy of this kind, while any true cascade... necessarily does."* **This directly
  answers the discriminating question our cosmology proposal left as "a data project outside this repository":
  the test exists, it is a CMB-fluctuation statistic, and it is 4–5 orders of magnitude more constraining than
  the background-level test we had in mind.**
- **Bai, Lu & Orlofsky 2026**, arXiv:2605.30259. A genuine discrete-cascade model (quantum tunnelling + partial
  dark-matter conversion + domain walls) fits DESI DR2 "comparably to or better than CPL" at z_t ∼ 7, with
  O(1–10) bubbles per Hubble patch — few and discrete, testable via finite-bubble CMB-anisotropy statistics.
- **Friedman-Shaw, Johnson & Mack 2026**, arXiv:2607.18376. The single-bubble parameter region that would
  reproduce the DESI Alcock–Paczynski anomaly is **already excluded at 2σ** by combined CMB-dipole + kSZ +
  sound-horizon constraints — a concrete exclusion, not a possibility left open.

### QCD-sector line: status unchanged, sharpened on what's conjectured
- **Van Waerbeke & Zhitnitsky 2025/26**, arXiv:2506.14182 (still arXiv-only). Confirmed: the H³×S¹ computation
  is a genuine derivation; the extension κ → H to de Sitter is explicitly *"a conjecture"* by the authors' own
  words; the model's w(z) shape depends on an activation function β(t) that *"cannot be computed
  analytically... we leave [it]... to future work"* — **not yet a falsifiable alternative to CPL**; its nearer-
  term testable predictions are a ∼10⁻¹⁰ G Gpc-correlated magnetic field and a tabletop Casimir signature, not
  the cosmological w(z).

### Topological-defect DE: bound tightened, one honest nuance added
- **Cheng, Di Valentino & Visinelli 2026**, now published: JHEAp, DOI 10.1016/j.jheap.2026.100610
  (arXiv:2505.22066). Ω_s < 0.00824 (95%, CMB+DESI); Bayesian evidence favours ΛCDM in every combination.
  **Bib DOI corrected to the published record.**
- **An, Han & Zhang 2026**, *Topological defects as effective dynamical dark energy*, Phys. Rev. D, DOI
  10.1103/2m4c-1zl5 (arXiv:2506.10075). Cosmic strings: no preference. **Domain walls (w = −2/3) at Ω_dw ≈ 5%:
  a mild preference (ΔDIC = −0.94) with the DESY5 supernova sample only, disfavoured with Pantheon+/Union3.**
  **Nuance applied**: our proposal said defect DE is "excluded as dominant" — correct — but a *few-percent,
  sub-dominant, dataset-dependent* domain-wall component is not excluded by this analysis; the wording is
  softened accordingly.
- **Kobayashi, Tada, Takahashi & Terada 2026**, arXiv:2605.19841. A genuinely super-horizon anisotropic
  domain-wall model (distinct from a frustrated network) is a **no-go**: *"there are no regions that
  simultaneously satisfy the CMB anisotropy constraint and the condition for accelerated expansion at
  present."*

**(a) Sharpest available test, roll vs. cascade:** the CMB-anisotropy fluctuation statistic of Koren, Tsai &
Wang (arXiv:2509.07076), reaching r ≲ 10⁻⁵(β/H⋆)² versus ∼65% from the background alone — this is now the
concrete answer where our proposal only posed the question.
**(b) Already excluded at the relevant amplitude:** Ω_s ≳ 1% string networks (Bayesian evidence); super-horizon
domain-wall quintessence (no-go); the single-bubble fit to the DESI AP anomaly (2σ, CMB-dipole+kSZ); late
first-order transitions releasing > 1% of DE with β/H⋆ ≲ 25 (CMB-fluctuation bound); a discrete sign-flip inside
z < 2.33 (DESI BAO alone).
**(c) Top 5:** Koren–Tsai–Wang (arXiv:2509.07076); Kaloper JCAP 11 (2025) 075 (DOI
10.1088/1475-7516/2025/11/075); DESI DR2 + Lodha et al. (DOI 10.1103/tr6y-kpc6, 10.1103/w4c6-1r5j); Bai–Lu–
Orlofsky (arXiv:2605.30259); Cheng–Di Valentino–Visinelli + An–Han–Zhang (DOI 10.1016/j.jheap.2026.100610,
10.1103/2m4c-1zl5).

---

## Report 4 — random-wave vortex statistics: our A1/A3 results are 25-year-old theorems

### The screening theory behind A1 (density) and A3 (perimeter law)
- **Berry & Dennis 2000**, *Phase singularities in isotropic random waves*, Proc. R. Soc. A 456, 2059, DOI
  10.1098/rspa.2000.0602. The founding derivation of the vortex density and pair-correlation functions for the
  isotropic random-wave model; secondary sources give the exact density n_vortex = k₀²/(4π) = π/λ² — **the same
  formula, verbatim, as our A1 result (π/λ_dB², measured to 1 %)**. This is the field-independent, 25-years-older
  root of the number Hui et al. quote; we now cite it directly.
- **Freund & Wilkinson 1998**, *Critical-point screening in random wave fields*, J. Opt. Soc. Am. A 15, 2892, DOI
  10.1364/josaa.15.002892. Introduces "critical-point screening": same-sign vortices repel, opposite-sign attract
  at short range, suppressing charge fluctuations below the Poissonian value — the mechanism behind our A3
  sub-area (perimeter) variance growth.
- **Dennis 2003**, *Correlations and screening of topological charges in Gaussian random fields*, J. Phys. A 36,
  6611, DOI 10.1088/0305-4470/36/24/301. The rigorous general derivation of the screening sum rule; **the correct
  primary citation for our A3 theorem**, not just Hui et al.'s numerical confirmation of it.
- **Foltin 2003**, DOI 10.1088/0305-4470/36/6/316, and **Wilkinson 2004**, DOI 10.1088/0305-4470/37/26/012:
  independent derivations with explicit curvature/perimeter correction terms — the "perimeter law" is established
  terminology in singular optics, not a coincidence of our fit.
- **Refinement (important, applied below): the screening is power-law, not exponential.** Houston, Gradhand &
  Dennis (arXiv:1612.01839) show the second moment defining a "screening length" **diverges** for the isotropic
  random-wave model, because the sign-correlation function decays as g_s(R) ∼ cos(2R)/R² — algebraic, not
  Debye-like. **Correction applied**: our A3 write-up must not imply a finite screening length; "power-law
  screening" is the precise term, consistent with — and now explained by — our measured α ≈ 1.00 (a pure
  power law with no crossover scale in the fitted range).
- **Hui, Joyce, Landry & Li**, now published: JCAP 01 (2021) 011, DOI 10.1088/1475-7516/2021/01/011. **Bib DOI
  corrected** from arXiv-only.

### 3D halos: our exact question, already posed by a working 3D code
- **Brax & Valageas 2025**, *3D Vortices and rotating solitons in ultralight dark matter*, arXiv:2502.12100.
  **The single most directly relevant paper found in the whole review.** In 3D GPE simulations of a rotating
  self-interacting ULDM soliton they find, inside the relaxed core, *"a regular lattice of vertical vortex
  lines, aligned with the total angular momentum"* of uniform density n_v = Ω/(πε) — literally the sector — while
  *"in the outer envelope we find a tangle of intertwining and curved vortex lines of any direction"* with random
  ±1 windings when cut by a plane — literally the pairs. They state the open problem in almost our own words:
  *"A difficulty for numerical computations would be to distinguish the extended vortex lines that link distant
  halos... from the chaotic maze of vortices generated by the random interferences between excited modes... in
  the outer virialized halos."* **Independent confirmation, from a working 3D halo code, that no one has yet
  built the discriminating instrument** — reinforcing report 1's gap finding from the lensing side.
- **Rindler-Daller & Shapiro 2012**, MNRAS 422, 135, DOI 10.1111/j.1365-2966.2012.20588.x (already cited).
  **A genuine refinement, not just a visibility statement**: *"vortices cannot form for vanishing
  self-interaction (i.e. when λ_dB ≲ R)."* A halo needs both angular momentum L > Nℏ **and** strong-enough
  self-interaction to cross the vortex-formation threshold at all — in the pure-quantum-pressure (fuzzy) regime
  Hui et al. and our Part A study, interference (pair) vortices appear regardless of rotation, with no threshold,
  while sector vortices require crossing into the Thomas–Fermi/self-interacting regime. **Correction applied**:
  "sector" and "pair" vortices are not just distinguished by the large-R observable; in this literature they can
  be different physical regimes (self-interaction strength) that don't even coexist in the same halo.
- Companions: **Kain & Ling 2010**, Phys. Rev. D 82, 064042, DOI 10.1103/physrevd.82.064042; **Zinner 2011**,
  DOI 10.1155/2011/734543. **Not** "Schobesberger, Rindler-Daller & Shapiro 2021" (this agent could not locate
  it) — but report 1 *did* independently verify that DOI (10.1093/mnras/stab1153, Schobesberger, Rindler-Daller
  & Shapiro, MNRAS 505, 802, 2021); no conflict, just this agent's search missed it. The closest solo match this
  agent found, **Rindler-Daller 2021**, *To Observe, or Not to Observe...*, Frontiers Astron. Space Sci., DOI
  10.3389/fspas.2021.697140, is a genuine additional review, not a substitute.

### Laboratory ring-BEC: TOF readout, and a real exception to "pairs are invisible"
- **Ryu et al. 2007**, Phys. Rev. Lett. 99, 260401, DOI 10.1103/physrevlett.99.260401. First direct persistent-
  current observation via time-of-flight interference with a reference condensate (fork-dislocation pattern) —
  a stronger sector-readout than a plain density hole.
- **Moulder, Beattie, Smith, Tammuz & Hadzibabic 2012**, Phys. Rev. A 86, 013629, DOI
  10.1103/physreva.86.013629; **Kumar et al. 2016**, New J. Phys. 18, 025001, DOI 10.1088/1367-2630/18/2/025001
  (non-destructive Bragg readout, an alternative instrument design).
- **Eckel et al. 2014**, *Hysteresis in a quantized superfluid 'atomtronic' circuit*, Nature, DOI
  10.1038/nature12958. **The primary reference for "TOF density image = winding number readout"**: *"Time of
  flight expansion of the condensate allows us to determine the winding number by measuring the size of the
  central hole that appears in the cloud."* **A genuine, important exception to "pairs are invisible to net
  winding":** *"If a (anti-)vortex were to be nucleated at the (inner) outer edges, move to center, and
  annihilate, the winding number would change by one unit"* — an asymmetric pair, with one member crossing a
  boundary and escaping, is the literal microscopic mechanism by which net winding (the sector) changes in a
  **bounded** ring. **Correction applied**: on our own doubly-periodic torus (no boundary), this leak channel
  does not exist by construction — a pair cannot "escape" a periodic box the way it escapes a ring's inner/outer
  edge — so round 4's "pairs are invisible at large R" claim is unaffected *on the torus*, but the caveat is now
  recorded for any future non-periodic (halo) extension, where a boundary-crossing pair genuinely can leak into
  the sector.
- **Corman et al. 2014**, *Quench-Induced Supercurrents in an Annular Bose Gas*, Phys. Rev. Lett. 113, 135302,
  DOI 10.1103/physrevlett.113.135302. A Kibble–Zurek quench spontaneously leaves a **random, mean-zero but
  nonzero-variance** net winding from a random-phase configuration with no imposed rotation — an independent
  experimental confirmation, in a different system, of exactly our A3 statement (Var[W(R)] > 0, ⟨W(R)⟩ = 0).
- **Gauthier et al. 2019**, *Giant vortex clusters in a two-dimensional quantum fluid*, Science 364, 1264, DOI
  10.1126/science.aat5718 (already in our bibliography via the causal-topology stream). Gives a ready-made
  alternative sector-detector: the Onsager-cluster dipole moment D = N⁻¹|Σⱼ sgn(Γⱼ) xⱼ|, ≈ 0 in the disordered
  (paired) phase, growing as D ∝ (E − E_c)^{1/2} above the clustering transition. **Actionable, not yet done**:
  compute this statistic on our own vortex configurations (round 2/3/4 samples already record positions and
  charges) as a second, independent cross-check of "only pairs, no sector" alongside Var[W(R)].
- **Johnstone et al. 2019**, Science 364, 1267, DOI 10.1126/science.aat5793 (already cited); a related 2025/26
  follow-up (Yang & Tsubota, arXiv:2502.06133) shows the 2D inverse-cascade/clustering phenomenology is
  suppressed in 3D (Kelvin-wave-mediated forward cascade dominates) — relevant if the round-4 protocol is ever
  extended from 2D to 3D: the "only pairs survive at large R" story is not guaranteed to carry over unchanged.
- **Groszek, Davis, Paganin, Helmerson & Simula 2018**, *Vortex Thermometry for Turbulent Two-Dimensional
  Fluids*, Phys. Rev. Lett. 120, 034504, DOI 10.1103/physrevlett.120.034504 — already the method behind this
  repository's own `vortex_thermometer_cal*.json` (rounds 2–3); confirmed as the standard reference, already in
  our trail.

**Top 5 (this report):** Brax & Valageas 2025 (arXiv:2502.12100, poses our exact 3D question with a working
code); Berry & Dennis 2000 + Dennis 2003 (DOI 10.1098/rspa.2000.0602, 10.1088/0305-4470/36/24/301, the actual
theorems behind our A1/A3); Eckel et al. 2014 (DOI 10.1038/nature12958, TOF readout + the boundary-leak
refinement); Rindler-Daller & Shapiro 2012 (DOI 10.1111/j.1365-2966.2012.20588.x, the self-interaction threshold
that separates sector-capable from sector-incapable regimes); Gauthier et al. 2019 (DOI 10.1126/science.aat5718,
an importable second order parameter).

**Where the literature qualifies our reading:** (1) "pairs are invisible to net-winding observables" needs the
boundary-leak exception (Eckel et al.) — true on our periodic torus, not automatically true on a bounded ring or
a non-periodic halo; (2) "screening" should be called power-law/algebraic, not given a finite length scale
(Houston–Gradhand–Dennis); (3) a sector vortex is not automatic even with nonzero angular momentum — it
additionally requires strong-enough self-interaction (Rindler-Daller & Shapiro's λ_dB ≲ R threshold), a second,
independent condition beside the large-R visibility argument.

---

## Corrections applied to the repository (this session)

1. `docs/designs/COSMOLOGY_SECTORS_PROPOSAL.md` — added the "dispersion-supported, no vortices needed in the
   core" argument, properly cited (Rindler-Daller & Shapiro 2012 + Hui 2021 review + Schobesberger, Rindler-
   Daller & Shapiro 2021, DOI 10.1093/mnras/stab1153), with the quoted quantitative statement; not a correction
   of prior text, this argument was not previously in the file. Added: Zhou et al. 2025's and Brax & Valageas
   2025's own explicit statements of our exact open question (no published simulation runs the Ω=0 control);
   the Berry–Dennis/Dennis grounding of the π/λ² density and perimeter-law screening (power-law, not
   exponential); the Eckel et al. boundary-leak caveat to "pairs are invisible."
2. `paper/refs_cosmology_sectors.bib` — Kaloper2025 DOI updated to the published JCAP record
   (10.1088/1475-7516/2025/11/075); ChengDiValentinoVisinelli2025 DOI updated to the published JHEAp record
   (10.1016/j.jheap.2026.100610); added AnHanZhang2026, Hui2021Review, SchobesbergerRindlerDallerShapiro2021,
   ZhouLeungPoonChu2025 already present, KorenTsaiWang2025.
3. `paper/cosmology_sectors.tex` — dark-energy section: replaced the placeholder "a data project outside this
   repository" with the concrete Koren–Tsai–Wang discriminator and its number; softened "excluded as dominant"
   to note the dataset-dependent, sub-dominant domain-wall allowance (An–Han–Zhang); added a footnote on the
   K3×T² vs. T⁶/CHL boundary (Dabholkar–Gaiotto–Nampuri; Sen) so the "entropy is a function of D" slogan is not
   read as general.
4. `lean_src/ChargeLattice.lean` — doc comment: added the same K3×T² vs. T⁶/CHL boundary note (no theorem
   changed; the Lean statements are about a generic bilinear form and remain correct as stated).
5. `paper/duality_sector.tex` — addendum section citing Aasen–Mong–Fendley, Choi–Córdova–Hsin–Lam–Shao,
   Kaidi–Ohmori–Zheng, Shao's TASI lectures and Hayashi–Tanizaki's Cardy–Rabinovici analysis: these sharpen
   (not contradict) the published criterion with an explicit anomaly-matching mechanism for when a self-dual
   point is forced to be a transition. Recompiled; will ship in v1.13.0.
6. `docs/designs/PGPE_R4_PREREG.md` / `PGPE_R4_RESULTS.md` — A1/A3 now cite Berry & Dennis 2000 and Dennis 2003
   directly as the primary theorems (not only Hui et al.'s numerical confirmation); the screening is recorded as
   power-law/algebraic (Houston–Gradhand–Dennis), not given a finite "screening length"; a note that on our
   periodic torus the Eckel et al. boundary-leak exception to "pairs are invisible" does not apply, with the
   caveat recorded for any future non-periodic extension.
7. `paper/refs_cosmology_sectors.bib` — `HuiJoyceLandryLi2020` DOI updated to the published JCAP record
   (10.1088/1475-7516/2021/01/011); added Berry & Dennis 2000, Dennis 2003, Brax & Valageas 2025, Eckel et al.
   2014; the Rindler-Daller & Shapiro self-interaction threshold added as a distinct, second condition (beside
   the large-R visibility argument) for when a sector vortex can exist at all.

None of the four reports contradicted a theorem; all corrections are to prose/citations/bibliography.
