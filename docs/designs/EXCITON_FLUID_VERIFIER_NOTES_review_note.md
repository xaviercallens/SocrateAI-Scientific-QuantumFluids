# Referee report: gated_kernel_note.tex (hostile read, analysis/PDE)

Verdict: no blocking mathematical error found. Theorem 1, Steps 1-4 and Proposition 2 are correct as stated
(for z_e, z_h in the slab). Two statements need fixing before it goes out (Remark; "all real z"), and Prop. 2
needs its proof written out because that is exactly what the reader is asked to check. One unconditional
strengthening (lattices, Montgomery) is missing and is the most valuable addition.

I re-ran python3 exploration/exciton/python/gated_note_check.py: image series vs Laplace integral agree to
~1e-12 at r=0.3, 1, 2.5 (script is independent: direct signed image sum N=2e5 symmetric truncation vs quad of mu
from the eigen-formula). Lean file: 1083 lines, 52 theorem/lemma, 17 #print axioms, no sorry/axiom/native_decide
(the only "sorry" hit is a comment) -- matches the note.

## (1) Eq. (images)  -- CORRECT
- Reflections z->2h1-z and z->-2h2-z compose to translation by 2(h1+h2)=P. Images of a charge at z': +1 at
  z'+Pn, -1 at 2h1-z'+Pn (the family -2h2-z'+Pn' is the same family, Pn' shifted by P). Signs and offsets in
  (images) match. K=4piG=1/R in free space: OK.
- Pair n: a=z-z'-Pn, b=z+z'-2h1-Pn; a-b=2(h1-z') constant, a+b~-2Pn, so a^2-b^2=O(n) and the pair difference is
  O(n)/|n|^3=O(n^-2). Absolute convergence of the paired series: correct. (Remark: the unpaired sums diverge
  like sum 1/|n|, so "paired by n" is part of the definition; the note says so. Good. Vanishing on z=h1:
  b_n=-a_{-n}, pairs cancel exactly -- fine.)
- Sharper but optional: in a symmetric truncation the n^-2 leading term is odd in n and cancels, so symmetric
  partial sums converge like N^-2; explains the 1e-12 numerics at N=2e5.

## (2) Steps 1-4  -- CORRECT, with wording issues
- Step 1: product structure and image form of q_s: correct. Eigen-normalisation: int phi_m^2 = l/2, so q_s=(2/l)sum.
- Step 2: s^{-1}ds -> dsigma/sigma under sigma=1/(4s): checked (s^{-1}=4sigma, ds=dsigma/(4sigma^2)).
  mu=sigma^{-1}S_{1/4sigma}. Converges for r>0: q_s<=g_s(0) by domain monotonicity, spectral gap lambda_1>0 gives
  e^{-s lambda_1} at large s. Correct. (Also: each K_ab alone is already a Laplace transform of a positive
  density because the Dirichlet heat kernel is pointwise positive; only the minus sign in U needs Step 3.)
- Step 3: semigroup + symmetry => S_s = int (q_{s/2}(z_e,w)-q_{s/2}(z_h,w))^2 dw: correct. 4/(P sigma)=2/(l sigma): correct.
  Trig identity in the Lean table: 2-cos2a-cos2b-2cos(b-a)+2cos(a+b)=2(sin a-sin b)^2 and
  2(1-cos(b-a))(1+cos(a+b)) equal it: verified by hand. Poisson formula in the table: verified (FT of e^{-s x^2}),
  and e^{-pi^2m^2/(P^2 s_L)} with s_L=1/(4s_h) equals e^{-s_h lambda_m}: consistent.
- Step 4 asymptotics: mu->0 as sigma->0 correct (e^{-lambda_1/4sigma}/sigma). mu~2(pi sigma)^{-1/2} as
  sigma->inf is correct for z_e != z_h, and 2/r = int e^{-r^2 sigma} 2(pi sigma)^{-1/2} dsigma checks out.
  BUT the justification "Riemann sum with spacing ~ sigma^{-1/2}" is not right as stated: the summand
  (phi_m(z_e)-phi_m(z_h))^2 oscillates in m, so it is not a Riemann sum of a continuous function; it is an
  averaging (equidistribution) statement. Cleaner and rigorous: sigma->inf is s->0, and the image form gives
  S_s = 2 g_s(0) + O(e^{-c/s}) for z_e != z_h, hence mu = (2/sigma)(sigma/pi)^{1/2}(1+o(1)). Replace the sentence.
  Also state z_e != z_h (for z_e=z_h, mu=0 and U=0).
- mu continuous (locally uniform convergence of the series) and bounded (->0 at both ends): correct. Differentiation
  under the integral with sigma^k e^{-t sigma}<=C e^{-t0 sigma/2}, mu bounded: correct.

## (3) Proposition 2 (layered dielectric) -- CORRECT; proof too terse (MAJOR for presentation)
Checked: B=eps^{-1}(-div eps grad) = -Delta_x + A, A=-eps^{-1} d_z eps d_z self-adjoint, >=0 on L^2(eps dz) (form
int eps|u'|^2 on H^1_0). L=-div eps grad = eps B, so L^{-1}=B^{-1} eps^{-1}; if b is the kernel of B^{-1}
w.r.t. eps dx'dz', then L^{-1}f=int b f dx'dz', i.e. G=b: the Green function w.r.t. Lebesgue measure is the
kernel w.r.t. eps dz. This is the point the reader is asked about and it is correct, but the note never writes it.
Homogeneous check: eps const => G=1/(4 pi eps R). OK.
K_0 identity: int_0^inf u^{-1}e^{-au-b/u}du=2K_0(2 sqrt(ab)); with a=t, b=lambda/4: K_0(sqrt(lambda t)) =
(1/2) int e^{-ts}e^{-lambda/4s} ds/s. Correct, and s there is the Laplace variable sigma (conjugate to t=r^2),
not the heat time; say so. Heat-time form: int s^{-1}e^{-r^2/4s}e^{-s lambda}ds = 2K_0(sqrt(lambda) r), so with
phi_m orthonormal in L^2(eps dz), c_m = 2 exactly (c_m >= 0 is true but weaker than needed). Sanity: 2D Green
function of -Delta+lambda is K_0/(2pi), 4pi*K_0/(2pi)=2K_0. For the sin-eigenfunctions of Thm 1: c_m = 4/l.
Discontinuous eps is fine: H^1 in 1D => point values of phi_m and q_s are continuous, flux eps phi' is
continuous; resolvent compact; charges exactly on an interface are allowed. Measurable, bounded, bounded-below
suffices; "stack of homogeneous layers" is more restrictive than needed.
Things to write out in the proof (all easy, none wrong):
 a) form/self-adjointness/compact resolvent on L^2(eps dz); b) G=b relation above; c) Step 2 integrability for
 s->0 is not "verbatim": there is no explicit g_s(0) bound; use 1D ultracontractivity ||e^{-sA}||_{L1->Linf}<=C s^{-1/2}
 (Nash/Sobolev, uniform ellipticity); d) the eigen-sum for U converges by Tonelli since every term is >=0
 (this removes any worry about sum/integral interchange); e) phi_m here is orthonormal, differently normalised
 from Theorem 1 -- rename (psi_m) to avoid a notation clash.
