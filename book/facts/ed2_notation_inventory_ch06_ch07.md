Inventory of `book/chapters/ch06.tex` (694 lines) and `book/chapters/ch07.tex` (499 lines). I read every line of both. Line numbers are those of the files on 2026-10-10. Nothing was created or changed, and LaTeX was not run.

Other files I read (read-only):
- `book/figures/ch06_constants.json`, `book/figures/ch06_numbers.json`, and the header of `book/figures/ch06_numbers.py`. These are the macro sources.
- Targeted greps of ch01, ch03, ch04, ch05, ch09, ch10 and the appendices, for Section E.

ch07 defines no `\cn...` macros; all its numbers are literals.

**Quoting convention.** Section A quotes the source verbatim. In table cells only, the source's `|` is written `\vert` and its `\|` is written `\Vert` (they mean the same in LaTeX), so the Markdown tables do not break. Everything else is verbatim.

## ch06 — Vortices in Two Dimensions: the Kosterlitz--Thouless Flow
`\chapter` is at l.119; the generated macro block `\cn...` is at l.6–118.

### A. Units and conventions

**Helium-film side (cgs, kelvin)**
- l.134: `\frac{\rho_s(T_c^-)}{T_c}=8\pi k_B\Big(\frac{m}{h}\Big)^{2}=\cnJump\times10^{-9}\ \mathrm{g\,cm^{-2}\,K^{-1}}`. `\cnJump` = 3.49 (l.57). Kelvin is typeset `\mathrm{K}`, the same letter as the stiffness K. Only the cgs value is printed; the SI value exists only in the JSON.
- l.136: "the superfluid areal mass density". So ρ_s is a 2D mass per area.
- l.131–132: "With `$m=4.002\,603\,254\,13$` atomic mass units (the NIST value for `$^4$He`) and the CODATA values of the constants shipped with SciPy". The JSON records SciPy 1.18.1.
- l.137–138: "In the units of this book, with the thermal wavelength `$\lambda_T^2=2\pi\hbar^2/(mk_BT)$` and the superfluid number density `$n_s=\rho_s/m$`".
- l.140: `n_s\lambda_T^2=4\quad\text{at }T_c^-,\qquad n_s\lambda_T^2\to0\quad\text{above }T_c.`

**KT couplings in units of k_BT**
- l.166: "with the stiffness `$J=\hbar^2n_s/m$` (an energy)".
- l.170: `K\equiv\frac{J}{k_BT}=\frac{n_s\lambda_T^2}{2\pi}`. l.174 calls it "The dimensionless stiffness `$K$` is the variable of this chapter".
- l.281: "`$K>2/\pi$` in Kosterlitz--Thouless units is `$2\pi K>4$`, that is, `$n_s\lambda_T^2>4$`". The chapter names two conventions: "Kosterlitz–Thouless units" (K) and "the units of this book" (`n_s\lambda_T^2`).
- l.201: "the vortex fugacity `$y(l)$` (the Boltzmann weight of a core, `$y\sim e^{-E_c/k_BT}$`)".
- l.212: "The coefficient `$4\pi^3$` depends on how the fugacity is normalised; none of the conclusions do".
- l.200: "integrate out the pairs of size between `$a$` and `$ae^{l}$`". So l is the log of the length in units of the core size a. It is written `l`, never `\ell`.
- l.506 and l.517: "`$l=\ln(L/a)$`" for a film or box of size L.
- l.207: "We write `$u=1/K$`". l.486: "the upper axis gives `$n_s\lambda_T^2=2\pi/u$`".
- l.508: "`$\xi=e^{l^*}\sim e^{\pi^2/4a}$`"; l.529: "`$\xi\sim e^{l^*}$`". Here ξ is the KT correlation length, in units of a.

**Dimensionless Gross–Pitaevskii (solver) units**
- l.383: "(`$\hbar=m=1$`, mean density `$n=1$`, `$gn=1$`, so the healing length is `$\xi=1$`; the field lives on a periodic box of side `$L$`, ...)". No formula for ξ is written. ξ=1 under these settings means ξ=ℏ/√(mgn), with no factor 2; ch03 l.41 writes that formula explicitly.
- Energy unit:
  - l.402: "(`$\Delta E$` from `$\cnElowSixtyfour$` to `$\cnEhighSixtyfour$` in units `$\hbar^2n/m$`)".
  - l.405–406: "if the coupling is `$2\pi\hbar^2n/m$`".
  - l.408: "The Coulomb-gas coupling of the programme's projected field is therefore `$2\pi\hbar^2n_s/m$` with `$n_s=n$` at zero temperature".
- Velocity: no unit is ever stated (implicitly ℏ/(mξ)). l.388: "a uniform counterflow `$v=2\pi d/L^2$` is added, of kinetic energy `$\tfrac12 nv^2L^2=2\pi^2d^2/L^2$`".
- Box sizes:
  - `$L=64\,\xi$` and `$L=128\,\xi$` (l.397–398).
  - Ladder at `$L=64\,\xi$` (l.542) and `$L=32\,\xi$` (l.544).
  - "six `$L=192$` runs" (l.606), with no ξ written.
  - The Weiss–McWilliams function is "for a box rescaled to `$2\pi$`" (l.386).
- Temperature of the classical field:
  - l.538–539: "its temperature is \emph{measured} from the trajectory (equipartition of the modes near the cutoff), not imposed".
  - l.548: "`$T$`, from equipartition of the high-wavenumber modes, in units `$\hbar^2/(m\xi^2)$` with `$k_B=1$`".
- l.550: "`$n_s\lambda_T^2=(n_s/n)\,2\pi/T$` (for `$n=1$`, `$\lambda_T^2=2\pi/T$`)". l.593: "`$n\lambda_T^2=2\pi/T_{\rm BKT}=\cnNlambda$`".
- l.549: "`$n_s/n=1-\langle|J_T|^2\rangle/\langle|J_L|^2\rangle$`" (current correlators at the smallest wavevectors).
- Coupling: l.594 "`$\tilde g=1$` here, which is not small"; l.653 "in units where `$\tilde g=1$` is not small". `\tilde g` is never defined.
- Energy per particle: l.541–542 "(energy per particle `$e=0.90$`, evolved to `$t=4000$`, two seeds) ... `$e=1.00,1.05,\dots,1.40$`". The unit of e is not stated.
- Time:
  - l.542: "a transient of `$500$` time units and is averaged over `$t=500$` to `$1500$`".
  - l.545: "last `$4000$` time units, with the last `$1000$` sampled".
  - l.606: "`$t=13\,510$` to `$14\,500$`".
  - The time unit is never defined in ch06. ch03 l.41 and ch01 l.186 define it as ξ/c.
- Grid, cutoff and number of modes:
  - The only grid statement is l.588: "positions are on the grid, so separations below `$0.5\,\xi$` are not resolved". This implies a 0.5ξ spacing for the L=64 ladder.
  - The cutoff is never given a value: "with a cutoff" (l.539), "a classical field with a sharp cutoff" (l.595), "a classical Bose gas with a cutoff" (l.653).
  - The grid size and number of modes are never stated.
- Wavevectors and distances:
  - "reciprocal lattice (all `$|n_x|,|n_y|\le6$`)" (l.608).
  - "`$k_1=2\pi/L$`" (l.679).
  - "shells `$m^2=4,\dots,16$`" (l.614).
  - Minimum-image separations (l.373, l.607).
- Engine provenance (needs a check): l.538 says "The engine of \cref{ch06:coulomb} is a classical field: the projected Gross--Pitaevskii equation ...", and that engine is qf-pgpe. But l.648–649 says the ladder values "come from runs of the programme's numpy engine ..., recomputed here from the raw records, not re-run".
- Solver settings:
  - `atol=1e-13`, `max_steps=500000` (l.429–430).
  - "Adams at `$\mathrm{rtol}=10^{-9}$`" (l.474).
  - Environment probe: "`$y'=-y$` on `$[0,10]$` with Adams at `$\mathrm{rtol}=10^{-8}$`" (l.447).

### B. Symbols

These do not occur anywhere in ch06 (checked by grep): `\mu`, `\beta`, `\Gamma`, `\ell`, `\kappa`, `\gamma`, `\alpha`, `D` as a symbol, `T_{\rm KT}`.

