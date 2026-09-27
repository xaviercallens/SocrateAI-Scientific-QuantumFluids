# Deep notes, 2026-09-25: after round 2 — thought experiments F–I, the literature that already contains them, and the round-3 design

Companion to `CAUSAL_TOPOLOGY.md` and `PGPE_R2_RESULTS.md`. Everything here is either a reading of the literature
(DOIs Crossref-verified) or a design; **nothing here is a result**.

## 1. The anomaly that drives this

Round 2's I2 failed on every base: at the same E, N, P the vortex arm is *colder* by 5–16 %, more than the energy
surplus, and colder than the untouched base by 4 %. The pre-data amendment had not anticipated it.

## 2. Thought experiment F — topological sectors carry their own temperature

Microcanonical entropy is sector-dependent, S(E, N, P, W). Then 1/T = ∂S/∂E *at fixed W* differs between sectors,
and two boxes at the same E have no reason to share a temperature. I2's clause was wrong **in principle**. More
precisely the field is a two-temperature system: the phonon bath (what the equipartition thermometer reads) and the
vortex gas, whose own temperature Onsager defined on the vortex positions, T_v = (∂S_v/∂E_v)⁻¹, and which can be
negative. Topological protection is the weak coupling that lets the two temperatures differ for a long time.

**Literature status: established.** Onsager (Nuovo Cimento 6, 279, 1949); Kraichnan–Montgomery (Rep. Prog. Phys.
43, 547, 1980). Experiments: Gauthier et al., Science 364, 1264 (2019), 10.1126/science.aat5718 — "the vortices must
form a well-isolated subsystem and effectively decouple from the other fluid degrees of freedom", T = (∂S/∂E)⁻¹ from
the point-vortex density of states, thermal friction as the coupling, decay time vs condensate fraction; Johnstone et
al., Science 364, 1267 (2019), 10.1126/science.aat5793. Instrument: **Groszek, Davis, Paganin, Helmerson, Simula, PRL
120, 034504 (2018), "Vortex thermometry"** — cluster and dipole fractions are monotonic in β and calibrated by Monte
Carlo; β_BKT = 2/E∘, β_EBC = −4/(N E∘), E∘ = ρ_s κ²/4π; they cite **Purcell–Pound (1951) and Ramsey (1956)**, i.e.
the spin-temperature analogy is the field's own framing. Mechanism of the energy flow: Kanai–Guo (arXiv:2105.01253)
show pair annihilation emits intense sound (vortex energy → bath); our injection is the reverse arrow (bath → vortex
configuration: more pairs nucleated, condensate scrambled into low-k structure). They also show that in an ideal
periodic 2D box an isolated pair cannot annihilate without a third vortex (Baggaley–Barenghi 2018, N ∝ t^{−1/3}) —
which is why our eight imprinted vortices at e = 0.60 survived 1500 time units untouched.

**What F changes in the paper's reading of I2:** the thermometer was not blind and not biased; it read one of two
temperatures. The composite claim's clause "and measured T" should have been "and measured *bath* T", and even then
it would be expected to fail, in the direction observed.

## 3. Thought experiment G — the Thouless pump is the existing intervention paradigm

Threading an adiabatic cycle that winds once in parameter space pumps exactly one particle per cycle; a cycle with the
same energy input that does not wind pumps none. Realised with cold atoms: Lohse et al., Nat. Phys. 12, 350 (2016),
10.1038/nphys3584; Nakajima et al., Nat. Phys. 12, 296 (2016), 10.1038/nphys3622. This is a matched pair of the
kind Part I built, done in a laboratory a decade ago, with a Chern number as the intervened variable.

## 4. Thought experiment H — the canonical two boxes

Deliver the same ΔE to both arms and couple both to a reservoir (SPGPE). Then bath T is equal by construction and the
question becomes: how long does the topological label survive contact with the reservoir, and does the condensate
differ at equal T while it survives? This separates the two effects that Part I mixed (sector temperature and
difference-making). It is the natural next intervention design.

## 5. Thought experiment I — the entropy accounting

Hamiltonian evolution keeps the fine-grained entropy constant; the vortex arm starts as a low-entropy macrostate
(a specified phase pattern) and is out of equilibrium. Its bath cooled while its condensate collapsed: energy moved
from thermal high-k modes into the vortex configuration (more pairs, dipole expansion) and into a broad low-k
quasi-condensate. There is no topological refrigerator: annihilation returns the energy as sound (Kanai–Guo). What
the accounting says is that W(R) at large R is a slow variable that holds energy out of the bath — a battery, not a
Maxwell demon.

## 6. The +12–27 % duality offset and F1/F2 are known finite-size physics