Free generalisation worth stating (hBN!): uniaxial eps_par(z), eps_perp(z): operator -eps_par Delta_x - d_z eps_perp d_z
divided by eps_par is -Delta_x + A with A=-eps_par^{-1} d_z eps_perp d_z, self-adjoint on L^2(eps_par dz): the
same proof works; lateral eps_par may vary with z. Only lateral inhomogeneity / finite screening breaks it.

## (4) Schoenberg remark -- LITERALLY INCORRECT AS WORDED (MAJOR, easy fix)
U(0)=+infinity (U~2/r), so x->U(|x|) is not a positive-definite *function* in Bochner's sense (needs finite
value at 0). It is a positive-definite *distribution* on R^d for d>=2: 1/r is locally integrable for d>=2 and
its Fourier transform int mu(sigma)(pi/sigma)^{d/2}e^{-k^2/4sigma}dsigma is positive and finite for k != 0
(integrand ~ sigma^{-(1+d)/2} at infinity). For d=1 it FAILS: 2/|x| is not locally integrable and the
transform diverges logarithmically. So "to all R^d" must read d>=2 (or: regularise U(r)->U(sqrt(r^2+eps^2)),
or "positive-definite on R^d off the diagonal"). The direction used (CM => PD) is Bernstein + Gaussians, not
Schoenberg's theorem; Schoenberg is only needed for the converse. Rephrase.