| symbol (LaTeX as in source) | meaning in this chapter | units / convention | line(s) | remarks |
|---|---|---|---|---|
| `$T_c$`, `$T_c^-$` | transition temperature of the ⁴He film; `T_c^-` means just below it | kelvin (jump formula) | 124, 129, 134, 140; generic in the RG text at 220, 222, 227, 508, 529 | (ii) the film is `T_c`, the simulated field is `T_{\rm BKT}`; `T_{\rm KT}` never appears |
| `$T_{\rm BKT}(L{=}64)$`, `$T_{\rm BKT}(L{=}32)$`, `$T_{\rm BKT}(64)$` | temperature at which the field's interpolated `n_s\lambda_T^2` crosses 4 | ℏ²/(mξ²), k_B=1 | 576, 578, 587, 593, 600, 648 | a finite-box crossing, not an infinite-size value; ch07 reuses 0.821 |
| `$\rho_s$`, `$\rho_s(T_c^-)$` | superfluid areal mass density of the film | g cm⁻² | 129, 136 | (ii) in ch07, ρ_s is the field density with m=1 |
| `$m$` | mass of a ⁴He atom; =1 in the solver | u (NIST) | 131–132, 166, 383 | (i) also the negative-vortex positions `m_j` (347, 357, 365, 376) and the shell index `m^2` (614) |
| `$k_B$`, `$h$`, `$\hbar$` | Boltzmann's and Planck's constants | CODATA via SciPy; ℏ=1 (383), k_B=1 (548) | 129, 138 | |
| `$\lambda_T$` | thermal wavelength, `\lambda_T^2=2\pi\hbar^2/(mk_BT)` | length; `\lambda_T^2=2\pi/T` in GP units (550) | 138 | (ii) ch07 uses λ for a rate (ch07 l.435) |
| `$n_s$` | superfluid number density `n_s=\rho_s/m` (areal) | m⁻²; in the field, `n_s/n` | 138, 549 | |
| `$n_s\lambda_T^2$` | stiffness "in the units of this book" | dimensionless; 4 at `T_c^-` | 138–140 | equals 2πK; equals ch07's K |
| `$n$`, `$n\lambda_T^2$` | mean density (=1); phase-space density | | 165, 383, 593 | |
| `$\psi$`, `$\theta$` | order parameter `\psi=\sqrt{n}\,e^{i\theta}`, and its phase | | 165 | |
| `$J$` | phase stiffness `J=\hbar^2n_s/m` | energy | 166 | (i) `J_T`, `J_L` are currents (549); (ii) ch07 `\mathbf J` is a probability current |
| `$J_R$` | stiffness felt at large distances, `J\to J_R<J` | energy | 199 | |
| `$a$` | short-distance cutoff (167), then "the core size" (179) | length | 167, 179, 200, 390, 506, 517 | (i) second meaning `a^2=(\pi/2)(f(\pi/2)-H_0)` (508) = `(\pi/2)\epsilon` (527–528), `a\propto\sqrt{T-T_c}` |
| `$g_1(r)$` | `\frac{\langle\psi^*(0)\psi(r)\rangle}{n}` | dimensionless | 170 | |
| `$\eta$` | exponent of `g_1(r)\sim r^{-\eta}`; `\eta=\frac{k_BT}{2\pi J}=\frac{1}{2\pi K}=\frac{1}{n_s\lambda_T^2}` | dimensionless; 1/4 at the jump | 170, 176, 551 | (ii) in ch07/ch10, η is the vortex diffusion constant |
| `$K$` | dimensionless stiffness `J/k_BT=n_s\lambda_T^2/2\pi` | 2/π at the jump | 170, 174 | (ii) kelvin `\mathrm{K}` (134, 653); ch07 `K=2\pi\rho_s/T` (= 2π× this K) and K = set of modes; ch04 K = coefficient of T⁸ |
| `$K(l)$`, `$K_R$`, `$K_0$`, `$K_{0c}$` | running, renormalised (`K_R=1/u_*`), bare, and critical bare stiffness | | 200, 217, 504–505, 513 | |
| `$q$` | integer winding; θ increases by `2\pi q` | | 178 | ch07 uses `q_i=\pm1` |
| `$R$` | size of the film | length | 179–180 | (i) also the remainder R (376) |
| `$E_c$` | core energy | energy | 179 | "no claim is made about `$E_c$`" (410) |
| `$F$` | free energy of one free vortex, `(\pi J-2k_BT)\ln\frac{R}{a}+E_c` | energy | 182 | (ii) ch07 F is a drag force |
| `$d$`, `$E_{\rm pair}(d)$` | pair separation; `E_{\rm pair}(d)=2\pi J\ln\frac{d}{a}+2E_c` | length (ξ in the solver), energy | 190–192 | |
| `$l$` | RG scale | dimensionless | 200 | (i) the Python list `L` holds l values (442) |
| `$y$`, `$y(l)$` | vortex fugacity | normalisation is conventional (212) | 200–201 | (i) `y'=-y` is the probe ODE (447, 467); (ii) in ch07, y is a coordinate |
| `$u$` | `u=1/K` | dimensionless | 207 | (ii) ch03 `\mathbf u` velocity; ch07 u = two drift velocities; ch04 u = series variable |
| `$u_*$`, `$u_0$`, `$y_0$`, `$u_{0c}$` | root of `f(u_*)=H_0` (end point on the fixed line); initial values; critical bare u | | 217, 291, 337, 506, 513 | |
| `$\xi$` | (a) healing length = 1 | length unit | 383, 397ff | (i) (b) correlation length, `\xi\sim\exp(b/\sqrt{T-T_c})`, `\xi=e^{l^*}` in units of a (222, 508, 529) |
| `$b$` | non-universal constant in `\exp(b/\sqrt{T-T_c})` | | 222, 529 | not defined further; (ii) ch07 b = stall point |
| `$f(u)$` | `2u-\pi\ln u` | | 237, 256 | (ii) ch07 `f_k` = drag factor |
| `$H(u,y)$`, `$H_0$` | invariant `f(u)-2\pi^3y^2`; `H_0=H(u(0),y(0))` | | 238, 254, 335 | (ii) ch07 H = point-vortex energy |
| `$x$` | `x=u-\pi/2` | | 257, 519, 527, 670 | (i) `x=2u/\pi\neq1` in the description of `f_gt_fc` (336) |
| `$c$` | `c:=4\pi^3y(0)^2` (305); arbitrary c>0 replacing 4π³ in Ex. 1 (669) | | 305, 669 | (i) also the intermediate-value point `c` in the Lean proof (271, 278) |
| `$l_1$` | escape bound `(\pi/2-u_0)/(2(f(\pi/2)-H_0))` | | 337 | |
| `$\epsilon$` | offset of H₀ from f(π/2): `H_0=f(\pi/2)+\epsilon` (515), but `H_0=f(\pi/2)-\epsilon` (527) | | 515, 527–531 | the sign convention flips between the two paragraphs; (i) differs from `\varepsilon` (628) |
| `$X$`, `$l^*$` | half-width of the crossing interval; scale at which a flow leaves the critical region | | 528; 508, 531 | |
| `$\rho(k)$` | vortex charge density `\sum_{+}e^{ik\cdot p}-\sum_{-}e^{ik\cdot m}` | dimensionless | 347 | captions write `\rho_q(k)` (611, 614) |
| `$p_i$`, `$m_j$`, `$N$` | positions of + and − vortices; number of each sign | | 347 | `N_v` is the total count (561) |
| `$k$`, `$k_1$`, `$n_x,n_y$` | wavevector; smallest wavevector `2\pi/L`; reciprocal-lattice integers | 1/ξ | 347, 679, 608 | |
| `$\sigma$` | a pairing of + with − vortices | | 356, 370 | (ii) ch07 uses `\sigma_{\rm tr}` |
| `$W$` | optimal-transport (minimum matching) cost between the two signs | length | 372, 607 | (ii) in ch07, W is a hypothesis label |
| `$d_i$`, `$P(k)$`, `$R$` | `d_i=p_i-m_i`; polarisation density `\sum_id_ie^{ik\cdot m_i}`; remainder `\vert R\vert\le\sum_i(k\cdot d_i)^2` | | 375–376 | |
| `$H_{\rm WM}(d)$` | Weiss–McWilliams periodic point-vortex pair energy, box rescaled to 2π | energy = `\pi H_{\rm WM}` in ℏ²n/m | 385–386 | |
| `$v$` | uniform counterflow `2\pi d/L^2` | ℏ/(mξ), implicit | 388 | same quantity as ch03 `\bar{\mathbf u}` and ch07 u (352) |
| `$\Delta E(d)$`, `$C_L$` | excess energy of the imprinted pair; `C_L=2\pi\ln\frac{L}{2\pi a}+2E_c` | ℏ²n/m | 390, 402, 405 | |
| `$L$` | box side; also the film size in `\ln(L/a)` | ξ | 383, 506, 517 | |
| `$e$`, `$t$`, `$T$` | energy per particle; time; field temperature | unstated; "time units"; ℏ²/(mξ²), k_B=1 | 541–548 | |
| `$n_s/n$`, `$J_T$`, `$J_L$` | superfluid fraction; transverse and longitudinal currents | | 549 | |
| `$N_v$` | number of vortices (all runs, both signs) | | 559–561 | |
| `$\tilde g$` | dimensionless coupling, = 1 | | 594, 653 | never defined |
| `$\tau$` | `\tau=\vert\rho(k_1)\vert/(\vert k_1\vert W)` | | 619, 678 | (ii) ch07 τ = lag; ch09 τ = time unit |
| `$m^2$` | wavevector shell index, 4…16 | | 614 | not defined (presumably the squared integer wavevector); unclear |
| `$\varepsilon$` | dielectric constant, `\varepsilon-1\propto\sum d^2` | | 628 | distinct from `\epsilon` |

