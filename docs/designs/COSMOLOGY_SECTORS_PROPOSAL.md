# The sector is the cause — what that reading says about dark matter, dark energy and K3, and what it does not

Stream opened 2026-09-25, after v1.12.0 (DOI 10.5281/zenodo.22967670). Follows `CAUSAL_TOPOLOGY_DEEP_NOTES.md`
§14, `paper/duality_sector.tex` and the astrophysics transfer rule of `paper/astro_topological_measurement.tex`.
Lean: `ChargeLattice.lean` (this stream), `CompactBoson.lean`, `TopologicalProtection.lean`,
`ScaleResolvedWinding.lean`, `ContinuumWinding.lean`. Every DOI below was resolved through Crossref or read on
arXiv before being cited.

## 0. The rule this stream works under

What transfers from the quantum-fluid laboratory (memory `causal-topology-transfer-to-astrophysics`): the chain
*integrality → conservation by continuity → barrier → scale additivity (W(R) = net charge) → continuum limit*,
valid for any U(1) phase field, and the **method** — a causal claim about a topological label needs a matched
control arm that is equally arbitrary, and the label must be read at a stated scale. What does not transfer:
link 4, the coupling between the integer and the observables (η, n_s, T_v/T_b), which is empirical and specific
to the fluid. So this document may say *where* a sector is, *what* must be conserved, *at what scale* it is
visible, and *what would count as an intervention*; it may not carry a number from the torus to the sky. No
α′ = ℓ_P c/H₀; no superfluid–K3 identification (excluded in v1.9–v1.12).

The reading being applied: a duality is a reindexing of a sector lattice that preserves a spectrum (Savit 1980;
`CompactBoson.partition_dual`); the physics happens when a sector crosses a threshold, proliferates, annihilates,
is imposed, or is selected. The question for each cosmological problem is therefore: **what is the sector group,
what is the function of the sector the observable depends on, what is the event on the lattice, and what is the
duality doing (relabelling) as opposed to causing?**

## 1. Dark matter as a U(1) phase field: vortices in wave dark matter

**The sector.** Ultralight bosonic dark matter (m ≲ 30 eV in a Milky-Way halo is wave-like; fuzzy DM at
10⁻²²–10⁻¹⁹ eV; Hu–Barkana–Gruzinov 2000, DOI 10.1103/PhysRevLett.85.1158; Hui–Ostriker–Tremaine–Witten 2017,
DOI 10.1103/PhysRevD.95.043541) is a complex field ψ = √ρ e^{iS}; the U(1) is particle number, the winding of S
around a loop is an integer, the circulation is quantised in units of 2π/m. This is our `VortexWinding` /
`QuantizedCirculation` setting with a different m and no confining box.

**What the literature establishes (read, not extended).**
* Hui, Joyce, Landry, Li 2020 (arXiv:2004.01188): in a virialised halo the interference of waves *inevitably*
  produces vortices — vortex **rings** in 3D, about **one ring per de Broglie volume**, **winding ±1 only**
  (higher windings are non-generic), density ρ ∝ r⊥² and velocity ∝ 1/r⊥ near the line, ring speed ∝ 1/(m ℓ);
  rings **reconnect rather than frustrate**; they appear even in a halo with **zero net angular momentum**.
  Lensing flux anomalies of 5–10 % from interference substructure in strong lenses.
* Zhou, Leung, Poon, Chu 2025 (arXiv:2512.03357): in a *rotating* BEC-ULDM halo (m = 2.9×10⁻²² eV, repulsive
  g, core 6×10¹⁰ M☉, v₀ = 40–120 km/s at 2 kpc) a **vortex lattice** forms; vortices are under-density columns;
  lensing brightness anomalies of the lensed arcs, regularly spaced, if the rotation axis is along the line of
  sight and the PSF is ≲ 10 mas (VLBI); indistinguishable at 70 mas (HST).
* Berezhiani–Khoury 2015 (DOI 10.1103/PhysRevD.92.103510): superfluid DM with m ∼ eV; ω ≫ ω_cr so vortex
  formation is unavoidable; N_v ∼ 10²³ per halo, core ∼ mm, energy-density contrast ∼ 10⁻³³ λ ρ — vortices
  individually invisible.

**What the sector reading adds — three statements and one prediction, no numbers.**