* Gawryluk–Brewczyk (arXiv:1809.10967, classical fields, finite N): η exceeds m²k_BT/2πℏ²ρ_s near the transition
  because ρ_s is overestimated at finite N; an "intermediate region" with algebraic g₁ and η > 1/4; the transition
  temperature moves up and the curves flatten as N decreases. Our ladder points at e = 1.25–1.40 (algebraic, η =
  0.30–0.66), our F1 and F2, and the sign of our offset are all in that paper.
* Hasenbusch (cond-mat/0502556, XY, L up to 2048): Υ(L) = 0.63650818 + 0.31889945/(ln L + C) at T_KT. At our L =
  64 and 32 (in units of ξ) this is a +10–11 % stiffness excess, the right sign and roughly the right size.
  **Prediction for round 3:** the offset of η·n_sλ² falls as 1/ln L; L = 128 should give ≈ +8 %.

## 7. Ross (Synthese 2020) and where our case sits

Ross's criteria: an explanation is *topological* if its explanans is topological; *causal* if its dependency relation
is empirical rather than mathematical. Her causal-topological cases (bow ties, chokepoint enzymes, food webs) have
system-level explananda and explanantia — patterns of causal *connections*, not single variables. Our case satisfies
both criteria (the explanans is W; the W → condensate dependency was established by intervention) and differs from
hers in that the topological explanans **is a single variable**, a conserved invariant that enters Woodward's frame
directly. That is a new species in her taxonomy, and the stability theorems are what make the variable
interventionable. This is worth one section in a follow-up paper; it is not in the published one.

## 8. The instrument: torus point-vortex energy (`exploration/pgpe/vortex_thermometer.py`)

Weiss & McWilliams, Phys. Fluids A 3, 835 (1991), eq. (12): h(x, y) = Σ_m ln[(cosh(x − 2πm) − cos y)/cosh 2πm] −
x²/2π on the 2π box, H = −Σ_{i<j} κ_iκ_j h, zero total circulation and zero vortex momentum.
Known answers run 2026-09-25: dipole energy slope ΔE = 2 ln 2 per doubling (1.384, 1.377 vs 1.386 — 2D Coulomb);
W&M N = 6, P = 0 density of states: rms 2.985 vs their 2.90 (3 %), mean 1.077 vs their −0.28 — an additive
convention; T = (dS/dE)⁻¹ does not see it. The rms is the shape check; it passes.

## 9. Round-3 design sketch (to be pre-registered before any run)