**Lean and code notation (ch06)**

| symbol | meaning | line(s) | remarks |
|---|---|---|---|
| `u y : ℝ → ℝ` | stiffness⁻¹ and fugacity as functions of l | 240, 316 | |
| `hu`, `hy`, `hpos` | KTFlow: two-sided `HasDerivAt` and `0 < u l` for every real l. Ch06_KTForward: `HasDerivWithinAt … (Set.Ici 0)` and positivity for `0 ≤ l` only | 241–243, 317–319 | the "too generous" hypothesis is discussed at 288–308 |
| `f`, `H` | Lean definitions of f(u) and H(u,y) | 237–238 | |
| `h0`, `hH`, `hl`, `hne` | `u 0 < π / 2`; `f (π / 2) < H (u 0) (y 0)`; `0 ≤ l`; `H (u 0) (y 0) ≠ f (π / 2)` | 247–249, 330 | |
| theorem names | KTFlow: `kt_invariant`, `kt_trapped`, `kt_fugacity_bounded`, `u_monotone`, `kt_units` (in words only), `f_ge_H`. Ch06_KTForward: `kt_eternal_trivial`, `kt_escape`, `kt_escape_time`, `kt_dichotomy`, `kt_scalar`, `f_gt_fc`, `kt_stiffness_vanishes`, `u_monotoneOn` | 232–341 | |
| `E` | type of positions and wavevectors (MatchingScreening) | 351–357 | declaration not shown; `inner ℝ` implies a real inner-product space; otherwise unclear |
| `wave k r`, `rho k p m`, `I` | e^{ik·r}; charge density; complex unit | 351–354 | |
| `p m : Fin N → E`, `σ : Fin N ≃ Fin N`, `hk` | positions; pairing; premise that the absolute value of `inner ℝ k (p i - m i)` is ≤ 1 | 353–364 | |
| `norm_rho_le_matching`, `matching_lower_bound`, `norm_rho_le_matching_torus`, `rho_polarisation`; `VortexWinding` | vortex-position theorems; winding-rule module | 356, 363, 370–374, 552 | |
| `A_COEF`, `rtol`, `atol`, `max_steps`, `L`/`U`/`Y`, `lmax`, `dl`, `ustop`, `ystop` | Python: 4π³, tolerances, solver step cap, lists of l/u/y, loop variables | 417–444 | the list `L` holds l values, not the box side |

### C. Physical constants and material values quoted

| quantity | value as printed (units) | source the chapter gives | line | remarks |
|---|---|---|---|---|
| universal jump `8\pi k_B(m/h)^2` = `\rho_s(T_c^-)/T_c` | `\cnJump\times10^{-9}\ \mathrm{g\,cm^{-2}\,K^{-1}}` = 3.49×10⁻⁹ | "computed by `\texttt{figures/ch06\_constants.py}`" (l.136); formula from `\cite{NelsonKosterlitz1977}`, as quoted in the abstract of `\cite{BishopReppy1978}` | 129, 134, 653 | JSON `universal_jump_cgs_g_cm2_K` = 3.4913578770496592e-09 |
| same, SI | not printed | `ch06_constants.json` `universal_jump_SI_kg_m2_K` = 3.4913578770496594e-08 kg m⁻² K⁻¹ | — | 3.49×10⁻⁸ kg m⁻² K⁻¹ if App. D wants SI |
| m(⁴He) | `$m=4.002\,603\,254\,13$` atomic mass units | "the NIST value for `$^4$He`" | 132 | JSON `m_He4_kg` = 6.646479080869192e-27 kg (not printed); ch03 prints 4.002603254 u |
| k_B, h, ℏ | not printed | "the CODATA values of the constants shipped with SciPy" | 132 | JSON: 1.380649e-23 J/K, 6.62607015e-34 J s, 1.0545718176461565e-34 J s; SciPy 1.18.1 |
| jump in book units | `n_s\lambda_T^2=4` at `T_c^-`, `\to0` above | Nelson–Kosterlitz | 140, 143 | |
| critical values | `$K=2/\pi$`, `$\eta=1/4$`; fixed point `$(u,y)=(\pi/2,0)$` | derived | 176, 186, 216 | JSON `two_over_pi`, `pi_over_two`, `eta_at_jump` = 0.25 |
| RG coefficient | `4\pi^3` (and `2\pi^3` inside H) | Kosterlitz `\cite{Kosterlitz1974}`; normalisation-dependent | 203, 212, 238 | JSON 124.025…, 62.012… |
| `f(\pi/2)` | `$\pi-\pi\ln(\pi/2)=\cnFc$` = 1.723 | `ch06_constants.json` `f_at_pi_over_2` | 256 | `f''(\pi/2)=4/\pi` (671) |
| critical approach | `n_s\lambda_T^2(l)\simeq4+\frac{2}{l}`; Ex. 2: `l\,(n_s\lambda_T^2-4)=2-\tfrac23\,(\ln l)/l+O(1/l)` | derivation | 521, 673 | CVODE: 1.78, 1.96, 1.9993 at l = 10, 10², 10⁴ (525) |
| essential singularity and cusp | `\xi\sim\exp(b/\sqrt{T-T_c})`; asymptote `\pi^2/(4a)`; `K_R-2/\pi\simeq(4/\pi^2)\sqrt{\pi\epsilon/2}` | | 222, 508, 515, 528 | ratios 0.59, 0.95, 0.998; offset −3.07 (530–531) |
| `2\pi\ln2` | 4.355 (`\cnTwoPiLnTwo`) | ch06_constants.json | 405 | fitted constant differences 4.351 (window variants 4.368, 4.349) |
| Coulomb coupling of the field | `2\pi\hbar^2n_s/m`, `n_s=n` at T=0, "to within `$0.3\%$`" | `figures/ch06_loglaw.py`, `ch06_coulomb.py` | 405–408 | rms 0.043 / 0.033 and max 0.071 / 0.064 in ℏ²n/m (404); naive slopes 1.07 and 1.04 ×2π (406–407) |
| weak-coupling critical value | `$\ln(380/\tilde g)=\cnLnThreeEighty$` = 5.94 | Prokof'ev–Ruebenacker–Svistunov `\cite{Prokofev2001}` | 594 | |
| cutoff estimate (not used) | `$T_{\rm BKT}=0.811$`, `$n\lambda_T^2=7.75$` | "The programme's literature review" | 596 | explicitly "a hypothesis ..., not a test" |
| T_BKT(L=64) | 0.821; seeds 0.809–0.836; "±0.014" | `figures/ch06_pgpe_data.py` on `data/generated/pgpe/r2/` `II_*.json`; `ch06_pgpe_numbers.json` | 576–577, 661 | at the crossing: η = 0.307, n_s/n = 0.52 |
| T_BKT(L=32) | 0.893; seeds 0.877–0.912 | same | 578 | crossing slopes 32 and 13 (579); size shift 9% for the field vs 1% for the toy (582–583) |
| nλ_T² at the crossing | 7.65, "29 %" above ln 380 | = 2π/T_BKT(64) | 593–595 | |
| spin-wave product `\eta\,n_s\lambda_T^2` | 1.12–1.22 (L=64), 1.14–1.27 (L=32): "12 to 27%" excess | ch06_pgpe_numbers.json | 597–598, 659 | open item |
| round-1 T_BKT | ≈0.72, withdrawn | — | 600, 658 | |
| ladder table | e = 1.00…1.40 gives T = 0.571…0.966, n_s/n = 0.809…0.255, n_sλ_T² = 8.90…1.66, η = 0.126…0.660, ηn_sλ_T² = 1.09–1.34, N_v = 19…212 | `figures/ch06_pgpe_numbers.json` (caption) | 563–571 | |
| figure temperatures | T = 0.57, 0.82, 0.96 (= 0.69, 1.00, 1.16 × T_BKT(64) = 0.82) | — | 586–587 | |
| pair sizes | 0.6ξ, 1.1ξ, 1.6ξ; 126 vortices at T_BKT | `ch06_field_info.json` | 604–605 | |
| toy KT flow | `y_0=0.03`; `K_{0c}=0.7734` (`u_{0c}=1.293`); K_R = 0.715 at K₀ = 0.8; K_R = 0.654 (n_sλ_T² = 4.11) | `figures/ch06_flow_compute.py` | 505, 511–514 | finite-box shifts 6.1 / 3.8 / 2.6 / 1.4% at L/a = 16 / 64 / 256 / 4096 (518) |
| vortex-position certificates | τ = 0.04–1.00 (fields) and 0.04–0.11 (L=192); remainder 0.12; bound 0.55; plateau 0.79–0.95; stale file ≈0.009; coherence 0.06–0.28 | `ch06_certificates.py`; `primary_C4.json`; `PGPE_DIELECTRIC_RESULTS.md` | 619–633 | |
| Bishop–Reppy | **no numbers quoted**; only the abstract's qualitative agreement | `\cite{BishopReppy1978}` | 123–129, 150, 652 | "we re-analyse no film data" |
| Godfrin, 2D ³He | no numbers | `\cite{Godfrin2012}`, `\cite{Godfrin2012b}` | 153–155 | |
| CVODE environment probe | y'=−y: 237 022 vs 511 right-hand-side calls; errors 6.4×10⁻⁴ vs 2.0×10⁻⁷; KT links 12 898 vs 64 and 353 469 vs 354 | `ch06_cvode_probe.py` and its two JSON files | 465–468 | ch07 l.154 repeats 237 022 / 511 as literals |
| drift of the invariant | Adams 2.3×10⁻⁵ → 1.9×10⁻¹¹; BDF 6.0×10⁻⁶ → 6.3×10⁻¹⁰; negative control 9.5×10⁻⁴–0.25 | `ch06_flow_compute.log` | 450–458, 491–493 | |