## (5) Universal optimality section
- Citations: Cohn-Kumar, J. Amer. Math. Soc. 20 (2007), 99-148: correct as far as I know. CKMRV, Ann. of Math.
  196 (2022), no. 3, 983-1082: correct as far as I know. Neither verified online here.
- Wording: Cohn-Kumar 2007 define universal optimality on SPHERES (CM functions of squared chordal distance);
  the Euclidean/periodic version is the CK conjecture in their last section and the setting of CKMRV. The
  sentence "Cohn and Kumar defined ... for every CM function of squared distance" is acceptable but slightly
  conflates; suggest "on spheres [CK07]; in R^n [CKMRV22]".
- The repo [OpenAI2026] (github.com/openai/math, "family 090"): I could not verify it exists/says that. Make sure
  the URL resolves and that the family number is right before sending; a mathematician will click it.
- Conditional proposition: logically fine. Sharpen: via the Gaussian-mixture representation only Gaussian
  potentials are needed (this is the Cohn-Kumar reduction), and a singularity t^{-1/2} at 0 plus exponential
  decay satisfies any reasonable convergence condition. MISSING UNCONDITIONAL COROLLARY: among lattices the
  statement is a THEOREM (Rankin/Cassels/Ennola/Diananda 1950s; Montgomery, "Minimal theta functions", Glasgow
  Math. J. 30 (1988) 75-85 -- journal pages from memory, check): the triangular lattice minimises
  sum_{v in L\{0}} e^{-sigma|v|^2} at fixed density for every sigma>0. By Tonelli,
  E_L = int mu(sigma) (theta_L(sigma)-1) d sigma, so for every z_e,z_h,h1,h2 the triangular lattice minimises
  the U-energy per particle among all Bravais lattices of given density, unconditionally. This is the
  rigorous, refereed core of the "hexagonal pattern" claim and should be a proposition.
- Overclaim (minor): "a triangular lattice is the ground state of nearly every monotone repulsion in 2D" is
  too strong (soft-core / cluster-crystal potentials of Likos type have non-triangular ground states). Say "of
  the usual long-range repulsions (Coulomb, Yukawa, dipolar)" or restrict to CM potentials plus the caveat.

## (6) Other gaps / overclaims (minor)
1. Theorem says "for all real z_e,z_h": the Green-function interpretation needs z_e,z_h in [-h2,h1]; outside, (images)
   is just the odd P-periodic extension (still equals (mu), but is not a physical Green function and has
   singularities at images). State z in [-h2,h1] (closed is fine: boundary gives K=0).
2. "U(r)~2/r at 0 for z_e != z_h": needs both planes in the OPEN slab; on a conductor that charge's K_aa=0 and
   the coefficient is 1/r. (Not an issue for physical 2D layers.)
3. "U>0 is proved as a consequence of mu>=0": mu>=0 gives U>=0; U>0 needs mu not identically 0, i.e.
   z_e != z_h (U=0 identically when z_e=z_h, and for z_h=z_e+P mod images). Reword.
4. "K_ee - 2K_eh can be negative mode by mode": true; clarify that neutrality fixes the quadratic form
   (phi_e-phi_h)^2 and that the dropped K_hh is what completes the square.
5. "Units of e^2/eps": with K=4piG in Prop. 2 the unit is e^2 (eps absorbed in G). Say "Gaussian-type
   units, K=4 pi G" once.
6. Priority: the modal form U=(4/l) sum_m (dphi)^2 K_0(m pi r/l) is the classical parallel-plate expansion
   (Smythe, Jackson-type cylindrical expansion; Rytova/Keldysh-type literature for slabs) and K_0(sqrt(t)) being CM is
   standard. The honest novelty is only the neutral-square argument + formalisation; the abstract already says
   "may well be known" -- keep that, and in item 1 of the questions mention the modal expansion as the likely
   place it is already implicit.
7. Lean table: "sum_m" in gsum_poisson is over m in Z (cos even), so the prefactor convention (m>=1 gets a 2)
   should be stated; and the Lean bound statement "for sigma>=1 / sigma<=1" is fine. "Poisson summation ...
   derived from Mathlib's Jacobi theta results" fine.
8. Author line: "written with an AI system" good; consider also saying the numerical check is a symmetric
   truncation (N=2e5) -- the 1e-12 claim depends on it.