* **Two thermometers on the V arm**: bath T (equipartition, as before) and T_v (torus density of states for the
  detected N, P ≈ 0; and Groszek's dipole/cluster fractions as a cross-check). Predictions: T_v ≠ T_bath in the first
  blocks; |T_v − T_bath| decreases monotonically; the bath cooling of Part I is matched by the vortex energy gain.
  Needs vortex positions saved per block (round 2 saved only counts and Q).
* **Canonical two boxes** (H): SPGPE with a reservoir at the base T; measure the label's lifetime and the condensate
  gap at equal T.
* **L = 128** (256² grid, ≈ 4× the cost per run): the 1/ln L test of §6, three energies around the jump.
* **Kill rules**: if the torus thermometer fails a fresh known answer (a thermal MC ensemble at set β must read β
  back within 10 %), no T_v is quoted.

## 10. Literature map (all verified)

Onsager 1949 · Kraichnan–Montgomery 1980 · Weiss–McWilliams 1991 (10.1063/1.858014) · Simula–Davis–Helmerson PRL 113,
165302 (2014) · Groszek et al. PRL 120, 034504 (2018) · Gauthier et al. Science 364, 1264 (2019) · Johnstone et al.
Science 364, 1267 (2019) · Kanai–Guo arXiv:2105.01253 · Gawryluk–Brewczyk arXiv:1809.10967 · Hasenbusch
cond-mat/0502556 · Lohse et al. Nat. Phys. 2016 · Nakajima et al. Nat. Phys. 2016 · Ross, Synthese 2020
(10.1007/s11229-020-02685-1) · Huneman 2010 · Kostić 2018 · Woodward 2003.

## 11. First exploratory reading on round-2 final states (2026-09-25, post hoc, NOT a result)

Torus point-vortex energy of the detected configurations at t = 1500, placed against the density of states of random
neutral P = 0 configurations with the same N (20 000 samples). Units: E_phys = π E_WM here (ρ = 1, κ = 2π), so
T_v,phys = π T_v,WM.

| arm (t = 1500) | N_v | E_WM | (E − ⟨E⟩_rand)/σ | reading |
|---|---|---|---|---|
| e0.60 V (8 imprinted, untouched) | 8 | +0.36 | **−0.27** | at the maximum-entropy energy: β_v ≈ 0, "infinite" vortex temperature, while the bath sits at T = 0.09–0.11 |
| e0.90 0 (s11, s12) | 4, 4 | −10.5, −12.8 | −4.5, −5.5 | tightly bound thermal pairs, low positive T_v |
| e0.90 P (s11) | 6 | −17.2 | −6.1 | same |
| e0.90 V (s11, s12) | 12, 10 | −20.8, −12.6 | −3.6, −2.8 | intermediate: imprinted pairs plus thermal ones |

**What can and cannot be said.** The *placement* in the density of states is robust and is the two-temperature
picture in its rawest form: the untouched imprinted configuration is a β_v ≈ 0 vortex gas coexisting for 1500 time
units with a β_bath ≈ 10 phonon bath. The *numerical* T_v from the slope of ln ρ is **not** quotable: at 3–6 σ below
the mean the random-sampling histogram is empty or noisy (the routine returned nan or unstable values there). A
canonical Monte Carlo calibration at set β (Groszek's method, on the torus) is required before any T_v is quoted —
this is the kill rule of §9, and it fired on the first try, as it should.

## 12. Energy budget of the intervention (2026-09-25, post hoc, `exploration/pgpe/energy_budget_r2.py`)

Where did the energy the high-k bath lost in arm V go? Field decomposition (kinetic energy per k-band; Nore–Abid–Brachet
incompressible / compressible / quantum-pressure split; interaction energy), final states t = 1500:

| base | ref | bath (k ≥ 0.4 k_cut) | low-k kinetic (k < 0.4 k_cut) | interaction | incompressible | compressible |
|---|---|---|---|---|---|---|
| e0.60 | P | **−50** | **+61** | −10 | **+63** | −41 |
| e0.90 s11 | 0 | −8 (P: +62) | +42 | +21 | **+39** | −16 (P: +36) |
| e0.90 s12 | 0 | −9 (P: +31) | +53 | −4 | **+41** | +13 (P: +34) |

Reading: the bath's loss (and the injected surplus) sits in **low-k incompressible flow energy** — the imprinted pairs
plus the pairs they nucleated — and, at e = 0.90, in interaction energy (more depleted cores); not in sound. Arm P put
its surplus into compressible energy (sound) and high-k modes, as expected. At e = 0.60 the bath loss (−50) and the
incompressible gain (+63) agree within 26 %: kill rule K3 as intended would PASS there; at e = 0.90 the block-resolved
run is needed because the surplus dominates the difference to arm 0.

**Correction of §11's point-vortex budget.** The Weiss–McWilliams Hamiltonian carries an additive constant per pair
(the −Σ ln cosh 2πm normalisation), so energy differences between configurations with different N are not
meaningful; the earlier "E_v(final) − E_v(imprint) = −26" compared N = 14 and N = 12 and is void. Placement in the
density of states at fixed N (§11) stands; cross-N budgets must use the field functional. The proposal paper's K3 is
reworded accordingly.

**Literature that frames this.** Mehdi, Hope, Szigeti, Bradley (arXiv:2205.04065): energy damping (number-conserving
scattering) is the dominant vortex–bath coupling, two orders above number damping; the noise term is dissipative and
fluctuation–dissipation does not hold for the vortex equation because the bath's equilibrium contains no vortices —
the two-temperature state is intrinsically transient, T_v relaxes towards "no vortices". Groszek & Billam
(arXiv:2601.02687, 2026): conservative PGPE coarsening of a uniform 2D gas after a quench — exactly the V-arm
relaxation problem — with L_c ~ t^{1/z}, z ≈ 1.5 near BKT to 1.9 at low T, thermal dipoles forming a late-time plateau
in N_v (our round-1 A3/A4 lesson), data CC-BY. Prediction for a larger round-3 box: the V arm's free-vortex density
decays as t^{−2/z} with z in that range.

## 13. Dense calibration (2026-09-25, `vortex_thermometer_cal_dense.py`, 6000 sweeps, β grid 0.8–1.6)

Closure at β₀ = 1.2, three repetitions: N = 6 → 1.222, 1.200, 1.175 (mean 1.199); N = 8 → 1.241, 1.260, 1.305 (mean 1.269). The fast run's N = 6, 8 failures were precision; the instrument closes at the per-mille level with long chains on a dense grid. Restriction to β ≥ 0.3 (negative-T branch) stands.

## 14. Duality is a structure; the sector is the cause — the general principle (2026-09-25)

**Thesis.** A duality is a bijection of the *description* — of the sector lattice and its parameters — that preserves
the spectrum. It is exact where it is exact, and it is verified numerically in this programme (η·n_sλ² = 1 to
12–27 % on eleven energies in two boxes). It is not a cause: intervening on a description is not an intervention.
The cause is the topological sector — a conserved label the dynamics cannot change continuously (`TopologicalProtection`),
additive in scale (`ScaleResolvedWinding`), readable as the continuum degree (`ContinuumWinding`), carrying its own
temperature (`SectorTemperature`), and shown to be a difference-maker under an energy-matched intervention (rounds 2–3).
And the duality is not a bridge to K3 × T²: the Fricke involution is the same map without the group (`Fricke.lean`,
v1.9.0), and it is not even a symmetry of the Hall plateau set (`QHFricke.lean`).

**The mathematical anchor (`CompactBoson.lean`).** For the compact boson, sectors are (n, w) ∈ ℤ² with
Δ(n, w; R) = n²/R² + w²R²/4. Kernel-checked: (i) Δ(n, w; R) = Δ(w, n; 2/R) and the sector sum Σ_{ℤ²} is invariant
under R ↦ 2/R because it is a *reindexing* (`Equiv.tsum_eq`, no convergence assumption) — that is what the duality is;
(ii) Δ(1,0)·Δ(0,1) = 1/4 for every R — the duality-invariant product, which in the superfluid dictionary is
η·n_sλ² = 1, i.e. *our numerical test of the duality was the measurement of this product*; (iii) the self-dual radius
√2 (Δ = 1/2 each) and the vortex-marginality radius 2√2 (Δ(0,1) = 2, η = 1/4) differ: the transition is the
threshold of one sector, not the fixed point of the exchange. Savit's review (RMP 52, 453, 1980) gives the general
form: a duality is a Fourier (Pontryagin) transform on the group of sectors, electric charges in G ↔ magnetic charges
in Ĝ; the Lagrangian sum over one sector family becomes the Hamiltonian sum over the dual family by Poisson
summation. The partition function is invariant; no sector is special except at the self-dual point.

**When is a self-dual point physical? The refined criterion.**
* It pins a transition when the two dual sectors are simultaneously critical and the fixed-point structure is
  *discrete*: Kramers–Wannier (Phys. Rev. 60, 252, 1941) fixes the Ising T_c at sinh 2K = 1 because order and
  disorder operators (Fradkin–Susskind, PRD 17, 2637, 1978) exchange and Z₂ has one symmetric point.
* It does **not** pin the transition when the fixed points form a *line* and the transition is the marginality of one
  sector: the compact boson / XY / 2D superfluid — BKT at 2√2, self-dual at √2.
* It is a *preferred equilibrium* when both sectors are populated with symmetric weights and compete energetically:
  string gas cosmology (Brandenberger–Vafa, Nucl. Phys. B 316, 391, 1989; Brandenberger's review arXiv:0808.0746):
  momentum modes prevent contraction, winding modes prevent expansion, the radion is stabilised at the self-dual
  radius; but the *transition* out of the Hagedorn phase is, again, the **annihilation of winding modes** — a sector
  event — and T-duality is "the symmetry we make use of" of the spectrum.
* The superconductor–insulator transition (Fisher, PRL 65, 923, 1990; Cha–Fisher–Girvin, PRB 44, 6883, 1991):
  boson–vortex duality (Fisher–Lee, PRB 39, 2756, 1989; Dasgupta–Halperin, PRL 47, 1556, 1981) predicts a universal
  resistance at a self-dual critical point; experiments scatter around it. Here the cause is again the sector — the
  proliferation of vortices (or of charges on the dual side) — and self-duality is a *constraint on the critical
  point*, exact only if the transition happens to be self-dual, which is a property of the fixed point, not of the
  duality.
* Quantum Hall (Lütken–Ross): Γ₀(2) organises the plateau diagram; the cause of quantisation is Laughlin's gauge
  argument on the Chern sector; the Fricke element is not a symmetry of the plateaux.

**The generalised statement.** Across these domains the same triad recurs: (1) a group of sectors G (ℤ for U(1)
windings; Z₂ for Ising; Chern numbers; string windings), (2) a duality = a Fourier/reindexing map between G-sectors
and Ĝ-sectors that preserves the spectrum, (3) physics that happens when a *sector* crosses a threshold (marginality,
proliferation, annihilation) or is imposed by an intervention. Causes live in (3); (2) constrains where (3) can
happen only when the dual sectors are symmetric at the transition. This is why "the same involution" appears in
helium, Hall bars, K3 moduli and string gases — and why it explains none of them.

**Literature (DOIs verified 2026-09-25):** Savit 10.1103/RevModPhys.52.453 · Kramers–Wannier 10.1103/PhysRev.60.252 ·
Fradkin–Susskind 10.1103/PhysRevD.17.2637 · Dasgupta–Halperin 10.1103/PhysRevLett.47.1556 · Fisher–Lee
10.1103/PhysRevB.39.2756 · Fisher 1990 10.1103/PhysRevLett.65.923 · Cha–Fisher–Girvin 10.1103/PhysRevB.44.6883 ·
Brandenberger–Vafa 10.1016/0550-3213(89)90037-0 · Brandenberger review arXiv:0808.0746.