### D. Glossary terms introduced in this chapter

| term | one-line definition (chapter's sense) | line |
|---|---|---|
| universal jump (Nelson–Kosterlitz) | the superfluid density jumps at T_c by an amount fixed by constants: `\rho_s(T_c^-)=8\pi k_B(m/h)^2T_c`, i.e. `n_s\lambda_T^2` falls from 4 to 0; the line `n_s\lambda_T^2=4` is the "Nelson--Kosterlitz level" | 126–129, 140, 220, 575 |
| thermal wavelength | `\lambda_T^2=2\pi\hbar^2/(mk_BT)`, the unit in which n_s is measured | 138 |
| phase stiffness J | coefficient in the phase energy `\tfrac{J}{2}\int(\nabla\theta)^2`, `J=\hbar^2n_s/m` | 165–166 |
| dimensionless stiffness K | `J/k_BT=n_s\lambda_T^2/2\pi`, "the variable of this chapter" | 170, 174 |
| quasi-long-range order | no long-range order, but a stiff phase (n_s≠0) with power-law g₁ | 173–174 |
| spin-wave relation | `\eta\,n_s\lambda_T^2=1`; the ledger and ch10 call it the Josephson relation | 175 |
| Kosterlitz–Thouless free-energy argument | a free vortex costs `(\pi J-2k_BT)\ln(R/a)+E_c`, which changes sign at K=2/π | 178–187 |
| vortex pair / Coulomb gas / screening | opposite-sign pairs are dipoles of the 2D Coulomb gas; they polarise and lower the long-distance stiffness, `J\to J_R` | 190–199 |
| vortex fugacity | Boltzmann weight of a core, `y\sim e^{-E_c/k_BT}`, followed with scale | 200–201 |
| Kosterlitz renormalisation-group flow | leading-order flow of K (or u = 1/K) and y as pairs between a and ae^l are integrated out; y is relevant for K<2/π and irrelevant for K>2/π | 199–212 |
| line of fixed points / renormalised stiffness | y=0 is a line of fixed points, stable for u<π/2; the measured stiffness is `K_R=1/u_*` | 215–218 |
| separatrix | the boundary flow entering (π/2, 0) between superfluid and normal flows; exactly the level set H = f(π/2), not the textbook line | 219, 339 |
| essential singularity | the correlation length (scale where y~1) diverges as `\exp(b/\sqrt{T-T_c})` | 221–222 |
| exact invariant H | `H(u,y)=2u-\pi\ln u-2\pi^3y^2` is constant along solutions; its level sets are the flow lines | 254–256 |
| trapping / escape / dichotomy | for u(0)<π/2: stays below π/2 forever if H₀>f(π/2); crosses within RG time l₁ if H₀<f(π/2) | 261, 335–339 |
| vortex charge density and matching bound | `\rho(k)`; `\vert\rho(k)\vert/\vert k\vert` ≤ the cost of any pairing; "a certificate, not a detector" | 347, 370–373, 621 |
| polarisation form | `\rho(k)=i\,k\cdot P(k)+R`: bound charge is `i\,k\cdot P` up to second order | 374–377 |
| torus point-vortex law | `\Delta E(d)=\pi H_{\rm WM}(d)+\frac{2\pi^2d^2}{L^2}+C_L` for an imprinted pair on the periodic box | 385–392 |
| heating ladder / equilibrium admission test | equilibrated cold states raised by random phonons to e = 1.00…1.40; only runs whose current fluctuations are compatible with equilibrium are admitted | 541–543, 554 |
| LL-15 | the programme's rule: name the property a result depends on and check that the other system has it before using an analogy | 159–160 |

**Used but not defined here:**
- Mermin–Wagner and Hohenberg theorems (173); Berezinskii's analysis (187).
- The projected Gross–Pitaevskii equation is named but not written (382, 538; ch07 l.189 writes it). The healing length is given only by value.
- Equipartition thermometer and current correlators are given only operationally (548–549).
- Vortex imprint and the winding rule / `VortexWinding` (383, 552; both in ch03).
- Optimal transport, minimum image, reciprocal lattice (372–374).
- The AHNS dynamic theory (128).
- Fermi liquid, Fermi wave number, roton-like minimum (154–158).
- CVODE, Adams, BDF, rtol, "chain of solves".
- Helicity modulus (692), quench (600), pre-registration amendment R2-A4 (544).

## ch07 — Friction, Diffusion and the Dissipative Vortex
`\chapter` is at l.1.

### A. Units and conventions
- l.28: "Work in units `$\hbar=m=1$`, so that the circulation quantum is `$\kappa=2\pi$`, in the frame where the normal component is at rest."
- l.53: "an Einstein relation `$\eta=\alpha T/(2\pi\rho)$` (`$k_B=1$`)".
- l.60–61: Mehdi et al. keep the constants, "`$\eta=\alpha k_BT/(2\pi\hbar\rho_0)$` (`$\rho_0$` the two-dimensional number density)".
- l.38–39: the point-vortex energy is dimensionless with its own normalisation: "`$H=-\sum_{i<j}q_iq_j\ln r_{ij}^2$`" with "`$\mathbf v_{s,i}=-\tfrac12 q_i\,\hat{\mathbf z}\times\nabla_iH$`". On the torus, `\ln r^2` is replaced by the Weiss–McWilliams Green function.
- l.99: "the superfluid velocity at either vortex is `$(d_y,-d_x)/\texttt{r2}$`", i.e. speed 1/d.
- l.189–190: "`$i\partial_t\psi=\mathcal P[-\tfrac12\nabla^2\psi+g|\psi|^2\psi]$` on a periodic square box of side `$L=64$`, with `$\hbar=m=g=1$` and mean density `$n=1$` (healing length `$\xi=1$`, sound speed `$c=1$`), `$128\times128$` grid points and a sharp cutoff `$|k|\le k_c=\pi$`, half the grid wavenumber".
  - This implies ξ=ℏ/√(mgn) (no factor 2), a grid spacing of 0.5ξ, and a velocity unit of c.
  - The equation as written has no −μψ term.
- l.190: "The energy is conserved (to `$10^{-7}$`--`$10^{-6}$` over every run of the campaign); nothing is damped and no noise is added."
- l.190–191: "The temperature of a base state comes from an equipartition thermometer and its normal fraction from the current correlators~\cite{Callens2026a}".
- l.191: "`$e=0.60$` state: `$T=0.115$`, that is `$T/T_{\rm BKT}=0.14$` with `$T_{\rm BKT}(L{=}64)=0.821$` from a heating ladder". The units of T and e are not restated; ch06 l.548 gives ℏ²/(mξ²) with k_B=1.
- l.335: "In a classical field every mode carries the energy `$T$`, so `$n_k=T/\varepsilon_k$`".
- l.339–340: "the temperature of the classical field is a parameter of the model, which maps onto a physical temperature only through the cutoff".
- l.336: "`$\varepsilon_k^2=k^2+k^4/4$`", the Bogoliubov dispersion with ℏ=m=gn=1.
- l.292: "a finite set of modes `$k\in K$` (3208 of them at `$k_c=\pi$` in this box)". l.490: "the `$3208$` modes of the disk `$|k|\le\pi$`, `$L=64$`".
- Cutoff scan: l.320 "cutoffs (`$k_c=2\pi/3$` and `$2\pi$`, same instrument, ...)"; l.324 "`$k_c\xi=2.1,\ 3.1,\ 6.3$`". The grid used for these other cutoffs is not stated.
- l.212: "`\texttt{qf\_pgpe.Pgpe(128, 64.0)}`" (grid points per side, L).
- l.195: tracks are "recorded every time unit"; continuity means "nearest detection within `$3\xi$`".
- l.242: "`$\mathrm{Im}(\psi^*\nabla\psi)/|\psi|^2$` coarse-grained over `$3\xi$`".
- Time: the unit is never defined. Values in time units: runs of 1500, 2000 and 4000; lag 10 (250); lags 20–400 (395).
- Densities appear as fractions `\rho_n/\rho` (192). With m=n=1, number density and mass density coincide, but the chapter does not say so.
- KT coupling, l.361: "`$p\propto|\mathbf d|^{-K}$` with `$K=2\pi\rho_s/T$`". This K equals ch06's `n_s\lambda_T^2`, not ch06's K.
- Frames:
  - l.352: "field momentum `$2\pi nd$`, which in a periodic box is a mean superfluid velocity `$u=2\pi d/L^2$`".
  - Box frame and fluid frame are distinguished at l.352–353.
  - l.348: the α′ values are "In the frame of the simulation box".
- l.473: "(one box, `$mg=1$`, cutoffs `$2\pi/3$`, `$\pi$`, `$2\pi$`, `$T<0.45\,T_{\rm BKT}$`)". "mg=1" is not defined; it may be ch06's `\tilde g`, which is not defined there either. Unclear.
- l.75: "Lean~4.34.0-rc2, the pinned Mathlib".

### B. Symbols

These do not occur in ch07 (checked by grep): `\mu`, `\beta`, `\Gamma`, `\ell`, `\epsilon` (only `\varepsilon` is used), `T_{\rm KT}`.

| symbol (LaTeX as in source) | meaning in this chapter | units / convention | line(s) | remarks |
|---|---|---|---|---|
| `$\alpha$` | (longitudinal) mutual-friction coefficient, the dissipative term | dimensionless | 8, 16, 30, 35 | (ii) not the dispersion coefficients `\alpha_2`…`\alpha_6` of ch01/02/04/05/10; the code calls it `a` (158) |
| `$\alpha'$`, `$\hat\alpha'$`, `$1-\alpha'$` | transverse (non-dissipative) coefficient; its estimate; speed factor | dimensionless | 16, 30, 35–36, 51, 348 | the code calls it `ap` |
| `$\alpha_{\rm energy}$`, `$\alpha_{\rm regression}$`, `$\alpha_E$`, `$\alpha_R$`, `$\alpha_{\rm apparent}$`, `$\alpha_{d_0=8}/\alpha_{d_0=12}$` | outputs of the two estimators; single-run values; apparent α at T=0; pair-size ratio | | 93, 252, 257, 263, 232, 271 | |
| `$\eta$` | vortex diffusion constant, `\langle\vert\Delta\mathbf r\vert^2\rangle=4\eta t` | length²/time | 17, 52, 60 | (ii) in ch06, η is the g₁ exponent |
| `$\kappa$` | circulation quantum = 2π (ℏ=m=1) | | 28, 294, 325 | consistent with ch03 κ=h/m |
| `$q$`, `$q_i$` | vortex charge ±1 | | 28 | |
| `$\mathbf v_s$`, `$\mathbf v_{s,i}$` | superfluid velocity induced at vortex i by the other vortices | velocity, c=1 | 29, 39 | |
| `$\mathbf r_i$`, `$r_{ij}$`, `$\hat{\mathbf z}$` | position; distance; unit normal | | 32, 38 | |
| `$H$` | point-vortex energy `-\sum_{i<j}q_iq_j\ln r_{ij}^2`; H(t) along tracks | dimensionless | 38, 256 | (ii) in ch06, H is the KT invariant |
| `$A$` | skew part, `\langle \mathbf v,A\mathbf v\rangle=0` | | 42–46 | (ii) ch04 A = coefficient of T³ |
| `$\gamma$` | (a) gradient-flow coefficient in `energy_dissipation`, γ = α/2 | | 83–90 | (i) (b) local exponent of `\langle\vert e\vert^2\rangle-c_0` against lag (388, 395) |
| `$\mathbf p$`, `$\mathbf m$`; `$\mathbf p_1$`, `$\mathbf p_2$` | + and − vortex of a dipole; the two vortices of a same-sign pair | | 99, 131 | `\mathbf m` clashes with the mass m |
| `$\mathbf d$`, `$d$`, `$d_0$`, `$\mathbf d_0$`, `\texttt{r2}` | separation vector, its length, initial value; `\vert\mathbf d\vert^2` | ξ | 99, 107, 123, 131 | |
| `$s$` | centre displacement, `s=(1-\alpha')(d_0-d)/2\alpha` | | 180 | |
| `$\psi$`, `$\mathcal P$`, `$g$`, `$n$` | field, projector, coupling, mean density | ℏ=m=g=n=1 | 189 | |
| `$\xi$`, `$c$` | healing length = 1; sound speed = 1 | | 189 | (i) c also means the coefficient `\alpha/(\rho_n/\rho)` (258, 325, 328), the Lean `c` in `wind_stall` (412), and the Fourier amplitudes in code (200, 212); see also `c_0`, `c_g` |
| `$k$`, `$k_c$` | wavevector; sharp cutoff | 1/ξ | 190, 324 | |
| `$e$` | energy per particle of the base state (e=0.60) | not stated | 191 | (i) also the regression residual in `\langle\vert e\vert^2\rangle` (395, 399) |
| `$T$`, `$T_{\rm BKT}$`, `$T/T_{\rm BKT}$`, `$T/T_c$` | field temperature; ch06's L=64 crossing (0.821); generic quantum-gas `T_c` | | 191, 340 | (i) the Lean `T` in `dipole_sq_law` / `corot_sq_law` is a time horizon, `t ∈ Icc 0 T` (111, 114, 136) |
| `$\rho$`, `$\rho_n$`, `$\rho_s$`, `$\rho_n/\rho$`, `$\rho_0$` | total, normal and superfluid densities; normal fraction; Mehdi's 2D number density | m=1, n=1 | 58, 61, 192, 293, 361 | the Einstein relation is written with ρ (53, 381) while K uses ρ_s (361) |
| `$c_0$` | zero-lag offset of the residuals (core jitter) | length² | 247, 395, 399 | |
| `$I(t)$` | `\int2\sum_i\vert\mathbf v_{s,i}\vert^2dt` | | 256 | |
| `$S$` | appears in "`\int2S\,dt`" | | 465 | **not defined**; by comparison with I(t) it seems to be `\sum_i\vert\mathbf v_{s,i}\vert^2`, but this is unclear |
| `$K$` | (a) finite set of bath modes, `k\in K` | | 292; Lean 301 | (i) (b) stiffness exponent `K=2\pi\rho_s/T` (361, 381–382, 388, 395) |
| `$n_k$`, `$n_{\rm RJ}$`, `$n_{\rm Bose}$` | mode occupation; equipartition `T/\varepsilon_k`; Bose `1/(e^{\varepsilon_k/T}-1)` | | 292, 335–336, 490 | |
| `$\sigma_{\rm tr}(k)$` | transport cross-section of the vortex, "(a length, in two dimensions)" | ξ | 292 | (ii) in ch06, σ is a pairing |
| `$F$`, `$D$`, `$v$` | drag `F=-Dv`; drag coefficient `D=\tfrac12\int\frac{d^2k}{(2\pi)^2}(-\partial n/\partial\varepsilon)\,k^2\,c_g\sigma_{\rm tr}`; vortex speed relative to the gas | | 292–293 | (i) D also means the separation diffusion `D=2\eta` (360, Lean 368–376); (ii) ch04 D = coefficient of T⁶ |
| `$c_g$` | group velocity `d\varepsilon/dk` | | 293 | |
| `$\varepsilon$`, `$\varepsilon(k)$`, `$\varepsilon_k$` | excitation energy | energy | 67, 293, 335–336 | (i) also a small ε in the fence argument (421) |
| `$w_k$`, `$f_k$` | nonnegative weights; drag factors `c_g\sigma_{\rm tr}` | | 294 | (i) w also means `2\pi\rho_s/(\rho_nL^2)` (424) |
| `$u$` | (a) mean superfluid velocity of a single pair, `2\pi d/L^2` | | 352 | (i) (b) phonon drift `2\pi\rho_s(d_0-d)/(\rho_nL^2)` (408) |
| `$\mathbf b$` | drift on the separation, `-2\alpha\,\mathbf d/\vert\mathbf d\vert^2` | | 360 | (i) b is also the upper root / stall point (412–437) |
| `$\mathbf J$`, `$p$` | probability current `\mathbf bp-D\nabla p`; pair distribution `p\propto\vert\mathbf d\vert^{-K}` | | 360–361 | p clashes with the vortex position `\mathbf p` |
| `$R_E$` | `\eta K/\alpha`; equals 1 exactly when detailed balance holds at stiffness K | | 382 | |
| `$\tau$` | lag | time | 399 | (ii) in ch06, τ is a ratio |
| `$a_k$` | amplitudes of a finite cosine sum | | 403 | |
| `$a$`, `$b$`, `$w$`, `$\lambda$` | roots of the wind equation (`a+b=d_0`, `ab=1/w`); `w=2\pi\rho_s/(\rho_nL^2)`; linearised rate `2\alpha w(b-a)/b` | ξ; 1/ξ²; 1/time | 424, 435 | (ii) ch06 uses λ_T |
| `$L$` | box side (64, 96) | ξ | 189, 449 | |
| `$\chi^2$`, σ (as in "18σ") | statistics | | 324–330, 349 | |
| f in `$1/f^{0.5}$` | frequency | | 452 | (i) differs from `f_k` |
| labels W, W2, FL2, FL-A1, E2, G0 | pre-registered hypotheses, controls, rules and gates | | 408, 451, 320, 329, 395, 458 | |

**Lean-only and code notation (ch07)**

| symbol | meaning | line(s) | remarks |
|---|---|---|---|
| `X`, `H`, `gradH`, `hH`, `A`, `hA`, `γ`, `r`, `hr` | `energy_dissipation`: inner-product space, energy, its gradient, skew map, damping, path; `hr` = path differentiable for all t | 81–85 | `hr` is the hypothesis behind the diffusion bias (97, 464) |
| `px py mx my`, `α α'`, `r2`, `hpx hpy hmx hmy hpos`, `T`, `cx' cy'` | dipole coordinates; coefficients; squared separation; model hypotheses; time horizon; centre velocity | 104–118 | |
| `x1 y1 x2 y2` | same-sign pair (`corot_sq_law`) | 136–137 | |
| `K : Finset ι`, `w f : ι → ℝ`, `ρs κ ρ`, `hρn hρ hw hpos`, `m M` | FrictionKinetic: mode set, weights, drag factors, densities; `m`, `M` are lower and upper bounds of f | 298–311 | another m |
| `p (K x y)`, `Jx`, `Jy`, `zero_flux_iff (α D K)`, `einstein_vortex (α η ρ T)` | EinsteinRelation: `\vert d\vert^{-K}` and the current; `einstein_vortex` substitutes D=2η and `K = 2 * π * ρ / T` | 366–376 | uses ρ, not ρ_s |
| `wind_stall {a b c}`, `d`, `hd`, `h0` | stall of `-c*(d-a)*(d-b)/d`; c corresponds to 2αw (by comparison with 424) | 412–414 | |
| `wind_stall_at_b {α w d0}`, `h4`, `stallPoint w d0` | `stallPoint w d0` = `[d_0+\sqrt{d_0^2-4/w}]/2` | 428–432 | |
| theorem names | DissipativeVortexDynamics: `energy_dissipation`, `dissipation_indep_of_skew`, `dipole_sq_law`, `centre_velocity_identity`, `r2_hasDerivAt`, `dipole_lifetime_bound`, `wind_stall`. Ch07_DissipativePairs: `corot_sq_law`, `wind_stall_at_b`, `wind_no_zero`. FrictionKinetic: `coeff_eq_weighted_mean`, `weighted_mean_mem_Icc`, `rayleigh_jeans_mean`. EinsteinRelation: `zero_flux_iff`, `einstein_vortex`. QuasiPeriodicBound: `msd_bound`, `not_qp_of_msd_large`. Also `VortexWinding` (195) | 82–449 | `\Lthm{DissipativePairs}{…}` at l.149 and l.449, but the module is `Ch07_DissipativePairs` (130, 134, 426) |
| code: `a`, `ap`, `dx`, `dy`, `r2`, `s`, `c`, `E0`, `pos`, `q`, `dp`, `dq`, `last`, `cur`, `a.r_track` | `a`/`ap` = α/α′ in `ch07_dipole.py`; but `a` is the options object in `ch07_pairrun.py`; `c` = projected Fourier amplitudes; `s` = solver or engine | 158–212 | |

### C. Physical constants and material values quoted

| quantity | value as printed (units) | source the chapter gives | line | remarks |
|---|---|---|---|---|
| α in an oblate sodium BEC | "between `$0.01$` and `$0.03$` over the `$200$`--`$450$`~nK explored" | `\cite{Moon2015}` | 8–9 | read through a dissipative point-vortex model |
| α in a rubidium BEC, hard-walled trap | `$\alpha=3.3(1)\times10^{-3}$`; random wandering "about a hundred times larger" than the theory | `\cite{Neely2024}` | 10–11, 401 | |
| ⁴He excitation spectrum | Phys. Rev. B 103, 104516 (2021), IN5 at ILL; no numbers | `\cite{Godfrin2021}` | 65–67 | |
| transverse-force theories | Thouless–Ao–Niu α′=0; Iordanskii `$\alpha'=\rho_n/\rho$`, giving `$+2.7\%$`, `$+5.3\%$`, `$+9.4\%$` at the three bases | `\cite{ThoulessAoNiu1996}`, `\cite{Iordanskii1964}`, `\cite{Sonin1997}` | 56–58, 354 | the Iordanskii values are excluded |
| diffusion from SPGPE | `$\eta=\alpha k_BT/(2\pi\hbar\rho_0)$` | `\cite{Mehdi2023}` | 60–61 | |
| Einstein relation in the model | `$\eta=\alpha T/(2\pi\rho)$` (k_B=1); `$DK=2\alpha$` | Lean `EinsteinRelation` | 53, 381 | |
| circulation quantum | `$\kappa=2\pi$` | — | 28 | |
| Shukla–Brachet–Pandit | window `$[0.004,0.045]$` (interpolation); measured value "a factor two below" at 0.14 T_BKT | `\cite{Shukla2014}` | 219, 285 | their T_BKT "is an estimate" |
| T_BKT(L=64) | `$0.821$` "from a heating ladder" | ch06, not cross-referenced | 191 | a literal, equal to ch06's `\cnTbktSixtyfour` |
| base state | `$e=0.60$`: `$T=0.115$`, `$T/T_{\rm BKT}=0.14$`, `$\rho_n/\rho=0.027$` | `\cite{Callens2026a}` | 191–192 | |
| Table ch07:tab-alpha | T = 0, 0.115, 0.220, 0.353†; T/T_BKT = 0, 0.14, 0.27, 0.43; ρ_n/ρ = 0, 0.027, 0.053, 0.095. α (energy) = 4.1×10⁻⁴ (floor), 0.0062±0.0004, 0.0138±0.0023, 0.0205±0.0138. α (regression) = 2.0×10⁻⁴, 0.0064±0.0004, 0.0156±0.0014, 0.0242±0.0065 | archived campaign re-analysed with the Rust estimators | 273–276 | L=64, k_c=π |
| headline friction | `$\alpha=0.0062(4)$`, `$0.014(2)$`, `$0.02(1)$` | energy estimator, "low by 5–20%" | 20, 473 | regression values: 0.0064, 0.0156, 0.0242 (466) |
| **α/T slope** | `$\alpha/T=0.0540\pm0.0026$` (energy, χ²=1.28 for 5 dof) and `$0.0598\pm0.0023$` (regression, χ²=5.15); printed as "`$\alpha=0.054\,T$`" and "`$0.060\,T$`" | six arms of the cutoff scan; `\cite{Callens2026b}` | 258, 328, 466, 473 | tested only for T = 0.10–0.22 (331) |
| α/(ρ_n/ρ) | 0.23, 0.26, 0.22 at k_c=π; 0.31±0.03, 0.232±0.014, 0.102±0.011 at k_cξ = 2.1, 3.1, 6.3 | — | 286, 319, 324 | FL2 fails (spread 0.98 vs 0.2); Born χ²=204/2; common c χ²=76/5 |
| implied cross-section | "≈1.4ξ" as "the geometric size of the core" (withdrawn); 1.9ξ, 1.4ξ, 0.59ξ | `\cite{Callens2026a}`; ledger | 319, 325, 478 | |
| Born-law ratio; FL-A1 | 0.67 : 1 : 2. Prediction 0.0094±0.0010 at k_c=2π, T=0.173 (vs 0.0077); measured 0.0096±0.0018 | — | 320, 329–330 | |
| α′ | box frame −0.0100±0.0015, −0.0154±0.0029, −0.0093±0.0106 (+0.0014 at T=0), slope −0.31±0.05. Corrected −0.0060±0.0015, −0.0112±0.0031, −0.0055±0.0106. Cutoff scan −0.017, −0.031 (k_c=2π/3), −0.005, −0.004 (k_c=2π). 1−α′ = 1.007±0.006 (fresh run), 1.0100±0.0015 (campaign) | CLAIM-082; `qf_pgpe.analyse_tracks` | 247, 252, 349, 354–356 | |
| pair speed at T=0; Jones–Roberts | box-frame ratio 1.05 (d=6) to 1.46 (d=16), where the programme's note says 1.06 and 1.49. Compressibility correction +3–4% (d=3–4), +1% (d=6), +0.4% (d≥8) | `pair_speed_T0.json`; CLAIM-082 | 352–354 | |
| table of random kicks | γ = 0.71, 0.82, 1.28; η = (3.7±0.7)×10⁻⁴, (10.8±3.5)×10⁻⁴, (18.3±3.6)×10⁻⁴; K = 53.2, 27.1, 16.1; R_E = 3.2±0.6, 2.1±0.7, 1.4±0.3 | — | 390–392, 400 | only T/T_BKT = 0.27 is quoted (rule E2) |
| classical vs Bose bath | 3208 modes. At k=π: ε = 5.85 = 51T, occupation 0.020 vs 8×10⁻²³. Ratio 1.7×10³ at k=1; agreement within ×3 only for k≲0.2 (ε≈1.75T). 0.25% of the Landau sum from ε<T, 2.2% from ε<3T. Normal fraction 0.0227 vs 0.00075. The equipartition sum is 64–84% of the measured value; the Bose sum is 6–48× smaller | `figures/ch07_bath.py` | 292, 336–339 | |
| wind hypothesis | w = 0.055, wd₀² = 7.9, b = 10.2, a = 1.8, λ = 5.6×10⁻⁴ (about 1800 time units). L=96: ρ_n/ρ = 0.029, wd₀² = 3.2, 44.3 > 36 | — | 435–436, 449 | |
| synthetic gate G0 | α=0.02, α′=0.10, η=2×10⁻³; energy-estimator bias 8.5, 18.5, 22% at η = 5×10⁻⁴, 10⁻³, 2×10⁻³ | `qf-pgpe` example `g0_scan`; CLAIM-098 | 458, 461 | |
| first gate and T=0 control | fits 0.0093, 0.0062, 0.0028, 0.0022 (median 0.0045); apparent α at T=0 = 0.0100; corrected `\vert\alpha_{\rm apparent}\vert<10^{-5}`; replacement gate α_energy = 0.00705±0.00012 in [0.0028, 0.0112] | CLAIM-075 | 219, 229–234 | |
| CVODE probe | 237 022 vs 511 right-hand-side evaluations; commit 5db8041 | — | 154 | the same numbers are macros in ch06 |

### D. Glossary terms introduced in this chapter

| term | one-line definition (chapter's sense) | line |
|---|---|---|
| mutual friction | momentum exchange between a vortex and the gas of thermal excitations (the normal component) | 15 |
| dissipative point vortex (model) | `\dot{\mathbf r}_i=(1-\alpha')\mathbf v_{s,i}-\alpha q_i\hat{\mathbf z}\times\mathbf v_{s,i}`, in the normal-fluid frame (HVBK, weakly damped) | 28–36 |
| friction coefficient α | coefficient of the term perpendicular to v_s that carries energy from the vortices to the gas | 35, 51 |
| transverse coefficient α′ | rescales the speed with which a vortex follows the superfluid; dissipates nothing | 35–36, 51 |
| vortex diffusion (η) | random kicks with `\langle\vert\Delta\mathbf r\vert^2\rangle=4\eta t` | 52, 60 |
| Einstein relation | `\eta=\alpha T/(2\pi\rho)`; in the model, equivalent to zero probability current for the pair gas `\vert\mathbf d\vert^{-K}` (DK = 2α) | 52–53, 381 |
| skew part / gradient flow | `\dot{\mathbf r}=A(\nabla H)-\tfrac{\alpha}{2}\nabla H`: A moves vortices along level sets of H, the gradient part moves them down H | 42–46 |
| Magnus force | the total non-dissipative transverse force, proportional to the superfluid density (Thouless–Ao–Niu: α′=0) | 56–57 |
| Iordanskii force | transverse force from scattering of thermal excitations, registered as `\alpha'=\rho_n/\rho` | 57–58 |
| energy estimator | `\alpha_{\rm energy}=-\Delta H/(2\int\sum_i\vert\mathbf v_{s,i}\vert^2dt)`, from tracked positions only and blind to α′ | 92–97 |
| regression estimator | displacements over a lag of 10 regressed on `\int\mathbf v_s` and `-q\int\hat{\mathbf z}\times\mathbf v_s`; the coefficients are 1−α′ and α, and the residual mean square gives η | 250–251 |
| dipole square law / centre identity | `\vert\mathbf d\vert^2=\vert\mathbf d_0\vert^2-4\alpha t` whatever α′ (a same-sign pair gives +4αt); the centre moves at `(1-\alpha')/\vert\mathbf d\vert` whatever α | 123–125, 132 |
| known-answer gate / T=0 control | testing the instrument where the answer is known; at T=0 a pair must not shrink | 218, 235 |
| imprint | Jacobi-theta phase made single-valued by a uniform gradient, times the Bernoulli amplitude `[1+\vert\mathbf v\vert^2/2]^{-1/2}` | 194 |
| zero-impulse geometry | two antiparallel pairs at x = L/4 and 3L/4: zero net charge, dipole moment and impulse | 196, 452 |
| kinetic drag model / transport cross-section / Landau normal density | `F=-Dv` with D the k²c_gσ_tr-weighted bath integral; ρ_n is the same integral without c_gσ_tr; α=D/(ρ_sκ), so α/(ρ_n/ρ) is a bath-weighted mean of c_gσ_tr | 292–294, 316–317 |
| temperature law | α∝T, independent of the cutoff (α/T = 0.054 energy, 0.060 regression); a law of this model only | 328–331, 340 |
| equipartition vs Bose occupation | `n_k=T/\varepsilon_k` in the classical field vs `1/(e^{\varepsilon_k/T}-1)`; the field's normal density lives in modes a quantum gas would not populate | 335–339 |
| Jones–Roberts correction | the speed excess of a finite compressible pair (a solitary wave) over the point-vortex speed | 353–354 |
| R_E | `\eta K/\alpha`; equals 1 iff the pair gas can be in equilibrium at stiffness K | 382 |
| hypothesis W / phonon wind / stall point | the impulse of a shrinking pair drives the phonons at u, reducing friction: `\dot d=-2\alpha\,(1/d-u)`; the pair stalls at root b | 408, 424, 432 |
| diffusion bias of the energy estimator | for η>0 the energy estimator reads 8.5–22% low, because its identity assumes a differentiable path (`hr`) | 461–465 |

**Used but not defined here:**
- Landau's two-fluid description and the normal component (14, cited); the HVBK equations (30).
- Stochastic projected Gross–Pitaevskii theory (61).
- The Weiss–McWilliams periodic Green function (39); the Jacobi theta function (194).
- The plaquette winding rule (195, ch03); the equipartition thermometer and current correlators (191).
- T_BKT and the heating ladder (191, from ch06).
- Block jackknife (251); χ² (324).
- The Born law of long-wavelength phonon scattering (320; only its k_c scaling is given).
- Rayleigh–Jeans bath (316); Bogoliubov quasiparticles (336; dispersion only); solitary wave (353).
- Local exponent / sub-diffusion and regular island (395, 403; given only operationally); the 1/f^{0.5} spectrum (452).
- Metastable counterflow in the Fourier-truncated GP equation (439).
- CVODE, BDF, Adams.
- The programme labels FL2, FL-A1, W2, E2, G0 and CLAIM-nnn.

## E. Cross-chapter notes

1. **K is the biggest conflict.**
   - ch06 defines `K\equiv J/k_BT=n_s\lambda_T^2/2\pi`, which is 2/π at the jump (l.170, 176).
   - ch07 defines `K=2\pi\rho_s/T` (l.361, 395). That is 2π × ch06's K, i.e. ch06's `n_s\lambda_T^2`, which is 4 at the jump. The table values 53.2, 27.1, 16.1 check out as 2π(1−ρ_n/ρ)/T.
   - ch06 l.196 has the same pair weight, `(d/a)^{-2\pi K}=(d/a)^{-n_s\lambda_T^2}`, which ch07 writes as `\vert\mathbf d\vert^{-K}`.
   - ch07 also uses K for the set of bath modes (l.292, Lean l.301).
   - ch04 l.25 uses K for the coefficient of T⁸ in `C_V=A\,T^3+C\,T^5+D\,T^6+E\,T^7+K\,T^8+L\,T^9`; ch06 uses K for kelvin (l.134, 653).
   - Appendix D needs distinct symbols here, or explicit per-chapter entries.

2. **η has four meanings.** ch06: exponent of g₁ (1/4 at the jump). ch07 and ch10 (l.49–52): vortex diffusion constant. ch04 l.86–88: coefficient of u⁷ in the inverse dispersion series. ch05 l.321: noise amplitude 10⁻⁶.

3. **ξ (healing length).** ch06 l.383 and ch07 l.189 both get ξ=1 from ℏ=m=1, gn=1, i.e. ξ=ℏ/√(mgn) with no factor 2. This matches ch03 l.41, ch05 l.225 ("ξ=ℏ/mc, the convention of the solver") and ch01 l.186. ch09 l.25 uses ξ=ℏ/√(mμ) and τ=ℏ/μ (Kwon–Shin); this is equivalent only if μ=gn. No chapter uses ℏ/√(2mgn). However, ch06 also uses ξ for the KT correlation length (l.222, 508, 529), and ch10 l.49–52 uses a bold ξ_i for unit white noise.

4. **Time, velocity and temperature units of the classical field.**
   - Neither ch06 nor ch07 defines the time unit. ch03 l.41 and ch01 l.186 give ξ/c (= ℏ/(gn)).
   - Neither states the velocity unit (c=1 per ch07 l.189).
   - The temperature unit is given only in ch06 l.548: ℏ²/(mξ²) with k_B=1. ch07 relies on it and adds that T is "a parameter of the model" (l.340).
   - ch06 never gives the cutoff of its ladder, yet ch07 normalises its k_c=π temperatures by ch06's 0.821.
   - ch07 l.473 states "T<0.45 T_BKT" across cutoffs 2π/3 and 2π, but gives no T_BKT for those cutoffs.

5. **D.** In ch07, D is both the drag coefficient (l.292–294) and the separation diffusion D=2η (l.360, Lean). In ch04 (and ch01 l.31/82), D is the coefficient of T⁶. ch06 does not use D.

6. **α.** ch07's α and α′ (friction; ch10 l.49, 134–135 agree) are unrelated to the dispersion coefficients `\alpha_2`…`\alpha_6` (`\alpha_1=0`, units Å^n) of ch01/02/04/05/10, to `\alpha_2^{\rm Bog}=1/(8m^2c^2)` (ch05 l.244), and to the Bogoliubov amplitude `\alpha_k` (ch05 l.324).

7. **γ.** ch07 has two meanings: Lean damping γ=α/2 (l.83–90) and the local exponent (l.388). ch05 l.128 uses "`\alpha_2=-\gamma`" (Godfrin's notation).

8. **Transition-temperature names.** ch06 uses `T_c` for the film (l.124–529) and `T_{\rm BKT}(L)` for the field crossing (l.576–658). ch07 uses `T_{\rm BKT}`, plus a generic `T/T_c` (l.340). `T_{\rm KT}` occurs nowhere. ch05 l.321 uses T for a duration, and ch07's Lean `T` is a time horizon.

9. **The torus mean flow 2πd/L² has three names.** ch03 calls it `\bar{\mathbf u}=\frac{\kappa}{L^2}(\dots)` (l.275), ch06 calls it v (l.388), ch07 calls it u (l.352). ch07's u also means the phonon drift (l.408). ch06's u is 1/K, ch04's u is the series variable, and ch03's `\mathbf u` is the velocity field.

10. **H has several normalisations.** ch06's H is the KT invariant `f(u)-2\pi^3y^2`, and its `H_{\rm WM}` gives energy `\pi H_{\rm WM}` in ℏ²n/m. ch07's H is the dimensionless `-\sum q_iq_j\ln r_{ij}^2`. ch06's pair energy is `2\pi J\ln(d/a)`.

11. **ρ in ch07's Einstein relation.** The keybox (l.53), l.381 and the Lean `einstein_vortex` (l.374–376) use ρ, but K uses ρ_s (l.361, 395). R_E=1 needs ρ=ρ_s. Mehdi's formula uses ρ₀ (l.60–61). Separately, ch06's ρ_s is an areal mass density in g cm⁻², while ch06's ρ(k) and the captions' `\rho_q(k)` are vortex charge densities.

12. **κ is consistent.** ch07 κ=2π, ch03 κ=h/m and =2π in solver units (l.16, 41), ch01 l.245 κ=2πℏ/m. ch06 does not use κ. ch03 calls the winding number w (l.24, 77), while ch06/07 use q, and ch07's w is the wind parameter.

13. **Capital letters reused from the C_V series of ch04 (A, C, D, E, K, L):** ch07 A (skew operator), ch06 C_L, E_c and E_pair (energies), K (stiffness), and L (box side, vs the coefficient of T⁹).

14. **Other repeated letters:**
    - ε: ch06 `\epsilon` (H-offset, sign flips between l.515 and l.527) and `\varepsilon` (dielectric constant, l.628); ch07 ε(k) (excitation energy, as in ch04/05).
    - τ: ratio (ch06), lag (ch07), time unit (ch09).
    - λ: λ_T (ch06) vs a rate (ch07 l.435).
    - W: matching cost (ch06) vs hypothesis label (ch07).
    - m: mass vs vortex positions in both chapters, shell index (ch06 l.614), Lean lower bound (ch07 l.310).
    - c: about five meanings in ch07.
    - a, b: core size / KT parameter (ch06) vs roots of the wind equation (ch07).

15. **Hard-coded duplicates.** ch07 writes T_BKT(L=64)=0.821 (l.191), 237 022 / 511 and commit 5db8041 (l.154) as literals; in ch06 these are the macros `\cnTbktSixtyfour`, `\cnPoneOld`, `\cnPoneNew`, `\cnCommitShort`. They agree now but are not linked.

16. **m(⁴He) precision.** ch06 prints `4.002\,603\,254\,13` u (l.132); ch03 prints 4.002603254 u (`\cthreeNum{mHeU}`, `ch03_numbers.json`). Same NIST value, different number of digits.

17. **Wrong script name in ch06's header.** l.3–4 says the macro block is generated "by figures/ch06_inject_macros.py". No such file exists in `book/figures/`. The injector is `figures/ch06_numbers.py` (its docstring l.1–4 and line 172–175; the JSON "note" agrees).

18. **Engine provenance in ch06.** l.538 attributes the field section to "The engine of \cref{ch06:coulomb}" (qf-pgpe); l.648 says the ladder values come from "the programme's numpy engine".

19. **Undefined couplings.** `\tilde g` (ch06 l.594, 653) and "mg=1" (ch07 l.473) are both undefined. They are probably the same dimensionless 2D coupling, but that is unclear.

20. **Lean module naming in ch07.** `\Lthm{DissipativePairs}{…}` at l.149 and l.449, but the module is `Ch07_DissipativePairs` (l.130, 134, 426). ch06's new module, Ch06_KTForward, is cited with `\lean{…}` and theorem names only.

21. **Relation name.** ch06's "spin-wave relation" `\eta\,n_s\lambda_T^2=1` is the "Josephson relation" of ch10 (l.511). ch06 l.175 says so, but Appendix D should list both names.

22. **Low priority, within ch07.** The replacement gate gives α_energy = 0.00705±0.00012 at T=0.115 (l.234), while Table ch07:tab-alpha gives 0.0062±0.0004 at the same T (l.274). These are different measurements (a single gate vs the 8-run ensemble), but the text does not reconcile them.