1. *Scale-resolved reading.* By `ScaleResolvedWinding` (W(R) = net enclosed charge), a vortex ring is a
   dipole at every scale larger than the ring: its winding through a plane is +1 and −1 at two points, net
   zero. Hui et al.'s rings — size distribution exponential in ℓ/λ_dB — are therefore **invisible to any sector
   observable read at R ≫ λ_dB**; they are pair physics, not sector physics. What they *can* do is exactly what
   our round-2 pairs did: carry energy, scatter, heat (the "dynamical heating of stars by interference
   granules" of the ULDM literature is the astrophysical avatar of "topology cools the bath / the bath heats
   when pairs annihilate", Part D).
2. *The only sector-level observable of a halo is its net circulation.* Σ over all vortex lines threading a
   large loop = W(R→halo) = the quantised circulation = angular momentum in units of ħ per particle. Zhou et
   al.'s lattice is the halo's *sector* (W = number of vortices of one sign in the lattice, set by Ω); Hui et
   al.'s rings are its *thermal pairs*. The two are distinguished by one measurement, the net winding at large
   R — the same distinction as our s12 persistent current (W = −3, intact at t = 1500) versus the s11 coarsening
   arm (W = 0). A lensing survey that sees regularly spaced under-densities (lattice) is seeing the sector; one
   that sees random 5–10 % anomalies is seeing the pairs.
3. *Conservation and the barrier.* A non-zero halo winding can change only by a vortex line crossing the
   boundary or by nucleation at a density zero (`TopologicalProtection.winding_conserved`,
   `slip_of_winding_change`). In a halo there is no wall: the "boundary" is where ρ → 0 at the halo edge, and
   lines leave freely. So halo circulation is *not* protected the way a ring current is — the sector is real
   but its barrier is low. This is a statement about the mechanism, checkable in a GPP simulation with an
   imposed W and a matched non-rotating arm at equal energy (the design of round 2, transplanted).

**Prediction (falsifiable, no fitted number).** In a rotating ULDM halo simulation, the *lattice* vortices'
lensing signature scales with W (the imposed sector) at fixed total energy, while the *ring* vortices'
signature does not change when W is set to zero at the same energy. If a "vortex lensing anomaly" survives
setting W = 0, it is interference substructure (Hui et al.), not a sector effect, and the claim "BEC dark
matter detected through its vortices" would be a claim about pairs. This is the round-2 protocol
(V arm vs P arm) written for a halo. The instrument is `W(R)` from the phase, as in `ScaleResolvedWinding`.

**What is not claimed.** No mass, no Ω_DM, no lensing amplitude. Whether DM is a U(1) field at all is the
hypothesis of the cited papers.

## 2. Dark energy as a sector lattice: three models, one algebra, and the honest limit

**Bousso–Polchinski 2000 (DOI 10.1088/1126-6708/2000/06/006).** With J four-form fluxes of charges q_i and
integer quanta n_i, Λ(n) = Λ_bare + ½ Σ n_i² q_i². The observable is a **function on ℤ^J**; membrane
nucleation moves one step (n_i ↦ n_i − 1) and lowers Λ by (n_i − ½) q_i²; with J ∼ 100 (or 4 with large
extra dimensions) the discretuum near Λ = 0 is dense enough (10⁻¹²⁰ M_P⁴ spacing). What selects the observed
value is **anthropic** in the weakest sense ("galaxies only in regions of small Λ"). Lean: `bp_step`,
`bp_step_neg_iff` (monotone inward while n_i ≥ 1), `bp_ge_bare`, `bp_min_at_zero`.

**Kaloper 2025, "Discretely evanescent dark energy" (arXiv:2506.04317).** A hidden SU(N) at Λ_dark ∼ 10⁻³ eV;
after dark chiral symmetry breaking the top-form flux is quantised, F = N Q, θ_dark = (1 − N) θ̂,
V = ½ X_dark θ_dark²; membranes of tension ∼ 1.2 Λ_dark³ nucleate at Γ ∼ H₀⁴ (mm-size bubbles), lowering V in
**discrete random steps** down to exactly zero at the CP-invariant sector N = 1; w ≠ −1 transiently; the
acceleration may cease within ∼ 1/H₀; bubble collisions give Ω_GW < 10⁻⁹ at f ≲ 10⁻¹² Hz. Lean: `kaloper_step`,
`kaloper_min` (V = 0 iff N = 1), `kaloper_terminates` (from N ≤ 1, exactly 1 − N nucleations). **This is the
phase-slip cascade of our e = 0.60 arm** (winding 2 → 0 by slips, the current's energy going to the bath)
written for the vacuum: each nucleation is a slip of the top-form sector, and the model's content is the
*rate*, not the algebra.

**Van Waerbeke–Zhitnitsky 2025/26 (arXiv:2506.14182).** DE from the QCD θ-sectors |k⟩ via the Zeldovich
subtraction ρ_FRW − ρ_Mink ≈ c_H Λ_QCD³ H, giving ρ_DE ∼ (3.4×10⁻³ eV)⁴ and t₀ ∼ 7 Gyr/c̄_H from Λ_QCD alone;
w(z) may cross −1 (DESI-like). Here the sector *structure* (tunnelling between k-sectors, non-local holonomy)
is claimed to be the cause and no new field is introduced. The statement "the leftover is linear in H" is the
model's hypothesis (proved on H³×S¹, conjectured for de Sitter).

**Topological-defect dark energy (Bucher–Spergel 1999, DOI 10.1103/PhysRevD.60.043505; Vilenkin 1984, DOI
10.1103/PhysRevLett.53.1016).** Frustrated non-Abelian string networks give w = −1/3, domain-wall networks
w = −2/3, stabilised against short-wavelength collapse by a shear modulus (a *solid*). Here the sector is
literal (π₁(G/H) non-commuting elements prevent intercommutation). **Status: excluded as the dominant DE.**
Cheng–Di Valentino–Visinelli 2025 (arXiv:2505.22066): Ω_s < 0.0066–0.009 (95 %) from CMB+DESI(+SN) for
positive-energy string networks; the negative-Ω_s fits (Δχ² = −6.8 CMB-only) do not overcome the Occam
penalty; Bayesian evidence favours ΛCDM in all four models.

**The reading, and its limit.** In all four models the vacuum energy is a **function of an integer sector**
(n ∈ ℤ^J; N ∈ ℤ; k ∈ ℤ; the defect class in π₁); the dynamics is a **walk on the lattice by slips**
(membrane nucleation = phase slip); the end point is a **distinguished sector** (Λ ≈ 0 shell; N = 1; the
frustrated configuration). This is structurally identical to `TopologicalProtection` + `SectorTemperature`:
the sector is conserved between slips, a slip costs a barrier (the bounce action B = 27π²T⁴/(2ΔV³)), and the
energy released goes elsewhere (reheating; the bath). The *causal* content is the same as in the fluid: the
integer is the difference-maker, the duality (where one exists — the electric/magnetic top-form dual, the
θ ↔ F degeneracy Kaloper notes explicitly) relabels it.

The limit: **none of this decides which lattice, if any, the universe sits on.** The algebra is shared; the
data (DESI DR2, Planck, Pantheon+) constrain w(z), not the lattice. What the sector reading contributes is a
*discriminating question*: is the observed w(z) ≠ −1 (if it survives) a **continuous** roll (quintessence: no
sector) or a **discrete** cascade (Kaloper: sector, with mm bubbles percolating, Ω_GW < 10⁻⁹ at 10⁻¹² Hz, and
a w(z) that is piecewise −1 with steps)? The former has no integer; the latter has one, and the integer's
signature is the *step*, exactly as the ring current's signature was the integer W in the momentum
distribution (29.5 % of atoms at k = (−3, 0)). A pre-registered test would be: fit DESI+SN w(z) with a
step-function family against a CPL family at equal parameter count — but this is a cosmology-data project
outside this repository's competence and is recorded as a direction, not started.

## 3. K3 as a charge lattice: the attractor mechanism is the sector reading, exactly

This is the place where the thesis is not an analogy but a theorem of the string literature.

**Moore 1998, "Arithmetic and attractors" (arXiv:hep-th/9807087).** For type II on K3 × T², a dyon is a
charge vector γ = (p, q) ∈ Λ = II_{22,6} ⊕ II_{22,6} (with p, q taken in H²(K3, ℤ) = II_{3,19} after
U-duality). The attractor equations fix the moduli at the horizon **from the charges alone**: the K3
complex structure is Ω ∝ q − τ̄ p with τ = (p·q + √D)/p², so the attractor K3 has NS(S) = ⟨p, q⟩^⊥, Picard
rank 20 — an *attractive* (singular) K3 whose transcendental lattice is the rank-2 lattice ⟨p, q⟩ with Gram
matrix 2Q_{p,q}; by Shioda–Inose it is the Kummer-type surface built from two CM elliptic curves. The
horizon area and the BPS asymptotics depend only on the **discriminant**

    D(p, q) = (p·q)² − p² q²,   A/4π = √(−D),   log dim H_BPS = π √(−D) + ⋯  (Strominger–Vafa; DVV 1997,
    DOI 10.1016/S0550-3213(96)00640-2).

The U-duality group SL(2, ℤ) × O(6, 22; ℤ) acts on charges; **D is invariant**; but the number of
U-inequivalent charges with the same D is the **class number h(D)** (eq. 3.17–3.18), growing like |D|^{1/2−ε}:
*many sectors, same entropy, permuted by nothing in string theory* — Moore notes the Galois group permutes
them but "is not a symmetry of string theory".

**Lean (`ChargeLattice.lean`, Part 1).** With Λ any additive group carrying a symmetric ℤ-bilinear form,
`disc_sl2`: D(ap + bq, cp + dq) = (ad − bc)² D(p, q); `disc_sl2_invariant` for det 1;
`disc_electric_magnetic_swap` for S: (p, q) ↦ (q, −p); `disc_scale`: D(tp, tq) = t⁴ D; `disc_zero_of_parallel`:
D(p, kp) = 0; `area_sl2_invariant` over ℝ. Elementary — bilinearity and `ring` — and that is the point: the
part of "K3 mirror/duality" that carries physics is a polynomial identity on the charge lattice.

**What this says for the programme.**
* The K3 that appears is an **output of the sector** (attractor), not an input geometry that a fluid could
  share. The claim excluded in v1.9–v1.11 (superfluid ↔ K3 × T²) was an attempt to transfer the *input*;
  Moore's theorem shows the geometry is *determined by the charges*, so nothing about a fluid's spectrum
  could fix it — there are no charges (p, q) in a superfluid, only W ∈ ℤ.
* The Fricke/Dolgachev–Nikulin mirror involution on Γ₀(N)+N (Dolgachev 1996, alg-geom/9502005) is a map
  between *families* of lattice-polarised K3s — a reindexing of the lattice M ↔ M^⊥ inside II_{3,19} — of the
  same kind as `partition_dual`: it preserves the structure and moves no dyon's entropy. Consistent with
  `QHFricke`: the Fricke element fixes an orbit and is not a symmetry of the sectors.
* The **cross-domain criterion** of §14 / `duality_sector.tex` gets a fourth clean case: K3 × T² black holes
  are the case where the duality group is large, the invariant is a single integer function D, and the
  physics (entropy) reads the invariant — "organisation, not cause", as for the Hall plateaux, with the added
  twist that the *level set* of the invariant is strictly larger than the orbit (class number > 1).

**What is not claimed.** Nothing about real black holes, nothing about K3 beyond H²(K3, ℤ) as a lattice with
a form; the attractive-K3 statement is Moore's, cited; our theorems are about D on an abstract form.

## 4. What this stream will and will not do next

Will (in this repository, with its instruments):
1. `ChargeLattice.lean` through Comparator (two kernels), three negative controls, LEDGER claim.
2. A GPP-free, torus-PGPE **halo-shaped test of §1's prediction**: not a halo (we have no gravity solver) but
   the same protocol in our box — impose W = 3 (s12-type) vs W = 0 at equal energy with equal numbers of
   thermal pairs, and measure a "lensing proxy" = the projected column-density power spectrum at k ∼ 1/λ:
   does the lattice/current change it at fixed energy while the pairs do not? Pre-registered as round 4
   Part B if the owner wants it; it would test the *method*, not dark matter.
3. The cosmology paper `paper/cosmology_sectors.tex`: the reading, the three theorems, the discriminating
   questions, the excluded routes — with the transfer rule printed as a box on page 1.

Will not:
* Fit cosmological data; claim Ω_DM, Ω_Λ, w(z), a boson mass, a string tension.
* Run GPP halo simulations (no code, no known answers here; Zhou et al. and Hui et al. have them).
* Re-open α′ = ℓ_P c/H₀ or a fluid ↔ K3 identification.

## 5. References resolved this session

Bousso–Polchinski JHEP 06 (2000) 006 · Bucher–Spergel PRD 60, 043505 (1999) · Vilenkin PRL 53, 1016 (1984) ·
Kibble J. Phys. A 9, 1387 (1976) · Hu–Barkana–Gruzinov PRL 85, 1158 (2000) · Hui–Ostriker–Tremaine–Witten PRD
95, 043541 (2017) · Berezhiani–Khoury PRD 92, 103510 (2015) · Dijkgraaf–Verlinde–Verlinde NPB 484, 543 (1997) ·
Ferrara–Kallosh–Strominger PRD 52, R5412 (1995) · Eguchi–Ooguri–Tachikawa Exp. Math. 20, 91 (2011) · Moore
hep-th/9807087 · Hui–Joyce–Landry–Li 2004.01188 · Zhou–Leung–Poon–Chu 2512.03357 · Kaloper 2506.04317 · Van
Waerbeke–Zhitnitsky 2506.14182 · Cheng–Di Valentino–Visinelli 2505.22066 · Dolgachev alg-geom/9502005.
