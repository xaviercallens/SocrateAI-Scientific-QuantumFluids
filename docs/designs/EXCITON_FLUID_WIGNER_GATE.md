# Exciton fluids: quantum crystallisation of 2D dipolar bosons, literature gate

Date 2026-10-11. Written before any computation of the Wigner package (pre-registration:
`EXCITON_FLUID_WIGNER_PREREG.md`). Every number below was read by me in the text of the paper at the stated arXiv
id (PDF fetched and converted with `pdftotext`; copies in the session scratchpad, not in the repository). A number not
read is not quoted.

## Sources actually read

### S1. Astrakharchik, Boronat, Kurbakov, Lozovik, arXiv:cond-mat/0608246v3 (20 Feb 2007)
"Quantum phase transition in a two-dimensional system of dipoles". The arXiv page lists Phys. Rev. Lett. 98, 060405
(2007); the journal page itself was **not** read, only the arXiv text (and the citation of the PRL in S3's reference list).

* Model: bosons of mass M, `H = -(hbar^2/2M) sum Laplacian_i + (C_dd/4 pi) sum_{j<k} 1/|r_j - r_k|^3`, dipoles
  perpendicular to the plane, so purely repulsive; **bare unscreened 1/r^3**, no short-range term, no gate.
* Definition: `r_0 = M C_dd / (4 pi hbar^2)`, energy unit `E_0 = hbar^2/(M r_0^2)`; the only parameter is the dimensionless
  density `n r_0^2` (n = areal density). The pair potential is therefore `V(r) = hbar^2 r_0 / (M r^3)`. For indirect
  excitons the paper writes `C_dd = e^2 D^2 / epsilon` (D = electron-hole separation, epsilon = dielectric constant of the
  semiconductor).
* Method: diffusion Monte Carlo, T = 0, Bijl-Jastrow guiding function, gas trial state and solid trial state
  (Gaussian localisation); tail-energy correction and `E(N) = E_th + C/sqrt(N)` extrapolation.
* Result: gas-solid transition at `n r_0^2 = 290(30)` (text: "critical density n r_0^2 = 290(30)"); coexistence region
  "very small", freezing and melting "indistinguishable within the error bars". Classical triangular lattice potential
  energy `E_triang/N = 4.446 (n r_0^2)^{3/2}` (in units E_0). Lindemann ratio at the transition
  `gamma = sqrt(<(r - r_c)^2>)/a_L = 0.230(6)` (a_L = lattice length); they quote 0.235(15) for Yukawa bosons and
  0.24(1) for Coulomb bosons (from their ref. [16], not read) and 0.279 for hard disks. Condensate fraction about 2% at
  the transition.

### S2. Astrakharchik, Boronat, Casulleras, Kurbakov, Lozovik, arXiv:0707.4630v1 (31 Jul 2007)
"Ground state properties of a homogeneous 2D system of Bosons with dipolar interactions." Same model and the same
`r_0` as S1 (their eq. 1 and text). VMC and DMC. Repeats `n_c r_0^2 = 290(30)` and, as quoted values from other works
(their refs [4], [5], which I read only through this paper, S3 being the first of them): a path-integral value
`n_c r_0^2 = 320(140)` at low finite temperature and a Green's-function Monte Carlo value `230(20)` obtained on a
discrete model. Also: s-wave scattering length `a = e^{2 gamma} r_0 = 3.17 r_0`. Supersolid (abstract): "Non-zero superfluid fraction is found in a finite-size crystal,
the signal being dramatically increased in presence of vacancies"; I did not read beyond the first sections of the
supersolid discussion and make no bulk claim. Unscreened 1/r^3.

### S3. Buechler, Demler, Lukin, Micheli, Prokof'ev, Pupillo, Zoller, arXiv:cond-mat/0607294v1 (11 Jul 2006)
"Strongly correlated 2D quantum phases with cold polar molecules: controlling the shape of the interaction potential",
Phys. Rev. Lett. 98, 060404 (2007) (journal number as printed in S2's reference list).

* Model: `V_eff(R) = D/R^3`, bosonic polar molecules of mass m; **bare unscreened 1/r^3** for the quantum-melting study.
* Definition: `r_d = D m / (hbar^2 a)` with `a` "the average interparticle distance" and `n = 1/a^2`. Hence
  `r_0 = m D / hbar^2` and `r_d^2 = n r_0^2`: the same density parameter as S1 once S1's `C_dd/4 pi` is identified with `D`
  (this identification is mine, from the two Hamiltonians; both papers have `V = const/r^3`).
* Method: path-integral Monte Carlo with the worm algorithm, finite temperature `T = 0.014 D/a^3`, N = 36 and 90.
* Result: "transition point r_QM = 18 +- 4"; the superfluid fraction drops to zero at `r_d ~ 15`, with occasional
  jumps between 0 and 1 in `r_d ~ 15-20`. In terms of S1: `n r_0^2 = r_d^2 = 324`, interval 196-484 (square of 18 +- 4;
  my conversion). The crystal has triangular lattice with `a_L = (4/3)^{1/4} a`. They state a classical melting
  temperature `T_m ~ 0.09 D/a^3` citing their ref. [8], which I did **not** read.

### S4. Boening, Filinov, Bonitz, arXiv:1101.1757v2 (17 Apr 2011)
"Crystallization of an exciton superfluid". Read: abstract, introduction, model section and the parts of the results
that my text search hit; I did not read it end to end, and I quote **no critical density** from it. Qualitative content
that I read: path-integral Monte Carlo of composite indirect excitons (finite quantum-well width, electron and hole
masses, Coulomb interactions among 2N charges); the exciton-exciton interaction "strongly deviates from a dipole
potential at small distances"; as a consequence the crystal "exists only in a finite density interval and undergoes
quantum melting both at high and low density", and no supersolid phase was seen. Not the 1/r^3 model and not gated.

### S5. Valenti, Calvera, Yang, Morales, Kivelson, Esterlis, Zhang, arXiv:2501.16430v1 (27 Jan 2025)
"Critical gate distance for Wigner crystallization in the two-dimensional electron gas". This is the only gated
quantum-Monte-Carlo crystallisation study I found; it is **Coulomb electrons (fermions)**, not dipolar bosons, with a
dual-gate screened interaction `v_sc(q) = e^2 tanh(d|q|)/(2 eps_0 |q|)` (gates at distance d from the 2DEG; for
`r >> d` the real-space potential is `~ exp(-pi r/2d)`). DMC (fixed node) with N = 56 (120 in special cases). Relevant
for method, not for numbers:

* They apply exactly the programme asked for here: harmonic-phonon Lindemann criterion, `gamma_c ~ 0.3` "fixed by
  matching to the d = infinity transition" (`r_s ~ 30`), then transferred to gated geometry; DMC critical gate distance
  `d_c ~ 29`, Lindemann/Hansen-Verlet estimates `d_c ~ 35`, "exceeding the DMC-obtained value by only about 20%".
* Phase diagram: for finite d the crystal is bounded at both low and high density (at low density, when the spacing
  exceeds the interaction range, a fluid (metal) is stable).

### Sources not read
* Mazzanti et al.: the searches surfaced a Macia-Mazzanti-Boronat work on anisotropy (arXiv:1210.3969) and a thesis
  (tdx.cat/handle/10803/286784); **not read**, no number quoted. I did not find, and therefore make no statement about,
  a Mazzanti et al. crystallisation paper.
* Moroni-Boninsegni style or other PIMC finite-temperature melting studies of 2D dipoles: not searched; no statement.
* Dipolar bosons in a gated (metal-screened) quantum-Monte-Carlo study: none found in two searches (one general, one
  with "metallic gate"). Absence of evidence in a short search, not a proof of absence.

## What these sources give, in one table

| Source | Parameter (as defined) | Critical value | Method | Potential |
|---|---|---|---|---|
| S1 | `n r_0^2`, `r_0 = M C_dd/(4 pi hbar^2)` | 290(30) | DMC, T=0 | bare 1/r^3 |
| S2 | same | 290(30); quotes 320(140) (PIMC), 230(20) (GFMC, lattice model) | DMC/VMC | bare 1/r^3 |
| S3 | `r_d = D m/(hbar^2 a)`, `n = 1/a^2` | `r_QM = 18 +- 4` i.e. `n r_0^2 = r_d^2 ~ 324` (196-484) | PIMC worm, T = 0.014 D/a^3 | bare 1/r^3 |

S1 and S3 agree within S3's error bar. The quantum Monte Carlo statistical spread is about 10% (S1) to 45% (S3 in
`n r_0^2`).

## Where our gated kernel differs from the case studied

Theorem 1 of `EXCITON_FLUID_GATE_IMAGE_CM.md`: `U(r) = V_ee + V_hh - 2 V_eh` from the image series of two grounded gates
at `z = +-h` with layers at `z = +-d/2`; `U(r) = int_0^inf mu(s) exp(-s r^2) ds`, `mu >= 0`.

1. **Short distance.** `U(r) = 2/r - 2/sqrt(r^2 + d^2)` without gates: `U ~ 2/r` (Coulomb-like) for `r << d`, and
   `U -> d^2/r^3` only for `r >> d`. The 1/r^3 studied in S1-S3 is the large-distance asymptote only; it has no `1/r`
   core. The two coincide when the interparticle spacing is much larger than d. Equating `d^2 e^2/(epsilon r^3)` with
   `hbar^2 r_0/(M r^3)` gives `r_0 = M e^2 d^2/(epsilon hbar^2)` (Gaussian units), i.e. `r_0/d = d/a_M`,
   `a_M = epsilon hbar^2/(M e^2)`.
2. **Long distance.** With gates, `U` is exponentially small for `r > D = 2h`; S1-S3 have a `1/r^3` tail that matters
   (S1's tail-energy correction is a 1/sqrt(N) effect). The harmonic phonon sums are convergent for the gated kernel
   with a short cutoff, for 1/r^3 they need a tail term.
3. **Re-entrance.** An interaction with finite range cannot keep the system crystalline at low density (S5 found a fluid
   there; S4 found two-sided melting for a different reason, the short-distance softness). The 1/r^3 case has only
   the high-density melting boundary of S1-S3 (as density goes to zero, `n r_0^2 -> 0`, a gas).
4. **Statistics, mass and composite character.** The kernel is the classical rigid-exciton kernel; no exchange,
   no polarisation, no biexciton, no Mott physics. S4 shows these matter when the spacing approaches d.
5. **No QMC exists, as far as I found, for this kernel.** Any statement about its critical density is therefore an
   estimate calibrated on S1-S3, not a check against data.
